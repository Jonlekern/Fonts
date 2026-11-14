# KARKAS : chiffres, ponctuation, signes, accents et lettres en plus. Même langage : fûts, barres, obliques.
import unicodedata as ud
from kar_core import *
from kar_letters import letter, Gl
from kar_liga import shared, stack

def ring(w_, y0, y1, S, B, c=0, corners='', ):
    """cadre ; c = coin coupé ; corners : lettres parmi a (bas gauche) b (bas droite) c (haut droite) d (haut gauche)"""
    def box(x0, ya, x1, yb, cc):
        pts = []
        pts += [(x0 + cc, ya)] if 'a' in corners and cc > 0 else []
        pts += [(x0, ya)] if not ('a' in corners and cc > 0) else []
        if 'b' in corners and cc > 0: pts += [(x1 - cc, ya), (x1, ya + cc)]
        else: pts += [(x1, ya)]
        if 'c' in corners and cc > 0: pts += [(x1, yb - cc), (x1 - cc, yb)]
        else: pts += [(x1, yb)]
        if 'd' in corners and cc > 0: pts += [(x0 + cc, yb), (x0, yb - cc)]
        else: pts += [(x0, yb)]
        if 'a' in corners and cc > 0: pts += [(x0, ya + cc)]
        return poly(pts)
    ci = c - (B - 0.414 * S)
    return D(box(0, y0, w_, y1, c), box(S, y0 + B, w_ - S, y1 - B, ci if ci > 1 else 0))

def para(x0, y0, x1, y1, t):
    """trait oblique de largeur horizontale t, du bas (x0) au haut (x1)"""
    return poly([(x0, y0), (x0 + t, y0), (x1 + t, y1), (x1, y1)])

def thin(w, k=0.62, kc=0.62):
    return Wt(w.nom, max(12, round(w.S * k)), max(11, round(w.B * k)), round(w.CT * kc), w.wclass)

def digits(w, y0=0, y1=CAP, ww=None):
    S, B, CT = w.S, w.B, w.CT; W = w.W if ww is None else ww; h = y1 - y0
    ym = y0 + round(0.56 * h); dk = min(1.25 * CT, 0.20 * h); tk = max(min(1.10 * CT, 0.15 * h), B + 0.55 * CT)
    bar = lambda x0, x1, yc: rect(x0, yc - B / 2, x1, yc + B / 2)
    top = lambda x0, x1: rect(x0, y1 - B, x1, y1)
    bot = lambda x0, x1: rect(x0, y0, x1, y0 + B)
    mast = lambda x, a=None, b=None: rect(x, y0 if a is None else a, x + S, y1 if b is None else b)
    c = max(0.50 * (W - 2 * S), 0.9 * S)
    Dg = {}
    Dg['zero'] = ring(W, y0, y1, S, B, c, 'abcd')
    x1 = round(0.5 * (W - S) + 0.12 * (W - 2 * S))
    Dg['one'] = U(mast(x1), top(0, x1 + S), bot(0, W))
    Dg['two'] = U(top(0, W), rect(0, y1 - tk, S, y1), mast(W - S, ym - B / 2, y1), bar(0, W, ym), mast(0, y0, ym + B / 2), bot(0, W))
    Dg['three'] = U(mast(W - S), top(0, W), bot(0, W), bar(round(0.30 * (W - 2 * S)), W, ym), rect(0, y1 - tk, S, y1), rect(0, y0, S, y0 + tk))
    yq = y0 + round(0.34 * h)
    Dg['four'] = U(mast(0, yq - B / 2, y1), bar(0, W, yq), mast(W - S))
    Dg['five'] = U(top(0, W), mast(0, ym - B / 2, y1), bar(0, W, ym), mast(W - S, y0, ym + B / 2), bot(0, W), rect(0, y0, S, y0 + tk))
    Dg['six'] = U(mast(0), top(0, W), rect(W - S, y1 - tk, W, y1), bar(0, W, ym), mast(W - S, y0, ym + B / 2), bot(0, W))
    yz = y0 + 0.5 * h
    Dg['seven'] = U(top(0, W), mast(W - S, yz + dk, y1), link(S / 2, yz - dk, W - S / 2, yz + dk, S, S, S), mast(0, y0, yz - dk))
    Dg['eight'] = U(D(rect(0, y0, W, y1), rect(S, y0 + B, W - S, y1 - B)), bar(0, W, ym))
    yn = y0 + h - round(0.56 * h)
    Dg['nine'] = U(mast(W - S), bot(0, W), rect(0, y0, S, y0 + tk), bar(0, W, yn), mast(0, yn - B / 2, y1), top(0, W))
    return {k: Gl(v, W) for k, v in Dg.items()}

