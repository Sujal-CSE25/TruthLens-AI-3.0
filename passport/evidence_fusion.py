"""
TruthLens Border Intelligence — Evidence Fusion Engine
Combines all module outputs into a unified, cross-signal evidence structure.

ARCHITECTURE:
  OCR + MRZ + validation + forensics + face + identity + registry
  → cross-signal evidence
  → explainable risk

IMPORTANT: This is the central architectural hub.
Every input module contributes evidence items. Fusion correlates them.
No individual module result is authoritative — only their combination.

SIH 2026 · PS 26188 · PROTOTYPE — NOT FOR OPERATIONAL USE
"""


def fuse_evidence(
    ocr_result: dict,
    mrz_result: dict,
    validation_result: dict,
    forensics_result: dict,
    tamper_result: dict,
    face_result: dict,
    identity_result: dict,
    registry_result: dict,
) -> dict:
    """
    Fuse all module outputs into a single evidence package.

    Returns:
      {
        "evidence_items": [...],          # all individual evidence items
        "module_summaries": {...},        # per-module high-level summary
        "cross_signals": [...],           # inter-module correlations
        "total_evidence_count": int,
        "concerning_evidence_count": int,
      }
    """
    evidence_items = []
    cross_signals  = []

    # ── OCR Evidence ──────────────────────────────────────────
    ocr_conf = ocr_result.get("ocr_confidence", 0)
    ocr_warnings = ocr_result.get("warnings", [])
    evidence_items.append({
        "module":      "ocr",
        "signal":      "ocr_confidence",
        "description": f"OCR extraction confidence: {ocr_conf:.2f}",
        "value":       ocr_conf,
        "concerning":  ocr_conf < 0.4,
        "severity":    "MEDIUM" if ocr_conf < 0.4 else "NONE",
        "confidence":  0.7,
        "limitations": "OCR confidence is an estimate from character density, not Tesseract's internal score.",
    })
    for w in ocr_warnings:
        evidence_items.append({
            "module":      "ocr",
            "signal":      "ocr_warning",
            "description": w,
            "value":       None,
            "concerning":  True,
            "severity":    "LOW",
            "confidence":  0.6,
            "limitations": "OCR warnings may indicate document quality issues rather than forgery.",
        })

    # ── MRZ Evidence ──────────────────────────────────────────
    mrz_summary = mrz_result.get("summary", {})
    checks_passed = mrz_summary.get("checks_passed", 0)
    checks_total  = mrz_summary.get("checks_total", 0)
    failed_checks = mrz_summary.get("failed_checks", [])

    for check in mrz_result.get("check_results", []):
        evidence_items.append({
            "module":      "mrz",
            "signal":      f"mrz_check_{check['field']}",
            "description": check.get("reason", check["field"]),
            "value":       check.get("found_digit"),
            "concerning":  not check["passed"],
            "severity":    check["severity"],
            "confidence":  check["confidence"],
            "limitations": check["limitations"],
        })

    # Date validation from MRZ
    date_val = mrz_result.get("date_validation", {})
    if date_val.get("expired"):
        evidence_items.append({
            "module":      "mrz",
            "signal":      "document_expired",
            "description": date_val.get("expiry_note", "Document is expired"),
            "value":       date_val.get("expiry_parsed"),
            "concerning":  True,
            "severity":    "CRITICAL",
            "confidence":  1.0,
            "limitations": "Expiry check is deterministic from MRZ data.",
        })

    if not mrz_result.get("mrz_detected", False):
        evidence_items.append({
            "module":      "mrz",
            "signal":      "mrz_not_detected",
            "description": "MRZ zone not detected in OCR output — document may lack MRZ or image quality is insufficient",
            "value":       None,
            "concerning":  True,
            "severity":    "HIGH",
            "confidence":  0.7,
            "limitations": "MRZ detection depends on OCR quality. Low-resolution or rotated documents may fail.",
        })

    # ── Validation Evidence ────────────────────────────────────
    for ev in validation_result.get("evidence", []):
        if not ev["passed"] or ev.get("severity") not in ("NONE", ""):
            evidence_items.append({
                "module":      "document_validation",
                "signal":      ev["rule"],
                "description": ev["reason"],
                "value":       ev.get("found"),
                "concerning":  not ev["passed"],
                "severity":    ev["severity"] if not ev["passed"] else "NONE",
                "confidence":  ev.get("confidence", 0.8),
                "limitations": ev.get("limitations", ""),
            })

    # ── Forensics Evidence ────────────────────────────────────
    manip_score = forensics_result.get("manipulation_score", 0)
    evidence_items.append({
        "module":      "forensics",
        "signal":      "ela_manipulation_score",
        "description": f"Image forensics composite manipulation score: {manip_score}/100",
        "value":       manip_score,
        "concerning":  manip_score > 50,
        "severity":    "HIGH" if manip_score > 70 else ("MEDIUM" if manip_score > 40 else "NONE"),
        "confidence":  0.65,
        "limitations": (
            "Forensic scores are statistical indicators, not definitive proof. "
            "JPEG compression, scanning artifacts, and re-saving can elevate scores on genuine documents."
        ),
    })

    for finding in forensics_result.get("all_findings", []):
        evidence_items.append({
            "module":      "forensics",
            "signal":      "forensic_finding",
            "description": finding,
            "value":       None,
            "concerning":  any(w in finding.lower() for w in
                               ["possible", "suspected", "manipulation", "splicing", "inconsist"]),
            "severity":    "LOW",
            "confidence":  0.6,
            "limitations": "Individual forensic findings are statistical observations.",
        })

    # ── Document Tamper Evidence ──────────────────────────────
    tamper_score = tamper_result.get("tamper_score", 0)
    evidence_items.append({
        "module":      "document_tamper",
        "signal":      "document_tamper_score",
        "description": tamper_result.get("summary", f"Document tamper score: {tamper_score}/100"),
        "value":       tamper_score,
        "concerning":  tamper_score > 40,
        "severity":    "HIGH" if tamper_score > 60 else ("MEDIUM" if tamper_score > 30 else "NONE"),
        "confidence":  tamper_result.get("confidence", 0.6),
        "limitations": tamper_result.get("limitations", ""),
    })
    for sig in tamper_result.get("signals", []):
        if sig.get("score", 0) > 30:
            evidence_items.append({
                "module":      "document_tamper",
                "signal":      sig.get("signal", "tamper_signal"),
                "description": sig.get("signal", ""),
                "value":       sig.get("measurement"),
                "concerning":  True,
                "severity":    "MEDIUM",
                "confidence":  sig.get("confidence", 0.5),
                "limitations": sig.get("limitations", ""),
            })

    # ── Face Verification Evidence ────────────────────────────
    face_result_str = face_result.get("result", "UNAVAILABLE")
    similarity = face_result.get("similarity")
    face_concerning = face_result_str in ("NO_MATCH", "UNAVAILABLE")
    evidence_items.append({
        "module":      "face_verification",
        "signal":      "face_comparison_result",
        "description": face_result.get("reason", face_result_str),
        "value":       similarity,
        "concerning":  face_concerning,
        "severity":    ("HIGH" if face_result_str == "NO_MATCH" else
                        "MEDIUM" if face_result_str in ("REVIEW", "UNAVAILABLE") else "NONE"),
        "confidence":  face_result.get("confidence", 0),
        "limitations": face_result.get("limitations", ""),
    })

    # ── Identity Intelligence Evidence ────────────────────────
    id_status = identity_result.get("status", "NO_CONCERN")
    for flag in identity_result.get("flags", []):
        evidence_items.append({
            "module":      "identity_intelligence",
            "signal":      flag.get("type", "identity_flag"),
            "description": flag.get("description", ""),
            "value":       flag.get("value"),
            "concerning":  True,
            "severity":    flag.get("severity", "MEDIUM"),
            "confidence":  flag.get("confidence", 0.7),
            "limitations": flag.get("limitations", "Identity checks are based on indexed screening history."),
        })

    # ── Registry Evidence ─────────────────────────────────────
    reg_passport = registry_result.get("passport", {})
    reg_watchlist = registry_result.get("watchlist", {})
    if reg_watchlist.get("match_found"):
        evidence_items.append({
            "module":      "registry",
            "signal":      "watchlist_match",
            "description": reg_watchlist.get("note", "Watchlist match detected"),
            "value":       reg_watchlist.get("matched_entry"),
            "concerning":  True,
            "severity":    "CRITICAL",
            "confidence":  0.9,
            "limitations": "Watchlist is synthetic demo data — not connected to real government databases.",
        })
    if reg_passport.get("status") == "FLAGGED":
        evidence_items.append({
            "module":      "registry",
            "signal":      "registry_flag",
            "description": reg_passport.get("note", "Passport flagged in registry"),
            "value":       None,
            "concerning":  True,
            "severity":    "HIGH",
            "confidence":  0.85,
            "limitations": "Registry check uses synthetic demo data.",
        })

    # ── Cross-Signal Correlations ─────────────────────────────
    # If MRZ check fails AND forensics are elevated → strong corroboration
    mrz_failed = len(failed_checks) > 0
    forensics_elevated = manip_score > 40 or tamper_score > 40
    if mrz_failed and forensics_elevated:
        cross_signals.append({
            "type":        "corroborated_anomaly",
            "description": ("MRZ validation failures corroborated by elevated forensic signals — "
                            "multiple independent indicators suggest document may be manipulated"),
            "modules":     ["mrz", "forensics"],
            "severity":    "HIGH",
            "confidence":  0.80,
        })

    # If face NO_MATCH AND MRZ fails → strong identity risk
    face_no_match = face_result_str == "NO_MATCH"
    if face_no_match and mrz_failed:
        cross_signals.append({
            "type":        "identity_biometric_conflict",
            "description": ("Face mismatch combined with MRZ anomaly — "
                            "document may not belong to presented person"),
            "modules":     ["face_verification", "mrz"],
            "severity":    "CRITICAL",
            "confidence":  0.75,
        })

    # If validation passes but forensics are high → potential sophisticated forgery
    val_score = validation_result.get("validation_score", 100)
    if val_score >= 80 and (manip_score > 60 or tamper_score > 60):
        cross_signals.append({
            "type":        "visual_forensic_discrepancy",
            "description": ("Visual fields appear valid but forensic signals are elevated — "
                            "possible high-quality forgery where visual content matches but "
                            "physical/digital integrity is compromised"),
            "modules":     ["document_validation", "forensics"],
            "severity":    "HIGH",
            "confidence":  0.65,
        })

    # Count concerning items
    concerning_count = sum(1 for e in evidence_items if e.get("concerning", False))

    # Module summaries
    module_summaries = {
        "ocr": {
            "confidence": ocr_conf,
            "warnings": len(ocr_warnings),
        },
        "mrz": {
            "detected":   mrz_result.get("mrz_detected", False),
            "checks_passed": checks_passed,
            "checks_total":  checks_total,
            "risk_contribution": mrz_summary.get("risk_contribution", "UNKNOWN"),
        },
        "document_validation": {
            "score":       validation_result.get("validation_score", 0),
            "rules_passed": validation_result.get("rules_passed", 0),
            "rules_total":  validation_result.get("rules_run", 0),
        },
        "forensics": {
            "manipulation_score": manip_score,
            "authenticity_score": forensics_result.get("authenticity_score", 100),
        },
        "document_tamper": {
            "tamper_score": tamper_score,
            "suspicious_regions": len(tamper_result.get("suspicious_regions", [])),
        },
        "face_verification": {
            "result":     face_result_str,
            "similarity": similarity,
        },
        "identity_intelligence": {
            "status": id_status,
            "flags":  len(identity_result.get("flags", [])),
        },
        "registry": {
            "watchlist_hit": reg_watchlist.get("match_found", False),
            "passport_status": reg_passport.get("status", "UNKNOWN"),
        },
    }

    return {
        "evidence_items":          evidence_items,
        "module_summaries":        module_summaries,
        "cross_signals":           cross_signals,
        "total_evidence_count":    len(evidence_items),
        "concerning_evidence_count": concerning_count,
    }
