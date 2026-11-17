# Les contours pleins (fusionnés) : pour les polices fixes, le crénage et les mesures.
from pathops import Path, op, PathOp


def chemin(contours):
    """Les contours d'un glyphe (listes de ('l', p) / ('c', p1, p2, p3)) fusionnés en un seul tracé."""
    tout = Path(); pen = tout.getPen()
    for c in contours:
        pen.moveTo(tuple(c[0][1]))
        for s in c[1:]:
            if s[0] == 'l':
                pen.lineTo(tuple(s[1]))
            else:
                pen.curveTo(tuple(s[1]), tuple(s[2]), tuple(s[3]))
        pen.closePath()
    a = op(tout, Path(), PathOp.UNION, fix_winding=True, keep_starting_points=False)
    return a


def rect(x0, y0, x1, y1):
    p = Path(); pen = p.getPen()
    pen.moveTo((x0, y0)); pen.lineTo((x1, y0)); pen.lineTo((x1, y1)); pen.lineTo((x0, y1)); pen.closePath()
    return p


def coupe(a, x0, y0, x1, y1):
    """Ce qui reste de a dans la boîte."""
    return op(a, rect(x0, y0, x1, y1), PathOp.INTERSECTION, fix_winding=True, keep_starting_points=False)
