"""
TruthLens AI 2.0 — Multi-Agent AI System
6 specialized agents orchestrated for deep claim verification.

Agent 1: Claim Extractor
Agent 2: Evidence Finder
Agent 3: Fact Checker
Agent 4: Risk Assessor
Agent 5: Explainability Agent
Agent 6: Final Judge Agent
"""
import json
import re
from typing import List, Dict, Any
from utils.gemini_client import call_gemini_json, call_gemini
from utils.config import GEMINI_API_KEY
from forensics.text_forensics import (
    run_linguistic_analysis, detect_misinformation_keywords,
    compute_propaganda_score, compute_clickbait_score,
)
from forensics.embedding_analysis import (
    cluster_claims, rerank_evidence_by_similarity, detect_misinformation_similarity,
)
from rag.evidence_retriever import retrieve_evidence


# ─── Agent Base ──────────────────────────────────────────────

class Agent:
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role

    def run(self, *args, **kwargs) -> dict:
        raise NotImplementedError


# ─── Agent 1: Claim Extractor ────────────────────────────────

class ClaimExtractorAgent(Agent):
    def __init__(self):
        super().__init__("ClaimExtractor", "Extract verifiable factual claims from text")

    def run(self, text: str) -> dict:
        if not GEMINI_API_KEY:
            return self._demo_claims(text)

        prompt = f"""You are a claim extraction expert for fact-checking.
Extract all verifiable factual claims from the text below.
Focus on: statistics, named entities, event claims, causal claims, medical/scientific claims.

TEXT:
\"\"\"
{text[:2000]}
\"\"\"

Return ONLY valid JSON:
{{
  "claims": [
    {{
      "claim": "<the specific verifiable claim>",
      "type": "<statistic|event|person|scientific|causal|other>",
      "verifiability": <0-100, how easily this can be verified>,
      "entities": ["<entity1>", "<entity2>"]
    }}
  ],
  "total_claims": <number>,
  "primary_topic": "<main topic>",
  "claim_density": "<low|medium|high>"
}}"""
        try:
            return call_gemini_json(prompt)
        except Exception as e:
            print(f"[ClaimExtractor Error] {e}")
            return self._demo_claims(text)


    def _demo_claims(self, text: str) -> dict:
        sentences = [s.strip() for s in re.split(r"[.!?]+", text) if len(s.strip()) > 20]
        claims = [{"claim": s, "type": "general", "verifiability": 50, "entities": []}
                  for s in sentences[:4]]
        return {
            "claims": claims,
            "total_claims": len(claims),
            "primary_topic": "general",
            "claim_density": "medium",
        }


# ─── Agent 2: Evidence Finder ────────────────────────────────

class EvidenceFinderAgent(Agent):
    def __init__(self):
        super().__init__("EvidenceFinder", "Retrieve evidence for each claim")

    def run(self, claims: List[Dict]) -> dict:
        evidence_map = {}
        for i, claim_obj in enumerate(claims[:5]):  # limit to 5 claims
            claim_text = claim_obj.get("claim", "")
            evidence = retrieve_evidence(claim_text)
            # Re-rank using sentence-embedding similarity (falls back to keyword overlap)
            evidence = rerank_evidence_by_similarity(claim_text, evidence)
            evidence_map[f"claim_{i}"] = {
                "claim":    claim_text,
                "evidence": evidence,
            }
        return {"evidence_map": evidence_map, "total_searched": len(evidence_map)}


# ─── Agent 3: Fact Checker ───────────────────────────────────

