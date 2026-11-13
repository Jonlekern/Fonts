# Les pièces : on prend des contours d'Overshoot, on les coupe, on les retourne, on les assemble.
from pathops import Path, op, PathOp
from fontTools.pens.transformPen import TransformPen


def _propre(p):
    return op(p, Path(), PathOp.UNION, fix_winding=True, keep_starting_points=False)


def glyphe(font, nom):
    p = Path(); font.getGlyphSet()[nom].draw(p.getPen())
    return _propre(p)


def rect(x0, y0, x1, y1):
    p = Path(); pen = p.getPen()
    pen.moveTo((x0, y0)); pen.lineTo((x1, y0)); pen.lineTo((x1, y1)); pen.lineTo((x0, y1)); pen.closePath()
    return p


def union(*formes):
    out = Path()
    for f in formes:
        out = op(out, f, PathOp.UNION, fix_winding=True, keep_starting_points=False)
    return out


def moins(a, b):
    return op(a, b, PathOp.DIFFERENCE, fix_winding=True, keep_starting_points=False)


def coupe(a, x0, y0, x1, y1):
    """Ce qui reste de a dans la boîte."""
    return op(a, rect(x0, y0, x1, y1), PathOp.INTERSECTION, fix_winding=True, keep_starting_points=False)


def transforme(p, m):
    out = Path(); p.draw(TransformPen(out.getPen(), m))
    return _propre(out)


def decale(p, dx, dy=0):
    return transforme(p, (1, 0, 0, 1, dx, dy))


def miroir(p, chasse):
    """Retourné gauche-droite dans la même chasse (R → Я, N → И)."""
    return transforme(p, (-1, 0, 0, 1, chasse, 0))


def renverse(p, haut):
    """Retourné haut-bas entre 0 et haut (L → Г)."""
    return transforme(p, (1, 0, 0, -1, 0, haut))


def bornes(p):
    x0, y0, x1, y1 = p.bounds
    return round(x0), round(y0), round(x1), round(y1)


def courses(p, y):
    """Les morceaux d'encre que coupe la ligne horizontale y, de gauche à droite."""
    bande = coupe(p, -5000, y, 5000, y + 1)
    out = []
    for c in bande.contours:
        x0, _, x1, _ = c.bounds
        out.append((round(x0), round(x1)))
    return sorted(out)


def egaux(a, b, tol=1.0):
    return op(a, b, PathOp.XOR, fix_winding=True).area < tol
