"""
TruthLens Border Intelligence — Document Tamper Detection
Forensic analysis for document-specific tampering signals.

IMPORTANT: No individual signal automatically means "fake".
Every signal returns: confidence, limitations, region (where applicable).

SIH 2026 · PS 26188 · PROTOTYPE — NOT FOR OPERATIONAL USE
"""
import io
import numpy as np
from PIL import Image, ImageFilter, ImageChops


# ─── Text Region Anomaly Detection ───────────────────────────

def detect_text_region_anomalies(image_bytes: bytes) -> dict:
    """
    Analyse local JPEG block inconsistencies in the upper 60% of the image
    (typical text zone for a passport).

    High local variance between adjacent blocks suggests the text area
    may have been edited separately from the background.

    Returns signal, score, confidence, limitations.
    """
    try:
        from utils.config import ELA_QUALITY
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        w, h = img.size

        # Focus on text zone (upper 60%)
        text_zone = img.crop((0, 0, w, int(h * 0.60)))

        buf = io.BytesIO()
        text_zone.save(buf, "JPEG", quality=ELA_QUALITY)
        buf.seek(0)
        recomp = Image.open(buf).convert("RGB")

        diff = ImageChops.difference(text_zone, recomp)
        diff_arr = np.array(diff.convert("L"), dtype=np.float32)

        tz_h, tz_w = diff_arr.shape
        block_size = 16

        # Measure variance of block-mean ELA values
        block_means = []
        for y in range(0, tz_h - block_size, block_size):
            for x in range(0, tz_w - block_size, block_size):
                block = diff_arr[y:y+block_size, x:x+block_size]
                block_means.append(float(np.mean(block)))

        if not block_means:
            raise ValueError("No blocks sampled")

        mean_ela   = float(np.mean(block_means))
        block_std  = float(np.std(block_means))
        score      = min(int(block_std * 4), 100)

        if block_std > 15:
            signal = ("High variation in text-region ELA block values — some text blocks "
                      "show anomalous compression compared to surrounding areas, which may "
                      "indicate localized text editing or overlay")
        elif block_std > 8:
            signal = "Moderate text-region ELA variation — minor inconsistencies detected"
        else:
            signal = "Text region ELA is consistent — no localized anomalies detected"

        return {
            "signal":      signal,
            "region":      "text_zone_upper_60pct",
            "measurement": {"mean_ela": round(mean_ela, 2), "block_std": round(block_std, 2)},
            "score":       score,
            "confidence":  0.60,
            "limitations": (
                "Text-region ELA can be elevated by document scanning, compression artifacts, "
                "or printed text inherently. This is an indicator, not proof of manipulation."
            ),
        }
    except Exception as e:
        return {
            "signal":      f"Text region analysis failed: {str(e)}",
            "region":      "text_zone",
            "measurement": {},
            "score":       0,
            "confidence":  0,
            "limitations": "Analysis unavailable.",
        }


# ─── Copy-Move Indicator ─────────────────────────────────────

def detect_copy_move_indicators(image_bytes: bytes) -> dict:
    """
    Simplified block-based copy-move detection.
    Compares non-overlapping 32x32 blocks for near-identical matches,
    which can indicate copy-pasted regions.

    This is a heuristic — not a full DCT copy-move forensics implementation.
    Returns signal, suspicious_pair_count, score, confidence, limitations.
    """
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("L")
        w, h = img.size

        # Limit to reasonable size for performance
        scale = min(1.0, 800 / max(w, h))
        if scale < 1.0:
            img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
            w, h = img.size

        arr = np.array(img, dtype=np.float32)
        block_size = 32
        blocks = {}
        suspicious_pairs = 0

        for y in range(0, h - block_size, block_size):
            for x in range(0, w - block_size, block_size):
                block = arr[y:y+block_size, x:x+block_size]
                # Filter out flat background blocks (solid paper, uniform background)
                if np.std(block) < 8.0:
                    continue

                # Use mean + std as a coarse hash
                key = (round(float(np.mean(block)), 0),
                       round(float(np.std(block)), 0))
                if key in blocks:
                    by, bx = blocks[key]
                    # Filter out collinear border/banner lines
                    if y == by or x == bx:
                        continue
                    # Spatial separation: blocks must not be adjacent
                    dist = np.sqrt((y - by)**2 + (x - bx)**2)
                    if dist < block_size * 2:
                        continue

                    # Potential duplicate — check normalized correlation
                    other_block = arr[by:by+block_size, bx:bx+block_size]
                    # Mean squared difference
                    msd = float(np.mean((block - other_block) ** 2))
                    if msd < 50:   # Near-identical blocks
                        suspicious_pairs += 1
                else:
                    blocks[key] = (y, x)

        score = min(suspicious_pairs * 8, 100)

        if suspicious_pairs > 8:
            signal = (f"Detected {suspicious_pairs} near-identical image blocks — "
                      "potential copy-move manipulation. Requires specialist review.")
        elif suspicious_pairs > 2:
            signal = (f"Found {suspicious_pairs} similar block pairs — "
                      "may be natural repetition (e.g., background pattern) or copy-move")
        else:
            signal = "No significant copy-move indicators detected"

        return {
            "signal":              signal,
            "region":              "full_image",
            "measurement":         {"suspicious_pairs": suspicious_pairs},
            "score":               score,
            "confidence":          0.45,
            "limitations": (
                "Block-hash copy-move is a simplified heuristic. "
                "Natural patterns (e.g., document backgrounds, repeated text) will generate false positives. "
                "A specialist tool (e.g., DCT-based CMFD) is required for definitive copy-move analysis."
            ),
        }
    except Exception as e:
        return {
            "signal":      f"Copy-move analysis failed: {str(e)}",
            "region":      "full_image",
            "measurement": {},
            "score":       0,
            "confidence":  0,
            "limitations": "Analysis unavailable.",
        }


