"""Hand-built story-order deck for Session 4.4: problem and result first, then how each preparation step got there."""
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
here = Path(__file__).resolve().parent
old = (here / "deck_template.html").read_text()
head = old[:old.index("</style>")]
script = old[old.rindex("<script>"):].replace("[...box.querySelectorAll('pre')].some((pre) => pre.scrollHeight > pre.clientHeight + 6 || pre.scrollWidth > pre.clientWidth + 6)", "[...box.querySelectorAll('pre, .outbox')].some((pre) => pre.scrollHeight > pre.clientHeight + 6 || pre.scrollWidth > pre.clientWidth + 2)")
assert ".outbox')].some" in script
head = head.replace("<title>Session 3.1 Lecture</title>", "<title>Session 4.4 Lecture</title>")
EXTRA = """
.stack { display: flex; flex-direction: column; gap: .14in; width: 100%; min-height: 0; }
.answer { font-size: 19pt; margin: .06in 0; line-height: 1.25; }
.answer b { color: #991B1B; }
.mdtable td.good { background: #DCFCE7; font-weight: bold; }
.mdtable td.bad { background: #FEE2E2; }
.mdtable tr.best td { background: #DCFCE7; font-weight: bold; }
.mdtable tr.old td { background: #FEF3C7; }
.code-panel.w55 { width: 55%; }
.code-panel.w48 { width: 48%; }
.lead-q { font-size: 22pt; font-style: italic; color: #991B1B; margin: .06in 0 .1in; }
.mdtable td, .mdtable th { vertical-align: middle; }
.check { font-size: 22pt; }
.check p { margin: 0; }
.stack .card { flex-shrink: 0; }
.mdtable.files code { white-space: nowrap; overflow-wrap: normal; }
.overview { grid-template-columns: 1fr 1.25fr; }
.answer { font-size: inherit; }
.outbox.wrap { white-space: pre-wrap; overflow-wrap: anywhere; }
.code-panel.w46 { width: 46%; }
.stack { height: 100%; }
.figbox { flex: 1 1 0; min-height: 0; display: flex; align-items: center; justify-content: center; }
.figbox img { max-width: 100%; max-height: 100%; object-fit: contain; display: block; }
.figrow { display: grid; gap: .22in; width: 100%; min-height: 0; }
.figrow > .figbox { height: 100%; }
.figrow > .card { align-self: center; }
"""
md = (ROOT / "6141.md").read_text()
sec = md[md.index('<a id="session-04-04"></a>'):]
codes = [re.sub(r"(?m)^    ", "", c) for c in re.findall(r"```python\n(.*?)```", sec, re.S)]
outs = [re.sub(r"(?m)^    ", "", c) for c in re.findall(r"```text\n(.*?)```", sec, re.S)]

e = html.escape


def inline(t):
    t = e(t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    return re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)


def code_html(c):
    lines = []
    for ln in c.rstrip("\n").split("\n"):
        if re.match(r"\s*# \d\.", ln):
            lines.append(f'<span class="sec">{e(ln)}</span>')
        else:
            lines.append(e(ln))
    return "\n".join(lines)


def table(rows, cls="mdtable", rowcls=None):
    h = "".join(f"<th>{inline(c)}</th>" for c in rows[0])
    body = ""
    for i, r in enumerate(rows[1:]):
        rc = f' class="{rowcls[i]}"' if rowcls and rowcls[i] else ""
        body += f"<tr{rc}>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>"
    return f'<table class="{cls}"><thead><tr>{h}</tr></thead><tbody>{body}</tbody></table>'


def ul(items):
    return '<ul class="tight">' + "".join(f"<li>{inline(i)}</li>" for i in items) + "</ul>"


slides = []


def fig(name, alt):
    return f'<div class="figbox"><img src="../assets/session_04_04_fig_{name}.png" alt="{e(alt)}"></div>'


def slide(kicker, title, body, cls="body"):
    slides.append((kicker, title, body, cls))




def code_slide(kicker, title, fname, code, how, out, check, start="21", width="w55", wrap=False):
    slide(kicker, title,
          f'<div class="code-panel {width} fitbox" data-start="{start}" data-floor="13"><div class="code-header">'
          '<span class="dot" style="background:#EF4444"></span><span class="dot" style="background:#F59E0B"></span>'
          f'<span class="dot" style="background:#22C55E"></span>&nbsp;{fname}<span class="ipo">Input &#8594; Process &#8594; Output</span></div>'
          f"<pre>{code_html(code)}</pre></div>"
          '<div class="notes"><div class="card fitbox how" data-start="21"><div class="tag">HOW IT WORKS</div>' + ul(how) + "</div>"
          f'<div class="card fitbox out" data-start="21"><div class="tag">OUTPUT</div><div class="outbox{' wrap' if wrap else ''}">{e(out.rstrip())}</div></div>'
          f'<div class="check fitbox" data-start="20"><p><b>Quick Check:</b> {inline(check)}</p></div></div>')




