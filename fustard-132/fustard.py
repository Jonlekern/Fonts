# Fûstard 132 : Jalousia en techno gothique. Géométrie stricte (90°, 0°, 67,5°, 45°),
# chaque jonction devient un croisement (les traits dépassent de OV),
# bouts en pointe, arrondis réguliers, O en ogive.
import sys, math
import numpy as np
from PIL import Image, ImageDraw
import os
_ICI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [_ICI, os.path.join(_ICI, '..', 'jalousia')]
import essai, droit, arrondi

OV = 70.0                          # dépassement aux croisements
T67 = math.tan(math.radians(67.5))
C67, S67 = math.cos(math.radians(67.5)), math.sin(math.radians(67.5))

def path(pts, nseg=20):
    """pts : (x, y) ou (x, y, rayon) ; un rayon > 0 arrondit le coin."""
    P = [np.array(p[:2], float) for p in pts]
    rads = [p[2] if len(p) > 2 else 0 for p in pts]
    out = [P[0]]
    for i in range(1, len(P) - 1):
        a, b, c = P[i - 1], P[i], P[i + 1]
        if rads[i] <= 0:
            out.append(b); continue
        u1 = (b - a) / np.linalg.norm(b - a); u2 = (c - b) / np.linalg.norm(c - b)
        turn = math.acos(np.clip(u1 @ u2, -1, 1))
        if turn < 1e-3:
            out.append(b); continue
        t = rads[i] * math.tan(turn / 2)
        p1 = b - u1 * t; p2 = b + u2 * t
        nrm = np.array([-u1[1], u1[0]])
        if u1[0] * u2[1] - u1[1] * u2[0] < 0: nrm = -nrm
        ctr = p1 + nrm * rads[i]
        a1 = math.atan2(*(p1 - ctr)[::-1]); a2 = math.atan2(*(p2 - ctr)[::-1])
        da = (a2 - a1 + math.pi) % (2 * math.pi) - math.pi
        for k in range(nseg + 1):
            ang = a1 + da * k / nseg
            out.append(ctr + rads[i] * np.array([math.cos(ang), math.sin(ang)]))
    out.append(P[-1])
    # retirer les points quasi confondus (un segment de longueur ~0 fausse les coins à l'onglet)
    propre = [out[0]]
    for p in out[1:-1]:
        if np.linalg.norm(p - propre[-1]) > 2.0:
            propre.append(p)
    if np.linalg.norm(out[-1] - propre[-1]) <= 2.0 and len(propre) > 1:
        propre[-1] = out[-1]
    else:
        propre.append(out[-1])
    return propre

def S(*pts):
    return dict(p=path(pts), caps=['tip', 'tip'])

H = 1000
MEME_TAILLE = True   # toutes les capitales montent à H + ov et descendent à -ov
PC = lambda: 70 if MEME_TAILLE else 90   # bout extérieur des petites croix (70 f = ov)

def ogive_over(ov, cx=315.0, top=1010.0, bot=-5.0, w=245.0):
    """Longueur de dépassement des arcs de l'ogive pour que les pointes montent à H + ov."""
    lo, hi = ov, 4 * ov
    for _ in range(40):
        m = (lo + hi) / 2
        L, R_ = arrondi.ogive(cx=cx, top=top, bot=bot, w=w, over=m)
        y = max(p[1] for p in L['p'])
        lo, hi = (m, hi) if y < H + ov else (lo, m)
    return (lo + hi) / 2

