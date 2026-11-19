"""Hand-built story-order deck for Session 3.2: problem and result first, then how each preparation step got there."""
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
head = head.replace("<title>Session 3.1 Lecture</title>", "<title>Session 3.2 Lecture</title>")
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
sec = md[md.index('<a id="session-03-02"></a>'): md.index('<a id="session-03-03"></a>')]
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
    return f'<div class="figbox"><img src="../assets/session_03_02_fig_{name}.png" alt="{e(alt)}"></div>'


def slide(kicker, title, body, cls="body"):
    slides.append((kicker, title, body, cls))



# 1. Problem and result
slide("The Problem and the Result", "Session 3.2: Can Our User Table Feed a Model?",
      '<div class="card fitbox" data-start="22"><div class="tag">THE PROBLEM</div>'
      + ul(["A music app wants to predict who cancels, from 4 clues: age, monthly minutes, weeks inactive, plan",
            "A model stops twice: `could not convert string to float: 'Student'` and `Input X contains NaN`",
            "Silent problem: minutes go up to `2,400`, weeks only to `6`",
            "The team lead asks: can we make this table model-ready, and keep a fair test?"])
      + '<p class="flow">Today: the result first, then the three steps that got it</p></div>'
      '<div class="card fitbox" data-start="22"><div class="tag">THE RESULT</div>'
      + table([["Problem", "Raw table", "Prepared table"],
               ["Text columns", "`1` (`Plan_Type`)", "`0`: two 0/1 columns"],
               ["Empty cells", "`2`", "`0`"],
               ["Units", "minutes `90`-`2,400`; weeks `0`-`6`", "average `0`, spread `1` (training users)"],
               ["Fair test", "none", "`4` users set aside first"]], rowcls=[None, None, None, "best"])
      + '<p class="answer"><b>1.</b> Only numbers, no gaps, one common scale.</p>'
        '<p class="answer"><b>2.</b> All rules come from the 12 training users, so the test shows a real difference: test users are older (<code>+1.24</code>) and listen less (<code>-0.78</code>).</p></div>',
      "body grid2 overview")

# 2. Features and target
slide("Key Ideas", "Features (X) and Target (y)",
      '<div class="stack"><div class="card fitbox" data-start="24">'
      + table([["Column", "Role", "Why"],
               ["`Age_Years_Count`, `Monthly_Minutes_Count`, `Weeks_Inactive_Count`, `Plan_Type`", "features `X`: the clues", "known about the user today"],
               ["`Cancelled_Binary`", "target `y`: the answer", "`1` = cancelled next month, `0` = stayed"],
               ["`User_ID`", "neither", "a label; it says nothing about the user"]])
      + '</div><div class="check"><b>Common mistake:</b> leaving the target inside <code>X</code>. The model reads the answer, scores perfectly in testing, and is useless next month.</div></div>')

# 3. Four tools
slide("Key Ideas", "Four Preparation Tools and Two Verbs",
      '<div class="stack"><div class="card fitbox" data-start="23">'
      + table([["Tool", "What it does", "An everyday version"],
               ["Imputation", "fills an empty cell with the column's **median** (middle value)", "a blank age on a form: assume a typical age"],
               ["One-hot encoding", "one text column → one 0/1 column per category", "a checkbox: \"Student plan? yes = 1\""],
               ["Standardization", "value → distance from the average, in standard deviations", "\"2 points above the class average\""],
               ["Train/test split", "keeps some rows aside for the final test", "an exam with questions you have not practiced"]])
      + '</div><div class="check"><code>.fit()</code> learns (a median, an average); <code>.transform()</code> applies it. Fit on training rows only; transform both. Breaking this rule is <b>data leakage</b>.</div></div>')

# 4. Data
slide("The Data", "One Small File (Fictional Teaching Data)",
      '<div class="stack"><div class="card fitbox" data-start="24">'
      + ul(["`session_03_02_dataset.csv`: **16 music app users**, one row per user; 4 cancelled",
            "`User_ID` (label), `Age_Years_Count`, `Monthly_Minutes_Count`, `Weeks_Inactive_Count` (as in Session 3.1), `Plan_Type`",
            "`Cancelled_Binary`: `1` = cancelled next month, `0` = stayed",
            "2 empty cells on purpose: `USR-207` skipped the age question; `USR-209`'s listening log was lost"])
      + '</div><div class="check">First time only: <code>pip install scikit-learn</code> in the Terminal.</div></div>')


