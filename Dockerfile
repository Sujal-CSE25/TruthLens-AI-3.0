# ─────────────────────────────────────────────
# TruthLens AI 2.0 — Multi-Stage Production Dockerfile
# ─────────────────────────────────────────────

# Stage 1: Build React Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Python Backend & Final Image
FROM python:3.11-slim

# System dependencies: tesseract for OCR, build tools for scipy/torch wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libtesseract-dev \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy built React frontend assets from Stage 1 into frontend/dist
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Create writable directory for the SQLite database
RUN mkdir -p /app/data
ENV DATABASE_PATH=/app/data/truthlens.db

EXPOSE 8000

HEALTHCHECK CMD curl --fail http://localhost:8000/health || exit 1


CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

