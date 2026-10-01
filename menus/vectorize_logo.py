"""Trace a flat-colour raster logo into vector paths (JSON) for sharp large-format print.

Usage: python3 menus/vectorize_logo.py SRC.png OUT.json "#RRGGBB:name" ...
Colours are listed bottom-to-top; each pixel goes to its nearest listed colour
(white/background excluded), so later layers sit on top of earlier ones.
"""
import json
import sys

import numpy as np
import potrace
from PIL import Image

SCALE = 3


def hex2rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=float)


def main(src, out, specs):
    im = Image.open(src).convert("RGB")
    a = np.asarray(im, dtype=float)
    bg = np.all(a > 252, axis=2)                         # pure white page
    ys, xs = np.where(~bg)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    im = im.crop((x0, y0, x1, y1))
    im = im.resize((im.width * SCALE, im.height * SCALE), Image.LANCZOS)
    a = np.asarray(im, dtype=float)
    bg = np.all(a > 252, axis=2)

    cols = [(hex2rgb(s.split(":")[0]), s.split(":")[1], s.split(":")[0]) for s in specs]
    # White competes as well, so pale anti-aliased fringes stay background.
    dist = np.stack([np.linalg.norm(a - 255, axis=2)] + [np.linalg.norm(a - c, axis=2) for c, _, _ in cols])
    nearest = dist.argmin(axis=0) - 1
    bg |= nearest < 0

    layers = []
    for i, (_, name, hx) in enumerate(cols):
        # A layer covers its own pixels and everything stacked above it, so
        # anti-aliased seams between colours never show a gap.
        mask = (nearest >= i) & ~bg
        # potracer traces False pixels as ink, so pass the inverted mask.
        plist = potrace.Bitmap(~mask).trace(turdsize=8, alphamax=1.0,
                                            opticurve=True, opttolerance=0.2)
        curves = []
        for curve in plist:
            segs = []
            for s in curve.segments:
                if s.is_corner:
                    segs.append(["L", s.c.x, s.c.y, s.end_point.x, s.end_point.y])
                else:
                    segs.append(["C", s.c1.x, s.c1.y, s.c2.x, s.c2.y, s.end_point.x, s.end_point.y])
            curves.append({"start": [curve.start_point.x, curve.start_point.y], "segs": segs})
        layers.append({"name": name, "color": hx, "curves": curves})
        print(name, len(curves), "curves")

    json.dump({"w": im.width, "h": im.height, "layers": layers}, open(out, "w"))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3:])
