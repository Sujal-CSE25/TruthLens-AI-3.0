import os
import sqlite3
import json
from datetime import datetime
from utils.config import DATABASE_PATH
from utils.helpers import ts_now

_db_initialized = False

# ─── Connection ───────────────────────────────────────────────

def get_conn():
    global DATABASE_PATH, _db_initialized
    
    # Ensure directory exists if path is specified
    db_dir = os.path.dirname(DATABASE_PATH)
    if db_dir:
        try:
            os.makedirs(db_dir, exist_ok=True)
        except Exception:
            pass

    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    except sqlite3.OperationalError:
        # Fallback for serverless environments (Vercel / Lambda) where current dir is read-only
        DATABASE_PATH = "/tmp/truthlens.db"
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)

    conn.row_factory = sqlite3.Row

    if not _db_initialized:
        init_database(conn)
        _db_initialized = True

    return conn


# ─── Init ─────────────────────────────────────────────────────

def init_database(existing_conn=None):
    """Create all tables if they do not exist."""
    global _db_initialized

    ddl = """
    CREATE TABLE IF NOT EXISTS users (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id  TEXT    UNIQUE NOT NULL,
        created_at  TEXT    DEFAULT (datetime('now','utc')),
        last_seen   TEXT    DEFAULT (datetime('now','utc'))
    );

    CREATE TABLE IF NOT EXISTS analyses (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        analysis_id TEXT    UNIQUE NOT NULL,
        type        TEXT    NOT NULL,          -- 'text' | 'image' | 'document'
        input_hash  TEXT    NOT NULL,
        verdict     TEXT,
        fake_score  REAL,
        confidence  REAL,
        result_json TEXT,
        created_at  TEXT    DEFAULT (datetime('now','utc'))
    );

    CREATE TABLE IF NOT EXISTS claims (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        analysis_id TEXT    NOT NULL,
        claim_text  TEXT    NOT NULL,
        verdict     TEXT,
        confidence  REAL,
        sources     TEXT,                      -- JSON list
        created_at  TEXT    DEFAULT (datetime('now','utc'))
    );

    CREATE TABLE IF NOT EXISTS evidence (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        claim_id    INTEGER NOT NULL,
        source_url  TEXT,
        source_title TEXT,
        snippet     TEXT,
        relevance   REAL,
        supports    INTEGER,                   -- 1=supports, 0=contradicts, -1=unknown
        created_at  TEXT    DEFAULT (datetime('now','utc')),
        FOREIGN KEY (claim_id) REFERENCES claims(id)
    );

    CREATE TABLE IF NOT EXISTS feedback (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        analysis_id TEXT    NOT NULL,
        is_correct  INTEGER NOT NULL,          -- 1=correct, 0=incorrect
        user_note   TEXT,
        created_at  TEXT    DEFAULT (datetime('now','utc'))
    );

    CREATE TABLE IF NOT EXISTS documents (
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        doc_id         TEXT UNIQUE NOT NULL,
        doc_type       TEXT,
        authenticity   REAL,
        forgery_score  REAL,
        ocr_text       TEXT,
        result_json    TEXT,
        created_at     TEXT DEFAULT (datetime('now','utc'))
    );

    CREATE TABLE IF NOT EXISTS model_versions (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        version     TEXT NOT NULL,
        accuracy    REAL,
        samples     INTEGER,
        notes       TEXT,
        created_at  TEXT DEFAULT (datetime('now','utc'))
    );

    CREATE TABLE IF NOT EXISTS analytics_events (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        event       TEXT NOT NULL,
        payload     TEXT,
        created_at  TEXT DEFAULT (datetime('now','utc'))
    );

    -- ── PS 26188: Screening tables ────────────────────────────────
    CREATE TABLE IF NOT EXISTS screenings (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        screening_id    TEXT    UNIQUE NOT NULL,
        document_type   TEXT    DEFAULT 'passport',
        risk_level      TEXT,                    -- CLEAR | MANUAL_REVIEW | HIGH_RISK
        risk_score      REAL,
        verdict         TEXT,
        actor           TEXT,                    -- officer / system
        demo_case       TEXT,                    -- NULL or demo case ID
        result_json     TEXT,                    -- full pipeline result
        created_at      TEXT    DEFAULT (datetime('now','utc'))
    );

    CREATE TABLE IF NOT EXISTS screening_persons (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        person_id       TEXT    UNIQUE NOT NULL,
        passport_number TEXT,
        name_visual     TEXT,
        dob_visual      TEXT,
        nationality     TEXT,
        gender          TEXT,
        face_embedding_hash TEXT,               -- SHA256 of embedding vector (not the vector itself)
        linked_screenings   TEXT,               -- JSON list of screening_ids
        created_at      TEXT    DEFAULT (datetime('now','utc'))
    );

    -- Append-only tamper-evident audit chain
    CREATE TABLE IF NOT EXISTS audit_events (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id        TEXT    UNIQUE NOT NULL,
        screening_id    TEXT,
        actor           TEXT,
        event_type      TEXT    NOT NULL,        -- SCREENING_STARTED | OCR_COMPLETE | MRZ_CHECKED | etc.
        payload_hash    TEXT    NOT NULL,        -- SHA256 of canonical event JSON
        previous_hash   TEXT    NOT NULL,        -- hash of previous row (GENESIS for first)
        current_hash    TEXT    NOT NULL,        -- SHA256(payload_hash + previous_hash)
        created_at      TEXT    DEFAULT (datetime('now','utc'))
    );

    CREATE INDEX IF NOT EXISTS idx_analyses_type ON analyses(type);
    CREATE INDEX IF NOT EXISTS idx_analyses_verdict ON analyses(verdict);
    CREATE INDEX IF NOT EXISTS idx_feedback_aid ON feedback(analysis_id);
    CREATE INDEX IF NOT EXISTS idx_evidence_claim ON evidence(claim_id);
    CREATE INDEX IF NOT EXISTS idx_claims_analysis ON claims(analysis_id);
    CREATE INDEX IF NOT EXISTS idx_screenings_risk ON screenings(risk_level);
    CREATE INDEX IF NOT EXISTS idx_audit_screening ON audit_events(screening_id);
    CREATE INDEX IF NOT EXISTS idx_persons_passport ON screening_persons(passport_number);

    -- Blockchain-style integrity anchors (PS 26188)
    CREATE TABLE IF NOT EXISTS blockchain_anchors (
        id                   INTEGER PRIMARY KEY AUTOINCREMENT,
        anchor_id            TEXT UNIQUE NOT NULL,
        merkle_root          TEXT NOT NULL,
        timestamp            TEXT NOT NULL,
        event_count          INTEGER NOT NULL,
        previous_anchor_hash TEXT NOT NULL,
        anchor_hash          TEXT NOT NULL,
        status               TEXT NOT NULL,
        created_at           TEXT DEFAULT (datetime('now','utc'))
    );
    CREATE INDEX IF NOT EXISTS idx_anchor_id ON blockchain_anchors(anchor_id);
    """
    if existing_conn is not None:
        existing_conn.executescript(ddl)
    else:
        with get_conn() as conn:
            conn.executescript(ddl)
    _db_initialized = True



