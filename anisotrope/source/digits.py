# Chiffres de Johnny : petite boucle, long fût. Aucun chiffre n'est le miroir ou le retourné d'un autre (6 ≠ 9 tourné).
from core import *

DH = CAP                                  # hauteur des chiffres
LR = round(70 + 0.75 * ST)                # rayon d'une petite boucle
LRY = round(LR * 1.1)

def loop(cx, cy, rx=LR, ry=LRY): return ring(cx, cy, rx, ry, sx=ST, sy=TH, r=0)

def at(cx, cy, rx, ry, deg):
    """point d'une ellipse sur le rayon d'angle deg (celui que coupe pie)"""
    a = math.radians(deg); c, s_ = math.cos(a), math.sin(a)
    r = 1 / math.sqrt((c / rx) ** 2 + (s_ / ry) ** 2)
    return (cx + r * c, cy + r * s_)

def ends(cx, cy, rx, ry, deg):
    """bout d'une boucle coupée à deg : (point extérieur, point intérieur)"""
    return at(cx, cy, rx, ry, deg), at(cx, cy, rx - ST, ry - TH, deg)

def beak_dn(x, y, dx=1):
    L = round(SH * 1.2); return poly([(x, y), (x, y - L), (x - dx * 10, y - L), (x - dx * ST * 0.8, y)])

@reg('nine', '9')
def g_nine():
    # petite boucle en haut à gauche, long fût droit, crochet en bas vers la gauche
    cx = LR; cy = DH + OV - LRY; xs = cx + LR - ST
    h = round(120 + 0.2 * ST); r = round(max(0.55 * ST + 70, ST + 50))
    o = ellipse(xs + ST - r, h, r, h + OV); i = ellipse(xs + ST - r, h, r - ST, h + OV - TH)
    hook = I(D(o, i), rect(xs + ST - 2 * r - 10, -OV - 5, xs + ST, h))
    xc = xs + ST - r
    hook = I(hook, U(rect(xc - r - 10, -OV - 5, xc, h - 34), rect(xc - 1, -OV - 5, xs + ST + 5, h + 1)))
    return out(U(loop(cx, cy), stem(xs, h - 2, cy + 2), hook), 'T', 'P')

@reg('one', '1')
def g_one():
    # long fût, long drapeau en V pointu, pas de pied
    t = round(TH * 1.25); L = round(DH * 0.27)
    flag = I(bar(ST * 0.25, DH + t * 0.3, -round(0.20 * DH), DH - L, t), rect(-1000, 0, 1000, DH))
    return out(U(stem(0, 0, DH), flag), 'T', 'P')

@reg('eight', '8')
def g_eight():
    ryl = (DH + 2 * OV + TH) / (2 * 1.68); ryu = 0.68 * ryl
    rxl = round(0.31 * DH + 0.25 * ST); rxu = round(0.72 * rxl)
    cyl = -OV + ryl; cyu = DH + OV - ryu; cx = rxl
    return out(U(loop(cx, cyu, rxu, ryu), loop(cx, cyl, rxl, ryl)), 'O', 'O')

@reg('zero', '0')
def g_zero():
    # zéro étroit à côtés droits : impossible à prendre pour un O
    w = round(0.40 * DH + 0.9 * ST); r = w / 2
    outer = U(rect(0, r - OV, w, DH + OV - r), ellipse(r, r - OV, r, r), ellipse(r, DH + OV - r, r, r))
    ri = r - ST * 0.95; ry = r - TH
    inner = U(rect(r - ri, r - OV, r + ri, DH + OV - r), ellipse(r, r - OV, ri, ry), ellipse(r, DH + OV - r, ri, ry))
    return out(D(outer, inner), 'O', 'O')

@reg('six', '6')
def g_six():
    # le 9 retourné (choix de Johnny)
    p, l, r = g_nine(); b = p.bounds
    return rot(p, 180, (b[0] + b[2]) / 2, (b[1] + b[3]) / 2), r, l

