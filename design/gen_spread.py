#!/usr/bin/env python3
"""Generate an Adobe Illustrator-compatible SVG magazine spread:
'Astrocartography' editorial layout — black left page + terracotta celestial right page.
Outputs SVG 1.1 with named layer groups (AI reads top-level <g id> as layers).
"""
import math
import random

random.seed(42)

W, H = 1680, 1120          # full spread
PW = W // 2                # single page width = 840

CREAM = "#e8dfd0"
CREAM_DIM = "#cfc4b0"
BLACK = "#101010"
PAGE_BLACK = "#141414"
TERRA = "#b45a35"
TERRA_DK = "#8a3f22"
INK = "#2a2033"            # dark violet-ink for chart engraving

frag = []
add = frag.append

# ---------------------------------------------------------------- helpers
def esc(s):
    return s.replace("&", "&amp;")

def stipple_circle(cx, cy, r, n, color, rmin=0.4, rmax=1.6, bias=1.0, opacity=0.8):
    """Random dots inside a circle, denser toward edge if bias>1."""
    out = []
    for _ in range(n):
        a = random.uniform(0, 2 * math.pi)
        rr = r * (random.random() ** (1.0 / bias))
        x = cx + rr * math.cos(a)
        y = cy + rr * math.sin(a)
        dr = random.uniform(rmin, rmax)
        op = opacity * random.uniform(0.35, 1.0)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{dr:.2f}" fill="{color}" opacity="{op:.2f}"/>')
    return "\n".join(out)

# ================================================================ DEFS
add(f'''<defs>
  <radialGradient id="moonGrad" cx="42%" cy="38%" r="75%">
    <stop offset="0%" stop-color="#efe8da"/>
    <stop offset="55%" stop-color="#d9cfba"/>
    <stop offset="85%" stop-color="#a99d84"/>
    <stop offset="100%" stop-color="#6f6553"/>
  </radialGradient>
  <radialGradient id="chartVign" cx="50%" cy="50%" r="72%">
    <stop offset="0%" stop-color="{TERRA}"/>
    <stop offset="78%" stop-color="{TERRA}"/>
    <stop offset="100%" stop-color="{TERRA_DK}"/>
  </radialGradient>
  <linearGradient id="gutter" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#000000" stop-opacity="0"/>
    <stop offset="0.5" stop-color="#000000" stop-opacity="0.5"/>
    <stop offset="1" stop-color="#000000" stop-opacity="0"/>
  </linearGradient>
  <clipPath id="clipLeft"><rect x="0" y="0" width="{PW}" height="{H}"/></clipPath>
  <clipPath id="clipRight"><rect x="{PW}" y="0" width="{PW}" height="{H}"/></clipPath>
  <clipPath id="clipMoon"><circle cx="300" cy="600" r="150"/></clipPath>
</defs>''')

# ================================================================ LEFT PAGE
L = []
L.append(f'<rect x="0" y="0" width="{PW}" height="{H}" fill="{PAGE_BLACK}"/>')

# --- running head
L.append(f'''<g id="running-head" fill="{CREAM_DIM}" font-family="Futura, 'Century Gothic', 'Avenir Next', sans-serif" font-size="13" letter-spacing="4">
  <text x="96" y="118">LOCATIONAL</text>
  <text x="{PW//2}" y="96" text-anchor="middle" font-family="Didot, 'Bodoni 72', 'Playfair Display', serif" font-size="22" letter-spacing="2">IV.</text>
  <text x="{PW-96}" y="150" text-anchor="end">ASTROLOGY</text>
</g>''')
# ornament under IV.
cxo = PW // 2
L.append(f'''<g id="ornament" stroke="{CREAM_DIM}" stroke-width="1" fill="none">
  <line x1="{cxo}" y1="118" x2="{cxo}" y2="150"/>
  <g fill="{CREAM_DIM}" stroke="none">
    <path d="M {cxo} 126 l 3.2 8.2 8.2 3.2 -8.2 3.2 -3.2 8.2 -3.2 -8.2 -8.2 -3.2 8.2 -3.2 z" transform="rotate(45 {cxo} 137.5) scale(0.8) translate({cxo*0.25} {137.5*0.25})" opacity="0"/>
  </g>
  <path d="M {cxo-9} 134 L {cxo} 128 L {cxo+9} 134 L {cxo} 140 Z" fill="{CREAM_DIM}" stroke="none"/>
</g>''')

