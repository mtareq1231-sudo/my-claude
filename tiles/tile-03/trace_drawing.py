"""Trace tile 03 (12-point rosette quarter tile) from the line drawing into SVGs.

The drawing shows four tiles laid 2x2. Each tile is a mirror copy of the top-left one, and
the rosette centre is the corner where the four tiles meet. So only the top-left tile is
traced; the 2x2 pattern is built from it by mirroring.

Every enclosed white area of the drawing except the strapwork (the one big connected area)
is a piece. Each piece outline is fitted with straight edges snapped to the design's angles:
multiples of 15 degrees for the rosette, plus 36/54 degrees for the five-point star field.

Usage:  python3 trace_drawing.py DRAWING.png OUT_DIR
Needs:  numpy, Pillow
"""
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from vectorize import clip_polygon, label, offset_polygon, straight_polygon, trace  # noqa: E402

CROP = 366                    # top-left tile of the drawing, frame included
LO, HI = 1.5, 364.5           # centre lines of the tile's frame (pixel-corner coordinates)
LINE = 3.0                    # drawn line width, px
TILE_MM = 200.0               # finished tile size
MM = TILE_MM / (HI - LO)
ANGLES = sorted(set([15 * k for k in range(12)] + [36, 54, 126, 144]))

# Fez zellige palette (ivory strapwork, black ground, gold, cobalt and turquoise)
IVORY, BLACK, GOLD, BLUE, TEAL = "#EFE8D6", "#1C1B1D", "#C8902C", "#3F62A8", "#2E9A92"
JOINT = "#D9D0BC"             # thin joint line around each coloured piece


def trace_tile(path):
    a = np.asarray(Image.open(path).convert("L"))[:CROP, :CROP]
    lab, n = label(a >= 128)
    sizes = [(lab == k).sum() for k in range(1, n + 1)]
    strapwork = 1 + int(np.argmax(sizes))
    pieces = []
    for k in range(1, n + 1):
        comp = lab == k
        if k == strapwork or comp.sum() < 30:
            continue
        inner = straight_polygon(trace(comp), ANGLES, tol=2.5, eps=1.5, tip=2.0)
        outline = clip_polygon(offset_polygon(inner, LINE / 2), LO, LO, HI, HI)
        ys, xs = np.nonzero(comp)
        cx, cy = xs.mean() + 0.5, ys.mean() + 0.5
        pieces.append({"pts": outline, "r": math.hypot(HI - cx, HI - cy),
                       "phi": math.degrees(math.atan2(HI - cy, HI - cx)), "area": int(comp.sum())})
    return pieces


def colour(p):
    """Colour by position in the rosette (r = distance from the rosette centre, phi = angle)."""
    r, phi = p["r"], p["phi"]
    on_15 = min(abs(phi - a) for a in (15, 45, 75)) < 8      # slivers, arrows
    if r < 60:
        return GOLD                       # central 12-point star
    if r < 120:
        return BLACK                      # slivers around the star
    if r < 230:
        return BLACK                      # petals
    if r < 300:
        return BLUE if abs(phi - 45) < 8 else TEAL if on_15 else BLACK   # arrows
    if r < 350:
        return GOLD                       # ring of small stars
    if r < 395:
        return GOLD if abs(phi - 45) < 8 else BLACK     # five-point star / long edge pieces
    if r < 430:
        return TEAL                       # pentagons beside the five-point star
    if r < 470:
        return BLUE                       # small pieces near the tile corner
    return TEAL                           # corner square


def to_mm(pts, flip_x=False, flip_y=False, dx=0.0, dy=0.0):
    out = []
    for x, y in pts:
        X = (x - LO) * MM
        Y = (y - LO) * MM
        if flip_x:
            X = 2 * TILE_MM - X
        if flip_y:
            Y = 2 * TILE_MM - Y
        out.append((X + dx, Y + dy))
    return out


def d(pts):
    return "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in pts) + " Z"


COPIES = {"top-left": (False, False), "top-right": (True, False),
          "bottom-left": (False, True), "bottom-right": (True, True)}


def svg_doc(size, title, body):
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size:g} {size:g}" width="{size:g}mm" height="{size:g}mm">
  <title>{title}</title>
{body}
</svg>
'''


def coloured(pieces, copies):
    size = TILE_MM * (2 if len(copies) > 1 else 1)
    body = [f'  <rect id="strapwork" width="{size:g}" height="{size:g}" fill="{IVORY}"/>']
    for name, (fx, fy) in copies.items():
        rows = [f'      <path fill="{colour(p)}" d="{d(to_mm(p["pts"], fx, fy))}"/>' for p in pieces]
        body.append(f'  <g id="tile-{name}" stroke="{JOINT}" stroke-width="0.5" stroke-linejoin="round">\n'
                    + "\n".join(rows) + "\n  </g>")
    joints = [f'<rect width="{size:g}" height="{size:g}"/>']
    if len(copies) > 1:
        joints += [f'<path d="M{TILE_MM:g} 0 V{size:g} M0 {TILE_MM:g} H{size:g}"/>']
    body.append(f'  <g id="tile-joints" fill="none" stroke="#8C8576" stroke-width="0.6">{"".join(joints)}</g>')
    return svg_doc(size, "Tile 03 - 12-point rosette, coloured", "\n".join(body))


def line_art(pieces, copies):
    size = TILE_MM * (2 if len(copies) > 1 else 1)
    w = LINE * MM
    body = []
    for name, (fx, fy) in copies.items():
        rows = [f'      <path d="{d(to_mm(p["pts"], fx, fy))}"/>' for p in pieces]
        body.append(f'  <g id="tile-{name}" fill="#FFFFFF" stroke="#000000" stroke-width="{w:.2f}" '
                    f'stroke-linejoin="miter">\n' + "\n".join(rows) + "\n  </g>")
    frames = "".join(f'<rect x="{x:g}" y="{y:g}" width="{TILE_MM:g}" height="{TILE_MM:g}"/>'
                     for x in range(0, int(size), int(TILE_MM)) for y in range(0, int(size), int(TILE_MM)))
    body.append(f'  <g id="tile-frames" fill="none" stroke="#000000" stroke-width="{w:.2f}">{frames}</g>')
    return svg_doc(size, "Tile 03 - 12-point rosette, line drawing", "\n".join(body))


if __name__ == "__main__":
    src, out = sys.argv[1], Path(sys.argv[2])
    pieces = trace_tile(src)
    one = {"top-left": COPIES["top-left"]}
    (out / "tile-03-quarter.svg").write_text(coloured(pieces, one))
    (out / "tile-03-pattern.svg").write_text(coloured(pieces, COPIES))
    (out / "tile-03-quarter-lines.svg").write_text(line_art(pieces, one))
    (out / "tile-03-pattern-lines.svg").write_text(line_art(pieces, COPIES))
    print(len(pieces), "pieces per tile")
