#!/usr/bin/env python3
"""Build a 16-slide lecture deck for one session directly from 6141.md.

Slides: overview, session map, business context, data basics, dataset, keywords, core
foundations, one real-data table, three code demonstrations each followed by its Quick
Check, references, and one Exercises slide (Goal / File / Check from slide_briefs.py). Text that is too long for a card is shrunk
in the browser (never below 15pt) by the autofit script at the end of the page.

Usage: python3 scripts/build_deck_from_md.py 2.2 [3.1 ...]
"""
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

ROOT = Path(__file__).resolve().parent.parent
CSS = (ROOT / "scripts" / "deck_style.css").read_text()
FOOT = '<div class="footer"><span>Business Analytics &amp; AI Application | Course 6141</span><span>Slide 0 / 0</span></div>'

EXTRA_CSS_BASE = """
.fitbox { min-height: 0; overflow: hidden; }
.card.fitbox p, .card.fitbox li { font-size: 18pt; }
.mdtable { border-collapse: collapse; width: 100%; margin: .06in 0; }
.mdtable th, .mdtable td { text-align: left; padding: .05in .1in; border-bottom: 1px solid #E2E8F0; font-size: 17pt; vertical-align: top; }
.mdtable th { border-bottom: 2px solid #18181B; font-weight: bold; }
.mdtable code { white-space: normal; }
.card ul.tight { margin: .04in 0 0; padding-left: .3in; }
.card ul.tight li { margin: .05in 0; line-height: 1.25; }
.outbox { background: #18181B; color: #34D399; border-radius: 8px; padding: .1in .14in; font: 13.5pt/1.35 "DejaVu Sans Mono", monospace; white-space: pre; overflow: hidden; }
.card p.remember { color: #991B1B; margin-top: .06in; }
.card p.remember b { color: #991B1B; }
.f7 .card h2 { font-size: 24pt; margin-bottom: .12in; }
.f7 .card p.remember { margin-top: .16in; }
.exg .card h2 { font-size: 24pt; }
.exg .card p { margin: .1in 0; }
.exg .card p code { font-size: .88em; }
.big-q { font-size: 20pt; }
.mdtable.cols td:first-child code { white-space: nowrap; overflow-wrap: normal; }
.card code, .check code, .mdtable code, .card h2 { white-space: normal; overflow-wrap: anywhere; }
.notes .card.how { flex: 1 1 auto; }
.notes .card.out { flex: 0 0 auto; }

"""

from update_map_slide import MAP_CSS, map_body  # noqa: E402
EXTRA_CSS = EXTRA_CSS_BASE + MAP_CSS

AUTOFIT = """
<script>
window.__fitDone = false;
function fitAll() {
  document.querySelectorAll('.fitbox').forEach((box) => {
    let size = parseFloat(box.dataset.start || '18');
    const floor = parseFloat(box.dataset.floor || '15');
    const apply = () => box.querySelectorAll('p, li, td, th, .outbox, pre').forEach((el) => {
      if (el.tagName === 'PRE') { el.style.fontSize = Math.max(9.5, size - 3.5) + 'pt'; return; }
      if (el.classList.contains('outbox')) { el.style.fontSize = Math.max(11, size - 4.5) + 'pt'; return; }
      el.style.fontSize = size + 'pt';
    });
    apply();
    const over = () => box.scrollHeight > box.clientHeight + 1 || box.scrollWidth > box.clientWidth + 1
      || [...box.querySelectorAll('pre')].some((pre) => pre.scrollHeight > pre.clientHeight + 6 || pre.scrollWidth > pre.clientWidth + 6);
    while (over() && size > floor) { size -= 0.5; apply(); }
    if (over()) box.dataset.overflow = 'yes';
    box.__apply = (v) => { size = v; apply(); };
    box.dataset.size = size;
  });
  // cards on one slide share one size, so they read as a set
  document.querySelectorAll('[data-uniform]').forEach((group) => {
    const boxes = [...group.querySelectorAll('.fitbox')];
    const min = Math.min(...boxes.map((b) => parseFloat(b.dataset.size)));
    boxes.forEach((b) => b.__apply(min));
  });
  window.__fitDone = true;
}
document.fonts.ready.then(() => { fitAll(); document.querySelectorAll('[data-overflow]').forEach((el) => el.removeAttribute('data-overflow')); fitAll(); });
</script>
"""


