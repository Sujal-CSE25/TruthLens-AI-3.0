"""
TruthLens Border Intelligence — Passport OCR Engine
Robust, modular OCR pipeline supporting:
1. RapidOCR (pure ONNX Runtime local OCR - high accuracy, cross-platform)
2. Tesseract OCR (if configured via TESSERACT_CMD or installed on PATH)
3. Windows Native OCR (winocr)
4. Clear error reporting if no local engine is available (never silent fake data)

SIH 2026 · PS 26188 · PROTOTYPE — NOT FOR OPERATIONAL USE
"""
import io
import os
import re
import shutil
import numpy as np
from PIL import Image, ImageFilter, ImageOps
from passport.passport_fields import PassportFields
from passport.mrz_engine import run_mrz_pipeline


# ─── Modular Engine Detection ────────────────────────────────

_ACTIVE_PROVIDER = None
_RAPID_OCR_INSTANCE = None


def get_ocr_engine_info() -> dict:
    """Detect and return information about the active local OCR engine."""
    global _ACTIVE_PROVIDER, _RAPID_OCR_INSTANCE

    # 1. Try RapidOCR (ONNX-based local OCR)
    try:
        from rapidocr_onnxruntime import RapidOCR
        if _RAPID_OCR_INSTANCE is None:
            _RAPID_OCR_INSTANCE = RapidOCR()
        _ACTIVE_PROVIDER = "rapidocr"
        return {
            "provider": "rapidocr",
            "available": True,
            "details": "RapidOCR ONNX Runtime engine (local, CPU/GPU)",
        }
    except Exception:
        pass

    # 2. Try Tesseract OCR
    tess_path = os.getenv("TESSERACT_CMD") or shutil.which("tesseract")
    if not tess_path:
        for p in [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            os.path.expanduser(r"~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"),
            "/usr/bin/tesseract",
            "/usr/local/bin/tesseract",
        ]:
            if os.path.exists(p):
                tess_path = p
                break

    if tess_path:
        try:
            import pytesseract
            pytesseract.pytesseract.tesseract_cmd = tess_path
            _ACTIVE_PROVIDER = "tesseract"
            return {
                "provider": "tesseract",
                "available": True,
                "details": f"Tesseract OCR at {tess_path}",
            }
        except Exception:
            pass

    # 3. Try Windows Media Native OCR
    try:
        import winocr  # noqa
        _ACTIVE_PROVIDER = "winocr"
        return {
            "provider": "winocr",
            "available": True,
            "details": "Windows Media Native OCR runtime",
        }
    except Exception:
        pass

    _ACTIVE_PROVIDER = "none"
    return {
        "provider": "none",
        "available": False,
        "details": "No local OCR engine available. Install rapidocr-onnxruntime or configure Tesseract.",
    }


# ─── Image Preprocessing ──────────────────────────────────────

def _preprocess_for_ocr(image_bytes: bytes) -> bytes:
    """Preprocess passport image for optimal character legibility."""
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        w, h = img.size

        if w < 1600:
            scale = 1600 / w
            img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

        gray = img.convert("L")
        gray = ImageOps.autocontrast(gray, cutoff=1)
        gray = gray.filter(ImageFilter.SHARPEN)

        buf = io.BytesIO()
        gray.save(buf, "PNG")
        return buf.getvalue()
    except Exception:
        return image_bytes


# ─── OCR Text Extraction ──────────────────────────────────────