def signs(w):
    S, B, CT, W, G = w.S, w.B, w.CT, w.W, w.G
    H = CAP; DOT = round(1.2 * S) + 6; YM = round(0.44 * H); LO, HI = -round(0.11 * H), H + round(0.04 * H)
    bar = lambda x0, x1, yc: rect(x0, yc - B / 2, x1, yc + B / 2)
    dot = lambda x, y: rect(x, y, x + DOT, y + DOT)
    Sg = {}
    def put(n, p, w_=None):
        b = bounds(p); p = mv(p, -b[0]) if w_ is None else p
        Sg[n] = Gl(p, (b[2] - b[0]) if w_ is None else w_)
    ln = round(0.30 * DOT) + 6; ch = DOT + round(0.085 * H)
    tail = lambda y: poly([(ln, y + ch), (ln + DOT, y + ch), (ln + DOT, y + ch - DOT), (DOT * 0.55, y), (0, y), (ln, y + ch - DOT)])   # virgule : un carré et sa pointe
    put('period', dot(0, 0)); put('comma', tail(DOT - ch))
    put('colon', U(dot(0, 0), dot(0, round(0.36 * H)))); put('semicolon', U(mv(tail(DOT - ch), 0), mv(dot(0, round(0.36 * H)), ln)))
    put('ellipsis', U(dot(0, 0), dot(DOT + round(0.7 * G), 0), dot(2 * (DOT + round(0.7 * G)), 0)))
    put('periodcentered', dot(0, YM - DOT / 2)); put('bullet', rect(0, YM - DOT * 0.85, DOT * 1.7, YM + DOT * 0.85))
    eg = round(0.5 * DOT) + 14
    ex = U(rect((DOT - S) / 2, DOT + eg, (DOT + S) / 2, H), dot(0, 0)); put('exclam', ex); put('exclamdown', flipv(ex, H / 2))
    Wq = S + round(0.80 * CT); yq = round(0.50 * H); xs = round((Wq - S) / 2)
    qu = U(rect(0, H - B, Wq, H), rect(0, H - max(min(1.1 * CT, 0.15 * H), B + 0.55 * CT), S, H), rect(Wq - S, yq, Wq, H), rect(xs, yq, Wq, yq + B), rect(xs, DOT + eg, xs + S, yq + B), rect(xs + (S - DOT) / 2, 0, xs + (S + DOT) / 2, DOT))
    put('question', qu); put('questiondown', mirror(flipv(qu, H / 2), Wq / 2))
    qh = round(0.20 * H)
    put('quotesingle', rect(0, H - qh, S, H)); put('quotedbl', U(rect(0, H - qh, S, H), rect(S + round(0.45 * G), H - qh, 2 * S + round(0.45 * G), H)))
    qr = tail(H - ch); ql = mirror(flipv(qr, H - ch / 2), (ln + DOT) / 2); dq = ln + DOT + round(0.35 * G)
    put('quoteright', qr); put('quoteleft', ql); put('quotesinglbase', tail(DOT - ch))
    put('quotedblright', U(qr, mv(qr, dq))); put('quotedblleft', U(ql, mv(ql, dq))); put('quotedblbase', U(tail(DOT - ch), mv(tail(DOT - ch), dq)))
    hw_ = round(0.90 * CT)
    put('hyphen', bar(0, hw_, YM)); put('endash', bar(0, round(1.7 * CT), YM)); put('emdash', bar(0, round(3.0 * CT), YM))
    put('underscore', mv(rect(0, -80 - B, W + G, -80), 0), W + G); Sg['underscore'].raw = True
    c = round(0.42 * CT) + round(0.4 * S); pw_ = S + c
    pl = I(ring(4 * pw_, LO, HI, S, B, c, 'ad'), rect(0, LO, pw_, HI))
    put('parenleft', pl); put('parenright', mirror(pl, pw_ / 2))
    bw = S + round(0.34 * CT); bl = U(rect(0, LO, S, HI), rect(0, LO, bw, LO + B), rect(0, HI - B, bw, HI))
    put('bracketleft', bl); put('bracketright', mirror(bl, bw / 2))
    nb = round(0.28 * CT); ymid = (LO + HI) / 2
    br = U(mv(bl, nb), poly([(0, ymid), (nb + 1, ymid + nb + S * 0.7), (nb + 1, ymid - nb - S * 0.7)]))
    put('braceleft', br); put('braceright', mirror(br, (bw + nb) / 2))
    sw = round(0.95 * CT); st = round(1.08 * S)
    put('slash', para(0, LO, sw, HI, st)); put('backslash', mirror(para(0, LO, sw, HI, st), (sw + st) / 2))
    put('bar', rect(0, LO, S, HI)); gap = round(0.07 * H)
    put('brokenbar', U(rect(0, LO, S, ymid - gap), rect(0, ymid + gap, S, HI)))
    pw = round(1.25 * CT) + S; a = pw / 2
    put('plus', U(bar(0, pw, YM), rect(a - S / 2, YM - a, a + S / 2, YM + a))); put('uni2212', bar(0, pw, YM))
    eq = round(0.11 * H); put('equal', U(bar(0, pw, YM + eq), bar(0, pw, YM - eq)))
    put('multiply', U(link(0, YM - a, pw, YM + a, S, 0, 0), link(0, YM + a, pw, YM - a, S, 0, 0)))
    put('divide', U(bar(0, pw, YM), dot(a - DOT / 2, YM + B / 2 + eq * 0.7), dot(a - DOT / 2, YM - B / 2 - eq * 0.7 - DOT)))
    lt = U(link(0, YM, pw, YM + a, S, 0, 0), link(0, YM, pw, YM - a, S, 0, 0))
    put('less', lt); put('greater', mirror(lt, pw / 2))
    ga = round(0.55 * CT); gb = round(0.13 * H); gt = round(0.85 * S)
    gl = U(link(0, YM, ga, YM + gb, gt, 0, 0), link(0, YM, ga, YM - gb, gt, 0, 0)); gg = ga + round(0.50 * G)
    put('guilsinglleft', gl); put('guilsinglright', mirror(gl, ga / 2))
    put('guillemotleft', U(gl, mv(gl, gg))); put('guillemotright', mirror(U(gl, mv(gl, gg)), (ga + gg) / 2))
    t = thin(w, 0.80, 0.70); ta = thin(w, 0.50, 1.0); at_ = round(1.10 * CT + 0.9 * S)
    put('asterisk', mv(U(link(0, -at_ / 2, at_, at_ / 2, ta.S, 0, 0), link(0, at_ / 2, at_, -at_ / 2, ta.S, 0, 0), rect(at_ / 2 - ta.S / 2, -at_ * 0.62, at_ / 2 + ta.S / 2, at_ * 0.62)), 0, H - at_ * 0.62))
    nw = 2 * S + round(1.2 * CT) + 2 * round(0.3 * CT); n0 = round(0.3 * CT)
    put('numbersign', U(rect(n0, 0, n0 + S, H), rect(nw - n0 - S, 0, nw - n0, H), bar(0, nw, round(0.62 * H)), bar(0, nw, round(0.34 * H))))
    rw = 2 * t.S + round(0.42 * CT); rh = round(0.36 * H); rg = lambda: ring(rw, 0, rh, t.S, t.B)
    psw = round(0.70 * CT); pst = round(0.9 * S); pg = round(0.36 * psw) + 18
    pc = U(mv(rg(), 0, H - rh), para(rw + pg - psw, 0, rw + pg, H, pst), mv(rg(), rw + pg - psw + pst + pg, 0))
    put('percent', pc); pcw = bounds(pc)[2]
    put('perthousand', U(pc, mv(rg(), pcw + round(0.5 * t.CT), 0)))
    put('degree', mv(ring(rw, 0, round(0.26 * H), t.S, t.B), 0, H - round(0.26 * H)))
    E_ = letter('E', w); xt = E_.w - round(0.30 * CT); yb = round(0.68 * H)
    put('ampersand', U(E_.ink, rect(0, yb - B / 2, xt + S + round(0.30 * CT), yb + B / 2), rect(xt, yb - round(0.13 * H), xt + S, yb + round(0.13 * H))))
    ti = thin(w, 0.70, 0.60); aw = ti.W; ah0, ah1 = round(0.22 * H), round(0.62 * H); gp = max(w.g, 26)
    Wa = S + gp + aw - ti.S + S
    at = U(D(ring(Wa, 0, round(0.84 * H), S, B), rect(Wa - S - gp, -1, Wa + 1, ah0)), mv(ring(aw, ah0, ah1, ti.S, ti.B), Wa - S - aw + ti.S))
    put('at', mv(at, 0, -round(0.04 * H)))
    tk = round(0.075 * H)
    def ticks(g_): xc = g_.w / 2; return U(g_.ink, rect(xc - S / 2, H - 1, xc + S / 2, H + tk), rect(xc - S / 2, -tk, xc + S / 2, 1))
    put('dollar', ticks(letter('S', w))); put('cent', ticks(letter('C', w)))
    xs_ = round(0.26 * CT); Ws = xs_ + S + round(0.80 * CT)
    put('sterling', U(rect(xs_, 0, xs_ + S, H), rect(xs_, H - B, Ws, H), rect(Ws - S, H - min(1.1 * CT, 0.15 * H), Ws, H), rect(0, 0, Ws, B), bar(0, xs_ + S + round(0.5 * CT), round(0.42 * H))))
    Y_ = letter('Y', w); yw = round(0.86 * W); y0_ = (W - yw) / 2
    put('yen', U(Y_.ink, bar(y0_, y0_ + yw, round(0.34 * H)), bar(y0_, y0_ + yw, round(0.20 * H))))
    C_ = letter('C', w); ex_ = round(0.28 * CT)
    put('Euro', U(mv(C_.ink, ex_), bar(0, ex_ + round(0.72 * C_.w), round(0.57 * H)), bar(0, ex_ + round(0.72 * C_.w), round(0.43 * H))))
    put('section', stack(w, 'S').ink)
    px = round(0.55 * CT) + S; pg = round(0.32 * CT)
    put('paragraph', U(rect(0, round(0.56 * H), px, H), rect(px - S, LO, px, H), rect(px + pg, LO, px + pg + S, H), rect(0, H - B, px + pg + S, H)))
    dw = round(0.95 * CT) + S
    put('dagger', U(rect((dw - S) / 2, LO, (dw + S) / 2, H), bar(0, dw, round(0.70 * H))))
    # exposants, fractions, №, ™, ©, ®
    sh = round(0.46 * H); ts = thin(w, 0.72, 0.62); sd = digits(ts, 0, sh)
    for n, d in (('onesuperior', 'one'), ('twosuperior', 'two'), ('threesuperior', 'three')): put(n, mv(sd[d].ink, 0, H - sh))
    fs = round(0.60 * CT); ft = round(0.9 * S); gf = max(round(0.25 * CT), 20); r_ = sh / H
    xb = ts.W + gf - fs * (1 - r_); xd = xb + fs * r_ + ft + gf
    for n, a_, b_ in (('onequarter', 'one', 'four'), ('onehalf', 'one', 'two'), ('threequarters', 'three', 'four')):
        put(n, U(mv(sd[a_].ink, 0, H - sh), para(xb, 0, xb + fs, H, ft), mv(sd[b_].ink, xd, 0)))
    N_ = letter('N', w); o_ = ring(ts.W, 0, round(0.40 * H), ts.S, ts.B); xn = N_.w + round(0.45 * G)
    put('uni2116', U(N_.ink, mv(o_, xn, H - round(0.40 * H)), rect(xn, H - round(0.40 * H) - round(0.05 * H) - ts.B, xn + ts.W, H - round(0.40 * H) - round(0.05 * H))))
    th = round(0.40 * H); T_ = letter('T', ts, 0, th); M_ = letter('M', ts, 0, th)
    put('trademark', mv(U(T_.ink, mv(M_.ink, T_.w + round(0.5 * ts.G))), 0, H - th))
    for n, ch_, hh in (('copyright', 'C', round(0.62 * H)), ('registered', 'R', round(0.62 * H))):
        g_ = letter(ch_, ts, 0, hh - 2 * (ts.B + ts.g)); wb = g_.w + 2 * (ts.S + ts.g)
        put(n, mv(U(ring(wb, 0, hh, ts.S, ts.B), mv(g_.ink, ts.S + ts.g, ts.B + ts.g)), 0, H - hh))
    put('asciicircum', mv(marks(w)[0x302], 0, H - 100))
    tl = round(0.95 * CT); tst = round(0.075 * H)
    tb = round(0.8 * B); tl += round(0.5 * S)
    put('asciitilde', U(rect(0, YM - tb, tl, YM), rect(tl - tb, YM - tb, tl, YM + tst), rect(tl - tb, YM + tst - tb, 2 * tl - tb, YM + tst)))
    return Sg

