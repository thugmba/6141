"""Hand-built story-order deck for Session 3.1: problem and result first, then how ML got there."""
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
head = head.replace("<title>Session 3.1 Lecture</title>", "<title>Session 3.1 Lecture</title>")
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
.stack { height: 100%; }
.figbox { flex: 1 1 0; min-height: 0; display: flex; align-items: center; justify-content: center; }
.figbox img { max-width: 100%; max-height: 100%; object-fit: contain; display: block; }
.figrow { display: grid; gap: .22in; width: 100%; min-height: 0; }
.figrow > .figbox { height: 100%; }
.figrow > .card { align-self: center; }
"""
md = (ROOT / "6141.md").read_text()
sec = md[md.index('<a id="session-03-01"></a>'): md.index('<a id="session-03-02"></a>')]
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
    return f'<div class="figbox"><img src="../assets/session_03_01_fig_{name}.png" alt="{e(alt)}"></div>'


def slide(kicker, title, body, cls="body"):
    slides.append((kicker, title, body, cls))


# 1. Problem and result
slide("The Problem and the Result", "Session 3.1: Can a Spam Filter Learn a Better Rule?",
      '<div class="card fitbox" data-start="23"><div class="tag">THE PROBLEM</div>'
      + ul(["Every email service decides: inbox or spam folder?",
            "Two ways to be wrong: **missed spam** (a scam in your inbox) and **false alarm** (a real email hidden in spam)",
            "The team's old rule: **3 or more links = spam**. The number 3 was a guess",
            "The manager asks: can a rule learned from our past emails do better, and can we trust its score?"])
      + '<p class="flow">Today: the result first, then how machine learning got it</p></div>'
      '<div class="card fitbox" data-start="23"><div class="tag">THE RESULT</div>'
      + table([["Rule", "Mistakes (20 past emails)", "Accuracy, past", "Accuracy, 10 new"],
               ["Old rule: `3` or more links → spam", "`4`", "`80%`", "`60%`"],
               ["Learned rule: `4` or more links → spam", "`1`", "`95%`", "`80%`"]], rowcls=["old", "best"])
      + '<p class="answer"><b>1.</b> The learned rule is better: it removes all 3 false alarms.</p>'
        '<p class="answer"><b>2.</b> Report <b>80%</b>, not 95%: only new emails give an honest score.</p>'
        '<p class="answer"><b>3.</b> Nobody guessed <code>4</code>: Python tried many thresholds and kept the one with the fewest mistakes.</p></div>',
      "body grid2 overview")

# 2. AI ML DL
slide("Key Ideas", "AI, ML, and DL: Three Nested Ideas",
      '<div class="stack">' + fig("ai_ml_dl", "AI, ML, and DL nested; rule-based system compared with machine learning")
      + '<div class="check"><b>The one difference today:</b> in a rule-based system a person writes the rule; in machine learning the computer finds it from past examples. An app sold as "AI" can still be rule-based: ask which examples it learned from.</div></div>')

# 3. Four cases and accuracy
slide("Key Ideas", "How to Judge a Rule: Four Cases and Accuracy",
      '<div class="figrow" style="grid-template-columns: 1.55fr 1fr;">' + fig("four_cases", "The four cases of the old rule on 20 past emails")
      + '<div class="card fitbox" data-start="22"><div class="tag">ONE EMAIL IN EACH BOX</div>'
      + ul(["**Threshold** = the cut-off value: 3 or more links → spam folder",
            "\"You won a free iPhone!\" (`5` links): spam caught",
            "\"Lunch on Friday?\" (`0`): real email delivered",
            "\"Weekly news from the campus\" (`3`): **false alarm**",
            "\"Verify your bank account now\" (`2`): **missed spam**",
            "**Accuracy** = correct / all = `16 / 20` = 80%"])
      + "</div></div>")

# 4. Data
slide("The Data", "Three Small Files (Fictional Teaching Data)",
      '<div class="stack"><div class="card fitbox" data-start="24">'
      + ul(["`session_03_01_dataset.csv`: **20 past emails** (9 spam), for Steps 1-3. Columns: `Message_ID`, `Subject`, `Link_Count`, `Is_Spam_Binary`",
            "`session_03_01_new_messages.csv`: **10 emails from next month**, the same 4 columns. Step 3 uses them as \"the future\"",
            "`session_03_01_churn.csv`: **16 music app users** (7 cancelled), for Exercises 2-3. Columns: `User_ID`, `Weeks_Inactive_Count`, `Cancelled_Binary`"])
      + '</div><div class="check"><code>Is_Spam_Binary</code>: <code>1</code> = spam, <code>0</code> = real email. These known answers are what the computer learns from.</div></div>')


def code_slide(kicker, title, fname, code, how, out, check, start="21", width="w55"):
    slide(kicker, title,
          f'<div class="code-panel {width} fitbox" data-start="{start}" data-floor="13"><div class="code-header">'
          '<span class="dot" style="background:#EF4444"></span><span class="dot" style="background:#F59E0B"></span>'
          f'<span class="dot" style="background:#22C55E"></span>&nbsp;{fname}<span class="ipo">Input &#8594; Process &#8594; Output</span></div>'
          f"<pre>{code_html(code)}</pre></div>"
          '<div class="notes"><div class="card fitbox how" data-start="21"><div class="tag">HOW IT WORKS</div>' + ul(how) + "</div>"
          f'<div class="card fitbox out" data-start="21"><div class="tag">OUTPUT</div><div class="outbox">{e(out.rstrip())}</div></div>'
          f'<div class="check fitbox" data-start="20"><p><b>Quick Check:</b> {inline(check)}</p></div></div>')


code_slide("Step 1", "Step 1: Count the Old Rule's Mistakes", "YourName_S31_step_1.py", codes[0],
           ["`>= 3` applies the rule to all 20 emails at once: `True` = spam folder",
            "`== 1` turns the answer `1` / `0` into `True` / `False`",
            "`!=` marks a mistake: the rule and the real answer disagree",
            "`.sum()` counts the `True` values"],
           outs[0], "add `df[\"Flagged\"].mean()`: the share sent to spam is `0.55`")

slide("Step 1", "Step 1: What the Mistakes Tell Us",
      '<div class="stack">' + fig("old_rule_line", "The 20 past emails by link count with the old rule's threshold and its 4 mistakes ringed")
      + '<div class="check"><b>False alarms:</b> 3 real emails with exactly 3 links (newsletter, photos, booking). <b>Missed spam:</b> "Verify your bank account now" (2 links). 4 of 20 wrong = <b>80%</b>.</div></div>')

code_slide("Step 2", "Step 2: Let the Data Choose the Threshold", "YourName_S31_step_2.py", codes[1],
           ["`count_mistakes()` packs Step 1 into a function (Session 2.4)",
            "The `for` loop tries each threshold and prints its mistakes",
            "Trying rules and keeping the best is the \"learning\" in machine learning"],
           outs[1], "use `range(1, 10, 2)`: the best of `1, 3, 5, 7, 9` is `5`; the step skipped `4`")

slide("Step 2", "Step 2: Why 4 Links Is the Best Balance",
      '<div class="figrow" style="grid-template-columns: 1.6fr 1fr;">' + fig("mistakes_by_threshold", "False alarms and missed spam for thresholds 1 to 6")
      + '<div class="card fitbox" data-start="22">'
      + ul(["**Too low** (1 or 2 links): many real emails go to spam (blue)",
            "**Too high** (5 or 6 links): spam gets through (red)",
            "**4 links** has the fewest mistakes: `1`",
            "The computer does not \"understand\" spam; it finds the rule that best matches the known answers"])
      + "</div></div>")

slide("Step 2", "Step 2: Move the Line from 3 to 4 Links",
      '<div class="stack">' + fig("learned_rule_line", "The learned rule at 4 links on the 20 past emails, with its 1 mistake ringed")
      + '<div class="check">Compare with Step 1: one step to the right, the three real emails with 3 links return to the inbox, and the same spam is still caught. Only the 2-link scam is left.</div></div>')

code_slide("Step 3", "Step 3: Test Both Rules on New Emails", "YourName_S31_step_3.py", codes[2],
           ["The function takes the table too, so one function scores past and new emails",
            "`==` marks correct decisions; `.mean()` turns them into accuracy",
            "`:.0%` prints `0.95` as `95%`"],
           outs[2], "add `(\"Strict rule\", 6)`: past `80%`, new `80%`")

slide("Step 3", "Step 3: Why the Score Drops on New Emails",
      '<div class="figrow" style="grid-template-columns: 1.75fr 1fr;">' + fig("past_vs_new", "Accuracy on past and new emails for both rules")
      + '<div class="card fitbox" data-start="22"><div class="tag">NEW CASES THE PAST DID NOT SHOW</div>'
      + ul(["\"Online course newsletter\" (`4` links, real): false alarm",
            "\"Reset your password here\" (`2` links, spam): missed spam",
            "Links alone cannot catch every scam; real filters use many clues"])
      + '<p><b>Common mistake:</b> reporting the past score ("95%"). Compare rules by the red bars.</p></div></div>')

slide("Summary", "What Machine Learning Did",
      '<div class="stack">' + fig("ml_steps", "Collect examples, search for the best rule, test on new data")
      + '<div class="card fitbox" data-start="22">'
      + ul(["Later in Module 3: music app users (3.2) and used phone sales (3.3) as examples",
            "Scikit-Learn's `.fit()` does the search for you (3.3); the train/test split keeps new data aside (3.2)"])
      + '</div><div class="check"><b>Remember:</b> try many rules on past examples, keep the one with the fewest mistakes, then judge it only on new examples.</div></div>')

slide("Summary", "When Is a Written Rule Enough?",
      '<div class="stack"><div class="card fitbox" data-start="24">'
      + table([["Decision", "Rule or ML?", "Why"],
               ["Student discount with a valid student ID", "rule", "the policy is clear and never guesses"],
               ["Free delivery for orders over $30", "rule", "a fixed, written shop policy"],
               ["Which emails are spam?", "ML", "spammers keep changing their tricks"],
               ["Which songs will you like next?", "ML", "many signals combine in ways no one can write down"],
               ["Unlocking a phone with your face", "ML (deep learning)", "images need many-layered models"]])
      + "</div></div>")


def ex_slide(n, level, title, goal, file, steps, check):
    slide(f"Exercise {n}: {level}", f"Exercise {n}: {title}",
          '<div class="stack"><div class="card fitbox" data-start="24">'
          f'<p><b>Goal:</b> {inline(goal)}</p><p><b>Script:</b> <code>{file}</code></p>' + ul(steps)
          + f'</div><div class="check"><b>Check:</b> {inline(check)}</div></div>')


slide("Exercise 1: Guided", "Exercise 1: Missed Spam or False Alarm?",
      '<div class="code-panel w55 fitbox" data-start="21" data-floor="13"><div class="code-header">'
      '<span class="dot" style="background:#EF4444"></span><span class="dot" style="background:#F59E0B"></span>'
      '<span class="dot" style="background:#22C55E"></span>&nbsp;YourName_S31_mistakes.py<span class="ipo">Input &#8594; Process &#8594; Output</span></div>'
      f"<pre>{code_html(codes[3])}</pre></div>"
      '<div class="notes"><div class="card fitbox how" data-start="21"><div class="tag">TYPE, RUN, INTERPRET</div>'
      + ul(["`(flagged == False) & is_spam` = spam that reached the inbox",
            "`df.loc[missed, \"Subject\"]` lists those emails",
            "In two comment lines: which mistake did the learned rule remove? Why can no link threshold catch \"Verify your bank account now\"?"])
      + '</div><div class="check fitbox" data-start="20"><p><b>Check:</b> old rule: missed spam <code>1</code>, false alarms <code>3</code>; learned rule: missed spam <code>1</code>, false alarms <code>0</code></p></div></div>')
ex_slide(2, "Applied", "Who Will Cancel the Music App?",
         "the app sends a \"come back\" discount to users inactive for `2`+ weeks. Is there a better threshold?",
         "YourName_S31_cancel.py",
         ["Load `data/session_03_01_churn.csv`; print the cancel share with `.mean()`",
          "Write `count_mistakes(threshold)` on `Weeks_Inactive_Count`, as in Step 2",
          "Try `range(1, 7)` and print the accuracy of the best threshold and of `2` weeks"],
         "best `3` weeks: accuracy `0.875` vs `0.8125`")
ex_slide(3, "Advanced", "Let the Computer Search",
         "write `find_best_threshold(data, feature, target)` that tries every value in a column and keeps the best",
         "YourName_S31_search.py",
         ["Run it on the emails and on the music app users",
          "Apply the best email threshold to the 10 new emails",
          "Requirements and hints: section 13 of the reading"],
         "emails: best `4` links, `1` mistake (`20` tried); users: best `3` weeks (`16` tried); new emails: `8` of `10` correct")

N = len(slides)
parts = []
for i, (kicker, title, body, cls) in enumerate(slides, 1):
    parts.append(f'<section class="slide">\n  <div><span class="eyebrow">MODULE 3</span><span class="kicker">{e(kicker)}</span></div>\n'
                 f'  <div class="title">{e(title)}</div><div class="rule"></div>\n  <div class="{cls}">{body}</div>\n'
                 f'  <div class="footer"><span>Business Analytics &amp; AI Application | Course 6141</span><span>Slide {i} / {N}</span></div>\n</section>\n')
out = head + EXTRA + "</style>\n</head>\n<body>\n" + "\n".join(parts) + "\n" + script
(ROOT / "slides_src" / "session_03_01.html").write_text(out)
print("slides:", N)
