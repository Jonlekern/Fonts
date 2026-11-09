# Majuscules : mêmes coins, mêmes ronds de plume. I à barres plates (ne se confond ni avec l ni avec 1).
from core import *

SC = round(ST * 1.06)                 # fût des capitales
TC = round(TH * 1.06)                 # barres des capitales
HW = round(1.10 * NW + 100)           # largeur d'un H
CRY = CAP / 2 + OV

def cstem(x, y0=0, y1=CAP): return rect(x, y0, x + SC, y1)

def serifs(x0, x1, bottom=True, top=True, l=True, r=True):
    ps = []
    if bottom: ps.append(cap_foot(x0, x1, l, r))
    if top: ps.append(cap_foot(x0, x1, l, r, y=CAP, top=True))
    return U(*ps)

def beak(x, y, dx=1, dy=-1, L=None, wb=None):
    """bec au bout d'une barre : coin vertical coupé net"""
    L = L or round(SH * 1.25); wb = wb or round(SC * 0.9)
    return poly([(x, y), (x, y + dy * L), (x - dx * 10, y + dy * L), (x - dx * wb, y)])

def cring(cx, rx, cy=CAP / 2, ry=CRY): return ring(cx, cy, rx, ry, sx=SC, sy=TC)

@reg('H', 'H')
def g_H():
    x1 = HW - SC; my = round(CAP * 0.52)
    return out(U(cstem(0), cstem(x1), rect(SC - 2, my - TC / 2, x1 + 2, my + TC / 2),
                 serifs(0, SC), serifs(x1, x1 + SC)))

@reg('I', 'I')
def g_I():
    slab = lambda y: rect(-round(W * 1.4), y, SC + round(W * 1.4), y + round(TC * 0.95))
    return out(U(cstem(0), slab(0), slab(CAP - round(TC * 0.95))), 'P', 'P')

@reg('J', 'J')
def g_J():
    h = 150; r = round(max(0.6 * SC + 60, SC + 50)); yb = -110
    o = ellipse(-r + SC, yb + h, r, h + OV); i = ellipse(-r + SC, yb + h, r - SC, h + OV - TC)
    hook = I(D(o, i), rect(-2 * r - 10, yb - OV - 5, SC, yb + h))
    hook = D(hook, rect(-2 * r - 20, yb + h - 40, -2 * r + SC + 4, yb + h + 10))
    return out(U(cstem(0, yb + h, CAP), hook, cap_foot(0, SC, y=CAP, top=True)), 'T', 'S')

@reg('L', 'L')
def g_L():
    x1 = round(0.80 * HW)
    return out(U(cstem(0), rect(0, 0, x1, TC), beak(x1, TC, dy=1), serifs(0, SC, bottom=False), cap_foot(0, SC, right=False)), 'S', 'T')

@reg('E', 'E')
def g_E():
    x1 = round(0.82 * HW); my = round(CAP * 0.52)
    return out(U(cstem(0), rect(0, 0, x1, TC), rect(0, CAP - TC, x1 - 20, CAP), rect(0, my - TC / 2, x1 - 90, my + TC / 2),
                 beak(x1, TC, dy=1), beak(x1 - 20, CAP - TC, dy=-1), cap_foot(0, SC, right=False), cap_foot(0, SC, right=False, y=CAP, top=True)), 'S', 'T')

@reg('F', 'F')
def g_F():
    x1 = round(0.80 * HW); my = round(CAP * 0.50)
    return out(U(cstem(0), rect(0, CAP - TC, x1, CAP), rect(0, my - TC / 2, x1 - 80, my + TC / 2),
                 beak(x1, CAP - TC, dy=-1), cap_foot(0, SC), cap_foot(0, SC, right=False, y=CAP, top=True)), 'S', 'T')

@reg('T', 'T')
def g_T():
    w = round(0.88 * HW); xs = w / 2 - SC / 2
    return out(U(rect(0, CAP - TC, w, CAP), cstem(xs), cap_foot(xs, xs + SC),
                 beak(0, CAP - TC, dx=-1, dy=-1), beak(w, CAP - TC, dy=-1)), 'T', 'T')

