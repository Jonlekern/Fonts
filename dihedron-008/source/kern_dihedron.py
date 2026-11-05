"""Crénage de DIHEDRON-008 : pour chaque paire de lettres, on mesure le blanc entre les deux formes
(ligne par ligne, sans aller trop loin dans les creux) et on rapproche les paires trop ouvertes
(AV, LT, To…) vers le blanc de référence (HH pour les capitales, nn pour les minuscules).
Garde un écart minimal pour que rien ne se touche. Les lettres accentuées suivent leur lettre de base.
usage : kern_dihedron.py police.ttf sortie.ttf"""
import sys, unicodedata
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString

H, XH = 700, 490
STEP = 10
FACTOR, DEPTH, MAXK = 0.65, 0.22, 0.30        # part de l'écart corrigée, profondeur des creux, crénage max (× hauteur capitale)
LEFT = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
PUNCT = '.,'

class Flat(BasePen):
    def __init__(self, gs): super().__init__(gs); self.c = []; self.cur = []
    def _moveTo(self, p): self.cur = [p]
    def _lineTo(self, p): self.cur.append(p)
    def _qCurveToOne(self, p1, p2):
        p0 = self.cur[-1]
        for i in range(1, 9):
            t = i / 8; self.cur.append(tuple((1-t)**2*p0[j] + 2*(1-t)*t*p1[j] + t*t*p2[j] for j in (0, 1)))
    def _curveToOne(self, p1, p2, p3):
        p0 = self.cur[-1]
        for i in range(1, 9):
            t = i / 8; m = 1 - t; self.cur.append(tuple(m**3*p0[j] + 3*m*m*t*p1[j] + 3*m*t*t*p2[j] + t**3*p3[j] for j in (0, 1)))
    def _closePath(self):
        if self.cur: self.c.append(self.cur); self.cur = []
    _endPath = _closePath

def profile(gs, n):
    fp = Flat(gs); gs[n].draw(fp)
    edges = [(c[i], c[(i + 1) % len(c)]) for c in fp.c for i in range(len(c))]
    prof = {}
    for y in range(-300, 900, STEP):
        yy = y + STEP / 2
        xs = [x0 + (yy - y0) * (x1 - x0) / (y1 - y0) for (x0, y0), (x1, y1) in edges if (y0 <= yy < y1) or (y1 <= yy < y0)]
        if xs: prof[y] = (min(xs), max(xs))
    return prof

def measure(pl, adv, pr):
    rows = [y for y in pl if y in pr]
    if not rows: return None
    rmax = max(pl[y][1] for y in rows); lmin = min(pr[y][0] for y in rows)
    top = max(rows); bot = min(rows); depth = DEPTH * H
    gaps = [(adv + min(pr[y][0], lmin + depth)) - max(pl[y][1], rmax - depth) for y in rows]
    raw = [adv + pr[y][0] - pl[y][1] for y in rows]
    return sum(gaps) / len(gaps), min(raw), top - bot

def kerning(f):
    gs = f.getGlyphSet(); cm = f.getBestCmap(); hm = f['hmtx']
    names = {ch: cm[ord(ch)] for ch in LEFT + PUNCT if ord(ch) in cm}
    prof = {ch: profile(gs, n) for ch, n in names.items()}
    adv = {ch: hm[n][0] for ch, n in names.items()}
    ref_cap = measure(prof['H'], adv['H'], prof['H'])[0]
    ref_low = measure(prof['n'], adv['n'], prof['n'])[0]
    stem = ref_cap / 2
    min_gap = 0.45 * ref_cap                         # écart minimal entre deux formes
    out = {}
    for a in LEFT:
        for b in LEFT + PUNCT:
            m = measure(prof[a], adv[a], prof[b])
            if not m: continue
            mean, mn, band = m
            ref = ref_cap if (a.isupper() and b.isupper()) else ref_low
            k = min(0, FACTOR * (ref - mean))
            k = max(k, -MAXK * H, min_gap - mn) if b not in PUNCT else max(k, -MAXK * H, 0.25 * ref_cap - mn)
            k = round(k / 5) * 5
            if abs(k) >= 15: out[(a, b)] = k
    return out, names

def groups(f, names):
    """lettre de base -> glyphes (la lettre + ses accentuées)"""
    rev = {v: k for k, v in f.getBestCmap().items()}; g = {ch: [n] for ch, n in names.items()}
    for n in f.getGlyphOrder():
        u = rev.get(n)
        if not u: continue
        base = unicodedata.normalize('NFD', chr(u))[0]
        if base in g and chr(u) != base and n not in g[base]: g[base].append(n)
    return g

def apply(f, pairs, names):
    gr = groups(f, names)
    fea = []
    for ch, gl in gr.items():
        fea.append(f'@L_{ord(ch)} = [{" ".join(gl)}];'); fea.append(f'@R_{ord(ch)} = [{" ".join(gl)}];')
    fea.append('feature kern {')
    for (a, b), k in sorted(pairs.items()): fea.append(f'  pos @L_{ord(a)} @R_{ord(b)} {k};')
    fea.append('} kern;')
    addOpenTypeFeaturesFromString(f, '\n'.join(fea))

if __name__ == '__main__':
    f = TTFont(sys.argv[1]); pairs, names = kerning(f); apply(f, pairs, names); f.save(sys.argv[2])
    print(sys.argv[1].split('/')[-1], len(pairs), 'paires', {k: v for k, v in sorted(pairs.items(), key=lambda t: t[1])[:12]})
