"""Trace tile 02 (50x50 cm zellige panel, 12-point rosette) from a photo into an SVG.

The panel is symmetric, which the tracing leans on:
  * the whole square has 4-fold mirror symmetry (D4);
  * the rosette (every piece away from the border) has 12-fold mirror symmetry (D12);
  * every edge in the design runs at a multiple of 15 degrees.

All copies of a piece in the photo are lined up on their centres and averaged, which
cancels glaze, lighting and hand-laying wobble without shrinking small pieces. The averaged
shape is traced, its edges are snapped to 15 degree lines, and the exact symmetric copies
are generated from it. The central star is constructed (12 right-angled points).

Usage:  python3 trace_photo.py PHOTO.jpg OUT_DIR
Needs:  numpy, Pillow
"""
import json
import math
import sys
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

N = 1000                 # working grid: 1000 px = 500 mm panel
C = N / 2
MM = 500 / N             # mm per grid px
R_ROSETTE = 440          # pieces closer to the centre than this belong to the 12-fold rosette
SNAP = 15.0              # all edges run at multiples of this angle

# panel corners in the supplied product photo (TL, TR, BR, BL), measured by hand
PHOTO_CORNERS = [(74, 72), (661.5, 72), (662, 664.5), (75.5, 664)]

# central 12-point star: right-angled points (edges at 45 deg to the radius)
STAR_TIP_R = 86.0
STAR_VALLEY_R = STAR_TIP_R * math.sqrt(2 / 3)   # = 0.8165 * tip radius for 90-degree points

GREEN, BEIGE, GROUT = "#2A6650", "#DCCDC9", "#F3EDE9"
GROUT_W = 5.0            # bright grout showing around each green piece, grid px (2.5 mm)


# ------------------------------------------------------------------ photo -> symmetric mask
def rectify(src):
    A, b = [], []
    for (x, y), (u, v) in zip([(0, 0), (N, 0), (N, N), (0, N)], PHOTO_CORNERS):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); b.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); b.append(v)
    coef = np.linalg.solve(np.array(A, float), np.array(b, float))
    return Image.open(src).convert("RGB").transform((N, N), Image.PERSPECTIVE, tuple(coef), Image.BICUBIC)


def green_mask(img):
    a = np.asarray(img).astype(float)
    # green-ness 0..1: beige strips have red above green (G-R ~ -20), glazed green has G-R 15..60
    g = np.clip((a[..., 1] - a[..., 0] + 5) / 30.0, 0, 1)
    pad = 5   # the outermost pixels are chipped edge / background: copy inward values out
    g[:, :pad] = g[:, pad:pad + 1]; g[:, -pad:] = g[:, -pad - 1:-pad]
    g[:pad, :] = g[pad:pad + 1, :]; g[-pad:, :] = g[-pad - 1:-pad, :]
    return g > 0.5


def label(m):
    lab = np.zeros(m.shape, np.int32)
    n = 0
    for i0, j0 in zip(*np.nonzero(m)):
        if lab[i0, j0]:
            continue
        n += 1
        lab[i0, j0] = n
        q = deque([(i0, j0)])
        while q:
            i, j = q.popleft()
            for a, b in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
                if 0 <= a < N and 0 <= b < N and m[a, b] and not lab[a, b]:
                    lab[a, b] = n
                    q.append((a, b))
    return lab, n


def trace(comp):
    """Outer boundary of a 4-connected component as pixel-corner points (crack following)."""
    ys, xs = np.nonzero(comp)
    i0 = ys.min()
    j0 = xs[ys == i0].min()

    def inside(px, py):
        return 0 <= px < N and 0 <= py < N and comp[py, px]

    p, d = (j0, i0), (1, 0)
    start, pts = (p, d), []
    while True:
        pts.append(p)
        q = (p[0] + d[0], p[1] + d[1])
        right, left = (-d[1], d[0]), (d[1], -d[0])
        ahead_r = (math.floor(q[0] + d[0] / 2 + right[0] / 2), math.floor(q[1] + d[1] / 2 + right[1] / 2))
        ahead_l = (math.floor(q[0] + d[0] / 2 + left[0] / 2), math.floor(q[1] + d[1] / 2 + left[1] / 2))
        if not inside(*ahead_r):
            d = right
        elif inside(*ahead_l):
            d = left
        p = q
        if (p, d) == start:
            return np.array(pts, float)