def build(ov=70.0):
    f = ov / 70.0
    G = {}
    G['L'] = [S((0, H + ov), (0, -ov)),
              S((-150, H), (330, H)),
              S((-ov, 0), (560, 0))]
    # A : celui de la version sharp, gardé tel quel
    if MEME_TAILLE:
        # A de la version sharp, avec les dépassements : les deux traits se croisent au-dessus
        # de la barre du haut, et chaque pied traverse une barre posée sur la ligne
        pd, pa = np.array([12.0, 15.0]), np.array([430.0, 1000.0])     # diagonale gauche
        qa, qd = np.array([390.0, 1000.0]), np.array([616.0, 21.0])    # trait de droite
        ud = (pa - pd) / np.linalg.norm(pa - pd); ur = (qd - qa) / np.linalg.norm(qd - qa)
        g0 = pd - ud * ((pd[1] + ov) / ud[1]); g1 = pa + ud * (ov / ud[1])
        d0 = qa - ur * (ov / -ur[1]); d1 = qd + ur * ((qd[1] + ov) / -ur[1])
        xg = pd[0] - pd[1] * ud[0] / ud[1]; xd = qd[0] + qd[1] * ur[0] / -ur[1]
        G['A'] = [S((230, H), (650, H)), S(tuple(g0), tuple(g1)), S(tuple(d0), tuple(d1)),
                  S((100, 347), (660, 347)),
                  S((xg - 150, 0), (xg + 150, 0)), S((xd - 150, 0), (xd + 150, 0))]
    else:
        G['A'] = arrondi.G3s['A']
    G['F'] = [S((120, H + ov), (120, -ov)),
              S((0, H), (560, H)),
              S((560 - 30 * f, H + PC() * f), (560 - 30 * f, H - 110 * f)),
              S((120 - ov, 520), (440, 520)),
              S((-30, 0), (290, 0))]
    G['E'] = [S((0, H + ov), (0, -ov)),
              S((-ov, H), (540, H)),
              S((540 - 30 * f, H + PC() * f), (540 - 30 * f, H - 110 * f)),
              S((-ov, 510), (420, 510)),
              S((-ov, 0), (560, 0))]
    xr = 560
    yb = (xr - 360) * T67
    G['U'] = [S((-60, H), (260, H)),
              S((100, H + ov), (100, 0, 130), (360, 0, 150), (xr + ov * C67, yb + ov * S67)),
              S((xr, H + ov), (xr, -ov if MEME_TAILLE else 0)),
              S((xr - 80, H), (xr + 180, H))] + ([S((xr - 130, 0), (xr + 150, 0))] if MEME_TAILLE else [])
    xl = 260 + 480 / T67
    G['R'] = [S((0, H + ov), (0, 0)),
              S((-ov, H), (480, H, 240), (480, 480, 240), (-ov, 480)),
              dict(S((-ov + 30 * f, 480 + 80 * f), (-ov + 30 * f, 480 - 80 * f)), detail=True),
              S((260 - ov * C67, 480 + ov * S67), (xl + ov * C67, -ov * S67)),
              S((xl - 110, 0), (xl + 150, 0))]
    G['S'] = [S((560, H), (40, H, 160), (40, 700, 120), (520, 220, 170), (520, 0, 150), (0, 0)),
              S((560 - 30 * f, H + PC() * f), (560 - 30 * f, H - 110 * f)),
              S((30 * f, 110 * f), (30 * f, -PC() * f))]
    G['T'] = [S((0, H), (700, H)),
              S((350, H + ov), (350, -ov)),
              S((200, 0), (500, 0))]
    r2 = math.sqrt(0.5)
    G['D'] = [S((0, H + ov), (0, -ov)),
              S((-ov * r2, H + ov * r2), (520, H - 520 - min(ov, 210.0) * r2, 220), (520, 0, 220), (-ov, 0))]
    G['I'] = [S((0, H + ov), (0, -ov)),
              S((-200, H), (200, H)),
              S((-220, 0), (220, 0))]
    ov_o = ov   # l'ogive garde ses pointes courbes (le cercle plafonne vers 1150)
    G['O'] = arrondi.ogive(over=ov_o)

    # ---- le reste de l'alphabet ----
    def croix_haut(x, y):   # petite croix verticale en bout de barre (E, F, S)
        return dict(S((x, y + PC() * f), (x, y - 110 * f)), detail=True)
    def croix_bas(x, y):
        return dict(S((x, y + 110 * f), (x, y - PC() * f)), detail=True)
    def diag(x0, y0, x1, y1, a=True, b=True):   # trait qui dépasse de ov à ses bouts
        u = np.array([x1 - x0, y1 - y0], float); u /= np.linalg.norm(u)
        p = np.array([x0, y0]) - (u * ov if a else 0)
        q = np.array([x1, y1]) + (u * ov if b else 0)
        return S(tuple(p), tuple(q))
    w67 = H / T67          # largeur d'une diagonale à 67,5° sur toute la hauteur (414)

    # V (dessin) : fût gauche droit, diagonale à 67,5°, posé sur une barre
    G['V'] = [S((0, H + ov), (0, -ov)),
              diag(0, 0, w67, H, a=True, b=True),
              S((-150, H), (180, H)),
              S((w67 - 110, H), (w67 + 230, H)),
              S((-160, 0), (240, 0))]
    # X (dessin) : deux diagonales à 67,5°, quatre barres
    G['X'] = [diag(0, H, w67, 0), diag(0, 0, w67, H),
              S((-160, H), (150, H)), S((w67 - 120, H), (w67 + 170, H)),
              S((-170, 0), (140, 0)), S((w67 - 140, 0), (w67 + 160, 0))]
    # M (dessin) : /|/| pendu à une barre
    G['M'] = [diag(0, 0, w67, H, a=False),
              S((w67, H + ov), (w67, -ov)),
              diag(w67, 0, 2 * w67, H),
              S((2 * w67, H + ov), (2 * w67, 0)),
              S((90, H), (2 * w67 + 160, H))]
    # W : le M retourné, barre en bas
    G['W'] = [S((0, H + ov), (0, -ov)),
              diag(0, 0, w67, H),
              S((w67, H + ov), (w67, -ov)),
              diag(w67, 0, 2 * w67, H),
              S((-90, 0), (2 * w67 + 90, 0)),
              S((-150, H), (170, H)),
              S((2 * w67 - 110, H), (2 * w67 + 230, H))]
    # C (dessin) : C carré, croix au bout de la barre du haut
    G['C'] = [S((0, H + ov), (0, -ov)),
              S((-ov, H), (540, H)),
              croix_haut(540 - 30 * f, H),
              S((-ov, 0), (560, 0))]
    # G : le C, plus un jambage à droite et une barre vers l'intérieur
    G['G'] = [S((0, H + ov), (0, -ov)),
              S((-ov, H), (540, H)),
              croix_haut(540 - 30 * f, H),
              S((-ov, 0), (520 + ov, 0)),
              S((520, -ov), (520, 470 + ov)),
              S((300, 470), (520 + ov, 470))]
    # B : deux panses du R
    G['B'] = [S((0, H + ov), (0, -ov)),
              S((-ov, H), (440, H, 220), (440, 530, 220), (-ov, 530)),
              S((-ov, 530), (500, 530, 250), (500, 0, 250), (-ov, 0))]
    # P : fût, panse du R, pied
    G['P'] = [S((0, H + ov), (0, -ov)),
              S((-ov, H), (480, H, 240), (480, 440, 240), (-ov, 440)),
              dict(S((-ov + 30 * f, 440 + 80 * f), (-ov + 30 * f, 440 - 80 * f)), detail=True),
              S((-150, 0), (170, 0))]
    # H : deux fûts, barre, empattements en croix
    G['H'] = [S((0, H + ov), (0, -ov)), S((540, H + ov), (540, -ov)),
              S((-ov, 500), (540 + ov, 500)),
              S((-150, H), (150, H)), S((390, H), (690, H)),
              S((-150, 0), (150, 0)), S((390, 0), (690, 0))]
    # J : fût, crosse arrondie, croix du S au bout
    G['J'] = [S((360, H + ov), (360, 0, 170), (0, 0)),
              S((210, H), (510, H)),
              croix_bas(30 * f, 0)]
    # K : fût, bras à 45°, jambe à 67,5°
    xk = 200 + 680 / T67
    G['K'] = [S((0, H + ov), (0, -ov)),
              S((-150, H), (150, H)), S((-150, 0), (150, 0)),
              diag(0, 480, 520, H),
              S((400, H), (680, H)),
              diag(200, 680, xk, 0),
              S((xk - 130, 0), (xk + 150, 0))]
    # N : fût, diagonale à 67,5°, fût
    G['N'] = [S((0, H + ov), (0, -ov)), S((w67, H + ov), (w67, -ov)),
              diag(0, H, w67, 0),
              S((-150, 0), (150, 0)), S((w67 - 150, H), (w67 + 150, H))]
    # Q : l'ogive du O, queue à 45° qui traverse la pointe du bas
    # Q : l'arc de gauche du O continue sa courbe en longue queue, barrée d'une croix
    Ov = arrondi.ogive(over=ov_o)
    cxq, hq, wq = 315.0, 507.5, 245.0
    aq = (hq * hq - wq * wq) / (2 * wq); rq = aq + wq; cyq = 502.5
    phq = math.atan2(hq, aq)
    t0, t1 = math.pi - phq - ov_o / rq, math.pi + phq + 520 / rq
    queue = [np.array([cxq + aq + rq * math.cos(t), cyq + rq * math.sin(t)]) for t in np.linspace(t0, t1, 120)]
    tc = t1 - 30 * f / rq
    xc, yc_ = cxq + aq + rq * math.cos(tc), cyq + rq * math.sin(tc)
    G['Q'] = [dict(p=queue, caps=['tip', 'tip']), Ov[1], dict(S((xc, yc_ + 55 * f), (xc, yc_ - 45 * f)), detail=True)]   # croix moitié plus courte
    # Y : deux bras à 67,5° qui se croisent, fût, pied
    yc = 470
    by = (H - yc) / T67
    G['Y'] = [diag(0, H, by, yc), diag(2 * by, H, by, yc),
              S((by, yc + ov), (by, -ov)),
              S((-140, H), (150, H)), S((2 * by - 150, H), (2 * by + 140, H)),
              S((by - 160, 0), (by + 160, 0))]
    # Z : barres, diagonale à 67,5°, croix aux deux bouts comme le S
    G['Z'] = [S((0, H), (w67 + 140, H)),
              diag(w67 + 140, H, 140, 0),
              S((-ov, 0), (w67 + 160, 0)),
              croix_haut(30 * f, H),
              croix_bas(w67 + 160 - 30 * f, 0)]

    # ---- chiffres ----
    def boucle(pts):   # trait fermé : départ et arrivée se recouvrent
        st = S(*pts); st['caps'] = ['T', 'T']; return st
    o0 = arrondi.ogive(cx=250.0, top=H + 5, bot=-5.0, w=200.0, over=ov)
    G['0'] = o0 + [diag(250 - 380 / T67 / 2 * 1.0, 310, 250 + 380 / T67 / 2 * 1.0, 690)]
    G['1'] = [S((260, H + ov), (260, -ov)),
              diag(260, H, 40, H - 220 / 1.0),
              S((100, 0), (420, 0))]
    G['2'] = [S((0, H), (460, H, 180), (460, 460, 120), (0, 0)),
              croix_haut(30 * f, H),
              S((-ov, 0), (520, 0)),
              S((0, 0), (-ov * 0.7071, -ov * 0.7071))]
    G['3'] = [S((0, H), (420, H, 180), (420, 540, 180), (120, 540)),
              S((120 - ov, 540), (460, 540, 200), (460, 0, 200), (0, 0)),
              croix_haut(30 * f, H), croix_bas(30 * f, 0)]
    x4 = 360 - 700 / T67
    G['4'] = [S((360, H + ov), (360, -ov)),
              diag(360, H, x4, 300),
              S((x4 - ov, 300), (360 + ov + 80, 300)),
              S((220, 0), (500, 0))]
    G['5'] = [S((40, H), (480, H)), croix_haut(480 - 30 * f, H),
              S((40, H + ov), (40, 560)),
              S((40 - ov, 560), (460, 560, 200), (460, 0, 200), (0, 0)),
              croix_bas(30 * f, 0)]
    G['6'] = [S((420, H), (0, H, 180), (0, 0, 180), (460, 0, 180), (460, 560, 180), (-ov, 560)),
              croix_haut(420 - 30 * f, H)]
    x7 = 480 - H / T67
    G['7'] = [S((0, H), (480, H)), croix_haut(30 * f, H),
              diag(480, H, x7, 0),
              S((x7 + 480 / T67 - 140, 480), (x7 + 480 / T67 + 140, 480)),
              S((x7 - 130, 0), (x7 + 150, 0))]
    G['8'] = [boucle([(230, 540), (400, 540, 150), (400, H, 150), (60, H, 150), (60, 540, 150), (230, 540)]),
              boucle([(230, 540), (460, 540, 180), (460, 0, 180), (0, 0, 180), (0, 540, 180), (230, 540)]),
              S((-ov, 540), (460 + ov, 540))]
    G['9'] = [S((40, 0), (460, 0, 180), (460, H, 180), (0, H, 180), (0, 440, 180), (460 + ov, 440)),
              croix_bas(40 + 30 * f, 0)]
    return G

