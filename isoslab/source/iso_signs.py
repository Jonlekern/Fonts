# ISOSLAB : ponctuation, signes, lettres de plus, accents et lettres accentuées
import math, unicodedata as ud
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.transformPen import TransformPen
from iso_core import *
from iso_lower import XH, ASC, DESC, OVL, rrect

def tr(p, m):
    """applique la matrice (a, b, c, d, e, f) à un chemin"""
    out = P(); rp = RecordingPen(); p.draw(rp); rp.replay(TransformPen(out.getPen(), m)); return out
def mv(p, dx=0, dy=0): return tr(p, (1, 0, 0, 1, dx, dy))
def sc(p, sx, sy=None, ox=0, oy=0):
    sy = sx if sy is None else sy; return tr(p, (sx, 0, 0, sy, ox - ox * sx, oy - oy * sy))
def rot180(p, cx, cy): return tr(p, (-1, 0, 0, -1, 2 * cx, 2 * cy))
def flipx(p, cx): return tr(p, (-1, 0, 0, 1, 2 * cx, 0))

def wave(cx, cy, wd, h, t):
    """vague (~) : demi-anneau en haut à gauche + demi-anneau en bas à droite, bouts coupés à plat"""
    a = wd / 4 + t / 4; b = h
    up = I(D(superell(cx - wd / 4, cy, a, b + t / 2, 2.2), superell(cx - wd / 4, cy, a - t, b - t / 2, 2.2)), rect(cx - wd, cy, cx, cy + 1000))
    dn = I(D(superell(cx + wd / 4, cy, a, b + t / 2, 2.2), superell(cx + wd / 4, cy, a - t, b - t / 2, 2.2)), rect(cx, cy - 1000, cx + wd, cy))
    return U(up, dn)

