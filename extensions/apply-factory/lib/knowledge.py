"""
Knowledge base for form-fill Q&A.

- Each canonical question type has an `intent_key` (snake_case)
- One answer per intent_key
- Every observed phrasing appended to kb_question_variants for future matching
"""
from __future__ import annotations

from . import db
from . import llm


def all_intents(conn) -> list[dict]:
    rows = conn.execute("""
        SELECT e.intent_key, e.answer_type, e.answer, e.confidence,
               GROUP_CONCAT(v.question_text, ' || ') AS variants
        FROM kb_entries e
        LEFT JOIN kb_question_variants v ON v.intent_key = e.intent_key
        GROUP BY e.intent_key
    """).fetchall()
    return [dict(r) for r in rows]


def lookup_by_intent(conn, intent_key: str) -> dict | None:
    row = conn.execute(
        "SELECT * FROM kb_entries WHERE intent_key = ?", (intent_key,)
    ).fetchone()
    return dict(row) if row else None


def lookup_by_question(conn, question_text: str) -> dict | None:
    row = conn.execute("""
        SELECT e.* FROM kb_entries e
        JOIN kb_question_variants v ON v.intent_key = e.intent_key
        WHERE v.question_text = ?
        LIMIT 1
    """, (question_text,)).fetchone()
    return dict(row) if row else None


_NORMALIZE_SYSTEM = """You normalize job-application form field labels to canonical intent_keys.

Input: a form field label + type + existing intent_keys.
Output JSON only:
  {"intent_key": "snake_case_key", "is_new": true|false,
   "confidence": 0.0-1.0, "answer_type": "boolean|select|text|number|date|file",
   "reason": "one line"}

Rules:
- If it clearly maps to an existing key, is_new=false and use that key.
- Otherwise invent a short snake_case key.
- Only claim a match if confidence >= 0.8.
- Do not duplicate existing keys with new wording.
"""


def normalize_question(conn, question_text: str, field_type: str = "text") -> dict:
    existing = lookup_by_question(conn, question_text)
    if existing:
        return {
            "intent_key": existing["intent_key"],
            "is_new": False, "confidence": 1.0,
            "answer_type": existing["answer_type"],
            "reason": "exact question variant match",
        }

    intents = all_intents(conn)
    intent_table = "\n".join(
        f"- {i['intent_key']} ({i['answer_type']}): {i['variants'] or '(no variants yet)'}"
        for i in intents
    ) or "(knowledge base is empty)"

    prompt = f"""EXISTING INTENT_KEYS:
{intent_table}

NEW FIELD:
  question: "{question_text}"
  field_type: {field_type}

Return JSON only."""

    result = llm.call_json(prompt, system=_NORMALIZE_SYSTEM)
    if not result.get("is_new") and not lookup_by_intent(conn, result["intent_key"]):
        result["is_new"] = True
        result["reason"] = "LLM referenced nonexistent key; forced new"
    return result


def upsert(
    conn, intent_key: str, answer: str, *,
    question_text: str, field_type: str = "text",
    answer_type: str = "text", source: str = "manual",
    confidence: float = 1.0, app_id: int | None = None,
) -> str:
    """Returns event_type: 'new' | 'reinforced' | 'corrected'."""
    existing = lookup_by_intent(conn, intent_key)

    if existing is None:
        conn.execute("""
            INSERT INTO kb_entries
                (intent_key, answer_type, answer, confidence, source, seen_count)
            VALUES (?, ?, ?, ?, ?, 1)
        """, (intent_key, answer_type, answer, confidence, source))
        event_type = "new"
        old_answer = None
    else:
        old_answer = existing["answer"]
        if _same(old_answer, answer):
            conn.execute("""
                UPDATE kb_entries
                SET seen_count = seen_count + 1,
                    last_seen = CURRENT_TIMESTAMP,
                    confidence = MIN(1.0, confidence + 0.05)
                WHERE intent_key = ?
            """, (intent_key,))
            event_type = "reinforced"
        else:
            conn.execute("""
                UPDATE kb_entries
                SET answer = ?, confidence = ?, source = 'corrected',
                    seen_count = seen_count + 1,
                    last_seen = CURRENT_TIMESTAMP
                WHERE intent_key = ?
            """, (answer, confidence, intent_key))
            event_type = "corrected"

    conn.execute("""
        INSERT OR IGNORE INTO kb_question_variants (intent_key, question_text, field_type)
        VALUES (?, ?, ?)
    """, (intent_key, question_text, field_type))

    conn.execute("""
        INSERT INTO learning_events
            (app_id, intent_key, question_text, old_answer, new_answer, event_type)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (app_id, intent_key, question_text, old_answer, answer, event_type))

    return event_type


def _same(a: str | None, b: str | None) -> bool:
    if a is None or b is None:
        return a == b
    a, b = a.strip(), b.strip()
    if len(a) < 40 and len(b) < 40:
        return a.lower() == b.lower()
    return a == b