def build_chiffres_maj(ov):
    """Chiffres majuscules : coins vifs, chaque jonction en croix, comme les capitales."""
    f = ov / 70.0
    def croix_haut(x, y):
        return dict(S((x, y + PC() * f), (x, y - 110 * f)), detail=True)
    def croix_bas(x, y):
        return dict(S((x, y + 110 * f), (x, y - PC() * f)), detail=True)
    def diag(x0, y0, x1, y1, a=True, b=True):
        u = np.array([x1 - x0, y1 - y0], float); u /= np.linalg.norm(u)
        p = np.array([x0, y0]) - (u * ov if a else 0)
        q = np.array([x1, y1]) + (u * ov if b else 0)
        return S(tuple(p), tuple(q))
    def v(x, y0, y1):        # vertical qui dépasse en haut et en bas
        return S((x, y1 + ov), (x, y0 - ov))
    def h(y, x0, x1):        # horizontale qui dépasse à gauche et à droite
        return S((x0 - ov, y), (x1 + ov, y))
    W = 440
    C = {}
    C['0'] = [v(0, 0, H), v(W, 0, H), h(H, 0, W), h(0, 0, W),
              diag(W / 2 - 300 / T67, 200, W / 2 + 300 / T67, 800)]
    C['1'] = [v(220, 0, H), S((40, 0), (400, 0)),
              diag(220, H, 20, H - 200)]
    C['2'] = [h(H, 0, W), S((W, H + ov), (W, 440)),
              diag(W, 440, 0, 0) if not MEME_TAILLE else S((W + ov * 0.7071, 440 + ov * 0.7071), (-ov, -ov)), h(0, 0, W)]
    C['3'] = [h(H, 0, W), v(W, 0, H), S((100, 520), (W + ov, 520)), h(0, 0, W)]
    x4 = 360 - 700 / T67
    C['4'] = [v(360, 0, H), diag(360, H, x4, 300),
              S((x4 - ov, 300), (360 + ov + 80, 300)), S((220, 0), (500, 0)),
              S((260, H), (460, H))]
    C['5'] = [h(H, 0, W), S((0, H + ov), (0, 520 - ov)), h(520, 0, W),
              S((W, 520 + ov), (W, -ov)), h(0, 0, W)]
    C['6'] = [v(0, 0, H), S((-ov, H), (W, H)), croix_haut(W - 30 * f, H),
              h(520, 0, W), S((W, 520 + ov), (W, -ov)), h(0, 0, W)]
    x7 = 480 - H / T67
    C['7'] = [h(H, 0, 480), diag(480, H, x7, 0),
              S((x7 + 480 / T67 - 150, 480), (x7 + 480 / T67 + 150, 480)),
              S((x7 - 140, 0), (x7 + 160, 0))]
    C['8'] = [v(0, 0, H), v(W, 0, H), h(H, 0, W), h(520, 0, W), h(0, 0, W)]
    C['9'] = [v(W, 0, H), h(H, 0, W), S((0, H + ov), (0, 480 - ov)), h(480, 0, W),
              S((0, 0), (W + ov, 0)), croix_bas(30 * f, 0)]
    return C

