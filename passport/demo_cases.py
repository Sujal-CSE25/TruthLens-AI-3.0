"""
TruthLens Border Intelligence — Demo Cases
8 deterministic synthetic demo cases for SIH 2026 demonstration.

ARCHITECTURE REQUIREMENT: Demo cases run through the SAME real screening pipeline
as live submissions. They inject synthetic passport image bytes (or override specific
OCR fields directly) so the pipeline runs authentically.

Demo cases define:
  - Synthetic OCR text with specific anomalies baked in
  - Expected risk level (for result verification only, not to hardcode output)
  - Description for display in the UI

The real verdict comes from the pipeline — not from hardcoded JSON.

SIH 2026 · PS 26188 · PROTOTYPE — NOT FOR OPERATIONAL USE
"""
import io
import struct
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np


# ─── Synthetic Passport Image Generator ─────────────────────
# Creates a minimal JPEG passport-like image with embedded text
# so the real OCR + forensics pipeline runs on real pixel data.

def _get_demo_fonts():
    font_header = None
    font_label = None
    font_mrz = None
    for name in ["consola.ttf", "cour.ttf", "lucon.ttf", "arial.ttf"]:
        try:
            font_mrz = ImageFont.truetype(name, 18)
            break
        except Exception:
            pass
    for name in ["arial.ttf", "calibri.ttf", "segoeui.ttf"]:
        try:
            font_header = ImageFont.truetype(name, 22)
            font_label = ImageFont.truetype(name, 16)
            break
        except Exception:
            pass
    return font_header, font_label, font_mrz


