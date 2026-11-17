# Les outils de dessin : une lettre se décrit avec quelques tuyaux.
import math
import numpy as np
from tuyaux import Tuyau as T, _u, _gauche

JOINT = 2          # un tuyau qui bute contre un autre y entre de 2 unités


class D:
    """Les mesures d'une graisse, avec les repères qui servent partout."""

    def __init__(self, m):
        self.m = m
        self.F, self.B, self.d = m['fut'], m['barre'], m['dep']
        self.cap, self.x, self.asc, self.desc = m['cap'], m['x'], m['asc'], m['desc']
        self.L, self.Lr, self.g = m['app'], m['appr'], m['large']
        self.c = m['coude']

    # axe d'une barre en haut / en bas d'une hauteur
    def haut(self, h, rond=False):
        return h - self.B / 2 + (self.d if rond else 0)

    def bas(self, rond=False, y=0):
        return y + self.B / 2 - (self.d if rond else 0)

    def taille(self, h=None, n=1):
        """La hauteur de l'axe d'une barre du milieu : taille basse, mais jamais collée à la barre du bas."""
        h = self.cap if h is None else h
        return max(self.m['taille'] * h, 2.05 * self.B)

    def R(self, larg, h=None, k=0.44):
        """Le grand rayon d'une ronde : large, mais qui laisse un peu de droit."""
        h = self.x if h is None else h
        return max(min(k * h, larg / 2 - 4), 1)

    def ep(self, p0, p1):
        u = _u(np.subtract(p1, p0)); s = abs(u[1])
        return self.B + (self.F - self.B) * s * s

    def contre(self, p0, p1, cote):
        """La coupe d'un tuyau qui bute contre le bord du tronçon p0→p1 (cote = +1 : son bord gauche)."""
        u = _u(np.subtract(p1, p0)); n = _gauche(u)
        return (np.asarray(p0, float) + n * cote * (self.ep(p0, p1) / 2 - JOINT), u)


def fut(x, y0, y1, **k):
    return T([(x, y0), (x, y1)], **k)


def barre(x0, x1, y, **k):
    return T([(x0, y), (x1, y)], **k)


def point(cx, cy, taille):
    """Un point : une pastille entre le rond et le carré."""
    a = taille / 4
    return T([(cx - a, cy - a), (cx - a, cy + a), (cx + a, cy + a), (cx + a, cy - a)], r=a, ferme=True, disque=True, ep=taille / 2)


def boite(tuyaux, m, chrome=0):
    xs = [p[0] for t in tuyaux for c in t.contours(m, chrome) for s in c for p in s[1:]]
    ys = [p[1] for t in tuyaux for c in t.contours(m, chrome) for s in c for p in s[1:]]
    return min(xs), min(ys), max(xs), max(ys)
