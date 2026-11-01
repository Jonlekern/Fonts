"""Calebard Extra Goofy: Calebard Black where each letter is rotated, alternating direction and
mixing 4°, 7° and 10°. Cycle per word: +7, -4, +10, -7, +4, -10 (then repeats).
- default glyphs: +7° ; alternates '<name>.eg1'..'.eg5' for the other steps
- 'calt': each glyph takes the next step of the cycle after the previous glyph; restarts after spaces
- kerning copied to all alternates; ligatures off so every letter takes part
usage: build_extra_goofy.py Calebard-Black.ttf out.ttf"""
import sys, math, copy
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib.tables import otTables as ot

CYCLE = [7, -4, 10, -7, 4, -10]
src, dst = sys.argv[1], sys.argv[2]
f = TTFont(src); gs = f.getGlyphSet(); order = f.getGlyphOrder()
gdef = f["GDEF"].table if "GDEF" in f else None
marks = {g for g, c in (gdef.GlyphClassDef.classDefs.items() if gdef and gdef.GlyphClassDef else []) if c == 3}

def ink(name):
    bp = BoundsPen(gs); gs[name].draw(bp); return bp.bounds

def rotated(name, deg):
    rec = DecomposingRecordingPen(gs); gs[name].draw(rec)
    x0, y0, x1, y1 = ink(name); cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    a = math.radians(deg); c, s = math.cos(a), math.sin(a)
    tt = TTGlyphPen(None)
    rec.replay(TransformPen(tt, (c, s, -s, c, cx - cx * c + cy * s, cy - cx * s - cy * c)))
    return tt.glyph()

parts = [n for n in order if n not in marks and n not in (".notdef", "space") and ink(n)]
glyf, hmtx = f["glyf"], f["hmtx"]
variants = {k: {n: rotated(n, CYCLE[k]) for n in parts} for k in range(6)}   # computed from the originals
alts = {k: {n: f"{n}.eg{k}" for n in parts} for k in range(1, 6)}
for n in parts: glyf[n] = variants[0][n]
new_names = [alts[k][n] for k in range(1, 6) for n in parts]
f.setGlyphOrder(order + new_names)
for k in range(1, 6):
    for n in parts:
        glyf[alts[k][n]] = variants[k][n]; hmtx[alts[k][n]] = hmtx[n]
for n in order + new_names:
    g = glyf[n]; g.recalcBounds(glyf)
    hmtx[n] = (hmtx[n][0], getattr(g, "xMin", 0) if g.numberOfContours else 0)
if gdef and gdef.GlyphClassDef:
    for k in range(1, 6):
        for n in parts:
            if n in gdef.GlyphClassDef.classDefs: gdef.GlyphClassDef.classDefs[alts[k][n]] = gdef.GlyphClassDef.classDefs[n]

# ---- kerning copied to every alternate
gid = f.getReverseGlyphMap(rebuild=True)
all_alts = {n: [alts[k][n] for k in range(1, 6)] for n in parts}
gpos = f["GPOS"].table
for lk in gpos.LookupList.Lookup:
    for st in lk.SubTable:
        st = st.ExtSubTable if lk.LookupType == 9 else st
        if lk.LookupType not in (2, 9) or not hasattr(st, "Coverage"): continue
        if st.Format == 1 and hasattr(st, "PairSet"):
            for ps in st.PairSet:
                extra = []
                for r in ps.PairValueRecord:
                    for a in all_alts.get(r.SecondGlyph, []):
                        r2 = copy.deepcopy(r); r2.SecondGlyph = a; extra.append(r2)
                ps.PairValueRecord = sorted(ps.PairValueRecord + extra, key=lambda r: gid[r.SecondGlyph]); ps.PairValueCount = len(ps.PairValueRecord)
            pairs = list(zip(st.Coverage.glyphs, st.PairSet))
            pairs += [(a, copy.deepcopy(ps)) for g, ps in list(pairs) for a in all_alts.get(g, [])]
            pairs.sort(key=lambda p: gid[p[0]])
            st.Coverage.glyphs = [g for g, _ in pairs]; st.PairSet = [ps for _, ps in pairs]; st.PairSetCount = len(st.PairSet)
        elif st.Format == 2 and hasattr(st, "ClassDef1"):
            st.Coverage.glyphs = sorted(set(st.Coverage.glyphs) | {a for g in st.Coverage.glyphs for a in all_alts.get(g, [])}, key=gid.get)
            for cd in (st.ClassDef1, st.ClassDef2):
                for g, c in list(cd.classDefs.items()):
                    for a in all_alts.get(g, []): cd.classDefs[a] = c

