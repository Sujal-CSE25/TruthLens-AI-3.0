from fastapi import APIRouter

from database.db import get_analyses_stats, get_daily_counts
from analytics.continuous_learning import (
    compute_retraining_readiness,
    get_model_versions,
    suggest_threshold_adjustment,
    ensure_baseline_version,
)


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


@router.get("/stats")
def get_stats():
    return get_analyses_stats()


@router.get("/daily")
def get_daily_analytics(days: int = 30):
    return get_daily_counts(days)


@router.get("/learning")
def get_continuous_learning():
    ensure_baseline_version()
    readiness = compute_retraining_readiness(target_samples=100)
    versions = get_model_versions()
    recs = suggest_threshold_adjustment()
    return {
        "readiness": readiness,
        "versions": versions,
        "recommendations": recs,
    }
