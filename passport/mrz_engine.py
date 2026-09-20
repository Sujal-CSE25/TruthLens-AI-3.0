"""
TruthLens Border Intelligence — MRZ Engine
ICAO Doc 9303 Part 4 (TD3 — Passport) compliant MRZ parser and validator.

All validation is DETERMINISTIC. No LLM is used at any point.

MRZ format (TD3):
  Line 1 (44 chars): P<COUNTRY<SURNAME<<GIVEN<<NAMES<<<<<<<<<<<<<<<<
  Line 2 (44 chars): NNNNNNNNCNNNNNNNNCNNNNNNCNNNNNNNNNNNNNNNNNNNNC
                     [0:9]  [9] [10:13] [13:19] [19] [20:22] [22:28] [28] [29:42] [42]
                     passport# check  nationality dob  check   expiry  check personal# check composite

  Composite check covers positions 0–9, 13–19, 21–26, 28, 29–42

Check-digit algorithm (ICAO):
  Weights cycle: 7, 3, 1
  Characters: 0–9 → face value; A–Z → 10–35; < → 0
  Check digit = sum(value * weight) mod 10

SIH 2026 · PS 26188 · PROTOTYPE — NOT FOR OPERATIONAL USE
"""
import re
from datetime import datetime, date
from passport.passport_fields import PassportFields


# ─── MRZ Character Table ──────────────────────────────────────

_CHAR_VALUES: dict[str, int] = {str(i): i for i in range(10)}
_CHAR_VALUES.update({chr(ord('A') + i): 10 + i for i in range(26)})
_CHAR_VALUES['<'] = 0

_WEIGHTS = [7, 3, 1]


def _check_digit(s: str) -> int:
    """
    Compute ICAO MRZ check digit for string s.
    Returns expected single digit (0–9).
    Unknown characters are treated as 0 (same as '<').
    """
    total = 0
    for i, ch in enumerate(s):
        total += _CHAR_VALUES.get(ch.upper(), 0) * _WEIGHTS[i % 3]
    return total % 10


def _verify_check(field_str: str, claimed_digit: str, field_name: str) -> dict:
    """
    Verify a MRZ check digit.
    Returns structured evidence item.
    """
    # Per ICAO 9303 Part 4: if optional personal_number field is unused, both field and check digit are '<' or '0'
    clean_input = field_str.replace('<', '').strip()
    if field_name == "personal_number" and not clean_input and str(claimed_digit) in ('<', '0', ''):
        return {
            "field": field_name,
            "signal": "mrz_check_digit",
            "input": field_str,
            "expected_digit": claimed_digit,
            "found_digit": claimed_digit,
            "passed": True,
            "severity": "NONE",
            "confidence": 1.0,
            "limitations": "Optional personal number field not used by issuing state.",
        }

    try:
        expected = _check_digit(field_str)
        actual = int(claimed_digit)
        passed = expected == actual
    except (ValueError, TypeError):
        passed = False
        expected = -1
        actual = -1

    return {
        "field": field_name,
        "signal": "mrz_check_digit",
        "input": field_str,
        "expected_digit": expected,
        "found_digit": actual if actual != -1 else claimed_digit,
        "passed": passed,
        "severity": "HIGH" if not passed else "NONE",
        "confidence": 1.0,   # Check digit is deterministic — result is certain
        "limitations": "Check digit only validates the digit field itself, not the issuing authority.",
    }


# ─── Date Parsing ─────────────────────────────────────────────

def _parse_mrz_date(yymmdd: str, future_if_ambiguous: bool = False) -> str:
    """
    Convert YYMMDD to YYYY-MM-DD.
    YY < 30 → 20YY (born/expires 2000+)
    YY >= 30 → 19YY for DOB, 20YY for expiry (per ICAO heuristic)
    Returns empty string on parse failure.
    """
    if not yymmdd or len(yymmdd) != 6 or not yymmdd.isdigit():
        return ""
    yy = int(yymmdd[:2])
    mm = int(yymmdd[2:4])
    dd = int(yymmdd[4:6])

    if future_if_ambiguous:
        # Expiry dates: always in the future side
        year = 2000 + yy
    else:
        # DOB: if yy >= 30, assume 19XX (born in 20th century)
        year = (2000 + yy) if yy < 30 else (1900 + yy)

    try:
        d = date(year, mm, dd)
        return d.strftime("%Y-%m-%d")
    except ValueError:
        return ""


