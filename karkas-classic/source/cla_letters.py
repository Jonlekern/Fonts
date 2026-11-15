# KARKAS CLASSIC : les lettres du manuscrit. Fûts épais à bouts en coin, traits fins, petites boucles pointues, nœuds.
# Même interface que kar_letters.letter : une lettre se dessine entre y0 et y1.
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'karkas', 'source'))
from kar_core import *
from kar_letters import Gl

LM = set('BDEFHIKLMNPRU') | set('БВГЕКМНПРЦШЩЫЬЮИ')     # fût entier à gauche
RM = set('AHMNUJY') | set('АЛИМНПШЫЯЧУ')               # fût entier à droite
TWIN = {'А': 'A', 'В': 'B', 'Е': 'E', 'К': 'K', 'М': 'M', 'Н': 'H', 'О': 'O', 'Р': 'P', 'С': 'C', 'Т': 'T', 'Х': 'X', 'У': 'Y'}

def cwt(nom, S, h, CT, wclass):
    w = Wt(nom, S, h, CT, wclass); w.G = round(0.62 * CT + 0.20 * S); w.SB = w.G // 2; w.g = max(round(0.70 * w.G) + round(0.40 * S), h + 10); return w      # le blanc dans une ligature compte les bouts évasés des fûts
WEIGHTS = {'Skoropis': cwt('Skoropis', 22, 8, 50, 300), 'Poluustav': cwt('Poluustav', 38, 11, 40, 500), 'Ustav': cwt('Ustav', 54, 15, 42, 800)}

def lens(cx, y0, y1, a):
    """amande pointue : deux arcs qui se rejoignent en pointe en haut et en bas ; demi-largeur a"""
    H = y1 - y0; c = a / 0.75; p = P(); pen = p.getPen(); pen.moveTo((cx, y0))
    pen.curveTo((cx + c, y0 + 0.24 * H), (cx + c, y1 - 0.24 * H), (cx, y1))
    pen.curveTo((cx - c, y1 - 0.24 * H), (cx - c, y0 + 0.24 * H), (cx, y0)); pen.closePath(); return p
def amande(cx, y0, y1, a, ts, tv):
    """anneau en amande : épais sur les flancs (ts), fin aux pointes"""
    return D(lens(cx, y0, y1, a), lens(cx, y0 + tv, y1 - tv, a - ts))
K = 0.5522847498
def ell(cx, cy, a, b):
    p = P(); pen = p.getPen(); pen.moveTo((cx + a, cy))
    pen.curveTo((cx + a, cy + K * b), (cx + K * a, cy + b), (cx, cy + b)); pen.curveTo((cx - K * a, cy + b), (cx - a, cy + K * b), (cx - a, cy))
    pen.curveTo((cx - a, cy - K * b), (cx - K * a, cy - b), (cx, cy - b)); pen.curveTo((cx + K * a, cy - b), (cx + a, cy - K * b), (cx + a, cy)); pen.closePath(); return p

def fut(x, y0, y1, S, top=True, bot=True):
    """fût à bouts en coin : il s'évase un peu en haut et en bas, comme un trait de plume large"""
    e = round(0.20 * S); f = min(round(1.3 * S), (y1 - y0) / 3)
    pts = [(x - (e if bot else 0), y0), (x + S + (e if bot else 0), y0)] + ([(x + S, y0 + f)] if bot else [])
    pts += ([(x + S, y1 - f)] if top else []) + [(x + S + (e if top else 0), y1), (x - (e if top else 0), y1)] + ([(x, y1 - f)] if top else []) + ([(x, y0 + f)] if bot else [])
    return poly(pts)
def noeud(x, yc, S):
    """le nœud : un losange au milieu d'un long fût"""
    return losange(x + S / 2, yc, S / 2 + round(0.42 * S), 1.5 * (S / 2 + round(0.42 * S)))
def coin(x, y, s, sens):
    """petit coin au bout d'un trait fin (sens : 1 vers le haut, -1 vers le bas)"""
    return poly([(x - s * 0.5, y), (x + s * 0.5, y), (x, y + sens * 1.9 * s)])