XH, ASC, DESC = 600.0, 1000.0, -380.0   # hauteur des minuscules, montantes, descendantes

def build_lc(ov):
    """Minuscules. ov : dépassement des croisements (en proportion de la hauteur des minuscules)."""
    f = ov / 70.0
    X, A, D = XH, ASC, DESC
    def croix_haut(x, y):
        return dict(S((x, y + PC() * f), (x, y - 110 * f)), detail=True)
    def croix_bas(x, y):
        return dict(S((x, y + 110 * f), (x, y - PC() * f)), detail=True)
    def diag(x0, y0, x1, y1, a=True, b=True):
        u = np.array([x1 - x0, y1 - y0], float); u /= np.linalg.norm(u)
        p = np.array([x0, y0]) - (u * ov if a else 0)
        q = np.array([x1, y1]) + (u * ov if b else 0)
        return S(tuple(p), tuple(q))
    def croix_point(x, y, s=70):     # le point du i et du j est une croix
        return [S((x, y + s), (x, y - s)), S((x - s, y), (x + s, y))]
    w = X / T67
    L = {}
    L['a'] = [S((360, X + ov), (360, -ov)),
              S((40, X), (360 + ov, X)), croix_haut(40 + 30 * f, X),
              S((360 + ov, 320), (0, 320, 150), (0, 0, 150), (360 + ov, 0))]
    L['b'] = [S((0, A + ov), (0, -ov)), S((-150, A), (150, A)),
              S((-ov, X), (420, X, 200), (420, 0, 200), (-ov, 0))]
    L['c'] = [S((0, X + ov), (0, -ov)),
              S((-ov, X), (400, X)), croix_haut(400 - 30 * f, X),
              S((-ov, 0), (420, 0))]
    L['d'] = [S((420, A + ov), (420, -ov)), S((270, A), (570, A)),
              S((420 + ov, X), (0, X, 200), (0, 0, 200), (420 + ov, 0))]
    # e : un seul trait, arrondi en haut, coin vif en bas à gauche, barre qui traverse à gauche
    L['e'] = [S((-ov, 300), (420, 300), (420, X, 150), (0, X, 150), (0, 0), (440, 0)),
              croix_bas(440 - 30 * f, 0)]
    L['f'] = [S((120, A + ov), (120, -ov)),
              S((120 - ov, A), (440, A)), croix_haut(440 - 30 * f, A),
              S((-30, X), (320, X)),
              S((-30, 0), (290, 0))]
    L['g'] = [S((420, X + ov), (420, D, 150), (0, D)), croix_bas(30 * f, D),
              S((420 + ov, X), (0, X, 200), (0, 0, 200), (420 + ov, 0))]
    L['h'] = [S((0, A + ov), (0, 0)), S((-150, A), (150, A)),
              S((-ov, X), (420, X, 200), (420, 0))]
    L['i'] = [S((0, X + ov), (0, -ov)), S((-150, X), (150, X)), S((-150, 0), (150, 0))] + \
             croix_point(0, X + ov + 160)
    L['j'] = [S((300, X + ov), (300, D, 150), (0, D)), croix_bas(30 * f, D),
              S((150, X), (450, X))] + croix_point(300, X + ov + 160)
    xk = 150 + 400 / T67
    L['k'] = [S((0, A + ov), (0, -ov)), S((-150, A), (150, A)), S((-150, 0), (150, 0)),
              diag(0, 250, 350, X), S((230, X), (500, X)),
              diag(150, 400, xk, 0), S((xk - 120, 0), (xk + 140, 0))]
    L['l'] = [S((0, A + ov), (0, -ov)), S((-200, A), (80, A)), S((-ov, 0), (260, 0))]
    L['m'] = [S((0, X + ov), (0, 0)),
              S((-ov, X), (620, X, 150), (620, 0)),
              S((310, X + ov), (310, 0))]
    L['n'] = [S((0, X + ov), (0, 0)),
              S((-ov, X), (420, X, 200), (420, 0))]
    L['o'] = arrondi.ogive(cx=220.0, top=X + 5, bot=-5.0, w=190.0, over=ov)
    L['p'] = [S((0, X + ov), (0, D - ov)), S((-150, D), (150, D)),
              S((-ov, X), (420, X, 200), (420, 0, 200), (-ov, 0))]
    L['q'] = [S((420, X + ov), (420, D - ov)), S((270, D), (570, D)),
              S((420 + ov, X), (0, X, 200), (0, 0, 200), (420 + ov, 0))]
    L['r'] = [S((0, X + ov), (0, -ov)), S((-150, 0), (150, 0)),
              S((-ov, X), (380, X)), croix_haut(380 - 30 * f, X)]
    L['s'] = [S((440, X), (30, X, 90), (30, 470, 80), (390, 110, 100), (390, 0, 60), (0, 0)),
              croix_haut(440 - 30 * f, X), croix_bas(30 * f, 0)]
    L['t'] = [S((150, 820), (150, 0, 120), (400, 0)), croix_haut(400 - 30 * f, 0),
              S((-20, X), (380, X))]
    xr = 440; yb = (xr - 300) * T67
    L['u'] = [S((-60, X), (200, X)),
              S((100, X + ov), (100, 0, 110), (300, 0, 120), (xr + ov * C67, yb + ov * S67)),
              S((xr, X + ov), (xr, 0)), S((xr - 80, X), (xr + 140, X))]
    L['v'] = [S((0, X + ov), (0, -ov)), diag(0, 0, w, X),
              S((-120, X), (140, X)), S((w - 90, X), (w + 180, X)),
              S((-130, 0), (190, 0))]
    L['w'] = [S((0, X + ov), (0, -ov)), diag(0, 0, w, X),
              S((w, X + ov), (w, -ov)), diag(w, 0, 2 * w, X),
              S((-80, 0), (2 * w + 80, 0)),
              S((-120, X), (140, X)), S((2 * w - 90, X), (2 * w + 180, X))]
    L['x'] = [diag(0, X, w, 0), diag(0, 0, w, X),
              S((-130, X), (120, X)), S((w - 100, X), (w + 140, X)),
              S((-140, 0), (110, 0)), S((w - 110, 0), (w + 130, 0))]
    L['y'] = [S((-60, X), (200, X)),
              S((100, X + ov), (100, 0, 110), (300, 0, 120), (xr + ov * C67, yb + ov * S67)),
              S((xr, X + ov), (xr, D, 150), (60, D)), croix_bas(60 + 30 * f, D),
              S((xr - 80, X), (xr + 140, X))]
    L['z'] = [S((0, X), (w + 110, X)),
              diag(w + 110, X, 110, 0),
              S((-ov, 0), (w + 130, 0)),
              croix_haut(30 * f, X), croix_bas(w + 130 - 30 * f, 0)]
    return L

