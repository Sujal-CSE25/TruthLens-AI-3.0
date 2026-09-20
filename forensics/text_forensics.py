"""
TruthLens AI 2.0 — Text Forensics Engine
Linguistic + semantic analysis without LLM dependency.
"""
import re
import math
from collections import Counter
from forensics.embedding_analysis import detect_misinformation_similarity

# ─── Wordlists ────────────────────────────────────────────────

CLICKBAIT_PATTERNS = [
    r"you won'?t believe", r"this will shock you", r"the truth about",
    r"they don'?t want you to know", r"secret(s)? revealed", r"doctors hate",
    r"share before (it'?s )?(deleted|removed)", r"breaking[!:]+", r"\bOMG\b",
    r"must (see|read|watch)", r"\b(100|1000)%\b", r"what happens next",
]

EMOTIONAL_WORDS = {
    "outrage", "shocking", "disgusting", "terrifying", "horrible", "evil",
    "incredible", "amazing", "unbelievable", "devastating", "catastrophic",
    "explosive", "bombshell", "scandalous", "alarming", "urgent", "critical",
    "danger", "threat", "crisis", "panic", "fear", "hate", "rage", "fury",
}

URGENCY_PATTERNS = [
    r"\bnow\b", r"\bimmediately\b", r"\basap\b", r"\burgent\b",
    r"\btoday only\b", r"\bhurry\b", r"\bact fast\b", r"\bbreaking\b",
    r"\bdeveloping\b", r"last chance", r"time is running out",
]

CERTAINTY_HEDGES = [
    r"\ballegedly\b", r"\bapparently\b", r"\bsource(s)? say\b",
    r"\bsome say\b", r"\baccording to\b", r"\breports suggest\b",
    r"\bcould be\b", r"\bmight be\b", r"\bpossibly\b", r"\bperhaps\b",
]

CERTAINTY_ABSOLUTES = [
    r"\balways\b", r"\bnever\b", r"\beveryone\b", r"\bno one\b",
    r"\bproven\b", r"\bfact\b", r"\bdefinitely\b", r"\bclearly\b",
    r"\bobviously\b", r"\bguaranteed\b", r"\b100%\b",
]

PROPAGANDA_PATTERNS = [
    r"mainstream media", r"fake news", r"\bdeep state\b", r"\bwake up\b",
    r"\bsheeple\b", r"\bagenda\b", r"\belites\b", r"\bglobalists?\b",
    r"(they|we) are being (lied to|controlled|manipulated)",
    r"\bplandemic\b", r"\bpyramid of power\b",
]

CREDIBILITY_SOURCES = [
    "reuters", "ap news", "bbc", "cnn", "nyt", "new york times",
    "washington post", "guardian", "npr", "cdc", "who", "fda", "nasa",
    "nature", "science", "lancet", "pubmed",
]

MISINFORMATION_INDICATORS = [
    "bleach cure", "vaccine chip", "5g covid", "chemtrail", "flat earth",
    "crisis actor", "sandy hook hoax", "moon landing fake",
    "illuminati", "new world order", "qanon",
]


# ─── Scoring Functions ────────────────────────────────────────

def _count_patterns(text: str, patterns: list) -> int:
    count = 0
    text_lower = text.lower()
    for p in patterns:
        if re.search(p, text_lower):
            count += 1
    return count


def _word_match_ratio(text: str, wordset: set) -> float:
    words = re.findall(r"\b\w+\b", text.lower())
    if not words:
        return 0.0
    hits = sum(1 for w in words if w in wordset)
    return hits / len(words)


def compute_clickbait_score(text: str) -> int:
    hits = _count_patterns(text, CLICKBAIT_PATTERNS)
    exclamations = text.count("!")
    all_caps = len(re.findall(r"\b[A-Z]{3,}\b", text))
    raw = hits * 20 + min(exclamations * 5, 30) + min(all_caps * 8, 30)
    return min(int(raw), 100)


def compute_emotional_score(text: str) -> int:
    ratio = _word_match_ratio(text, EMOTIONAL_WORDS)
    raw = ratio * 500
    return min(int(raw), 100)


def compute_urgency_score(text: str) -> int:
    hits = _count_patterns(text, URGENCY_PATTERNS)
    raw = hits * 15
    return min(int(raw), 100)


def compute_certainty_score(text: str) -> int:
    """
    High score = high certainty (absolutes dominate).
    Low score = hedged/uncertain language.
    """
    absolutes = _count_patterns(text, CERTAINTY_ABSOLUTES)
    hedges    = _count_patterns(text, CERTAINTY_HEDGES)
    total = absolutes + hedges
    if total == 0:
        return 50
    raw = (absolutes / total) * 100
    return int(raw)