# ------------------------------------------------------------------ contour -> straight polygon
def douglas_peucker(pts, eps):
    keep = {0, len(pts) - 1}
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        if b <= a + 1:
            continue
        p, v = pts[a], pts[b] - pts[a]
        L = max(np.hypot(*v), 1e-9)
        seg = pts[a + 1:b]
        dist = np.abs(v[0] * (seg[:, 1] - p[1]) - v[1] * (seg[:, 0] - p[0])) / L
        k = int(np.argmax(dist))
        if dist[k] > eps:
            m = a + 1 + k
            keep.add(m)
            stack += [(a, m), (m, b)]
    return sorted(keep)


def corner_indices(contour, eps=2.5):
    far = int(np.argmax(np.hypot(*(contour - contour[0]).T)))
    a = list(range(0, far + 1))
    b = list(range(far, len(contour))) + [0]
    idx = [a[k] for k in douglas_peucker(contour[a], eps)] + [b[k] for k in douglas_peucker(contour[b], eps)[1:-1]]
    return sorted(set(idx))


def snap_dir(u):
    ang = math.degrees(math.atan2(u[1], u[0])) % 180
    r = math.radians(round(ang / SNAP) * SNAP % 180)
    return np.array([math.cos(r), math.sin(r)])


def intersect(l1, l2):
    (p, u), (q, v) = l1, l2
    den = u[0] * v[1] - u[1] * v[0]
    if abs(den) < 1e-6:
        return None
    t = ((q[0] - p[0]) * v[1] - (q[1] - p[1]) * v[0]) / den
    return p + t * u


def merge_parallel(lines):
    changed = True
    while changed and len(lines) > 3:
        changed = False
        for i in range(len(lines)):
            j = (i + 1) % len(lines)
            if abs(lines[i][1][0] * lines[j][1][1] - lines[i][1][1] * lines[j][1][0]) < 1e-6:
                c1, u1, s1, b1, d1 = lines[i]; c2, u2, s2, b2, d2 = lines[j]
                lines[i] = [(c1 * s1 + c2 * s2) / (s1 + s2), u1, s1 + s2, b1 or b2, d1 + d2]
                del lines[j]
                changed = True
                break


def edge_lines(contour):
    """One straight line per contour run: (point, unit dir snapped to 15 deg, length, on_border)."""
    idx = corner_indices(contour)
    n = len(contour)
    lines = []
    for k in range(len(idx)):
        a, b = idx[k], idx[(k + 1) % len(idx)]
        span = (b - a) % n
        seg = np.array([contour[(a + t) % n] for t in range(span + 1)])
        core = seg[2:len(seg) - 2] if span > 10 else seg
        c = core.mean(axis=0)
        u = snap_dir(np.linalg.svd(core - c)[2][0])
        border = False
        if np.all(np.abs(seg[:, 0]) < 0.5) or np.all(np.abs(seg[:, 0] - N) < 0.5):
            c, u, border = np.array([seg[0, 0], 0.0]), np.array([0.0, 1.0]), True
        if np.all(np.abs(seg[:, 1]) < 0.5) or np.all(np.abs(seg[:, 1] - N) < 0.5):
            c, u, border = np.array([0.0, seg[0, 1]]), np.array([1.0, 0.0]), True
        lines.append([c, u, float(span), border, seg[-1] - seg[0]])
    merge_parallel(lines)
    return lines


def vertices(lines):
    out = []
    for k in range(len(lines)):
        p = intersect((lines[k - 1][0], lines[k - 1][1]), (lines[k][0], lines[k][1]))
        out.append(p if p is not None else lines[k][0])
    return np.array(out)


def straight_polygon(contour, tol=4.0):
    """Polygon of 15-degree edges; edges that create spikes away from the outline are dropped."""
    lines = edge_lines(contour)
    while len(lines) > 3:
        poly = vertices(lines)
        dist = np.array([0.0 if (lines[i - 1][3] or lines[i][3]) else np.min(np.hypot(*(contour - v).T))
                         for i, v in enumerate(poly)])
        k = int(np.argmax(dist))
        if dist[k] > tol:
            a, b = (k - 1) % len(lines), k
            del lines[a if lines[a][2] < lines[b][2] else b]
            merge_parallel(lines)
            continue
        # tiny edges (< 3 px) and edges running backwards against the outline are corner
        # noise: let their neighbours meet directly
        vec = np.roll(poly, -1, axis=0) - poly
        edge = np.hypot(*vec.T)
        tiny = [i for i in range(len(lines))
                if not lines[i][3] and (edge[i] < 3 or vec[i] @ lines[i][4] < 0)]
        if not tiny:
            return poly
        del lines[tiny[0]]
        merge_parallel(lines)
    return vertices(lines)


