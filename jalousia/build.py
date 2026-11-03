# Fabrique Jalousia Craie et Jalousia Net (TTF + WOFF2), capitales et minuscules, jeu GF Latin Core.
#   python3 build.py <dossier_sortie> [net|craie]
# Les lettres accentuées sont des composites (lettre + accent).
import sys, os, json, zlib, unicodedata
import numpy as np
import pathops
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.areaPen import AreaPen
from fontTools.pens.reverseContourPen import ReverseContourPen
from fontTools.pens.roundingPen import RoundingPen
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.ttLib import TTFont
from fontTools.agl import UV2AGL
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import essai, signes, minuscules

FAMILLE = 'Jalousia'
VERSION = 1.0
SC = 0.7                      # unités de dessin (capitales à 1000) -> unités de police (capitales à 700)
R, GAP, BAND = essai.R, essai.GAP, essai.BAND
XH = minuscules.XH
ASC, DESC = 950, -300
ESPACE_MOT = 300
CHEVAUCHE = 120               # deux lettres peuvent se glisser l'une sous l'autre de 120 au plus
BARRES_COLLEES = {'V', 'W', 'v', 'w'}    # leurs barres peuvent toucher la lettre d'à côté

def gname(cp):
    if cp == 0x20: return 'space'
    return UV2AGL.get(cp, 'uni%04X' % cp)

# ---------------------------------------------------------------- jeu de caractères
CORE = json.load(open(os.path.join(HERE, 'gf_core.json')))
D = {}                        # nom -> traits (unités de dessin), glyphes simples avec chasse
for ch, sts in list(essai.G.items()) + list(signes.S.items()) + list(minuscules.m.items()):
    D[gname(ord(ch))] = sts
D['Dcroat'] = signes.S['Đ']; D.pop('Eth', None)
for ch, sts in signes.CASSE.items(): D[gname(ord(ch)) + '.case'] = sts
MATH = ['plus', 'minus', 'equal', 'multiply', 'divide', 'less', 'greater']   # même chasse
MARQ = {}                     # nom -> traits, accents sans chasse (posés autour de x = 0)
NOM_MARQUE = {}
for cp, m in signes.COMB.items():
    MARQ[gname(cp)] = signes.M[m]; NOM_MARQUE[m] = gname(cp)
for m, n in (('caron_virgule', 'caroncomb.alt'), ('virgule_haut', 'commaturnedabovecomb')):
    MARQ[n] = signes.M[m]; NOM_MARQUE[m] = n

def base_de(ch):
    """Glyphe d'un caractère sans accent."""
    special = {'Ð': 'Dcroat'}
    return special.get(ch, gname(ord(ch)))

COMPO = {}                    # nom -> (base, [marques])
for cp in CORE:
    ch = chr(cp)
    if 0x300 <= cp <= 0x36F: continue
    dec = unicodedata.normalize('NFD', ch)
    if len(dec) < 2 or not dec[0].isalpha(): continue
    marques = [signes.COMB[ord(c)] for c in dec[1:]]
    if ch in signes.VIRGULE_DESSOUS: marques = ['virgule' if m == 'cedille' else m for m in marques]
    if ch == 'ģ': marques = ['virgule_haut']
    if ch in 'ďľťĽ': marques = ['caron_virgule']
    base = base_de(dec[0])
    if base == 'i' and any(m not in signes.BAS for m in marques): base = 'dotlessi'
    COMPO[gname(cp)] = (base, marques)
COMPO['iogonek.dotless'] = ('dotlessi', ['ogonek'])          # lituanien : į sans point sous un accent
ACC = {gname(ord(c)): m for c, m in signes.ESPACE.items()}     # accents avec chasse

CMAP = {}
for cp in CORE:
    ch = chr(cp)
    if cp == 0x20: CMAP[cp] = 'space'
    elif 0x300 <= cp <= 0x36F: CMAP[cp] = gname(cp)
    elif gname(cp) in COMPO or gname(cp) in ACC: CMAP[cp] = gname(cp)
    else: CMAP[cp] = base_de(ch)