# ─── User Tracking ────────────────────────────────────────────

def get_or_create_user(session_id: str) -> None:
    """Register a session as a 'user' row, updating last_seen on repeat visits."""
    with get_conn() as conn:
        existing = conn.execute(
            "SELECT id FROM users WHERE session_id=?", (session_id,)
        ).fetchone()
        if existing:
            conn.execute(
                "UPDATE users SET last_seen=datetime('now','utc') WHERE session_id=?",
                (session_id,),
            )
        else:
            conn.execute(
                "INSERT INTO users (session_id) VALUES (?)", (session_id,)
            )


def get_user_count() -> int:
    with get_conn() as conn:
        return conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]


# ─── Analysis CRUD ────────────────────────────────────────────

def save_analysis(analysis_id: str, analysis_type: str, input_hash: str, result: dict) -> None:
    sql = """
        INSERT OR REPLACE INTO analyses
            (analysis_id, type, input_hash, verdict, fake_score, confidence, result_json)
        VALUES (?,?,?,?,?,?,?)
    """
    with get_conn() as conn:
        conn.execute(sql, (
            analysis_id,
            analysis_type,
            input_hash,
            result.get("verdict", ""),
            result.get("fake_score", result.get("ai_generated_score", 0)),
            result.get("confidence", 0),
            json.dumps(result),
        ))


