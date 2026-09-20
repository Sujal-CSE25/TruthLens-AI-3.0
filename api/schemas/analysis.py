from typing import Optional
from pydantic import BaseModel, Field


# ─── Request Schemas ────────────────────────────────────────────

class TextAnalysisRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=15,
        max_length=25000,
        description="Text content to analyze (15 to 25,000 characters)"
    )


class FeedbackRequest(BaseModel):
    """
    Feedback on an analysis result.
    `is_correct` = True means the user agrees with the verdict.
    """
    analysis_id: str = Field(..., max_length=100)
    is_correct: bool
    user_note: Optional[str] = Field(None, max_length=1000)



# ─── Response Schemas ───────────────────────────────────────────

class AnalysisHistoryItem(BaseModel):
    analysis_id: str
    type: str                        # 'text' | 'image' | 'document'
    verdict: Optional[str] = None
    fake_score: Optional[float] = None
    confidence: Optional[float] = None
    created_at: str