class FactCheckerAgent(Agent):
    def __init__(self):
        super().__init__("FactChecker", "Verify each claim against retrieved evidence")

    def run(self, claims: List[Dict], evidence_map: Dict) -> dict:
        if not GEMINI_API_KEY:
            return self._demo_verdict(claims)

        verified_claims = []
        for i, claim_obj in enumerate(claims[:5]):
            claim_text = claim_obj.get("claim", "")
            evid = evidence_map.get(f"claim_{i}", {}).get("evidence", [])
            evid_text = "\n".join([f"- {e.get('snippet', '')}" for e in evid[:3]])

            prompt = f"""You are a professional fact-checker.
Evaluate this claim against the provided evidence.

CLAIM: {claim_text}

EVIDENCE:
{evid_text if evid_text else "No external evidence retrieved."}

Return ONLY valid JSON:
{{
  "claim": "{claim_text[:200]}",
  "verdict": "<SUPPORTED|CONTRADICTED|UNVERIFIED|PARTIALLY_TRUE>",
  "confidence": <0-100>,
  "reasoning": "<1-2 sentence reasoning>",
  "sources_used": <number of evidence pieces used>
}}"""
            try:
                result = call_gemini_json(prompt)
                result["evidence_count"] = len(evid)
                verified_claims.append(result)
            except Exception:
                verified_claims.append({
                    "claim": claim_text,
                    "verdict": "UNVERIFIED",
                    "confidence": 40,
                    "reasoning": "Unable to verify due to API error.",
                    "sources_used": 0,
                    "evidence_count": len(evid),
                })

        return {"verified_claims": verified_claims}

    def _demo_verdict(self, claims: List[Dict]) -> dict:
        """
        Demo-mode heuristic fact-check.

        Without a Gemini API key we can't run LLM-based fact-checking, but we
        can still give a representative, signal-grounded verdict per claim
        using the same local linguistic + embedding tools used elsewhere —
        so the demo isn't just a wall of "UNVERIFIED".
        """
        verified = []
        for c in claims[:5]:
            claim_text = c.get("claim", "")
            kw      = detect_misinformation_keywords(claim_text)
            sem     = detect_misinformation_similarity(claim_text)
            prop    = compute_propaganda_score(claim_text)
            click   = compute_clickbait_score(claim_text)

            if kw or sem["is_similar"] or prop >= 40:
                verdict = "CONTRADICTED"
                conf    = 62
                reason  = (
                    "Demo mode (no API key): local signal match — "
                    + (f"known misinformation keyword(s) {', '.join(kw)}; " if kw else "")
                    + (f"{int(sem['max_similarity']*100)}% semantic similarity to known "
                       f"misinformation narrative; " if sem["is_similar"] else "")
                    + (f"propaganda score {prop}/100." if prop >= 40 else "")
                ).strip()
            elif click >= 60:
                verdict = "PARTIALLY_TRUE"
                conf    = 50
                reason  = (
                    "Demo mode (no API key): claim phrasing is highly clickbait-styled "
                    f"(score {click}/100) — verify against a primary source."
                )
            else:
                verdict = "UNVERIFIED"
                conf    = 40
                reason  = "Demo mode — connect GEMINI_API_KEY for live evidence-based fact-checking."

            verified.append({
                "claim": claim_text,
                "verdict": verdict,
                "confidence": conf,
                "reasoning": reason,
                "sources_used": 0,
                "evidence_count": 0,
            })
        return {"verified_claims": verified}


# ─── Agent 4: Risk Assessor ──────────────────────────────────

class RiskAssessorAgent(Agent):
    def __init__(self):
        super().__init__("RiskAssessor", "Assess overall misinformation risk")

    def run(self, text: str, linguistic: dict, verified_claims: List[Dict]) -> dict:
        # Linguistic risk component
        linguistic_risk = linguistic.get("aggregate_risk", 50)

        # Claim verification component
        verdicts = [c.get("verdict", "UNVERIFIED") for c in verified_claims]
        contradicted = verdicts.count("CONTRADICTED")
        unverified   = verdicts.count("UNVERIFIED")
        supported    = verdicts.count("SUPPORTED")
        partial      = verdicts.count("PARTIALLY_TRUE")
        total_claims = len(verdicts)

        if total_claims == 0:
            claim_risk = 50
        else:
            claim_risk = int(
                (contradicted * 80 + unverified * 40 + partial * 55 + supported * 5)
                / total_claims
            )

        # Combined risk
        combined_risk = int(linguistic_risk * 0.45 + claim_risk * 0.55)
        combined_risk = max(0, min(100, combined_risk))

        # Risk level
        if combined_risk >= 70:
            risk_level = "HIGH"
            verdict    = "LIKELY FAKE"
        elif combined_risk >= 40:
            risk_level = "MEDIUM"
            verdict    = "UNCERTAIN"
        else:
            risk_level = "LOW"
            verdict    = "LIKELY REAL"

        risk_factors = []
        if linguistic_risk >= 50:
            risk_factors.append(f"High linguistic manipulation score ({linguistic_risk})")
        if contradicted > 0:
            risk_factors.append(f"{contradicted} claim(s) contradicted by evidence")
        if partial > 0:
            risk_factors.append(f"{partial} claim(s) only partially true")
        if unverified > 0:
            risk_factors.append(f"{unverified} claim(s) could not be verified")
        if linguistic.get("misinfo_keywords"):
            risk_factors.append(f"Known misinformation keywords detected: {', '.join(linguistic['misinfo_keywords'])}")

        return {
            "fake_score":     combined_risk,
            "trust_score":    max(0, 100 - combined_risk),
            "bias_score":     linguistic.get("propaganda_score", 0),
            "manipulation_score": linguistic.get("emotional_score", 0),
            "risk_level":     risk_level,
            "verdict":        verdict,
            "risk_factors":   risk_factors,
            "claim_stats": {
                "total":       total_claims,
                "supported":   supported,
                "contradicted":contradicted,
                "unverified":  unverified,
                "partial":     partial,
            },
        }