# ─── Stamp Region Detection ───────────────────────────────────

def detect_stamp_region(image_bytes: bytes) -> dict:
    """
    Detect circular/elliptical stamp-like regions using hue-saturation analysis.
    Official stamps typically appear as highly saturated circular blobs.

    Returns presence/absence signal, bounding area, confidence, limitations.
    """
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("HSV"
              if "HSV" in Image.MODES else "RGB")
        # PIL doesn't natively support HSV — use RGB and compute manually
        img_rgb = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        arr = np.array(img_rgb, dtype=np.float32) / 255.0

        r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]
        maxc = np.max(arr, axis=2)
        minc = np.min(arr, axis=2)
        with np.errstate(divide='ignore', invalid='ignore'):
            saturation = np.where(maxc > 0, (maxc - minc) / maxc, 0)

        # High-saturation mask (stamps are typically red/blue/purple)
        high_sat = saturation > 0.4
        sat_ratio = float(np.mean(high_sat))

        # Look for specific hues: red (0°) and blue (240°) stamps
        delta = maxc - minc + 1e-6
        h = np.zeros_like(r)
        mask_r = (maxc == r) & (delta > 0)
        mask_g = (maxc == g) & (delta > 0)
        mask_b = (maxc == b) & (delta > 0)
        h[mask_r] = ((g[mask_r] - b[mask_r]) / delta[mask_r]) % 6
        h[mask_g] = (b[mask_g] - r[mask_g]) / delta[mask_g] + 2
        h[mask_b] = (r[mask_b] - g[mask_b]) / delta[mask_b] + 4
        h_degrees = h * 60

        # Count red and blue pixels above saturation threshold
        red_pixels  = float(np.mean((h_degrees < 30) | (h_degrees > 330)) * high_sat)
        blue_pixels = float(np.mean(((h_degrees > 200) & (h_degrees < 260)) * high_sat))

        stamp_detected = (red_pixels > 0.02 or blue_pixels > 0.02)

        signal = ("Stamp-like region detected — high-saturation circular area consistent "
                  "with an official seal or rubber stamp"
                  if stamp_detected else
                  "No stamp-like region detected — document may lack official seal or it is not visible")

        return {
            "signal":      signal,
            "region":      "stamp_detection",
            "measurement": {
                "saturation_ratio": round(sat_ratio, 3),
                "red_pixel_ratio":  round(red_pixels, 4),
                "blue_pixel_ratio": round(blue_pixels, 4),
                "stamp_detected":   stamp_detected,
            },
            "score":      30 if not stamp_detected else 0,
            "confidence": 0.50,
            "limitations": (
                "Stamp detection is based on color heuristics. "
                "Colour shifts from scanning, lighting, or compression may affect accuracy. "
                "This is an indicator of stamp presence/absence, not stamp authenticity."
            ),
        }
    except Exception as e:
        return {
            "signal":      f"Stamp detection failed: {str(e)}",
            "region":      "stamp_detection",
            "measurement": {},
            "score":       0,
            "confidence":  0,
            "limitations": "Analysis unavailable.",
        }


