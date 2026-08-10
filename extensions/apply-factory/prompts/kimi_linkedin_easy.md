# Kimi: LinkedIn Easy Apply

Fill LinkedIn's Easy Apply modal wizard using pre-drafted answers.
This differs from a normal form because Easy Apply is 2-4 steps inside a modal.

## Inputs

- Answers (from career-ops's Section G + KB):

{ANSWERS_JSON}

- Resume file: `{RESUME_PATH}`
- Snapshot output: `{SNAPSHOT_PATH}`

## Procedure

### 1. Verify

Confirm the visible Apply button says "Easy Apply", not just "Apply":

```javascript
document.querySelector('.jobs-apply-button')?.innerText.trim()
```

If it's "Apply" (external redirect), write `{"error": "external_apply",
"apply_url": "<href>"}` to `{SNAPSHOT_PATH}` and STOP. The user will
handle that URL through `/career-ops <url>` instead.

### 2. Click Easy Apply

Click the button. A modal opens.

### 3. Walk the wizard

For each step of the modal:

**a.** Read all visible fields (same DOM procedure as
`prompts/kimi_snapshot.md`). Track internally what you'll fill.

**b.** For each field, match label to a key in the answers above:
- Exact question match → use that answer
- Semantic match with confidence ≥ 0.7 → use
- No match → leave blank, add to `unfilled_fields`

**c.** For file upload: upload `{RESUME_PATH}`.

**d.** Click Next. If LinkedIn shows a validation error, STOP and report
which fields need attention.

**e.** On each step, keep a running record of what you filled and the
step number — you need this for the final snapshot.

### 4. Review step

When you reach the "Review your application" step (final step), DO NOT
click Submit. Print:

```
Ready to submit. Filled: <n>. Unfilled (please fill in the modal):
[<labels>].
When done, tell me "snapshot".
```

Then STOP.

### 5. Snapshot (do NOT submit)

When user says "snapshot":

1. Walk BACK through the wizard steps if possible (click "Back" button)
   and capture each step's fields, OR use your internal record from step 3.

2. Merge all steps into one array. Each field:
   ```
   {"label": "...", "field_type": "...", "value": "...",
    "options": [...], "was_prefilled": true/false, "prefilled_value": "..."}
   ```

3. Write the JSON to `{SNAPSHOT_PATH}`:
   ```json
   {
     "url": "https://linkedin.com/jobs/view/...",
     "captured_at": "2026-...",
     "easy_apply": true,
     "steps": 3,
     "fields": [ ... ]
   }
   ```

4. Report: "Snapshot saved. On the Review step now — click Submit yourself
   when ready. I will NOT click submit."

5. STOP. Do NOT click Submit application. Do NOT click Save application.

## Hard rules

- **Never** click Submit application — user does.
- **Never** click "Save application" — LinkedIn saves drafts on close;
  the user's snapshot is the record.
- **Never** click Follow company / Discover / More jobs.
- **If a "Complete your profile" popup appears**, STOP — do not fill
  fields on the user's LinkedIn profile.
- **If validation blocks progress on any step**, stop and report the
  specific field. Do not retry blindly.
