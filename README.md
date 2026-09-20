# TruthLens AI 2.0 — Institutional Verification & Forensic Analysis Platform

> **Smart India Hackathon (SIH 2026) · Problem Statement PS 26059**  

> AI-powered multimodal misinformation, deepfake, and document-forgery verification platform powered by a **6-Agent reasoning pipeline**, **RAG evidence grounding**, **multimodal forensic signals**, and an **institutional government-grade React UI**.

---

## 🏛️ Key Highlights & Architecture

TruthLens AI 2.0 is built as a production-grade institutional forensic tool rather than a generic prompt-based LLM wrapper. It employs a defense-in-depth verification pipeline:

```
[ User Input: Text / Image / Document / PDF ]
                     │
                     ▼
             [ FastAPI Gateway ] (Port 8000)
                     │
     ┌───────────────┴───────────────┐
     ▼                               ▼
[ 6-Agent AI Pipeline ]     [ Forensic Analysis Engines ]
1. Claim Extractor          • Image: Error Level Analysis (ELA)
2. Evidence Finder (RAG)    • Image: EXIF Metadata Audit & Photoshop Detection
3. Fact Checker             • Image: Gaussian Sensor Noise Consistency
4. Risk Assessor            • Text: Emotional Valence, Clickbait & Urgency
5. Explainability Agent     • Text: Linguistic Propagandistic Lexicon
6. Final Judge              • Document: OCR Text Extraction & Schema Checklists
     │                               │
     └───────────────┬───────────────┘
                     ▼
          [ Calibrated Verdict ]
     Trust Score · Risk Level · 5-Axis Radar · Reasoning Chain
                     │
                     ▼
          [ Continuous Learning ]
     Operator Feedback Loop (Accuracy Tracking & Model Recalibration)
```

---

## 🤖 The 6-Agent Verification Pipeline

1. **Claim Extractor Agent**: Parses raw text and isolates atomic, verifiable assertions, statistics, entities, and temporal claims.
2. **Evidence Finder Agent (RAG)**: Executes retrieval-augmented generation over Wikipedia API and curated news archives to find ground-truth passages.
3. **Fact Checker Agent**: Cross-references claims against evidence to produce per-claim verdicts (`SUPPORTED`, `CONTRADICTED`, `PARTIALLY_TRUE`, `UNVERIFIED`).
4. **Risk Assessor Agent**: Calibrates fake probability and distrust scores by synthesizing linguistic red flags with fact-checking contradictions.
5. **Explainability Agent**: Generates a transparent, step-by-step audit chain answering *"Why did TruthLens reach this verdict?"* with no black-box outputs.
6. **Final Judge Agent**: Synthesizes upstream agent outputs to issue the institutional verdict (`LIKELY REAL`, `LIKELY MISLEADING`, `HIGH RISK FAKE`, `SUSPICIOUS DOCUMENT`).

---

## 🔬 Multimodal Forensic Signals

- **Image & Deepfake Forensics**:
  - **Error Level Analysis (ELA)**: Detects compression differentials and resaved artifacts indicating spliced or digitally altered image areas.
  - **EXIF Metadata Inspector**: Audits camera serials, timestamps, GPS geolocation, and flags editing software signatures (Photoshop, GIMP).
  - **Noise Pattern Consistency**: Measures high-frequency sensor noise variance between subject and background.
- **Text & Linguistic Forensics**:
  - Clickbait structural pattern recognition.
  - Urgency and panic detection (`"share before deleted"`).
  - Polarization and conspiratorial propaganda lexicon matcher.
  - Readability indices (Flesch-Kincaid, Gunning Fog).
- **Document & Credential Forensics**:
  - Tesseract OCR text extraction with one-click clipboard copying.
  - Template Field Completeness checklist (e.g., Certificate ID, Issue Date, Authority Name).
  - Visual forgery flags (font mismatches, date anomalies, boundary tampering).

---

## 💻 Technology Stack

