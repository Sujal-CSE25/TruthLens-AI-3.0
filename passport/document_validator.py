"""
TruthLens Border Intelligence — Document Validation Engine
Deterministic rule-based validation for passport documents.

Every rule returns structured evidence with:
  rule, field, expected, found, severity, passed, reason, confidence, limitations

No LLM is used. All checks are deterministic Python.
SIH 2026 · PS 26188 · PROTOTYPE — NOT FOR OPERATIONAL USE
"""
import re
from datetime import datetime, date
from utils.config import PASSPORT_NUMBER_REGEX


# ─── Evidence Item Schema ─────────────────────────────────────

def _evidence(rule: str, field: str, expected: str, found: str,
              passed: bool, severity: str, reason: str,
              confidence: float = 1.0, limitations: str = "") -> dict:
    return {
        "rule":        rule,
        "field":       field,
        "expected":    expected,
        "found":       str(found),
        "passed":      passed,
        "severity":    severity,     # NONE | LOW | MEDIUM | HIGH | CRITICAL
        "reason":      reason,
        "confidence":  confidence,
        "limitations": limitations,
    }


# ─── Individual Rules ─────────────────────────────────────────

def _check_required_fields(fields: dict) -> list:
    """All mandatory passport fields must be present."""
    required = {
        "passport_number_visual": "Passport Number",
        "dob_visual":             "Date of Birth",
        "expiry_visual":          "Expiry Date",
        "nationality_visual":     "Nationality",
    }
    results = []
    for key, label in required.items():
        val = str(fields.get(key, "")).strip()
        present = bool(val)
        results.append(_evidence(
            rule="required_field",
            field=key,
            expected="Non-empty value",
            found=val if val else "(empty)",
            passed=present,
            severity="HIGH" if not present else "NONE",
            reason=f"{label} is present" if present else f"{label} is missing from extracted fields",
        ))
    # Name: accept either full name or surname
    has_name = bool(fields.get("surname_visual") or
                    fields.get("given_names_visual") or
                    fields.get("name_visual", ""))
    results.append(_evidence(
        rule="required_field",
        field="name",
        expected="Surname and/or given names",
        found=fields.get("surname_visual", "") + " " + fields.get("given_names_visual", ""),
        passed=has_name,
        severity="HIGH" if not has_name else "NONE",
        reason="Name field extracted" if has_name else "Name not found in visual zone",
    ))
    return results


def _check_expiry(fields: dict, mrz_parsed: dict) -> list:
    """Document must not be expired."""
    results = []
    today = date.today()

    # Check visual expiry
    expiry_str = str(fields.get("expiry_visual", "")).strip()
    if expiry_str:
        try:
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
                try:
                    exp_date = datetime.strptime(expiry_str, fmt).date()
                    break
                except ValueError:
                    exp_date = None
            if exp_date:
                expired = exp_date < today
                days = (exp_date - today).days
                results.append(_evidence(
                    rule="expiry_check",
                    field="expiry_visual",
                    expected="Future date",
                    found=expiry_str,
                    passed=not expired,
                    severity="CRITICAL" if expired else "NONE",
                    reason=("DOCUMENT EXPIRED — " + str(abs(days)) + " days ago")
                           if expired else f"Valid — expires in {days} days",
                    confidence=1.0,
                ))
        except Exception:
            results.append(_evidence(
                rule="expiry_check",
                field="expiry_visual",
                expected="Parseable date",
                found=expiry_str,
                passed=False,
                severity="MEDIUM",
                reason="Expiry date could not be parsed from visual zone",
                confidence=0.7,
                limitations="Date format may be non-standard",
            ))

    # Cross-check with MRZ expiry
    mrz_expired = mrz_parsed.get("date_validation", {}).get("expired")
    mrz_expiry_note = mrz_parsed.get("date_validation", {}).get("expiry_note", "")
    if mrz_expired is not None:
        results.append(_evidence(
            rule="expiry_check_mrz",
            field="expiry_mrz",
            expected="Future date",
            found=mrz_parsed.get("date_validation", {}).get("expiry_parsed", ""),
            passed=not mrz_expired,
            severity="CRITICAL" if mrz_expired else "NONE",
            reason=mrz_expiry_note,
            confidence=1.0,
        ))
    return results