slide("The Problem and the Result", "Session 4.4: Is the Internship Screening Tool Fair?",
      '<div class="card fitbox" data-start="22"><div class="tag">THE PROBLEM</div>'
      + ul(["An AI tool scores internship applicants; **0.70 or more** gets an interview",
            "It uses GPA, a coding test, and the number of club activities",
            "Two protected groups, A and B: the tool never sees the group",
            "Recruiting asks: are both groups invited at similar rates, why was each applicant rejected, and what should we do?"])
      + '<p class="flow">Today: the result first, then the audit</p></div>'
      '<div class="card fitbox" data-start="22"><div class="tag">THE RESULT (20 APPLICANTS)</div>'
      + table([["", "Group A", "Group B"], ["Invited", "70%", "30%"], ["GPA (average)", "3.31", "3.35"],
               ["Coding test (average)", "70.7", "70.1"], ["Club activities (average)", "3.4", "1.1"]], rowcls=["old", None, None, "old"])
      + '<p class="answer">Ratio <b>0.429</b>: fails the four-fifths rule. Same skills; the gap comes from club activities.</p></div>',
      "body grid2 overview\" style=\"grid-template-columns: 1fr 1.2fr;")

slide("Key Ideas", "Unfair Without Seeing the Group",
      '<div class="stack">' + fig("proxy", "How a proxy feature creates a gap")
      + '<div class="check">A feature that differs between groups (a <b>proxy</b>) carries the gap into the score. Nobody intended it.</div></div>')

slide("Key Ideas", "Two Kinds of Unfair Treatment and a First Test",
      '<div class="stack"><div class="card fitbox" data-start="23">'
      + table([["Idea", "Meaning"],
               ["Disparate treatment", "deciding by group, e.g. a different threshold per group: forbidden"],
               ["Disparate impact", "one rule for all, but one group is selected far less often: investigate"],
               ["Four-fifths rule", "a group's rate below 80% of the highest rate needs review"],
               ["Feature effect", "coefficient x (value - average): what pushed the score down"]])
      + '</div><div class="check">Failing the four-fifths rule is a reason to investigate, not proof of discrimination. The EU AI Act treats AI in hiring as high-risk.</div></div>')

slide("The Data", "One Small File (Fictional Teaching Data)",
      '<div class="stack"><div class="card fitbox" data-start="24">'
      + ul(["`session_04_04_dataset.csv`: **20 internship applicants**, 10 per group",
            "`Group`: `Group_A` or `Group_B`, a protected characteristic, used only for the audit",
            "`GPA`, `Coding_Test_Score` (0-100), `Club_Activities_Count` (0-5)",
            "`Screening_Score`: the tool's score; invited at `0.70` or more"])
      + "</div></div>")

code_slide("Step 1", "Step 1: Are Both Groups Invited at Similar Rates?", "YourName_S44_step_1.py", codes[0],
           ["Mean of a 0/1 column = the invite rate",
            "Ratio = lower rate / higher rate; pass at `0.80`"],
           outs[0], "`pd.crosstab()`: A 7 invited, B 3 invited")

slide("Step 1", "Step 1: Group B Is Far Below the Line",
      '<div class="figrow" style="grid-template-columns: 1.4fr 1fr;">' + fig("rates", "Invite rates and the four-fifths line")
      + '<div class="card fitbox" data-start="22">'
      + ul(["7 of 10 in Group A, 3 of 10 in Group B",
            "Four-fifths of 70% is 56%: Group B's 30% is far below",
            "**Common mistake:** \"the tool never sees the group, so it is fair\""])
      + "</div></div>")

code_slide("Step 2", "Step 2: Where Does the Gap Come From?", "YourName_S44_step_2.py", codes[1],
           ["Average each feature and the score by group",
            "`.T` flips the table: measures become rows"],
           outs[1], "clubs: Group A 1-5, Group B 0-3")

slide("Step 2", "Step 2: Same Skills, Fewer Clubs",
      '<div class="stack">' + fig("profiles", "Feature averages by group")
      + '<div class="check">The real question, for people: do club activities measure ability for this job, or free time? Students with part-time jobs have less time for clubs.</div></div>')

