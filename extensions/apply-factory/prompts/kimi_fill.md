# Kimi: fill this application form

You have these pre-drafted answers (from career-ops's Section G + KB):

{ANSWERS_JSON}

Each key is either an intent_key (e.g. `citizen_of_india`) or `report_q<N>`.
Each value is: `{"question": "...", "answer": "...", "confidence": 0-1, "source": "kb|report"}`.

Resume file to upload for CV/resume fields: `{RESUME_PATH}`
Snapshot output path: `{SNAPSHOT_PATH}`

You will do this in three phases. Do not skip. Do not click Submit yourself.

---

## Phase 1 — Fill known

For every visible form field:

1. Read the label — `<label for=>`, wrapping `<label>`, `aria-label`,
   `aria-labelledby`, or nearest visible text.

2. Match against the questions in the answers above:
   - Exact question text match → use that answer
   - Close semantic match (same intent, e.g. "Are you a citizen of India?"
     matches `citizen_of_india`) → use if confidence ≥ 0.7
   - No good match → LEAVE BLANK. Add label to `unfilled_fields`.

3. File upload fields:
   - Resume/CV → upload `{RESUME_PATH}`
   - Cover letter → leave blank unless a cover file was explicitly passed

4. Track internally, per field: what value you put, what the label was.
   You'll need this for the Phase 3 snapshot.

Then print:

```
Filled: <n>
Low confidence (please review): [<labels>]
Unfilled (please fill manually): [<labels>]
```

Say: "Review the form. Fix anything wrong, complete unfilled fields.
When done, tell me 'snapshot'."

Then STOP.

---

## Phase 2 — Wait

Do not touch the DOM. User completes remaining fields in the browser.

---

## Phase 3 — Snapshot, do NOT submit

When user says "snapshot":

1. Run the DOM walk from `prompts/kimi_snapshot.md` in this same folder.

2. For each field in the result, add:
   - `was_prefilled`: true if you filled it in Phase 1
   - `prefilled_value`: what you originally put there in Phase 1 (or null)

3. Write the merged JSON to `{SNAPSHOT_PATH}`.

4. Report: "Snapshot saved to {SNAPSHOT_PATH}. Form is ready — click
   Submit yourself when you're happy. I will not click submit."

5. Stop. Do NOT click Submit. Do NOT click Save Draft.

---

## Hard rules

- **Never** click Submit. User clicks Submit.
- **Never** click Save Draft — some ATSs treat drafts as submissions.
- **Never** invent answers for legal, EEO, sponsorship, salary, disability,
  veteran status, or citizenship fields — those must come from the answers
  loaded above or be filled by the user manually.
- **If the form has multiple steps/pages** (e.g. LinkedIn Easy Apply,
  Workday), walk them one at a time — fill this page, click Next, fill
  the next, etc. Only snapshot at the final review step.
- **If validation fails on Next**, stop and report which fields need
  attention. Do not retry blindly.
- **If the site logs you out or shows a captcha**, stop and report.
  Do not attempt evasion.
