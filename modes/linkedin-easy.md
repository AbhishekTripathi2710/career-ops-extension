# /career-ops linkedin-easy — LinkedIn Easy Apply autofill

**Mode:** application
**Extension:** apply-factory
**Depends on:** an evaluated report in `reports/<slug>.md` with Section G

Fill LinkedIn's Easy Apply multi-step modal via Kimi Webbridge. Different from
`/career-ops fill` because Easy Apply is a 2-4 step wizard inside a modal,
not a normal form.

## When to invoke

- User: "/career-ops linkedin-easy <slug>"
- User: "easy apply to <slug>"
- After you've run `/career-ops <linkedin-url>` and `/career-ops apply <slug>`
  so Section G exists

## Prerequisites

- `reports/<slug>.md` has Section G
- The LinkedIn job URL is open in the browser
- User is logged into LinkedIn
- The job page shows the "Easy Apply" button (not "Apply" — that redirects
  to an external portal)

## Procedure

1. Resolve `<slug>` (most recent report if not given, confirm with user).

2. Run:
   ```
   cd extensions/apply-factory && python3 orchestrator.py fill <slug> \
       --prompt easy-apply
   ```
   Same fill logic as `/career-ops fill`, but emits the Easy Apply prompt
   (`prompts/kimi_linkedin_easy.md`) instead of the generic form-fill one.

3. Show the user:
   ```
   LinkedIn Easy Apply prompt ready.

   1. Confirm the job page is open and you can see the "Easy Apply" button.
   2. Launch Kimi Webbridge on that tab.
   3. Paste the prompt below.
   4. Kimi will click Easy Apply, walk each step, fill known fields, pause.
   5. Review each step, fix as needed.
   6. On the final Review step, tell Kimi "snapshot".
   7. YOU click Submit application.
   8. Come back with "learn <slug>".

   <the printed prompt>
   ```

4. Wait for user's word before /career-ops learn.

## Guardrails

- **Never** click Submit — user does.
- **If the button says "Apply" not "Easy Apply"**, this is an external redirect.
  Kimi will report `external_apply` and stop; hand the redirected URL to
  `/career-ops <url>` for normal handling.
- **If LinkedIn shows a "Complete profile to apply" popup**, STOP. We don't
  want to accidentally edit the user's LinkedIn profile.
- **Never** touch Follow / Save / Share buttons.
- **Never** save as draft — some ATSs count drafts as submissions.

## Reads / writes

- Reads: `reports/<slug>.md`, `output/<slug>.pdf`, `kb.sqlite`
- Writes: `extensions/apply-factory/artifacts/<slug>/answers.json`
- Writes: `extensions/apply-factory/snapshots/<slug>.json` (via Kimi)