# accents : (dessin centré sur x = 0, posé sur y = 0)
TOP = {0x300: 'grave', 0x301: 'acute', 0x302: 'circumflex', 0x303: 'tilde', 0x304: 'macron', 0x306: 'breve', 0x307: 'dotaccent',
       0x308: 'dieresis', 0x30A: 'ring', 0x30B: 'hungarumlaut', 0x30C: 'caron'}
BOT = {0x326: 'commaaccent', 0x327: 'cedilla', 0x328: 'ogonek'}
SPACING = {0x60: 0x300, 0xB4: 0x301, 0x2C6: 0x302, 0x2DC: 0x303, 0xAF: 0x304, 0x2D8: 0x306, 0x2D9: 0x307, 0xA8: 0x308, 0x2DA: 0x30A,
           0x2DD: 0x30B, 0x2C7: 0x30C, 0xB8: 0x327, 0x2DB: 0x328}
MGAP = 34

def marks(w):
    S, B, CT = w.S, w.B, w.CT
    mt = round(0.72 * S) + 8; mh = 100; md = round(0.80 * S) + 10; a = round(0.34 * CT) + mt / 2
    M = {}
    ac = para(-a / 2 - mt / 2 + 2, 0, a / 2 - mt / 2 + 2, mh, mt)
    M[0x301] = ac; M[0x300] = mirror(ac, 0)
    cf = I(U(link(-a - mt * 0.3, 0, 0, mh, mt, 0, 0), link(0, mh, a + mt * 0.3, 0, mt, 0, 0)), rect(-400, 0, 400, mh))
    M[0x302] = cf; M[0x30C] = flipv(cf, mh / 2)
    dg = round(0.22 * CT) + 6
    M[0x308] = U(rect(-dg / 2 - md, 0, -dg / 2, md), rect(dg / 2, 0, dg / 2 + md, md)); M[0x307] = rect(-md / 2, 0, md / 2, md)
    mb = round(0.85 * B) + 4; mw = round(0.75 * CT) + S
    M[0x304] = rect(-mw / 2, 20, mw / 2, 20 + mb)
    bt = min(mt, round(0.30 * mw))
    M[0x306] = U(rect(-mw / 2, 0, mw / 2, mb), rect(-mw / 2, 0, -mw / 2 + bt, mh * 0.8), rect(mw / 2 - bt, 0, mw / 2, mh * 0.8))
    rs = min(round(0.62 * S) + 6, 34); rw_ = 2 * rs + max(round(0.30 * CT), 34)
    M[0x30A] = mv(ring(rw_, 0, mh + 6, rs, rs), -rw_ / 2)
    st = round(0.36 * mh); tw = round(0.40 * CT) + mt
    M[0x303] = mv(U(rect(-tw, 0, mt / 2, mb), rect(-mt / 2, 0, mt / 2, st + mb), rect(-mt / 2, st, tw, st + mb)), 0, 16)
    hg = round(0.5 * a) + mt * 0.6
    M[0x30B] = U(mv(ac, -hg), mv(ac, hg))
    cw = round(0.30 * CT) + mt
    ms = min(mt, S)
    M[0x327] = U(rect(-ms / 2, -70, ms / 2, 0), rect(-cw + ms / 2, -70 - mb, ms / 2, -70))
    M[0x328] = U(rect(-S / 2, -70, S / 2, 0), rect(-S / 2, -70 - mb, cw - S / 2, -70))       # l'ogonek prolonge le fût : même largeur
    M[0x326] = mirror(para(-mt / 2 - 12, -150, -mt / 2 + 12, -48, mt), 0)
    return M

