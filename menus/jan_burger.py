"""Jan Burger standing menu panel — print file.

Trim size 600 x 2000 mm, 5 mm bleed on every side, vector text and vector logo.
Edit MEALS below and re-run:  python3 menus/jan_burger.py

Colours are RGB so the page background matches the product photos' backdrop
exactly; the printer's RIP converts the whole file to CMYK in one pass.
"""
import json
import os

import numpy as np
import uharfbuzz as hb
from fontTools.pens.basePen import BasePen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont as FTFont
from PIL import Image, ImageFilter
from reportlab.lib.colors import Color
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "jan-burger-menu-600x2000mm.pdf")
ASSETS = os.path.join(HERE, "assets")
LOGO = os.path.join(ASSETS, "jan-logo.json")                 # from vectorize_logo.py

TRIM_W, TRIM_H, BLEED = 600 * mm, 2000 * mm, 5 * mm
W, H = TRIM_W + 2 * BLEED, TRIM_H + 2 * BLEED

# From the Food World e-menu (foodworld.web.order.sa). Prices in SAR.
CURRENCY = "SAR"
MEALS = [
    # (English, Arabic, price, kcal, photo)
    ("Original Beef Meal", "وجبة اللحم الأصلي", "44", "1,151", "jan-original-beef.jpg"),
    ("Jan Fried Spicy Chicken Meal", "وجبة جان فرايد سبايسي تشيكن", "42", "999", "jan-fried-spicy-chicken.jpg"),
    ("Jan Crunchy Chicken Meal", "وجبة جان كرانشي تشيكن", "42", "1,069", "jan-crunchy-chicken.jpg"),
    ("Jan Chicken Meal", "وجبة جان تشيكن", "39", "881", "jan-chicken.jpg"),
]


def rgb(h):
    h = h.lstrip("#")
    return Color(*(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)))


# Jan brand palette (sampled from the supplied logo and photos)
CREAM = rgb("#FDF4E5")    # photo backdrop
CREAM_LT = rgb("#FFFAF4")  # logo disc
ORANGE = rgb("#F58020")
MAROON = rgb("#9B1C23")
MAROON_DK = rgb("#6E1218")
INK = rgb("#3B1F17")       # warm dark brown for body text
RULE = rgb("#E7C9A6")

for name in ["Oswald-Bold", "Oswald-Medium", "Montserrat-Medium", "Montserrat-Bold"]:
    pdfmetrics.registerFont(TTFont(name, os.path.join(HERE, "fonts", name + ".ttf")))


def X(v):  # trim-relative mm -> canvas pt
    return BLEED + v * mm


def Y(v):  # mm measured down from the top of the trim
    return BLEED + TRIM_H - v * mm


class CanvasPathPen(BasePen):
    """fontTools pen that writes into a ReportLab canvas path."""

    def __init__(self, glyphSet, path):
        super().__init__(glyphSet)
        self.path = path

    def _moveTo(self, p):
        self.path.moveTo(*p)

    def _lineTo(self, p):
        self.path.lineTo(*p)

    def _curveToOne(self, p1, p2, p3):
        self.path.curveTo(*p1, *p2, *p3)

    def _closePath(self):
        self.path.close()


class Arabic:
    """Arabic text shaped with HarfBuzz and drawn as vector glyph outlines.

    ReportLab can't apply Arabic joining forms itself, so shaping happens here
    and each glyph is drawn as a path (no font embedding needed).
    """

    def __init__(self, text, font, size):
        path = os.path.join(HERE, "fonts", font + ".ttf")
        self.ft = FTFont(path)
        self.upem = self.ft["head"].unitsPerEm
        hbf = hb.Font(hb.Face(hb.Blob.from_file_path(path)))
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(hbf, buf)
        self.glyphs = list(zip(buf.glyph_infos, buf.glyph_positions))
        self.size = size
        self.width = sum(p.x_advance for _, p in self.glyphs) * size / self.upem

    def fit(self, max_width):
        if self.width > max_width:
            self.size *= max_width / self.width
            self.width = max_width
        return self

    def draw(self, c, x, y, color):
        gs, order = self.ft.getGlyphSet(), self.ft.getGlyphOrder()
        k = self.size / self.upem
        pen_x = 0
        path = c.beginPath()
        for info, pos in self.glyphs:
            pen = CanvasPathPen(gs, path)
            gs[order[info.codepoint]].draw(TransformPen(
                pen, (k, 0, 0, k, x + (pen_x + pos.x_offset) * k, y + pos.y_offset * k)))
            pen_x += pos.x_advance
        c.setFillColor(color)
        c.drawPath(path, stroke=0, fill=1, fillMode=1)


