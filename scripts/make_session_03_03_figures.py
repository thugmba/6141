#!/usr/bin/env python3
"""Draw the Session 3.3 diagrams from the lab data into assets/session_03_03_fig_*.png.

Every number in a chart is computed from data/session_03_03_dataset.csv with the same
steps as the code in 6141.md, so the figures always match the code outputs.
Usage: python3 scripts/make_session_03_03_figures.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import KFold, cross_val_score, train_test_split

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
df = pd.read_csv(ROOT / "data" / "session_03_03_dataset.csv", index_col="Listing_ID")
FEATURES = ["Age_Months", "Storage_GB", "Battery_Health_Pct"]
X_train, X_test, y_train, y_test = train_test_split(
    df[FEATURES], df["Sold_Price_TWD"], test_size=0.25, random_state=42)
model = LinearRegression().fit(X_train, y_train)
predicted = model.predict(X_test)

BLUE, RED, GREEN, AMBER, INK, MUTED = "#2563EB", "#991B1B", "#16A34A", "#F59E0B", "#1F2937", "#64748B"
STORAGE_COLORS = {128: "#93C5FD", 256: BLUE, 512: "#1E3A8A"}
plt.rcParams.update({"font.family": "Times New Roman", "font.size": 15, "axes.edgecolor": MUTED,
                     "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white"})


def save(fig, name):
    fig.savefig(OUT / f"session_03_03_fig_{name}.png", dpi=200, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)


def box(ax, x, y, w, h, text, fc, ec, size=15, weight="normal", color=INK):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec=ec, lw=2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=size, weight=weight,
            color=color, linespacing=1.35)


def arrow(ax, x1, y1, x2, y2, color=MUTED):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=22, lw=2.2, color=color))


def ntd(v):
    # "\$" keeps matplotlib from reading a pair of $ signs as math
    return f"NT\\${v:,.0f}"


# 1. Price against age, with the best straight line through all 20 sales
def price_vs_age():
    fig, ax = plt.subplots(figsize=(7.8, 4.4))
    for gb, color in STORAGE_COLORS.items():
        part = df[df["Storage_GB"] == gb]
        ax.scatter(part["Age_Months"], part["Sold_Price_TWD"], s=110, color=color, edgecolors="white",
                   linewidths=1.2, label=f"{gb} GB", zorder=3)
    line = LinearRegression().fit(df[["Age_Months"]], df["Sold_Price_TWD"])
    ages = np.array([[4], [44]])
    ax.plot(ages.ravel(), line.predict(pd.DataFrame(ages, columns=["Age_Months"])), color=RED, lw=3, zorder=2,
            label="best straight line")
    ax.set_xlabel("Age of the phone (months)", fontsize=15)
    ax.set_ylabel("Sold price (NT\\$)", fontsize=15)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, fontsize=13.5, loc="upper right")
    ax.grid(color="#E2E8F0", zorder=0)
    save(fig, "price_vs_age")


# 2. Create, fit, predict
def fit_predict():
    fig, ax = plt.subplots(figsize=(13, 3.9))
    ax.set_xlim(0, 13); ax.set_ylim(0, 3.9); ax.axis("off")
    box(ax, 0.05, 0.9, 2.5, 2.1, "1. Create\nLinearRegression()\n(an empty model)", "#F8FAFC", MUTED, size=14.5)
    box(ax, 3.2, 0.9, 3.0, 2.1, f"2. Fit\n.fit(X_train, y_train)\nlearns from {len(X_train)} past sales", "#EFF6FF", BLUE, size=14.5)
    box(ax, 6.85, 0.9, 2.7, 2.1, "the price formula\n(start value\n+ effects)", "#FFFFFF", BLUE, size=14.5)
    box(ax, 10.2, 0.9, 2.75, 2.1, f"3. Predict\n.predict(new phone)\n{ntd(model.predict(pd.DataFrame([[24, 256, 88]], columns=FEATURES))[0])}", "#DCFCE7", GREEN, size=14.5, weight="bold")
    arrow(ax, 2.55, 1.95, 3.2, 1.95); arrow(ax, 6.2, 1.95, 6.85, 1.95, BLUE); arrow(ax, 9.55, 1.95, 10.2, 1.95, GREEN)
    ax.text(11.57, 0.55, "24 months, 256 GB, 88%", ha="center", fontsize=13.5, color=MUTED)
    save(fig, "fit_predict")


# 3. Actual vs predicted prices of the 5 test phones
def test_predictions():
    ids = list(X_test.index)
    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    xs = np.arange(len(ids)); w = 0.36
    ax.bar(xs - w / 2, y_test.values, w * 0.92, color="#CBD5E1", label="Actual price")
    ax.bar(xs + w / 2, predicted, w * 0.92, color=BLUE, label="Predicted price")
    for x, a, p in zip(xs, y_test.values, predicted):
        err = round(p) - a
        ax.text(x, max(a, p) + 450, f"{err:+,} ", ha="center", fontsize=15, weight="bold", color=RED)
    ax.set_xticks(xs, ids, fontsize=15)
    ax.set_ylim(15000, 25500)
    ax.set_ylabel("Price (NT\\$)", fontsize=15)
    ax.set_xlabel("Red numbers: error = predicted - actual (NT\\$)", fontsize=14.5)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, fontsize=14, loc="upper left", ncol=2)
    save(fig, "test_predictions")


# 4. The model against guessing the average price
def model_vs_guess():
    mae_model = mean_absolute_error(y_test, predicted)
    mae_guess = mean_absolute_error(y_test, [y_train.mean()] * len(y_test))
    fig, ax = plt.subplots(figsize=(9, 3.4))
    labels = ["Guess the average price", "The learned formula"]
    vals = [mae_guess, mae_model]
    ax.barh([1, 0], vals, color=["#CBD5E1", BLUE], height=0.55)
    for y, v in zip([1, 0], vals):
        ax.text(v + 40, y, ntd(v), va="center", fontsize=17, weight="bold", color=INK)
    ax.set_yticks([1, 0], labels, fontsize=15)
    ax.set_xlim(0, mae_guess * 1.25)
    ax.set_xlabel("Typical error on the 5 test phones (MAE, NT\\$)", fontsize=15)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, "model_vs_guess")


# 5. Five-fold cross-validation
def cv_folds():
    errors = -cross_val_score(LinearRegression(), df[FEATURES], df["Sold_Price_TWD"], cv=5,
                              scoring="neg_mean_absolute_error")
    folds = list(KFold(5).split(df))
    n = len(df)
    fig, ax = plt.subplots(figsize=(13, 4.6))
    ax.set_xlim(-2.2, n + 3.6); ax.set_ylim(-0.9, 5.2); ax.axis("off")
    for r, (train_idx, test_idx) in enumerate(folds):
        y = 4 - r
        ax.text(-0.3, y + 0.4, f"Round {r + 1}", ha="right", va="center", fontsize=15, color=INK)
        for i in range(n):
            test = i in test_idx
            ax.add_patch(Rectangle((i + 0.06, y + 0.08), 0.88, 0.64, fc="#FCA5A5" if test else "#DBEAFE",
                                   ec=RED if test else "#93C5FD", lw=1.5))
        ax.text(n + 0.3, y + 0.4, ntd(errors[r]), va="center", fontsize=15, weight="bold", color=RED)
    ax.text(n + 0.3, 5.0, "typical error", fontsize=14, color=MUTED, va="center")
    ax.text(n / 2, -0.45, f"red: 4 test phones   blue: 16 training phones   average {ntd(errors.mean())}, worst {ntd(errors.max())}",
            ha="center", fontsize=14.5, color=INK)
    ax.text(0, 5.0, "the 20 phones, in file order", fontsize=14, color=MUTED, va="center")
    save(fig, "cv_folds")


# 6. The steps of a prediction model
def model_steps():
    errors = -cross_val_score(LinearRegression(), df[FEATURES], df["Sold_Price_TWD"], cv=5,
                              scoring="neg_mean_absolute_error")
    steps = [("1. Prepare", f"X: 3 features, y: price\n{len(X_train)} train / {len(X_test)} test"),
             ("2. Fit", "learn the formula\nfrom the training sales"),
             ("3. Test", f"MAE {ntd(mean_absolute_error(y_test, predicted))}\n(guessing: {ntd(mean_absolute_error(y_test, [y_train.mean()] * len(y_test)))})"),
             ("4. Cross-validate", f"5 rounds: {ntd(errors.mean())}\non average")]
    fig, ax = plt.subplots(figsize=(14, 3.3))
    ax.set_xlim(0, 14); ax.set_ylim(0, 3.3); ax.axis("off")
    for i, (head, body) in enumerate(steps):
        x = 0.05 + i * 2.95
        box(ax, x, 0.2, 2.6, 2.8, "", "#EFF6FF" if i in (1, 2) else "#F8FAFC", BLUE if i in (1, 2) else MUTED)
        ax.text(x + 1.3, 2.35, head, ha="center", va="center", fontsize=17, weight="bold", color=INK)
        ax.text(x + 1.3, 1.1, body, ha="center", va="center", fontsize=14.5, color=INK, linespacing=1.4)
        arrow(ax, x + 2.62, 1.6, x + 2.93, 1.6)
    box(ax, 11.85, 0.6, 2.1, 2.0, "5. Predict\nnew listings", "#DCFCE7", GREEN, size=16, weight="bold")
    save(fig, "model_steps")


if __name__ == "__main__":
    price_vs_age(); fit_predict(); test_predictions(); model_vs_guess(); cv_folds(); model_steps()
    print("Wrote", len(list(OUT.glob("session_03_03_fig_*.png"))), "figures to assets/")
