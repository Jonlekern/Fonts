# Le crénage de Sibard, calculé sur le corps des lettres (sans les signatures, qui passent chez la voisine).
# On mesure le blanc entre deux lettres bande par bande ; on ne crénne que les paires où une lettre est
# ouverte (diagonales, bras, ponctuation) et on écarte toute paire qui se touche.
import unicodedata
import numpy as np
from functools import lru_cache
from formes import coupe
from glyphes import corps as tous, tous as entiers, nom, CAPS_ACC, ESSAI_MIN, PLUS_MIN, CAPS_TOUTES
from accents import ACCENTUEES
from mesures import mesures

BANDES = np.arange(-260, 960, 10)
OUVERTES = set('AFJKLPRTVWXYZfkrtvwxyz.,:;-–—\'"‘’“”‚„«»‹›/') | set('ÆŁĽ')
MIN_BLANC = 44          # deux lettres ne s'approchent jamais plus près
CHIFFRES_NOMS = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']


@lru_cache(None)
def profil(poids, g):
    """Pour chaque bande : bord gauche et bord droit de l'encre (nan si vide)."""
    p, ch, _ = tous(poids)[g]
    gch = np.full(len(BANDES), np.nan); dr = np.full(len(BANDES), np.nan)
    if list(p.contours):
        x0, y0, x1, y1 = p.bounds
        for i, y in enumerate(BANDES):
            if y + 10 < y0 or y > y1:
                continue
            b = coupe(p, -5000, y, 5000, y + 10)
            cs = list(b.contours)
            if cs:
                gch[i] = min(c.bounds[0] for c in cs); dr[i] = max(c.bounds[2] for c in cs)
    return gch, dr, ch


FENETRE = 12          # bandes de 10 u : on regarde l'encre 120 u au-dessus et au-dessous (le bras du T « voit » le o)


def _etale(v, f, plus_grand):
    out = np.full(len(v), np.nan)
    for i in range(len(v)):
        w = v[max(0, i - f): i + f + 1]
        if not np.isnan(w).all():
            out[i] = np.nanmax(w) if plus_grand else np.nanmin(w)
    return out


@lru_cache(None)
def profil_etale(poids, g):
    gch, dr, ch = profil(poids, g)
    return _etale(gch, FENETRE, False), _etale(dr, FENETRE, True), ch


def blancs(poids, a, b, etale=False):
    if etale:
        _, da, cha = profil_etale(poids, a); gb, _, _ = profil_etale(poids, b)
        # on ne garde que les bandes où les deux lettres ont vraiment de l'encre, à la fenêtre près
        _, da0, _ = profil(poids, a); gb0, _, _ = profil(poids, b)
        m = (~np.isnan(_etale(da0, FENETRE, True))) & (~np.isnan(_etale(gb0, FENETRE, False)))
        bl = (cha - da) + gb
        bl[~m] = np.nan
        return bl
    ga, da, cha = profil(poids, a)
    gb, db, _ = profil(poids, b)
    return (cha - da) + gb


@lru_cache(None)
def _entiers(poids):
    return entiers(poids)


@lru_cache(None)
def profil_entier(poids, g):
    """Le bord gauche et le bord droit de la lettre entière, signatures comprises."""
    p, ch, _ = _entiers(poids)[g]
    gch = np.full(len(BANDES), np.nan); dr = np.full(len(BANDES), np.nan)
    if list(p.contours):
        x0, y0, x1, y1 = p.bounds
        for i, y in enumerate(BANDES):
            if y + 10 < y0 or y > y1:
                continue
            cs = list(coupe(p, -5000, y, 5000, y + 10).contours)
            if cs:
                gch[i] = min(c.bounds[0] for c in cs); dr[i] = max(c.bounds[2] for c in cs)
    return gch, dr, ch


def garde(poids, a, b, k):
    """Les signatures passent chez la voisine dans les maigres (un cheveu croise un cheveu).
    Plus la lettre est grasse, moins elles ont le droit d'entrer : à 900 elles ne touchent plus rien."""
    _, da, cha = profil_entier(poids, a); gb, _, _ = profil_entier(poids, b)
    bl = (cha - da) + gb
    if np.isnan(bl).all():
        return k
    besoin = -200 + min(1.0, max(0.0, (poids - 400) / 500)) * 280
    return max(k, besoin - float(np.nanmin(bl)))


def zone(poids, a, b):
    """Les bandes qui comptent : la hauteur d'x si une minuscule est en jeu, sinon la hauteur des capitales."""
    m = mesures(poids)
    ca, cb = caractere(a), caractere(b)
    mins = [c for c in (ca, cb) if c and c.isalpha() and c.islower()]
    haut = m['x'] if mins else m['cap']
    return (BANDES >= 0) & (BANDES + 10 <= haut)


def vu(poids, a, b, ref):
    """Le blanc moyen entre deux lettres dans leur zone, chaque bande bornée à 2,5 fois le blanc de référence."""
    bl = blancs(poids, a, b)[zone(poids, a, b)]
    bl = bl[~np.isnan(bl)]
    if not len(bl):
        return None
    return float(np.mean(np.minimum(bl, 2.0 * ref)))


@lru_cache(None)
def reference(poids):
    """Le blanc « vu » de référence : entre deux n (minuscules) et entre deux H (capitales)."""
    rn = float(np.nanmin(blancs(poids, 'n', 'n')))
    rh = float(np.nanmin(blancs(poids, 'H', 'H')))
    return vu(poids, 'n', 'n', rn), vu(poids, 'H', 'H', rh), rn


