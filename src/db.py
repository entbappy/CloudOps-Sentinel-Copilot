import json
import sqlite3
from datetime import datetime, timezone
from src.config import get_settings


def init_db() -> None:
    path = get_settings().database_file
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS rag_audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            route TEXT,
            used_web INTEGER DEFAULT 0,
            support_status TEXT,
            usefulness TEXT,
            trace_json TEXT,
            sources_json TEXT
        )
        """)
        conn.commit()


def save_audit(question: str, result: dict) -> None:
    path = get_settings().database_file
    with sqlite3.connect(path) as conn:
        conn.execute(
            """INSERT INTO rag_audit
            (created_at, question, answer, route, used_web, support_status, usefulness, trace_json, sources_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                datetime.now(timezone.utc).isoformat(),
                question,
                result.get("answer", ""),
                result.get("route", ""),
                int(bool(result.get("used_web_search"))),
                result.get("support_status", ""),
                result.get("usefulness", ""),
                json.dumps(result.get("trace", []), ensure_ascii=False),
                json.dumps(result.get("sources", []), ensure_ascii=False),
            ),
        )
        conn.commit()


def latest_audits(limit: int = 25):
    path = get_settings().database_file
    with sqlite3.connect(path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM rag_audit ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]
