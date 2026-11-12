# LAMINAR : ponctuation et signes
from lam_core import *
from lam_letters import rcorner
from lam_digits import tangent_pt, strip, hbowl, digits
from lam_letters import letters

def drop(cx, cy, r, tip, flat=0.14):
    """goutte : cercle + tangentes vers la pointe, pointe coupée net"""
    dx, dy = tip[0] - cx, tip[1] - cy; d = math.hypot(dx, dy); a = math.atan2(dy, dx); b = math.acos(r / d)
    t1 = (cx + r * math.cos(a + b), cy + r * math.sin(a + b)); t2 = (cx + r * math.cos(a - b), cy + r * math.sin(a - b))
    body = U(circ(cx, cy, r), poly([t1, tip, t2, (cx, cy)]))
    k = 1 - flat * 2 * r / d; c0 = (cx + dx * k, cy + dy * k); n = (-dy, dx)
    return D(body, half(c0, (c0[0] + n[0], c0[1] + n[1]), 1 if (dx * n[1] - dy * n[0]) < 0 else -1))

def signs(w, c, Gc, Gs, digs, DW):
    """c : jeu des capitales ; Gc, Gs : capitales et petites capitales ; renvoie {nom: Gl}"""
    H, S, h = CAP, c.S, c.h
    tm = round(max(2.2 * h, 0.42 * S + 0.3 * h))       # trait moyen (tirets, signes de calcul)
    rd = round(0.50 * S + 14)                            # rayon du point
    G = {}
    def g(ink, sides='OO', x0=None, x1=None): return Gl(ink, x0, x1, sides)
    dot = lambda x, y: circ(x, y, rd)
    # . , : ; …
    G['period'] = g(dot(rd, rd))
    com = drop(rd, rd, rd, (rd - 0.55 * rd, -1.55 * rd - 40))
    G['comma'] = g(com)
    yc = round(0.62 * SC)
    G['colon'] = g(U(dot(rd, rd), dot(rd, yc)))
    G['semicolon'] = g(U(com, dot(rd, yc)))
    sp = round(2 * rd + 0.9 * rd)
    G['ellipsis'] = g(U(dot(rd, rd), dot(rd + sp, rd), dot(rd + 2 * sp, rd)))
    # ! ? ¡ ¿
    ex = U(rect(rd - S / 2, 2 * rd + round(0.10 * H), rd + S / 2, H), dot(rd, rd))
    G['exclam'] = g(ex); G['exclamdown'] = g(mv(rot(ex, 180, rd, H / 2), 0, -round(0.20 * H)))
    rq = round(0.26 * H); qcx = rq; qcy = H - rq
    qbowl = I(ring_off(qcx, qcy, rq, round(1.06 * S), h, 1), U(rect(-100, qcy, 3000, 3000), rect(qcx, -100, 3000, qcy + 1)))
    qx = qcx - S / 2 + round(0.08 * rq)
    qstem = rect(qx + 0.0, 2 * rd + round(0.08 * H), qx + S, qcy - rq + h)
    qbar = rect(qx, qcy - rq, qcx + 1, qcy - rq + h)
    q = U(qbowl, qstem, qbar, dot(qx + S / 2, rd))
    G['question'] = g(q); G['questiondown'] = g(mv(rot(q, 180, rq, H / 2), 0, -round(0.20 * H)))
    # tirets
    ym = round(0.40 * SC)
    G['hyphen'] = g(rect(0, ym - tm / 2, round(0.24 * H), ym + tm / 2))
    G['endash'] = g(rect(0, ym - tm / 2, round(0.50 * H), ym + tm / 2))
    G['emdash'] = g(rect(0, ym - tm / 2, round(1.00 * H), ym + tm / 2))
    G['underscore'] = g(rect(0, -round(0.12 * H) - tm, round(0.60 * H), -round(0.12 * H)))
    # apostrophes et guillemets
    qr = round(0.82 * rd)
    q1 = drop(qr, H - qr, qr, (qr - 0.55 * qr, H - 2 * qr - 1.3 * qr - 30))
    G['quoteright'] = g(q1); G['quoteleft'] = g(rot(q1, 180, qr, H - qr - (1.3 * qr + 30) / 2 - qr / 2))
    G['quotesinglbase'] = g(mv(q1, 0, -(H - 2 * qr)))
    dq = round(2 * qr + 0.7 * qr)
    G['quotedblright'] = g(U(q1, mv(q1, dq))); G['quotedblleft'] = g(U(G['quoteleft'].ink, mv(G['quoteleft'].ink, dq)))
    G['quotedblbase'] = g(U(G['quotesinglbase'].ink, mv(G['quotesinglbase'].ink, dq)))
    ts = round(0.62 * S); tl = round(0.26 * H)
    qs = poly([(0, H), (ts, H), (ts * 0.72, H - tl), (ts * 0.28, H - tl)])
    G['quotesingle'] = g(qs); G['quotedbl'] = g(U(qs, mv(qs, ts + round(0.55 * ts) + 8)))
    # guillemets : chevrons pleins
    def chev(wc, hc, t):
        wv = hw(t, wc, hc / 2)
        up = diag(0, wc - wv, wv, 0, hc / 2)
        return I(U(up, flipv(up, hc / 2)), rect(-10, -10, wc - 0.35 * wv, hc + 10))
    hc = round(0.50 * SC); wc = round(0.24 * H); tc = round(0.42 * S + 6)
    cv = mirror(chev(wc, hc, tc), wc / 2); yb = ym - hc / 2
    cvR = mv(chev(wc, hc, tc), 0, yb); cvL = mv(cv, 0, yb)
    G['guilsinglleft'] = g(cvL); G['guilsinglright'] = g(cvR)
    dg = round(0.50 * wc + 0.6 * tc)
    G['guillemotleft'] = g(U(cvL, mv(cvL, dg))); G['guillemotright'] = g(U(cvR, mv(cvR, dg)))
    # parenthèses : arcs au compas ; crochets ; accolades
    pr = round(0.95 * H); pcy = H / 2 + round(0.02 * H); ph = round(0.62 * H)
    tp = round(0.55 * S + 0.45 * h + 6)
    pa = I(D(circ(pr, pcy, pr), circ(pr + round(0.35 * tp), pcy, pr - tp)), rect(-10, pcy - ph, pr, pcy + ph))
    G['parenleft'] = g(pa); G['parenright'] = g(mirror(pa, pr / 2 * 0 + bounds(pa)[2] / 2 + bounds(pa)[0] / 2))
    by0, by1 = round(-0.14 * H), round(1.06 * H); bw = round(0.22 * H)
    bl = U(rect(0, by0, round(0.62 * S), by1), rect(0, by1 - h, bw, by1), rect(0, by0, bw, by0 + h))
    G['bracketleft'] = g(bl, 'SO'); G['bracketright'] = g(mirror(bl, bw / 2), 'OS')
    tb = round(0.55 * S); nose = round(0.10 * H)
    br = U(rect(nose, by0, nose + tb, by1), rect(nose, by1 - h, nose + bw, by1), rect(nose, by0, nose + bw, by0 + h),
           rect(0, (by0 + by1) / 2 - h, nose + 1, (by0 + by1) / 2 + h))
    G['braceleft'] = g(br, 'OO'); G['braceright'] = g(mirror(br, (nose + bw) / 2), 'OO')
    # / \ |
    sw = round(0.42 * H); ws = hw(round(0.55 * S + 4), sw, H - by0 * 0)
    sl = I(diag(0, sw - ws, ws, round(-0.10 * H), round(1.04 * H)), rect(-10, -0.10 * H, 3000, 1.04 * H))
    G['slash'] = g(sl, 'DD'); G['backslash'] = g(mirror(sl, sw / 2), 'DD')
    G['bar'] = g(rect(0, by0, round(0.42 * S + 8), by1), 'SS')
    G['brokenbar'] = g(D(G['bar'].ink, rect(-10, H / 2 - 0.06 * H, 1000, H / 2 + 0.06 * H)), 'SS')
    # signes de calcul
    mw = round(0.52 * H); mc = round(0.40 * SC) + 0; L = mw / 2
    hbar = rect(0, mc - tm / 2, mw, mc + tm / 2); vbar = rect(L - tm / 2, mc - L, L + tm / 2, mc + L)
    G['plus'] = g(U(hbar, vbar)); G['uni2212'] = g(hbar)
    G['multiply'] = g(rot(U(rect(0.12 * mw, mc - tm / 2, 0.88 * mw, mc + tm / 2), rect(L - tm / 2, mc - 0.38 * mw, L + tm / 2, mc + 0.38 * mw)), 45, L, mc))
    gq = round(0.36 * mw)
    G['equal'] = g(U(mv(hbar, 0, gq / 2), mv(hbar, 0, -gq / 2)))
    dr = round(0.9 * tm)
    G['divide'] = g(U(hbar, circ(L, mc + 0.32 * mw, dr), circ(L, mc - 0.32 * mw, dr)))
    lw = hw(tm, mw, L)
    le = U(poly([(0, mc - tm / 2), (mw, mc - L), (mw, mc - L + lw * (L / mw) * 0 + tm * 1.15), (tm * 1.6, mc)]),
           poly([(0, mc + tm / 2), (mw, mc + L), (mw, mc + L - tm * 1.15), (tm * 1.6, mc)]))
    le = U(le, poly([(0, mc - tm / 2), (tm * 1.6, mc), (0, mc + tm / 2)]))
    G['less'] = g(le); G['greater'] = g(mirror(le, mw / 2))
    G['asciitilde'] = None
    # ~ ^
    rt = round(0.13 * H); tt = tm
    til = U(I(D(circ(rt, mc, rt), circ(rt, mc, rt - tt)), rect(-10, mc, 1000, 1000)), I(D(circ(3 * rt - tt, mc, rt), circ(3 * rt - tt, mc, rt - tt)), rect(-10, -1000, 1000, mc)))
    G['asciitilde'] = g(til)
    ch = round(0.30 * H); cw = round(0.42 * H); wcv = hw(tm, cw / 2, ch)
    cir = U(diag(0, cw / 2 - wcv / 2, wcv, H - ch, H), diag(cw - wcv, cw / 2 - wcv / 2, wcv, H - ch, H))
    G['asciicircum'] = g(cir)
    # * #
    ar = round(0.20 * H); acy = H - ar
    spoke = rect(-tm / 2 * 0.9, 0, tm / 2 * 0.9, ar)
    ast = U(*[mv(rot(spoke, a, 0, 0), ar, acy) for a in (0, 72, 144, 216, 288)])
    G['asterisk'] = g(ast)
    nw = round(0.56 * H); nv = round(0.50 * S + 6); sl_ = round(0.10 * H)
    ns = U(I(diag(round(0.18 * nw), round(0.18 * nw) + sl_, nv, 0, H), rect(-10, 0, 2000, H)),
           I(diag(round(0.60 * nw), round(0.60 * nw) + sl_, nv, 0, H), rect(-10, 0, 2000, H)),
           rect(0, round(0.32 * H), nw, round(0.32 * H) + h * 1.6), rect(0, round(0.64 * H), nw, round(0.64 * H) + h * 1.6))
    G['numbersign'] = g(ns)
    # $ ¢ € £ ¥
    Sg = Gc['S']; sb = bounds(Sg.ink); lx = (sb[0] + sb[2]) / 2
    G['dollar'] = g(U(Sg.ink, rect(lx - h * 1.5, -0.10 * H, lx + h * 1.5, 1.10 * H)), 'OO', sb[0], sb[2])
    Cs = Gs['C']; cb = bounds(Cs.ink); cx = cb[2] * 0.52
    G['cent'] = g(U(Cs.ink, rect(cx - h * 1.5, -0.10 * SC, cx + h * 1.5, 1.10 * SC)), 'OO', cb[0], cb[2])
    Cc = Gc['C']; ccb = bounds(Cc.ink)
    eb = lambda y: rect(-round(0.08 * H), y - h, round(0.62 * ccb[2]), y + h)
    G['Euro'] = g(U(Cc.ink, eb(0.40 * H), eb(0.58 * H)), 'OO')
    lw2 = round(0.56 * H); rlb = round(0.20 * H); xs = round(0.16 * H)
    hook = I(ring_off(xs + rlb, H - rlb, rlb, S, h, -1), U(rect(-100, H - rlb, 3000, 3000)))
    hook = I(hook, rect(-100, -100, xs + rlb + 0.75 * rlb, 3000))
    lb = U(rect(xs, 0, xs + S, H - rlb + 1), hook, rect(0, 0, lw2, h), rect(0, round(0.42 * H), xs + S + round(0.20 * H), round(0.42 * H) + h))
    G['sterling'] = g(lb)
    Yg = Gc['Y']; yb_ = bounds(Yg.ink)
    G['yen'] = g(U(Yg.ink, rect(yb_[2] * 0.14, 0.30 * H, yb_[2] * 0.86, 0.30 * H + h), rect(yb_[2] * 0.14, 0.18 * H, yb_[2] * 0.86, 0.18 * H + h)), 'DD', yb_[0], yb_[2])
    # % ‰
    pr0 = round(0.16 * H); pt_ = round(0.55 * S + 4)
    o_ = lambda x, y: ring_off(x, y, pr0, pt_, h, -1)
    pw = round(0.60 * H)
    psl = I(diag(round(0.06 * pw), pw - round(0.06 * pw) - hw(round(0.45 * S + 4), pw, H), hw(round(0.45 * S + 4), pw, H), 0, H), rect(-10, 0, 3000, H))
    G['percent'] = g(U(o_(pr0, H - pr0), o_(pw - pr0, pr0), psl))
    G['perthousand'] = g(U(o_(pr0, H - pr0), o_(pw - pr0, pr0), o_(pw + pr0 + round(0.04 * H), pr0), psl))
    # & : anneau haut, anneau bas, jambe pleine
    rb_ = round(0.30 * H); rt_ = round(0.20 * H); aw = round(0.70 * H)
    lowr = ring_off(rb_, rb_, rb_, round(1.06 * S), h, -1)
    upr = ring_off(rb_ - round(0.02 * H), H - rt_, rt_, round(0.9 * S), h, -1)
    legw = hw(round(0.93 * S), aw - rb_, H - rt_ - 0)
    leg = I(diag(aw - legw, round(rb_ - 0.02 * H + 0.10 * rt_), legw, 0, H - rt_ * 1.0), rect(-10, 0, 3000, H))
    leg = D(leg, D(circ(rb_ - round(0.02 * H), H - rt_, rt_ - round(0.9 * S) * 0.5), rect(-10, 0, 3000, H - rt_ - 2)))
    arm = rect(rb_, round(0.40 * H), aw, round(0.40 * H) + h)
    G['ampersand'] = g(U(I(lowr, D(rect(-100, -100, 3000, 3000), rect(rb_ + 0.55 * rb_, rb_ - 0.2 * rb_, 3000, 3000))), upr, leg, arm))
    # @ : anneau et A
    ra = round(0.48 * H); acx, acy = ra, round(0.40 * H)
    ringa = ring_off(acx, acy, ra, round(0.55 * S + 6), h, -1)
    sm = lambda Hm, km: letters(C(w, Hm, sc=True, S=km * S + 6))          # petites lettres dessinées à leur taille (le délié reste un délié)
    Gm = sm(round(0.46 * H), 0.50)
    ai = Gm['A'].ink; ab = bounds(ai); ai = mv(ai, acx - (ab[0] + ab[2]) / 2 + round(0.04 * ra), acy - (ab[1] + ab[3]) / 2)
    G['at'] = g(U(ringa, ai))
    # § ¶
    # § : crochet haut (demi-anneau gauche), anneau du milieu, crochet bas (demi-anneau droit)
    y0s, y1s = round(-0.10 * H), H; rs = (y1s - y0s + 2 * h) / 6; SOs = round(0.9 * S)
    ct, cm_, cb_ = y1s - rs, y1s - 3 * rs + h, y1s - 5 * rs + 2 * h
    rg = lambda cy_: D(circ(rs, cy_, rs), ell(rs, cy_, rs - SOs, rs - h))
    xt_ = round(1.62 * rs); xb_ = round(0.38 * rs); tsp = round(0.8 * S); hsp = round(0.55 * rs)
    G['section'] = g(U(I(rg(ct), rect(-10, ct - rs - 1, rs, ct + rs + 1)), rect(rs - 1, y1s - h, xt_, y1s), rect(xt_ - tsp, y1s - hsp, xt_, y1s),
                       rg(cm_), I(rg(cb_), rect(rs, cb_ - rs - 1, 3000, cb_ + rs + 1)), rect(xb_, y0s, rs + 1, y0s + h), rect(xb_, y0s, xb_ + tsp, y0s + hsp)))
    pp = round(0.20 * H)
    para = U(rect(2 * pp, -0.12 * H, 2 * pp + round(0.5 * S), H), rect(2 * pp + round(0.5 * S) + round(0.12 * H), -0.12 * H, 2 * pp + round(0.5 * S) + round(0.12 * H) + h * 2, H),
             rect(2 * pp, H - h, 2 * pp + round(0.5 * S) + round(0.12 * H) + h * 2, H), I(circ(2 * pp, H - pp * 1.15, pp * 1.15), rect(-10, -10, 2 * pp + 1, 3000)))
    G['paragraph'] = g(para)
    # © ® ™ ° • ·
    rc = round(0.42 * H); ccy = H / 2
    rng = D(circ(rc, ccy, rc), circ(rc, ccy, rc - round(0.6 * h + 0.18 * S)))
    Gr = sm(round(0.44 * H), 0.55)
    def inside(gl):
        b = bounds(gl.ink); return mv(gl.ink, rc - (b[0] + b[2]) / 2, ccy - (b[1] + b[3]) / 2)
    G['copyright'] = g(U(rng, inside(Gr['C'])))
    G['registered'] = g(U(rng, inside(Gr['R'])))
    Gt = sm(round(0.40 * H), 0.45); Ht = round(0.40 * H)
    tT = mv(Gt['T'].ink, 0, H - Ht); tb_ = bounds(tT)
    mM = mv(Gt['M'].ink, tb_[2] + round(0.04 * H), H - Ht)
    G['trademark'] = g(U(tT, mM))
    G['degree'] = g(ring_off(round(0.13 * H), H - round(0.13 * H), round(0.13 * H), round(0.45 * S + 4), h, -1))
    G['bullet'] = g(circ(round(0.9 * rd + 10), ym, round(0.9 * rd + 10)))
    G['periodcentered'] = g(circ(rd, ym, rd))
    G['uni00B7'] = None
    del G['uni00B7']
    # № : N + o souligné
    Nn = Gc['N']; nb = bounds(Nn.ink); ro_ = round(0.13 * H); ox = nb[2] + round(0.06 * H) + ro_
    G['numero'] = g(U(Nn.ink, ring_off(ox, H - ro_ - round(0.10 * H), ro_, round(0.5 * S + 4), h, -1), rect(ox - ro_, H - round(0.62 * H), ox + ro_, H - round(0.62 * H) + h * 1.6)), 'SO')
    # fractions, exposants
    Hs_ = round(0.52 * H); dsm, _ = digits(C(w, Hs_, sc=True, S=0.55 * S + 6))
    sup = {n: mv(dsm[n], 0, H - Hs_) for n in ('one', 'two', 'three', 'four')}
    G['onesuperior'] = g(sup['one']); G['twosuperior'] = g(sup['two']); G['threesuperior'] = g(sup['three'])
    fw_ = hw(round(0.40 * S + 4), round(0.40 * H), H)
    fsl = I(diag(0, round(0.40 * H) - fw_, fw_, 0, H), rect(-10, 0, 3000, H))
    def frac(a, b):
        A = sup[a]; ab_ = bounds(A); Bb = dsm[b]; bb_ = bounds(Bb)
        x1 = ab_[2] - round(0.10 * H); x2 = x1 + round(0.40 * H) - round(0.10 * H)
        return U(A, mv(fsl, x1), mv(Bb, x2 - bb_[0]))
    G['onehalf'] = g(frac('one', 'two')); G['onequarter'] = g(frac('one', 'four')); G['threequarters'] = g(frac('three', 'four'))
    G = {k_: v for k_, v in G.items() if v is not None}
    return G
