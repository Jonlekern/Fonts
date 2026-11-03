# Fûsard-032 : les 9 fichiers de police, de 100 (Hairline) à 900 (Black).
# Chaque graisse = même squelette + règles de triche.regles(poids), contours à épaisseur variable,
# union skia-pathops, approche + crénage calculés sur les profils, chiffres minuscules via « onum ».
import sys, os, math
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import triche
import fusard as techno
import droit
import pathops
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.reverseContourPen import ReverseContourPen
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.misc.timeTools import timestampNow
from build_font import NOMS, nom

SC = 0.7
UPM = 1000
INTR = 84
BAND = 14
GRAISSES = [(100, 'Hairline'), (200, 'Thin'), (300, 'Light'), (400, 'Regular'), (500, 'Medium'),
            (600, 'Bold'), (700, 'Extra Bold'), (800, 'Super Bold'), (900, 'Black')]

def traits_graisse(R):
    """Tous les traits de la graisse : capitales, minuscules, chiffres, ponctuation (règles du gras comprises)."""
    G = triche.glyphes(R)                                  # capitales + minuscules (+ chiffres minuscules)
    ov, ovl = R['ov'], R['ov'] * techno.XH / 1000.0
    def prep(sts):
        sts = [dict(p=[np.array([x * R['sx'], y]) for x, y in st['p']], caps=list(st['caps']),
                    detail=st.get('detail', False)) for st in sts]
        return triche.couper_biais(sts, ov) if R['poids'] >= 500 else sts
    P = techno.build_ponct(ovl)
    P['@'] = techno.arobase(ovl, techno.build_lc(ovl)['a'])
    maj = techno.build_chiffres_maj(ov)
    out = {}
    for ch in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz':
        out[ch] = G[ch]
    for ch in '0123456789':
        out[nom(ch)] = prep(maj[ch])
        out[nom(ch) + '.onum'] = G[ch]
    for ch in NOMS:
        if ch.isdigit(): continue
        out[nom(ch)] = prep(P[ch])
    return out

def nettoie(poly):
    """Points en double retirés, orientation trigo ; None si le polygone est plat."""
    pts = []
    for p in poly:
        p = (round(p[0], 3), round(p[1], 3))
        if not pts or abs(p[0] - pts[-1][0]) + abs(p[1] - pts[-1][1]) > 1e-3:
            pts.append(p)
    if len(pts) > 1 and abs(pts[0][0] - pts[-1][0]) + abs(pts[0][1] - pts[-1][1]) <= 1e-3:
        pts.pop()
    if len(pts) < 3:
        return None
    a = 0.0
    for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
        a += x0 * y1 - x1 * y0
    if abs(a) < 1.0:
        return None
    return pts if a > 0 else pts[::-1]

def _chemin(polys):
    p = pathops.Path()
    for pts in polys:
        p.moveTo(*pts[0])
        for pt in pts[1:]:
            p.lineTo(*pt)
        p.close()
    return p

def contour_un_trait(st, X, R):
    """Un seul polygone par trait : bord gauche puis bord droit, épaisseur variable (mêmes règles que triche)."""
    rv = R['rv']; rh = rv * R['horiz']
    P, coin = triche.densifier(st['p'])
    caps = st['caps']; n = len(P)
    U = [(P[i + 1] - P[i]) / (np.linalg.norm(P[i + 1] - P[i]) + 1e-9) for i in range(n - 1)]
    N = [np.array([-u[1], u[0]]) for u in U]
    tang = [U[0]] + [(U[i - 1] + U[i]) / 2 for i in range(1, n - 1)] + [U[-1]]
    r = np.array([rh + (rv - rh) * abs(t[1] / (np.linalg.norm(t) + 1e-9)) ** 2 for t in tang])
    if triche.est_detail(st, R['ov']):
        r *= R['detail']
    for c in X:
        dist = np.array([np.linalg.norm(p - c) for p in P])
        r = r * (1 - (1 - R['piege']) * np.clip(1 - dist / (1.0 * rv), 0, 1))
    s_ = np.concatenate([[0], np.cumsum([np.linalg.norm(P[i + 1] - P[i]) for i in range(n - 1)])]); L = s_[-1]
    tl = R['pointe'] * rv
    if caps[0] == 'tip': r = r * np.clip(s_ / min(tl, 0.45 * L), 0, 1)
    if caps[1] == 'tip': r = r * np.clip((L - s_) / min(tl, 0.45 * L), 0, 1)
    P = list(P)
    if caps[0] == 'T': P[0] = P[0] - U[0] * r[0] * 0.8
    if caps[1] == 'T': P[-1] = P[-1] + U[-1] * r[-1] * 0.8
    gauche, droite = [], []
    for i in range(n):
        if i == 0: m, k = N[0], 1.0
        elif i == n - 1: m, k = N[-1], 1.0
        else:
            m = N[i - 1] + N[i]; nm = np.linalg.norm(m)
            m = m / nm if nm > 1e-9 else N[i]
            k = 1.0 / max(float(m @ N[i]), 0.125)          # onglet, limité à 8 fois
        gauche.append(P[i] + m * r[i] * k); droite.append(P[i] - m * r[i] * k)
    return gauche + droite[::-1]