def extract_full_ocr(image_bytes: bytes) -> tuple[str, float]:
    """
    Run local OCR on image.
    Returns (extracted_text, confidence_0_to_1).
    Never fabricates fake data if OCR engine is unavailable.
    """
    info = get_ocr_engine_info()
    provider = info["provider"]

    if provider == "rapidocr":
        try:
            global _RAPID_OCR_INSTANCE
            if _RAPID_OCR_INSTANCE is None:
                from rapidocr_onnxruntime import RapidOCR
                _RAPID_OCR_INSTANCE = RapidOCR()

            # RapidOCR handles raw bytes or PIL Image
            res, _ = _RAPID_OCR_INSTANCE(image_bytes)
            if not res:
                return "", 0.0

            lines = [item[1] for item in res]
            scores = [float(item[2]) for item in res]
            mean_conf = float(np.mean(scores)) if scores else 0.0
            return "\n".join(lines), round(mean_conf, 3)
        except Exception as e:
            return f"[RapidOCR error: {str(e)}]", 0.0

    elif provider == "tesseract":
        try:
            import pytesseract
            preprocessed = _preprocess_for_ocr(image_bytes)
            img = Image.open(io.BytesIO(preprocessed))
            text = pytesseract.image_to_string(img, config="--psm 6 -l eng")
            clean = text.strip()
            if not clean:
                return "", 0.0
            alnum = sum(1 for c in clean if c.isalnum())
            conf = min(alnum / max(len(clean), 1), 1.0)
            return clean, round(conf, 3)
        except Exception as e:
            return f"[Tesseract error: {str(e)}]", 0.0

    elif provider == "winocr":
        try:
            import asyncio, winocr
            img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            res = asyncio.run(winocr.recognize_pil(img, lang="en"))
            lines = [l.text for l in res.lines] if hasattr(res, "lines") else [res.text]
            text = "\n".join(lines).strip()
            alnum = sum(1 for c in text if c.isalnum())
            conf = min(alnum / max(len(text), 1), 1.0)
            return text, round(conf, 3)
        except Exception as e:
            return f"[WinOCR error: {str(e)}]", 0.0

    return "[OCR unavailable — No OCR engine configured on system]", 0.0


# ─── Passport Field Extraction ────────────────────────────────

_PASSPORT_NUMBER_PATTERNS = [
    re.compile(r'\b([A-Z]\d{7})\b'),
    re.compile(r'\b([A-Z]{1,2}\d{6,9})\b'),
]

_DATE_PATTERNS = [
    re.compile(r'\b(\d{2})[/\-](\d{2})[/\-](\d{4})\b'),
    re.compile(r'\b(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})\b', re.IGNORECASE),
    re.compile(r'\b(\d{4})[/\-](\d{2})[/\-](\d{2})\b'),
]

_MONTH_MAP = {
    'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
    'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
    'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
}


def _normalise_date(match, pattern_idx: int) -> str:
    try:
        if pattern_idx == 0:
            return f"{match.group(3)}-{match.group(2)}-{match.group(1)}"
        elif pattern_idx == 1:
            mm = _MONTH_MAP.get(match.group(2).lower(), "00")
            dd = match.group(1).zfill(2)
            return f"{match.group(3)}-{mm}-{dd}"
        elif pattern_idx == 2:
            return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
    except Exception:
        pass
    return ""


def _extract_dates_from_text(text: str) -> list:
    dates = []
    for i, pat in enumerate(_DATE_PATTERNS):
        for m in pat.finditer(text):
            d = _normalise_date(m, i)
            if d and d not in dates:
                dates.append(d)
    return dates


def _extract_passport_number(text: str) -> str:
    # First search for explicit label
    m_lbl = re.search(r'(?:passport\s*no\.?|document\s*no\.?)[:\s]*([A-Z0-9]{7,9})\b', text, re.IGNORECASE)
    if m_lbl:
        return m_lbl.group(1).upper()

    for pat in _PASSPORT_NUMBER_PATTERNS:
        m = pat.search(text)
        if m:
            return m.group(1).upper()
    return ""


def _extract_nationality(text: str) -> str:
    m = re.search(r'\b(?:NATIONALITY|CITIZENSHIP)[:\s]*([A-Z]{3})\b', text, re.IGNORECASE)
    if m:
        return m.group(1).upper()
    if re.search(r'\bINDIAN\b|\bINDIA\b', text, re.IGNORECASE):
        return "IND"
    return ""


def _extract_gender(text: str) -> str:
    m = re.search(r'\b(?:SEX|GENDER)[:\s]*([MFX<])\b', text, re.IGNORECASE)
    if m:
        return m.group(1).upper()
    m2 = re.search(r'\b(MALE|FEMALE)\b', text, re.IGNORECASE)
    if m2:
        return "M" if m2.group(1).upper() == "MALE" else "F"
    return ""