# ------------------------------------------------------------------ symmetry
def group(n):
    """Dihedral group of order 2n about the panel centre."""
    mirror = np.array([[-1.0, 0.0], [0.0, 1.0]])
    els = []
    for k in range(n):
        a = 2 * math.pi * k / n
        R = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
        els += [R, R @ mirror]
    return els


def apply(g, pts):
    return (np.asarray(pts) - C) @ g.T + C


def in_wedge(pt, lo, hi):
    x, y = pt[0] - C, C - pt[1]
    return math.hypot(x, y) < 2 or lo - 1 <= math.degrees(math.atan2(y, x)) <= hi + 1


def raster(poly):
    im = Image.new("1", (N, N), 0)
    ImageDraw.Draw(im).polygon([(float(x), float(y)) for x, y in poly], fill=1)
    return np.asarray(im, bool)


def symmetrise(pts, g, comp):
    """Make a piece that sits on mirror g exactly symmetric about it."""
    img = apply(g, pts)
    if len(img) == len(pts):
        dists = np.hypot(*(pts[:, None, :] - img[None, :, :]).transpose(2, 0, 1))
        j = dists.argmin(axis=1)
        if len(set(j)) == len(pts) and dists[np.arange(len(pts)), j].max() <= 6:
            return (pts + img[j]) / 2
    # vertices don't pair up: rebuild from whichever half matches the photo better
    w, v = np.linalg.eig(g)
    ax = np.real(v[:, np.argmin(np.abs(w - 1))])
    nrm = np.array([-ax[1], ax[0]])
    best, best_iou = pts, -1.0
    for sgn in (1, -1):
        half = []
        for i in range(len(pts)):
            a, b = pts[i] - C, pts[(i + 1) % len(pts)] - C
            da, db = sgn * (nrm @ a), sgn * (nrm @ b)
            if da >= 0:
                half.append(a + C)
            if (da >= 0) != (db >= 0):
                half.append(a + da / (da - db) * (b - a) + C)
        on = [i for i, p in enumerate(half) if abs(nrm @ (p - C)) < 1e-6]
        if len(on) < 2:
            continue
        seq = half[on[0]:] + half[:on[0]]
        if abs(nrm @ (seq[1] - C)) < 1e-6:
            seq = [seq[0]] + seq[1:][::-1]
        full = np.array(seq + list(apply(g, np.array(seq))[::-1][1:-1]))
        r = raster(full)
        iou = (r & comp).sum() / max((r | comp).sum(), 1)
        if iou > best_iou:
            best, best_iou = full, iou
    return best


def star():
    pts = []
    for k in range(12):
        for r, off in ((STAR_TIP_R, 0), (STAR_VALLEY_R, 15)):
            a = math.radians(90 + 30 * k + off)
            pts.append((C + r * math.cos(a), C - r * math.sin(a)))
    return np.array(pts)


def piece_types(mask):
    """Group the photo's pieces into types: all copies of one piece under the symmetry group.

    Each copy is mapped back into the fundamental wedge and centred on the type's mean
    position before averaging, so slightly misplaced hand-laid pieces don't shrink the shape.
    """
    lab, n = label(mask)
    yy, xx = np.mgrid[0:N, 0:N]
    G12, G4 = group(12), group(4)
    types = []
    for k in range(1, n + 1):
        comp = lab == k
        if comp.sum() < 30:
            continue
        cen = np.array([xx[comp].mean() + 0.5, yy[comp].mean() + 0.5])
        r = math.hypot(*(cen - C))
        touches = bool(comp[0].any() or comp[-1].any() or comp[:, 0].any() or comp[:, -1].any())
        kind = "star" if r < 30 else "rosette" if (r < R_ROSETTE - 15 and not touches) else "field"
        els = G12 if kind != "field" else G4
        wedge = (75, 90) if kind != "field" else (45, 90)
        g = next(g for g in els if in_wedge(apply(g, [cen])[0], *wedge))
        cc = apply(g, [cen])[0]
        for t in types:
            if t["kind"] == kind and np.hypot(*(t["cens"][0] - cc)) < 28:
                break
        else:
            t = {"kind": kind, "els": els, "touches": touches, "items": [], "cens": []}
            types.append(t)
        t["items"].append((g, cc, comp))
        t["cens"].append(cc)
        t["touches"] = t["touches"] or touches
    return types


def type_mirror(t):
    """The mirror a piece type sits on (its centre is within 6 px of the mirror line), if any."""
    cc = np.mean(t["cens"], axis=0)
    for g in t["els"]:
        if np.linalg.det(g) < 0 and np.hypot(*(apply(g, [cc])[0] - cc)) < 12:
            return g
    return None


