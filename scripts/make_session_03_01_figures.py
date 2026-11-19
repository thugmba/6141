#!/usr/bin/env python3
"""Draw the Session 3.1 diagrams from the lab data into assets/session_03_01_fig_*.png.

Every number in a chart is computed from data/session_03_01_*.csv, so the figures
always match the code outputs in 6141.md.
Usage: python3 scripts/make_session_03_01_figures.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
past = pd.read_csv(ROOT / "data" / "session_03_01_dataset.csv")
new = pd.read_csv(ROOT / "data" / "session_03_01_new_messages.csv")

REAL, SPAM, MISTAKE, GOOD, INK, MUTED = "#2563EB", "#991B1B", "#F59E0B", "#16A34A", "#1F2937", "#64748B"
plt.rcParams.update({"font.family": "Times New Roman", "font.size": 15, "axes.edgecolor": MUTED,
                     "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white"})


def save(fig, name):
    fig.savefig(OUT / f"session_03_01_fig_{name}.png", dpi=200, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)


def box(ax, x, y, w, h, text, fc, ec, size=15, weight="normal", color=INK):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.06",
                                fc=fc, ec=ec, lw=2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=size,
            weight=weight, color=color, linespacing=1.3)


def arrow(ax, x1, y1, x2, y2, color=MUTED):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=22,
                                 lw=2.2, color=color))


def plural(n, word):
    return f"{n} {word}" if n == 1 else f"{n} {word}s"


def mistakes(data, t):
    flagged = data["Link_Count"] >= t
    spam = data["Is_Spam_Binary"] == 1
    return int((~flagged & spam).sum()), int((flagged & ~spam).sum())


def accuracy(data, t):
    m, f = mistakes(data, t)
    return 1 - (m + f) / len(data)


# 1. AI > ML > DL, and how a rule-based system differs from machine learning
def ai_ml_dl():
    fig, (a, b) = plt.subplots(1, 2, figsize=(11.5, 4.7), gridspec_kw={"width_ratios": [1, 1.3]})
    for ax in (a, b):
        ax.set_xlim(0, 10); ax.set_ylim(0, 6.2); ax.axis("off")
    a.set_title("Three nested ideas", fontsize=19, weight="bold", color=INK)
    box(a, 0.1, 0.1, 9.8, 5.9, "", "#F1F5F9", MUTED)
    a.text(0.45, 5.35, "AI: any system that does a task\nwe link to human thinking", fontsize=15, color=INK, va="center")
    box(a, 0.6, 0.4, 8.8, 4.1, "", "#FEF2F2", SPAM)
    a.text(0.9, 3.85, "ML: learns a rule from past\nexamples (a spam filter)", fontsize=15, color=SPAM, va="center", weight="bold")
    box(a, 1.1, 0.7, 7.8, 2.3, "DL: many-layered neural\nnetworks for images, sound,\nand text (face unlock)",
        "#FFFFFF", INK, size=15)

    b.set_xlim(-0.15, 10.45)
    b.set_title("Who writes the rule?", fontsize=19, weight="bold", color=INK)
    rows = [("Rule-based system", INK, MUTED, "#F1F5F9", 3.45,
             ["A person writes:\n\"3 or more links\"", "Computer\napplies it", "Inbox or\nspam folder"]),
            ("Machine learning", SPAM, SPAM, "#FEF2F2", 0.6,
             ["20 past emails\n+ known answers", "Computer tries\nmany rules", "Best rule:\n\"4 or more links\""])]
    for title, tc, ec, fc, y, texts in rows:
        b.text(0, y + 1.85, title, fontsize=17, weight="bold", color=tc, va="center")
        xs = [(0, 3.3), (3.85, 2.6), (7.0, 3.3)]
        for i, ((x, w), t) in enumerate(zip(xs, texts)):
            box(b, x, y, w, 1.45, t, fc if i != 1 else "#FFFFFF", ec, size=14.5,
                weight="bold" if (i == 2 and tc == SPAM) else "normal")
        arrow(b, 3.3, y + 0.72, 3.85, y + 0.72, ec); arrow(b, 6.45, y + 0.72, 7.0, y + 0.72, ec)
    fig.tight_layout(w_pad=2)
    save(fig, "ai_ml_dl")


# 2. The four cases of the old rule on the 20 past emails
def four_cases():
    missed, false_alarm = mistakes(past, 3)
    n_spam = int(past["Is_Spam_Binary"].sum())
    n_real = len(past) - n_spam
    cells = [[("Spam caught", n_spam - missed, "correct", GOOD), ("Missed spam", missed, "mistake", MISTAKE)],
             [("False alarm", false_alarm, "mistake", MISTAKE), ("Real email delivered", n_real - false_alarm, "correct", GOOD)]]
    fig, ax = plt.subplots(figsize=(8.6, 5.4))
    ax.set_xlim(0, 10); ax.set_ylim(0, 6.6); ax.axis("off")
    ax.text(6.05, 6.25, "The old rule's decision (3 or more links)", ha="center", fontsize=16, weight="bold", color=INK)
    ax.text(4.1, 5.6, "Spam folder", ha="center", fontsize=16, color=INK)
    ax.text(8.0, 5.6, "Inbox", ha="center", fontsize=16, color=INK)
    ax.text(0.95, 3.85, f"Really\nspam\n({n_spam})", ha="center", va="center", fontsize=16, color=SPAM, weight="bold")
    ax.text(0.95, 1.55, f"Really\nreal\n({n_real})", ha="center", va="center", fontsize=16, color=REAL, weight="bold")
    for r, row in enumerate(cells):
        for c, (name, n, kind, col) in enumerate(row):
            x, y = 2.15 + c * 3.9, 2.75 - r * 2.3
            fill = "#DCFCE7" if kind == "correct" else "#FEF3C7"
            box(ax, x, y, 3.7, 2.1, "", fill, col)
            ax.text(x + 1.85, y + 1.42, name, ha="center", va="center", fontsize=19, weight="bold", color=INK)
            ax.text(x + 1.85, y + 0.62, f"{plural(n, 'email')}: {kind}", ha="center", va="center", fontsize=18, color=INK)
    correct = len(past) - missed - false_alarm
    ax.text(6.05, -0.05, f"Accuracy = correct / all = {correct} / {len(past)} = {correct / len(past):.0%}",
            ha="center", fontsize=16, weight="bold", color=INK)
    save(fig, "four_cases")


# 3. Every past email on a line of link counts, with the threshold drawn in
def strip(ax, data, t, label):
    spam = data["Is_Spam_Binary"] == 1
    flagged = data["Link_Count"] >= t
    ax.axvspan(t - 0.5, 9.8, color="#FEE2E2", zorder=0)
    ax.axvline(t - 0.5, color=SPAM, lw=3, zorder=1)
    top = 2.35
    ax.text(t - 0.35, top, "spam folder  →", color=SPAM, fontsize=14, weight="bold", va="center")
    ax.text(t - 0.65, top, "←  inbox", color=REAL, fontsize=14, weight="bold", va="center", ha="right")
    for row, (is_spam, y, color, marker) in enumerate([(False, 1.45, REAL, "o"), (True, 0.45, SPAM, "s")]):
        part = data[spam == is_spam]
        for links, group in part.groupby("Link_Count"):
            for k, (_, e) in enumerate(group.iterrows()):
                yy = y + (k - (len(group) - 1) / 2) * 0.26
                wrong = flagged[e.name] != is_spam
                ax.scatter(links, yy, s=150, marker=marker, color=color, zorder=3,
                           edgecolors=MISTAKE if wrong else "white", linewidths=3.2 if wrong else 1)
    m, f = mistakes(data, t)
    ax.set_title(f"{label}: {m} missed spam + {plural(f, 'false alarm')} = {plural(m + f, 'mistake')}",
                 fontsize=16, weight="bold", color=INK, loc="left")
    ax.set_xlim(-0.6, 9.8); ax.set_ylim(-0.05, 2.65)
    ax.set_yticks([1.45, 0.45], ["Real emails", "Spam"])
    for tick, c in zip(ax.get_yticklabels(), [REAL, SPAM]):
        tick.set_color(c); tick.set_fontweight("bold")
    ax.set_xticks(range(10))
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)


def thresholds():
    fig, ax = plt.subplots(figsize=(12, 3.6))
    strip(ax, past, 3, "Old rule, 3 or more links")
    ax.set_xlabel("Links in the email  (orange ring = mistake)", fontsize=15)
    save(fig, "old_rule_line")

    fig, ax = plt.subplots(figsize=(12, 3.6))
    strip(ax, past, 4, "Learned rule, 4 or more links")
    ax.set_xlabel("Links in the email  (orange ring = mistake)", fontsize=15)
    save(fig, "learned_rule_line")

    fig, axes = plt.subplots(2, 1, figsize=(12, 6.8), sharex=True)
    strip(axes[0], past, 3, "Old rule, 3 or more links")
    strip(axes[1], past, 4, "Learned rule, 4 or more links")
    axes[1].set_xlabel("Links in the email  (orange ring = mistake)", fontsize=15)
    fig.tight_layout(h_pad=1.6)
    save(fig, "rule_compare_line")


# 4. Mistakes for each threshold: too low gives false alarms, too high misses spam
def mistake_bars():
    ts = range(1, 7)
    missed = [mistakes(past, t)[0] for t in ts]
    alarms = [mistakes(past, t)[1] for t in ts]
    fig, ax = plt.subplots(figsize=(8.6, 4.9))
    ax.bar(ts, alarms, color=REAL, width=0.62, label="False alarms (real email sent to spam)")
    ax.bar(ts, missed, bottom=alarms, color=SPAM, width=0.62, label="Missed spam (scam in the inbox)")
    best = min(ts, key=lambda t: sum(mistakes(past, t)))
    for t, a, m in zip(ts, alarms, missed):
        ax.text(t, a + m + 0.2, str(a + m), ha="center", fontsize=17, weight="bold", color=INK)
    ax.annotate("fewest mistakes:\nthe learned rule", xy=(best, 1.9), xytext=(best + 0.15, 6.2),
                fontsize=15, color=GOOD, weight="bold", ha="center",
                arrowprops=dict(arrowstyle="-|>", color=GOOD, lw=2.2))
    ax.annotate("old rule", xy=(2.85, 4.9), xytext=(2.1, 6.9), fontsize=15, color=MUTED, ha="center",
                arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.8))
    ax.set_xticks(list(ts), [f"{t} or more" for t in ts])
    ax.set_xlabel("Spam if the email has ... links", fontsize=15)
    ax.set_ylabel("Mistakes on 20 past emails", fontsize=15)
    ax.set_ylim(0, 9.3)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, fontsize=14, loc="upper right")
    save(fig, "mistakes_by_threshold")


# 5. Past score vs new score for both rules
def past_vs_new():
    rules = [("Old rule\n(3 or more links)", 3), ("Learned rule\n(4 or more links)", 4)]
    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    w = 0.34
    for i, (name, t) in enumerate(rules):
        for j, (data, label, color) in enumerate([(past, "20 past emails (used to choose the rule)", "#CBD5E1"),
                                                  (new, "10 new emails (the honest score)", SPAM)]):
            v = accuracy(data, t)
            ax.bar(i + (j - 0.5) * w, v, w * 0.92, color=color, label=label if i == 0 else None)
            ax.text(i + (j - 0.5) * w, v + 0.02, f"{v:.0%}", ha="center", fontsize=17, weight="bold", color=INK)
    ax.set_xticks([0, 1], [r[0] for r in rules], fontsize=15)
    ax.set_ylim(0, 1.32); ax.set_yticks([0, 0.25, 0.5, 0.75, 1], ["0%", "25%", "50%", "75%", "100%"])
    ax.set_ylabel("Accuracy", fontsize=15)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, fontsize=14, loc="upper left", ncol=1)
    save(fig, "past_vs_new")


# 6. The three steps of machine learning
def ml_steps():
    best = min(range(1, 7), key=lambda t: sum(mistakes(past, t)))
    fig, ax = plt.subplots(figsize=(14, 3.4))
    ax.set_xlim(0, 14); ax.set_ylim(0, 3.4); ax.axis("off")
    steps = [("1. Collect examples", f"{len(past)} past emails, each\nmarked spam or not"),
             ("2. Search", f"try thresholds 1 to 6;\nfewest mistakes: {best} or more links"),
             ("3. Test on new data", f"{len(new)} new emails:\n{accuracy(new, best):.0%}, not {accuracy(past, best):.0%}")]
    for i, (head, body) in enumerate(steps):
        x = 0.1 + i * 4.75
        box(ax, x, 0.2, 4.0, 2.9, "", "#FEF2F2" if i == 1 else "#F8FAFC", SPAM if i == 1 else MUTED)
        ax.text(x + 2.0, 2.35, head, ha="center", va="center", fontsize=19, weight="bold", color=SPAM if i == 1 else INK)
        ax.text(x + 2.0, 1.25, body, ha="center", va="center", fontsize=16, color=INK, linespacing=1.4)
        if i < 2:
            arrow(ax, x + 4.05, 1.65, x + 4.7, 1.65)
    save(fig, "ml_steps")


if __name__ == "__main__":
    ai_ml_dl(); four_cases(); thresholds(); mistake_bars(); past_vs_new(); ml_steps()
    print("Wrote", len(list(OUT.glob("session_03_01_fig_*.png"))), "figures to assets/")