def build_ponct(ov):
    """Ponctuation. Les points sont des croix ; guillemets en chevrons croisés à la pointe."""
    f = ov / 70.0
    def croix_haut(x, y):
        return dict(S((x, y + PC() * f), (x, y - 110 * f)), detail=True)
    def point(x, y, s=80):
        return [S((x, y + s), (x, y - s)), S((x - s, y), (x + s, y))]
    def virgule(x, y, s=80):
        return [S((x + 45, y + s), (x - 70, y - 200)), S((x - s, y), (x + s, y))]
    def dague(x, y=H):       # apostrophe droite : petite dague
        return [S((x, y + 100), (x, y - 280)), S((x - 70, y - 60), (x + 70, y - 60))]
    def dague_penchee(x, sens, y=H):
        return [S((x - 60 * sens, y - 300), (x + 60 * sens, y + 40)), S((x - 75, y - 80), (x + 75, y - 80))]
    def chevron(x, sens, y=400, a=220, d=90):   # sens -1 : pointe à gauche
        tip = np.array([x, y], float)
        out = []
        for dy in (a, -a):
            far = tip + np.array([-sens * a, dy])
            u = (tip - far) / np.linalg.norm(tip - far)
            out.append(S(tuple(far), tuple(tip + u * d)))
        return out
    P = {}
    P['.'] = point(0, 80)
    P[','] = virgule(0, 80)
    P[':'] = point(0, 80) + point(0, 500)
    P[';'] = virgule(0, 80) + point(0, 500)
    P['!'] = [S((0, H + ov), (0, 300)), S((-130, H), (130, H))] + point(0, 80)
    P['?'] = [S((0, H), (380, H, 160), (380, 620, 140), (200, 620), (200, 300)), croix_haut(30 * f, H)] + point(200, 80)
    P["'"] = dague(0)
    P['"'] = dague(0) + dague(200)
    P['’'] = dague_penchee(0, 1)
    P['‘'] = dague_penchee(0, -1)
    P['”'] = dague_penchee(0, 1) + dague_penchee(200, 1)
    P['“'] = dague_penchee(0, -1) + dague_penchee(200, -1)
    P['«'] = chevron(0, -1) + chevron(230, -1)
    P['»'] = chevron(0, 1) + chevron(230, 1)
    P['‹'] = chevron(0, -1)
    P['›'] = chevron(0, 1)
    P['-'] = [S((0, 420), (320, 420))]
    P['–'] = [S((0, 420), (520, 420))]
    P['—'] = [S((0, 420), (920, 420))]
    P['('] = [arrondi.ogive(cx=150.0, top=1120.0, bot=-220.0, w=150.0, over=1.0)[0]]
    P[')'] = [arrondi.ogive(cx=0.0, top=1120.0, bot=-220.0, w=150.0, over=1.0)[1]]
    P['['] = [S((0, 1120 + ov), (0, -220 - ov)), S((-ov, 1120), (220, 1120)), S((-ov, -220), (220, -220))]
    P[']'] = [S((220, 1120 + ov), (220, -220 - ov)), S((0, 1120), (220 + ov, 1120)), S((0, -220), (220 + ov, -220))]
    w = 1340 / T67
    u = np.array([C67, S67])
    P['/'] = [S(tuple(np.array([0, -220]) - u * ov), tuple(np.array([w, 1120]) + u * ov))]
    P['\\'] = [S(tuple(np.array([w, -220]) + np.array([C67, -S67]) * ov), tuple(np.array([0, 1120]) - np.array([C67, -S67]) * ov))]
    P['|'] = [S((0, 1120 + ov), (0, -220 - ov))]
    P['&'] = [S((0, H + ov), (0, -ov)), S((-ov, H), (300, H)), S((-ov, 0), (300, 0)),
              S((-ov, 520), (640, 520)),
              S((480, 760), (480, 0, 120), (700, 0)), croix_haut(700 - 30 * f, 0)]
    P['@'] = [S((460, 710), (460, 250), (640, 250, 120), (640, 900, 250), (0, 900, 250), (0, -100, 250), (600, -100)),
              S((520, 650), (180, 650, 150), (180, 250, 150), (520, 250))]
    P['#'] = [S((150, 800 + ov), (150, -ov)), S((400, 800 + ov), (400, -ov)),
              S((-ov, 250), (550 + ov, 250)), S((-ov, 550), (550 + ov, 550))]
    c = np.array([0.0, 780.0]); r = 170
    P['*'] = [S(tuple(c - r * np.array([math.cos(t), math.sin(t)])), tuple(c + r * np.array([math.cos(t), math.sin(t)])))
              for t in (0, math.pi / 4, math.pi / 2, 3 * math.pi / 4)]
    P['+'] = [S((0, 420), (440, 420)), S((220, 200), (220, 640))]
    P['='] = [S((0, 320), (440, 320)), S((0, 520), (440, 520))]
    P['%'] = [S(tuple(np.array([60, 0]) - u * 60), tuple(np.array([60 + 900 / T67, 900]) + u * 60))] + \
             arrondi.ogive(cx=60.0, top=900.0, bot=560.0, w=90.0, over=60.0) + \
             arrondi.ogive(cx=60 + 900 / T67, top=340.0, bot=0.0, w=90.0, over=60.0)
    P['_'] = [S((0, -220), (600, -220))]
    P['…'] = point(0, 80) + point(230, 80) + point(460, 80)
    P['·'] = point(0, 420)
    P[' '] = [dict(p=[np.array([0.0, -9000.0]), np.array([800.0, -9000.0])], caps=["tip", "tip"])]   # espace
    return P

