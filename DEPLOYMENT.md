# TruthLens AI 3.0 — Deployment Guide (GitHub + Render)

This document outlines the deployment procedure for **TruthLens AI 3.0** (AI-Based Fake Identity & Document Screening System · PS 26188).

---

## 1. Architecture Overview

TruthLens AI 3.0 consists of:
- **Backend**: FastAPI web service running on Python 3.11 with RapidOCR (ONNX Runtime), PIL, SciPy, and rule-based identity validation.
- **Frontend**: Single Page Application (SPA) built with React 19, TypeScript, and Vite.
- **Integrity & Storage**: Local SQLite database and SHA-256 Merkle audit anchor chain.

---

## 2. Render Cloud Deployment (Step-by-Step)

The repository includes a root [`render.yaml`](./render.yaml) blueprint defining both services.

### Step 1: Push to GitHub
Ensure the project is committed to your GitHub repository. Sensitive files (`.env`, `truthlens.db`, virtual environments, caches) are automatically ignored via [`.gitignore`](./.gitignore).

### Step 2: Create Blueprint Instance on Render
1. Log in to [Render](https://render.com).
2. Click **New +** → **Blueprint**.
3. Connect your TruthLens GitHub repository.
4. Render will detect [`render.yaml`](./render.yaml) and configure two services:
   - **`truthlens-backend`** (Python Web Service)
   - **`truthlens-frontend`** (Static Site)

### Step 3: Two-Phase URL Pairing (CORS & Frontend API Base)
Because Vite environment variables are baked into static JavaScript bundles at **build time**, and FastAPI requires explicit allowed origins:

1. **Deploy Backend**:
   - Allow `truthlens-backend` to complete its initial deployment.
   - Copy your deployed backend URL: `https://truthlens-backend-xxxx.onrender.com`.
   - Verify health at: `https://truthlens-backend-xxxx.onrender.com/health` (should return `{"status": "ok", ...}`).

2. **Configure Frontend**:
   - Navigate to **`truthlens-frontend`** → **Environment**.
   - Set:
     ```env
     VITE_API_BASE_URL=https://truthlens-backend-xxxx.onrender.com
     ```
   - Trigger a **Manual Deploy** (Clear build cache & deploy) so Vite bakes this URL into the production assets.
   - Copy your deployed frontend URL: `https://truthlens-frontend-xxxx.onrender.com`.

3. **Configure Backend CORS**:
   - Navigate to **`truthlens-backend`** → **Environment**.
   - Set:
     ```env
     CORS_ORIGINS=https://truthlens-frontend-xxxx.onrender.com
     ```
   - Render will automatically restart the backend with the new CORS allowlist.

---

## 3. SQLite Ephemeral Storage Notice

> [!WARNING]
> **Prototype Storage Limitation**:
> TruthLens AI 3.0 currently uses local SQLite (`truthlens.db`) for storing screening logs, audit events, and feedback.
> On Render's free-tier Web Services, the filesystem is **ephemeral**: any new screening records or local state written at runtime will reset when the instance sleeps, restarts, or redeploys.
> For long-term production persistence, attach a **Render Persistent Disk** (`DATABASE_PATH=/var/data/truthlens.db`) or configure an external database (such as PostgreSQL) for operational deployment.

---

## 4. Manual Service Configuration (Alternative to Blueprint)

If you prefer deploying services individually without `render.yaml`:

### Backend Web Service
- **Environment**: `Python`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
- **Health Check Path**: `/health`
- **Environment Variables**:
  - `PYTHON_VERSION`: `3.11.9`
  - `APP_ENV`: `production`
  - `CORS_ORIGINS`: `https://<your-frontend-render-url>`
  - `GEMINI_API_KEY`: *(Optional, for live multimodal reasoning)*

### Frontend Static Site
- **Build Command**: `npm install && npm run build`
- **Publish Directory**: `dist`
- **Root Directory**: `frontend`
- **Rewrite Rules**:
  - Source: `/*`
  - Destination: `/index.html`
- **Environment Variables**:
  - `VITE_API_BASE_URL`: `https://<your-backend-render-url>`

---

## 5. Local Development Setup

To run locally without cloud deployment:

```bash
# 1. Clone repository
git clone https://github.com/<your-username>/TruthLens-AI.git
cd TruthLens-AI

# 2. Set up Python virtual environment
python -m venv .venv
# Windows:
.\.venv\Scripts\activate
# Linux / macOS:
source .venv/bin/activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Install Frontend dependencies
cd frontend
npm install
cd ..

# 5. Launch both services with unified launcher
python start.py
```

- Web Portal: `http://localhost:5173`
- API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`