@reg('O', 'O')
def g_O():
    rx = round(0.56 * HW + 0.1 * SC)
    return out(cring(rx, rx), 'O', 'O')

@reg('Q', 'Q')
def g_Q():
    rx = round(0.56 * HW + 0.1 * SC)
    tail = poly([(rx - 40, 40), (rx + 20, 40 + TC * 0.4), (2 * rx + 60, -150), (2 * rx + 30, -170 - TC * 0.3)])
    tail = U(tail, poly([(rx - 50, 70), (rx + 40, 70), (rx + 60, -10), (rx - 20, -10)]))
    return out(U(cring(rx, rx), I(tail, rect(rx - 60, -200, 2 * rx + 80, 80))), 'O', 'D')

@reg('C', 'C')
def g_C():
    # un rond ouvert à droite par une fenêtre : les deux bouts finissent par une face horizontale, comme le crochet du 9
    rx = round(0.53 * HW + 0.1 * SC); cx = rx; cy = CAP / 2; o = round(0.27 * CAP)
    return out(D(cring(cx, rx), rect(cx + 0.15 * rx, cy - o, cx + rx + 10, cy + o)), 'O', 'T')

@reg('G', 'G')
def g_G():
    # le C, fermé en bas à droite par un fût qui monte jusqu'à la barre ; la fenêtre ne s'ouvre qu'au-dessus de la barre
    rx = round(0.55 * HW + 0.1 * SC); cx = rx; cy = CAP / 2; o = round(0.27 * CAP); yb = round(CAP * 0.46)
    r = D(cring(cx, rx), rect(cx + 0.15 * rx, yb - TC, cx + rx + 10, cy + o))
    xs = cx + rx - SC
    jamb = rect(xs, 30, xs + SC, yb)
    barre = rect(cx + 20, yb - TC, xs + SC, yb)
    return out(U(r, jamb, barre), 'O', 'S')

@reg('D', 'D')
def g_D():
    rx = round(0.48 * HW); cx = round(0.42 * HW)
    half = I(cring(cx, rx, ry=CAP / 2), rect(cx, -OV - 5, cx + rx + 5, CAP + OV + 5))
    bars = U(rect(0, CAP - TC, cx + 2, CAP), rect(0, 0, cx + 2, TC))
    return out(U(cstem(0), half, bars, cap_foot(0, SC, right=False), cap_foot(0, SC, right=False, y=CAP, top=True)), 'S', 'O')

def bowl_r(x0, y0, y1, xr):
    """bol fermé à droite entre y0 et y1, accroché au fût, finit en xr"""
    ry = (y1 - y0) / 2; cy = y0 + ry; rx = min(ry * 1.05, (xr - x0) * 0.62); cx = xr - rx
    half = I(D(ellipse(cx, cy, rx, ry), ellipse(cx, cy, rx - SC * 0.96, ry - TC)), rect(cx, y0 - 5, xr + 5, y1 + 5))
    return U(half, rect(x0, y1 - TC, cx + 2, y1), rect(x0, y0, cx + 2, y0 + TC))

@reg('P', 'P')
def g_P():
    x1 = round(0.78 * HW)
    return out(U(cstem(0), bowl_r(0, round(CAP * 0.40), CAP, x1), cap_foot(0, SC), cap_foot(0, SC, right=False, y=CAP, top=True)), 'S', 'O')

@reg('R', 'R')
def g_R():
    x1 = round(0.78 * HW); yb = round(CAP * 0.42)
    leg = I(bar(round(0.48 * HW), yb + 10, x1 + 20, 0, SC * 1.02), rect(SC, 0, x1 + 200, yb + TC))
    return out(U(cstem(0), bowl_r(0, yb, CAP, x1), leg, cap_foot(0, SC), cap_foot(0, SC, right=False, y=CAP, top=True),
                 cap_foot(x1 + 20 - SC * 0.5, x1 + 20 + SC * 0.52, left=False)), 'S', 'D')