def inline(text):
    """Markdown inline -> HTML: code, bold, italic, links (text only)."""
    parts = re.split(r"(`[^`]+`)", text)
    out = []
    for part in parts:
        if part.startswith("`") and part.endswith("`") and len(part) > 1:
            out.append(f"<code>{html.escape(part[1:-1])}</code>")
            continue
        p = html.escape(part)
        p = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", p)
        p = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", p)
        p = re.sub(r"(?<![*\w])\*([^*]+)\*(?![*\w])", r"<i>\1</i>", p)
        out.append(p)
    return "".join(out)


def section(md, sid):
    i = md.index(f"### Session {sid}:")
    j = md.find("\n### Session", i + 5)
    k = md.find("\n## Module", i)
    ends = [x for x in (j, k) if x > 0]
    return md[i: min(ends) if ends else len(md)]


def part(sec, num):
    m = re.search(rf"(?m)^\* \*\*{num}\. ([^*]+)\*\*(.*)$", sec)
    start = m.end()
    nxt = re.search(r"(?m)^\* \*\*\d+\. ", sec[start:])
    body = sec[start: start + nxt.start()] if nxt else sec[start:]
    return m.group(1).rstrip(":"), m.group(2).strip(), body


def bullets(body, level=2):
    """Top-level bullets at a given indent (2 spaces = level 1 under the section)."""
    pad = " " * level
    items = []
    for line in body.splitlines():
        if line.startswith(pad + "* ") and not line.startswith(pad + "  "):
            items.append(line[len(pad) + 2:].strip())
    return items


def tables(body):
    """Return all pipe tables in a block as (header, rows)."""
    found = []
    lines = body.splitlines()
    i = 0
    while i < len(lines):
        if lines[i].strip().startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|[-| ]+\|\s*$", lines[i + 1]):
            head = [c.strip() for c in lines[i].strip().strip("|").split("|")]
            rows = []
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            found.append((head, rows))
        else:
            i += 1
    return found


def table_html(head, rows):
    th = "".join(f"<th>{inline(h)}</th>" for h in head)
    trs = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows)
    return f'<table class="mdtable"><tr>{th}</tr>{trs}</table>'


def slide(module, kicker, title, body):
    return (f'<section class="slide">\n  <div><span class="eyebrow">MODULE {module}</span>'
            f'<span class="kicker">{kicker}</span></div>\n  <div class="title">{title}</div><div class="rule"></div>\n'
            f'{body}\n  {FOOT}\n</section>\n')


def card(tag, h2, inner, cls="card fitbox", start=None):
    st = f' data-start="{start}"' if start else ""
    return f'<div class="{cls}"{st}><div class="tag">{tag}</div>{f"<h2>{h2}</h2>" if h2 else ""}{inner}</div>'


def cap(text):
    return text[:1].upper() + text[1:] if text else text


def first_sentence(text):
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z`(])", text.strip())
    return parts[0]


def tree(body, level=2, max_top=7, max_sub=6):
    """Bullets at `level` spaces with their children (bullets or numbered items) as nested lists."""
    lines = body.splitlines()
    out, i, n = [], 0, 0
    in_code = False
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("```"):
            in_code = not in_code
        if not in_code and line.startswith(" " * level + "* ") and not line.startswith(" " * (level + 1)):
            n += 1
            text = line[level + 2:].strip()
            subs, j, sub_code = [], i + 1, False
            while j < len(lines) and (not lines[j].strip() or len(lines[j]) - len(lines[j].lstrip()) > level):
                l2 = lines[j]
                if l2.strip().startswith("```"):
                    sub_code = not sub_code
                m = re.match(rf"^ {{{level + 2}}}(?:\* |\d+\. )(.*)$", l2)
                if m and not sub_code:
                    subs.append(m.group(1).strip())
                j += 1
            if n <= max_top and not text.startswith("|"):
                inner = "".join(f"<li>{inline(x)}</li>" for x in subs[:max_sub])
                out.append(f"<li>{inline(first_sentence(text))}" + (f'<ul class="tight">{inner}</ul>' if inner else "") + "</li>")
            i = j
            continue
        i += 1
    return '<ul class="tight">' + "".join(out) + "</ul>"


def ul(items):
    return '<ul class="tight">' + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ul>"


