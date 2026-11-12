# LAMINAR : lignes de vitesse (blanches dans la lettre, noires entre les lettres)
import math
from lam_core import *
from fontTools.pens.recordingPen import RecordingPen

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

def merge(iv):
    iv = sorted(iv); out = []
    for a, b in iv:
        if out and a <= out[-1][1]: out[-1] = (out[-1][0], max(out[-1][1], b))
        else: out.append((a, b))
    return out

def proj(segs, y0, y1, step=2):
    """intervalles en x couverts par l'encre entre y0 et y1"""
    iv = []; y = y0 + 0.01
    while y <= y1:
        iv += spans_at(segs, y); y += step
    return merge(iv)

def free(ink, w, y0, y1, x0, x1):
    """morceaux de [x0, x1] libres à GAP près de l'encre, pour une bande y0..y1"""
    segs = flat(ink); gy = round(0.5 * w.GAP)
    busy = merge([(a - w.GAP, b + w.GAP) for a, b in proj(segs, y0 - gy, y1 + gy)])
    out = []; cur = x0
    for a, b in busy:
        if b <= cur: continue
        if a > cur: out.append((cur, min(a, x1)))
        cur = max(cur, b)
        if cur >= x1: break
    if cur < x1: out.append((cur, x1))
    return [(a, b) for a, b in out if b - a > 0.5]

def extent(ink, w):
    """bords gauche et droit de l'encre à la hauteur des lignes"""
    segs = flat(ink); y0 = w.BANDS[0][0] - w.GAP; y1 = w.BANDS[-1][1] + w.GAP
    iv = proj(segs, y0, y1)
    return (iv[0][0], iv[-1][1]) if iv else None

def capsule(x0, x1, y0, y1, left_round=False, right_round=False):
    r = (y1 - y0) / 2; cy = (y0 + y1) / 2; p = rect(x0 + (r if left_round else 0), y0, x1 - (r if right_round else 0), y1)
    if left_round: p = U(p, circ(x0 + r, cy, r))
    if right_round: p = U(p, circ(x1 - r, cy, r))
    return p

def taper(x0, x1, y0, y1, k=0.42):
    """trait qui s'affine vers la gauche jusqu'à un bout rond (pas de pointe)"""
    t = y1 - y0; cy = (y0 + y1) / 2; tl = k * t; r = tl / 2
    return U(poly([(x0 + r, cy - tl / 2), (x1, y0), (x1, y1), (x0 + r, cy + tl / 2)]), circ(x0 + r, cy, r))

TRAIL = (0.70, 1.0, 0.55)
LAST_DX = [0]        # longueur de chaque ligne de la traîne (haut, milieu, bas), en part de la traîne

def speed(ink, adv, w, pos='med', mode='cut', o=1.5):
    """pos : med, init, fina, isol ; mode : cut (lignes blanches dans la lettre), behind (derrière), trail (traîne seule)"""
    Ltr = round(0.34 * CAP) if pos in ('init', 'isol') else 0          # traîne à gauche
    Lend = round(0.10 * CAP) if pos in ('fina', 'isol') else 0          # sortie à droite, bout rond
    e0 = extent(ink, w); m = w.GAP + round(1.0 * w.B)               # chaque lien noir entre deux lettres fait au moins 2,6 lignes
    if e0:
        l = max(0, m - e0[0]); r = max(0, m - (adv - e0[1])); ink = mv(ink, l); adv += l + r
    ink = mv(ink, Ltr); adv2 = adv + Ltr + Lend
    LAST_DX[0] = Ltr + (l if e0 else 0)
    ex = extent(ink, w); B = w.BANDS
    out = ink
    if mode == 'cut': out = D(ink, *[rect(-3000, y0, 6000, y1) for y0, y1 in B])
    lines = []
    for k, (y0, y1) in enumerate(B):
        if mode == 'trail':
            if pos in ('init', 'isol') and ex:
                xs = ex[0] - w.GAP; L = TRAIL[k] * Ltr
                if xs - (Ltr - L) > y1 - y0: lines.append(taper(Ltr - L, xs, y0, y1))
            continue
        x0 = -o if pos in ('med', 'fina') else 0
        x1 = adv2 + o if pos in ('med', 'init') else (ex[1] + w.GAP + Lend if ex else adv2)
        fr = free(ink, w, y0, y1, x0, x1)
        for i, (a, b) in enumerate(fr):
            first = (i == 0 and a <= x0 + 0.01); last = (i == len(fr) - 1 and b >= x1 - 0.01)
            if pos in ('init', 'isol') and first:
                L = TRAIL[k] * Ltr; a2 = Ltr - L
                if b - a2 > (y1 - y0): lines.append(taper(a2, b, y0, y1))
                continue
            if pos in ('fina', 'isol') and last:
                if b - a > (y1 - y0): lines.append(capsule(a, b, y0, y1, right_round=True))
                continue
            if not first and not last: continue          # dans les contre-formes : rien, la ligne passe en blanc
            lines.append(rect(a, y0, b, y1))
    return U(out, *lines), adv2
