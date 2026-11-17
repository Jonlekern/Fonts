# Le moteur à tuyaux d'Époque.
# Une lettre est une liste de tuyaux. Un tuyau est un tracé (des droites, des virages arrondis) avec une épaisseur.
# Rien n'est découpé après coup : à toute graisse, toute pente et tout chrome, un tuyau sort les mêmes contours
# avec les mêmes points. C'est ce qui permet la police variable.
import math
import numpy as np

RECOUVRE = 1.0
MINI = 2.4              # le plus petit chanfrein d'un angle vif


def _u(v):
    v = np.asarray(v, float); l = math.hypot(*v)
    return v / l if l > 1e-9 else np.array([1.0, 0.0])


def _gauche(u):
    return np.array([-u[1], u[0]])


def _croise(p, d, q, e):
    """Le point où la droite (p, d) coupe la droite (q, e). None si elles sont parallèles."""
    den = d[0] * e[1] - d[1] * e[0]
    if abs(den) < 1e-9:
        return None
    t = ((q[0] - p[0]) * e[1] - (q[1] - p[1]) * e[0]) / den
    return np.asarray(p, float) + t * np.asarray(d, float)


class Tuyau:
    """pts : les points de passage de l'axe. r : le rayon de l'axe à chaque point intérieur (0 = angle vif).
    debut, fin : la coupe de chaque bout — None (d'équerre), 'h' (à l'horizontale), 'v' (à la verticale),
    ou (point, direction) pour couper sur une droite. ferme : le tracé se referme (O, o).
    plein : jamais de filets (accents, ponctuation). ep : épaisseur imposée (sinon celle de la graisse).
    disque : tracé fermé rempli (points). tension : virages plus ou moins tendus."""

    def __init__(self, pts, r=0, debut=None, fin=None, ferme=False, plein=False, ep=None, disque=False, tension=None, k=None):
        self.pts = [np.asarray(p, float) for p in pts]
        n = len(self.pts)
        nb = n if ferme else n - 2
        self.r = list(r) if isinstance(r, (list, tuple)) else [r] * max(nb, 0)
        assert len(self.r) == max(nb, 0), (len(self.r), nb)
        self.debut, self.fin, self.ferme, self.plein, self.ep, self.disque = debut, fin, ferme, plein or disque, ep, disque
        self.tension = tension
        self.k = list(k) if k is not None else [1.0] * n       # l'épaisseur à chaque point (1 = pleine, 0 = en pointe) : les traits effilés

    boite = None        # (gauche, droite) de la lettre : posé par dessin.lettre()
    ech = 1.0           # un tuyau réduit (exposants, © ® ™) : ses épaisseurs se réduisent avec lui
    groupe = 0          # les tuyaux d'un même groupe partagent leur gauche et leur droite

    # --- l'épaisseur d'un tronçon : selon sa direction (verticales pleines, horizontales un peu plus fines)
    # --- et selon sa place dans la lettre : la gauche est légère, la droite lourde
    def _ep(self, u, m, x=None):
        if self.ep is not None:
            ev, eh = (self.ep if isinstance(self.ep, (tuple, list)) else (self.ep, self.ep))
        else:
            ev, eh = m['fut'], m['barre']
            if self.boite is not None and x is not None and self.boite[1] - self.boite[0] > 1:
                k = min(1.0, max(0.0, (x - self.boite[0]) / (self.boite[1] - self.boite[0])))
                ev = ev * (1 - m['ecart'] + 2 * m['ecart'] * k)
            else:
                ev = ev * (1 + 0.5 * m['ecart'])         # un fût seul (I, l) : entre le moyen et le gras
        s = abs(u[1])               # 1 : vertical, 0 : horizontal
        return (eh + (ev - eh) * s * s) * self.ech

    def _bandes(self, w, m, chrome, monte=0.0):
        """Les bandes dans l'épaisseur, en décalages (gauche du trajet positif).
        La gauche de la lettre est légère, la droite lourde : deux filets à gauche, la bande pleine à droite.
        monte = +1 quand le tronçon monte (sa gauche est la gauche de la lettre), −1 quand il descend ;
        entre les deux (barres, haut et bas des rondes), les trois bandes s'égalisent en douceur."""
        if True:                                   # le Chrome en trois bandes est retiré : une seule bande, le trait plein
            return [(-w / 2, w / 2)]
        f = min(1.15, max(0.55, w / m['fut'])) ** 0.5       # un trait fin a des filets plus fins
        t, g = m['filet'] * f, m['blanc'] * f
        coeur = w - 2 * t - 2 * g
        A = [w / 2, w / 2 - t, w / 2 - t - g, w / 2 - 2 * t - g, w / 2 - 2 * t - 2 * g, -w / 2]      # filets du côté positif
        B = [w / 2, w / 2 - coeur, w / 2 - coeur - g, w / 2 - coeur - g - t, w / 2 - coeur - 2 * g - t, -w / 2]
        k = (1 + monte) / 2
        e = [k * x + (1 - k) * y for x, y in zip(A, B)]
        m1, m2 = (e[1] + e[2]) / 2, (e[3] + e[4]) / 2
        c = chrome; r = RECOUVRE
        return [(m1 - r + (e[1] - m1 + r) * c, e[0]),
                (m2 - r + (e[3] - m2 + r) * c, m1 + r + (e[2] - m1 - r) * c),
                (e[5], m2 + r + (e[4] - m2 - r) * c)]

    def _trajet(self, k, cote, m, chrome):
        """Le bord n° cote (0 ou 1) de la bande k : départ, virages (4 points chacun), arrivée."""
        P = self.pts; n = len(P)
        segs = [(i, (i + 1) % n) for i in range(n if self.ferme else n - 1)]
        U = [_u(P[b] - P[a]) for a, b in segs]
        W = [self._ep(u, m, (P[a][0] + P[b][0]) / 2) for u, (a, b) in zip(U, segs)]
        dec = [self._bandes(w, m, chrome, u[1])[k][cote] for w, u in zip(W, U)]
        K = self.k
        # chaque bord va du décalage au départ du tronçon au décalage à son arrivée (un trait effilé n'a pas des bords parallèles)
        pa = [P[a] + _gauche(U[i]) * dec[i] * K[a] for i, (a, b) in enumerate(segs)]
        pb = [P[b] + _gauche(U[i]) * dec[i] * K[b] for i, (a, b) in enumerate(segs)]
        Ue = [_u(pb[i] - pa[i]) if math.hypot(*(pb[i] - pa[i])) > 1e-6 else U[i] for i in range(len(segs))]
        base = pa
        tension = self.tension if self.tension is not None else m['tension']
        L = [math.hypot(*(P[b] - P[a])) for a, b in segs]

        def virage(i_in, i_out, R):
            u1, u2 = Ue[i_in], Ue[i_out]
            a = math.atan2(u1[0] * u2[1] - u1[1] * u2[0], u1[0] * u2[0] + u1[1] * u2[1])    # > 0 : virage à gauche
            if abs(a) > 1e-4:                    # un virage ne mange jamais plus que la moitié de ses deux tronçons
                dispo = min(L[i_in] * (1.0 if (not self.ferme and i_in == 0) else 0.5),
                            L[i_out] * (1.0 if (not self.ferme and i_out == len(segs) - 1) else 0.5))
                R = min(R, dispo / math.tan(abs(a) / 2))
            X = _croise(pb[i_in], u1, pa[i_out], u2)
            if X is None or abs(a) < 1e-4:
                X = pa[i_out] if X is None else X
                return [X, X, X, X]
            s = 1 if a > 0 else -1
            kv = K[segs[i_out][0]]
            # un angle vif garde un chanfrein de 2 unités : jamais de courbe de longueur nulle (elle gêne certains logiciels)
            t1 = max(max(R - s * dec[i_in] * kv, 0) * math.tan(abs(a) / 2), MINI)
            t2 = max(max(R - s * dec[i_out] * kv, 0) * math.tan(abs(a) / 2), MINI)
            h = min(0.98, (4 / 3) * math.tan(abs(a) / 4) / math.tan(abs(a) / 2) * tension)
            A = X - u1 * t1; D = X + u2 * t2
            return [A, A + u1 * h * t1, D - u2 * h * t2, D]

        if self.ferme:
            return None, [virage((j - 1) % n, j, self.r[j]) for j in range(n)], None

        def bout(coupe, i, p):
            if coupe is None:
                q, d = p, _gauche(U[i])
            elif coupe == 'h':
                q, d = p, np.array([1.0, 0.0])
            elif coupe == 'v':
                q, d = p, np.array([0.0, 1.0])
            elif isinstance(coupe[0], str):          # ('contre', p0, p1, cote) : bute contre le bord d'un autre tronçon
                _, a0, a1, cote = coupe
                uu = _u(np.subtract(a1, a0))
                ww = self._ep(uu, m, (a0[0] + a1[0]) / 2)
                q, d = np.asarray(a0, float) + _gauche(uu) * cote * (ww / 2 - 2), uu
            else:
                q, d = np.asarray(coupe[0], float), np.asarray(coupe[1], float)
            x = _croise(pa[i], Ue[i], q, d)
            return x if x is not None else pa[i]

        vir = [virage(j - 1, j, self.r[j - 1]) for j in range(1, n - 1)]
        return bout(self.debut, 0, P[0]), vir, bout(self.fin, len(segs) - 1, P[-1])

    def contours(self, m, chrome=0.0):
        """Les contours du tuyau : une liste de contours, chacun une liste de ('l', p) et ('c', p1, p2, p3).
        Le premier élément est toujours ('l', départ)."""
        out = []
        nb = 1
        for k in range(nb):
            if self.ferme:
                boucles = []
                for cote in ((1,) if self.disque else (1, 0)):
                    _, vir, _ = self._trajet(k, cote, m, chrome)
                    c = []
                    for A, B, C, D in vir:
                        c.append(('l', A)); c.append(('c', B, C, D))
                    boucles.append(c if cote == 1 else _renverse(c))
                out.extend(boucles)
            else:
                d1, v1, f1 = self._trajet(k, 1, m, chrome)
                d0, v0, f0 = self._trajet(k, 0, m, chrome)
                c = [('l', d1)]
                for A, B, C, D in v1:
                    c.append(('l', A)); c.append(('c', B, C, D))
                c.append(('l', f1)); c.append(('l', f0))
                for A, B, C, D in reversed(v0):
                    c.append(('l', D)); c.append(('c', C, B, A))
                c.append(('l', d0))
                out.append(c)
        return out