def code_slide(kicker, title, fname, code, how, out, check, start="21", width="w46", wrap=False):
    slide(kicker, title,
          f'<div class="code-panel {width} fitbox" data-start="{start}" data-floor="13"><div class="code-header">'
          '<span class="dot" style="background:#EF4444"></span><span class="dot" style="background:#F59E0B"></span>'
          f'<span class="dot" style="background:#22C55E"></span>&nbsp;{fname}<span class="ipo">Input &#8594; Process &#8594; Output</span></div>'
          f"<pre>{code_html(code)}</pre></div>"
          '<div class="notes"><div class="card fitbox how" data-start="21"><div class="tag">HOW IT WORKS</div>' + ul(how) + "</div>"
          f'<div class="card fitbox out" data-start="21"><div class="tag">OUTPUT</div><div class="outbox{' wrap' if wrap else ''}">{e(out.rstrip())}</div></div>'
          f'<div class="check fitbox" data-start="20"><p><b>Quick Check:</b> {inline(check)}</p></div></div>')


code_slide("Step 1", "Step 1: Find the Clues, the Answer, and the Problems", "YourName_S32_step_1.py", codes[0],
           ["`index_col=\"User_ID\"`: the ID is a row label, never a clue",
            "`isnull().sum()`: gaps per column; `describe()`: min and max"],
           outs[1], "`y.value_counts(normalize=True)`: `0.75` stayed, `0.25` cancelled")

slide("Step 1", "Step 1: Three Problems in the Raw Table",
      '<div class="figrow" style="grid-template-columns: 1.5fr 1fr;">' + fig("raw_table", "The raw table with column roles, gaps, and the text column")
      + '<div class="card fitbox" data-start="22">'
      + ul(["**Gaps** (orange): 1 age, 1 minutes value → fill (Step 3)",
            "**Text** (purple): `Plan_Type` → 0/1 columns (Step 2)",
            "**Units**: minutes up to `2400`, weeks up to `6` → one scale (Step 3)"])
      + "</div></div>")

code_slide("Step 2", "Step 2: Turn Text into 0/1 Columns", "YourName_S32_step_2.py", codes[1],
           ["`get_dummies()`: one 0/1 column per plan",
            "Plans sorted: `Family`, `Individual`, `Student`; `drop_first=True` leaves out `Family`"],
           outs[2].replace("', '", "',\n '", 4), "`drop_first=False` adds `Plan_Type_Family`")

slide("Step 2", "Step 2: One Text Column Becomes Two Yes/No Columns",
      '<div class="stack">' + fig("one_hot", "Plan_Type becomes two 0/1 columns")
      + '<div class="check"><b>Why not 1, 2, 3?</b> It would make a Student plan "three times" a Family plan. <b>Why drop one?</b> 0 in both columns already means Family.</div></div>')

code_slide("Step 3", "Step 3: Split First, Then Fill and Scale", "YourName_S32_step_3.py", codes[2],
           ["`stratify=y`: 25% cancelled in both sets",
            "`fit_transform` on training rows; `transform` on test rows"],
           outs[3], "`scaler.mean_` is `[30.08, 1083.33, 1.75]`")

slide("Step 3", "Step 3: Putting the Numbers on One Scale",
      '<div class="stack">' + fig("scales", "The three number columns before and after scaling")
      + '<div class="check"><b>By hand:</b> <code>USR-210</code> is 44; training average 30.08, standard deviation 8.20: <code>(44 - 30.08) / 8.20 = 1.70</code> standard deviations above average.</div></div>')

slide("Step 3", "Step 3: Split First, Fit on Training, Transform Both",
      '<div class="stack">' + fig("split_fit", "Split first, fit on the training users, transform both sets")
      + '<div class="check">The medians and averages come from the 12 training users only. The 4 test users play the role of next month\'s new users.</div></div>')

