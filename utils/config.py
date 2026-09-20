"""
TruthLens Border Intelligence — Configuration
SIH 2026 · PS 26188 — AI-Based Fake Identity & Document Screening
"""
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_CSE_ID  = os.getenv("GOOGLE_CSE_ID", "")
HF_TOKEN       = os.getenv("HF_TOKEN", "")

# ─── App Meta ────────────────────────────────────────────────
APP_NAME           = "TruthLens Border Intelligence"
APP_VERSION        = "2.0.0"
APP_TAGLINE        = "AI-Powered Identity Screening & Document Forensics"
APP_PS             = "PS 26188"
APP_PROTOTYPE_NOTICE = "SIH 2026 PROTOTYPE — NOT FOR OPERATIONAL USE"

# ─── Gemini ──────────────────────────────────────────────────
GEMINI_MODEL       = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")



# ─── Thresholds ──────────────────────────────────────────────
THRESHOLD_HIGH_RISK   = 70
THRESHOLD_MEDIUM_RISK = 40

# ─── File Support ────────────────────────────────────────────
SUPPORTED_IMAGE_TYPES = ["jpg", "jpeg", "png", "webp"]
SUPPORTED_DOC_TYPES   = ["pdf", "png", "jpg", "jpeg"]

# ─── Database ────────────────────────────────────────────────
# On serverless platforms (Vercel, AWS Lambda), the deployment directory is strictly read-only.
# The only writable location is /tmp.
if os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME") or os.getenv("SERVERLESS"):
    DATABASE_PATH = os.getenv("DATABASE_PATH", "/tmp/truthlens.db")
else:
    DATABASE_PATH = os.getenv("DATABASE_PATH", "truthlens.db")

# ─── Forensics ───────────────────────────────────────────────
ELA_QUALITY   = 90      # JPEG quality for ELA
ELA_SCALE     = 20      # Amplification scale for ELA diff

# ─── MRZ / Passport ──────────────────────────────────────────
MRZ_MIN_CONFIDENCE      = 0.6    # Below this → MRZ result marked UNCERTAIN
PASSPORT_NUMBER_REGEX   = r"^[A-Z][0-9]{7}$"  # Indian passport format

# ─── Face Verification ───────────────────────────────────────
# Thresholds for cosine similarity (DeepFace embeddings)
FACE_MATCH_THRESHOLD    = 0.72   # ≥ this → MATCH
FACE_REVIEW_THRESHOLD   = 0.50   # ≥ this, < MATCH → REVIEW
# Below REVIEW_THRESHOLD → NO_MATCH
FACE_MIN_SIZE_PX        = 80     # Minimum face side length in pixels

# ─── Risk Engine ─────────────────────────────────────────────
# Evidence module weights — these are RELATIVE weights, not absolute scores.
# Normalised internally so total always sums to 1.0.
# Increase a weight to give that module more influence on final risk.
RISK_WEIGHTS = {
    "mrz_validation":        0.25,  # MRZ check-digit and parse failures are strong signals
    "document_validation":   0.20,  # Deterministic field checks
    "forensic_tamper":       0.20,  # ELA + noise + compression composite
    "face_verification":     0.20,  # Biometric match result
    "expiry_check":          0.10,  # Expired document
    "identity_consistency":  0.05,  # Cross-case duplicate / conflict signals
}
# Risk state thresholds (applied to 0–100 final risk score)
RISK_THRESHOLD_HIGH    = 65   # >= this → HIGH_RISK
RISK_THRESHOLD_REVIEW  = 35   # >= this, < HIGH → MANUAL_REVIEW
# < REVIEW_THRESHOLD → CLEAR