CMAP[0xA0] = 'space'
CMAP[0x25CC] = 'uni25CC'
manque = sorted({n for n in CMAP.values()} - set(D) - set(MARQ) - set(COMPO) - set(ACC) - {'space'})
assert not manque, manque

# ---------------------------------------------------------------- géométrie
def echant(st, pas):
    """Échantillons réguliers le long du trait (courbe de essai.cr)."""
    P = essai.cr(st)
    if len(P) < 2: return P
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]
    n = max(2, int(np.ceil(d[-1] / pas)) + 1)
    t = np.linspace(0, d[-1], n)
    return np.c_[np.interp(t, d, P[:, 0]), np.interp(t, d, P[:, 1])]

def normales(P):
    T = np.gradient(P, axis=0)
    T /= np.maximum(np.linalg.norm(T, axis=1)[:, None], 1e-9)
    return np.c_[-T[:, 1], T[:, 0]]

def poly(pen, pts):
    pts = np.asarray(pts, float)
    x, y = pts[:, 0], pts[:, 1]
    if np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y) < 0: pts = pts[::-1]   # tout dans le même sens
    pen.moveTo(tuple(pts[0]))
    for p in pts[1:]: pen.lineTo(tuple(p))
    pen.closePath()

def rond(c, r, n):
    a = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return np.c_[c[0] + r * np.cos(a), c[1] + r * np.sin(a)]

def capsules(pen, C, r, Nm):
    """Cercles aux échantillons + quadrilatères entre deux échantillons : le trait plein."""
    for i in range(len(C)):
        poly(pen, rond(C[i], r[i], 16 if r[i] > 10 else 10))
    for i in range(len(C) - 1):
        a, b = C[i], C[i + 1]
        poly(pen, [a + Nm[i] * r[i], b + Nm[i + 1] * r[i + 1], b - Nm[i + 1] * r[i + 1], a - Nm[i] * r[i]])

def bruit(rng, n, corr, pas):
    """Bruit lisse le long du trait : écart type 1, corrélé sur ~corr unités."""
    s = max(corr / pas, 0.5)
    k = np.exp(-0.5 * (np.arange(-int(4 * s) - 1, int(4 * s) + 2) / s) ** 2)
    v = np.convolve(rng.standard_normal(n + 2 * len(k)), k, mode='same')[len(k):len(k) + n]
    return v / (v.std() + 1e-9)

class Polys:
    """Collecte des polygones (pour pouvoir les secouer un peu si pathops bloque)."""
    def __init__(self): self.l = []
    def moveTo(self, p): self.cur = [p]
    def lineTo(self, p): self.cur.append(p)
    def closePath(self): self.l.append((np.array(self.cur, float), True))

def polys_de(path):
    rec = RecordingPen(); path.draw(rec); out = []; cur = []
    for op, args in rec.value:
        if op == 'moveTo': cur = [args[0]]
        elif op in ('lineTo',): cur.append(args[0])
        elif op in ('qCurveTo', 'curveTo'): cur.extend(args)
        elif op in ('closePath', 'endPath') and len(cur) >= 3: out.append((np.array(cur, float), False))
    return out

def union(polys, rng):
    """Union (règle non nulle) avec reprises : pathops échoue parfois sur des bords presque confondus."""
    for k in range(8):
        jit = 0.0 if k == 0 else 0.01 * k
        p = pathops.Path(); pen = p.getPen()
        for q, orienter in polys:
            q = q + rng.uniform(-jit, jit, q.shape) if jit else q
            if orienter: poly(pen, q)
            else:
                pen.moveTo(tuple(q[0])); [pen.lineTo(tuple(v)) for v in q[1:]]; pen.closePath()
        try:
            return pathops.simplify(p, fix_winding=True)
        except pathops.PathOpsError:
            pass
    raise RuntimeError('union impossible')