# ─── MRZ Line Extraction from OCR Text ───────────────────────

_MRZ_LINE_RE = re.compile(r'^[A-Z0-9<]{44}$')


def _clean_mrz_candidate(raw: str) -> str:
    """Clean and normalize potential MRZ line from OCR output."""
    cleaned = raw.strip().upper()
    # Replace common OCR misreads of '<'
    for sym in ['«', '‹', '{', '}', '(', ')', '[', ']', '|', '\\', '/', ' ']:
        cleaned = cleaned.replace(sym, '<' if sym != ' ' else '')
    return cleaned


def extract_mrz_from_text(ocr_text: str) -> tuple[str, str]:
    """
    Locate two 44-character MRZ-format lines in OCR output.
    Cleans OCR artifacts and normalizes candidate lines.
    Returns (line1, line2) or ("", "") if not found.
    """
    raw_lines = [l.strip() for l in ocr_text.splitlines() if l.strip()]
    cleaned_lines = [_clean_mrz_candidate(l) for l in raw_lines]

    # Find Line 1 candidates (starts with P< or P[A-Z])
    l1_candidates = []
    l2_candidates = []

    for l in cleaned_lines:
        if (l.startswith("P<") or (len(l) >= 2 and l[0] == "P" and l[1] in "ACIPV<")) and "<" in l:
            norm = (l + "<" * 44)[:44]
            if _MRZ_LINE_RE.match(norm):
                l1_candidates.append(norm)
        elif len(l) >= 20 and any(c.isdigit() for c in l[:10]) and ("IND" in l or "<" in l):
            norm = (l + "<" * 44)[:44]
            if _MRZ_LINE_RE.match(norm):
                l2_candidates.append(norm)

    if l1_candidates and l2_candidates:
        return l1_candidates[0], l2_candidates[0]

    # Fallback: check adjacent pairs
    for i in range(len(cleaned_lines) - 1):
        c1 = (cleaned_lines[i] + "<" * 44)[:44]
        c2 = (cleaned_lines[i + 1] + "<" * 44)[:44]
        if _MRZ_LINE_RE.match(c1) and _MRZ_LINE_RE.match(c2):
            return c1, c2

    return "", ""


# ─── Line 1 Parser ───────────────────────────────────────────

def _parse_line1(line1: str) -> dict:
    """
    Parse TD3 MRZ Line 1.
    Layout: [0:2] doc_type, [2:5] country, [5:44] name_field
    Name field: SURNAME<<GIVEN<<NAMES separated by <<
    """
    if len(line1) != 44:
        return {"error": f"Line 1 length {len(line1)}, expected 44"}

    doc_type = line1[0:2].replace('<', '').strip()
    country  = line1[2:5].replace('<', '').strip()
    name_field = line1[5:44]

    parts = name_field.split('<<', 1)
    surname = parts[0].replace('<', ' ').strip()
    given   = parts[1].replace('<', ' ').strip() if len(parts) > 1 else ""

    return {
        "document_type": doc_type,
        "country_code": country,
        "surname": surname,
        "given_names": given,
    }


# ─── Line 2 Parser ───────────────────────────────────────────

