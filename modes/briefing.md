# /career-ops briefing — daily overview

**Mode:** overview
**Extension:** apply-factory

Show what's new in the pipeline, what needs the user's attention, and what's
ready to apply to. Meant to be the first command of the day.

## When to invoke

- User: "/career-ops briefing"
- User: "morning brief" / "what's new" / "where am I"
- Start of a work session

## Procedure

1. Run:
   ```
   cd extensions/apply-factory && python3 orchestrator.py briefing
   ```

   Output shape (adjust display but keep the sections):

   ```
   === MORNING BRIEF — 2026-07-22 ===

   NEW SINCE YESTERDAY (career-ops + linkedin combined):
     ★ Senior Backend Engineer     Acme       (linkedin, easy-apply, past-24h)
       Backend Engineer            Beta Inc   (linkedin, easy-apply, past-24h)
       Staff Engineer              Gamma      (greenhouse, scanned by career-ops)
     ★ Payments Engineer           Delta      (lever, scanned by career-ops)

   READY TO APPLY (tailored, Section G exists):
     - acme-senior-backend         (Section G has 12 answers, 2 need candidate)
     - delta-payments              (Section G has 8 answers, all resolved)

   NEEDS ATTENTION:
     - beta-backend: JD says Kubernetes required but resume doesn't show it
       → run `/career-ops training` if you want to address it
     - gamma-staff: comp range 45-60 LPA, your expected is 42 LPA → likely stretch

   UNCONFIRMED KB (learned once, never reinforced): 7 entries
     → run `/career-ops kb-review` to check them

   PIPELINE COUNTS:
     new: 12   evaluated: 8   tailored: 3   applied: 24   interview: 2
   ```

2. Star (★) the top 1-2 items by score or freshness so the user sees them first.

3. Don't dump the whole pipeline. Cap sections at 5 items each; add
   "and N more" if there are more.

4. Do NOT run any other command from this one. Briefing is read-only.

## Guardrails

- **Read-only.** No status updates, no ingests, no learnings.
- **Do not** call the LLM for summaries — this should be instant. If you
  want richer natural-language summaries, add them as a separate mode.
- If a data file is missing (e.g. no `data/linkedin-inbox.json`), just
  skip that section rather than erroring.

## Reads / writes

- Reads: `data/pipeline.tsv`, `data/linkedin-inbox.json`, `kb.sqlite`, `reports/*.md`
- Writes: nothing