def union_par_paquets(polys, rng, paquet=120):
    while len(polys) > paquet:
        res = []
        for i in range(0, len(polys), paquet):
            res += polys_de(union(polys[i:i + paquet], rng))
        if len(res) >= len(polys): break
        polys = res
    return union(polys, rng)

def contour(sts, style, graine):
    rng = np.random.default_rng(graine)
    pleins = []; trous = Polys()
    for st in sts:
        pen = Polys()
        if style == 'net':
            P = echant(st, 5.0); Nm = normales(P)
            capsules(pen, P, np.full(len(P), float(R)), Nm)
            pleins += polys_de(union_par_paquets(pen.l, rng))
            continue
        pas = 2.5
        P = echant(st, pas); Nm = normales(P); n = len(P)
        r = R * (1 + 0.22 * bruit(rng, n, 5, pas) + 0.12 * bruit(rng, n, 25, pas))
        d = np.minimum(np.arange(n), np.arange(n)[::-1]) * pas
        r *= 0.82 + 0.18 * np.clip(d / 14.0, 0, 1)                        # bouts un peu plus fins
        r = np.clip(r, 0.55 * R, 1.45 * R)
        C = P + Nm * (0.2 * R * bruit(rng, n, 12, pas))[:, None]
        capsules(pen, C, r, Nm)
        L = n * pas
        for _ in range(rng.poisson(L / 22)):                              # trous dans le trait
            i = rng.integers(n); c = C[i] + Nm[i] * rng.uniform(-0.6, 0.6) * r[i]
            poly(trous, rond(c, rng.uniform(2.5, 5.0), 8))
        for _ in range(rng.poisson(L / 40)):                              # poussière autour
            i = rng.integers(n); c = C[i] + Nm[i] * rng.choice([-1, 1]) * (r[i] + rng.uniform(2, 10))
            poly(pen, rond(c, rng.uniform(2.5, 4.5), 8))
        pleins += polys_de(union_par_paquets(pen.l, rng))
    plein = union(pleins, rng)
    if style == 'craie' and trous.l:
        t = union(trous.l, rng)
        for k in range(8):
            try:
                return pathops.op(plein, t, pathops.PathOp.DIFFERENCE, fix_winding=True)
            except pathops.PathOpsError:
                plein = union([(q + rng.uniform(-0.02, 0.02, q.shape), o) for q, o in polys_de(plein)], rng)
        raise RuntimeError('trous impossibles')
    return plein

def dp(pts, tol):
    """Douglas-Peucker sur un contour fermé."""
    pts = np.asarray(pts, float)
    if len(pts) < 5: return pts
    i0 = 0; i1 = int(np.argmax(np.linalg.norm(pts - pts[0], axis=1)))
    def rec(a):
        if len(a) < 3: return a
        p, q = a[0], a[-1]; v = q - p; L = np.linalg.norm(v)
        w = a - p
        dist = np.abs(v[0] * w[:, 1] - v[1] * w[:, 0]) / L if L > 1e-9 else np.linalg.norm(w, axis=1)
        k = int(np.argmax(dist))
        if dist[k] <= tol: return np.vstack([p, q])
        return np.vstack([rec(a[:k + 1])[:-1], rec(a[k:])])
    a = rec(pts[i0:i1 + 1]); b = rec(np.vstack([pts[i1:], pts[:1]]))
    return np.vstack([a[:-1], b[:-1]])

def polys_rec(path):
    rec = RecordingPen(); path.draw(rec); return rec.value

