# KARKAS : outils de dessin. Tout est droit : rectangles, obliques, unions.
import math
import pathops
from fontTools.pens.recordingPen import RecordingPen

CAP, UPM = 800, 1000

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
    rp = RecordingPen(); p.draw(rp); out = P(); pen = out.getPen()
    T = lambda q: (a * q[0] + c * q[1] + e, b * q[0] + d * q[1] + f)
    for op, args in rp.value: getattr(pen, op)(*[T(q) for q in args])
    return out
def mv(p, dx, dy=0): return xf(p, (1, 0, 0, 1, dx, dy))
def mirror(p, x): return xf(p, (-1, 0, 0, 1, 2 * x, 0))
def flipv(p, y): return xf(p, (1, 0, 0, -1, 0, 2 * y))
def bounds(p):
    b = p.bounds
    return b if b else (0, 0, 0, 0)

def link(xa, ya, xb, yb, t, wa, wb):
    """oblique d'épaisseur t entre deux fûts (centres xa et xb, largeurs wa et wb), coupée net dans les fûts"""
    dx, dy = xb - xa, yb - ya; L = math.hypot(dx, dy); ux, uy = dx / L, dy / L
    s = uy / ux; tv = t / abs(ux)
    yc = lambda x: ya + (x - xa) * s
    xi, xj = xa + wa / 2, xb - wb / 2
    hi = max(yc(xi), yc(xj)) + tv / 2; lo = min(yc(xi), yc(xj)) - tv / 2
    nx, ny = -uy * t / 2, ux * t / 2; e = 6 * t
    a = (xa - ux * e, ya - uy * e); b = (xb + ux * e, yb + uy * e)
    st = poly([(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny), (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)])
    return I(st, rect(xa - wa / 2, lo, xb + wb / 2, hi))

def chevron(x0, x1, ybase, ytip, S, t, flat=True):
    """Λ entre deux fûts (de x0 à x1, fûts de largeur S) : part de ybase, pointe en ytip. ytip < ybase donne un V."""
    xm = (x0 + x1) / 2
    up = ytip > ybase
    yt = ytip - (0.25 * t if up else -0.25 * t)
    c = U(link(x0 + S / 2, ybase, xm, yt, t, S, 0), link(xm, yt, x1 - S / 2, ybase, t, 0, S))
    if flat: c = I(c, rect(x0, min(ybase, ytip) - 4000, x1, ytip) if up else rect(x0, ytip, x1, ybase + 4000))
    return c

def silhouette(p):
    """l'encre, trous bouchés (seulement les contours extérieurs)"""
    q = U(p); q.simplify(fix_winding=True, clockwise=False)
    rp = RecordingPen(); q.draw(rp); cs = []; cur = []
    for op, a in rp.value:
        if op == 'moveTo': cur = [a[0]]
        elif op == 'lineTo': cur.append(a[0])
        elif op == 'closePath': cs.append(cur)
    ar = lambda c: sum(c[i][0] * c[(i + 1) % len(c)][1] - c[(i + 1) % len(c)][0] * c[i][1] for i in range(len(c))) / 2
    big = max(cs, key=lambda c: abs(ar(c))); sg = 1 if ar(big) > 0 else -1
    return U(*[poly(c) for c in cs if ar(c) * sg > 0])

def losange(cx, cy, a, b):
    return poly([(cx - a, cy), (cx, cy - b), (cx + a, cy), (cx, cy + b)])

class Wt:
    """une graisse : S fût, B barre, CT contre-forme"""
    def __init__(s, nom, S, B, CT, wclass):
        s.nom, s.S, s.B, s.CT, s.wclass = nom, S, B, CT, wclass
        s.W = CT + 2 * S                      # chasse (encre) d'une lettre à deux fûts
        s.G = round(0.50 * CT + 0.25 * S)     # blanc entre deux lettres
        s.g = round(22 + 0.20 * S)            # blanc à l'intérieur d'une ligature
        s.SB = s.G // 2

WEIGHTS = {'M150': Wt('M150', 24, 22, 104, 300), 'M300': Wt('M300', 44, 40, 96, 500), 'M500': Wt('M500', 68, 60, 84, 800)}
