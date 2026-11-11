# Sans géométrique : lettres en plus, accents, lettres accentuées
import math, json, os, unicodedata as ud
from geo_core import *

def mv(p, dx, dy=0): return xf(p, (1, 0, 0, 1, dx, dy))
def shift(g, dx):
    """une lettre décalée (encre, coupes, centres)"""
    return mv(g.ink, dx), [mv(c, dx) for c in g.cuts], [(c[0] + dx,) + tuple(c[1:]) for c in g.centers], (g.alt and mv(g.alt, dx))
bar_ = rbar
def cross_cuts(piece, through, e):
    """jonction : le morceau « piece » s'arrête à e de part et d'autre du trait « through »"""
    return I(piece, D(dilate(through, e), through))
def dilate(p, e):
    """épaissit grossièrement un contour en l'unissant à ses copies décalées (8 directions)"""
    return U(p, *[mv(p, e * math.cos(math.radians(a)), e * math.sin(math.radians(a))) for a in range(0, 360, 30)])

def build_extras(w, G):
    ST, S, T, J, R = w.ST, w.STC, w.TDC, w.J, w.R
    e = 1.15 * J; Wd = w.W; cy = XH / 2; E = {}
    def gl(ink, cuts, centers, sides, x0=None, x1=None, alt=None, sbk=1.0):
        g = Gl(ink, cuts, centers, sides, x0, x1, alt); g.sbk = sbk; return g
    # ı ȷ
    E['dotlessi'] = gl(rect(0, 0, ST, XH), [], [], 'SS')
    j = G['j']; jb = j.ink
    E['uni0237'] = gl(D(jb, rect(-500, XH + 1, 500, 2000)), j.cuts, j.centers, 'SS', j.x0, j.x1)
    # æ œ : a + e et o + e qui partagent un trait
    for nm, a_, b_ in (('ae', 'a', 'e'), ('oe', 'o', 'e')):
        A_, Bg = G[a_], G[b_]; ink, cu, ce, al = shift(Bg, Wd - ST)
        if a_ == 'a':                                     # le rond du e ne dépasse pas du fût du a
            ink = I(ink, half((Wd - ST, 0), (Wd - ST, 1000), -1)); al = al if al is None else I(al, half((Wd - ST, 0), (Wd - ST, 1000), -1))
        alt = U(A_.alt if A_.alt is not None else A_.ink, al if al is not None else ink)
        E[nm] = gl(U(A_.ink, ink), A_.cuts + cu, A_.centers + ce, 'OO', 0, 2 * Wd - ST, alt=alt)
    # ø Ø : barre oblique qui traverse le rond
    for nm, base, h0, h1, t in (('oslash', 'o', -0.06 * XH, 1.06 * XH, round(0.82 * ST)), ('Oslash', 'O', -0.05 * CAP, 1.05 * CAP, round(0.82 * S))):
        g = G[base]; b = ubounds(g.ink)
        sl = bar_((b[0] + 0.10 * (b[2] - b[0]), h0), (b[2] - 0.10 * (b[2] - b[0]), h1), t)
        E[nm] = gl(U(g.ink, sl), g.cuts + [cross_cuts(g.ink, sl, e)], g.centers, 'OO', b[0], b[2], sbk=getattr(g, 'sbk', 1.0))
    # þ : p avec hampe
    p = G['p']; E['thorn'] = gl(U(p.ink, rect(0, 0, ST, ASC)), p.cuts, p.centers, 'SO')
    # ł Ł : barre oblique sur le fût
    lb = round(0.22 * Wd); tl = round(0.80 * ST)
    lsl = I(bar_((0, 0.32 * ASC), (2 * lb + ST, 0.62 * ASC), tl), rect(-50, 0, 2 * lb + ST + 50, ASC))
    lst = rect(lb, 0, lb + ST, ASC)
    E['lslash'] = gl(U(lst, lsl), [D(cross_cuts(lsl, lst, e), lst)], [], 'SS', 0, 2 * lb + ST)
    L_ = G['L']; lb2 = round(0.14 * CAP); Lsl = bar_((0, 0.30 * CAP), (2 * lb2 + S, 0.58 * CAP), round(0.8 * S))
    Lk, Lc, Lce, _ = shift(L_, lb2)
    E['Lslash'] = gl(U(Lk, Lsl), Lc + [D(cross_cuts(Lsl, rect(lb2, 0, lb2 + S, CAP), e), rect(lb2, 0, lb2 + S, CAP))], [], 'SS', 0, L_.x1 + lb2, sbk=1.3)
    # đ ħ : barre droite à travers le fût
    tb = round(0.75 * ST); yb = round(min(XH + 0.55 * (ASC - XH), ASC - 0.6 * tb - tb / 2) - tb / 2)
    d = G['d']; db = ubounds(d.ink); xs = Wd - ST
    dbar = rect(xs - 0.32 * Wd, yb, Wd + 0.12 * Wd, yb + tb); dst = rect(xs, 0, Wd, ASC)
    E['dcroat'] = gl(U(d.ink, dbar), d.cuts + [D(cross_cuts(dbar, dst, e), dst)], d.centers, 'OS', 0, Wd + 0.12 * Wd)
    h = G['h']; hb = round(0.16 * Wd)
    hk, hc, hce, hal = shift(h, hb)
    hbar = rect(0, yb, hb + ST + 0.30 * Wd, yb + tb); hst = rect(hb, 0, hb + ST, ASC)
    E['hbar'] = gl(U(hk, hbar), hc + [D(cross_cuts(hbar, hst, e), hst)], hce, 'SS', 0, hb + Wd)
    H_ = G['H']; hw = H_.x1; hb2 = round(0.08 * CAP); Hk, Hc, Hce, _ = shift(H_, hb2)
    Hbar = rect(0, 0.74 * CAP, hw + 2 * hb2, 0.74 * CAP + 0.75 * S)
    stems = U(rect(hb2, 0, hb2 + S, CAP), rect(hb2 + hw - S, 0, hb2 + hw, CAP))
    E['Hbar'] = gl(U(Hk, Hbar), Hc + [D(cross_cuts(Hbar, stems, e), stems)], [], 'SS', 0, hw + 2 * hb2, sbk=1.3)
    # Ð Đ
    Dg = G['D']; db2 = round(0.10 * CAP); Dk, Dc, Dce, _ = shift(Dg, db2)
    Dbar = rect(0, CAP / 2 - 0.38 * S, db2 + S + 0.16 * CAP, CAP / 2 + 0.38 * S); Dst = rect(db2, 0, db2 + S, CAP)
    for nm in ('Eth', 'Dcroat'):
        E[nm] = gl(U(Dk, Dbar), Dc + [D(cross_cuts(Dbar, Dst, e), Dst)], Dce, 'SO', 0, Dg.x1 + db2, sbk=1.3)
    # ð : rond + hampe au compas (arc d'un grand cercle qui prolonge le flanc droit), barrette
    o = G['o']; Rb = ASC - cy - 10; cxb = R - (Rb - R)
    hamp = D(arc(cxb, cy, Rb, ST, 0, 66), circ(R, cy, R - ST))
    yb_ = XH + 0.42 * (cy + Rb * math.sin(math.radians(66)) - XH); xb_ = cxb + math.sqrt(max(0, (Rb - ST / 2) ** 2 - (yb_ - cy) ** 2))
    ebar = rect(xb_ - 0.21 * Wd, yb_ - 0.38 * ST, xb_ + 0.19 * Wd, yb_ + 0.38 * ST)
    E['eth'] = gl(U(o.ink, hamp, ebar), [D(cross_cuts(ebar, hamp, e), hamp)], o.centers, 'OO', 0, max(Wd, xb_ + 0.19 * Wd))
    # Þ : fût + panse au milieu
    yb0, yb1 = round(0.17 * CAP), round(0.83 * CAP); rp = (yb1 - yb0) / 2; pw = round(0.56 * CAP + 0.4 * S); xc = pw - rp
    Tp = U(rect(0, 0, S, CAP), tbar(0, yb1 - S, xc, yb1, xc, yb0 + rp, rp), tbar(0, yb0, xc, yb0 + S, xc, yb0 + rp, rp), I(ring(xc, yb0 + rp, rp, S), vreal(xc, yb0 + rp, -1)))
    E['Thorn'] = gl(Tp, [rect(S, yb0 - 10, S + J, yb1 + 10)], [(xc, yb0 + rp, rp)], 'SO', sbk=1.3)
    # Æ Œ : un E accolé
    Eg = G['E']; ewd = Eg.x1
    Ag = G['A']; aw = Ag.x1
    xe = round(0.55 * aw); hA = fit_h(T, xe + S, CAP)
    diag = poly(para2(0, xe + S - hA, hA, 0, CAP))
    ya = round(0.17 * CAP); tb3 = round(0.85 * S)
    lA = pedges(para2(0, xe + S - hA, hA, 0, CAP))[1]
    abar = I(rect(0, ya, xe + 1, ya + tb3), half(lA[0], lA[1], -1))
    Ek, Ec, Ece, _ = shift(Eg, xe)
    E['AE'] = gl(U(diag, Ek, abar), Ec + [D(cross_cuts(abar, diag, e), diag)], [], 'DS', 0, xe + ewd, sbk=1.3)
    rq = CAP / 2; lo = U(I(ring(rq, rq, rq, S), vreal(rq, rq, 1)), tbarL(rq, 0, rq + S, S, rq, rq, rq), tbarL(rq, CAP - S, rq + S, CAP, rq, rq, rq))
    Ek2, Ec2, _, _ = shift(Eg, rq)
    Ek2 = I(Ek2, U(circ(rq, rq, rq), vreal(rq, rq, -1)))          # penché, le pied du E ne dépasse pas sous le rond
    E['OE'] = gl(U(lo, Ek2), Ec2 + [rect(rq - J, -10, rq, S + 10), rect(rq - J, CAP - S - 10, rq, CAP + 10)], [(rq, rq, rq)], 'OS', 0, rq + ewd, sbk=1.3)
    # ß : fût + arche + panse
    r1 = round(0.24 * Wd + 0.45 * ST); ya_ = ASC + OV - r1
    yt = round(0.60 * ASC); rb = yt / 2; xb2 = max(round(2 * r1 + 0.12 * Wd - rb), 2 * r1 - ST)
    foot = rect(2 * r1 - ST, yt - ST, 2 * r1, ya_ + 1)
    ss = U(rect(0, 0, ST, ya_ + 1), arc(r1, ya_, r1, ST, 0, 180), foot,
           tbar(min(2 * r1 - ST, xb2), yt - ST, max(2 * r1 - ST, xb2), yt, xb2, rb, rb), I(ring(xb2, rb, rb, ST), vreal(xb2, rb, -1)), tbar(ST + round(0.12 * Wd), 0, xb2, ST, xb2, rb, rb))
    E['germandbls'] = gl(ss, [rect(ST, ya_ - 1, ST + J, ASC + 60), rect(2 * r1 - ST - 10, ya_ - J, 2 * r1 + 10, ya_)], [(r1, ya_, r1), (xb2, rb, rb)], 'SO')
    # ẞ : fût, barre de tête, oblique, panse
    tw_ = round(0.52 * CAP + 0.3 * S); ym_ = round(0.56 * CAP); rb2 = ym_ / 2; xb3 = tw_ + round(0.06 * CAP) - rb2
    hd = fit_h(T, tw_ - (xb3 - 0.04 * CAP), CAP - ym_)
    dg = poly(para2(xb3 - 0.04 * CAP - hd * 0.5, tw_ - hd, hd, ym_ - S, CAP))
    pd_ = para2(xb3 - 0.04 * CAP - hd * 0.5, tw_ - hd, hd, ym_ - S, CAP); ld_ = pedges(pd_)[0]
    sbar = I(rect(pd_[0][0], ym_ - S, xb3, ym_), half(ld_[0], ld_[1], -1))
    SS_ = U(rect(0, 0, S, CAP), rect(0, CAP - S, tw_, CAP), dg, sbar, I(ring(xb3, rb2, rb2, S), vreal(xb3, rb2, -1)), tbar(S + round(0.10 * CAP), 0, xb3, S, xb3, rb2, rb2), I(rect(xb3 - 1, ym_ - S, xb3 + 0.45 * rb2, ym_), circ(xb3, rb2, rb2)))
    E['uni1E9E'] = gl(SS_, [rect(S, -10, S + J, CAP + 10), rect(0, ym_, tw_ + 50, ym_ + J) and I(dg, rect(-10, ym_, 2000, ym_ + J))], [(xb3, rb2, rb2)], 'SO', sbk=1.3)
    return E

