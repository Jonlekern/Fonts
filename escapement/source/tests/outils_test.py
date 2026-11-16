# Outils de mesure pour les tests.
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt
from pathops import Path, op, PathOp, FillType
from fontTools.pens.basePen import BasePen


def sans_recouvrement(p):
    """Vrai si aucun contour n'en recouvre un autre : le remplissage non nul et le pair-impair donnent la même encre."""
    nz = Path(); p.draw(nz.getPen()); nz.fillType = FillType.WINDING
    eo = Path(); p.draw(eo.getPen()); eo.fillType = FillType.EVEN_ODD
    a = op(nz, Path(), PathOp.UNION); b = op(eo, Path(), PathOp.UNION)
    return op(a, b, PathOp.XOR).area < 1.0


class _Poly(BasePen):
    def __init__(s):
        super().__init__(None); s.polys = []; s.cur = []
    def _moveTo(s, p): s.cur = [p]
    def _lineTo(s, p): s.cur.append(p)
    def _curveToOne(s, a, b, c):
        p0 = s.cur[-1]
        for k in range(1, 17):
            t = k / 16; u = 1 - t
            s.cur.append(tuple(u ** 3 * q0 + 3 * u * u * t * q1 + 3 * u * t * t * q2 + t ** 3 * q3 for q0, q1, q2, q3 in zip(p0, a, b, c)))
    def _closePath(s): s.polys.append(s.cur); s.cur = []


def trait_max(p):
    """L'épaisseur la plus forte : le diamètre du plus grand cercle qui tient dans l'encre (en unités)."""
    pen = _Poly(); p.draw(pen)
    x0, y0, x1, y1 = p.bounds
    im = Image.new('1', (int(x1 - x0) + 4, int(y1 - y0) + 4), 0)
    for poly in pen.polys:
        q = Image.new('1', im.size, 0)
        ImageDraw.Draw(q).polygon([(x - x0 + 2, y1 - y + 2) for x, y in poly], fill=1)
        im = Image.fromarray(np.logical_xor(np.array(im), np.array(q)))
    return 2 * distance_transform_edt(np.array(im)).max()
