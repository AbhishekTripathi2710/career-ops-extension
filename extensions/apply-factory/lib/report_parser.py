"""
Parse Section G (application responses) from a career-ops report.

Based on the format described in career-ops's modes/apply.md:
  ## Section G — Application Responses   (or similar heading)
  ### 1. [Exact form question]
  > [Response, or "Ask candidate: ..." if unknown]
  ### 2. [Next question]
  > [Response]

If your actual reports use a slightly different heading or block style,
tweak SECTION_G_HEADING at the top.
"""
from __future__ import annotations
import re
from pathlib import Path
from typing import NamedTuple


SECTION_G_HEADING = re.compile(
    r"^#{1,3}\s*(section\s+g|g\.|g\s*[—\-:]|application\s+responses)",
    re.IGNORECASE | re.MULTILINE,
)
# Only H1 or H2 delimits a new top-level section. Question headings use H3/H4.
NEXT_SECTION = re.compile(r"^#{1,2}\s+", re.MULTILINE)
QUESTION_HEADING = re.compile(
    r"^#{3,4}\s*(\d+)[.):]?\s*(.+?)\s*$", re.MULTILINE
)


class ReportAnswer(NamedTuple):
    number: int
    question: str
    answer: str
    needs_confirmation: bool


def parse_section_g(report_path: str) -> list[ReportAnswer]:
    """Parse Section G from a career-ops report. Returns list of answers."""
    text = Path(report_path).read_text()

    m = SECTION_G_HEADING.search(text)
    if not m:
        return []

    # Section starts after the matched heading line
    section_start = text.find("\n", m.end()) + 1 if m.end() < len(text) else m.end()
    rest = text[section_start:]

    # Section ends at next H1-H3 heading (or EOF)
    m2 = NEXT_SECTION.search(rest)
    section = rest[: m2.start()] if m2 else rest

    answers = []
    matches = list(QUESTION_HEADING.finditer(section))
    for i, qm in enumerate(matches):
        number = int(qm.group(1))
        question = qm.group(2).strip()

        resp_start = qm.end()
        resp_end = matches[i + 1].start() if i + 1 < len(matches) else len(section)
        resp_block = section[resp_start:resp_end].strip()

        # Response is inside > blockquote lines; strip the > prefix
        lines = [
            line.lstrip("> ").rstrip()
            for line in resp_block.splitlines()
            if line.strip()
        ]
        response = "\n".join(lines).strip()

        needs_conf = response.lower().startswith(
            ("ask candidate", "[ask candidate", "**ask candidate")
        )

        answers.append(ReportAnswer(
            number=number,
            question=question,
            answer="" if needs_conf else response,
            needs_confirmation=needs_conf,
        ))

    return answers


def rewrite_section_g(report_path: str, answers: list[ReportAnswer]) -> None:
    """
    Overwrite Section G in the report with the given answers.
    Used by the learner after ingesting a snapshot.
    """
    text = Path(report_path).read_text()
    m = SECTION_G_HEADING.search(text)
    if not m:
        # No Section G yet — append one
        text = text.rstrip() + "\n\n## Section G — Application Responses\n\n"
        Path(report_path).write_text(text)
        m = SECTION_G_HEADING.search(text)

    section_start = text.find("\n", m.end()) + 1
    rest = text[section_start:]
    m2 = NEXT_SECTION.search(rest)
    section_end = section_start + (m2.start() if m2 else len(rest))

    lines = ["\n"]
    for a in answers:
        lines.append(f"### {a.number}. {a.question}\n")
        body = a.answer if a.answer else "[Ask candidate]"
        for bl in body.splitlines() or [""]:
            lines.append(f"> {bl}")
        lines.append("")

    new_body = "\n".join(lines) + "\n"
    Path(report_path).write_text(text[:section_start] + new_body + text[section_end:])
