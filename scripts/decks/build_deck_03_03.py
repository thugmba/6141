"""Hand-built story-order deck for Session 3.3: problem and result first, then how each preparation step got there."""
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
head = head.replace("<title>Session 3.1 Lecture</title>", "<title>Session 3.3 Lecture</title>")
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
sec = md[md.index('<a id="session-03-03"></a>'): md.index('<a id="session-03-04"></a>')]
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
    return f'<div class="figbox"><img src="../assets/session_03_03_fig_{name}.png" alt="{e(alt)}"></div>'


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



# 1. Problem and result
slide("The Problem and the Result", "Session 3.3: What Price Should I Ask for My Used Phone?",
      '<div class="card fitbox" data-start="22"><div class="tag">THE PROBLEM</div>'
      + ul(["Selling a used phone: too high, nobody buys; too low, you lose money",
            "A marketplace app wants to **suggest a fair price** from the phone's details",
            "Data: **20 used iPhone 13 sales**: age, storage, battery health, sold price",
            "The product manager asks: can a model learned from past sales suggest a price, and how far off will it be?"])
      + '<p class="flow">Today: the result first, then how Scikit-Learn got it</p></div>'
      '<div class="card fitbox" data-start="22"><div class="tag">THE RESULT</div>'
      + table([["How to price a phone", "Typical error on unseen phones"],
               ["Guess the average price", "NT$`2,448`"],
               ["Learned formula, 5 test phones", "NT$`555` (about 3%)"],
               ["Learned formula, 5 rounds of testing", "NT$`475` on average"]], rowcls=["old", "best", "best"])
      + '<p class="answer"><b>1.</b> Yes: about 4 to 5 times closer than guessing the average.</p>'
        '<p class="answer"><b>2.</b> Typically off by about NT$500, so the app can show a range.</p></div>',
      "body grid2 overview")

slide("Key Ideas", "Regression: Learning a Formula for a Number",
      '<div class="figrow" style="grid-template-columns: 1.7fr 1fr;">' + fig("price_vs_age", "Sold price against age with the best straight line")
      + '<div class="card fitbox" data-start="22">'
      + ul(["**Regression** predicts a number (a price); **classification** predicts a category (spam, cancel)",
            "**Linear regression**: price = start value + effect x feature + ...",
            "It picks the effects that make the training errors smallest",
            "**Coefficient** = change in price for one more unit, the other features held fixed"])
      + "</div></div>")

slide("Key Ideas", "Every Scikit-Learn Model: Create, Fit, Predict",
      '<div class="stack">' + fig("fit_predict", "Create an empty model, fit it to past sales, predict a new phone")
      + '<div class="card fitbox" data-start="22">'
      + table([["Idea", "Meaning"],
               ["MAE (Mean Absolute Error)", "the typical error, in NT$: lower is better"],
               ["Benchmark", "the simplest guess: the average past price for every phone"],
               ["Cross-validation", "test several times, each time on different phones"]])
      + "</div></div>")

slide("The Data", "One Small File (Fictional Teaching Data)",
      '<div class="stack"><div class="card fitbox" data-start="24">'
      + ul(["`session_03_03_dataset.csv`: **20 used iPhone 13 sales**, one row per sale",
            "`Listing_ID` (label), `Age_Months` (6-42), `Storage_GB` (128/256/512), `Battery_Health_Pct` (76-98)",
            "`Photos_Count`: photos in the listing, only for Exercise 3",
            "`Sold_Price_TWD`: the sold price in New Taiwan dollars: the target"])
      + '</div><div class="check">Activate your <code>.venv</code> first (Python Setup Clinic).</div></div>')

code_slide("Step 1", "Step 1: Learn a Price Formula", "YourName_S33_step_1.py", codes[0],
           ["`LinearRegression()` creates; `.fit()` learns from 15 sales",
            "`intercept_` = start value; `coef_` = one effect per feature"],
           outs[0], "`model.score(X_test, y_test)` is `0.841`")

slide("Step 1", "Step 1: Reading the Formula",
      '<div class="figrow" style="grid-template-columns: 1fr 1.1fr;"><div class="card fitbox" data-start="22">'
      + ul(["Each month older: about **NT$159 less**",
            "Each extra GB: about **NT$12 more** (128 to 256 GB: about NT$1,560)",
            "Each point of battery health: about **NT$129 more**",
            "Always \"with the other features held fixed\""])
      + '</div><div class="card fitbox" data-start="22"><div class="tag">24 MONTHS, 256 GB, 88% BATTERY</div>'
      + table([["Part", "Amount"], ["start value", "`8,776.8`"], ["age: `-159.4 x 24`", "`-3,825.6`"],
               ["storage: `12.2 x 256`", "`3,123.2`"], ["battery: `129.1 x 88`", "`11,360.8`"], ["**price**", "about NT$`19,435`"]], rowcls=[None, None, None, None, "best"])
      + "</div></div>")

slide("Step 1", "Step 1: Do Not Trust It Far Outside the Data",
      '<div class="stack"><div class="card fitbox" data-start="24">'
      + table([["Phone", "Inside the past sales?", "Model's price"],
               ["24 months, 256 GB, 88%", "yes (6-42 months)", "NT$`19,427`"],
               ["120 months, 128 GB, 60%", "no: 10 years old", "NT$`-1,042`"]], rowcls=["best", "old"])
      + '</div><div class="check"><b>Common mistake:</b> a formula knows only the range it learned from. A negative price is a warning, not an answer.</div></div>')

