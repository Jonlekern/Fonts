# BALLASTLINE : outils (lecture des contours de BARYCENTRE-032, ligne de flottaison, plombs)
import math, pathops
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from ball_geom import P, poly, rect, U, D, I, circ, ell, mv, bounds, xf

def flat(p):
    rp = RecordingPen(); p.draw(rp); segs = []; cur = None; st = None
    for op, a in rp.value:
        if op == 'moveTo': cur = st = a[0]
        elif op == 'lineTo': segs.append((cur, a[0])); cur = a[0]
        elif op == 'curveTo':
            p0 = cur; p1, p2, p3 = a
            for k in range(1, 17):
                t = k / 16; m = 1 - t
                q = tuple(m**3*p0[i]+3*m*m*t*p1[i]+3*m*t*t*p2[i]+t**3*p3[i] for i in (0, 1)); segs.append((cur, q)); cur = q
        elif op in ('closePath', 'endPath'):
            if cur != st: segs.append((cur, st))
    return segs

def spans_at(segs, y):
    xs = sorted(x0 + (y - a) * (x1 - x0) / (b - a) for (x0, a), (x1, b) in segs if (a <= y < b) or (b <= y < a))
    return [(xs[i], xs[i + 1]) for i in range(0, len(xs) - 1, 2)]

XH, DESC = 468, -220
def load(path):
    t = TTFont(path); gs = t.getGlyphSet(); G = {}
    for n in t.getGlyphOrder():
        rp = RecordingPen(); gs[n].draw(rp); p = P(); rp.replay(p.getPen())
        G[n] = (p, t['hmtx'][n][0])
    return t, G

def stem_w(G):
    segs = flat(G['l'][0]); sp = spans_at(segs, 300); return sp[0][1] - sp[0][0]

def drop(cx, top, r):
    """plomb : une goutte, la pointe en haut, le rond en bas (pas de pointe aiguë : bout coupé)"""
    cy = top - 2.3 * r
    tip = (cx, top); d = top - cy; a = math.atan2(d, 0); b = math.acos(r / d)
    t1 = (cx + r * math.cos(a + b), cy + r * math.sin(a + b)); t2 = (cx + r * math.cos(a - b), cy + r * math.sin(a - b))
    body = U(circ(cx, cy, r), poly([t1, tip, t2, (cx, cy)]))
    return D(body, rect(cx - 2 * r, top - 0.18 * r, cx + 2 * r, top + r))

def feet(p):
    """là où la lettre touche le bas : intervalles d'encre juste au-dessus de son point le plus bas"""
    b = bounds(p); segs = flat(p); y = b[1] + 6
    return [(a, c) for a, c in spans_at(segs, y) if c - a > 2], b[1]

def lest(p, sw):
    """le lest : un fil sous le pied principal, puis un plomb"""
    fs, y0 = feet(p)
    if not fs: return P()
    a, c = max(fs, key=lambda q: (round((q[1] - q[0]) / 8), -q[0]))      # le pied le plus large, à égalité le plus à gauche
    cx = (a + c) / 2; th = max(8, 0.16 * sw); L = 70; r = 0.42 * sw + 16
    fil = rect(cx - th / 2, y0 - L, cx + th / 2, y0 + 8)
    return U(fil, drop(cx, y0 - L + 4, r))

WL = (-0.16 * XH, 0.30 * XH)                       # la bande de flottaison : du dessous de la ligne de base au tiers de x
def flottaison(p, adv, o=10):                  # les bandes de deux lettres voisines se chevauchent (pas de fil clair entre elles)
    band = rect(-o, WL[0], adv + o, WL[1])
    return pathops.op(p, band, pathops.PathOp.XOR)

def plumb_dots(p, sw, ymin):
    """remplace les points (contours au-dessus de ymin) par des plombs en goutte"""
    from fontTools.pens.recordingPen import RecordingPen
    rp = RecordingPen(); p.draw(rp); keep = P(); dots = []; cur = []
    for op, a in rp.value:
        cur.append((op, a))
        if op in ('closePath', 'endPath'):
            q = P(); pen = q.getPen()
            for o, aa in cur: getattr(pen, o)(*aa)
            b = bounds(q)
            (dots if b[1] > ymin else [None]).append(b) if b[1] > ymin else None
            if b[1] <= ymin: keep = U(keep, q)
            cur = []
    out = keep
    for b in dots:
        r = 0.5 * (b[2] - b[0]); cx = 0.5 * (b[0] + b[2]); out = U(out, drop(cx, b[3] + 0.6 * r, 0.82 * r))
    return out
