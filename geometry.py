"""Stick geometry. A *unit* is {"s": strokes, "w": width, "h": height};
a stroke is a list of [x, y] points; glyph art lives in a 100x100 box."""
import math

def unit(strokes, w=100, h=100):
    return {"s": strokes, "w": w, "h": h}

def shift(strokes, dx=0, dy=0):
    return [[[x + dx, y + dy] for x, y in st] for st in strokes]

def place(strokes, x, y, w, h):
    """Map strokes drawn in a 100x100 box into the box (x, y, w, h)."""
    return [[[x + px * w / 100, y + py * h / 100] for px, py in st] for st in strokes]

def layout_row(units, gap=4, height=100):
    out, x = [], 0
    for u in units:
        out += shift(u["s"], x, (height - u["h"]) / 2)
        x += u["w"] + gap
    return unit(out, max(x - gap, 1), height)

def circle(cx, cy, r, n=14):
    pts = [[cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)] for i in range(n)]
    return pts + [pts[0]]

def rect(x, y, w, h):
    return [[x, y], [x + w, y], [x + w, y + h], [x, y + h], [x, y]]

def arrow(x1, y1, x2, y2, head=7):
    a = math.atan2(y2 - y1, x2 - x1)
    return [[[x1, y1], [x2, y2]]] + [
        [[x2, y2], [x2 - head * math.cos(a + s), y2 - head * math.sin(a + s)]] for s in (0.5, -0.5)]

def star(cx, cy, r):
    pts = [[cx + r * math.cos(math.radians(-90 + 144 * i)), cy + r * math.sin(math.radians(-90 + 144 * i))] for i in range(6)]
    return pts

def dashed(strokes, dash=4, gap=4):
    out = []
    for st in strokes:
        for (x1, y1), (x2, y2) in zip(st, st[1:]):
            L = math.hypot(x2 - x1, y2 - y1)
            d = 0
            while d < L:
                e = min(d + dash, L)
                out.append([[x1 + (x2 - x1) * d / L, y1 + (y2 - y1) * d / L],
                            [x1 + (x2 - x1) * e / L, y1 + (y2 - y1) * e / L]])
                d += dash + gap
    return out

def fig(cx, by, s=1.0, arms=((-12, 12), (12, 12)), lean=0, drop=0):
    """Stick figure standing on y=by. arms: (dx, dy) offsets from the shoulder."""
    hx, hy = cx + lean, by - 46 * s + drop
    hip = by - 18 * s
    nx, ny = hx, hy + 6 * s
    sh = (nx + (cx - nx) * .25, ny + (hip - ny) * .25)
    st = [circle(hx, hy, 6 * s, 10), [[nx, ny], [cx, hip]],
          [[cx, hip], [cx - 9 * s, by]], [[cx, hip], [cx + 9 * s, by]]]
    for dx, dy in arms:
        st.append([[sh[0], sh[1]], [sh[0] + dx * s, sh[1] + dy * s]])
    return st
