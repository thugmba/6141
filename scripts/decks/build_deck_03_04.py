"""Hand-built story-order deck for Session 3.4: problem and result first, then how each preparation step got there."""
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
head = head.replace("<title>Session 3.1 Lecture</title>", "<title>Session 3.4 Lecture</title>")
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
sec = md[md.index('<a id="session-03-04"></a>'): md.index('<a id="session-04-01"></a>')]
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
    return f'<div class="figbox"><img src="../assets/session_03_04_fig_{name}.png" alt="{e(alt)}"></div>'


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




slide("The Problem and the Result", "Session 3.4: Who Should Get a \"Come Back\" Coupon?",
      '<div class="card fitbox" data-start="22"><div class="tag">THE PROBLEM</div>'
      + ul(["The music app sends a NT$60 coupon to users likely to cancel",
            "**Missed** canceller: NT$1,800 lost. **False alarm**: NT$60 wasted",
            "Marketing also wants to know what kinds of listeners there are",
            "The manager asks: who gets a coupon, how good is the model beyond accuracy, and what groups exist?"])
      + '<p class="flow">Today: the result first, then the classifier and K-Means</p></div>'
      '<div class="card fitbox" data-start="22"><div class="tag">THE RESULT (20 TEST USERS)</div>'
      + table([["Threshold", "Missed", "False alarms", "Cost"],
               ["0.5 (default)", "2 of 7", "2", "NT$3,720"],
               ["0.3 (by cost)", "0 of 7", "3", "NT$180"]], rowcls=["old", "best"])
      + '<p class="answer"><b>1.</b> Coupon at a chance of <b>0.3</b> or more: a miss costs 30 times a coupon.</p>'
        '<p class="answer"><b>2.</b> 80% accurate, yet 2 of 7 cancellers missed: look at <b>recall</b> and cost.</p>'
        '<p class="answer"><b>3.</b> K-Means finds steady (0% cancel), casual (29%), and drifting (79%) listeners.</p></div>',
      "body grid2 overview\" style=\"grid-template-columns: 1fr 1.3fr;")

slide("Key Ideas", "Two Kinds of Learning",
      '<div class="stack">' + fig("two_kinds", "Supervised and unsupervised learning")
      + '<div class="check"><b>Supervised:</b> past examples come with the answer; the model learns to predict it. <b>Unsupervised:</b> no answers; the method finds groups by itself.</div></div>')

slide("Key Ideas", "Four Cases and Three Scores",
      '<div class="stack"><div class="card fitbox" data-start="22"><div class="tag">A CLASSIFIER GIVES A CHANCE; A THRESHOLD DECIDES</div>'
      + table([["", "Coupon", "No coupon"], ["**Cancelled**", "TP: caught", "FN: missed (NT$1,800)"], ["**Stayed**", "FP: false alarm (NT$60)", "TN: left alone"]])
      + '</div><div class="card fitbox" data-start="22">'
      + table([["Score", "Formula", "Question"],
               ["Accuracy", "(TP+TN) / all", "share of decisions right?"],
               ["Precision", "TP / (TP+FP)", "coupons that went to real cancellers?"],
               ["Recall", "TP / (TP+FN)", "cancellers we caught?"]])
      + "</div></div>")

slide("The Data", "One Small File (Fictional Teaching Data)",
      '<div class="stack"><div class="card fitbox" data-start="24">'
      + ul(["`session_03_04_dataset.csv`: **40 music app users**, one row per user; 15 cancelled",
            "`User_ID` (label), `Weeks_Inactive_Count` (0-7), `Monthly_Minutes_Count` (60-2,800)",
            "`Cancelled_Binary`: `1` = cancelled the next month, `0` = stayed",
            "20 users train the classifier; 20 test it. K-Means uses all 40, without the answers"])
      + '</div><div class="check">Activate your <code>.venv</code> first (Python Setup Clinic).</div></div>')

code_slide("Step 1", "Step 1: Train a Classifier", "YourName_S34_step_1.py", codes[0],
           ["`make_pipeline(StandardScaler(), LogisticRegression())`: scale, then classify",
            "`predict_proba(X_test)[:, 1]`: each user's chance of cancelling"],
           "\n".join(outs[0].rstrip().split("\n")[:8]) + "\n... (14 more users)", "`model.predict(X_test).sum()` gives `7` coupons at 0.5")

slide("Step 1", "Step 1: A Good Ranking, Not a Perfect One",
      '<div class="stack"><div class="card fitbox" data-start="24">'
      + ul(["Long inactive and few minutes: chances near `1`; heavy recent listeners: near `0`",
            "`USR-334` (`0.73`) and `USR-337` (`0.63`) **stayed**",
            "`USR-315` (`0.40`) and `USR-338` (`0.36`) **cancelled**",
            "The model gives chances, not decisions: the threshold decides"])
      + '</div><div class="check"><b>Common mistake:</b> keeping both columns of <code>predict_proba()</code>. Keep <code>[:, 1]</code>, the chance of cancelling.</div></div>')

code_slide("Step 2", "Step 2: From Chances to Coupons", "YourName_S34_step_2.py", codes[1],
           ["`chance >= 0.5`: coupon or not, as `1` / `0`",
            "`confusion_matrix(...).ravel()`: TN, FP, FN, TP in that order"],
           outs[1], "\"never send\" is `0.65` accurate with recall `0`")