@reg('seven', '7')
def g_seven():
    # barre en haut, long fût en biais, petite barre au milieu (à la suisse)
    w = round(0.48 * DH + 0.3 * ST); xb = round(0.22 * DH)
    d = I(bar(w - ST * 0.45, DH - TH, xb, 0, ST * 1.02), rect(-100, 0, w, DH - TH + 2))
    top = rect(0, DH - TH, w, DH)
    ym = DH * 0.44; xm = xb + (w - ST * 0.45 - xb) * ym / (DH - TH)
    cross = rect(xm - 120, ym - TH / 2, xm + 110, ym + TH / 2)
    return out(U(d, top, cross), 'T', 'T')


# ---- 2 3 4 5 : construits avec les pièces des chiffres validés (0 1 6 7 8 9) ----
def eight_dims(k=1.0):
    ryl = (DH + 2 * OV + TH) / (2 * 1.68); ryu = 0.68 * ryl
    rxl = (0.31 * DH + 0.25 * ST) * k; rxu = 0.72 * rxl
    return rxu, ryu, DH + OV - ryu, rxl, ryl, -OV + ryl

BEAK = round(SH * 1.2)

def _unit(v):
    L = math.hypot(*v); return (v[0] / L, v[1] / L)

def fillet_out(p, Q, u, v, R):
    """arrondit un coin saillant de l'encre en Q, entre les demi-droites u et v (unitaires), par un arc de rayon R tangent aux deux"""
    u, v = _unit(u), _unit(v)
    cosang = u[0] * v[0] + u[1] * v[1]; ang = math.acos(max(-1, min(1, cosang)))
    d = R / math.tan(ang / 2)
    Tu = (Q[0] + u[0] * d, Q[1] + u[1] * d); Tv = (Q[0] + v[0] * d, Q[1] + v[1] * d)
    bis = _unit((u[0] + v[0], u[1] + v[1])); h = R / math.sin(ang / 2)
    C = (Q[0] + bis[0] * h, Q[1] + bis[1] * h)
    tip = D(poly([Q, Tu, Tv]), ellipse(C[0], C[1], R, R))
    return D(p, tip)

def fillet_in(p, Q, u, v, R):
    """arrondit un coin rentrant de l'encre en Q (ajoute de l'encre)"""
    u, v = _unit(u), _unit(v)
    cosang = u[0] * v[0] + u[1] * v[1]; ang = math.acos(max(-1, min(1, cosang)))
    d = R / math.tan(ang / 2)
    Tu = (Q[0] + u[0] * d, Q[1] + u[1] * d); Tv = (Q[0] + v[0] * d, Q[1] + v[1] * d)
    bis = _unit((u[0] + v[0], u[1] + v[1])); h = R / math.sin(ang / 2)
    C = (Q[0] + bis[0] * h, Q[1] + bis[1] * h)
    e = 2.5; sh = lambda P: (P[0] - bis[0] * e, P[1] - bis[1] * e)
    return U(p, D(poly([sh(Q), sh(Tu), sh(Tv)]), ellipse(C[0], C[1], R, R)))

def two_var(k=1.0, cut=0.36, bec_=True, A=-32):
    """k : taille de la boucle ; cut : hauteur du bout gauche (0 = au milieu) ; bec_ : bec au bout de la base"""
    lr, lry = round(LR * k), round(LRY * k)
    w = max(round(0.40 * DH + 0.6 * ST), 2 * lr + 30); cx = w - lr; cy = DH + OV - lry
    arc = I(ring(cx, cy, lr, lry, sx=min(ST, lr - 24), sy=min(TH, lry - 24), r=0), pie(cx, cy, A, 180))
    arc = D(arc, rect(cx - lr - 10, cy - 10, cx, cy + round(cut * lry)))
    po, pi_ = ends(cx, cy, lr, lry, A)
    xf_ = round(W * 0.9); td = ST * 1.15
    # la diagonale descend jusqu'à la ligne de base ; son bord gauche y est raccordé par un arc tangent
    yb = TH * 0.6; ql = (xf_, yb); qr = (xf_ + td, yb)
    dx, dy = ql[0] - pi_[0], ql[1] - pi_[1]
    Q = (ql[0] - dx * yb / dy, 0.0)                      # le bord gauche prolongé jusqu'à la ligne de base
    diag = poly([pi_, po, (qr[0] - dx * yb / dy, 0), Q])
    base = rect(Q[0] + TH * dx / dy, 0, w + 20, TH)      # la base part du bord gauche de la diagonale
    p = U(arc, diag, base)
    p = fillet_out(p, Q, (pi_[0] - Q[0], pi_[1] - Q[1]), (1.0, 0.0), round(0.09 * DH + 0.3 * ST))
    dxr, dyr = qr[0] - po[0], qr[1] - po[1]              # pente du bord droit (la diagonale s'affine : pas la même qu'à gauche)
    Q2 = (qr[0] - dxr * (yb - TH) / dyr, TH)             # coin intérieur : bord droit de la diagonale et dessus de la base
    p = fillet_in(p, Q2, (po[0] - Q2[0], po[1] - Q2[1]), (1.0, 0.0), round(0.04 * DH + 0.12 * ST))
    if bec_: p = U(p, poly([(w + 20, TH), (w + 20, TH + BEAK), (w + 10, TH + BEAK), (w + 20 - ST * 0.8, TH)]))
    return p