slide("Step 3", "Why Split First? What Leakage Hides",
      '<div class="figrow" style="grid-template-columns: 1.6fr 1fr;">' + fig("leakage", "Test averages with training rules vs scaled on their own")
      + '<div class="card fitbox" data-start="22"><div class="tag">COMMON MISTAKE</div>'
      + ul(["`scaler.fit_transform(X_test[numbers])` learns the test users' own average",
            "Every test average becomes `0`: they look \"average\"",
            "In fact they are older and listen less: a difference the model must face"])
      + "</div></div>")

slide("Summary", "What Data Preparation Did",
      '<div class="stack">' + fig("prep_steps", "The three preparation steps")
      + '<div class="card fitbox" data-start="22">'
      + ul(["Session 3.3 trains a model on `X_train` and scores it on `X_test`",
            "Session 4.1 saves the scaler together with the model, so new data gets the training rules"])
      + '</div><div class="check"><b>Remember:</b> split first, <code>fit</code> on the training rows, <code>transform</code> both sets.</div></div>')


def ex_slide(n, level, title, goal, file, steps, check):
    slide(f"Exercise {n}: {level}", f"Exercise {n}: {title}",
          '<div class="stack"><div class="card fitbox" data-start="24">'
          f'<p><b>Goal:</b> {inline(goal)}</p><p><b>Script:</b> <code>{file}</code></p>' + ul(steps)
          + f'</div><div class="check"><b>Check:</b> {inline(check)}</div></div>')


ex_slide(1, "Guided", "Check the Prepared Data",
         "run the preparation of Step 3, then check the result four ways",
         "YourName_S32_check.py",
         ["Type the code in section 11 of the reading (parts 1-2 are Step 3)",
          "Print the gaps left, the training averages and spreads, and the cancels in each set",
          "In two comments: why are the training averages exactly `0`? Why does the test set hold 1 cancel?"],
         "`Gaps left: 0`; averages `0.0`; spreads `1.0`; `Cancelled in train: 3 | in test: 1`")
ex_slide(2, "Applied", "A New Clue and a Leakage Check",
         "add one clue, read a common error, and see what leakage hides",
         "YourName_S32_practice.py",
         ["Add `Inactive_3_Plus_Flag` (3 or more weeks, from Session 3.1) and print `pd.crosstab()`",
          "Call `.transform()` on an unfitted `StandardScaler()`: read the `NotFittedError` with the AI Chat",
          "Print the test averages; then scale the test users on their own and print again"],
         "flag: all 4 flagged users cancelled; test averages `[1.24, -0.78, 0.13]` vs leaky `[0.0, 0.0, 0.0]`")
ex_slide(3, "Advanced", "A Reusable Preparation Pipeline",
         "one object that fills, scales, and encodes, fitted on the training users",
         "YourName_S32_pipeline.py",
         ["`Pipeline` (median, then scale) for numbers + `OneHotEncoder(handle_unknown=\"ignore\")` in a `ColumnTransformer`",
          "Transform the test users and one new user: no age, `300` minutes, `4` weeks, plan `\"Duo\"`",
          "Requirements and hints: section 13 of the reading"],
         "6 output columns; new user `0.11`, `-1.12`, `1.17`, `0.0`, `0.0`, `0.0`, with no crash")

N = len(slides)
parts = []
for i, (kicker, title, body, cls) in enumerate(slides, 1):
    parts.append(f'<section class="slide">\n  <div><span class="eyebrow">MODULE 3</span><span class="kicker">{e(kicker)}</span></div>\n'
                 f'  <div class="title">{e(title)}</div><div class="rule"></div>\n  <div class="{cls}">{body}</div>\n'
                 f'  <div class="footer"><span>Business Analytics &amp; AI Application | Course 6141</span><span>Slide {i} / {N}</span></div>\n</section>\n')
out = head + EXTRA + "</style>\n</head>\n<body>\n" + "\n".join(parts) + "\n" + script
(ROOT / "slides_src" / "session_03_02.html").write_text(out)
print("slides:", N)
