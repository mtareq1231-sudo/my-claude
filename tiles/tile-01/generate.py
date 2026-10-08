"""Generate SVG files for tile 01 (quatrefoil with red clovers and grey acanthus).

Coordinates: the 2x2 composition is centred on (0, 0) and spans -200..200.
A single tile is the top-left quarter (-200..0); the other three tiles in the
layout are the same tile rotated, so one stencil/mould set covers the floor.

Run:  python3 generate.py   ->  writes the .svg files next to this script.
"""
import math
import re
from pathlib import Path

OUT = Path(__file__).parent

# Colours sampled from the physical tile
BG = "#F1F0EB"      # off-white base
DARK = "#3B2A26"    # dark brown
RED = "#B5573F"     # terracotta
GREY = "#BEBDBA"    # light grey

# Quatrefoil band
LOBE_OFFSET = 100   # distance from centre to each lobe circle centre
LOBE_R_IN = 70.9    # inner edge radius of each lobe (inner edges meet at the spike tips)
LOBE_R_OUT = 88.5    # outer edge radius of each lobe


def f(x):
    return f"{x:.2f}".rstrip("0").rstrip(".")


def pt(p):
    return f"{f(p[0])} {f(p[1])}"


def diag_intersection(r, outer=True):
    """Where lobe circles (0,-d) and (-d,0) of radius r cross on the diagonal y=x."""
    d = LOBE_OFFSET
    disc = d * d - 2 * (d * d - r * r)
    t = (-d - math.sqrt(disc)) / 2 if outer else (-d + math.sqrt(disc)) / 2
    return t


def quatrefoil_path():
    """Dark band as one compound path: outer outline + inner hole (even-odd)."""
    ro, ri = LOBE_R_OUT, LOBE_R_IN
    a = diag_intersection(ro)   # outer cusps
    b = diag_intersection(ri)   # inner cusps = spike tips pointing at the clovers
    def ring(r, c):
        # go clockwise: TL -> TR (top lobe) -> BR (right) -> BL (bottom) -> TL (left)
        tl, tr, br, bl = (c, c), (-c, c), (-c, -c), (c, -c)
        return (f"M{pt(tl)} A{f(r)} {f(r)} 0 1 1 {pt(tr)} A{f(r)} {f(r)} 0 1 1 {pt(br)} "
                f"A{f(r)} {f(r)} 0 1 1 {pt(bl)} A{f(r)} {f(r)} 0 1 1 {pt(tl)}Z")
    return ring(ro, a) + " " + ring(ri, b)


def vesica(cx, cy, length, width):
    """Pointed leaf (almond), vertical."""
    h, w = length / 2, width / 2
    r = (h * h + w * w) / (2 * w)
    return (f"M{f(cx)} {f(cy - h)} A{f(r)} {f(r)} 0 0 1 {f(cx)} {f(cy + h)} "
            f"A{f(r)} {f(r)} 0 0 1 {f(cx)} {f(cy - h)}Z")


def clover(cx, cy, stem_angle_deg, lobe_r=8.2, lobe_d=10):
    """Three-lobed clover; the missing fourth lobe points along stem_angle."""
    parts = []
    for k in (1, 2, 3):
        a = math.radians(stem_angle_deg + 90 * k)
        parts.append(f'<circle cx="{f(cx + lobe_d * math.cos(a))}" cy="{f(cy + lobe_d * math.sin(a))}" r="{f(lobe_r)}"/>')
    # filled heart so the three lobes read as one piece
    parts.append(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(lobe_d * 0.9)}"/>')
    # short, thick neck on the stem side
    a = math.radians(stem_angle_deg)
    nx, ny = cx + 5 * math.cos(a), cy + 5 * math.sin(a)
    parts.append(f'<path d="M{f(cx)} {f(cy)} L{f(nx)} {f(ny)}" stroke-width="11" stroke-linecap="round"/>')
    return parts


def spline(points):
    """Smooth curve (Catmull-Rom as cubic Beziers) through points, without the initial M."""
    p = [points[0]] + list(points) + [points[-1]]
    out = []
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        out.append(f"C{pt(c1)} {pt(c2)} {pt(p2)}")
    return " ".join(out)


def mirror(points):
    """Mirror across the tile diagonal y = x."""
    return [(y, x) for x, y in points]


# Crescent in the top lobe (traced from the photo). Sharp point at the bottom,
# rounded hook at the top; it opens toward the inner clover.
CRESCENT = [(-25.5, -66), (-16, -70), (-10, -77.5), (-6.9, -87.5), (-6.2, -98.5), (-8.7, -108.7),
            (-15, -117.5), (-23.7, -125), (-32.5, -128.2), (-40, -129), (-48.7, -127),
            (-53.7, -122.5), (-56.2, -116), (-55.6, -110), (-52.5, -103.8), (-49.4, -100.3),
            (-47.5, -104.5), (-45.6, -110), (-41.2, -113.2), (-33.7, -113.8), (-26.2, -110),
            (-20.6, -102.5), (-18.1, -92.5), (-18.7, -83.7), (-20.6, -75), (-25.5, -66)]

