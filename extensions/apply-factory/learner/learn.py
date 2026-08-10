"""
Learn from a pre-submit form snapshot.

Snapshot shape (from prompts/kimi_snapshot.md):
  {
    "url": "https://...",
    "captured_at": "2026-...",
    "fields": [
      {"label": "...", "field_type": "radio", "value": "Yes",
       "options": [...], "was_prefilled": true, "prefilled_value": "Yes"},
      ...
    ]
  }

For each field, normalize label -> intent_key, then upsert into KB.
event_type in {new, reinforced, corrected} tracked in learning_events.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from lib import db, knowledge


# Never learn from these — they're job-specific and shouldn't persist
SKIP_INTENTS = {
    "cover_letter", "resume_upload", "job_specific_question",
    "captcha", "additional_notes", "why_company", "why_this_role",
    "why_company_free", "additional_information",
}
SKIP_FIELD_TYPES = {"file", "hidden"}


def learn_from_snapshot(snapshot_path: str, db_path: str,
                        app_id: int | None = None) -> dict:
    snap = json.loads(Path(snapshot_path).read_text())
    events = {"new": [], "reinforced": [], "corrected": [], "skipped": []}

    with db.tx(db_path) as conn:
        for field in snap["fields"]:
            outcome = _process_field(conn, field, app_id)
            events[outcome["event_type"]].append(outcome)

    return events


def _process_field(conn, field: dict, app_id: int | None) -> dict:
    label = (field.get("label") or "").strip()
    value = field.get("value")
    field_type = field.get("field_type", "text")

    if not label or value in (None, "", []) or field_type in SKIP_FIELD_TYPES:
        return {"event_type": "skipped", "label": label,
                "reason": "empty or non-learnable"}

    norm = knowledge.normalize_question(conn, label, field_type)
    intent_key = norm["intent_key"]

    if intent_key in SKIP_INTENTS:
        return {"event_type": "skipped", "label": label,
                "reason": f"blocklisted intent: {intent_key}"}

    stored_value = _coerce(value)

    event_type = knowledge.upsert(
        conn,
        intent_key=intent_key,
        answer=stored_value,
        question_text=label,
        field_type=field_type,
        answer_type=norm.get("answer_type", "text"),
        source="manual" if not field.get("was_prefilled") else "corrected",
        confidence=1.0,
        app_id=app_id,
    )
    return {"event_type": event_type, "label": label,
            "intent_key": intent_key, "value": stored_value}


def _coerce(v) -> str:
    if isinstance(v, list):
        return ", ".join(str(x) for x in v)
    return str(v)


def _print_summary(events: dict) -> None:
    for kind in ("new", "corrected", "reinforced"):
        rows = events[kind]
        if not rows:
            continue
        print(f"\n== {kind.upper()} ({len(rows)}) ==")
        for r in rows:
            print(f"  {r['intent_key']:35s} <- {r['value']!r:40s} ({r['label']!r})")
    if events["skipped"]:
        print(f"\n== SKIPPED ({len(events['skipped'])}) ==")
        for r in events["skipped"][:10]:
            print(f"  {r['label']!r}: {r['reason']}")
        if len(events["skipped"]) > 10:
            print(f"  ... and {len(events['skipped']) - 10} more")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--snapshot", required=True)
    p.add_argument("--db", default="kb.sqlite")
    p.add_argument("--app-id", type=int, default=None)
    args = p.parse_args()

    events = learn_from_snapshot(args.snapshot, args.db, args.app_id)
    _print_summary(events)
    print(f"\nSummary: {len(events['new'])} new, "
          f"{len(events['corrected'])} corrected, "
          f"{len(events['reinforced'])} reinforced, "
          f"{len(events['skipped'])} skipped")
