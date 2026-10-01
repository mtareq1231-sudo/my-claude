"""Trace a flat-colour raster logo into a clean, scalable SVG.

Usage:
  python3 menus/logo_to_svg.py SRC OUT.svg --bg "#RRGGBB" "#RRGGBB:name" ...

Layers are listed bottom-to-top. The source is upscaled and smoothed before
tracing so curves come out clean. The background colour is dropped
(transparent), except where a layer uses the background colour itself: that
layer is limited to the inside of the layers below it (white letters on a
coloured disc, for example) and the layer below is traced solid.
"""
import argparse

import numpy as np
import potrace
from PIL import Image, ImageFilter
from scipy import ndimage as ndi

SCALE = 4


def hex2rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=float)


def trace(mask, turd):
    paths = []
    for cv in potrace.Bitmap(~mask).trace(turdsize=turd, alphamax=1.0, opticurve=True, opttolerance=0.2):
        d = [f"M{cv.start_point.x / SCALE:.2f} {cv.start_point.y / SCALE:.2f}"]
        for s in cv.segments:
            if s.is_corner:
                d.append(f"L{s.c.x / SCALE:.2f} {s.c.y / SCALE:.2f}L{s.end_point.x / SCALE:.2f} {s.end_point.y / SCALE:.2f}")
            else:
                d.append(f"C{s.c1.x / SCALE:.2f} {s.c1.y / SCALE:.2f} {s.c2.x / SCALE:.2f} {s.c2.y / SCALE:.2f} "
                         f"{s.end_point.x / SCALE:.2f} {s.end_point.y / SCALE:.2f}")
        paths.append("".join(d) + "Z")
    return paths


def classify(a, palette):
    """Nearest palette colour, treating edge pixels as blends of two colours.

    An anti-aliased pixel lies on the line between the two colours it mixes,
    so pick the closest colour pair and take whichever end the pixel is nearer
    to. Plain nearest-colour would send grey edges of black text to a
    mid-tone colour such as gold.
    """
    best_d = np.full(a.shape[:2], np.inf)
    cls = np.zeros(a.shape[:2], int)
    for i in range(len(palette)):
        for j in range(i, len(palette)):
            p, q = palette[i], palette[j]
            v = q - p
            t = np.clip(((a - p) @ v) / max(v @ v, 1e-9), 0, 1) if j > i else np.zeros(a.shape[:2])
            d = np.linalg.norm(a - (p + t[..., None] * v), axis=2)
            better = d < best_d
            best_d[better] = d[better]
            cls[better] = np.where(t[better] < 0.5, i, j)
    return cls


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--bg", required=True)
    ap.add_argument("--scale", type=int, default=4, help="upscale factor before tracing (lower for big sources)")
    ap.add_argument("layers", nargs="+")
    args = ap.parse_args()
    global SCALE
    SCALE = args.scale

    im = Image.open(args.src).convert("RGB")
    im = im.resize((im.width * SCALE, im.height * SCALE), Image.LANCZOS).filter(ImageFilter.GaussianBlur(SCALE * 0.6))
    a = np.asarray(im, dtype=float)
    bg = hex2rgb(args.bg)
    specs = [(s.split(":")[0], s.split(":")[1]) for s in args.layers]
    palette = [bg] + [hex2rgb(h) for h, _ in specs]
    cls = classify(a, palette)   # 0 = background

    svg_layers, below = [], np.zeros(cls.shape, bool)
    for i, (hx, name) in enumerate(specs, start=1):
        if np.allclose(hex2rgb(hx), bg):
            mask = (cls == 0) & below            # background colour inside the shapes below
        else:
            # This colour plus every colour above it, so seams never show a gap.
            mask = np.isin(cls, [j for j in range(i, len(palette)) if not np.allclose(palette[j], bg)])
            if any(np.allclose(hex2rgb(h), bg) for h, _ in specs[i:]):
                mask = ndi.binary_fill_holes(mask)   # solid under a background-coloured layer
        below |= mask
        paths = trace(mask, turd=8 * SCALE * SCALE)
        svg_layers.append(f'  <path id="{name}" fill="{hx}" fill-rule="evenodd" d="{" ".join(paths)}"/>')
        print(name, len(paths), "paths")

    ys, xs = np.where(below)
    x0, y0 = xs.min() / SCALE, ys.min() / SCALE
    w, h = (xs.max() - xs.min()) / SCALE, (ys.max() - ys.min()) / SCALE
    with open(args.out, "w") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0:.1f} {y0:.1f} {w:.1f} {h:.1f}" '
                f'width="{w:.0f}" height="{h:.0f}">\n' + "\n".join(svg_layers) + "\n</svg>\n")
    print("wrote", args.out)


if __name__ == "__main__":
    main()
