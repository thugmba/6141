#!/usr/bin/env python3
"""Draw the good and bad screenshot examples of the Python Setup Clinic.

The bad example is a whole 1920 x 1080 screen with the editor's normal small text;
the good example is only the Terminal, with the text zoomed in. Both are shown at the
same page width, which is how they look once pasted into the Word template.
Writes assets/setup_clinic_fig_screenshots.png.
Usage: python3 scripts/make_setup_clinic_screenshots.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SERIF = str(Path.home() / ".local/share/fonts/times.ttf")
SERIF_BOLD = str(Path.home() / ".local/share/fonts/timesbd.ttf")

TERMINAL = [
    ("mina@MacBook practice % python3 hello.py", "#E5E7EB"),
    ("Hello! This is Python 3.13.17", "#E5E7EB"),
    ("This Python lives at: /Library/Frameworks/Python.framework/Versions/3.13/bin/python3", "#E5E7EB"),
    ("mina@MacBook practice % echo $?", "#E5E7EB"),
    ("0", "#E5E7EB"),
    ("mina@MacBook practice % ", "#E5E7EB"),
]
CODE = ["import sys", "", 'print("Hello! This is Python", sys.version.split()[0])',
        'print("This Python lives at:", sys.executable)']


def whole_screen():
    """A full desktop with an IDE window: what a whole-screen capture contains."""
    w, h = 1920, 1080
    img = Image.new("RGB", (w, h), "#2B3A55")
    d = ImageDraw.Draw(img)
    small = ImageFont.truetype(SANS, 13)
    mono = ImageFont.truetype(MONO, 13)
    d.rectangle([0, 0, w, 26], fill="#E5E7EB")                      # the system menu bar
    d.text((14, 6), "Antigravity   File   Edit   View   Terminal   Help", font=small, fill="#111827")
    d.rectangle([0, 1040, w, h], fill="#1F2937")                     # the dock / taskbar
    for i in range(12):
        d.rounded_rectangle([700 + i * 44, 1046, 736 + i * 44, 1076], 6, fill=["#60A5FA", "#F59E0B", "#34D399", "#F472B6"][i % 4])
    x0, y0, x1, y1 = 40, 50, 1880, 1020                              # the IDE window
    d.rectangle([x0, y0, x1, y1], fill="#1E1E1E")
    d.rectangle([x0, y0, x1, y0 + 30], fill="#323233")
    d.text((x0 + 760, y0 + 8), "practice - Google Antigravity", font=small, fill="#CCCCCC")
    d.rectangle([x0, y0 + 30, x0 + 48, y1], fill="#333333")          # activity bar
    d.rectangle([x0 + 48, y0 + 30, x0 + 300, y1], fill="#252526")    # [1] File Explorer
    for i, name in enumerate(["PRACTICE", "  .venv", "  images", "  bugs.py", "  check_packages.py", "  hello.py", "  list_images.py"]):
        d.text((x0 + 60, y0 + 44 + i * 22), name, font=small, fill="#CCCCCC")
    d.rectangle([x1 - 420, y0 + 30, x1, y1], fill="#252526")         # [3] AI Agent Chat
    d.text((x1 - 400, y0 + 44), "AGENT", font=small, fill="#CCCCCC")
    for i in range(6):
        d.rounded_rectangle([x1 - 400, y0 + 80 + i * 70, x1 - 20, y0 + 135 + i * 70], 6, fill="#2D2D30")
    d.text((x0 + 320, y0 + 40), "hello.py", font=small, fill="#FFFFFF")  # [2] Code Editor
    for i, line in enumerate(CODE):
        d.text((x0 + 320, y0 + 74 + i * 20), f"{i + 1:>3}  {line}", font=mono, fill="#D4D4D4")
    ty = y1 - 230                                                    # [4] Terminal
    d.line([x0 + 300, ty, x1 - 420, ty], fill="#3C3C3C", width=1)
    d.text((x0 + 320, ty + 8), "TERMINAL", font=small, fill="#FFFFFF")
    for i, (line, color) in enumerate(TERMINAL):
        d.text((x0 + 320, ty + 36 + i * 18), line, font=mono, fill=color)
    return img


def terminal_only():
    """Only the Terminal, after zooming the editor in: what a good capture contains."""
    size = 34
    mono = ImageFont.truetype(MONO, size)
    line_h = int(size * 1.45)
    w = 1820
    h = 70 + line_h * len(TERMINAL) + 30
    img = Image.new("RGB", (w, h), "#1E1E1E")
    d = ImageDraw.Draw(img)
    d.text((28, 18), "TERMINAL", font=ImageFont.truetype(SANS, 26), fill="#FFFFFF")
    for i, (line, color) in enumerate(TERMINAL):
        d.text((28, 70 + i * line_h), line, font=mono, fill=color)
    return img


def compose():
    width = 1820
    bad = whole_screen().resize((width, round(1080 * width / 1920)), Image.LANCZOS)
    good = terminal_only()
    head = ImageFont.truetype(SERIF_BOLD, 46)
    body = ImageFont.truetype(SERIF, 36)
    blocks = [
        ("#991B1B", "Not readable: the whole screen", "The text is too small to read once the picture fits the page.", bad),
        ("#16A34A", "Readable: only the Terminal, with the text zoomed in", "Every command and every line of output can be read.", good),
    ]
    pad, gap = 30, 50
    total_h = sum(60 + 50 + b[3].height + 2 * 8 for b in blocks) + gap * (len(blocks) - 1) + 2 * pad
    out = Image.new("RGB", (width + 2 * pad + 16, total_h), "white")
    d = ImageDraw.Draw(out)
    y = pad
    for color, title, note, pic in blocks:
        mark = "X" if color == "#991B1B" else "OK"
        d.rounded_rectangle([pad, y, pad + 70, y + 52], 10, fill=color)
        d.text((pad + 35, y + 26), mark, font=ImageFont.truetype(SANS, 30), fill="white", anchor="mm")
        d.text((pad + 90, y + 2), title, font=head, fill=color)
        d.text((pad + 90, y + 60), note, font=body, fill="#374151")
        y += 110
        d.rectangle([pad, y, pad + pic.width + 16, y + pic.height + 16], outline=color, width=8)
        out.paste(pic, (pad + 8, y + 8))
        y += pic.height + 16 + gap
    out.save(ROOT / "assets" / "setup_clinic_fig_screenshots.png", dpi=(200, 200))
    print("Wrote assets/setup_clinic_fig_screenshots.png", out.size)


if __name__ == "__main__":
    compose()
