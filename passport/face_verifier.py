"""
TruthLens Border Intelligence — Face Verification Engine
Real face detection + embedding-based similarity verification.

DESIGN PRINCIPLES:
- Uses real face embeddings (DeepFace when available, OpenCV as fallback for detection only)
- When biometric model is unavailable: returns REVIEW/UNAVAILABLE — NEVER fakes a similarity score
- All results include confidence and limitations
- Does NOT claim absolute biometric certainty

RESULT STATES: MATCH | REVIEW | NO_MATCH | UNAVAILABLE

SIH 2026 · PS 26188 · PROTOTYPE — NOT FOR OPERATIONAL USE
"""
import io
import numpy as np
from PIL import Image
from utils.config import FACE_MATCH_THRESHOLD, FACE_REVIEW_THRESHOLD, FACE_MIN_SIZE_PX


# ─── Availability Checks ─────────────────────────────────────

def _opencv_available() -> bool:
    try:
        import cv2
        return True
    except ImportError:
        return False


def _deepface_available() -> bool:
    try:
        import deepface  # noqa
        return True
    except ImportError:
        return False


# ─── Face Detection ───────────────────────────────────────────

def detect_face(image_bytes: bytes) -> dict:
    """
    Detect faces in an image using OpenCV Haar cascade.
    Returns:
      {
        "faces_found": int,
        "face_boxes": [(x, y, w, h), ...],
        "quality_ok": bool,
        "issues": [...],
        "available": bool
      }
    """
    if not _opencv_available():
        return {
            "faces_found": 0,
            "face_boxes": [],
            "quality_ok": False,
            "issues": ["OpenCV not installed — face detection unavailable"],
            "available": False,
        }

    try:
        import cv2

        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img_np = np.array(img)
        gray   = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)

        # Load Haar cascade (bundled with cv2)
        cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

        faces = cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(FACE_MIN_SIZE_PX, FACE_MIN_SIZE_PX),
        )

        face_boxes = []
        issues = []

        if len(faces) == 0:
            issues.append("No face detected — image may not contain a visible face")
        elif len(faces) > 1:
            issues.append(f"{len(faces)} faces detected — expected exactly 1")
            face_boxes = [tuple(int(v) for v in f) for f in faces]
        else:
            face_boxes = [tuple(int(v) for v in faces[0])]
            x, y, w, h = face_boxes[0]
            if w < FACE_MIN_SIZE_PX or h < FACE_MIN_SIZE_PX:
                issues.append(f"Face too small ({w}×{h}px) — quality may be insufficient")

        quality_ok = len(faces) == 1 and not issues

        return {
            "faces_found": len(faces),
            "face_boxes":  face_boxes,
            "quality_ok":  quality_ok,
            "issues":      issues,
            "available":   True,
        }
    except Exception as e:
        return {
            "faces_found": 0,
            "face_boxes": [],
            "quality_ok": False,
            "issues": [f"Face detection error: {str(e)}"],
            "available": True,
        }


# ─── Face Quality Check ───────────────────────────────────────

def check_face_quality(image_bytes: bytes, face_box: tuple = None) -> dict:
    """
    Estimate face image quality for biometric use:
    - Blur (Laplacian variance)
    - Size adequacy
    Returns quality assessment dict.
    """
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        w, h = img.size

        # Crop to face box if provided
        if face_box:
            x, y, fw, fh = face_box
            face_img = img.crop((x, y, x + fw, y + fh))
        else:
            face_img = img

        fw, fh = face_img.size

        # Blur estimation via Laplacian variance
        gray_arr = np.array(face_img.convert("L"), dtype=np.float32)
        # Laplacian kernel
        lap = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]])
        from scipy.signal import convolve2d
        lap_result = convolve2d(gray_arr, lap, mode="same")
        blur_score = float(np.var(lap_result))

        issues = []
        if fw < FACE_MIN_SIZE_PX or fh < FACE_MIN_SIZE_PX:
            issues.append(f"Face region too small ({fw}×{fh}px)")
        if blur_score < 50:
            issues.append(f"Image appears blurry (blur score: {blur_score:.1f})")

        quality_score = min(int(blur_score / 10), 100)

        return {
            "size_px":     (fw, fh),
            "blur_score":  round(blur_score, 1),
            "quality_score": quality_score,
            "quality_ok":  not issues,
            "issues":      issues,
        }
    except ImportError:
        # scipy unavailable — do simple variance check
        try:
            img = Image.open(io.BytesIO(image_bytes)).convert("L")
            arr = np.array(img, dtype=np.float32)
            var = float(np.var(arr))
            return {
                "size_px": img.size,
                "blur_score": round(var, 1),
                "quality_score": min(int(var / 20), 100),
                "quality_ok": var > 100,
                "issues": [] if var > 100 else ["Image may be blurry"],
            }
        except Exception as e:
            return {"size_px": (0, 0), "blur_score": 0, "quality_score": 0,
                    "quality_ok": False, "issues": [str(e)]}
    except Exception as e:
        return {"size_px": (0, 0), "blur_score": 0, "quality_score": 0,
                "quality_ok": False, "issues": [f"Quality check error: {str(e)}"]}