code_slide("Step 3", "Step 3: Why Was Each Applicant Rejected?", "YourName_S44_step_3.py", codes[2],
           ["A linear model copies the hidden score (a surrogate)",
            "Effect = coefficient x (value - average); `idxmin` gives the main reason"],
           "\n".join(outs[2].rstrip().split("\n")[:8] + ["... (5 more rejected applicants)"]), "Group B: clubs is the main reason 5 times")

slide("Step 3", "Step 3: Two Applicants Side by Side",
      '<div class="stack">' + fig("two_applicants", "Feature effects for APP-315 and APP-319")
      + '<div class="check"><code>APP-315</code> has the better GPA and coding score but no clubs: rejected. <code>APP-319</code> has weaker skills but 5 clubs: invited.</div></div>')

slide("Step 3", "Step 3: The Main Reason for Each Rejection",
      '<div class="stack"><div class="card fitbox" data-start="24">'
      + table([["Rejected in", "GPA", "Coding test", "Club activities"],
               ["Group A (3)", "1", "2", "0"], ["Group B (7)", "0", "2", "5"]], rowcls=[None, "old"])
      + '</div><div class="check">The copy explains 98.7% of the scores (R-squared <code>0.987</code>), so these reasons can be trusted. <b>Common mistake:</b> explaining a model you have not checked.</div></div>')

slide("Decide", "What a Fix May and May Not Do",
      '<div class="stack"><div class="card fitbox" data-start="23">'
      + table([["Possible fix", "Allowed?"],
               ["A lower threshold for Group B", "no: deciding by group"],
               ["One lower threshold for everyone", "only with care (Exercise 3)"],
               ["Review whether club activities belong in the score", "yes: fixes the cause"],
               ["A person reviews applicants just below 0.70", "yes: human oversight"],
               ["Document every test and decision", "yes: accountability"]], rowcls=["old", None, "best", "best", "best"])
      + "</div></div>")

slide("Summary", "A Fairness Audit in Three Steps",
      '<div class="stack">' + fig("audit_steps", "The audit steps")
      + '<div class="check"><b>Remember:</b> a tool can be unfair without seeing the group; compare rates, find the feature behind the gap, explain each decision, never decide by group, and write everything down.</div></div>')

def ex_slide(n, level, title, goal, file, steps, check):
    slide(f"Exercise {n}: {level}", f"Exercise {n}: {title}",
          '<div class="stack"><div class="card fitbox" data-start="24">'
          f'<p><b>Goal:</b> {inline(goal)}</p><p><b>Script:</b> <code>{file}</code></p>' + ul(steps)
          + f'</div><div class="check"><b>Check:</b> {inline(check)}</div></div>')








ex_slide(1, "Guided", "The Audit Report",
         "a report with counts, rates, the ratio, and an alert",
         "YourName_S44_audit.py",
         ["Type the code in section 11 of the reading",
          "`.map()` turns True/False into Invited/Rejected",
          "In two comments: why investigate, and why failing is not proof?"],
         "A 70%, B 30%; ratio `0.429`; the `ALERT` line prints")
ex_slide(2, "Applied", "A Reusable Audit Function and a Governance Record",
         "a function for any threshold, and a one-row record for management",
         "YourName_S44_record.py",
         ["`screening_audit(df, threshold)` returns `rates, ratio`",
          "`print(ratio)` outside the function: `NameError`; ask the AI Chat why",
          "Save the record to `data/governance_record.csv`"],
         "`Ratio` `0.429`, `Status` `Review before use`")
ex_slide(3, "Advanced", "Can One Shared Threshold Fix the Gap?",
         "test thresholds 0.50 to 0.80 for fairness and for the coding skill bar (60)",
         "YourName_S44_threshold.py",
         ["Count invites below the skill bar at each threshold",
          "Find the highest passing threshold, with and without below-bar invites",
          "Requirements and hints: section 13 of the reading"],
         "only `0.50` passes, with `3` below the skill bar: the threshold cannot fix it")

N = len(slides)
parts = []
for i, (kicker, title, body, cls) in enumerate(slides, 1):
    parts.append(f'<section class="slide">\n  <div><span class="eyebrow">MODULE 4</span><span class="kicker">{e(kicker)}</span></div>\n'
                 f'  <div class="title">{e(title)}</div><div class="rule"></div>\n  <div class="{cls}">{body}</div>\n'
                 f'  <div class="footer"><span>Business Analytics &amp; AI Application | Course 6141</span><span>Slide {i} / {N}</span></div>\n</section>\n')
out = head + EXTRA + "</style>\n</head>\n<body>\n" + "\n".join(parts) + "\n" + script
(ROOT / "slides_src" / "session_04_04.html").write_text(out)
print("slides:", N)
