"""Mark Burger standing menu panel — ALTERNATIVE brand-DNA design (not the chosen one).

Same panel system as jan_burger.py (600 x 2000 mm trim, 5 mm bleed, vector
text and logo), styled on the Mark brand DNA: checkerboard bands, big lowercase
blue/white + orange type, cut-out food and thin line art.
Two page themes: white (main) and blue (alternative).
Edit BURGERS below and re-run:  python3 menus/mark_burger_dna.py
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

import jan_burger as base
from jan_burger import Arabic, H, W, X, Y, calorie_notice, draw_logo, rgb, runs

HERE = base.HERE
OUTS = {"white": os.path.join(HERE, "out", "mark-burger-dna-white-600x2000mm.pdf"),
        "blue": os.path.join(HERE, "out", "mark-burger-dna-blue-600x2000mm.pdf")}
CURRENCY = "SAR"
BURGERS = [
    # (headline word 1, headline word 2 (orange), Arabic, price, kcal, photo) — Food World e-menu
    ("mark", "double", "مارك دبل سماش برجر", "42", "410", "mark-double-smash.jpg"),
    ("mark", "triple", "مارك تربل سماش برجر", "48", "488", "mark-triple-smash.jpg"),
]

# Mark brand DNA (sampled from the supplied artwork)
BLUE = rgb("#1A4589")
BLUE_DK = rgb("#193C74")
CHECK = rgb("#4B7DB8")
ORANGE = rgb("#EC6B3A")
WHITE = rgb("#FFFFFF")
INK = rgb("#14294A")
RULE = rgb("#C9D3E3")

# Per-theme colours: page, main text / line art, drop shadow (RGB, alpha)
THEMES = {
    "white": dict(page=WHITE, fg=BLUE, shadow=((20, 40, 80), 80)),
    "blue": dict(page=BLUE, fg=WHITE, shadow=((11, 30, 62), 150)),
}
T = THEMES["white"]

pdfmetrics.registerFont(TTFont("Montserrat-ExtraBold", os.path.join(HERE, "fonts", "Montserrat-ExtraBold.ttf")))
HEAD = "Montserrat-ExtraBold"

# The shared calorie notice reads these module globals: white box, blue text.
base.LOGO = os.path.join(base.ASSETS, "mark-logo-white.json")
base.CREAM_LT, base.MAROON, base.ORANGE, base.INK, base.RULE = WHITE, BLUE, ORANGE, INK, RULE


def checker(c, y_top, rows=2, size=16):
    """Checkerboard band across the full bleed width (brand pattern)."""
    c.setFillColor(BLUE_DK)
    c.rect(0, Y(y_top + rows * size), W, rows * size * mm, stroke=0, fill=1)
    c.setFillColor(CHECK)
    for r in range(rows):
        for k in range(-1, int(610 / size) + 2):
            if (k + r) % 2 == 0:
                c.rect(X(k * size), Y(y_top + (r + 1) * size), size * mm, size * mm, stroke=0, fill=1)


def cutout(fname):
    """Remove the grey studio backdrop and add a soft drop shadow."""
    im = Image.open(os.path.join(base.ASSETS, fname)).convert("RGB")
    a = np.asarray(im, dtype=float)
    bg_l = np.median(a[:20, :20].mean(axis=2))
    sat = a.max(axis=2) - a.min(axis=2)
    lum = a.mean(axis=2)
    # Backdrop and its shadow are neutral grey; flood from the border so
    # neutral pixels inside the burger (onion, dark crust) stay.
    cand = (sat < 16) & (lum > 140) & (lum < bg_l + 12)
    m = Image.fromarray((cand * 255).astype(np.uint8)).copy()   # writable copy for floodfill
    for p in [(0, 0), (m.width - 1, 0), (0, m.height - 1), (m.width - 1, m.height - 1)]:
        ImageDraw.floodfill(m, p, 128)
    fg = Image.fromarray(((np.asarray(m) != 128) * 255).astype(np.uint8))
    fg = fg.filter(ImageFilter.MinFilter(5)).filter(ImageFilter.GaussianBlur(1.5))
    box = fg.point(lambda v: 255 if v > 128 else 0).getbbox()
    pad = 40
    l, t, r, b = box
    sh_h = int((r - l) * 0.10)                      # room for the shadow below
    out = Image.new("RGBA", (r - l + 2 * pad, b - t + 2 * pad + sh_h), (*T["shadow"][0], 0))
    sh = Image.new("L", out.size, 0)
    ImageDraw.Draw(sh).ellipse((pad + (r - l) * 0.12, b - t + pad - sh_h * 0.6,
                                pad + (r - l) * 0.88, b - t + pad + sh_h * 0.7), fill=T["shadow"][1])
    out.putalpha(sh.filter(ImageFilter.GaussianBlur(sh_h * 0.45)))
    food = im.crop(box).convert("RGBA")
    food.putalpha(fg.crop(box))
    out.alpha_composite(food, (pad, pad))
    return ImageReader(out), out.width / out.height


def line_art(c, cx, cy, r, flip):
    """Thin '6'-style stroke from the brand artwork."""
    c.setStrokeColor(T["fg"])
    c.setLineWidth(2.2 * mm)
    c.setLineCap(1)
    c.circle(X(cx), Y(cy), r * mm, stroke=1, fill=0)
    s = -1 if flip else 1
    p = c.beginPath()
    p.moveTo(X(cx - s * r), Y(cy))
    p.curveTo(X(cx - s * r), Y(cy - r * 1.1), X(cx + s * r * 0.1), Y(cy - r * 1.5), X(cx + s * r * 1.1), Y(cy - r * 1.45))
    c.drawPath(p, stroke=1, fill=0)


def burger_card(c, item, top, height, left):
    w1, w2, ar_name, price, kcal, photo = item
    bottom = top + height

    # Line art behind everything, on the side away from the headline
    line_art(c, 455 if left else 145, top + 150, 80, flip=not left)

    # Big lowercase headline: first word in the theme colour, second in orange
    size = 330
    for word, color, base_y in ((w1, T["fg"], top + 112), (w2, ORANGE, top + 222)):
        c.setFillColor(color)
        c.setFont(HEAD, size)
        if left:
            c.drawString(X(32), Y(base_y), word)
        else:
            c.drawRightString(X(568), Y(base_y), word)

    # Cut-out burger overlapping the headline
    img, ratio = cutout(photo)
    w = 490 * mm
    h = w / ratio
    c.drawImage(img, X(300) - w / 2 + (12 if left else -12) * mm, Y(top + 160) - h, w, h, mask="auto")

    # Arabic name, then price pill + calories
    cx = X(300)
    runs(c, [(Arabic(ar_name, "Cairo-ExtraBold", 72).fit(520 * mm), T["fg"])], cx, Y(bottom - 92))
    y = bottom - 70
    pw = (pdfmetrics.stringWidth(price, HEAD, 130)
          + pdfmetrics.stringWidth(" " + CURRENCY, HEAD, 48) + 50 * mm)
    ar_k = Arabic("سعرة حرارية", "Cairo-Bold", 42)
    kw = max(pdfmetrics.stringWidth(kcal + " kcal", HEAD, 52), ar_k.width)
    gap = 35 * mm
    x0 = cx - (pw + gap + kw) / 2
    c.setFillColor(ORANGE)
    c.roundRect(x0, Y(y + 58), pw, 58 * mm, 29 * mm, stroke=0, fill=1)
    runs(c, [(price, HEAD, 130, WHITE), (" " + CURRENCY, HEAD, 48, WHITE)], x0 + pw / 2, Y(y + 45))
    kx = x0 + pw + gap + kw / 2
    runs(c, [(kcal + " kcal", HEAD, 52, T["fg"])], kx, Y(y + 27))
    runs(c, [(ar_k, T["fg"])], kx, Y(y + 49))


def build(theme):
    global T
    T = THEMES[theme]
    OUT = OUTS[theme]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    c = canvas.Canvas(OUT, pagesize=(W, H))
    c.setTitle("Mark Burger — Menu Panel 600x2000mm")
    c.setAuthor("Rakhy Group Food Court")
    cx = X(300)

    c.setFillColor(T["page"])
    c.rect(0, 0, W, H, stroke=0, fill=1)
    checker(c, -5, rows=3)

    # Logo: white lettering (on a blue disc on the white page), thin ring
    if theme == "white":
        c.setFillColor(BLUE)
        c.circle(cx, Y(215), 158 * mm, stroke=0, fill=1)
    draw_logo(c, cx, Y(215), 300 * mm)
    c.setStrokeColor(T["fg"])
    c.setLineWidth(2.2 * mm)
    c.circle(cx, Y(215), 168 * mm, stroke=1, fill=0)

    # Section title: burgers | البرجر
    y_t = 470
    runs(c, [("burgers", HEAD, 150, T["fg"]), ("   ", HEAD, 150, T["fg"]),
             (Arabic("البرجر", "Cairo-ExtraBold", 130), ORANGE)], cx, Y(y_t))

    top, bottom = 500, 1765
    ch = (bottom - top) / len(BURGERS)
    for i, item in enumerate(BURGERS):
        t = top + i * ch
        if i:
            c.setStrokeColor(CHECK)
            c.setLineWidth(1.6 * mm)
            c.setDash(0.1, 5 * mm)
            c.line(X(60), Y(t), X(540), Y(t))
            c.setDash()
        burger_card(c, item, t, ch, left=(i % 2 == 0))

    calorie_notice(c, 1775, 1856)

    # Footer: VAT note + checkerboard
    runs(c, [("PRICES INCLUDE VAT", HEAD, 52, T["fg"]), ("   |   ", HEAD, 52, ORANGE),
             (Arabic("الأسعار شاملة ضريبة القيمة المضافة", "Cairo-Bold", 54).fit(290 * mm), T["fg"])],
         cx, Y(1905))
    checker(c, 1957, rows=3)

    c.showPage()
    c.save()

    import pymupdf
    doc = pymupdf.open(OUT)
    pg = doc[0]
    doc.xref_set_key(pg.xref, "TrimBox", f"[{base.BLEED} {base.BLEED} {W - base.BLEED} {H - base.BLEED}]")
    doc.xref_set_key(pg.xref, "BleedBox", f"[0 0 {W} {H}]")
    doc.saveIncr()
    doc.close()
    print("wrote", OUT)


if __name__ == "__main__":
    for theme in THEMES:
        build(theme)
