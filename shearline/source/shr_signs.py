# SHEARLINE : chiffres, ponctuation, signes et signes liturgiques (à la plume)
from shr_core import *
from shr_lower import Cross, Wt

def wsmall(w, scale, kW):
    """plume pour un dessin qu'on réduira de scale : après réduction, plume kW·W et fil d'origine"""
    return Wt(w.name, kW * w.W / scale, w.t / scale)

DN = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']

def digits(w, H=CAP * 0.92):
    """chiffres de la hauteur des capitales (un peu plus bas), tous de la même chasse"""
    k, yb, pen = w.k, w.yb, w.pen; st = pen.stroke
    D = 1.0 * w.s + 0.25 * w.W; yt = H - 0.32 * w.W; G = {}
    G['zero'] = st([(0.45 * D, yt), (0, yt - 0.35 * D), (0, yb + 0.35 * D), (0.45 * D, yb), (0.9 * D, yb + 0.35 * D), (0.9 * D, yt - 0.35 * D), (0.45 * D, yt)])
    G['one'] = st([(0.15 * D, yt - 0.3 * D), (0.55 * D, yt), (0.55 * D, yb + k), (0.55 * D + k, yb)])
    G['two'] = st([(0.05 * D, yt - 0.25 * D), (0.4 * D, yt), (0.85 * D, yt - 0.3 * D), (0.85 * D, 0.55 * H), (0.05 * D, yb), (0.9 * D, yb + 0.06 * D)])
    G['three'] = st([(0.05 * D, yt - 0.2 * D), (0.4 * D, yt), (0.85 * D, yt - 0.25 * D), (0.4 * D, 0.55 * H), (0.9 * D, 0.4 * H), (0.9 * D, yb + 0.3 * D), (0.45 * D, yb), (0, yb + 0.2 * D)])
    G['four'] = U(st([(0.65 * D, yt), (0.0, 0.33 * H), (0.95 * D, 0.33 * H)]), st([(0.65 * D, yt), (0.65 * D, yb + k), (0.65 * D + k, yb)]))
    G['five'] = U(st([(0.15 * D, yt), (0.9 * D, yt + 0.02 * D)]), st([(0.15 * D, yt), (0.1 * D, 0.55 * H), (0.5 * D, 0.62 * H), (0.9 * D, 0.45 * H), (0.9 * D, yb + 0.3 * D), (0.45 * D, yb), (0, yb + 0.2 * D)]))
    six = st([(0.85 * D, yt - 0.1 * D), (0.5 * D, yt), (0, yt - 0.45 * D), (0, yb + 0.3 * D), (0.45 * D, yb), (0.9 * D, yb + 0.3 * D), (0.9 * D, 0.45 * H), (0.45 * D, 0.6 * H), (0.0, 0.45 * H)])
    G['six'] = six
    b = bounds(six); G['nine'] = xf(six, (-1, 0, 0, -1, b[0] + b[2], b[1] + b[3]))
    G['seven'] = st([(0.05 * D, yt), (0.9 * D, yt), (0.35 * D, yb)])
    G['eight'] = st([(0.45 * D, yt), (0.08 * D, yt - 0.25 * D), (0.08 * D, 0.62 * H), (0.9 * D, 0.38 * H), (0.9 * D, yb + 0.3 * D), (0.45 * D, yb), (0, yb + 0.3 * D), (0, 0.38 * H),
                     (0.82 * D, 0.62 * H), (0.82 * D, yt - 0.25 * D), (0.45 * D, yt)])
    return G, D

def diamond(pen, x, y, k):
    """point en losange : un coup de plume court, de travers"""
    return pen.stroke([(x - 0.35 * k, y + 0.4 * k), (x + 0.35 * k, y - 0.4 * k)])

