"""Calebard 1.0.2, étape 1 : L, U et lettres rondes réglés sur le vrai logo LAFLEURSTUDIO (t-shirt).
- L : la barre du bas s'allonge de 13,4 % de la largeur (le montant ne bouge pas)
- U : 4,35 % moins large (le milieu suit à moitié)
- C G J O Q S U Ə Œ : dépassement 58 sous la ligne de base, 57 au-dessus des capitales (logo : U −55, S −59/+57, O −60/+56)
- variantes dessinées à part (Ų Ư Ứ Ừ Ử Ữ Ự Ơ… Ç Ş Ł Ľ Ø Ǫ Ḉ) : même traitement, les accents bougent d'un bloc
- composites et ancres des accents suivent
- Goofy et Extra Goofy ne sont pas touchés
usage : logo102.py <ttf entrée> <ttf sortie>"""
import sys, math
from fontTools.ttLib import TTFont

H = 1350; OV_B, OV_T = 58, 57; YJ = 1000.0
L_RATIO, U_RATIO = 0.1337, 0.0435
FAMILLES = {
    'L': ['L', 'Lslash', 'Lcaron'],
    'U': ['U', 'Uhorn', 'uni1EE8', 'uni1EEA', 'uni1EEC', 'uni1EEE', 'uni1EF0', 'Uogonek'],
    'O': ['O', 'Ohorn', 'uni1EDA', 'uni1EDC', 'uni1EDE', 'uni1EE0', 'uni1EE2', 'uni01EA', 'Oslash'],
    'C': ['C', 'Ccedilla', 'uni1E08'], 'G': ['G'], 'J': ['J'], 'J.ss01': ['J.ss01'], 'Q': ['Q'],
    'S': ['S', 'Scedilla'], 'uni018F': ['uni018F'], 'OE': ['OE'],
}
HAUT_ROND = {'O', 'C', 'G', 'Q', 'S', 'uni018F', 'OE'}
BAS_ROND = {'O', 'C', 'G', 'Q', 'S', 'uni018F', 'OE', 'U', 'J', 'J.ss01'}

def clamp(v): return max(0.0, min(1.0, v))

class Regle:
    """déplacement d'un point selon la lettre de base"""
    def __init__(s, f, base):
        g = f['glyf'][base]; c = list(g.coordinates); on = [p for p, fl in zip(c, g.flags) if fl & 1]
        s.base = base
        s.ymin = min(y for _, y in c); s.ymax = max(y for _, y in c)
        ybas = min(y for _, y in f['glyf']['O'].coordinates) if base == 'Q' else s.ymin   # Q : le bas du rond, pas la queue
        s.kb = (OV_B + ybas) if base in BAS_ROND else 0       # ymin négatif : −16 → kb = 42
        s.kt = (OV_T - (s.ymax - H)) if base in HAUT_ROND else 0
        s.d = 0
        if base == 'L':
            s.cadre0 = s.cadre_L(c); x0, x1 = s.cadre0
            stem = max(x for x, y in c if y == s.ymax)
            s.r = ((stem + x1)/2 - x0)/(x1 - x0)
            s.d = round(L_RATIO*(x1 - x0))
        elif base == 'U':
            s.utop = max(y for _, y in c)
            s.cadre0 = s.cadre_U(c, s.utop); x0, x1 = s.cadre0
            s.d = -round(U_RATIO*(x1 - x0))
        if base == 'OE':
            low = min(on, key=lambda p: p[1]); s.oe_c = low[0]
            s.oe_e = min(x for x, y in on if y == 0)
    @staticmethod
    def cadre_L(c):
        top = max(y for _, y in c)
        return min(x for x, y in c if y == top), max(x for x, y in c if y == 0)
    @staticmethod
    def cadre_U(c, top):
        xs = [x for x, y in c if abs(y - top) <= 1]; x0 = min(xs)
        return x0, max(x for x in xs)
    def cadre(s, c):
        if s.base == 'L': return s.cadre_L(c)
        if s.base == 'U':
            xs = sorted(x for x, y in c if abs(y - s.utop) <= 1); x0 = xs[0]
            w0 = s.cadre0[1] - s.cadre0[0]
            return x0, max(x for x in xs if x <= x0 + w0 + 400)
        return None
    def fx(s, x, cad, extra=0):
        d = s.d - (extra if s.base == 'U' else 0)
        if s.base == 'L':
            x0, x1 = cad; return d if x > x0 + s.r*(x1 - x0) else 0
        if s.base == 'U':
            x0, x1 = cad; cx = (x0 + x1)/2; tol = 0.25*(cx - x0)
            return 0 if x < cx - tol else (d/2 if x <= cx + tol else d)
        return 0
    def fy(s, y, x=None):
        v = -s.kb*clamp(1 - y/YJ) + s.kt*clamp(1 - (H - y)/YJ)
        if s.base == 'OE' and x is not None:
            v *= 1.0 if x <= s.oe_c else clamp((s.oe_e - x)/(s.oe_e - s.oe_c))
        return v

