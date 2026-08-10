#!/usr/bin/env python3
"""
apply-factory orchestrator (extension inside career-ops).

Commands:
  ./orchestrator.py init                 — create KB
  ./orchestrator.py fill <slug>          — parse report, emit Kimi prompt
  ./orchestrator.py learn <slug>         — ingest snapshot, update KB + Section G
  ./orchestrator.py kb list|get|set      — inspect / seed KB
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

import yaml

_ROOT = Path(__file__).resolve().parent          # extensions/apply-factory/
_CAREEROPS = _ROOT.parent.parent                  # career-ops/
sys.path.insert(0, str(_ROOT))

from lib import db, knowledge
from lib.report_parser import parse_section_g, rewrite_section_g, ReportAnswer
from learner import learn as learner


def _cfg() -> dict:
    return yaml.safe_load((_ROOT / "config.yaml").read_text())


def _report_path(slug: str) -> Path:
    return _CAREEROPS / "reports" / f"{slug}.md"


def _snapshot_path(slug: str) -> Path:
    return _ROOT / "snapshots" / f"{slug}.json"


def _output_pdf(slug: str) -> Path:
    return _CAREEROPS / "output" / f"{slug}.pdf"


# ---------- Commands ----------

def cmd_init(args):
    cfg = _cfg()
    db_path = _ROOT / cfg["paths"]["kb_db"]
    db.init(str(db_path), str(_ROOT / "schema.sql"))
    for d in ("artifacts", "snapshots"):
        (_ROOT / d).mkdir(exist_ok=True)
    print(f"initialized {db_path}")


def cmd_fill(args):
    cfg = _cfg()
    slug = args.slug
    report = _report_path(slug)
    if not report.exists():
        sys.exit(f"no report at {report}\n  → run /career-ops apply <url> first")

    section_g = parse_section_g(str(report))
    if not section_g:
        sys.exit(
            f"no Section G in {report}\n"
            f"  → either the report is pre-apply-mode, or the heading regex\n"
            f"    in lib/report_parser.py needs tweaking to match your format"
        )

    db_path = str(_ROOT / cfg["paths"]["kb_db"])
    answers = {}

    with db.tx(db_path) as conn:
        for a in section_g:
            # KB wins if it has a high-confidence answer for this exact question
            kb_row = knowledge.lookup_by_question(conn, a.question)
            if kb_row and kb_row["confidence"] >= 0.9:
                answers[kb_row["intent_key"]] = {
                    "question": a.question,
                    "answer": kb_row["answer"],
                    "confidence": kb_row["confidence"],
                    "source": "kb",
                }
                continue

            # Otherwise use the report's Section G draft
            if not a.needs_confirmation and a.answer:
                key = f"report_q{a.number}"
                answers[key] = {
                    "question": a.question,
                    "answer": a.answer,
                    "confidence": 0.7,
                    "source": "report",
                }
            # If needs_confirmation and no KB match → skip, user fills manually

    # Write artifacts/<slug>/answers.json for the record
    art_dir = _ROOT / "artifacts" / slug
    art_dir.mkdir(parents=True, exist_ok=True)
    (art_dir / "answers.json").write_text(json.dumps(answers, indent=2))

    # Emit the Kimi prompt — pick the right template
    prompt_name = args.prompt or "generic"
    prompt_file = {
        "generic": "prompts/kimi_fill.md",
        "easy-apply": "prompts/kimi_linkedin_easy.md",
    }.get(prompt_name)
    if not prompt_file:
        sys.exit(f"unknown prompt template: {prompt_name}")

    prompt_tpl = (_ROOT / prompt_file).read_text()
    resume_path = str(_output_pdf(slug))
    prompt = (prompt_tpl
              .replace("{ANSWERS_JSON}", json.dumps(answers, indent=2))
              .replace("{RESUME_PATH}", resume_path)
              .replace("{SLUG}", slug)
              .replace("{SNAPSHOT_PATH}", str(_snapshot_path(slug))))
    print("=" * 60)
    print(f"Paste into Kimi Webbridge on the job application page.")
    print(f"After you submit, run:  /career-ops learn {slug}")
    print("=" * 60)
    print(prompt)


# ---------- LinkedIn ----------

def cmd_linkedin_url(args):
    """Print the LinkedIn search URL for manual browsing. No Kimi involved."""
    from urllib.parse import urlencode

    tpr_map = {
        "past-24h": "r86400", "past-week": "r604800",
        "past-month": "r2592000", "any": "",
    }
    remote_map = {"onsite": "1", "remote": "2", "hybrid": "3", "any": ""}
    exp_map = {
        "entry": "2", "associate": "3", "mid-senior": "4",
        "director": "5", "any": "",
    }

    params = {"keywords": args.query}
    tpr = tpr_map.get(args.date_posted, "")
    if tpr:
        params["f_TPR"] = tpr
    if not args.all:
        params["f_AL"] = "true"
    remote = remote_map.get(args.remote, "")
    if remote:
        params["f_WT"] = remote
    exp = exp_map.get(args.experience, "")
    if exp:
        params["f_E"] = exp
    if args.location:
        params["location"] = args.location

    url = "https://www.linkedin.com/jobs/search/?" + urlencode(params)
    print(url)
    print()
    print("Open in your browser. When you find jobs to add:")
    print("  /career-ops linkedin add <url1> <url2> ...")


def cmd_linkedin_add(args):
    """Add one or more LinkedIn job URLs to the inbox manually."""
    from stages import linkedin as ls

    inbox_path = _ROOT / "data" / "linkedin-inbox.json"
    inbox_path.parent.mkdir(exist_ok=True)

    existing = json.loads(inbox_path.read_text()) if inbox_path.exists() else []
    seen = {j["url"] for j in existing}

    added, skipped, needs_info = [], [], []

    for url in args.urls:
        url = url.strip()
        if not url:
            continue
        if url in seen:
            skipped.append(url)
            continue

        # If --company and --role given AND we have one URL, use those directly.
        # Otherwise try to fetch metadata from LinkedIn's og: tags.
        if args.company and args.role and len(args.urls) == 1:
            company, role = args.company, args.role
            jd_text = ""
            if args.jd_file:
                jd_text = Path(args.jd_file).read_text()
        else:
            meta = _fetch_linkedin_meta(url)
            if not meta:
                needs_info.append(url)
                continue
            company = meta.get("company", "")
            role = meta.get("role", "")
            jd_text = meta.get("jd_text", "")

        if not company or not role:
            needs_info.append(url)
            continue

        entry = {
            "slug": ls._slug(company, role),
            "company": company, "role": role,
            "url": url, "location": "",
            "easy_apply": False,  # unknown from URL alone
            "jd_text": jd_text, "posted_at": "",
            "source": "linkedin-manual",
            "scraped_at": __import__("datetime").datetime.now().isoformat(),
            "status": "inbox",
        }
        existing.append(entry)
        seen.add(url)
        added.append(entry)

    inbox_path.write_text(json.dumps(existing, indent=2))

    print(f"Added: {len(added)}")
    for a in added:
        print(f"  ✓ {a['company']:30s}— {a['role']}")
    if skipped:
        print(f"Already in inbox: {len(skipped)}")
    if needs_info:
        print(f"Need company/role: {len(needs_info)}")
        for u in needs_info:
            print(f"  ✗ {u}")
        print()
        print("For each, rerun with:")
        print(f"  /career-ops linkedin add <url> --company \"X\" --role \"Y\"")


def _fetch_linkedin_meta(url: str) -> dict | None:
    """
    Try to extract company + role from LinkedIn's public OpenGraph tags.
    LinkedIn job pages are semi-public — og:title usually holds the role,
    og:site_name and og:description often reveal the company.
    Returns None if the fetch or parse fails.
    """
    try:
        import urllib.request
        import re
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; career-ops)"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")

        def og(prop):
            m = re.search(
                rf'<meta[^>]+property=["\']og:{prop}["\'][^>]+content=["\']([^"\']+)',
                html,
            )
            return m.group(1) if m else None

        title = og("title") or ""
        desc = og("description") or ""

        # LinkedIn title format: "Company hiring Role in Location | LinkedIn"
        m = re.match(r"^(.+?)\s+hiring\s+(.+?)(?:\s+in\s+|$|\s*\|)", title)
        if m:
            return {
                "company": m.group(1).strip(),
                "role": m.group(2).strip(),
                "jd_text": desc[:2000],
            }
        # Fallback: title as role, empty company
        return {"company": "", "role": title, "jd_text": desc[:2000]}
    except Exception:
        return None


def cmd_linkedin_search(args):
    from stages import linkedin as ls
    import time

    (_ROOT / "data").mkdir(exist_ok=True)
    output = args.output or f"/tmp/linkedin_{int(time.time())}.json"

    prompt = ls.emit_search_prompt(
        query=args.query,
        output_json=output,
        max_jobs=args.max,
        date_posted=args.date_posted,
        experience=args.experience,
        remote=args.remote,
        easy_apply_only=not args.all,
        prompt_path=str(_ROOT / "prompts/kimi_linkedin_search.md"),
    )
    print("=" * 60)
    print(f"Paste into Kimi Webbridge (opens linkedin.com in the tab).")
    print(f"When Kimi finishes, run:  /career-ops linkedin ingest {output}")
    print("=" * 60)
    print(prompt)


def cmd_linkedin_ingest(args):
    from stages import linkedin as ls
    inbox = _ROOT / "data" / "linkedin-inbox.json"
    result = ls.ingest_search(args.kimi_output, str(inbox))

    if "error" in result:
        sys.exit(f"scrape had error: {result['error']}")

    print(f"Ingested {result['n_new']} new jobs ({result['n_dup']} duplicates).")
    print(f"Inbox now has {result['n_total']} jobs total.")
    print()
    print(ls.format_inbox_summary(result["jobs"]))
    print()
    print(f"Inbox saved to: {inbox}")
    print(f"To add to career-ops pipeline: pick jobs and run /career-ops <url>")


# ---------- KB Review ----------

def cmd_kb_review(args):
    cfg = _cfg()
    db_path = str(_ROOT / cfg["paths"]["kb_db"])
    with db.tx(db_path) as conn:
        rows = conn.execute("""
            SELECT e.intent_key, e.answer, e.answer_type, e.source, e.created_at,
                   (SELECT question_text FROM kb_question_variants v
                    WHERE v.intent_key = e.intent_key LIMIT 1) AS example_q
            FROM kb_entries e
            WHERE e.seen_count = 1
              AND e.source IN ('manual', 'llm', 'corrected')
            ORDER BY e.created_at DESC
        """).fetchall()

        if not rows:
            print("No unconfirmed entries. KB is clean.")
            return

        print(f"Unconfirmed KB entries (seen once, never reinforced): {len(rows)}\n")
        for i, r in enumerate(rows, 1):
            age = r["created_at"] or "unknown"
            q = r["example_q"] or "(no question recorded)"
            print(f"{i:3d}. {r['intent_key']:35s} = {r['answer'][:40]!r:42s}")
            print(f"     learned {age} from: {q!r}")
            print()

        print(f"Actions:")
        print(f"  /career-ops kb-approve <intent_key>   — reinforce, seen_count += 1")
        print(f"  /career-ops kb set <intent_key> \"<value>\"  — correct")
        print(f"  /career-ops kb-delete <intent_key>    — remove from KB")


def cmd_kb_approve(args):
    cfg = _cfg()
    db_path = str(_ROOT / cfg["paths"]["kb_db"])
    with db.tx(db_path) as conn:
        row = knowledge.lookup_by_intent(conn, args.key)
        if not row:
            sys.exit(f"unknown intent_key: {args.key}")
        conn.execute("""
            UPDATE kb_entries
            SET seen_count = seen_count + 1,
                confidence = MIN(1.0, confidence + 0.1),
                last_seen = CURRENT_TIMESTAMP
            WHERE intent_key = ?
        """, (args.key,))
        conn.execute("""
            INSERT INTO learning_events
                (intent_key, question_text, old_answer, new_answer, event_type)
            VALUES (?, '(kb-review approved)', ?, ?, 'reinforced')
        """, (args.key, row["answer"], row["answer"]))
        print(f"approved: {args.key} = {row['answer']!r}")


def cmd_kb_delete(args):
    cfg = _cfg()
    db_path = str(_ROOT / cfg["paths"]["kb_db"])
    with db.tx(db_path) as conn:
        row = knowledge.lookup_by_intent(conn, args.key)
        if not row:
            sys.exit(f"unknown intent_key: {args.key}")
        conn.execute("DELETE FROM kb_question_variants WHERE intent_key = ?", (args.key,))
        conn.execute("DELETE FROM kb_entries WHERE intent_key = ?", (args.key,))
        conn.execute("""
            INSERT INTO learning_events
                (intent_key, question_text, old_answer, new_answer, event_type)
            VALUES (?, '(kb-review deleted)', ?, '', 'deleted')
        """, (args.key, row["answer"]))
        print(f"deleted: {args.key} (was {row['answer']!r})")


# ---------- Briefing ----------

def cmd_briefing(args):
    cfg = _cfg()
    db_path = str(_ROOT / cfg["paths"]["kb_db"])
    from datetime import datetime, timedelta, timezone

    print(f"=== BRIEFING — {datetime.now().date()} ===\n")

    # NEW: LinkedIn inbox jobs staged in last 24h
    inbox = _ROOT / "data" / "linkedin-inbox.json"
    if inbox.exists():
        jobs = json.loads(inbox.read_text())
        cutoff = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        recent = [j for j in jobs if j.get("scraped_at", "") > cutoff][:5]
        if recent:
            print("NEW (linkedin, last 24h):")
            for j in recent:
                ea = " [EA]" if j.get("easy_apply") else ""
                print(f"  {j['role']:40s}— {j['company']:25s}{ea}")
            print()

    # READY: reports with a Section G (tailored but user hasn't run /fill yet)
    reports_dir = _CAREEROPS / "reports"
    if reports_dir.exists():
        ready = []
        for r in sorted(reports_dir.glob("*.md"), key=lambda p: -p.stat().st_mtime)[:20]:
            try:
                if parse_section_g(str(r)):
                    ready.append(r.stem)
            except Exception:
                pass
            if len(ready) >= 5:
                break
        if ready:
            print("READY TO APPLY (Section G exists):")
            for r in ready:
                print(f"  {r}")
            print(f"  → /career-ops fill <slug>")
            print()

    # UNCONFIRMED KB
    with db.tx(db_path) as conn:
        n = conn.execute(
            "SELECT COUNT(*) as c FROM kb_entries WHERE seen_count = 1"
        ).fetchone()["c"]
        if n:
            print(f"UNCONFIRMED KB: {n} entries → /career-ops kb-review\n")

    # KB size
    with db.tx(db_path) as conn:
        total = conn.execute("SELECT COUNT(*) as c FROM kb_entries").fetchone()["c"]
        events_24h = conn.execute("""
            SELECT COUNT(*) as c FROM learning_events
            WHERE created_at > datetime('now', '-1 day')
        """).fetchone()["c"]
        print(f"KB: {total} entries · {events_24h} learning events in last 24h")


def cmd_learn(args):
    cfg = _cfg()
    slug = args.slug
    snap = _snapshot_path(slug)
    if not snap.exists():
        sys.exit(f"no snapshot at {snap}\n  → did Kimi write it before submit?")

    db_path = str(_ROOT / cfg["paths"]["kb_db"])
    events = learner.learn_from_snapshot(str(snap), db_path)
    learner._print_summary(events)

    print(f"\nSummary: {len(events['new'])} new, "
          f"{len(events['corrected'])} corrected, "
          f"{len(events['reinforced'])} reinforced, "
          f"{len(events['skipped'])} skipped")

    # Update Section G in the report with final answers
    report = _report_path(slug)
    if report.exists():
        snap_data = json.loads(snap.read_text())
        answers = []
        idx = 1
        for f in snap_data.get("fields", []):
            if not f.get("value"):
                continue
            answers.append(ReportAnswer(
                number=idx,
                question=f["label"],
                answer=str(f["value"]),
                needs_confirmation=False,
            ))
            idx += 1
        rewrite_section_g(str(report), answers)
        print(f"\nSection G updated in reports/{slug}.md with final answers.")


def cmd_kb(args):
    cfg = _cfg()
    db_path = str(_ROOT / cfg["paths"]["kb_db"])
    with db.tx(db_path) as conn:
        if args.action == "list":
            rows = conn.execute("""
                SELECT intent_key, answer_type, answer, confidence, seen_count, source
                FROM kb_entries ORDER BY seen_count DESC
            """).fetchall()
            for r in rows:
                print(f"  {r['intent_key']:30s} = {r['answer']!r:30s} "
                      f"({r['answer_type']}, c={r['confidence']:.2f}, "
                      f"n={r['seen_count']}, {r['source']})")
            print(f"\n{len(rows)} entries")

        elif args.action == "get":
            entry = knowledge.lookup_by_intent(conn, args.key)
            variants = conn.execute(
                "SELECT question_text FROM kb_question_variants WHERE intent_key = ?",
                (args.key,)
            ).fetchall()
            history = conn.execute("""
                SELECT event_type, old_answer, new_answer, created_at
                FROM learning_events WHERE intent_key = ?
                ORDER BY created_at DESC LIMIT 10
            """, (args.key,)).fetchall()
            print(json.dumps({
                "entry": entry,
                "variants": [v["question_text"] for v in variants],
                "history": [dict(h) for h in history],
            }, indent=2, default=str))

        elif args.action == "set":
            knowledge.upsert(
                conn, intent_key=args.key, answer=args.value,
                question_text=f"(manual seed: {args.key})",
                source="manual", confidence=1.0,
            )
            print(f"set {args.key} = {args.value!r}")


# ---------- CLI ----------

def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init")

    a = sub.add_parser("fill")
    a.add_argument("slug")
    a.add_argument("--prompt", choices=["generic", "easy-apply"], default="generic",
                   help="Which Kimi prompt template to emit")

    a = sub.add_parser("learn"); a.add_argument("slug")

    a = sub.add_parser("kb")
    a.add_argument("action", choices=["list", "get", "set"])
    a.add_argument("key", nargs="?")
    a.add_argument("value", nargs="?")

    # LinkedIn
    a = sub.add_parser("linkedin-search")
    a.add_argument("query")
    a.add_argument("--output", default=None)
    a.add_argument("--max", type=int, default=25)
    a.add_argument("--date-posted", default="past-24h",
                   choices=["past-24h", "past-week", "past-month", "any"])
    a.add_argument("--experience", default="any",
                   choices=["entry", "associate", "mid-senior", "director", "any"])
    a.add_argument("--remote", default="any",
                   choices=["onsite", "remote", "hybrid", "any"])
    a.add_argument("--all", action="store_true",
                   help="Include non-Easy-Apply jobs (default: EA only)")

    a = sub.add_parser("linkedin-url",
                       help="Print LinkedIn search URL for manual browsing")
    a.add_argument("query")
    a.add_argument("--date-posted", default="past-24h",
                   choices=["past-24h", "past-week", "past-month", "any"])
    a.add_argument("--experience", default="any",
                   choices=["entry", "associate", "mid-senior", "director", "any"])
    a.add_argument("--remote", default="any",
                   choices=["onsite", "remote", "hybrid", "any"])
    a.add_argument("--location", default=None)
    a.add_argument("--all", action="store_true",
                   help="Include non-Easy-Apply jobs (default: EA only)")

    a = sub.add_parser("linkedin-add",
                       help="Add one or more LinkedIn URLs to the inbox manually")
    a.add_argument("urls", nargs="+", help="One or more job URLs")
    a.add_argument("--company", default=None)
    a.add_argument("--role", default=None)
    a.add_argument("--jd-file", dest="jd_file", default=None)

    a = sub.add_parser("linkedin-ingest")
    a.add_argument("kimi_output", help="Path to the JSON Kimi wrote")

    # KB review
    sub.add_parser("kb-review")
    a = sub.add_parser("kb-approve"); a.add_argument("key")
    a = sub.add_parser("kb-delete"); a.add_argument("key")

    # Briefing
    sub.add_parser("briefing")

    args = p.parse_args()

    handlers = {
        "init": cmd_init, "fill": cmd_fill, "learn": cmd_learn, "kb": cmd_kb,
        "linkedin-search": cmd_linkedin_search,
        "linkedin-url": cmd_linkedin_url,
        "linkedin-add": cmd_linkedin_add,
        "linkedin-ingest": cmd_linkedin_ingest,
        "kb-review": cmd_kb_review,
        "kb-approve": cmd_kb_approve,
        "kb-delete": cmd_kb_delete,
        "briefing": cmd_briefing,
    }
    handlers[args.cmd](args)


if __name__ == "__main__":
    main()