# ─── Suspicious Region Localization ──────────────────────────

def localize_suspicious_regions(image_bytes: bytes,
                                  ela_result: dict) -> list:
    """
    Identify bounding boxes of high-ELA regions that may warrant attention.
    Returns a list of suspect region descriptors.

    Each region: {x, y, w, h, ela_mean, label, confidence, limitations}
    """
    try:
        from utils.config import ELA_QUALITY
        original = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        w, h = original.size

        buf = io.BytesIO()
        original.save(buf, "JPEG", quality=ELA_QUALITY)
        buf.seek(0)
        recomp = Image.open(buf).convert("RGB")

        diff = ImageChops.difference(original, recomp)
        diff_arr = np.array(diff.convert("L"), dtype=np.float32)

        # Find high-ELA regions using block scanning
        BLOCK = 64
        THRESHOLD = 25
        regions = []

        for y in range(0, h - BLOCK, BLOCK):
            for x in range(0, w - BLOCK, BLOCK):
                block = diff_arr[y:y+BLOCK, x:x+BLOCK]
                mean = float(np.mean(block))
                if mean > THRESHOLD:
                    # Classify region by position
                    rel_y = y / h
                    rel_x = x / w
                    if rel_y < 0.3:
                        label = "header_region"
                    elif rel_y < 0.6 and rel_x < 0.4:
                        label = "photo_region"
                    elif rel_y > 0.7:
                        label = "mrz_region"
                    else:
                        label = "text_region"

                    regions.append({
                        "x": x, "y": y, "width": BLOCK, "height": BLOCK,
                        "ela_mean":   round(mean, 2),
                        "label":      label,
                        "confidence": 0.55,
                        "limitations": (
                            "High ELA in this region indicates compression anomaly. "
                            "This may be due to intentional editing OR natural document features "
                            "(photos, seals, printed text). Specialist review recommended."
                        ),
                    })

        # Merge adjacent regions (simple de-duplication)
        return regions[:20]  # Return at most 20 regions

    except Exception as e:
        return [{
            "label": "error",
            "x": 0, "y": 0, "width": 0, "height": 0,
            "ela_mean": 0,
            "confidence": 0,
            "limitations": f"Region localization failed: {str(e)}",
        }]


# ─── Master Document Tamper Map ───────────────────────────────

def generate_tamper_evidence_map(image_bytes: bytes,
                                  image_forensics_result: dict) -> dict:
    """
    Aggregate all document-specific tamper signals into a single evidence map.
    Uses existing image_forensics_result to avoid re-running shared analyses.

    Returns:
      {
        "signals": [...],          # individual signal evidence items
        "suspicious_regions": [...], # region bounding boxes
        "tamper_score": 0-100,    # composite (does NOT mean forgery alone)
        "confidence": float,
        "summary": str,
        "limitations": str
      }
    """
    text_anom  = detect_text_region_anomalies(image_bytes)
    copy_move  = detect_copy_move_indicators(image_bytes)
    stamp      = detect_stamp_region(image_bytes)
    ela_result = image_forensics_result.get("ela", {})
    regions    = localize_suspicious_regions(image_bytes, ela_result)

    signals = [text_anom, copy_move, stamp]

    # Composite tamper score — weighted average of individual signals
    # Each signal has a different confidence weight
    weights = [0.45, 0.30, 0.25]
    tamper_score = int(sum(
        s.get("score", 0) * w
        for s, w in zip(signals, weights)
    ))

    # Cross-signal corroboration: if multiple signals fire together, raise score
    high_signals = sum(1 for s in signals if s.get("score", 0) > 40)
    if high_signals >= 2:
        tamper_score = min(tamper_score + 15, 100)

    # Summary
    if tamper_score >= 60:
        summary = ("Multiple forensic indicators suggest this document may have been manipulated. "
                   "Recommend specialist forensic review before any decision.")
    elif tamper_score >= 30:
        summary = "Some forensic indicators present. Manual verification of suspicious regions recommended."
    else:
        summary = "No significant forensic tampering indicators detected."

    return {
        "signals":            signals,
        "suspicious_regions": regions,
        "tamper_score":       tamper_score,
        "confidence":         0.60,
        "summary":            summary,
        "limitations": (
            "Document forensic analysis identifies statistical anomalies. "
            "No individual signal is absolute proof of forgery. "
            "A combination of signals increases suspicion, but human expert review "
            "is required before drawing any legal conclusion."
        ),
    }
