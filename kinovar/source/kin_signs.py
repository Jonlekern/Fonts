# КИНОВАРЬ : chiffres, ponctuation, signes. Même plume : traits fins, flancs épais, points en losange.
from kin_letters import *

def digits(w):
    S, h = w.S, w.h; y0, y1 = 0, H; ov = 8; DW = round(0.52 * H + 0.9 * S); t = round(0.95 * S)
    ring = lambda cx, cy, a, b, ts=S, tv=None: D(ell(cx, cy, a, b), ell(cx, cy, a - ts, b - (h * 1.25 if tv is None else tv)))
    hb = lambda xa, xb, y: rect(xa, y, xb, y + h)
    def goutte(x, y, sens=-1, k=1.0):
        s = (1.5 * h + 0.10 * S) * k; return poly([(x - s * 0.55, y), (x + s * 0.45, y), (x + s * 0.45, y + sens * 2.1 * s)])
    diag = lambda xb, xt, tt, a=y0, b=y1: poly([(xb, a), (xb + tt, a), (xt + tt, b), (xt, b)])
    fin = lambda xa, ya, xb, yb: link(xa, ya, xb, yb, h * 1.2, 0, 0)
    G = {}
    G['zero'] = ring(DW / 2, H / 2, DW / 2, H / 2 + ov)
    x1 = round(DW * 0.50 - S / 2 + 0.06 * H)
    G['one'] = U(rect(x1, 0, x1 + S, H), fin(x1 - 0.30 * H, H - 0.26 * H, x1 + S * 0.5, H - 0.01 * H), I(U(poly([(x1 + S - 2, 0), (x1 + S + 0.30 * S, 0), (x1 + S - 2, 0.42 * S)]), poly([(x1 + 2, 0), (x1 - 0.30 * S, 0), (x1 + 2, 0.42 * S)])), rect(-100, 0, 2000, H)))
    b2 = 0.27 * H
    G['two'] = U(I(ring(DW / 2, H - b2 + ov / 2, DW / 2, b2), rect(-5, H - b2 * 1.02, DW + 5, H + 30)), diag(0, DW - t, t, h, H - b2 * 0.98), hb(0, DW, 0), goutte(DW - 0.5 * h, h - 1, 1))
    a3 = DW * 0.98
    G['three'] = U(I(ring(0, H - 0.24 * H + ov / 2, a3 * 0.90, 0.24 * H), rect(0.12 * DW, 0, DW + 20, H + 30)), I(ring(0, 0.30 * H - ov / 2, a3, 0.30 * H), rect(0.04 * DW, -30, DW + 20, H)))
    x4 = DW - S - round(0.10 * DW); y4 = round(0.28 * H)
    G['four'] = U(rect(x4, 0, x4 + S, H), fin(h * 0.6, y4 + h, x4 + S * 0.5, H - 0.01 * H), hb(0, DW, y4))
    lo5 = D(ring(DW / 2, 0.30 * H - ov / 2, DW / 2, 0.30 * H), rect(-5, 0.26 * H, DW * 0.50, 0.70 * H))
    G['five'] = U(hb(0.10 * DW, DW * 0.94, H - h), goutte(DW * 0.94 - 0.5 * h, H - h + 1), rect(0.10 * DW, 0.50 * H, 0.10 * DW + round(0.7 * S), H), lo5)
    six = U(ring(DW / 2, 0.31 * H - ov / 2, DW / 2, 0.31 * H), I(ring(DW * 0.66, H / 2, DW * 0.66, H / 2 + ov), rect(-5, 0.31 * H, DW * 0.84, H + 30)))
    G['six'] = six
    G['seven'] = U(hb(0, DW, H - h), goutte(0.6 * h, H - h + 1), diag(round(0.20 * DW), DW - t, t, 0, H - h + 1))
    G['eight'] = U(ring(DW / 2, H - 0.235 * H + ov / 2, DW * 0.44, 0.235 * H), ring(DW / 2, 0.29 * H - ov / 2, DW / 2, 0.29 * H))
    G['nine'] = mirror(flipv(six, H / 2), DW / 2)
    return {k: (I(v, rect(-200, -ov, 3000, H + ov)), DW) for k, v in G.items()}

