# /career-ops linkedin — search LinkedIn and stage results

**Mode:** discovery
**Extension:** apply-factory
**Complements:** `/career-ops scan` (which covers open ATSs but not LinkedIn)

Search LinkedIn using the user's logged-in browser session via Kimi Webbridge,
then stage the results so the user can decide which to ingest into career-ops's
pipeline.

## When to invoke

- User: "/career-ops linkedin <query>"
- User: "search linkedin for <role>"
- User: "any new backend jobs on linkedin"

Do NOT invoke automatically — LinkedIn rate-limits sessions.

## Defaults

Unless the user overrides, defaults are:
- Date posted: **past 24 hours** (`--date-posted past-24h`)
- Easy Apply only: **true** (`--easy-apply-only`)
- Max jobs: 25

These match "quick daily check for new stuff I can actually apply to fast."

## Flags

- `--date-posted past-24h | past-week | past-month | any` (default: past-24h)
- `--experience entry | associate | mid-senior | director | any` (default: any)
- `--remote onsite | remote | hybrid | any` (default: any)
- `--all` — turn OFF easy-apply filter (include external redirects)
- `--max N` — cap at N results (default 25, max 50)

## Three ways to use this — pick based on the user's intent

### Full scrape (Kimi does everything)

User says: "/career-ops linkedin <query>" — they want automated.

Follow the full procedure below. Takes 2-5 min at human speed.

### URL only (user browses themselves)

User says: "manual", "just give me the URL", "I'll browse", or "no Kimi".

Print the search URL and stop:
```
cd extensions/apply-factory && python3 orchestrator.py linkedin-url "<query>" [flags]
```

Show them:
```
Open this in your browser:
https://www.linkedin.com/jobs/search/?...

When you find jobs, come back with:
  /career-ops linkedin add <url1> <url2> ...
```

Then STOP. Don't invoke Kimi, don't scrape.

### Manual add (user pastes URLs)

User says: "/career-ops linkedin add <urls>" or "add these jobs" with URLs.

Run:
```
cd extensions/apply-factory && python3 orchestrator.py linkedin-add <url1> <url2> ...
```

The command tries to fetch company + role from LinkedIn's OpenGraph tags.
If a URL fails (login-walled, weird format), report it and ask the user
for `--company "X" --role "Y"`, then rerun for that specific URL.

For any URL where JD text matters (usually because the user will run
`/career-ops <url>` next to evaluate), suggest the user paste the JD:
```
/career-ops linkedin add <url> --company "X" --role "Y" --jd-file /tmp/jd.txt
```

## Full scrape procedure (only when user chose "full scrape" above)

1. Parse the user's query and flags. If they said "past week" in prose,
   translate to `--date-posted past-week`. Same for other filters.

2. Run:
   ```
   cd extensions/apply-factory && python3 orchestrator.py linkedin-search \
       "<query>" [flags]
   ```
   This prints the Kimi Webbridge prompt.

3. Show the user:
   ```
   LinkedIn search prepped. Filters: past-24h, Easy Apply only.

   1. Open linkedin.com in your browser (confirm you're logged in).
   2. Launch Kimi Webbridge on that tab.
   3. Paste this prompt:

   <the printed Kimi prompt>

   4. Kimi will search and scrape (2-5 min at human speed).
      When it finishes, tell me "ingest" and I'll stage the results.
   ```

4. Wait. Do not simulate progress.

5. When the user says "ingest" (or "ingest linkedin"):
   ```
   cd extensions/apply-factory && python3 orchestrator.py linkedin-ingest \
       <output_path>
   ```

   This prints a numbered list of jobs with title, company, location,
   Easy Apply flag. Also writes to `extensions/apply-factory/data/linkedin-inbox.json`.

6. Ask the user which they want in the pipeline:

   ```
   Pick jobs to add to pipeline (comma-separated, or "all"):
   1. Senior Backend Engineer  — Acme       — Bangalore   [Easy Apply]
   2. Backend Engineer         — Beta Inc   — Remote      [Easy Apply]
   3. Staff Engineer           — Gamma      — Bangalore   [Easy Apply]
   ...
   ```

7. For each picked job, run career-ops's normal ingest:
   ```
   /career-ops <url>
   ```
   (which triggers career-ops's own evaluate → report → pdf flow)

## Guardrails

- **No more than one search per 10 minutes** without explicit confirmation.
- **If Kimi reports `auth_required`**, tell the user to log in and stop.
- **Zero results = LinkedIn changed DOM.** Report zero, don't fabricate.
- **Do not scrape LinkedIn profiles or messages** — jobs only.
- **Do not click Apply during this run.** This is scrape-only.
  Applying happens in a separate turn via `/career-ops <url>` or
  `/career-ops linkedin-easy <slug>`.

## Reads / writes

- Writes: `extensions/apply-factory/data/linkedin-inbox.json` (staged results)
- Emits: Kimi Webbridge prompt to stdout
- Downstream: career-ops's `/career-ops <url>` handles evaluate + report
