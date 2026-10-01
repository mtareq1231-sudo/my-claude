# Food court menu panels

Standing menu panels for the Rakhy Group food court. Each panel is 600 × 2000 mm
(plus 5 mm bleed) and exported as a print-ready PDF.

```bash
pip install reportlab pymupdf pillow numpy uharfbuzz fonttools potracer
python3 menus/jan_burger.py          # -> menus/out/jan-burger-menu-600x2000mm.pdf
```

- `assets/` — logos (traced to vector JSON with `vectorize_logo.py`) and product photos
- `fonts/` — Oswald, Montserrat, Cairo (SIL Open Font License)
- Arabic is shaped with HarfBuzz and drawn as vector outlines.
