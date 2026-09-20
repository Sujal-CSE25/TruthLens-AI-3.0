"""
TruthLens AI 2.0 — Image Analysis Model
Local forensics (ELA, EXIF, noise, compression, edge) + Gemini Vision AI
"""
import io
import uuid
from PIL import Image
from forensics.image_forensics import run_full_image_forensics
from explainability.reasoning import build_image_explainability_report
from utils.gemini_client import call_gemini_json
from utils.config import GEMINI_API_KEY, SUPPORTED_IMAGE_TYPES
from database.db import save_analysis
from utils.helpers import hash_text


def run_image_analysis(uploaded_file) -> dict:
    """
    Full image analysis pipeline:
    1. Validate and read image
    2. Local forensics (ELA, EXIF, noise, compression, edge)
    3. Gemini Vision AI analysis
    4. Merge scores and persist
    """
    if uploaded_file is None:
        return {"error": "No image uploaded."}

    ext = uploaded_file.name.split(".")[-1].lower()
    if ext not in SUPPORTED_IMAGE_TYPES:
        return {"error": f"Unsupported file type: .{ext}. Supported: JPG, PNG, WEBP."}

    image_bytes = uploaded_file.read()

    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.verify()
    except Exception:
        return {"error": "Could not open image. Please upload a valid image file."}

    mime_map = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}
    mime_type = mime_map.get(ext, "image/jpeg")

    try:
        # Step 1: Local forensics
        forensics = run_full_image_forensics(image_bytes)

        # Step 2: Gemini Vision (if key available)
        ai_result = _run_gemini_vision(image_bytes, mime_type, forensics)

        # Step 3: Merge results
        local_manip    = forensics.get("manipulation_score", 0)
        ai_generated   = ai_result.get("ai_generated_score", 0)
        ai_manip       = ai_result.get("manipulation_score", 0)
        ai_confidence  = ai_result.get("confidence", 60)

        # Weighted final scores
        final_manip       = int(local_manip * 0.4 + ai_manip * 0.6)
        final_ai_gen      = ai_generated
        final_auth        = max(0, 100 - final_manip)

        # Determine verdict
        if final_ai_gen >= 70:
            verdict = "LIKELY AI-GENERATED"
        elif final_manip >= 70:
            verdict = "LIKELY MANIPULATED"
        elif final_manip >= 40 or final_ai_gen >= 40:
            verdict = "POSSIBLY MANIPULATED"
        else:
            verdict = "LIKELY AUTHENTIC"

        result = {
            "ai_generated_score":   final_ai_gen,
            "manipulation_score":   final_manip,
            "authenticity_score":   final_auth,
            "confidence":           ai_confidence,
            "verdict":              verdict,
            "explanation":          ai_result.get("explanation", ""),
            "findings":             _merge_findings(forensics, ai_result),
            "metadata_flags":       forensics.get("metadata_flags", []),
            "exif_metadata":        forensics.get("exif_metadata", {}),
            "image_size":           forensics.get("image_size", ""),
            "image_mode":           forensics.get("image_mode", ""),
            "file_size":            forensics.get("file_size", ""),
            "format":               forensics.get("format", ""),
            "forensic_detail": {
                "ela":         forensics.get("ela", {}),
                "noise":       forensics.get("noise", {}),
                "compression": forensics.get("compression", {}),
                "edge":        forensics.get("edge", {}),
                "exif":        forensics.get("exif", {}),
            },
        }

        # Persist
        analysis_id = str(uuid.uuid4())
        result["analysis_id"] = analysis_id
        result["explainability_report"] = build_image_explainability_report(result)
        save_analysis(
            analysis_id   = analysis_id,
            analysis_type = "image",
            input_hash    = hash_text(str(len(image_bytes))),
            result        = result,
        )

        return result

    except Exception as e:
        return {"error": f"Image analysis failed: {str(e)}"}


def _run_gemini_vision(image_bytes: bytes, mime_type: str, forensics: dict) -> dict:
    """Use Gemini Vision to analyze image with local forensics context."""
    if not GEMINI_API_KEY:
        return _demo_vision_result(forensics)

    local_context = (
        f"Local forensic analysis already completed:\n"
        f"- ELA manipulation score: {forensics.get('ela', {}).get('manipulation_score', 0)}/100\n"
        f"- Noise anomaly score: {forensics.get('noise', {}).get('noise_score', 0)}/100\n"
        f"- EXIF anomaly score: {forensics.get('exif', {}).get('anomaly_score', 0)}/100\n"
        f"- Edge sharpness score: {forensics.get('edge', {}).get('edge_score', 0)}/100\n"
        f"- EXIF flags: {'; '.join(forensics.get('metadata_flags', []))}"
    )

    prompt = f"""You are an expert deepfake and image manipulation forensic analyst.
Analyze this image carefully for signs of AI generation, manipulation, or splicing.
Consider pixel-level details, lighting physics, facial geometry, and texture consistency.

{local_context}

Return ONLY valid JSON (no markdown, no extra text):
{{
  "ai_generated_score": <0-100, probability of AI generation>,
  "manipulation_score": <0-100, probability of manipulation/editing>,
  "confidence": <0-100>,
  "verdict": "<LIKELY AUTHENTIC|POSSIBLY MANIPULATED|LIKELY MANIPULATED|LIKELY AI-GENERATED|DEEPFAKE SUSPECTED>",
  "explanation": "<2-3 sentence professional analysis>",
  "ai_findings": ["<finding1>", "<finding2>", "<finding3>"],
  "visual_anomalies": ["<anomaly1>", "<anomaly2>"]
}}"""

    try:
        return call_gemini_json(prompt, image_bytes, mime_type)
    except Exception as e:
        print(f"[ImageAnalyzer Gemini Vision Error] {e}")
        return _demo_vision_result(forensics)



def _demo_vision_result(forensics: dict) -> dict:
    local_manip = forensics.get("manipulation_score", 30)
    return {
        "ai_generated_score": max(20, local_manip - 10),
        "manipulation_score": local_manip,
        "confidence": 60,
        "verdict": "POSSIBLY MANIPULATED" if local_manip >= 40 else "LIKELY AUTHENTIC",
        "explanation": "Demo mode — set GEMINI_API_KEY for live AI vision analysis. Local forensics have been applied.",
        "ai_findings": ["Demo mode active", "Local forensic analysis completed"],
        "visual_anomalies": [],
    }


def _merge_findings(forensics: dict, ai_result: dict) -> list:
    findings = []
    findings.extend(forensics.get("all_findings", [])[:5])
    findings.extend(ai_result.get("ai_findings", [])[:3])
    findings.extend(ai_result.get("visual_anomalies", [])[:2])
    return findings
