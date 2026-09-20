"""
TruthLens Border Intelligence — FastAPI Application
SIH 2026 · PS 26188 · PROTOTYPE — NOT FOR OPERATIONAL USE
Run with: uvicorn api.main:app --reload --port 8000
"""
import traceback
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.routes.analysis import router as analysis_router
from api.routes.analytics import router as analytics_router
from api.routes.history import router as history_router
from api.routes.screening import router as screening_router
from api.routes.audit import router as audit_router, legacy_router as audit_legacy_router
from database.db import init_database

try:
    init_database()
except Exception:
    pass

# ─── App Definition ──────────────────────────────────────────────


app = FastAPI(
    title="TruthLens Border Intelligence",
    version="2.0.0",
    description=(
        "AI-Based Fake Identity & Document Screening System — PS 26188. "
        "SIH 2026 PROTOTYPE — NOT FOR OPERATIONAL USE. "
        "Passport OCR • MRZ Validation • Forensic Tamper Detection • "
        "Face Verification • Evidence Fusion • Explainable Risk • Audit Chain."
    ),
    contact={
        "name": "TruthLens Border Intelligence",
        "url": "https://github.com/truthlens-ai",
    },
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─── CORS & Security Middleware ──────────────────────────────────
import time
from collections import defaultdict

# In-memory sliding window rate limiter: max 45 requests/minute per client IP
RATE_LIMIT_MAX_REQUESTS = 45
RATE_LIMIT_WINDOW_SECONDS = 60
_request_history = defaultdict(list)

@app.middleware("http")
async def security_and_rate_limit_middleware(request: Request, call_next):
    # 1. Rate Limiting for Analysis Endpoints
    path = request.url.path
    if path.startswith("/analyze/"):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        # Clean timestamps older than window
        _request_history[client_ip] = [t for t in _request_history[client_ip] if now - t < RATE_LIMIT_WINDOW_SECONDS]
        if len(_request_history[client_ip]) >= RATE_LIMIT_MAX_REQUESTS:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too Many Requests",
                    "detail": "Rate limit exceeded. Please wait a moment before running more analyses.",
                },
            )
        _request_history[client_ip].append(now)

    # 2. Process Request
    response = await call_next(request)

    # 3. Inject OWASP Defensive Security Headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response


# ─── CORS Middleware ─────────────────────────────────────────────
import os

app_env = os.getenv("APP_ENV", "development").lower()
cors_origins_env = os.getenv("CORS_ORIGINS", "").strip()

# Explicit allowed origins list
allowed_origins = []

# Include localhost origins only in development mode
if app_env != "production":
    allowed_origins.extend([
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ])

# In production (and development), add explicit origins provided via CORS_ORIGINS
if cors_origins_env:
    for origin in cors_origins_env.split(","):
        cleaned = origin.strip().rstrip("/")
        if cleaned and cleaned not in allowed_origins:
            allowed_origins.append(cleaned)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




# ─── Global Error Handler ────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all: return a structured JSON error instead of a 500 HTML page."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "path": str(request.url),
        },
    )

# ─── Routers ─────────────────────────────────────────────────────

app.include_router(analysis_router)
app.include_router(analytics_router)
app.include_router(history_router)
# PS 26188 — Border Intelligence routers
app.include_router(screening_router)
app.include_router(audit_router)
app.include_router(audit_legacy_router)

# ─── Health Check ────────────────────────────────────────────────

@app.get("/health", tags=["Health"], summary="API health check")
def health_check():
    return {
        "status": "ok",
        "service": "TruthLens Border Intelligence",
        "version": "2.0.0",
        "prototype": True,
        "notice": "SIH 2026 PROTOTYPE — NOT FOR OPERATIONAL USE",
    }

# ─── Static Frontend (React SPA) ─────────────────────────────────
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

DIST_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "dist")

if os.path.exists(DIST_DIR):
    assets_dir = os.path.join(DIST_DIR, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/", include_in_schema=False)
    async def serve_root():
        index_file = os.path.join(DIST_DIR, "index.html")
        return FileResponse(index_file)

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_react_app(full_path: str):
        file_path = os.path.join(DIST_DIR, full_path)
        if full_path and os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        index_file = os.path.join(DIST_DIR, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return JSONResponse(status_code=404, content={"detail": "Not found"})