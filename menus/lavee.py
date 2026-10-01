"""La Vee Bakery & Cafe standing menu panel — text-only print file.

Same panel system as jan_burger.py (600 x 2000 mm trim, 5 mm bleed, vector
text and logo). Black and gold on warm white, like the La Vee logo.
Items come from assets/lavee-menu.xlsx; Arabic names are added here.
Edit SECTIONS below and re-run:  python3 menus/lavee.py
"""
import os

from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas

from pilatta import draw_svg_logo   # noqa: E402  (also loads the shared helpers)
import jan_burger as base
from jan_burger import Arabic, H, W, X, Y, calorie_notice, rgb, runs

HERE = base.HERE
OUT = os.path.join(HERE, "out", "lavee-menu-600x2000mm.pdf")
LOGO_SVG = os.path.join(HERE, "logos", "lavee-logo.svg")
CURRENCY = "SAR"

SECTIONS = [
    # (English title, Arabic title, [(English, Arabic, price, kcal or None), ...])
    ("HOT DRINKS", "المشروبات الساخنة", [
        ("Cappuccino", "كابتشينو", "18", None),
        ("Spanish Latte", "سبانش لاتيه", "22", None),
        ("Hot Latte", "لاتيه ساخن", "21", None),
        ("Americano", "أمريكانو", "16", None),
        ("Café Latte", "كافيه لاتيه", "21", None),
        ("Cortado", "كورتادو", "18", None),
        ("Flat White", "فلات وايت", "21", None),
        ("Espresso", "إسبريسو", "16", None),
        ("Coffee of the Day", "قهوة اليوم", "15", None),
    ]),
    ("COLD DRINKS", "المشروبات الباردة", [
        ("Iced Americano", "آيس أمريكانو", "18", None),
        ("Iced Spanish Latte", "آيس سبانش لاتيه", "23", None),
        ("Iced Latte", "آيس لاتيه", "21", None),
        ("Iced Coffee of the Day", "قهوة اليوم المثلجة", "16", None),
        ("Freddo Espresso", "فريدو إسبريسو", "18", None),
    ]),
    ("SANDWICHES & SALAD", "الساندويتشات والسلطة", [
        ("Light Sandwiches", "ساندويتشات خفيفة", "18", None),
        ("Heavy Sandwiches", "ساندويتشات كبيرة", "22", None),
        ("Salad", "سلطة", "21", None),
    ]),
    ("SWEETS", "الحلويات", [
        ("Honey Cake", "كيكة العسل", "18", None),
        ("Cheesecake", "تشيز كيك", "18", None),
        ("Carrot Cake", "كيكة الجزر", "18", None),
        ("Date Cake", "كيكة التمر", "18", None),
        ("Brownie Bites", "قطع البراونيز", "16", None),
        ("Coconut Bites", "قطع جوز الهند", "16", None),
    ]),
]

# La Vee palette (gold sampled from the logo)
PAGE = rgb("#FBF8F2")
BLACK = rgb("#151515")
GOLD = rgb("#C9A04A")
GREY = rgb("#8A8378")
RULE = rgb("#E6D7B5")
WHITE = rgb("#FFFFFF")

# Shared calorie notice: white box, black text, gold numbers.
base.CREAM_LT, base.MAROON, base.ORANGE, base.INK, base.RULE = WHITE, BLACK, GOLD, BLACK, RULE


def tracked(c, text, font, size, x, y, tracking, color, align="left"):
    """Letter-spaced text (tracking in pt), aligned left / right / centre at x."""
    w = pdfmetrics.stringWidth(text, font, size) + tracking * (len(text) - 1)
    x0 = {"left": x, "right": x - w, "centre": x - w / 2}[align]
    t = c.beginText(x0, y)
    t.setFont(font, size)
    t.setCharSpace(tracking)
    t.setFillColor(color)
    t.textOut(text)
    t.setCharSpace(0)
    c.drawText(t)
    return w


def section_header(c, title, ar_title, top):
    tracked(c, title, "Montserrat-Bold", 54, X(45), Y(top + 30), 9, BLACK)
    a = Arabic(ar_title, "Cairo-Bold", 54)
    a.draw(c, X(555) - a.width, Y(top + 30), GOLD)
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.4 * mm)
    c.line(X(45), Y(top + 42), X(555), Y(top + 42))


