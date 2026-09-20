"""
TruthLens Border Intelligence — Risk Engine
Transforms fused evidence into an explainable, traceable risk verdict.

METHODOLOGY (documented — not arbitrary):
─────────────────────────────────────────
For each evidence module:

1. SEVERITY MAPPING
   Each evidence item's severity is mapped to a 0–1 raw risk value:
     NONE     → 0.0
     LOW      → 0.25
     MEDIUM   → 0.50
     HIGH     → 0.75
     CRITICAL → 1.0

2. MODULE RISK SCORE
   The highest-severity evidence within each module determines the module's
   base risk. This prevents low-severity noise from overshadowing critical signals.
   Score = max(severity_values) for that module.

3. CORROBORATION ADJUSTMENT
   If multiple items within a module are concerning, the score is raised slightly:
   +0.10 per additional concerning item (capped at +0.20 per module).
   Corroboration principle: independent signals pointing the same direction
   are more credible than a single signal.

4. CONFIDENCE WEIGHTING
   Each module's score is multiplied by the mean confidence of its evidence items.
   Low-confidence signals contribute proportionally less.

5. NORMALISED MODULE WEIGHTS
   Config-defined relative weights (RISK_WEIGHTS) are normalised to sum to 1.0.
   Final risk = Σ (normalised_weight × confidence-weighted_score)

6. CROSS-SIGNAL BONUS
   Corroborated cross-module signals (from evidence_fusion) add 0.05 per
   HIGH cross-signal and 0.08 per CRITICAL cross-signal to the final score.

7. RISK STATE THRESHOLDS
   Final score (0–100):
     ≥ RISK_THRESHOLD_HIGH    → HIGH_RISK
     ≥ RISK_THRESHOLD_REVIEW  → MANUAL_REVIEW
     < RISK_THRESHOLD_REVIEW  → CLEAR

8. EVIDENCE TRACE
   Every risk contribution is recorded with: module, score, weight, reason.
   Final result carries full RESULT → REASON → EVIDENCE chain.

SIH 2026 · PS 26188 · PROTOTYPE — NOT FOR OPERATIONAL USE
"""
from utils.config import RISK_WEIGHTS, RISK_THRESHOLD_HIGH, RISK_THRESHOLD_REVIEW


_SEVERITY_VALUES = {
    "NONE":     0.0,
    "LOW":      0.25,
    "MEDIUM":   0.50,
    "HIGH":     0.75,
    "CRITICAL": 1.0,
}

# Module name mapping: evidence_item module → RISK_WEIGHTS key
_MODULE_TO_WEIGHT_KEY = {
    "mrz":                   "mrz_validation",
    "document_validation":   "document_validation",
    "forensics":             "forensic_tamper",
    "document_tamper":       "forensic_tamper",      # combined with forensics
    "face_verification":     "face_verification",
    "identity_intelligence": "identity_consistency",
    "registry":              "identity_consistency",  # combined
    "ocr":                   "document_validation",   # OCR quality feeds validation
}


def _normalise_weights(weights: dict) -> dict:
    total = sum(weights.values())
    if total == 0:
        return {k: 1 / len(weights) for k in weights}
    return {k: v / total for k, v in weights.items()}