def arobase(ov, a_min):
    """@ : fenêtre de cathédrale (côtés droits, sommet en ogive, posée sur une barre), le a de Fûstard dedans."""
    def arc(c, r, t0, t1, n=80):
        return [np.array([c[0] + r * math.cos(t), c[1] + r * math.sin(t)]) for t in np.linspace(t0, t1, n)]
    cx, top, bot, w = 350.0, 950.0, -150.0, 330.0
    cy = (top + bot) / 2; h = (top - bot) / 2; a = (h * h - w * w) / (2 * w); rho = a + w
    phi = math.atan2(h, a); d = ov / rho
    cL = (cx + a, cy); cR = (cx - a, cy)
    xg, xd, yl = cx - w, cx + w, 230.0
    gauche = dict(p=path(((xg, bot - ov), (xg, cy))) + arc(cL, rho, math.pi, math.pi - phi - d)[1:], caps=['tip', 'tip'])
    droite = dict(p=path(((500, yl), (xd, yl), (xd, cy))) + arc(cR, rho, 0.0, phi + d)[1:], caps=['T', 'tip'])
    pied = S((xg - ov, bot), (xd + 40, bot))
    sc = 0.75; dx = 500 - 360 * sc
    dedans = [dict(p=[np.array([x * sc + dx, y * sc + yl]) for x, y in st['p']], caps=st['caps']) for st in a_min]
    return [gauche, droite, pied] + dedans

