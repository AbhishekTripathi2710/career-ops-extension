# /career-ops fill — type the answers into the form

**Mode:** application
**Extension:** apply-factory
**Depends on:** an evaluated report in `reports/<slug>.md` with Section G

Career-ops's `/career-ops apply` generates answers as copy-paste text. This
mode takes those same answers, hands them to Kimi Webbridge, and Kimi types
them into the DOM for you. You review, correct anything wrong, then submit
yourself.

## When to invoke

- User: "/career-ops fill <slug>"
- User: "fill this form" (with a job open in a browser tab)
- After `/career-ops <url>` or `/career-ops apply <slug>` has run

## Prerequisites

- `reports/<slug>.md` exists with Section G (draft answers)
- Kimi Webbridge extension installed, job URL open in the tab
- `extensions/apply-factory/` set up (KB initialized via `orchestrator.py init`)

## Procedure

1. Resolve `<slug>`. If the user didn't specify, use the most recently
   modified file in `reports/` and confirm which job it is before proceeding.

2. Run the extension:
   ```
   cd extensions/apply-factory && python3 orchestrator.py fill <slug>
   ```

   This:
   - Parses Section G from `reports/<slug>.md`
   - Merges with the KB (from `kb.sqlite`) — KB wins on high-confidence entries
   - Writes `artifacts/<slug>/answers.json` for the record
   - Prints the Kimi Webbridge prompt to stdout

3. Show the user the Kimi prompt in a code block plus these steps:

   ```
   1. Confirm the job application URL is open in your browser and the form
      is visible.
   2. Launch Kimi Webbridge on that tab.
   3. Paste the prompt below into Kimi.
   4. Kimi will fill known fields and stop. Review the form in the browser.
      Fix anything wrong; fill the fields Kimi couldn't match.
   5. Tell Kimi "snapshot". Kimi writes snapshots/<slug>.json and stops.
   6. YOU click Submit yourself.
   7. Come back and say "learn <slug>".
   ```

4. Do NOT proceed to `/career-ops learn` on your own. Wait for the user
   to confirm they submitted.

## Guardrails

- If Section G is missing, tell the user to run `/career-ops apply <url>` first.
- If the job on-screen differs from the report's company/role, surface the
  mismatch (same policy as career-ops's own apply preflight).
- Kimi Webbridge never clicks Submit — the user does. This is intentional.
- Do not lower the confidence threshold in `orchestrator.py fill` to "help"
  Kimi fill more fields. Blank is safer than wrong.

## Reads / writes

- Reads: `reports/<slug>.md`, `output/<slug>.pdf`, `kb.sqlite`
- Writes: `extensions/apply-factory/artifacts/<slug>/answers.json`
- Emits: Kimi Webbridge prompt to stdout
