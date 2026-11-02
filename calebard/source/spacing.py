"""Espacement Calebard réglé sur le logo LAFLEURSTUDIO.
1. Capitales : règles par type de côté (droit, rond, bras, ouvert, diagonale, jambe), fixées sur le Black.
   Les autres graisses gardent leurs différences : chaque côté est multiplié par le même rapport que dans le Black.
2. Minuscules, chiffres, signes : élargis dans la même proportion moyenne que les capitales.
3. Lettres accentuées et composées : suivent leur lettre de base. Chiffres tabulaires : largeur inchangée.
4. L'ancien réglage L–A est retiré ; 12 paires règlent LAFLEURSTUDIO exactement sur le logo.
usage : spacing.py <dossier ttf> espaces-logo.json"""
import sys, re, json, unicodedata
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.otlLib.builder import buildPairPosGlyphsSubtable, buildLookup, buildValue
import uharfbuzz as hb, io

D, LOGO = sys.argv[1], sys.argv[2]
WEIGHTS = ['Hairline', 'Thin', 'Light', 'Regular', 'Medium', 'Bold', 'ExtraBold', 'SuperBold', 'Black', 'ExtraBlack', 'ExtremeBlack']
CAP = 1350
RULE = {'droit': 0.192, 'rond': 0.103, 'bras': 0.128, 'ouvert': 0.049, 'diagonale': 0.025, 'jambe': 0.066}
RULE['mi-rond'] = (RULE['droit'] + RULE['rond']) / 2
SIDES = {'A': 'diagonale diagonale', 'B': 'droit rond', 'C': 'rond bras', 'D': 'droit rond', 'E': 'droit bras',
 'F': 'droit bras', 'G': 'rond mi-rond', 'H': 'droit droit', 'I': 'droit droit', 'J': 'ouvert droit',
 'K': 'droit diagonale', 'L': 'droit ouvert', 'M': 'droit droit', 'N': 'droit droit', 'O': 'rond rond',
 'P': 'droit rond', 'Q': 'rond jambe', 'R': 'droit jambe', 'S': 'rond rond', 'T': 'ouvert ouvert',
 'U': 'droit droit', 'V': 'diagonale diagonale', 'W': 'diagonale diagonale', 'X': 'diagonale diagonale',
 'Y': 'diagonale diagonale', 'Z': 'bras bras', 'J.ss01': 'bras droit'}
SPECIAL = {'AE': ('A', 'E'), 'OE': ('O', 'E'), 'Eth': ('D', 'D'), 'uni018F': ('O', 'O'), 'Eng': ('N', 'N'),
           'Thorn': ('P', 'P'), 'uni1E9E': ('B', 'B'), 'V.ss01': ('V', 'V')}
MARK_CATS = ('Mn', 'Mc', 'Me', 'Sk', 'Lm')

def ink(gs, n):
    b = BoundsPen(gs); gs[n].draw(b); return b.bounds

def sides(f, n):
    b = ink(f.getGlyphSet(), n); aw = f['hmtx'][n][0]
    return (b[0], aw - b[2]) if b else None

def rev_cmap(f): return {v: k for k, v in f.getBestCmap().items()}

def cap_base(f, n, rev):
    """lettre dont la capitale n suit l'espacement, côté gauche et côté droit"""
    if n in SIDES: return n, n
    if n in SPECIAL: return SPECIAL[n]
    u = rev.get(n) or rev.get(n.split('.')[0])
    if u and unicodedata.category(chr(u)) == 'Lu':
        m = re.match(r'LATIN CAPITAL LETTER ([A-Z]) ', unicodedata.name(chr(u)) + ' ')
        if m: return m.group(1), m.group(1)
    return None

# ---- 1. cibles sur le Black
B = TTFont(f'{D}/Calebard-Black.ttf'); revB = rev_cmap(B); cmB = B.getBestCmap()
name_of = lambda ch: cmB[ord(ch)] if len(ch) == 1 else ch
ratio = {}            # glyphe -> (rapport gauche, rapport droit) ou ('delta', dl, dr)
for key, s in SIDES.items():
    n = name_of(key); l, r = s.split(); cl, cr = sides(B, n)
    tl, tr = RULE[l] * CAP, RULE[r] * CAP
    ratio[n] = (('r', tl / cl) if cl > 20 else ('d', tl - cl), ('r', tr / cr) if cr > 20 else ('d', tr - cr))
cur = sum(sum(sides(B, name_of(k))) for k in SIDES if len(k) == 1)
tgt = sum((RULE[SIDES[k].split()[0]] + RULE[SIDES[k].split()[1]]) * CAP for k in SIDES if len(k) == 1)
G = tgt / cur
print('capitales : espaces ×', round(G, 3), '(minuscules, chiffres et signes suivent)')
for n in B.getGlyphOrder():
    if n in ratio or B['glyf'][n].isComposite() or B['glyf'][n].numberOfContours <= 0: continue
    cb = cap_base(B, n, revB)
    if cb: ratio[n] = (ratio[name_of(cb[0])][0], ratio[name_of(cb[1])][1])

def apply_side(v, rr): return v * rr[1] if rr[0] == 'r' else v + rr[1]

