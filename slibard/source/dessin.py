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
        self.Fg = self.F * (1 - m['ecart'])        # le fût de gauche : un filet
        self.Fd = self.F * (1 + m['ecart'])        # le fût de droite : le gras
        self.Fm = self.F * (1 + 0.5 * m['ecart'])  # un fût seul

    def gd(self, W, L=None):
        """Les axes du fût de gauche et du fût de droite d'une lettre de largeur W (bords extérieurs à L et L + W)."""
        L = self.L if L is None else L
        return L + self.Fg / 2, L + W - self.Fd / 2

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
        return max(min(k * h, larg / 2 - 4, self.m.get('rayon', 1e9)), 1)

    def ep(self, p0, p1):
        u = _u(np.subtract(p1, p0)); s = abs(u[1])
        return self.B + (self.F - self.B) * s * s

    def sillage(self, xs, y, contre=None):
        """Le trait de vitesse : la barre du milieu file derrière la lettre, à gauche du fût d'axe xs.
        À Vitesse 0 il a une longueur nulle. contre : (p0, p1) du tronçon penché contre lequel il bute (A)."""
        n = self.m['sillage']
        if contre is not None:
            t = T([(xs - self.F / 2 - n, y), (xs, y)], fin=self.contre(contre[0], contre[1], 1))
            if n == 0:
                t.pts[0][0] = xs - self.F / 2      # longueur nulle (au bord près)
        else:
            x1 = xs - self.F / 2 + JOINT
            t = T([(x1 - n, y), (x1, y)])
        t.hors = True                              # ne compte pas dans la largeur de la lettre
        return t

    def contre(self, p0, p1, cote):
        """La coupe d'un tuyau qui bute contre le bord du tronçon p0→p1 (cote = +1 : son bord gauche)."""
        return ('contre', tuple(p0), tuple(p1), cote)


def lettre(tuyaux, m):
    """Finit une lettre : la gauche légère, la droite lourde. Chaque tuyau apprend où il est dans la lettre,
    et les bouts qui butent contre un fût se recalent sur son vrai bord (un fût de gauche est plus fin)."""
    if not tuyaux:
        return tuyaux
    for g in set(t.groupe for t in tuyaux):
        membres = [t for t in tuyaux if t.groupe == g]
        xs = [p[0] for t in membres if not t.plein and not getattr(t, 'hors', False) for p in t.pts] or [p[0] for t in membres for p in t.pts]
        bo = (min(xs), max(xs))
        for t in membres:
            t.boite = bo
    nominaux = [m['fut'] * f / 2 - JOINT for f in (1, 1 - m['ecart'], 1 + m['ecart'], 1 + 0.5 * m['ecart'])]
    nominaux += [n_ * e_ for n_ in list(nominaux) for e_ in set(t.ech for t in tuyaux) if e_ != 1]
    for t in tuyaux:
        if t.ferme:
            continue
        for i_bout, i_vois, coupe in ((0, 1, t.debut), (-1, -2, t.fin)):
            p, v = t.pts[i_bout], t.pts[i_vois]
            if coupe is not None or abs(p[1] - v[1]) > 1e-6:
                continue                                   # seulement les bouts horizontaux coupés d'équerre
            cale = False
            for q in tuyaux:
                if cale or q is t:                         # un bout se cale une seule fois, et jamais contre son propre tuyau
                    continue
                n = len(q.pts)
                for a in range(n if q.ferme else n - 1):
                    A, B = q.pts[a], q.pts[(a + 1) % n]
                    if abs(A[0] - B[0]) > 1e-6 or not (min(A[1], B[1]) - 1 <= p[1] <= max(A[1], B[1]) + 1):
                        continue
                    ecart = p[0] - A[0]
                    if min(abs(abs(ecart) - n_) for n_ in nominaux) < 0.75:
                        if q.groupe != t.groupe:
                            continue
                        w = q._ep(np.array([0.0, 1.0]), m, A[0])
                        p[0] = A[0] + (1 if ecart > 0 else -1) * (w / 2 - JOINT)
                        cale = True; break
    return tuyaux


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


_GROUPE = [0]


def reduit(tuyaux, s, dx=0.0, dy=0.0):
    """Les mêmes tuyaux en plus petit (exposants, © ® ™, %), posés en (dx, dy). Ils forment un groupe à part."""
    _GROUPE[0] += 1
    for t in tuyaux:
        t.pts = [np.array([p[0] * s + dx, p[1] * s + dy]) for p in t.pts]
        t.r = [r * s for r in t.r]
        t.ech *= s
        if t.ep is not None:
            t.ep = tuple(e * s for e in t.ep) if isinstance(t.ep, (tuple, list)) else t.ep * s
        for nom in ('debut', 'fin'):
            c = getattr(t, nom)
            if isinstance(c, tuple) and isinstance(c[0], str):
                setattr(t, nom, ('contre', tuple(np.array(c[1]) * s + (dx, dy)), tuple(np.array(c[2]) * s + (dx, dy)), c[3]))
            elif isinstance(c, tuple):
                setattr(t, nom, (tuple(np.array(c[0], float) * s + (dx, dy)), c[1]))
        t.groupe = _GROUPE[0]
    return tuyaux


def decale(tuyaux, dx=0.0, dy=0.0):
    """Les mêmes tuyaux, déplacés (sans changer de groupe)."""
    g = [t.groupe for t in tuyaux]
    reduit(tuyaux, 1.0, dx, dy)
    for t, gg in zip(tuyaux, g):
        t.groupe = gg
    return tuyaux


def retourne(tuyaux, cx, cy):
    """Les mêmes tuyaux, tournés d'un demi-tour autour de (cx, cy) : le 9 est un 6 retourné."""
    for t in tuyaux:
        t.pts = [np.array([2 * cx - p[0], 2 * cy - p[1]]) for p in t.pts]
        for nom in ('debut', 'fin'):
            c = getattr(t, nom)
            if isinstance(c, tuple) and not isinstance(c[0], str):
                setattr(t, nom, ((2 * cx - c[0][0], 2 * cy - c[0][1]), c[1]))
    return tuyaux