# ─── Face Embedding ───────────────────────────────────────────

def extract_face_embedding(image_bytes: bytes) -> dict:
    """
    Extract a real face embedding using DeepFace.
    Falls back to UNAVAILABLE (not to a fake embedding) if DeepFace is absent.

    Returns:
      {
        "embedding": list[float] | None,
        "model_used": str,
        "available": bool,
        "error": str | None
      }
    """
    if not _deepface_available():
        return {
            "embedding": None,
            "model_used": None,
            "available": False,
            "error": "DeepFace not installed — biometric embedding unavailable",
        }

    try:
        from deepface import DeepFace
        import tempfile, os

        # DeepFace requires a file path or numpy array
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img_np = np.array(img)

        # Use Facenet model (lightweight, well-tested)
        result = DeepFace.represent(
            img_path=img_np,
            model_name="Facenet",
            enforce_detection=False,  # Don't throw if no face — we handle separately
        )

        if result and len(result) > 0:
            embedding = result[0]["embedding"]
            return {
                "embedding": embedding,
                "model_used": "DeepFace/Facenet",
                "available": True,
                "error": None,
            }
        return {
            "embedding": None,
            "model_used": "DeepFace/Facenet",
            "available": True,
            "error": "DeepFace returned empty embedding — no face detected in image",
        }
    except Exception as e:
        return {
            "embedding": None,
            "model_used": "DeepFace/Facenet",
            "available": True,
            "error": f"Embedding extraction failed: {str(e)}",
        }


# ─── Cosine Similarity ────────────────────────────────────────

def _cosine_similarity(a: list, b: list) -> float:
    va = np.array(a, dtype=np.float64)
    vb = np.array(b, dtype=np.float64)
    denom = np.linalg.norm(va) * np.linalg.norm(vb)
    if denom == 0:
        return 0.0
    return float(np.clip(np.dot(va, vb) / denom, -1.0, 1.0))


# ─── Face Comparison ─────────────────────────────────────────

