# Accents : coupés net, un poil plus fins que les lettres. Composition automatique des lettres accentuées (jeu GF Latin Core),
# accents seuls (´ ¨ ˇ …) et accents combinants (U+0300…).
import os, json, math, unicodedata as ud
from core import *
import lower, caps, signs

AT = round(ST * 0.86)                      # trait d'un accent (un peu plus fin que le fût)
def ah(cap): return round(92 + 0.25 * ST) if not cap else round(74 + 0.2 * ST)     # hauteur d'un accent
def GAP(cap): return round(46 + 0.14 * ST) if not cap else round(30 + 0.1 * ST)    # espace lettre / accent

def _norm(p):
    b = p.bounds; return mv(p, -(b[0] + b[2]) / 2, -b[1])

def m_acute(cap, s=1):
    h = ah(cap); w = round(h * 0.95)
    p = poly([(-w / 2 - AT * 0.36, 0), (-w / 2 + AT * 0.46, 0), (w / 2 + AT * 0.30, h), (w / 2 - AT * 0.42, h)])
    return _norm(p if s > 0 else flipx(p, 0))
def m_grave(cap): return m_acute(cap, -1)
def m_circ(cap, flip=False):
    h = round(ah(cap) * 0.82); w = round(h * 1.9)
    p = U(poly([(-w / 2, 0), (-w / 2 + AT * 1.05, 0), (AT * 0.45, h), (-AT * 0.45, h)]),
          poly([(w / 2 - AT * 1.05, 0), (w / 2, 0), (AT * 0.45, h), (-AT * 0.45, h)]))
    return _norm(flipy(p, h / 2) if flip else p)
def m_caron(cap): return m_circ(cap, True)
def m_dieresis(cap):
    r = round(ST * 0.52 + 4); g = round(r * 2 + 0.75 * ST)
    return _norm(U(dot(-g / 2, r, r), dot(g / 2, r, r)))
def m_dot(cap):
    r = round(ST * 0.52 + 4); return _norm(dot(0, r, r))
def m_tilde(cap):
    w = round(ah(cap) * 2.1); a = round(ah(cap) * 0.28); t = round(AT * 0.78); n = 30
    top = [(w * i / n - w / 2, a * math.sin(math.pi * 2 * i / n - math.pi) * -1 + t / 2) for i in range(n + 1)]
    bot = [(w * i / n - w / 2, a * math.sin(math.pi * 2 * i / n - math.pi) * -1 - t / 2) for i in range(n, -1, -1)]
    return _norm(poly(top + bot))
def m_ring(cap):
    r = round(ST * 0.78 + 16); return _norm(ring(0, r, r, r, sx=AT * 0.9, sy=round(TH * 0.72), r=0))
def m_macron(cap):
    w = round(ah(cap) * 2.0); return _norm(rect(-w / 2, 0, w / 2, round(TH * 0.9)))
def m_breve(cap):
    w = round(ah(cap) * 1.6); h = round(ah(cap) * 0.75)
    p = I(ring(0, h, w / 2, h, sx=AT * 0.95, sy=round(TH * 0.8), r=0), rect(-w, -5, w, h - 4))
    return _norm(p)
def m_hung(cap):
    a = m_acute(cap); b = a.bounds; g = round((b[2] - b[0]) * 0.55 + AT * 0.3)
    return _norm(U(mv(a, -g / 2), mv(a, g / 2)))
def m_commabelow(cap):
    p = signs.comma_shape(); return _norm(xf(p, (0.8, 0, 0, 0.8, 0, 0)))
def m_cedilla(cap):
    # un petit fût sous la lettre, puis une panse ouverte à gauche (comme le bas du 5)
    t = round(AT * 0.72); h = round(0.30 * XH); r = round(h * 0.52); cy = -h * 0.36 - r + 4
    s_ = rect(-t / 2, -h * 0.36, t / 2, 0)
    panse = I(ring(0, cy, r + t * 0.15, r, sx=t, sy=round(TH * 0.58), r=0), pie(0, cy, -165, 90))
    return U(s_, panse)

def m_ogonek(cap):
    # crochet ouvert à droite, accroché sous le pied droit de la lettre
    t = round(AT * 0.8); h = round(0.42 * XH); r = round(h * 0.52)
    p = I(ring(-r, -h + r, r + t * 0.2, r, sx=t, sy=round(TH * 0.6), r=0), pie(-r, -h + r, 90, 380))
    return p

MARK = {'́': m_acute, '̀': m_grave, '̂': m_circ, '̌': m_caron, '̈': m_dieresis, '̇': m_dot,
        '̃': m_tilde, '̊': m_ring, '̄': m_macron, '̆': m_breve, '̋': m_hung,
        '̦': m_commabelow, '̧': m_cedilla, '̨': m_ogonek}
ABOVE = set('́̀̂̌̈̇̃̊̄̆̋')

def gname(ch): return 'uni%04X' % ord(ch)

def base_glyph(b):
    if b == 'i': return GLYPHS['dotlessi']()
    if b == 'j': return GLYPHS['uni0237']()
    return GLYPHS[b]()

def zone_center(path, y0, y1):
    z = I(path, rect(-5000, y0, 5000, y1))
    b = z.bounds if z.bounds and z.bounds != (0, 0, 0, 0) else path.bounds
    return (b[0] + b[2]) / 2

