# Shrikhard : Shrikhand (Jonny Pinhorn, OFL) en latin seulement, élargie sans être déformée.
# On redresse la lettre, on l'étire, puis on rend à chaque trait son épaisseur d'origine
# en déplaçant les points existants : toutes les versions gardent les mêmes points (police variable).
import math
import numpy as np
import pathops
from fontTools.ttLib import TTFont
from fontTools.subset import Subsetter, Options
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.reverseContourPen import ReverseContourPen
from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates

PENTE = 14.0                      # l'italique d'origine
TAN = math.tan(math.radians(PENTE))
Y0 = 260                          # on penche autour de la mi-hauteur d'x
LARGEUR = 1.29
EPAISSEUR_MAX = 290               # au-delà, le rayon traverse la longueur d'un trait, pas son épaisseur


def latin(chemin):
    """La police d'origine, sans le gujarati."""
    f = TTFont(chemin)
    garde = [c for c in f.getBestCmap() if not (0x0900 <= c <= 0x0DFF or 0xA830 <= c <= 0xA83F)
             and c not in (0xFB01, 0xFB02, 0x200C, 0x200D, 0x25CC)]     # fi et fl restent des ligatures (liga), sans code à eux
    o = Options(); o.layout_features = ['*']; o.layout_scripts = ['DFLT', 'latn']
    o.name_IDs = ['*']; o.notdef_outline = True; o.glyph_names = True; o.hinting = False
    o.drop_tables += ['DSIG']
    s = Subsetter(o); s.populate(unicodes=garde); s.subset(f)
    return f


def redresse(f):
    """Chaque glyphe décomposé, sans chevauchement, redressé de 14° : la base de toutes les versions."""
    gs = f.getGlyphSet()
    base = {}
    for n in f.getGlyphOrder():
        rec = DecomposingRecordingPen(gs); gs[n].draw(rec)
        p = pathops.Path(); pen = p.getPen()
        rec.replay(TransformPen(pen, (1, 0, -TAN, 1, TAN * Y0, 0)))
        try:
            p.simplify(fix_winding=True, keep_starting_points=True)
        except pathops.PathOpsError:
            pass
        tt = TTGlyphPen(None); p.draw(ReverseContourPen(tt))   # pathops sort à l'envers de TrueType
        g = tt.glyph()
        if g.numberOfContours > 0:
            coords = np.array(g.coordinates, float)
            ends = list(g.endPtsOfContours)
            on = np.array([fl & 1 for fl in g.flags], bool)
        else:
            coords, ends, on = np.zeros((0, 2)), [], np.zeros(0, bool)
        base[n] = (coords, ends, on, g)
    return base


def _contours(coords, ends):
    d = 0
    for e in ends:
        yield d, e + 1
        d = e + 1


def _echantillons(coords, ends, on, pas=8):
    """Le contour aplati en petits segments (pour lancer des rayons)."""
    segs = []
    for a, b in _contours(coords, ends):
        pts, ons = coords[a:b], on[a:b]
        k = len(pts)
        # on-curve explicites et implicites
        seq = []
        for i in range(k):
            seq.append((pts[i], ons[i]))
            if not ons[i] and not ons[(i + 1) % k]:
                seq.append(((pts[i] + pts[(i + 1) % k]) / 2, True))
        i0 = next(i for i, (_, o) in enumerate(seq) if o)
        seq = seq[i0:] + seq[:i0]
        poly = []
        m = len(seq)
        i = 0
        while i < m:
            p0 = seq[i][0]; q, qo = seq[(i + 1) % m]
            if qo:
                poly.append(p0); i += 1
            else:
                p2 = seq[(i + 2) % m][0]
                for t in np.linspace(0, 1, pas, endpoint=False):
                    poly.append((1 - t) ** 2 * p0 + 2 * t * (1 - t) * q + t * t * p2)
                i += 2
        poly = np.array(poly)
        segs.append(np.stack([poly, np.roll(poly, -1, axis=0)], axis=1))
    return np.concatenate(segs) if segs else np.zeros((0, 2, 2))


def _rayon(o, d, segs):
    A = segs[:, 0]; B = segs[:, 1]; E = B - A
    den = d[0] * E[:, 1] - d[1] * E[:, 0]
    ok = np.abs(den) > 1e-9
    w = A - o
    s = np.where(ok, (w[:, 0] * E[:, 1] - w[:, 1] * E[:, 0]) / np.where(ok, den, 1), np.inf)
    u = np.where(ok, (w[:, 0] * d[1] - w[:, 1] * d[0]) / np.where(ok, den, 1), -1)
    m = ok & (s > 1.0) & (u >= 0) & (u <= 1)
    return float(s[m].min()) if m.any() else np.inf


def _normale(v):
    """Normale extérieure d'un bord parcouru dans le sens des aiguilles (contour extérieur TrueType)."""
    n = np.array([-v[1], v[0]], float)
    l = np.hypot(*n)
    return n / l if l > 1e-9 else None


