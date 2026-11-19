#!/usr/bin/env python3
"""Draw the Session 3.4 diagrams from the lab data into assets/session_03_04_fig_*.png.

Every number in a chart is computed from data/session_03_04_dataset.csv with the same
steps as the code in 6141.md, so the figures always match the code outputs.
Usage: python3 scripts/make_session_03_04_figures.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
df = pd.read_csv(ROOT / "data" / "session_03_04_dataset.csv", index_col="User_ID")
FEATURES = ["Weeks_Inactive_Count", "Monthly_Minutes_Count"]
X_train, X_test, y_train, y_test = train_test_split(
    df[FEATURES], df["Cancelled_Binary"], test_size=0.5, random_state=42, stratify=df["Cancelled_Binary"])
model = make_pipeline(StandardScaler(), LogisticRegression()).fit(X_train, y_train)
chance = model.predict_proba(X_test)[:, 1]
MISS_COST, COUPON_COST = 1800, 60

BLUE, RED, GREEN, AMBER, INK, MUTED = "#2563EB", "#991B1B", "#16A34A", "#F59E0B", "#1F2937", "#64748B"
plt.rcParams.update({"font.family": "Times New Roman", "font.size": 15, "axes.edgecolor": MUTED,
                     "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white"})


def save(fig, name):
    fig.savefig(OUT / f"session_03_04_fig_{name}.png", dpi=200, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)


def box(ax, x, y, w, h, text, fc, ec, size=15, weight="normal", color=INK):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec=ec, lw=2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=size, weight=weight,
            color=color, linespacing=1.35)


def arrow(ax, x1, y1, x2, y2, color=MUTED):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=22, lw=2.2, color=color))


def ntd(v):
    return f"NT\\${v:,.0f}"


def counts(threshold):
    tn, fp, fn, tp = confusion_matrix(y_test, (chance >= threshold).astype(int)).ravel()
    return tp, fp, fn, tn


# 1. The test users sorted by chance, with thresholds 0.5 and 0.3
def threshold_line():
    order = np.argsort(-chance)
    ch = chance[order]
    actual = y_test.values[order]
    fig, ax = plt.subplots(figsize=(11, 4.6))
    xs = np.arange(len(ch))
    ax.bar(xs, ch, color=[RED if a == 1 else "#93C5FD" for a in actual], width=0.75, zorder=2)
    for t, style, label in [(0.5, "--", "threshold 0.5"), (0.3, "-", "threshold 0.3")]:
        ax.axhline(t, color=INK, lw=2, ls=style, zorder=3)
        ax.text(len(ch) - 0.4, t + 0.02, label, ha="right", fontsize=14.5, weight="bold", color=INK)
    ax.set_xticks(xs, [u.replace("USR-", "") for u in X_test.index[order]], fontsize=11.5, rotation=60)
    ax.set_xlabel("The 20 test users (USR-...), highest chance first", fontsize=14.5)
    ax.set_ylabel("Chance of cancelling", fontsize=15)
    ax.set_ylim(0, 1.05)
    ax.spines[["top", "right"]].set_visible(False)
    ax.bar([0], [0], color=RED, label="really cancelled")
    ax.bar([0], [0], color="#93C5FD", label="really stayed")
    ax.legend(frameon=False, fontsize=14, loc="upper center", ncol=2)
    save(fig, "threshold_line")


# 2. The confusion matrix at 0.5
def confusion():
    tp, fp, fn, tn = counts(0.5)
    cells = [[("Caught", tp, "coupon, would cancel", "#DCFCE7", GREEN), ("Missed", fn, f"no coupon: {ntd(MISS_COST)} each", "#FEE2E2", RED)],
             [("False alarm", fp, f"wasted coupon: {ntd(COUPON_COST)} each", "#FEF3C7", AMBER), ("Left alone", tn, "no coupon, stayed", "#DCFCE7", GREEN)]]
    fig, ax = plt.subplots(figsize=(9.5, 5.4))
    ax.set_xlim(0, 10); ax.set_ylim(0, 6.4); ax.axis("off")
    ax.text(6.1, 6.05, "Decision at threshold 0.5", ha="center", fontsize=16, weight="bold", color=INK)
    ax.text(4.15, 5.45, "Coupon", ha="center", fontsize=16, color=INK)
    ax.text(8.05, 5.45, "No coupon", ha="center", fontsize=16, color=INK)
    ax.text(1.0, 3.95, f"Really\ncancelled\n({tp + fn})", ha="center", va="center", fontsize=16, color=RED, weight="bold")
    ax.text(1.0, 1.65, f"Really\nstayed\n({fp + tn})", ha="center", va="center", fontsize=16, color=BLUE, weight="bold")
    for r, row in enumerate(cells):
        for c, (name, n, note, fill, edge) in enumerate(row):
            x, y = 2.2 + c * 3.9, 2.85 - r * 2.3
            box(ax, x, y, 3.7, 2.1, "", fill, edge)
            ax.text(x + 1.85, y + 1.45, f"{name}: {n}", ha="center", va="center", fontsize=19, weight="bold", color=INK)
            ax.text(x + 1.85, y + 0.65, note, ha="center", va="center", fontsize=14.5, color=INK)
    save(fig, "confusion")


# 3. Cost of mistakes by threshold
def cost_by_threshold():
    ts = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
    miss = [counts(t)[2] * MISS_COST for t in ts]
    alarm = [counts(t)[1] * COUPON_COST for t in ts]
    fig, ax = plt.subplots(figsize=(9.5, 4.6))
    xs = np.arange(len(ts))
    ax.bar(xs, alarm, color=AMBER, width=0.6, label="wasted coupons")
    ax.bar(xs, miss, bottom=alarm, color=RED, width=0.6, label="missed cancellers")
    best = min(range(len(ts)), key=lambda i: (miss[i] + alarm[i], ts[i]))
    for i in xs:
        ax.text(i, miss[i] + alarm[i] + 150, ntd(miss[i] + alarm[i]), ha="center", fontsize=14,
                weight="bold", color=GREEN if i == best else INK)
    ax.set_xticks(xs, [str(t) for t in ts], fontsize=15)
    ax.set_xlabel("Threshold (coupon if the chance is at or above it)", fontsize=15)
    ax.set_ylabel("Cost of mistakes (NT\\$)", fontsize=15)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax.set_ylim(0, max(m + a for m, a in zip(miss, alarm)) * 1.18)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, fontsize=14, loc="upper left")
    save(fig, "cost_by_threshold")


# 4. K-Means groups
def kmeans_groups():
    scaled = StandardScaler().fit_transform(df[FEATURES])
    groups = KMeans(n_clusters=3, random_state=42, n_init=10).fit_predict(scaled)
    prof = df.assign(Group=groups).groupby("Group")[FEATURES].mean()
    order = prof.sort_values("Weeks_Inactive_Count").index
    names = dict(zip(order, ["steady listeners", "casual listeners", "drifting away"]))
    colors = dict(zip(order, [GREEN, AMBER, RED]))
    fig, ax = plt.subplots(figsize=(9.5, 5))
    for g in order:
        part = df[groups == g]
        ax.scatter(part["Weeks_Inactive_Count"] + np.linspace(-0.12, 0.12, len(part)), part["Monthly_Minutes_Count"],
                   s=110, color=colors[g], edgecolors="white", linewidths=1.2, label=f"{names[g]} ({len(part)})", zorder=3)
    ax.set_xlabel("Weeks inactive", fontsize=15)
    ax.set_ylabel("Minutes played last month", fontsize=15)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(color="#E2E8F0", zorder=0)
    ax.legend(frameon=False, fontsize=14, loc="upper right")
    save(fig, "kmeans_groups")


# 5. Supervised vs unsupervised
def two_kinds():
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.set_xlim(0, 14); ax.set_ylim(0, 5.2); ax.axis("off")
    ax.text(0.05, 4.85, "Supervised learning: the answers are known", fontsize=17, weight="bold", color=BLUE, va="center")
    row = [("past users\n+ answers\n(cancelled?)", "#EFF6FF"), ("train a\nclassifier", "#FFFFFF"), ("chance of\ncancelling", "#FFFFFF"),
           ("threshold\n(chosen by cost)", "#FFFFFF"), ("coupon\nor not", "#DCFCE7")]
    for i, (t, fc) in enumerate(row):
        box(ax, 0.05 + i * 2.85, 2.75, 2.3, 1.6, t, fc, BLUE, size=15)
        if i < 4:
            arrow(ax, 2.35 + i * 2.85, 3.55, 2.9 + i * 2.85, 3.55, BLUE)
    ax.text(0.05, 2.15, "Unsupervised learning: no answers", fontsize=17, weight="bold", color=GREEN, va="center")
    row = [("users\n(no answers)", "#F0FDF4"), ("put the columns\non one scale", "#FFFFFF"), ("K-Means\nfinds K groups", "#FFFFFF"),
           ("read each\ngroup's profile", "#DCFCE7")]
    for i, (t, fc) in enumerate(row):
        box(ax, 0.05 + i * 2.85, 0.1, 2.3, 1.6, t, fc, GREEN, size=15)
        if i < 3:
            arrow(ax, 2.35 + i * 2.85, 0.9, 2.9 + i * 2.85, 0.9, GREEN)
    save(fig, "two_kinds")


if __name__ == "__main__":
    threshold_line(); confusion(); cost_by_threshold(); kmeans_groups(); two_kinds()
    print("Wrote", len(list(OUT.glob("session_03_04_fig_*.png"))), "figures to assets/")