# ─── Agent 5: Explainability Agent ──────────────────────────

class ExplainabilityAgent(Agent):
    def __init__(self):
        super().__init__("ExplainabilityAgent", "Generate human-readable reasoning chain")

    def run(self, text: str, risk: dict, linguistic: dict,
            verified_claims: List[Dict]) -> dict:
        if not GEMINI_API_KEY:
            return self._demo_explanation(risk)

        claim_summary = "\n".join([
            f"  • Claim: {c['claim'][:100]} → {c['verdict']} (confidence: {c['confidence']}%)"
            for c in verified_claims[:4]
        ])

        prompt = f"""You are an AI explainability expert for misinformation detection.

ANALYSIS CONTEXT:
- Overall fake score: {risk['fake_score']}/100
- Verdict: {risk['verdict']}
- Linguistic risk: {linguistic['aggregate_risk']}/100
- Clickbait score: {linguistic['clickbait_score']}/100
- Emotional manipulation: {linguistic['emotional_score']}/100
- Propaganda signals: {linguistic['propaganda_score']}/100
- Red flags: {', '.join(linguistic.get('red_flags', [])[:3])}
- Risk factors: {', '.join(risk.get('risk_factors', [])[:3])}

VERIFIED CLAIMS:
{claim_summary if claim_summary else "No claims verified."}

ORIGINAL TEXT (first 300 chars): {text[:300]}

Generate a professional, detailed explanation of WHY this verdict was reached.
Include: specific signals found, what evidence says, and confidence basis.

Return ONLY valid JSON:
{{
  "explanation": "<3-4 sentence professional explanation>",
  "reasoning_chain": [
    "<step 1: what was analyzed>",
    "<step 2: what linguistic signals were found>",
    "<step 3: what the evidence shows>",
    "<step 4: how the verdict was reached>"
  ],
  "key_signals": ["<signal1>", "<signal2>", "<signal3>"],
  "confidence_basis": "<why the AI is this confident>"
}}"""
        try:
            return call_gemini_json(prompt)
        except Exception as e:
            print(f"[ExplainabilityAgent Error] {e}")
            return self._demo_explanation(risk)


    def _demo_explanation(self, risk: dict) -> dict:
        return {
            "explanation": (
                f"The content analysis returned a fake score of {risk['fake_score']}/100, "
                f"indicating {risk['risk_level'].lower()} risk. "
                "Demo mode active — set GEMINI_API_KEY for detailed AI-powered explanation."
            ),
            "reasoning_chain": [
                "Linguistic analysis completed",
                "Claims extracted and categorized",
                "Evidence retrieval attempted",
                f"Final verdict: {risk['verdict']}",
            ],
            "key_signals": risk.get("risk_factors", [])[:3],
            "confidence_basis": "Based on linguistic pattern matching",
        }


# ─── Agent 6: Final Judge ────────────────────────────────────