@reg('B', 'B')
def g_B():
    x1 = round(0.80 * HW); ym = round(CAP * 0.54)
    return out(U(cstem(0), bowl_r(0, ym - TC, CAP, x1 - 40), bowl_r(0, 0, ym, x1),
                 cap_foot(0, SC, right=False), cap_foot(0, SC, right=False, y=CAP, top=True)), 'S', 'O')

@reg('U', 'U')
def g_U():
    x1 = HW - SC; h = round(CAP * 0.36)
    cx = (x1 + SC) / 2; rx = cx
    c = I(D(ellipse(cx, h, rx, h + OV), ellipse(cx, h, rx - SC, h + OV - TC)), rect(-5, -OV - 5, x1 + SC + 5, h + 2))
    tr = SC                                   # même épaisseur que la cuvette : pas de marche
    return out(U(cstem(0, h - 2, CAP), rect(x1 + SC - tr, h - 2, x1 + SC, CAP), c,
                 cap_foot(0, SC, y=CAP, top=True), cap_foot(x1 + SC - tr, x1 + SC, y=CAP, top=True)), 'S', 'S')

def vee(x0, x1, top, t1, t2, bot=0):
    m = (x0 + x1) / 2
    return I(U(bar(x0, top, m - 4, bot, t1), bar(x1, top, m + 4, bot, t2)), rect(x0 - 300, bot, x1 + 300, top))

@reg('V', 'V')
def g_V():
    x1 = round(0.96 * HW); t1 = SC * 1.06; t2 = SC * 0.72
    return out(U(vee(0, x1, CAP, t1, t2), cap_foot(-t1 / 2, t1 / 2, y=CAP, top=True), cap_foot(x1 - t2 / 2, x1 + t2 / 2, y=CAP, top=True)), 'D', 'D')

@reg('A', 'A')
def g_A():
    x1 = round(0.96 * HW); m = x1 / 2; t1 = SC * 0.72; t2 = SC * 1.06
    a = I(U(bar(0, 0, m - 6, CAP, t1), bar(x1, 0, m + 6, CAP, t2)), rect(-300, 0, x1 + 300, CAP + 10))
    apex = rect(m - t1 / 2 - 8, CAP - 6, m + t2 / 2 + 8, CAP + 10)
    yb = round(CAP * 0.30); xl = yb / CAP * (m - 6); xr = x1 - yb / CAP * (x1 - m - 6)
    cross = rect(xl, yb, xr, yb + TC)
    return out(U(a, apex, cross, cap_foot(-t1 / 2 - 4, t1 / 2 + 4), cap_foot(x1 - t2 / 2, x1 + t2 / 2)), 'D', 'D')

@reg('W', 'W')
def g_W():
    s = round(0.70 * HW); t1 = SC * 1.0; t2 = SC * 0.70
    w = U(vee(0, s, CAP, t1, t2), vee(s, 2 * s, CAP, t1, t2))
    w = D(w, rect(s - t1, CAP - round(SH * 0.9), s + t2, CAP + 50))                # sommet du milieu coupé droit, un peu plus bas
    return out(U(w, cap_foot(-t1 / 2, t1 / 2, y=CAP, top=True), cap_foot(2 * s - t2 / 2, 2 * s + t2 / 2, y=CAP, top=True)), 'D', 'D')

@reg('X', 'X')
def g_X():
    x1 = round(0.90 * HW); t1 = SC * 1.04; t2 = SC * 0.72
    x = I(U(bar(0, CAP, x1, 0, t1), bar(x1, CAP, 0, 0, t2)), rect(-300, 0, x1 + 300, CAP))
    return out(U(x, cap_foot(-t1 / 2, t1 / 2, y=CAP, top=True), cap_foot(x1 - t2 / 2, x1 + t2 / 2, y=CAP, top=True),
                 cap_foot(-t2 / 2, t2 / 2), cap_foot(x1 - t1 / 2, x1 + t1 / 2)), 'D', 'D')

