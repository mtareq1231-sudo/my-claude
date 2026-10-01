"""Pilatta standing menu panel — print file.

Same panel system as jan_burger.py (600 x 2000 mm trim, 5 mm bleed, vector
text, side-by-side cards). Styled on the Pilatta packaging: periwinkle page,
deep-green type, yellow pasta doodles (fusilli, farfalle, dots), bowls floating
on the page (photo backdrop matched to it, doodles painted out).
Edit PASTAS below and re-run:  python3 menus/pilatta.py
"""
import io
import math
import os

import numpy as np
from PIL import Image, ImageFilter
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from scipy import ndimage as ndi

import jan_burger as base
from jan_burger import Arabic, H, W, X, Y, calorie_notice, rgb, runs, wrap

HERE = base.HERE
OUT = os.path.join(HERE, "out", "pilatta-menu-600x2000mm.pdf")
CURRENCY = "SAR"
PASTAS = [
    # (English, Arabic, price, kcal or None, photo) — from the Food World e-menu
    ("Spaghetti Bolognese", "سباغيتي بولونيز", "41", None, "pilatta-spaghetti-bolognese.jpg"),
    ("Fettuccine Alfredo", "فوتوتشيني ألفريدو", "43", None, "pilatta-fettuccine-alfredo.jpg"),
    ("Truffle Pasta", "ترافل", "51", None, "pilatta-truffle.jpg"),
    ("Three Cheese Pasta", "باستا الثلاثة أجبان", "39", None, "pilatta-three-cheese.jpg"),
]

# Pilatta palette (sampled from the packaging photos)
PAGE = rgb("#DCE3FC")
LAVENDER = rgb("#B8C3F3")
GREEN = rgb("#2F5747")
YELLOW = rgb("#FED604")
WHITE = rgb("#FFFFFF")
RULE = rgb("#B8C3F3")

for name in ["Fredoka-SemiBold", "Fredoka-Bold"]:
    pdfmetrics.registerFont(TTFont(name, os.path.join(HERE, "fonts", name + ".ttf")))
HEAD = "Fredoka-Bold"

# Shared calorie notice: white box, green text and numbers.
base.CREAM_LT, base.MAROON, base.ORANGE, base.INK, base.RULE = WHITE, GREEN, GREEN, GREEN, RULE


# --- pasta doodles (from the packaging) -------------------------------------

def fusilli(c, x, y, length, angle, thick=16):
    """Yellow wavy fusilli with a thin green squiggle inside. x, y, length in mm."""
    ca, sa = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    pts = []
    for i in range(41):
        t = i / 40
        u, v = (t - 0.5) * length, math.sin(t * 2 * math.pi * 2.5) * thick * 0.28
        pts.append((x + u * ca - v * sa, y + u * sa + v * ca))
    for color, width in ((YELLOW, thick), (GREEN, 1.4)):
        c.setStrokeColor(color)
        c.setLineWidth(width * mm)
        c.setLineCap(1)
        c.setLineJoin(1)
        p = c.beginPath()
        p.moveTo(X(pts[0][0]), Y(pts[0][1]))
        for px, py in pts[1:]:
            p.lineTo(X(px), Y(py))
        c.drawPath(p, stroke=1, fill=0)
        if color == YELLOW:   # thinner, tighter squiggle for the green line
            pts = [(px, py) for px, py in pts[4:-4]]