def vers_glyphe(path, f, tol):
    """Path (unités de dessin) -> glyphe TrueType, avec f(x, y) -> (x, y) en unités de police."""
    rec = RecordingPen(); path.draw(rec)
    out = pathops.Path(); pen = out.getPen()
    cont = []
    for op, args in rec.value:
        if op == 'moveTo': cont = [args[0]]
        elif op == 'lineTo': cont.append(args[0])
        elif op in ('qCurveTo', 'curveTo'): cont.extend(args)
        elif op in ('closePath', 'endPath') and len(cont) >= 3:
            q = dp(cont, tol)
            if len(q) >= 3:
                pen.moveTo(f(*q[0]))
                for p in q[1:]: pen.lineTo(f(*p))
                pen.closePath()
            cont = []
    out = pathops.simplify(out, fix_winding=True)
    for _ in range(3):                         # arrondir aux unités entières sans laisser de bords en double
        rp = pathops.Path(); out.draw(RoundingPen(rp.getPen()))
        out = pathops.simplify(rp, fix_winding=True)
        if all(float(v).is_integer() for op, args in polys_rec(out) for p in args for v in p): break
    fin = pathops.Path(); fpen = fin.getPen()
    for c in out.contours:
        a = AreaPen(); c.draw(a)
        if abs(a.value) >= 3: c.draw(fpen)
    a = AreaPen(); fin.draw(a)
    g = TTGlyphPen(None)
    fin.draw(ReverseContourPen(g) if a.value > 0 else g)
    return g.glyph()

# ---------------------------------------------------------------- mesures (unités de dessin)
def points(sts):
    return np.vstack([essai.cr(s) for s in sts])

def boite(sts):
    P = points(sts)
    return P[:, 0].min() - R, P[:, 0].max() + R

def placement(b, m):
    """Où poser l'accent m sur la lettre b : (x, décalage vertical), en unités de dessin."""
    sts = D[b]; lo, hi = boite(sts); P = points(sts)
    if m == 'caron_virgule':                      # ď ľ ť : virgule à droite du haut du fût
        xt, yt = P[np.argmax(P[:, 1])]
        if b == 'L': return xt + 60, 1190 - 1000       # Ľ : au-dessus de la barre du haut
        return xt + 80, yt - 20 - 1000
    if m == 'ogonek':
        bas = P[P[:, 1] < 80]
        return ((bas[:, 0].max() - 30) if len(bas) else hi - R - 30), 0
    if m in signes.BAS:
        return (lo + hi) / 2, 0
    dy = 0 if P[:, 1].max() > 800 else -(1000 - XH)   # minuscules sans hampe : accent à hauteur d'x
    return (lo + hi) / 2, dy

def genre(m):
    return 'ogonek' if m == 'ogonek' else ('bas' if m in signes.BAS else 'haut')

def est_barre(s):
    P = essai.cr(s); w = np.ptp(P[:, 0]); h = np.ptp(P[:, 1])
    return w > 80 and h < 0.2 * w

def traits_complets(nom):
    """Traits d'un glyphe avec chasse, accents compris, avec pour chacun : est-ce une barre qui peut toucher ?"""
    if nom in ACC: return [(s, False) for s in signes.M[ACC[nom]]]
    if nom in D: b, extra = nom, []
    else:
        b, ms = COMPO[nom]; extra = []
        for m in ms:
            x, dy = placement(b, m); extra += signes.mv(signes.M[m], x, dy)
    colle = b in BARRES_COLLEES
    return [(s, colle and est_barre(s)) for s in D[b]] + [(s, False) for s in extra]

# ---------------------------------------------------------------- crénage
BMIN, BMAX = -20, 75
def profil(traits):
    sts = [s for s, _ in traits]; lo, hi = boite(sts)
    nb = BMAX - BMIN
    g = {False: np.full(nb, np.inf), True: np.full(nb, np.inf)}
    d = {False: np.full(nb, np.inf), True: np.full(nb, np.inf)}
    for s, barre in traits:
        for x, y in essai.cr(s):
            b = int(np.floor(y / BAND))
            for bb in range(b - 2, b + 3):                         # ±2 bandes : un peu d'air au-dessus et au-dessous
                i = bb - BMIN
                if 0 <= i < nb:
                    g[barre][i] = min(g[barre][i], (x - R) - lo)     # marge à gauche dans la bande
                    d[barre][i] = min(d[barre][i], hi - (x + R))     # marge à droite dans la bande
    return g[False], g[True], d[False], d[True], hi - lo