def code_blocks(text):
    return [m.group(1) for m in re.finditer(r"```python\n(.*?)```", text, re.S)]


def dedent(code):
    lines = code.rstrip("\n").split("\n")
    margin = min(len(l) - len(l.lstrip()) for l in lines if l.strip())
    return "\n".join(l[margin:] for l in lines)


def highlight(code):
    out = []
    for line in html.escape(code).split("\n"):
        if re.match(r"^# \d\. ", line):
            out.append(f'<span class="sec">{line}</span>')
        elif line.lstrip().startswith("#"):
            out.append(f'<span class="cm">{line}</span>')
        else:
            out.append(line)
    return "\n".join(out)


def sub_bullets(block, label):
    """Bullets nested under a '* *Label:*' line inside a micro-example block."""
    m = re.search(rf"(?m)^(\s*)\* \*{re.escape(label)}:\*(.*)$", block)
    if not m:
        return []
    indent = len(m.group(1)) + 2
    items = []
    for line in block[m.end():].splitlines()[1:]:
        if not line.strip():
            continue
        cur = len(line) - len(line.lstrip())
        if cur < indent:
            break
        if cur == indent and line.lstrip().startswith("* "):
            items.append(line.strip()[2:])
    return items


def text_block(block):
    m = re.search(r"```text\n(.*?)```", block, re.S)
    return dedent(m.group(1)) if m else ""


