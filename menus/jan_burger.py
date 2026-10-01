"""Jan Burger standing menu panel — print file.

Trim size 600 x 2000 mm, 5 mm bleed on every side, vector text and vector logo.
Edit MENU below and re-run:  python3 menus/jan_burger.py

Colours are RGB so the page background matches the product photo's backdrop
exactly; the printer's RIP converts the whole file to CMYK in one pass.
"""
import json
import os

from PIL import Image, ImageFilter
from reportlab.lib.colors import Color
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "jan-burger-menu-600x2000mm.pdf")
LOGO = os.path.join(HERE, "assets", "jan-logo.json")         # from vectorize_logo.py
PHOTO = os.path.join(HERE, "assets", "jan-burger-photo.jpg")
PHOTO_CROP = (300, 200, 1620, 1000)                           # px box around the products

TRIM_W, TRIM_H, BLEED = 600 * mm, 2000 * mm, 5 * mm
W, H = TRIM_W + 2 * BLEED, TRIM_H + 2 * BLEED

# Placeholder content — replace with Jan's real items/prices.
CURRENCY = "SAR"
MENU = [
    ("BURGERS", [("Classic Burger", "95"), ("Cheese Burger", "105"),
                 ("Double Burger", "135"), ("Spicy Burger", "115")]),
    ("SIDES", [("French Fries", "35"), ("Onion Rings", "40"),
               ("Mozzarella Sticks", "50")]),
    ("DRINKS", [("Soft Drinks", "20"), ("Water", "15")]),
]


def rgb(h):
    h = h.lstrip("#")
    return Color(*(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)))


# Jan brand palette (sampled from the supplied logo and photo)
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


def spaced(c, text, font, size, cx, y, tracking=0):
    """Centred text with letter-spacing (tracking in pt)."""
    w = pdfmetrics.stringWidth(text, font, size) + tracking * (len(text) - 1)
    t = c.beginText(cx - w / 2, y)
    t.setFont(font, size)
    t.setCharSpace(tracking)
    t.textOut(text)
    t.setCharSpace(0)  # reset, otherwise tracking leaks into later text
    c.drawText(t)


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


def photo_reader():
    """Crop to the products and feather the edges into the page colour."""
    im = Image.open(PHOTO).convert("RGB").crop(PHOTO_CROP)
    im = im.resize((im.width * 2, im.height * 2), Image.LANCZOS)
    m = Image.new("L", im.size, 0)
    f = int(im.width * 0.06)
    m.paste(255, (f, f, im.width - f, im.height - f))
    m = m.filter(ImageFilter.GaussianBlur(f / 2))
    bg = Image.new("RGB", im.size, (253, 244, 229))
    return ImageReader(Image.composite(im, bg, m)), im.width / im.height


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
    p.moveTo(0, H); p.lineTo(W, H); p.lineTo(W, Y(330))
    p.curveTo(X(470), Y(430), X(130), Y(430), 0, Y(330))
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    stripes(c, -5, 75, MAROON_DK)
    c.setFillColor(ORANGE)
    c.rect(0, Y(80), W, 8 * mm, stroke=0, fill=1)

    # Logo sits on the header edge, cream disc on maroon
    logo_w = 430 * mm
    draw_logo(c, cx, Y(320), logo_w)

    # "MENU"
    y_menu = 650
    c.setFillColor(MAROON)
    spaced(c, "MENU", "Oswald-Bold", 150, cx, Y(y_menu), 30)
    c.setStrokeColor(ORANGE)
    c.setLineWidth(2.2 * mm)
    c.setLineCap(1)
    c.line(X(60), Y(y_menu - 20), X(170), Y(y_menu - 20))
    c.line(X(430), Y(y_menu - 20), X(540), Y(y_menu - 20))

    # Menu sections
    left, right = 60, 540
    y = y_menu + 85
    for title, items in MENU:
        # orange pill with the section name
        tw = pdfmetrics.stringWidth(title, "Oswald-Bold", 110)
        c.setFillColor(ORANGE)
        c.roundRect(X(left), Y(y + 14), tw + 50 * mm, 56 * mm, 28 * mm, stroke=0, fill=1)
        c.setFillColor(CREAM_LT)
        c.setFont("Oswald-Bold", 110)
        c.drawString(X(left) + 25 * mm, Y(y), title)
        c.setStrokeColor(RULE)
        c.setLineWidth(1.2 * mm)
        c.line(X(left) + tw + 65 * mm, Y(y - 14), X(right), Y(y - 14))
        y += 66
        for name, price in items:
            c.setFillColor(INK)
            c.setFont("Montserrat-Bold", 80)
            c.drawString(X(left + 6), Y(y), name)
            c.setFillColor(MAROON)
            c.setFont("Oswald-Bold", 100)
            c.drawRightString(X(right), Y(y), price)
            nw = pdfmetrics.stringWidth(name, "Montserrat-Bold", 80)
            pw = pdfmetrics.stringWidth(price, "Oswald-Bold", 100)
            c.setStrokeColor(RULE)
            c.setLineWidth(1.6 * mm)
            c.setDash(0.1, 5 * mm)
            c.line(X(left + 6) + nw + 10 * mm, Y(y - 1), X(right) - pw - 10 * mm, Y(y - 1))
            c.setDash()
            y += 44
        y += 34
    c.setFillColor(INK)
    c.setFont("Montserrat-Medium", 40)
    c.drawRightString(X(right), Y(y - 20), f"Prices in {CURRENCY}")

    # Product photo, full width, feathered into the cream
    img, ratio = photo_reader()
    ph_w = 610 * mm
    ph_h = ph_w / ratio
    ph_bottom = Y(1860)
    c.drawImage(img, 0, ph_bottom, ph_w, ph_h)

    # Footer: stripes + "SINCE 1985"
    c.setFillColor(MAROON)
    c.rect(0, 0, W, Y(1870), stroke=0, fill=1)
    stripes(c, 1940, 65, MAROON_DK)
    c.setFillColor(ORANGE)
    c.rect(0, Y(1878), W, 8 * mm, stroke=0, fill=1)
    c.setFillColor(CREAM_LT)
    spaced(c, "SINCE 1985", "Oswald-Medium", 80, cx, Y(1922), 14)

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