OV_CHOISI = 210.0   # niveau 2 (croisements x3), choisi
OV_MIN = OV_CHOISI * XH / 1000.0   # même exagération, en proportion des minuscules
G = build(OV_CHOISI)
G.update(build_lc(OV_MIN))
G.update(build_ponct(OV_MIN))
G['@'] = arobase(OV_MIN, G['a'])
GP = {ch: [s['p'] for s in v] for ch, v in G.items()}

def render(word, out, k=0.3, ss=3, gap=284, G=G):
    G0, cr0, gap0 = essai.G, essai.cr, essai.GAP
    GP = {ch: [st['p'] for st in v] for ch, v in G.items()}
    essai.G, essai.cr = GP, lambda s, n=20: droit.dens(s)
    if gap: essai.GAP = gap
    try:
        xs, end = essai.layout(word)
    finally:
        essai.G, essai.cr, essai.GAP = G0, cr0, gap0
    K = k * ss
    top, bot = 1380, -640
    W = int((end + 600) * K); Hh = int((top - bot) * K)
    img = Image.new('L', (W, Hh), 0)
    d = ImageDraw.Draw(img)
    for ch, ox in zip(word, xs):
        for st in G[ch]:
            for q in droit.outline_quads(st['p'], *st['caps']):
                d.polygon([((x + ox + 300) * K, (top - y) * K) for x, y in q], fill=238)
    img.resize((W // ss, Hh // ss), Image.LANCZOS).convert('RGB').save(out)

def planche(out, lignes=('ABCDEFGHI', 'JKLMNOPQR', 'STUVWXYZ'), k=0.3, G=G):
    """Planche de l'alphabet, une image par ligne collées les unes sous les autres."""
    imgs = []
    for i, l in enumerate(lignes):
        fn = out + f'.ligne{i}.png'
        render(l, fn, k=k, G=G)
        imgs.append(Image.open(fn))
    W = max(im.width for im in imgs)
    sheet = Image.new('RGB', (W, sum(im.height for im in imgs)), (0, 0, 0))
    y = 0
    for im in imgs:
        sheet.paste(im, (0, y)); y += im.height
    sheet.save(out)
    import os
    for i in range(len(lignes)):
        os.remove(out + f'.ligne{i}.png')

GMAJ = dict(G); GMAJ.update(build_chiffres_maj(OV_CHOISI))   # chiffres majuscules

def planche_chiffres(out, k=0.3):
    """Chiffres minuscules, chiffres majuscules, puis LAFLEUR2026 en majuscules."""
    from PIL import ImageFont
    import os
    try:
        F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 34)
    except OSError:
        F = ImageFont.load_default()
    rows = []
    for i, (word, g, lab) in enumerate([('0123456789', G, 'minuscules'), ('0123456789', GMAJ, 'MAJUSCULES'),
                                        ('LAFLEUR2026', GMAJ, '')]):
        fn = out + f'.ligne{i}.png'
        render(word, fn, G=g, k=k)
        im = Image.open(fn)
        if lab:
            ImageDraw.Draw(im).text((25, 20), lab, font=F, fill=(255, 210, 60))
        rows.append(im); os.remove(fn)
    W = max(r.width for r in rows)
    sheet = Image.new('RGB', (W, sum(r.height for r in rows)), (0, 0, 0))
    y = 0
    for r in rows:
        sheet.paste(r, (0, y)); y += r.height
    sheet.save(out)

def planche_ponct(out, k=0.3):
    """Ponctuation, puis deux phrases d'essai."""
    import os
    lignes = [('.,:;!?\'"\u2018\u2019\u201c\u201d', G),
              ('\u00ab\u00bb\u2039\u203a-\u2013\u2014()[]/\\|', G),
              ('&@#*+=%_\u2026\u00b7', G),
              ('\u00abLAFLEUR STUDIO\u00bb : 132 !', GMAJ),
              ('(la fleur) & @studio #132 ?', G)]
    rows = []
    for i, (t, g) in enumerate(lignes):
        fn = out + f'.ligne{i}.png'
        render(t, fn, G=g, k=k); rows.append(Image.open(fn)); os.remove(fn)
    W = max(r.width for r in rows)
    sheet = Image.new('RGB', (W, sum(r.height for r in rows)), (0, 0, 0))
    y = 0
    for r in rows:
        sheet.paste(r, (0, y)); y += r.height
    sheet.save(out)

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'LAFLEURSTUDIO'
    out = sys.argv[2] if len(sys.argv) > 2 else None
    if cmd == 'alphabet':
        planche(out or 'alphabet.png')
    elif cmd == 'minuscules':
        planche(out or 'minuscules.png', lignes=('abcdefghi', 'jklmnopqr', 'stuvwxyz', 'lafleurstudio'))
    elif cmd == 'chiffres':
        planche_chiffres(out or 'chiffres.png')
    elif cmd == 'ponctuation':
        planche_ponct(out or 'ponctuation.png')
    else:
        render(cmd, out or 'fustard-132.png')
