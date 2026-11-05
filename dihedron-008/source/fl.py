# Police "flèche" — toutes les graisses.
# Tout est dessiné en segments droits (unités : capitales de 700, y vers le haut).
# set_weight(f, wx) : f = épaisseur relative (1 = ExtraBold), wx = élargissement (Black).
import math, os, pathops
from pathops import Path
from fontTools.pens.transformPen import TransformPen

H = 700          # hauteur des capitales
OV = 22          # débord des pointes
K = 180 / 165    # pente des coupes en biais
MID = 0.42       # hauteur du milieu (top heavy)
ACC_Y = 780      # bas des accents

# épaisseurs, recalculées par set_weight
WF = 1.0
S = B = D = C = BT = BB = TM = TT = TB = 0.0
def _thick(f):
    global WF, S, B, D, C, BT, BB, TM, TT, TB
    WF = f
    S = 165*f; B = 135*f; D = 145*f; C = S*K
    BT = 170*f; BB = 100*f; TM = (BT + BB)/2
    TT = 140*f*170/135; TB = 140*f*100/135   # losanges : haut épais, bas fin
def ww():  # largeur des coins : ils s'amincissent moins vite que les fûts
    return WF**0.75
def g():  # taille des points, virgules : varie moins que les fûts
    return 0.35 + 0.65*WF
_thick(1.0)

# ---------------------------------------------------------------- outils
def P(pts):
    p = Path(); p.moveTo(*pts[0])
    for q in pts[1:]: p.lineTo(*q)
    p.close(); return p
def U(*ps):
    out = ps[0]
    for p in ps[1:]: out = pathops.op(out, p, pathops.PathOp.UNION)
    return out
def Dif(a, *bs):
    out = a
    for b in bs: out = pathops.op(out, b, pathops.PathOp.DIFFERENCE)
    return out
def X(a, b): return pathops.op(a, b, pathops.PathOp.INTERSECTION)
def tf(path, m):
    out = Path(); path.draw(TransformPen(out.getPen(), m)); return out
