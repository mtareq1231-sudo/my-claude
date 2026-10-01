"""Pizzaratti standing menu panel — print file.

Same panel system as jan_burger.py (600 x 2000 mm trim, 5 mm bleed, vector
text and logo, side-by-side meal cards). White page, Pizzaratti red header
with the logo reversed out, checkered-tablecloth bands, cut-out pizzas.
Edit PIZZAS below and re-run:  python3 menus/pizzaratti.py
"""
import io
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from scipy import ndimage as ndi

import jan_burger as base
from jan_burger import Arabic, H, W, X, Y, calorie_notice, draw_logo, meal_card, rgb, runs

HERE = base.HERE
OUT = os.path.join(HERE, "out", "pizzaratti-menu-600x2000mm.pdf")
PIZZAS = [
    # (English, Arabic, price, kcal, photo) — from the Food World e-menu
    ("Ranch Chicken Pizza", "رانش تشيكن بيتزا", "41", "1,585", "pizzaratti-ranch-chicken.jpg"),
    ("Pizzaratti Pizza", "بيتزا بيتزاراتي", "41", "1,221", "pizzaratti-pizzaratti.jpg"),
    ("Margherita Pizza", "بيتزا مارغريتا", "39", "1,368", "pizzaratti-margherita.jpg"),
    ("Super Mix Pizza", "سوبر ميكس", "46", "1,480", "pizzaratti-super-mix.jpg"),
]

# Pizzaratti palette (red sampled from the supplied logo)
WHITE = rgb("#FFFFFF")
RED = rgb("#EC3701")
RED_DK = rgb("#B92B00")
INK = rgb("#2B1A12")
RULE = rgb("#F3CDBE")
PAGE_RGB = (255, 255, 255)

# The shared card and notice helpers read these module globals.
base.LOGO = os.path.join(base.ASSETS, "pizzaratti-logo.json")
base.CREAM_LT, base.MAROON, base.ORANGE, base.INK, base.RULE = WHITE, RED, RED, INK, RULE