# --- headline
L.append(f'''<g id="headline" fill="{CREAM}" font-family="Didot, 'Bodoni 72', 'Playfair Display', serif" font-size="40" text-anchor="middle" letter-spacing="1.5">
  <text x="{PW//2}" y="230">LOCATING THE BEST</text>
  <text x="{PW//2}" y="278">ENVIRONMENT FOR YOU</text>
</g>''')

# --- intro body copy (original text), slight rotation like the photo
body1 = [
 "Locational astrology is a tool for understanding your path in",
 "life. This niche form of the practice blends mapmaking and",
 "charting techniques that describe how planetary energies may",
 "color your experience of a place. Tracking planetary lines is",
 "an old craft, consulted by travellers for centuries when siting",
 "a home, a venture, or a season of rest. With modern mapping",
 "we can revisit this practice and apply it in a contemporary way."
]
ty = 318
lines = "".join(f'<tspan x="120" dy="{0 if i==0 else 19}">{esc(t)}</tspan>' for i, t in enumerate(body1))
L.append(f'''<g id="body-intro" transform="rotate(-2 420 380)">
  <text x="120" y="{ty}" fill="{CREAM_DIM}" font-family="Futura, 'Century Gothic', 'Avenir Next', sans-serif" font-size="14.5" letter-spacing="0.4">{lines}</text>
</g>''')

# --- moon plate -------------------------------------------------
MX, MY, MR = 300, 600, 150   # moon center in a frame
# frame (square, thin) — moon square sits offset left, per reference
fx, fy, fs = 150, 445, 310
L.append(f'<rect id="plate-frame" x="{fx}" y="{fy}" width="{fs}" height="{fs+20}" fill="none" stroke="{CREAM_DIM}" stroke-width="1"/>')
L.append(f'<text x="{fx+fs+18}" y="{fy+42}" fill="{CREAM_DIM}" font-family="Futura, sans-serif" font-size="10" letter-spacing="3">FIG. 01</text>')

moon = []
moon.append(f'<circle cx="{MX}" cy="{MY}" r="{MR}" fill="url(#moonGrad)"/>')
# maria (dark patches)
maria = [(-45,-55,52),(30,-20,38),(-10,25,44),(55,40,30),(-70,35,26),(20,75,30)]
moon_maria = "".join(
    f'<ellipse cx="{MX+dx}" cy="{MY+dy}" rx="{r}" ry="{r*random.uniform(0.7,1.0):.0f}" '
    f'fill="#857a63" opacity="{random.uniform(0.25,0.45):.2f}" '
    f'transform="rotate({random.randint(-40,40)} {MX+dx} {MY+dy})"/>'
    for dx, dy, r in maria)
