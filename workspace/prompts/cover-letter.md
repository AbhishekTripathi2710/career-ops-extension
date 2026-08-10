# Prompt: Generate Cover Letter

You are a technical hiring expert. Your task is to write a highly compelling, personalized cover letter matching a candidate's profile to a specific Job Description (JD).

---

## Instructions

1.  **Strict Match:** Align the JD requirements directly with the candidate's achievements and experiences.
2.  **No Fluff:** Avoid generic introductory sentences (e.g., "I am writing to express my enthusiastic interest..."). Start directly with alignment.
3.  **STAR-based Hook:** Include a brief narrative based on one of the candidate's interview stories (e.g. solving the layout scrambling bug or scaling database throughput).
4.  **Tone:** Professional, engaging, and result-oriented.

---

## Input Variables

```yaml
job_description: |
  [Paste Job Description Here]
company_name: "[Company Name]"
role_title: "[Role Title]"
profile_file: "[Path to Profile, e.g. profiles/backend.md]"
interview_stories_dir: "knowledge/interview-stories/"
```

---

## Core Prompts to execute

```markdown
Analyze the [job_description].
Using details in [profile_file] and [interview_stories_dir], write a 3-paragraph cover letter tailored for [role_title] at [company_name].

Structure:
- Paragraph 1: Direct alignment statement linking your core competencies to their major engineering challenges.
- Paragraph 2: Deep dive into a matching project or experience, outlining the problem, your action, and quantifiable metrics (e.g. latency reduced by 40%).
- Paragraph 3: Cultural alignment and a brief sentence indicating next steps.
```
