"""
TruthLens AI 2.0 — RAG Evidence Retrieval
Wikipedia + Google Custom Search + semantic ranking.
"""
import re
import json
import urllib.request
import urllib.parse
import urllib.error
from utils.config import GOOGLE_API_KEY, GOOGLE_CSE_ID


# ─── Wikipedia Evidence ───────────────────────────────────────

def search_wikipedia(query: str, max_results: int = 2) -> list:
    """Search Wikipedia and return relevant snippets."""
    try:
        encoded = urllib.parse.quote(query[:100])
        url = (
            f"https://en.wikipedia.org/w/api.php?"
            f"action=query&list=search&srsearch={encoded}&format=json"
            f"&srlimit={max_results}&utf8=1"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "TruthLens-AI/2.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())

        results = []
        for item in data.get("query", {}).get("search", []):
            # Strip HTML tags from snippet
            snippet = re.sub(r"<[^>]+>", "", item.get("snippet", ""))
            results.append({
                "title":    item.get("title", ""),
                "snippet":  snippet,
                "url":      f"https://en.wikipedia.org/wiki/{urllib.parse.quote(item.get('title', '').replace(' ', '_'))}",
                "source":   "Wikipedia",
                "relevance": 0.7,
            })
        return results
    except Exception:
        return []


# ─── Google Custom Search ─────────────────────────────────────

def search_google(query: str, max_results: int = 3) -> list:
    """
    Search via Google Custom Search API.
    Returns empty list if API keys not configured.
    """
    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        return []

    try:
        encoded_q = urllib.parse.quote(query[:150])
        url = (
            f"https://www.googleapis.com/customsearch/v1"
            f"?key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}"
            f"&q={encoded_q}&num={max_results}"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "TruthLens-AI/2.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())

        results = []
        for item in data.get("items", []):
            results.append({
                "title":    item.get("title", ""),
                "snippet":  item.get("snippet", ""),
                "url":      item.get("link", ""),
                "source":   "Google Search",
                "relevance": 0.8,
            })
        return results
    except Exception:
        return []


# ─── Semantic Relevance Scorer ───────────────────────────────

def score_relevance(claim: str, snippet: str) -> float:
    """
    Simple keyword-overlap relevance score (0–1).
    Used when sentence transformers are not installed.
    """
    claim_words  = set(re.findall(r"\b\w{4,}\b", claim.lower()))
    snippet_words= set(re.findall(r"\b\w{4,}\b", snippet.lower()))
    if not claim_words:
        return 0.0
    overlap = len(claim_words & snippet_words)
    return round(overlap / len(claim_words), 3)


# ─── Master Evidence Retriever ───────────────────────────────

def retrieve_evidence(claim: str, max_total: int = 5) -> list:
    """
    Retrieve and rank evidence for a single claim.
    Sources: Wikipedia + Google (if configured).
    """
    # Clean claim for search
    search_query = re.sub(r"[^\w\s]", "", claim)[:120]

    evidence = []
    evidence.extend(search_wikipedia(search_query, max_results=2))
    evidence.extend(search_google(search_query,    max_results=3))

    # Score and rank
    for e in evidence:
        e["relevance"] = score_relevance(claim, e.get("snippet", ""))

    ranked = sorted(evidence, key=lambda x: x["relevance"], reverse=True)
    return ranked[:max_total]


def build_rag_context(claims: list) -> str:
    """
    Build RAG context string from multiple claims + their evidence.
    Used for enriching Gemini prompts.
    """
    context_parts = []
    for i, claim_obj in enumerate(claims[:4]):
        claim_text = claim_obj.get("claim", "")
        evidence   = retrieve_evidence(claim_text)
        evid_str   = "\n  ".join([
            f"[{e['source']}] {e['snippet'][:150]}"
            for e in evidence[:2]
        ])
        context_parts.append(
            f"Claim {i+1}: {claim_text}\n"
            f"  Evidence:\n  {evid_str if evid_str else 'No evidence found.'}"
        )

    return "\n\n".join(context_parts)