def build_signs(w, C, L):
    """C : capitales, L : minuscules. Rend {nom: chemin} et des réglages d'approche."""
    ST, TH, W, CW = w.ST, w.TH, w.W, w.CW
    SL = round(0.78 * w.SL); SX = round(0.85 * w.SX); R = round(0.45 * SX)
    G = {}
    dr = round(0.58 * ST + 8)                                  # demi-côté d'un point
    def pt(cx, cy, r=None): r = r or dr; return superell(cx, cy, r, r, 3.0, 100)
    # ---------- points, virgules ----------
    G['period'] = pt(dr, dr)
    def comma_at(cx, cy):
        ball = superell(cx, cy, dr, dr, 2.2, 100)
        tail = poly([(cx + dr * 0.97, cy - dr * 0.10), (cx - dr * 0.40, cy - dr * 2.55), (cx - dr * 0.98, cy - dr * 2.25), (cx - dr * 0.15, cy - dr * 0.75)])
        return U(ball, tail)
    G['comma'] = comma_at(dr, dr)
    G['colon'] = U(pt(dr, dr), pt(dr, XH - dr))
    G['semicolon'] = U(G['comma'], pt(dr, XH - dr))
    G['ellipsis'] = U(pt(dr, dr), pt(dr * 3 + dr * 1.3, dr), pt(dr * 5 + dr * 2.6, dr))
    G['periodcentered'] = pt(dr, XH * 0.5)
    G['bullet'] = superell(dr * 1.4, XH * 0.5, dr * 1.4, dr * 1.4, 2.0, 120)
    # apostrophes et guillemets
    def qr_at(x, top):                                          # ’ : virgule levée, la boule en haut
        c = comma_at(x + dr, dr); b = c.bounds; return mv(c, 0, top - b[3])
    def ql_at(x, top):                                          # ‘ : virgule retournée
        c = rot180(comma_at(dr, dr), dr, dr); b = c.bounds; return mv(c, x - b[0], top - b[3])
    gapq = round(dr * 0.9)
    G['quoteright'] = qr_at(0, CAP)
    G['quoteleft'] = ql_at(0, CAP)
    G['quotesinglbase'] = G['comma']
    G['quotedblright'] = U(qr_at(0, CAP), qr_at(2 * dr + gapq, CAP))
    G['quotedblleft'] = U(ql_at(0, CAP), ql_at(2 * dr + gapq, CAP))
    G['quotedblbase'] = U(G['comma'], mv(G['comma'], 2 * dr + gapq))
    wq, wqb, hq = ST * 0.95, ST * 0.62, round(0.30 * CAP)
    def straight(x): return poly([(x, CAP), (x + wq, CAP), (x + wq / 2 + wqb / 2, CAP - hq), (x + wq / 2 - wqb / 2, CAP - hq)])
    G['quotesingle'] = straight(0)
    G['quotedbl'] = U(straight(0), straight(wq + gapq))
    # ! ? et leurs inversés
    def exclam_at(cx):
        yb = 2 * dr + round(0.08 * CAP)
        return U(poly([(cx - ST * 0.55, CAP), (cx + ST * 0.55, CAP), (cx + ST * 0.36, yb), (cx - ST * 0.36, yb)]), pt(cx, dr))
    G['exclam'] = exclam_at(ST * 0.55)
    qw = round(0.72 * W + 20); rq = round(qw / 2); riq = max(round(0.3 * CW), rq - ST)
    y1 = round(0.36 * CAP); cxq = qw / 2
    loop = D(rrect(0, y1, qw, CAP, tl=rq, tr=rq, br=round(0.6 * rq)), rrect(ST, y1 + TH, qw - ST, CAP - TH, tl=riq, tr=riq, br=max(round(0.6 * rq) - ST, 10)))
    ytq = round(0.70 * CAP)
    loop = D(loop, rect(-10, y1 - 10, cxq - ST * 0.5, ytq))            # bout gauche coupé, le bas part du milieu
    rbq = round(0.45 * ST + 20)
    G['question'] = U(loop, rect(cxq - ST * 0.5, 2 * dr + round(0.08 * CAP), cxq + ST * 0.5, y1 + TH),
                      superell(rbq, ytq, rbq, rbq, 2.0, 100), pt(cxq, dr))
    for n, src in (('exclamdown', 'exclam'), ('questiondown', 'question')):
        b = G[src].bounds; p = rot180(G[src], (b[0] + b[2]) / 2, (b[1] + b[3]) / 2); b2 = p.bounds
        G[n] = mv(p, 0, XH - b2[3])
    # ---------- tirets, barres ----------
    my = round(XH * 0.48); th = round(TH * 1.0)
    G['hyphen'] = rect(0, my - th / 2, round(0.42 * W + 40), my + th / 2)
    G['endash'] = rect(0, my - th * 0.45, W, my + th * 0.45)
    G['emdash'] = rect(0, my - th * 0.45, 2 * W, my + th * 0.45)
    G['underscore'] = rect(0, -150, W, -150 + th * 0.8)
    G['bar'] = rect(0, DESC + 30, ST * 0.8, ASC)
    G['slash'] = I(pbar((0, DESC * 0.45), (0.55 * W, CAP + 40), ST * 0.85), rect(-200, DESC * 0.45, 2000, CAP + 40))
    G['backslash'] = flipx(G['slash'], (G['slash'].bounds[0] + G['slash'].bounds[2]) / 2)
    # ---------- maths ----------
    ma = round(XH * 0.52); mw_ = round(0.80 * W); mt = round(TH * 0.85)
    G['plus'] = U(rect(0, ma - mt / 2, mw_, ma + mt / 2), rect(mw_ / 2 - mt / 2, ma - mw_ / 2, mw_ / 2 + mt / 2, ma + mw_ / 2))
    G['uni2212'] = rect(0, ma - mt / 2, mw_, ma + mt / 2)
    eq = round(mt * 1.1)
    G['equal'] = U(rect(0, ma + eq / 2, mw_, ma + eq / 2 + mt), rect(0, ma - eq / 2 - mt, mw_, ma - eq / 2))
    d_ = mw_ * 0.40
    G['multiply'] = U(pbar((mw_ / 2 - d_, ma - d_), (mw_ / 2 + d_, ma + d_), mt), pbar((mw_ / 2 - d_, ma + d_), (mw_ / 2 + d_, ma - d_), mt))
    rdd = round(dr * 0.85)
    G['divide'] = U(G['uni2212'], pt(mw_ / 2, ma + mt / 2 + rdd + mt * 0.6, rdd), pt(mw_ / 2, ma - mt / 2 - rdd - mt * 0.6, rdd))
    def chev(x0, x1, yc, h, t, right=True):
        """chevron : deux bras d'épaisseur t aux bouts d'équerre (aucune pointe), pointe rabotée à plat"""
        tip = (x1, yc); e1 = (x0, yc + h); e2 = (x0, yc - h)
        p = U(pbar(e1, tip, t), pbar(e2, tip, t), pbar(tip, (x1 + 1, yc), t))
        L_ = math.hypot(x1 - x0, h); cut = (t / 2) * L_ / h * 0.55
        p = I(p, rect(-5000, -5000, x1 - cut, 5000))
        return p if right else flipx(p, (x0 + x1) / 2)
    G['greater'] = chev(0, mw_, ma, mw_ * 0.45, mt, True)
    G['less'] = chev(0, mw_, ma, mw_ * 0.45, mt, False)
    G['asciitilde'] = wave(mw_ / 2, ma, mw_, mw_ * 0.16, mt)
    G['asciicircum'] = tr(chev(0, round(0.30 * CAP), 0, round(0.30 * W + 0.2 * ST), ST * 0.55 + 10, True), (0, 1, -1, 0, 0, 0))
    b = G['asciicircum'].bounds; G['asciicircum'] = mv(G['asciicircum'], -b[0], CAP - b[3])
    # # (dièse)
    hw_ = round(0.85 * W); sl_ = 0.18 * CAP
    G['numbersign'] = U(*[I(pbar((x, 0), (x + sl_ * 0.35, CAP * 0.92), ST * 0.70), rect(-100, 0, 2000, CAP * 0.92)) for x in (hw_ * 0.22, hw_ * 0.62)],
                        rect(0, CAP * 0.30, hw_ + 30, CAP * 0.30 + mt), rect(0, CAP * 0.60, hw_ + 30, CAP * 0.60 + mt))
    # * (astérisque)
    al = round(0.15 * CAP + 0.25 * ST); ac = (al + 10, CAP - al)
    G['asterisk'] = U(*[pbar(ac, (ac[0] + al * math.cos(math.radians(90 + 72 * k)), ac[1] + al * math.sin(math.radians(90 + 72 * k))), ST * 0.42 + 12) for k in range(5)])
    # ---------- parenthèses, crochets, accolades ----------
    pa = round(0.55 * W); pb = (ASC - DESC) / 2 + 10; pc = (ASC + DESC) / 2
    ringp = D(superell(pa, pc, pa, pb, 2.6), superell(pa, pc, pa - ST * 0.85, pb - TH * 0.8, 2.6))
    G['parenleft'] = I(ringp, rect(-10, -2000, pa * 0.85, 2000))
    G['parenright'] = flipx(G['parenleft'], pa * 0.425)
    bw_ = round(0.38 * W); bt = ST * 0.85
    G['bracketleft'] = U(rect(0, DESC + 20, bt, ASC), rect(0, ASC - TH * 0.9, bw_, ASC), rect(0, DESC + 20, bw_, DESC + 20 + TH * 0.9))
    G['bracketright'] = flipx(G['bracketleft'], bw_ / 2)
    yb0, yb1, ymid = DESC + 20, ASC, (ASC + DESC + 20) / 2; br_ = round(0.30 * W); xb = round(0.16 * W)
    up = D(rrect(xb, ymid, xb + br_ + bt, yb1, tl=br_), rrect(xb + bt, ymid - 5, xb + br_ + bt + 5, yb1 - TH * 0.85, tl=max(br_ - bt, 8)))
    lo = D(rrect(xb, yb0, xb + br_ + bt, ymid, bl=br_), rrect(xb + bt, yb0 + TH * 0.85, xb + br_ + bt + 5, ymid + 5, bl=max(br_ - bt, 8)))
    up = I(up, rect(-100, ymid + bt * 0.6, 2000, 2000)); lo = I(lo, rect(-100, -2000, 2000, ymid - bt * 0.6))
    notch = poly([(xb + bt, ymid + bt * 1.3), (0, ymid + bt * 0.35), (0, ymid - bt * 0.35), (xb + bt, ymid - bt * 1.3)])
    G['braceleft'] = U(up, lo, notch)
    G['braceright'] = flipx(G['braceleft'], (xb + br_ + bt) / 2)
    # ---------- guillemets ----------
    gw_, gh_, gt_ = round(0.26 * W + 0.5 * ST), round(0.20 * XH + 0.15 * ST), ST * 0.75
    G['guilsinglleft'] = chev(0, gw_, XH * 0.48, gh_, gt_, False)
    G['guilsinglright'] = chev(0, gw_, XH * 0.48, gh_, gt_, True)
    G['guillemotleft'] = U(G['guilsinglleft'], mv(G['guilsinglleft'], gw_ * 0.80))
    G['guillemotright'] = U(G['guilsinglright'], mv(G['guilsinglright'], gw_ * 0.80))
    # ---------- monnaies et divers ----------
    cc = L['c']; b = cc.bounds; xm_ = (b[0] + b[2]) / 2
    G['cent'] = U(cc, rect(xm_ - ST * 0.3, b[1] - 90, xm_ + ST * 0.3, b[1] + TH), rect(xm_ - ST * 0.3, b[3] - TH, xm_ + ST * 0.3, b[3] + 90))
    S_ = C['S']; b = S_.bounds; xm_ = (b[0] + b[2]) / 2
    G['dollar'] = U(S_, rect(xm_ - ST * 0.32, b[1] - 110, xm_ + ST * 0.32, b[1] + TH), rect(xm_ - ST * 0.32, b[3] - TH, xm_ + ST * 0.32, b[3] + 110))
    Y_ = C['Y']; b = Y_.bounds
    G['yen'] = U(Y_, rect(b[0] + W * 0.18, CAP * 0.30, b[2] - W * 0.18, CAP * 0.30 + mt * 0.9), rect(b[0] + W * 0.18, CAP * 0.30 + mt * 1.9, b[2] - W * 0.18, CAP * 0.30 + mt * 2.8))
    E_ = C['C']; b = E_.bounds
    G['Euro'] = U(E_, rect(b[0] - W * 0.12, CAP * 0.40, b[0] + W * 0.70, CAP * 0.40 + mt * 0.85), rect(b[0] - W * 0.12, CAP * 0.58, b[0] + W * 0.66, CAP * 0.58 + mt * 0.85))
    # £ : crochet en goutte en haut, barre, pied plat avec bec
    lw = round(0.80 * W); xs_ = round(0.22 * W); rL = round(0.30 * W)
    hookL = D(rrect(xs_, CAP * 0.62, xs_ + rL * 2, CAP, tl=rL, tr=rL), rrect(xs_ + ST, CAP * 0.62 - 5, xs_ + rL * 2 - ST, CAP - TH, tl=max(rL - ST, 10), tr=max(rL - ST, 10)))
    rbl = round(0.42 * ST + 18)
    G['sterling'] = U(rect(xs_, TH, xs_ + ST, CAP * 0.80), hookL, superell(xs_ + 2 * rL - rbl, CAP * 0.62, rbl, rbl, 2.0, 100),
                      rect(0, CAP * 0.42, xs_ + ST + W * 0.30, CAP * 0.42 + mt), rect(0, 0, lw, TH),
                      U(rect(lw - round(SL * 0.8), TH - 1, lw, TH + round(0.12 * CAP)), wedge((lw - round(SL * 0.8), TH), (0, 1), (-1, 0), R)))
    # § : deux s superposés
    from iso_lower import build_lower as _bl
    s_ = sc(_bl(Wt(round(ST * 0.72)))['s'], 0.95); b = s_.bounds; hS = b[3] - b[1]
    G['section'] = U(mv(s_, 0, CAP - b[3] - 10), mv(s_, 0, CAP - b[3] - 10 - hS * 0.62))
    # ¶
    pw = round(0.85 * W); pt_ = ST * 0.80
    G['paragraph'] = U(I(superell(pw * 0.45, CAP * 0.72, pw * 0.45, CAP * 0.28, 2.4), rect(-10, 0, pw * 0.45 + 1, CAP)),
                       rect(pw * 0.45, CAP * 0.44, pw * 0.45 + 2, CAP), rect(pw * 0.45, DESC + 40, pw * 0.45 + pt_, CAP),
                       rect(pw - pt_, DESC + 40, pw, CAP), rect(pw * 0.45, CAP - TH * 0.8, pw, CAP))
    # © ® ™ ° 
    cr = round(0.58 * CAP); ct = round(TH * 0.55)
    circ = D(superell(cr, CAP / 2, cr, cr, 2.0, 160), superell(cr, CAP / 2, cr - ct, cr - ct, 2.0, 160))
    def inner(g, k):
        p = sc(g, k); b = p.bounds; return mv(p, cr - (b[0] + b[2]) / 2, CAP / 2 - (b[1] + b[3]) / 2)
    G['copyright'] = U(circ, inner(C['C'], 0.50))
    G['registered'] = U(circ, inner(C['R'], 0.50))
    t_ = sc(C['T'], 0.40); m_ = sc(C['M'], 0.40); bt_ = t_.bounds
    G['trademark'] = mv(U(t_, mv(m_, bt_[2] + 20 - m_.bounds[0])), 0, CAP - CAP * 0.40)
    G['degree'] = D(superell(dr * 1.5, CAP - dr * 1.5, dr * 1.5, dr * 1.5, 2.0, 100), superell(dr * 1.5, CAP - dr * 1.5, dr * 0.75, dr * 0.75, 2.0, 100))
    # ª º
    for n, g in (('ordfeminine', 'a'), ('ordmasculine', 'o')):
        p = sc(L[g], 0.55); b = p.bounds
        G[n] = U(mv(p, -b[0], CAP - b[3]), rect(0, CAP - (b[3] - b[1]) - 40 - mt * 0.8, b[2] - b[0], CAP - (b[3] - b[1]) - 40))
    # @
    Ra = round(0.62 * W + 40); Rb = round(0.50 * CAP); cxa, cya = Ra, CAP * 0.42; ta = round(TH * 0.75)
    outer = D(superell(cxa, cya, Ra, Rb, 2.4), superell(cxa, cya, Ra - ta, Rb - ta, 2.4))
    ycut = cya - Rb * 0.28
    outer = D(outer, rect(cxa, cya - Rb - 5, cxa + Ra + 5, ycut - ta))
    ia, ib = Ra * 0.42, Rb * 0.40; icx = cxa - Ra * 0.08
    ino = D(superell(icx, cya, ia, ib, 2.4), superell(icx, cya, ia - ST * 0.8, ib - ta, 2.4))
    xs2 = icx + ia - ST * 0.8
    G['at'] = U(outer, ino, rect(xs2, ycut - ta, xs2 + ST * 0.8, cya + ib * 0.4), rect(xs2, ycut - ta, cxa + Ra - ta * 0.5, ycut))
    # & : « Et »
    E_ = C['E']; t2 = L['t']; bE = E_.bounds; bt2 = t2.bounds
    G['ampersand'] = U(E_, mv(t2, bE[2] - SX * 0.4 - bt2[0] - (C['E'].bounds[2] - C['E'].bounds[0]) * 0.0, 0))
    # ★ ☆
    G['uni2605'] = C['star']
    st = C['star']; b = st.bounds; cxs, cys = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
    G['uni2606'] = D(st, sc(st, 0.55, 0.55, cxs, cys - 8))
    # ---------- ajouts d'affiche ----------
    # ☞ ☜ : main qui pointe — manchette à lèvre d'empattement, doigts en barres arrondies séparées par un jour
    f = round(0.12 * XH + 0.28 * ST); g = max(round(0.15 * f), 12)
    tot = 4 * f + 4 * g + round(0.85 * f); yb = round(XH / 2 - tot / 2)
    px = round(2.4 * f)                                                     # bord droit de la paume
    parts = []
    for k, Lk in enumerate((0.55, 0.70, 0.82)):                            # trois doigts repliés, courts
        y0 = yb + k * (f + g); parts.append(rrect(px - f, y0, px + Lk * f, y0 + f, tr=f / 2, br=f / 2, n=2.0))
    yi = yb + 3 * (f + g); parts.append(rrect(px - f, yi, px + 4.8 * f, yi + f, tr=f / 2, br=f / 2, n=2.0))   # index, long
    yt = yi + f + g; parts.append(rrect(px - 1.4 * f, yt, px + 0.55 * f, yt + 0.85 * f, tr=0.42 * f, br=0.42 * f, n=2.0))  # pouce
    palm = rrect(px - 2.3 * f, yb, px - 0.6 * f, yt + 0.85 * f, tl=0.55 * f, bl=0.55 * f)
    cx1 = px - 2.3 * f - g; cw_ = round(1.9 * f); lip = round(0.30 * f)
    cuff = U(rect(cx1 - cw_, yb + 0.10 * f, cx1, yt + 0.75 * f),
             rect(cx1 - cw_, yb + 0.10 * f - lip, cx1 - cw_ + round(0.40 * f), yt + 0.75 * f + lip),   # lèvres d'empattement des deux côtés
             rect(cx1 - round(0.40 * f), yb + 0.10 * f - lip, cx1, yt + 0.75 * f + lip))
    hand = U(palm, *parts, cuff)
    G['uni261E'] = hand
    hb = hand.bounds; G['uni261C'] = flipx(hand, (hb[0] + hb[2]) / 2)
    # → ← ↑ ↓ : fût + tête en chevron (bouts d'équerre, pointe rabotée)
    aw_ = round(1.15 * W + 40); ah = round(0.24 * XH + 0.2 * ST); at_ = ST * 0.72; sh_ = round(TH * 0.85)
    hx0 = aw_ - round(0.42 * W + 0.4 * ST); head = chev(hx0, aw_, ma, ah, at_, True)
    phi = math.atan2(ah, aw_ - hx0)
    # le fût finit en pointe le long du bord intérieur des bras : raccord plein, sans marche ni trou
    e_ = (at_ / 2) / math.cos(phi); s_ = sh_ / 2
    xa = aw_ - (0.9 * s_ + e_) / math.tan(phi); xv = aw_ - e_ / math.tan(phi) + 4
    right = U(poly([(0, ma - s_), (xa, ma - s_), (xv, ma), (xa, ma + s_), (0, ma + s_)]), head)
    G['uni2192'] = right
    G['uni2190'] = flipx(right, aw_ / 2)
    up_ = tr(right, (0, 1, -1, 0, 0, 0)); b = up_.bounds; up_ = mv(up_, -b[0], (CAP / 2 - (b[1] + b[3]) / 2))
    G['uni2191'] = up_
    b = up_.bounds; G['uni2193'] = tr(up_, (1, 0, 0, -1, 0, b[1] + b[3]))
    # ◆ ● ■ : séparateurs, centrés sur la hauteur d'x
    sq = round(0.50 * XH + 0.15 * ST); cyx = XH / 2
    G['uni25A0'] = rect(0, cyx - sq / 2, sq, cyx + sq / 2)
    rc = round(0.30 * XH + 0.08 * ST); G['uni25CF'] = superell(rc, cyx, rc, rc, 2.0)
    dd = round(0.36 * XH + 0.10 * ST); G['uni25C6'] = poly([(dd, cyx - dd), (2 * dd, cyx), (dd, cyx + dd), (0, cyx)])
    # VS : V et S serrés entre deux filets, comme sur les affiches (ligature contextuelle)
    kk = 0.64; v_ = sc(C['V'], kk); s_ = sc(C['S'], kk); bv, bs = v_.bounds, s_.bounds
    y0 = CAP * 0.18
    v_ = mv(v_, -bv[0], y0 - bv[1]); s_ = mv(s_, (bv[2] - bv[0]) + 0.10 * W - bs[0], y0 - bs[1])
    x1 = s_.bounds[2]; rt = round(TH * 0.65); gp = round(0.06 * CAP)
    G['V_S'] = U(v_, s_, rect(0, y0 - gp - rt, x1, y0 - gp), rect(0, y0 + kk * CAP + gp + 2, x1, y0 + kk * CAP + gp + 2 + rt))
    # ---------- lettres de plus ----------
    G['dotlessi'] = D(L['i'], rect(-500, XH + 20, 1000, 2000))
    G['uni0237'] = D(L['j'], rect(-500, XH + 20, 1000, 2000))
    def bar_through(g, y, x0, x1, t=None):
        t = t or mt * 0.9; return U(g, rect(x0, y - t / 2, x1, y + t / 2))
    b = C['D'].bounds
    G['Eth'] = bar_through(C['D'], CAP * 0.5, -SX * 0.6, ST + W * 0.22)
    G['Dcroat'] = G['Eth']
    b = L['d'].bounds; xs3 = b[2] - (SX + ST)
    SLl = round(0.78 * w.SL); room_ = (ASC - SLl) - XH; tb_ = min(mt * 0.9, 0.55 * room_); yb_ = XH + room_ / 2
    G['dcroat'] = bar_through(L['d'], yb_, xs3 - W * 0.22, b[2] + 10, tb_)
    b = C['H'].bounds
    roomH = (CAP - w.SL) - (CAP * 0.5 + TH / 2); tbH = min(mt * 0.9, 0.55 * roomH)
    G['Hbar'] = bar_through(C['H'], CAP * 0.5 + TH / 2 + roomH / 2, b[0] - 10, b[2] + 10, tbH)
    G['hbar'] = bar_through(L['h'], yb_, -SX - 25, ST + W * 0.25, tb_)
    G['Lslash'] = U(C['L'], I(pbar((-SX * 0.6, CAP * 0.30), (ST + W * 0.28, CAP * 0.56), mt * 0.95), rect(-500, -50, 2000, CAP)))
    G['lslash'] = U(L['l'], I(pbar((-SX * 0.8, ASC * 0.38), (ST + W * 0.25, ASC * 0.60), mt * 0.95), rect(-500, -50, 2000, ASC)))
    O_ = C['O']; b = O_.bounds
    G['Oslash'] = U(O_, I(pbar((b[0] - 10, b[1] - 30), (b[2] + 10, b[3] + 30), ST * 0.62), rect(b[0] - 30, b[1] - 40, b[2] + 30, b[3] + 40)))
    o_ = L['o']; b = o_.bounds
    G['oslash'] = U(o_, I(pbar((b[0] - 10, b[1] - 30), (b[2] + 10, b[3] + 30), ST * 0.62), rect(b[0] - 30, b[1] - 40, b[2] + 30, b[3] + 40)))
    # Þ þ
    tb0, tb1 = round(CAP * 0.18), round(CAP * 0.80); tw_ = W + 10; rt_ = round(0.45 * (tb1 - tb0)); rti = max(rt_ - ST, 12)
    G['Thorn'] = U(C['I'], D(rrect(0, tb0, tw_, tb1, tr=rt_, br=rt_), rrect(ST, tb0 + TH, tw_ - ST, tb1 - TH, tr=rti, br=rti, tl=round(0.2 * CW), bl=round(0.2 * CW))))
    G['thorn'] = U(D(L['p'], rect(-1000, XH + 1, 3000, 3000)), rect(0, XH - 1, ST, ASC), D(L['b'], rect(-1000, -1000, ST, 3000)))
    # Æ Œ æ œ
    E_ = C['E']; A_ = C['A']; bA = A_.bounds
    leg = I(A_, rect(-1000, -100, (bA[0] + bA[2]) / 2 - ST * 0.1, CAP + 10))
    Ep = mv(D(E_, rect(-1000, -100, 0, 2000)), (bA[0] + bA[2]) / 2 - ST * 0.6)
    G['AE'] = U(leg, Ep, rect(bA[0] + W * 0.35, CAP * 0.25, (bA[0] + bA[2]) / 2, CAP * 0.25 + TH))
    O_ = C['O']; bO = O_.bounds; half = I(O_, rect(-100, -100, (bO[0] + bO[2]) / 2 + 1, 2000))
    G['OE'] = U(half, mv(D(E_, rect(-1000, -100, 0, 2000)), (bO[0] + bO[2]) / 2 - ST * 0.5))
    a_ = L['a']; e_ = L['e']; ba = a_.bounds
    G['ae'] = U(D(a_, rect(ba[2] - SX - 2, -10, 3000, SL + 2)), mv(e_, ba[2] - SX - ST * 1.05))
    o_ = L['o']; bo = o_.bounds
    G['oe'] = U(o_, mv(e_, bo[2] - ST * 1.0))
    # ß ẞ : fût, arche en haut, deux panses
    def sharp(top, wd, ym):
        r1 = round(0.5 * wd)
        upper = D(rrect(0, ym - TH, wd, top, tl=r1, tr=r1, br=round(0.45 * (top - ym))),
                  rrect(ST, ym, wd - ST, top - TH, tl=max(r1 - ST, 10), tr=max(r1 - ST, 10), br=max(round(0.45 * (top - ym)) - ST, 10)))
        lower = D(rrect(ST - 5, 0, wd + 20, ym, tr=round(0.45 * ym), br=round(0.45 * ym)),
                  rrect(ST, TH, wd + 20 - ST, ym - TH, tr=max(round(0.45 * ym) - ST, 10), br=max(round(0.45 * ym) - ST, 10), tl=10, bl=10))
        return U(rect(0, 0, ST, top - r1), upper, lower)
    nwl = 2 * ST + round(0.80 * CW)
    G['germandbls'] = U(sharp(ASC, nwl, round(0.55 * XH)), U(rect(-SX, 0, ST, SL), wedge((0, SL), (0, 1), (-1, 0), R)))
    G['uni1E9E'] = U(sharp(CAP, W, round(0.50 * CAP)), U(rect(-SX, 0, ST, SL), wedge((0, SL), (0, 1), (-1, 0), R)))
    # ð
    o_ = L['o']; bo = o_.bounds
    G['eth'] = U(o_, I(pbar((bo[2] - ST * 0.6, XH * 0.40), (bo[0] + (bo[2] - bo[0]) * 0.35, ASC), ST * 0.85), rect(-100, 0, 3000, ASC)),
                 rect((bo[0] + bo[2]) / 2 - W * 0.24, ASC - 150 - mt * 0.42, (bo[0] + bo[2]) / 2 + W * 0.30, ASC - 150 + mt * 0.42))
    return G

