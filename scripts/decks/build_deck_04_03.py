"""Hand-built story-order deck for Session 4.3: problem and result first, then how each preparation step got there."""
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
head = head.replace("<title>Session 3.1 Lecture</title>", "<title>Session 4.3 Lecture</title>")
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
sec = md[md.index('<a id="session-04-03"></a>'): md.index('<a id="session-04-04"></a>')]
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
    return f'<div class="figbox"><img src="../assets/session_04_03_fig_{name}.png" alt="{e(alt)}"></div>'


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




slide("The Problem and the Result", "Session 4.3: What Should the Campus Store Charge?",
      '<div class="card fitbox" data-start="22"><div class="tag">THE PROBLEM</div>'
      + ul(["The campus store sells 10 university products; the semester ends in **14 days**",
            "Leftovers go to a wholesaler at 40% of cost: a loss of 60% of the cost per item",
            "Prices were set by gut feeling: some too low, some too high",
            "The manager asks: how strongly do students react to price, which prices go up or down, and how do we clear the stock?"])
      + '<p class="flow">Today: the result first, then the steps</p></div>'
      '<div class="card fitbox" data-start="22"><div class="tag">THE RESULT</div>'
      + table([["", "Result"], ["Price test (hoodie)", "elasticity -1.55"],
               ["Best store-wide change", "+5%: NT$18,646 a day"],
               ["Will not sell out in time", "5 of 10 products"],
               ["Best price per product, 14 days", "NT$253,557 (+NT$11,185)"]], rowcls=[None, None, "old", "best"])
      + '<p class="answer">Profit, not revenue, is the goal; count the cost of leftovers.</p></div>',
      "body grid2 overview\" style=\"grid-template-columns: 1fr 1.2fr;")

slide("Key Ideas", "Margin, Sales, and Profit",
      '<div class="stack">' + fig("price_tradeoff", "The hoodie at three prices")
      + '<div class="card fitbox" data-start="22">'
      + ul(["**Unit margin** = price - unit cost; **profit** = margin x sales",
            "**Elasticity** `-1.55`: a 1% price rise loses about 1.55% of sales",
            "New daily sales = old sales x (1 + elasticity x price change), for changes up to about 20%"])
      + "</div></div>")

slide("Key Ideas", "Stock and Time",
      '<div class="stack"><div class="card fitbox" data-start="24">'
      + table([["Term", "Meaning", "Hoodie"],
               ["Days of stock", "stock / daily sales", "`120 / 8 = 15.0` days"],
               ["Days left", "until the semester ends", "`14`"],
               ["Leftover loss", "0.6 x unit cost per unsold item", "`0.6 x 420 = NT$252` each"]])
      + '</div><div class="check">If the days of stock are more than the days left, a cut that sells the leftovers can earn more than keeping the price.</div></div>')

slide("The Data", "Two Small Files (Fictional Teaching Data)",
      '<div class="stack"><div class="card fitbox" data-start="24">'
      + ul(["`session_04_03_dataset.csv`: **10 campus store products**: price, unit cost, stock, daily sales (NT$)",
            "Hoodie, T-shirt, Cap, Tote bag, Mug, Water bottle, Notebook, Umbrella, Lanyard, Keychain",
            "`session_04_03_price_test.csv`: **5 weeks** of tested hoodie prices (NT$790 to NT$990)"])
      + "</div></div>")

code_slide("Step 1", "Step 1: How Strongly Do Students React to Price?", "YourName_S43_step_1.py", codes[0],
           ["`np.log()` turns % changes into differences",
            "`np.polyfit(x, y, 1)`: the best straight line; its slope is the elasticity"],
           outs[0], "`.pct_change()` shows week-to-week reactions")

slide("Step 1", "Step 1: The Price Test",
      '<div class="figrow" style="grid-template-columns: 1.6fr 1fr;">' + fig("price_test", "Hoodie price test with the fitted line")
      + '<div class="card fitbox" data-start="22">'
      + ul(["5 weeks, 5 prices: higher price, fewer hoodies",
            "`-1.55` is below `-1`: students react strongly",
            "A line through several weeks is more reliable than one change"])
      + "</div></div>")

slide("Step 1", "Step 1: Using the Elasticity",
      '<div class="stack"><div class="card fitbox" data-start="24"><div class="tag">THE HOODIE: 8 A DAY AT NT$890, MARGIN NT$470</div>'
      + table([["Change", "Price", "Daily sales", "Daily profit"],
               ["-10%", "NT$801", "8 x (1 + 0.155) = 9.2", "NT$3,520"],
               ["none", "NT$890", "8.0", "NT$3,760"],
               ["+10%", "NT$979", "8 x (1 - 0.155) = 6.8", "NT$3,779"]], rowcls=[None, None, "best"])
      + '</div><div class="check">For the hoodie, a 10% rise keeps profit about the same: the higher margin makes up for the lost sales.</div></div>')

