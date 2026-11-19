"""Hand-built story-order deck for Session 4.2: problem and result first, then how each preparation step got there."""
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
head = head.replace("<title>Session 3.1 Lecture</title>", "<title>Session 4.2 Lecture</title>")
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
sec = md[md.index('<a id="session-04-02"></a>'): md.index('<a id="session-04-03"></a>')]
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
    return f'<div class="figbox"><img src="../assets/session_04_02_fig_{name}.png" alt="{e(alt)}"></div>'


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




slide("The Problem and the Result", "Session 4.2: Which Members Should Get Which Offer?",
      '<div class="card fitbox" data-start="22"><div class="tag">THE PROBLEM</div>'
      + ul(["A drink shop's membership app: some regulars slowly stop coming",
            "Offers: a **free drink** (NT$45, brings back 25%) or a **BOGO month** (NT$150, 45%)",
            "Members bring in very different profit: NT$30 to NT$265 a month",
            "The owner asks: who is about to stop, how much profit is at stake, and which offer pays?"])
      + '<p class="flow">Today: the result first, then the steps</p></div>'
      '<div class="card fitbox" data-start="22"><div class="tag">THE RESULT (12 CURRENT MEMBERS)</div>'
      + table([["Plan", "Contacted", "Net benefit"],
               ["Coupon if chance 0.5 or more", "3", "NT$689"],
               ["Coupon if chance 0.3 or more", "7", "NT$1,349"],
               ["Coupon where it pays", "8", "NT$1,441"],
               ["Best offer per member", "8", "NT$2,059"]], rowcls=["old", None, None, "best"])
      + '<p class="answer">Profit at risk: <b>NT$7,355</b>. Judge each member by expected money, not by one cut-off.</p></div>',
      "body grid2 overview\" style=\"grid-template-columns: 1fr 1.2fr;")

slide("Key Ideas", "Learn from the Past, Act on the Present",
      '<div class="stack"><div class="card fitbox" data-start="24">'
      + table([["File", "Members", "Outcome known?", "Used to"],
               ["History", "30 past members", "yes: stopped or stayed", "train the churn model"],
               ["Active", "12 current members", "no, not yet", "score and choose offers"]])
      + '</div><div class="check">An offer can only help members who have not left yet. <b>Churn</b> = customers leaving.</div></div>')

slide("Key Ideas", "Expected Value: A Chance Times an Amount",
      '<div class="stack">' + fig("expected_value", "Expected value of a coupon for one member")
      + '<div class="card fitbox" data-start="22">'
      + ul(["**Net benefit** = saved profit - cost (NT$): what the campaign adds to profit",
            "**ROI** = net benefit / cost x 100 (%): what each NT$1 spent brings back"])
      + "</div></div>")

slide("The Data", "Two Small Files (Fictional Teaching Data)",
      '<div class="stack"><div class="card fitbox" data-start="24">'
      + ul(["`session_04_02_dataset.csv`: **30 past members**; 11 stopped coming within 60 days",
            "`session_04_02_active.csv`: **12 current members**, same columns, no outcome",
            "Clues: months as member, visits last month, days since last visit",
            "`Monthly_Profit_TWD`: the shop's profit from the member per month (NT$30-265)"])
      + "</div></div>")

code_slide("Step 1", "Step 1: Who Is About to Stop Coming?", "YourName_S42_step_1.py", codes[0],
           ["`history` trains the model; `active` is only scored",
            "Same pipeline as 3.4 and 4.1: scale, then classify"],
           "\n".join(outs[0].rstrip().split("\n")[:8] + ["... (6 more members)"]), "past stop rate: `0.37` (11 of 30)")

slide("Step 1", "Step 1: Three Members Are Very Likely to Stop",
      '<div class="stack"><div class="card fitbox" data-start="24">'
      + ul(["`NOW-209`, `NOW-203`, `NOW-201`: chances above `0.7`",
            "`NOW-201` and `NOW-203`: no visit for over 50 days",
            "`NOW-209`: last visit 29 days ago, but no visit at all last month",
            "Four members are clearly safe (chances below `0.03`)"])
      + '</div><div class="check"><b>Common mistake:</b> training on the current members. They have no outcome yet: they are only scored.</div></div>')

code_slide("Step 2", "Step 2: How Much Profit Is at Risk?", "YourName_S42_step_2.py", codes[1],
           ["Yearly profit = monthly profit x 12",
            "Profit at risk = chance x yearly profit: the expected loss"],
           "\n".join(outs[1].rstrip().split("\n")[:8] + ["... (6 more members)", outs[1].rstrip().split("\n")[-1]]), "the top 3 hold `0.56` of the risk")

slide("Step 2", "Step 2: Ranked by Money, the Order Changes",
      '<div class="stack">' + fig("chance_vs_risk", "Ranked by chance and by profit at risk")
      + '<div class="check"><code>NOW-203</code>: very likely to stop, but only NT$600 a year. <code>NOW-204</code>: a lower chance, but the most profit (NT$3,180).</div></div>')