def farfalle(c, x, y, size, angle):
    """Yellow bow-tie pasta with a green squiggle on each wing."""
    c.saveState()
    c.translate(X(x), Y(y))
    c.rotate(-angle)
    s = size * mm
    c.setFillColor(YELLOW)
    p = c.beginPath()
    p.moveTo(0, 0)
    p.curveTo(-0.3 * s, 0.55 * s, -0.75 * s, 0.6 * s, -0.8 * s, 0.35 * s)
    p.curveTo(-0.9 * s, 0.1 * s, -0.9 * s, -0.1 * s, -0.8 * s, -0.35 * s)
    p.curveTo(-0.75 * s, -0.6 * s, -0.3 * s, -0.55 * s, 0, 0)
    p.curveTo(0.3 * s, 0.55 * s, 0.75 * s, 0.6 * s, 0.8 * s, 0.35 * s)
    p.curveTo(0.9 * s, 0.1 * s, 0.9 * s, -0.1 * s, 0.8 * s, -0.35 * s)
    p.curveTo(0.75 * s, -0.6 * s, 0.3 * s, -0.55 * s, 0, 0)
    c.drawPath(p, stroke=0, fill=1)
    c.setStrokeColor(GREEN)
    c.setLineWidth(1.3 * mm)
    c.setLineCap(1)
    for sx in (-1, 1):
        q = c.beginPath()
        q.moveTo(sx * 0.62 * s, 0.25 * s)
        q.curveTo(sx * 0.35 * s, 0.25 * s, sx * 0.62 * s, 0, sx * 0.45 * s, -0.05 * s)
        q.curveTo(sx * 0.3 * s, -0.1 * s, sx * 0.55 * s, -0.3 * s, sx * 0.35 * s, -0.28 * s)
        c.drawPath(q, stroke=1, fill=0)
    c.restoreState()


def dot(c, x, y, r):
    c.setFillColor(YELLOW)
    c.circle(X(x), Y(y), r * mm, stroke=0, fill=1)


def wave_band(c, y_top, y_bottom, color, down=True, amp=9, waves=4):
    """Full-bleed band with a gentle wavy free edge (pasta ribbon)."""
    edge = y_bottom if down else y_top
    other = y_top if down else y_bottom
    p = c.beginPath()
    p.moveTo(X(-5), Y(other))
    p.lineTo(X(605), Y(other))
    n = 80
    for i in range(n + 1):
        xm = 605 - i * 610 / n
        p.lineTo(X(xm), Y(edge + amp * math.sin(xm / 610 * waves * 2 * math.pi)))
    p.close()
    c.setFillColor(color)
    c.drawPath(p, stroke=0, fill=1)


# --- photos and cards ---------------------------------------------------------

PAGE_RGB = (220, 227, 252)
BOWL_W = 235   # mm, drawn width of every bowl
BREAD_MOVE = {"pilatta-three-cheese.jpg": (-235, 35)}   # px shift for a bread shot far from its bowl