- **Frontend**: React 19, TypeScript, Vite, Pure CSS Institutional Design System (Gov-grade Indian Institutional Theme, Noto Sans typography, SVG Gauge and Radar charts).
- **Backend API**: FastAPI, Uvicorn, Python 3.11, Pydantic v2.
- **AI & Reasoning**: Google Gemini Flash API (`google-genai` SDK) with heuristic and deterministic offline fallbacks.
- **Forensics & Vision**: Pillow (PIL), NumPy, SciPy, pytesseract (OCR), python-multipart.
- **Database**: SQLite with Continuous Learning feedback store (`truthlens.db`).

---

## 🚀 Quick Start & Local Setup

### 1. Prerequisites
- **Python 3.10+**
- **Node.js 18+** and `npm`
- *(Optional)* [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) for local document OCR on Windows.

### 2. Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/Truthlens-AI-2.0-Updated.git
   cd Truthlens-AI-2.0-Updated
   ```

2. **Setup Python Virtual Environment:**
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate

   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Setup React Frontend Dependencies:**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Configure Environment Variables:**
   Copy the example configuration:
   ```bash
   # Windows:
   copy .env.example .env
   # Linux/macOS:
   cp .env.example .env
   ```
   Open `.env` and add your **Google Gemini API Key**:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-2.0-flash
   ```
   *(Note: If no API key is provided, the platform automatically runs its built-in heuristic/linguistic fallback so all UI flows and forensics remain testable).*

---

## 🏃 Running the Application

### Option A: Unified Launcher (Recommended)
Start both the FastAPI backend and React frontend with a single command:
```bash
python start.py
```
- **Web Portal**: [http://localhost:5173](http://localhost:5173)
- **FastAPI Interactive Docs (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **API Health Check**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

### Option B: Run Services Separately

1. **Terminal 1 — FastAPI Backend**:
   ```bash
   python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Terminal 2 — React Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

---

## 🐳 Docker Deployment

TruthLens AI 2.0 includes a multi-stage production Dockerfile that compiles the React application and serves both the API and frontend via FastAPI:

```bash
docker compose up --build
```
The entire containerized application will be available at [http://localhost:8000](http://localhost:8000).

---

## 📁 Repository Structure

```
Truthlens-AI-2.0-Updated/
├── agents/                     # 6-Agent AI reasoning pipeline
│   ├── multi_agent.py          # Orchestrator & agent definitions
│   └── claim_clustering.py     # Embedding clustering for duplicate claims
├── analytics/                  # Continuous learning & model versioning
│   └── continuous_learning.py  # Retraining readiness & calibration logic
├── api/                        # FastAPI REST API layer
│   ├── main.py                 # FastAPI application root & SPA static mount
│   └── routes/                 # analysis, analytics, history endpoints
├── database/                   # SQLite persistence & audit log
├── forensics/                  # Multimodal forensic engines
│   ├── image_forensics.py      # ELA, EXIF audit, noise analysis
│   ├── text_forensics.py       # Linguistic pattern analysis & readability
│   └── document_forensics.py   # OCR extraction & template checklists
├── frontend/                   # Government-Grade React Application
│   ├── src/
│   │   ├── components/         # SVG charts, institutional header, feedback
│   │   ├── pages/              # Detection, Forensics, Dashboard, Analytics, About
│   │   └── services/api.ts     # Type-safe API client
│   └── index.css               # Institutional Indian Government Design System tokens
├── models/                     # High-level analyzers (text, image, document)
├── rag/                        # RAG knowledge retriever & Wikipedia search
├── utils/                      # Config & Gemini API client
├── start.py                    # Unified concurrent launcher (FastAPI + React)
├── Dockerfile                  # Multi-stage production container
└── docker-compose.yml          # Container configuration
```

---

## 🛡️ License & Acknowledgments
Developed for **Smart India Hackathon (SIH 2026)**. Built with government-grade design standards, accessibility principles (WCAG 2.1 AA), and zero black-box explainability.
