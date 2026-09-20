"""
TruthLens AI 2.0 — Analysis History Route
GET /api/v1/history  → paginated list of past analysis records
"""
from typing import Optional
from fastapi import APIRouter, Query
from database.db import get_conn

router = APIRouter(
    prefix="/history",
    tags=["History"],
)


@router.get("", summary="Fetch paginated analysis history")
def get_history(
    limit: int = Query(default=50, ge=1, le=200, description="Max records to return"),
    offset: int = Query(default=0, ge=0, description="Pagination offset"),
    type: Optional[str] = Query(default=None, description="Filter by type: text | image | document"),
):
    """
    Return recent analyses ordered newest-first.
    Optionally filter by content type.
    """
    if type:
        sql = """
            SELECT analysis_id, type, verdict, fake_score, confidence, created_at
            FROM analyses
            WHERE type = ?
            ORDER BY id DESC
            LIMIT ? OFFSET ?
        """
        params = (type, limit, offset)
    else:
        sql = """
            SELECT analysis_id, type, verdict, fake_score, confidence, created_at
            FROM analyses
            ORDER BY id DESC
            LIMIT ? OFFSET ?
        """
        params = (limit, offset)

    with get_conn() as conn:
        rows = conn.execute(sql, params).fetchall()
        if type:
            total = conn.execute(
                "SELECT COUNT(*) FROM analyses WHERE type=?", (type,)
            ).fetchone()[0]
        else:
            total = conn.execute(
                "SELECT COUNT(*) FROM analyses"
            ).fetchone()[0]

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": [dict(r) for r in rows],
    }