MARKX = {'L': lambda g, w: w.S / 2}

def accented(w, cps, glyph_of):
    """lettres accentuées : cp -> Gl ; glyph_of(base) donne la lettre de base"""
    M = marks(w); out = {}
    for cp in cps:
        d = ud.normalize('NFD', chr(cp))
        if len(d) < 2 or not all(ord(m) in M for m in d[1:]): continue
        b = d[0]
        if b not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ': continue
        if cp == 0x13D:      # Ľ : un trait droit dans le creux du L
            g = glyph_of('L'); t = round(0.72 * w.S) + 8; x = g.w - t
            out[cp] = Gl(U(g.ink, rect(x, CAP - 150, x + t, CAP)), g.w); continue
        g = glyph_of(b); ink = g.ink; x0, x1 = 0, g.w
        xc = MARKX[b](g, w) if b in MARKX else g.w / 2
        for m in d[1:]:
            mk = M[0x326 if (ord(m) == 0x327 and b in 'GKLNR') else ord(m)]
            if ord(m) in BOT: xc = g.w / 2
            if ord(m) in TOP: mk = mv(mk, xc, CAP + MGAP)
            elif ord(m) == 0x328: mk = mv(mk, g.w - w.S / 2, 0)
            elif ord(m) == 0x327: mk = mv(mk, xc if b not in 'CG' else g.w / 2 + 0, 0)
            else: mk = mv(mk, xc, 0)
            ink = U(ink, mk); bb = bounds(mk); x0 = min(x0, bb[0]); x1 = max(x1, bb[2])
        out[cp] = Gl(mv(ink, -x0), x1 - x0); out[cp].dx = -x0
    return out

