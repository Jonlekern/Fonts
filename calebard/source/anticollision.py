"""Anti-collision : aucune paire qui contient une lettre russe ne doit se toucher.
Chaque paire (russe + russe, russe + latin, chiffres, ponctuation) est composée avec HarfBuzz, dans tous les contextes
de Goofy et Extra Goofy (les lettres penchent une sur deux, ou tournent sur 6 pas). On mesure le blanc entre les deux
encres, rangée par rangée de 4 unités. Si le blanc est plus petit que SEUIL, on ajoute un crénage positif pour cette
paire précise de glyphes, dans un lookup à part de la fonction kern.
usage : anticollision.py fichier.ttf [...]"""
import sys, numpy as np, uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from fontTools.ttLib.tables import otTables as ot

PAS = 4; YS = np.arange(-1200, 3200, PAS) + PAS / 2; K = 8

class Plat(BasePen):
    def __init__(s, gs): super().__init__(gs); s.segs = []; s.cur = s.dep = None
    def _moveTo(s, p): s.cur = s.dep = p
    def _lineTo(s, p): s.segs.append((s.cur, p)); s.cur = p
    def _curveToOne(s, p1, p2, p3):
        p0 = s.cur
        for i in range(1, 13):
            t = i / 12; m = 1 - t
            s._lineTo((m**3*p0[0]+3*m*m*t*p1[0]+3*m*t*t*p2[0]+t**3*p3[0], m**3*p0[1]+3*m*m*t*p1[1]+3*m*t*t*p2[1]+t**3*p3[1]))
    def _qCurveToOne(s, p1, p2):
        p0 = s.cur
        for i in range(1, 11):
            t = i / 10; m = 1 - t
            s._lineTo((m*m*p0[0]+2*m*t*p1[0]+t*t*p2[0], m*m*p0[1]+2*m*t*p1[1]+t*t*p2[1]))
    def _closePath(s):
        if s.cur != s.dep: s._lineTo(s.dep)
    _endPath = _closePath

def trame(gs, n):
    p = Plat(gs); gs[n].draw(p)
    if not p.segs: return None
    L = np.full((len(YS), K), np.nan); R = np.full((len(YS), K), np.nan)
    S = np.array([[a[0], a[1], b[0], b[1]] for a, b in p.segs]); x0, y0, x1, y1 = S.T
    for i, y in enumerate(YS):
        m = ((y0 <= y) & (y1 > y)) | ((y1 <= y) & (y0 > y))
        if not m.any(): continue
        xa = x0[m] + (y - y0[m]) * (x1[m] - x0[m]) / (y1[m] - y0[m]); w = np.where(y1[m] > y0[m], 1, -1)
        o = np.argsort(xa); xa = xa[o]; c = np.cumsum(w[o]); seg = []; dedans = False
        for j in range(len(xa)):
            if not dedans and c[j] != 0: st = xa[j]; dedans = True
            elif dedans and c[j] == 0: seg.append((st, xa[j])); dedans = False
        mg = []
        for a, b in seg:
            if mg and a <= mg[-1][1]: mg[-1] = (mg[-1][0], max(b, mg[-1][1]))
            else: mg.append((a, b))
        for k, (a, b) in enumerate(mg[:K]): L[i, k] = a; R[i, k] = b
    return L, R

def blanc(ta, xa, tb, xb):
    if ta is None or tb is None: return None
    La, Ra = ta; Lb, Rb = tb
    r = ~np.isnan(La[:, 0]) & ~np.isnan(Lb[:, 0])
    if not r.any(): return None
    la = La[r][:, :, None] + xa; ra = Ra[r][:, :, None] + xa; lb = Lb[r][:, None, :] + xb; rb = Rb[r][:, None, :] + xb
    ov = np.minimum(ra, rb) - np.maximum(la, lb)
    return float(np.nanmin(np.where(ov > 0, -ov, np.maximum(lb - ra, la - rb))))

