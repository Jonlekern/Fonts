# ISOSLAB : géométrie de base (slab étroite, fûts presque monolignes, empattements carrés raccordés)
import math
import pathops

CAP, OV = 700, 12

def P(): return pathops.Path()
def poly(pts):
    p = P(); pen = p.getPen(); pen.moveTo(pts[0])
    for q in pts[1:]: pen.lineTo(q)
    pen.closePath(); return p
def rect(x0, y0, x1, y1): return poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
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
def unit(v): l = math.hypot(*v); return (v[0] / l, v[1] / l)

def wedge(Q, u, v, R):
    """congé : coin rentrant arrondi entre les demi-droites u et v partant de Q (une seule courbe)"""
    u, v = unit(u), unit(v); ang = math.acos(max(-1, min(1, u[0] * v[0] + u[1] * v[1])))
    d = R / math.tan(ang / 2); k = 4 / 3 * math.tan((math.pi - ang) / 4) * R
    Tu = (Q[0] + u[0] * d, Q[1] + u[1] * d); Tv = (Q[0] + v[0] * d, Q[1] + v[1] * d)
    b = unit((u[0] + v[0], u[1] + v[1])); Qi = (Q[0] - b[0] * 3, Q[1] - b[1] * 3)
    p = P(); pen = p.getPen(); pen.moveTo(Qi); pen.lineTo(Tu)
    pen.curveTo((Tu[0] - u[0] * k, Tu[1] - u[1] * k), (Tv[0] - v[0] * k, Tv[1] - v[1] * k), Tv); pen.closePath(); return p

def se_k(n):
    """longueur de poignée (en fraction du rayon) d'un quart de superellipse d'exposant n en une seule courbe"""
    return (8 * 2 ** (-1 / n) - 4) / 3

def superell(cx, cy, a, b, n=2.7, N=None):
    """superellipse en 4 vraies courbes (pas de polygone : aucune facette à la loupe)"""
    k = se_k(n); p = P(); pen = p.getPen(); pen.moveTo((cx + a, cy))
    pen.curveTo((cx + a, cy + k * b), (cx + k * a, cy + b), (cx, cy + b))
    pen.curveTo((cx - k * a, cy + b), (cx - a, cy + k * b), (cx - a, cy))
    pen.curveTo((cx - a, cy - k * b), (cx - k * a, cy - b), (cx, cy - b))
    pen.curveTo((cx + k * a, cy - b), (cx + a, cy - k * b), (cx + a, cy))
    pen.closePath(); return p

def se_x(a, b, y, n=2.7):
    """demi-largeur d'une superellipse (a, b) à la hauteur y (relative au centre)"""
    t = abs(y) / b
    return a * (1 - t ** n) ** (1 / n) if t < 1 else 0.0

def pbar(p, q, w):
    dx, dy = q[0] - p[0], q[1] - p[1]; L = math.hypot(dx, dy); nx, ny = -dy / L * w / 2, dx / L * w / 2
    return poly([(p[0] + nx, p[1] + ny), (q[0] + nx, q[1] + ny), (q[0] - nx, q[1] - ny), (p[0] - nx, p[1] - ny)])

class Wt:
    def __init__(s, st):
        s.ST = st; s.TH = round(0.80 * st)          # fûts presque monolignes
        s.SL = round(0.92 * st + 10)                 # épaisseur de l'empattement : un poil plus gras que le fût
        s.SX = round(0.42 * st + 22)                 # avancée de l'empattement
        s.R = round(0.45 * s.SX)                     # congé : la moitié de l'avancée, le bout reste carré
        s.CW = round(110 + 0.90 * st)                # contre-forme d'une capitale droite : toujours ~70 de jour entre deux empattements
        s.BK = round(0.15 * CAP)                     # hauteur des becs (E, F, L, T, Z)
        s.W = 2 * st + s.CW                          # largeur d'un H (sans empattements)
