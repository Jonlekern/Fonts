# Les mesures d'Overshoot, lues dans ses fichiers (on les lit, on ne les touche jamais).
import os
from functools import lru_cache
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.basePen import BasePen

RACINE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))


def chemin(graisse):
    return os.path.join(RACINE, 'overshoot', 'fonts', 'otf', f'Overshoot-{graisse}.otf')


@lru_cache(None)
def police(graisse):
    return TTFont(chemin(graisse))


def points(font, nom):
    """Les points d'appui (débuts et fins de segments) du glyphe, arrondis."""
    rp = RecordingPen(); font.getGlyphSet()[nom].draw(rp)
    return [tuple(round(v) for v in a[-1]) for op, a in rp.value if a]


class _Echantillons(BasePen):
    """Des points pris le long de chaque contour (les courbes découpées en 24)."""
    def __init__(self, gs):
        super().__init__(gs); self.contours = []; self.cur = []

    def _moveTo(self, p):
        self.cur = [p]

    def _lineTo(self, p):
        a = self.cur[-1]
        self.cur += [(a[0] + (p[0] - a[0]) * k / 8, a[1] + (p[1] - a[1]) * k / 8) for k in range(1, 9)]

    def _curveToOne(self, p1, p2, p3):
        p0 = self.cur[-1]
        for k in range(1, 25):
            t = k / 24; u = 1 - t
            self.cur.append(tuple(u ** 3 * a + 3 * u * u * t * b + 3 * u * t * t * c + t ** 3 * d
                                  for a, b, c, d in zip(p0, p1, p2, p3)))

    def _closePath(self):
        self.contours.append(self.cur); self.cur = []


def expo_du(font, nom='o'):
    """L'exposant de superellipse du contour extérieur, ajusté aux moindres carrés."""
    gs = font.getGlyphSet(); pen = _Echantillons(gs); gs[nom].draw(pen)
    ext = max(pen.contours, key=lambda c: (max(x for x, _ in c) - min(x for x, _ in c)))
    x0, x1 = min(x for x, _ in ext), max(x for x, _ in ext)
    y0, y1 = min(y for _, y in ext), max(y for _, y in ext)
    cx, cy, a, b = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2, (y1 - y0) / 2
    best = None
    for k in range(200, 801):
        n = k / 100
        err = sum(((abs((x - cx) / a) ** n + abs((y - cy) / b) ** n) ** (1 / n) - 1) ** 2 for x, y in ext)
        if best is None or err < best[0]:
            best = (err, n)
    return best[1]


@lru_cache(None)
def releve(graisse):
    f = police(graisse)
    xs = sorted({x for x, y in points(f, 'H')})
    e = points(f, 'E'); l = sorted({x for x, y in points(f, 'l')}); z = points(f, 'z')
    r = points(f, 'R')
    pied_r = max(x for x, y in r if y == 0)
    fut_r = max(x for x, y in r if 0 < y < 400)
    return {
        'fut_cap': xs[1] - xs[0], 'barre_cap': e[2][1], 'fut_min': l[1] - l[0], 'barre_min': z[2][1],
        'pied': pied_r - fut_r, 'expo': expo_du(f, 'o'), 'expo_O': expo_du(f, 'O'),
        'cap': f['OS/2'].sCapHeight, 'x': f['OS/2'].sxHeight,
    }