def traite(chemin):
    t = TTFont(chemin); gs = t.getGlyphSet(); noms = t.getGlyphOrder()
    font = hb.Font(hb.Face(open(chemin, 'rb').read()))
    goofy, extra = 'A.goofy' in noms, 'A.eg1' in noms
    SEUIL = 40 if (goofy or extra) else 60
    cyr = [chr(c) for c in range(0x410, 0x450)] + ['Ё', 'ё']
    aut = list('.,:;!?«»—–()-') + [str(i) for i in range(10)] + [chr(c) for c in range(65, 91)] + [chr(c) for c in range(97, 123)]
    paires = [(a, b) for a in cyr for b in cyr] + [(a, b) for a in cyr for b in aut] + [(a, b) for a in aut for b in cyr]
    prefixes = ['', 'н', 'нн', 'ннн', 'нннн', 'ннннн'][:6 if extra else 2 if goofy else 1]
    cache = {}
    def T(n):
        if n not in cache: cache[n] = trame(gs, n)
        return cache[n]
    besoin = {}
    for a, b in paires:
        for pre in prefixes:
            buf = hb.Buffer(); buf.add_str(pre + a + b); buf.guess_segment_properties(); buf.script = 'cyrl'; buf.direction = 'ltr'
            hb.shape(font, buf)
            x = 0; pos = {}
            for i, p in zip(buf.glyph_infos, buf.glyph_positions):
                pos.setdefault(i.cluster, []).append((noms[i.codepoint], x + p.x_offset)); x += p.x_advance
            ga, gb = pos.get(len(pre)), pos.get(len(pre) + 1)
            if not ga or not gb or len(ga) != 1 or len(gb) != 1: continue
            g = blanc(T(ga[0][0]), ga[0][1], T(gb[0][0]), gb[0][1])
            if g is not None and g < SEUIL:
                k = (ga[0][0], gb[0][0]); besoin[k] = max(besoin.get(k, 0), int(np.ceil(SEUIL - g)))
    if not besoin: print(chemin.split('/')[-1], 'aucune collision'); return
    gpos = t['GPOS'].table; gid = t.getReverseGlyphMap(rebuild=True)
    st = ot.PairPos(); st.Format = 1; st.ValueFormat1 = 4; st.ValueFormat2 = 0
    prem = {}
    for (a, b), v in besoin.items(): prem.setdefault(a, {})[b] = v
    st.Coverage = ot.Coverage(); st.Coverage.glyphs = sorted(prem, key=gid.get); st.PairSet = []
    for a in st.Coverage.glyphs:
        ps = ot.PairSet(); ps.PairValueRecord = []
        for b in sorted(prem[a], key=gid.get):
            r = ot.PairValueRecord(); r.SecondGlyph = b; r.Value1 = ot.ValueRecord(); r.Value1.XAdvance = prem[a][b]; ps.PairValueRecord.append(r)
        ps.PairValueCount = len(ps.PairValueRecord); st.PairSet.append(ps)
    st.PairSetCount = len(st.PairSet)
    lk = ot.Lookup(); lk.LookupType = 2; lk.LookupFlag = 0; lk.SubTable = [st]; lk.SubTableCount = 1
    gpos.LookupList.Lookup.append(lk); gpos.LookupList.LookupCount = len(gpos.LookupList.Lookup)
    i = gpos.LookupList.LookupCount - 1
    for fr in gpos.FeatureList.FeatureRecord:
        if fr.FeatureTag == 'kern': fr.Feature.LookupListIndex.append(i); fr.Feature.LookupCount = len(fr.Feature.LookupListIndex)
    t.save(chemin)
    pire = sorted(besoin.items(), key=lambda kv: -kv[1])[:6]
    print(chemin.split('/')[-1], len(besoin), 'paires écartées, les plus fortes :', pire)

for p in sys.argv[1:]: traite(p)