def average_type(t):
    """Canonical mask of one piece type: aligned average of all its copies.

    A type that sits on a mirror is centred exactly on the mirror line and averaged together
    with its mirror image, so the result is symmetric before it is traced.
    """
    cc = np.mean(t["cens"], axis=0)
    mirror = type_mirror(t)
    if mirror is not None:
        cc = (cc + apply(mirror, [cc])[0]) / 2          # nearest point on the mirror line
    copies = [(g, c_i, comp) for g, c_i, comp in t["items"]]
    if mirror is not None:
        copies += [(mirror @ g, apply(mirror, [c_i])[0], comp) for g, c_i, comp in t["items"]]
    acc = np.zeros((N, N))
    ys, xs = np.mgrid[0:N, 0:N]
    q = np.stack([xs.ravel() + 0.5, ys.ravel() + 0.5], axis=1)
    for g, c_i, comp in copies:
        shift = np.zeros(2) if t["touches"] else (cc - c_i)
        p = (q - shift - C) @ g + C          # g is orthogonal: inverse = transpose
        px, py = np.floor(p[:, 0]).astype(int), np.floor(p[:, 1]).astype(int)
        ok = (px >= 0) & (px < N) & (py >= 0) & (py < N)
        v = np.zeros(len(q))
        v[ok] = comp[py[ok], px[ok]]
        acc += v.reshape(N, N)
    return acc / len(copies) > 0.5, cc


def trace_pieces(mask):
    out = []
    for t in piece_types(mask):
        if t["kind"] == "star":
            out.append({"kind": "star", "pts": star().tolist()})
            continue
        comp, cen = average_type(t)
        lab, n = label(comp)
        if n > 1:   # keep the main blob
            sizes = [(lab == i).sum() for i in range(1, n + 1)]
            comp = lab == (1 + int(np.argmax(sizes)))
        els, kind = t["els"], t["kind"]
        poly = straight_polygon(trace(comp))
        for g in els:
            if np.linalg.det(g) < 0 and np.hypot(*(apply(g, [cen])[0] - cen)) < 12:
                poly = symmetrise(poly, g, comp)
        seen = []
        for g in els:
            img = apply(g, poly)
            c = img.mean(axis=0)
            if any(np.hypot(*(c - s)) < 4 for s in seen):
                continue
            seen.append(c)
            out.append({"kind": kind, "pts": np.clip(img, 0, N).tolist()})
    return out


# ------------------------------------------------------------------ SVG
def svg(pieces):
    def path(pts):
        return "M" + " L".join(f"{x * MM:.2f} {y * MM:.2f}" for x, y in pts) + " Z"
    rows = "\n".join(f'      <path d="{path(p["pts"])}"/>' for p in pieces)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="500mm" height="500mm">
  <title>Tile 02 - zellige 12-point rosette, 50 x 50 cm</title>
  <defs><clipPath id="panel"><rect width="500" height="500"/></clipPath></defs>
  <rect id="white-strips" width="500" height="500" fill="{BEIGE}"/>
  <g clip-path="url(#panel)">
    <g id="grout" fill="{GROUT}" stroke="{GROUT}" stroke-width="{2 * GROUT_W * MM:.2f}" stroke-linejoin="round">
{rows}
    </g>
    <g id="green-pieces" fill="{GREEN}">
{rows}
    </g>
  </g>
</svg>
'''


def cut_lines(pieces):
    """Outline-only version: one closed path per green piece plus the panel edge."""
    def path(pts):
        return "M" + " L".join(f"{x * MM:.2f} {y * MM:.2f}" for x, y in pts) + " Z"
    rows = "\n".join(f'    <path d="{path(p["pts"])}"/>' for p in pieces)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="500mm" height="500mm">
  <title>Tile 02 - cut lines, 50 x 50 cm</title>
  <rect id="panel-edge" width="500" height="500" fill="none" stroke="#000" stroke-width="0.3"/>
  <g id="green-piece-outlines" fill="none" stroke="#000" stroke-width="0.3">
{rows}
  </g>
</svg>
'''


if __name__ == "__main__":
    src, out = sys.argv[1], Path(sys.argv[2])
    rect = rectify(src)
    pieces = trace_pieces(green_mask(rect))
    (out / "tile-02.svg").write_text(svg(pieces))
    (out / "tile-02-cut-lines.svg").write_text(cut_lines(pieces))
    print(len(pieces), "pieces ->", out / "tile-02.svg")