def _extract_name_from_text(text: str) -> tuple[str, str]:
    lines = text.splitlines()
    surname = ""
    given_names = ""

    # Check same-line matches first
    for line in lines:
        if not surname:
            m_sur = re.search(r'(?:surname|last\s*name)[:\s]+([A-Za-z\s]+)', line, re.IGNORECASE)
            if m_sur:
                cand = m_sur.group(1).strip()
                if cand and not any(k in cand.lower() for k in ['given', 'name', 'birth', 'date']):
                    surname = cand.title()
        if not given_names:
            m_giv = re.search(r'(?:given\s*names?|first\s*name)[:\s]+([A-Za-z\s]+)', line, re.IGNORECASE)
            if m_giv:
                cand = m_giv.group(1).strip()
                if cand and not any(k in cand.lower() for k in ['surname', 'birth', 'date', 'national']):
                    given_names = cand.title()

    # Next-line fallback
    if not surname or not given_names:
        for i, line in enumerate(lines):
            lower = line.lower()
            if not surname and ('surname' in lower or 'last name' in lower):
                for j in range(i + 1, min(i + 3, len(lines))):
                    cand = lines[j].strip()
                    if cand and not any(k in cand.lower() for k in ['given', 'name', 'birth', 'date']):
                        surname = cand.title()
                        break
            if not given_names and ('given name' in lower or 'first name' in lower):
                for j in range(i + 1, min(i + 3, len(lines))):
                    cand = lines[j].strip()
                    if cand and not any(k in cand.lower() for k in ['surname', 'birth', 'date', 'national']):
                        given_names = cand.title()
                        break

    return surname, given_names


# ─── Master Passport OCR Pipeline ────────────────────────────

def run_passport_ocr(image_bytes: bytes) -> dict:
    """Run full passport OCR, field extraction, and MRZ parsing."""
    engine_info = get_ocr_engine_info()
    ocr_text, ocr_confidence = extract_full_ocr(image_bytes)

    warnings = []
    if not ocr_text or "[OCR" in ocr_text:
        warnings.append(f"OCR extraction unavailable or empty ({engine_info.get('details')}).")

    dates = _extract_dates_from_text(ocr_text)
    surname, given_names = _extract_name_from_text(ocr_text)
    passport_number = _extract_passport_number(ocr_text)
    nationality     = _extract_nationality(ocr_text)
    gender          = _extract_gender(ocr_text)

    dob_visual    = ""
    expiry_visual = ""
    if dates:
        dates_sorted = sorted(dates)
        if len(dates_sorted) >= 2:
            dob_visual    = dates_sorted[0]
            expiry_visual = dates_sorted[-1]
        elif len(dates_sorted) == 1:
            dob_visual = dates_sorted[0]

    if not passport_number and ocr_text and "[OCR" not in ocr_text:
        warnings.append("Passport number not clearly identified in visual zone.")
    if not dob_visual and ocr_text and "[OCR" not in ocr_text:
        warnings.append("Date of birth not found in visual zone.")
    if not expiry_visual and ocr_text and "[OCR" not in ocr_text:
        warnings.append("Expiry date not found in visual zone.")
    if not nationality and ocr_text and "[OCR" not in ocr_text:
        warnings.append("Nationality not found in visual zone.")

    # Run MRZ pipeline
    mrz_result = run_mrz_pipeline(ocr_text, image_bytes)

    return {
        "ocr_text":       ocr_text,
        "ocr_confidence": ocr_confidence,
        "ocr_provider":   engine_info.get("provider", "unknown"),
        "fields": {
            "surname_visual":          surname,
            "given_names_visual":      given_names,
            "passport_number_visual":  passport_number,
            "nationality_visual":      nationality,
            "dob_visual":              dob_visual,
            "expiry_visual":           expiry_visual,
            "gender_visual":           gender,
            "all_dates_found":         dates,
            "passport_number":         passport_number,
            "name":                    f"{surname} {given_names}".strip() if (surname or given_names) else "",
            "dob":                     dob_visual,
            "expiry":                  expiry_visual,
            "nationality":             nationality,
            "gender":                  gender,
        },
        "mrz": mrz_result,
        "warnings": warnings,
    }