def crenage(noms):
    pr = [profil(traits_complets(n)) for n in noms]
    Gc = np.array([p[0] for p in pr]); Gb = np.array([p[1] for p in pr])
    Dc = np.array([p[2] for p in pr]); Db = np.array([p[3] for p in pr]); W = np.array([p[4] for p in pr])
    k = np.zeros((len(noms), len(noms)))
    for i in range(len(noms)):
        # écart GAP entre deux traits ; une barre de V ou W peut aller jusqu'à toucher
        t = np.minimum.reduce([Dc[i] + Gc, Db[i] + Gc + GAP, Dc[i] + Gb + GAP, Db[i] + Gb + GAP])
        k[i] = -np.min(t, axis=1)
    lim = -(GAP + np.minimum(CHEVAUCHE, 0.25 * np.minimum(W[:, None], W[None, :])))
    k = np.maximum(k, lim)
    k = np.where(np.isfinite(k), k, lim)
    return np.round(k * SC / 5.0) * 5.0

def fea_crenage(noms, k):
    lignes = {}; colonnes = {}
    for i, n in enumerate(noms): lignes.setdefault(tuple(k[i]), []).append(n)
    for j, n in enumerate(noms): colonnes.setdefault(tuple(k[:, j]), []).append(n)
    cg = list(lignes.values()); cd = list(colonnes.values())
    out = []
    for i, g in enumerate(cg): out.append(f"@kg{i} = [{' '.join(g)}];")
    for j, g in enumerate(cd): out.append(f"@kd{j} = [{' '.join(g)}];")
    idx = {n: i for i, n in enumerate(noms)}
    out.append('feature kern {')
    npairs = 0
    for i, g in enumerate(cg):
        for j, d in enumerate(cd):
            v = int(k[idx[g[0]], idx[d[0]]])
            if v <= -5: out.append(f'  pos @kg{i} @kd{j} {v};'); npairs += 1
    out.append('} kern;')
    return '\n'.join(out), len(cg), len(cd), npairs

