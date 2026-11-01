"""Calebard Goofy: Calebard Black where letters lean alternately right / left (12°).
- default glyphs: slanted right; '<name>.goofy' alternates: slanted left
- 'calt' feature: a glyph following a right-slanted glyph becomes left-slanted (restarts after spaces)
- kerning copied to the alternates
usage: build_goofy.py Calebard-Black.ttf Calebard-Goofy.ttf [angle]"""
import sys, math, copy
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib.tables import otTables as ot

src, dst = sys.argv[1], sys.argv[2]
T = math.tan(math.radians(float(sys.argv[3]) if len(sys.argv) > 3 else 12.0))
f = TTFont(src); gs = f.getGlyphSet(); order = f.getGlyphOrder()
gdef = f["GDEF"].table if "GDEF" in f else None
marks = {g for g, c in (gdef.GlyphClassDef.classDefs.items() if gdef and gdef.GlyphClassDef else []) if c == 3}

def ink(name):
    bp = BoundsPen(gs); gs[name].draw(bp); return bp.bounds

def slanted(name, s):
    rec = DecomposingRecordingPen(gs); gs[name].draw(rec)
    b = ink(name); cy = (b[1] + b[3]) / 2
    tt = TTGlyphPen(None); rec.replay(TransformPen(tt, (1, 0, s, 1, -s * cy, 0)))
    return tt.glyph()

parts = [n for n in order if n not in marks and n not in (".notdef", "space") and ink(n)]
glyf, hmtx = f["glyf"], f["hmtx"]
new_glyphs = {n: slanted(n, -T) for n in parts}          # left versions (computed before touching originals)
for n in parts:
    glyf[n] = slanted(n, T)                                # defaults lean right
alt = {n: n + ".goofy" for n in parts}
f.setGlyphOrder(order + [alt[n] for n in parts])
for n in parts:
    glyf[alt[n]] = new_glyphs[n]; hmtx[alt[n]] = hmtx[n]
for n in order + [alt[n] for n in parts]:
    g = glyf[n]; g.recalcBounds(glyf)
    hmtx[n] = (hmtx[n][0], getattr(g, "xMin", 0) if g.numberOfContours else 0)
if gdef and gdef.GlyphClassDef:
    for n in parts:
        if n in gdef.GlyphClassDef.classDefs: gdef.GlyphClassDef.classDefs[alt[n]] = gdef.GlyphClassDef.classDefs[n]

# ---- kerning: copy every pair-positioning entry to the alternates
gid = f.getReverseGlyphMap(rebuild=True)
def subtables(table):
    for lk in table.LookupList.Lookup:
        for st in lk.SubTable:
            yield lk, (st.ExtSubTable if lk.LookupType == 9 else st)
gpos = f["GPOS"].table
for lk, st in subtables(gpos):
    if getattr(st, "LookupType", None) not in (None, 2) or not hasattr(st, "Format"): continue
    if not hasattr(st, "Coverage"): continue
    if st.Format == 1 and hasattr(st, "PairSet"):
        for ps in st.PairSet:
            extra = [copy.deepcopy(r) for r in ps.PairValueRecord if r.SecondGlyph in alt]
            for r in extra: r.SecondGlyph = alt[r.SecondGlyph]
            ps.PairValueRecord = sorted(ps.PairValueRecord + extra, key=lambda r: gid[r.SecondGlyph]); ps.PairValueCount = len(ps.PairValueRecord)
        pairs = list(zip(st.Coverage.glyphs, st.PairSet))
        pairs += [(alt[g], copy.deepcopy(ps)) for g, ps in pairs if g in alt]
        pairs.sort(key=lambda p: gid[p[0]])
        st.Coverage.glyphs = [g for g, _ in pairs]; st.PairSet = [ps for _, ps in pairs]; st.PairSetCount = len(st.PairSet)
    elif st.Format == 2 and hasattr(st, "ClassDef1"):
        st.Coverage.glyphs = sorted(set(st.Coverage.glyphs) | {alt[g] for g in st.Coverage.glyphs if g in alt}, key=gid.get)
        for cd in (st.ClassDef1, st.ClassDef2):
            for g, c in list(cd.classDefs.items()):
                if g in alt: cd.classDefs[alt[g]] = c

# ---- GSUB 'calt': right-slanted glyph followed by a right-slanted glyph -> left
gsub = f["GSUB"].table
def cov(glyphs):
    c = ot.Coverage(); c.glyphs = sorted(glyphs, key=gid.get); return c
single = ot.SingleSubst(); single.mapping = dict(alt); single.Format = 2
lk_single = ot.Lookup(); lk_single.LookupType = 1; lk_single.LookupFlag = 0; lk_single.SubTable = [single]; lk_single.SubTableCount = 1
gsub.LookupList.Lookup.append(lk_single); i_single = len(gsub.LookupList.Lookup) - 1
chain = ot.ChainContextSubst(); chain.Format = 3
chain.BacktrackCoverage = [cov(parts)]; chain.BacktrackGlyphCount = 1
chain.InputCoverage = [cov(parts)]; chain.InputGlyphCount = 1
chain.LookAheadCoverage = []; chain.LookAheadGlyphCount = 0
rec = ot.SubstLookupRecord(); rec.SequenceIndex = 0; rec.LookupListIndex = i_single
chain.SubstLookupRecord = [rec]; chain.SubstCount = 1
lk_chain = ot.Lookup(); lk_chain.LookupType = 6; lk_chain.LookupFlag = 8  # ignore marks
lk_chain.SubTable = [chain]; lk_chain.SubTableCount = 1
gsub.LookupList.Lookup.append(lk_chain); i_chain = len(gsub.LookupList.Lookup) - 1
gsub.LookupList.LookupCount = len(gsub.LookupList.Lookup)

fr = ot.FeatureRecord(); fr.FeatureTag = "calt"; fr.Feature = ot.Feature()
fr.Feature.FeatureParams = None; fr.Feature.LookupListIndex = [i_chain]; fr.Feature.LookupCount = 1
old = list(gsub.FeatureList.FeatureRecord); allf = old + [fr]
new_order = sorted(range(len(allf)), key=lambda i: (allf[i].FeatureTag, i))
remap = {old_i: new_i for new_i, old_i in enumerate(new_order)}
gsub.FeatureList.FeatureRecord = [allf[i] for i in new_order]; gsub.FeatureList.FeatureCount = len(allf)
calt_idx = remap[len(allf) - 1]
def fix_langsys(ls):
    if ls is None: return
    ls.FeatureIndex = sorted([remap[i] for i in ls.FeatureIndex] + [calt_idx]); ls.FeatureCount = len(ls.FeatureIndex)
    if ls.ReqFeatureIndex != 0xFFFF: ls.ReqFeatureIndex = remap[ls.ReqFeatureIndex]
for sr in gsub.ScriptList.ScriptRecord:
    fix_langsys(sr.Script.DefaultLangSys)
    for lsr in sr.Script.LangSysRecord: fix_langsys(lsr.LangSys)

f["OS/2"].recalcAvgCharWidth(f)
f.save(dst)
print("slanted glyphs:", len(parts), "| alternates:", len(alt), "| GSUB lookups:", gsub.LookupList.LookupCount, "| calt index:", calt_idx)