def item_row(c, item, top):
    en, ar, price, kcal = item
    # line 1: English name ..... price
    c.setFillColor(BLACK)
    c.setFont("Montserrat-Medium", 56)
    c.drawString(X(45), Y(top + 20), en)
    pw = pdfmetrics.stringWidth(price, "Montserrat-Bold", 64)
    sw = pdfmetrics.stringWidth(" " + CURRENCY, "Montserrat-Medium", 26)
    c.setFillColor(GOLD)
    c.setFont("Montserrat-Bold", 64)
    c.drawString(X(555) - pw - sw, Y(top + 20), price)
    c.setFont("Montserrat-Medium", 26)
    c.drawString(X(555) - sw, Y(top + 20), " " + CURRENCY)
    x1 = X(45) + pdfmetrics.stringWidth(en, "Montserrat-Medium", 56) + 8 * mm
    x2 = X(555) - pw - sw - 8 * mm
    if x2 > x1:
        c.setStrokeColor(RULE)
        c.setLineWidth(1.1 * mm)
        c.setLineCap(1)
        c.setDash(0.1, 4.5 * mm)
        c.line(x1, Y(top + 20), x2, Y(top + 20))
        c.setDash()
    # line 2: calories (left) ..... Arabic name (right)
    a = Arabic(ar, "Cairo-Medium", 46)
    a.draw(c, X(555) - a.width, Y(top + 41), BLACK)
    if kcal:
        c.setFillColor(GREY)
        c.setFont("Montserrat-Medium", 28)
        c.drawString(X(45), Y(top + 40), kcal + " kcal")
        k = Arabic("سعرة حرارية", "Cairo-Medium", 28)
        k.draw(c, X(45) + pdfmetrics.stringWidth(kcal + " kcal  ", "Montserrat-Medium", 28), Y(top + 40), GREY)


def build():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    c = canvas.Canvas(OUT, pagesize=(W, H))
    c.setTitle("La Vee Bakery & Cafe — Menu Panel 600x2000mm")
    c.setAuthor("Rakhy Group Food Court")
    cx = X(300)

    c.setFillColor(PAGE)
    c.rect(0, 0, W, H, stroke=0, fill=1)

    # Header: thin black band with gold rule, logo, MENU | القائمة
    c.setFillColor(BLACK)
    c.rect(0, Y(22), W, 27 * mm, stroke=0, fill=1)
    c.setFillColor(GOLD)
    c.rect(0, Y(27), W, 5 * mm, stroke=0, fill=1)
    draw_svg_logo(c, LOGO_SVG, cx, Y(175), 430 * mm)
    y_m = 345
    tracked(c, "MENU", "Montserrat-Medium", 48, cx - 18 * mm, Y(y_m), 14, BLACK, align="right")
    a = Arabic("القائمة", "Cairo-Medium", 48)
    a.draw(c, cx + 18 * mm, Y(y_m), BLACK)
    c.setFillColor(GOLD)
    c.circle(cx, Y(y_m + 6), 2.6 * mm, stroke=0, fill=1)

    # Sections: share the space evenly between rows
    top, bottom = 380, 1760
    head_h, gap = 62, 26
    n_items = sum(len(s[2]) for s in SECTIONS)
    row_h = (bottom - top - len(SECTIONS) * head_h - (len(SECTIONS) - 1) * gap) / n_items
    y = top
    for i, (title, ar_title, items) in enumerate(SECTIONS):
        if i:
            y += gap
        section_header(c, title, ar_title, y)
        y += head_h
        for item in items:
            item_row(c, item, y)
            y += row_h

    calorie_notice(c, 1775, 1856)

    # Footer: black band, VAT note in white with a gold divider
    c.setFillColor(GOLD)
    c.rect(0, Y(1878), W, 5 * mm, stroke=0, fill=1)
    c.setFillColor(BLACK)
    c.rect(0, 0, W, Y(1878) - 0, stroke=0, fill=1)
    runs(c, [("PRICES INCLUDE VAT", "Montserrat-Medium", 50, WHITE), ("   |   ", "Montserrat-Medium", 50, GOLD),
             (Arabic("الأسعار شاملة ضريبة القيمة المضافة", "Cairo-Medium", 52).fit(300 * mm), WHITE)],
         cx, Y(1945))

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
