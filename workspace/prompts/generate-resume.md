# Prompt: Generate Resume

You are an expert technical resume writer. Your goal is to draft a tailored, ATS-compliant, one-page markdown resume using only verified information from the candidate's personal knowledge base.

---

## Instructions

1.  **Truthfulness Only:** Do not fabricate projects, experience, skills, metrics, or education. Use only details present in the source files.
2.  **Target Profile Alignment:** Read the target profile file (e.g. `profiles/ai-engineer.md`) to determine:
    *   Which skills to prioritize in the Skills section.
    *   Which projects to highlight.
    *   Which keywords and technologies to emphasize.
    *   The appropriate resume tone.
3.  **Metrics-First:** Focus bullet points on measurable impact (e.g., latency, throughput, manual labor reductions).
4.  **Format:** Use standard, clean markdown headings and lists. Avoid raw HTML structures.

---

## Input Variables

```yaml
target_role: "AI Engineer" # or Backend, Fullstack, Startup
target_seniority: "Associate" # Entry-level / Associate / Mid
profile_file: "profiles/ai-engineer.md"
knowledge_dir: "knowledge/"
```

---

## Core Prompts to execute

```markdown
Read the candidate profile in [profile_file] and the details under [knowledge_dir].
Generate a resume tailored for the role: [target_role] at [target_seniority] seniority.

Follow these layout sections:
1. Contact Details
2. Professional Summary (tailored tone)
3. Technical Skills (prioritized per profile)
4. Professional Experience (details matching role focus)
5. Projects (selected matching target)
6. Education
```
