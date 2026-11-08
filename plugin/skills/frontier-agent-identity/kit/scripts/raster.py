#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Pure-Python rasteriser for agent icons - standard library only, same pixels on every machine.

Draws what the identity icons need:
  * SVG path data filled with the non-zero rule (M L H V C S Q T A Z, absolute and relative),
  * round-capped, round-joined strokes (original glyphs and the environment label font),
  * axis-aligned rectangles,
and writes 8-bit RGBA PNG files. Fills use exact area coverage (the accumulation method of font
rasterisers); strokes use a distance field. No Node.js, browser or imaging library is needed, so a
customer's build agent can regenerate every icon.
"""
from __future__ import annotations

import math
import re
import struct
import zlib

# ------------------------------------------------------------------ colour

def rgb(hex_colour: str) -> tuple[float, float, float]:
    h = hex_colour.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


# ------------------------------------------------------------------ SVG path data

_CMDS = set("MmLlHhVvCcSsQqTtAaZz")
_NUM = re.compile(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")


class _Reader:
    def __init__(self, d: str):
        self.d, self.i, self.n = d, 0, len(d)

    def skip(self):
        while self.i < self.n and self.d[self.i] in " \t\r\n,":
            self.i += 1

    def at_end(self) -> bool:
        self.skip()
        return self.i >= self.n

    def command(self):
        self.skip()
        if self.i < self.n and self.d[self.i] in _CMDS:
            self.i += 1
            return self.d[self.i - 1]
        return None

    def has_number(self) -> bool:
        self.skip()
        return self.i < self.n and self.d[self.i] in "+-.0123456789"

    def number(self) -> float:
        self.skip()
        m = _NUM.match(self.d, self.i)
        if not m:
            raise ValueError(f"number expected at {self.i}: {self.d[self.i:self.i + 16]!r}")
        self.i = m.end()
        return float(m.group(0))

    def flag(self) -> bool:
        self.skip()
        c = self.d[self.i] if self.i < self.n else ""
        if c not in "01":
            raise ValueError(f"arc flag expected at {self.i}")
        self.i += 1
        return c == "1"


def parse_path(d: str) -> list:
    """Absolute segments: ('M', x, y) ('L', x, y) ('C', x1, y1, x2, y2, x, y) ('Q', x1, y1, x, y)
    ('A', rx, ry, rot, large, sweep, x, y) ('Z',)."""
    r = _Reader(d)
    out = []
    cx = cy = sx = sy = 0.0
    prev_c = prev_q = None          # last control points for S and T
    cmd = None
    while not r.at_end():
        c = r.command()
        if c is None:
            if cmd is None or cmd in "Zz":
                raise ValueError(f"command expected at {r.i}")
            c = cmd
        cmd = c
        rel, C = c.islower(), c.upper()
        if C == "Z":
            out.append(("Z",))
            cx, cy = sx, sy
            prev_c = prev_q = None
            continue
        first = True
        while first or r.has_number():
            if C == "M" and not first:
                C = "L"                      # implicit lineto after the first moveto pair
            ox, oy = (cx, cy) if rel else (0.0, 0.0)
            if C == "M":
                x, y = r.number() + ox, r.number() + oy
                out.append(("M", x, y))
                cx, cy, sx, sy = x, y, x, y
                prev_c = prev_q = None
            elif C == "L":
                x, y = r.number() + ox, r.number() + oy
                out.append(("L", x, y)); cx, cy = x, y; prev_c = prev_q = None
            elif C == "H":
                x = r.number() + (cx if rel else 0.0)
                out.append(("L", x, cy)); cx = x; prev_c = prev_q = None
            elif C == "V":
                y = r.number() + (cy if rel else 0.0)
                out.append(("L", cx, y)); cy = y; prev_c = prev_q = None
            elif C == "C":
                x1, y1 = r.number() + ox, r.number() + oy
                x2, y2 = r.number() + ox, r.number() + oy
                x, y = r.number() + ox, r.number() + oy
                out.append(("C", x1, y1, x2, y2, x, y)); prev_c = (x2, y2); prev_q = None; cx, cy = x, y
            elif C == "S":
                x1, y1 = (2 * cx - prev_c[0], 2 * cy - prev_c[1]) if prev_c else (cx, cy)
                x2, y2 = r.number() + ox, r.number() + oy
                x, y = r.number() + ox, r.number() + oy
                out.append(("C", x1, y1, x2, y2, x, y)); prev_c = (x2, y2); prev_q = None; cx, cy = x, y
            elif C == "Q":
                x1, y1 = r.number() + ox, r.number() + oy
                x, y = r.number() + ox, r.number() + oy
                out.append(("Q", x1, y1, x, y)); prev_q = (x1, y1); prev_c = None; cx, cy = x, y
            elif C == "T":
                x1, y1 = (2 * cx - prev_q[0], 2 * cy - prev_q[1]) if prev_q else (cx, cy)
                x, y = r.number() + ox, r.number() + oy
                out.append(("Q", x1, y1, x, y)); prev_q = (x1, y1); prev_c = None; cx, cy = x, y
            elif C == "A":
                rx, ry, rot = r.number(), r.number(), r.number()
                large, sweep = r.flag(), r.flag()
                x, y = r.number() + ox, r.number() + oy
                out.append(("A", rx, ry, rot, large, sweep, x, y)); prev_c = prev_q = None; cx, cy = x, y
            first = False
    return out


def _arc_centre(x1, y1, rx, ry, phi_deg, large, sweep, x2, y2):
    """SVG endpoint arc -> centre parameterisation (SVG 1.1 implementation notes F.6.5)."""
    if rx == 0 or ry == 0 or (x1 == x2 and y1 == y2):
        return None
    phi = math.radians(phi_deg % 360)
    cos_p, sin_p = math.cos(phi), math.sin(phi)
    dx, dy = (x1 - x2) / 2.0, (y1 - y2) / 2.0
    x1p, y1p = cos_p * dx + sin_p * dy, -sin_p * dx + cos_p * dy
    rx, ry = abs(rx), abs(ry)
    lam = (x1p * x1p) / (rx * rx) + (y1p * y1p) / (ry * ry)
    if lam > 1:
        s = math.sqrt(lam)
        rx, ry = rx * s, ry * s
    num = rx * rx * ry * ry - rx * rx * y1p * y1p - ry * ry * x1p * x1p
    den = rx * rx * y1p * y1p + ry * ry * x1p * x1p
    coef = math.sqrt(max(0.0, num / den)) if den else 0.0
    if large == sweep:
        coef = -coef
    cxp, cyp = coef * rx * y1p / ry, -coef * ry * x1p / rx
    cx = cos_p * cxp - sin_p * cyp + (x1 + x2) / 2.0
    cy = sin_p * cxp + cos_p * cyp + (y1 + y2) / 2.0

    def angle(ux, uy, vx, vy):
        return math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)

    ux, uy = (x1p - cxp) / rx, (y1p - cyp) / ry
    vx, vy = (-x1p - cxp) / rx, (-y1p - cyp) / ry
    th1 = angle(1.0, 0.0, ux, uy)
    dth = angle(ux, uy, vx, vy)
    if not sweep and dth > 0:
        dth -= 2 * math.pi
    elif sweep and dth < 0:
        dth += 2 * math.pi
    return cx, cy, rx, ry, cos_p, sin_p, th1, dth


def flatten(d: str, transform=(1.0, 1.0, 0.0, 0.0), tolerance: float = 0.35) -> list:
    """Path data -> list of polylines in device pixels. transform = (sx, sy, tx, ty)."""
    sx_, sy_, tx, ty = transform
    scale = max(abs(sx_), abs(sy_))

    def dev(x, y):
        return (x * sx_ + tx, y * sy_ + ty)

    def steps(length_user):
        return max(2, min(256, int(math.ceil(length_user * scale / (tolerance * 4.0)))))

    polys, cur = [], []
    px = py = 0.0
    for seg in parse_path(d):
        k = seg[0]
        if k == "M":
            if len(cur) > 1:
                polys.append(cur)
            px, py = seg[1], seg[2]
            cur = [dev(px, py)]
        elif k == "L":
            px, py = seg[1], seg[2]
            cur.append(dev(px, py))
        elif k == "C":
            x1, y1, x2, y2, x, y = seg[1:]
            est = math.hypot(x1 - px, y1 - py) + math.hypot(x2 - x1, y2 - y1) + math.hypot(x - x2, y - y2)
            n = steps(est)
            for i in range(1, n + 1):
                t = i / n
                mt = 1 - t
                bx = mt * mt * mt * px + 3 * mt * mt * t * x1 + 3 * mt * t * t * x2 + t * t * t * x
                by = mt * mt * mt * py + 3 * mt * mt * t * y1 + 3 * mt * t * t * y2 + t * t * t * y
                cur.append(dev(bx, by))
            px, py = x, y
        elif k == "Q":
            x1, y1, x, y = seg[1:]
            n = steps(math.hypot(x1 - px, y1 - py) + math.hypot(x - x1, y - y1))
            for i in range(1, n + 1):
                t = i / n
                mt = 1 - t
                cur.append(dev(mt * mt * px + 2 * mt * t * x1 + t * t * x, mt * mt * py + 2 * mt * t * y1 + t * t * y))
            px, py = x, y
        elif k == "A":
            rx, ry, rot, large, sweep, x, y = seg[1:]
            centre = _arc_centre(px, py, rx, ry, rot, large, sweep, x, y)
            if centre is None:
                cur.append(dev(x, y))
            else:
                cx, cy, rx2, ry2, cp, sp, th1, dth = centre
                n = steps(abs(dth) * max(rx2, ry2))
                for i in range(1, n + 1):
                    th = th1 + dth * i / n
                    ex, ey = rx2 * math.cos(th), ry2 * math.sin(th)
                    cur.append(dev(cp * ex - sp * ey + cx, sp * ex + cp * ey + cy))
            px, py = x, y
        elif k == "Z":
            if cur:
                cur.append(cur[0])
                polys.append(cur)
                start = cur[0]
                cur = [start]
                inv_x = (start[0] - tx) / sx_ if sx_ else 0.0
                inv_y = (start[1] - ty) / sy_ if sy_ else 0.0
                px, py = inv_x, inv_y
    if len(cur) > 1:
        polys.append(cur)
    return polys


# ------------------------------------------------------------------ coverage

def fill_coverage(polys: list, w: int, h: int) -> list:
    """Exact area coverage (0..1) per pixel for the non-zero fill of closed polylines."""
    stride = w + 2
    acc = [0.0] * (stride * h + 2)
    for pts in polys:
        n = len(pts)
        for k in range(n):
            x0, y0 = pts[k]
            x1, y1 = pts[(k + 1) % n]
            _accumulate_line(acc, stride, w, h, x0, y0, x1, y1)
    cov = [0.0] * (w * h)
    xs = [x for pts in polys for x, _ in pts]
    ys = [y for pts in polys for _, y in pts]
    if not xs:
        return cov
    x_lo = max(0, int(min(xs)) - 1)
    x_hi = min(w, int(max(xs)) + 3)
    y_lo = max(0, int(min(ys)) - 1)
    y_hi = min(h, int(max(ys)) + 2)
    for y in range(y_lo, y_hi):
        run = 0.0
        base, ob = y * stride, y * w
        for x in range(x_lo, x_hi):
            run += acc[base + x]
            v = -run if run < 0 else run
            cov[ob + x] = 1.0 if v > 1.0 else v
    return cov


def _accumulate_line(acc, stride, w, h, x0, y0, x1, y1):
    if abs(y0 - y1) < 1e-9:
        return
    if y0 < y1:
        direction = 1.0
    else:
        direction = -1.0
        x0, y0, x1, y1 = x1, y1, x0, y0
    dxdy = (x1 - x0) / (y1 - y0)
    x = x0
    if y0 < 0:
        x -= y0 * dxdy
    y_start = max(0, int(math.floor(y0)))
    y_end = min(h, int(math.ceil(y1)))
    lim = w - 1e-6
    for y in range(y_start, y_end):
        dy = min(float(y + 1), y1) - max(float(y), y0)
        xnext = x + dxdy * dy
        d = dy * direction
        xa, xb = (x, xnext) if x < xnext else (xnext, x)
        xa = 0.0 if xa < 0 else (lim if xa > lim else xa)
        xb = 0.0 if xb < 0 else (lim if xb > lim else xb)
        x0f = math.floor(xa)
        x0i = int(x0f)
        x1i = int(math.ceil(xb))
        line = y * stride
        if x1i <= x0i + 1:
            xmf = 0.5 * (xa + xb) - x0f
            acc[line + x0i] += d - d * xmf
            acc[line + x0i + 1] += d * xmf
        else:
            s = 1.0 / (xb - xa)
            x0frac = xa - x0f
            a0 = 0.5 * s * (1.0 - x0frac) * (1.0 - x0frac)
            x1frac = xb - x1i + 1.0
            am = 0.5 * s * x1frac * x1frac
            acc[line + x0i] += d * a0
            if x1i == x0i + 2:
                acc[line + x0i + 1] += d * (1.0 - a0 - am)
            else:
                a1 = s * (1.5 - x0frac)
                acc[line + x0i + 1] += d * (a1 - a0)
                for xi in range(x0i + 2, x1i - 1):
                    acc[line + xi] += d * s
                a2 = a1 + (x1i - x0i - 3) * s
                acc[line + x1i - 1] += d * (1.0 - a2 - am)
            acc[line + x1i] += d * am
        x = xnext


def stroke_coverage(polys: list, width: float, w: int, h: int, cov: list | None = None) -> list:
    """Coverage of round-capped, round-joined strokes (distance field), merged with max()."""
    hw = width / 2.0
    cov = cov if cov is not None else [0.0] * (w * h)
    for pts in polys:
        if len(pts) == 1:
            pts = [pts[0], pts[0]]
        for k in range(len(pts) - 1):
            ax, ay = pts[k]
            bx, by = pts[k + 1]
            x_lo = max(0, int(math.floor(min(ax, bx) - hw - 1)))
            x_hi = min(w - 1, int(math.ceil(max(ax, bx) + hw + 1)))
            y_lo = max(0, int(math.floor(min(ay, by) - hw - 1)))
            y_hi = min(h - 1, int(math.ceil(max(ay, by) + hw + 1)))
            vx, vy = bx - ax, by - ay
            l2 = vx * vx + vy * vy
            for py in range(y_lo, y_hi + 1):
                cy = py + 0.5
                row = py * w
                for px in range(x_lo, x_hi + 1):
                    cx = px + 0.5
                    if l2 > 0:
                        t = ((cx - ax) * vx + (cy - ay) * vy) / l2
                        t = 0.0 if t < 0 else (1.0 if t > 1 else t)
                    else:
                        t = 0.0
                    ex, ey = cx - (ax + t * vx), cy - (ay + t * vy)
                    c = hw + 0.5 - math.sqrt(ex * ex + ey * ey)
                    if c > 0:
                        if c > 1:
                            c = 1.0
                        if c > cov[row + px]:
                            cov[row + px] = c
    return cov


# ------------------------------------------------------------------ canvas

class Canvas:
    """Premultiplied RGBA float canvas."""

    def __init__(self, w: int, h: int, background: str | None = None):
        self.w, self.h = w, h
        self.px = [0.0] * (w * h * 4)
        if background:
            self.fill_rect(0, 0, w, h, background)

    def blend(self, cov: list, colour: str, opacity: float = 1.0) -> None:
        r, g, b = rgb(colour)
        p = self.px
        for i, c in enumerate(cov):
            if c <= 0:
                continue
            a = c * opacity
            inv = 1.0 - a
            j = i * 4
            p[j] = r * a + p[j] * inv
            p[j + 1] = g * a + p[j + 1] * inv
            p[j + 2] = b * a + p[j + 2] * inv
            p[j + 3] = a + p[j + 3] * inv

    def rect_coverage(self, x: float, y: float, rw: float, rh: float) -> list:
        cov = [0.0] * (self.w * self.h)
        x0, x1, y0, y1 = max(0.0, x), min(float(self.w), x + rw), max(0.0, y), min(float(self.h), y + rh)
        for py in range(int(math.floor(y0)), int(math.ceil(y1))):
            fy = min(y1, py + 1) - max(y0, py)
            if fy <= 0:
                continue
            for px in range(int(math.floor(x0)), int(math.ceil(x1))):
                fx = min(x1, px + 1) - max(x0, px)
                if fx > 0:
                    cov[py * self.w + px] = fx * fy
        return cov

    def fill_rect(self, x, y, rw, rh, colour):
        self.blend(self.rect_coverage(x, y, rw, rh), colour)

    def png(self) -> bytes:
        raw = bytearray()
        p = self.px
        for y in range(self.h):
            raw.append(0)
            for x in range(self.w):
                j = (y * self.w + x) * 4
                a = p[j + 3]
                if a <= 0:
                    raw += b"\x00\x00\x00\x00"
                    continue
                inv = 1.0 / a
                raw.append(min(255, int(round(p[j] * inv * 255))))
                raw.append(min(255, int(round(p[j + 1] * inv * 255))))
                raw.append(min(255, int(round(p[j + 2] * inv * 255))))
                raw.append(min(255, int(round(a * 255))))
        return encode_png(self.w, self.h, bytes(raw))


def encode_png(w: int, h: int, raw_rows: bytes) -> bytes:
    """8-bit RGBA PNG from filtered rows (each row starts with its filter byte, here always 0)."""
    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw_rows, 9)) + chunk(b"IEND", b""))


# ------------------------------------------------------------------ stroke font for environment labels
# Capitals, digits and a hyphen drawn as centre-line strokes on a cap height of 10 units (y grows down).

def _arc(cx, cy, rx, ry, a0, a1, n=18):
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def _ellipse(cx, cy, rx, ry, n=36):
    return _arc(cx, cy, rx, ry, 0, 360, n)


FONT = {
    "A": (7.0, [[(0, 10), (3.5, 0), (7, 10)], [(1.3, 6.6), (5.7, 6.6)]]),
    "B": (6.4, [[(0, 0), (0, 10)], [(0, 0), (3.5, 0)] + _arc(3.5, 2.45, 2.5, 2.45, -90, 90) + [(3.5, 4.9), (0, 4.9)],
                [(0, 4.9), (3.7, 4.9)] + _arc(3.7, 7.45, 2.7, 2.55, -90, 90) + [(3.7, 10), (0, 10)]]),
    "C": (6.6, [_arc(3.6, 5, 3.6, 5, 318, 42, 24)]),
    "D": (6.6, [[(0, 0), (0, 10)], [(0, 0), (2.4, 0)] + _arc(2.4, 5, 4.2, 5, -90, 90, 20) + [(2.4, 10), (0, 10)]]),
    "E": (5.6, [[(5.6, 0), (0, 0), (0, 10), (5.6, 10)], [(0, 5), (4.6, 5)]]),
    "F": (5.6, [[(5.6, 0), (0, 0), (0, 10)], [(0, 5), (4.6, 5)]]),
    "G": (7.2, [_arc(3.6, 5, 3.6, 5, 315, 0, 24) + [(4.1, 5)]]),
    "H": (6.2, [[(0, 0), (0, 10)], [(6.2, 0), (6.2, 10)], [(0, 5), (6.2, 5)]]),
    "I": (0.0, [[(0, 0), (0, 10)]]),
    "J": (5.0, [[(5, 0), (5, 7.2)] + _arc(2.5, 7.2, 2.5, 2.8, 0, 180, 14)]),
    "K": (6.2, [[(0, 0), (0, 10)], [(6.2, 0), (0, 6.3)], [(2.2, 4.1), (6.2, 10)]]),
    "L": (5.2, [[(0, 0), (0, 10), (5.2, 10)]]),
    "M": (7.6, [[(0, 10), (0, 0), (3.8, 6.6), (7.6, 0), (7.6, 10)]]),
    "N": (6.2, [[(0, 10), (0, 0), (6.2, 10), (6.2, 0)]]),
    "O": (7.4, [_ellipse(3.7, 5, 3.7, 5)]),
    "P": (6.0, [[(0, 10), (0, 0), (3.3, 0)] + _arc(3.3, 2.75, 2.7, 2.75, -90, 90) + [(3.3, 5.5), (0, 5.5)]]),
    "Q": (7.6, [_ellipse(3.7, 5, 3.7, 5), [(4.6, 7.2), (7.6, 10.4)]]),
    "R": (6.2, [[(0, 10), (0, 0), (3.3, 0)] + _arc(3.3, 2.75, 2.7, 2.75, -90, 90) + [(3.3, 5.5), (0, 5.5)],
                [(3.2, 5.5), (6.2, 10)]]),
    "S": (6.0, [_arc(3.0, 2.6, 2.9, 2.6, 335, 90, 18) + _arc(3.0, 7.55, 3.0, 2.45, -90, 150, 18)]),
    "T": (6.4, [[(0, 0), (6.4, 0)], [(3.2, 0), (3.2, 10)]]),
    "U": (6.2, [[(0, 0), (0, 6.8)] + _arc(3.1, 6.8, 3.1, 3.2, 180, 0, 16) + [(6.2, 6.8), (6.2, 0)]]),
    "V": (6.8, [[(0, 0), (3.4, 10), (6.8, 0)]]),
    "W": (9.2, [[(0, 0), (2.3, 10), (4.6, 2.6), (6.9, 10), (9.2, 0)]]),
    "X": (6.4, [[(0, 0), (6.4, 10)], [(6.4, 0), (0, 10)]]),
    "Y": (6.6, [[(0, 0), (3.3, 5.2), (6.6, 0)], [(3.3, 5.2), (3.3, 10)]]),
    "Z": (6.0, [[(0, 0), (6, 0), (0, 10), (6, 10)]]),
    "0": (6.0, [_ellipse(3.0, 5, 3.0, 5)]),
    "1": (3.2, [[(0, 2.2), (3.2, 0), (3.2, 10)]]),
    "2": (6.0, [_arc(3.0, 3.0, 3.0, 3.0, 200, 380, 16) + [(0, 10), (6.0, 10)]]),
    "3": (6.0, [_arc(2.9, 2.6, 2.9, 2.6, 205, 450, 18) + _arc(3.0, 7.55, 3.0, 2.45, -90, 150, 18)]),
    "4": (6.6, [[(5.0, 10), (5.0, 0), (0, 7.0), (6.6, 7.0)]]),
    "5": (6.0, [[(5.6, 0), (0.8, 0), (0.4, 4.7)] + _arc(3.0, 6.9, 3.0, 3.1, 228, 500, 20)]),
    "6": (6.0, [_arc(3.6, 6.4, 3.6, 6.4, 290, 180, 12) + _arc(3.0, 7.1, 3.0, 2.9, 180, 540, 30)]),
    "7": (6.0, [[(0, 0), (6, 0), (2.0, 10)]]),
    "8": (6.0, [_ellipse(3.0, 2.55, 2.6, 2.45), _ellipse(3.0, 7.45, 3.0, 2.55)]),
    "9": (6.0, [_arc(3.0, 2.9, 3.0, 2.9, 0, 360, 30) + _arc(2.4, 3.6, 3.6, 6.4, 0, 110, 12)]),
    "-": (4.0, [[(0, 5.6), (4, 5.6)]]),
    " ": (3.2, []),
}


def label_polylines(text: str, x_centre: float, cap_top: float, cap_height: float, spacing: float = 2.2) -> list:
    """Polylines (device pixels) for an upper-case label centred on x_centre."""
    s = cap_height / 10.0
    chars = [c for c in text.upper() if c in FONT]
    total = sum(FONT[c][0] for c in chars) + spacing * max(0, len(chars) - 1)
    x = x_centre - total * s / 2.0
    out = []
    for c in chars:
        width, strokes = FONT[c]
        for pl in strokes:
            out.append([(x + px * s, cap_top + py * s) for px, py in pl])
        x += (width + spacing) * s
    return out


def label_width(text: str, cap_height: float, spacing: float = 2.2) -> float:
    chars = [c for c in text.upper() if c in FONT]
    return (sum(FONT[c][0] for c in chars) + spacing * max(0, len(chars) - 1)) * cap_height / 10.0


def polylines_to_path(polys: list, digits: int = 2) -> str:
    """Polylines -> compact SVG path data (absolute)."""
    parts = []
    for pl in polys:
        if not pl:
            continue
        pts = [f"{round(x, digits):g} {round(y, digits):g}" for x, y in pl]
        parts.append("M" + pts[0] + ("L" + "L".join(pts[1:]) if len(pts) > 1 else ""))
    return "".join(parts)