slide("Step 2", "Step 2: The Four Cases at Threshold 0.5",
      '<div class="figrow" style="grid-template-columns: 1.5fr 1fr;">' + fig("confusion", "Confusion matrix at threshold 0.5")
      + '<div class="card fitbox" data-start="22">'
      + ul(["Accuracy `0.80`: 16 of 20 decisions right",
            "Precision `0.71`: 5 of 7 coupons went to real cancellers",
            "Recall `0.71`: 5 of 7 cancellers caught; 2 missed (NT$1,800 each)"])
      + "</div></div>")

slide("Step 2", "Step 2: Move the Threshold",
      '<div class="stack">' + fig("threshold_line", "Test users sorted by chance with thresholds 0.5 and 0.3")
      + '<div class="check">Down to <b>0.3</b>: the 2 missed cancellers are caught, at the price of 1 more wasted coupon.</div></div>')

slide("Step 2", "Accuracy Hides the Costly Mistakes",
      '<div class="stack"><div class="card fitbox" data-start="24">'
      + table([["Rule", "Accuracy", "Recall", "Cost of mistakes"],
               ["Never send a coupon", "`0.65`", "`0.00`", "NT$`12,600`"],
               ["Model, threshold `0.5`", "`0.80`", "`0.71`", "NT$`3,720`"],
               ["Model, threshold `0.3`", "`0.85`", "`1.00`", "NT$`180`"]], rowcls=["old", None, "best"])
      + '</div><div class="check">Most users stay, so a lazy rule already looks 65% accurate. When one mistake is expensive, judge by <b>recall</b> and <b>cost</b>.</div></div>')

code_slide("Step 3", "Step 3: Find Groups Without Answers (K-Means)", "YourName_S34_step_3.py", codes[2],
           ["Only the 2 listening columns go in: no answers",
            "Scale first, then `KMeans(n_clusters=3)`; `.fit_predict()` gives each user a group"],
           outs[2], "`n_clusters=2`: two groups of 20 (75% and 0% cancelled)")

slide("Step 3", "Step 3: Three Kinds of Listeners",
      '<div class="figrow" style="grid-template-columns: 1.5fr 1fr;">' + fig("kmeans_groups", "K-Means groups of 40 users")
      + '<div class="card fitbox" data-start="22">'
      + ul(["**Steady**: 0.6 weeks, 2,117 minutes; 0% cancelled",
            "**Casual**: 3 weeks, 1,485 minutes; 29% cancelled",
            "**Drifting away**: 5.3 weeks, 591 minutes; 79% cancelled",
            "Group numbers are only names: read the profile"])
      + "</div></div>")

slide("Summary", "Choose the Threshold by Cost",
      '<div class="stack">' + fig("cost_by_threshold", "Cost of mistakes by threshold")
      + '<div class="check"><b>Remember:</b> a classifier gives chances; a threshold chosen by cost makes the decisions; recall shows what accuracy hides. Supervised predicts answers; unsupervised finds groups.</div></div>')

def ex_slide(n, level, title, goal, file, steps, check):
    slide(f"Exercise {n}: {level}", f"Exercise {n}: {title}",
          '<div class="stack"><div class="card fitbox" data-start="24">'
          f'<p><b>Goal:</b> {inline(goal)}</p><p><b>Script:</b> <code>{file}</code></p>' + ul(steps)
          + f'</div><div class="check"><b>Check:</b> {inline(check)}</div></div>')




ex_slide(1, "Guided", "What Do the Mistakes Cost?",
         "put a price on each kind of mistake at threshold 0.5",
         "YourName_S34_cost.py",
         ["Copy parts 1-2 of Step 2; part 3 in section 11 of the reading",
          "Cost = missed x NT$1,800 + false alarms x NT$60",
          "In two comments: which mistake makes most of the cost? Threshold up or down?"],
         "NT$`3,600` + NT$`120` = NT$`3,720`: the threshold should go **down**")
ex_slide(2, "Applied", "Find the Cheapest Threshold",
         "try thresholds 0.2 to 0.8 and keep the cheapest",
         "YourName_S34_threshold.py",
         ["Loop over `[0.2, 0.3, ..., 0.8]`; print caught, missed, false alarms, cost",
          "`confusion_matrix(y_test, chance)` stops with a `ValueError`: ask the AI Chat about \"continuous\"",
          "Print the cheapest threshold and its recall"],
         "`0.3`: NT$`180`, recall `1.00`")
ex_slide(3, "Advanced", "Is the Best-Ranking Model the Cheapest?",
         "compare weeks only, minutes only, and both with ROC-AUC and with the lowest cost",
         "YourName_S34_compare.py",
         ["`roc_auc_score(y_test, chance)`: how well the chances rank cancellers above stayers",
          "Find each model's cheapest threshold with the loop of Exercise 2",
          "Requirements and hints: section 13 of the reading"],
         "best AUC: weeks only (`0.934`); cheapest: both (NT$`180`)")

N = len(slides)
parts = []
for i, (kicker, title, body, cls) in enumerate(slides, 1):
    parts.append(f'<section class="slide">\n  <div><span class="eyebrow">MODULE 3</span><span class="kicker">{e(kicker)}</span></div>\n'
                 f'  <div class="title">{e(title)}</div><div class="rule"></div>\n  <div class="{cls}">{body}</div>\n'
                 f'  <div class="footer"><span>Business Analytics &amp; AI Application | Course 6141</span><span>Slide {i} / {N}</span></div>\n</section>\n')
out = head + EXTRA + "</style>\n</head>\n<body>\n" + "\n".join(parts) + "\n" + script
(ROOT / "slides_src" / "session_03_04.html").write_text(out)
print("slides:", N)