def build_marks(w, H):
    """accents : (encre, coupes) centrés en x=0 ; dessus posés sur y=0, dessous pendus sous y=0"""
    ST, J = w.ST, w.J; e = 1.15 * J; Wd = w.W; M = {}
    dd = round(1.16 * ST)
    for cap in (False, True):
        k = 0.80 if cap else 1.0; tag = '.cap' if cap else ''
        t = round(0.72 * ST); h = round((110 + 0.45 * ST) * k)
        dx = 0.55 * h / k * 0.9; ha = hwidth(t, dx, h)
        ac = poly(para2(-dx / 2 - ha / 2, dx / 2 - ha / 2, ha, 0, h))
        M['acute' + tag] = (ac, []); M['grave' + tag] = (mirror(ac, 0), [])
        M['hungarumlaut' + tag] = (U(mv(ac, -0.75 * ha - 0.4 * t), mv(ac, 0.75 * ha + 0.4 * t)), [])
        cw = round(0.22 * Wd + 0.25 * ST); hc = round(h * 0.85); f = round(0.3 * t)
        pL, pR, _ = vpair_pts(0, hc, 0, cw, f, t); L_, R_ = clip_pair(pL, pR)
        M['circumflex' + tag] = (U(L_, R_), [I(L_, band(pR, -1, e))])
        pL, pR, _ = vpair_pts(0, 0, hc, cw, f, t); L_, R_ = clip_pair(pL, pR)
        M['caron' + tag] = (U(L_, R_), [I(L_, band(pR, -1, e))])
        rd = round(dd / 2 * (0.88 if cap else 0.95)); gap = round(0.9 * rd + 0.1 * Wd)
        M['dieresis' + tag] = (U(circ(-rd - gap / 2, rd, rd), circ(rd + gap / 2, rd, rd)), [])
        M['dotaccent' + tag] = (circ(0, rd, rd), [])
        rr = round(0.13 * Wd + 0.35 * ST); trr = round(0.55 * ST)
        M['ring' + tag] = (ring(0, rr, rr, trr), [])
        mw = round(0.24 * Wd + 0.15 * ST); M['macron' + tag] = (rect(-mw, 0, mw, round(0.8 * t)), [])
        rb = round((0.22 * Wd + 0.15 * ST)); tb_ = round(0.85 * t)
        M['breve' + tag] = (I(arc(0, rb, rb, tb_, 180, 360), rect(-2000, 0, 2000, round(rb * 0.75 * k + tb_ * 0.4))), [])
        rt = round(0.10 * Wd + 0.2 * ST); tt = round(0.8 * t)
        til = U(arc(-rt + tt / 2, 0, rt, tt, 0, 180), arc(rt - tt / 2, 0, rt, tt, 180, 360)); bt = ubounds(til)
        M['tilde' + tag] = (mv(til, -(bt[0] + bt[2]) / 2, -bt[1]), [])
    # dessous
    rr_ = dd / 2 * 0.85
    cm = drop(0, 0, rr_, (-0.30 * 2 * rr_, -0.85 * 2 * rr_)); b = ubounds(cm)
    M['commabelow'] = (mv(cm, 0, -45 - b[3]), [])
    ct = rot(cm, 180, 0, 0); b = ubounds(ct); M['commaturned'] = (mv(ct, -(b[0] + b[2]) / 2 * 0, -b[1]), [])
    tc = round(0.62 * ST); rc = round(0.11 * XH + 0.25 * ST); cyr = -round(0.10 * XH) - rc
    ced = U(rect(-tc / 2, cyr + rc - tc, tc / 2, 12), arc(0, cyr, rc, tc, -150, 90))
    M['cedilla'] = (ced, [rect(-tc, -round(0.10 * XH) - J * 0 - 1, tc, -round(0.10 * XH) + J)] if False else [])
    to = round(0.62 * ST); ro = round(0.13 * XH + 0.25 * ST); cyo = -round(0.12 * XH)
    og = U(rect(-to / 2, cyo, to / 2, 12), arc(-to / 2 + ro, cyo, ro, to, 180, 300))
    M['ogonek'] = (og, [])
    return M

