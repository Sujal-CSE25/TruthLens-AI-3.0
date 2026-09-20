"""
TruthLens Border Intelligence — Audit Trail API Routes
FastAPI router for SHA-256 hash chain audit endpoints.

SIH 2026 · PS 26188 · PROTOTYPE — NOT FOR OPERATIONAL USE
"""
from fastapi import APIRouter, HTTPException
from passport.audit_trail import verify_audit_chain
from passport.blockchain_anchor import (
    get_blockchain_status,
    create_blockchain_anchor,
    verify_blockchain_anchor,
)
from database import db

router = APIRouter(prefix="/api/v1/audit", tags=["audit"])
legacy_router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("/chain/verify")
async def verify_chain():
    """
    Verify the integrity of the entire audit hash chain.
    Returns chain_valid, total_events, and details of any breach.
    """
    result = verify_audit_chain()
    return result


@router.get("/events")
async def list_audit_events(limit: int = 100):
    """List recent audit events (all screenings)."""
    events = db.list_audit_events(limit=limit)
    return {"events": events, "count": len(events)}


@router.get("/events/{screening_id}")
async def get_screening_audit_trail(screening_id: str):
    """Get all audit events for a specific screening."""
    events = db.list_audit_events(screening_id=screening_id, limit=100)
    if not events:
        raise HTTPException(
            status_code=404,
            detail=f"No audit events found for screening: {screening_id}"
        )
    return {
        "screening_id": screening_id,
        "events":       events,
        "count":        len(events),
    }


# ─── Blockchain Integrity Anchors (PS 26188) ───────────────────

@router.get("/blockchain/status")
@legacy_router.get("/blockchain/status")
async def blockchain_status():
    """Get latest blockchain integrity anchor and audit chain status."""
    return get_blockchain_status()


@router.post("/blockchain/anchor")
@legacy_router.post("/blockchain/anchor")
async def make_blockchain_anchor():
    """Create a new Merkle Root anchor over all current audit events."""
    return create_blockchain_anchor()


@router.get("/blockchain/verify")
@legacy_router.get("/blockchain/verify")
async def check_blockchain_anchor(anchor_id: str = None):
    """Independently recompute Merkle Root and verify anchor integrity."""
    return verify_blockchain_anchor(anchor_id=anchor_id)
