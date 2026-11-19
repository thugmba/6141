#!/usr/bin/env python3
"""Draw the diagrams of the Python Setup Clinic into assets/setup_clinic_fig_*.png.

Usage: python3 scripts/make_setup_clinic_figures.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
BLUE, RED, GREEN, AMBER, INK, MUTED = "#2563EB", "#991B1B", "#16A34A", "#F59E0B", "#1F2937", "#64748B"
MONO = "DejaVu Sans Mono"
plt.rcParams.update({"font.family": "Times New Roman", "font.size": 15,
                     "figure.facecolor": "white", "savefig.facecolor": "white"})


def save(fig, name):
    fig.savefig(OUT / f"setup_clinic_fig_{name}.png", dpi=200, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)


def box(ax, x, y, w, h, text, fc, ec, size=15, weight="normal", color=INK, family=None):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                fc=fc, ec=ec, lw=2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=size, weight=weight,
            color=color, linespacing=1.35, family=family or plt.rcParams["font.family"])


def arrow(ax, x1, y1, x2, y2, color=MUTED):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=22, lw=2.2, color=color))


# 1. Which Python answers when you type `python`?
def which_python():
    fig, ax = plt.subplots(figsize=(13, 5.4))
    ax.set_xlim(0, 13); ax.set_ylim(0, 5.6); ax.axis("off")
    box(ax, 0.05, 2.1, 3.15, 1.4, "Terminal\n$ python my_script.py", "#F8FAFC", MUTED, size=13.5, family=MONO)
    box(ax, 4.0, 3.4, 4.2, 1.8, "(.venv) is shown\nthe project's own Python\n+ tensorflow, pillow, ...", "#DCFCE7", GREEN, size=15)
    box(ax, 4.0, 0.4, 4.2, 1.8, "no (.venv)\nanother Python on the computer\n(no tensorflow)", "#FEF3C7", AMBER, size=15)
    arrow(ax, 3.2, 3.0, 4.0, 4.2, GREEN); arrow(ax, 3.2, 2.6, 4.0, 1.4, AMBER)
    box(ax, 9.2, 3.55, 3.7, 1.5, "script runs\nreturn code 0", "#DCFCE7", GREEN, size=16, weight="bold")
    box(ax, 9.2, 0.55, 3.7, 1.5, "ModuleNotFoundError:\nNo module named\n'tensorflow'", "#FEE2E2", RED, size=14, family=MONO)
    arrow(ax, 8.2, 4.3, 9.2, 4.3, GREEN); arrow(ax, 8.2, 1.3, 9.2, 1.3, AMBER)
    ax.text(6.1, 2.8, "Which Python answers depends on what is active", ha="center", fontsize=15,
            color=MUTED, style="italic")
    save(fig, "which_python")


# 2. The folder you are in decides which files Python can find
def folders():
    fig, ax = plt.subplots(figsize=(12.5, 5.6))
    ax.set_xlim(0, 12.5); ax.set_ylim(0, 5.8); ax.axis("off")
    tree = ["cats_dogs/                <- open in Antigravity",
            "    .venv/                <- project's Python",
            "    Image_classifier.py   <- the script",
            "    images/               <- photos to sort",
            "        cats/",
            "        dogs/",
            "        photo_1.jpg",
            "        photo_2.jpg"]
    box(ax, 0.1, 0.2, 7.3, 5.4, "", "#F8FAFC", MUTED)
    for i, line in enumerate(tree):
        ax.text(0.45, 5.05 - i * 0.6, line, fontsize=13, family=MONO, color=INK, va="center")
    box(ax, 7.75, 3.1, 4.7, 2.3, "Terminal in cats_dogs/\n$ python Image_classifier.py\nfinds  images/", "#DCFCE7", GREEN, size=13, family=MONO)
    box(ax, 7.75, 0.3, 4.7, 2.3, "Terminal in Downloads/\n$ python Image_classifier.py\nFileNotFoundError", "#FEE2E2", RED, size=13, family=MONO)
    ax.text(10.1, 2.85, "check with:  pwd  (Windows: cd)", ha="center", fontsize=14, family=MONO, color=MUTED)
    save(fig, "folders")


# 3. How to read a traceback: start at the last line
def traceback():
    lines = [("Traceback (most recent call last):", MUTED, "normal"),
             ('  File "/Users/mina/cats_dogs/Image_classifier.py", line 75, in <module>', BLUE, "bold"),
             ("    for filename in os.listdir(input_folder):", INK, "normal"),
             ("                    ^^^^^^^^^^^^^^^^^^^^^^^^", MUTED, "normal"),
             ("FileNotFoundError: [Errno 2] No such file or directory: 'images'", RED, "bold")]
    fig, ax = plt.subplots(figsize=(13, 5.2))
    ax.set_xlim(0, 13); ax.set_ylim(0, 5.4); ax.axis("off")
    ax.add_patch(FancyBboxPatch((0.1, 2.35), 12.8, 2.85, boxstyle="round,pad=0.02,rounding_size=0.08", fc="#18181B", ec="none"))
    colors = {MUTED: "#A1A1AA", BLUE: "#93C5FD", INK: "#E5E7EB", RED: "#FCA5A5"}
    for i, (t, c, w) in enumerate(lines):
        ax.text(0.35, 4.85 - i * 0.55, t, fontsize=13.5, family=MONO, color=colors[c], weight=w, va="center")
    notes = [("1. Read the LAST line first", "the error type and what went wrong:\nthe folder 'images' was not found", RED, 0.15),
             ("2. Then find YOUR file and line", "Image_classifier.py, line 75:\nthe line that failed", BLUE, 4.45),
             ("3. Ask: what did Python expect?", "a folder named images/ inside the\nfolder the Terminal is in", GREEN, 8.75)]
    for head, body, c, x in notes:
        box(ax, x, 0.1, 4.1, 1.95, "", "#FFFFFF", c)
        ax.text(x + 2.05, 1.65, head, ha="center", va="center", fontsize=15.5, weight="bold", color=c)
        ax.text(x + 2.05, 0.8, body, ha="center", va="center", fontsize=14, color=INK, linespacing=1.3)
    save(fig, "traceback")


if __name__ == "__main__":
    which_python(); folders(); traceback()
    print("Wrote", len(list(OUT.glob("setup_clinic_fig_*.png"))), "figures to assets/")