ANGLES = [math.radians(a) for a in (-60, -30, 0, 30, 60)]
LONG = 300           # plus long qu'un fût (251–267) : le rayon est parti dans la longueur


def _tourne(v, t):
    c, s_ = math.cos(t), math.sin(t)
    return np.array([c * v[0] - s_ * v[1], s_ * v[0] + c * v[1]])


def mesures(coords, ends, on, g=None):
    """Pour chaque point : normale des bords entrant/sortant et épaisseur du trait (rayon vers l'intérieur)."""
    segs = _echantillons(coords, ends, on)
    N = len(coords)
    nin = np.zeros((N, 2)); nout = np.zeros((N, 2)); ep = np.zeros(N)
    for a, b in _contours(coords, ends):
        k = b - a
        for j in range(k):
            i = a + j
            p = coords[i]
            prev = coords[a + (j - 1) % k]; nxt = coords[a + (j + 1) % k]
            n1 = _normale(p - prev); n2 = _normale(nxt - p)
            if n1 is None: n1 = n2
            if n2 is None: n2 = n1
            if n1 is None: n1 = n2 = np.array([0.0, 1.0])
            nin[i], nout[i] = n1, n2
            nm = n1 + n2
            nm = nm / np.hypot(*nm) if np.hypot(*nm) > 1e-6 else n1
            # l'épaisseur : le rayon droit vers l'intérieur. S'il est trop long, il file dans la longueur d'un trait
            # (bout d'empattement, terminaison) : on prend alors le plus court des rayons en éventail
            r0 = _rayon(p, -nm, segs)
            if r0 <= LONG - 60:
                ep[i] = r0
            else:                                   # passage en douceur, pas de cassure
                w = min(1.0, (r0 - (LONG - 60)) / 120)
                ev = min(_rayon(p, _tourne(-nm, t), segs) * math.cos(t) for t in ANGLES)
                ep[i] = (1 - w) * min(r0, LONG) + w * ev
        # un point hors courbe est hors de l'encre : son rayon ne mesure rien, il prend l'épaisseur de ses voisins sur la courbe
        sur = [j for j in range(k) if on[a + j]]
        if sur:
            for j in range(k):
                if not on[a + j]:
                    av = max(x for x in sur if x < j) if any(x < j for x in sur) else sur[-1] - k
                    ap = min(x for x in sur if x > j) if any(x > j for x in sur) else sur[0] + k
                    ep[a + j] = (ep[a + av % k] * (ap - j) + ep[a + ap % k] * (j - av)) / (ap - av)
        # on lisse l'épaisseur le long du contour, et on la borne
        e = np.minimum(ep[a:b], EPAISSEUR_MAX)
        ep[a:b] = (np.roll(e, 1) + 2 * e + np.roll(e, -1)) / 4
    return nin, nout, ep


def _lisse(e, k):
    """Médiane glissante le long d'un contour fermé (les rayons qui partent dans une jonction sont écartés)."""
    n = len(e)
    if n < 3:
        return e
    idx = (np.arange(n)[:, None] + np.arange(-k, k + 1)[None, :]) % n
    return np.median(e[idx], axis=1)


def epaisseurs(base_glyphe, mes):
    """Épaisseur retenue en chaque point : médiane sur le contour (on ne la borne qu'au moment de l'utiliser)."""
    coords, ends = base_glyphe[0], base_glyphe[1]
    ep = mes[2].copy()
    for a, b in _contours(coords, ends):
        ep[a:b] = _lisse(ep[a:b], 2)
    return ep


# Bornes de l'épaisseur selon le sens : fûts (côtés gauche/droit) et traits horizontaux (haut/bas)
FUT = (30, 270)
TRAIT = (20, 170)


