#!/usr/bin/env python3
"""Draw the Session 3.2 diagrams from the lab data into assets/session_03_02_fig_*.png.

Every number in a chart is computed from data/session_03_02_dataset.csv with the same
steps as the code in 6141.md, so the figures always match the code outputs.
Usage: python3 scripts/make_session_03_02_figures.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
df = pd.read_csv(ROOT / "data" / "session_03_02_dataset.csv", index_col="User_ID")

FEAT, TARGET, LABEL, GAP, TEXT, GOOD, INK, MUTED = (
    "#2563EB", "#991B1B", "#64748B", "#F59E0B", "#7C3AED", "#16A34A", "#1F2937", "#64748B")
plt.rcParams.update({"font.family": "Times New Roman", "font.size": 15, "axes.edgecolor": MUTED,
                     "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white"})

# The preparation of Step 3: encode, split first, then fill and scale with training rules
NUMBERS = ["Age_Years_Count", "Monthly_Minutes_Count", "Weeks_Inactive_Count"]
X = pd.get_dummies(df.drop(columns=["Cancelled_Binary"]), columns=["Plan_Type"], drop_first=True, dtype=int)
y = df["Cancelled_Binary"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
imputer = SimpleImputer(strategy="median").fit(X_train[NUMBERS])
scaler = StandardScaler().fit(imputer.transform(X_train[NUMBERS]))
train_filled = imputer.transform(X_train[NUMBERS])
train_scaled = scaler.transform(train_filled)
test_scaled = scaler.transform(imputer.transform(X_test[NUMBERS]))
test_leaky = StandardScaler().fit_transform(imputer.transform(X_test[NUMBERS]))
SHORT = {"Age_Years_Count": "Age", "Monthly_Minutes_Count": "Minutes", "Weeks_Inactive_Count": "Weeks inactive"}


def save(fig, name):
    fig.savefig(OUT / f"session_03_02_fig_{name}.png", dpi=200, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)


def box(ax, x, y, w, h, text, fc, ec, size=15, weight="normal", color=INK):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.06",
                                fc=fc, ec=ec, lw=2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=size,
            weight=weight, color=color, linespacing=1.3)


def arrow(ax, x1, y1, x2, y2, color=MUTED, text=None):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=22,
                                 lw=2.2, color=color))
    if text:
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.22, text, ha="center", fontsize=14,
                color=color, weight="bold")


def fmt(v):
    return "empty" if pd.isna(v) else (f"{v:.0f}" if isinstance(v, float) else str(v))


# 1. The raw table: each column's role, the gaps, and the text column
def raw_table():
    rows = df.head(10).reset_index()
    cols = list(rows.columns)
    widths = [1.5, 1.35, 1.7, 1.6, 1.45, 1.6]
    heads = ["User_ID", "Age", "Monthly\nminutes", "Weeks\ninactive", "Plan_Type", "Cancelled"]
    xs = np.concatenate([[0], np.cumsum(widths)])
    fig, ax = plt.subplots(figsize=(11, 6.4))
    ax.set_xlim(-0.05, xs[-1] + 0.05); ax.set_ylim(-0.6 * len(rows) - 0.2, 2.1); ax.axis("off")
    for x0, x1, label, color in [(xs[0], xs[1], "label", LABEL), (xs[1], xs[5], "X: features (the clues)", FEAT),
                                 (xs[5], xs[6], "y: target", TARGET)]:
        ax.add_patch(Rectangle((x0 + 0.04, 1.35), x1 - x0 - 0.08, 0.6, fc=color, ec="none"))
        ax.text((x0 + x1) / 2, 1.65, label, ha="center", va="center", color="white", fontsize=16, weight="bold")
    for i, h in enumerate(heads):
        ax.text((xs[i] + xs[i + 1]) / 2, 0.65, h, ha="center", va="center", fontsize=15, weight="bold", color=INK)
    ax.plot([0, xs[-1]], [0.15, 0.15], color=INK, lw=1.5)
    for r, row in rows.iterrows():
        yy = -0.6 * r - 0.3
        for i, c in enumerate(cols):
            v = row[c]
            fill = None
            if pd.isna(v):
                fill = "#FEF3C7"
            elif c == "Plan_Type":
                fill = "#EDE9FE"
            if fill:
                ax.add_patch(Rectangle((xs[i] + 0.06, yy - 0.26), widths[i] - 0.12, 0.52, fc=fill,
                                       ec=GAP if pd.isna(v) else "none", lw=2))
            ax.text((xs[i] + xs[i + 1]) / 2, yy, fmt(v), ha="center", va="center", fontsize=15,
                    color=GAP if pd.isna(v) else (TEXT if c == "Plan_Type" else INK),
                    weight="bold" if pd.isna(v) else "normal")
    ax.text(xs[-1] / 2, -0.6 * len(rows) - 0.15, f"first 10 of {len(df)} users", ha="center",
            fontsize=14, color=MUTED, style="italic")
    save(fig, "raw_table")


# 2. One-hot encoding: one text column becomes two 0/1 columns
def one_hot():
    users = [u for u in ["USR-204", "USR-202", "USR-201"]]
    plans = df.loc[users, "Plan_Type"].tolist()
    fig, ax = plt.subplots(figsize=(11, 4.6))
    ax.set_xlim(0, 11); ax.set_ylim(0, 4.7); ax.axis("off")
    ax.text(1.0, 4.2, "User", ha="center", fontsize=16, weight="bold", color=INK)
    ax.text(3.0, 4.2, "Plan_Type", ha="center", fontsize=16, weight="bold", color=TEXT)
    ax.text(7.2, 4.2, "Plan_Type_\nIndividual", ha="center", fontsize=16, weight="bold", color=FEAT, va="center")
    ax.text(9.5, 4.2, "Plan_Type_\nStudent", ha="center", fontsize=16, weight="bold", color=FEAT, va="center")
    for k, (u, p) in enumerate(zip(users, plans)):
        yy = 2.95 - k * 1.05
        ax.text(1.0, yy, u, ha="center", va="center", fontsize=16, color=INK)
        box(ax, 2.1, yy - 0.38, 1.8, 0.76, p, "#EDE9FE", TEXT, size=16)
        for x, col in [(7.2, "Individual"), (9.5, "Student")]:
            one = p == col
            box(ax, x - 0.6, yy - 0.38, 1.2, 0.76, "1" if one else "0", "#DCFCE7" if one else "#FFFFFF",
                GOOD if one else MUTED, size=18, weight="bold" if one else "normal")
    arrow(ax, 4.3, 1.9, 6.2, 1.9, TEXT, "pd.get_dummies")
    ax.text(5.5, 0.15, "Family is the row with 0 in both columns: drop_first=True leaves its column out",
            ha="center", fontsize=15, color=MUTED, style="italic")
    save(fig, "one_hot")


# 3. The number columns on one ruler, before and after scaling (training users)
def scales():
    fig, axes = plt.subplots(2, 1, figsize=(12, 6.4))
    data = [(train_filled, "Before scaling: the raw numbers on one ruler", None),
            (train_scaled, "After scaling: each value = standard deviations from the training average", None)]
    colors = [FEAT, TEXT, TARGET]
    for ax, (values, title, _) in zip(axes, data):
        for j, col in enumerate(NUMBERS):
            yy = 2 - j
            ax.scatter(values[:, j], np.full(len(values), yy), s=110, color=colors[j], alpha=0.85,
                       edgecolors="white", linewidths=1, zorder=3)
        ax.set_yticks([2, 1, 0], [SHORT[c] for c in NUMBERS])
        for tick, c in zip(ax.get_yticklabels(), colors):
            tick.set_color(c); tick.set_fontweight("bold")
        ax.set_ylim(-0.6, 2.6)
        ax.set_title(title, fontsize=16, weight="bold", color=INK, loc="left")
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.tick_params(axis="y", length=0)
        ax.grid(axis="x", color="#E2E8F0", zorder=0)
    axes[0].set_xlim(-100, 2500)
    axes[0].annotate("age and weeks are squeezed\nnear 0 on this ruler", xy=(40, 0.4), xytext=(500, 1.55),
                     fontsize=14, color=MUTED, arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.6))
    axes[1].set_xlim(-2.2, 2.7)
    axes[1].axvline(0, color=MUTED, lw=1.5, ls="--")
    axes[1].text(0.05, 2.35, "average = 0", fontsize=14, color=MUTED)
    fig.tight_layout(h_pad=2)
    save(fig, "scales")


# 4. Split first, fit on the training users, transform both sets
def split_fit():
    med = [f"{v:g}" for v in imputer.statistics_]
    avg = [f"{v:.2f}" for v in scaler.mean_]
    fig, ax = plt.subplots(figsize=(13, 4.8))
    ax.set_xlim(0, 13); ax.set_ylim(0, 4.8); ax.axis("off")
    box(ax, 0.1, 1.6, 2.2, 1.4, f"{len(df)} users", "#F8FAFC", MUTED, size=17, weight="bold")
    ax.text(1.2, 3.3, "1. split first", ha="center", fontsize=15, color=INK, weight="bold")
    box(ax, 3.1, 3.0, 3.0, 1.3, f"{len(X_train)} training users\n({y_train.sum()} cancelled)", "#EFF6FF", FEAT, size=16, weight="bold")
    box(ax, 3.1, 0.3, 3.0, 1.3, f"{len(X_test)} test users\n({y_test.sum()} cancelled), set aside", "#FEF2F2", TARGET, size=15.5, weight="bold")
    arrow(ax, 2.3, 2.6, 3.1, 3.5); arrow(ax, 2.3, 2.0, 3.1, 1.1)
    box(ax, 6.9, 2.85, 3.6, 1.6, f"Rules learned\nmedians: {', '.join(med)}\naverages: {', '.join(avg)}",
        "#FFFFFF", FEAT, size=14)
    arrow(ax, 6.1, 3.65, 6.9, 3.65, FEAT)
    ax.text(6.5, 4.5, "2. fit", ha="center", fontsize=15, color=FEAT, weight="bold")
    box(ax, 11.1, 3.0, 1.8, 1.3, "prepared\ntraining set", "#EFF6FF", FEAT, size=15)
    box(ax, 11.1, 0.3, 1.8, 1.3, "prepared\ntest set", "#FEF2F2", TARGET, size=15)
    arrow(ax, 10.5, 3.65, 11.1, 3.65, FEAT)
    arrow(ax, 9.6, 2.85, 11.1, 1.6, FEAT)
    ax.text(9.7, 2.3, "3. transform\nboth sets", fontsize=14, color=FEAT, weight="bold", ha="right", va="center")
    arrow(ax, 6.1, 0.95, 11.1, 0.95, TARGET)
    ax.text(8.6, 0.45, "test users only receive the rules", ha="center", fontsize=14, color=TARGET)
    save(fig, "split_fit")


# 5. Leakage: the test users' scaled averages with training rules vs scaled on their own
def leakage():
    correct = test_scaled.mean(axis=0)
    leaky = test_leaky.mean(axis=0)
    fig, ax = plt.subplots(figsize=(9.2, 4.6))
    xs = np.arange(len(NUMBERS)); w = 0.36
    ax.bar(xs - w / 2, correct, w * 0.92, color=FEAT, label="Correct: scaled with the training rules")
    ax.bar(xs + w / 2, np.where(np.abs(leaky) < 1e-9, 0.02, leaky), w * 0.92, color=TARGET,
           label="Leaky: test users scaled on their own")
    for x, v in zip(xs, correct):
        ax.text(x - w / 2, v + (0.06 if v >= 0 else -0.16), f"{v:.2f}", ha="center", fontsize=17, weight="bold", color=INK)
    for x, v in zip(xs, leaky):
        ax.text(x + w / 2, 0.08, f"{abs(v):.2f}", ha="center", fontsize=17, weight="bold", color=TARGET)
    ax.axhline(0, color=INK, lw=1.2)
    ax.set_xticks(xs, [SHORT[c] for c in NUMBERS], fontsize=16)
    ax.set_ylabel("Average of the 4 test users", fontsize=15)
    ax.set_ylim(-1.15, 2.05)
    ax.spines[["top", "right", "bottom"]].set_visible(False)
    ax.tick_params(axis="x", length=0)
    ax.legend(frameon=False, fontsize=14, loc="upper right")
    save(fig, "leakage")


# 6. The three preparation steps
def prep_steps():
    steps = [("1. Find the problems", f"X: {df.shape[1] - 1} clues, y: cancelled\n"
                                      f"{int(df.isnull().sum().sum())} gaps, 1 text column"),
             ("2. Text to 0/1", "Plan_Type becomes\n2 columns of 0 and 1"),
             ("3. Split, then fill\nand scale", f"{len(X_train)} train / {len(X_test)} test;\nrules from training users")]
    fig, ax = plt.subplots(figsize=(14, 3.4))
    ax.set_xlim(0, 14); ax.set_ylim(0, 3.4); ax.axis("off")
    for i, (head, body) in enumerate(steps):
        x = 0.05 + i * 3.75
        box(ax, x, 0.2, 3.25, 2.9, "", "#EFF6FF" if i == 2 else "#F8FAFC", FEAT if i == 2 else MUTED)
        ax.text(x + 1.62, 2.4, head, ha="center", va="center", fontsize=18, weight="bold", color=FEAT if i == 2 else INK)
        ax.text(x + 1.62, 1.05, body, ha="center", va="center", fontsize=15.5, color=INK, linespacing=1.4)
        arrow(ax, x + 3.28, 1.65, x + 3.72, 1.65)
    box(ax, 11.3, 0.75, 2.6, 1.8, "Model-ready\ndata\n(Session 3.3)", "#DCFCE7", GOOD, size=17, weight="bold")
    save(fig, "prep_steps")


if __name__ == "__main__":
    raw_table(); one_hot(); scales(); split_fit(); leakage(); prep_steps()
    print("Wrote", len(list(OUT.glob("session_03_02_fig_*.png"))), "figures to assets/")