def bowl_photo(fname):
    """Bowl + bread on a backdrop matched to the page, doodles and captions removed, soft edges."""
    im = Image.open(os.path.join(base.ASSETS, fname)).convert("RGB")
    a = np.asarray(im, dtype=float)
    blur = np.asarray(im.filter(ImageFilter.GaussianBlur(2)), dtype=float)
    border = np.concatenate([blur[:15].reshape(-1, 3), blur[-15:].reshape(-1, 3),
                             blur[:, :15].reshape(-1, 3), blur[:, -15:].reshape(-1, 3)])
    bg = np.median(border, axis=0)
    m = ndi.binary_opening(np.linalg.norm(blur - bg, axis=2) > 22, iterations=3)
    lab, n = ndi.label(m)
    main = lab == (np.argmax(ndi.sum(m, lab, range(1, n + 1))) + 1)   # bowl + bread (+ shadow)
    keep = Image.fromarray((ndi.binary_dilation(main, iterations=30) * 255).astype(np.uint8))
    keep = np.asarray(keep.filter(ImageFilter.GaussianBlur(14)), dtype=float)[..., None] / 255
    a = a * keep + bg * (1 - keep)                       # paint over doodles / captions
    if fname in BREAD_MOVE:                               # bring a far-off garlic bread next to the bowl
        warm = ndi.binary_opening((a[..., 0] > a[..., 2] + 40) & (a[..., 0] > 120), iterations=3)
        wl, wn = ndi.label(warm)
        sizes = ndi.sum(warm, wl, range(1, wn + 1))
        bread = wl == (np.argsort(sizes)[::-1][1] + 1)    # 2nd-largest warm blob (1st is the pasta)
        dx, dy = BREAD_MOVE[fname]
        sel = Image.fromarray((ndi.binary_dilation(bread, iterations=10) * 255).astype(np.uint8))
        sel = np.asarray(sel.filter(ImageFilter.GaussianBlur(4)), dtype=float)[..., None] / 255
        patch = a.copy()
        a = a * (1 - sel) + bg * sel                      # lift the bread off its old spot
        sel2 = np.roll(sel, (dy, dx), axis=(0, 1))
        a = a * (1 - sel2) + np.roll(patch, (dy, dx), axis=(0, 1)) * sel2
        main = (main & ~ndi.binary_dilation(bread, iterations=40)) | np.roll(bread, (dy, dx), axis=(0, 1))
        x_end = np.where(np.roll(bread, (dy, dx), axis=(0, 1)).any(axis=0))[0].max() + 20
        main[:, x_end:] = False
        ramp = np.clip((np.arange(a.shape[1]) - x_end) / 40, 0, 1)[None, :, None]
        a = a * (1 - ramp) + bg * ramp                    # clear leftovers beyond the bread
    a = np.clip(a + (np.array(PAGE_RGB) - bg), 0, 255)   # backdrop -> page colour
    ys, xs = np.where(main)
    pad = int(0.10 * (xs.max() - xs.min()))
    box = (max(xs.min() - pad, 0), max(ys.min() - pad, 0), min(xs.max() + pad, im.width), min(ys.max() + pad, im.height))
    out = Image.fromarray(a.astype(np.uint8)).crop(box)
    f = int(min(out.size) * 0.06)                        # feather the crop edge into the page
    mask = Image.new("L", out.size, 0)
    mask.paste(255, (f, f, out.width - f, out.height - f))
    out = Image.composite(out, Image.new("RGB", out.size, PAGE_RGB), mask.filter(ImageFilter.GaussianBlur(f / 2)))
    buf = io.BytesIO()
    out.save(buf, "JPEG", quality=92, subsampling=0)
    buf.seek(0)
    # Bowl rim width (top part of the mask, above the bread) as a share of the crop,
    # so every bowl can be drawn at the same size whatever the framing.
    top = main[ys.min():ys.min() + int(0.35 * (ys.max() - ys.min()))]
    cols = np.where(top.any(axis=0))[0]
    rim = (cols.max() - cols.min()) / (box[2] - box[0])
    return ImageReader(buf), out.width / out.height, rim


def pasta_card(c, item, top, height, photo_left):
    en, ar_name, price, kcal, photo = item
    photo_w, margin, gap = 330, 22, 6
    text_w = 600 - 2 * margin - photo_w - gap
    px = margin if photo_left else 600 - margin - photo_w
    tx = (margin + photo_w + gap) if photo_left else margin
    tcx = X(tx + text_w / 2)

    img, ratio, rim = bowl_photo(photo)
    w = BOWL_W * mm / rim            # same bowl width on every card
    h = min(w / ratio, (height - 10) * mm)
    w = h * ratio
    c.drawImage(img, X(px + photo_w / 2) - w / 2, Y(top + height / 2) - h / 2, w, h)

    lines = wrap(en, HEAD, 78, text_w * mm)
    lh = 30
    block = len(lines) * lh + 30 + 72 + (22 if kcal else 0)
    y = top + (height - block) / 2 + 24
    for ln in lines:
        runs(c, [(ln, HEAD, 78, GREEN)], tcx, Y(y))
        y += lh
    runs(c, [(Arabic(ar_name, "Cairo-Bold", 58).fit(text_w * mm), GREEN)], tcx, Y(y + 2))
    y += 30

    pw = (pdfmetrics.stringWidth(price, HEAD, 140)
          + pdfmetrics.stringWidth(" " + CURRENCY, "Fredoka-SemiBold", 52) + 50 * mm)
    c.setFillColor(YELLOW)
    c.roundRect(tcx - pw / 2, Y(y + 60), pw, 60 * mm, 30 * mm, stroke=0, fill=1)
    runs(c, [(price, HEAD, 140, GREEN), (" " + CURRENCY, "Fredoka-SemiBold", 52, GREEN)], tcx, Y(y + 47))
    y += 72 + 18
    if kcal:
        runs(c, [(kcal + " kcal", "Montserrat-Bold", 40, GREEN), ("   |   ", "Montserrat-Medium", 40, RULE),
                 (Arabic("سعرة حرارية", "Cairo-Medium", 42), GREEN)], tcx, Y(y))