def _check_dob(fields: dict, mrz_date_val: dict) -> list:
    """DOB must be in the past and imply a plausible age (0–120 years)."""
    results = []
    today = date.today()

    dob_str = str(fields.get("dob_visual", "")).strip()
    if dob_str:
        try:
            dob_date = None
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
                try:
                    dob_date = datetime.strptime(dob_str, fmt).date()
                    break
                except ValueError:
                    pass
            if dob_date:
                age = (today - dob_date).days / 365.25
                plausible = 0 <= age <= 120
                results.append(_evidence(
                    rule="dob_plausibility",
                    field="dob_visual",
                    expected="DOB in past, age 0–120",
                    found=dob_str,
                    passed=plausible,
                    severity="HIGH" if not plausible else "NONE",
                    reason=f"DOB implies age {int(age)} years" +
                           (" — IMPLAUSIBLE" if not plausible else " — plausible"),
                    confidence=1.0,
                ))
        except Exception:
            results.append(_evidence(
                rule="dob_plausibility",
                field="dob_visual",
                expected="Parseable date",
                found=dob_str,
                passed=False,
                severity="MEDIUM",
                reason="Date of birth could not be parsed",
                confidence=0.6,
                limitations="Date format may be non-standard or OCR error",
            ))

    # MRZ DOB validity
    mrz_dob_valid = mrz_date_val.get("dob_valid", None)
    mrz_dob_note  = mrz_date_val.get("dob_note", "")
    if mrz_dob_valid is not None:
        results.append(_evidence(
            rule="dob_plausibility_mrz",
            field="dob_mrz",
            expected="Plausible DOB in MRZ",
            found=mrz_date_val.get("dob_parsed", ""),
            passed=mrz_dob_valid,
            severity="HIGH" if not mrz_dob_valid else "NONE",
            reason=mrz_dob_note,
            confidence=1.0,
        ))
    return results


def _check_passport_number_format(fields: dict, mrz_parsed: dict) -> list:
    """Passport number must match expected format."""
    results = []
    pattern = re.compile(PASSPORT_NUMBER_REGEX)

    pn_visual = str(fields.get("passport_number_visual", "")).strip().upper()
    if pn_visual:
        match = bool(pattern.match(pn_visual))
        results.append(_evidence(
            rule="passport_number_format",
            field="passport_number_visual",
            expected="Letter + 7 digits (Indian passport format)",
            found=pn_visual,
            passed=match,
            severity="MEDIUM" if not match else "NONE",
            reason="Format matches expected pattern" if match
                   else "Passport number does not match expected format — may be non-Indian or OCR error",
            confidence=0.8,
            limitations="Format check is for Indian passports. Other countries use different formats.",
        ))

    pn_mrz = str(mrz_parsed.get("passport_number_mrz", "")).strip().upper()
    if pn_mrz:
        match_mrz = bool(pattern.match(pn_mrz))
        results.append(_evidence(
            rule="passport_number_format_mrz",
            field="passport_number_mrz",
            expected="Letter + 7 digits (Indian passport format)",
            found=pn_mrz,
            passed=match_mrz,
            severity="MEDIUM" if not match_mrz else "NONE",
            reason="MRZ passport number format" +
                   (" matches" if match_mrz else " does not match — possible forgery or non-Indian passport"),
            confidence=0.8,
            limitations="Format check is for Indian passports.",
        ))
    return results


