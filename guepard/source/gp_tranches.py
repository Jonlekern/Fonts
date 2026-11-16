"""Découpe d'un glyphe en tranches horizontales.

Les 3 tranches basses (rangs 0, 1, 2) sont prises dans le bas noir ; le rang 3 est le haut.
À l'état fermé, les tranches se chevauchent de RECOUVRE unités : pas de joint visible.
"""
import pathops
from fontTools.pens.recordingPen import DecomposingRecordingPen

COUPES = (110, 220, 330)
RECOUVRE = 4
INF = 10000


def _chemin(glyphset, nom):
    rec = DecomposingRecordingPen(glyphset)
    glyphset[nom].draw(rec)
    p = pathops.Path()
    rec.replay(p.getPen())
    return p


def _rect(y0, y1):
    r = pathops.Path()
    pen = r.getPen()
    pen.moveTo((-INF, y0)); pen.lineTo((-INF, y1)); pen.lineTo((INF, y1)); pen.lineTo((INF, y0)); pen.closePath()
    return r


def bornes_fermees(rang):
    """(bas, haut) de la tranche à l'état fermé."""
    bas = -INF if rang == 0 else COUPES[rang - 1] - RECOUVRE
    haut = INF if rang == len(COUPES) else COUPES[rang] + RECOUVRE
    return bas, haut


def _points(chemin):
    """Contours au format [[x, y, on], ...] depuis un chemin pathops (quadratiques)."""
    contours, cur = [], None
    for op, pts in chemin.segments:
        if op == "moveTo":
            cur = [[pts[0][0], pts[0][1], 1]]
        elif op == "lineTo":
            cur.append([pts[0][0], pts[0][1], 1])
        elif op == "qCurveTo":
            if cur is None:
                cur = []
            for p in pts[:-1]:
                cur.append([p[0], p[1], 0])
            if pts[-1] is not None:
                cur.append([pts[-1][0], pts[-1][1], 1])
        elif op == "curveTo":
            raise ValueError("cubique inattendue")
        elif op in ("closePath", "endPath"):
            if cur and len(cur) > 1 and cur[-1][:2] == cur[0][:2] and cur[-1][2] and cur[0][2]:
                cur.pop()
            if cur and len(cur) >= 3:
                contours.append(cur)
            cur = None
    return contours


def decouper(glyphset, nom):
    """Liste de 4 tranches (rang 0..3), chacune une liste de contours [[x, y, on], ...]."""
    p = _chemin(glyphset, nom)
    tranches = []
    for rang in range(len(COUPES) + 1):
        bas, haut = bornes_fermees(rang)
        t = pathops.op(p, _rect(bas, haut), pathops.PathOp.INTERSECTION, clockwise=True)
        tranches.append(_points(t))
    return tranches
