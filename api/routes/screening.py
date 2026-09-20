"""
TruthLens Border Intelligence — Passport Screening API Routes
FastAPI router for PS 26188 passport screening endpoints.

SIH 2026 · PS 26188 · PROTOTYPE — NOT FOR OPERATIONAL USE
"""
import uuid
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional

from passport.screening_pipeline import run_passport_screening
from passport.demo_cases import build_demo_image, build_demo_probe_image, get_demo_case_list, DEMO_CASES
from database import db

router = APIRouter(prefix="/api/v1/screening", tags=["screening"])


# ─── Health / Info ────────────────────────────────────────────

@router.get("/info")
async def screening_info():
    """API metadata for PS 26188 screening module."""
    return {
        "module":    "Passport Screening — PS 26188",
        "prototype": True,
        "notice":    "SIH 2026 PROTOTYPE — NOT FOR OPERATIONAL USE",
        "capabilities": [
            "passport_ocr",
            "mrz_validation",
            "document_forensics",
            "face_verification",
            "evidence_fusion",
            "risk_assessment",
            "audit_trail",
            "identity_intelligence",
        ],
    }


# ─── Live Screening ───────────────────────────────────────────

@router.post("/passport")
async def screen_passport(
    document: UploadFile = File(..., description="Passport image (JPEG/PNG/PDF)"),
    probe: Optional[UploadFile] = File(None, description="Optional live photo for face comparison"),
    actor: str = Form("officer"),
):
    """
    Run full PS 26188 passport screening pipeline.
    
    - Accepts passport image (required) and optional probe/live photo
    - Runs: OCR → MRZ → Validation → Forensics → Face → Identity → Registry → Risk
    - Returns complete result with evidence chain
    """
    # Validate file type
    allowed_types = {"image/jpeg", "image/png", "image/tiff", "application/pdf"}
    if document.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {document.content_type}. Allowed: JPEG, PNG, TIFF, PDF"
        )

    doc_bytes   = await document.read()
    probe_bytes = await probe.read() if probe else None

    if len(doc_bytes) < 1000:
        raise HTTPException(status_code=400, detail="Document image is too small or empty")

    result = run_passport_screening(
        document_image_bytes=doc_bytes,
        probe_image_bytes=probe_bytes,
        actor=actor,
        demo_case=None,
    )

    return JSONResponse(content=result)


# ─── Demo Cases ───────────────────────────────────────────────

@router.get("/demo/cases")
async def list_demo_cases():
    """List all available demo cases."""
    return {
        "cases": get_demo_case_list(),
        "notice": "SIH 2026 PROTOTYPE — All demo data is SYNTHETIC",
    }


@router.post("/demo/run/{case_id}")
async def run_demo_case(case_id: str, actor: str = "demo_system"):
    """
    Run a demo case through the REAL screening pipeline.
    
    The demo pipeline generates a synthetic passport image and runs
    the full screening — no hardcoded verdicts.
    """
    if case_id not in DEMO_CASES:
        raise HTTPException(
            status_code=404,
            detail=f"Demo case '{case_id}' not found. Available: {list(DEMO_CASES.keys())}"
        )

    doc_bytes = build_demo_image(case_id)
    probe_bytes = build_demo_probe_image(case_id)
    result = run_passport_screening(
        document_image_bytes=doc_bytes,
        probe_image_bytes=probe_bytes,
        actor=actor,
        demo_case=case_id,
    )

    # Attach demo metadata
    case_meta = DEMO_CASES[case_id]
    result["demo_metadata"] = {
        "case_id":       case_id,
        "title":         case_meta["title"],
        "description":   case_meta["description"],
        "expected_risk": case_meta["expected_risk"],
        "actual_risk":   result.get("risk_level"),
        "pipeline_match": result.get("risk_level") == case_meta["expected_risk"],
        "notice": "Expected risk is for demonstration only — actual result comes from the real pipeline",
    }

    return JSONResponse(content=result)


# ─── Screening History ────────────────────────────────────────

@router.get("/history")
async def get_screening_history(
    limit: int = 20,
    offset: int = 0,
    risk_level: Optional[str] = None,
):
    """Retrieve recent screening results."""
    valid_risk = {None, "CLEAR", "MANUAL_REVIEW", "HIGH_RISK"}
    if risk_level not in valid_risk:
        raise HTTPException(status_code=400, detail=f"Invalid risk_level filter: {risk_level}")

    rows = db.list_screenings(limit=limit, offset=offset, risk_level=risk_level)
    return {"screenings": rows, "count": len(rows), "offset": offset}


@router.get("/result/{screening_id}")
async def get_screening_result(screening_id: str):
    """Retrieve a specific screening result by ID."""
    row = db.get_screening(screening_id)
    if not row:
        raise HTTPException(status_code=404, detail=f"Screening not found: {screening_id}")
    return row