def contours(strokes, R):
    X = triche.croisements(strokes)
    polys = []
    for st in strokes:
        pts = nettoie([(float(x) * SC, float(y) * SC) for x, y in contour_un_trait(st, X, R)])
        if pts: polys.append(pts)
    p = _chemin(polys)
    try:
        return pathops.simplify(p, fix_winding=True, keep_starting_points=False)
    except pathops.PathOpsError:
        acc = pathops.Path()
        for pts in polys:
            for eps in (0.0, 0.013, -0.017):
                try:
                    acc = pathops.op(acc, _chemin([[(x + eps, y + eps) for x, y in pts]]), pathops.PathOp.UNION,
                                     fix_winding=True, keep_starting_points=False)
                    break
                except pathops.PathOpsError:
                    continue
        return acc

def profil(strokes, dx, r):
    bands = {}
    for st in strokes:
        for x, y in droit.dens(st['p'], step=8.0):
            x = x * SC + dx; y = y * SC
            b = int(math.floor(y / BAND))
            for bb in (b - 1, b, b + 1):
                lo, hi = bands.get(bb, (1e9, -1e9))
                bands[bb] = (min(lo, x - r), max(hi, x + r))
    return bands

def _dedans(pt, poly):
    x, y = pt; c = False
    for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
        if (y0 > y) != (y1 > y) and x < (x1 - x0) * (y - y0) / (y1 - y0) + x0:
            c = not c
    return c

def _aire(poly):
    return sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1])) / 2

def glyphe_ttf(path, dx):
    """Contours orientés d'après leur imbrication : extérieurs dans le sens horaire, trous dans l'autre."""
    rec = RecordingPen(); path.draw(rec)
    polys, cur = [], []
    for op, args in rec.value:
        if op == 'moveTo':
            cur = [args[0]]
        elif op == 'lineTo':
            cur.append(args[0])
        elif op in ('closePath', 'endPath'):
            if len(cur) >= 3: polys.append(cur)
            cur = []
        else:
            raise ValueError(op)
    pen = TTGlyphPen(None)
    for i, P in enumerate(polys):
        # point de test : milieu d'un côté, poussé un tout petit peu vers l'intérieur du contour
        (x0, y0), (x1, y1) = P[0], P[1]
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        nx, ny = -(y1 - y0), (x1 - x0); l = math.hypot(nx, ny) or 1
        sgn = 1 if _aire(P) > 0 else -1
        test = (mx + sgn * nx / l * 0.05, my + sgn * ny / l * 0.05)
        prof = sum(1 for j, Q in enumerate(polys) if j != i and _dedans(test, Q))
        exterieur = (prof % 2 == 0)
        horaire = _aire(P) < 0
        if exterieur != horaire:
            P = P[::-1]
        pts = [(round(x + dx), round(y)) for x, y in P]
        pen.moveTo(pts[0])
        for q in pts[1:]:
            pen.lineTo(q)
        pen.closePath()
    return pen.glyph()

def notdef(R):
    w, h = 420 / SC, 700 / SC
    st = [techno.S((0, 0), (w, 0)), techno.S((w, 0), (w, h)), techno.S((w, h), (0, h)), techno.S((0, h), (0, 0))]
    for s in st: s['caps'] = ['T', 'T']
    return st