@reg('Y', 'Y')
def g_Y():
    x1 = round(0.92 * HW); m = x1 / 2; t1 = SC * 1.04; t2 = SC * 0.72; yj = round(CAP * 0.42)
    arms = I(U(bar(0, CAP, m - 2, yj, t1), bar(x1, CAP, m + 2, yj, t2)), rect(-300, yj - 20, x1 + 300, CAP))
    s = cstem(m - SC / 2, 0, yj + 30)
    return out(U(arms, s, cap_foot(m - SC / 2, m + SC / 2), cap_foot(-t1 / 2, t1 / 2, y=CAP, top=True),
                 cap_foot(x1 - t2 / 2, x1 + t2 / 2, y=CAP, top=True)), 'D', 'D')

@reg('K', 'K')
def g_K():
    x1 = round(0.84 * HW); t = SC * 0.9
    arm = I(bar(SC + 10, round(CAP * 0.30), x1 - 10, CAP, t), rect(SC - 20, 0, x1 + 200, CAP))
    yj = round(CAP * 0.46); xj = SC + 10 + (yj - CAP * 0.30) / (CAP * 0.70) * (x1 - 20 - SC)
    leg = I(bar(xj, yj, x1 + 20, 0, SC * 1.04), rect(SC - 20, 0, x1 + 200, CAP))
    return out(U(cstem(0), arm, leg, serifs(0, SC), cap_foot(x1 - 10 - t / 2, x1 - 10 + t / 2, y=CAP, top=True),
                 cap_foot(x1 + 20 - SC * 0.52, x1 + 20 + SC * 0.52, left=False)), 'S', 'D')

@reg('N', 'N')
def g_N():
    x1 = round(0.98 * HW); tn = round(SC * 0.70)
    diag = I(poly([(0, CAP), (SC * 1.15, CAP), (x1, 0), (x1 - SC * 1.15, 0)]), rect(0, 0, x1, CAP))
    return out(U(rect(0, 0, tn, CAP), rect(x1 - tn, 0, x1, CAP), diag,
                 cap_foot(0, tn), cap_foot(0, tn, right=False, y=CAP, top=True), cap_foot(x1 - tn, x1, y=CAP, top=True)), 'S', 'S')

@reg('M', 'M')
def g_M():
    x1 = round(1.20 * HW); tn = round(SC * 0.70); m = x1 / 2
    d1 = poly([(0, CAP), (SC * 1.15, CAP), (m + SC * 0.4, 0), (m - SC * 0.6, 0)])
    d2 = poly([(x1 - tn, CAP), (x1, CAP), (m + tn * 0.5, 0), (m - tn * 0.5, 0)])
    body = I(U(d1, d2), rect(0, 0, x1, CAP))
    return out(U(rect(0, 0, tn, CAP), rect(x1 - SC, 0, x1, CAP), body,
                 cap_foot(0, tn), cap_foot(0, tn, right=False, y=CAP, top=True), cap_foot(x1 - SC, x1),
                 cap_foot(x1 - SC, x1, left=False, y=CAP, top=True)), 'S', 'S')

@reg('Z', 'Z')
def g_Z():
    x1 = round(0.84 * HW); t = SC * 1.04
    z = U(rect(0, CAP - TC, x1, CAP), rect(0, 0, x1, TC), bar(x1 - t / 2 - 6, CAP - TC, t / 2 + 6, TC, t))
    z = I(z, rect(0, 0, x1, CAP))
    return out(U(z, beak(0, CAP - TC, dx=-1, dy=-1), beak(x1, TC, dy=1)), 'T', 'T')

@reg('S', 'S')
def g_S():
    rx = round(0.42 * HW + 0.2 * SC); ry = (CAP + TC) / 4 + OV / 2; cx = rx
    up = I(ring(cx, CAP + OV - ry, rx, ry, sx=SC * 0.92, sy=TC, r=0), pie(cx, CAP + OV - ry, 30, 270))
    lo = I(ring(cx, -OV + ry, rx, ry, sx=SC * 0.92, sy=TC, r=0), pie(cx, -OV + ry, 210, 450))
    return out(U(up, lo), 'T', 'T')

