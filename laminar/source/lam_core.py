# LAMINAR : moteur (Art déco : pleins verticaux, déliés horizontaux, ronds au compas, lignes de vitesse)
import math
import pathops

CAP, SC, DESC, OV = 720, 500, -200, 10      # capitales, petites capitales, jambage, débord des ronds

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
def X(a, b): return pathops.op(a, b, pathops.PathOp.XOR)

K = 0.5522847498
def ell(cx, cy, a, b):
    p = P(); pen = p.getPen(); pen.moveTo((cx + a, cy))
    pen.curveTo((cx + a, cy + K * b), (cx + K * a, cy + b), (cx, cy + b))
    pen.curveTo((cx - K * a, cy + b), (cx - a, cy + K * b), (cx - a, cy))
    pen.curveTo((cx - a, cy - K * b), (cx - K * a, cy - b), (cx, cy - b))
    pen.curveTo((cx + K * a, cy - b), (cx + a, cy - K * b), (cx + a, cy))
    pen.closePath(); return p
def circ(cx, cy, r): return ell(cx, cy, r, r)
def sector(cx, cy, a0, a1, R=3000):
    n = max(2, int(abs(a1 - a0) / 8) + 1)
    pts = [(cx, cy)] + [(cx + R * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + R * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
    return poly(pts)
def half(p, q, side=1, F=4000):
    """demi-plan à gauche (side=1) ou à droite (-1) de la droite p→q"""
    dx, dy = q[0] - p[0], q[1] - p[1]; L = math.hypot(dx, dy); ux, uy = dx / L, dy / L; nx, ny = -uy * side, ux * side
    a = (p[0] - ux * F, p[1] - uy * F); b = (p[0] + ux * F, p[1] + uy * F)
    return poly([a, b, (b[0] + nx * F, b[1] + ny * F), (a[0] + nx * F, a[1] + ny * F)])
def xf(p, m):
    a, b, c, d, e, f = m
    from fontTools.pens.recordingPen import RecordingPen
    rp = RecordingPen(); p.draw(rp); out = P(); pen = out.getPen()
    T = lambda q: (a * q[0] + c * q[1] + e, b * q[0] + d * q[1] + f)
    for op, args in rp.value: getattr(pen, op)(*[T(q) for q in args])
    return out
def mv(p, dx, dy=0): return xf(p, (1, 0, 0, 1, dx, dy))
def mirror(p, x): return xf(p, (-1, 0, 0, 1, 2 * x, 0))
def flipv(p, y): return xf(p, (1, 0, 0, -1, 0, 2 * y))
def rot(p, ang, cx, cy):
    c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    return xf(p, (c, s, -s, c, cx - c * cx + s * cy, cy - s * cx - c * cy))
def bounds(p):
    b = p.bounds
    return b if b else (0, 0, 0, 0)
def stroke(p, q, t):
    """trait droit d'épaisseur t (bouts carrés) de p à q"""
    dx, dy = q[0] - p[0], q[1] - p[1]; L = math.hypot(dx, dy); nx, ny = -dy / L * t / 2, dx / L * t / 2
    return poly([(p[0] + nx, p[1] + ny), (q[0] + nx, q[1] + ny), (q[0] - nx, q[1] - ny), (p[0] - nx, p[1] - ny)])
def diag(xb, xt, w, y0, y1):
    """oblique : bas gauche en xb (à y0), haut gauche en xt (à y1), largeur horizontale w"""
    return poly([(xb, y0), (xb + w, y0), (xt + w, y1), (xt, y1)])
def hw(t, dx, dy):
    """largeur horizontale d'un trait d'épaisseur t qui monte de dy sur dx"""
    return t * math.hypot(dx, dy) / abs(dy)
def fit_w(t, span, H, n=8):
    """largeur horizontale d'une oblique qui couvre span (bord gauche bas → bord droit haut) sur H"""
    w = t
    for _ in range(n): w = hw(t, span - w, H)
    return w

def ring_off(cx, cy, R, thick, thin, side=-1):
    """rond au compas : cercle extérieur R, cercle intérieur décalé ; plein (thick) du côté side (-1 gauche, 1 droite), délié de l'autre"""
    r = R - (thick + thin) / 2; d = (thick - thin) / 2
    return D(circ(cx, cy, R), circ(cx - side * d, cy, r))
def oring(cx, cy, R, thick, thin, side=-1, vt=None):
    """rond à contraste vertical : extérieur cercle, intérieur ellipse (déliés en haut/bas)"""
    vt = thin if vt is None else vt
    return D(circ(cx, cy, R), ell(cx, cy, R - thick, R - vt))
def stadium(x0, y0, x1, y1):
    """rectangle aux bouts ronds (le plus petit côté fait le diamètre)"""
    w, h = x1 - x0, y1 - y0
    if h >= w:
        r = w / 2; return U(rect(x0, y0 + r, x1, y1 - r), circ(x0 + r, y0 + r, r), circ(x0 + r, y1 - r, r))
    r = h / 2; return U(rect(x0 + r, y0, x1 - r, y1), circ(x0 + r, y0 + r, r), circ(x1 - r, y0 + r, r))

def xdil(p, g, step):
    """épaissit horizontalement (somme de Minkowski avec un segment [-g, g])"""
    n = max(2, int(math.ceil(2 * g / max(step, 1))))
    return U(p, *[mv(p, -g + 2 * g * i / n, 0) for i in range(n + 1)])
def dil(p, g, n=16):
    """épaissit dans toutes les directions (union de copies décalées)"""
    return U(p, *[mv(p, g * math.cos(2 * math.pi * i / n), g * math.sin(2 * math.pi * i / n)) for i in range(n)])

class Wt:
    """une graisse : S plein, h délié ; les chasses suivent"""
    def __init__(s, num, S, h, wclass):
        s.num, s.S, s.h, s.wclass = num, S, h, wclass
        s.SB = round(18 + 0.30 * S)                  # approche d'un fût
        s.SBO = round(0.55 * s.SB)                    # approche d'un rond
        s.SBD = round(0.12 * s.SB)                    # approche d'une oblique
        # lignes de vitesse : trois bandes, mêmes hauteurs pour capitales et petites capitales
        s.B = round(12 + 0.12 * S)                   # épaisseur d'une ligne
        s.BG = round(0.62 * s.B)                     # blanc entre deux lignes
        s.GAP = round(6 + 0.06 * S)                  # blanc entre une ligne et la lettre
        mid = 0.36 * SC
        tot = 3 * s.B + 2 * s.BG; y0 = mid - tot / 2
        s.BANDS = [(round(y0 + i * (s.B + s.BG)), round(y0 + i * (s.B + s.BG)) + s.B) for i in range(3)]

class C:
    """jeu de proportions pour une hauteur donnée (capitales ou petites capitales)"""
    def __init__(s, w, H, sc=False, S=None):
        s.w, s.H, s.sc = w, H, sc
        k = H / CAP
        s.S = round(w.S * (0.90 if sc else 1.0)) if S is None else round(S)      # plein
        s.h = w.h                                     # délié (même fil partout)
        s.ov = round(OV * k)
        s.BAR = round(0.62 * H)                      # barres hautes (A E F H R) : axe de la barre
        s.CT = round(0.40 * H) if not sc else round(0.46 * H)   # contre-forme courante
        s.W = s.CT + 2 * s.S                         # chasse d'un H (encre)

class Gl:
    """encre + bords d'approche (x0, x1) + type d'approche (S fût, O rond, D oblique)"""
    def __init__(s, ink, x0=None, x1=None, sides='SS', adv=None):
        b = bounds(ink)
        s.ink = ink; s.x0 = b[0] if x0 is None else x0; s.x1 = b[2] if x1 is None else x1; s.sides = sides; s.adv = adv

def sb_of(w, c, k):
    f = {'S': w.SB, 'O': w.SBO, 'D': w.SBD, 'N': 0, 'W': round(1.4 * w.SB)}[k]
    if c is not None and c.sc: f = round(f * 0.9)
    return f

def place(g, w, c):
    """met la lettre à sa place : approche gauche, chasse"""
    l = sb_of(w, c, g.sides[0]); r = sb_of(w, c, g.sides[1])
    p = mv(g.ink, l - g.x0); adv = g.adv if g.adv is not None else (g.x1 - g.x0) + l + r
    return p, adv
