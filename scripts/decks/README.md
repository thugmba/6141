# Hand-built lecture decks (Sessions 3.1 to 4.4)

Each `build_deck_MM_SS.py` writes `slides_src/session_MM_SS.html` (16 slides) from the
code blocks and outputs in `6141.md`, the figures in `assets/session_MM_SS_fig_*.png`,
and `deck_template.html` (shared styles and the text-fitting script).

Rebuild one deck:

```text
python3 scripts/make_session_03_03_figures.py        # only if the data or figures changed
python3 scripts/decks/build_deck_03_03.py
node scripts/render_with_playwright.js 03_03        # PDF and PNG previews
```

Do not rebuild these sessions with `scripts/build_deck_from_md.py`: it would replace the
hand-built decks with generic ones.
