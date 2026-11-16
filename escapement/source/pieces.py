# Les pièces : rectangles, rondes entre l'ovale et le carré, ouvertures à bouts plats.
# Les outils de base sont ceux de SHKVAL (mêmes noms, mêmes signatures).
from pathops import Path, op, PathOp
from fontTools.pens.transformPen import TransformPen


def _propre(p):
    return op(p, Path(), PathOp.UNION, fix_winding=True, keep_starting_points=False)


def rect(x0, y0, x1, y1):
    p = Path(); pen = p.getPen()
    pen.moveTo((x0, y0)); pen.lineTo((x1, y0)); pen.lineTo((x1, y1)); pen.lineTo((x0, y1)); pen.closePath()
    return p


def poly(*pts):
    p = Path(); pen = p.getPen(); pen.moveTo(pts[0])
    for q in pts[1:]:
        pen.lineTo(q)
    pen.closePath()
    return _propre(p)


def union(*formes):
    """L'union de toutes les formes. pathops se trompe parfois quand deux formes ont des bords communs :
    on la calcule de deux façons et on garde la plus grande (une union ratée perd toujours un morceau)."""
    tout = Path(); pen = tout.getPen()
    for f in formes:
        f.draw(pen)
    a = _propre(tout)
    b = Path()
    for f in formes:
        b = op(b, f, PathOp.UNION, fix_winding=True, keep_starting_points=False)
    return a if abs(a.area) >= abs(b.area) else b


def moins(a, b):
    return op(a, b, PathOp.DIFFERENCE, fix_winding=True, keep_starting_points=False)


def coupe(a, x0, y0, x1, y1):
    """Ce qui reste de a dans la boîte."""
    return op(a, rect(x0, y0, x1, y1), PathOp.INTERSECTION, fix_winding=True, keep_starting_points=False)


def inter(a, b):
    return op(a, b, PathOp.INTERSECTION, fix_winding=True, keep_starting_points=False)


def transforme(p, m):
    out = Path(); p.draw(TransformPen(out.getPen(), m))
    return _propre(out)


def decale(p, dx, dy=0):
    return transforme(p, (1, 0, 0, 1, dx, dy))


def miroir(p, chasse):
    return transforme(p, (-1, 0, 0, 1, chasse, 0))


def bornes(p):
    x0, y0, x1, y1 = p.bounds
    return round(x0), round(y0), round(x1), round(y1)


def aire(p):
    return abs(p.area)


def courses(p, y):
    """Les morceaux d'encre que coupe la ligne horizontale y, de gauche à droite."""
    bande = coupe(p, -5000, y, 5000, y + 1)
    return sorted((round(c.bounds[0]), round(c.bounds[2])) for c in bande.contours)


def egaux(a, b, tol=1.0):
    return op(a, b, PathOp.XOR, fix_winding=True).area < tol


def _poignee(expo):
    """Longueur des poignées (en part du rayon) pour qu'un quart de courbe passe par le point
    de la superellipse sur la diagonale : x(½) = r·(4+3k)/8 = r·2^(-1/n)."""
    return (8 * 2 ** (-1 / expo) - 4) / 3


def superellipse(cx, cy, rx, ry, expo):
    """La forme pleine : |x/rx|^n + |y/ry|^n = 1, un quart de courbe par quadrant."""
    k = _poignee(expo); p = Path(); pen = p.getPen()
    pen.moveTo((cx + rx, cy))
    pen.curveTo((cx + rx, cy + k * ry), (cx + k * rx, cy + ry), (cx, cy + ry))
    pen.curveTo((cx - k * rx, cy + ry), (cx - rx, cy + k * ry), (cx - rx, cy))
    pen.curveTo((cx - rx, cy - k * ry), (cx - k * rx, cy - ry), (cx, cy - ry))
    pen.curveTo((cx + k * rx, cy - ry), (cx + rx, cy - k * ry), (cx + rx, cy))
    pen.closePath()
    return _propre(p)


def anneau(cx, cy, rx, ry, ep_v, ep_h, expo):
    """La ronde moins sa contre-forme : ep_v d'épaisseur sur les côtés, ep_h en haut et en bas."""
    return moins(superellipse(cx, cy, rx, ry, expo), superellipse(cx, cy, rx - ep_v, ry - ep_h, expo))


def ouverture(forme, x0, y_bas, y_haut, cote='droite'):
    """Ouvre la forme du côté donné entre deux hauteurs : les deux bouts sortent coupés à l'horizontale."""
    if cote == 'droite':
        return moins(forme, rect(x0, y_bas, 5000, y_haut))
    return moins(forme, rect(-5000, y_bas, x0, y_haut))