def mv(path, dx, dy=0): return tf(path, (1, 0, 0, 1, dx, dy))
def rot180(path, cx, cy): return tf(path, (-1, 0, 0, -1, 2*cx, 2*cy))
def scale(path, s, dx=0, dy=0): return tf(path, (s, 0, 0, s, dx, dy))
def box(x0, y0, x1, y1): return P([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
def wedge(x0, x1, ytop, tip): return P([(x0, ytop), (x1, ytop), tip])
def dia(cx, cy, hw, hh): return P([(cx, cy + hh), (cx + hw, cy), (cx, cy - hh), (cx - hw, cy)])

def inter(p1, d1, p2, d2):
    den = d1[0]*d2[1] - d1[1]*d2[0]
    s = ((p2[0]-p1[0])*d2[1] - (p2[1]-p1[1])*d2[0]) / den
    return (p1[0]+d1[0]*s, p1[1]+d1[1]*s)

def inset(poly, ts):
    n = len(poly); cx = sum(x for x, _ in poly)/n; cy = sum(y for _, y in poly)/n
    L = []
    for i in range(n):
        (x1, y1), (x2, y2) = poly[i], poly[(i+1) % n]
        dx, dy = x2-x1, y2-y1; l = math.hypot(dx, dy); nx, ny = -dy/l, dx/l
        if (cx-x1)*nx + (cy-y1)*ny < 0: nx, ny = -nx, -ny
        t = ts[i] if isinstance(ts, (list, tuple)) else ts
        L.append(((x1+nx*t, y1+ny*t), (dx, dy)))
    return [inter(*L[i-1], *L[i]) for i in range(n)]

def ring(poly, ts):
    return Dif(P(poly), hole(poly, ts))

def hole(poly, ts):
    """Creux : intersection des demi-plans décalés (jamais de polygone croisé)."""
    n = len(poly); cx = sum(x for x, _ in poly)/n; cy = sum(y for _, y in poly)/n
    hole = P(poly); Z = 1e4
    for i in range(n):
        (x1, y1), (x2, y2) = poly[i], poly[(i+1) % n]
        dx, dy = x2-x1, y2-y1; l = math.hypot(dx, dy); ux, uy = dx/l, dy/l; nx, ny = -uy, ux
        if (cx-x1)*nx + (cy-y1)*ny < 0: nx, ny = -nx, -ny
        t = ts[i] if isinstance(ts, (list, tuple)) else ts
        ox, oy = x1 + nx*t, y1 + ny*t
        half = P([(ox - ux*Z, oy - uy*Z), (ox + ux*Z, oy + uy*Z),
                  (ox + ux*Z + nx*Z, oy + uy*Z + ny*Z), (ox - ux*Z + nx*Z, oy - uy*Z + ny*Z)])
        hole = X(hole, half)
    return hole

def poly_stroke(pts, t, miter=8):
    sp = Path(); sp.moveTo(*pts[0])
    for q in pts[1:]: sp.lineTo(*q)
    sp.stroke(t, pathops.LineCap.BUTT_CAP, pathops.LineJoin.MITER_JOIN, miter)
    return sp

def stem(x, y0, y1, top=None, bot=None, w=None):
    """Fût vertical. 'R' intérieur à droite, 'L' à gauche, 'P' pointe, None plat."""
    w = S if w is None else w
    c = C*w/S; p = c/2
    tl, tr = (x, y1), (x+w, y1); mt = []
    if top == 'R': tl = (x, y1-c)
    elif top == 'L': tr = (x+w, y1-c)
    elif top == 'P': tl, tr, mt = (x, y1-p), (x+w, y1-p), [(x+w/2, y1)]
    bl, br = (x, y0), (x+w, y0); mb = []
    if bot == 'R': bl = (x, y0+c)
    elif bot == 'L': br = (x+w, y0+c)
    elif bot == 'P': bl, br, mb = (x, y0+p), (x+w, y0+p), [(x+w/2, y0)]
    return P([bl, tl] + mt + [tr, br] + mb)

def bar(x0, x1, y, t=None, left=None, right=None):
    """Barre horizontale de y à y+t. 'U' intérieur en haut, 'D' en bas, 'P' pointe, None plat."""
    t = B if t is None else t
    r = t/K; pts = []
    if left == 'U': pts += [(x0+r, y), (x0, y+t)]
    elif left == 'D': pts += [(x0, y), (x0+r, y+t)]
    elif left == 'P': pts += [(x0+r/2, y), (x0, y+t/2), (x0+r/2, y+t)]
    else: pts += [(x0, y), (x0, y+t)]
    if right == 'U': pts += [(x1, y+t), (x1-r, y)]
    elif right == 'D': pts += [(x1-r, y+t), (x1, y)]
    elif right == 'P': pts += [(x1-r/2, y+t), (x1, y+t/2), (x1-r/2, y)]
    else: pts += [(x1, y+t), (x1, y)]
    return P(pts)

def kite(w):
    cx = w/2
    return [(cx, H+OV), (w, H*MID), (cx, -OV), (0, H*MID)], [TT, TB, TB, TT]

def kring(cx, y0, y1, hw, ym, tt, tb):
    pts = [(cx, y1), (cx + hw, ym), (cx, y0), (cx - hw, ym)]
    return ring(pts, [tt, tb, tb, tt]), pts

def counter_top(w):
    pts, ts = kite(w)
    return max(y for _, y in inset(pts, ts))

# ---------------------------------------------------------------- registre
G = {}      # caractère -> (path, largeur dessin, approche gauche, approche droite)
ORDER = []
def add(ch, path, w, l=40, r=40):
    if ch not in G: ORDER.append(ch)
    G[ch] = (path, w, l, r)

# ---------------------------------------------------------------- capitales
def a_shape(w):
    cx = w/2; xf = 166.5*WF; hf = 183*WF
    ya = H + OV - (H + OV - 400*MID/0.5)*WF
    return Dif(P([(cx, H+OV), (w, hf), (w-xf, 0), (xf, 0), (0, hf)]), P([(cx, ya), (w-xf, 0), (xf, 0)]))

def v_poly(w, ox=0, xf=None):
    cx = w/2 + ox; xf = (w/2 - 120)*WF if xf is None else xf; hf = 183*WF
    yv = -OV + (H - 464 + OV)*WF
    out = P([(cx, -OV), (ox + w, H - hf), (ox + w - xf, H), (ox + xf, H), (ox, H - hf)])
    return Dif(out, P([(cx, yv), (ox + w - xf, H), (ox + xf, H)]))

def u_shape(w):
    cx = w/2; ym = H*0.40; Dd = D*BB/B
    out = [(0, H), (0, ym), (cx, -OV), (w, ym), (w, H)]
    dl = (cx, -OV-ym); l = math.hypot(*dl); nl = (-dl[1]/l, dl[0]/l)
    a = inter((nl[0]*Dd, ym+nl[1]*Dd), dl, (S, 0), (0, 1))
    b = inter((nl[0]*Dd, ym+nl[1]*Dd), dl, (cx, 0), (0, 1))
    body = Dif(P(out), P([(S, H+10), a, b, (w-a[0], a[1]), (w-S, H+10)]))
    cut = U(P([(-1, H-C), (S, H), (-1, H+50)]), P([(w+1, H-C), (w-S, H), (w+1, H+50)]))
    return Dif(body, cut)

def m_shape(w, flip=False):
    cx = w/2; t = 200*WF*170/135; yv = H*0.28; xd = S + 20*WF; dv = t*1.35
    up_d = (cx - xd, yv + dv - H)
    yS = yv + (S - cx)*up_d[1]/up_d[0]
    left = P([(0, H), (xd, H), (cx, yv + dv), (cx, yv), (S - 5, yS), (S - 5, H)])
    right = P([(w, H), (w - xd, H), (cx, yv + dv), (cx, yv), (w - S + 5, yS), (w - S + 5, H)])
    gl = U(stem(0, 0, H, None, 'R'), stem(w - S, 0, H, None, 'L'), left, right)
    return tf(gl, (1, 0, 0, -1, 0, H)) if flip else gl

def v_top(w, hw):
    cx = w/2; wa = 230*WF; yb = H*MID - 20
    yn = H + (cx - wa)*(yb - H)/(cx - hw)
    return P([(0, H), (wa, H), (cx, yn), (w - wa, H), (w, H), (cx + hw, yb), (cx - hw, yb)]), yb

def zdiag(w, wt, xb, bt, bb):
    return P([(w - wt, H), (w, H), (w, H - bt), (xb, bb), (0, bb)])

def bowl_ring(x1, y0, y1, ttop, tbot):
    cx = x1*0.48
    return ring([(0, y0), (0, y1), (cx, y1), (x1, (y0+y1)/2), (cx, y0)], [S, ttop, D*ttop/B, D*tbot/B, tbot])

def build_letters():
    add('A', a_shape(573), 573, 12, 12)
    pts, ts = kite(600); add('O', ring(pts, ts), 600, 15, 15)
    w = 200*ww(); add('I', P([(0, H), (w, H), (w/2, -OV)]), w, 40, 40)
    add('L', U(stem(0, 0, H), bar(0, 470, 0, BB, right='U')), 470, 45, 20)
    w = 470
    add('E', U(stem(0, 0, H), bar(0, w, H-BT, BT, right='D'), bar(0, w-40, H*MID - TM/2, TM),
               bar(0, w, 0, BB, right='U')), w, 45, 20)
    w = 450
    add('F', U(stem(0, 0, H, None, 'R'), bar(0, w, H-BT, BT, right='D'), bar(0, w-40, H*MID - TM/2 - 20, TM)), w, 45, 20)
    w = 560
    add('T', U(bar(0, w, H-BT, BT, left='D', right='D'), P([(w/2-100*ww(), H), (w/2+100*ww(), H), (w/2, -OV)])), w, 20, 20)
    w = 560; cx = w*0.48
    add('D', ring([(0, 0), (0, H), (cx, H), (w, H*MID), (cx, 0)], [S, BT, D*BT/B, D*BB/B, BB]), w, 45, 15)
    add('U', u_shape(560), 560, 45, 45)
    # R
    w = 540; yb = 290 - (0.5-MID)*H*0.8; wb = 500; cx = wb*0.48
    bowl = ring([(0, yb), (0, H), (cx, H), (wb, (H+yb)/2), (cx, yb)], [S, BT, D*BT/B, D*TM/B, TM])
    tip = (w-40, -OV); x_l = cx + (cx - tip[0])*TM/(yb - tip[1])
    add('R', U(bowl, stem(0, 0, H, None, 'R'), P([(x_l, yb+TM), (x_l+220*ww(), yb+TM), tip])), w, 45, 10)
    # S carré
    w = 540; ym = H*MID - TM/2
    add('S', U(bar(0, w, H-BT, BT, right='D'), stem(0, ym, H), bar(0, w, ym, TM),
               stem(w-S, 0, ym+TM), bar(0, w, 0, BB)), w, 35, 35)
    # B
    w = 530; ym = H*MID - TM/2; wl = w - 30
    up = ring([(0, ym), (0, H), (w*0.48, H), (w, (H+ym)/2), (w*0.48, ym)], [S, BT, D*BT/B, D*TM/B, TM])
    lo = ring([(0, 0), (0, ym+TM), (wl*0.48, ym+TM), (wl, (ym+TM)/2), (wl*0.48, 0)], [S, TM, D*TM/B, D*BB/B, BB])
    add('B', U(up, lo), w, 45, 15)
    # C, G : bouche à droite
    w = 600; pts, ts = kite(w); y = H*MID; mt = min(counter_top(w), y + 140)
    add('C', Dif(ring(pts, ts), box(w/2, y - 70, w + 1e3, mt)), w, 15, 0)
    yt = mt - 110
    o = Dif(ring(pts, ts), box(w/2, yt, w + 1e3, mt))
    add('G', U(o, X(box(w/2, yt - TM*0.85, w + 10, yt), P(pts))), w, 15, 15)
    # H
    w = 560
    add('H', U(stem(0, 0, H, 'R', 'R'), stem(w-S, 0, H, 'L', 'L'), bar(0, w, H*MID - TM/2, TM)), w, 45, 45)
    # J
    w = 520; yj = H*0.40 + 120
    body = Dif(u_shape(w), box(-1e3, yj, w/2, 1e3))
    add('J', Dif(body, P([(-1, yj - C), (S, yj), (-1, yj + 10)])), w, 15, 45)
    # K
    w = 560; wa = 230*WF; y0 = H*MID - 90
    d = (w - S, H - y0)
    top_s = inter((w - wa, H), d, (S - 5, 0), (0, 1))
    arm = P([(S - 5, y0), (w, H), (w - wa, H), top_s])
    tipk = (w - 20, -OV); yj = y0 + 30
    leg = P([(S - 5, yj), (S + 200*ww(), yj + 200*ww()*d[1]/d[0] + 20*WF), tipk])
    add('K', U(stem(0, 0, H, 'R', 'R'), arm, leg), w, 45, 0)
    # M, W
    add('M', m_shape(720), 720, 45, 45)
    vw = 480; xf = 120*WF; ox = vw - xf
    fill = P([(vw - xf, H), (vw, H), (vw - xf/2, H - 300*WF)])
    add('W', U(v_poly(vw, 0, xf), v_poly(vw, ox, xf), fill), ox + vw, 12, 12)
    # N
    w = 580
    add('N', U(stem(0, 0, H, None, 'R'), stem(w - S, 0, H, 'L', None),
               P([(0, H), (260*WF, H), (w, 0), (w - 190*WF, 0)])), w, 45, 45)
    # P
    w = 520; yb = 290 - (0.5-MID)*H*0.8; cx = w*0.48
    add('P', U(ring([(0, yb), (0, H), (cx, H), (w, (H+yb)/2), (cx, yb)], [S, BT, D*BT/B, D*TM/B, TM]),
               stem(0, 0, H, None, 'R')), w, 45, 15)
    # Q
    w = 600; pts, ts = kite(w); cx = w/2
    mx, my = (w + cx)/2, (H*MID - OV)/2
    dd = (cx - w, -OV - H*MID); l = math.hypot(*dd); dd = (dd[0]/l, dd[1]/l)
    n = (-dd[1], dd[0])
    if n[0]*(cx - mx) + n[1]*(H*MID - my) < 0: n = (-n[0], -n[1])
    c = (mx + n[0]*45*WF, my + n[1]*45*WF)
    tail = P([(c[0] + dd[0]*100*WF, c[1] + dd[1]*100*WF), (c[0] - dd[0]*100*WF, c[1] - dd[1]*100*WF), (w + 40, -110)])
    add('Q', U(ring(pts, ts), tail), w, 15, 15)
    # V
    add('V', v_poly(573), 573, 12, 12)
    # X, Y
    w = 600; cx = w/2; hw = 120*WF
    top, yb = v_top(w, hw)
    ll = P([(cx - hw, yb + 10), (cx + 20*WF, yb + 10), (180*WF, 0), (0, 0)])
    lr = P([(cx + hw, yb + 10), (cx - 20*WF, yb + 10), (w - 180*WF, 0), (w, 0)])
    add('X', U(top, ll, lr), w, 10, 10)
    hw = 100*WF; top, yb = v_top(w, hw)
    add('Y', U(top, P([(cx - hw, yb + 10), (cx + hw, yb + 10), (cx, -OV)])), w, 10, 10)
    # Z
    w = 540
    add('Z', U(bar(0, w, H - BT, BT), bar(0, w, 0, BB), zdiag(w, 300*WF, 200*WF, BT, BB)), w, 20, 20)

# ---------------------------------------------------------------- accents
def m_acute(): return P([(150 - 170*WF, ACC_Y + 200), (150, ACC_Y + 200), (-95, ACC_Y)])
def m_grave(): return P([(-150 + 170*WF, ACC_Y + 200), (-150, ACC_Y + 200), (95, ACC_Y)])
def m_circ():
    i = 185 - 105*WF
    return P([(0, ACC_Y + 205), (185, ACC_Y), (i, ACC_Y), (0, ACC_Y + 205 - 110*WF), (-i, ACC_Y), (-185, ACC_Y)])
def m_dier():
    hw, hh = 78*g(), 95*g()
    return U(dia(-112, ACC_Y + hh, hw, hh), dia(112, ACC_Y + hh, hw, hh))
def m_tilde():
    sp = poly_stroke([(-230, ACC_Y + 20), (-80, ACC_Y + 165), (80, ACC_Y + 35), (230, ACC_Y + 180)], 100*WF, 4)
    return X(sp, box(-190, ACC_Y - 60, 190, ACC_Y + 240))
def m_cedilla(): return P([(-55*g(), 40), (55*g(), 40), (-75, -220)])
MARKS = {'acute': m_acute, 'grave': m_grave, 'circ': m_circ, 'dier': m_dier, 'tilde': m_tilde, 'cedilla': m_cedilla}

def compose(new, base, mark):
    p, w, l, r = G[base]
    m = mv(MARKS[mark](), w/2)
    x0, _, x1, _ = m.bounds
    add(new, U(p, m), w, max(l, -x0 + 25), max(r, x1 - w + 25))

def build_accents():
    table = {
        'À': ('A', 'grave'), 'Â': ('A', 'circ'), 'Ä': ('A', 'dier'), 'Á': ('A', 'acute'),
        'É': ('E', 'acute'), 'È': ('E', 'grave'), 'Ê': ('E', 'circ'), 'Ë': ('E', 'dier'),
        'Í': ('I', 'acute'), 'Î': ('I', 'circ'), 'Ï': ('I', 'dier'), 'Ñ': ('N', 'tilde'),
        'Ó': ('O', 'acute'), 'Ô': ('O', 'circ'), 'Ö': ('O', 'dier'),
        'Ú': ('U', 'acute'), 'Ù': ('U', 'grave'), 'Û': ('U', 'circ'), 'Ü': ('U', 'dier'),
        'Ÿ': ('Y', 'dier'), 'Ç': ('C', 'cedilla'),
    }
    for new, (b, m) in table.items(): compose(new, b, m)
    e = G['E'][0]
    pts, ts = kite(600); cx = 300
    add('Œ', U(X(ring(pts, ts), box(-10, 0, cx, H)), mv(e, cx - S/2)), cx - S/2 + 470, 15, 20)
    ca = 573/2
    add('Æ', U(X(a_shape(573), box(-10, -100, ca - S/2 + 1, H + 100)), mv(e, ca - S/2)), ca - S/2 + 470, 12, 20)
    w = 520; ym = H*MID - TM/2
    lo = ring([(0, 0), (0, ym+TM), (w*0.48, ym+TM), (w, (ym+TM)/2), (w*0.48, 0)], [S, TM, D*TM/B, D*BB/B, BB])
    lo = Dif(lo, box(S - 1, -50, S + 70*g(), ym))
    dw = 190*WF
    dg = P([(w - 20 - dw, H - 1), (w - 20, H - 1), (w*0.50, ym + TM - 1), (w*0.50 - dw, ym + TM - 1)])
    add('ẞ', U(stem(0, 0, H), bar(0, w - 20, H - BT, BT), dg, lo), w, 45, 15)

# ---------------------------------------------------------------- ponctuation, symboles
def build_specials():
    gg = g()
    dhw, dhh = 85*gg, 105*gg
    dot_y = dhh - OV
    dot = lambda cx: dia(cx, dot_y, dhw, dhh)
    dw = 2*dhw
    add('.', dot(dhw), dw)
    comma = wedge(0, dw, 2*dhh - OV, (0.15*dw, -210))
    add(',', comma, dw)
    add(':', U(dot(dhw), dia(dhw, 400, dhw, dhh)), dw)
    add(';', U(comma, dia(dhw, 400, dhw, dhh)), dw)
    add('…', U(dot(dhw), dot(dhw + 230*gg), dot(dhw + 460*gg)), dw + 460*gg)
    ew = max(190*ww(), dw)
    excl = U(wedge(ew/2 - 95*ww(), ew/2 + 95*ww(), H, (ew/2, 250)), dot(ew/2))
    add('!', excl, ew, 45, 45)
    add('¡', rot180(excl, ew/2, H/2), ew, 45, 45)
    w = 470; xc = w*0.42
    q = U(stem(0, H - 290, H, None, 'R'), bar(0, w, H - BT, BT), stem(w - S, 430, H),
          P([(w - S, 431), (w, 431), (xc, 235)]), dot(xc))
    add('?', q, w, 35, 35)
    add('¿', rot180(q, w/2, H/2), w, 35, 35)
    # guillemets
    qw = 150*(0.25 + 0.75*WF)
    ap = wedge(0, qw, H, (qw/2, H - 290))
    add("'", ap, qw); add('"', U(ap, mv(ap, qw + 60)), 2*qw + 60)
    rq = wedge(0, qw, H, (0.13*qw, H - 300)); lq = rot180(rq, qw/2, H - 150)
    add('’', rq, qw); add('‘', lq, qw)
    add('”', U(rq, mv(rq, qw + 50)), 2*qw + 50); add('“', U(lq, mv(lq, qw + 50)), 2*qw + 50)
    add('„', U(comma, mv(comma, dw + 40)), 2*dw + 40)
    def chev(x0, cy, h=340, wd=210, d_in=None):
        d_in = 130*WF if d_in is None else d_in
        c = d_in*(h/2)/wd
        return P([(x0, cy), (x0 + wd, cy + h/2), (x0 + wd, cy + h/2 - c), (x0 + d_in, cy),
                  (x0 + wd, cy - h/2 + c), (x0 + wd, cy - h/2)])
    cy = H*MID + 20
    left2 = U(chev(0, cy), chev(190, cy))
    add('«', left2, 400, 30, 30); add('»', tf(left2, (-1, 0, 0, 1, 400, 0)), 400, 30, 30)
    add('‹', chev(0, cy), 210, 30, 30); add('›', tf(chev(0, cy), (-1, 0, 0, 1, 210, 0)), 210, 30, 30)
    # tirets
    yh = H*MID - TM/2
    add('-', bar(0, 270, yh, TM), 270, 35, 35)
    add('–', bar(0, 500, yh, TM), 500, 30, 30)
    add('—', bar(0, 900, yh, TM), 900, 30, 30)
    # parenthèses, barre
    top, bot = H + 90, -160; cyp = (top + bot)/2; wp = 240; th = 150*WF
    paren = P([(wp, top), (wp - th*0.9, top), (0, cyp), (wp - th*0.9, bot), (wp, bot), (th*1.05, cyp)])
    add('(', paren, wp, 40, 20); add(')', tf(paren, (-1, 0, 0, 1, wp, 0)), wp, 20, 40)
    sw_ = 190*WF
    add('/', P([(0, -100), (sw_, -100), (440, H + 60), (440 - sw_, H + 60)]), 440, 10, 10)
    # + =
    pc = 300
    add('+', U(box(0, pc - 60*WF, 440, pc + 60*WF), box(220 - 60*WF, pc - 220, 220 + 60*WF, pc + 220)), 440, 40, 40)
    add('=', U(box(0, pc + 50, 440, pc + 50 + 115*WF), box(0, pc - 50 - 115*WF, 440, pc - 50)), 440, 40, 40)
    # *
    ac = (190, 540); arms = []
    for k in range(5):
        a = math.pi/2 + k*2*math.pi/5
        tip = (ac[0] + 190*math.cos(a), ac[1] + 190*math.sin(a))
        nx, ny = -math.sin(a), math.cos(a)
        arms.append(P([(ac[0] + nx*55*gg, ac[1] + ny*55*gg), tip, (ac[0] - nx*55*gg, ac[1] - ny*55*gg)]))
    add('*', U(*arms, dia(ac[0], ac[1], 60*gg, 60*gg)), 380, 30, 30)
    add('°', ring([(110, H + OV), (220, H - 130), (110, H - 290), (0, H - 130)], 70*WF), 220, 40, 40)
    hw_ = 560
    add('#', U(box(180 - 60*WF, 0, 180 + 60*WF, H), box(hw_ - 180 - 60*WF, 0, hw_ - 180 + 60*WF, H),
               box(0, 225 - 55*WF, hw_, 225 + 55*WF), box(0, 485 - 55*WF, hw_, 485 + 55*WF)), hw_, 30, 30)
    small = lambda cx, cy: ring([(cx, cy + 170), (cx + 125, cy), (cx, cy - 170), (cx - 125, cy)], 65*WF)
    pw = 160*WF
    add('%', U(small(125, H - 170), small(575, 170),
               P([(150 - pw/2, -OV), (150 + pw/2, -OV), (550 + pw/2, H + OV), (550 - pw/2, H + OV)])), 700, 25, 25)
    cp_, cw_, cl_, cr_ = G['C']; y0 = H*MID
    add('€', U(cp_, box(-90, y0 + 70 - 45*WF, 150, y0 + 70 + 45*WF), box(-90, y0 - 70 - 45*WF, 150, y0 - 70 + 45*WF)), cw_, cl_ + 90, cr_)
    sp, sw, sl, sr = G['S']
    add('$', U(sp, box(sw/2 - 55*WF, -120, sw/2 + 55*WF, H + 120)), sw, sl, sr)
    lw = 500
    add('£', U(stem(90, 0, H), bar(90, lw, H - BT, BT, right='D'), bar(0, lw, 0, BB),
               bar(0, 90 + S + 140, H*MID - TM/2, TM)), lw, 30, 20)
    sk = [(640, -150), (150, 470), (260, H + 40), (380, 520), (70, 240), (250, -20), (560, 310)]
    amp = X(poly_stroke(sk, 125*WF, 8), box(-50, -OV, 700, H + OV))
    x0, _, x1, _ = amp.bounds
    add('&', mv(amp, -x0), x1 - x0, 25, 20)
    aw = 800; acx = aw/2; acy = 300; at = 85*WF
    outer = Dif(ring([(acx, H + 60), (aw, acy), (acx, -100), (0, acy)], at), box(acx + 60, -200, aw + 50, acy - 90))
    inner = ring([(acx - 40, acy + 250), (acx + 110, acy + 30), (acx - 40, acy - 190), (acx - 190, acy + 30)], at)
    add('@', U(outer, inner, box(acx + 100, -30, acx + 100 + 90*WF, acy + 30)), aw, 25, 25)
    def badge(lp, lw_):
        bw = 760; bcx = bw/2; bcy = H*MID + 40; s_ = 0.36
        return U(ring([(bcx, H + OV), (bw, bcy), (bcx, -OV), (0, bcy)], 80*WF),
                 scale(lp, s_, bcx - lw_*s_/2, bcy - H*s_/2 - 10)), bw
    p_, bw = badge(G['C'][0], 430); add('©', p_, bw, 25, 25)
    p_, bw = badge(G['R'][0], G['R'][1]); add('®', p_, bw, 25, 25)
    s_ = 0.42; tp, tw = G['T'][0], G['T'][1]; mp, mw = G['M'][0], G['M'][1]
    add('™', U(scale(tp, s_, 0, H - H*s_), scale(mp, s_, tw*s_ + 30, H - H*s_)), tw*s_ + 30 + mw*s_, 40, 40)

# ---------------------------------------------------------------- chiffres
def build_digits():
    yt = H*MID + TM/2
    w = 470; z, _ = kring(w/2, -OV, H + OV, w/2, H*MID, TT, TB); add('0', z, w, 25, 25)
    w = 200*ww(); add('1', P([(0, H), (w, H), (w*0.65, -OV)]), w, 40, 40)
    # 2 : haut en pointe
    w = 500; cx = w/2; yr = 0.62*H
    tri = [(cx, H + OV), (w, yr), (0, yr)]
    hl = hole(tri, [TT, -10, TT])
    top2 = P(tri)
    if hl.area and hl.bounds[3] - yr > 60:
        top2 = Dif(top2, hl)        # graisses fines : pointe creuse ; grasses : pointe pleine
    dg2 = P([(w - 200*WF, yr + 1), (w, yr + 1), (w, yr - 60*WF), (200*WF, BB), (0, BB)])
    add('2', U(top2, X(dg2, box(0, 0, w, H)), bar(0, w, 0, BB)), w, 35, 35)
    # 3 carré
    w = 500; ym3 = H*MID - TM/2
    add('3', U(bar(0, w, H - BT, BT), bar(110, w, ym3, TM), bar(0, w, 0, BB), stem(w - S, 0, H)), w, 35, 35)
    # 4
    w = 540; xs = w - 240; yc = H*MID - TM/2 - 40
    add('4', U(P([(xs, H), (xs + 200*ww(), H), (xs + 100*ww(), -OV)]),
               P([(xs - 175*WF, H), (xs, H), (175*WF, yc + TM - 1), (0, yc + TM - 1)]),
               bar(0, w, yc, TM)), w, 20, 20)
    # 5
    w = 500; cxb = w*0.48
    bel = ring([(0, 0), (0, yt), (cxb, yt), (w, yt/2), (cxb, 0)], [S, TM, D*TM/B, D*BB/B, BB])
    bel = Dif(bel, box(-1, BB, S + 1, yt - TM))
    add('5', U(stem(0, yt - TM, H), bar(0, w, H - BT, BT, right='D'), bel), w, 40, 35)
    # 6, 9
    w = 500; cx = w/2; yb = 0.62*H; ym = (yb - OV)/2
    bowl, _ = kring(cx, -OV, yb, cx, ym, 135*WF, 120*WF)
    st6 = P([(w*0.50, H), (w*0.50 + 200*WF, H), (200*WF, ym + 150*WF), (0, ym)])
    six = U(bowl, X(st6, P([(0, H), (w, H), (w, ym), (cx, yb), (0, ym)])))
    add('6', six, w, 20, 20); add('9', rot180(six, w/2, H/2), w, 20, 20)
    # 7
    w = 500
    add('7', U(bar(0, w, H - BT, BT), P([(w - 215*ww(), H - BT + 1), (w, H - BT + 1), (w*0.30, -OV)])), w, 25, 25)
    # 8
    w = 500; cx = w/2; yj = 0.38*H
    up, _ = kring(cx, yj - 20, H + OV, cx, (yj + H)/2 + 10, 150*WF, 125*WF)
    lo, _ = kring(cx, -OV, yj + 120, cx - 25, (yj + 120 - OV)/2, 125*WF, 115*WF)
    add('8', U(up, lo), w, 20, 20)

# ---------------------------------------------------------------- minuscules
XH = 490          # hauteur des minuscules
DE = -230         # bas des descendantes

def build_lower():
    # minuscules un peu plus légères que les capitales (sinon les creux se bouchent)
    SL = S*0.92; BTl = BT*0.52; BBl = BB*0.52; TMl = (BTl + BBl)/2
    TTl = TT*0.8; TBl = TB*0.8; Dl = D*0.85
    def lst(x, y0, y1, top=None, bot=None): return stem(x, y0, y1, top, bot, w=SL)
    WL = 200*ww()*0.92                     # largeur du coin (comme le i)
    def lw(x, y1): return P([(x, y1), (x + WL, y1), (x + WL/2, -OV)])   # fût en coin
    def left_of(p1, p2):   # tout ce qui est à gauche de la droite p1 -> p2 (p1 en haut)
        dx, dy = p2[0] - p1[0], p2[1] - p1[1]
        return P([(p1[0] - dx*20, p1[1] - dy*20), (p1[0] + dx*20, p1[1] + dy*20), (-5000, p1[1] + dy*20), (-5000, p1[1] - dy*20)])
    def lkite(w, y0=-OV, y1=XH + OV):
        cx = w/2; ym = y0 + (y1 - y0)*MID
        return [(cx, y1), (w, ym), (cx, y0), (0, ym)], [TTl, TBl, TBl, TTl]
    # o
    w = 500; pts, ts = lkite(w); add('o', ring(pts, ts), w, 15, 15)
    # a, d : losange + fût à droite
    w = 480; pts, ts = lkite(w); o_ = ring(pts, ts)
    for ch, top in (('a', XH), ('d', H)):
        k = X(o_, left_of((w, top), (w - WL/2, -OV)))      # le losange ne dépasse pas du coin
        add(ch, U(k, lw(w - WL, top)), w, 15, 40)
    # l
    add('l', lw(0, H), WL, 40, 40)
    # i : petit coin + point en losange
    iw = 200*ww()*0.92; gg = g()
    dot = dia(iw/2, XH + 90 + 105*gg, 85*gg, 105*gg)
    add('i', U(P([(0, XH), (iw, XH), (iw/2, -OV)]), dot), iw, 40, 40)
    # f
    w = 380
    add('f', U(lw(0, H), bar(0, w, H - BTl, BTl, right='D'), bar(-60, w - 40, XH - TMl, TMl)), w, 60, 10)
    # t
    w = 360
    add('t', U(lw(0, XH + 170), bar(-60, w - 60, XH - TMl, TMl)), w - 60, 60, 15)
    # e : losange, barre au milieu, bouche en bas à droite
    w = 500; pts, ts = lkite(w); ym = pts[1][1]
    e_ = Dif(ring(pts, ts), box(w/2 + 40, -100, w + 1e3, ym - TMl/2))
    add('e', U(e_, X(box(0, ym - TMl/2, w, ym + TMl/2), P(pts))), w, 15, 10)
    # u : U en petit + fût droit jusqu'en bas
    w = 480; cx = w/2; ymu = XH*0.40
    out = [(0, XH), (0, ymu), (cx, -OV), (w, ymu), (w, XH)]
    dl = (cx, -OV - ymu); l = math.hypot(*dl); nl = (-dl[1]/l, dl[0]/l)
    a_ = inter((nl[0]*Dl, ymu + nl[1]*Dl), dl, (SL, 0), (0, 1))
    b_ = inter((nl[0]*Dl, ymu + nl[1]*Dl), dl, (cx, 0), (0, 1))
    body = Dif(P(out), P([(SL, XH + 10), a_, b_, (w - a_[0], a_[1]), (w - SL, XH + 10)]))
    body = Dif(body, P([(-1, XH - C*0.92), (SL, XH), (-1, XH + 50)]))
    body = X(body, left_of((w - WL, XH), (w - WL/2, -OV)))
    add('u', U(body, lw(w - WL, XH)), w, 45, 40)
    # r
    w = 330
    add('r', U(lw(0, XH), bar(0, w, XH - BTl, BTl, right='D')), w, 40, 10)
    # s : S carré en petit
    w = 440; ym = XH*MID - TMl/2 + 15
    add('s', U(bar(0, w, XH - BTl, BTl, right='D'), lst(0, ym, XH), bar(0, w, ym, TMl),
               lst(w - SL, 0, ym + TMl), bar(0, w, 0, BBl)), w, 30, 30)

    DE = -230                                  # bas des descendantes
    def lwd(x, y1, y0=-OV, tipx=None):         # coin qui descend jusqu'à y0
        return P([(x, y1), (x + WL, y1), (x + WL/2 if tipx is None else tipx, y0)])
    def right_of(p1, p2):
        dx, dy = p2[0] - p1[0], p2[1] - p1[1]
        return P([(p1[0] - dx*20, p1[1] - dy*20), (p1[0] + dx*20, p1[1] + dy*20), (5000, p1[1] + dy*20), (5000, p1[1] - dy*20)])
    # b, p : coin à gauche + losange
    w = 480; pts, ts = lkite(w); o_ = ring(pts, ts)
    for ch, top, bot in (('b', H, -OV), ('p', XH, DE)):
        st = lwd(0, top, bot)
        k = X(o_, right_of((0, top), (WL/2, bot)))
        add(ch, U(k, st), w, 40, 15)
    # q : losange + coin droit qui descend
    k = X(o_, left_of((w, XH), (w - WL/2, DE)))
    add('q', U(k, lwd(w - WL, XH, DE)), w, 15, 40)
    # g : losange + coin en biais qui descend vers la gauche
    gl = P([(w - WL, XH), (w, XH), (w*0.28, DE)])
    k = X(o_, left_of((w, XH), (w*0.28, DE)))
    add('g', U(k, gl), w, 15, 30)
    # c : losange avec une bouche à droite
    w = 480; pts, ts = lkite(w); ym = pts[1][1]
    ct = hole(pts, ts).bounds[3]
    add('c', Dif(ring(pts, ts), box(w/2, ym - 50, w + 1e3, min(ct, ym + 100))), w, 15, 0)
    # n, h, m : coins reliés par une barre en haut (comme le r)
    def arches(xs, w, first_top):
        parts = [lwd(xs[0], first_top), bar(0, w, XH - BTl, BTl)]
        for x in xs[1:]: parts.append(lwd(x, XH))
        return U(*parts)
    w = 470; add('n', arches([0, w - WL], w, XH), w, 40, 40)
    add('h', arches([0, w - WL], w, H), w, 40, 40)
    w = 760; add('m', arches([0, (w - WL)/2, w - WL], w, XH), w, 40, 40)
    # j : point + coin qui descend, pointe à gauche
    jw = WL
    dot = dia(jw/2, XH + 90 + 105*gg, 85*gg, 105*gg)
    add('j', U(P([(0, XH), (jw, XH), (jw*0.15, DE)]), dot), jw, 30, 40)
    # k : coin + bras en haut + jambe en coin
    w = 470; wa = 190*WF; y0 = XH*0.30
    xs_ = WL - (WL/2)*(H - y0)/(H + OV) - 5          # bord droit du coin à cette hauteur
    d = (w - xs_, XH - y0)
    top_s = inter((w - wa, XH), d, (xs_, 0), (0, 1))
    arm = P([(xs_, y0), (w, XH), (w - wa, XH), top_s])
    leg = P([(xs_ - 10, y0 + 30), (xs_ + 170*ww(), y0 + 30 + 170*ww()*d[1]/d[0]), (w - 20, -OV)])
    add('k', U(lwd(0, H), arm, leg), w, 40, 0)
    # v : V à hauteur des minuscules
    def vpoly(w, ox=0, xf=None):
        cx = w/2 + ox; xf = 140*WF if xf is None else xf; hf = xf*K
        yv = -OV + 0.40*(XH + OV)*WF
        out = P([(cx, -OV), (ox + w, XH - hf), (ox + w - xf, XH), (ox + xf, XH), (ox, XH - hf)])
        return Dif(out, P([(cx, yv), (ox + w - xf, XH), (ox + xf, XH)]))
    add('v', vpoly(480), 480, 12, 12)
    # w : deux v soudés
    vw = 400; xf = 105*WF; ox = vw - xf
    fill = P([(vw - xf, XH), (vw, XH), (vw - xf/2, XH - 200*WF)])
    add('w', U(vpoly(vw, 0, xf), vpoly(vw, ox, xf), fill), ox + vw, 12, 12)
    # x : deux coins en diagonale qui se croisent (comme deux i penchés)
    w = 480
    add('x', U(P([(0, XH), (WL, XH), (w - 30, -OV)]), P([(w - WL, XH), (w, XH), (30, -OV)])), w, 15, 15)
    # y : coin court à gauche qui rejoint un long coin à droite qui descend
    w = 480; cx = w/2
    add('y', U(P([(0, XH), (WL, XH), (cx + 20, 10)]), P([(w - WL, XH), (w, XH), (cx - 110, DE)])), w, 15, 15)
    # z
    w = 440
    add('z', U(bar(0, w, XH - BTl, BTl), bar(0, w, 0, BBl),
               P([(w - 250*WF, XH), (w, XH), (w, XH - BTl), (170*WF, BBl), (0, BBl)])), w, 20, 20)


def build_lower_accents():
    up = XH + 90 - ACC_Y              # les accents descendent au-dessus des minuscules
    gg = g(); iw = G['i'][1]
    add('ı', P([(0, XH), (iw, XH), (iw/2, -OV)]), iw, 40, 40)
    table = {
        'à': ('a', 'grave'), 'â': ('a', 'circ'), 'ä': ('a', 'dier'), 'á': ('a', 'acute'),
        'é': ('e', 'acute'), 'è': ('e', 'grave'), 'ê': ('e', 'circ'), 'ë': ('e', 'dier'),
        'í': ('ı', 'acute'), 'î': ('ı', 'circ'), 'ï': ('ı', 'dier'), 'ñ': ('n', 'tilde'),
        'ó': ('o', 'acute'), 'ô': ('o', 'circ'), 'ö': ('o', 'dier'),
        'ú': ('u', 'acute'), 'ù': ('u', 'grave'), 'û': ('u', 'circ'), 'ü': ('u', 'dier'),
        'ÿ': ('y', 'dier'), 'ç': ('c', 'cedilla'),
    }
    for new, (b, m) in table.items():
        p, w, l, r = G[b]
        mk = MARKS[m]()
        mk = mv(mk, w/2, 0 if m == 'cedilla' else up)
        x0, _, x1, _ = mk.bounds
        add(new, U(p, mk), w, max(l, -x0 + 25), max(r, x1 - w + 25))
    # œ, æ : deux losanges qui se chevauchent
    op, ow = G['o'][0], G['o'][1]; ep, ew_ = G['e'][0], G['e'][1]
    add('œ', U(op, mv(ep, ow*0.62)), ow*0.62 + ew_, 15, 10)
    ap_, aw_ = G['a'][0], G['a'][1]
    add('æ', U(ap_, mv(ep, aw_ - 40)), aw_ - 40 + ew_, 15, 10)     # le e s'accroche au coin du a
    # ß : coin haut, barre, diagonale, ventre ouvert contre le coin
    w = 470; WLs = 200*ww()*0.92; BTl = BT*0.52; BBl = BB*0.52; TMl = (BTl + BBl)/2
    yt = XH*0.72; cxb = w*0.48
    bel = ring([(0, 0), (0, yt), (cxb, yt), (w, yt/2), (cxb, 0)], [S*0.92, TMl, TT*0.8, TB*0.8, BBl])
    bel = Dif(bel, box(-1, BBl, S*0.92 + 1, yt - TMl))
    # rien ne dépasse à gauche du coin
    dx, dy = WLs/2, -OV - H
    bel = X(bel, P([(-dx*20, H - dy*20), (dx*20, H + dy*20), (5000, H + dy*20), (5000, H - dy*20)]))
    dw = 170*WF
    dg = P([(w - 20 - dw, H - 1), (w - 20, H - 1), (w*0.5, yt - 1), (w*0.5 - dw, yt - 1)])
    add('ß', U(P([(0, H), (WLs, H), (WLs/2, -OV)]), bar(0, w - 20, H - BTl, BTl), dg, bel), w, 40, 15)

# ---------------------------------------------------------------- tout
def set_weight(f, wx=1.0):
    G.clear(); ORDER.clear()
    _thick(f/wx)
    build_letters(); build_accents(); build_specials(); build_digits()
    build_lower(); build_lower_accents()
    build_ext()                      # GF Latin Core : accents, lettres barrées, symboles, accents combinants
    add(' ', Path(), 220, 0, 0)
    if wx != 1.0:
        for ch in list(G):
            p, w, l, r = G[ch]
            G[ch] = (tf(p, (wx, 0, 0, 1, 0, 0)), w*wx, l*wx, r*wx)

WEIGHTS = [  # nom (les centaines en klingon : vatlh = cent), poids, épaisseur, élargissement
    ("wa'vatlh", 100, 0.18, 1.0), ("cha'vatlh", 200, 0.30, 1.0), ('wejvatlh', 300, 0.43, 1.0),
    ('loSvatlh', 400, 0.56, 1.0), ('vaghvatlh', 500, 0.68, 1.0), ('javvatlh', 600, 0.80, 1.0),
    ('Sochvatlh', 700, 0.90, 1.0), ('chorghvatlh', 800, 1.00, 1.0), ('Hutvatlh', 900, 1.18, 1.12),
]

# ---------------------------------------------------------------- rendu
def contours(path):
    out = []
    for c in path.contours:
        pts = []
        for verb, ps in c.segments:
            if verb in ('moveTo', 'lineTo'): pts.append(ps[-1])
            elif verb != 'closePath': pts.extend(ps)
        out.append(pts)
    return out

def render(text, out, px_h=220, margin=60, track=0, ytop=H+OV, ybot=-OV):
    from PIL import Image, ImageDraw, ImageChops
    sc = px_h / H; SS = 4
    adv = sum(G[c][1] + G[c][2] + G[c][3] + track for c in text)
    Wpx = int(adv*sc) + 2*margin; Hpx = int((ytop-ybot)*sc) + 2*margin
    img = Image.new('1', (Wpx*SS, Hpx*SS), 0)
    x = margin/sc
    for c in text:
        p, w, l, r = G[c]; x += l
        for pts in contours(p):
            m = Image.new('1', img.size, 0)
            ImageDraw.Draw(m).polygon([((x+px)*sc*SS, (margin + (ytop - py)*sc)*SS) for px, py in pts], fill=1)
            img = ImageChops.logical_xor(img, m)
        x += w + r + track
    ImageChops.invert(img.convert('L')).resize((Wpx, Hpx), Image.LANCZOS).save(out)

# ---------------------------------------------------------------- GF Latin Core (version 1.1)
# Accents en plus : macron, caron, brève, point, rond, double aigu, ogonek, virgules (même langage : coins, losanges, pointes)
def m_macron():
    t = 15 + 100*WF; y0 = ACC_Y + 60
    return P([(-200, y0 + t/2), (-150, y0 + t), (150, y0 + t), (200, y0 + t/2), (150, y0), (-150, y0)])
def m_caron():
    return tf(m_circ(), (1, 0, 0, -1, 0, 2*ACC_Y + 205))
def m_breve():
    t = 15 + 100*WF; top = ACC_Y + 200; k = 85/200; dx = t*1.087
    outer = P([(-185, top), (-100, ACC_Y), (100, ACC_Y), (185, top)])
    yi = ACC_Y + t; yt = top + 80
    inner = P([(-100 - k*t + dx, yi), (100 + k*t - dx, yi), (100 + k*(yt - ACC_Y) - dx, yt), (-100 - k*(yt - ACC_Y) + dx, yt)])
    return Dif(outer, inner)
def m_dot():
    hw, hh = 78*g(), 95*g()
    return dia(0, ACC_Y + hh, hw, hh)
def m_ring():
    h = 230; hw = 130
    r, _ = kring(0, ACC_Y, ACC_Y + h, hw, ACC_Y + h*0.42, 12 + 70*WF, 9 + 48*WF)
    return r
def m_dacute():
    a = tf(m_acute(), (0.72, 0, 0, 1, 0, 0))
    return U(mv(a, -95), mv(a, 95))
def m_ogonek():                       # placé au pied droit (voir compose_x)
    return P([(-55*g(), 40), (55*g(), 40), (75, -220)])
def m_commabelow():
    gg = g(); dw = 170*gg
    return P([(-dw/2, -45), (dw/2, -45), (-0.30*dw, -265)])
def m_commaabove():                   # pour ģ : virgule retournée au-dessus
    gg = g(); dw = 170*gg
    return P([(dw/2, ACC_Y + 210), (-dw/2, ACC_Y + 210), (0.25*dw, ACC_Y - 10)])
MARKS.update({'macron': m_macron, 'caron': m_caron, 'breve': m_breve, 'dot': m_dot, 'ring': m_ring,
              'dacute': m_dacute, 'ogonek': m_ogonek, 'commabelow': m_commabelow, 'commaabove': m_commaabove})
BELOW = {'cedilla', 'ogonek', 'commabelow'}

def foot_right(p):
    """x du pied droit : le point d'encre le plus à droite tout en bas"""
    lows = [(x, y) for c in contours(p) for (x, y) in c if y < 40]
    return max(x for x, _ in lows) if lows else None

def compose2(new, base, marks, lower=False):
    p, w, l, r = G[base]; out = p
    for m in marks:
        mk = MARKS[m]()
        dy = 0
        if m == 'ogonek' and base in ('I', 'i'):     # base en pointe : la queue part du milieu, un peu plus haut
            x = w/2 + 10; dy = 70
        elif m == 'ogonek':
            x = (foot_right(p) or w) - 60*g()
        else:
            x = w/2
        if lower and m not in BELOW: dy = XH + 90 - ACC_Y
        mk = mv(mk, x, dy)
        out = U(out, mk)
    x0, _, x1, _ = out.bounds
    add(new, out, w, max(l, -x0 + 25), max(r, x1 - w + 25))

# ---------------------------------------------------------------- GF Latin Core : le reste
ACCENTED = {
 'Ã': ('A', ['tilde']), 'Å': ('A', ['ring']), 'Ì': ('I', ['grave']), 'Ò': ('O', ['grave']), 'Õ': ('O', ['tilde']), 'Ý': ('Y', ['acute']),
 'Ā': ('A', ['macron']), 'Ă': ('A', ['breve']), 'Ą': ('A', ['ogonek']), 'Ć': ('C', ['acute']), 'Ċ': ('C', ['dot']), 'Č': ('C', ['caron']),
 'Ď': ('D', ['caron']), 'Ē': ('E', ['macron']), 'Ė': ('E', ['dot']), 'Ę': ('E', ['ogonek']), 'Ě': ('E', ['caron']),
 'Ğ': ('G', ['breve']), 'Ġ': ('G', ['dot']), 'Ģ': ('G', ['commabelow']), 'Ī': ('I', ['macron']), 'Į': ('I', ['ogonek']), 'İ': ('I', ['dot']),
 'Ķ': ('K', ['commabelow']), 'Ĺ': ('L', ['acute']), 'Ļ': ('L', ['commabelow']), 'Ń': ('N', ['acute']), 'Ņ': ('N', ['commabelow']),
 'Ň': ('N', ['caron']), 'Ő': ('O', ['dacute']), 'Ŕ': ('R', ['acute']), 'Ř': ('R', ['caron']), 'Ś': ('S', ['acute']), 'Ş': ('S', ['cedilla']),
 'Š': ('S', ['caron']), 'Ť': ('T', ['caron']), 'Ū': ('U', ['macron']), 'Ů': ('U', ['ring']), 'Ű': ('U', ['dacute']), 'Ų': ('U', ['ogonek']),
 'Ŵ': ('W', ['circ']), 'Ŷ': ('Y', ['circ']), 'Ź': ('Z', ['acute']), 'Ż': ('Z', ['dot']), 'Ž': ('Z', ['caron']), 'Ș': ('S', ['commabelow']),
 'Ț': ('T', ['commabelow']), 'Ẁ': ('W', ['grave']), 'Ẃ': ('W', ['acute']), 'Ẅ': ('W', ['dier']), 'Ỳ': ('Y', ['grave']),
}
ACCENTED_LOW = {
 'ã': ('a', ['tilde']), 'å': ('a', ['ring']), 'ì': ('ı', ['grave']), 'ò': ('o', ['grave']), 'õ': ('o', ['tilde']), 'ý': ('y', ['acute']),
 'ā': ('a', ['macron']), 'ă': ('a', ['breve']), 'ą': ('a', ['ogonek']), 'ć': ('c', ['acute']), 'ċ': ('c', ['dot']), 'č': ('c', ['caron']),
 'ē': ('e', ['macron']), 'ė': ('e', ['dot']), 'ę': ('e', ['ogonek']), 'ě': ('e', ['caron']), 'ğ': ('g', ['breve']), 'ġ': ('g', ['dot']),
 'ģ': ('g', ['commaabove']), 'ī': ('ı', ['macron']), 'į': ('i', ['ogonek']), 'ķ': ('k', ['commabelow']), 'ļ': ('l', ['commabelow']),
 'ń': ('n', ['acute']), 'ņ': ('n', ['commabelow']), 'ň': ('n', ['caron']), 'ő': ('o', ['dacute']), 'ŕ': ('r', ['acute']), 'ř': ('r', ['caron']),
 'ś': ('s', ['acute']), 'ş': ('s', ['cedilla']), 'š': ('s', ['caron']), 'ū': ('u', ['macron']), 'ů': ('u', ['ring']), 'ű': ('u', ['dacute']),
 'ų': ('u', ['ogonek']), 'ŵ': ('w', ['circ']), 'ŷ': ('y', ['circ']), 'ź': ('z', ['acute']), 'ż': ('z', ['dot']), 'ž': ('z', ['caron']),
 'ș': ('s', ['commabelow']), 'ț': ('t', ['commabelow']), 'ẁ': ('w', ['grave']), 'ẃ': ('w', ['acute']), 'ẅ': ('w', ['dier']), 'ỳ': ('y', ['grave']),
}

def top_x(p, ymin):
    """milieu de l'encre au-dessus de ymin (le haut d'un fût)"""
    xs = [x for c in contours(p) for (x, y) in c if y >= ymin]
    return (min(xs) + max(xs)) / 2

def stroke_bar(x0, x1, yc, t):           # barre aux bouts en pointe, comme le macron
    k = min(t/2, (x1 - x0)/4)
    return P([(x0, yc), (x0 + k, yc + t/2), (x1 - k, yc + t/2), (x1, yc), (x1 - k, yc - t/2), (x0 + k, yc - t/2)])

def caronvert():                      # caron en apostrophe pour ď ľ ť Ľ
    qw = 150*(0.25 + 0.75*WF)*0.9
    return wedge(0, qw, H, (0.13*qw, H - 270)), qw

def build_ext():
    gg = g(); up = XH + 90 - ACC_Y
    for new, (b, m) in ACCENTED.items(): compose2(new, b, m)
    for new, (b, m) in ACCENTED_LOW.items(): compose2(new, b, m, lower=True)
    # ĺ : l'aigu au-dessus du fût
    p, w, l, r = G['l']; mk = mv(MARKS['acute'](), w/2 + 40)
    add('ĺ', U(p, mk), w, l, max(r, mk.bounds[2] - w + 25))
    # ď ľ ť Ľ : caron en apostrophe à droite du fût
    cv, qw = caronvert()
    for new, base, xx, top in (('ď', 'd', None, H), ('ľ', 'l', None, H), ('ť', 't', None, H - 40), ('Ľ', 'L', S + 70, H)):
        p, w, l, r = G[base]
        if xx is None:
            xs = [x for c in contours(p) for (x, y) in c if y >= top - 60]
            xx = max(xs) + 45
        m = mv(cv, xx, top - H)
        add(new, U(p, m), w, l, max(r, xx + qw - w + 30))
    # lettres barrées
    tB = TM*0.8; tl = TM*0.52*1.1
    p, w, l, r = G['D']; dbar = stroke_bar(-90, S + 150, H*MID, tB)
    add('Ð', U(p, dbar), w, l + 90, r); add('Đ', U(p, dbar), w, l + 90, r)
    p, w, l, r = G['d']; xs = top_x(p, H - 5); yb = (XH + H)/2 + 30
    add('đ', U(p, stroke_bar(xs - 150, xs + 110, yb, tl)), w, l, max(r, xs + 110 - w + 30))
    p, w, l, r = G['H']; add('Ħ', U(p, stroke_bar(-70, w + 70, H*0.80, tB*0.85)), w, l + 70, r + 70)
    p, w, l, r = G['h']; xs = top_x(p, H - 5)
    add('ħ', U(p, stroke_bar(xs - 130, xs + 150, yb, tl)), w, l + 40, r)
    sw = 15 + 95*WF
    p, w, l, r = G['L']; add('Ł', U(p, poly_stroke([(-70, H*0.30), (S + 170, H*0.58)], sw)), w, l + 70, r)
    p, w, l, r = G['l']; add('ł', U(p, poly_stroke([(w/2 - 150, H*0.40), (w/2 + 150, H*0.64)], sw*0.9)), w, l + 60, r + 60)
    p, w, l, r = G['O']; add('Ø', U(p, poly_stroke([(-40, -70), (w + 40, H + 70)], sw)), w, l + 30, r + 30)
    p, w, l, r = G['o']; add('ø', U(p, poly_stroke([(-35, -60), (w + 35, XH + 80)], sw*0.9)), w, l + 25, r + 25)
    # Þ þ ð
    p, w, l, r = G['P']
    add('Þ', U(stem(0, 0, H), X(mv(p, 0, -150), box(S - 1, -200, 3000, H))), w, l, r)
    pb, wb, lb, rb = G['b']; pp = G['p'][0]
    add('þ', U(pb, pp), wb, lb, rb)
    po, wo, lo_, ro = G['o']; sl = S*0.92*0.85
    eth = U(po, poly_stroke([(wo*0.70, XH*0.62), (wo*0.30, H)], sl), poly_stroke([(wo*0.22, H*0.80), (wo*0.78, H*0.92)], tl))
    add('ð', eth, wo, lo_, ro)
    # ȷ : j sans point
    jw = G['j'][1]; add('ȷ', P([(0, XH), (jw, XH), (jw*0.15, DE)]), jw, 30, 40)
    # ª º
    sa = 0.6; yo = H*0.40
    for new, base in (('ª', 'a'), ('º', 'o')):
        p, w, l, r = G[base]
        small = tf(p, (sa, 0, 0, sa, 0, yo))
        add(new, U(small, stroke_bar(0, w*sa, yo - 70, 12 + 60*WF)), w*sa, 40, 40)
    # ---------------------------------------------------------------- symboles
    pc = 300
    def chev(x0, cy, h, wd, d_in):
        c = d_in*(h/2)/wd
        return P([(x0, cy), (x0 + wd, cy + h/2), (x0 + wd, cy + h/2 - c), (x0 + d_in, cy), (x0 + wd, cy - h/2 + c), (x0 + wd, cy - h/2)])
    lt = chev(0, pc, 460, 400, 40 + 130*WF)
    add('<', lt, 400, 40, 40); add('>', tf(lt, (-1, 0, 0, 1, 400, 0)), 400, 40, 40)
    add('^', tf(m_circ(), (1.3, 0, 0, 1.5, 240, 390 - 1.5*ACC_Y)), 480, 30, 30)
    tv = 15 + 110*WF; add('|', box(0, -160, tv, H + 90), tv, 70, 70)
    sp = poly_stroke([(-230, pc - 80), (-80, pc + 65), (80, pc - 65), (230, pc + 80)], 10 + 110*WF, 4)
    add('~', mv(X(sp, box(-200, pc - 200, 200, pc + 200)), 200), 400, 40, 40)
    p, w, l, r = G['c']; tc = 12 + 75*WF; cx = 0.45*w
    add('¢', U(p, box(cx - tc/2, -110, cx + tc/2, XH + 130)), w, l, max(r, 20))
    p, w, l, r = G['Y']; cy_ = w/2; tbY = TM*0.6
    add('¥', U(p, stroke_bar(cy_ - 190, cy_ + 190, 130, tbY), stroke_bar(cy_ - 190, cy_ + 190, 290, tbY)), w, l, r)
    plus = G['+'][0]; c45 = math.sqrt(0.5)
    rot = tf(mv(plus, -220, -pc), (c45, c45, -c45, c45, 0, 0))
    add('×', mv(rot, 220, pc), 440, 40, 40)
    minus = box(0, pc - 60*WF, 440, pc + 60*WF)
    add('−', minus, 440, 40, 40)
    dd = 70*gg; dh = 85*gg
    add('÷', U(minus, dia(220, pc + 60*WF + 50 + dh, dd, dh), dia(220, pc - 60*WF - 50 - dh, dd, dh)), 440, 40, 40)
    Sp = G['S'][0]; ss = 0.6; sw_S = G['S'][1]*ss
    add('§', U(tf(Sp, (ss, 0, 0, ss, 0, H*0.40)), tf(Sp, (ss, 0, 0, ss, 0, -H*0.12))), sw_S, 40, 40)
    t1 = S*0.75; t2 = S*0.55; x1 = 210; x2 = x1 + t1 + 70
    bowl = P([(x1 + 1, H), (x1 + 1, H*0.38), (0, H*0.69), (60, H)])
    add('¶', U(box(x1, -160, x1 + t1, H), box(x2, -160, x2 + t2, H), box(x1, H - BT*0.7, x2 + t2, H), bowl), x2 + t2, 40, 40)
    tbk = S*0.85; tbb = TM*0.8; wb_ = 210
    br = U(box(0, -160, tbk, H + 90), box(0, H + 90 - tbb, wb_, H + 90), box(0, -160, wb_, -160 + tbb))
    add('[', br, wb_, 50, 20); add(']', tf(br, (-1, 0, 0, 1, wb_, 0)), wb_, 20, 50)
    sl_ = G['/'][0]; add('\\', tf(sl_, (-1, 0, 0, 1, 440, 0)), 440, 10, 10)
    add('_', box(0, -160, 500, -160 + TM*0.7), 500, 0, 0)
    top, bot = H + 90, -160; cyb = (top + bot)/2; wp = 260; thb = 15 + 125*WF
    brace = poly_stroke([(wp, top - thb/2), (wp*0.45, top - thb/2 - 20), (wp*0.40, cyb + 80), (0, cyb), (wp*0.40, cyb - 80),
                         (wp*0.45, bot + thb/2 + 20), (wp, bot + thb/2)], thb, 4)
    brace = X(brace, box(-100, bot, wp, top))
    add('{', brace, wp, 40, 20); add('}', tf(brace, (-1, 0, 0, 1, wp, 0)), wp, 20, 40)
    dhw, dhh = 85*gg, 105*gg
    add('·', dia(dhw, H*MID, dhw, dhh), 2*dhw, 40, 40)
    p, w, l, r = G[','];  add('‚', p, w, l, r)
    add('•', dia(150*gg, H*MID, 150*gg, 175*gg), 300*gg, 50, 50)
    # ¦ † (jeu de caractères Velvetyne)
    add('¦', U(box(0, -160, tv, 230), box(0, 370, tv, H + 90)), tv, 70, 70)
    wd = 420; cxd = wd/2; hwd = 75*ww()
    add('†', U(P([(cxd - hwd, H + 40), (cxd + hwd, H + 40), (cxd, -160)]), stroke_bar(0, wd, H*0.66, TM*0.75)), wd, 30, 30)
    # monogramme VTF (demandé par Velvetyne, version pour eux seulement) : le V, puis le T et le F qui partagent la barre du haut
    Vp, Vw = G['V'][0], G['V'][1]; Tp, Tw = G['T'][0], G['T'][1]; Fp, Fw = G['F'][0], G['F'][1]
    xT = Vw + 30; xF = xT + Tw/2 + 140
    Wm = xF + Fw
    if os.environ.get('VELVETYNE'):          # seulement dans la version envoyée à Velvetyne
        add('VTF', U(Vp, mv(Tp, xT), mv(Fp, xF), bar(xT, xF + 10, H - BT, BT)), Wm, 40, 40)
    # ---------------------------------------------------------------- accents seuls (avec chasse) et combinants
    SPACING = {'`': 'grave', '¨': 'dier', '¯': 'macron', '´': 'acute', '¸': 'cedilla', '˘': 'breve', '˙': 'dot', '˚': 'ring',
               '˛': 'ogonek', '˜': 'tilde', '˝': 'dacute', 'ˆ': 'circ', 'ˇ': 'caron'}
    for ch, m in SPACING.items():
        mk = MARKS[m]()
        if m not in BELOW: mk = mv(mk, 0, up)
        x0, _, x1, _ = mk.bounds
        add(ch, mv(mk, -x0), x1 - x0, 40, 40)
    for nm, m in (('acute.case', 'acute'), ('grave.case', 'grave'), ('circumflex.case', 'circ'), ('tilde.case', 'tilde'),
                  ('dieresis.case', 'dier'), ('ring.case', 'ring')):          # accents seuls à hauteur de capitale (jeu Velvetyne)
        mk = MARKS[m](); x0, _, x1, _ = mk.bounds
        add(nm, mv(mk, -x0), x1 - x0, 40, 40)
    COMB = {'̀': 'grave', '́': 'acute', '̂': 'circ', '̃': 'tilde', '̄': 'macron', '̆': 'breve',
            '̇': 'dot', '̈': 'dier', '̊': 'ring', '̋': 'dacute', '̌': 'caron', '̦': 'commabelow',
            '̧': 'cedilla', '̨': 'ogonek'}
    for ch, m in COMB.items():
        mk = MARKS[m]()
        if m not in BELOW: mk = mv(mk, 0, up)
        add(ch, mk, 0, 0, 0)


set_weight(1.0)
