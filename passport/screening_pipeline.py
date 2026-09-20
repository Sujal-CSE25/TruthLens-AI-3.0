"""
TruthLens Border Intelligence — Passport Screening Pipeline
Master pipeline that orchestrates all modules.

Flow:
  image_bytes → OCR → MRZ → Validation → Forensics → Face → Identity → Registry
  → Evidence Fusion → Risk Engine → Audit Trail → Result

SIH 2026 · PS 26188 · PROTOTYPE — NOT FOR OPERATIONAL USE
"""
import uuid
import hashlib
from datetime import datetime

from passport.ocr_engine import run_passport_ocr
from passport.document_validator import run_document_validation
from passport.mrz_engine import run_mrz_pipeline
from passport.face_verifier import compare_faces
from passport.identity_intelligence import analyze_identity_consistency
from passport.registry_adapter import run_all_registry_checks
from passport.evidence_fusion import fuse_evidence
from passport.risk_engine import calculate_risk
from passport.audit_trail import (
    log_screening_start, log_risk_assessment, log_screening_complete,
    log_audit_event, AuditEventType
)
from forensics.image_forensics import run_full_image_forensics, generate_forensic_heatmap_b64
from forensics.document_tamper import generate_tamper_evidence_map
from database import db


def run_passport_screening(
    document_image_bytes: bytes,
    probe_image_bytes: bytes = None,
    actor: str = "system",
    demo_case: str = None,
) -> dict:
    """
    Run the complete passport screening pipeline.

    Args:
        document_image_bytes: passport image bytes
        probe_image_bytes:    optional live photo for face comparison
        actor:                officer ID or 'system'
        demo_case:            demo case label if this is a demo run

    Returns: complete screening result with all module outputs
    """
    screening_id = str(uuid.uuid4())
    started_at   = datetime.utcnow().isoformat() + "Z"

    # ── Audit: Screening Started ──────────────────────────────
    log_screening_start(screening_id, actor=actor)

    result = {
        "screening_id":  screening_id,
        "document_type": "passport",
        "started_at":    started_at,
        "actor":         actor,
        "demo_case":     demo_case,
        "prototype_notice": "SIH 2026 PROTOTYPE — NOT FOR OPERATIONAL USE",
    }

    try:
        # ── Step 1: OCR ───────────────────────────────────────
        ocr_result = run_passport_ocr(document_image_bytes)
        result["ocr"] = {
            "ocr_text":       ocr_result.get("ocr_text", ""),
            "ocr_confidence": ocr_result.get("ocr_confidence", 0),
            "fields":         ocr_result.get("fields", {}),
            "warnings":       ocr_result.get("warnings", []),
        }
        log_audit_event(
            screening_id=screening_id,
            event_type=AuditEventType.OCR_COMPLETE,
            actor=actor,
            payload={
                "confidence": ocr_result.get("ocr_confidence", 0),
                "warnings":   len(ocr_result.get("warnings", [])),
            },
        )

        # ── Step 2: MRZ ───────────────────────────────────────
        mrz_result = ocr_result.get("mrz", {})
        result["mrz"] = mrz_result
        log_audit_event(
            screening_id=screening_id,
            event_type=AuditEventType.MRZ_CHECKED,
            actor=actor,
            payload={
                "detected":       mrz_result.get("mrz_detected", False),
                "checks_passed":  mrz_result.get("summary", {}).get("checks_passed", 0),
                "checks_total":   mrz_result.get("summary", {}).get("checks_total", 0),
                "risk_contribution": mrz_result.get("summary", {}).get("risk_contribution", "UNKNOWN"),
            },
        )

        # ── Step 3: Document Validation ───────────────────────
        validation_result = run_document_validation(ocr_result)
        result["validation"] = validation_result
        log_audit_event(
            screening_id=screening_id,
            event_type=AuditEventType.VALIDATION_COMPLETE,
            actor=actor,
            payload={
                "rules_passed": validation_result.get("rules_passed", 0),
                "rules_run":    validation_result.get("rules_run", 0),
                "validation_score": validation_result.get("validation_score", 0),
            },
        )

        # ── Step 4: Image Forensics ───────────────────────────
        forensics_result = run_full_image_forensics(document_image_bytes)
        heatmap_result   = generate_forensic_heatmap_b64(document_image_bytes)
        tamper_result    = generate_tamper_evidence_map(document_image_bytes, forensics_result)
        result["forensics"] = forensics_result
        result["heatmap"]   = heatmap_result
        result["tamper"]    = tamper_result
        log_audit_event(
            screening_id=screening_id,
            event_type=AuditEventType.FORENSICS_COMPLETE,
            actor=actor,
            payload={
                "manipulation_score": forensics_result.get("manipulation_score", 0),
                "tamper_score":       tamper_result.get("tamper_score", 0),
                "suspicious_regions": len(tamper_result.get("suspicious_regions", [])),
            },
        )

        # ── Step 5: Face Verification ─────────────────────────
        face_result = compare_faces(document_image_bytes, probe_image_bytes)
        result["face_verification"] = face_result
        log_audit_event(
            screening_id=screening_id,
            event_type=AuditEventType.FACE_CHECKED,
            actor=actor,
            payload={
                "result":     face_result.get("result", "UNAVAILABLE"),
                "similarity": face_result.get("similarity"),
            },
        )

        # ── Step 6: Identity Intelligence ─────────────────────
        fields = ocr_result.get("fields", {})
        mrz_parsed = mrz_result.get("parsed", {})
        passport_number = (mrz_parsed.get("passport_number_mrz") or
                           fields.get("passport_number_visual", "") or
                           fields.get("passport_number", ""))
        surname = mrz_parsed.get("surname_mrz") or fields.get("surname_visual", "")
        given_names = mrz_parsed.get("given_names_mrz") or fields.get("given_names_visual", "")
        name = f"{surname} {given_names}".strip() if (surname or given_names) else fields.get("name", "")
        dob  = (mrz_parsed.get("dob_mrz_parsed") or fields.get("dob_visual", "") or fields.get("dob", ""))
        expiry = (mrz_parsed.get("expiry_mrz_parsed") or fields.get("expiry_visual", "") or fields.get("expiry", ""))
        nationality = (mrz_parsed.get("nationality_mrz") or fields.get("nationality_visual", "") or fields.get("nationality", ""))
        gender = (mrz_parsed.get("gender_mrz") or fields.get("gender_visual", "") or fields.get("gender", ""))

        identity_record = {
            "passport_number": passport_number,
            "name":            name,
            "surname":         surname,
            "given_names":     given_names,
            "dob":             dob,
            "expiry":          expiry,
            "nationality":     nationality,
            "gender":          gender,
        }
        result["identity_record"] = identity_record
        validation_result["passport_number"] = passport_number
        validation_result["name"] = name
        validation_result["dob"] = dob
        validation_result["expiry"] = expiry
        validation_result["nationality"] = nationality
        validation_result["gender"] = gender

        identity_result = analyze_identity_consistency(
            passport_number=passport_number,
            name=name,
            dob=dob,
            nationality=nationality,
        )
        result["identity"] = identity_result
        log_audit_event(
            screening_id=screening_id,
            event_type=AuditEventType.IDENTITY_CHECKED,
            actor=actor,
            payload={
                "status": identity_result.get("status", "NO_CONCERN"),
                "flags":  len(identity_result.get("flags", [])),
            },
        )

        # ── Step 7: Registry Checks ───────────────────────────
        registry_result = run_all_registry_checks(
            passport_number=passport_number,
            name=name,
            nationality=nationality,
        )
        result["registry"] = registry_result
        log_audit_event(
            screening_id=screening_id,
            event_type=AuditEventType.REGISTRY_CHECKED,
            actor=actor,
            payload={
                "watchlist_hit":   registry_result.get("watchlist", {}).get("match_found", False),
                "passport_status": registry_result.get("passport", {}).get("status", "UNKNOWN"),
            },
        )

        # ── Step 8: Evidence Fusion ───────────────────────────
        fused = fuse_evidence(
            ocr_result=ocr_result,
            mrz_result=mrz_result,
            validation_result=validation_result,
            forensics_result=forensics_result,
            tamper_result=tamper_result,
            face_result=face_result,
            identity_result=identity_result,
            registry_result=registry_result,
        )
        result["fused_evidence"] = fused

        # ── Step 9: Risk Assessment ───────────────────────────
        risk_result = calculate_risk(fused)
        result["risk"] = risk_result
        result["risk_level"] = risk_result["risk_level"]
        result["risk_score"]  = risk_result["risk_score"]
        result["verdict"]     = risk_result["verdict"]

        log_risk_assessment(
            screening_id=screening_id,
            risk_level=risk_result["risk_level"],
            risk_score=risk_result["risk_score"],
            actor=actor,
        )

        # ── Step 10: Persist Person Record ────────────────────
        if passport_number:
            face_hash = ""
            try:
                import hashlib, json
                # Store hash of passport_number+name as a proxy person_id
                person_id = hashlib.sha256(
                    f"{passport_number}:{name}:{dob}".encode()
                ).hexdigest()[:32]
                db.upsert_screening_person(
                    person_id=person_id,
                    passport_number=passport_number,
                    name=name,
                    dob=dob,
                    nationality=nationality,
                    gender=gender,
                    face_hash=face_hash,
                    screening_id=screening_id,
                )
            except Exception:
                pass

        # ── Step 11: Save Screening ───────────────────────────
        db.save_screening(
            screening_id=screening_id,
            result=result,
            actor=actor,
            demo_case=demo_case,
        )

        # ── Audit: Complete ───────────────────────────────────
        log_screening_complete(screening_id, risk_result["risk_level"], actor=actor)

        result["completed_at"] = datetime.utcnow().isoformat() + "Z"
        result["status"] = "complete"

    except Exception as e:
        import traceback
        result["status"] = "error"
        result["error"]  = str(e)
        result["risk_level"] = "MANUAL_REVIEW"
        result["risk_score"]  = 50
        result["verdict"]     = "Screening error — manual review required"
        log_audit_event(
            screening_id=screening_id,
            event_type=AuditEventType.SCREENING_ERROR,
            actor=actor,
            payload={"error": str(e)},
        )
        db.save_screening(screening_id=screening_id, result=result, actor=actor)

    return result
