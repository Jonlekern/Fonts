# SHEARLINE : minuscules a–z, ſ, ß et ligatures, tracées à la plume large
from shr_core import *

class Wt:
    def __init__(s, name, W, t, wclass=400):
        s.name, s.W, s.t, s.wclass = name, W, t, wclass
        s.pen = Pen(W, t)
        s.s = 1.05 * W + 70                     # écart entre deux fûts (axe à axe)
        s.k = 0.28 * W                          # tête et pied en losange
        s.yb = 0.32 * W                         # axe de la plume au pied (l'encre touche la ligne de base)
        s.yt = XH - 0.32 * W                    # axe de la plume en haut de x
        s.ya = ASC - 0.32 * W                   # haut des hampes
        s.yc = CAP - 0.32 * W                   # haut des capitales
        s.yd = DESC + 0.32 * W                  # bas des jambages
        s.tb = 0.30 * W + 5                     # épaisseur des barres de croix
        s.SB = 0.18 * W + 22                    # approche

class Cross:
    """les croix : mode 'mix' (chaque lettre la sienne), 'latin', 'patri', 'pattee', 'none'"""
    def __init__(s, w, mode='mix'): s.w, s.mode = w, mode
    def __call__(s, kind, cx, y, width):
        w = s.w; kind = kind if s.mode == 'mix' else s.mode
        if kind == 'none': return None
        if kind == 'latin': return bar_latin(cx, y, width, w.tb)
        if kind == 'patri': return bar_patriarch(cx, y - 0.9 * w.tb, width, w.tb, 2.4 * w.tb)
        return bar_pattee(cx, y, width, w.tb)

def stem(w, x, top, bot=None, foot=True, head=True):
    k = w.k; bot = w.yb if bot is None else bot
    pts = [(x - k, top), (x, top - 1.2 * k)] if head else [(x, top)]
    pts.append((x, bot + (k if foot else 0)))
    if foot: pts.append((x + k, bot))
    return pts