# ---- GSUB: cycle through the 6 steps
gsub = f["GSUB"].table
def cov(glyphs):
    c = ot.Coverage(); c.glyphs = sorted(glyphs, key=gid.get); return c
def add_lookup(lk):
    gsub.LookupList.Lookup.append(lk); gsub.LookupList.LookupCount = len(gsub.LookupList.Lookup); return gsub.LookupList.LookupCount - 1
single_idx = {}
for k in range(1, 6):
    st = ot.SingleSubst(); st.mapping = dict(alts[k]); st.Format = 2
    lk = ot.Lookup(); lk.LookupType = 1; lk.LookupFlag = 0; lk.SubTable = [st]; lk.SubTableCount = 1
    single_idx[k] = add_lookup(lk)
step_glyphs = {0: parts, **{k: list(alts[k].values()) for k in range(1, 6)}}
chain_subs = []
for k in range(0, 5):                       # after step k comes step k+1 ; after step 5 comes step 0 (default)
    ch = ot.ChainContextSubst(); ch.Format = 3
    ch.BacktrackCoverage = [cov(step_glyphs[k])]; ch.BacktrackGlyphCount = 1
    ch.InputCoverage = [cov(parts)]; ch.InputGlyphCount = 1
    ch.LookAheadCoverage = []; ch.LookAheadGlyphCount = 0
    r = ot.SubstLookupRecord(); r.SequenceIndex = 0; r.LookupListIndex = single_idx[k + 1]
    ch.SubstLookupRecord = [r]; ch.SubstCount = 1
    chain_subs.append(ch)
lk = ot.Lookup(); lk.LookupType = 6; lk.LookupFlag = 8; lk.SubTable = chain_subs; lk.SubTableCount = len(chain_subs)
i_chain = add_lookup(lk)

fr = ot.FeatureRecord(); fr.FeatureTag = "calt"; fr.Feature = ot.Feature()
fr.Feature.FeatureParams = None; fr.Feature.LookupListIndex = [i_chain]; fr.Feature.LookupCount = 1
old = list(gsub.FeatureList.FeatureRecord); allf = old + [fr]
new_order = sorted(range(len(allf)), key=lambda i: (allf[i].FeatureTag, i))
remap = {o: n for n, o in enumerate(new_order)}
gsub.FeatureList.FeatureRecord = [allf[i] for i in new_order]; gsub.FeatureList.FeatureCount = len(allf)
calt_idx = remap[len(allf) - 1]
liga = {remap[i] for i, fr_ in enumerate(old) if fr_.FeatureTag in ("liga", "dlig", "clig")}
def fix(ls):
    if ls is None: return
    ls.FeatureIndex = sorted([remap[i] for i in ls.FeatureIndex if remap[i] not in liga] + [calt_idx]); ls.FeatureCount = len(ls.FeatureIndex)
    if ls.ReqFeatureIndex != 0xFFFF: ls.ReqFeatureIndex = remap[ls.ReqFeatureIndex]
for sr in gsub.ScriptList.ScriptRecord:
    fix(sr.Script.DefaultLangSys)
    for l in sr.Script.LangSysRecord: fix(l.LangSys)

# ---- vertical metrics: rotated letters reach higher / lower, avoid clipping
ymax = max(getattr(glyf[n], "yMax", 0) for n in f.getGlyphOrder()); ymin = min(getattr(glyf[n], "yMin", 0) for n in f.getGlyphOrder())
os2 = f["OS/2"]
os2.usWinAscent = max(os2.usWinAscent, ymax); os2.usWinDescent = max(os2.usWinDescent, -ymin)
os2.recalcAvgCharWidth(f)
f.save(dst)
print("letters:", len(parts), "| glyphs:", len(f.getGlyphOrder()), "| yMax/yMin:", ymax, ymin, "| win:", os2.usWinAscent, os2.usWinDescent)