# ---------- accents ----------
def build_marks(w):
    """marques : (nom → (chemin centré en x=0, posé sur y=0 pour le dessus / pendu sous y=0 pour le dessous)) ; cap=True : plus plates"""
    ST, TH = w.ST, w.TH
    M = {}
    for cap in (False, True):
        k = 0.80 if cap else 1.0; t = ST * 0.68; h = round((120 + 0.40 * ST) * k)
        tag = '.cap' if cap else ''
        d = unit((0.55, 1.0))
        L_ = h / d[1]
        M['acute' + tag] = pbar((-L_ * d[0] / 2, 0), (L_ * d[0] / 2, h), t)
        M['grave' + tag] = flipx(M['acute' + tag], 0)
        M['hungarumlaut' + tag] = U(mv(M['acute' + tag], -t * 0.85), mv(M['acute' + tag], t * 0.85))
        cw_ = round((120 + 0.45 * ST)); ch_ = round(h * 0.80)
        circ = U(pbar((-cw_, 0), (0, ch_), t * 0.92), pbar((cw_, 0), (0, ch_), t * 0.92))
        circ = I(circ, rect(-3000, 0, 3000, ch_ - t * 0.25))
        M['circumflex' + tag] = circ
        M['caron' + tag] = rot180(circ, 0, (ch_ - t * 0.25) / 2)
        r = round(0.50 * ST + 8) * (0.90 if cap else 1.0); gap = r * 0.9
        M['dieresis' + tag] = U(superell(-r - gap / 2, r, r, r, 3.0, 80), superell(r + gap / 2, r, r, r, 3.0, 80))
        M['dotaccent' + tag] = superell(0, r, r, r, 3.0, 80)
        rr_ = round(r * 1.25); rt = max(round(ST * 0.36), 14)
        M['ring' + tag] = D(superell(0, rr_, rr_, rr_, 2.0, 100), superell(0, rr_, rr_ - rt, rr_ - rt, 2.0, 100))
        mw = round(150 + 0.6 * ST)
        M['macron' + tag] = rect(-mw, 0, mw, TH * 0.85 * k)
        bw = round(130 + 0.45 * ST); bh = round(h * 0.75)
        M['breve' + tag] = I(D(superell(0, bh, bw, bh, 2.2), superell(0, bh, bw - ST * 0.75, bh - TH * 0.8, 2.2)), rect(-3000, 0, 3000, bh * 0.85))
        tw = round(150 + 0.5 * ST); ta = round(h * 0.28)
        M['tilde' + tag] = mv(wave(0, 0, 2 * tw, ta * 0.55, t * 0.80), 0, ta * 0.55 + t * 0.4)
    # dessous
    r = round(0.58 * ST + 8)
    def comma_shape(rr):
        ball = superell(0, 0, rr, rr, 2.2, 100)
        return U(ball, poly([(rr * 0.97, -rr * 0.10), (-rr * 0.40, -rr * 2.55), (-rr * 0.98, -rr * 2.25), (-rr * 0.15, -rr * 0.75)]))
    cm = comma_shape(min(round(r * 0.85), 62)); b = cm.bounds
    M['commabelow'] = mv(cm, 0, -40 - b[3])                                  # pendu sous la ligne
    M['commaturned'] = rot180(cm, 0, 0); b = M['commaturned'].bounds; M['commaturned'] = mv(M['commaturned'], 0, -b[1])
    # cédille : petit fût, puis un crochet « ⊃ » qui revient à gauche et finit en goutte
    tc = ST * 0.62; tt = max(round(TH * 0.55), 22); HC = round(0.40 * XH); HW = round(0.30 * XH); x0 = -tc / 2
    rh = round(0.45 * (HC - 40)); rhi = max(rh - tt, 8)
    hook = D(rrect(x0, -HC, x0 + HW, -40, tr=rh, br=rh), rrect(x0 - 5, -HC + tt, x0 + HW - tt * 1.3, -40 - tt, tr=rhi, br=rhi))
    rdc = round(tt * 0.95)
    M['cedilla'] = U(rect(x0, -40 - tt + 1, x0 + tc, 25), hook, superell(x0 + rdc, -HC + rdc, rdc, rdc, 2.0, 60))
    # ogonek : descend du pied, tourne à droite, bout coupé net
    to = ST * 0.62; HO = round(0.36 * XH); OW = round(0.30 * XH); ro = round(0.50 * OW); roi = max(ro - to, 8)
    M['ogonek'] = D(rrect(-to / 2, -HO, -to / 2 + OW, 20, bl=ro), rrect(-to / 2 + to, -HO + tt, -to / 2 + OW + 10, 40, bl=roi))
    return M

MARK_OF = {0x300: 'grave', 0x301: 'acute', 0x302: 'circumflex', 0x303: 'tilde', 0x304: 'macron', 0x306: 'breve',
           0x307: 'dotaccent', 0x308: 'dieresis', 0x30A: 'ring', 0x30B: 'hungarumlaut', 0x30C: 'caron',
           0x326: 'commabelow', 0x327: 'cedilla', 0x328: 'ogonek'}
