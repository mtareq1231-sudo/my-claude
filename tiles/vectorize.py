"""Shared helpers for turning a traced tile image into straight-edged polygons.

Used by the per-tile scripts (tile-02/trace_photo.py, tile-03/trace_drawing.py).
Coordinates are pixel corners: pixel (row i, col j) covers [j, j+1] x [i, i+1].
"""
import math
from collections import deque

import numpy as np


def label(m):
    """4-connected components of a boolean image: (labels, count)."""
    H, W = m.shape
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
                if 0 <= a < H and 0 <= b < W and m[a, b] and not lab[a, b]:
                    lab[a, b] = n
                    q.append((a, b))
    return lab, n


def trace(comp):
    """Outer boundary of a 4-connected component as pixel-corner points (crack following)."""
    H, W = comp.shape
    ys, xs = np.nonzero(comp)
    i0 = ys.min()
    j0 = xs[ys == i0].min()

    def inside(px, py):
        return 0 <= px < W and 0 <= py < H and comp[py, px]

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


def snap_dir(u, snap):
    """Snap a direction to multiples of `snap` degrees, or to the nearest angle in a list."""
    ang = math.degrees(math.atan2(u[1], u[0])) % 180
    if isinstance(snap, (int, float)):
        best = round(ang / snap) * snap % 180
    else:
        best = min(snap, key=lambda s: min(abs(ang - s) % 180, 180 - abs(ang - s) % 180))
    r = math.radians(best)
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


def edge_lines(contour, snap=15.0, size=None, eps=2.5):
    """One straight line per contour run: [point, unit dir snapped to `snap` degrees, length,
    on_border, chord]. With `size`, runs along the image border are pinned to it."""
    idx = corner_indices(contour, eps)
    n = len(contour)
    lines = []
    for k in range(len(idx)):
        a, b = idx[k], idx[(k + 1) % len(idx)]
        span = (b - a) % n
        seg = np.array([contour[(a + t) % n] for t in range(span + 1)])
        core = seg[2:len(seg) - 2] if span > 10 else seg
        c = core.mean(axis=0)
        u = snap_dir(np.linalg.svd(core - c)[2][0], snap)
        border = False
        if size is not None:
            if np.all(np.abs(seg[:, 0]) < 0.5) or np.all(np.abs(seg[:, 0] - size) < 0.5):
                c, u, border = np.array([seg[0, 0], 0.0]), np.array([0.0, 1.0]), True
            if np.all(np.abs(seg[:, 1]) < 0.5) or np.all(np.abs(seg[:, 1] - size) < 0.5):
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


def straight_polygon(contour, snap=15.0, size=None, tol=4.0, eps=2.5, tip=0.0):
    """Polygon whose edges all run at multiples of `snap` degrees.

    Edges that would put a corner more than `tol` px away from the traced outline are dropped,
    as are tiny edges and edges running backwards (corner noise). A traced outline stops short
    of a sharp point, so with `tip` > 0 a corner of angle a may lie up to
    tol + tip / sin(a / 2) px away."""
    lines = edge_lines(contour, snap, size, eps)
    while len(lines) > 3:
        poly = vertices(lines)
        dist = np.array([0.0 if (lines[i - 1][3] or lines[i][3]) else np.min(np.hypot(*(contour - v).T))
                         for i, v in enumerate(poly)])
        allow = np.full(len(poly), tol)
        if tip > 0:
            for i in range(len(poly)):
                a, b = poly[i - 1] - poly[i], poly[(i + 1) % len(poly)] - poly[i]
                cosang = a @ b / max(np.hypot(*a) * np.hypot(*b), 1e-9)
                half = math.acos(max(-1.0, min(1.0, cosang))) / 2
                allow[i] = tol + tip / max(math.sin(half), 0.05)
        k = int(np.argmax(dist - allow))
        if dist[k] > allow[k]:
            a, b = (k - 1) % len(lines), k
            del lines[a if lines[a][2] < lines[b][2] else b]
            merge_parallel(lines)
            continue
        vec = np.roll(poly, -1, axis=0) - poly
        edge = np.hypot(*vec.T)
        tiny = [i for i in range(len(lines))
                if not lines[i][3] and (edge[i] < 3 or vec[i] @ lines[i][4] < 0)]
        if not tiny:
            return poly
        del lines[tiny[0]]
        merge_parallel(lines)
    return vertices(lines)


def polygon_area(p):
    x, y = p[:, 0], p[:, 1]
    return 0.5 * (np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


def offset_polygon(p, dist):
    """Move every edge of a simple polygon outward by `dist` (negative = inward), mitred corners."""
    sign = 1.0 if polygon_area(p) > 0 else -1.0
    lines = []
    for a, b in zip(p, np.roll(p, -1, axis=0)):
        v = b - a
        L = np.hypot(*v)
        if L < 1e-9:
            continue
        u = v / L
        nout = sign * np.array([u[1], -u[0]])
        lines.append((a + nout * dist, u))
    out = []
    for k in range(len(lines)):
        x = intersect(lines[k - 1], lines[k])
        out.append(x if x is not None else lines[k][0])
    return np.array(out)


def clip_polygon(p, x0, y0, x1, y1):
    """Sutherland-Hodgman clip of a polygon to an axis-aligned box."""
    def clip(pts, inside, cross):
        out = []
        for i in range(len(pts)):
            a, b = pts[i - 1], pts[i]
            if inside(b):
                if not inside(a):
                    out.append(cross(a, b))
                out.append(b)
            elif inside(a):
                out.append(cross(a, b))
        return out

    def at_x(x):
        return lambda a, b: np.array([x, a[1] + (b[1] - a[1]) * (x - a[0]) / (b[0] - a[0])])

    def at_y(y):
        return lambda a, b: np.array([a[0] + (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]), y])

    pts = [np.asarray(v, float) for v in p]
    for inside, cross in ((lambda v: v[0] >= x0, at_x(x0)), (lambda v: v[0] <= x1, at_x(x1)),
                          (lambda v: v[1] >= y0, at_y(y0)), (lambda v: v[1] <= y1, at_y(y1))):
        if not pts:
            break
        pts = clip(pts, inside, cross)
    return np.array(pts)
