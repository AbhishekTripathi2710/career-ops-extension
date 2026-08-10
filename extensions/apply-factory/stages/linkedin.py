"""
LinkedIn discovery stage.

Two ops:
  - emit_search_prompt(query, ...) — fills the Kimi prompt template
  - ingest_search(kimi_output_path) — reads Kimi's JSON, writes staging inbox
"""
from __future__ import annotations
import hashlib
import json
from datetime import datetime
from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def _slug(company: str, role: str) -> str:
    """Generate a career-ops-style slug: company-role-hash."""
    base = f"{company}-{role}".lower()
    base = "".join(c if c.isalnum() or c == "-" else "-" for c in base)
    base = "-".join(p for p in base.split("-") if p)[:60]
    h = hashlib.sha1(f"{company}|{role}".encode()).hexdigest()[:6]
    return f"{base}-{h}"


def emit_search_prompt(
    query: str,
    output_json: str,
    *,
    max_jobs: int = 25,
    date_posted: str = "past-24h",
    experience: str = "any",
    remote: str = "any",
    easy_apply_only: bool = True,
    prompt_path: str = "prompts/kimi_linkedin_search.md",
) -> str:
    tpl = Path(prompt_path).read_text()
    return (tpl
            .replace("{QUERY}", query)
            .replace("{OUTPUT_JSON}", output_json)
            .replace("{MAX_JOBS}", str(max_jobs))
            .replace("{DATE_POSTED}", date_posted)
            .replace("{EXPERIENCE}", experience)
            .replace("{REMOTE}", remote)
            .replace("{EASY_APPLY_ONLY}", "true" if easy_apply_only else "false"))


def ingest_search(kimi_output_path: str, inbox_path: str) -> dict:
    """
    Read Kimi's scrape output, dedup against existing inbox, write updated inbox.
    Does NOT touch career-ops's pipeline.tsv — the user picks which to add.
    """
    data = json.loads(Path(kimi_output_path).read_text())

    if "error" in data:
        return {"error": data["error"], "n_new": 0, "n_dup": 0, "jobs": []}

    inbox = _load_inbox(inbox_path)
    seen_urls = {j["url"] for j in inbox}
    new_jobs = []

    for j in data.get("jobs", []):
        if j["url"] in seen_urls:
            continue
        new_jobs.append({
            "slug": _slug(j["company"], j["title"]),
            "company": j["company"],
            "role": j["title"],
            "location": j.get("location", ""),
            "url": j["url"],
            "easy_apply": j.get("easy_apply", False),
            "jd_text": j.get("jd_text", ""),
            "posted_at": j.get("posted_at", ""),
            "source": "linkedin",
            "scraped_at": data.get("scraped_at", datetime.utcnow().isoformat()),
            "status": "inbox",
        })

    updated = inbox + new_jobs
    Path(inbox_path).parent.mkdir(parents=True, exist_ok=True)
    Path(inbox_path).write_text(json.dumps(updated, indent=2))

    return {
        "query": data.get("query"),
        "n_new": len(new_jobs),
        "n_dup": len(data.get("jobs", [])) - len(new_jobs),
        "n_total": len(updated),
        "jobs": new_jobs,
    }


def _load_inbox(inbox_path: str) -> list[dict]:
    p = Path(inbox_path)
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text())
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def format_inbox_summary(jobs: list[dict], limit: int = 25) -> str:
    """Format a numbered list for the agent to show the user."""
    if not jobs:
        return "(inbox is empty)"
    lines = []
    for i, j in enumerate(jobs[:limit], 1):
        ea = " [Easy Apply]" if j.get("easy_apply") else ""
        loc = f"— {j['location']}" if j.get("location") else ""
        lines.append(
            f"{i:3d}. {j['role']:40s}— {j['company']:25s}{loc}{ea}"
        )
    if len(jobs) > limit:
        lines.append(f"     ... and {len(jobs) - limit} more")
    return "\n".join(lines)