def get_analyses_stats() -> dict:
    with get_conn() as conn:
        total   = conn.execute("SELECT COUNT(*) FROM analyses").fetchone()[0]
        fake    = conn.execute("SELECT COUNT(*) FROM analyses WHERE fake_score >= 70").fetchone()[0]
        docs    = conn.execute("SELECT COUNT(*) FROM analyses WHERE type='document'").fetchone()[0]
        images  = conn.execute("SELECT COUNT(*) FROM analyses WHERE type='image'").fetchone()[0]
        texts   = conn.execute("SELECT COUNT(*) FROM analyses WHERE type='text'").fetchone()[0]
        fb_total= conn.execute("SELECT COUNT(*) FROM feedback").fetchone()[0]
        fb_ok   = conn.execute("SELECT COUNT(*) FROM feedback WHERE is_correct=1").fetchone()[0]
        accuracy = round((fb_ok / fb_total * 100), 1) if fb_total else 0
        recent  = conn.execute(
            "SELECT verdict, fake_score, type, created_at FROM analyses ORDER BY id DESC LIMIT 20"
        ).fetchall()
        return {
            "total": total, "fake": fake, "docs": docs,
            "images": images, "texts": texts,
            "fb_total": fb_total, "fb_ok": fb_ok, "accuracy": accuracy,
            "recent": [dict(r) for r in recent],
        }


# ─── Claims & Evidence CRUD ──────────────────────────────────

def save_claims(analysis_id: str, claims: list, evidence_map: dict = None) -> None:
    """
    Persist claims and, if provided, link retrieved evidence to each claim.

    evidence_map keys are expected as 'claim_0', 'claim_1', ... matching
    the order of `claims` (as produced by agents/multi_agent.py).
    """
    sql = """
        INSERT INTO claims (analysis_id, claim_text, verdict, confidence, sources)
        VALUES (?,?,?,?,?)
    """
    evidence_sql = """
        INSERT INTO evidence (claim_id, source_url, source_title, snippet, relevance, supports)
        VALUES (?,?,?,?,?,?)
    """
    with get_conn() as conn:
        for i, c in enumerate(claims):
            cur = conn.execute(sql, (
                analysis_id,
                c.get("claim", ""),
                c.get("verdict", ""),
                c.get("confidence", 0),
                json.dumps(c.get("sources", [])),
            ))
            claim_id = cur.lastrowid

            if evidence_map:
                entry = evidence_map.get(f"claim_{i}", {})
                verdict = (c.get("verdict") or "").upper()
                supports = 1 if verdict == "SUPPORTED" else (0 if verdict == "CONTRADICTED" else -1)
                for ev in entry.get("evidence", [])[:5]:
                    conn.execute(evidence_sql, (
                        claim_id,
                        ev.get("url", ""),
                        ev.get("title", ""),
                        ev.get("snippet", "")[:500],
                        ev.get("relevance", 0),
                        supports,
                    ))