def _make_passport_image(
    name: str = "SHARMA RAHUL",
    passport_no: str = "J1234567",
    nationality: str = "IND",
    dob: str = "01/01/1990",
    expiry: str = "01/01/2030",
    gender: str = "M",
    mrz_line1: str = None,
    mrz_line2: str = None,
    ela_tamper: bool = False,
    face_image_bytes: bytes = None,
) -> bytes:
    """
    Generate a synthetic passport image with text fields.
    Returns JPEG bytes.
    """
    width, height = 900, 650
    img = Image.new("RGB", (width, height), color=(245, 245, 240))
    draw = ImageDraw.Draw(img)
    font_header, font_label, font_mrz = _get_demo_fonts()

    # Background border
    draw.rectangle([0, 0, width, height], outline=(20, 60, 120), width=6)

    # Header
    draw.rectangle([0, 0, width, 75], fill=(20, 60, 120))
    draw.text((width//2 - 140, 14), "REPUBLIC OF INDIA", fill="white", font=font_header)
    draw.text((width//2 - 50, 44), "PASSPORT", fill="white", font=font_label)

    # Photo placeholder
    draw.rectangle([35, 100, 220, 310], fill=(215, 215, 215), outline=(100, 100, 100), width=2)
    if face_image_bytes:
        try:
            face_pil = Image.open(io.BytesIO(face_image_bytes)).convert("RGB").resize((185, 210))
            img.paste(face_pil, (35, 100))
        except Exception:
            draw.text((95, 195), "PHOTO", fill=(100, 100, 100), font=font_label)
    else:
        draw.text((95, 195), "PHOTO", fill=(100, 100, 100), font=font_label)

    # Fields
    y = 100
    fields = [
        ("Surname", name.split()[0] if name else ""),
        ("Given Names", " ".join(name.split()[1:]) if name else ""),
        ("Nationality", nationality),
        ("Date of Birth", dob),
        ("Sex", gender),
        ("Passport No.", passport_no),
        ("Date of Expiry", expiry),
    ]
    for label, val in fields:
        draw.text((250, y), f"{label}: {val}", fill="black", font=font_label)
        y += 32

    # Stamp region (bottom right)
    draw.ellipse([680, 360, 840, 510], outline=(180, 30, 30), width=3)
    draw.text((720, 420), "DEMO\nSTAMP", fill=(180, 30, 30), font=font_label)

    # MRZ Zone
    draw.rectangle([0, 520, width, height], fill=(255, 255, 255), outline=(180, 180, 180), width=2)
    l1 = mrz_line1 or f"P<IND{name.replace(' ', '<').upper():<39}"
    l1 = (l1 + "<" * 44)[:44]
    l2 = mrz_line2 or f"{passport_no}0{nationality}{dob.replace('/', '')[:6]}0{gender}{expiry.replace('/', '')[:6]}0{'<' * 14}0"
    # Draw monospaced MRZ characters at exact ICAO pitch
    pitch = 19.5
    for i, ch in enumerate(l1):
        draw.text((25 + i * pitch, 545), ch, fill="black", font=font_mrz)
    for i, ch in enumerate(l2):
        draw.text((25 + i * pitch, 585), ch, fill="black", font=font_mrz)

    # Optional: Apply tamper simulation by overlaying a slightly different color block
    if ela_tamper:
        draw.rectangle([250, 100, 550, 140], fill=(235, 235, 225))
        draw.text((250, 100), f"Surname: {name.split()[0] if name else ''}", fill="black", font=font_label)

    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=95)
    return buf.getvalue()


# ─── MRZ Check Digit Helper ──────────────────────────────────

_CHAR_VALUES: dict[str, int] = {str(i): i for i in range(10)}
_CHAR_VALUES.update({chr(ord('A') + i): 10 + i for i in range(26)})
_CHAR_VALUES['<'] = 0


def _check_digit(s: str) -> int:
    weights = [7, 3, 1]
    return sum(_CHAR_VALUES.get(c.upper(), 0) * weights[i % 3]
               for i, c in enumerate(s)) % 10


def _build_mrz_line2(passport_no: str, nationality: str, dob_yymmdd: str,
                      sex: str, expiry_yymmdd: str) -> str:
    """Build a valid MRZ Line 2 with correct check digits per ICAO 9303 TD3."""
    pn = (passport_no + "<" * 9)[:9]
    c1 = str(_check_digit(pn))
    nat = (nationality + "<<<")[:3]
    c2 = str(_check_digit(dob_yymmdd))
    c3 = str(_check_digit(expiry_yymmdd))
    personal = "<<<<<<<<<<<<<<"
    c_personal = "<"
    composite_input = pn + c1 + dob_yymmdd + c2 + expiry_yymmdd + c3 + personal + c_personal
    c4 = str(_check_digit(composite_input))
    return f"{pn}{c1}{nat}{dob_yymmdd}{c2}{sex}{expiry_yymmdd}{c3}{personal}{c_personal}{c4}"


# ─── 8 Demo Case Definitions ─────────────────────────────────

DEMO_CASES = {

    "01_CLEAN_PASSPORT": {
        "id":           "01_CLEAN_PASSPORT",
        "title":        "01 — Clean Passport",
        "description":  "All checks expected to pass — healthy baseline case",
        "expected_risk": "CLEAR",
        "params": {
            "name": "PATEL AMIT",
            "passport_no": "P1234567",
            "nationality": "IND",
            "dob": "15/03/1985",
            "dob_yymmdd": "850315",
            "expiry": "14/03/2035",
            "expiry_yymmdd": "350314",
            "gender": "M",
            "ela_tamper": False,
        },
    },

    "02_TAMPERED_DOB": {
        "id":           "02_TAMPERED_DOB",
        "title":        "02 — Tampered Date of Birth",
        "description":  "DOB in visual zone differs from MRZ — typical forgery pattern",
        "expected_risk": "HIGH_RISK",
        "params": {
            "name": "KUMAR SURESH",
            "passport_no": "Q9876543",
            "nationality": "IND",
            "dob": "01/01/2005",      # Visual shows 2005
            "dob_yymmdd": "700101",    # MRZ says 1970 — mismatch
            "expiry": "31/12/2030",
            "expiry_yymmdd": "301231",
            "gender": "M",
            "ela_tamper": True,
        },
    },

    "03_MRZ_MISMATCH": {
        "id":           "03_MRZ_MISMATCH",
        "title":        "03 — MRZ Check Digit Failures",
        "description":  "MRZ line 2 has deliberate check digit errors",
        "expected_risk": "HIGH_RISK",
        "params": {
            "name": "SINGH PRIYA",
            "passport_no": "R1111111",
            "nationality": "IND",
            "dob": "10/06/1992",
            "dob_yymmdd": "920610",
            "expiry": "09/06/2032",
            "expiry_yymmdd": "320609",
            "gender": "F",
            "ela_tamper": False,
            "mrz_line2_override": "R11111110IND920610F3206090<<<<<<<<<<<<<<5",  # wrong check digits
        },
    },

    "04_FACE_MISMATCH": {
        "id":           "04_FACE_MISMATCH",
        "title":        "04 — Face Mismatch",
        "description":  "Presented live probe photo does not match document photo — real biometric mismatch detected",
        "expected_risk": "MANUAL_REVIEW",
        "params": {
            "name": "NAIR MEERA",
            "passport_no": "S2222222",
            "nationality": "IND",
            "dob": "22/09/1988",
            "dob_yymmdd": "880922",
            "expiry": "21/09/2028",
            "expiry_yymmdd": "280921",
            "gender": "F",
            "ela_tamper": False,
            "face_image": "demo_face_woman.jpg",
            "probe_image": "demo_face_man.jpg",
        },
    },

    "05_EXPIRED_DOCUMENT": {
        "id":           "05_EXPIRED_DOCUMENT",
        "title":        "05 — Expired Document",
        "description":  "Passport expiry date is in the past",
        "expected_risk": "HIGH_RISK",
        "params": {
            "name": "VERMA RAVI",
            "passport_no": "T3333333",
            "nationality": "IND",
            "dob": "05/08/1975",
            "dob_yymmdd": "750805",
            "expiry": "04/08/2020",    # Expired
            "expiry_yymmdd": "200804",
            "gender": "M",
            "ela_tamper": False,
        },
    },

    "06_VISA_INCONSISTENCY": {
        "id":           "06_VISA_INCONSISTENCY",
        "title":        "06 — Visa Inconsistency",
        "description":  "Passport not found in visa registry — inconsistency flagged",
        "expected_risk": "MANUAL_REVIEW",
        "params": {
            "name": "GUPTA ANITA",
            "passport_no": "U4444444",   # Not in demo visa registry
            "nationality": "IND",
            "dob": "12/11/1995",
            "dob_yymmdd": "951112",
            "expiry": "11/11/2030",
            "expiry_yymmdd": "301111",
            "gender": "F",
            "ela_tamper": False,
        },
    },

    "07_POTENTIAL_DUPLICATE_IDENTITY": {
        "id":           "07_POTENTIAL_DUPLICATE_IDENTITY",
        "title":        "07 — Potential Duplicate Identity",
        "description":  "Same name and DOB as a previously screened person with different passport",
        "expected_risk": "MANUAL_REVIEW",
        "params": {
            "name": "SHARMA RAHUL",
            "passport_no": "V5555555",
            "nationality": "IND",
            "dob": "01/01/1990",
            "dob_yymmdd": "900101",
            "expiry": "31/12/2030",
            "expiry_yymmdd": "301231",
            "gender": "M",
            "ela_tamper": False,
        },
    },

    "08_MULTI_ANOMALY": {
        "id":           "08_MULTI_ANOMALY",
        "title":        "08 — Multi-Anomaly Case",
        "description":  "Multiple concurrent red flags: tampered DOB + MRZ mismatch + ELA anomaly",
        "expected_risk": "HIGH_RISK",
        "params": {
            "name": "DEMO SUSPECT PERSON",
            "passport_no": "Z9999999",     # Flagged in registry
            "nationality": "IND",
            "dob": "01/01/2010",
            "dob_yymmdd": "600101",         # DOB mismatch (visual 2010, MRZ 1960)
            "expiry": "31/12/2025",         # Near-expired
            "expiry_yymmdd": "251231",
            "gender": "M",
            "ela_tamper": True,
            "mrz_line2_override": "Z99999990IND600101M2512310<<<<<<<<<<<<<<1",  # bad check digit
        },
    },
}


def build_demo_image(case_id: str) -> bytes:
    """
    Build a synthetic passport image for the given demo case.
    Returns JPEG bytes that are fed into the REAL screening pipeline.
    """
    case = DEMO_CASES.get(case_id)
    if not case:
        raise ValueError(f"Unknown demo case: {case_id}")

    p = case["params"]
    dob_yymmdd    = p["dob_yymmdd"]
    expiry_yymmdd = p["expiry_yymmdd"]
    passport_no   = p["passport_no"]
    nationality   = p["nationality"]
    gender        = p["gender"]

    # Build valid MRZ line 2 (unless override)
    mrz_l2 = p.get("mrz_line2_override") or _build_mrz_line2(
        passport_no, nationality, dob_yymmdd, gender, expiry_yymmdd
    )

    # Build MRZ line 1 (ICAO TD3 format: P<COUNTRY<SURNAME<<GIVEN<NAMES<<<<...)
    name_parts = p["name"].split()
    surname = name_parts[0].upper() if name_parts else ""
    given = "<".join(name_parts[1:]).upper() if len(name_parts) > 1 else ""
    name_field = f"{surname}<<{given}" if given else surname
    mrz_l1 = f"P<IND{name_field}<<{'<' * 44}"[:44]

    face_image_bytes = None
    face_rel = p.get("face_image")
    if face_rel:
        asset_path = Path(__file__).parent / "demo_assets" / face_rel
        if asset_path.exists():
            face_image_bytes = asset_path.read_bytes()

    return _make_passport_image(
        name=p["name"],
        passport_no=passport_no,
        nationality=nationality,
        dob=p["dob"],
        expiry=p["expiry"],
        gender=gender,
        mrz_line1=mrz_l1,
        mrz_line2=mrz_l2,
        ela_tamper=p.get("ela_tamper", False),
        face_image_bytes=face_image_bytes,
    )


def build_demo_probe_image(case_id: str) -> bytes | None:
    """
    Return a live probe photo for demo cases that include one (e.g. 04_FACE_MISMATCH).
    Returns JPEG bytes or None if no probe photo is included.
    """
    case = DEMO_CASES.get(case_id)
    if not case:
        return None
    probe_rel = case["params"].get("probe_image")
    if not probe_rel:
        return None
    asset_path = Path(__file__).parent / "demo_assets" / probe_rel
    if asset_path.exists():
        return asset_path.read_bytes()
    return None


def get_demo_case_list() -> list:
    """Return list of demo cases for UI display."""
    return [
        {
            "id":           v["id"],
            "title":        v["title"],
            "description":  v["description"],
            "expected_risk": v["expected_risk"],
        }
        for v in DEMO_CASES.values()
    ]