def valeur(poids, a, b, ref=None):
    """Le crénage de la paire (a, b), en unités, arrondi à 5."""
    rn_vu, rh_vu, rn = reference(poids)
    z = zone(poids, a, b)
    cible = rn_vu if z.sum() * 10 <= mesures(poids)['x'] + 10 else rh_vu
    v = vu(poids, a, b, rn)
    vrai = blancs(poids, a, b)
    mn0 = np.nanmin(vrai) if not np.isnan(vrai).all() else 999
    k = 0
    if v is not None:
        k = min(0, round((cible - v) * 0.65))
        k = max(k, -round(0.85 * rn))
        # après crénage, le point le plus proche garde au moins la moitié du blanc entre deux n
        k = max(k, min(0, round(0.55 * rn - mn0)))
    if mn0 + k < MIN_BLANC:                       # jamais collé
        k = MIN_BLANC - mn0
    k = garde(poids, a, b, k)
    return int(round(k / 5) * 5)


def a_ouverte(g):
    c = caractere(g)
    return c is not None and (c in OUVERTES or base(c) in OUVERTES)


@lru_cache(None)
def caractere(g):
    for n, (_, _, code) in tous(500).items():
        if n == g and code:
            return chr(code)
    return None


def base(c):
    return unicodedata.normalize('NFD', c)[0]


def familles(poids):
    """Les familles de crénage : la lettre de base et ses accents. ď ľ ť gardent leur côté droit à part."""
    g = tous(poids)
    gauche, droite = {}, {}          # nom de famille -> glyphes (gauche = côté droit de la 1re lettre)
    def ajoute(d, fam, n):
        d.setdefault(fam, []).append(n)
    reps = []
    for c in ESSAI_MIN + PLUS_MIN + CAPS_TOUTES + '.,:;-–—\'"‘’“”‚„«»‹›!?¡¿()[]{}/&@*' :
        n = nom(c)
        if n in g:
            reps.append(n)
    for n in CHIFFRES_NOMS:
        reps.append(n)
    for r in reps:
        ajoute(gauche, r, r); ajoute(droite, r, r)
    for c in ACCENTUEES:
        n = nom(c); b = nom(base(c)) if base(c) not in 'ıȷ' else nom(base(c))
        b = nom(base(c))
        if b not in gauche:
            continue
        ajoute(droite, b, n)
        if c in 'ďľĽť':
            ajoute(gauche, n, n)
        else:
            ajoute(gauche, b, n)
    return gauche, droite


# Les paires qu'on crénne : les classiques d'une police de texte (le reste est réglé par l'espacement).
_DIAG = 'TVWYAFPKLR'
PAIRES = []
def _p(g, d):
    for a in g:
        for b in d:
            PAIRES.append((a, b))
_p('LA', 'TVWY')
_p('TVWY', 'A')
_p('FP', 'A')
_p('TVWYFP', 'acdegmnopqrsuvwxyz')
_p('TVWYFPL', '.,')
_p('TVWY', ':;-«»')
_p('K', 'oeacuy')
_p('L', 'yvw’”\'"')
_p('A', 'yvwtTVWY’”\'"')
_p('‘“\'"', 'A')
_p('’”', 'sA')
_p('rvwyf', '.,')
_p('«‹', 'TVWYA')
_p('TVWYA', '»›')
_p('ROD', 'TVWYA')
_p('TVWY', 'OCGQ')
_p('RKX', 'oeyv')
_p('f', '’”\'"')
PAIRES = sorted(set(PAIRES))


def table(poids):
    """Le crénage par familles : {(famille gauche, famille droite): valeur}."""
    gauche, droite = familles(poids)
    out = {}
    voulues = set()
    for a, b in PAIRES:
        na, nb = nom(a), nom(b)
        voulues.add((na, nb))
    for a in gauche:
        for b in droite:
            if (a, b) in voulues:
                v = valeur(poids, a, b)
            else:                      # ailleurs, on ne touche que si deux lettres se touchent
                vrai = blancs(poids, a, b)
                if np.isnan(vrai).all():
                    continue
                mn = np.nanmin(vrai)
                v = int(round((MIN_BLANC - mn) / 5 + 0.5) * 5) if mn < MIN_BLANC else 0
                v = int(round(garde(poids, a, b, v) / 5) * 5)
            if (abs(v) >= 10 or v > 0) and a not in CHIFFRES_NOMS and b not in CHIFFRES_NOMS:     # les chiffres gardent leur chasse fixe
                out[(a, b)] = v
    return out, gauche, droite


def fea(poids):
    """Le code OpenType (feaLib) du crénage."""
    t, gauche, droite = table(poids)
    lignes = []
    cl = lambda pre, fam: f'@{pre}_' + fam.replace('.', '_')
    for fam, gl in gauche.items():
        lignes.append(f"{cl('kG', fam)} = [{' '.join(gl)}];")
    for fam, gl in droite.items():
        lignes.append(f"{cl('kD', fam)} = [{' '.join(gl)}];")
    lignes.append('feature kern {')
    for (a, b), v in sorted(t.items()):
        lignes.append(f"  pos {cl('kG', a)} {cl('kD', b)} {v};")
    lignes.append('} kern;')
    return '\n'.join(lignes), len(t)
