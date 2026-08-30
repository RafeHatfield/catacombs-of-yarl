#!/usr/bin/env python3
"""A ROUTE, AS A LINE — the Python twin of `src/Logic/ECS/RoutePolyline.cs`.

RULED on round 21's diagnosis: **a per-tile field cannot draw a line.** Every wear lever built so
far was keyed to a per-tile scalar, and a route is a path-scale object. Measured on the review
scene, the travel axis derived from that scalar agreed between neighbouring tiles only **34% of
the time** — it flipped two times in three, so a grain keyed to it could never accumulate into the
continuous line a viewer follows.

This is the crack network's shape applied to traffic: a field-scale object drawn ACROSS tiles
rather than inside them, which is the one system class blind seats have consistently praised here.

WORN, NOT BUILT. The polyline is KEYING, NEVER PAVING. Nothing is drawn along it; the existing age
layer re-keys to distance from it and to its tangent, and therefore concentrates along it.

COHERENT BY CONSTRUCTION. Distance to a polyline and the tangent of the nearest segment are pure
functions of a WORLD position, so two tiles sharing a stone across their boundary compute the
identical answer for the identical pixel. The corner theorem is satisfied without a keying table,
because there is nothing per-tile left to disagree about.
"""
import math

REACH = 1.35            # how far from the line the wear reaches, in tiles


def smooth(path, passes=2):
    """Chaikin corner-cutting: a walked line has walking curvature, not a staircase of grid moves.

    Chaikin rather than a spline because it stays inside the convex hull of the original path — a
    smoothed route cannot wander into a wall the pathfinder avoided, which a spline can.
    """
    pts = [(float(x), float(y)) for x, y in path]
    for _ in range(passes):
        if len(pts) <= 2:
            break
        nxt = [pts[0]]
        for a, b in zip(pts, pts[1:]):
            nxt.append((0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]))
            nxt.append((0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1]))
        nxt.append(pts[-1])
        pts = nxt
    return pts


def _hash(x, y, seed):
    h = (x * 374761393 + y * 668265263 + seed * 1442695041) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return abs(h ^ (h >> 16))


def jitter(pts, walkable, seed, amp=0.28):
    """Push each point sideways deterministically, then refuse any push that leaves walkable ground.

    DISCOVERED, NOT DRAWN. A route down the exact centre of every corridor is a route somebody
    surveyed, and §8.1's register has no surveyor in it.
    """
    out = []
    for i, (px, py) in enumerate(pts):
        a = pts[max(i - 1, 0)]
        b = pts[min(i + 1, len(pts) - 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(tx, ty)
        if ln < 1e-9:
            out.append((px, py))
            continue
        nx, ny = -ty / ln, tx / ln
        h = _hash(int(round(px * 16)), int(round(py * 16)), seed)
        d = ((h % 1000) / 1000.0 - 0.5) * 2.0 * amp
        qx, qy = px + nx * d, py + ny * d
        out.append((qx, qy) if walkable(int(math.floor(qx + 0.5)), int(math.floor(qy + 0.5)))
                   else (px, py))
    return out


# HOW FAR ALONG THE LINE THE TANGENT IS TAKEN, in points either side of the nearest segment.
#
# ⚠ NOT ONE SEGMENT. A single segment of a jittered, corner-cut line is a few hundredths of a tile
# long and its direction is almost entirely the jitter, so a dead-straight north-south route came
# back as [1, 2, 1, 2, 1, 1, 1, 3] — diagonals, all the way down a line that never turns. The
# tangent has to be read over a span long enough to be the ROUTE rather than the wobble, and a
# span is also what a walker's eye follows: nobody reads the next four pixels of a path, they read
# where it is going.
TANGENT_SPAN = 6


def nearest(lines, x, y):
    """(distance in tiles, that line's weight, tangent x, tangent y) to the nearest point."""
    best, bw, btx, bty = float("inf"), 0.0, 1.0, 0.0
    for pts, wgt in lines:
        for i in range(len(pts) - 1):
            (ax, ay), (bx, by) = pts[i], pts[i + 1]
            dx, dy = bx - ax, by - ay
            l2 = dx * dx + dy * dy
            t = 0.0 if l2 < 1e-12 else max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / l2))
            cx, cy = ax + t * dx, ay + t * dy
            d = math.hypot(x - cx, y - cy)
            if d < best:
                lo = pts[max(i - TANGENT_SPAN, 0)]
                hi = pts[min(i + 1 + TANGENT_SPAN, len(pts) - 1)]
                best, bw = d, wgt
                btx, bty = hi[0] - lo[0], hi[1] - lo[1]
    return best, bw, btx, bty


def strength(lines, x, y):
    """Full on the line, gone by REACH. Smoothstep, so the lane has shoulders and not an edge."""
    if not lines:
        return 0.0
    d, w, _, _ = nearest(lines, x, y)
    if d >= REACH:
        return 0.0
    u = 1.0 - d / REACH
    return w * u * u * (3.0 - 2.0 * u)


def axis(lines, x, y):
    """0 = E-W, 1 = NE-SW, 2 = N-S, 3 = NW-SE, -1 = off every route."""
    if not lines:
        return -1
    d, _, tx, ty = nearest(lines, x, y)
    if d >= REACH:
        return -1
    ang = math.degrees(math.atan2(ty, tx)) % 180.0
    return int(round(ang / 45.0)) % 4
