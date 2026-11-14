# KARKAS : les lettres. Chaque lettre se dessine entre y0 et y1 : une lettre logée est la même, moins haute, même trait.
from kar_core import *

class Gl:
    """encre, largeur, fût entier à gauche (lm) et à droite (rm)"""
    def __init__(s, ink, w, lm=False, rm=False):
        s.ink, s.w, s.lm, s.rm = ink, w, lm, rm

LM = set('ABDEFHKLMNOPQRUWCG')         # fût à gauche : peut recevoir le fût de la lettre d'avant (pas le V : sa pointe laisserait une fente)
RM = set('AHMNUOJWQ')                 # fût à droite : peut le donner (pas le D : le fût voisin boucherait ses coins coupés)

# le cyrillique (bonus) : lettres jumelles du latin, et celles qu'il faut dessiner
TWIN = {'А': 'A', 'В': 'B', 'Е': 'E', 'К': 'K', 'М': 'M', 'Н': 'H', 'О': 'O', 'Р': 'P', 'С': 'C', 'Т': 'T', 'Х': 'X', 'У': 'Y'}
RU = 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
LM |= set('БВГЕКМНОПРСИЛАШЩЫЬЮ')
RM |= set('АЛИМНОПШЫЯЧ')

def wedge(ch, w, y0, y1, side):
    """A, Л : le coin entre la pente et le fût voisin, à remplir en gras quand le fût est partagé (sinon il reste une fente)"""
    if ch not in 'AАЛ': return None
    S, CT, W = w.S, w.CT, w.W; h = y1 - y0
    da = min(1.5 * CT, 0.24 * h); ya = y1 - da; xm = W / 2; yt = y1 - 0.25 * S
    s = (ya - yt) / ((W - S / 2) - xm); tv = S * (1 + s * s) ** 0.5
    yu = lambda x: yt + (x - xm) * s + tv / 2
    x1 = xm + (y1 - yu(xm)) / s
    if W - S - x1 >= 20: return None       # graisses fines : le coin est assez large, on le laisse ouvert (le remplir ferait une tache noire)
    p = poly([(x1, y1), (W, yu(W)), (W, y1)])
    return p if side == 'R' else mirror(p, W / 2)

