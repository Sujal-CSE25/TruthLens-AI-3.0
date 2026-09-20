"""
TruthLens AI 2.0 — Document Verification Model
"""
import io
import uuid
from PIL import Image
from forensics.document_forensics import run_full_document_analysis
from database.db import save_document
from utils.config import SUPPORTED_DOC_TYPES
from utils.helpers import hash_text


def run_document_verification(uploaded_file) -> dict:
    """
    Full document verification pipeline:
    1. OCR text extraction
    2. Document type detection
    3. Template structure analysis
    4. Font/date consistency checks
    5. AI-powered forgery detection
    6. Aggregate authenticity scoring
    """
    if uploaded_file is None:
        return {"error": "No document uploaded."}

    ext = uploaded_file.name.split(".")[-1].lower()
    if ext not in SUPPORTED_DOC_TYPES:
        return {"error": f"Unsupported type: .{ext}. Supported: PDF, PNG, JPG, JPEG."}

    image_bytes = uploaded_file.read()

    mime_map = {"jpg": "image/jpeg", "jpeg": "image/jpeg",
                "png": "image/png", "pdf": "application/pdf"}
    mime_type = mime_map.get(ext, "image/jpeg")

    # For PDF, convert first page to image or extract text
    if ext == "pdf":
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(image_bytes))
            page = reader.pages[0]
            # Extract text directly from PDF if possible
            pdf_text = page.extract_text() or ""
            if pdf_text.strip():
                # Use PDF text directly for analysis (pass image_bytes=None because raw PDF is application/pdf)
                result = _analyze_pdf_text(image_bytes, pdf_text, uploaded_file.name)
                _persist_result(result, uploaded_file.name)
                return result
        except ImportError:
            pass
        except Exception:
            pass
        mime_type = "application/pdf"


    try:
        result = run_full_document_analysis(image_bytes, uploaded_file.name, mime_type)
        _persist_result(result, uploaded_file.name)
        return result
    except Exception as e:
        return {"error": f"Document analysis failed: {str(e)}"}


def _analyze_pdf_text(image_bytes: bytes, pdf_text: str, filename: str) -> dict:
    """Analyze PDF using directly extracted text."""
    from forensics.document_forensics import (
        detect_document_type, run_font_consistency_check,
        check_date_consistency, run_template_analysis,
        run_gemini_doc_verification,
    )

    doc_type    = detect_document_type(pdf_text, filename)
    font_sig    = run_font_consistency_check(pdf_text)
    date_sig    = check_date_consistency(pdf_text)
    template    = run_template_analysis(pdf_text, doc_type)
    ai_result   = run_gemini_doc_verification(image_bytes, pdf_text, doc_type, mime_type="application/pdf")


    template_penalty = max(0, 100 - template["completeness"]) * 0.2
    ai_forgery       = ai_result.get("forgery_score", 30) * 0.6
    signal_penalty   = (len(font_sig) + len(date_sig)) * 5
    aggregate_forgery= min(int(ai_forgery + template_penalty + signal_penalty), 100)

    return {
        "doc_type":            doc_type,
        "ocr_text":            pdf_text,
        "forgery_score":       aggregate_forgery,
        "authenticity_score":  max(0, 100 - aggregate_forgery),
        "confidence":          ai_result.get("confidence", 55),
        "verdict":             ai_result.get("verdict", "INCONCLUSIVE"),
        "explanation":         ai_result.get("explanation", ""),
        "recommendation":      ai_result.get("recommendation", ""),
        "forgery_indicators":  font_sig + date_sig + ai_result.get("forgery_indicators", []),
        "authenticity_signals":ai_result.get("authenticity_signals", []),
        "structural_issues":   ai_result.get("structural_issues", []),
        "template_analysis":   template,
        "file_size":           f"{len(image_bytes) / 1024:.1f} KB",
    }


def _persist_result(result: dict, filename: str) -> None:
    doc_id = str(uuid.uuid4())
    result["doc_id"] = doc_id
    save_document(
        doc_id   = doc_id,
        doc_type = result.get("doc_type", "unknown"),
        result   = result,
    )
