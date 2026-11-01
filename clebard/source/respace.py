# Espacement de Calebard appliqué à Clebard : approches lettre par lettre + crénage, à l'échelle des capitales
import sys, copy, statistics
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen

src, cal_fn, out = sys.argv[1:4]
f = TTFont(src); cal = TTFont(cal_fn)
gs = f.getGlyphSet(); cgs = cal.getGlyphSet()
def bnd(g, n):
    bp = BoundsPen(g); g[n].draw(bp); return bp.bounds
S = bnd(gs, 'H')[3] / bnd(cgs, 'H')[3]           # hauteur des capitales Clebard / Calebard
cal_names = set(cal.getGlyphOrder())
order = f.getGlyphOrder()
cs = f['CFF '].cff.topDictIndex[0].CharStrings

import unicodedata
cmap = f.getBestCmap(); rev = {g_: c for c, g_ in cmap.items()}
def base_of(n):
    """lettre de base d'un caractère accentué (Ï -> I), sinon None"""
    c = rev.get(n)
    if c is None: return None
    d = unicodedata.decomposition(chr(c)).split()
    if not d or d[0].startswith('<'): return None
    b = cmap.get(int(d[0], 16))
    return b if b and b != n else None
new_sb = {}; ratios = []
for n in order:
    b = bnd(gs, n); adv = f['hmtx'][n][0]
    if not b or adv <= 0 or n not in cal_names: continue
    cb = bnd(cgs, n); cadv = cal['hmtx'][n][0]
    if not cb: continue
    l, r = cb[0] * S, (cadv - cb[2]) * S
    ol, orr = b[0], adv - b[2]
    new_sb[n] = (l - ol, (l - ol) + (r - orr))       # (décalage du dessin, ajout à la chasse)
    if n.isalpha() and len(n) == 1:
        if ol > 5: ratios.append(l / ol)
        if orr > 5: ratios.append(r / orr)
# lettres accentuées : même placement que leur lettre de base (les accents ne comptent pas)
for n in order:
    bn = base_of(n)
    while bn and base_of(bn): bn = base_of(bn)
    if bn and bn in new_sb and f['hmtx'][n][0] == f['hmtx'][bn][0]:
        new_sb[n] = new_sb[bn]
R = statistics.median(ratios)
print('échelle', round(S, 4), 'rapport médian des approches', round(R, 3), 'glyphes repris de Calebard', len(new_sb))

for n in order:
    b = bnd(gs, n); adv = f['hmtx'][n][0]
    if not b or adv <= 0: 
        if adv > 0:                                          # espaces : largeur de Calebard
            f['hmtx'][n] = (round(cal['hmtx'][n][0] * S) if n in cal_names else round(adv * R), 0)
            t2 = T2CharStringPen(f['hmtx'][n][0], gs); cs[n] = t2.getCharString(private=cs[n].private, globalSubrs=cs[n].globalSubrs)
        continue
    ol, orr = b[0], adv - b[2]
    if n in new_sb:
        dx, dw = new_sb[n]; w = round(adv + dw)
    else:
        dx = ol * R - ol; w = round(ol * R + (b[2] - b[0]) + orr * R)
    t2 = T2CharStringPen(w, gs)
    gs[n].draw(TransformPen(t2, (1, 0, 0, 1, round(dx), 0)))
    cs[n] = t2.getCharString(private=cs[n].private, globalSubrs=cs[n].globalSubrs)
    f['hmtx'][n] = (w, round(b[0] + dx))

# crénage : celui de Calebard (sans le positionnement des accents), filtré et mis à l'échelle
have = set(order)
G = copy.deepcopy(cal['GPOS'].table)
keep = [i for i, lk in enumerate(G.LookupList.Lookup) if lk.LookupType == 2]
remap = {old: new for new, old in enumerate(keep)}
G.LookupList.Lookup = [G.LookupList.Lookup[i] for i in keep]; G.LookupList.LookupCount = len(keep)
def sc(v):
    if v is None: return
    for a in ('XAdvance', 'XPlacement'):
        if hasattr(v, a) and getattr(v, a): setattr(v, a, round(getattr(v, a) * S))
for lk in G.LookupList.Lookup:
    for st in lk.SubTable:
        if st.Format == 1:
            pairs = sorted([(g_, ps) for g_, ps in zip(st.Coverage.glyphs, st.PairSet) if g_ in have], key=lambda x: f.getGlyphID(x[0]))
            st.Coverage.glyphs = [g_ for g_, _ in pairs]; st.PairSet = [ps for _, ps in pairs]
            for ps in st.PairSet:
                ps.PairValueRecord = [r for r in ps.PairValueRecord if r.SecondGlyph in have]
                ps.PairValueCount = len(ps.PairValueRecord)
                for r in ps.PairValueRecord: sc(r.Value1); sc(r.Value2)
            st.PairSetCount = len(st.PairSet)
        else:
            st.Coverage.glyphs = sorted([g_ for g_ in st.Coverage.glyphs if g_ in have], key=f.getGlyphID)
            st.ClassDef1.classDefs = {g_: c for g_, c in st.ClassDef1.classDefs.items() if g_ in have}
            st.ClassDef2.classDefs = {g_: c for g_, c in st.ClassDef2.classDefs.items() if g_ in have}
            for c1 in st.Class1Record:
                for c2 in c1.Class2Record: sc(c2.Value1); sc(c2.Value2)
recs = []
for fr in G.FeatureList.FeatureRecord:
    if fr.FeatureTag != 'kern': continue
    fr.Feature.LookupListIndex = [remap[i] for i in fr.Feature.LookupListIndex if i in remap]
    fr.Feature.LookupCount = len(fr.Feature.LookupListIndex); recs.append(fr)
old_idx = {id(fr): i for i, fr in enumerate(G.FeatureList.FeatureRecord)}
new_idx = {old_idx[id(fr)]: i for i, fr in enumerate(recs)}
G.FeatureList.FeatureRecord = recs; G.FeatureList.FeatureCount = len(recs)
for sr in G.ScriptList.ScriptRecord:
    for ls in [sr.Script.DefaultLangSys] + [l.LangSys for l in sr.Script.LangSysRecord]:
        if ls is None: continue
        ls.FeatureIndex = [new_idx[i] for i in ls.FeatureIndex if i in new_idx]; ls.FeatureCount = len(ls.FeatureIndex)
        if ls.ReqFeatureIndex != 0xFFFF: ls.ReqFeatureIndex = new_idx.get(ls.ReqFeatureIndex, 0xFFFF)
f['GPOS'].table = G
f.save(out); print('ok', out)