def get_evidence_for_analysis(analysis_id: str) -> list:
    """Fetch all evidence rows linked to claims for a given analysis."""
    sql = """
        SELECT e.source_url, e.source_title, e.snippet, e.relevance, e.supports, c.claim_text
        FROM evidence e
        JOIN claims c ON c.id = e.claim_id
        WHERE c.analysis_id = ?
        ORDER BY e.relevance DESC
    """
    with get_conn() as conn:
        rows = conn.execute(sql, (analysis_id,)).fetchall()
    return [dict(r) for r in rows]


# ─── Feedback CRUD ────────────────────────────────────────────

def save_feedback(analysis_id: str, is_correct: bool, user_note: str = "") -> None:
    sql = "INSERT INTO feedback (analysis_id, is_correct, user_note) VALUES (?,?,?)"
    with get_conn() as conn:
        conn.execute(sql, (analysis_id, 1 if is_correct else 0, user_note))
    # Log analytics event
    log_event("feedback_submitted", {"analysis_id": analysis_id, "correct": is_correct})


# ─── Document CRUD ───────────────────────────────────────────

def save_document(doc_id: str, doc_type: str, result: dict) -> None:
    sql = """
        INSERT OR REPLACE INTO documents
            (doc_id, doc_type, authenticity, forgery_score, ocr_text, result_json)
        VALUES (?,?,?,?,?,?)
    """
    with get_conn() as conn:
        conn.execute(sql, (
            doc_id,
            doc_type,
            result.get("authenticity_score", 0),
            result.get("forgery_score", 0),
            result.get("ocr_text", ""),
            json.dumps(result),
        ))


# ─── Analytics ───────────────────────────────────────────────

def log_event(event: str, payload: dict = None) -> None:
    sql = "INSERT INTO analytics_events (event, payload) VALUES (?,?)"
    with get_conn() as conn:
        conn.execute(sql, (event, json.dumps(payload or {})))


def get_daily_counts(days: int = 30) -> list:
    sql = """
        SELECT date(created_at) as day, COUNT(*) as cnt
        FROM analyses
        WHERE created_at >= date('now', ?)
        GROUP BY day ORDER BY day
    """
    with get_conn() as conn:
        rows = conn.execute(sql, (f"-{days} days",)).fetchall()
        return [{"day": r["day"], "count": r["cnt"]} for r in rows]


# ─── Screening CRUD (PS 26188) ───────────────────────────────

def save_screening(screening_id: str, result: dict, actor: str = "system",
                   demo_case: str = None) -> None:
    sql = """
        INSERT OR REPLACE INTO screenings
            (screening_id, document_type, risk_level, risk_score,
             verdict, actor, demo_case, result_json)
        VALUES (?,?,?,?,?,?,?,?)
    """
    with get_conn() as conn:
        conn.execute(sql, (
            screening_id,
            result.get("document_type", "passport"),
            result.get("risk_level", "MANUAL_REVIEW"),
            result.get("risk_score", 50),
            result.get("verdict", ""),
            actor,
            demo_case,
            json.dumps(result),
        ))


def get_screening(screening_id: str) -> dict | None:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM screenings WHERE screening_id=?", (screening_id,)
        ).fetchone()
    if not row:
        return None
    r = dict(row)
    try:
        r["result"] = json.loads(r.get("result_json") or "{}")
    except Exception:
        r["result"] = {}
    return r


def list_screenings(limit: int = 20, offset: int = 0,
                    risk_level: str = None) -> list:
    if risk_level:
        sql = ("SELECT screening_id, document_type, risk_level, risk_score, "
               "actor, demo_case, created_at FROM screenings "
               "WHERE risk_level=? ORDER BY id DESC LIMIT ? OFFSET ?")
        args = (risk_level, limit, offset)
    else:
        sql = ("SELECT screening_id, document_type, risk_level, risk_score, "
               "actor, demo_case, created_at FROM screenings "
               "ORDER BY id DESC LIMIT ? OFFSET ?")
        args = (limit, offset)
    with get_conn() as conn:
        rows = conn.execute(sql, args).fetchall()
    return [dict(r) for r in rows]


