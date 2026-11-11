# Crénage automatique par profils, écrit dans la police (GPOS kern, par classes : une lettre + ses accents)
import sys, os, math, unicodedata as ud
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString

import geo_kshim as core
CAP = core.CAP
class Segs(BasePen):
    def __init__(s): super().__init__(None); s.segs = []; s.cur = None; s.st = None
    def _moveTo(s, p): s.cur = p; s.st = p
    def _lineTo(s, p): s.segs.append((s.cur, p)); s.cur = p
    def _curveToOne(s, a, b, c):
        p0 = s.cur
        for i in range(1, 9):
            t = i / 8; m = 1 - t
            q = tuple(m**3*p0[j] + 3*m*m*t*a[j] + 3*m*t*t*b[j] + t**3*c[j] for j in (0, 1)); s.segs.append((s.cur, q)); s.cur = q
    def _qCurveToOne(s, a, b): s.segs.append((s.cur, b)); s.cur = b
    def _closePath(s):
        if s.cur != s.st: s.segs.append((s.cur, s.st))

BASES = list('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789') + \
        ['period', 'comma', 'colon', 'semicolon', 'exclam', 'question', 'hyphen', 'endash', 'emdash', 'quotesingle', 'quotedbl',
         'quoteright', 'quoteleft', 'quotedblright', 'quotedblleft', 'guillemotleft', 'guillemotright', 'guilsinglleft',
         'guilsinglright', 'parenleft', 'parenright', 'bracketleft', 'bracketright', 'slash', 'ampersand', 'quotesinglbase',
         'quotedblbase', 'ellipsis', 'AE', 'OE', 'Oslash', 'Lslash', 'Eth', 'Thorn', 'ae', 'oe', 'oslash', 'germandbls',
         'eth', 'thorn', 'lslash', 'uni1E9E', 'question_exclam', 'exclam_question', 'uni203C', 'uni203D', 'uni2665', 'w_t_f']
