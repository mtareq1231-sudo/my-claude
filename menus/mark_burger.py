"""Mark Burger standing menu panel — print file.

Same panel system as jan_burger.py (600 x 2000 mm trim, 5 mm bleed, vector
text and logo); this file only swaps in the Mark brand and its items.
With two burgers each card stacks a large photo over the text.
Edit BURGERS below and re-run:  python3 menus/mark_burger.py
"""
import os

from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas

import jan_burger as base
from jan_burger import (Arabic, H, W, X, Y, calorie_notice, draw_logo, product_photo, rgb,
                        runs, spaced, stripes, wrap)

HERE = base.HERE
OUT = os.path.join(HERE, "out", "mark-burger-menu-600x2000mm.pdf")
CURRENCY = "SAR"
BURGERS = [
    # (English, Arabic, price, kcal, photo) — from the Food World e-menu
    ("Mark Double Smash Burger", "مارك دبل سماش برجر", "42", "410", "mark-double-smash.jpg"),
    ("Mark Triple Smash Burger", "مارك تربل سماش برجر", "48", "488", "mark-triple-smash.jpg"),
]

# Mark brand palette (blue sampled from the supplied logo, yellow from the cheese)
PAGE = rgb("#F2F4F8")
WHITE = rgb("#FFFFFF")
BLUE = rgb("#194689")
BLUE_DK = rgb("#11335F")
YELLOW = rgb("#FFC20E")
INK = rgb("#14294A")
RULE = rgb("#C9D3E3")

# The shared helpers (photos, logo, calorie notice) read these module globals.
base.PAGE_RGB = (242, 244, 248)
base.LOGO = os.path.join(base.ASSETS, "mark-logo.json")
base.CREAM_LT, base.MAROON, base.ORANGE, base.INK, base.RULE = WHITE, BLUE, BLUE, INK, RULE


def burger_card(c, item, top, height):
    """Large photo on top, name / price / calories centred below it."""
    en, ar_name, price, kcal, photo = item
    cx = X(300)
    bottom = top + height

    img, ratio = product_photo(photo, 0.04)
    box_h = height - 205
    w = 560 * mm
    h = min(w / ratio, box_h * mm)
    w = h * ratio
    c.drawImage(img, cx - w / 2, Y(top + 8 + box_h / 2) - h / 2, w, h)

    y = bottom - 163
    for ln in wrap(en.upper(), "Oswald-Bold", 88, 540 * mm):
        c.setFillColor(BLUE)
        spaced(c, ln, "Oswald-Bold", 88, cx, Y(y), 1.5)
        y += 31
    runs(c, [(Arabic(ar_name, "Cairo-Bold", 66).fit(520 * mm), INK)], cx, Y(y + 5))

    # Price pill and calories side by side
    y = bottom - 92
    pw = (pdfmetrics.stringWidth(price, "Oswald-Bold", 150)
          + pdfmetrics.stringWidth(" " + CURRENCY, "Oswald-Medium", 54) + 50 * mm)
    ar_k = Arabic("سعرة حرارية", "Cairo-Medium", 42)
    kw = max(pdfmetrics.stringWidth(kcal + " kcal", "Montserrat-Bold", 52), ar_k.width)
    gap = 35 * mm
    x0 = cx - (pw + gap + kw) / 2
    c.setFillColor(YELLOW)
    c.roundRect(x0, Y(y + 62), pw, 62 * mm, 31 * mm, stroke=0, fill=1)
    runs(c, [(price, "Oswald-Bold", 150, BLUE), (" " + CURRENCY, "Oswald-Medium", 54, BLUE)],
         x0 + pw / 2, Y(y + 50))
    kx = x0 + pw + gap + kw / 2
    runs(c, [(kcal + " kcal", "Montserrat-Bold", 52, INK)], kx, Y(y + 29))
    runs(c, [(ar_k, INK)], kx, Y(y + 51))


def build():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    c = canvas.Canvas(OUT, pagesize=(W, H))
    c.setTitle("Mark Burger — Menu Panel 600x2000mm")
    c.setAuthor("Rakhy Group Food Court")
    cx = X(300)

    c.setFillColor(PAGE)
    c.rect(0, 0, W, H, stroke=0, fill=1)

    # Header: blue block with a bun-shaped bottom edge, stripes on top
    c.setFillColor(BLUE)
    p = c.beginPath()
    p.moveTo(0, H); p.lineTo(W, H); p.lineTo(W, Y(290))
    p.curveTo(X(470), Y(380), X(130), Y(380), 0, Y(290))
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    stripes(c, -5, 70, BLUE_DK)
    c.setFillColor(YELLOW)
    c.rect(0, Y(73), W, 8 * mm, stroke=0, fill=1)

    # Round logo on a white disc with a yellow ring, sitting on the header edge
    c.setFillColor(YELLOW)
    c.circle(cx, Y(270), 186 * mm, stroke=0, fill=1)
    c.setFillColor(WHITE)
    c.circle(cx, Y(270), 178 * mm, stroke=0, fill=1)
    draw_logo(c, cx, Y(270), 340 * mm)

    # Section title: BURGERS | البرجر
    y_t = 545
    runs(c, [("BURGERS", "Oswald-Bold", 140, BLUE), ("   ", "Oswald-Bold", 140, BLUE),
             (Arabic("البرجر", "Cairo-Bold", 120), BLUE)], cx, Y(y_t))
    c.setStrokeColor(YELLOW)
    c.setLineWidth(2.2 * mm)
    c.setLineCap(1)
    c.line(X(30), Y(y_t - 18), X(95), Y(y_t - 18))
    c.line(X(505), Y(y_t - 18), X(570), Y(y_t - 18))

    top, bottom = 570, 1765
    ch = (bottom - top) / len(BURGERS)
    for i, item in enumerate(BURGERS):
        t = top + i * ch
        if i:
            c.setStrokeColor(RULE)
            c.setLineWidth(1.6 * mm)
            c.setDash(0.1, 5 * mm)
            c.line(X(60), Y(t), X(540), Y(t))
            c.setDash()
        burger_card(c, item, t, ch)

    calorie_notice(c, 1775, 1856)

    # Footer: stripes + VAT note
    c.setFillColor(BLUE)
    c.rect(0, 0, W, Y(1872), stroke=0, fill=1)
    stripes(c, 1945, 60, BLUE_DK)
    c.setFillColor(YELLOW)
    c.rect(0, Y(1880), W, 8 * mm, stroke=0, fill=1)
    runs(c, [("PRICES INCLUDE VAT", "Oswald-Medium", 60, WHITE), ("   |   ", "Oswald-Medium", 60, YELLOW),
             (Arabic("الأسعار شاملة ضريبة القيمة المضافة", "Cairo-Bold", 54).fit(300 * mm), WHITE)],
         cx, Y(1925))

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
    build()