def version(base_glyphe, mes, sx, sy, force_x=1.0, force_y=1.0):
    """Le glyphe étiré (sx, sy). Les points glissent seulement à l'horizontale pour rendre aux fûts leur
    épaisseur, et seulement à la verticale pour les traits horizontaux (force = part de l'épaisseur rendue)."""
    coords, ends, on = base_glyphe[:3]
    if not len(coords):
        return coords
    nin, nout, _ = mes
    ep = epaisseurs(base_glyphe, mes)
    out = coords * np.array([sx, sy])
    dep = np.zeros_like(out)
    sur = np.ones_like(out)                      # la confiance du déplacement (1 : bord bien orienté)
    for i in range(len(coords)):
        dx_num = dx_den = dy_num = dy_den = 0.0
        for n in (nin[i], nout[i]):
            m = np.array([n[0] / sx, n[1] / sy]); lm = np.hypot(*m); mu = m / lm
            # épaisseur gagnée par l'étirement, séparée en part horizontale et part verticale
            tx = np.clip(ep[i], *FUT); ty = np.clip(ep[i], *TRAIT)
            fin = np.clip((ep[i] - 40) / 120, 0, 1)        # les petits détails (boutons, pointes) s'étirent sans être creusés
            gx = tx * (1 / math.hypot(n[0] / sx, n[1]) - 1) / 2      # la largeur seule
            gy = ty * (1 / math.hypot(n[0], n[1] / sy) - 1) / 2      # la hauteur seule
            dx_num += -gx * fin * force_x * mu[0]; dx_den += mu[0] ** 2
            dy_num += -gy * force_y * mu[1]; dy_den += mu[1] ** 2
        if dx_den > 1e-6:
            dep[i, 0] = dx_num / dx_den
        if dy_den > 1e-6:
            dep[i, 1] = dy_num / dy_den
        sur[i] = (min(1.0, dx_den), min(1.0, dy_den))
    # sur un bord presque horizontal, glisser à l'horizontale ne change rien à la forme : ces points
    # suivent leurs voisins (le fond d'un creux suit le fût qui le borde, au lieu de rester sur place)
    for a, b in _contours(coords, ends):
        k = b - a
        if k < 3:
            continue
        propre = dep[a:b].copy(); w = sur[a:b].copy(); d = propre.copy()
        # les creux (le contour tourne vers l'intérieur : jonction fût-courbe) suivent aussi leurs voisins
        pts = coords[a:b]
        u = pts - np.roll(pts, 1, axis=0); v = np.roll(pts, -1, axis=0) - pts
        tour = u[:, 0] * v[:, 1] - u[:, 1] * v[:, 0]          # > 0 : virage à gauche, un creux (contour horaire)
        creux = tour > 0.05 * np.hypot(u[:, 0], u[:, 1]) * np.hypot(v[:, 0], v[:, 1])
        w[creux] *= 0.2
        for _ in range(30):
            voisins = (np.roll(d, 1, axis=0) + np.roll(d, -1, axis=0)) / 2
            d = w * propre + (1 - w) * voisins
        dep[a:b] = d
    # les pointes (le contour fait demi-tour) suivent leurs voisins, sinon il reste une aiguille
    for a, b in _contours(coords, ends):
        k = b - a
        for j in range(k):
            i = a + j
            p, q, r = coords[a + (j - 1) % k], coords[i], coords[a + (j + 1) % k]
            u, v = q - p, r - q
            lu, lv = np.hypot(*u), np.hypot(*v)
            if lu > 1e-6 and lv > 1e-6 and np.dot(u, v) / (lu * lv) < -0.3:
                dep[i] = (dep[a + (j - 1) % k] + dep[a + (j + 1) % k]) / 2
    # les petits détails (boutons, crochets) ne doivent pas se retourner : là où un bout de contour
    # change de sens ou s'écrase par rapport à l'étirement simple, on y retient les déplacements
    for a, b in _contours(coords, ends):
        k = b - a
        for _ in range(12):
            nb = out[a:b]; nd = nb + dep[a:b]
            eb = np.roll(nb, -1, axis=0) - nb; en = np.roll(nd, -1, axis=0) - nd
            lb = (eb ** 2).sum(axis=1)
            mal = (lb > 1) & ((eb * en).sum(axis=1) < 0.35 * lb)
            if not mal.any():
                break
            for j in np.nonzero(mal)[0]:
                dep[a + j] *= 0.5; dep[a + (j + 1) % k] *= 0.5
    return out + dep


def penche(coords, pente=True):
    if not pente or not len(coords):
        return coords
    c = coords.copy(); c[:, 0] = c[:, 0] + TAN * (c[:, 1] - Y0)
    return c


TRAIT_FINAL = 120      # au bout du curseur, chaque lettre n'est plus qu'un trait de l'épaisseur du _


def trait(base_glyphe, avance, voisin=None, place=(0.0, 1.0)):
    """La lettre écrasée jusqu'au bout : un trait de l'épaisseur du _ qui remplit toute sa chasse.
    On aplatit sans rien croiser (aucun contour ne se retourne) ; les contreformes se referment."""
    coords, ends, on = base_glyphe[:3]
    if not len(coords):
        return coords
    out = coords.copy()
    x0, x1 = coords[:, 0].min(), coords[:, 0].max()
    y0, y1 = coords[:, 1].min(), coords[:, 1].max()
    lo, hi = place          # la part de la chasse que le trait occupe (le caron d'un ď reste à droite)
    out[:, 0] = (lo + (coords[:, 0] - x0) / max(x1 - x0, 1) * (hi - lo)) * avance
    out[:, 1] = (coords[:, 1] - y0) / max(y1 - y0, 1) * TRAIT_FINAL
    for a, b in _contours(coords, ends):
        p = coords[a:b]
        aire = 0.5 * np.sum(p[:, 0] * np.roll(p[:, 1], -1) - np.roll(p[:, 0], -1) * p[:, 1])
        if aire > 0:            # contreforme : elle se referme presque entièrement sur son centre
            m = out[a:b].mean(axis=0)
            ref = voisin if voisin is not None else coords          # le dessin de la version voisine, en tout petit
            out[a:b] = m + (ref[a:b] - ref[a:b].mean(axis=0)) * np.array([0.08, 0.0])   # à plat : rien ne se voit
    return out