code_slide("Step 2", "Step 2: Test on Phones the Model Has Not Seen", "YourName_S33_step_2.py", codes[1],
           ["`.predict(X_test)`: 5 predicted prices",
            "`mean_absolute_error()`: the typical error (MAE)",
            "Benchmark: the average training price for every phone"],
           outs[1], "RMSE (large errors count extra) is NT$`692`")

slide("Step 2", "Step 2: How Close Is Each Prediction?",
      '<div class="figrow" style="grid-template-columns: 1.9fr 1fr;">' + fig("test_predictions", "Actual and predicted prices of the 5 test phones")
      + '<div class="card fitbox" data-start="22">'
      + ul(["Very close on `PH-118` (NT$77)",
            "About NT$1,000 high on two young phones with very good batteries",
            "All 5 errors are positive: on these phones the model suggests a little too much"])
      + "</div></div>")

slide("Step 2", "Step 2: Beat the Simple Guess",
      '<div class="stack">' + fig("model_vs_guess", "Typical error: guessing the average vs the learned formula")
      + '<div class="check">The formula is about <b>4 times closer</b> than guessing the average. <b>Common mistake:</b> measuring the error on the training sales: they always look easier.</div></div>')

code_slide("Step 3", "Step 3: Test Five Times (Cross-Validation)", "YourName_S33_step_3.py", codes[2],
           ["`cv=5`: 5 rounds; each tests a different 4 phones",
            "Scores come back negative; `-scores` gives the MAE"],
           outs[2].replace("round: [", "round:\n["), "`cv=4`: average NT$`511`, worst NT$`611`")

slide("Step 3", "Step 3: Every Phone Is Tested Once",
      '<div class="stack">' + fig("cv_folds", "Five rounds of cross-validation with the typical error of each")
      + '<div class="check">Average NT$475, close to the single test (NT$555): that result was not luck. Report the average <b>and</b> the worst round.</div></div>')

slide("Summary", "What the Model Did",
      '<div class="stack">' + fig("model_steps", "The steps of a prediction model")
      + '<div class="card fitbox" data-start="22">'
      + ul(["Session 3.4: the same create-fit-predict pattern with a classifier",
            "Session 4.1: a saved model predicts new rows every night"])
      + '</div><div class="check"><b>Remember:</b> create, fit, predict; measure the error on unseen rows; beat the simple guess; cross-validate.</div></div>')


def ex_slide(n, level, title, goal, file, steps, check):
    slide(f"Exercise {n}: {level}", f"Exercise {n}: {title}",
          '<div class="stack"><div class="card fitbox" data-start="24">'
          f'<p><b>Goal:</b> {inline(goal)}</p><p><b>Script:</b> <code>{file}</code></p>' + ul(steps)
          + f'</div><div class="check"><b>Check:</b> {inline(check)}</div></div>')



ex_slide(1, "Guided", "Suggest Prices for New Listings",
         "predict three new phones and show each price with a range of NT$500 on each side",
         "YourName_S33_suggest.py",
         ["Type the code in section 11 of the reading",
          "New rows need the **same column names** as the training data",
          "In two comments: why is the oldest phone, `NEW-3`, priced above `NEW-2`?"],
         "NT$`22,600`, NT$`17,600`, NT$`19,500`")
ex_slide(2, "Applied", "Error per Phone and a One-Row Prediction",
         "show each test phone's error in percent, then price one phone",
         "YourName_S33_practice.py",
         ["Add `Error_Pct` and print MAPE (the average percentage error)",
          "`model.predict([24, 256, 88])` stops with a `ValueError`: ask the AI Chat what \"2D\" means",
          "Fix it with a one-row DataFrame: `pd.DataFrame([[24, 256, 88]], columns=features)`"],
         "MAPE `2.7`%; your phone NT$`19,427`")
ex_slide(3, "Advanced", "Which Details Should the App Ask For?",
         "compare four feature lists with 5-fold cross-validation and pick the simplest good one",
         "YourName_S33_details.py",
         ["A: age; B: + storage; C: + battery; D: + photos",
          "Rule: among models within NT$50 of the best, choose the fewest features",
          "Requirements and hints: section 13 of the reading"],
         "B: age + storage (MAE NT$`470`): battery health adds almost nothing")


N = len(slides)
parts = []
for i, (kicker, title, body, cls) in enumerate(slides, 1):
    parts.append(f'<section class="slide">\n  <div><span class="eyebrow">MODULE 3</span><span class="kicker">{e(kicker)}</span></div>\n'
                 f'  <div class="title">{e(title)}</div><div class="rule"></div>\n  <div class="{cls}">{body}</div>\n'
                 f'  <div class="footer"><span>Business Analytics &amp; AI Application | Course 6141</span><span>Slide {i} / {N}</span></div>\n</section>\n')
out = head + EXTRA + "</style>\n</head>\n<body>\n" + "\n".join(parts) + "\n" + script
(ROOT / "slides_src" / "session_03_03.html").write_text(out)
print("slides:", N)