def pizza_photo(fname, pad_frac=0.04):
    """Cut the pizza out of its styled shoot (props dropped), soft shadow, on white."""
    im = Image.open(os.path.join(base.ASSETS, fname)).convert("RGB")
    a = np.asarray(im, dtype=float)
    # Pizza = largest saturated blob; the grey concrete backdrop is neutral.
    m = ndi.binary_opening(a.max(axis=2) - a.min(axis=2) > 38, iterations=3)
    m = ndi.binary_closing(m, iterations=12)
    lab, n = ndi.label(m)
    m = ndi.binary_fill_holes(lab == (np.argmax(ndi.sum(m, lab, range(1, n + 1))) + 1))
    alpha = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(4))
    alpha = alpha.point(lambda v: 0 if v < 110 else (255 if v > 150 else (v - 110) * 255 // 40))
    l, t, r, b = alpha.getbbox()
    pad = int(pad_frac * (r - l))
    sh = int((r - l) * 0.05)
    box = (l - pad, t - pad, r + pad, b + pad + sh)
    canvas_im = Image.new("RGB", (box[2] - box[0], box[3] - box[1]), PAGE_RGB)
    shadow = Image.new("L", canvas_im.size, 0)
    ImageDraw.Draw(shadow).ellipse((pad + (r - l) * 0.04, pad + sh * 1.2, r - l + pad - (r - l) * 0.04,
                                    b - t + pad + sh), fill=110)
    shadow = shadow.filter(ImageFilter.GaussianBlur(sh))
    canvas_im.paste(Image.new("RGB", canvas_im.size, (60, 40, 30)), (0, 0), shadow)
    canvas_im.paste(im.crop(box), (0, 0), alpha.crop(box))
    canvas_im = canvas_im.resize((canvas_im.width * 2, canvas_im.height * 2), Image.LANCZOS)
    buf = io.BytesIO()                       # JPEG keeps the print file small
    canvas_im.save(buf, "JPEG", quality=92, subsampling=0)
    buf.seek(0)
    return ImageReader(buf), canvas_im.width / canvas_im.height


base.product_photo = pizza_photo


def checker(c, y_top, rows=2, size=18):
    """Red / white tablecloth check across the full bleed width."""
    c.setFillColor(WHITE)
    c.rect(0, Y(y_top + rows * size), W, rows * size * mm, stroke=0, fill=1)
    c.setFillColor(RED)
    for r in range(rows):
        for k in range(-1, int(610 / size) + 2):
            if (k + r) % 2 == 0:
                c.rect(X(k * size), Y(y_top + (r + 1) * size), size * mm, size * mm, stroke=0, fill=1)


def scallop_block(c, y_top, y_bottom, color, bumps=8, depth=22, down=True):
    """Full-width block whose free edge is a row of round scallops (pizza-crust edge)."""
    c.setFillColor(color)
    edge = y_bottom if down else y_top
    p = c.beginPath()
    if down:
        p.moveTo(0, Y(y_top)); p.lineTo(W, Y(y_top)); p.lineTo(W, Y(edge))
    else:
        p.moveTo(0, Y(y_bottom)); p.lineTo(W, Y(y_bottom)); p.lineTo(W, Y(edge))
    step = 610 / bumps
    s = 1 if down else -1
    for i in range(bumps):
        x1 = 605 - i * step
        x0 = x1 - step
        p.curveTo(X(x1 - step * 0.05), Y(edge + s * depth * 1.3), X(x0 + step * 0.05), Y(edge + s * depth * 1.3),
                  X(x0), Y(edge))
    p.close()
    c.drawPath(p, stroke=0, fill=1)


def build():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    c = canvas.Canvas(OUT, pagesize=(W, H))
    c.setTitle("Pizzaratti — Menu Panel 600x2000mm")
    c.setAuthor("Rakhy Group Food Court")
    cx = X(300)

    c.setFillColor(WHITE)
    c.rect(0, 0, W, H, stroke=0, fill=1)

    # Header: tablecloth check, red block with a scalloped crust edge, white logo
    checker(c, -5, rows=2)
    scallop_block(c, 31, 300, RED)
    c.setFillColor(RED_DK)
    c.rect(0, Y(37), W, 6 * mm, stroke=0, fill=1)
    draw_white_logo(c, cx, Y(170), 380 * mm)

    # Section title: PIZZA | بيتزا
    y_t = 420
    runs(c, [("PIZZA", "Oswald-Bold", 140, RED), ("   ", "Oswald-Bold", 140, RED),
             (Arabic("بيتزا", "Cairo-Bold", 120), RED)], cx, Y(y_t))
    c.setStrokeColor(RED)
    c.setLineWidth(2.2 * mm)
    c.setLineCap(1)
    c.line(X(40), Y(y_t - 18), X(140), Y(y_t - 18))
    c.line(X(460), Y(y_t - 18), X(560), Y(y_t - 18))

    top, bottom = 445, 1765
    ch = (bottom - top) / len(PIZZAS)
    for i, pizza in enumerate(PIZZAS):
        t = top + i * ch
        if i:
            c.setStrokeColor(RULE)
            c.setLineWidth(1.6 * mm)
            c.setDash(0.1, 5 * mm)
            c.line(X(60), Y(t), X(540), Y(t))
            c.setDash()
        meal_card(c, pizza, t, ch, photo_left=(i % 2 == 0))

    calorie_notice(c, 1775, 1856)

    # Footer: red block with scalloped top edge, VAT note, tablecloth check
    scallop_block(c, 1880, 1975, RED, down=False, depth=14)
    runs(c, [("PRICES INCLUDE VAT", "Oswald-Medium", 60, WHITE), ("   |   ", "Oswald-Medium", 60, WHITE),
             (Arabic("الأسعار شاملة ضريبة القيمة المضافة", "Cairo-Bold", 54).fit(300 * mm), WHITE)],
         cx, Y(1937))
    checker(c, 1969, rows=2, size=18)

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


def draw_white_logo(c, cx, cy, width):
    """The supplied logo is red-on-white; reverse it to white on the red header."""
    import json
    data = json.load(open(base.LOGO))
    for layer in data["layers"]:
        layer["color"] = "#FFFFFF"
    tmp = base.LOGO + ".white.tmp"
    json.dump(data, open(tmp, "w"))
    keep, base.LOGO = base.LOGO, tmp
    try:
        draw_logo(c, cx, cy, width)
    finally:
        base.LOGO = keep
        os.remove(tmp)


if __name__ == "__main__":
    build()
