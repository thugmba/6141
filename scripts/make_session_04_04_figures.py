#!/usr/bin/env python3
"""Draw the Session 4.4 diagrams from the lab data into assets/session_04_04_fig_*.png.

Every number in a chart is computed from data/session_04_04_dataset.csv with the same
steps as the code in 6141.md, so the figures always match the code outputs.
Usage: python3 scripts/make_session_04_04_figures.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
df = pd.read_csv(ROOT / "data" / "session_04_04_dataset.csv", index_col="Applicant_ID")
FEATURES = ["GPA", "Coding_Test_Score", "Club_Activities_Count"]
THRESHOLD = 0.70
rates = (df["Screening_Score"] >= THRESHOLD).groupby(df["Group"]).mean()
copy = LinearRegression().fit(df[FEATURES], df["Screening_Score"])
effects = (df[FEATURES] - df[FEATURES].mean()) * copy.coef_

BLUE, RED, GREEN, AMBER, INK, MUTED = "#2563EB", "#991B1B", "#16A34A", "#F59E0B", "#1F2937", "#64748B"
GA, GB = "#2563EB", "#F59E0B"
plt.rcParams.update({"font.family": "Times New Roman", "font.size": 15, "axes.edgecolor": MUTED,
                     "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white"})


def save(fig, name):
    fig.savefig(OUT / f"session_04_04_fig_{name}.png", dpi=200, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)


def box(ax, x, y, w, h, text, fc, ec, size=15, weight="normal", color=INK):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec=ec, lw=2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=size, weight=weight,
            color=color, linespacing=1.35)


def arrow(ax, x1, y1, x2, y2, color=MUTED):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=22, lw=2.2, color=color))


# 1. How a proxy creates a gap
def proxy():
    prof = df.groupby("Group")[FEATURES].mean()
    fig, ax = plt.subplots(figsize=(14, 4.3))
    ax.set_xlim(0, 14); ax.set_ylim(0, 4.3); ax.axis("off")
    box(ax, 0.05, 1.4, 2.8, 1.6, "Group\n(never used\nby the tool)", "#F1F5F9", MUTED, size=15)
    box(ax, 3.6, 2.5, 3.4, 1.5, f"GPA, coding score\nalmost equal\n({prof.loc['Group_A', 'GPA']:.2f} vs {prof.loc['Group_B', 'GPA']:.2f})", "#FFFFFF", MUTED, size=14.5)
    box(ax, 3.6, 0.3, 3.4, 1.5, f"club activities\n{prof.loc['Group_A', 'Club_Activities_Count']:.1f} vs {prof.loc['Group_B', 'Club_Activities_Count']:.1f}\n(free time?)", "#FEF3C7", AMBER, size=14.5, weight="bold")
    arrow(ax, 2.85, 2.5, 3.6, 3.2); arrow(ax, 2.85, 1.9, 3.6, 1.05, AMBER)
    box(ax, 7.8, 1.4, 2.6, 1.6, "screening\nscore", "#EFF6FF", BLUE, size=15.5)
    arrow(ax, 7.0, 3.2, 7.8, 2.5); arrow(ax, 7.0, 1.05, 7.8, 1.9, AMBER)
    box(ax, 11.2, 1.4, 2.75, 1.6, f"invited\nA {rates['Group_A']:.0%} vs B {rates['Group_B']:.0%}", "#FEE2E2", RED, size=15.5, weight="bold")
    arrow(ax, 10.4, 2.2, 11.2, 2.2)
    save(fig, "proxy")


# 2. Invite rates and the four-fifths line
def rates_chart():
    fig, ax = plt.subplots(figsize=(8, 4.6))
    ax.bar([0, 1], rates.values, color=[GA, GB], width=0.55)
    for x, v in zip([0, 1], rates.values):
        ax.text(x, v + 0.02, f"{v:.0%}", ha="center", fontsize=18, weight="bold")
    line = 0.8 * rates.max()
    ax.axhline(line, color=RED, lw=2.2, ls="--")
    ax.text(1.32, line + 0.02, f"four-fifths of {rates.max():.0%} = {line:.0%}", ha="right", fontsize=14.5, color=RED, weight="bold")
    ax.set_xticks([0, 1], ["Group A", "Group B"], fontsize=16)
    ax.set_ylim(0, 1); ax.set_yticks([0, 0.25, 0.5, 0.75, 1], ["0%", "25%", "50%", "75%", "100%"])
    ax.set_ylabel("Invited to an interview", fontsize=15)
    ax.set_title(f"ratio {rates.min():.2f} / {rates.max():.2f} = {rates.min() / rates.max():.3f}: fails", fontsize=15.5, color=INK)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, "rates")


# 3. Feature profiles by group
def profiles():
    prof = df.groupby("Group")[FEATURES].mean()
    titles = ["GPA", "Coding test score", "Club activities"]
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2))
    for ax, col, title in zip(axes, FEATURES, titles):
        vals = prof[col]
        ax.bar([0, 1], vals, color=[GA, GB], width=0.55)
        for x, v in zip([0, 1], vals):
            ax.text(x, v * 1.02, f"{v:.2f}" if col == "GPA" else f"{v:.1f}", ha="center", fontsize=15, weight="bold")
        ax.set_xticks([0, 1], ["Group A", "Group B"], fontsize=14.5)
        ax.set_title(title, fontsize=16, weight="bold", color=RED if col == "Club_Activities_Count" else INK)
        ax.set_yticks([]); ax.set_ylim(0, vals.max() * 1.2)
        ax.spines[["top", "right", "left"]].set_visible(False)
    fig.tight_layout(w_pad=3)
    save(fig, "profiles")


# 4. Two applicants' feature effects
def two_applicants():
    ids = ["APP-315", "APP-319"]
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.4), sharey=True)
    labels = ["GPA", "Coding test", "Clubs"]
    for ax, i in zip(axes, ids):
        e = effects.loc[i].values
        ax.barh([2, 1, 0], e, color=[GREEN if v > 0 else RED for v in e], height=0.55)
        for y, v in zip([2, 1, 0], e):
            ax.text(v + (0.006 if v > 0 else -0.006), y, f"{v:+.3f}", va="center", ha="left" if v > 0 else "right", fontsize=14)
        ax.axvline(0, color=INK, lw=1.2)
        r = df.loc[i]
        decision = "invited" if r["Screening_Score"] >= THRESHOLD else "rejected"
        ax.set_title(f"{i} ({r['Group'].replace('_', ' ')}): score {r['Screening_Score']:.2f}, {decision}\n"
                     f"GPA {r['GPA']}, coding {r['Coding_Test_Score']}, clubs {r['Club_Activities_Count']}",
                     fontsize=14.5, color=GREEN if decision == "invited" else RED)
        ax.set_yticks([2, 1, 0], labels, fontsize=14.5)
        ax.set_xlim(-0.22, 0.22)
        ax.spines[["top", "right"]].set_visible(False)
        ax.set_xlabel("effect on the score (vs the average applicant)", fontsize=13.5)
    fig.tight_layout(w_pad=3)
    save(fig, "two_applicants")


# 5. The audit steps
def audit_steps():
    fig, ax = plt.subplots(figsize=(14, 3.3))
    ax.set_xlim(0, 14); ax.set_ylim(0, 3.3); ax.axis("off")
    steps = [("1. Compare rates", "selection rate by group;\nfour-fifths rule", "#EFF6FF", BLUE),
             ("2. Find the cause", "compare the groups'\nfeatures", "#FEF3C7", AMBER),
             ("3. Explain", "feature effects for\neach decision", "#F8FAFC", MUTED),
             ("4. Decide and record", "fix the cause, add review;\nnever decide by group", "#DCFCE7", GREEN)]
    for i, (head, body, fc, ec) in enumerate(steps):
        x = 0.05 + i * 3.5
        box(ax, x, 0.25, 3.0, 2.8, "", fc, ec)
        ax.text(x + 1.5, 2.35, head, ha="center", va="center", fontsize=17, weight="bold", color=INK)
        ax.text(x + 1.5, 1.15, body, ha="center", va="center", fontsize=14.5, color=INK, linespacing=1.4)
        if i < 3:
            arrow(ax, x + 3.02, 1.65, x + 3.48, 1.65)
    save(fig, "audit_steps")


if __name__ == "__main__":
    proxy(); rates_chart(); profiles(); two_applicants(); audit_steps()
    print("Wrote", len(list(OUT.glob("session_04_04_fig_*.png"))), "figures to assets/")
