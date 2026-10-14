#!/usr/bin/env python3
"""Build one A4 reading PDF per session from 6141.md.

Each session becomes handouts/session_MM_SS_reading.pdf. Top-level bullets such as
"* **3. Business Context: ...**" become section headings; their children are dedented.
Usage: python3 scripts/build_readings.py [1.3 2.2 ...]   (no arguments = all sessions)
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "handouts" / "build"
OUT = ROOT / "handouts"

FRONT = r'''---
title: "{title}"
subtitle: "Course 6141: Business Analytics & AI Application | Reading for Week {week}"
format:
  pdf:
    pdf-engine: lualatex
    papersize: a4
    mainfont: "Times New Roman"
    sansfont: "Times New Roman"
    monofont: "DejaVu Sans Mono"
    monofontoptions:
      - Scale=0.82
    fontsize: 11pt
    linestretch: 1.15
    geometry:
      - margin=2.2cm
    number-sections: false
    colorlinks: true
    highlight-style: github
    filters:
      - ../../scripts/breakable_code.lua
    include-in-header:
      text: |
        \usepackage{{booktabs}}
        \usepackage{{longtable}}
        \usepackage{{array}}
        \usepackage{{ragged2e}}
        \usepackage{{fvextra}}
        \DefineVerbatimEnvironment{{Highlighting}}{{Verbatim}}{{breaklines,breakanywhere,commandchars=\\\{{\}}}}
        \setlength{{\emergencystretch}}{{3em}}
        \setlength{{\LTleft}}{{0pt}}
        \setlength{{\LTright}}{{0pt}}
        \AtBeginDocument{{\justifying\pagenumbering{{arabic}}\pagestyle{{plain}}}}
---

'''


def sessions(text):
    parts = re.split(r"\n(?=### Session \d\.\d: )", text)
    for part in parts[1:]:
        m = re.match(r"### Session (\d)\.(\d): ([^\n]+)\n", part)
        end = re.search(r"\n---\n|\n## Module|\n<a id=", part)
        yield m.group(1), m.group(2), m.group(3).strip(), part[m.end(): end.start() if end else len(part)]


def convert(module, session, title, body):
    week = re.search(r"Week (\d+)", body).group(1)
    out = [FRONT.format(title=f"Session {module}.{session}: {title}", week=week)]
    in_code = False
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
        if not in_code:
            img = re.match(r"!\[[^\]]*\]\((assets/[^)]+)\)", stripped)
            if img and not line.startswith(" "):
                out.append(f"\\noindent ![](../../{img.group(1)}){{width=100%}}\n")
                continue
            if stripped.startswith(("* **Lecture Presentation:**", "* **Reading (PDF):**")):
                continue
            head = re.match(r"^\* \*\*(.+?)\*\*\s*(.*)$", line)
            if head:
                name = head.group(1).rstrip(":")
                rest = head.group(2).strip()
                if name == "Schedule":
                    # dates change every semester, so the handout shows only the week
                    rest = re.sub(r"\s*\([0-9/ \-]+\)", "", rest)
                    out.append(f"**Schedule:** {rest}\n")
                    continue
                out.append(f"\n## {name}\n")
                if rest:
                    out.append(rest + "\n")
                continue
            # local file links become plain code text; web links stay clickable
            line = re.sub(r"\[([^\]]+)\]\(((?:data|slides|handouts|assets)/[^)]+)\)", r"`\2`", line)
        if line.startswith("  "):
            line = line[2:]
        out.append(line)
    text = "\n".join(out) + "\n"
    # Pandoc needs a blank line between a paragraph and a following list
    text = re.sub(r"(\n[^\n*\-\s|#!][^\n]*)\n(\* )", r"\1\n\n\2", text)
    return text


def main():
    wanted = set(sys.argv[1:])
    BUILD.mkdir(parents=True, exist_ok=True)
    md = (ROOT / "6141.md").read_text()
    built = []
    for module, session, title, body in sessions(md):
        sid = f"{module}.{session}"
        if wanted and sid not in wanted:
            continue
        name = f"session_0{module}_0{session}_reading"
        qmd = BUILD / f"{name}.qmd"
        qmd.write_text(convert(module, session, title, body))
        subprocess.run(["quarto", "render", str(qmd), "--to", "pdf", "--quiet"], check=True, cwd=BUILD)
        (BUILD / f"{name}.pdf").replace(OUT / f"{name}.pdf")
        built.append(name)
    print(f"Built {len(built)} reading PDFs in handouts/:", ", ".join(built))


if __name__ == "__main__":
    main()