def _check_nationality(fields: dict, mrz_parsed: dict) -> list:
    """Nationality must be a valid ISO 3166-1 alpha-3 code."""
    # Non-exhaustive sample of valid codes
    VALID_CODES = {
        "AFG","ALB","DZA","AND","AGO","ARG","ARM","AUS","AUT","AZE",
        "BHS","BHR","BGD","BLR","BEL","BLZ","BEN","BTN","BOL","BIH",
        "BWA","BRA","BRN","BGR","BFA","BDI","CPV","KHM","CMR","CAN",
        "CAF","TCD","CHL","CHN","COL","COM","COG","CRI","CIV","HRV",
        "CUB","CYP","CZE","DNK","DJI","DOM","ECU","EGY","SLV","GNQ",
        "ERI","EST","SWZ","ETH","FJI","FIN","FRA","GAB","GMB","GEO",
        "DEU","GHA","GRC","GTM","GIN","GNB","GUY","HTI","HND","HUN",
        "ISL","IND","IDN","IRN","IRQ","IRL","ISR","ITA","JAM","JPN",
        "JOR","KAZ","KEN","PRK","KOR","KWT","KGZ","LAO","LVA","LBN",
        "LSO","LBR","LBY","LIE","LTU","LUX","MDG","MWI","MYS","MDV",
        "MLI","MLT","MRT","MUS","MEX","MDA","MCO","MNG","MNE","MAR",
        "MOZ","MMR","NAM","NPL","NLD","NZL","NIC","NER","NGA","NOR",
        "OMN","PAK","PAN","PNG","PRY","PER","PHL","POL","PRT","QAT",
        "ROU","RUS","RWA","SAU","SEN","SRB","SLE","SGP","SVK","SVN",
        "SOM","ZAF","SSD","ESP","LKA","SDN","SUR","SWE","CHE","SYR",
        "TWN","TJK","TZA","THA","TLS","TGO","TON","TTO","TUN","TUR",
        "TKM","UGA","UKR","ARE","GBR","USA","URY","UZB","VEN","VNM",
        "YEM","ZMB","ZWE",
        # Placeholder for demo
        "XXX",
    }

    results = []
    nat_visual = str(fields.get("nationality_visual", "")).strip().upper()
    if nat_visual:
        valid = nat_visual in VALID_CODES
        results.append(_evidence(
            rule="nationality_format",
            field="nationality_visual",
            expected="Valid ISO 3166-1 alpha-3 code",
            found=nat_visual,
            passed=valid,
            severity="LOW" if not valid else "NONE",
            reason=f"{nat_visual} is a recognized nationality code" if valid
                   else f"{nat_visual} not in ISO 3166-1 alpha-3 code set — possible OCR error",
            confidence=0.9,
            limitations="Code list is not exhaustive. OCR errors may cause false negatives.",
        ))

    nat_mrz = str(mrz_parsed.get("nationality_mrz", "")).strip().upper()
    if nat_mrz and nat_mrz != nat_visual:
        results.append(_evidence(
            rule="nationality_format_mrz",
            field="nationality_mrz",
            expected="Valid ISO 3166-1 alpha-3",
            found=nat_mrz,
            passed=nat_mrz in VALID_CODES,
            severity="LOW" if nat_mrz not in VALID_CODES else "NONE",
            reason=f"MRZ nationality code: {nat_mrz}",
            confidence=0.9,
        ))
    return results


def _check_gender(fields: dict, mrz_parsed: dict) -> list:
    """Gender field must be M, F, or X."""
    VALID = {"M", "F", "X"}
    results = []

    gender_visual = str(fields.get("gender_visual", "")).strip().upper()
    if gender_visual:
        valid = gender_visual in VALID
        results.append(_evidence(
            rule="gender_format",
            field="gender_visual",
            expected="M, F, or X",
            found=gender_visual,
            passed=valid,
            severity="LOW" if not valid else "NONE",
            reason="Gender field is valid" if valid
                   else f"Gender '{gender_visual}' is not one of M/F/X",
            confidence=0.85,
            limitations="Some older passports use other characters. OCR may misread.",
        ))

    gender_mrz = str(mrz_parsed.get("gender_mrz", "")).strip().upper()
    if gender_mrz and gender_visual and gender_mrz != gender_visual:
        results.append(_evidence(
            rule="gender_visual_mrz_consistency",
            field="gender",
            expected=f"Visual ({gender_visual}) matches MRZ ({gender_mrz})",
            found=f"Visual: {gender_visual}, MRZ: {gender_mrz}",
            passed=False,
            severity="MEDIUM",
            reason="Gender in visual zone differs from MRZ — possible OCR error or document manipulation",
            confidence=0.9,
        ))
    return results


