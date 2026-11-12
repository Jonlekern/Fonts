# LAMINAR : lettres en plus, accents, lettres accentuées (capitales et petites capitales)
import json, os, unicodedata as ud
from lam_core import *
from lam_letters import rcorner
from lam_digits import hbowl
from lam_signs import drop

def extras(c, G):
    """Æ Œ Ø Ð Đ Þ Ł Ħ ẞ pour une hauteur donnée (G : les 26 lettres de cette hauteur)"""
    H, S, h, W = c.H, c.S, c.h, c.W; E = {}; rr = round(0.85 * S); tm = round(0.48 * S + 6)
    # Æ : jambe déliée du A, barre, E
    Eg = G['E'].ink; xa = round(0.46 * W + 0.1 * S); wl = hw(h, xa, H)
    leg = diag(0, xa, wl, 0, H); ya = round(0.60 * H) if not c.sc else round(0.58 * H)
    hull = poly([(0, 0), (xa + 2, 0), (xa + 2, H), (xa, H)])
    E['AE'] = Gl(U(leg, mv(Eg, xa), I(rect(0, ya - h / 2, xa + 2, ya + h / 2), hull)), sides='DO')
    # Œ : le fût du E remplace le délié du O
    O = G['O']; R = O.x1 / 2
    E['OE'] = Gl(U(O.ink, mv(Eg, 2 * R - S)), 0, 2 * R - S + G['E'].x1, sides='OO')
    # Ø
    ob = bounds(O.ink); sl = I(stroke((ob[0] + 0.12 * R, ob[1] - 0.04 * H), (ob[2] - 0.12 * R, ob[3] + 0.04 * H), tm), rect(-100, ob[1] - 0.04 * H, 3000, ob[3] + 0.04 * H))
    E['Oslash'] = Gl(U(O.ink, sl), 0, O.x1, sides='OO')
    # Ð Đ
    db = round(0.10 * H); Dg = G['D']
    dbar = rect(0, H / 2 - tm / 2, db + S + round(0.12 * H), H / 2 + tm / 2)
    E['Eth'] = E['Dcroat'] = Gl(U(mv(Dg.ink, db), dbar), 0, Dg.x1 + db, sides='SO')
    # Þ
    y0, y1 = round(0.18 * H), round(0.82 * H); rp = (y1 - y0) / 2; pw = round(0.94 * W); xp = pw - rp
    th_ = U(rect(0, 0, S, H), rect(0, y1 - h, xp + 1, y1), rect(0, y0, xp + 1, y0 + h), hbowl(xp, y0, y1, S, h))
    E['Thorn'] = Gl(th_, 0, pw, sides='SO')
    # Ł
    lb = round(0.10 * H); Lg = G['L']
    lsl = I(stroke((0, 0.32 * H), (2 * lb + S, 0.60 * H), tm), rect(-50, 0, 2 * lb + S + 50, H))
    E['Lslash'] = Gl(U(mv(Lg.ink, lb), lsl), 0, Lg.x1 + lb, sides='SO')
    # Ħ
    hb = round(0.06 * H); Hg = G['H']; yb = round(0.80 * H)
    E['Hbar'] = Gl(U(mv(Hg.ink, hb), rect(0, yb, Hg.x1 + 2 * hb, yb + h * 1.5)), 0, Hg.x1 + 2 * hb, sides='SS')
    # ẞ : fût, tête, oblique déliée, panse basse
    tw = round(0.62 * W); ym = round(0.56 * H); rL = (ym + h / 2) / 2; bw = round(0.96 * W); xl = bw - rL
    wd = hw(h, tw - (xl - 0.05 * W), H - ym)
    dg = I(diag(xl - 0.05 * W, tw - wd, wd, ym - h / 2, H), rect(-10, ym - h / 2, 3000, H))
    ss = U(rect(0, 0, S, H), rect(0, H - h, tw, H), dg, rect(xl - 0.05 * W, ym - h / 2, xl + 1, ym + h / 2), hbowl(xl, 0, ym + h / 2, round(1.06 * S), h),
           rect(S + round(0.12 * W), 0, xl + 1, h))
    E['uni1E9E'] = Gl(rcorner(ss, 0, H, rr, 'tl'), 0, bw, sides='SO')
    return E