def compose(ch):
    n = ud.normalize('NFD', ch); b, marks = n[0], n[1:]
    def fn():
        get = (lambda: base_glyph(b)) if any(c in ABOVE for c in marks) else (lambda: GLYPHS[b]())
        path, lsb, rsb = get()
        x0, y0, x1, y1 = path.bounds
        cap = b.isupper(); top = CAP if cap else XH
        tall = (not cap) and b in 'bdhklt'
        if tall: top = ASC if b != 't' else XH + 120
        cx = zone_center(path, 0, top if not tall else XH)
        if b in 'dl' and not cap: cx = zone_center(path, XH, ASC)
        if b == 't': cx = zone_center(path, 0, XH + 120)
        out_ = path; stack = 0; grow = False
        for m in marks:
            if m == '̌' and b in 'dlLt':                       # ď ľ Ľ ť : apostrophe à droite
                q = signs.comma_shape(); qb = q.bounds
                q = mv(q, x1 + 20 - qb[0], (CAP if b == 'L' else ASC) + 10 - qb[3])
                out_ = U(out_, q); grow = True; continue
            f = MARK[m]
            if m in ABOVE:
                mk = f(cap or tall); mb = mk.bounds
                yb = top + GAP(cap or tall) * (0.7 if tall else 1) + stack
                mk = mv(mk, cx, yb - mb[1]); stack += (mb[3] - mb[1]) + GAP(cap) * 0.5
                out_ = U(out_, mk)
            elif m == '̦' or (m == '̧' and b in 'gGkKlLnNrR'):
                mk = m_commabelow(cap); mb = mk.bounds
                if b == 'g':
                    mk = rot(mk, 180, 0, 0); mb = mk.bounds
                    out_ = U(out_, mv(mk, cx - (mb[0] + mb[2]) / 2, XH + GAP(False) - mb[1])); continue
                xc = zone_center(path, 0, 60)
                out_ = U(out_, mv(mk, xc - (mb[0] + mb[2]) / 2, -40 - mb[3]))
            elif m == '̧':
                xc = zone_center(path, 0, 50)
                out_ = U(out_, mv(m_cedilla(cap), xc, 0))
            elif m == '̨':
                mk = m_ogonek(cap); ax = x1 - ST * 0.5 if b not in 'iI' else x1
                out_ = U(out_, mv(mk, ax, 0))
        nb = out_.bounds
        if grow: return out_, lsb, rsb
        return out_, lsb - (x0 - nb[0]), rsb - (nb[2] - x1)
    return fn

def install():
    d = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'nexum', 'gf_core.json')))
    base = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'); done = []
    for cp in d:
        ch = chr(cp); n = ud.normalize('NFD', ch)
        if len(n) > 1 and n[0] in base and all(c in MARK for c in n[1:]):
            GLYPHS[gname(ch)] = compose(ch); UNI[gname(ch)] = ch; done.append(ch)
    return done

# accents seuls
def spacing(fn, below=False):
    def f():
        m = fn(False); b = m.bounds
        m = mv(m, -b[0], (0 if below else XH + GAP(False)) - (b[3] if below else b[1]))
        return out(m, 'T', 'T')
    return f
SPACING = {'acute': ('´', m_acute), 'grave': ('`', m_grave), 'circumflex': ('ˆ', m_circ), 'caron': ('ˇ', m_caron),
           'breve': ('˘', m_breve), 'dotaccent': ('˙', m_dot), 'ring': ('˚', m_ring), 'tilde': ('˜', m_tilde),
           'hungarumlaut': ('˝', m_hung), 'dieresis': ('¨', m_dieresis), 'macron': ('¯', m_macron)}
for nm, (ch, fn) in SPACING.items():
    GLYPHS[nm] = spacing(fn); UNI[nm] = ch
GLYPHS['cedilla'] = spacing(m_cedilla, True); UNI['cedilla'] = '¸'
GLYPHS['ogonek'] = spacing(m_ogonek, True); UNI['ogonek'] = '˛'

# accents combinants : largeur nulle, centrés sur la lettre qui précède
def combining(fn, above=True):
    def f():
        m = fn(False); b = m.bounds
        if above: m = mv(m, 0, XH + GAP(False) - b[1])
        b = m.bounds; iw = b[2] - b[0]
        half = round(NW / 2 + S_STEM)
        m = mv(m, -half - (b[0] + b[2]) / 2, 0); b = m.bounds
        return m, b[0], -b[0] - iw
    return f
COMB = {'0300': m_grave, '0301': m_acute, '0302': m_circ, '0303': m_tilde, '0304': m_macron, '0306': m_breve,
        '0307': m_dot, '0308': m_dieresis, '030A': m_ring, '030B': m_hung, '030C': m_caron}
BELOW = {'0326': m_commabelow, '0327': m_cedilla, '0328': m_ogonek}
for cp, fn in COMB.items():
    GLYPHS['uni' + cp] = combining(fn, True); UNI['uni' + cp] = chr(int(cp, 16))
for cp, fn in BELOW.items():
    GLYPHS['uni' + cp] = combining(fn, False); UNI['uni' + cp] = chr(int(cp, 16))

ACC_DONE = install()
