"""
TruthLens AI 2.0 — Explainability Module
Builds a structured explainability report for every verdict:
Evidence, Confidence, Reasoning Chain, Supporting Sources, Risk Factors, Trust Score.
"""


def build_explainability_report(result: dict) -> dict:
    """
    Assemble a unified explainability report from a multi-agent analysis result.

    This is the canonical "show your work" structure required for every
    verdict — used by the Detection UI and stored alongside the analysis.

    Returns:
        {
          "trust_score":       int,
          "confidence":        int,
          "verdict":           str,
          "reasoning_chain":   [str, ...],
          "risk_factors":      [str, ...],
          "supporting_sources": [{"title", "url", "source", "relevance"}],
          "evidence_summary":  str,
          "claim_breakdown": {
              "total": int, "supported": int,
              "contradicted": int, "unverified": int
          },
          "duplicate_claims_detected": int,
        }
    """
    evidence_map   = result.get("evidence_map", {})
    claim_stats    = result.get("claim_stats", {})
    cluster_info   = result.get("claim_clusters", {})

    # Flatten supporting sources from evidence map (deduplicated by URL)
    seen_urls = set()
    sources = []
    for entry in evidence_map.values():
        for ev in entry.get("evidence", []):
            url = ev.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                sources.append({
                    "title":     ev.get("title", "Untitled"),
                    "url":       url,
                    "source":    ev.get("source", "Web"),
                    "relevance": ev.get("relevance", 0),
                })
    sources.sort(key=lambda x: x["relevance"], reverse=True)

    evidence_summary = (
        f"{len(sources)} unique source(s) retrieved across "
        f"{len(evidence_map)} claim(s)."
        if evidence_map else
        "No external evidence was retrieved for this content."
    )

    duplicate_groups = cluster_info.get("duplicate_groups", 0)

    return {
        "trust_score":       result.get("trust_score", 0),
        "confidence":        result.get("confidence", 0),
        "verdict":           result.get("verdict", "UNCERTAIN"),
        "reasoning_chain":   result.get("reasoning_chain", []),
        "risk_factors":      result.get("risk_factors", []),
        "supporting_sources": sources[:8],
        "evidence_summary":  evidence_summary,
        "claim_breakdown":   {
            "total":        claim_stats.get("total", 0),
            "supported":    claim_stats.get("supported", 0),
            "contradicted": claim_stats.get("contradicted", 0),
            "unverified":   claim_stats.get("unverified", 0),
        },
        "duplicate_claims_detected": duplicate_groups,
        "confidence_basis":  result.get("confidence_basis", ""),
    }


def build_image_explainability_report(result: dict) -> dict:
    """
    Equivalent explainability report for image / deepfake analysis.
    """
    forensic = result.get("forensic_detail", {})

    reasoning_chain = [
        f"Error Level Analysis scored {forensic.get('ela', {}).get('manipulation_score', 0)}/100 "
        f"for re-compression anomalies.",
        f"EXIF metadata analysis scored {forensic.get('exif', {}).get('anomaly_score', 0)}/100 "
        f"for tampering indicators.",
        f"Noise consistency analysis scored {forensic.get('noise', {}).get('noise_score', 0)}/100.",
        f"Compression artifact analysis scored {forensic.get('compression', {}).get('compression_score', 0)}/100.",
        f"Edge sharpness analysis scored {forensic.get('edge', {}).get('edge_score', 0)}/100.",
        f"Gemini Vision AI cross-checked all local signals and produced a final "
        f"verdict of {result.get('verdict', 'UNCERTAIN')}.",
    ]

    return {
        "trust_score":      result.get("authenticity_score", 0),
        "confidence":       result.get("confidence", 0),
        "verdict":          result.get("verdict", "UNCERTAIN"),
        "reasoning_chain":  reasoning_chain,
        "risk_factors":     result.get("findings", []),
        "supporting_sources": [],
        "evidence_summary": "Forensic signals computed locally; no external sources used for image analysis.",
        "claim_breakdown":  {},
        "duplicate_claims_detected": 0,
        "confidence_basis": "Weighted combination of 5 local forensic signals and Gemini Vision AI.",
    }
