# Kimi: LinkedIn job search

You're scraping LinkedIn using the user's logged-in browser session.
**Human speed** — 3-5 seconds between actions. LinkedIn detects rapid activity.

## Inputs

- Search query: `{QUERY}`
- Filters:
  - Date posted: `{DATE_POSTED}` (past-24h | past-week | past-month | any)
  - Experience: `{EXPERIENCE}`
  - Remote: `{REMOTE}`
  - Easy Apply only: `{EASY_APPLY_ONLY}`
- Max jobs: `{MAX_JOBS}` (do not exceed 50)
- Output file: `{OUTPUT_JSON}`

## Procedure

### 1. Navigate

Open `https://www.linkedin.com/jobs/search/` in the current tab.

Fill the search box with `{QUERY}` (split into role + location if the query
mentions a city).

Apply filters via the LinkedIn filter UI (Date posted → past-24h,
"Easy Apply" toggle if `{EASY_APPLY_ONLY}` is true).

Wait for results to render.

**If prompted to log in or hit with a security check**, write
`{"error": "auth_required"}` to `{OUTPUT_JSON}` and STOP.

### 2. Scroll to load

LinkedIn virtualizes the results list. Scroll the left panel slowly —
one viewport per 2 seconds — until either `{MAX_JOBS}` cards are loaded
or "You've viewed all jobs" appears.

### 3. Extract cards

Run this in the tab:

```javascript
Array.from(document.querySelectorAll('[data-job-id], .job-card-container')).map(card => {
  const jobId = card.getAttribute('data-job-id') ||
                card.querySelector('[data-job-id]')?.getAttribute('data-job-id');
  const titleEl = card.querySelector('.job-card-list__title, .job-card-container__link, a.job-card-list__title--link');
  const companyEl = card.querySelector('.job-card-container__primary-description, .artdeco-entity-lockup__subtitle');
  const locationEl = card.querySelector('.job-card-container__metadata-item, .artdeco-entity-lockup__caption');
  const easyApplyBadge = !!card.querySelector('[aria-label*="Easy Apply"], .job-card-container__apply-method');

  return {
    linkedin_job_id: jobId,
    title: titleEl?.innerText.trim() || '',
    company: companyEl?.innerText.trim() || '',
    location: locationEl?.innerText.trim() || '',
    url: 'https://www.linkedin.com/jobs/view/' + jobId,
    easy_apply: easyApplyBadge,
  };
}).filter(j => j.linkedin_job_id && j.title);
```

### 4. Enrich JD (optional)

For each card, click it to load the JD in the right pane, wait 2 seconds:

```javascript
{
  jd_text: document.querySelector('.jobs-description__content, .jobs-box__html-content')?.innerText.trim(),
  posted_at: document.querySelector('.jobs-unified-top-card__posted-date, span.tvm__text--positive')?.innerText.trim(),
}
```

Merge into the card. If a card fails to load JD, keep it with `jd_text: null`.

### 5. Write results

Write the array to `{OUTPUT_JSON}` in this shape:

```json
{
  "query": "{QUERY}",
  "scraped_at": "2026-...",
  "filters": {
    "date_posted": "{DATE_POSTED}",
    "easy_apply_only": {EASY_APPLY_ONLY}
  },
  "count": 18,
  "jobs": [
    {
      "linkedin_job_id": "3812345678",
      "title": "Senior Backend Engineer",
      "company": "Acme",
      "location": "Bangalore, India",
      "url": "https://www.linkedin.com/jobs/view/3812345678",
      "easy_apply": true,
      "jd_text": "...",
      "posted_at": "2 hours ago"
    }
  ]
}
```

Then say: "search done — {count} jobs written to {OUTPUT_JSON}".

## Hard rules

- **Do not** scrape more than one search per 10 minutes without confirmation.
- **Do not** click Apply during this scrape. Applying is a separate turn.
- **Do not** attempt to defeat login walls or captchas.
- **Zero results** = LinkedIn probably changed markup. Report zero and stop,
  do NOT fabricate.
