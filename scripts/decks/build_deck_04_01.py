"""Hand-built story-order deck for Session 4.1: problem and result first, then how each preparation step got there."""
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
head = head.replace("<title>Session 3.1 Lecture</title>", "<title>Session 4.1 Lecture</title>")
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
sec = md[md.index('<a id="session-04-01"></a>'): md.index('<a id="session-04-02"></a>')]
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
    return f'<div class="figbox"><img src="../assets/session_04_01_fig_{name}.png" alt="{e(alt)}"></div>'


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




slide("The Problem and the Result", "Session 4.1: How Does the Coupon Model Run Every Night?",
      '<div class="card fitbox" data-start="22"><div class="tag">THE PROBLEM</div>'
      + ul(["The coupon model of Session 3.4 must score new users **every night, by itself**",
            "Tonight is during final exams: students still open the app but listen much less",
            "The data team asks: how do we run it without retraining, how do we notice when tonight looks different, and what if the model file is missing?"])
      + '<p class="flow">Today: the result first, then save, score, and check drift</p></div>'
      '<div class="card fitbox" data-start="22"><div class="tag">THE RESULT</div>'
      + table([["Tonight", "Result"], ["Users scored", "10"], ["Coupons (chance 0.3 or more)", "5"],
               ["Minutes vs training", "-42.7%: drift flagged"]], rowcls=[None, "best", "old"])
      + '<p class="answer"><b>1.</b> Train once, save with <code>joblib</code>, load and score every night.</p>'
        '<p class="answer"><b>2.</b> Tonight\'s users listen 43% less: send the coupons, but flag the night for review.</p>'
        '<p class="answer"><b>3.</b> No model file? Use the 3-weeks rule (Session 3.1) instead of crashing.</p></div>',
      "body grid2 overview\" style=\"grid-template-columns: 1fr 1.2fr;")

slide("Key Ideas", "Train Once, Use Every Night",
      '<div class="stack">' + fig("decision_system", "Train once and save; every night ingest, validate, score, act")
      + '<div class="check">Training needs past users <b>with answers</b>, so it is done rarely. Scoring needs only the saved model, so it runs every night.</div></div>')

slide("Key Ideas", "Drift, Monitoring, and a Fallback",
      '<div class="stack"><div class="card fitbox" data-start="24">'
      + table([["Idea", "Meaning", "Today"],
               ["Data drift", "new data no longer looks like the training data", "exam season: minutes fall"],
               ["Monitoring", "a run log: records, latency (ms), accuracy per night", "Exercise 1"],
               ["Fallback", "a simple, safe rule when the model cannot run", "3+ weeks inactive (Exercise 2)"]])
      + '</div><div class="check">A model never says "I have not seen data like this": the system has to check and report it.</div></div>')

slide("The Data", "Three Small Files (Fictional Teaching Data)",
      '<div class="stack"><div class="card fitbox" data-start="24">'
      + ul(["`session_03_04_dataset.csv`: the **40 users with answers** from Session 3.4: train once",
            "`session_04_01_new_batch.csv`: **10 new users tonight**, during final exams: no answers",
            "`session_04_01_dataset.csv`: a **run log**, 5 nights x 4 stages, for Exercise 1"])
      + '</div><div class="check"><code>joblib</code> comes with Scikit-Learn: nothing new to install. Step 1 creates a <code>models/</code> folder.</div></div>')

code_slide("Step 1", "Step 1: Train Once and Save", "YourName_S41_step_1.py", codes[0],
           ["Same pipeline as 3.4, now trained on **all** 40 users",
            "`joblib.dump(model, path)` saves the scaler and the classifier together"],
           outs[0], "`os.path.exists(...)` prints `True`")

slide("Step 1", "Step 1: Why Train on All Users, and Save the Whole Pipeline?",
      '<div class="stack"><div class="card fitbox" data-start="24">'
      + ul(["Session 3.4 **tested** the model on half of the users; now it learns from every example",
            "Training accuracy `0.90` is optimistic: the honest test was in Session 3.4",
            "The saved file holds the **scaler and the classifier** together"])
      + '</div><div class="check"><b>Common mistake:</b> saving only the classifier. Tonight\'s minutes would go in unscaled, and every chance would be wrong.</div></div>')

code_slide("Step 2", "Step 2: The Nightly Job: Load, Score, Decide", "YourName_S41_step_2.py", codes[1],
           ["`joblib.load(path)`: the trained pipeline, no training data needed",
            "Coupon at a chance of `0.3` or more (Session 3.4); `.to_csv()` is the action"],
           "\n".join(outs[1].rstrip().split("\n")[:6] + ["... (6 more users)", outs[1].rstrip().split("\n")[-1]]),
           "`chance.sum()`: about `4.0` cancellations expected")

slide("Step 2", "Step 2: Tonight's Coupons",
      '<div class="figrow" style="grid-template-columns: 1.6fr 1fr;">' + fig("tonight", "Tonight's 10 users and the coupon threshold")
      + '<div class="card fitbox" data-start="22">'
      + ul(["5 coupons; `USR-407` is the clearest case (`0.94`)",
            "`USR-401`: only 2 weeks inactive, but just 250 minutes: coupon",
            "`USR-410`: 3 weeks inactive, but 1,650 minutes: no coupon"])
      + "</div></div>")

