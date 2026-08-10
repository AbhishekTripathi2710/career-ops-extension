# /career-ops learn — ingest the pre-submit snapshot into the KB

**Mode:** application
**Extension:** apply-factory
**Depends on:** a snapshot at `extensions/apply-factory/snapshots/<slug>.json`

After you submit an application, this mode processes the snapshot Kimi
captured, updates Section G in the report with your FINAL answers, and adds
new question→answer pairs to the KB so they auto-fill next time.

## When to invoke

- User: "/career-ops learn <slug>"
- User: "I submitted" / "learn from that" with a recent snapshot on disk

## Procedure

1. Resolve `<slug>` (same rules as `/career-ops fill`).

2. Verify `extensions/apply-factory/snapshots/<slug>.json` exists. If not,
   tell the user Kimi didn't write it — do NOT fabricate data.

3. Run:
   ```
   cd extensions/apply-factory && python3 orchestrator.py learn <slug>
   ```

   Output shape:
   ```
   == NEW (n) ==
     <intent_key>: "<value>"  (from "<question>")
   == CORRECTED (n) ==
     <intent_key>: "<old>" → "<new>"
   == REINFORCED (n) ==
     <intent_key>, <intent_key>, ...
   == SKIPPED (n) ==
     first 10 shown

   Section G in reports/<slug>.md updated.
   ```

4. Section G in the report is now overwritten with your final answers.
   Career-ops's other modes (tracker, followup) see the update automatically.

5. Update the pipeline status via career-ops's tracker (its own mode):
   ```
   /career-ops tracker mark <slug> applied
   ```

6. Review the NEW intent_keys with the user. Point out anything that looks
   wrong:
   - Misclassified (label got mapped to a bad intent_key)
   - Job-specific answer that shouldn't persist (e.g. why_company —
     though these should already be caught by SKIP_INTENTS in learn.py)
   - Duplicate of an existing intent_key with different wording

   Offer to fix via:
   ```
   python3 orchestrator.py kb set <key> <value>
   ```
   or a direct DELETE if the intent_key itself is bad.

## Guardrails

- Every event goes to `learning_events` in `kb.sqlite`. If a bad correction
  slips in, we can revert.
- `SKIP_INTENTS` in `learner/learn.py` filters per-job answers like
  `why_company`. If you notice one of those persisting, add it to the set.

## Reads / writes

- Reads: `extensions/apply-factory/snapshots/<slug>.json`, `reports/<slug>.md`
- Writes: `extensions/apply-factory/kb.sqlite` (KB + audit log)
- Writes: `reports/<slug>.md` (rewrites Section G with final answers)
