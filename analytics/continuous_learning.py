"""
TruthLens AI 2.0 — Continuous Learning Module
User Feedback System → Dataset Building → Retraining Readiness → Model Versioning.
"""
import json
from database.db import get_conn, log_event


# ─── Dataset Export ───────────────────────────────────────────

def export_feedback_dataset() -> list:
    """
    Build a labeled dataset from analyses + feedback.
    Each row: {analysis_id, type, fake_score, verdict, is_correct, result_json}

    This dataset is the input for a future retraining pass — e.g. to
    recalibrate the linguistic risk-component weights in
    forensics/text_forensics.py based on real user corrections.
    """
    sql = """
        SELECT a.analysis_id, a.type, a.fake_score, a.verdict,
               f.is_correct, f.user_note, a.result_json
        FROM analyses a
        JOIN feedback f ON f.analysis_id = a.analysis_id
        ORDER BY f.created_at DESC
    """
    with get_conn() as conn:
        rows = conn.execute(sql).fetchall()

    dataset = []
    for r in rows:
        dataset.append({
            "analysis_id": r["analysis_id"],
            "type":        r["type"],
            "fake_score":  r["fake_score"],
            "verdict":     r["verdict"],
            "is_correct":  bool(r["is_correct"]),
            "user_note":   r["user_note"],
        })
    return dataset


# ─── Retraining Readiness ────────────────────────────────────

def compute_retraining_readiness(target_samples: int = 100) -> dict:
    """
    Determine how close the platform is to having enough labeled
    feedback to justify a retraining / recalibration pass.
    """
    dataset = export_feedback_dataset()
    total   = len(dataset)
    correct = sum(1 for d in dataset if d["is_correct"])
    incorrect = total - correct

    progress_pct = min(int(total / target_samples * 100), 100) if target_samples else 0
    ready = total >= target_samples

    # Simple heuristic: if "incorrect" feedback rate is high on a given
    # content type, flag that type for priority recalibration.
    type_errors = {}
    for d in dataset:
        t = d["type"]
        type_errors.setdefault(t, {"total": 0, "incorrect": 0})
        type_errors[t]["total"] += 1
        if not d["is_correct"]:
            type_errors[t]["incorrect"] += 1

    priority_types = []
    for t, stats in type_errors.items():
        if stats["total"] >= 5:
            err_rate = stats["incorrect"] / stats["total"]
            if err_rate > 0.3:
                priority_types.append({"type": t, "error_rate": round(err_rate, 2)})

    return {
        "total_samples":   total,
        "correct":         correct,
        "incorrect":       incorrect,
        "target_samples":  target_samples,
        "progress_pct":    progress_pct,
        "ready_to_retrain": ready,
        "priority_types":  priority_types,
    }


# ─── Threshold Recalibration (lightweight heuristic) ──────────

def suggest_threshold_adjustment() -> dict:
    """
    Heuristic recalibration suggestion based on feedback patterns.

    If users frequently mark HIGH-risk verdicts as "Incorrect", the
    HIGH_RISK threshold may be too low (too many false positives) —
    suggest raising it slightly, and vice versa.

    This does NOT mutate config automatically; it returns a
    recommendation for a human-in-the-loop review, consistent with
    safe continuous-learning practice.
    """
    dataset = export_feedback_dataset()
    if len(dataset) < 10:
        return {
            "has_recommendation": False,
            "reason": "Not enough feedback samples yet (need at least 10).",
        }

    high_risk_wrong = sum(
        1 for d in dataset
        if d["fake_score"] >= 70 and not d["is_correct"]
    )
    high_risk_total = sum(1 for d in dataset if d["fake_score"] >= 70)

    low_risk_wrong = sum(
        1 for d in dataset
        if d["fake_score"] < 40 and not d["is_correct"]
    )
    low_risk_total = sum(1 for d in dataset if d["fake_score"] < 40)

    recs = []
    if high_risk_total >= 5 and (high_risk_wrong / high_risk_total) > 0.35:
        recs.append(
            "High false-positive rate on HIGH-risk verdicts "
            f"({high_risk_wrong}/{high_risk_total}) — consider raising "
            "THRESHOLD_HIGH_RISK from 70 to ~75."
        )
    if low_risk_total >= 5 and (low_risk_wrong / low_risk_total) > 0.35:
        recs.append(
            "High false-negative rate on LOW-risk verdicts "
            f"({low_risk_wrong}/{low_risk_total}) — consider lowering "
            "THRESHOLD_MEDIUM_RISK from 40 to ~35."
        )

    return {
        "has_recommendation": len(recs) > 0,
        "recommendations": recs,
        "sample_size": len(dataset),
    }


# ─── Model Versioning ─────────────────────────────────────────

def record_model_version(version: str, accuracy: float, samples: int, notes: str = "") -> None:
    sql = "INSERT INTO model_versions (version, accuracy, samples, notes) VALUES (?,?,?,?)"
    with get_conn() as conn:
        conn.execute(sql, (version, accuracy, samples, notes))
    log_event("model_version_recorded", {"version": version, "accuracy": accuracy})


def get_model_versions() -> list:
    sql = "SELECT version, accuracy, samples, notes, created_at FROM model_versions ORDER BY id DESC"
    with get_conn() as conn:
        rows = conn.execute(sql).fetchall()
    return [dict(r) for r in rows]


def ensure_baseline_version() -> None:
    """Seed an initial model_versions row on first run, if table is empty."""
    versions = get_model_versions()
    if not versions:
        record_model_version(
            version="2.0.0-baseline",
            accuracy=0.0,
            samples=0,
            notes="Initial multi-agent pipeline deployment. "
                  "Linguistic forensics + RAG + 6-agent reasoning.",
        )
