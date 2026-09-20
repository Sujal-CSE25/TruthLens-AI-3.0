"""
TruthLens AI 2.0 — Utility Helpers
"""
import re
import time
import hashlib
from datetime import datetime
from utils.config import THRESHOLD_HIGH_RISK, THRESHOLD_MEDIUM_RISK


def slugify(text: str) -> str:
    """Return a filesystem-safe slug from text."""
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[\s_-]+", "-", text).strip("-")


def truncate(text: str, max_chars: int = 300) -> str:
    """Truncate text to max_chars with ellipsis."""
    return text[:max_chars] + "…" if len(text) > max_chars else text


def score_label(score: int) -> str:
    """Convert 0–100 score to risk label."""
    if score >= 70:
        return "HIGH"
    if score >= 40:
        return "MEDIUM"
    return "LOW"


def clamp(val: float, lo: float = 0, hi: float = 100) -> float:
    """Clamp a value between lo and hi."""
    return max(lo, min(hi, val))


def ts_now() -> str:
    """Return UTC timestamp string."""
    return datetime.utcnow().isoformat()


def hash_text(text: str) -> str:
    """Return MD5 hash of text (for deduplication)."""
    return hashlib.md5(text.encode()).hexdigest()


def format_bytes(n: int) -> str:
    """Format byte count as human-readable string."""
    for unit in ["B", "KB", "MB", "GB"]:
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def get_risk_label(score: int) -> str:
    """Convert a numeric score (0-100) to a human-readable risk label."""
    if score >= THRESHOLD_HIGH_RISK:
        return "HIGH RISK"
    elif score >= THRESHOLD_MEDIUM_RISK:
        return "MEDIUM RISK"
    return "LOW RISK"


def get_risk_color(score: int) -> str:
    """Return a hex color based on risk score."""
    if score >= THRESHOLD_HIGH_RISK:
        return "#FF4560"
    elif score >= THRESHOLD_MEDIUM_RISK:
        return "#FFB800"
    return "#00E5A0"


def get_verdict_emoji(verdict: str) -> str:
    """Map a verdict string to a simple ASCII glyph (kept emoji-free for enterprise UI)."""
    mapping = {
        "LIKELY REAL": "✓", "UNCERTAIN": "?", "LIKELY FAKE": "✕", "SATIRE": "~",
        "LIKELY AUTHENTIC": "✓", "POSSIBLY MANIPULATED": "?",
        "LIKELY AI-GENERATED": "AI", "DEEPFAKE SUSPECTED": "✕",
        "LIKELY MANIPULATED": "✕", "LIKELY FORGED": "✕",
        "SUSPICIOUS": "?", "INCONCLUSIVE": "?",
    }
    return mapping.get((verdict or "").upper(), "?")


def truncate_text(text: str, max_chars: int = 500) -> str:
    """Truncate text for display with ellipsis."""
    return text[:max_chars] + "..." if len(text) > max_chars else text


def image_bytes_to_base64(image_bytes: bytes) -> str:
    """Convert image bytes to base64 string for embedding."""
    import base64
    return base64.b64encode(image_bytes).decode("utf-8")
