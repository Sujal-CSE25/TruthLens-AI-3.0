"""
TruthLens Border Intelligence — Blockchain-Style Integrity Anchoring
PS 26188 · SIH 2026 PROTOTYPE — NOT FOR OPERATIONAL USE

Provides a lightweight, local cryptographic anchoring layer sitting on top of
the existing SHA-256 audit chain:
  Existing Audit Chain -> Event Hashes -> Merkle Root -> Blockchain Anchor

Properties:
  - Collects existing audit event current_hashes
  - Computes a deterministic SHA-256 Merkle Root
  - Chained anchors with previous_anchor_hash
  - Stores strictly cryptographic metadata (NO PII, NO raw document/face data)
  - 100% local SQLite-backed, no external wallet, network, or gas fees
"""
import hashlib
import uuid
from datetime import datetime
from database import db
from passport.audit_trail import verify_audit_chain

GENESIS_ANCHOR_HASH = "GENESIS_ANCHOR_00000000000000000000000000000000000000000000000000000000"


def _sha256(text: str) -> str:
    """Standard SHA-256 helper."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def compute_merkle_root(hashes: list) -> str:
    """
    Computes a deterministic pairwise SHA-256 Merkle Root from a list of hashes.
    - If hashes is empty, returns a 64-char zero string.
    - If odd number of nodes at any level, duplicates the last node.
    - Combines left + right and hashes iteratively until root is reached.
    """
    if not hashes:
        return "0" * 64

    current_level = list(hashes)
    while len(current_level) > 1:
        next_level = []
        for i in range(0, len(current_level), 2):
            left = current_level[i]
            if i + 1 < len(current_level):
                right = current_level[i + 1]
            else:
                right = left  # duplicate last node if odd
            combined_hash = _sha256(left + right)
            next_level.append(combined_hash)
        current_level = next_level

    return current_level[0]


def compute_anchor_hash(anchor_id: str, merkle_root: str, timestamp: str,
                        event_count: int, previous_anchor_hash: str) -> str:
    """
    Computes deterministic SHA-256 anchor hash over metadata fields.
    Guarantees no PII is included in the anchor hash calculation.
    """
    payload = f"{anchor_id}|{merkle_root}|{timestamp}|{event_count}|{previous_anchor_hash}"
    return _sha256(payload)


def get_blockchain_status() -> dict:
    """
    Inspects current anchor and audit chain status.
    """
    chain_status = verify_audit_chain()
    latest_anchor = db.get_last_blockchain_anchor()
    all_events = db.get_all_audit_events_ordered()

    return {
        "has_anchor": latest_anchor is not None,
        "latest_anchor": latest_anchor,
        "audit_chain_verified": chain_status.get("chain_valid", False),
        "current_audit_events_count": len(all_events),
        "notice": "Blockchain Anchor — Prototype · Local Demonstration · No External Network",
        "anchors_count": len(db.list_blockchain_anchors(limit=100)),
    }


def create_blockchain_anchor(actor: str = "system") -> dict:
    """
    Creates a new cryptographic blockchain anchor over current audit events:
    1. Reads ordered audit events from the immutable audit trail.
    2. Collects current_hash for each event.
    3. Computes the deterministic Merkle Root.
    4. Obtains the previous anchor hash (or GENESIS_ANCHOR_HASH).
    5. Calculates anchor_hash using SHA-256.
    6. Stores anchor record in blockchain_anchors table.
    """
    events = db.get_all_audit_events_ordered()
    event_hashes = [e["current_hash"] for e in events if e.get("current_hash")]

    merkle_root = compute_merkle_root(event_hashes)
    event_count = len(event_hashes)

    last_anchor = db.get_last_blockchain_anchor()
    prev_anchor_hash = last_anchor["anchor_hash"] if last_anchor else GENESIS_ANCHOR_HASH

    anchor_id = f"ANC-{uuid.uuid4().hex[:12].upper()}"
    timestamp = datetime.utcnow().isoformat() + "Z"

    anchor_hash = compute_anchor_hash(
        anchor_id=anchor_id,
        merkle_root=merkle_root,
        timestamp=timestamp,
        event_count=event_count,
        previous_anchor_hash=prev_anchor_hash,
    )

    db.append_blockchain_anchor(
        anchor_id=anchor_id,
        merkle_root=merkle_root,
        timestamp=timestamp,
        event_count=event_count,
        previous_anchor_hash=prev_anchor_hash,
        anchor_hash=anchor_hash,
        status="ANCHORED",
    )

    return {
        "anchor_id": anchor_id,
        "merkle_root": merkle_root,
        "timestamp": timestamp,
        "event_count": event_count,
        "previous_anchor_hash": prev_anchor_hash,
        "anchor_hash": anchor_hash,
        "status": "ANCHORED",
        "notice": "Blockchain Anchor — Prototype · Local Demonstration · No External Network",
    }


def verify_blockchain_anchor(anchor_id: str = None) -> dict:
    """
    Independently verifies a blockchain anchor by recomputing:
    1. Re-fetches the anchor from the database.
    2. Re-fetches the audit events up to event_count.
    3. Re-computes the Merkle Root from the events' current_hashes.
    4. Re-computes the anchor_hash from metadata.
    5. Compares computed values against stored values.
    """
    if anchor_id:
        anchors = [a for a in db.list_blockchain_anchors(limit=100) if a["anchor_id"] == anchor_id]
        anchor = anchors[0] if anchors else None
    else:
        anchor = db.get_last_blockchain_anchor()

    if not anchor:
        return {
            "verified": False,
            "event_count": 0,
            "merkle_root": None,
            "anchor_hash": None,
            "timestamp": None,
            "details": "No integrity anchor found to verify.",
            "notice": "Blockchain Anchor — Prototype · Local Demonstration · No External Network",
        }

    # Fetch audit events up to anchored event count
    all_events = db.get_all_audit_events_ordered()
    anchored_events = all_events[:anchor["event_count"]]
    event_hashes = [e["current_hash"] for e in anchored_events if e.get("current_hash")]

    recomputed_merkle_root = compute_merkle_root(event_hashes)
    recomputed_anchor_hash = compute_anchor_hash(
        anchor_id=anchor["anchor_id"],
        merkle_root=recomputed_merkle_root,
        timestamp=anchor["timestamp"],
        event_count=anchor["event_count"],
        previous_anchor_hash=anchor["previous_anchor_hash"],
    )

    merkle_valid = (recomputed_merkle_root == anchor["merkle_root"])
    hash_valid = (recomputed_anchor_hash == anchor["anchor_hash"])
    chain_status = verify_audit_chain()

    is_verified = merkle_valid and hash_valid and chain_status.get("chain_valid", False)

    return {
        "verified": is_verified,
        "event_count": anchor["event_count"],
        "merkle_root": anchor["merkle_root"],
        "anchor_hash": anchor["anchor_hash"],
        "timestamp": anchor["timestamp"],
        "recomputed_merkle_root": recomputed_merkle_root,
        "recomputed_anchor_hash": recomputed_anchor_hash,
        "merkle_root_matches": merkle_valid,
        "anchor_hash_matches": hash_valid,
        "underlying_chain_verified": chain_status.get("chain_valid", False),
        "details": (
            f"Integrity verified: Merkle Root matches {anchor['event_count']} audit events. "
            f"Anchor cryptographic hash is authentic."
            if is_verified else
            "Verification failure: Recomputed Merkle root or anchor hash does not match stored anchor."
        ),
        "notice": "Blockchain Anchor — Prototype · Local Demonstration · No External Network",
    }