MARK_OF = {0x300: 'grave', 0x301: 'acute', 0x302: 'circumflex', 0x303: 'tilde', 0x304: 'macron', 0x306: 'breve',
           0x307: 'dotaccent', 0x308: 'dieresis', 0x30A: 'ring', 0x30B: 'hungarumlaut', 0x30C: 'caron',
           0x326: 'commabelow', 0x327: 'cedilla', 0x328: 'ogonek'}
SPACING = {'grave': 0x60, 'acute': 0xB4, 'dieresis': 0xA8, 'macron': 0xAF, 'cedilla': 0xB8, 'circumflex': 0x2C6, 'caron': 0x2C7,
           'breve': 0x2D8, 'dotaccent': 0x2D9, 'ring': 0x2DA, 'ogonek': 0x2DB, 'tilde': 0x2DC, 'hungarumlaut': 0x2DD}

def build_accented(w, G, H):
    """lettres accentuées : la chasse suit la lettre de base, l'accent peut déborder"""
    ST, S = w.ST, w.STC; M = build_marks(w, H); A = {}; CAPS = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    ABOVE_GAP = round(0.12 * XH)
    for n, sp in SPACING.items():
        ink, cu = M[n]
        if n not in ('cedilla', 'ogonek'): ink, cu = mv(ink, 0, XH + ABOVE_GAP), [mv(c, 0, XH + ABOVE_GAP) for c in cu]
        b = ubounds(ink); A['_sp_' + n] = Gl(ink, cu, [], 'OO', b[0], b[2])
    for cp, n in MARK_OF.items():
        ink, cu = M[n]
        if n not in ('cedilla', 'ogonek', 'commabelow'): ink, cu = mv(ink, 0, XH + ABOVE_GAP), [mv(c, 0, XH + ABOVE_GAP) for c in cu]
        A['uni%04X' % cp] = Gl(ink, cu, [], 'NN', 0, 0)
    def center(bn, g):
        b = ubounds(g.ink) if bn not in ('dotlessi', 'uni0237', 'i', 'j') else (g.x0, 0, g.x1, 0); c = (b[0] + b[2]) / 2
        if bn in ('a', 'd', 'q', 'g'): c = w.R - 0.0 * ST + (0.5 * ST if bn != 'g' else 0.5 * ST)
        if bn in ('b', 'p'): c = w.W - w.R - 0.5 * ST
        if bn in ('h', 'n', 'm', 'r', 'k'): c = (b[0] + b[2]) / 2
        if bn == 'uni0237': c = (g.x0 + g.x1) / 2
        if bn in ('G',): c = w.RC
        if getattr(g, 'is_alt', False): c = (b[0] + b[2]) / 2
        return c
    comps = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'composites.json')))
    for cp in comps:
        ch = chr(cp); dec = ud.normalize('NFD', ch); base = dec[0]; marks = [ord(m) for m in dec[1:]]
        above = [m for m in marks if m not in (0x326, 0x327, 0x328)]
        bn = base
        if base == 'i' and above: bn = 'dotlessi'
        if base == 'j' and above: bn = 'uni0237'
        if bn not in G: print('base manquante', ch); continue
        g = G[bn]; isc = base in CAPS
        ink = g.ink; alt = g.alt; cuts = list(g.cuts); x1 = g.x1
        b0 = ubounds(g.ink); cx = center(bn, g); ytop = b0[3] if bn not in ('dotlessi',) else XH
        stem_x = S / 2 if isc else ST / 2
        def add(mk, dx, dy):
            nonlocal ink, alt, cuts
            mi, mc = mk; mi = mv(mi, dx, dy); ink = U(ink, mi); alt = U(alt, mi) if alt is not None else None; cuts += [mv(c, dx, dy) for c in mc]
        for m in marks:
            mn = MARK_OF[m]
            if m in (0x326, 0x327) and base == 'g':
                mi, mc = M['commaturned']; b = ubounds(mi); add((mi, mc), cx - (b[0] + b[2]) / 2, ytop + ABOVE_GAP); continue
            if m in (0x326, 0x327):
                use = 'commabelow' if (m == 0x326 or base in 'GKLNRgklnr') else 'cedilla'
                xb = cx
                if base in 'KLNRklnr': xb = stem_x
                if use == 'cedilla' and base in 'cC': xb = (w.R if base == 'c' else w.RC)
                add(M[use], xb, 0); continue
            if m == 0x328:
                if base in 'aAuU': xa = b0[2] - (ST if not isc else S) / 2
                elif base in 'eE': xa = b0[2] - 0.30 * (b0[2] - b0[0])
                elif base in 'iI': xa = (g.x0 + g.x1) / 2
                else: xa = cx
                if base in 'Aa' and isc: xa = b0[2] - 0.12 * (b0[2] - b0[0])
                if base in 'auiI':
                    sw = S if isc else ST; to = round(0.62 * ST); cyo = -round(0.12 * XH); ro = round(0.13 * XH + 0.25 * ST)
                    og = U(poly([(-sw / 2, 1), (sw / 2, 1), (to / 2, cyo), (-to / 2, cyo)]), arc(-to / 2 + ro, cyo, ro, to, 180, 300))
                    add((og, []), xa, 0); continue
                add(M['ogonek'], xa, 0); continue
            if m == 0x30C and base in 'dltL':
                ap = H['quoteright'].ink; ba = ubounds(ap); sc_ = 0.85
                ap = xf(ap, (sc_, 0, 0, sc_, 0, 0)); ba = ubounds(ap)
                if base == 'd': xr, yt = b0[2] + 0.06 * w.W, ASC
                elif base == 'l': xr, yt = ST + 0.06 * w.W, ASC
                elif base == 't': xr, yt = b0[2] + 0.03 * w.W, XH + round(0.30 * (ASC - XH))
                else: xr, yt = S + 0.08 * CAP, CAP
                add((ap, []), xr - ba[0], yt - ba[3]); x1 = max(x1, xr + (ba[2] - ba[0])); continue
            mi, mc = M[mn + ('.cap' if isc else '')]; mb = ubounds(mi)
            gap = round(0.06 * CAP) if isc else (ABOVE_GAP if bn not in ('l', 'h', 'k', 'b', 'd', 't') else ABOVE_GAP)
            add((mi, mc), cx, ytop + gap - mb[1]); ytop = ytop + gap + (mb[3] - mb[1])
        gg = Gl(ink, cuts, g.centers, g.sides, g.x0, x1, alt); gg.sbk = getattr(g, 'sbk', 1.0)
        A['uni%04X' % cp] = gg
    return A
