#!/usr/bin/env python3
"""Session map content: for each numbered section of a session in 6141.md, its short name
and one line describing what that section of THIS session actually covers.

Used by build_deck_from_md.py, update_map_slide.py, and render_session_maps.js, so the
slide 2 map and the course-page map image always show the same content.

CLI: python3 scripts/session_map.py 2.1   -> JSON {"question": ..., "items": [...]}
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

NAMES = {1: "Session Purpose", 2: "Learning Outcomes", 5: "Lab Dataset", 6: "Keywords",
         7: "Core Foundations", 8: "IDE Setup", 9: "Code Examples", 10: "References"}


def section(md, sid):
    i = md.index(f"### Session {sid}:")
    ends = [x for x in (md.find("\n### Session", i + 5), md.find("\n## Module", i)) if x > 0]
    return md[i: min(ends) if ends else len(md)]


def part(sec, num):
    m = re.search(rf"(?m)^\* \*\*{num}\. ([^*]+)\*\*(.*)$", sec)
    start = m.end()
    nxt = re.search(r"(?m)^\* \*\*\d+\. ", sec[start:])
    return m.group(1).rstrip(":").strip(), m.group(2).strip(), sec[start: start + nxt.start()] if nxt else sec[start:]


def clean(text):
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    return re.sub(r"\*+", "", text).strip()


def first_clause(text):
    text = clean(text)
    text = re.split(r"(?<=[.!?])\s+(?=[A-Z`(])", text)[0]
    return text.rstrip(".")


def strip_gloss(text):
    """Drop parenthesized glosses: 'read HTML (HyperText ... page)' -> 'read HTML'."""
    text = text.replace("()", "\x00")
    out, depth = [], 0
    for ch in text:
        if ch == "(":
            depth += 1
            continue
        if ch == ")" and depth:
            depth -= 1
            continue
        if not depth:
            out.append(ch)
    return re.sub(r"\s+", " ", "".join(out)).replace(" ,", ",").replace("\x00", "()").strip()


def brief(data):
    """Slide version: a few words per item, so the map reads at a glance."""
    out = []
    for it in data["items"]:
        num, d = it["num"], it["detail"]
        if num == 1:
            d = "answer today's question"
        elif num == 2:
            d = f"{len(d.split(' / '))} skills you will show today"
        elif num == 5:
            kinds = {}
            for f in it["files"]:
                k = {"csv": "CSV", "html": "web page", "xlsx": "Excel", "json": "JSON", "joblib": "model"}.get(f.rsplit(".", 1)[-1], "file")
                kinds[k] = kinds.get(k, 0) + 1
            d = ", ".join(f"{n} {k}{'s' if n > 1 else ''}" for k, n in kinds.items())
        elif num == 6:
            d = f"{len(it['terms'])} terms"
        elif num == 7:
            d = f"{len(d.split(' / '))} ideas, one at a time"
        elif num == 8:
            d = d if d.startswith("`pip") else "name files, run in the Terminal"
        elif num == 9:
            d = f"{len(d.split(' / '))} demos + Quick Checks"
        elif num == 10:
            d = f"{len(d.split(' / '))} official docs"
        out.append({"num": num, "name": it["name"], "detail": d})
    return {"question": data["question"], "items": out}


def items(sid):
    md = (ROOT / "6141.md").read_text()
    sec = section(md, sid)
    found = {int(m.group(1)): m.group(2) for m in re.finditer(r"(?m)^\* \*\*(\d+)\. ([^*]+)\*\*", sec)}
    q = re.search(r"asks: ([^?]+\?)", sec)
    question = (q.group(1)[0].upper() + q.group(1)[1:]) if q else ""
    out = []
    for num in sorted(found):
        heading, rest, body = part(sec, num)
        name, detail, extra = NAMES.get(num, heading), "", {}
        if num == 1:
            first = re.search(r"(?m)^  \* (.+)$", body)
            detail = first_clause(first.group(1)) if first else ""
        elif num == 2:
            skills = []
            for m in re.finditer(r"(?m)^\s*\d+\. \"[^\"]+\": (.+)$", body):
                s = strip_gloss(clean(m.group(1)))
                s = re.split(r",? and (?=fix|handle|write|turn|review|choose|calculate)", s)[0]
                skills.append(s[:1].upper() + s[1:])
            detail = " / ".join(skills)
        elif num in (3, 4):
            name, detail = ("Business Context" if num == 3 else "Data Basics"), clean(heading.split(": ", 1)[-1])
        elif num == 5:
            files = []
            for f in re.findall(r"data/([\w.-]+\.\w+)", body):
                if f not in files:
                    files.append(f)
            detail = ", ".join(f"`{f}`" for f in files)
            extra = {"files": files + [f for f in dict.fromkeys(re.findall(rf"data/(session_0{sid[0]}_0{sid[2]}_[\w.-]+\.\w+)", sec)) if f not in files]}
        elif num == 6:
            names = re.findall(r"(?m)^  \* (.+?):\n    \* What:", body)
            detail = ", ".join(strip_gloss(clean(n).replace("`", "")) for n in names)
            extra = {"terms": names}
        elif num == 7:
            heads = re.findall(r"(?m)^  \* \*\*7\.\d ([^*]+)\*\*", body)
            detail = " / ".join(clean(h).split(":")[0] for h in heads)
        elif num == 8:
            pip = re.search(r"First time only: `(pip install [^`]+)`", body)
            code = re.search(r"YourName_(S\d\d)_", sec)
            detail = f"`{pip.group(1)}`" if pip else f"name files `YourName_{code.group(1) if code else 'Sxx'}_...py`, run in the Terminal"
        elif num == 9:
            titles = re.findall(r"(?m)^  \* \*Micro-Example \d \(((?:[^()]|\([^()]*\))*)\):\*", body)
            detail = " / ".join(clean(t) for t in titles)
        elif num == 10:
            refs = []
            for r in re.findall(r"\[([^\]]+)\]\(", body):
                r = strip_gloss(clean(r).replace("`", ""))
                r = r.split(": ", 1)[0] if ": " in r else r
                r = re.sub(r"\s*(Official Documentation|Documentation|Official Overview)$", "", r).strip()
                if r not in refs:
                    refs.append(r)
            detail = " / ".join(refs)
        elif num >= 11:
            m = re.match(r"Exercise (\d): (Guided|Applied|Advanced) Practice - (.+)", heading)
            if m:
                name, detail = f"Exercise {m.group(1)}: {m.group(2)}", clean(m.group(3))
        out.append({"num": num, "name": name, "detail": detail, **extra})
    return {"question": question, "items": out}


if __name__ == "__main__":
    data = items(sys.argv[1])
    print(json.dumps(brief(data) if "--brief" in sys.argv else data, ensure_ascii=False, indent=1))