def upsert_screening_person(person_id: str, passport_number: str,
                             name: str, dob: str, nationality: str,
                             gender: str, face_hash: str,
                             screening_id: str) -> None:
    with get_conn() as conn:
        existing = conn.execute(
            "SELECT linked_screenings FROM screening_persons WHERE person_id=?",
            (person_id,)
        ).fetchone()
        if existing:
            linked = json.loads(existing["linked_screenings"] or "[]")
            if screening_id not in linked:
                linked.append(screening_id)
            conn.execute(
                "UPDATE screening_persons SET linked_screenings=? WHERE person_id=?",
                (json.dumps(linked), person_id)
            )
        else:
            conn.execute(
                """INSERT INTO screening_persons
                   (person_id, passport_number, name_visual, dob_visual,
                    nationality, gender, face_embedding_hash, linked_screenings)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (person_id, passport_number, name, dob, nationality,
                 gender, face_hash, json.dumps([screening_id]))
            )


def find_persons_by_passport(passport_number: str) -> list:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM screening_persons WHERE passport_number=?",
            (passport_number,)
        ).fetchall()
    return [dict(r) for r in rows]


def find_persons_by_name_dob(name: str, dob: str) -> list:
    """Exact match — fuzzy matching is done in identity_intelligence layer."""
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM screening_persons WHERE name_visual=? AND dob_visual=?",
            (name, dob)
        ).fetchall()
    return [dict(r) for r in rows]


# ─── Audit Chain CRUD (PS 26188) ─────────────────────────────

def get_last_audit_hash() -> str:
    """Return current_hash of the most recent audit event, or GENESIS."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT current_hash FROM audit_events ORDER BY id DESC LIMIT 1"
        ).fetchone()
    return row["current_hash"] if row else "GENESIS"


def append_audit_event(event_id: str, screening_id: str, actor: str,
                       event_type: str, payload_hash: str,
                       previous_hash: str, current_hash: str) -> None:
    sql = """INSERT INTO audit_events
             (event_id, screening_id, actor, event_type,
              payload_hash, previous_hash, current_hash)
             VALUES (?,?,?,?,?,?,?)"""
    with get_conn() as conn:
        conn.execute(sql, (event_id, screening_id, actor, event_type,
                            payload_hash, previous_hash, current_hash))


def list_audit_events(screening_id: str = None, limit: int = 100) -> list:
    if screening_id:
        sql = ("SELECT * FROM audit_events WHERE screening_id=? "
               "ORDER BY id ASC LIMIT ?")
        args = (screening_id, limit)
    else:
        sql = "SELECT * FROM audit_events ORDER BY id DESC LIMIT ?"
        args = (limit,)
    with get_conn() as conn:
        rows = conn.execute(sql, args).fetchall()
    return [dict(r) for r in rows]


def get_all_audit_events_ordered() -> list:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM audit_events ORDER BY id ASC"
        ).fetchall()
    return [dict(r) for r in rows]


# ─── Blockchain Anchors (PS 26188) ──────────────────────────

def get_last_blockchain_anchor() -> dict | None:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM blockchain_anchors ORDER BY id DESC LIMIT 1"
        ).fetchone()
    return dict(row) if row else None


def append_blockchain_anchor(anchor_id: str, merkle_root: str, timestamp: str,
                             event_count: int, previous_anchor_hash: str,
                             anchor_hash: str, status: str = "ANCHORED") -> None:
    sql = """INSERT INTO blockchain_anchors
             (anchor_id, merkle_root, timestamp, event_count, previous_anchor_hash, anchor_hash, status)
             VALUES (?, ?, ?, ?, ?, ?, ?)"""
    with get_conn() as conn:
        conn.execute(sql, (anchor_id, merkle_root, timestamp, event_count,
                           previous_anchor_hash, anchor_hash, status))
        conn.commit()


def list_blockchain_anchors(limit: int = 10) -> list:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM blockchain_anchors ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]