def respace(path):
    f = TTFont(path); glyf, hmtx = f['glyf'], f['hmtx']; gs = f.getGlyphSet(); rev = rev_cmap(f)
    gdef = f['GDEF'].table.GlyphClassDef.classDefs
    def is_mark(n):
        if gdef.get(n) == 3: return True
        u = rev.get(n) or rev.get(n.split('.')[0])
        return bool(u) and unicodedata.category(chr(u)) in MARK_CATS
    mv = {}                                                   # glyphe -> (dx, dw)
    for n in f.getGlyphOrder():
        g = glyf[n]
        if g.isComposite() or n.startswith('flower'): continue
        if g.numberOfContours == 0:
            if n in ('space', 'uni00A0'): aw = hmtx[n][0]; hmtx[n] = (round(aw * G), 0); mv[n] = (0, hmtx[n][0] - aw)
            continue
        if hmtx[n][0] == 0 or (is_mark(n) and gdef.get(n) == 3): continue
        b = ink(gs, n); cl, cr = b[0], hmtx[n][0] - b[2]
        if n in ratio: nl, nr = apply_side(cl, ratio[n][0]), apply_side(cr, ratio[n][1])
        else: nl, nr = cl * G, cr * G
        dx = round(nl - cl); new_aw = round(nl) + round(b[2] - b[0]) + round(nr)
        g.coordinates.translate((dx, 0)); g.recalcBounds(glyf)
        mv[n] = (dx, new_aw - hmtx[n][0]); hmtx[n] = (new_aw, g.xMin)
    def comp(n):
        if n in mv or not glyf[n].isComposite(): return mv.get(n, (0, 0))
        g = glyf[n]; comps = g.components
        bases = [i for i, c in enumerate(comps) if not is_mark(c.glyphName)] or [0]
        info = {i: comp(comps[i].glyphName) for i in bases}
        if n.endswith('.tf'):                                  # chiffres tabulaires : même largeur, même place
            for c in comps: c.x -= info[bases[0]][0]
            g.recalcBounds(glyf); hmtx[n] = (hmtx[n][0], g.xMin); mv[n] = (0, 0); return mv[n]
        cum, shift = 0, {}
        for i in bases: shift[i] = cum; cum += info[i][1]
        for i, c in enumerate(comps):
            if i in bases: c.x += shift[i]
            else:
                a = max([j for j in bases if j < i], default=bases[0]); c.x += shift[a] + info[a][0]
        g.recalcBounds(glyf); dx0 = info[bases[0]][0]
        mv[n] = (dx0, cum); hmtx[n] = (hmtx[n][0] + cum, g.xMin if g.numberOfContours else 0); return mv[n]
    for n in f.getGlyphOrder(): comp(n)
    # ancres des accents et des ligatures
    for lk in f['GPOS'].table.LookupList.Lookup:
        for st in lk.SubTable:
            if lk.LookupType == 4:
                for i, n in enumerate(st.BaseCoverage.glyphs):
                    for a in st.BaseArray.BaseRecord[i].BaseAnchor:
                        if a is not None: a.XCoordinate += mv.get(n, (0, 0))[0]
            elif lk.LookupType == 5:
                for i, n in enumerate(st.LigatureCoverage.glyphs):
                    for cr in st.LigatureArray.LigatureAttach[i].ComponentRecord:
                        for a in cr.LigatureAnchor:
                            if a is not None: a.XCoordinate += mv.get(n, (0, 0))[0]
            elif lk.LookupType == 2 and getattr(st, 'Format', 0) == 1 and st.Coverage.glyphs == ['L'] \
                    and len(st.PairSet) == 1 and [r.SecondGlyph for r in st.PairSet[0].PairValueRecord] == ['A']:
                st.PairSet[0].PairValueRecord[0].Value1.XAdvance = 0          # ancien réglage L–A retiré
    f['OS/2'].recalcAvgCharWidth(f)
    f.save(path)

for w in WEIGHTS: respace(f'{D}/Calebard-{w}.ttf')

# ---- 4. paires de LAFLEURSTUDIO réglées sur le logo (mêmes valeurs dans toutes les graisses)
target = list(json.load(open(LOGO))['espaces'].values())
TEXT = 'LAFLEURSTUDIO'
def gaps(path):
    data = open(path, 'rb').read(); f = TTFont(io.BytesIO(data)); gs = f.getGlyphSet()
    font = hb.Font(hb.Face(data)); buf = hb.Buffer(); buf.add_str(TEXT); buf.guess_segment_properties(); hb.shape(font, buf, {'kern': True})
    x = 0; bx = []
    for i, p in zip(buf.glyph_infos, buf.glyph_positions):
        b = ink(gs, font.glyph_to_string(i.codepoint)); bx.append((x + p.x_offset + b[0], x + p.x_offset + b[2])); x += p.x_advance
    return [b2[0] - b1[1] for b1, b2 in zip(bx, bx[1:])]
now = gaps(f'{D}/Calebard-Black.ttf')
pairs = {}
for (a, b), t, c in zip(zip(TEXT, TEXT[1:]), target, now):
    pairs[(a, b)] = pairs.get((a, b), 0) + round(t - c)
print('réglage des paires :', {a + b: v for (a, b), v in pairs.items()})
for w in WEIGHTS:
    p = f'{D}/Calebard-{w}.ttf'; f = TTFont(p); gpos = f['GPOS'].table
    st = buildPairPosGlyphsSubtable({k: (buildValue({'XAdvance': v}), None) for k, v in pairs.items()}, f.getReverseGlyphMap())
    gpos.LookupList.Lookup.append(buildLookup([st])); gpos.LookupList.LookupCount = len(gpos.LookupList.Lookup)
    idx = gpos.LookupList.LookupCount - 1
    for fr in gpos.FeatureList.FeatureRecord:
        if fr.FeatureTag == 'kern': fr.Feature.LookupListIndex.append(idx); fr.Feature.LookupCount += 1
    f.save(p)
print('écart restant sur le logo (unités) :', [round(t - c) for t, c in zip(target, gaps(f'{D}/Calebard-Black.ttf'))])
