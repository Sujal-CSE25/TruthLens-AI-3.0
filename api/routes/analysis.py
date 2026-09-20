"""
TruthLens AI 2.0 — Analysis Routes
POST /api/v1/analyze/text      → misinformation / fake-news detection
POST /api/v1/analyze/image     → deepfake / image forensics
POST /api/v1/analyze/document  → document forgery detection
GET  /api/v1/analyze/{id}/evidence → evidence for a given analysis
POST /api/v1/analyze/feedback  → user correctness feedback
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from database.db import get_evidence_for_analysis, save_feedback
from api.schemas.analysis import TextAnalysisRequest, FeedbackRequest
from models.text_analyzer import run_text_analysis
from models.image_analyzer import run_image_analysis
from models.document_analyzer import run_document_verification

router = APIRouter(
    prefix="/analyze",
    tags=["Analysis"],
)


# ─── Helpers ─────────────────────────────────────────────────────

class _FileAdapter:
    """Adapts raw bytes into the interface expected by the model functions."""
    def __init__(self, filename: str, content: bytes):
        self.name = filename
        self._content = content

    def read(self):
        return self._content


def _raise_if_error(result: dict):
    """Convert an error dict from the model layer into an HTTP 422 response."""
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=result["error"],
        )


# Maximum file upload size: 25 MB
MAX_UPLOAD_SIZE = 25 * 1024 * 1024

# Allowed file header signatures (magic bytes)
IMAGE_MAGIC_BYTES = [
    b"\xff\xd8\xff",               # JPEG
    b"\x89PNG\r\n\x1a\n",          # PNG
    b"RIFF",                       # WEBP (starts with RIFF....WEBP)
]

DOCUMENT_MAGIC_BYTES = [
    b"%PDF-",                      # PDF
    b"\x89PNG\r\n\x1a\n",          # PNG
    b"\xff\xd8\xff",               # JPEG
]


def _validate_file(file_bytes: bytes, filename: str, allowed_magic: list, file_type_label: str):
    """Validate non-empty content, max size constraint, and genuine magic byte signatures."""
    if not file_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file received.")

    if len(file_bytes) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum permissible size of {MAX_UPLOAD_SIZE // (1024 * 1024)}MB.",
        )

    # Magic byte check
    is_valid_header = any(file_bytes.startswith(sig) for sig in allowed_magic)
    if not is_valid_header:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Invalid {file_type_label} signature. The uploaded file does not match an authentic image/document format.",
        )


# ─── Routes ──────────────────────────────────────────────────────

@router.post("/text", summary="Analyse text for misinformation")
def analyze_text(request: TextAnalysisRequest):
    result = run_text_analysis(request.text)
    _raise_if_error(result)
    return result


@router.post("/image", summary="Analyse image for deepfakes / manipulation")
async def analyze_image(file: UploadFile = File(...)):
    image_bytes = await file.read()
    _validate_file(image_bytes, file.filename or "upload.jpg", IMAGE_MAGIC_BYTES, "image")

    uploaded = _FileAdapter(file.filename or "upload.jpg", image_bytes)
    result = run_image_analysis(uploaded)
    _raise_if_error(result)
    return result


@router.post("/document", summary="Verify a document for forgery")
async def analyze_document(file: UploadFile = File(...)):
    file_bytes = await file.read()
    _validate_file(file_bytes, file.filename or "upload.pdf", DOCUMENT_MAGIC_BYTES, "document")

    uploaded = _FileAdapter(file.filename or "upload.pdf", file_bytes)
    result = run_document_verification(uploaded)
    _raise_if_error(result)
    return result



@router.get("/{analysis_id}/evidence", summary="Get evidence items for an analysis")
def get_analysis_evidence(analysis_id: str):
    evidence = get_evidence_for_analysis(analysis_id)
    return {
        "analysis_id": analysis_id,
        "evidence": evidence,
    }


@router.post(
    "/feedback",
    status_code=status.HTTP_201_CREATED,
    summary="Submit correctness feedback on an analysis",
)
def submit_feedback(request: FeedbackRequest):
    save_feedback(
        analysis_id=request.analysis_id,
        is_correct=request.is_correct,
        user_note=request.user_note or "",
    )
    return {"message": "Feedback submitted successfully"}