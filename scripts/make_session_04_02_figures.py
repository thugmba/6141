#!/usr/bin/env python3
"""Draw the Session 4.2 diagrams from the lab data into assets/session_04_02_fig_*.png.

Every number in a chart is computed from the lab CSV files with the same steps as the
code in 6141.md, so the figures always match the code outputs.
Usage: python3 scripts/make_session_04_02_figures.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
history = pd.read_csv(ROOT / "data" / "session_04_02_dataset.csv", index_col="Member_ID")
active = pd.read_csv(ROOT / "data" / "session_04_02_active.csv", index_col="Member_ID")
FEATURES = ["Months_As_Member_Count", "Visits_Last_Month_Count", "Days_Since_Last_Visit_Count"]
model = make_pipeline(StandardScaler(), LogisticRegression()).fit(history[FEATURES], history["Stopped_Visiting_Binary"])
active["Chance"] = model.predict_proba(active[FEATURES])[:, 1].round(3)
active["Annual_Profit"] = active["Monthly_Profit_TWD"] * 12
active["Profit_At_Risk"] = (active["Chance"] * active["Annual_Profit"]).round(0)
COUPON_COST, SUCCESS_RATE = 45, 0.25

BLUE, RED, GREEN, AMBER, INK, MUTED = "#2563EB", "#991B1B", "#16A34A", "#F59E0B", "#1F2937", "#64748B"
plt.rcParams.update({"font.family": "Times New Roman", "font.size": 15, "axes.edgecolor": MUTED,
                     "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white"})


def save(fig, name):
    fig.savefig(OUT / f"session_04_02_fig_{name}.png", dpi=200, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)


def box(ax, x, y, w, h, text, fc, ec, size=15, weight="normal", color=INK):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec=ec, lw=2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=size, weight=weight,
            color=color, linespacing=1.35)


def arrow(ax, x1, y1, x2, y2, color=MUTED):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=22, lw=2.2, color=color))


def ntd(v, decimals=0):
    return f"NT\\${v:,.{decimals}f}"


# 1. The expected value of a coupon for one member
def expected_value():
    m = active.loc["NOW-209"]
    saved = m["Chance"] * SUCCESS_RATE * m["Annual_Profit"]
    fig, ax = plt.subplots(figsize=(14, 3.6))
    ax.set_xlim(0, 14); ax.set_ylim(0, 3.6); ax.axis("off")
    parts = [(f"chance of stopping\n{m['Chance']}", "#FEE2E2", RED), (f"success rate\n{SUCCESS_RATE}", "#FEF3C7", AMBER),
             (f"yearly profit\n{ntd(m['Annual_Profit'])}", "#EFF6FF", BLUE), (f"saved profit\n{ntd(saved, 2)}", "#FFFFFF", INK),
             (f"net value\n+{ntd(saved - COUPON_COST, 2)}", "#DCFCE7", GREEN)]
    xs = [0.05, 2.75, 5.45, 8.4, 11.6]
    for (t, fc, ec), x in zip(parts, xs):
        box(ax, x, 1.0, 2.3, 1.6, t, fc, ec, size=15.5, weight="bold" if x == xs[-1] else "normal")
    for x, sym in [(2.55, "x"), (5.25, "x"), (8.0, "="), (11.2, f"- {COUPON_COST}")]:
        ax.text(x, 1.8, sym, ha="center", va="center", fontsize=20, weight="bold", color=INK)
    ax.text(7, 0.35, "NOW-209 and a free-drink coupon: an offer is worth sending when its net value is above 0",
            ha="center", fontsize=14.5, color=MUTED, style="italic")
    save(fig, "expected_value")


# 2. Ranked by chance vs ranked by profit at risk
def chance_vs_risk():
    by_chance = active.sort_values("Chance", ascending=False)
    by_risk = active.sort_values("Profit_At_Risk", ascending=False)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.6))
    for ax, data, col, title, fmt, color in [
            (axes[0], by_chance, "Chance", "Ranked by chance of stopping", "{:.2f}", "#93C5FD"),
            (axes[1], by_risk, "Profit_At_Risk", "Ranked by profit at risk (NT\\$)", "{:,.0f}", BLUE)]:
        ys = range(len(data))[::-1]
        colors = [RED if i == "NOW-203" else GREEN if i == "NOW-204" else color for i in data.index]
        ax.barh(list(ys), data[col], color=colors, height=0.7)
        for y, v in zip(ys, data[col]):
            ax.text(v, y, " " + fmt.format(v), va="center", fontsize=12.5)
        ax.set_yticks(list(ys), list(data.index), fontsize=12.5)
        ax.set_title(title, fontsize=16, weight="bold", color=INK)
        ax.spines[["top", "right"]].set_visible(False)
        ax.set_xticks([])
        ax.set_xlim(0, data[col].max() * 1.25)
    fig.text(0.5, -0.02, "red: NOW-203 (likely to stop, little profit)   green: NOW-204 (less likely, most profit)",
             ha="center", fontsize=14, color=INK)
    fig.tight_layout(w_pad=3)
    save(fig, "chance_vs_risk")


# 3. From a chance to a decision
def chance_to_decision():
    fig, ax = plt.subplots(figsize=(14, 3.3))
    ax.set_xlim(0, 14); ax.set_ylim(0, 3.3); ax.axis("off")
    steps = [("1. Chance", "the churn model\n(Step 1)", "#F8FAFC", MUTED),
             ("2. Profit at risk", "chance x yearly profit\n(Step 2)", "#EFF6FF", BLUE),
             ("3. Net value", "x success rate - cost\n(Step 3)", "#FEF3C7", AMBER),
             ("4. Decision", "which offer, if any\n(Exercises)", "#DCFCE7", GREEN)]
    for i, (head, body, fc, ec) in enumerate(steps):
        x = 0.05 + i * 3.5
        box(ax, x, 0.25, 3.0, 2.8, "", fc, ec)
        ax.text(x + 1.5, 2.35, head, ha="center", va="center", fontsize=17, weight="bold", color=INK)
        ax.text(x + 1.5, 1.15, body, ha="center", va="center", fontsize=15, color=INK, linespacing=1.4)
        if i < 3:
            arrow(ax, x + 3.02, 1.65, x + 3.48, 1.65)
    save(fig, "chance_to_decision")


if __name__ == "__main__":
    expected_value(); chance_vs_risk(); chance_to_decision()
    print("Wrote", len(list(OUT.glob("session_04_02_fig_*.png"))), "figures to assets/")