# lettres de plus
@reg('AE', 'Æ')
def g_AE():
    x1 = round(1.30 * HW); m = round(0.50 * HW); t1 = SC * 0.72; yb = round(CAP * 0.30)
    diag = I(bar(0, 0, m, CAP, t1), rect(-300, 0, x1, CAP))
    xs = m - 10; my = round(CAP * 0.52)
    e = U(cstem(xs), rect(xs, 0, x1, TC), rect(m - 20, CAP - TC, x1 - 20, CAP), rect(xs, my - TC / 2, x1 - 90, my + TC / 2),
          beak(x1, TC, dy=1), beak(x1 - 20, CAP - TC, dy=-1), cap_foot(xs, xs + SC, right=False))
    cross = rect(yb / CAP * m, yb, xs + 2, yb + TC)
    return out(U(diag, e, cross, cap_foot(-t1 / 2 - 4, t1 / 2 + 4)), 'D', 'T')

@reg('OE', 'Œ')
def g_OE():
    rx = round(0.50 * HW); cx = rx
    o = I(cring(cx, rx), rect(-10, -OV - 5, cx + 5, CAP + OV + 5))
    xs = cx; x1 = cx + round(0.70 * HW); my = round(CAP * 0.52)
    e = U(cstem(xs), rect(xs, 0, x1, TC), rect(xs, CAP - TC, x1 - 20, CAP), rect(xs, my - TC / 2, x1 - 90, my + TC / 2),
          beak(x1, TC, dy=1), beak(x1 - 20, CAP - TC, dy=-1))
    return out(U(o, e), 'O', 'T')

@reg('Oslash', 'Ø')
def g_Oslash():
    rx = round(0.56 * HW + 0.1 * SC)
    return out(U(cring(rx, rx), bar(2 * rx - 20, CAP + 50, 20, -50, TC * 1.05)), 'O', 'O')

@reg('Eth', 'Ð')
def g_Eth():
    p = g_D()[0]
    return out(U(p, rect(-80, CAP * 0.48 - TC / 2, SC + 160, CAP * 0.48 + TC / 2)), 'T', 'O')

@reg('Thorn', 'Þ')
def g_Thorn():
    x1 = round(0.76 * HW)
    return out(U(cstem(0), bowl_r(0, round(CAP * 0.18), round(CAP * 0.80), x1), serifs(0, SC)), 'S', 'O')

@reg('Lslash', 'Ł')
def g_Lslash():
    return out(U(g_L()[0], poly([(-90, CAP * 0.36), (SC + 120, CAP * 0.56), (SC + 120, CAP * 0.56 + TC), (-90, CAP * 0.36 + TC)])), 'T', 'T')

@reg('Dcroat', 'Đ')
def g_Dcroat(): return g_Eth()

@reg('Hbar', 'Ħ')
def g_Hbar():
    x1 = HW - SC
    return out(U(g_H()[0], rect(-50, CAP * 0.74, x1 + SC + 50, CAP * 0.74 + TC * 0.9)), 'T', 'T')

@reg('uni1E9E', 'ẞ')
def g_capsharps():
    x1 = round(0.80 * HW); top = CAP
    t = rect(0, top - TC, x1 - 30, top)
    d = I(bar(x1 - 40, top - TC / 2, round(0.42 * HW), round(CAP * 0.56), SC * 0.95), rect(0, CAP * 0.5, x1, top))
    lo = bowl_r(SC, 0, round(CAP * 0.60), x1 + 20)
    lo = D(lo, rect(SC - 5, -10, round(0.30 * HW), round(CAP * 0.60) + 10))
    lo = U(lo, rect(round(0.30 * HW) - 2, round(CAP * 0.60) - TC, round(0.46 * HW), round(CAP * 0.60)))
    return out(U(cstem(0), t, d, lo, cap_foot(0, SC), cap_foot(0, SC, right=False, y=CAP, top=True)), 'S', 'O')