def _parse_line2(line2: str) -> dict:
    """
    Parse TD3 MRZ Line 2.
    Positions:
      0–8   passport number (9 chars including check at [8])
      8     passport number check digit
      9–11  nationality (3 chars)
      12–17 DOB YYMMDD
      17    DOB check digit
      18    sex
      19–24 expiry YYMMDD
      25    expiry check digit  (note: ICAO positions use 0-based index)
      26–41 personal number (15 chars, check at [41] or [42])
      42    personal number check digit
      43    composite check digit (covers 0–9,13–19,21–26,28,29–42)

    Actual 0-based char offsets per ICAO 9303:
      [0:9]  = passport_number  [9]  = check1
      [10:13]= nationality
      [13:19]= dob              [19] = check2
      [20]   = sex
      [21:27]= expiry           [27] = check3
      [28:42]= personal_number  [42] = check4
      [43]   = composite check
    """
    if len(line2) != 44:
        return {"error": f"Line 2 length {len(line2)}, expected 44"}

    passport_number = line2[0:9]
    check1          = line2[9]
    nationality     = line2[10:13]
    dob             = line2[13:19]
    check2          = line2[19]
    sex             = line2[20]
    expiry          = line2[21:27]
    check3          = line2[27]
    personal_number = line2[28:42]
    check4          = line2[42]
    composite_check = line2[43]

    # Composite covers: passport_number+check1 + dob+check2 + expiry+check3 + personal_number+check4
    composite_input = line2[0:10] + line2[13:20] + line2[21:28] + line2[28:43]

    return {
        "passport_number": passport_number.replace('<', '').strip(),
        "passport_number_raw": passport_number,
        "check1": check1,
        "nationality": nationality.replace('<', '').strip(),
        "dob": dob,
        "check2": check2,
        "sex": sex,
        "expiry": expiry,
        "check3": check3,
        "personal_number": personal_number.replace('<', '').strip(),
        "check4": check4,
        "composite_check": composite_check,
        "composite_input": composite_input,
    }


# ─── Full MRZ Pipeline ────────────────────────────────────────

