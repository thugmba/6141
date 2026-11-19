#!/usr/bin/env python3
"""Draw the Session 4.3 diagrams from the lab data into assets/session_04_03_fig_*.png.

Every number in a chart is computed from the lab CSV files with the same steps as the
code in 6141.md, so the figures always match the code outputs.
Usage: python3 scripts/make_session_04_03_figures.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
df = pd.read_csv(ROOT / "data" / "session_04_03_dataset.csv", index_col="Product_ID")
test = pd.read_csv(ROOT / "data" / "session_04_03_price_test.csv")
slope, intercept = np.polyfit(np.log(test["Test_Price_TWD"]), np.log(test["Avg_Daily_Units"]), 1)
ELASTICITY = round(slope, 2)
DAYS_LEFT = 14

BLUE, RED, GREEN, AMBER, INK, MUTED = "#2563EB", "#991B1B", "#16A34A", "#F59E0B", "#1F2937", "#64748B"
plt.rcParams.update({"font.family": "Times New Roman", "font.size": 15, "axes.edgecolor": MUTED,
                     "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white"})
money = matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}")


def save(fig, name):
    fig.savefig(OUT / f"session_04_03_fig_{name}.png", dpi=200, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)


def box(ax, x, y, w, h, text, fc, ec, size=15, weight="normal", color=INK):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec=ec, lw=2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=size, weight=weight,
            color=color, linespacing=1.35)


def arrow(ax, x1, y1, x2, y2, color=MUTED):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=22, lw=2.2, color=color))


# 1. The hoodie at three prices: margin x sales = profit
def price_tradeoff():
    h = df.loc["MER-101"]
    changes = [-0.10, 0.0, 0.10]
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2), sharey=True)
    for ax, c in zip(axes, changes):
        price = h["Price_TWD"] * (1 + c)
        units = h["Daily_Units"] * (1 + ELASTICITY * c)
        margin = price - h["Unit_Cost_TWD"]
        ax.bar([0], [margin], width=0.5, color=BLUE)
        ax.bar([1], [units * 50], width=0.5, color=AMBER)
        ax.text(0, margin + 25, f"margin\nNT\\${margin:,.0f}", ha="center", fontsize=14)
        ax.text(1, units * 50 + 25, f"sales\n{units:.1f} a day", ha="center", fontsize=14)
        ax.set_title(f"price NT\\${price:,.0f} ({c * 100:+.0f}%)\nprofit NT\\${margin * units:,.0f} a day",
                     fontsize=15.5, weight="bold", color=INK)
        ax.set_xticks([]); ax.set_yticks([])
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.set_ylim(0, 720)
    fig.suptitle("The hoodie: a higher price earns more per item but sells fewer (elasticity -1.55)",
                 fontsize=15, color=MUTED, y=-0.02)
    fig.tight_layout()
    save(fig, "price_tradeoff")


# 2. The price test with the fitted line
def price_test():
    fig, ax = plt.subplots(figsize=(9, 4.6))
    ax.scatter(test["Test_Price_TWD"], test["Avg_Daily_Units"], s=130, color=BLUE, zorder=3)
    for _, r in test.iterrows():
        ax.text(r["Test_Price_TWD"], r["Avg_Daily_Units"] + 0.18, f"week {r['Test_Week']}", ha="center", fontsize=13)
    xs = np.linspace(770, 1010, 50)
    ax.plot(xs, np.exp(intercept) * xs ** slope, color=RED, lw=2.5, label=f"fitted line: elasticity {ELASTICITY}")
    ax.set_xlabel("Hoodie price in the test week (NT\\$)", fontsize=15)
    ax.set_ylabel("Hoodies sold per day", fontsize=15)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, fontsize=14)
    ax.grid(color="#E2E8F0", zorder=0)
    save(fig, "price_test")


# 3. Revenue and profit for store-wide price changes
def profit_curve():
    changes = [-0.15, -0.10, -0.05, 0.0, 0.05, 0.10, 0.15]
    rev, prof = [], []
    for c in changes:
        price = df["Price_TWD"] * (1 + c)
        units = df["Daily_Units"] * (1 + ELASTICITY * c)
        rev.append((price * units).sum()); prof.append(((price - df["Unit_Cost_TWD"]) * units).sum())
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))
    labels = [f"{c * 100:+.0f}%" for c in changes]
    for ax, vals, title, color in [(axes[0], rev, "Daily revenue (NT\\$)", "#93C5FD"), (axes[1], prof, "Daily profit (NT\\$)", GREEN)]:
        best = int(np.argmax(vals))
        ax.bar(range(len(vals)), vals, color=[RED if i == best else color for i in range(len(vals))], width=0.65)
        for i, v in enumerate(vals):
            ax.text(i, v + max(vals) * 0.005, f"{v:,.0f}", ha="center", fontsize=11.5, rotation=0)
        ax.set_xticks(range(len(vals)), labels, fontsize=13.5)
        ax.set_ylim(min(vals) * 0.9, max(vals) * 1.03)
        ax.yaxis.set_major_formatter(money)
        ax.set_title(title + "  (red: the highest)", fontsize=15.5, weight="bold")
        ax.set_xlabel("Change to every price", fontsize=14)
        ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(w_pad=3)
    save(fig, "profit_curve")


# 4. Days of stock against the days left
def days_of_stock():
    d = (df["Stock_Units"] / df["Daily_Units"]).sort_values()
    names = df.loc[d.index, "Product_Name"]
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.barh(range(len(d)), d, color=[RED if v > DAYS_LEFT else GREEN for v in d], height=0.65)
    for i, v in enumerate(d):
        ax.text(19.9, i, f"{v:.1f} days", va="center", ha="right", fontsize=13)
    ax.axvline(DAYS_LEFT, color=INK, lw=2.2, ls="--")
    ax.text(DAYS_LEFT + 0.1, len(d) - 0.4, f"{DAYS_LEFT} days left", fontsize=14.5, weight="bold")
    ax.set_yticks(range(len(d)), list(names), fontsize=14)
    ax.set_xlabel("Days of stock = stock / daily sales   (red: will not sell out in time)", fontsize=14.5)
    ax.set_xlim(0, 20)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, "days_of_stock")


# 5. The pricing steps
def pricing_steps():
    fig, ax = plt.subplots(figsize=(14, 3.3))
    ax.set_xlim(0, 14); ax.set_ylim(0, 3.3); ax.axis("off")
    steps = [("1. Price test", f"how strongly sales react\nelasticity {ELASTICITY}", "#EFF6FF", BLUE),
             ("2. Simulate", "profit, not revenue,\nfor each price change", "#F8FAFC", MUTED),
             ("3. Deadline", f"days of stock vs\n{DAYS_LEFT} days left", "#FEF3C7", AMBER),
             ("4. Season plan", "best price per product,\ncounting leftovers", "#DCFCE7", GREEN)]
    for i, (head, body, fc, ec) in enumerate(steps):
        x = 0.05 + i * 3.5
        box(ax, x, 0.25, 3.0, 2.8, "", fc, ec)
        ax.text(x + 1.5, 2.35, head, ha="center", va="center", fontsize=17, weight="bold", color=INK)
        ax.text(x + 1.5, 1.15, body, ha="center", va="center", fontsize=15, color=INK, linespacing=1.4)
        if i < 3:
            arrow(ax, x + 3.02, 1.65, x + 3.48, 1.65)
    save(fig, "pricing_steps")


if __name__ == "__main__":
    price_tradeoff(); price_test(); profit_curve(); days_of_stock(); pricing_steps()
    print("Wrote", len(list(OUT.glob("session_04_03_fig_*.png"))), "figures to assets/")