def signs(w):
    S, h = w.S, w.h; ov = 8; hs = round(h * 1.5); YM = round(0.44 * H); LO, HI = -round(0.14 * H), H + round(0.06 * H)
    ring = lambda cx, cy, a, b, ts=S, tv=None: D(ell(cx, cy, a, b), ell(cx, cy, a - ts, b - (h * 1.25 if tv is None else tv)))
    fin = lambda xa, ya, xb, yb, t=None: link(xa, ya, xb, yb, h * 1.2 if t is None else t, 0, 0)
    bar = lambda xa, xb, yc, t=None: rect(xa, yc - (hs if t is None else t) / 2, xb, yc + (hs if t is None else t) / 2)
    a = round(0.60 * S) + 9                                   # demi-diagonale du point en losange
    pt = lambda x, y: losange(x + a, y, a, a)
    para = lambda xb, ya, xt, yb, t: poly([(xb, ya), (xb + t, ya), (xt + t, yb), (xt, yb)])      # trait presque droit, coupé à plat
    Sg = {}
    def put(n, p):
        b = p.bounds; Sg[n] = (mv(p, -b[0]), b[2] - b[0])
    virg = lambda y: U(pt(0, y), poly([(a * 0.5, y - a * 0.5), (2 * a, y), (a * 1.25, y - 2.5 * a), (a * 0.15, y - 3.1 * a)]))
    put('period', pt(0, a)); put('comma', virg(a)); put('colon', U(pt(0, a), pt(0, round(0.40 * H))))
    put('semicolon', U(virg(a), pt(0, round(0.40 * H)))); put('periodcentered', pt(0, YM)); put('bullet', losange(1.6 * a, YM, 1.6 * a, 1.6 * a))
    put('ellipsis', U(pt(0, a), pt(3.4 * a, a), pt(6.8 * a, a)))
    ex = U(poly([(a - S * 0.55, H), (a + S * 0.55, H), (a + S * 0.18, 3.4 * a), (a - S * 0.18, 3.4 * a)]), pt(0, a)); put('exclam', ex); put('exclamdown', flipv(ex, H / 2 - 0.08 * H))
    wq = round(0.36 * H + 0.5 * S); bq = 0.25 * H
    qu = U(D(ring(wq / 2, H - bq + ov / 2, wq / 2, bq), rect(-5, H - 2 * bq - 5, wq / 2, H - bq)), rect(wq / 2 - hs / 2, 3.6 * a, wq / 2 + hs / 2, H - 2 * bq + h * 1.2), pt(wq / 2 - a, a))
    put('question', qu); put('questiondown', mirror(flipv(qu, H / 2 - 0.08 * H), wq / 2))
    tick = lambda x: poly([(x, H), (x + S * 0.8, H), (x + S * 0.55, H - 0.24 * H), (x + S * 0.25, H - 0.24 * H)])
    put('quotesingle', tick(0)); put('quotedbl', U(tick(0), tick(S * 0.8 + 0.07 * H)))
    qr = mv(virg(a), 0, H - 1.5 * a); ql = mirror(flipv(qr, H - 1.1 * a - 0.5 * a), a * 1.0); dq = 2 * a + 0.05 * H
    put('quoteright', qr); put('quoteleft', ql); put('quotesinglbase', virg(a))
    put('quotedblright', U(qr, mv(qr, dq))); put('quotedblleft', U(ql, mv(ql, dq))); put('quotedblbase', U(virg(a), mv(virg(a), dq)))
    put('hyphen', bar(0, round(0.26 * H), YM)); put('endash', bar(0, round(0.50 * H), YM)); put('emdash', bar(0, round(0.90 * H), YM)); put('uni2212', bar(0, round(0.50 * H), YM))
    Sg['underscore'] = (rect(0, -90 - hs, round(0.56 * H), -90), round(0.56 * H))
    pw = round(0.26 * H + 0.3 * S); par = I(ring(pw * 1.9, (LO + HI) / 2, pw * 1.9, (HI - LO) / 2 + 30, round(0.8 * S), h), rect(0, LO, pw, HI))
    put('parenleft', par); put('parenright', mirror(par, pw / 2))
    bs = round(0.6 * S); bw = bs + round(0.14 * H); br = U(rect(0, LO, bs, HI), rect(0, LO, bw, LO + h), rect(0, HI - h, bw, HI))
    put('bracketleft', br); put('bracketright', mirror(br, bw / 2))
    nb = round(0.07 * H); ymid = (LO + HI) / 2; bc = U(mv(br, nb), poly([(0, ymid), (nb + 1, ymid + nb * 1.6), (nb + 1, ymid - nb * 1.6)]))
    put('braceleft', bc); put('braceright', mirror(bc, (bw + nb) / 2))
    sw = round(0.34 * H); put('slash', para(0, LO, sw, HI, hs * 1.1)); put('backslash', para(sw, LO, 0, HI, hs * 1.1)); put('bar', rect(0, LO, hs, HI))
    m = round(0.42 * H); c = m / 2
    put('plus', U(bar(0, m, YM), rect(c - hs / 2, YM - c, c + hs / 2, YM + c))); eq = round(0.09 * H)
    put('equal', U(bar(0, m, YM + eq), bar(0, m, YM - eq)))
    put('multiply', U(fin(0, YM - c * 0.8, m * 0.8, YM + c * 0.8, hs), fin(0, YM + c * 0.8, m * 0.8, YM - c * 0.8, hs)))
    put('divide', U(bar(0, m, YM), pt(c - a, YM + eq + a * 0.9), pt(c - a, YM - eq - a * 0.9)))
    lt = U(fin(0, YM, m * 0.9, YM + c * 0.75, hs), fin(0, YM, m * 0.9, YM - c * 0.75, hs)); put('less', lt); put('greater', mirror(lt, m * 0.45))
    ga = round(0.20 * H); gb = round(0.17 * H); gl = U(fin(0, YM, ga, YM + gb, hs), fin(0, YM, ga, YM - gb, hs)); gg = ga + round(0.07 * H)
    put('guilsinglleft', gl); put('guilsinglright', mirror(gl, ga / 2)); put('guillemotleft', U(gl, mv(gl, gg))); put('guillemotright', mirror(U(gl, mv(gl, gg)), (ga + gg) / 2))
    r_ = round(0.13 * H); ya = H - r_
    put('asterisk', U(rect(r_ - hs / 2, ya - r_, r_ + hs / 2, ya + r_), fin(0, ya - r_ * 0.55, 2 * r_, ya + r_ * 0.55, hs), fin(0, ya + r_ * 0.55, 2 * r_, ya - r_ * 0.55, hs)))
    nw = round(0.56 * H); sl = round(0.10 * H)
    put('numbersign', U(para(nw * 0.20, 0, nw * 0.20 + sl, H, hs), para(nw * 0.62, 0, nw * 0.62 + sl, H, hs), bar(0, nw, round(0.64 * H)), bar(0, nw, round(0.34 * H))))
    rr = round(0.15 * H + 0.25 * S); rb = round(0.20 * H); sr = lambda: ring(rr, 0, rr, rb, round(0.7 * S), h)
    pc = U(mv(sr(), 0, H - rb), para(rr * 1.0, 0, rr * 2.9, H, hs * 1.1), mv(sr(), rr * 1.9, rb)); put('percent', pc)
    put('degree', mv(ring(rr * 0.8, 0, rr * 0.8, rr * 0.8, round(0.55 * S), round(0.9 * h)), 0, H - rr * 0.8))
    aw = round(0.50 * H + 0.6 * S)
    amp = U(ring(aw * 0.44, H - 0.22 * H + ov / 2, aw * 0.34, 0.22 * H, round(0.8 * S)), D(ring(aw * 0.44, 0.30 * H - ov / 2, aw * 0.44, 0.30 * H), rect(aw * 0.44, 0.30 * H, aw + 5, 0.50 * H)),
            fin(aw * 0.50, 0.34 * H, aw * 1.06, 0.34 * H - 0.001, h), bar(aw * 0.50, aw * 1.06, 0.34 * H, h)); put('ampersand', amp)
    R_ = round(0.42 * H); ri = round(0.17 * H)
    at = U(D(ring(R_, YM, R_, R_, h * 1.3, h * 1.3), rect(R_ * 1.25, YM - R_ - 5, 2 * R_ + 5, YM - R_ * 0.25)), ring(R_, YM, ri, ri * 1.15, round(0.7 * S), h), rect(R_ + ri - round(0.7 * S), YM - ri * 1.15, R_ + ri, YM + ri * 1.15),
           I(ring(R_ + ri + (R_ - ri) / 2 - h * 0.3, YM - ri * 0.2, (R_ - ri) / 2 + h * 0.3, ri * 1.0, h * 1.3, h * 1.3), rect(0, YM - R_, 3 * R_, YM - ri * 0.2))); put('at', at)
    def lettre(ch): p, ww = letter(ch, w); return p, ww
    def avec_ticks(ch):
        p, ww = lettre(ch); tk = round(0.09 * H); return U(I(p, rect(-200, -ov, 3000, H + ov)), rect(ww / 2 - hs / 2, H - 2, ww / 2 + hs / 2, H + tk), rect(ww / 2 - hs / 2, -tk, ww / 2 + hs / 2, 2))
    put('dollar', avec_ticks('S')); put('cent', avec_ticks('С'))
    p, ww = lettre('С'); put('Euro', U(mv(p, 0.08 * H), bar(0, 0.08 * H + ww * 0.70, round(0.56 * H), h * 1.3), bar(0, 0.08 * H + ww * 0.70, round(0.44 * H), h * 1.3)))
    p, ww = lettre('L'); put('sterling', U(mv(p, 0.06 * H), bar(0, 0.06 * H + ww * 0.78, round(0.40 * H), h * 1.3)))
    p, ww = lettre('V'); yy = round(0.42 * H)
    put('yen', U(I(mv(flipv(flipv(p, H / 2), H / 2), 0), rect(-200, 0, 3000, H)), bar(ww * 0.10, ww * 0.90, round(0.30 * H), h * 1.3), bar(ww * 0.10, ww * 0.90, round(0.18 * H), h * 1.3)))
    p, ww = lettre('Р'); put('uni20BD', U(I(p, rect(-200, 0, 3000, H + 30)), rect(0, 0, S, 0.3 * H), mv(bar(-0.10 * H, ww * 0.74, round(0.22 * H), h * 1.3), 0)))
    wp = Wt(w.nom, max(18, round(0.62 * S)), max(10, round(0.8 * h)), w.wclass)
    pn, wn = lettre('N'); po, wo = letter('О', wp, 0, round(0.40 * H)); xo = wn + round(0.05 * H)
    put('uni2116', U(pn, mv(po, xo, H - round(0.40 * H)), rect(xo, H - round(0.40 * H) - round(0.06 * H) - h, xo + wo, H - round(0.40 * H) - round(0.06 * H))))
    th = round(0.40 * H); pt_, wt_ = letter('Т', wp, 0, th); pm, wm = letter('М', wp, 0, th)
    put('trademark', mv(U(pt_, mv(pm, wt_ + round(0.04 * H))), 0, H - th))
    for n, ch in (('copyright', 'С'), ('registered', 'R')):
        hh = round(0.36 * H); pl, wl = letter(ch, wp, 0, hh); Rr = round(0.34 * H)
        put(n, U(ring(Rr, H - Rr, Rr, Rr, h * 1.3, h * 1.3), mv(pl, Rr - wl / 2, H - Rr - hh / 2)))
    ps, ws = letter('S', wp, 0, round(0.56 * H)); put('section', U(mv(ps, 0, H - round(0.56 * H)), mv(ps, 0, -round(0.04 * H))))
    px = round(0.22 * H)
    put('paragraph', U(I(ell(px, H - px, px, px), rect(0, H - 2 * px, px, H)), rect(px - hs, LO, px, H), rect(px + round(0.08 * H), LO, px + round(0.08 * H) + hs, H), rect(px - 2, H - h, px + round(0.08 * H) + hs, H)))
    put('asciicircum', mv(U(fin(0, 0, r_, r_ * 1.1, hs), fin(r_, r_ * 1.1, 2 * r_, 0, hs)), 0, H - r_ * 1.1))
    put('asciitilde', I(U(fin(0, YM - 0.02 * H, m * 0.35, YM + 0.035 * H, hs), fin(m * 0.35, YM + 0.035 * H, m * 0.65, YM - 0.035 * H, hs), fin(m * 0.65, YM - 0.035 * H, m, YM + 0.02 * H, hs)), rect(0, 0, m, H)))
    ac = poly([(0, 0), (S * 0.45, 0), (S * 0.45 + 0.09 * H, 0.15 * H), (0.09 * H - S * 0.35, 0.15 * H)])
    put('grave', mv(mirror(ac, 0), 0, H - 0.15 * H)); Sg['acutecomb'] = (ac, 0)
    return Sg
