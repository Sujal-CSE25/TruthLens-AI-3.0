"""
TruthLens Border Intelligence — Audit Trail
Append-only tamper-evident hash chain.

CHAIN INTEGRITY:
  current_hash = SHA256(canonical_JSON(event_payload) + previous_hash)
  
  Changing ANY past event makes verify_audit_chain() return False
  for all subsequent events.

This is NOT a blockchain. It is a simple SHA-256 hash chain
stored in SQLite. It provides:
  - Append-only audit log
  - Tamper detection on historical records
  - Traceable event timeline per screening

SIH 2026 · PS 26188 · PROTOTYPE — NOT FOR OPERATIONAL USE
"""
import json
import hashlib
import uuid
from datetime import datetime
from database import db

GENESIS_HASH = "GENESIS"


# ─── Event Types ─────────────────────────────────────────────

class AuditEventType:
    SCREENING_STARTED   = "SCREENING_STARTED"
    OCR_COMPLETE        = "OCR_COMPLETE"
    MRZ_CHECKED         = "MRZ_CHECKED"
    VALIDATION_COMPLETE = "VALIDATION_COMPLETE"
    FORENSICS_COMPLETE  = "FORENSICS_COMPLETE"
    FACE_CHECKED        = "FACE_CHECKED"
    IDENTITY_CHECKED    = "IDENTITY_CHECKED"
    REGISTRY_CHECKED    = "REGISTRY_CHECKED"
    RISK_ASSESSED       = "RISK_ASSESSED"
    SCREENING_COMPLETE  = "SCREENING_COMPLETE"
    OFFICER_REVIEW      = "OFFICER_REVIEW"
    SCREENING_ERROR     = "SCREENING_ERROR"


# ─── Hash Functions ───────────────────────────────────────────

def _canonical_json(data: dict) -> str:
    """Deterministic JSON serialization (sorted keys, no whitespace)."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, default=str)


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _compute_payload_hash(event_data: dict) -> str:
    """SHA256 of the canonical event payload."""
    return _sha256(_canonical_json(event_data))


def _compute_chain_hash(payload_hash: str, previous_hash: str) -> str:
    """SHA256(payload_hash + previous_hash)."""
    return _sha256(payload_hash + previous_hash)


# ─── Log Event ───────────────────────────────────────────────

def log_audit_event(screening_id: str,
                     event_type: str,
                     actor: str,
                     payload: dict) -> str:
    """
    Append a tamper-evident event to the audit chain.

    Returns the event_id of the created event.
    """
    event_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat() + "Z"

    # Canonical event payload (excludes hash fields — they're computed)
    event_data = {
        "event_id":    event_id,
        "screening_id": screening_id,
        "actor":       actor,
        "event_type":  event_type,
        "timestamp":   timestamp,
        "payload":     payload,
    }

    payload_hash   = _compute_payload_hash(event_data)
    previous_hash  = db.get_last_audit_hash()
    current_hash   = _compute_chain_hash(payload_hash, previous_hash)

    db.append_audit_event(
        event_id=event_id,
        screening_id=screening_id,
        actor=actor,
        event_type=event_type,
        payload_hash=payload_hash,
        previous_hash=previous_hash,
        current_hash=current_hash,
    )

    return event_id


# ─── Verify Chain ─────────────────────────────────────────────

def verify_audit_chain() -> dict:
    """
    Walk the entire audit chain and verify every hash link.

    Returns:
      {
        "chain_valid": bool,
        "total_events": int,
        "first_broken_at": int | None,  # event index (1-based) where chain breaks
        "broken_event_id": str | None,
        "events_verified": int,
        "summary": str
      }
    """
    events = db.get_all_audit_events_ordered()

    if not events:
        return {
            "chain_valid":      True,
            "total_events":     0,
            "first_broken_at":  None,
            "broken_event_id":  None,
            "events_verified":  0,
            "summary":          "Audit chain is empty",
        }

    prev_hash = GENESIS_HASH
    for i, event in enumerate(events):
        stored_prev     = event["previous_hash"]
        stored_payload  = event["payload_hash"]
        stored_current  = event["current_hash"]

        # Verify previous_hash matches what we tracked
        if stored_prev != prev_hash:
            return {
                "chain_valid":      False,
                "total_events":     len(events),
                "first_broken_at":  i + 1,
                "broken_event_id":  event["event_id"],
                "events_verified":  i,
                "summary": (
                    f"Chain broken at event #{i+1} (id: {event['event_id']}). "
                    f"Expected previous_hash={prev_hash[:16]}..., "
                    f"found {stored_prev[:16]}..."
                ),
            }

        # Verify current_hash
        expected_current = _compute_chain_hash(stored_payload, stored_prev)
        if expected_current != stored_current:
            return {
                "chain_valid":      False,
                "total_events":     len(events),
                "first_broken_at":  i + 1,
                "broken_event_id":  event["event_id"],
                "events_verified":  i,
                "summary": (
                    f"Hash mismatch at event #{i+1} (id: {event['event_id']}). "
                    "Stored hash does not match recomputed hash — event data may have been modified."
                ),
            }

        prev_hash = stored_current

    return {
        "chain_valid":      True,
        "total_events":     len(events),
        "first_broken_at":  None,
        "broken_event_id":  None,
        "events_verified":  len(events),
        "summary":          f"Audit chain is intact — all {len(events)} events verified",
    }


# ─── Helper: Log Screening Pipeline ──────────────────────────

def log_screening_start(screening_id: str, actor: str = "system",
                          document_type: str = "passport") -> str:
    return log_audit_event(
        screening_id=screening_id,
        event_type=AuditEventType.SCREENING_STARTED,
        actor=actor,
        payload={"document_type": document_type},
    )


def log_risk_assessment(screening_id: str, risk_level: str,
                          risk_score: int, actor: str = "system") -> str:
    return log_audit_event(
        screening_id=screening_id,
        event_type=AuditEventType.RISK_ASSESSED,
        actor=actor,
        payload={"risk_level": risk_level, "risk_score": risk_score},
    )


def log_screening_complete(screening_id: str, risk_level: str,
                             actor: str = "system") -> str:
    return log_audit_event(
        screening_id=screening_id,
        event_type=AuditEventType.SCREENING_COMPLETE,
        actor=actor,
        payload={"risk_level": risk_level},
    )
