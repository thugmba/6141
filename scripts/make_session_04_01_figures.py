#!/usr/bin/env python3
"""Draw the Session 4.1 diagrams from the lab data into assets/session_04_01_fig_*.png.

Every number in a chart is computed from the lab CSV files with the same steps as the
code in 6141.md, so the figures always match the code outputs.
Usage: python3 scripts/make_session_04_01_figures.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
train = pd.read_csv(ROOT / "data" / "session_03_04_dataset.csv", index_col="User_ID")
tonight = pd.read_csv(ROOT / "data" / "session_04_01_new_batch.csv", index_col="User_ID")
FEATURES = ["Weeks_Inactive_Count", "Monthly_Minutes_Count"]
model = make_pipeline(StandardScaler(), LogisticRegression()).fit(train[FEATURES], train["Cancelled_Binary"])
chance = model.predict_proba(tonight[FEATURES])[:, 1]
THRESHOLD = 0.3

BLUE, RED, GREEN, AMBER, INK, MUTED = "#2563EB", "#991B1B", "#16A34A", "#F59E0B", "#1F2937", "#64748B"
plt.rcParams.update({"font.family": "Times New Roman", "font.size": 15, "axes.edgecolor": MUTED,
                     "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white"})


def save(fig, name):
    fig.savefig(OUT / f"session_04_01_fig_{name}.png", dpi=200, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)


def box(ax, x, y, w, h, text, fc, ec, size=15, weight="normal", color=INK):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec=ec, lw=2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=size, weight=weight,
            color=color, linespacing=1.35)


def arrow(ax, x1, y1, x2, y2, color=MUTED):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=22, lw=2.2, color=color))


# 1. Train once; every night, four stages and a run log
def decision_system():
    fig, ax = plt.subplots(figsize=(14, 5.4))
    ax.set_xlim(0, 14); ax.set_ylim(0, 5.6); ax.axis("off")
    ax.text(0.05, 5.25, "Once", fontsize=17, weight="bold", color=BLUE, va="center")
    box(ax, 0.05, 3.55, 3.1, 1.35, "past users + answers\ntrain the model", "#EFF6FF", BLUE)
    box(ax, 3.9, 3.55, 3.6, 1.35, "save it to a file\nmodels/coupon_model.joblib", "#FFFFFF", BLUE, size=13.5)
    arrow(ax, 3.15, 4.22, 3.9, 4.22, BLUE)
    ax.text(0.05, 2.75, "Every night", fontsize=17, weight="bold", color=GREEN, va="center")
    stages = [("1. Ingestion", "tonight's users"), ("2. Validation", "columns present,\nno empty cells"),
              ("3. Scoring", "load the model;\nchance of cancelling"), ("4. Action", f"coupon at {THRESHOLD}\nor more")]
    for i, (head, body) in enumerate(stages):
        x = 0.05 + i * 3.5
        box(ax, x, 1.0, 2.9, 1.45, f"{head}\n{body}", "#DCFCE7" if i == 3 else "#F0FDF4", GREEN, size=14.5)
        if i < 3:
            arrow(ax, x + 2.9, 1.72, x + 3.5, 1.72, GREEN)
    arrow(ax, 5.7, 3.55, 7.5, 2.45, BLUE)
    ax.text(7.0, 0.35, "run log: records, latency (ms), and accuracy for every stage, every night",
            ha="center", fontsize=14.5, color=MUTED, style="italic")
    save(fig, "decision_system")


# 2. Tonight's chances and the coupon threshold
def tonight_chart():
    order = np.argsort(-chance)
    ids = tonight.index[order]
    ch = chance[order]
    fig, ax = plt.subplots(figsize=(10, 4.6))
    xs = np.arange(len(ch))
    ax.bar(xs, ch, color=[RED if c >= THRESHOLD else "#93C5FD" for c in ch], width=0.7, zorder=2)
    for x, c in zip(xs, ch):
        ax.text(x, c + 0.02, f"{c:.2f}", ha="center", fontsize=13.5, color=INK)
    ax.axhline(THRESHOLD, color=INK, lw=2, ls="--", zorder=3)
    ax.text(len(ch) - 0.5, THRESHOLD + 0.03, f"coupon at {THRESHOLD} or more", ha="right", fontsize=14.5, weight="bold")
    ax.set_xticks(xs, list(ids), fontsize=12.5, rotation=30)
    ax.set_ylabel("Chance of cancelling", fontsize=15)
    ax.set_ylim(0, 1.05)
    ax.spines[["top", "right"]].set_visible(False)
    ax.text(len(ch) - 0.5, 1.0, f"red: coupon ({int((chance >= THRESHOLD).sum())} of {len(ch)})", ha="right", fontsize=14.5, color=RED, va="top")
    save(fig, "tonight")


# 3. Drift: minutes of training users vs tonight's users
def drift_chart():
    col = "Monthly_Minutes_Count"
    tr, tn = train[col], tonight[col]
    change = (tn.mean() - tr.mean()) / tr.mean() * 100
    fig, ax = plt.subplots(figsize=(10, 3.9))
    for y, vals, color, label in [(1, tr, "#93C5FD", f"training users ({len(tr)})"), (0, tn, RED, f"tonight's users ({len(tn)})")]:
        ax.scatter(vals, np.full(len(vals), y) + np.linspace(-0.12, 0.12, len(vals)), s=80, color=color,
                   edgecolors="white", linewidths=1, zorder=3)
        ax.plot([vals.mean()] * 2, [y - 0.3, y + 0.3], color=INK, lw=3, zorder=4)
        ax.text(vals.mean(), y + 0.36, f"average {vals.mean():,.0f}", ha="center", fontsize=14.5, weight="bold")
    ax.set_yticks([1, 0], [f"training users ({len(tr)})", f"tonight ({len(tn)})"], fontsize=15)
    ax.set_ylim(-0.6, 1.7)
    ax.set_xlabel(f"Minutes played last month  (tonight's average: {change:.1f}%)", fontsize=15)
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", color="#E2E8F0", zorder=0)
    save(fig, "drift")


# 4. The nightly job with its fallback and its review flag
def nightly_job():
    fig, ax = plt.subplots(figsize=(14, 4.6))
    ax.set_xlim(0, 14); ax.set_ylim(0, 4.8); ax.axis("off")
    steps = [("validate", "#F8FAFC", MUTED), ("check drift", "#FEF3C7", AMBER), ("model file\nexists?", "#FFFFFF", INK)]
    for i, (t, fc, ec) in enumerate(steps):
        box(ax, 0.05 + i * 2.75, 1.9, 2.2, 1.3, t, fc, ec, size=15.5)
        if i < len(steps) - 1:
            arrow(ax, 2.25 + i * 2.75, 2.55, 2.8 + i * 2.75, 2.55)
    box(ax, 8.3, 3.15, 2.6, 1.3, "yes: load, score,\ncoupon at 0.3", "#DCFCE7", GREEN, size=14.5)
    box(ax, 8.3, 0.35, 2.6, 1.3, "no: fallback rule\n3+ weeks inactive", "#FEE2E2", RED, size=14.5)
    arrow(ax, 7.75, 2.75, 8.3, 3.7, GREEN); arrow(ax, 7.75, 2.35, 8.3, 1.0, RED)
    box(ax, 11.6, 1.9, 2.35, 1.3, "save decisions\n+ report", "#EFF6FF", BLUE, size=15)
    arrow(ax, 10.9, 3.8, 11.6, 2.9, GREEN); arrow(ax, 10.9, 1.0, 11.6, 2.2, RED)
    ax.text(12.78, 1.45, "needs review if drift\nor fallback", ha="center", va="top", fontsize=13.5, color=AMBER, weight="bold")
    save(fig, "nightly_job")


if __name__ == "__main__":
    decision_system(); tonight_chart(); drift_chart(); nightly_job()
    print("Wrote", len(list(OUT.glob("session_04_01_fig_*.png"))), "figures to assets/")
