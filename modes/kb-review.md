# /career-ops kb-review — review recently-learned KB entries

**Mode:** maintenance
**Extension:** apply-factory
**Depends on:** `kb.sqlite`

Show KB entries that were learned once and haven't been reinforced yet
(`seen_count == 1`) so the user can approve, correct, or delete them
before they're used to auto-fill future applications.

This is the safety net for the KB learning loop. Without periodic review,
a misclassified `intent_key` (e.g. LLM maps "How many hours per week can
you commit?" to `hours_per_day`) would silently poison future fills.

## When to invoke

- User: "/career-ops kb-review"
- User: "check the KB" / "review recent learnings"
- Suggested by other modes after `/career-ops learn` completes

Anytime, but especially:
- After a batch of applications (first few days of using this system)
- Before an important application where the wrong answer would hurt

## Procedure

1. Run:
   ```
   cd extensions/apply-factory && python3 orchestrator.py kb-review
   ```

   Output:
   ```
   Unconfirmed KB entries (seen once, never reinforced):

   1. citizen_of_india = "Yes"                        (learned 2 days ago from "Are you an Indian Citizen?")
   2. hours_per_day    = "40"                         (learned 1 day ago from "How many hours per week can you commit?")
   3. notice_period    = "60 days"                    (learned 3 days ago from "Notice period")
   ...
   ```

2. For each entry, ask the user to decide:
   - **Approve** — reinforce, marks confidence = 1.0 (won't show up again)
   - **Correct** — user gives the right value
   - **Delete** — bad intent_key, remove from KB entirely
   - **Skip** — leave for later

   Point out anything that looks suspicious BEFORE the user decides:
   - Intent_key that doesn't match the question shape
     (e.g. `hours_per_day` for a "per week" question — should be
     `hours_per_week`)
   - Values that look per-job (e.g. company-specific text)
   - Duplicates of existing high-confidence entries with slightly
     different names

3. Apply decisions:
   - Approve → `python3 orchestrator.py kb-approve <intent_key>`
   - Correct → `python3 orchestrator.py kb set <intent_key> "<value>"`
   - Delete → `python3 orchestrator.py kb-delete <intent_key>`

4. Summarize at the end:
   ```
   Reviewed 8: 5 approved, 2 corrected, 1 deleted.
   KB now has 47 entries (46 confirmed).
   ```

## Guardrails

- **Never** approve or delete without user confirmation.
- **Never** auto-fix intent_keys — always show the user first.
- **Do not** review already-confirmed entries (`seen_count > 1`) unless
  the user asks — those have been reinforced across multiple applications
  and are trustworthy.

## Reads / writes

- Reads: `kb.sqlite` (kb_entries, kb_question_variants, learning_events)
- Writes: `kb.sqlite` (via kb-approve / kb set / kb-delete subcommands)