def run_mrz_pipeline(ocr_text: str, image_bytes: bytes = None) -> dict:
    """
    Full MRZ pipeline:
      1. Extract MRZ lines from OCR text
      2. Parse Line 1 + Line 2
      3. Validate all check digits (deterministic)
      4. Validate dates
      5. Return structured evidence

    Returns:
      {
        "mrz_detected": bool,
        "mrz_confidence": float,
        "parsed": PassportFields-compatible dict,
        "check_results": [...],
        "date_validation": {...},
        "warnings": [...],
        "summary": {...}
      }
    """
    line1, line2 = extract_mrz_from_text(ocr_text)

    if not line1 or not line2:
        return {
            "mrz_detected": False,
            "mrz_confidence": 0.0,
            "parsed": {},
            "check_results": [],
            "date_validation": {},
            "warnings": ["MRZ not detected in OCR output. Check image quality or orientation."],
            "summary": {
                "checks_passed": 0,
                "checks_total": 0,
                "all_checks_pass": False,
                "risk_contribution": "UNCERTAIN",
            },
        }

    l1 = _parse_line1(line1)
    l2 = _parse_line2(line2)

    warnings = []
    if "error" in l1:
        warnings.append(f"Line 1 parse: {l1['error']}")
    if "error" in l2:
        warnings.append(f"Line 2 parse: {l2['error']}")

    # Run all check-digit verifications
    check_results = []

    if "error" not in l2:
        check_results.append(_verify_check(
            l2["passport_number_raw"], l2["check1"], "passport_number"))
        check_results.append(_verify_check(
            l2["dob"], l2["check2"], "date_of_birth"))
        check_results.append(_verify_check(
            l2["expiry"], l2["check3"], "expiry_date"))
        check_results.append(_verify_check(
            l2["personal_number"] + l2.get("check4", ""), l2.get("check4", "0"), "personal_number"))
        check_results.append(_verify_check(
            l2["composite_input"], l2["composite_check"], "composite"))

    checks_passed = sum(1 for c in check_results if c["passed"])
    checks_total  = len(check_results)

    # Date validation
    date_validation = {}
    if "error" not in l2:
        today = date.today()

        dob_parsed    = _parse_mrz_date(l2["dob"], future_if_ambiguous=False)
        expiry_parsed = _parse_mrz_date(l2["expiry"], future_if_ambiguous=True)

        dob_valid = False
        dob_note  = "Could not parse DOB"
        if dob_parsed:
            try:
                dob_date = datetime.strptime(dob_parsed, "%Y-%m-%d").date()
                age = (today - dob_date).days / 365.25
                if 0 <= age <= 120:
                    dob_valid = True
                    dob_note  = f"DOB plausible — age {int(age)} years"
                else:
                    dob_note = f"DOB implies implausible age: {age:.1f} years"
            except ValueError:
                dob_note = f"DOB parse failed: {dob_parsed}"

        expiry_valid = False
        expired      = None
        expiry_note  = "Could not parse expiry"
        if expiry_parsed:
            try:
                exp_date = datetime.strptime(expiry_parsed, "%Y-%m-%d").date()
                expired  = exp_date < today
                expiry_valid = True
                days_remaining = (exp_date - today).days
                if expired:
                    expiry_note = f"DOCUMENT EXPIRED — {abs(days_remaining)} days ago"
                else:
                    expiry_note = f"Valid — expires in {days_remaining} days"
            except ValueError:
                expiry_note = f"Expiry parse failed: {expiry_parsed}"

        date_validation = {
            "dob_raw":      l2["dob"],
            "dob_parsed":   dob_parsed,
            "dob_valid":    dob_valid,
            "dob_note":     dob_note,
            "expiry_raw":   l2["expiry"],
            "expiry_parsed": expiry_parsed,
            "expiry_valid": expiry_valid,
            "expired":      expired,
            "expiry_note":  expiry_note,
        }

    # Confidence: based on check pass rate + MRZ detection
    mrz_confidence = checks_passed / checks_total if checks_total > 0 else 0.0

    # Risk contribution from MRZ
    failed = checks_total - checks_passed
    if failed == 0 and checks_total > 0:
        risk_contribution = "NONE"
    elif failed == 1:
        risk_contribution = "LOW"
    elif failed <= 3:
        risk_contribution = "HIGH"
    else:
        risk_contribution = "CRITICAL"

    parsed = {}
    if "error" not in l1:
        parsed.update({
            "document_type_mrz": l1.get("document_type", ""),
            "country_code_mrz":  l1.get("country_code", ""),
            "surname_mrz":       l1.get("surname", ""),
            "given_names_mrz":   l1.get("given_names", ""),
        })
    if "error" not in l2:
        parsed.update({
            "passport_number_mrz":   l2.get("passport_number", ""),
            "nationality_mrz":       l2.get("nationality", ""),
            "dob_mrz":               l2.get("dob", ""),
            "dob_mrz_parsed":        date_validation.get("dob_parsed", ""),
            "gender_mrz":            l2.get("sex", ""),
            "expiry_mrz":            l2.get("expiry", ""),
            "expiry_mrz_parsed":     date_validation.get("expiry_parsed", ""),
            "personal_number_mrz":   l2.get("personal_number", ""),
            "check_passport_number": check_results[0]["passed"] if len(check_results) > 0 else False,
            "check_dob":             check_results[1]["passed"] if len(check_results) > 1 else False,
            "check_expiry":          check_results[2]["passed"] if len(check_results) > 2 else False,
            "check_personal_number": check_results[3]["passed"] if len(check_results) > 3 else False,
            "check_composite":       check_results[4]["passed"] if len(check_results) > 4 else False,
            "mrz_checks_passed":     checks_passed,
            "mrz_checks_total":      checks_total,
            "mrz_line1": line1,
            "mrz_line2": line2,
        })

    return {
        "mrz_detected":   True,
        "mrz_line1":      line1,
        "mrz_line2":      line2,
        "mrz_confidence": round(mrz_confidence, 3),
        "parsed":         parsed,
        "check_results":  check_results,
        "date_validation": date_validation,
        "warnings":       warnings,
        "summary": {
            "checks_passed":    checks_passed,
            "checks_total":     checks_total,
            "all_checks_pass":  failed == 0 and checks_total > 0,
            "failed_checks":    [c["field"] for c in check_results if not c["passed"]],
            "risk_contribution": risk_contribution,
        },
    }
