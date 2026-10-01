"""Jan Burger standing menu panel — print file.

Trim size 600 x 2000 mm, 5 mm bleed on every side, CMYK colours, vector text.
Edit MENU / PHOTO / LOGO below and re-run:  python3 menus/jan_burger.py
"""
import os
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import CMYKColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "jan-burger-menu-600x2000mm.pdf")

# Optional assets: drop files here and re-run.
LOGO = os.path.join(HERE, "assets", "jan-burger-logo.png")   # transparent PNG or high-res
PHOTO = os.path.join(HERE, "assets", "jan-burger-photo.jpg")  # >= 3600 px wide

TRIM_W, TRIM_H, BLEED = 600 * mm, 2000 * mm, 5 * mm
W, H = TRIM_W + 2 * BLEED, TRIM_H + 2 * BLEED

MENU = [
    ("BURGERS", [("Classic Burger", "95"), ("Cheese Burger", "105"),
                 ("Double Burger", "135"), ("Spicy Burger", "115")]),
    ("SIDES", [("French Fries", "35"), ("Onion Rings", "40"),
               ("Mozzarella Sticks", "50")]),
    ("DRINKS", [("Soft Drinks", "20"), ("Water", "15")]),
]

# CMYK palette
BLACK = CMYKColor(0.60, 0.40, 0.40, 1.00)   # rich black
PANEL = CMYKColor(0.70, 0.60, 0.55, 0.85)   # slightly lifted black for depth
GOLD = CMYKColor(0.00, 0.28, 1.00, 0.00)
GOLD_DK = CMYKColor(0.05, 0.45, 1.00, 0.20)
WHITE = CMYKColor(0, 0, 0, 0)
GREY = CMYKColor(0, 0, 0, 0.35)

for name in ["Oswald-Bold", "Oswald-Medium", "Oswald-Regular",
             "Montserrat-Regular", "Montserrat-Medium", "Montserrat-Bold"]:
    pdfmetrics.registerFont(TTFont(name, os.path.join(HERE, "fonts", name + ".ttf")))


def X(v):  # trim-relative mm -> canvas pt (origin bottom-left of bleed box)
    return BLEED + v * mm


def Y(v):  # trim-relative mm measured from TOP of trim
    return BLEED + TRIM_H - v * mm


def spaced(c, text, font, size, cx, y, tracking):
    """Centred text with letter-spacing (tracking in pt)."""
    w = pdfmetrics.stringWidth(text, font, size) + tracking * (len(text) - 1)
    t = c.beginText(cx - w / 2, y)
    t.setFont(font, size)
    t.setCharSpace(tracking)
    t.textOut(text)
    t.setCharSpace(0)  # reset, otherwise tracking leaks into later text
    c.drawText(t)


def burger_icon(c, cx, top, w, stroke):
    """Line-art burger mark (stand-in until the real logo is supplied)."""
    c.setStrokeColor(GOLD)
    c.setLineWidth(stroke)
    c.setLineCap(1)
    c.setLineJoin(1)
    h_bun = w * 0.42
    x0, x1 = cx - w / 2, cx + w / 2
    base = top - h_bun
    p = c.beginPath()
    p.moveTo(x0, base)
    p.curveTo(x0, top + h_bun * 0.05, x1, top + h_bun * 0.05, x1, base)
    p.close()
    c.drawPath(p, stroke=1, fill=0)
    for dx, dy in [(-0.22, 0.45), (0.0, 0.62), (0.22, 0.45), (-0.08, 0.30), (0.12, 0.28)]:
        sx, sy = cx + dx * w, base + dy * h_bun
        c.line(sx - w * 0.025, sy, sx + w * 0.025, sy)
    gap = w * 0.09
    c.line(x0, base - gap, x1, base - gap)                 # lettuce / cheese line
    c.roundRect(x0, base - 2 * gap - w * 0.11, w, w * 0.11, w * 0.05, stroke=1, fill=0)
    bb = base - 3 * gap - w * 0.11
    p = c.beginPath()
    p.moveTo(x0, bb)
    p.lineTo(x1, bb)
    p.curveTo(x1, bb - w * 0.16, x0, bb - w * 0.16, x0, bb)
    c.drawPath(p, stroke=1, fill=0)
    return bb - w * 0.16