def marks(c):
    """accents centrés en x = 0, posés sur y = 0 (dessus) ou pendus sous 0 (dessous)"""
    S, h = c.S, c.h; k = c.H / CAP; M = {}
    t = round(0.52 * S + 6); ah = round((120 + 0.25 * S) * (0.82 if c.sc else 1.0)); aw = round(0.55 * ah + 0.3 * t)
    wa = hw(t, aw, ah)
    ac = diag(-aw / 2 - wa / 2, aw / 2 - wa / 2, wa, 0, ah)
    M['acute'] = ac; M['grave'] = mirror(ac, 0)
    M['hungarumlaut'] = U(mv(ac, -0.55 * aw - 0.4 * wa), mv(ac, 0.55 * aw + 0.4 * wa))
    cw = round(0.30 * c.W + 0.2 * S); chh = round(0.82 * ah); tc = round(0.42 * S + 6); wv = hw(tc, cw / 2, chh)
    cf = U(diag(-cw / 2, -wv / 2, wv, 0, chh), diag(cw / 2 - wv, -wv / 2, wv, 0, chh))
    cf = I(cf, rect(-cw, -10, cw, chh - 0.35 * tc))
    M['circumflex'] = cf; M['caron'] = flipv(cf, (chh - 0.35 * tc) / 2)
    rd = round(0.42 * S + 12) * (0.9 if c.sc else 1.0); gap = round(0.9 * rd + 0.12 * c.W)
    M['dieresis'] = U(circ(-rd - gap / 2, rd, rd), circ(rd + gap / 2, rd, rd)); M['dotaccent'] = circ(0, rd, rd)
    rr = round(0.10 * c.H + 0.2 * S); M['ring'] = ring_off(0, rr, rr, round(0.42 * S + 6), h, -1)
    mw = round(0.24 * c.W + 0.25 * S); M['macron'] = rect(-mw, 0, mw, round(1.8 * h + 0.1 * S))
    rb = round(0.18 * c.W + 0.2 * S); M['breve'] = I(ring_off(0, rb, rb, round(0.42 * S + 6), h, 1) if False else D(circ(0, rb, rb), ell(0, rb, rb - round(0.42 * S + 6), rb - h * 1.2)), rect(-2000, 0, 2000, rb * 0.62))
    rt = round(0.10 * c.W + 0.15 * S); tt = round(0.42 * S + 6)
    til = U(I(D(circ(rt, 0, rt), circ(rt, 0, rt - tt)), rect(-1000, 0, 1000, 1000)), I(D(circ(3 * rt - tt, 0, rt), circ(3 * rt - tt, 0, rt - tt)), rect(-1000, -1000, 1000, 0)))
    tb = bounds(til); M['tilde'] = mv(til, -(tb[0] + tb[2]) / 2, -tb[1])
    # dessous
    rc = round(0.42 * S + 10); cm = drop(0, -rc - 40, rc, (-0.5 * rc, -2.6 * rc - 60)); M['commabelow'] = cm
    tc_ = round(0.40 * S + 6); rce = round(0.07 * CAP + 0.2 * S)
    y1c = round(0.06 * CAP); rcd = round(0.07 * CAP + 0.15 * S)
    hk = I(D(circ(0, -y1c - rcd, rcd), ell(0, -y1c - rcd, rcd - tc_, rcd - h)), rect(0, -1000, 1000, 1000))
    M['cedilla'] = U(rect(-tc_ / 2, -y1c - h, tc_ / 2, 12), hk, rect(-round(0.8 * rcd), -y1c - 2 * rcd, 1, -y1c - 2 * rcd + h))
    ro = round(0.09 * CAP + 0.2 * S); to = round(0.40 * S + 6)
    M['ogonek'] = U(rect(-to / 2, -round(0.05 * CAP), to / 2, 12), I(D(circ(-to / 2 + ro, -round(0.05 * CAP), ro), ell(-to / 2 + ro, -round(0.05 * CAP), ro - to, ro - h * 1.3)), rect(-1000, -1000, -to / 2 + ro, -round(0.05 * CAP))))
    return M