def letter(ch, w, y0=0, y1=CAP, nest=False, fw=None):
    """fw : largeur imposée (KARKAS Display, mot-bloc : toutes les lettres remplissent la même colonne)"""
    if ch in TWIN:
        g = letter(TWIN[ch], w, y0, y1, nest, fw); return Gl(g.ink, g.w, ch in LM, ch in RM)
    S, B, CT, W = w.S, w.B, w.CT, w.W
    if fw: W = fw; CT = fw - 2 * S
    h = y1 - y0
    yb = y0 + round((0.68 if h > 0.7 * CAP else 0.58) * h)   # taille haute ; un peu plus basse pour une petite lettre (logée, empilée)
    bar = lambda x0, x1, yc: rect(x0, yc - B / 2, x1, yc + B / 2)
    top = lambda x0, x1: rect(x0, y1 - B, x1, y1)
    bot = lambda x0, x1: rect(x0, y0, x1, y0 + B)
    mast = lambda x, a=None, b=None: rect(x, y0 if a is None else a, x + S, y1 if b is None else b)
    box = rect(-4000, y0, 4000, y1)
    dk = min(1.25 * CT, 0.20 * h)                  # demi-zone des obliques
    tk = max(min(1.10 * CT, 0.15 * h), B + 0.55 * CT)   # petits retours (C G S J) : toujours plus longs que la barre
    tw = min(S, round(0.55 * CT))                  # largeur des retours : ils ne doivent pas boucher la lettre
    We = S + max(round(0.86 * CT), tw + 34)        # lettres ouvertes à droite
    if fw: We = fw
    ww = W
    if ch == 'A':
        da = min(1.5 * CT, 0.24 * h); ya = y1 - da
        p = U(mast(0, y0, ya), mast(W - S, y0, ya), chevron(0, W, ya, y1, S, S), bar(0, W, y0 + 0.42 * h))
    elif ch == 'B':
        ins = round(0.26 * CT)
        p = U(mast(0), top(0, W - ins), bar(0, W, yb), bot(0, W), mast(W - S, y0, yb + B / 2), mast(W - S - ins, yb - B / 2, y1))
    elif ch == 'C':
        ww = We; p = U(mast(0), top(0, ww), bot(0, ww))
        if not nest: p = U(p, rect(ww - tw, y1 - tk, ww, y1), rect(ww - tw, y0, ww, y0 + tk))
    elif ch == 'D':
        c = max(0.55 * CT, 0.9 * S); k = S * (2 ** 0.5)
        out = poly([(0, y0), (W - c, y0), (W, y0 + c), (W, y1 - c), (W - c, y1), (0, y1)])
        xi = W - c - k + B; yi = c + k - S
        if xi < W - S - 1: inn = poly([(S, y0 + B), (xi, y0 + B), (W - S, y0 + yi), (W - S, y1 - yi), (xi, y1 - B), (S, y1 - B)])
        else: inn = rect(S, y0 + B, W - S, y1 - B)
        p = D(out, inn)
    elif ch == 'E':
        ww = We; p = U(mast(0), top(0, ww), bar(0, ww - round(0.22 * CT), yb), bot(0, ww))
    elif ch == 'F':
        ww = We; p = U(mast(0), top(0, ww), bar(0, ww - round(0.22 * CT), yb))
    elif ch == 'G':
        yg = y0 + round(0.44 * h)
        p = U(mast(0), top(0, W), bot(0, W), mast(W - S, y0, yg), rect(W - S - round(0.38 * CT), yg - B, W, yg), rect(W - S, y1 - tk, W, y1))
    elif ch == 'H':
        p = U(mast(0), mast(W - S), bar(0, W, yb))
    elif ch == 'I':
        ww = S; p = mast(0)
        if fw: ww = fw; p = U(mast((fw - S) / 2), top(0, fw), bot(0, fw))       # en colonne : un I à empattements, pour remplir
    elif ch == 'J':
        ww = fw or (S + tw + max(round(0.30 * CT), 24)); p = U(mast(ww - S), bot(0, ww), rect(0, y0, tw, y0 + max(tk, 0.22 * h)))
    elif ch == 'K':
        p = U(mast(0), mast(W - S, yb + dk, y1), mast(W - S, y0, yb - dk),
              link(S / 2, yb, W - S / 2, yb + dk, S, S, S), link(S / 2, yb, W - S / 2, yb - dk, S, S, S))
    elif ch == 'L':
        ww = fw or (S + round(0.74 * CT)); p = U(mast(0), bot(0, ww))
    elif ch == 'M':
        ww = fw or (2 * S + round(1.45 * CT)); dm = min(1.9 * CT, 0.30 * h)
        p = U(mast(0), mast(ww - S), chevron(0, ww, y1, y1 - dm, S, S))
    elif ch == 'N':
        zt, zb = y0 + 0.74 * h, y0 + 0.30 * h
        p = U(mast(0), mast(W - S), link(S / 2, zt, W - S / 2, zb, S, S, S))
    elif ch == 'O':
        p = D(rect(0, y0, W, y1), rect(S, y0 + B, W - S, y1 - B))
    elif ch == 'P':
        p = U(mast(0), top(0, W), bar(0, W, yb), mast(W - S, yb - B / 2, y1))
    elif ch == 'Q':
        p = D(rect(0, y0, W, y1), rect(S, y0 + B, W - S, y1 - B)); tq = min(S, round(0.45 * CT)); xq = W - S - tq
        # la queue : un trait sous la ligne, collé au fût droit (jamais de fente dans la lettre) ; logée, un coin plein à l'intérieur
        p = U(p, rect(xq, y0, W - S, y0 + B + 0.10 * h) if nest else rect(xq, y0 - 0.075 * CAP, xq + S, y0 + B))
    elif ch == 'R':
        p = U(mast(0), top(0, W), bar(0, W, yb), mast(W - S, yb - B / 2, y1),
              link(S / 2, yb, W - S / 2, yb - dk, S, S, S), mast(W - S, y0, yb - dk))
    elif ch == 'S':
        t1 = min(tk, B + 0.45 * (y1 - B - yb - B / 2)); t0 = min(tk, B + 0.45 * (yb - B / 2 - y0 - B))     # les retours ne ferment jamais la lettre
        p = U(top(0, W), mast(0, yb - B / 2, y1), bar(0, W, yb), mast(W - S, y0, yb + B / 2), bot(0, W),
              rect(W - S, y1 - t1, W, y1), rect(0, y0, S, y0 + t0))
    elif ch == 'T':
        p = U(top(0, W), mast((W - S) / 2))
    elif ch == 'U':
        p = U(mast(0), mast(W - S), bot(0, W))
    elif ch == 'V':
        dv = min(1.6 * CT, 0.26 * h); yv = y0 + dv
        p = U(mast(0, yv, y1), mast(W - S, yv, y1), chevron(0, W, yv, y0, S, S))
    elif ch == 'W':
        ww = fw or (2 * S + round(1.45 * CT)); dm = min(1.9 * CT, 0.30 * h)
        p = U(mast(0), mast(ww - S), chevron(0, ww, y0, y0 + dm, S, S))
    elif ch == 'X':
        ym = y0 + 0.5 * h
        p = U(mast(0, ym + dk, y1), mast(W - S, ym + dk, y1), mast(0, y0, ym - dk), mast(W - S, y0, ym - dk),
              link(S / 2, ym + dk, W - S / 2, ym - dk, S, S, S), link(S / 2, ym - dk, W - S / 2, ym + dk, S, S, S))
    elif ch == 'Y':
        dy = min(1.5 * CT, 0.24 * h); yy = y0 + 0.62 * h
        p = U(mast(0, yy, y1), mast(W - S, yy, y1), chevron(0, W, yy, yy - dy, S, S, flat=False), mast((W - S) / 2, y0, yy - dy + 0.3 * S))
        p = I(p, rect(0, y0, W, y1))
    elif ch == 'Z':
        ym = y0 + 0.5 * h
        p = U(top(0, W), bot(0, W), mast(W - S, ym + dk, y1), mast(0, y0, ym - dk), link(S / 2, ym - dk, W - S / 2, ym + dk, S, S, S))
    elif ch == 'Б':
        ym = y0 + round(0.52 * h)
        p = U(mast(0), top(0, We), bar(0, W, ym), mast(W - S, y0, ym + B / 2), bot(0, W))
    elif ch == 'Г':
        ww = We; p = U(mast(0), top(0, ww))
    elif ch in 'ДЛ':
        da = min(1.5 * CT, 0.24 * h); ya = y1 - da
        p = U(mast(0, y0, ya), mast(W - S, y0, ya), chevron(0, W, ya, y1, S, S))
        if ch == 'Д':
            e = round(0.20 * CT); ft = 0 if nest else 0.075 * CAP
            p = U(mv(p, e), rect(0, y0, W + 2 * e, y0 + B), rect(0, y0 - ft, S, y0 + B), rect(W + 2 * e - S, y0 - ft, W + 2 * e, y0 + B)); ww = W + 2 * e
    elif ch == 'Ж':
        ww = 2 * W - S; c = W - S
        p = U(mast(c), mast(0, yb + dk, y1), mast(0, y0, yb - dk), mast(ww - S, yb + dk, y1), mast(ww - S, y0, yb - dk),
              link(S / 2, yb + dk, c + S / 2, yb, S, S, S), link(S / 2, yb - dk, c + S / 2, yb, S, S, S),
              link(c + S / 2, yb, ww - S / 2, yb + dk, S, S, S), link(c + S / 2, yb, ww - S / 2, yb - dk, S, S, S))
    elif ch == 'З':
        ins = round(0.26 * CT)
        p = U(top(0, W - ins), bar(round(0.30 * CT), W, yb), bot(0, W), mast(W - S, y0, yb + B / 2), mast(W - S - ins, yb - B / 2, y1),
              rect(0, y1 - tk, S, y1), rect(0, y0, S, y0 + tk))
    elif ch in 'ИЙ':
        zt, zb = y0 + 0.74 * h, y0 + 0.30 * h
        p = U(mast(0), mast(W - S), link(S / 2, zb, W - S / 2, zt, S, S, S))
    elif ch == 'П':
        p = U(mast(0), mast(W - S), top(0, W))
    elif ch == 'Ф':
        ww = W + round(0.5 * CT) if W - 3 * S < 2 * 30 else W; c = (ww - S) / 2
        p = U(mast(c), D(rect(0, y0 + 0.42 * h, ww, y0 + 0.86 * h), rect(S, y0 + 0.42 * h + B, ww - S, y0 + 0.86 * h - B)))
    elif ch in 'ЦЩ':
        n = 2 if ch == 'Ц' else 3; e = round(0.24 * CT); wb = (n - 1) * (W - S) + S; ft = 0 if nest else 0.075 * CAP
        p = U(*[mast(i * (W - S)) for i in range(n)], bot(0, wb + e), rect(wb + e - S, y0 - ft, wb + e, y0 + B)); ww = wb + e
    elif ch == 'Ч':
        yq = y0 + round(0.46 * h)
        p = U(mast(0, yq - B / 2, y1), bar(0, W, yq), mast(W - S))
    elif ch == 'Ш':
        ww = 2 * W - S; p = U(mast(0), mast(W - S), mast(ww - S), bot(0, ww))
    elif ch in 'ЪЬЫ':
        ym = y0 + round(0.50 * h); e = round(0.36 * CT) if ch == 'Ъ' else 0
        p = U(mast(e), bar(e, e + W, ym), mast(e + W - S, y0, ym + B / 2), bot(e, e + W)); ww = e + W
        if ch == 'Ъ': p = U(p, top(0, e + S))
        if ch == 'Ы': gp = round(0.5 * w.G); p = U(p, mast(W + gp)); ww = W + gp + S
    elif ch == 'Э':
        ww = We; p = U(mast(ww - S), top(0, ww), bot(0, ww), bar(round(0.26 * CT), ww, y0 + 0.5 * h))
        if not nest: p = U(p, rect(0, y1 - tk, tw, y1), rect(0, y0, tw, y0 + tk))
    elif ch == 'Ю':
        e = S + round(0.34 * CT); ww = e + W
        p = U(mast(0), bar(0, e + S, y0 + 0.5 * h), D(rect(e, y0, ww, y1), rect(e + S, y0 + B, ww - S, y1 - B)))
    elif ch == 'Я':
        g = letter('R', w, y0, y1); p = mirror(g.ink, W / 2)
    else:
        raise KeyError(ch)
    if ch not in 'QДЦЩ' or nest: p = I(p, box)
    return Gl(p, ww, ch in LM, ch in RM)