# Acanthus leaf traced from the photo. It grows out of the corner stem on a
# short stalk, curls up toward the top edge, has three scallops on its inner
# edge and a hooked lower lobe. Each list is one smooth edge; corners sit
# between lists. The first and last points sit inside the stem.
LEAF_EDGES = [
    [(-144, -140), (-138.5, -144), (-135.5, -150), (-132.5, -159), (-127, -167.5), (-118.5, -174.5),
     (-110.5, -180), (-106, -186.5), (-104, -196)],
    [(-104, -196), (-98, -192.5), (-93.5, -186), (-93, -179.5), (-97.5, -172)],
    [(-97.5, -172), (-94, -167.5), (-95, -163), (-98.5, -160.5)],
    [(-98.5, -160.5), (-95, -157), (-96.5, -152), (-101, -148), (-105.5, -144),
     (-109, -140.5), (-113.5, -139)],
    [(-113.5, -139), (-116, -142), (-117.5, -147), (-121.5, -151.5), (-126.5, -150.5),
     (-129.5, -147), (-128.5, -141), (-126, -136), (-124, -128)],
]


def leaf_path(edges):
    return f"M{pt(edges[0][0])} " + " ".join(spline(e) for e in edges) + " Z"


def quarter_motif():
    """Everything in the top-left quarter of the composition (= one tile)."""
    dark, red, grey = [], [], []

    # crescents: one in the top lobe, its mirror in the left lobe; both cradle the inner clover
    for pts in (CRESCENT, mirror(CRESCENT)):
        dark.append(f'<path d="M{pt(pts[0])} {spline(pts)} Z"/>')

    # corner ornament: grey stem + two acanthus leaves, red clover at the tile corner
    grey.append('<path d="M-168 -168 L-97 -97" stroke-width="8" stroke-linecap="round"/>')
    grey.append(f'<path d="{leaf_path(LEAF_EDGES)}"/>')
    grey.append(f'<path d="{leaf_path([mirror(e) for e in LEAF_EDGES])}"/>')
    red += clover(-168, -168, 45)

    # inner clover at the tip of the band's spike
    red += clover(-55.5, -55.5, 225)
    # short rounded point where the band's two lobes meet on the outside
    dark.append('<path d="M-84 -84 L-95.5 -95.5" stroke-width="10" stroke-linecap="round"/>')
    return dark, red, grey


def layers(full):
    """Return SVG groups per colour. full=True draws all four quarters."""
    dark, red, grey = quarter_motif()
    if full:
        rot = ["", ' transform="scale(-1 1)"', ' transform="scale(1 -1)"', ' transform="scale(-1 -1)"']
    else:
        rot = [""]
    def group(name, colour, items, attr):
        body = "\n".join(f'      <g{t}>\n        ' + "\n        ".join(items) + "\n      </g>" for t in rot)
        return f'  <g id="{name}" {attr}>\n{body}\n  </g>'
    shared = [
        f'<path d="{quatrefoil_path()}" fill-rule="evenodd"/>',
        f'<circle cx="0" cy="0" r="32.75" fill="none" stroke="{DARK}" stroke-width="12.5"/>',
        f'<path d="{vesica(0, -141, 58, 30)}"/>',
        f'<path d="{vesica(0, 141, 58, 30)}"/>',
        f'<path d="{vesica(0, -141, 58, 30)}" transform="rotate(90)"/>',
        f'<path d="{vesica(0, -141, 58, 30)}" transform="rotate(-90)"/>',
    ]
    return "\n".join([
        group("grey", GREY, grey, f'fill="{GREY}" stroke="{GREY}" stroke-width="0"'),
        f'  <g id="dark-brown" fill="{DARK}" stroke="{DARK}" stroke-width="0">\n    '
        + "\n    ".join(shared) + "\n" + "\n".join(
            f'      <g{t}>\n        ' + "\n        ".join(dark) + "\n      </g>" for t in rot) + "\n  </g>",
        group("terracotta", RED, red, f'fill="{RED}" stroke="{RED}" stroke-width="0"'),
    ])


def svg(view, size_mm, full, title):
    x, y, w, h = view
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x} {y} {w} {h}" width="{size_mm[0]}mm" height="{size_mm[1]}mm">
  <title>{title}</title>
  <defs><clipPath id="tile"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath></defs>
  <rect id="background" x="{x}" y="{y}" width="{w}" height="{h}" fill="{BG}"/>
  <g clip-path="url(#tile)">
{layers(full)}
  </g>
</svg>
"""


if __name__ == "__main__":
    # one tile = 200 units = 200 mm (standard 20x20 cement tile)
    (OUT / "tile-01-single.svg").write_text(svg((-200, -200, 200, 200), (200, 200), True, "Tile 01 - single tile"))
    (OUT / "tile-01-4up.svg").write_text(svg((-200, -200, 400, 400), (400, 400), True, "Tile 01 - 2x2 layout"))
    print("written")