def construire(poids, style, sortie):
    R = triche.regles(poids)
    SB = R['gap'] * SC / 2; GAP = 2 * SB
    traits = traits_graisse(R)
    order = ['.notdef', 'space'] + list(traits.keys())
    cmap = {0x20: 'space'}
    for ch in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789':
        cmap[ord(ch)] = nom(ch)
    for ch in NOMS:
        cmap[ord(ch)] = nom(ch)
    glyphs, adv, encre = {}, {}, {}
    glyphs['space'] = TTGlyphPen(None).glyph(); adv['space'] = round(380 + 0.4 * (R['rv'] - 16))
    for n in ['.notdef'] + list(traits.keys()):
        st = notdef(R) if n == '.notdef' else traits[n]
        path = contours(st, R)
        xmin, ymin, xmax, ymax = path.bounds
        dx = SB - xmin
        glyphs[n] = glyphe_ttf(path, dx)
        adv[n] = round(xmax - xmin + 2 * SB)
        encre[n] = (st, dx, xmax - xmin, ymin, ymax)
    r_ink = R['rv'] * SC
    profils = {n: profil(e[0], e[1] - SB, r_ink) for n, e in encre.items() if n != '.notdef'}
    paires = []
    for a in profils:
        pa = profils[a]; wa = encre[a][2]
        for b in profils:
            pb = profils[b]; need = -1e9
            for k, (l, h) in pb.items():
                if k in pa:
                    need = max(need, pa[k][1] - l + GAP)
            need = max(need, wa - INTR)
            kern = int(round((need - (wa + GAP)) / 10.0)) * 10
            if kern <= -20:
                paires.append((a, b, kern))
    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyphs)
    gl = fb.font['glyf']; lsb = {}
    for n in order:
        g = gl[n]
        if g.numberOfContours:
            g.recalcBounds(gl); lsb[n] = g.xMin
        else:
            lsb[n] = 0
    fb.setupHorizontalMetrics({n: (adv[n], lsb[n]) for n in order})
    ymax = max(e[4] for e in encre.values()); ymin = min(e[3] for e in encre.values())
    asc, desc = int(math.ceil(ymax / 10) * 10), int(math.floor(ymin / 10) * 10)
    fb.setupHorizontalHeader(ascent=asc, descent=desc)
    fam = 'Fûsard-032'
    ps = 'Fusard032-' + style.replace(' ', '')
    regular = (style == 'Regular')
    fb.setupNameTable({
        'copyright': '© 2026 LaFleurStudio',
        'familyName': fam if regular else f'{fam} {style}', 'styleName': 'Regular',
        'typographicFamily': fam, 'typographicSubfamily': style,
        'uniqueFontIdentifier': f'LaFleurStudio: {fam} {style}: 0.200',
        'fullName': f'{fam} {style}', 'psName': ps,
        'version': 'Version 0.200', 'manufacturer': 'LaFleurStudio', 'designer': 'LaFleurStudio',
    })
    fb.setupOS2(sTypoAscender=850, sTypoDescender=-350, sTypoLineGap=0, usWinAscent=asc, usWinDescent=-desc,
                sxHeight=round(techno.XH * SC), sCapHeight=round(1000 * SC), achVendID='LFST', fsType=0,
                fsSelection=0x40, usWeightClass=poids, ulCodePageRange1=1)
    fb.setupPost()
    fb.setupHead(unitsPerEm=UPM, fontRevision=0.2, created=timestampNow(), modified=timestampNow())
    fea = 'languagesystem DFLT dflt;\nlanguagesystem latn dflt;\n'
    fea += 'feature onum {\n' + ''.join(f'  sub {nom(c)} by {nom(c)}.onum;\n' for c in '0123456789') + '} onum;\n'
    fea += 'feature kern {\n' + ''.join(f'  pos {a} {b} {k};\n' for a, b, k in paires) + '} kern;\n'
    addOpenTypeFeaturesFromString(fb.font, fea)
    fb.save(sortie)
    return len(order), len(paires)

def essai(fichiers, out):
    from PIL import Image, ImageDraw, ImageFont, features
    moteur = ImageFont.Layout.RAQM if features.check('raqm') else ImageFont.Layout.BASIC
    lignes = len(fichiers)
    im = Image.new('RGB', (2700, 175 * lignes + 40), (0, 0, 0)); d = ImageDraw.Draw(im)
    Fl = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 26) if os.path.exists(
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf') else ImageFont.load_default()
    y = 25
    for (p, style), f in fichiers:
        F = ImageFont.truetype(f, 105, layout_engine=moteur)
        d.text((20, y + 55), str(p), font=Fl, fill=(255, 210, 60))
        d.text((110, y), 'LAFLEURSTUDIO lafleurstudio 132', font=F, fill=(238, 238, 238))
        y += 175
    im.save(out)

if __name__ == '__main__':
    dossier = sys.argv[1] if len(sys.argv) > 1 else 'fonts'
    os.makedirs(dossier, exist_ok=True)
    faits = []
    for p, style in GRAISSES:
        f = os.path.join(dossier, 'Fusard032-' + style.replace(' ', '') + '.ttf')
        n, k = construire(p, style, f)
        print(f'{f} : {n} glyphes, {k} paires de crénage', flush=True)
        faits.append(((p, style), f))
    if len(sys.argv) > 2:
        essai(faits, sys.argv[2])
