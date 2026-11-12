# SHEARLINE : moteur à la plume large (Fraktur). Chaque trait est le passage d'une plume tenue à angle fixe.
import math
import pathops

XH, ASC, CAP, DESC = 450, 730, 680, -230
ANG = 40                      # angle de la plume (degrés)

def P(): return pathops.Path()
def poly(pts):
    p = P(); pen = p.getPen(); pen.moveTo(pts[0])
    for q in pts[1:]: pen.lineTo(q)
    pen.closePath(); return p
def rect(x0, y0, x1, y1):
    if x1 < x0: x0, x1 = x1, x0
    if y1 < y0: y0, y1 = y1, y0
    return poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
def U(*ps):
    out = P()
    for p in ps:
        if p is not None: out = pathops.op(out, p, pathops.PathOp.UNION)
    return out
def D(a, *bs):
    for b in bs:
        if b is not None: a = pathops.op(a, b, pathops.PathOp.DIFFERENCE)
    return a
def I(a, b): return pathops.op(a, b, pathops.PathOp.INTERSECTION)
def xf(p, m):
    a, b, c, d, e, f = m
    from fontTools.pens.recordingPen import RecordingPen
    rp = RecordingPen(); p.draw(rp); out = P(); pen = out.getPen()
    T = lambda q: (a * q[0] + c * q[1] + e, b * q[0] + d * q[1] + f)
    for op, args in rp.value: getattr(pen, op)(*[T(q) for q in args])
    return out
def mv(p, dx, dy=0): return xf(p, (1, 0, 0, 1, dx, dy))
def mirror(p, x): return xf(p, (-1, 0, 0, 1, 2 * x, 0))
def bounds(p):
    b = p.bounds
    return b if b else (0, 0, 0, 0)

def hull(pts):
    pts = sorted(set(pts))
    if len(pts) < 3: return pts
    def cr(o, a, b): return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], p) <= 0: lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cr(up[-2], up[-1], p) <= 0: up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]

class Pen:
    """plume large : largeur W, épaisseur t (le fil), angle a"""
    def __init__(s, W, t, a=ANG):
        s.W, s.t, s.a = W, t, a
        c, n = math.cos(math.radians(a)), math.sin(math.radians(a))
        u = (c * W / 2, n * W / 2); v = (-n * t / 2, c * t / 2)
        s.nib = [(u[0] + v[0], u[1] + v[1]), (u[0] - v[0], u[1] - v[1]), (-u[0] - v[0], -u[1] - v[1]), (-u[0] + v[0], -u[1] + v[1])]
    def at(s, p): return [(p[0] + q[0], p[1] + q[1]) for q in s.nib]
    def stroke(s, pts):
        """trace un chemin (liste de points) ; les arcs sont donnés déjà découpés"""
        parts = [poly(hull(s.at(pts[0])))]
        for a, b in zip(pts, pts[1:]):
            parts.append(poly(hull(s.at(a) + s.at(b))))
        return U(*parts)

def arc(cx, cy, rx, ry, a0, a1, n=None):
    n = n or max(4, int(abs(a1 - a0) / 6))
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]

# --- croix ---
def bar_latin(cx, y, w, t):
    return rect(cx - w / 2, y - t / 2, cx + w / 2, y + t / 2)
def bar_patriarch(cx, y, w, t, gap):
    return U(bar_latin(cx, y, w, t), bar_latin(cx, y + gap, 0.62 * w, t))
def bar_pattee(cx, y, w, t, flare=2.2):
    """barre pattée : fine au centre, évasée vers les bouts (bouts droits, pas de pointe)"""
    h0, h1 = t * 0.55, t * flare
    return U(poly([(cx, y - h0 / 2), (cx + w / 2, y - h1 / 2), (cx + w / 2, y + h1 / 2), (cx, y + h0 / 2)]),
             poly([(cx, y - h0 / 2), (cx - w / 2, y - h1 / 2), (cx - w / 2, y + h1 / 2), (cx, y + h0 / 2)]))