@reg('two', '2')
def g_two(): return out(two_var(), 'T', 'T')

@reg('three', '3')
def g_three():
    # le 8 ouvert à gauche, avec la flèche au milieu ; les boucles sont coupées le long des bords de la flèche
    rxu, ryu, cyu, rxl, ryl, cyl = eight_dims(0.80); cx = rxl
    sxu = min(ST, rxu - max(26, 0.15 * ST)); syu = min(TH, ryu - max(26, 0.15 * ST))   # la petite boucle garde un jour en gras
    ym = cyl + ryl - TH / 2
    up = D(ring(cx, cyu, rxu, ryu, sx=sxu, sy=syu, r=0), rect(cx - rxu - 10, ym, cx, cyu + round(0.36 * ryu)))
    lo = D(loop(cx, cyl, rxl, ryl), rect(cx - rxl - 10, cyl - round(0.36 * ryl), cx, ym))
    xr = cx + ST * 0.40; xv = cx - 0.62 * rxu
    P = (xv, ym); T = (xr, ym + TH * 0.95); B = (xr, ym - TH * 0.95)     # pointe de flèche, un peu plus haute que le trait
    y0, y1 = B[1], T[1]
    up = D(up, poly([(xv - 1000, ym), P, T, (xr, -1000), (xv - 1000, -1000)]))
    lo = D(lo, poly([(xv - 1000, ym), P, B, (xr, 2000), (xv - 1000, 2000)]))
    fleche = poly([P, T, (xr + 2, y1), (xr + 2, y0), B])
    return out(U(up, lo, fleche), 'T', 'O')

@reg('four', '4')
def g_four():
    # le 1 : son drapeau descend jusqu'à la barre et ferme une petite boucle
    w = round(0.36 * DH + 0.9 * ST); over = round(0.10 * DH)
    xs = w - ST - over; yb = round(0.28 * DH); t = round(TH * 1.25)
    diag = I(bar(xs + t * 0.2, DH + t * 0.3, t * 0.5, yb + TH, t), rect(0, yb, xs + ST, DH))
    return out(U(stem(xs, 0, DH), diag, rect(0, yb, w, yb + TH)), 'T', 'T')

@reg('five', '5')
def g_five():
    # la barre du 7 en haut, un fût court, la panse du 8 ouverte à gauche ; le bout finit par une coupe droite
    _, _, _, rxl, ryl, cyl = eight_dims(0.80); cx = rxl
    A = 128
    pan = I(loop(cx, cyl, rxl, ryl), pie(cx, cyl, -180, A))
    pan = D(pan, rect(cx - rxl - 10, cyl - round(0.36 * ryl), cx, cyl + 10))
    po, pi_ = ends(cx, cyl, rxl, ryl, A); x0 = po[0] - 4; yj = max(po[1], pi_[1])
    fut = U(rect(x0, yj, x0 + ST, DH), poly([po, pi_, (x0 + ST, yj + 2), (x0, yj + 2)]))
    fut = D(fut, ellipse(cx, cyl, rxl - ST, ryl - TH))             # le fût n'entre pas dans la panse
    w = round(2 * rxl - 10)
    barre = rect(x0, DH - TH, w, DH)
    bec = poly([(w, DH - TH), (w, DH - TH - BEAK), (w - 10, DH - TH - BEAK), (w - ST * 0.8, DH - TH)])
    return out(U(pan, fut, barre, bec), 'T', 'O')