def calculate_risk(fused_evidence: dict) -> dict:
    """
    Calculate explainable risk from fused evidence.

    Input: output of evidence_fusion.fuse_evidence()
    Returns:
      {
        "risk_level": "CLEAR" | "MANUAL_REVIEW" | "HIGH_RISK",
        "risk_score": int (0-100),
        "verdict": str,
        "module_contributions": [{module, raw_score, weight, weighted_contribution, reason}],
        "cross_signal_bonus": float,
        "reasoning_chain": [str],
        "key_evidence": [...],   # top concerning items
        "methodology": str,      # brief methodology note
        "limitations": str,
      }
    """
    evidence_items = fused_evidence.get("evidence_items", [])
    cross_signals  = fused_evidence.get("cross_signals", [])

    # Step 1: Group evidence by weight key
    module_evidence: dict[str, list] = {k: [] for k in RISK_WEIGHTS}
    for item in evidence_items:
        wkey = _MODULE_TO_WEIGHT_KEY.get(item.get("module", ""), None)
        if wkey and wkey in module_evidence:
            module_evidence[wkey].append(item)

    # Normalise weights
    norm_weights = _normalise_weights(RISK_WEIGHTS)

    # Step 2–5: Compute per-module contribution
    contributions = []
    for module_key, items in module_evidence.items():
        if not items:
            contributions.append({
                "module":               module_key,
                "raw_score":            0.0,
                "confidence_mean":      0.0,
                "weighted_contribution": 0.0,
                "weight":               norm_weights.get(module_key, 0),
                "reason":               "No evidence from this module",
            })
            continue

        concerning = [i for i in items if i.get("concerning", False)]

        # Step 2: Base score from highest severity
        max_sev = max(
            _SEVERITY_VALUES.get(i.get("severity", "NONE"), 0.0)
            for i in concerning
        ) if concerning else 0.0

        # Step 3: Corroboration adjustment
        extra = min(len(concerning) - 1, 2) * 0.10 if len(concerning) > 1 else 0.0
        base_score = min(max_sev + extra, 1.0)

        # Step 4: Confidence weighting
        conf_mean = (sum(i.get("confidence", 0.5) for i in items) / len(items))
        conf_weighted_score = base_score * conf_mean

        # Step 5: Apply module weight
        weighted = conf_weighted_score * norm_weights.get(module_key, 0)

        # Build reason string
        if concerning:
            top = sorted(concerning, key=lambda x: _SEVERITY_VALUES.get(x.get("severity", "NONE"), 0),
                         reverse=True)[0]
            reason = top.get("description", f"Issues in {module_key}")
        else:
            reason = f"No concerning evidence from {module_key}"

        contributions.append({
            "module":               module_key,
            "raw_score":            round(base_score * 100, 1),
            "confidence_mean":      round(conf_mean, 2),
            "weighted_contribution": round(weighted * 100, 1),
            "weight":               round(norm_weights.get(module_key, 0), 3),
            "concerning_count":     len(concerning),
            "reason":               reason,
        })

    # Sum all weighted contributions
    raw_total = sum(c["weighted_contribution"] for c in contributions)

    # Step 6: Cross-signal bonus
    cs_bonus = 0.0
    for cs in cross_signals:
        sev = cs.get("severity", "LOW")
        if sev == "CRITICAL":
            cs_bonus += 8.0
        elif sev == "HIGH":
            cs_bonus += 5.0
        elif sev == "MEDIUM":
            cs_bonus += 2.0

    final_score = min(int(raw_total + cs_bonus), 100)

    # Security Rule: Critical signals (biometric mismatch, visual-MRZ discrepancies, check digit failures)
    # cannot pass automated screening as CLEAR — minimum risk is MANUAL_REVIEW.
    has_review_trigger = any(
        i.get("severity") in ("HIGH", "CRITICAL") and i.get("concerning", False)
        for i in evidence_items
    )
    if has_review_trigger and final_score < RISK_THRESHOLD_REVIEW:
        final_score = RISK_THRESHOLD_REVIEW

    # Step 7: State thresholds
    if final_score >= RISK_THRESHOLD_HIGH:
        risk_level = "HIGH_RISK"
        verdict = "Document or identity presents HIGH RISK signals — do not clear without specialist review"
    elif final_score >= RISK_THRESHOLD_REVIEW:
        risk_level = "MANUAL_REVIEW"
        verdict = "Document requires MANUAL REVIEW — automated signals are inconclusive or mixed"
    else:
        risk_level = "CLEAR"
        verdict = "No significant risk indicators detected — document passes automated screening"

    # Step 8: Reasoning chain
    chain = []
    for c in sorted(contributions, key=lambda x: x["weighted_contribution"], reverse=True):
        if c["weighted_contribution"] > 0:
            chain.append(
                f"{c['module']} contributed {c['weighted_contribution']:.1f}/100 "
                f"(weight {c['weight']:.2f}, conf {c['confidence_mean']:.2f}): {c['reason']}"
            )
    for cs in cross_signals:
        chain.append(f"Cross-signal [{cs['type']}]: {cs['description']}")

    # Top concerning evidence items
    key_evidence = sorted(
        [e for e in evidence_items if e.get("concerning", False)],
        key=lambda x: _SEVERITY_VALUES.get(x.get("severity", "NONE"), 0),
        reverse=True,
    )[:8]

    return {
        "risk_level":          risk_level,
        "risk_score":          final_score,
        "verdict":             verdict,
        "module_contributions": contributions,
        "cross_signal_bonus":  round(cs_bonus, 1),
        "reasoning_chain":     chain,
        "key_evidence":        key_evidence,
        "methodology": (
            "Risk score = Σ(normalised_weight × confidence × corroboration_adjusted_severity) "
            "+ cross_signal_bonus. "
            f"Thresholds: HIGH_RISK≥{RISK_THRESHOLD_HIGH}, MANUAL_REVIEW≥{RISK_THRESHOLD_REVIEW}."
        ),
        "limitations": (
            "This risk score is a probabilistic indicator based on digital forensic signals. "
            "It is NOT a determination of guilt or innocence. "
            "All HIGH_RISK or MANUAL_REVIEW results require human officer review. "
            "Automated screening must not be the sole basis for any enforcement action."
        ),
    }