class FinalJudgeAgent(Agent):
    def __init__(self):
        super().__init__("FinalJudge", "Produce final unified verdict and trust score")

    def run(self, risk: dict, explainability: dict, linguistic: dict,
            verified_claims: List[Dict]) -> dict:
        # Final confidence = mean of claim confidences weighted by risk
        claim_confidences = [c.get("confidence", 50) for c in verified_claims]
        mean_conf = int(sum(claim_confidences) / len(claim_confidences)) if claim_confidences else 65

        # If high risk + high confidence in claims → high overall confidence
        if risk["fake_score"] >= 70 and mean_conf >= 70:
            overall_conf = mean_conf
        elif risk["fake_score"] <= 30 and mean_conf >= 70:
            overall_conf = mean_conf
        else:
            overall_conf = int((mean_conf + 65) / 2)

        # Build final result
        return {
            "verdict":             risk["verdict"],
            "fake_score":          risk["fake_score"],
            "trust_score":         risk["trust_score"],
            "bias_score":          risk["bias_score"],
            "manipulation_score":  risk["manipulation_score"],
            "confidence":          overall_conf,
            "risk_level":          risk["risk_level"],
            "explanation":         explainability.get("explanation", ""),
            "reasoning_chain":     explainability.get("reasoning_chain", []),
            "key_signals":         explainability.get("key_signals", []),
            "confidence_basis":    explainability.get("confidence_basis", ""),
            "red_flags":           linguistic.get("red_flags", []),
            "linguistic_scores": {
                "clickbait":   linguistic.get("clickbait_score", 0),
                "emotional":   linguistic.get("emotional_score", 0),
                "urgency":     linguistic.get("urgency_score", 0),
                "certainty":   linguistic.get("certainty_score", 0),
                "propaganda":  linguistic.get("propaganda_score", 0),
                "credibility": linguistic.get("credibility_score", 0),
            },
            "claim_verification":  verified_claims,
            "risk_factors":        risk.get("risk_factors", []),
            "claim_stats":         risk.get("claim_stats", {}),
            "bias_direction":      self._infer_bias(linguistic),
            "fact_check_summary":  self._summarize_claims(verified_claims),
        }

    def _infer_bias(self, linguistic: dict) -> str:
        propaganda = linguistic.get("propaganda_score", 0)
        if propaganda >= 60:
            return "STRONG BIAS"
        elif propaganda >= 30:
            return "MODERATE BIAS"
        return "MINIMAL BIAS"

    def _summarize_claims(self, verified_claims: List[Dict]) -> str:
        if not verified_claims:
            return "No specific claims were extracted for verification."
        total = len(verified_claims)
        supported = sum(1 for c in verified_claims if c.get("verdict") == "SUPPORTED")
        contradicted = sum(1 for c in verified_claims if c.get("verdict") == "CONTRADICTED")
        partial = sum(1 for c in verified_claims if c.get("verdict") == "PARTIALLY_TRUE")
        unverified = total - supported - contradicted - partial
        parts = [f"{total} claim(s) analyzed: {supported} supported, {contradicted} contradicted"]
        if partial:
            parts.append(f"{partial} partially true")
        parts.append(f"{unverified} unverified")
        return ", ".join(parts) + "."


# ─── Orchestrator ─────────────────────────────────────────────

def run_multi_agent_analysis(text: str) -> dict:
    """
    Orchestrate all 6 agents to produce a complete, deep analysis.
    """
    results = {"agent_trace": []}

    # Agent 1: Extract claims
    agent1 = ClaimExtractorAgent()
    claim_result = agent1.run(text)
    claims = claim_result.get("claims", [])
    results["agent_trace"].append({"agent": agent1.name, "claims_found": len(claims)})

    # Claim clustering — detect duplicate / near-duplicate claims via embeddings
    claim_texts = [c.get("claim", "") for c in claims]
    cluster_info = cluster_claims(claim_texts) if claim_texts else \
        {"clusters": [], "cluster_count": 0, "duplicate_groups": 0}

    # Agent 2: Find evidence
    agent2 = EvidenceFinderAgent()
    evidence_result = agent2.run(claims)
    evidence_map = evidence_result.get("evidence_map", {})
    results["agent_trace"].append({"agent": agent2.name, "sources_searched": len(evidence_map)})

    # Agent 3: Fact check
    agent3 = FactCheckerAgent()
    fact_result = agent3.run(claims, evidence_map)
    verified_claims = fact_result.get("verified_claims", [])
    results["agent_trace"].append({"agent": agent3.name, "claims_verified": len(verified_claims)})

    # Linguistic analysis (parallel to agents)
    linguistic = run_linguistic_analysis(text)

    # Agent 4: Risk assessment
    agent4 = RiskAssessorAgent()
    risk = agent4.run(text, linguistic, verified_claims)
    results["agent_trace"].append({"agent": agent4.name, "risk_level": risk["risk_level"]})

    # Agent 5: Explainability
    agent5 = ExplainabilityAgent()
    explanation = agent5.run(text, risk, linguistic, verified_claims)
    results["agent_trace"].append({"agent": agent5.name, "status": "complete"})

    # Agent 6: Final judge
    agent6 = FinalJudgeAgent()
    final = agent6.run(risk, explanation, linguistic, verified_claims)
    results["agent_trace"].append({"agent": agent6.name, "verdict": final["verdict"]})

    # Merge
    results.update(final)
    results["extracted_claims"]  = claims
    results["evidence_map"]      = evidence_map
    results["primary_topic"]     = claim_result.get("primary_topic", "general")
    results["claim_density"]     = claim_result.get("claim_density", "medium")
    results["claim_clusters"]    = cluster_info

    return results