def lower(w, mode='mix'):
    s, k, yb, yt, ya, yd, pen = w.s, w.k, w.yb, w.yt, w.ya, w.yd, w.pen
    cx = Cross(w, mode); G = {}
    st = pen.stroke
    yx = ASC - 0.50 * (ASC - XH)                # hauteur des croix sur les hampes (sous la tête du fût)
    def arch(x0=0, x1=None, foot=True, bot=None):
        x1 = s if x1 is None else x1; bot = yb if bot is None else bot
        p = [(x0, yt - 2.6 * k), (x0 + 0.5 * (x1 - x0), yt), (x1, yt - 1.2 * k), (x1, bot + (k if foot else 0))]
        if foot: p.append((x1 + k, bot))
        return p
    bowlL = [(s - k, yt), (0.35 * s, yt), (0, yt - 0.45 * s), (0, yb + 0.35 * s), (0.3 * s, yb), (0.9 * s, yb + 0.3 * s)]
    tailR = lambda x: [(x, 0.10 * s), (x - 0.15 * s, 0.45 * DESC), (x - 0.65 * s, 0.75 * DESC)]
    # a b c d e
    G['a'] = U(st(bowlL), st(stem(w, s, yt)))
    G['b'] = U(st(stem(w, 0, ya, foot=False)), st([(0, yt - 2.6 * k), (0.5 * s, yt), (s, yt - 1.2 * k), (s, yb + 0.35 * s), (0.6 * s, yb), (0, yb + 0.1 * s)]),
               cx('patri', 0, yx, 1.05 * s))
    G['c'] = st([(0.8 * s, yt - 0.2 * s), (0.6 * s, yt), (0.3 * s, yt), (0, yt - 0.4 * s), (0, yb + 0.35 * s), (0.3 * s, yb), (0.8 * s, yb + 0.25 * s)])
    G['d'] = U(st(bowlL[:-1] + [(s, yb + 0.3 * s)]), st([(s + k, yb), (s, yb + k), (s, yt - 0.05 * s), (0.2 * s, ya)]))
    G['e'] = st([(0.02 * s, 0.50 * XH), (0.8 * s, yt - 0.28 * s), (0.8 * s, yt - 0.18 * s), (0.6 * s, yt), (0.3 * s, yt), (0, yt - 0.4 * s), (0, yb + 0.35 * s), (0.3 * s, yb), (0.8 * s, yb + 0.25 * s)])
    # f ſ : hampe, crochet en haut ; la barre du f est une croix latine
    hook = [(0, ya - 0.55 * s), (0.3 * s, ya), (0.85 * s, ya - 0.15 * s)]
    G['longs'] = U(st(stem(w, 0, ya - 0.5 * s, head=False)), st(hook))
    G['f'] = U(G['longs'], cx('latin', 0.15 * s, XH - 0.5 * w.tb, 1.1 * s) if mode != 'none' else rect(-0.4 * s, XH - w.tb, 0.7 * s, XH))
    # g
    G['g'] = U(st(bowlL), st([(s - k, yt), (s, yt - 1.2 * k)] + tailR(s)))
    # h i j k l
    G['h'] = U(st(stem(w, 0, ya)), st(arch(foot=False, bot=0.10 * s)[:-1] + tailR(s)), cx('patri', 0, yx, 1.05 * s))
    yi = XH + 0.18 * (ASC - XH)
    def tittle(x):
        if mode == 'none': return st([(x - 0.35 * k, yi + 0.9 * k), (x + 0.35 * k, yi + 0.1 * k)])
        h = 0.62 * s
        return U(rect(x - 0.45 * w.tb, yi, x + 0.45 * w.tb, yi + h), cx('latin', x, yi + 0.66 * h, 0.55 * s))
    G['dotlessi'] = st(stem(w, 0, yt))
    G['i'] = U(G['dotlessi'], tittle(0))
    G['uni0237'] = st(stem(w, 0, yt, foot=False)[:-1] + tailR(0))
    G['j'] = U(G['uni0237'], tittle(0))
    G['k'] = U(st(stem(w, 0, ya)), st([(0, yt - 2.6 * k), (0.5 * s, yt), (0.8 * s, yt - 0.25 * s), (0.25 * s, 0.48 * XH)]),
               st([(0.25 * s, 0.48 * XH), (0.8 * s, 0.30 * XH), (0.8 * s, yb + k), (0.8 * s + k, yb)]), cx('patri', 0, yx, 1.05 * s))
    G['l'] = U(st(stem(w, 0, ya)), cx('latin', 0, yx, 1.05 * s))
    # m n o p q r
    G['n'] = U(st(stem(w, 0, yt)), st(arch()))
    G['m'] = U(st(stem(w, 0, yt)), st(arch(0, s)[:-1]), st(arch(s, 2 * s)))
    o = [(0.45 * s, yt), (0, yt - 0.4 * s), (0, yb + 0.35 * s), (0.45 * s, yb), (0.9 * s, yb + 0.35 * s), (0.9 * s, yt - 0.4 * s), (0.45 * s, yt)]
    G['o'] = st(o)
    G['p'] = U(st(stem(w, 0, yt, bot=yd, foot=False)), st([(0, yt - 2.6 * k), (0.5 * s, yt), (s, yt - 1.2 * k), (s, yb + 0.35 * s), (0.6 * s, yb), (0, yb + 0.1 * s)]))
    G['q'] = U(st(bowlL), st(stem(w, s, yt, bot=yd, foot=False)))
    G['r'] = U(st(stem(w, 0, yt)), st([(0, yt - 2.4 * k), (0.45 * s, yt), (0.75 * s, yt - 0.2 * s)]))
    # s rond (fin de mot)
    G['s'] = st([(0.8 * s, yt - 0.15 * s), (0.55 * s, yt), (0.1 * s, yt - 0.25 * s), (0.1 * s, 0.56 * XH), (0.75 * s, 0.44 * XH), (0.8 * s, yb + 0.3 * s), (0.5 * s, yb), (0, yb + 0.2 * s)])
    # t
    tt = XH + 0.55 * (ASC - XH) - 0.32 * w.W
    G['t'] = U(st([(-k, tt), (0, tt - 1.2 * k), (0, yb + 0.3 * s), (0.3 * s, yb), (0.75 * s, yb + 0.25 * s)]),
               cx('latin', 0.05 * s, XH - 0.5 * w.tb, 1.25 * s) if mode != 'none' else rect(-0.45 * s, XH - w.tb, 0.6 * s, XH))
    # u v w x y z
    G['u'] = U(st(stem(w, 0, yt, foot=False)[:-1] + [(0, yb + 0.35 * s), (0.4 * s, yb), (s, yb + 0.35 * s)]), st(stem(w, s, yt)))
    G['v'] = st(stem(w, 0, yt, foot=False)[:-1] + [(0, yb + 0.35 * s), (0.4 * s, yb), (0.9 * s, yb + 0.4 * s), (0.9 * s, yt - 0.3 * s), (0.6 * s, yt)])
    G['w'] = U(st(stem(w, 0, yt, foot=False)[:-1] + [(0, yb + 0.35 * s), (0.4 * s, yb), (s, yb + 0.35 * s)]),
               st(stem(w, s, yt, foot=False)[:-1] + [(s, yb + 0.35 * s), (1.4 * s, yb), (1.9 * s, yb + 0.4 * s), (1.9 * s, yt - 0.3 * s), (1.6 * s, yt)]))
    G['x'] = U(st([(-0.05 * s, yt), (0.25 * s, yt), (0.85 * s, yb + 0.2 * s), (0.85 * s, 0.3 * DESC), (0.45 * s, 0.6 * DESC)]), st([(0, yb), (0.85 * s, yt)]))
    G['y'] = st(stem(w, 0, yt, foot=False)[:-1] + [(0, yb + 0.35 * s), (0.4 * s, yb), (0.9 * s, yb + 0.4 * s), (0.9 * s, yt - 0.3 * s), (0.6 * s, yt)]) if False else \
        U(st(stem(w, 0, yt, foot=False)[:-1] + [(0, yb + 0.35 * s), (0.4 * s, yb), (0.9 * s, yb + 0.3 * s)]), st([(0.6 * s, yt), (0.9 * s, yt - 0.3 * s)] + tailR(0.9 * s)))
    G['z'] = st([(0.05 * s, yt - 0.05 * s), (0.85 * s, yt), (0.25 * s, 0.42 * XH), (0.8 * s, 0.30 * XH), (0.8 * s, 0.2 * DESC), (0.55 * s, 0.6 * DESC), (0.1 * s, 0.75 * DESC)])
    # ß = ſ + z
    G['germandbls'] = U(G['longs'], mv(G['z'], 0.9 * s))
    return G

# ligatures (paires serrées : les lettres se touchent)
LIGS = {'c_h': ('c', 'h'), 'c_k': ('c', 'k'), 't_z': ('t', 'z'), 'longs_t': ('longs', 't'), 'longs_longs': ('longs', 'longs')}
def ligatures(w, G):
    L = {}
    for n, (a, b) in LIGS.items():
        ga, gb = G[a], G[b]; ba, bb = bounds(ga), bounds(gb)
        gap = -0.06 * w.s if a != 'longs' else -0.30 * w.s           # le crochet du ſ vient toucher la lettre suivante
        L[n] = U(ga, mv(gb, ba[2] - bb[0] + gap))
    return L