moon.append(f'<g clip-path="url(#clipMoon)">{moon_maria}')
# craters
for _ in range(38):
    a = random.uniform(0, 2*math.pi); rr = MR * math.sqrt(random.random()) * 0.94
    cx = MX + rr*math.cos(a); cy = MY + rr*math.sin(a)
    cr = random.uniform(3, 14)
    moon.append(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{cr:.1f}" fill="none" stroke="#6f6553" stroke-width="{random.uniform(0.6,1.3):.2f}" opacity="{random.uniform(0.3,0.7):.2f}"/>')
    moon.append(f'<path d="M {cx-cr*0.7:.0f} {cy+cr*0.35:.0f} a {cr:.1f} {cr:.1f} 0 0 0 {cr*1.4:.1f} 0" fill="none" stroke="#4c4436" stroke-width="1" opacity="{random.uniform(0.25,0.5):.2f}"/>')
# stipple shading — heavier lower-right terminator
moon.append(stipple_circle(MX, MY, MR*0.98, 900, "#3d382c", 0.35, 1.1, bias=2.2, opacity=0.5))
moon.append(stipple_circle(MX+45, MY+45, MR*0.75, 500, "#332e24", 0.4, 1.3, bias=1.6, opacity=0.55))
moon.append(stipple_circle(MX-55, MY-55, MR*0.55, 220, "#f4eee0", 0.3, 0.9, bias=1.2, opacity=0.5))
moon.append('</g>')
moon.append(f'<circle cx="{MX}" cy="{MY}" r="{MR}" fill="none" stroke="#57503f" stroke-width="1"/>')
L.append(f'<g id="moon-plate">{"".join(moon)}</g>')

# orbit arc sweeping through the plate
L.append(f'<path id="orbit-arc" d="M -40 700 Q 420 560 900 660" fill="none" stroke="{CREAM_DIM}" stroke-width="1" opacity="0.7"/>')

# --- caption copy, angled
body2 = [
 "By projecting the natal chart over a world map in various",
 "ways, you can find supportive locations around the globe or",
 "within your hometown. There is a macro and a micro",
 "application of this cosmic science."
]
lines2 = "".join(f'<tspan x="96" dy="{0 if i==0 else 18}">{esc(t)}</tspan>' for i, t in enumerate(body2))
L.append(f'''<g id="body-caption" transform="rotate(-4 300 850)">
  <text x="96" y="828" fill="{CREAM_DIM}" font-family="Futura, 'Century Gothic', 'Avenir Next', sans-serif" font-size="13.5" letter-spacing="0.4">{lines2}</text>
</g>''')

# --- giant display word, cropped at left & bottom edges
L.append(f'''<g id="wordmark" clip-path="url(#clipLeft)">
  <text x="-42" y="1050" fill="{CREAM}" font-family="Didot, 'Bodoni 72', 'Playfair Display', serif" font-size="150" letter-spacing="4" transform="rotate(-3 0 1040)">ASTROCARTO</text>
</g>''')

add(f'<g id="page-left" clip-path="url(#clipLeft)">{"".join(L)}</g>')

# ================================================================ RIGHT PAGE
R = []
R.append(f'<rect x="{PW}" y="0" width="{PW}" height="{H}" fill="url(#chartVign)"/>')

CCX, CCY, CR = PW + PW/2, H/2, 500   # celestial chart circle (bleeds off page)

chart = []
# concentric rings + radial spokes (planisphere grid)
for r in (CR, CR*0.86, CR*0.62, CR*0.38, CR*0.16):
    chart.append(f'<circle cx="{CCX}" cy="{CCY}" r="{r:.0f}" fill="none" stroke="{INK}" stroke-width="1.2" opacity="0.75"/>')
for i in range(24):
    a = i * math.pi / 12
    x1 = CCX + CR*0.16*math.cos(a); y1 = CCY + CR*0.16*math.sin(a)
    x2 = CCX + CR*math.cos(a);      y2 = CCY + CR*math.sin(a)
    chart.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{INK}" stroke-width="0.6" opacity="0.35"/>')
# ecliptic band
chart.append(f'<ellipse cx="{CCX}" cy="{CCY}" rx="{CR*0.86:.0f}" ry="{CR*0.30:.0f}" fill="none" stroke="{INK}" stroke-width="1.4" opacity="0.6" transform="rotate(-24 {CCX} {CCY})"/>')

# constellation figures: stars + connecting lines + engraved swirl bodies
def constellation(cx, cy, scale, pts, swirl=True):
    s = []
    P = [(cx + px*scale, cy + py*scale) for px, py in pts]
    d = "M " + " L ".join(f"{x:.0f} {y:.0f}" for x, y in P)
    s.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="1.1" opacity="0.8"/>')
    for x, y in P:
        rr = random.uniform(2.2, 4.2)
        s.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rr:.1f}" fill="{INK}"/>')
        s.append(f'<g stroke="{INK}" stroke-width="0.8" opacity="0.9">'
                 f'<line x1="{x-rr*2.4:.0f}" y1="{y:.0f}" x2="{x+rr*2.4:.0f}" y2="{y:.0f}"/>'
                 f'<line x1="{x:.0f}" y1="{y-rr*2.4:.0f}" x2="{x:.0f}" y2="{y+rr*2.4:.0f}"/></g>')
    if swirl:  # engraved 'creature body' suggestion: flowing bezier around the figure
        x0, y0 = P[0]; x1, y1 = P[-1]
        mx, my = (x0+x1)/2 + 30*scale, (y0+y1)/2 - 24*scale
        s.append(f'<path d="M {x0:.0f} {y0:.0f} Q {mx:.0f} {my:.0f} {x1:.0f} {y1:.0f}" fill="none" stroke="{INK}" stroke-width="2.2" opacity="0.5" stroke-linecap="round"/>')
        s.append(f'<path d="M {x0:.0f} {y0:.0f} Q {mx+14:.0f} {my+26:.0f} {x1:.0f} {y1:.0f}" fill="none" stroke="{INK}" stroke-width="1" opacity="0.35"/>')
    return "".join(s)