code_slide("Step 2", "Step 2: Simulate Profit Before Changing a Price", "YourName_S43_step_2.py", codes[1],
           ["`daily_profit(change)`: new prices, new sales, total profit",
            "The hoodie's elasticity is used for every product"],
           outs[1], "`max(curve, key=curve.get)` gives `+5%`")

slide("Step 2", "Step 2: The Most Money Is Not the Most Profit",
      '<div class="stack">' + fig("profit_curve", "Revenue and profit for store-wide price changes")
      + '<div class="check">A 15% cut brings in the most revenue (NT$33,356) but the least profit (NT$17,063). Profit peaks at +5%.</div></div>')

code_slide("Step 3", "Step 3: Which Products Will Not Sell Out in Time?", "YourName_S43_step_3.py", codes[2],
           ["Days of stock = stock / daily sales",
            "Keep the products with more than 14 days of stock"],
           outs[2], "`np.where()`: `Markdown` 5, `Keep` 5", width="w46")

slide("Step 3", "Step 3: Five Products Need a Cut",
      '<div class="stack">' + fig("days_of_stock", "Days of stock against 14 days left")
      + '<div class="check">The mug is the slowest: 20 would be left over. The other 5 products sell out in time: their prices could go up. <b>Common mistake:</b> cutting every price before a deadline.</div></div>')

slide("Plans", "One Price Rule for All, or the Best Price per Product?",
      '<div class="stack"><div class="card fitbox" data-start="24">'
      + table([["Plan", "Profit over 14 days"],
               ["Today's prices", "NT$242,372"],
               ["Best change per product (5 cuts, 5 rises)", "NT$253,557"]], rowcls=["old", "best"])
      + '</div><div class="check">The cuts go exactly to the 5 slow products; products that sell out anyway carry a higher price (Exercise 3).</div></div>')

slide("Summary", "Pricing with Data",
      '<div class="stack">' + fig("pricing_steps", "The pricing steps")
      + '<div class="check"><b>Remember:</b> measure how customers react before changing a price; simulate profit, not revenue; count the cost of what will be left over.</div></div>')

def ex_slide(n, level, title, goal, file, steps, check):
    slide(f"Exercise {n}: {level}", f"Exercise {n}: {title}",
          '<div class="stack"><div class="card fitbox" data-start="24">'
          f'<p><b>Goal:</b> {inline(goal)}</p><p><b>Script:</b> <code>{file}</code></p>' + ul(steps)
          + f'</div><div class="check"><b>Check:</b> {inline(check)}</div></div>')







ex_slide(1, "Guided", "Revenue or Profit?",
         "simulate units, revenue, and profit for store-wide changes from -15% to +15%",
         "YourName_S43_curve.py",
         ["Type the code in section 11 of the reading",
          "Margin % per product, then one row per price change",
          "In two comments: why is the highest revenue not the highest profit?"],
         "profit peaks at `+5` (NT$`18,646`); revenue at `-15` (NT$`33,356`)")
ex_slide(2, "Applied", "Markdowns That Clear the Stock",
         "the price cut each slow product needs to sell out in 14 days",
         "YourName_S43_markdown.py",
         ["Needed sales = stock / 14; change = (needed / now - 1) / elasticity",
          "A missing bracket gives `SyntaxError: '(' was never closed`: ask the AI Chat",
          "Save the plan to `data/markdown_plan.csv`"],
         "mug `-18.4`% (NT$`286`), lanyard `-12.3`%, hoodie `-4.6`%")
ex_slide(3, "Advanced", "The Best Semester Price for Each Product",
         "the price change with the most profit over 14 days, counting leftover losses",
         "YourName_S43_plan.py",
         ["`season_profit(price, unit_cost, daily_units, stock)`",
          "Try `-20%` to `+20%` for every product; keep the best",
          "Requirements and hints: section 13 of the reading"],
         "5 cuts, 5 rises: NT$`253,557` vs NT$`242,372`")

N = len(slides)
parts = []
for i, (kicker, title, body, cls) in enumerate(slides, 1):
    parts.append(f'<section class="slide">\n  <div><span class="eyebrow">MODULE 4</span><span class="kicker">{e(kicker)}</span></div>\n'
                 f'  <div class="title">{e(title)}</div><div class="rule"></div>\n  <div class="{cls}">{body}</div>\n'
                 f'  <div class="footer"><span>Business Analytics &amp; AI Application | Course 6141</span><span>Slide {i} / {N}</span></div>\n</section>\n')
out = head + EXTRA + "</style>\n</head>\n<body>\n" + "\n".join(parts) + "\n" + script
(ROOT / "slides_src" / "session_04_03.html").write_text(out)
print("slides:", N)