def draw_svg_logo(c, path, cx, cy, width, color=None):
    """Draw a logo SVG made by logo_to_svg.py (absolute M/L/C/Z paths) centred at cx, cy."""
    import re
    svg = open(path).read()
    x0, y0, vw, vh = map(float, re.search(r'viewBox="([^"]+)"', svg).group(1).split())
    k = width / vw
    for fill, d in re.findall(r'fill="([^"]+)" fill-rule="evenodd" d="([^"]+)"', svg):
        p = c.beginPath()
        for cmd, nums in re.findall(r"([MLCZ])([^MLCZ]*)", d):
            v = [float(n) for n in nums.split()]
            pts = [(cx + (v[i] - x0 - vw / 2) * k, cy - (v[i + 1] - y0 - vh / 2) * k) for i in range(0, len(v), 2)]
            if cmd == "M":
                p.moveTo(*pts[0])
            elif cmd == "L":
                p.lineTo(*pts[0])
            elif cmd == "C":
                p.curveTo(*pts[0], *pts[1], *pts[2])
            else:
                p.close()
        c.setFillColor(color or rgb(fill))
        c.drawPath(p, stroke=0, fill=1, fillMode=0)
    return vh * k


def build():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    c = canvas.Canvas(OUT, pagesize=(W, H))
    c.setTitle("Pilatta — Menu Panel 600x2000mm")
    c.setAuthor("Rakhy Group Food Court")
    cx = X(300)

    c.setFillColor(PAGE)
    c.rect(0, 0, W, H, stroke=0, fill=1)

    # Header: lavender band with a wavy edge, wordmark, doodles
    wave_band(c, -5, 300, LAVENDER)
    draw_svg_logo(c, os.path.join(base.ASSETS, "pilatta-logo.svg"), cx, Y(165), 470 * mm, GREEN)
    fusilli(c, 110, 52, 110, -10)
    fusilli(c, 495, 262, 100, 6)
    farfalle(c, 80, 262, 40, 18)
    dot(c, 480, 45, 9)
    dot(c, 545, 55, 5)
    dot(c, 300, 272, 5)

    # Section title: PASTA | باستا
    y_t = 410
    runs(c, [("PASTA", HEAD, 150, GREEN), ("   ", HEAD, 150, GREEN),
             (Arabic("باستا", "Cairo-Bold", 125), GREEN)], cx, Y(y_t))
    fusilli(c, 75, y_t - 18, 70, 0, thick=11)
    fusilli(c, 525, y_t - 18, 70, 0, thick=11)

    top, bottom = 440, 1715
    ch = (bottom - top) / len(PASTAS)
    for i, item in enumerate(PASTAS):
        t = top + i * ch
        if i:
            c.setStrokeColor(LAVENDER)
            c.setLineWidth(1.6 * mm)
            c.setDash(0.1, 5 * mm)
            c.line(X(60), Y(t), X(540), Y(t))
            c.setDash()
        pasta_card(c, item, t, ch, photo_left=(i % 2 == 0))

    # Garlic bread note
    runs(c, [("Served with garlic bread  ·  cheese bread +1 SAR", "Fredoka-SemiBold", 34, GREEN)], cx, Y(1735))
    runs(c, [(Arabic("تُقدم مع خبز الثوم، مع إمكانية استبداله بخبز الجبن بإضافة ريال واحد", "Cairo-Bold", 32)
              .fit(520 * mm), GREEN)], cx, Y(1762))

    calorie_notice(c, 1775, 1856)

    # Footer: lavender wave band with the VAT note
    wave_band(c, 1872, 2005, LAVENDER, down=False)
    runs(c, [("PRICES INCLUDE VAT", HEAD, 58, GREEN), ("   |   ", HEAD, 58, GREEN),
             (Arabic("الأسعار شاملة ضريبة القيمة المضافة", "Cairo-Bold", 54).fit(300 * mm), GREEN)],
         cx, Y(1937))
    farfalle(c, 50, 1972, 30, -15)
    dot(c, 560, 1968, 7)

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
