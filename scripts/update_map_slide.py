#!/usr/bin/env python3
"""Render the Session Map (slide 2) from scripts/session_map.py.

map_body(sid) returns the slide body HTML; CSS and AUTOFIT are shared with the deck builder.
CLI: python3 scripts/update_map_slide.py 1.3 1.4 2.1   rewrites slide 2 of those hand-made decks.
"""
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from session_map import brief, items  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

MAP_CSS = """
/* session map with content */
.sm-phase.fitbox { display: flex; flex-direction: column; overflow: hidden; min-height: 0; }
.sm-phase p.sm-item { display: flex; gap: .1in; margin: .06in 0; line-height: 1.15; }
.sm-item i { font-style: normal; font-family: "DejaVu Sans Mono", monospace; font-weight: bold; color: #991B1B; min-width: .5in; flex-shrink: 0; }
.sm-p3 .sm-item i { color: #15803D; }
.sm-item b { display: block; font-size: 1em; }
.sm-item span.d { display: block; font-size: .9em; color: #334155; }
.sm-item code { font-size: .85em; white-space: normal; overflow-wrap: anywhere; }
/* end session map */
"""


def inline(text):
    parts = re.split(r"(`[^`]+`)", text)
    return "".join(f"<code>{html.escape(p[1:-1])}</code>" if p.startswith("`") and p.endswith("`") and len(p) > 1
                    else html.escape(p) for p in parts)


def map_body(sid):
    data = brief(items(sid))
    def col(lo, hi, cls, n, title, sub):
        rows = "".join(
            f'<p class="sm-item"><i>{it["num"]}.</i><span><b>{html.escape(it["name"])}</b>'
            f'<span class="d">{inline(it["detail"])}</span></span></p>'
            for it in data["items"] if lo <= it["num"] <= hi)
        return (f'<div class="sm-phase fitbox {cls}" data-start="22"><div class="sm-head"><span class="sm-step">{n}</span>'
                f'<span><b>{title}</b><small>{sub}</small></span></div>{rows}</div>')
    return ('  <div class="body" style="flex-direction: column; gap: .14in;">'
            f'<div class="sm-q"><b>Today\'s question:</b> {html.escape(data["question"])}</div>'
            f'<div class="sm-phases">{col(1, 4, "", 1, "Why it matters", "Lecture, part 1")}<div class="sm-arrow">&#8594;</div>'
            f'{col(5, 10, "", 2, "Learn the tools", "Lecture, part 2")}<div class="sm-arrow">&#8594;</div>'
            f'{col(11, 13, "sm-p3", 3, "Practice", "Lab")}</div></div>')


def update(sid):
    from build_deck_from_md import AUTOFIT
    mm, ss = sid.split(".")
    path = ROOT / "slides_src" / f"session_0{mm}_0{ss}.html"
    s = path.read_text()
    m = re.search(r'(<section class="slide">\s*<div><span class="eyebrow">[^<]*</span><span class="kicker">Session Map</span></div>\s*'
                  r'<div class="title">[^<]*</div><div class="rule"></div>\s*)(.*?)(\s*<div class="footer">)', s, re.S)
    s = s[:m.start(2)] + map_body(sid) + s[m.end(2):]
    s = re.sub(r"\n/\* session map with content \*/.*?(/\* end session map \*/\n|(?=</style>))", "", s, count=1, flags=re.S)
    s = s.replace("</style>", MAP_CSS + "</style>", 1)
    if "window.__fitDone" not in s:
        s = s.replace("</body>", AUTOFIT + "\n</body>", 1)
    path.write_text(s)
    print(f"{path.name}: slide 2 updated")


if __name__ == "__main__":
    for x in sys.argv[1:]:
        update(x)