def letter(ch, w, y0=0, y1=CAP, nest=False, fw=None):
    if ch in TWIN:
        g = letter(TWIN[ch], w, y0, y1, nest, fw); return Gl(g.ink, g.w, ch in LM, ch in RM)
    S, h, CT, W = w.S, w.B, w.CT, w.W; H = y1 - y0
    F = lambda x, a=None, b=None, **k: fut(x, y0 if a is None else a, y1 if b is None else b, S, **k)
    hbar = lambda xa, xb, y: rect(xa, y, xb, y + h)                              # trait fin horizontal (bord bas en y)
    hair = lambda xa, ya, xb, yb, wa=0, wb=0: link(xa, ya, xb, yb, h * 1.15, wa, wb)
    cs = round(0.9 * h) + 6                                                      # taille des petits coins
    ts = round(0.86 * S); tv = round(2.2 * h)                                    # flancs et pointes des boucles
    box = rect(-4000, y0, 4000, y1); ww = W; arm = CT + round(0.45 * S)
    big = H > 0.7 * CAP
    def boucle(ya, yb, wb=None):
        """petite boucle pointue à droite du fût"""
        a = (CT + ts) if wb is None else wb
        return I(amande(S - 1, ya, yb, a, ts, min(tv, (yb - ya) / 5)), rect(S - 2, ya, S + a + 5, yb))
    if ch == 'A':
        ww = S + round(1.25 * CT); x = ww - S
        p = U(F(x), hair(0, y0, x + S / 2, y1 - 0.02 * H, 0, S), hbar(0.30 * (ww - S), x + 1, y0 + 0.30 * H))
    elif ch == 'B':
        ww = S + CT + ts; p = U(F(0), boucle(y0 + 0.60 * H, y1), boucle(y0, y0 + 0.64 * H))
    elif ch == 'C':
        ww = CT + 2 * ts; r = amande(ww / 2, y0, y1, ww / 2, ts, tv)
        p = D(r, rect(ww / 2 + 0.12 * CT, y0 + 0.16 * H, ww + 5, y1 - 0.16 * H))
    elif ch == 'D':
        ww = S + CT + ts; p = U(F(0), boucle(y0, y1))
    elif ch in 'EF':
        ww = S + arm
        p = U(F(0), hbar(0, ww, y1 - h), coin(ww - cs * 0.5, y1 - h + 1, cs, -1), hbar(0, S + 0.62 * arm, y0 + 0.58 * H), coin(S + 0.62 * arm - cs * 0.5, y0 + 0.58 * H + h / 2, cs * 0.8, 1))
        if ch == 'E': p = U(p, hbar(0, ww, y0), coin(ww - cs * 0.5, y0 + h - 1, cs, 1))
    elif ch == 'G':
        ww = CT + 2 * ts; r = amande(ww / 2, y0, y1, ww / 2, ts, tv); yg = y0 + 0.40 * H
        p = U(D(r, rect(ww / 2 + 0.12 * CT, y0 + 0.16 * H, ww + 5, y1 - 0.16 * H)), rect(ww - round(0.8 * S), y0 + 0.16 * H - 4, ww, yg), hbar(ww / 2 - 0.1 * CT, ww, yg - h))
    elif ch == 'H':
        p = U(F(0), F(W - S), hbar(S - 1, W - S + 1, y0 + 0.56 * H))
    elif ch == 'I':
        ww = S; p = F(0)
        if big: p = U(p, noeud(0, y0 + 0.5 * H, S))
    elif ch == 'J':
        ww = S + round(0.8 * CT); p = U(F(ww - S, bot=False), hbar(0, ww, y0), coin(cs * 0.5, y0 + h - 1, cs, 1))
    elif ch == 'K':
        ww = S + round(1.35 * CT) + round(0.5 * S); ym = y0 + 0.56 * H; dk = min(0.26 * H, 3.2 * CT)
        p = U(F(0), hair(S / 2, ym, ww - h * 0.6, ym + dk, S, 0), diag_(S - 2, ym + h, ww - 0.7 * S, y0, 0.7 * S))
    elif ch == 'L':
        ww = S + arm; p = U(F(0), hbar(0, ww, y0), coin(ww - cs * 0.5, y0 + h - 1, cs, 1))
        if big: p = U(p, noeud(0, y0 + 0.55 * H, S))
    elif ch == 'M':
        ww = 2 * S + round(1.7 * CT); xm = ww / 2; yv = y0 + 0.50 * H
        p = U(F(0), F(ww - S), hair(S / 2, y1 - 0.04 * H, xm, yv, S, 0), hair(xm, yv, ww - S / 2, y1 - 0.04 * H, 0, S))
    elif ch == 'N':
        p = U(F(0), F(W - S), hair(S / 2, y0 + 0.74 * H, W - S / 2, y0 + 0.26 * H, S, S))
    elif ch in 'OQ':
        ww = CT + 2 * ts; p = amande(ww / 2, y0, y1, ww / 2, ts, tv)
        if ch == 'Q': p = U(p, link(ww / 2, y0 + 0.12 * H, ww + 0.2 * CT, y0 - (0 if nest else 0.06 * CAP), h * 1.6, 0, 0))
    elif ch == 'P':
        ww = S + CT + ts; p = U(F(0), boucle(y0 + 0.56 * H, y1))
        if big: p = U(p, noeud(0, y0 + 0.30 * H, S))
    elif ch == 'R':
        ww = S + CT + ts; yj = y0 + 0.58 * H
        p = U(F(0), boucle(yj, y1), diag_(S - 2, yj + 0.04 * H, ww - 0.7 * S, y0, 0.7 * S))
    elif ch == 'S':
        ym = y0 + 0.54 * H
        p = U(hbar(0, W, y1 - h), coin(W - cs * 0.5, y1 - h + 1, cs, -1), fut(0, ym, y1, S, bot=False), hbar(0, W, ym),
              fut(W - S, y0, ym + h, S, top=False), hbar(0, W, y0), coin(cs * 0.5, y0 + h - 1, cs, 1))
    elif ch == 'T':
        ww = S + 2 * round(0.85 * CT) if not fw else fw; xm = (ww - S) / 2
        p = U(F(xm, top=False), hbar(0, ww, y1 - h), coin(cs * 0.5, y1 - h + 1, cs, -1), coin(ww - cs * 0.5, y1 - h + 1, cs, -1))
        if big: p = U(p, noeud(xm, y0 + 0.5 * H, S))
    elif ch == 'U':
        p = U(F(0, bot=False), F(W - S, bot=False), hbar(0, W, y0))
    elif ch == 'V':
        ww = S + round(1.5 * CT); xm = ww * 0.56
        p = U(diag_(xm - S / 2, y0, 0, y1, S), hair(xm, y0, ww - h * 0.6, y1, 0, 0))
    elif ch == 'W':
        ww = 2 * S + round(1.7 * CT); xm = ww / 2; yv = y0 + 0.50 * H
        p = U(F(0), F(ww - S), hair(S / 2, y0 + 0.04 * H, xm, yv, S, 0), hair(xm, yv, ww - S / 2, y0 + 0.04 * H, 0, S))
    elif ch == 'X':
        ww = S + round(1.5 * CT)
        p = U(diag_(ww - S, y0, 0, y1, S), hair(h * 0.6, y0, ww - h * 0.6, y1, 0, 0))
    elif ch == 'Y':
        ww = S + round(1.25 * CT); x = ww - S
        p = U(F(x), hair(h * 0.6, y1, x + S / 2, y0 + 0.40 * H, 0, S))
    elif ch == 'Z':
        ww = S + round(1.25 * CT)
        p = U(hbar(0, ww, y1 - h), hbar(0, ww, y0), diag_(0, y0, ww - S, y1, S), coin(cs * 0.5, y1 - h + 1, cs, -1), coin(ww - cs * 0.5, y0 + h - 1, cs, 1))
    elif ch == 'Б':
        ww = S + CT + ts; p = U(F(0), hbar(0, ww - 0.2 * ts, y1 - h), coin(ww - 0.2 * ts - cs * 0.5, y1 - h + 1, cs, -1), boucle(y0, y0 + 0.56 * H))
    elif ch == 'Г':
        ww = S + arm; p = U(F(0), hbar(0, ww, y1 - h), coin(ww - cs * 0.5, y1 - h + 1, cs, -1))
        if big: p = U(p, noeud(0, y0 + 0.45 * H, S))
    elif ch in 'ДЛ':
        ww = S + round(1.25 * CT); x = ww - S
        p = U(F(x), hair(0, y0, x + S / 2, y1 - 0.02 * H, 0, S))
        if ch == 'Д':
            e = round(0.45 * S); ft = 0 if nest else 0.07 * CAP
            t = round(1.6 * h); p = U(mv(I(p, box), e), rect(0, y0, ww + 2 * e, y0 + h), rect(0, y0 - ft, t, y0 + h), rect(ww + 2 * e - t, y0 - ft, ww + 2 * e, y0 + h)); ww += 2 * e      # deux petits pieds sous la ligne
    elif ch == 'Ж':
        aw = round(1.15 * CT); ww = S + 2 * aw; c = aw; ym = y0 + 0.52 * H; dk = min(0.30 * H, 3.2 * CT)
        p = U(F(c), hair(h * 0.6, ym + dk, c + S / 2, ym, 0, S), hair(h * 0.6, ym - dk, c + S / 2, ym, 0, S),
              hair(c + S / 2, ym, ww - h * 0.6, ym + dk, S, 0), hair(c + S / 2, ym, ww - h * 0.6, ym - dk, S, 0))
    elif ch == 'З':
        a = CT + ts; ww = a + round(0.3 * ts); x0 = ww - a
        b1 = I(amande(x0, y0 + 0.56 * H, y1, a, ts, min(tv, 0.44 * H / 5)), rect(x0 - 2, y0, ww + 5, y1))
        b2 = I(amande(x0, y0, y0 + 0.62 * H, a, ts, min(tv, 0.62 * H / 5)), rect(x0 - 2, y0, ww + 5, y1))
        p = U(b1, b2, hbar(0, x0 + 2, y1 - h), hbar(0, x0 + 2, y0))
    elif ch in 'ИЙ':
        p = U(F(0), F(W - S), hair(S / 2, y0 + 0.26 * H, W - S / 2, y0 + 0.74 * H, S, S))
    elif ch == 'П':
        p = U(F(0, top=False), F(W - S, top=False), hbar(0, W, y1 - h))
    elif ch == 'Ф':
        ww = CT + 2 * ts + round(0.3 * S); c = (ww - S) / 2
        p = U(F(c), amande(ww / 2, y0 + 0.34 * H, y0 + 0.90 * H, ww / 2, ts * 0.8, tv * 0.7))
    elif ch in 'ЦЩШ':
        n = 2 if ch == 'Ц' else 3; st = W - S; wb = (n - 1) * st + S; e = round(0.5 * CT) if ch != 'Ш' else 0; ft = 0 if nest else 0.07 * CAP
        p = U(*[F(i * st, bot=False) for i in range(n)], hbar(0, wb + e, y0)); ww = wb + e
        if e: p = U(p, rect(wb + e - round(1.6 * h), y0 - ft, wb + e, y0 + h))
    elif ch == 'Ч':
        yq = y0 + 0.46 * H
        p = U(fut(0, yq, y1, S, bot=False), hbar(0, W - S + 1, yq), F(W - S))
    elif ch in 'ЪЬЫ':
        e = round(0.7 * CT) if ch == 'Ъ' else 0; ww = e + S + CT + ts
        p = U(mv(U(F(0), boucle(y0, y0 + 0.52 * H)), e))
        if ch == 'Ъ': p = U(p, hbar(0, e + 1, y1 - h), coin(cs * 0.5, y1 - h + 1, cs, -1))
        if ch == 'Ы': gp = round(0.8 * w.G); p = U(p, F(ww + gp)); ww += gp + S
    elif ch == 'Э':
        ww = CT + 2 * ts; r = amande(ww / 2, y0, y1, ww / 2, ts, tv)
        p = U(D(r, rect(-5, y0 + 0.16 * H, ww / 2 - 0.12 * CT, y1 - 0.16 * H)), hbar(ww / 2 - 0.3 * CT, ww - ts / 2, y0 + 0.5 * H))
    elif ch == 'Ю':
        e = S + round(0.6 * CT); wo = CT + 2 * ts; ww = e + wo
        p = U(F(0), hbar(S - 1, e + ts / 2, y0 + 0.5 * H), mv(amande(wo / 2, y0, y1, wo / 2, ts, tv), e))
    elif ch == 'Я':
        g = letter('R', w, y0, y1, nest); ww = g.w; p = mirror(g.ink, ww / 2)
    else:
        raise KeyError(ch)
    if ch not in 'QДЦЩ' or nest: p = I(p, box)
    return Gl(p, ww, ch in LM, ch in RM)

def diag_(xb, y0, xt, y1, t):
    """oblique épaisse : largeur horizontale t, du bas (xb) au haut (xt)"""
    return poly([(xb, y0), (xb + t, y0), (xt + t, y1), (xt, y1)])