def compute_propaganda_score(text: str) -> int:
    hits = _count_patterns(text, PROPAGANDA_PATTERNS)
    raw  = hits * 20
    return min(int(raw), 100)


def compute_credibility_score(text: str) -> int:
    """How many credible sources are mentioned."""
    text_lower = text.lower()
    hits = sum(1 for s in CREDIBILITY_SOURCES if s in text_lower)
    return min(hits * 20, 100)


def detect_misinformation_keywords(text: str) -> list:
    """Return list of known misinformation indicator phrases found."""
    text_lower = text.lower()
    found = [phrase for phrase in MISINFORMATION_INDICATORS if phrase in text_lower]
    return found


def detect_contradiction_signals(text: str) -> list:
    """
    Heuristic: look for sentences that contradict common logical structure.
    Returns a list of signal descriptions.
    """
    signals = []
    sentences = re.split(r"[.!?]+", text)

    negation_then_assertion = re.compile(
        r"\b(not|no|never|false)\b.{5,50}\b(but|however|yet|actually)\b", re.IGNORECASE
    )
    if negation_then_assertion.search(text):
        signals.append("Contradictory negation-assertion pattern detected")

    claim_patterns = [r"\bproven\b", r"\bconfirmed\b", r"\bfact\b"]
    counter_patterns = [r"\bunverified\b", r"\balleged\b", r"\bsuspected\b"]
    has_claim   = any(re.search(p, text, re.I) for p in claim_patterns)
    has_counter = any(re.search(p, text, re.I) for p in counter_patterns)
    if has_claim and has_counter:
        signals.append("Simultaneous 'proven fact' and 'unverified' language")

    numeric = re.findall(r"\b\d+(?:\.\d+)?%\b", text)
    if len(numeric) > 3:
        signals.append(f"Unusual density of statistics ({len(numeric)} percentages)")

    return signals


# ─── Main Entry ──────────────────────────────────────────────

def run_linguistic_analysis(text: str) -> dict:
    """
    Full linguistic + semantic analysis.
    Returns a dict of scores and signals.
    """
    clickbait   = compute_clickbait_score(text)
    emotional   = compute_emotional_score(text)
    urgency     = compute_urgency_score(text)
    certainty   = compute_certainty_score(text)
    propaganda  = compute_propaganda_score(text)
    credibility = compute_credibility_score(text)
    misinfo_kw  = detect_misinformation_keywords(text)
    contradictions = detect_contradiction_signals(text)

    # Semantic similarity to known misinformation narratives (embedding-based)
    semantic_match = detect_misinformation_similarity(text)
    semantic_score = int(semantic_match["max_similarity"] * 100)

    # Aggregate risk score
    risk_components = [clickbait * 0.20, emotional * 0.18, urgency * 0.12,
                       propaganda * 0.20, (100 - credibility) * 0.12,
                       semantic_score * 0.18]
    aggregate_risk  = min(int(sum(risk_components)), 100)

    red_flags = []
    if clickbait >= 40:
        red_flags.append(f"Clickbait language detected (score: {clickbait})")
    if emotional >= 40:
        red_flags.append(f"High emotional manipulation (score: {emotional})")
    if urgency >= 30:
        red_flags.append(f"Artificial urgency patterns (score: {urgency})")
    if propaganda >= 30:
        red_flags.append(f"Propaganda indicators present (score: {propaganda})")
    if misinfo_kw:
        red_flags.append(f"Known misinformation keywords: {', '.join(misinfo_kw)}")
    if semantic_match["is_similar"]:
        red_flags.append(
            f"Semantically similar to known misinformation narrative "
            f"({semantic_score}% match): \"{semantic_match['matched_template']}\""
        )
    red_flags.extend(contradictions)

    return {
        "clickbait_score":   clickbait,
        "emotional_score":   emotional,
        "urgency_score":     urgency,
        "certainty_score":   certainty,
        "propaganda_score":  propaganda,
        "credibility_score": credibility,
        "semantic_similarity_score": semantic_score,
        "semantic_match":    semantic_match,
        "aggregate_risk":    aggregate_risk,
        "misinfo_keywords":  misinfo_kw,
        "contradiction_signals": contradictions,
        "red_flags":         red_flags,
        "word_count":        len(text.split()),
        "sentence_count":    len(re.split(r"[.!?]+", text)),
    }