def compare_faces(document_image_bytes: bytes,
                   probe_image_bytes: bytes) -> dict:
    """
    Compare two face images — document photo vs presented person.

    Returns:
      {
        "result": "MATCH" | "REVIEW" | "NO_MATCH" | "UNAVAILABLE",
        "similarity": float | None,
        "threshold_match": float,
        "threshold_review": float,
        "confidence": float,
        "document_detection": {...},
        "probe_detection": {...},
        "document_quality": {...},
        "probe_quality": {...},
        "limitations": str
      }

    CRITICAL: Returns UNAVAILABLE when biometric model is absent.
    NEVER generates a fake similarity score.
    """
    # Step 1: Detect faces in both images
    doc_detection   = detect_face(document_image_bytes)
    probe_detection = detect_face(probe_image_bytes) if probe_image_bytes else None

    limitations = (
        "Face comparison uses deep learning embeddings (DeepFace/Facenet). "
        "Accuracy depends on image quality, lighting, and face angle. "
        "Result is a biometric indicator — not a legal determination. "
        "MATCH result requires corroboration from human officer review."
    )

    # Step 2: Check availability
    if not doc_detection.get("available", False):
        return {
            "result":        "UNAVAILABLE",
            "similarity":    None,
            "threshold_match":  FACE_MATCH_THRESHOLD,
            "threshold_review": FACE_REVIEW_THRESHOLD,
            "confidence":    0.0,
            "document_detection": doc_detection,
            "probe_detection":    probe_detection,
            "document_quality":   {},
            "probe_quality":      {},
            "reason":        "Face detection library (OpenCV) not available",
            "limitations":   limitations,
        }

    # Step 3: Face quality checks
    doc_box   = doc_detection["face_boxes"][0] if doc_detection["face_boxes"] else None
    probe_box = None
    if probe_detection and probe_detection.get("face_boxes"):
        probe_box = probe_detection["face_boxes"][0]

    doc_quality   = check_face_quality(document_image_bytes, doc_box)
    probe_quality = check_face_quality(probe_image_bytes, probe_box) if probe_image_bytes else {}

    # Step 4: Quality gating
    quality_issues = []
    if doc_detection["faces_found"] == 0:
        quality_issues.append("No face detected in document image")
    if probe_image_bytes and probe_detection and probe_detection["faces_found"] == 0:
        quality_issues.append("No face detected in probe image")
    if doc_detection["faces_found"] > 1:
        quality_issues.append("Multiple faces in document image")

    if quality_issues:
        return {
            "result":        "REVIEW",
            "similarity":    None,
            "threshold_match":  FACE_MATCH_THRESHOLD,
            "threshold_review": FACE_REVIEW_THRESHOLD,
            "confidence":    0.0,
            "document_detection": doc_detection,
            "probe_detection":    probe_detection,
            "document_quality":   doc_quality,
            "probe_quality":      probe_quality,
            "reason":        "; ".join(quality_issues),
            "limitations":   limitations,
        }

    # Step 5: If no probe image, can only check document face quality
    if not probe_image_bytes:
        return {
            "result":        "REVIEW",
            "similarity":    None,
            "threshold_match":  FACE_MATCH_THRESHOLD,
            "threshold_review": FACE_REVIEW_THRESHOLD,
            "confidence":    0.3,
            "document_detection": doc_detection,
            "probe_detection":    None,
            "document_quality":   doc_quality,
            "probe_quality":      {},
            "reason":        "No probe image provided — face comparison not possible",
            "limitations":   limitations,
        }

    # Step 6: Extract real embeddings
    doc_emb_result   = extract_face_embedding(document_image_bytes)
    probe_emb_result = extract_face_embedding(probe_image_bytes)

    # Step 7: Handle unavailable model
    if not doc_emb_result.get("available", False):
        return {
            "result":        "UNAVAILABLE",
            "similarity":    None,
            "threshold_match":  FACE_MATCH_THRESHOLD,
            "threshold_review": FACE_REVIEW_THRESHOLD,
            "confidence":    0.0,
            "document_detection": doc_detection,
            "probe_detection":    probe_detection,
            "document_quality":   doc_quality,
            "probe_quality":      probe_quality,
            "reason":        doc_emb_result.get("error", "Biometric model unavailable"),
            "limitations":   limitations,
        }

    doc_emb   = doc_emb_result.get("embedding")
    probe_emb = probe_emb_result.get("embedding")

    # Step 8: Handle embedding failures
    if doc_emb is None or probe_emb is None:
        errors = []
        if doc_emb is None:
            errors.append(f"Document embedding: {doc_emb_result.get('error', 'failed')}")
        if probe_emb is None:
            errors.append(f"Probe embedding: {probe_emb_result.get('error', 'failed')}")
        return {
            "result":        "REVIEW",
            "similarity":    None,
            "threshold_match":  FACE_MATCH_THRESHOLD,
            "threshold_review": FACE_REVIEW_THRESHOLD,
            "confidence":    0.2,
            "document_detection": doc_detection,
            "probe_detection":    probe_detection,
            "document_quality":   doc_quality,
            "probe_quality":      probe_quality,
            "reason":        "Embedding extraction failed — " + "; ".join(errors),
            "limitations":   limitations,
        }

    # Step 9: Compute cosine similarity
    similarity = _cosine_similarity(doc_emb, probe_emb)

    # Confidence is modulated by face quality
    doc_q  = doc_quality.get("quality_score", 50) / 100
    prob_q = probe_quality.get("quality_score", 50) / 100
    confidence = round((doc_q + prob_q) / 2, 2)

    # Step 10: Threshold-based verdict
    if similarity >= FACE_MATCH_THRESHOLD:
        result = "MATCH"
        reason = f"Similarity {similarity:.3f} ≥ threshold {FACE_MATCH_THRESHOLD} — faces are consistent"
    elif similarity >= FACE_REVIEW_THRESHOLD:
        result = "REVIEW"
        reason = (f"Similarity {similarity:.3f} is between review ({FACE_REVIEW_THRESHOLD}) "
                  f"and match ({FACE_MATCH_THRESHOLD}) thresholds — manual comparison required")
    else:
        result = "NO_MATCH"
        reason = (f"Similarity {similarity:.3f} < review threshold {FACE_REVIEW_THRESHOLD} — "
                  "faces appear to be different persons")

    return {
        "result":        result,
        "similarity":    round(similarity, 4),
        "threshold_match":  FACE_MATCH_THRESHOLD,
        "threshold_review": FACE_REVIEW_THRESHOLD,
        "confidence":    confidence,
        "model_used":    doc_emb_result.get("model_used", "unknown"),
        "document_detection": doc_detection,
        "probe_detection":    probe_detection,
        "document_quality":   doc_quality,
        "probe_quality":      probe_quality,
        "reason":        reason,
        "limitations":   limitations,
    }