def traite_contour(g, regle, cad, extra):
    """contours de la lettre et des accents dessinés dans la même forme"""
    c = list(g.coordinates); ends = g.endPtsOfContours; out = list(c)
    lo, hi = regle.ymin - 5, regle.ymax + 5
    x0, x1 = cad if cad else (-1e9, 1e9)
    def hors(p): return p[1] < lo or p[1] > hi or p[0] < x0 - 5 or p[0] > x1 + 5
    start = 0
    for e in ends:
        idx = list(range(start, e + 1)); pts = [c[i] for i in idx]
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        bb_hors = min(ys) < lo or max(ys) > hi or min(xs) < x0 - 5 or max(xs) > x1 + 5
        if all(hors(p) for p in pts) or (start > 0 and bb_hors and regle.base == 'L'):
            mx = sum(xs)/len(xs); my = sum(ys)/len(ys)
            dx = regle.fx(mx, cad, extra) if cad else 0; dy = regle.fy(my, mx)
            for i in idx: out[i] = (c[i][0] + dx, c[i][1] + dy)
        else:
            # suites de points hors de la lettre (accent soudé : corne, cédille, ogonek, barre du Ł)
            flags = [hors(p) for p in pts]; n = len(pts); vu = [False]*n
            for k in range(n):
                if not flags[k] or vu[k]: continue
                run = [k]; vu[k] = True; j = (k + 1) % n
                while flags[j] and not vu[j]: run.append(j); vu[j] = True; j = (j + 1) % n
                j = (k - 1) % n
                while flags[j] and not vu[j]: run.insert(0, j); vu[j] = True; j = (j - 1) % n
                mx = sum(pts[r][0] for r in run)/len(run); my = sum(pts[r][1] for r in run)/len(run)
                dx = regle.fx(mx, cad, extra) if cad else 0; dy = regle.fy(my, mx)
                for r in run: out[idx[r]] = (pts[r][0] + dx, pts[r][1] + dy)
            for k in range(n):
                if not flags[k]:
                    x, y = pts[k]
                    dx = regle.fx(x, cad, extra) if cad else 0
                    out[idx[k]] = (x + dx, y + regle.fy(y, x))
        start = e + 1
    for i, p in enumerate(out): g.coordinates[i] = (round(p[0]), round(p[1]))

def process(path, outpath, log=print):
    f = TTFont(path); glyf, hmtx = f['glyf'], f['hmtx']
    global H
    H = max(y for _, y in glyf['L'].coordinates)          # hauteur des capitales de cette graisse
    touche = {}            # nom -> (regle, cadre, extra)
    regles = {b: Regle(f, b) for b in FAMILLES if b in glyf}   # mesurées avant toute retouche
    for base, noms in FAMILLES.items():
        if base not in glyf: continue
        R = regles[base]
        cad_b = R.cadre(list(glyf[base].coordinates)) if base in ('L', 'U') else None
        for n in noms:
            if n not in glyf or glyf[n].isComposite(): continue
            g = glyf[n]; cad = R.cadre(list(g.coordinates)) if base in ('L', 'U') else None
            extra = 0
            if base == 'U':                     # variantes restées larges en 1.0.1
                extra = (cad[1] - cad[0]) - (cad_b[1] - cad_b[0])
            traite_contour(g, R, cad, extra)
            dadv = R.d - extra if base == 'U' else R.d
            hmtx[n] = (hmtx[n][0] + round(dadv), hmtx[n][1])
            g.recalcBounds(glyf); touche[n] = (R, cad, extra)
        log(base, 'd=%d kb=%d kt=%d' % (R.d, R.kb, R.kt))
    # composites posés sur une lettre touchée
    for n in f.getGlyphOrder():
        g = glyf[n]
        if not g.isComposite(): continue
        b0 = g.components[0].glyphName
        if b0 not in touche: continue
        R, cad, extra = touche[b0]
        gs = f.getGlyphSet()
        from fontTools.pens.boundsPen import BoundsPen
        for k in g.components[1:]:
            bp = BoundsPen(gs); gs[k.glyphName].draw(bp)
            if not bp.bounds: continue
            mx = (bp.bounds[0] + bp.bounds[2])/2 + k.x; my = (bp.bounds[1] + bp.bounds[3])/2 + k.y
            k.x = round(k.x + (R.fx(mx, cad, extra) if cad else 0)); k.y = round(k.y + R.fy(my, mx))
        dadv = R.d - extra if R.base == 'U' else R.d
        hmtx[n] = (hmtx[n][0] + round(dadv), hmtx[n][1]); g.recalcBounds(glyf); touche[n] = (R, cad, extra)
    # ancres des accents
    for lk in f['GPOS'].table.LookupList.Lookup:
        subs = lk.SubTable if lk.LookupType != 9 else [s.ExtSubTable for s in lk.SubTable]
        typ = lk.LookupType if lk.LookupType != 9 else lk.SubTable[0].ExtensionLookupType
        if typ != 4: continue
        for st in subs:
            bc = st.BaseCoverage.glyphs
            for n, (R, cad, extra) in touche.items():
                if n not in bc: continue
                for a in st.BaseArray.BaseRecord[bc.index(n)].BaseAnchor:
                    if a is None: continue
                    x, y = a.XCoordinate, a.YCoordinate
                    a.XCoordinate = round(x + (R.fx(x, cad, extra) if cad else 0)); a.YCoordinate = round(y + R.fy(y, x))
    f['OS/2'].recalcAvgCharWidth(f)
    f.save(outpath)
    return touche

if __name__ == '__main__':
    t = process(sys.argv[1], sys.argv[2]); print(len(t), 'glyphes touchés')