def spaced(c, text, font, size, cx, y, tracking=0):
    """Centred text with letter-spacing (tracking in pt)."""
    w = pdfmetrics.stringWidth(text, font, size) + tracking * (len(text) - 1)
    t = c.beginText(cx - w / 2, y)
    t.setFont(font, size)
    t.setCharSpace(tracking)
    t.textOut(text)
    t.setCharSpace(0)  # reset, otherwise tracking leaks into later text
    c.drawText(t)


def runs(c, parts, cx, y):
    """Draw [(text, font, size, color) | (Arabic, color), ...] as one centred line."""
    def width(p):
        return p[0].width if isinstance(p[0], Arabic) else pdfmetrics.stringWidth(*p[:3])
    x = cx - sum(width(p) for p in parts) / 2
    for p in parts:
        if isinstance(p[0], Arabic):
            p[0].draw(c, x, y, p[1])
        else:
            c.setFillColor(p[3])
            c.setFont(p[1], p[2])
            c.drawString(x, y, p[0])
        x += width(p)


def wrap(text, font, size, width):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if cur and pdfmetrics.stringWidth(trial, font, size) > width:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    return lines + [cur]


def stripes(c, y_top, height, color, pitch=36, duty=0.5):
    """Vertical candy stripes across the full bleed width (fries-box motif)."""
    c.setFillColor(color)
    x = -BLEED
    while x < W:
        c.rect(x, Y(y_top + height), pitch * duty * mm, height * mm, stroke=0, fill=1)
        x += pitch * mm


def draw_logo(c, cx, cy, width):
    data = json.load(open(LOGO))
    s = width / data["w"]
    ox, oy = cx - width / 2, cy + data["h"] * s / 2   # raster y grows downward
    for layer in data["layers"]:
        p = c.beginPath()
        for cv in layer["curves"]:
            p.moveTo(ox + cv["start"][0] * s, oy - cv["start"][1] * s)
            for sg in cv["segs"]:
                pts = [(ox + sg[i] * s, oy - sg[i + 1] * s) for i in range(1, len(sg), 2)]
                if sg[0] == "L":
                    p.lineTo(*pts[0]); p.lineTo(*pts[1])
                else:
                    p.curveTo(*pts[0], *pts[1], *pts[2])
            p.close()
        c.setFillColor(rgb(layer["color"]))
        c.drawPath(p, stroke=0, fill=1, fillMode=0)   # even-odd keeps letter holes
    return data["h"] * s


def product_photo(fname):
    """Crop to the products (auto-detected) and feather edges into the page colour."""
    im = Image.open(os.path.join(ASSETS, fname)).convert("RGB")
    a = np.asarray(im, dtype=float)
    ys, xs = np.where(np.linalg.norm(a - a[5, 5], axis=2) > 40)
    # Shift the photo so its backdrop matches the page cream exactly.
    a = np.clip(a + (np.array([253, 244, 229]) - np.median(a[:20, :20].reshape(-1, 3), axis=0)), 0, 255)
    im = Image.fromarray(a.astype(np.uint8))
    pad = int(0.08 * (xs.max() - xs.min()))
    im = im.crop((max(xs.min() - pad, 0), max(ys.min() - pad, 0),
                  min(xs.max() + pad, im.width), min(ys.max() + pad, im.height)))
    im = im.resize((im.width * 2, im.height * 2), Image.LANCZOS)
    m = Image.new("L", im.size, 0)
    f = int(min(im.size) * 0.07)
    m.paste(255, (f, f, im.width - f, im.height - f))
    m = m.filter(ImageFilter.GaussianBlur(f / 2))
    bg = Image.new("RGB", im.size, (253, 244, 229))
    return ImageReader(Image.composite(im, bg, m)), im.width / im.height


