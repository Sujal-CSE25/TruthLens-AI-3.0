import json
import logging
import traceback
from google import genai
from google.genai import types
from utils.config import GEMINI_API_KEY, GEMINI_MODEL

_client = None
logger = logging.getLogger("truthlens.gemini")

# Standard Google Gemini models in order of preference
CANDIDATE_MODELS = [
    GEMINI_MODEL,
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-2.5-flash",
]
# Remove duplicates while preserving order
MODELS_TO_TRY = list(dict.fromkeys(m for m in CANDIDATE_MODELS if m))


def get_client() -> genai.Client:
    """Return a cached Gemini client instance."""
    global _client
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not set in environment.")
    if _client is None:
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


def call_gemini(prompt: str, image_bytes: bytes = None, mime_type: str = "image/jpeg") -> str:
    """
    Send a prompt (optionally + image) to Gemini and return raw text response.
    Tries configured model, then falls back to gemini-2.0-flash / gemini-1.5-flash.
    """
    client = get_client()
    contents = []
    if image_bytes:
        contents.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type))
    contents.append(prompt)

    last_error = None
    for model_name in MODELS_TO_TRY:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=contents,
            )
            return (response.text or "").strip()
        except Exception as e:
            last_error = e
            print(f"[TruthLens Gemini API Error] Model '{model_name}' failed: {e}")
            continue

    if last_error:
        print(f"[TruthLens Gemini API Error] All candidate models failed. Last error: {last_error}")
        raise last_error

    return ""


def call_gemini_json(prompt: str, image_bytes: bytes = None, mime_type: str = "image/jpeg") -> dict:
    """
    Call Gemini and parse a JSON response with automatic model fallback.
    """
    client = get_client()
    contents = []
    if image_bytes:
        contents.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type))
    contents.append(prompt)

    last_error = None
    for model_name in MODELS_TO_TRY:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.3,
                ),
            )
            raw = (response.text or "").strip()

            # Defensive fence-stripping
            if raw.startswith("```"):
                parts = raw.split("```")
                raw = parts[1] if len(parts) > 1 else raw
                if raw.startswith("json"):
                    raw = raw[4:]
            raw = raw.strip()

            return json.loads(raw)
        except Exception as e:
            last_error = e
            print(f"[TruthLens Gemini API Error] Model '{model_name}' failed for JSON call: {e}")
            continue

    if last_error:
        print(f"[TruthLens Gemini API Error] All candidate models failed for JSON call: {last_error}")
        raise last_error

    return {}