def build(sid):
    md = (ROOT / "6141.md").read_text()
    sec = section(md, sid)
    module = sid.split(".")[0]
    full_title = re.match(r"### Session [\d.]+: ([^\n]+)", sec).group(1)
    S = []

    # 1. Overview
    _, _, b1 = part(sec, 1)
    _, _, b2 = part(sec, 2)
    purpose = bullets(b1)
    outcomes = []
    for line in b2.splitlines():
        m = re.match(r"\s*\d+\. \"([^\"]+)\": (.*)$", line)
        if m:
            outcomes.append(f'<li><span class="q">"{inline(m.group(1))}"</span> {inline(cap(m.group(2)))}</li>')
    S.append(slide(module, "1-2. Purpose and Outcomes", f"Session {sid}: {html.escape(full_title)}",
                   '  <div class="body grid2 overview">' +
                   card("THE BUSINESS SITUATION", "", ul(purpose) + '<p class="flow">Today\'s flow: 60 min lecture, then 120 min hands-on lab</p>') +
                   card("EXPECTED OUTCOMES", "By the end of today, you will be able to:", f'<ol class="biz">{"".join(outcomes)}</ol>') +
                   "</div>"))

    # 2. Session map (content from scripts/session_map.py)
    S.append(slide(module, "Session Map", "Session Map: Follow the Numbers", map_body(sid)))

    # 3-4. Business context and data basics: bullets + first table
    for num, kick in ((3, "3. Business Context"), (4, "4. Data Basics")):
        title, rest, body = part(sec, num)
        heading = title.split(": ", 1)[-1] if ": " in title else title
        tbls = tables(body)
        left = card("KEY POINTS", "", (f"<p>{inline(rest)}</p>" if rest else "") + tree(body))
        if tbls:
            right = card("SEE IT ON REAL DATA" if num == 3 else "AT A GLANCE", "", table_html(*tbls[0]))
            inner = f'  <div class="body grid2" style="grid-template-columns: 1fr 1.15fr;">{left}{right}</div>'
        else:
            inner = f'  <div class="body">{left}</div>'
        S.append(slide(module, kick, inline(heading), inner))

    # 5. Dataset
    _, _, b5 = part(sec, 5)
    cols = []
    for line in b5.splitlines():
        m = re.match(r"\s*\* `([^`]+)`: (.*)$", line)
        if m:
            cols.append((m.group(1), m.group(2)))
    files = []
    for f in re.findall(r"\(?(data/[\w./-]+\.\w+)", b5):
        if f not in files:
            files.append(f)
    files = [f"`{f}`" for f in files]
    rows = "".join(f"<tr><td><code>{html.escape(c)}</code></td><td>{inline(d)}</td></tr>" for c, d in cols[:9])
    S.append(slide(module, "5. Lab Practice Dataset", "The Data for Today",
                   f'  <div class="body grid2" style="grid-template-columns: 1fr 2.2fr;">'
                   + card("FILES", "", ul(files[:4]) + f"<p>{inline(first_sentence(bullets(b5)[-1] if bullets(b5) else ''))}</p>")
                   + card("COLUMNS", "", f'<table class="mdtable cols">{rows}</table>') + "</div>"))

    # 6. Keywords
    _, _, b6 = part(sec, 6)
    kw = re.findall(r"(?m)^  \* (.+?):\n    \* What: (.+)\n    \* Why: (.+)$", b6)
    cards = "".join(card(f"TERM {i}", inline(t), f'<p class="what"><b>What:</b> {inline(first_sentence(w))}</p><p class="why"><b>Why:</b> {inline(first_sentence(y))}</p>')
                    for i, (t, w, y) in enumerate(kw, 1))
    S.append(slide(module, "6. Keywords", f"{len(kw)} Terms You Need Today",
                   f'  <div class="body grid3" style="grid-template-rows: repeat({(len(kw)+2)//3}, 1fr);">{cards}</div>'))

    # 7.x concepts
    _, _, b7 = part(sec, 7)
    concepts = re.split(r"(?m)^(?=  \* \*\*7\.\d )", b7)[1:]
    parsed = []
    for c in concepts:
        head = re.match(r"  \* \*\*(7\.\d) ([^*]+)\*\*", c)
        rem = re.search(r"\* \*Remember:\* (.+)", c)
        idea = re.search(r"\* \*The idea:\* (.+)", c)
        first = re.split(r"(?<=[.!?])\s", idea.group(1))[0] if idea else ""
        parsed.append((head.group(1), head.group(2), first, rem.group(1) if rem else "", tables(c)))

    # 7. Real-data table from the first concept that has one
    def concept_table_slide(kicker, picks):
        for num, name, first, rem, tb in picks:
            if tb:
                head, rows = tb[0]
                return slide(module, kicker, f"{num} {inline(name.split(': ')[0])}: On Real Data",
                             f'  <div class="body" style="flex-direction: column; gap: .12in;">'
                             + card("SEE IT ON REAL DATA", "", table_html(head, rows[:8]), start=19)
                             + f'<div class="check"><b>Remember:</b> {inline(rem)}</div></div>')
        return None
    # 8. Foundations overview
    n = len(parsed)
    colsn = 3 if n > 4 else 2
    rowsn = (n + colsn - 1) // colsn
    fc = "".join(card(num, inline(name.split(": ")[0]), f'<p class="remember"><b>Remember:</b> {inline(rem)}</p>', start=24)
                 for num, name, first, rem, _ in parsed)
    S.append(slide(module, "7. Core Foundations", "How It Works",
                   f'  <div class="body f7" data-uniform style="display:grid; grid-template-columns: repeat({colsn}, 1fr); grid-template-rows: repeat({rowsn}, 1fr); gap: .16in;">{fc}</div>'))

    # 8. One real-data table (the first concept that has one)
    S.append(concept_table_slide("7. Core Foundations: On Real Data", parsed))

    # No IDE slide: it is the same every session. The one session-specific line,
    # the pip install, goes on Demo 1.
    pip = re.search(r"First time only: `pip install ([^`]+)`", sec)

    # 11-16. Demos and Quick Checks
    _, _, b9 = part(sec, 9)
    for k in (1, 2, 3):
        m = re.search(rf"(?m)^  \* \*Micro-Example {k} \(([^)]*(?:\([^)]*\)[^)]*)*)\):\* `([^`]+)`", b9)
        start = m.start()
        qc_m = re.search(rf"(?m)^  \* \*Quick Check {k} ", b9[start:])
        demo = b9[start: start + qc_m.start()]
        nxt = re.search(rf"(?m)^  \* \*Micro-Example {k+1} |\Z", b9[start + qc_m.start():])
        qblock = b9[start + qc_m.start(): start + qc_m.start() + (nxt.start() if nxt else len(b9))]
        src = dedent(code_blocks(demo)[0])
        how = sub_bullets(demo, "How it works, line by line")
        read = sub_bullets(demo, "Read the output")
        out = text_block(demo)
        if out and len(out.splitlines()) > 4:
            out = "\n".join(out.splitlines()[:3] + ["..."])
        how_items = [first_sentence(x) for x in how[:3]]
        if k == 1 and pip:
            how_items = [f"First time only, in the Terminal: `pip install {pip.group(1)}`"] + how_items[:2]
        right = card("HOW IT WORKS", "", ul(how_items), cls="card fitbox how", start=17)
        right += card("READ THE OUTPUT", "", (f'<div class="outbox">{html.escape(out)}</div>' if out and max(len(l) for l in out.splitlines()) <= 52 else "") + ul([first_sentence(x) for x in read[:1]]), cls="card fitbox out", start=17)
        S.append(slide(module, f"9. Code Demonstration {k}", inline(m.group(1)), f'''  <div class="body">
    <div class="code-panel fitbox" data-start="15.5" data-floor="13">
      <div class="code-header"><span class="dot" style="background:#EF4444"></span><span class="dot" style="background:#F59E0B"></span><span class="dot" style="background:#22C55E"></span>&nbsp;{html.escape(m.group(2))}<span class="ipo">Input &#8594; Process &#8594; Output</span></div>
<pre>{highlight(src)}</pre>
    </div>
    <div class="notes">{right}</div>
  </div>'''))
        qtitle = re.match(r"  \* \*Quick Check \d \((.*)\):\*", qblock).group(1)
        qb = bullets(qblock, 4)
        tool = next((x for x in qb if x.startswith("New tool:")), "")
        task = next((x for x in qb if x.startswith("Task:")), "")
        check = next((x for x in qb if x.startswith("Check:")), "")
        S.append(slide(module, f"9. Quick Check {k}", f"Quick Check {k}: {inline(qtitle)}", f'''  <div class="body" style="flex-direction: column; gap: 0;">
    <div class="grid2 qc" style="flex: 1; min-height: 0;">
      {card("NEW TOOL", inline(qtitle), f"<p>{inline(tool[len('New tool: '):])}</p>", start=20)}
      {card("YOUR TASK", "Fill in the Blank", f"<p>{inline(cap(task[len('Task: '):]))}</p>", start=20)}
    </div>
    <div class="check"><b>Check:</b> {inline(check[len('Check: '):])}</div>
  </div>'''))

    # 17. References
    _, _, b10 = part(sec, 10)
    refs = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", b10)
    rc = "".join(card("REFERENCE", html.escape(t.replace("`", "")), f"<p>{html.escape(u)}</p>") for t, u in refs[:4])
    S.append(slide(module, "10. Official References", "Where to Look Things Up",
                   f'  <div class="body" style="flex-direction: column; gap: .14in;">{rc}</div>'))

    # Exercises: one slide, Goal / File / Check each; full steps stay in 6141.md
    from slide_briefs import EXERCISES
    ex_cards = ""
    for n, level, (goal, check) in zip((11, 12, 13), ("GUIDED", "APPLIED", "ADVANCED"), EXERCISES[sid]):
        tt, _, bb = part(sec, n)
        f = re.search(r"`(YourName_S\d\d_\w+\.py)`", bb).group(1)
        ex_cards += card(f"EXERCISE {n - 10}: {level}", inline(tt.split(" - ", 1)[-1]),
                         f"<p><b>Goal:</b> {inline(goal)}</p><p><b>File:</b> <code>{f}</code></p>"
                         f'<p class="remember"><b>Check:</b> {inline(check)}</p>', start=21)
    S.append(slide(module, "11-13. Exercises", "Three Exercises", f'''  <div class="body" style="flex-direction: column; gap: 0;">
    <div class="grid3 exg" data-uniform style="flex: 1; min-height: 0;">{ex_cards}</div>
    <div class="check">Full steps for all three exercises: sections 11-13 of the course page.</div>
  </div>'''))

    out = (f'<!doctype html>\n<html lang="en-US">\n<head>\n<meta charset="utf-8">\n<title>Session {sid} Lecture</title>\n'
           f'<style>\n{CSS}\n{EXTRA_CSS}\n</style>\n</head>\n<body>\n\n' + "\n".join(S) + AUTOFIT + "\n</body>\n</html>\n")
    total = out.count('<section class="slide">')
    c = iter(range(1, 100))
    out = re.sub(r"Slide \d+ / \d+", lambda _: f"Slide {next(c)} / {total}", out)
    mm, ss = sid.split(".")
    path = ROOT / "slides_src" / f"session_0{mm}_0{ss}.html"
    path.write_text(out)
    print(f"{path.name}: {total} slides")


if __name__ == "__main__":
    for s in sys.argv[1:]:
        build(s)