def meal_card(c, meal, top, height, photo_left):
    en, ar_name, price, kcal, photo = meal
    photo_w, gap, margin = 330, 10, 30
    text_w = 600 - 2 * margin - photo_w - gap
    px = margin if photo_left else 600 - margin - photo_w
    tx = (margin + photo_w + gap) if photo_left else margin
    tcx = X(tx + text_w / 2)

    img, ratio = product_photo(photo)
    w = photo_w * mm
    h = min(w / ratio, (height - 20) * mm)
    w = h * ratio
    c.drawImage(img, X(px + photo_w / 2) - w / 2, Y(top + height / 2) - h / 2, w, h)

    # Text block, vertically centred in the card
    lines = wrap(en.upper(), "Oswald-Bold", 74, text_w * mm)
    lh = 27
    block = len(lines) * lh + 30 + 75 + 22
    y = top + (height - block) / 2 + 22
    c.setFillColor(MAROON)
    for ln in lines:
        spaced(c, ln, "Oswald-Bold", 74, tcx, Y(y))
        y += lh
    runs(c, [(Arabic(ar_name, "Cairo-Bold", 56).fit(text_w * mm), INK)], tcx, Y(y + 2))
    y += 30

    # Price pill
    pw = (pdfmetrics.stringWidth(price, "Oswald-Bold", 150)
          + pdfmetrics.stringWidth(" " + CURRENCY, "Oswald-Medium", 54) + 50 * mm)
    c.setFillColor(ORANGE)
    c.roundRect(tcx - pw / 2, Y(y + 62), pw, 62 * mm, 31 * mm, stroke=0, fill=1)
    runs(c, [(price, "Oswald-Bold", 150, CREAM_LT), (" " + CURRENCY, "Oswald-Medium", 54, CREAM_LT)],
         tcx, Y(y + 50))
    y += 75 + 18

    runs(c, [(kcal + " kcal", "Montserrat-Bold", 40, INK), ("   |   ", "Montserrat-Medium", 40, RULE),
             (Arabic("سعرة حرارية", "Cairo-Medium", 42), INK)], tcx, Y(y))


def build():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    c = canvas.Canvas(OUT, pagesize=(W, H))
    c.setTitle("Jan Burger — Menu Panel 600x2000mm")
    c.setAuthor("Rakhy Group Food Court")
    cx = X(300)

    # Page
    c.setFillColor(CREAM)
    c.rect(0, 0, W, H, stroke=0, fill=1)

    # Header: maroon block with a bun-shaped bottom edge, stripes on top
    c.setFillColor(MAROON)
    p = c.beginPath()
    p.moveTo(0, H); p.lineTo(W, H); p.lineTo(W, Y(290))
    p.curveTo(X(470), Y(380), X(130), Y(380), 0, Y(290))
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    stripes(c, -5, 70, MAROON_DK)
    c.setFillColor(ORANGE)
    c.rect(0, Y(73), W, 8 * mm, stroke=0, fill=1)

    # Logo sits on the header edge
    draw_logo(c, cx, Y(275), 370 * mm)

    # Section title: MEALS | الوجبات
    y_t = 545
    runs(c, [("MEALS", "Oswald-Bold", 140, MAROON), ("   ", "Oswald-Bold", 140, MAROON),
             (Arabic("الوجبات", "Cairo-Bold", 120), MAROON)], cx, Y(y_t))
    c.setStrokeColor(ORANGE)
    c.setLineWidth(2.2 * mm)
    c.setLineCap(1)
    c.line(X(40), Y(y_t - 18), X(120), Y(y_t - 18))
    c.line(X(480), Y(y_t - 18), X(560), Y(y_t - 18))

    # Meal cards, photos alternating sides
    top, bottom = 580, 1850
    ch = (bottom - top) / len(MEALS)
    for i, meal in enumerate(MEALS):
        t = top + i * ch
        if i:
            c.setStrokeColor(RULE)
            c.setLineWidth(1.6 * mm)
            c.setDash(0.1, 5 * mm)
            c.line(X(60), Y(t), X(540), Y(t))
            c.setDash()
        meal_card(c, meal, t, ch, photo_left=(i % 2 == 0))

    # Footer: stripes + note
    c.setFillColor(MAROON)
    c.rect(0, 0, W, Y(1872), stroke=0, fill=1)
    stripes(c, 1945, 60, MAROON_DK)
    c.setFillColor(ORANGE)
    c.rect(0, Y(1880), W, 8 * mm, stroke=0, fill=1)
    runs(c, [("PRICES IN SAR", "Oswald-Medium", 64, CREAM_LT), ("    |    ", "Oswald-Medium", 64, ORANGE),
             (Arabic("الأسعار بالريال السعودي", "Cairo-Bold", 58), CREAM_LT)], cx, Y(1925))

    c.showPage()
    c.save()

    # TrimBox / BleedBox so the printer's RIP knows the finished size.
    import pymupdf
    doc = pymupdf.open(OUT)
    pg = doc[0]
    doc.xref_set_key(pg.xref, "TrimBox", f"[{BLEED} {BLEED} {W - BLEED} {H - BLEED}]")
    doc.xref_set_key(pg.xref, "BleedBox", f"[0 0 {W} {H}]")
    doc.saveIncr()
    doc.close()
    print("wrote", OUT)


if __name__ == "__main__":
    build()
