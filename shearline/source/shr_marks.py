# SHEARLINE : lettres en plus, accents (à la plume) et lettres accentuées
import json, os, unicodedata as ud
from shr_core import *
from shr_signs import diamond

def extras(w, Gl, Gc):
    s, k, yb, yt, pen = w.s, w.k, w.yb, w.yt, w.pen; st = pen.stroke; E = {}
    def join(a, b, gap):
        ba, bb = bounds(a), bounds(b); return U(a, mv(b, ba[2] - bb[0] + gap))
    E['ae'] = join(Gl['a'], Gl['e'], -0.32 * s); E['oe'] = join(Gl['o'], Gl['e'], -0.32 * s)
    E['AE'] = join(Gc['A'], Gc['E'], -0.30 * s); E['OE'] = join(Gc['O'], Gc['E'], -0.30 * s)
    for n, b, y0, y1 in (('oslash', Gl['o'], -0.05 * XH, 1.05 * XH), ('Oslash', Gc['O'], -0.04 * CAP, 1.04 * CAP)):
        bb = bounds(b); E[n] = U(b, st([(bb[0] - 0.05 * s, y0), (bb[2] + 0.05 * s, y1)]))
    bar = lambda x0, x1, y: st([(x0, y), (x1, y)])
    yd = ASC - 0.30 * (ASC - XH)
    d = Gl['d']; db = bounds(d); E['dcroat'] = U(d, bar(db[2] - 0.65 * s, db[2] + 0.1 * s, yd - 0.08 * (ASC - XH)))
    E['eth'] = E['dcroat']
    h = Gl['h']; E['hbar'] = U(h, bar(-0.35 * s, 0.4 * s, yd - 0.06 * (ASC - XH)))
    l = Gl['l']; E['lslash'] = U(l, st([(-0.35 * s, 0.45 * XH), (0.35 * s, 0.8 * XH)]))
    p = Gl['p']; E['thorn'] = U(p, st([(0, w.ya - 0.3 * s), (0, yt)]), st([(-k, w.ya), (0, w.ya - 1.2 * k)]))
    E['dotlessi'] = Gl['dotlessi']; E['uni0237'] = Gl['uni0237']
    Dg = Gc['D']; E['Eth'] = U(Dg, bar(-0.3 * s, 0.45 * s, 0.45 * CAP)); E['Dcroat'] = E['Eth']
    Hg = Gc['H']; E['Hbar'] = U(Hg, bar(-0.25 * s, 1.4 * s, 0.8 * CAP))
    Lg = Gc['L']; E['Lslash'] = U(Lg, st([(-0.3 * s, 0.32 * CAP), (0.55 * s, 0.6 * CAP)]))
    return E

def marks(w, cap=False):
    s, k, pen = w.s, w.k, w.pen; st = pen.stroke; M = {}
    kk = 0.8 if cap else 1.0; h = 0.32 * s * kk
    M['acute'] = st([(-0.12 * s, 0), (0.12 * s, h)])
    M['grave'] = st([(0.12 * s, 0), (-0.12 * s, h)])
    M['hungarumlaut'] = U(mv(M['acute'], -0.16 * s), mv(M['acute'], 0.16 * s))
    M['circumflex'] = st([(-0.28 * s, 0), (0, h), (0.28 * s, 0)])
    M['caron'] = st([(-0.28 * s, h), (0, 0), (0.28 * s, h)])
    M['dieresis'] = U(diamond(pen, -0.22 * s, 0.35 * h, 1.3 * k), diamond(pen, 0.22 * s, 0.35 * h, 1.3 * k))
    M['dotaccent'] = diamond(pen, 0, 0.35 * h, 1.3 * k)
    r = 0.16 * s
    M['ring'] = st([(0, 2 * r), (-0.8 * r, 1.1 * r), (0, 0), (0.8 * r, 0.9 * r), (0, 2 * r)])
    M['macron'] = st([(-0.28 * s, 0), (0.28 * s, 0.04 * s)])
    M['breve'] = st([(-0.28 * s, h), (-0.12 * s, 0.1 * h), (0.12 * s, 0.1 * h), (0.28 * s, h)])
    M['tilde'] = st([(-0.3 * s, 0.1 * h), (-0.1 * s, h), (0.1 * s, 0.2 * h), (0.3 * s, h)])
    M['commabelow'] = st([(0.05 * k, -0.25 * s), (0.1 * k, -0.45 * s), (-0.4 * k, -0.85 * s)])
    M['cedilla'] = st([(0, 0.05 * s), (0.05 * s, -0.25 * s), (0.25 * s, -0.4 * s), (-0.2 * s, -0.65 * s)])
    M['ogonek'] = st([(0, 0.05 * s), (-0.15 * s, -0.35 * s), (0.2 * s, -0.6 * s)])
    for n in M:                                          # chaque accent posé sur y = 0 (dessus) ou pendu sous 0 (dessous)
        if n in ('commabelow', 'cedilla', 'ogonek'): continue
        b = bounds(M[n]); M[n] = mv(M[n], 0, -b[1])
    return M

