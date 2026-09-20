"""
TruthLens AI 2.0 — Unified Launcher
Starts FastAPI (port 8000) and React Vite Frontend (port 5173) together.

Usage:
    python start.py
"""
import subprocess
import sys
import time
import os
import signal
import atexit

ROOT = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(ROOT, "frontend")

api_proc = None
web_proc = None


def _shutdown(signum=None, frame=None):
    """Gracefully stop both child processes on exit."""
    print("\n[TruthLens] Shutting down...")
    for proc in (web_proc, api_proc):
        if proc and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
    print("[TruthLens] Done.")
    sys.exit(0)


atexit.register(_shutdown)
signal.signal(signal.SIGINT,  _shutdown)
signal.signal(signal.SIGTERM, _shutdown)


def main():
    global api_proc, web_proc

    python = sys.executable

    # ── 1. Start FastAPI ─────────────────────────────────────
    print("[TruthLens] Starting FastAPI on http://localhost:8000 ...")
    api_proc = subprocess.Popen(
        [
            python, "-m", "uvicorn",
            "api.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload",
        ],
        cwd=ROOT,
    )

    time.sleep(2)

    if api_proc.poll() is not None:
        print("[TruthLens] ERROR: FastAPI failed to start. Check the output above.")
        sys.exit(1)

    print("[TruthLens] FastAPI is up [OK]")

    # ── 2. Start React Frontend (Vite) ──────────────────────
    print("[TruthLens] Starting React Frontend on http://localhost:5173 ...")
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    web_proc = subprocess.Popen(
        [npm_cmd, "run", "dev"],
        cwd=FRONTEND_DIR,
    )


    print("\n" + "=" * 60)
    print("  TruthLens AI 2.0 is running!")
    print("  Web Portal   : http://localhost:5173")
    print("  FastAPI docs : http://localhost:8000/docs")
    print("  API health   : http://localhost:8000/health")
    print("=" * 60 + "\n")

    print("Press Ctrl+C to stop both services.\n")

    # Wait for React dev server (blocking) — FastAPI runs in background
    web_proc.wait()

    _shutdown()


if __name__ == "__main__":
    main()

