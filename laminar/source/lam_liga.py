# LAMINAR : ligatures (liga toujours actives, dlig sur demande) ; mêmes règles en capitales et petites capitales
from lam_core import *

LIGA = ['TT', 'LL', 'TH', 'LT']
DLIG = ['OO', 'CO', 'CA', 'LA', 'LE', 'AV', 'VA', 'AW', 'MM', 'NN', 'AR', 'ER']

def ligs(c, G):
    H, S, h, CT, W = c.H, c.S, c.h, c.CT, c.W; L = {}
    ink = lambda n: G[n].ink
    wd = lambda n: G[n].x1
    def gl(p, sides): return Gl(p, 0, bounds(p)[2], sides)
    Tw, Lw, Ew, Aw = wd('T'), wd('L'), wd('E'), wd('A')
    # TT : une seule barre
    L['TT'] = gl(U(ink('T'), mv(ink('T'), Tw)), 'OO')
    # LL : le second fût se pose au bout du pied
    L['LL'] = gl(U(ink('L'), mv(ink('L'), Lw - S)), 'SO')
    # TH : la barre du T rejoint le fût du H
    L['TH'] = gl(U(ink('T'), mv(ink('H'), Tw - S)), 'OS')
    # LT : la barre du T part du fût du L, le pied s'arrête avant le fût du T
    sh = Lw + round(0.18 * CT) - (Tw - S) / 2
    L['LT'] = gl(U(ink('L'), mv(ink('T'), sh), rect(0, H - h, sh + 1, H)), 'SO')
    # OO CO : anneaux enlacés
    O = ink('O'); R = wd('O') / 2; so = round(1.45 * R)
    L['OO'] = gl(U(O, mv(O, so)), 'OO')
    L['CO'] = gl(U(ink('C'), mv(O, so)), 'OO')
    # CA : le A entre dans la bouche du C
    L['CA'] = gl(U(ink('C'), mv(ink('A'), wd('C') - round(0.30 * Aw))), 'OD')
    # LA LE : le pied du L passe sous la lettre suivante
    xa = S + round(0.10 * CT)
    L['LA'] = gl(U(ink('L'), mv(ink('A'), xa), rect(0, 0, xa + Aw, h)), 'SO')
    xe = S + round(0.40 * CT)
    L['LE'] = gl(U(ink('L'), mv(ink('E'), xe), rect(0, 0, xe + Ew, h)), 'SO')
    # AV VA AW : la même oblique sert aux deux lettres
    wR = round(0.93 * S)
    for _ in range(8): wR = hw(round(0.93 * S), (Aw - wR) / 2, H)
    xap = (Aw - wR) / 2; wL = hw(h, xap, H)
    V = ink('V')
    L['AV'] = gl(U(ink('A'), mv(V, xap)), 'DD')
    L['VA'] = gl(U(V, mv(ink('A'), Aw - xap - wL)), 'DD')
    # W dont le premier V a la largeur du A (il partage l'oblique), le second reste étroit
    Vn_w = round(0.80 * Aw); wRn = round(0.93 * S)
    for _ in range(8): wRn = hw(round(0.93 * S), (Vn_w - wRn) / 2, H)
    xn = (Vn_w - wRn) / 2; wLn = hw(h, xn, H)
    vn = rot(U(diag(Vn_w - wRn, xn, wRn, 0, H), diag(0, xn, wLn, 0, H)), 180, Vn_w / 2, H / 2)
    L['AW'] = gl(U(ink('A'), mv(U(V, mv(vn, Aw - wL)), xap)), 'DD')
    # MM NN : un fût partagé
    Mw, Nw = wd('M'), wd('N')
    L['MM'] = gl(U(ink('M'), mv(ink('M'), Mw - S)), 'SS')
    L['NN'] = gl(U(ink('N'), mv(ink('N'), Nw - h)), 'SS')
    # AR : la barre du A file jusqu'au fût du R
    ya = round(0.60 * H) if not c.sc else round(0.58 * H)
    xr = Aw - S
    hullA = poly([(0, 0), (Aw, 0), (xap + wR, H), (xap, H)])
    L['AR'] = gl(U(ink('A'), mv(ink('R'), xr), I(rect(0, ya - h / 2, xr + 1, ya + h / 2), U(hullA, rect(xap, 0, xr + 1, H)))), 'DD')
    # ER : les barres du E filent jusqu'au fût du R
    xr2 = Ew + round(0.16 * CT)
    L['ER'] = gl(U(ink('E'), mv(ink('R'), xr2), rect(0, H - h, xr2 + 1, H), rect(0, c.BAR - h / 2, xr2 + 1, c.BAR + h / 2), rect(0, 0, xr2 + 1, h)), 'SD')
    return L