MARK_OF = {0x300: 'grave', 0x301: 'acute', 0x302: 'circumflex', 0x303: 'tilde', 0x304: 'macron', 0x306: 'breve',
           0x307: 'dotaccent', 0x308: 'dieresis', 0x30A: 'ring', 0x30B: 'hungarumlaut', 0x30C: 'caron',
           0x326: 'commabelow', 0x327: 'cedilla', 0x328: 'ogonek'}
SPACING = {'grave': 0x60, 'acute': 0xB4, 'dieresis': 0xA8, 'macron': 0xAF, 'cedilla': 0xB8, 'circumflex': 0x2C6, 'caron': 0x2C7,
           'breve': 0x2D8, 'dotaccent': 0x2D9, 'ring': 0x2DA, 'ogonek': 0x2DB, 'tilde': 0x2DC, 'hungarumlaut': 0x2DD}
GAP_L, GAP_C = 0.10 * XH, 0.07 * CAP
ASCL = set('bdhkl')

def mark_x(name, g, w):
    """axe des accents : le milieu de l'encre, sauf lettres à hampe ou à queue"""
    b = bounds(g); cx = 0.5 * (b[0] + b[2])
    if name in ('a', 'g', 'q', 'd'): cx = 0.5 * w.s
    if name in ('h', 'n', 'm', 'u', 'r', 'k', 'b', 'p'): cx = 0.5 * w.s if name != 'm' else w.s
    if name in ('i', 'j', 'dotlessi', 'uni0237', 'l', 't'): cx = 0.0
    return cx

def top_of(name, g, cap):
    if cap: return CAP
    if name in ASCL: return ASC
    if name == 't': return XH + 0.55 * (ASC - XH)
    return XH

def accented(w, G, apos):
    Ml, Mc = marks(w), marks(w, True); A = {}
    comps = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'composites.json')))
    for cp in comps:
        ch = chr(cp); dec = ud.normalize('NFD', ch); base = dec[0]; mk = [ord(m) for m in dec[1:]]
        cap = base.isupper(); M = Mc if cap else Ml
        bn = base
        if base == 'i' and any(m not in (0x326, 0x327, 0x328) for m in mk): bn = 'dotlessi'
        if base == 'j' and mk: bn = 'uni0237'
        g = G[bn]; ink = g; cx = mark_x(bn if not cap else base, g, w) if not cap else 0.5 * (bounds(g)[0] + bounds(g)[2])
        ytop = top_of(bn, g, cap) + (GAP_C if cap else GAP_L)
        for m in mk:
            n = MARK_OF[m]
            if m == 0x30C and base in 'dlLt':                     # ď ľ Ľ ť : apostrophe
                a = apos; ab = bounds(a); gb = bounds(g)
                xr = gb[2] + 0.05 * w.s if base in 'dt' else 0.45 * w.s
                yr = (ASC if base in 'dl' else (CAP if base == 'L' else XH + 0.55 * (ASC - XH)))
                ink = U(ink, mv(a, xr - ab[0], yr - ab[3])); continue
            mi = M[n]
            if m in (0x326, 0x327, 0x328):
                xb = cx
                if m == 0x328: xb = bounds(g)[2] - 0.25 * w.s
                if m == 0x327 and base in 'GKLNRgklnr': mi = M['commabelow']
                ink = U(ink, mv(mi, xb, 0)); continue
            mb = bounds(mi); ink = U(ink, mv(mi, cx, ytop - mb[1])); ytop += (mb[3] - mb[1]) + 0.05 * XH
        A['uni%04X' % cp] = ink
    for n, sp in SPACING.items():
        mi = Ml[n]
        if n not in ('cedilla', 'ogonek', 'commabelow'): mi = mv(mi, 0, XH + GAP_L)
        A['_sp_' + n] = mi
    for cp, n in MARK_OF.items(): A['uni%04X' % cp] = Ml[n]          # combinants : posés par la feature mark
    return A