MARK_OF = {0x300: 'grave', 0x301: 'acute', 0x302: 'circumflex', 0x303: 'tilde', 0x304: 'macron', 0x306: 'breve',
           0x307: 'dotaccent', 0x308: 'dieresis', 0x30A: 'ring', 0x30B: 'hungarumlaut', 0x30C: 'caron',
           0x326: 'commabelow', 0x327: 'cedilla', 0x328: 'ogonek'}
SPACING = {'grave': 0x60, 'acute': 0xB4, 'dieresis': 0xA8, 'macron': 0xAF, 'cedilla': 0xB8, 'circumflex': 0x2C6, 'caron': 0x2C7,
           'breve': 0x2D8, 'dotaccent': 0x2D9, 'ring': 0x2DA, 'ogonek': 0x2DB, 'tilde': 0x2DC, 'hungarumlaut': 0x2DD}
LOWER_EXTRA = {'ae': 'AE', 'oe': 'OE', 'oslash': 'Oslash', 'eth': 'Eth', 'dcroat': 'Dcroat', 'thorn': 'Thorn', 'lslash': 'Lslash',
               'hbar': 'Hbar', 'germandbls': 'uni1E9E', 'dotlessi': 'I', 'uni0237': 'J'}

GAP_UP, GAP_SC = round(0.08 * CAP), round(0.07 * CAP)
def mark_x(B, g, c):
    b = bounds(g.ink); cx = (b[0] + b[2]) / 2
    if B in ('D', 'B', 'P', 'R'): cx = c.S / 2 + (b[2] - c.S / 2) * 0.46
    if B in ('L', 'E', 'F'): cx = (c.S + b[2]) / 2 * 0.86
    if B == 'U': cx = b[2] / 2
    return cx

def accented(cc, cs, Gc, Gs, apos):
    """Gc, Gs : capitales et petites capitales (avec les lettres en plus) ; apos : apostrophe (encre)"""
    Mc, Ms = marks(cc), marks(cs); A = {}
    comps = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'composites.json')))
    for cp in comps:
        ch = chr(cp); dec = ud.normalize('NFD', ch); base = dec[0]; mk = [ord(m) for m in dec[1:]]
        up = base.isupper(); c = cc if up else cs; G = Gc if up else Gs; M = Mc if up else Ms
        g = G[base.upper()]; ink = g.ink; b = bounds(ink); x1 = g.x1
        cx = mark_x(base.upper(), g, c); ytop = c.H; gap = GAP_UP if up else GAP_SC
        B = base.upper()
        for m in mk:
            n = MARK_OF[m]
            if m == 0x30C and B in 'L' or (m == 0x30C and B == 'D' and False):
                a = xf(apos, (0.85 if up else 0.7, 0, 0, 0.85 if up else 0.7, 0, 0)); ab = bounds(a)
                xr = c.S + round(0.07 * CAP); ink = U(ink, mv(a, xr - ab[0], c.H - ab[3])); x1 = max(x1, xr + ab[2] - ab[0]); continue
            mi = M[n]; mb = bounds(mi)
            if m in (0x326, 0x327):
                xb = cx
                if B in 'KLNR': xb = c.S / 2
                if m == 0x327 and B in 'GKLNR': mi = M['commabelow']
                ink = U(ink, mv(mi, xb, 0)); continue
            if m == 0x328:
                if B == 'A': xa = b[2] - 0.16 * (b[2] - b[0])
                elif B == 'E': xa = b[2] - 0.30 * (b[2] - b[0])
                elif B == 'U': xa = c.S / 2
                elif B == 'I': xa = c.S / 2
                else: xa = cx
                ink = U(ink, mv(mi, xa, 0)); continue
            ink = U(ink, mv(mi, cx, ytop + gap - mb[1])); ytop = ytop + gap + (mb[3] - mb[1])
        A['uni%04X' % cp] = Gl(ink, g.x0, x1, g.sides)
    # accents seuls : espacement et combinants
    for n, sp in SPACING.items():
        mi = Mc[n]
        if n not in ('cedilla', 'ogonek'): mi = mv(mi, 0, round(0.80 * CAP))
        A['_sp_' + n] = Gl(mi, sides='OO')
    for cp, n in MARK_OF.items():                  # combinants : posés par la feature mark (ancre en 0, 0)
        A['uni%04X' % cp] = Gl(Ms[n], 0, 0, 'NN', adv=0)
    return A