figs = [
    (CCX-260, CCY-300, 1.15, [(-40,10),(-10,-18),(25,-6),(48,20),(30,52),(-5,44)]),
    (CCX+180, CCY-330, 1.0,  [(-50,0),(-20,-25),(15,-15),(40,10),(20,40)]),
    (CCX+300, CCY-60, 1.2,   [(-45,-20),(-10,0),(20,-22),(52,-4),(38,32),(0,40)]),
    (CCX+200, CCY+270, 1.1,  [(-40,20),(-15,-15),(20,-28),(46,0),(28,34)]),
    (CCX-240, CCY+300, 1.0,  [(-50,-10),(-18,15),(12,-12),(45,8),(60,-18)]),
    (CCX-330, CCY+60, 1.05,  [(-35,25),(-8,-8),(24,12),(40,-20),(10,-38)]),
    (CCX-40,  CCY-140, 0.9,  [(-30,0),(0,-24),(30,-4),(18,28),(-14,22)]),
    (CCX+40,  CCY+140, 0.95, [(-28,10),(2,-18),(30,6),(12,30)]),
]
for f in figs:
    chart.append(constellation(*f))

# scattered background stars over the whole right page
stars = []
for _ in range(150):
    x = random.uniform(PW+20, W-20); y = random.uniform(20, H-20)
    rr = random.uniform(0.6, 1.8)
    stars.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rr:.1f}" fill="{INK}" opacity="{random.uniform(0.3,0.8):.2f}"/>')
chart.append("".join(stars))

# engraved hatching texture (short random strokes, like old print grain)
hatch = []
for _ in range(260):
    x = random.uniform(PW+10, W-10); y = random.uniform(10, H-10)
    ln = random.uniform(6, 20); a = random.uniform(-0.5, 0.5)
    x2 = x + ln*math.cos(a); y2 = y + ln*math.sin(a)
    hatch.append(f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{INK}" stroke-width="0.5" opacity="{random.uniform(0.08,0.2):.2f}"/>')
chart.append("".join(hatch))

R.append(f'<g id="celestial-chart">{"".join(chart)}</g>')

# --- giant black "8" glyph overlaying the chart, cropped by page edges
# Built from two stacked ring shapes (even-odd), slightly rotated — editable vector, no font needed.
g8 = []
ETH = 66  # ring thickness
def ring(cx, cy, rx, ry):
    return (f'M {cx-rx} {cy} a {rx} {ry} 0 1 0 {2*rx} 0 a {rx} {ry} 0 1 0 {-2*rx} 0 Z '
            f'M {cx-rx+ETH} {cy} a {rx-ETH} {ry-ETH} 0 1 1 {2*(rx-ETH)} 0 a {rx-ETH} {ry-ETH} 0 1 1 {-2*(rx-ETH)} 0 Z ')
E8X = PW + 470
d8 = ring(E8X, 330, 235, 245) + ring(E8X + 26, 800, 262, 272)
g8.append(f'<path d="{d8}" fill="{BLACK}" fill-rule="evenodd" transform="rotate(4 {E8X} 560)"/>')
R.append(f'<g id="numeral-eight">{"".join(g8)}</g>')

# page-number footer
R.append(f'<text x="{W-90}" y="{H-52}" text-anchor="end" fill="{INK}" font-family="Futura, sans-serif" font-size="12" letter-spacing="3" opacity="0.9">ATLAS OF THE SKY</text>')

add(f'<g id="page-right" clip-path="url(#clipRight)">{"".join(R)}</g>')

# ================================================================ GUTTER + finish
add(f'<rect id="page-gutter" x="{PW-70}" y="0" width="140" height="{H}" fill="url(#gutter)"/>')
add(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" fill="none" stroke="#000" stroke-width="1" opacity="0.6"/>')

svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<!-- Astrocartography editorial spread — original artwork, Illustrator-compatible SVG 1.1 -->
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     version="1.1" width="{W}px" height="{H}px" viewBox="0 0 {W} {H}">
<title>Astrocarto — Locating the Best Environment for You</title>
{chr(10).join(frag)}
</svg>
'''
out = "/home/user/my-claude/design/astrocarto-spread.svg"
with open(out, "w") as f:
    f.write(svg)
print(f"wrote {out} ({len(svg)/1024:.0f} KB)")