def signs(w, Gl, Gc, digs):
    s, k, yb, yt, pen = w.s, w.k, w.yb, w.yt, w.pen; st = pen.stroke; G = {}
    py = 0.42 * w.W                                     # axe du point
    dot = lambda x, y=py: diamond(pen, x, y, 1.6 * k)
    G['period'] = dot(0)
    com = st([(0.25 * k, py + 0.5 * k), (0.35 * k, py - 0.2 * k), (-0.35 * k, -0.9 * k - 0.15 * s)])
    G['comma'] = com
    yc2 = XH - 0.42 * w.W
    G['colon'] = U(dot(0), dot(0, yc2)); G['semicolon'] = U(com, dot(0, yc2))
    G['ellipsis'] = U(dot(0), dot(0.75 * s), dot(1.5 * s))
    G['exclam'] = U(st([(-k, w.yc), (0, w.yc - 1.2 * k), (0, 2 * py + 0.25 * s)]), dot(0))
    G['exclamdown'] = mv(xf(G['exclam'], (-1, 0, 0, -1, 0, XH)), 0, -0.15 * CAP)
    q = U(st([(-0.1 * s, w.yc - 0.25 * s), (0.3 * s, w.yc), (0.75 * s, w.yc - 0.3 * s), (0.25 * s, 0.4 * CAP), (0.25 * s, 2 * py + 0.25 * s)]), dot(0.25 * s))
    G['question'] = q
    bq = bounds(q); G['questiondown'] = mv(xf(q, (-1, 0, 0, -1, bq[0] + bq[2], XH)), 0, -0.15 * CAP)
    # tirets : le trait d'union de la Fraktur est double et penché
    hy = U(st([(0, 0.40 * XH), (0.32 * s, 0.50 * XH)]), st([(0, 0.62 * XH), (0.32 * s, 0.72 * XH)]))
    G['hyphen'] = hy
    G['endash'] = st([(0, 0.5 * XH), (0.9 * s, 0.5 * XH)]); G['emdash'] = st([(0, 0.5 * XH), (2.0 * s, 0.5 * XH)])
    G['underscore'] = st([(0, -0.18 * CAP), (1.6 * s, -0.18 * CAP)])
    # apostrophes et guillemets
    qr = st([(0.25 * k, CAP - 0.3 * k), (0.35 * k, CAP - 0.9 * k), (-0.35 * k, CAP - 1.9 * k - 0.15 * s)])
    G['quoteright'] = qr; G['quoteleft'] = xf(qr, (-1, 0, 0, -1, 0, 2 * CAP - 2.1 * k - 0.15 * s))
    G['quotesinglbase'] = mv(qr, 0, -(CAP - 0.3 * k) + py + 0.5 * k)
    dq = 0.55 * s
    for n, b in (('quotedblright', 'quoteright'), ('quotedblleft', 'quoteleft'), ('quotedblbase', 'quotesinglbase')): G[n] = U(G[b], mv(G[b], dq))
    G['quotesingle'] = st([(0, CAP), (0, CAP - 0.3 * CAP)]); G['quotedbl'] = U(G['quotesingle'], mv(G['quotesingle'], 0.45 * s))
    chev = lambda d: st([(0.35 * s * d, 0.75 * XH), (0, 0.45 * XH), (0.35 * s * d, 0.15 * XH)])
    G['guilsinglleft'] = mv(chev(1), 0); G['guilsinglright'] = mv(chev(-1), 0.35 * s)
    G['guillemotleft'] = U(G['guilsinglleft'], mv(G['guilsinglleft'], 0.4 * s)); G['guillemotright'] = U(G['guilsinglright'], mv(G['guilsinglright'], 0.4 * s))
    # parenthèses, crochets, accolades
    pa = st([(0.4 * s, 1.0 * CAP), (0.05 * s, 0.70 * CAP), (0.05 * s, 0.05 * CAP), (0.4 * s, -0.22 * CAP)])
    G['parenleft'] = pa; bp = bounds(pa); G['parenright'] = mirror(pa, (bp[0] + bp[2]) / 2)
    bl = U(st([(0.0, 1.0 * CAP), (0.0, -0.22 * CAP)]), st([(0.0, 1.0 * CAP), (0.45 * s, 1.0 * CAP)]), st([(0.0, -0.22 * CAP), (0.45 * s, -0.22 * CAP)]))
    G['bracketleft'] = bl; bb = bounds(bl); G['bracketright'] = mirror(bl, (bb[0] + bb[2]) / 2)
    br = st([(0.45 * s, 1.0 * CAP), (0.15 * s, 0.85 * CAP), (0.15 * s, 0.5 * CAP), (-0.1 * s, 0.39 * CAP), (0.15 * s, 0.28 * CAP), (0.15 * s, -0.05 * CAP), (0.45 * s, -0.22 * CAP)])
    G['braceleft'] = br; bb = bounds(br); G['braceright'] = mirror(br, (bb[0] + bb[2]) / 2)
    G['slash'] = st([(0, -0.15 * CAP), (0.7 * s, CAP)]); G['backslash'] = st([(0, CAP), (0.7 * s, -0.15 * CAP)])
    G['bar'] = st([(0, CAP), (0, -0.22 * CAP)]); G['brokenbar'] = U(st([(0, CAP), (0, 0.48 * CAP)]), st([(0, 0.3 * CAP), (0, -0.22 * CAP)]))
    # calcul : traits à la plume, même chasse
    mw = 1.0 * s; mc = 0.42 * XH + 0.12 * XH; L = mw / 2
    th = lambda y, x0=0, x1=mw: st([(x0, y), (x1, y)])
    G['plus'] = U(th(mc), st([(L, mc - L), (L, mc + L)])); G['uni2212'] = th(mc)
    G['multiply'] = U(st([(0.15 * mw, mc - 0.35 * mw), (0.85 * mw, mc + 0.35 * mw)]), st([(0.15 * mw, mc + 0.35 * mw), (0.85 * mw, mc - 0.35 * mw)]))
    G['equal'] = U(th(mc - 0.17 * mw), th(mc + 0.17 * mw))
    G['divide'] = U(th(mc), dot(L, mc + 0.35 * mw), dot(L, mc - 0.35 * mw))
    G['less'] = st([(mw, mc + 0.4 * mw), (0, mc), (mw, mc - 0.4 * mw)]); G['greater'] = st([(0, mc + 0.4 * mw), (mw, mc), (0, mc - 0.4 * mw)])
    G['asciitilde'] = st([(0, mc - 0.05 * mw), (0.3 * mw, mc + 0.12 * mw), (0.7 * mw, mc - 0.12 * mw), (mw, mc + 0.05 * mw)])
    G['asciicircum'] = st([(0, 0.75 * CAP), (0.35 * s, CAP), (0.7 * s, 0.75 * CAP)])
    # * : une croix pattée à six branches
    ar = 0.32 * s; acy = CAP - ar - 0.05 * s
    G['asterisk'] = U(*[xf(bar_pattee(0, 0, 2 * ar, 0.35 * ar, 2.0), (math.cos(math.radians(a)), math.sin(math.radians(a)), -math.sin(math.radians(a)), math.cos(math.radians(a)), ar, acy))
                        for a in (90, 30, 150)])
    nw = 1.1 * s
    G['numbersign'] = U(st([(0.3 * nw, 0), (0.42 * nw, CAP * 0.85)]), st([(0.62 * nw, 0), (0.74 * nw, CAP * 0.85)]), th(0.3 * CAP, 0, nw), th(0.58 * CAP, 0.05 * nw, 1.05 * nw))
    # monnaies
    Sg = Gc['S']; sb = bounds(Sg); lx = (sb[0] + sb[2]) / 2
    G['dollar'] = U(Sg, rect(lx - 0.9 * w.t, -0.12 * CAP, lx + 0.9 * w.t, 1.08 * CAP))
    cc = Gl['c']; cb = bounds(cc); G['cent'] = U(cc, rect(cb[2] * 0.5 - 0.9 * w.t, -0.12 * XH, cb[2] * 0.5 + 0.9 * w.t, 1.15 * XH))
    Cc = Gc['C']; ccb = bounds(Cc); G['Euro'] = U(D(Cc, rect(ccb[0] + 0.25 * (ccb[2] - ccb[0]), 0.2 * CAP, ccb[2], 0.8 * CAP)) if False else Cc,
                                                  th(0.42 * CAP, ccb[0] - 0.15 * s, ccb[0] + 0.6 * (ccb[2] - ccb[0])), th(0.6 * CAP, ccb[0] - 0.15 * s, ccb[0] + 0.6 * (ccb[2] - ccb[0])))
    G['sterling'] = U(st([(0.95 * s, w.yc - 0.15 * s), (0.65 * s, w.yc), (0.3 * s, w.yc - 0.2 * s), (0.3 * s, 0.25 * CAP), (0.0, w.yb), (1.1 * s, w.yb)]), th(0.45 * CAP, 0.0, 0.75 * s))
    Yg = Gc['Y']; yb_ = bounds(Yg); G['yen'] = U(Yg, th(0.36 * CAP, yb_[0], yb_[2] * 0.9))
    o = lambda x, y, r: st([(x, y + r), (x - 0.75 * r, y + 0.1 * r), (x - 0.75 * r, y - 0.4 * r), (x, y - r), (x + 0.75 * r, y - 0.1 * r), (x + 0.75 * r, y + 0.4 * r), (x, y + r)])
    rr = 0.2 * CAP
    G['percent'] = U(o(0.2 * s, CAP - rr, rr), o(1.0 * s, rr, rr), st([(0.05 * s, 0.02 * CAP), (1.15 * s, 0.98 * CAP)]))
    G['perthousand'] = U(G['percent'], o(1.75 * s, rr, rr))
    # & : « et » à la plume (un e et un t liés)
    G['ampersand'] = U(st([(0.1 * s, 0.5 * CAP), (0.8 * s, 0.62 * CAP), (0.8 * s, 0.72 * CAP), (0.55 * s, w.yc), (0.25 * s, w.yc), (0, w.yc - 0.4 * s), (0, yb + 0.35 * s),
                          (0.3 * s, yb), (0.85 * s, yb + 0.25 * s)]),
                       st([(1.15 * s - k, w.yc - 0.1 * s), (1.15 * s, w.yc - 0.1 * s - 1.2 * k), (1.15 * s, yb + 0.3 * s), (1.45 * s, yb), (1.85 * s, yb + 0.25 * s)]),
                       bar_latin(1.2 * s, 0.6 * CAP, 1.1 * s, w.tb))
    # @ : un a dans un cercle brisé
    ra = 0.55 * CAP; acx, acy2 = ra, 0.42 * CAP
    ring = st([(acx, acy2 + ra), (acx - 0.8 * ra, acy2 + 0.45 * ra), (acx - 0.8 * ra, acy2 - 0.45 * ra), (acx, acy2 - ra), (acx + 0.85 * ra, acy2 - 0.6 * ra)])
    ring = U(ring, st([(acx + 0.8 * ra, acy2 - 0.2 * ra), (acx + 0.8 * ra, acy2 + 0.45 * ra), (acx, acy2 + ra)]))
    a_ = Gl['a']; ab = bounds(a_); G['at'] = U(ring, mv(a_, acx - (ab[0] + ab[2]) / 2, acy2 - (ab[1] + ab[3]) / 2))
    # § ¶
    G['section'] = st([(0.75 * s, w.yc - 0.12 * s), (0.45 * s, w.yc), (0.1 * s, w.yc - 0.25 * s), (0.1 * s, 0.62 * CAP), (0.75 * s, 0.5 * CAP), (0.75 * s, 0.38 * CAP),
                       (0.1 * s, 0.28 * CAP), (0.1 * s, 0.16 * CAP), (0.75 * s, 0.05 * CAP), (0.75 * s, -0.08 * CAP), (0.4 * s, -0.18 * CAP), (0.05 * s, -0.08 * CAP)])
    G['paragraph'] = U(st([(0.55 * s, w.yc), (0.15 * s, w.yc - 0.05 * s), (0.0, 0.62 * CAP), (0.25 * s, 0.45 * CAP), (0.6 * s, 0.45 * CAP)]),
                       st([(0.6 * s, w.yc), (0.6 * s, -0.2 * CAP)]), st([(1.0 * s, w.yc), (1.0 * s, -0.2 * CAP)]), st([(0.55 * s, w.yc), (1.1 * s, w.yc)]))
    # © ® ™ ° • ·
    rc = 0.48 * CAP; ccy = 0.5 * CAP
    rng = st([(rc, ccy + rc), (rc - 0.85 * rc, ccy + 0.5 * rc), (rc - 0.85 * rc, ccy - 0.5 * rc), (rc, ccy - rc), (rc + 0.85 * rc, ccy - 0.5 * rc), (rc + 0.85 * rc, ccy + 0.5 * rc), (rc, ccy + rc)])
    def inside(g, kk):
        b = bounds(g); return xf(g, (kk, 0, 0, kk, rc - kk * (b[0] + b[2]) / 2, ccy - kk * (b[1] + b[3]) / 2))
    G['copyright'] = U(rng, inside(Gl['c'], 0.9)); G['registered'] = U(rng, inside(Gl['r'], 0.9))
    from shr_caps import caps
    Cm = caps(wsmall(w, 0.42, 0.55), 'none'); tT = xf(Cm['T'], (0.42, 0, 0, 0.42, 0, 0.58 * CAP)); tb_ = bounds(tT)
    mM = xf(Cm['M'], (0.42, 0, 0, 0.42, 0, 0.58 * CAP)); mb_ = bounds(mM)
    G['trademark'] = U(tT, mv(mM, tb_[2] - mb_[0] + 0.06 * s))
    G['degree'] = o(0.25 * s, CAP - 0.16 * CAP, 0.16 * CAP)
    G['bullet'] = diamond(pen, 0, 0.5 * XH, 2.2 * k); G['periodcentered'] = dot(0, 0.5 * XH)
    Nn = Gc['N']; nb = bounds(Nn)
    G['uni2116'] = U(Nn, o(nb[2] + 0.35 * s, CAP - 0.25 * CAP, 0.17 * CAP), th(0.32 * CAP, nb[2] + 0.12 * s, nb[2] + 0.6 * s))
    # exposants et fractions : chiffres réduits, plume réduite
    kk = 0.55; dsm, _ = digits(wsmall(w, kk, 0.62))
    sup = {n: xf(dsm[n], (kk, 0, 0, kk, 0, CAP - kk * CAP * 0.92)) for n in ('one', 'two', 'three', 'four')}
    G['onesuperior'] = sup['one']; G['twosuperior'] = sup['two']; G['threesuperior'] = sup['three']
    fsl = st([(0, 0), (0.6 * s, CAP)])
    def frac(a, b_):
        A = sup[a]; ab_ = bounds(A); Bd = xf(dsm[b_], (kk, 0, 0, kk, 0, 0)); bd = bounds(Bd)
        x1 = ab_[2] - 0.05 * s; return U(A, mv(fsl, x1), mv(Bd, x1 + 0.6 * s - bd[0] - 0.05 * s))
    G['onehalf'] = frac('one', 'two'); G['onequarter'] = frac('one', 'four'); G['threequarters'] = frac('three', 'four')
    # signes liturgiques
    vr = w.tb * 1.1
    G['dagger'] = U(rect(-vr / 2, -0.12 * CAP, vr / 2, CAP), bar_latin(0, 0.68 * CAP, 0.85 * s, w.tb * 1.1))
    G['daggerdbl'] = U(rect(-vr / 2, -0.12 * CAP, vr / 2, CAP), bar_latin(0, 0.72 * CAP, 0.85 * s, w.tb * 1.1), bar_latin(0, 0.18 * CAP, 0.85 * s, w.tb * 1.1))
    G['uni271D'] = U(rect(-vr, -0.05 * CAP, vr, CAP), bar_latin(0, 0.68 * CAP, 1.1 * s, 2 * vr))                       # ✝ croix latine
    G['uni2626'] = U(rect(-vr / 2, -0.05 * CAP, vr / 2, CAP), bar_latin(0, 0.84 * CAP, 0.55 * s, w.tb), bar_latin(0, 0.64 * CAP, 1.0 * s, w.tb),
                     poly([(-0.32 * s, 0.24 * CAP - w.tb / 2), (0.32 * s, 0.14 * CAP - w.tb / 2), (0.32 * s, 0.14 * CAP + w.tb / 2), (-0.32 * s, 0.24 * CAP + w.tb / 2)]))  # ☦ orthodoxe
    pt = lambda cx_, cy_, r: U(bar_pattee(cx_, cy_, 2 * r, 0.32 * r, 2.6), xf(bar_pattee(0, 0, 2 * r, 0.32 * r, 2.6), (0, 1, -1, 0, cx_, cy_)))
    R = 0.5 * CAP
    G['uni2720'] = pt(R, 0.45 * CAP, R)                                                                              # ✠ croix de Malte
    G['uni2629'] = U(rect(R - vr, -0.05 * CAP + 0.0, R + vr, CAP - 0.05 * CAP), rect(0, 0.45 * CAP - vr, 2 * R, 0.45 * CAP + vr),
                     *[bar_latin(R + dx, 0.45 * CAP + dy, (0.5 * s if dx == 0 else 2 * vr), (2 * vr if dx == 0 else 0.5 * s)) for dx, dy in ((0, 0.5 * CAP), (0, -0.5 * CAP), (R, 0), (-R, 0))])  # ☩
    from shr_caps import caps as _caps
    Cn = _caps(w, 'none'); Vv = Cn['V']; vb = bounds(Vv); Rr = Cn['R']; rb = bounds(Rr)
    G['uni2123'] = U(Vv, st([(vb[0] + 0.2 * (vb[2] - vb[0]), -0.1 * CAP), (vb[2] - 0.1 * (vb[2] - vb[0]), 1.0 * CAP)]))        # ℣ versicule
    G['uni211F'] = U(Rr, st([(rb[0] + 0.45 * (rb[2] - rb[0]), -0.15 * CAP), (rb[2] + 0.05 * s, 0.35 * CAP)]))                  # ℟ répons
    a3 = G['asterisk']; ab3 = bounds(a3); sc = 0.85
    A3 = xf(a3, (sc, 0, 0, sc, 0, 0)); b3 = bounds(A3)
    G['uni2042'] = U(mv(A3, -b3[0], CAP - b3[3]), mv(A3, -b3[0] + 1.1 * (b3[2] - b3[0]), CAP - b3[3]), mv(A3, -b3[0] + 0.55 * (b3[2] - b3[0]), CAP - b3[3] - 1.0 * (b3[3] - b3[1])))  # ⁂
    return G