slide("Step 2", "Batch or Real-Time?",
      '<div class="stack"><div class="card fitbox" data-start="24">'
      + table([["", "Batch", "Real-time"],
               ["When", "on a schedule, e.g., every night", "on each request, in milliseconds"],
               ["Example", "tonight's coupons", "a song recommendation while the user waits"],
               ["Cost", "cheaper", "more expensive to build and run"]])
      + '</div><div class="check">The coupon can wait until morning, so a nightly batch is enough. <b>Common mistake:</b> retraining inside the nightly job: tonight\'s users have no answers yet.</div></div>')

code_slide("Step 3", "Step 3: Is Tonight Like the Training Data?", "YourName_S41_step_3.py", codes[2],
           ["Average per feature: training vs tonight",
            "Change in percent; `.abs() > 20` flags a large drop or rise"],
           outs[2], "`> 5` flags both features", width="w46")

slide("Step 3", "Step 3: Exam Season Shows Up as Drift",
      '<div class="stack">' + fig("drift", "Minutes of training users and tonight's users")
      + '<div class="check">Weeks inactive barely moved (<code>-5.7</code>%), minutes fell <code>42.7</code>%. The model learned that low minutes mean "about to leave": this week, that may not be true. Flag the night for review.</div></div>')

slide("Monitoring", "What a Run Log Records",
      '<div class="stack"><div class="card fitbox" data-start="24">'
      + table([["Run_Date", "Pipeline_Stage", "Records_Count", "Latency_Ms", "Model_Accuracy"],
               ["2026-12-07", "Ingestion", "52000", "350", ""], ["2026-12-07", "Validation", "51880", "180", ""],
               ["2026-12-07", "Scoring", "51880", "820", "0.912"], ["2026-12-07", "Action", "2100", "120", ""]])
      + '</div><div class="check">One row per stage per night. Rising latency or falling accuracy is an early warning: Exercise 1 reads 5 nights.</div></div>')

slide("Summary", "The Nightly Decision System",
      '<div class="stack">' + fig("nightly_job", "The nightly job with its fallback and review flag")
      + '<div class="check"><b>Remember:</b> train once, save, load every night; check that tonight looks like training; keep a fallback; log every run.</div></div>')

def ex_slide(n, level, title, goal, file, steps, check):
    slide(f"Exercise {n}: {level}", f"Exercise {n}: {title}",
          '<div class="stack"><div class="card fitbox" data-start="24">'
          f'<p><b>Goal:</b> {inline(goal)}</p><p><b>Script:</b> <code>{file}</code></p>' + ul(steps)
          + f'</div><div class="check"><b>Check:</b> {inline(check)}</div></div>')





ex_slide(1, "Guided", "Read the Run Log",
         "find the nights that need attention",
         "YourName_S41_monitoring.py",
         ["Type the code in section 11 of the reading",
          "Alert: latency above `900` ms **or** accuracy below `0.88`",
          "In two comments: the trend over 5 nights, and what the team should do"],
         "alerts on `2026-12-10` and `2026-12-11`; latency `1470` to `1730` ms")
ex_slide(2, "Applied", "Survive a Missing Model File",
         "keep the nightly job running when the model file is missing",
         "YourName_S41_fallback.py",
         ["A typo in the path stops the job with `FileNotFoundError`: ask the AI Chat how to check first",
          "`if os.path.exists(model_path):` model; otherwise the 3-weeks rule of Session 3.1",
          "Run both ways and print who gets a coupon"],
         "5 coupons both ways, but different users: the rule misses `USR-401` and wastes one on `USR-410`")
ex_slide(3, "Advanced", "One Function for the Whole Night",
         "validate, check drift, score or fall back, save, and report in one function",
         "YourName_S41_nightly.py",
         ["`run_nightly(batch_path, model_path, train_path)` returns a summary dictionary",
          "`needs_review` is `True` if anything drifted or the fallback was used",
          "Requirements and hints: section 13 of the reading"],
         "both runs: 10 records, 5 coupons, drift in `Monthly_Minutes_Count`, `needs_review: True`")

N = len(slides)
parts = []
for i, (kicker, title, body, cls) in enumerate(slides, 1):
    parts.append(f'<section class="slide">\n  <div><span class="eyebrow">MODULE 4</span><span class="kicker">{e(kicker)}</span></div>\n'
                 f'  <div class="title">{e(title)}</div><div class="rule"></div>\n  <div class="{cls}">{body}</div>\n'
                 f'  <div class="footer"><span>Business Analytics &amp; AI Application | Course 6141</span><span>Slide {i} / {N}</span></div>\n</section>\n')
out = head + EXTRA + "</style>\n</head>\n<body>\n" + "\n".join(parts) + "\n" + script
(ROOT / "slides_src" / "session_04_01.html").write_text(out)
print("slides:", N)
