"""Pizzaratti standing menu panel — print file.

Same panel system as jan_burger.py (600 x 2000 mm trim, 5 mm bleed, vector
text and logo, side-by-side meal cards). White page, Pizzaratti green header
with the logo reversed out, checkered-tablecloth bands, cut-out pizzas.
The logo is drawn straight from the brand's vector PDF.
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
from jan_burger import Arabic, H, W, X, Y, calorie_notice, meal_card, rgb, runs

HERE = base.HERE
OUT = os.path.join(HERE, "out", "pizzaratti-menu-600x2000mm.pdf")
PIZZAS = [
    # (English, Arabic, price, kcal, photo) — from the Food World e-menu
    ("Ranch Chicken Pizza", "رانش تشيكن بيتزا", "41", "1,585", "pizzaratti-ranch-chicken.jpg"),
    ("Pizzaratti Pizza", "بيتزا بيتزاراتي", "41", "1,221", "pizzaratti-pizzaratti.jpg"),
    ("Margherita Pizza", "بيتزا مارغريتا", "39", "1,368", "pizzaratti-margherita.jpg"),
    ("Super Mix Pizza", "سوبر ميكس", "46", "1,480", "pizzaratti-super-mix.jpg"),
]

# Pizzaratti green identity (from the brand's vector logo, #2E5637)
WHITE = rgb("#FFFFFF")
GREEN = rgb("#2E5637")
GREEN_DK = rgb("#1F3D26")
INK = rgb("#1E2B21")
RULE = rgb("#CFDDD2")
LOGO_PDF = os.path.join(base.ASSETS, "pizzaratti-logo-green.pdf")
PAGE_RGB = (255, 255, 255)

# The shared card and notice helpers read these module globals.
base.CREAM_LT, base.MAROON, base.ORANGE, base.INK, base.RULE = WHITE, GREEN, GREEN, INK, RULE


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
    c.setFillColor(GREEN)
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
    scallop_block(c, 31, 300, GREEN)
    c.setFillColor(GREEN_DK)
    c.rect(0, Y(37), W, 6 * mm, stroke=0, fill=1)
    draw_pdf_logo(c, LOGO_PDF, cx, Y(170), 380 * mm, WHITE)

    # Section title: PIZZA | بيتزا
    y_t = 420
    runs(c, [("PIZZA", "Oswald-Bold", 140, GREEN), ("   ", "Oswald-Bold", 140, GREEN),
             (Arabic("بيتزا", "Cairo-Bold", 120), GREEN)], cx, Y(y_t))
    c.setStrokeColor(GREEN)
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
    scallop_block(c, 1880, 1975, GREEN, down=False, depth=14)
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


def draw_pdf_logo(c, path, cx, cy, width, color):
    """Redraw the vector shapes of a one-page logo PDF, centred at cx, cy, in one colour."""
    import pymupdf
    drawings = pymupdf.open(path)[0].get_drawings()
    box = pymupdf.Rect()
    for d in drawings:
        box |= d["rect"]
    k = width / box.width

    def pt(q):  # PDF page space (y down) -> canvas
        return cx + (q.x - box.x0 - box.width / 2) * k, cy - (q.y - box.y0 - box.height / 2) * k

    c.setFillColor(color)
    for d in drawings:
        p, cur = c.beginPath(), None
        for it in d["items"]:
            start = pt(it[1])
            if cur is None or abs(start[0] - cur[0]) > 1e-3 or abs(start[1] - cur[1]) > 1e-3:
                if cur is not None:
                    p.close()
                p.moveTo(*start)
            if it[0] == "l":
                cur = pt(it[2])
                p.lineTo(*cur)
            elif it[0] == "c":
                cur = pt(it[4])
                p.curveTo(*pt(it[2]), *pt(it[3]), *cur)
        p.close()
        c.drawPath(p, stroke=0, fill=1, fillMode=0 if d.get("even_odd") else 1)
    return box.height * k


if __name__ == "__main__":
    build()
