# Prompt: Generate Recruiter Outreach Message

You are a professional networking strategist. Your task is to write a short, punchy outreach message targeting recruiters or hiring managers.

---

## Instructions

1.  **Strict Length Limit:** Keep the message under **150 words** (LinkedIn connection invite limit or quick DM).
2.  **Hook:** Address a specific challenge the company is facing or a recent technical announcement (if provided).
3.  **Core Value:** Focus on a single high-impact metric (e.g. "automated ETL processes, eliminating 95% of manual operational tasks").
4.  **Call to Action:** End with a low-friction question rather than a direct request for a phone call (e.g. "Are you open to a brief chat if my profile aligns?").

---

## Input Variables

```yaml
company_name: "[Company Name]"
recruiter_name: "[Recruiter Name or 'Hiring Team']"
target_role: "[Target Role]"
profile_file: "[Path to Profile, e.g. profiles/backend.md]"
custom_hook: "[Recent news, or leave blank]"
```

---

## Core Prompts to execute

```markdown
Draft a brief, professional outreach message to [recruiter_name] regarding a [target_role] position at [company_name].
Use the value proposition outlined in [profile_file] and incorporate [custom_hook] if provided. Keep it concise, engaging, and low-friction.
```