def _check_visual_mrz_consistency(fields: dict, mrz_parsed: dict) -> list:
    """Cross-check visual OCR fields against MRZ parsed fields."""
    results = []

    # Passport number
    pn_v = str(fields.get("passport_number_visual", "")).strip().upper().replace(" ", "")
    pn_m = str(mrz_parsed.get("passport_number_mrz", "")).strip().upper()
    if pn_v and pn_m:
        match = pn_v == pn_m
        results.append(_evidence(
            rule="visual_mrz_passport_number",
            field="passport_number",
            expected=f"Visual ({pn_v}) == MRZ ({pn_m})",
            found=f"Visual: {pn_v}, MRZ: {pn_m}",
            passed=match,
            severity="HIGH" if not match else "NONE",
            reason="Passport numbers match between visual and MRZ zones" if match
                   else "MISMATCH: Passport number differs between visual and MRZ — strong forgery indicator",
            confidence=0.9,
            limitations="OCR errors on either zone may cause false positives.",
        ))

    # DOB (normalise to YYMMDD for comparison)
    dob_v = str(fields.get("dob_visual", "")).strip().replace("-", "")
    dob_m_raw = str(mrz_parsed.get("dob_mrz", "")).strip()
    dob_m_parsed = str(mrz_parsed.get("dob_mrz_parsed", "")).strip().replace("-", "")
    if dob_v and dob_m_parsed:
        # Compare YYYY-MM-DD visual with parsed MRZ
        match = dob_v in dob_m_parsed or dob_m_parsed in dob_v
        results.append(_evidence(
            rule="visual_mrz_dob",
            field="date_of_birth",
            expected="DOB matches between visual and MRZ zones",
            found=f"Visual: {fields.get('dob_visual','')}, MRZ: {mrz_parsed.get('dob_mrz_parsed','')}",
            passed=match,
            severity="HIGH" if not match else "NONE",
            reason="DOB matches between visual and MRZ" if match
                   else "DOB MISMATCH between visual and MRZ — strong forgery indicator",
            confidence=0.85,
            limitations="Date format differences between zones may cause false positives.",
        ))

    # Name (partial match — OCR is imperfect)
    name_v = str(fields.get("surname_visual", "")).strip().upper()
    name_m = str(mrz_parsed.get("surname_mrz", "")).strip().upper()
    if name_v and name_m:
        # Allow partial match: one name starts with the other
        match = (name_v in name_m or name_m in name_v or
                 name_v[:4] == name_m[:4])  # first 4 chars
        results.append(_evidence(
            rule="visual_mrz_surname",
            field="surname",
            expected="Surname consistent between visual and MRZ",
            found=f"Visual: {name_v}, MRZ: {name_m}",
            passed=match,
            severity="MEDIUM" if not match else "NONE",
            reason="Surname broadly matches" if match
                   else "Surname differs between visual zone and MRZ",
            confidence=0.75,
            limitations="OCR errors are common in name fields. Partial match tolerance applied.",
        ))
    return results


# ─── Master Validator ─────────────────────────────────────────

def run_document_validation(ocr_result: dict) -> dict:
    """
    Run all deterministic validation rules on passport OCR output.

    Input: result from run_passport_ocr()
    Returns:
      {
        "rules_run": int,
        "rules_passed": int,
        "rules_failed": int,
        "failed_severities": {HIGH: n, MEDIUM: n, LOW: n},
        "evidence": [...],
        "summary": str,
        "validation_score": 0-100  (100 = all rules passed)
      }
    """
    fields     = ocr_result.get("fields", {})
    mrz_result = ocr_result.get("mrz", {})
    mrz_parsed = mrz_result.get("parsed", {})
    date_val   = mrz_result.get("date_validation", {})

    evidence = []

    # Run all rule groups
    evidence.extend(_check_required_fields(fields))
    evidence.extend(_check_expiry(fields, mrz_result))
    evidence.extend(_check_dob(fields, date_val))
    evidence.extend(_check_passport_number_format(fields, mrz_parsed))
    evidence.extend(_check_nationality(fields, mrz_parsed))
    evidence.extend(_check_gender(fields, mrz_parsed))
    evidence.extend(_check_visual_mrz_consistency(fields, mrz_parsed))

    # Add MRZ check-digit results as evidence
    for check in mrz_result.get("check_results", []):
        evidence.append({
            "rule":       "mrz_check_digit",
            "field":      check["field"],
            "expected":   f"Check digit {check['expected_digit']}",
            "found":      str(check["found_digit"]),
            "passed":     check["passed"],
            "severity":   check["severity"],
            "reason":     ("MRZ check digit valid" if check["passed"]
                           else f"MRZ check digit FAILED for {check['field']} — expected {check['expected_digit']}, found {check['found_digit']}"),
            "confidence": check["confidence"],
            "limitations": check["limitations"],
        })

    # Aggregate
    rules_run    = len(evidence)
    rules_passed = sum(1 for e in evidence if e["passed"])
    rules_failed = rules_run - rules_passed

    sev_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "CRITICAL": 0}
    for e in evidence:
        if not e["passed"]:
            sev = e.get("severity", "LOW")
            sev_counts[sev] = sev_counts.get(sev, 0) + 1

    validation_score = int(rules_passed / rules_run * 100) if rules_run > 0 else 0

    # Summary
    if sev_counts["CRITICAL"] > 0:
        summary = f"CRITICAL failures detected: {sev_counts['CRITICAL']} critical, {sev_counts['HIGH']} high severity"
    elif sev_counts["HIGH"] > 0:
        summary = f"{sev_counts['HIGH']} high-severity rule failures — manual review required"
    elif rules_failed > 0:
        summary = f"{rules_failed} minor validation issues — low confidence in some fields"
    else:
        summary = "All validation rules passed"

    return {
        "rules_run":         rules_run,
        "rules_passed":      rules_passed,
        "rules_failed":      rules_failed,
        "failed_severities": sev_counts,
        "evidence":          evidence,
        "summary":           summary,
        "validation_score":  validation_score,
    }
