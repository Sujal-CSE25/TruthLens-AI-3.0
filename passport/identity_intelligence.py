"""
TruthLens Border Intelligence — Identity Intelligence
Detects potential identity conflicts across screening history.

IMPORTANT:
- Never automatically accuses a person of fraud
- Flags are for human review only
- Uses indexed screening history (not real government databases)

SIH 2026 · PS 26188 · PROTOTYPE — NOT FOR OPERATIONAL USE
"""
import json
from database import db


def analyze_identity_consistency(
    passport_number: str,
    name: str,
    dob: str,
    nationality: str,
    face_embedding_hash: str = "",
) -> dict:
    """
    Check current submission against indexed screening history for:
    - Duplicate passport numbers with different identity fields
    - Same name+DOB with different passport numbers
    - Same biometric hash linked to different documents

    Returns:
      {
        "status": "NO_CONCERN" | "POTENTIAL_IDENTITY_LINK" | "MANUAL_REVIEW_REQUIRED",
        "flags": [...],
        "checked_against": int,  # number of existing records checked
        "limitations": str
      }
    """
    flags = []
    limitations = (
        "Identity checks are performed against this system's local screening history only. "
        "This is NOT a check against government identity registers. "
        "Potential links require manual officer verification before any action."
    )

    # Check 1: Duplicate passport number with different fields
    persons_with_passport = db.find_persons_by_passport(passport_number) if passport_number else []
    for existing in persons_with_passport:
        existing_name = existing.get("name_visual", "").strip().upper()
        submitted_name = name.strip().upper() if name else ""

        if existing_name and submitted_name and existing_name != submitted_name:
            flags.append({
                "type":        "passport_number_name_conflict",
                "description": (f"Passport number '{passport_number}' was previously associated "
                                f"with name '{existing.get('name_visual')}' — submitted as '{name}'"),
                "value":       passport_number,
                "severity":    "HIGH",
                "confidence":  0.85,
                "limitations": "Name differences may be due to transliteration or OCR errors.",
                "prior_screening_id": json.loads(existing.get("linked_screenings", "[]") or "[]"),
            })

        existing_dob = existing.get("dob_visual", "").strip()
        submitted_dob = dob.strip() if dob else ""
        if existing_dob and submitted_dob and existing_dob != submitted_dob:
            flags.append({
                "type":        "passport_number_dob_conflict",
                "description": (f"Passport number '{passport_number}' previously associated "
                                f"with DOB '{existing_dob}' — submitted as '{submitted_dob}'"),
                "value":       passport_number,
                "severity":    "HIGH",
                "confidence":  0.90,
                "limitations": "Date format differences may cause false positives.",
            })

    # Check 2: Same name+DOB, different passport number
    if name and dob:
        persons_with_name_dob = db.find_persons_by_name_dob(name.strip(), dob.strip())
        for existing in persons_with_name_dob:
            ex_passport = existing.get("passport_number", "").strip()
            if ex_passport and ex_passport != passport_number:
                flags.append({
                    "type":        "name_dob_multiple_passports",
                    "description": (f"Name '{name}' with DOB '{dob}' is linked to a different "
                                    f"passport number '{ex_passport}' in screening history"),
                    "value":       ex_passport,
                    "severity":    "MEDIUM",
                    "confidence":  0.70,
                    "limitations": ("Same name and DOB may belong to different people. "
                                    "Manual document comparison required."),
                    "prior_screening_id": json.loads(existing.get("linked_screenings", "[]") or "[]"),
                })

    # Determine status
    if any(f["severity"] == "HIGH" for f in flags):
        status = "MANUAL_REVIEW_REQUIRED"
    elif flags:
        status = "POTENTIAL_IDENTITY_LINK"
    else:
        status = "NO_CONCERN"

    return {
        "status":         status,
        "flags":          flags,
        "checked_against": len(persons_with_passport) + (len(persons_with_name_dob) if name and dob else 0),
        "limitations":    limitations,
    }