def extras(w):
    """Æ Œ Ø Ð Þ ẞ Ł Ħ"""
    S, B, CT, W = w.S, w.B, w.CT, w.W; H = CAP; yb = round(0.68 * H); X = {}
    bar = lambda x0, x1, yc: rect(x0, yc - B / 2, x1, yc + B / 2)
    X[0xC6] = shared(w, 'AE'); X[0x152] = shared(w, 'OE')
    O = letter('O', w); X[0xD8] = Gl(U(O.ink, link(S / 2, round(0.26 * H), W - S / 2, round(0.74 * H), S, S, S)), W)
    e = round(0.26 * CT); Dg = letter('D', w)
    X[0xD0] = Gl(U(mv(Dg.ink, e), bar(0, e + S + round(0.34 * CT), round(0.5 * H))), W + e); X[0x110] = X[0xD0]
    X[0xDE] = Gl(U(rect(0, 0, S, H), bar(0, W, round(0.74 * H)), bar(0, W, round(0.30 * H)), rect(W - S, round(0.30 * H) - B / 2, W, round(0.74 * H) + B / 2)), W)
    ins = round(0.26 * CT); xo = S + round(0.36 * CT)
    X[0x1E9E] = Gl(U(rect(0, 0, S, H), rect(0, H - B, W - ins, H), rect(W - S - ins, yb - B / 2, W - ins, H), bar(xo, W, yb), rect(W - S, 0, W, yb + B / 2), rect(xo, 0, W, B)), W)
    Lg = letter('L', w); e2 = round(0.30 * CT); ym = round(0.46 * H); dl = round(0.07 * H)
    X[0x141] = Gl(U(mv(Lg.ink, e2), I(link(0, ym - dl, e2 + S + round(0.36 * CT), ym + dl, round(0.9 * S), 0, 0), rect(0, 0, 4000, H))), Lg.w + e2)
    e3 = round(0.27 * CT); Hg = letter('H', w)
    X[0x126] = Gl(U(mv(Hg.ink, e3), bar(0, W + 2 * e3, round(0.86 * H))), W + 2 * e3)
    return X