NAME = {c: c for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'}
NAME.update({'0': 'zero', '1': 'one', '2': 'two', '3': 'three', '4': 'four', '5': 'five', '6': 'six', '7': 'seven', '8': 'eight', '9': 'nine'})

def classes(f):
    order = set(f.getGlyphOrder()); members = {NAME.get(b, b): [NAME.get(b, b)] for b in BASES if NAME.get(b, b) in order}
    for g in order:
        if g.startswith('uni') and len(g) == 7:
            try: ch = chr(int(g[3:], 16))
            except ValueError: continue
            n = ud.normalize('NFD', ch)
            if len(n) > 1 and n[0] in NAME and NAME[n[0]] in members: members[NAME[n[0]]].append(g)
    if 'i' in members and 'dotlessi' in order: members['i'].append('dotlessi')
    for b_, alt in (('a', '.ss01'), ('g', '.ss02')):           # variantes : même classe que la lettre de base
        if b_ in members: members[b_] += [g for g in order if g.endswith(alt) and (g == b_ + alt or g.startswith('uni'))]
    if 'j' in members and 'uni0237' in order: members['j'].append('uni0237')
    if 'D' in members and 'Dcroat' in order: members['D'].append('Dcroat')
    if 'i' in members and 'i.coeur' in order: members['i'].append('i.coeur')
    if 'j' in members and 'j.coeur' in order: members['j'].append('j.coeur')
    for c, ms in members.items():                 # les prises 1 et 2 suivent leur lettre
        members[c] = ms + [m + t for m in ms for t in ('.t1', '.t2') if m + t in order]
    return members

def profile(gs, g, cache):
    if g in cache: return cache[g]
    p = Segs(); gs[g].draw(p); L = {}; R = {}
    for y in range(-240, 1100, 10):
        xs = []
        for (x0, a), (x1, b) in p.segs:
            if (a <= y < b) or (b <= y < a): xs.append(x0 + (y - a) * (x1 - x0) / (b - a))
        if xs: L[y] = min(xs); R[y] = max(xs)
    cache[g] = (L, R); return L, R

def zone(g):
    lower = len(g) == 1 and g.islower() or g in ('ae', 'oe', 'oslash', 'germandbls', 'eth', 'thorn', 'lslash', 'w_t_f')
    return (0, core.XH) if lower else (0, CAP)

NOTL = {'period', 'comma', 'colon', 'semicolon', 'exclam', 'question', 'hyphen', 'endash', 'emdash', 'quotesingle', 'quotedbl',
        'quoteright', 'quoteleft', 'quotedblright', 'quotedblleft', 'guillemotleft', 'guillemotright', 'guilsinglleft', 'guilsinglright',
        'parenleft', 'parenright', 'bracketleft', 'bracketright', 'slash', 'ampersand', 'quotesinglbase', 'quotedblbase', 'ellipsis'}
QUOTES = {'quotesingle', 'quotedbl', 'quoteright', 'quoteleft', 'quotedblright', 'quotedblleft'}

def kern_font(path, out=None, extra='', targets=()):
    """mesure le crénage sur path (police pleine) ; l'écrit dans path et dans chaque cible (chemin, seulement_négatif)"""
    f = TTFont(path); gs = f.getGlyphSet(); hm = f['hmtx']; cache = {}
    V = hm['I'][0] - 2 * hm['I'][1]                 # épaisseur du fût (I = un fût)
    mem = classes(f); bases = list(mem)
    depth = 170
    def touch(a, b):
        """plus petit écart entre a et b, toutes prises voisines confondues (0→1, 1→2, 2→0)"""
        mn = 1e9
        for ta, tb in (('', '.t1'), ('.t1', '.t2'), ('.t2', ''), ('', '')):
            ga, gb = a + ta, b + tb
            if ga not in hm.metrics or gb not in hm.metrics: ga, gb = a, b
            La, Ra = profile(gs, ga, cache); Lb, Rb = profile(gs, gb, cache); adv = hm[ga][0]
            for y in range(-240, 1100, 10):
                ra = Ra.get(y); lb = Lb.get(y)
                if ra is not None and lb is not None: mn = min(mn, adv - ra + lb)
        return mn
    def gap(a, b):
        za, zb = zone(a), zone(b); y0, y1 = 0, min(za[1], zb[1])
        La, Ra = profile(gs, a, cache); Lb, Rb = profile(gs, b, cache); adv = hm[a][0]
        vals = []; mn = 1e9
        for y in range(y0, y1, 10):
            ra = Ra.get(y); lb = Lb.get(y)
            left = (adv - ra) if ra is not None else depth * 2
            right = lb if lb is not None else depth * 2
            vals.append(min(left + right, depth * 2))
        mn = touch(a, b)                                   # le contact se vérifie sur toute la hauteur et pour chaque prise
        if a in QUOTES or b in QUOTES:                    # apostrophes et guillemets : jamais au-dessus de la lettre voisine
            if Ra and Lb: mn = min(mn, adv - max(Ra.values()) + min(Lb.values()))
        return (sum(vals) / len(vals) if vals else 0), mn
    ref_c = gap('H', 'H')[0]; ref_l = gap('n', 'n')[0]
    pairs = {}
    DIG = {'zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine'}
    for a in bases:
        for b in bases:
            if a in DIG or b in DIG: continue          # chiffres tabulaires : jamais de crénage (les colonnes restent alignées)
            ca = a[0].isupper() if len(a) == 1 else False
            cb = b[0].isupper() if len(b) == 1 else False
            ref = ref_c if (ca and cb) else ref_l
            avg, mn = gap(a, b)
            k = (ref - avg) * 0.55
            k = max(-round(CAP * 0.22), min(round(CAP * 0.06), k))
            if not (a[0].isalnum() and len(a) <= 7 and b[0].isalnum() and len(b) <= 7) or a in NOTL or b in NOTL:
                k = max(k, -10)                               # la ponctuation ne se colle jamais aux lettres
            gmin = round(core.ST * 0.22 + 16)                # jamais de contact, même quand deux prises penchent l'une vers l'autre
            if mn + k < gmin: k = gmin - mn
            k = round(k / 5) * 5
            if abs(k) >= 15: pairs[(a, b)] = k
    fea = []
    for c, ms in mem.items():
        fea.append(f"@K_{c} = [{' '.join(ms)}];")
    # la traîne déborde dans l'espace : quand une ponctuation la suit directement, on l'écarte juste assez
    PONCT = [p for p in ('period', 'comma', 'colon', 'semicolon', 'exclam', 'question', 'parenright', 'bracketright', 'braceright',
                         'quoteright', 'quotedblright', 'quotesingle', 'quotedbl', 'guillemotright', 'guilsinglright', 'ellipsis',
                         'emdash', 'asterisk') if p in hm.metrics]
    qpairs = []
    for q in [g for g in f.getGlyphOrder() if g.endswith('.q')]:
        Lq, Rq = profile(gs, q, cache); adv = hm[q][0]
        for p in PONCT:
            Lp, Rp = profile(gs, p, cache); mn = 1e9
            for y in range(-240, 1100, 10):
                if y in Rq and y in Lp: mn = min(mn, adv - Rq[y] + Lp[y])
            need = round(core.ST * 0.3 + 24)
            if mn < need: qpairs.append((q, p, int(math.ceil((need - mn) / 5) * 5)))
    fea.append(extra)
    fea.append("feature kern {")
    for q, p, v in qpairs: fea.append(f"  pos {q} {p} {v};")
    for (a, b), k in pairs.items():
        fea.append(f"  pos @K_{a} @K_{b} {k};")
    fea.append("} kern;")
    addOpenTypeFeaturesFromString(f, '\n'.join(fea), tables=['GPOS'])
    f.save(out or path)
    for tp, nonpos in targets:
        t = TTFont(tp); fe = list(fea)
        if nonpos:                                   # filets de construction : on ne desserre jamais (les lignes restent continues)
            fe = [l if not l.strip().startswith('pos ') or int(l.strip().rstrip(';').split()[-1]) <= 0 else '' for l in fe]
        addOpenTypeFeaturesFromString(t, '\n'.join(fe), tables=['GPOS']); t.save(tp)
    return len(pairs)