def _renverse(c):
    """Le même contour fermé, parcouru dans l'autre sens (même nombre de points)."""
    pts = []          # la suite des points de passage, avec le type du tronçon qui y mène
    for s in c:
        pts.append(s)
    # points d'arrivée de chaque tronçon ; le contour est fermé : le dernier point rejoint le premier
    fin = [s[-1] for s in pts]
    out = [('l', fin[-1])]
    for i in range(len(pts) - 1, 0, -1):
        s = pts[i]
        if s[0] == 'l':
            out.append(('l', fin[i - 1]))
        else:
            out.append(('c', s[2], s[1], fin[i - 1]))
    return out


def penche(contours, pente, y0):
    """Penche les contours (pente = tangente de l'angle) autour de la hauteur y0."""
    if not pente:
        return contours
    f = lambda p: np.array([p[0] + pente * (p[1] - y0), p[1]])
    return [[(s[0],) + tuple(f(p) for p in s[1:]) for s in c] for c in contours]


def aire(c):
    """L'aire signée d'un contour (sur ses points de passage et de contrôle : le signe suffit)."""
    pts = [p for s in c for p in s[1:]]
    a = 0.0
    for i in range(len(pts)):
        x0, y0 = pts[i]; x1, y1 = pts[(i + 1) % len(pts)]
        a += x0 * y1 - x1 * y0
    return a / 2


def aplatis(c, pas=10):
    """Le contour en polygone (pour les images et les mesures)."""
    out = []; cur = None
    for s in c:
        if s[0] == 'l':
            out.append(tuple(s[1])); cur = s[1]
        else:
            p0, p1, p2, p3 = cur, s[1], s[2], s[3]
            for i in range(1, pas + 1):
                t = i / pas
                out.append(tuple((1 - t) ** 3 * p0 + 3 * t * (1 - t) ** 2 * p1 + 3 * t * t * (1 - t) * p2 + t ** 3 * p3))
            cur = s[3]
    return out
