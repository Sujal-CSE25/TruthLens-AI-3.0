"""
TruthLens AI 2.0 — Document Forensics Engine
OCR, metadata analysis, forgery detection for certificates, IDs, academic docs.
"""
import io
import re
import json
from PIL import Image, ImageFilter, ImageStat
from utils.config import GEMINI_API_KEY
from utils.gemini_client import call_gemini_json


# ─── OCR (lightweight via PIL/Pillow) ─────────────────────────

def extract_text_from_image(image_bytes: bytes) -> str:
    """
    Attempt OCR using local RapidOCR/Tesseract engine, otherwise return placeholder.
    """
    try:
        from passport.ocr_engine import extract_full_ocr
        text, _ = extract_full_ocr(image_bytes)
        if text and "[OCR unavailable" not in text:
            return text.strip()
    except Exception:
        pass

    try:
        import pytesseract
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        # Pre-process: grayscale, sharpen
        img_gray = img.convert("L")
        img_sharp = img_gray.filter(ImageFilter.SHARPEN)
        text = pytesseract.image_to_string(img_sharp)
        return text.strip()
    except ImportError:
        return "[OCR unavailable — No OCR engine configured on system]"
    except Exception as e:
        return f"[OCR error: {str(e)}]"


# ─── Document Structure Analysis ─────────────────────────────

def detect_document_type(ocr_text: str, filename: str = "") -> str:
    """Heuristically detect the document type."""
    text_lower = ocr_text.lower()
    fn_lower   = filename.lower()

    if any(k in text_lower for k in ["certificate", "certify", "awarded", "completion"]):
        return "certificate"
    if any(k in text_lower for k in ["degree", "bachelor", "master", "doctor", "university", "college"]):
        return "academic_degree"
    if any(k in text_lower for k in ["national id", "aadhaar", "passport", "identity card", "voter"]):
        return "identity_document"
    if any(k in text_lower for k in ["invoice", "receipt", "amount due", "bill to"]):
        return "financial_document"
    if "pdf" in fn_lower:
        return "pdf_document"
    return "general_document"


def run_font_consistency_check(ocr_text: str) -> list:
    """
    Heuristic font/formatting consistency signals from OCR text.
    """
    signals = []
    lines = ocr_text.split("\n")

    # Detect mixed case patterns that may indicate copy-paste
    upper_count = sum(1 for l in lines if l.strip().isupper() and len(l.strip()) > 5)
    if upper_count > len(lines) * 0.4:
        signals.append("Abnormal proportion of ALL-CAPS lines")

    # Detect unusual whitespace patterns
    trailing_spaces = sum(1 for l in lines if l.endswith("  "))
    if trailing_spaces > 3:
        signals.append("Multiple lines with trailing whitespace — possible OCR artifact from text overlay")

    # Detect special character anomalies
    weird_chars = re.findall(r"[^\x00-\x7F]", ocr_text)
    if len(weird_chars) > 10:
        signals.append(f"Non-ASCII characters detected ({len(weird_chars)}) — may indicate font substitution")

    return signals


def check_date_consistency(ocr_text: str) -> list:
    """Check for date anomalies in document text."""
    signals = []
    # Use a non-capturing group so findall returns the FULL 4-digit year,
    # not just the "19"/"20" prefix.
    all_years = re.findall(r"\b(?:19|20)\d{2}\b", ocr_text)

    if len(set(all_years)) > 3:
        signals.append(f"Multiple different years found ({', '.join(sorted(set(all_years)))}) — verify date consistency")

    future_years = [y for y in set(all_years) if int(y) > 2026]
    if future_years:
        signals.append(f"Future date detected: {', '.join(sorted(future_years))} — possible forgery indicator")

    return signals


def run_template_analysis(ocr_text: str, doc_type: str) -> dict:
    """
    Check if document text has expected structural elements for its type.
    """
    expected = {
        "certificate": ["name", "awarded", "date", "signature", "seal"],
        "academic_degree": ["university", "degree", "awarded", "registrar"],
        "identity_document": ["name", "date of birth", "id number", "expiry"],
        "financial_document": ["amount", "date", "account", "total"],
        "general_document": [],
    }

    text_lower = ocr_text.lower()
    required   = expected.get(doc_type, [])
    found      = [kw for kw in required if kw in text_lower]
    missing    = [kw for kw in required if kw not in text_lower]

    completeness = (len(found) / len(required) * 100) if required else 50

    return {
        "expected_fields": required,
        "found_fields":    found,
        "missing_fields":  missing,
        "completeness":    round(completeness, 1),
        "template_score":  round(completeness, 1),
    }


