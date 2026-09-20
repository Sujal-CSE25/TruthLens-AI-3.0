"""
TruthLens AI 2.0 — Embedding Analysis Engine
Sentence Transformers (all-MiniLM-L6-v2) for similarity scoring,
claim clustering, and misinformation similarity detection.

Gracefully falls back to keyword-overlap similarity if
sentence-transformers / torch are not installed — the app
never crashes due to a missing optional dependency.
"""
import re
from functools import lru_cache

_MODEL_NAME = "all-MiniLM-L6-v2"
_model = None
_model_load_failed = False


# ─── Known Misinformation Templates ──────────────────────────
# Canonical statements representing common misinformation narratives.
# Used for semantic similarity comparison (Phase 2C requirement).
MISINFO_TEMPLATES = [
    "Vaccines cause autism in children.",
    "5G towers spread the coronavirus.",
    "Drinking bleach or disinfectant cures cancer or COVID-19.",
    "The election results were fraudulent due to massive voter fraud.",
    "Climate change is a hoax invented by scientists for funding.",
    "The earth is flat and space agencies are lying.",
    "A secret global elite controls world governments and media.",
    "This natural remedy cures all diseases and big pharma is hiding it.",
    "The moon landing was faked by the government.",
    "Microchips are being implanted via vaccines to track people.",
]


# ─── Model Loading ────────────────────────────────────────────

def _get_model():
    """Lazily load the SentenceTransformer model. Cached after first load."""
    global _model, _model_load_failed
    if _model is not None:
        return _model
    if _model_load_failed:
        return None
    try:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(_MODEL_NAME)
        return _model
    except Exception:
        _model_load_failed = True
        return None


def embeddings_available() -> bool:
    """Check whether sentence-transformers is usable in this environment."""
    return _get_model() is not None


# ─── Fallback: Keyword-Overlap Similarity ────────────────────

def _keyword_similarity(a: str, b: str) -> float:
    """Jaccard-style overlap on 4+ letter words. Used when embeddings unavailable."""
    wa = set(re.findall(r"\b\w{4,}\b", a.lower()))
    wb = set(re.findall(r"\b\w{4,}\b", b.lower()))
    if not wa or not wb:
        return 0.0
    inter = len(wa & wb)
    union = len(wa | wb)
    return inter / union if union else 0.0


# ─── Core Similarity ──────────────────────────────────────────

def compute_similarity(text_a: str, text_b: str) -> float:
    """
    Return semantic similarity in [0, 1] between two texts.
    Uses sentence embeddings (cosine similarity) when available,
    otherwise falls back to keyword-overlap.
    """
    if not text_a or not text_b:
        return 0.0

    model = _get_model()
    if model is None:
        return round(_keyword_similarity(text_a, text_b), 4)

    try:
        import numpy as np
        emb = model.encode([text_a, text_b])
        a, b = emb[0], emb[1]
        denom = (np.linalg.norm(a) * np.linalg.norm(b))
        if denom == 0:
            return 0.0
        sim = float(np.dot(a, b) / denom)
        # Cosine similarity is in [-1, 1] — clamp to [0, 1] for scoring
        return round(max(0.0, min(1.0, sim)), 4)
    except Exception:
        return round(_keyword_similarity(text_a, text_b), 4)


def batch_similarity_matrix(texts: list) -> list:
    """
    Compute pairwise similarity matrix for a list of texts.
    Returns a list of lists (NxN).
    """
    n = len(texts)
    model = _get_model()

    if model is not None:
        try:
            import numpy as np
            emb = model.encode(texts)
            norms = np.linalg.norm(emb, axis=1, keepdims=True)
            norms[norms == 0] = 1
            normalized = emb / norms
            sim_matrix = normalized @ normalized.T
            return [[round(float(max(0.0, min(1.0, sim_matrix[i][j]))), 4)
                     for j in range(n)] for i in range(n)]
        except Exception:
            pass

    # Fallback: pairwise keyword similarity
    return [[round(_keyword_similarity(texts[i], texts[j]), 4) if i != j else 1.0
             for j in range(n)] for i in range(n)]


# ─── Claim Clustering ─────────────────────────────────────────

def cluster_claims(claims: list, threshold: float = 0.55) -> dict:
    """
    Greedily cluster semantically similar claims.

    Args:
        claims: list of claim strings.
        threshold: similarity threshold above which two claims are
                   considered the same cluster.

    Returns:
        {
          "clusters": [[idx1, idx2, ...], ...],
          "cluster_count": int,
          "duplicate_groups": int  # clusters with >1 member
        }
    """
    n = len(claims)
    if n == 0:
        return {"clusters": [], "cluster_count": 0, "duplicate_groups": 0}
    if n == 1:
        return {"clusters": [[0]], "cluster_count": 1, "duplicate_groups": 0}

    sim_matrix = batch_similarity_matrix(claims)
    assigned = [-1] * n
    clusters = []

    for i in range(n):
        if assigned[i] != -1:
            continue
        cluster_id = len(clusters)
        clusters.append([i])
        assigned[i] = cluster_id
        for j in range(i + 1, n):
            if assigned[j] == -1 and sim_matrix[i][j] >= threshold:
                clusters[cluster_id].append(j)
                assigned[j] = cluster_id

    duplicate_groups = sum(1 for c in clusters if len(c) > 1)

    return {
        "clusters": clusters,
        "cluster_count": len(clusters),
        "duplicate_groups": duplicate_groups,
    }


# ─── Misinformation Similarity Detection ─────────────────────

def detect_misinformation_similarity(text: str, threshold: float = 0.45) -> dict:
    """
    Compare input text against known misinformation narrative templates.

    Returns:
        {
          "max_similarity": float,
          "matched_template": str | None,
          "is_similar": bool,
          "all_scores": [{"template": ..., "score": ...}, ...]
        }
    """
    scores = []
    for template in MISINFO_TEMPLATES:
        sim = compute_similarity(text, template)
        scores.append({"template": template, "score": sim})

    scores.sort(key=lambda x: x["score"], reverse=True)
    top = scores[0] if scores else {"template": None, "score": 0.0}

    return {
        "max_similarity":  top["score"],
        "matched_template": top["template"] if top["score"] >= threshold else None,
        "is_similar":      top["score"] >= threshold,
        "all_scores":      scores[:3],
    }


# ─── Claim ↔ Evidence Re-ranking ─────────────────────────────

def rerank_evidence_by_similarity(claim: str, evidence: list) -> list:
    """
    Re-score evidence relevance using semantic similarity.
    Mutates and returns the evidence list with updated 'relevance' scores.
    """
    for e in evidence:
        snippet = e.get("snippet", "")
        if snippet:
            e["relevance"] = compute_similarity(claim, snippet)
    return sorted(evidence, key=lambda x: x.get("relevance", 0), reverse=True)