slide("Step 2", "Why Multiply by the Chance?",
      '<div class="stack"><div class="card fitbox" data-start="24">'
      + ul(["A member with a `0.4` chance costs, on average, 40% of their profit, not 100%",
            "The expected value is a fair average over many members like them",
            "One year of profit is a cautious basis; a member's whole value over many years is the **CLV** (Customer Lifetime Value)"])
      + '</div><div class="check">Total profit at risk for the 12 members: <b>NT$7,355</b>.</div></div>')

code_slide("Step 3", "Step 3: Is a Coupon Worth It for Each Member?", "YourName_S42_step_3.py", "# 1. Input: score the members and add Annual_Profit, as in Step 2\n# (full code: section 8 of the reading)\n\n# 2. Process" + codes[2].split("# 2. Process")[1],
           ["Saved = chance x success rate x yearly profit",
            "Coupon net = saved - NT$45; send only where it is above 0"],
           "\n".join(outs[2].rstrip().split("\n")[:6] + ["... (8 more members)"] + outs[2].rstrip().split("\n")[-2:]), "success rate `0.15`: 8 coupons, net NT$`721`")

slide("Step 3", "Step 3: 8 Coupons Pay, 4 Do Not",
      '<div class="stack"><div class="card fitbox" data-start="24">'
      + ul(["A coupon pays even for `NOW-202` (chance `0.296`): it brings in enough profit",
            "For the 4 safe members, each coupon loses about NT$30 to NT$45",
            "Net benefit **NT$1,441**: more than any single cut-off on the chance"])
      + '</div><div class="check"><b>Common mistake:</b> sending an offer to everyone "just in case".</div></div>')

slide("Plans", "Highest ROI or Most Profit?",
      '<div class="stack"><div class="card fitbox" data-start="24">'
      + table([["Cut-off", "Contacted", "Net benefit", "ROI"],
               ["0.3", "7", "NT$1,348.89", "428.2%"], ["0.4", "4", "NT$778.54", "432.5%"],
               ["0.5 to 0.7", "3", "NT$689.36", "510.6%"]], rowcls=["best", None, "old"])
      + '</div><div class="check">The small campaign has the highest ROI; the larger one adds the most profit. If the shop can afford it, choose the net benefit.</div></div>')

slide("Summary", "From a Chance to a Decision in NT$",
      '<div class="stack">' + fig("chance_to_decision", "From a chance to a decision")
      + '<div class="check"><b>Remember:</b> chance x money = expected value; send an offer only when its expected saved profit beats its cost; the highest ROI is not always the most profit.</div></div>')

def ex_slide(n, level, title, goal, file, steps, check):
    slide(f"Exercise {n}: {level}", f"Exercise {n}: {title}",
          '<div class="stack"><div class="card fitbox" data-start="24">'
          f'<p><b>Goal:</b> {inline(goal)}</p><p><b>Script:</b> <code>{file}</code></p>' + ul(steps)
          + f'</div><div class="check"><b>Check:</b> {inline(check)}</div></div>')






ex_slide(1, "Guided", "The Business Case at One Cut-Off",
         "price a coupon campaign for members with a chance of 0.5 or more",
         "YourName_S42_case.py",
         ["Copy part 1 of Step 3; parts 2-3 in section 11 of the reading",
          "Saved profit, cost, net benefit, and ROI",
          "In two comments: why multiply by the chance instead of counting the full yearly profit?"],
         "3 members; net NT$`689.36`; ROI `510.6`%")
ex_slide(2, "Applied", "Highest ROI or Most Profit?",
         "repeat the business case for the cut-offs 0.3 to 0.7",
         "YourName_S42_cutoffs.py",
         ["Collect cut-off, targeted, saved, cost, net benefit, ROI in one DataFrame",
          "Scoring with 2 features stops with a `ValueError`: ask the AI Chat why",
          "Print the best ROI and the best net benefit"],
         "best ROI `0.7` (`510.6`%); best net `0.3` (NT$`1,348.89`)")
ex_slide(3, "Advanced", "The Best Offer for Each Member",
         "choose BOGO, coupon, or nothing for each member by expected net value",
         "YourName_S42_offers.py",
         ["Coupon: NT$45, 25%; BOGO: NT$150, 45%",
          "Ordered rules with `.loc[]`: default None, then Coupon, then BOGO",
          "Requirements and hints: section 13 of the reading"],
         "7 BOGO, 1 coupon, 4 none: NT$`2,059.42`")

N = len(slides)
parts = []
for i, (kicker, title, body, cls) in enumerate(slides, 1):
    parts.append(f'<section class="slide">\n  <div><span class="eyebrow">MODULE 4</span><span class="kicker">{e(kicker)}</span></div>\n'
                 f'  <div class="title">{e(title)}</div><div class="rule"></div>\n  <div class="{cls}">{body}</div>\n'
                 f'  <div class="footer"><span>Business Analytics &amp; AI Application | Course 6141</span><span>Slide {i} / {N}</span></div>\n</section>\n')
out = head + EXTRA + "</style>\n</head>\n<body>\n" + "\n".join(parts) + "\n" + script
(ROOT / "slides_src" / "session_04_02.html").write_text(out)
print("slides:", N)
