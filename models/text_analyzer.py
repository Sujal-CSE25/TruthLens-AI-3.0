"""
TruthLens AI 2.0 — Text Analysis Model
Full pipeline: Forensics → Multi-Agent → Risk Score → Explainability → DB
"""
import uuid
from agents.multi_agent import run_multi_agent_analysis
from explainability.reasoning import build_explainability_report
from database.db import save_analysis, save_claims
from utils.helpers import hash_text


def run_text_analysis(text: str) -> dict:
    """
    Full text analysis pipeline.

    1. Validate input
    2. Run multi-agent analysis (claim extraction → evidence → fact check → risk → explain → judge)
    3. Build the explainability report (Phase 9)
    4. Store results + claims + evidence in database
    5. Return complete result dict
    """
    if not text or len(text.strip()) < 15:
        return {"error": "Text is too short. Please provide at least 15 characters."}

    try:
        # Run the full multi-agent pipeline
        result = run_multi_agent_analysis(text)

        # Build structured explainability report
        result["explainability_report"] = build_explainability_report(result)

        # Persist to database
        analysis_id = str(uuid.uuid4())
        result["analysis_id"] = analysis_id

        save_analysis(
            analysis_id   = analysis_id,
            analysis_type = "text",
            input_hash    = hash_text(text),
            result        = result,
        )

        # Save individual claims + linked evidence
        if result.get("claim_verification"):
            save_claims(analysis_id, result["claim_verification"], result.get("evidence_map"))

        return result

    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}