def build():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    c = canvas.Canvas(OUT, pagesize=(W, H))
    c.setTitle("Jan Burger — Menu Panel 600x2000mm")
    c.setAuthor("Rakhy Group Food Court")

    # Background (full bleed) + inner panel with thin gold frame
    c.setFillColor(BLACK)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setFillColor(PANEL)
    c.rect(X(22), Y(1978), 556 * mm, 1956 * mm, stroke=0, fill=1)
    c.setStrokeColor(GOLD_DK)
    c.setLineWidth(1.2 * mm)
    c.rect(X(22), Y(1978), 556 * mm, 1956 * mm, stroke=1, fill=0)

    # Top-left / top-right angular gold accents (bleed through edge)
    c.setFillColor(GOLD)
    p = c.beginPath(); p.moveTo(0, H); p.lineTo(X(190), H); p.lineTo(0, Y(95)); p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.setFillColor(GOLD_DK)
    p = c.beginPath(); p.moveTo(X(215), H); p.lineTo(X(245), H); p.lineTo(X(165), Y(40)); p.lineTo(X(150), Y(40)); p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.setFillColor(GOLD)
    p = c.beginPath(); p.moveTo(W, H); p.lineTo(X(470), H); p.lineTo(W, Y(60)); p.close()
    c.drawPath(p, stroke=0, fill=1)

    # Logo
    cx = X(300)
    if os.path.exists(LOGO):
        c.drawImage(LOGO, X(130), Y(470), 340 * mm, 330 * mm,
                    preserveAspectRatio=True, mask="auto", anchor="c")
        y_after_logo = 480
    else:
        bottom = burger_icon(c, cx, Y(150), 150 * mm, 7 * mm)
        c.setFillColor(GOLD)
        spaced(c, "JAN", "Oswald-Bold", 300, cx, bottom - 125 * mm, 6)
        spaced(c, "BURGER", "Oswald-Bold", 300, cx, bottom - 235 * mm, 6)
        y_after_logo = 2000 - (bottom - 235 * mm - BLEED) / mm

    # "MENU" with gold rules
    y_menu = y_after_logo + 85
    c.setFillColor(WHITE)
    spaced(c, "MENU", "Montserrat-Medium", 120, cx, Y(y_menu), 40)
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.5 * mm)
    c.line(X(70), Y(y_menu - 15), X(165), Y(y_menu - 15))
    c.line(X(435), Y(y_menu - 15), X(530), Y(y_menu - 15))

    # Menu sections
    left, right = 75, 525
    y = y_menu + 95
    for title, items in MENU:
        c.setFillColor(GOLD)
        c.setFont("Oswald-Bold", 130)
        c.drawString(X(left), Y(y), title)
        tw = pdfmetrics.stringWidth(title, "Oswald-Bold", 130)
        c.setStrokeColor(GOLD_DK)
        c.setLineWidth(1 * mm)
        c.line(X(left) + tw + 15 * mm, Y(y - 16), X(right), Y(y - 16))
        y += 62
        for name, price in items:
            c.setFillColor(WHITE)
            c.setFont("Montserrat-Medium", 84)
            c.drawString(X(left), Y(y), name)
            c.setFont("Oswald-Medium", 96)
            c.setFillColor(GOLD)
            c.drawRightString(X(right), Y(y), price)
            # dotted leader
            nw = pdfmetrics.stringWidth(name, "Montserrat-Medium", 84)
            pw = pdfmetrics.stringWidth(price, "Oswald-Medium", 96)
            c.setStrokeColor(GREY)
            c.setLineWidth(1.4 * mm)
            c.setDash(0.1, 4.5 * mm)
            c.line(X(left) + nw + 10 * mm, Y(y - 1), X(right) - pw - 10 * mm, Y(y - 1))
            c.setDash()
            y += 46
        y += 40

    # Hero photo area
    ph_top, ph_bot = y + 10, 1890
    if os.path.exists(PHOTO):
        c.saveState()
        p = c.beginPath(); p.rect(X(22), Y(ph_bot), 556 * mm, (ph_bot - ph_top) * mm)
        c.clipPath(p, stroke=0, fill=0)
        c.drawImage(PHOTO, X(22), Y(ph_bot), 556 * mm, (ph_bot - ph_top) * mm,
                    preserveAspectRatio=True, anchor="c")
        c.restoreState()
    else:
        c.setStrokeColor(GOLD)
        c.setLineWidth(1.5 * mm)
        c.setDash(12 * mm, 8 * mm)
        c.roundRect(X(60), Y(ph_bot - 20), 480 * mm, (ph_bot - ph_top - 40) * mm, 20 * mm, stroke=1, fill=0)
        c.setDash()
        mid = (ph_top + ph_bot) / 2
        c.setFillColor(GOLD)
        spaced(c, "BURGER PHOTO", "Oswald-Bold", 110, cx, Y(mid - 10), 6)
        c.setFillColor(GREY)
        spaced(c, "placeholder — supply high-res image", "Montserrat-Regular", 46, cx, Y(mid + 25), 0)

    # Bottom angular accents
    c.setFillColor(GOLD)
    p = c.beginPath(); p.moveTo(0, 0); p.lineTo(X(150), 0); p.lineTo(0, Y(1930)); p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.setFillColor(GOLD_DK)
    p = c.beginPath(); p.moveTo(W, 0); p.lineTo(X(400), 0); p.lineTo(W, Y(1950)); p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.setFillColor(GOLD)
    p = c.beginPath(); p.moveTo(W, 0); p.lineTo(X(480), 0); p.lineTo(W, Y(1965)); p.close()
    c.drawPath(p, stroke=0, fill=1)

    c.showPage()
    c.save()

    # Set TrimBox / BleedBox so the printer's RIP knows the finished size.
    import pymupdf as fitz
    doc = fitz.open(OUT)
    pg = doc[0]
    doc.xref_set_key(pg.xref, "TrimBox", f"[{BLEED} {BLEED} {W - BLEED} {H - BLEED}]")
    doc.xref_set_key(pg.xref, "BleedBox", f"[0 0 {W} {H}]")
    doc.saveIncr()
    doc.close()
    print("wrote", OUT)


if __name__ == "__main__":
    build()