# ─── Gemini Document Verification ────────────────────────────

def run_gemini_doc_verification(image_bytes: bytes, ocr_text: str, doc_type: str,
                                  mime_type: str = "image/jpeg") -> dict:
    """Use Gemini Vision to analyze document for forgery signals."""
    if not GEMINI_API_KEY:
        return _demo_doc_result(doc_type)

    prompt = f"""You are a forensic document verification expert.
Analyze this document image and the OCR text extracted from it.
Document type detected: {doc_type}

OCR Text (may be imperfect):
\"\"\"
{ocr_text[:1500]}
\"\"\"

Perform a comprehensive forgery detection analysis and return ONLY a valid JSON object.
No markdown, no extra text.

{{
  "authenticity_score": <0-100, higher means more authentic>,
  "forgery_score": <0-100, higher means more suspicious>,
  "confidence": <0-100>,
  "verdict": "<one of: LIKELY AUTHENTIC | SUSPICIOUS | LIKELY FORGED | INCONCLUSIVE>",
  "forgery_indicators": ["<indicator1>", "<indicator2>"],
  "authenticity_signals": ["<signal1>", "<signal2>"],
  "structural_issues": ["<issue1>"],
  "recommendation": "<one sentence recommendation>",
  "explanation": "<2-3 sentences explaining the verdict>"
}}"""

    try:
        return call_gemini_json(prompt, image_bytes, mime_type)
    except Exception as e:
        print(f"[DocumentForensics Gemini Error] {e}")
        return {"error": str(e), **_demo_doc_result(doc_type)}



def _demo_doc_result(doc_type: str) -> dict:
    return {
        "authenticity_score": 60,
        "forgery_score": 30,
        "confidence": 55,
        "verdict": "INCONCLUSIVE",
        "forgery_indicators": ["Demo mode — API key required for live analysis"],
        "authenticity_signals": ["Basic structural elements present"],
        "structural_issues": [],
        "recommendation": "Set GEMINI_API_KEY in .env for full AI-powered analysis.",
        "explanation": "Demo mode active. Add your Gemini API key for real forgery detection.",
    }


# ─── Master Document Analyzer ────────────────────────────────

def run_full_document_analysis(image_bytes: bytes, filename: str = "",
                                 mime_type: str = "image/jpeg") -> dict:
    """
    Complete document forensics pipeline:
    OCR → Type Detection → Template Analysis → Forgery Signals → AI Verification
    """
    # Step 1: OCR
    ocr_text = extract_text_from_image(image_bytes)

    # Step 2: Detect document type
    doc_type = detect_document_type(ocr_text, filename)

    # Step 3: Font and format consistency
    font_signals = run_font_consistency_check(ocr_text)

    # Step 4: Date consistency
    date_signals = check_date_consistency(ocr_text)

    # Step 5: Template analysis
    template = run_template_analysis(ocr_text, doc_type)

    # Step 6: AI verification
    ai_result = run_gemini_doc_verification(image_bytes, ocr_text, doc_type, mime_type)

    # Aggregate forgery score
    template_penalty = max(0, 100 - template["completeness"]) * 0.2
    ai_forgery = ai_result.get("forgery_score", 30) * 0.6
    signal_penalty = (len(font_signals) + len(date_signals)) * 5
    aggregate_forgery = min(int(ai_forgery + template_penalty + signal_penalty), 100)
    aggregate_authenticity = max(0, 100 - aggregate_forgery)

    all_signals = font_signals + date_signals
    if ai_result.get("forgery_indicators"):
        all_signals.extend(ai_result["forgery_indicators"])

    return {
        "doc_type":            doc_type,
        "ocr_text":            ocr_text,
        "forgery_score":       aggregate_forgery,
        "authenticity_score":  aggregate_authenticity,
        "confidence":          ai_result.get("confidence", 55),
        "verdict":             ai_result.get("verdict", "INCONCLUSIVE"),
        "explanation":         ai_result.get("explanation", ""),
        "recommendation":      ai_result.get("recommendation", ""),
        "forgery_indicators":  all_signals,
        "authenticity_signals":ai_result.get("authenticity_signals", []),
        "structural_issues":   ai_result.get("structural_issues", []),
        "template_analysis":   template,
        "font_signals":        font_signals,
        "date_signals":        date_signals,
        "file_size":           f"{len(image_bytes) / 1024:.1f} KB",
    }