# ---------------------------------------------------------------- police
def construire(style, outdir):
    ordre = ['.notdef', 'space']; glyf = {}; hm = {}
    pen = TTGlyphPen(None)
    for pts in ([(40, 0), (40, 700), (400, 700), (400, 0)], [(80, 40), (360, 40), (360, 660), (80, 660)]):
        pen.moveTo(pts[0]); [pen.lineTo(p) for p in pts[1:]]; pen.closePath()
    glyf['.notdef'] = pen.glyph(); hm['.notdef'] = (440, 40)
    glyf['space'] = TTGlyphPen(None).glyph(); hm['space'] = (ESPACE_MOT, 0)
    tol = 0.45 if style == 'net' else 0.6
    pos = {}                                                      # nom -> (lo) pour placer les accents
    largeur_math = max(boite(D[n])[1] - boite(D[n])[0] for n in MATH) + GAP
    for nom in sorted(D):
        sts = D[nom]; lo, hi = boite(sts)
        if nom in MATH:                                           # signes de calcul : même chasse, centrés
            lo -= (largeur_math - GAP - (hi - lo)) / 2; hi = lo + largeur_math - GAP
        f = lambda x, y, lo=lo: (round((x - lo + GAP / 2) * SC), round(y * SC))
        glyf[nom] = vers_glyphe(contour(sts, style, zlib.crc32(nom.encode())), f, tol)
        hm[nom] = (round((hi - lo + GAP) * SC), round(GAP / 2 * SC)); pos[nom] = lo
        ordre.append(nom)
    for nom in sorted(MARQ):
        f = lambda x, y: (round(x * SC), round(y * SC))
        glyf[nom] = vers_glyphe(contour(MARQ[nom], style, zlib.crc32(nom.encode())), f, tol)
        hm[nom] = (0, 0); ordre.append(nom)
    def ancre(b, m):
        x, dy = placement(b, m); return round((x - pos[b] + GAP / 2) * SC), round(dy * SC)
    for nom in sorted(COMPO):
        b, ms = COMPO[nom]
        g = TTGlyphPen(glyf); g.addComponent(b, (1, 0, 0, 1, 0, 0))
        for m in ms: g.addComponent(NOM_MARQUE[m], (1, 0, 0, 1) + ancre(b, m))
        glyf[nom] = g.glyph(); hm[nom] = hm[b]; ordre.append(nom)
    for nom in sorted(ACC):
        sts = signes.M[ACC[nom]]; lo, hi = boite(sts)
        g = TTGlyphPen(glyf); g.addComponent(NOM_MARQUE[ACC[nom]], (1, 0, 0, 1, round((GAP / 2 - lo) * SC), 0))
        glyf[nom] = g.glyph(); hm[nom] = (round((hi - lo + GAP) * SC), 0); ordre.append(nom)
    fb = FontBuilder(1000, isTTF=True)
    fb.setupGlyphOrder(ordre)
    fb.setupCharacterMap(CMAP)
    fb.setupGlyf(glyf)
    gl = fb.font['glyf']
    for n in ordre:                                                # lsb = xMin réel
        g = gl[n]; g.recalcBounds(gl)
        hm[n] = (hm[n][0], getattr(g, 'xMin', 0) if g.numberOfContours else 0)
    fb.setupHorizontalMetrics(hm)
    fb.setupHorizontalHeader(ascent=ASC, descent=DESC, lineGap=0)
    ps = f'{FAMILLE}-{style.capitalize()}'
    nom_style = style.capitalize()
    fb.setupNameTable({
        'copyright': '© 2026 LaFleurStudio. All rights reserved.',
        'familyName': f'{FAMILLE} {nom_style}', 'styleName': 'Regular',
        'uniqueFontIdentifier': f'{VERSION:.3f};LFST;{ps}',
        'fullName': f'{FAMILLE} {nom_style}', 'psName': ps,
        'version': f'Version {VERSION:.3f}',
        'manufacturer': 'LaFleurStudio', 'designer': 'Jonathan Kern',
        'vendorURL': 'https://jonlekern.github.io/Fonts/',
        'typographicFamily': FAMILLE, 'typographicSubfamily': nom_style,
    })
    ymin = min(getattr(gl[n], 'yMin', 0) for n in ordre); ymax = max(getattr(gl[n], 'yMax', 0) for n in ordre)
    fb.setupOS2(version=4, usWeightClass=400, usWidthClass=5, achVendID='LFST', fsSelection=0x40 | 0x80, fsType=0,
                sTypoAscender=ASC, sTypoDescender=DESC, sTypoLineGap=0,
                usWinAscent=max(ymax, ASC), usWinDescent=max(-ymin, -DESC),
                sxHeight=round(XH * SC), sCapHeight=700, yStrikeoutPosition=320, yStrikeoutSize=22, ulCodePageRange1=1)
    fb.setupPost(underlinePosition=-120, underlineThickness=22)
    fb.font['head'].fontRevision = VERSION
    from fontTools.ttLib import newTable
    from fontTools.ttLib.tables import ttProgram
    gasp = newTable('gasp'); gasp.version = 1; gasp.gaspRange = {0xFFFF: 0x000F}; fb.font['gasp'] = gasp
    prep = newTable('prep'); prep.program = ttProgram.Program()
    prep.program.fromAssembly(['PUSHW[ ]', '511', 'SCANCTRL[ ]', 'PUSHB[ ]', '4', 'SCANTYPE[ ]']); fb.font['prep'] = prep
    # accents posés par la police (marques combinantes) + crénage
    bases = sorted(D) + sorted(COMPO) + sorted(ACC)
    haut = [NOM_MARQUE[m] for m in signes.COMB.values() if genre(m) == 'haut']
    bas = [NOM_MARQUE[m] for m in signes.COMB.values() if genre(m) == 'bas']
    fea = ['languagesystem DFLT dflt;', 'languagesystem latn dflt;',
           f"markClass [{' '.join(haut)}] <anchor 0 0> @HAUT;",
           f"markClass [{' '.join(bas)}] <anchor 0 0> @BAS;",
           f"markClass [{NOM_MARQUE['ogonek']}] <anchor 0 0> @OGO;",
           # i et j perdent leur point sous un accent
           f"@HAUTS = [{' '.join(haut)}];", f"@BASSES = [{' '.join(bas + [NOM_MARQUE['ogonek']])}];",
           'feature ccmp {', "  sub i' @HAUTS by dotlessi;", "  sub i' @BASSES @HAUTS by dotlessi;",
           "  sub j' @HAUTS by uni0237;", "  sub j' @BASSES @HAUTS by uni0237;",
           "  sub i' @BASSES @BASSES @HAUTS by dotlessi;", "  sub j' @BASSES @BASSES @HAUTS by uni0237;",
           "  sub iogonek' @HAUTS by iogonek.dotless;", "  sub iogonek' @BASSES @HAUTS by iogonek.dotless;", '} ccmp;',
           'feature case {'] + [f'  sub {n[:-5]} by {n};' for n in sorted(D) if n.endswith('.case')] + ['} case;',
           'feature mark {']
    for b in sorted(D):
        ah, ab, ao = ancre(b, 'aigu'), ancre(b, 'cedille'), ancre(b, 'ogonek')
        fea.append(f"  pos base {b} <anchor {ah[0]} {ah[1]}> mark @HAUT <anchor {ab[0]} {ab[1]}> mark @BAS "
                   f"<anchor {ao[0]} {ao[1]}> mark @OGO;")
    for c in sorted(COMPO):                                   # lettres accentuées : un accent de plus se pose au-dessus
        b, ms = COMPO[c]
        ah, ab, ao = ancre(b, 'aigu'), ancre(b, 'cedille'), ancre(b, 'ogonek')
        if any(genre(m) == 'haut' for m in ms): ah = (ah[0], ah[1] + round(220 * SC))
        if any(genre(m) != 'haut' for m in ms): ab = (ab[0], ab[1] - round(220 * SC))
        fea.append(f"  pos base {c} <anchor {ah[0]} {ah[1]}> mark @HAUT <anchor {ab[0]} {ab[1]}> mark @BAS "
                   f"<anchor {ao[0]} {ao[1]}> mark @OGO;")
    fea.append('} mark;')
    fea.append('feature mkmk {')
    fea.append(f"  pos mark [{' '.join(haut)}] <anchor 0 {round(200 * SC)}> mark @HAUT;")
    fea.append('} mkmk;')
    fea.append('table GDEF {')
    fea.append(f"  GlyphClassDef [{' '.join(bases)}], , [{' '.join(sorted(MARQ))}], ;")
    fea.append('} GDEF;')
    noms_k = [n for n in bases]
    k = crenage(noms_k)
    kf, ng, nd, npairs = fea_crenage(noms_k, k)
    addOpenTypeFeaturesFromString(fb.font, '\n'.join(fea) + '\n' + kf)
    os.makedirs(f'{outdir}/ttf', exist_ok=True); os.makedirs(f'{outdir}/woff2', exist_ok=True)
    fb.font.save(f'{outdir}/ttf/{ps}.ttf')
    w2 = TTFont(f'{outdir}/ttf/{ps}.ttf'); w2.flavor = 'woff2'; w2.save(f'{outdir}/woff2/{ps}.woff2')
    taille = os.path.getsize(f'{outdir}/ttf/{ps}.ttf') // 1024
    print(f'{ps}: {len(ordre)} glyphes, {len(CMAP)} caractères, crénage {ng}x{nd} classes / {npairs} paires, {taille} Ko')

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'fonts')
    styles = sys.argv[2:] or ['net', 'craie']
    for st in styles: construire(st, out)
