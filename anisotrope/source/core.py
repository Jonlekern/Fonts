# Serif de lecture : squelette de plume vintage (axes penchés, têtes en biais à gauche, lettres asymétriques)
# + peau du futur (contraste faible, empattements en coin coupés net). Pensée pour lire avec une dyslexie :
# aucune lettre n'est le miroir d'une autre, contreformes ouvertes et constantes, espacement large.
# Chaque graisse est fabriquée dans son propre processus : la graisse est lue dans l'environnement (W) à l'import.
import math, os
import pathops
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.recordingPen import RecordingPen

FAMILY = 'ANISOTROPE'
PSFAM = 'ANISOTROPE'
SLUG = 'anisotrope'
UPM = 1000
XH, CAP, ASC, DESC = 500, 700, 750, -230
OV = 10

# graisses : (usWeightClass, nom provisoire, épaisseur du fût)
WEIGHTS = [(300, '030', 60), (400, '040', 84), (500, '050', 106), (700, '070', 136), (900, '090', 172)]
ST = int(os.environ.get('W', '84'))          # fût vertical
TH = round(0.68 * ST + 2)                    # partie fine (contraste faible)
W = round(26 + 0.24 * ST)                    # avancée d'un empattement
SH = round(34 + 0.31 * ST)                   # hauteur d'un empattement en coin
NW = round(290 + 1.55 * ST)                  # largeur d'un n : la contreforme se serre un peu en gras, sans fondre
BR = round(165 + 0.85 * ST)                  # demi-largeur d'un o
S_STEM = 72 + ST / 6                         # approche d'un fût nu
ROT = 14                                     # axe penché des ronds (plume)
K_ = 0.5523

# ---------- géométrie ----------
def P(): return pathops.Path()

def poly(pts):
    p = P(); pen = p.getPen(); pen.moveTo(pts[0])
    for q in pts[1:]: pen.lineTo(q)
    pen.closePath(); return p

def rect(x0, y0, x1, y1): return poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])

def ellipse(cx, cy, rx, ry, rot=0.0):
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    T = lambda x, y: (cx + x * c - y * s, cy + x * s + y * c)
    p = P(); pen = p.getPen(); pen.moveTo(T(rx, 0))
    pen.curveTo(T(rx, K_ * ry), T(K_ * rx, ry), T(0, ry))
    pen.curveTo(T(-K_ * rx, ry), T(-rx, K_ * ry), T(-rx, 0))
    pen.curveTo(T(-rx, -K_ * ry), T(-K_ * rx, -ry), T(0, -ry))
    pen.curveTo(T(K_ * rx, -ry), T(rx, -K_ * ry), T(rx, 0))
    pen.closePath(); return p

def U(*ps):
    out = P()
    for p in ps:
        if p is not None: out = pathops.op(out, p, pathops.PathOp.UNION)
    return out
def D(a, *bs):
    for b in bs: a = pathops.op(a, b, pathops.PathOp.DIFFERENCE)
    return a
def I(a, b): return pathops.op(a, b, pathops.PathOp.INTERSECTION)

def xf(p, m):
    out = P(); p.draw(TransformPen(out.getPen(), m)); return out
def mv(p, dx, dy=0): return xf(p, (1, 0, 0, 1, dx, dy))
def flipx(p, ax):  return xf(p, (-1, 0, 0, 1, 2 * ax, 0))
def flipy(p, ay):  return xf(p, (1, 0, 0, -1, 0, 2 * ay))
def rot(p, deg, cx, cy):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return xf(p, (c, s, -s, c, cx - c * cx + s * cy, cy - s * cx - c * cy))

def pie(cx, cy, a0, a1, R=3000):
    """part de tarte de a0 à a1 degrés (sens direct)"""
    if a1 < a0: a1 += 360
    n = max(2, int((a1 - a0) / 10) + 1)
    pts = [(cx, cy)] + [(cx + R * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
                         cy + R * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
    return poly(pts)

def bar(x0, y0, x1, y1, t):
    """trait droit d'épaisseur t (mesurée à l'horizontale) entre deux points"""
    return poly([(x0 - t / 2, y0), (x0 + t / 2, y0), (x1 + t / 2, y1), (x1 - t / 2, y1)])

# ---------- pièces ----------
def stem(x, y0, y1, w=None): return rect(x, y0, x + (w or ST), y1)

def ring(cx, cy, rx, ry, sx=None, sy=None, r=ROT, dx=0, dy=0):
    """rond de plume : l'axe penche (vintage), contraste faible (futur)"""
    sx = ST * 0.98 if sx is None else sx; sy = TH if sy is None else sy
    return D(ellipse(cx, cy, rx, ry), ellipse(cx + dx, cy + dy, rx - sx, ry - sy, r))

def bowl(cx):
    """bol d'un o, b, d, p, q"""
    return ring(cx, XH / 2, BR, XH / 2 + OV)

def arch_y(x0, x1, top, x, h=None):
    """hauteur du bord extérieur de l'arche à l'abscisse x"""
    h = h or round(0.46 * XH); cx = (x0 + x1) / 2; rx = (x1 - x0) / 2
    return top - h + (h + OV) * math.sqrt(max(0.0, 1 - ((x - cx) / rx) ** 2))

def arch(x0, x1, top, h=None):
    """arche du n : rejoint le fût de droite à pleine épaisseur, naît en encoche du fût de gauche"""
    h = h or round(0.46 * XH)
    cx = (x0 + x1) / 2; rx = (x1 - x0) / 2
    a = D(ellipse(cx, top - h, rx, h + OV), ellipse(cx, top - h, rx - ST, h + OV - TH))
    return I(a, rect(x0 + ST * 0.5, top - h - 2, x1 + 5, top + OV + 5))

def cup(x0, x1, bot=0, h=None):
    """bas du u (une arche à l'envers)"""
    h = h or round(0.46 * XH)
    cx = (x0 + x1) / 2; rx = (x1 - x0) / 2
    a = D(ellipse(cx, bot + h, rx, h + OV), ellipse(cx, bot + h, rx - ST, h + OV - TH))
    return I(a, rect(x0 - 5, bot - OV - 5, x1 + 5, bot + h + 2))      # la cuvette garde tout son mur droit : il se confond avec le fût

def foot(x0, x1, left=True, right=True, y=0):
    """empattement en coin : large en bas, coupé net, rejoint le fût en biais"""
    l = W if left else 0; r = W if right else 0; e = max(10, round(SH * 0.2))
    return poly([(x0 - l, y), (x1 + r, y), (x1 + r, y + e), (x1, y + SH), (x0, y + SH), (x0 - l, y + e)])

def cap_foot(x0, x1, left=True, right=True, y=0, top=False):
    """empattement des capitales (et dessus des barres) : même coin, retournable"""
    p = foot(x0, x1, left, right, 0)
    if top: p = flipy(p, 0)
    return mv(p, 0, y)

def pbar(x0, y0, x1, y1, w):
    """trait droit de largeur w (mesurée perpendiculairement), bouts coupés d'équerre : aucune pointe"""
    dx, dy = x1 - x0, y1 - y0; L = math.hypot(dx, dy); nx, ny = -dy / L * w / 2, dx / L * w / 2
    return poly([(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)])

def stroke(pts, w):
    """ligne brisée de largeur w : angles en onglet, bouts coupés d'équerre"""
    n = len(pts); L, R = [], []
    def off(p, q, s):
        dx, dy = q[0] - p[0], q[1] - p[1]; l = math.hypot(dx, dy); nx, ny = -dy / l * s, dx / l * s
        return (p[0] + nx, p[1] + ny), (q[0] + nx, q[1] + ny)
    def meet(a, b, c, d):
        x1, y1 = a; x2, y2 = b; x3, y3 = c; x4, y4 = d
        den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if abs(den) < 1e-9: return b
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
    for side, out_ in ((w / 2, L), (-w / 2, R)):
        segs = [off(pts[i], pts[i + 1], side) for i in range(n - 1)]
        out_.append(segs[0][0])
        for i in range(n - 2): out_.append(meet(*segs[i], *segs[i + 1]))
        out_.append(segs[-1][1])
    return poly(L + R[::-1])

def ncut(cx, cy, rx, ry, t, side, lim, L=4000):
    """zone à retirer pour finir un rond (ellipse rx, ry) par une coupe d'équerre au paramètre t (degrés) :
    la coupe suit la normale de l'ellipse. side=+1 garde la partie qui continue dans le sens direct, -1 l'autre.
    lim : angle (polaire) jusqu'où la zone retirée s'étend de l'autre côté de la coupe."""
    tr = math.radians(t); c, s = math.cos(tr), math.sin(tr)
    P = (cx + rx * c, cy + ry * s)
    T = (-rx * s, ry * c); lt = math.hypot(*T); T = (T[0] / lt * side, T[1] / lt * side)
    n = (ry * c, rx * s); ln = math.hypot(*n); n = (n[0] / ln, n[1] / ln)
    cutp = poly([(P[0] + L * n[0], P[1] + L * n[1]), (P[0] - L * n[0], P[1] - L * n[1]),
                 (P[0] - L * n[0] - L * T[0], P[1] - L * n[1] - L * T[1]), (P[0] + L * n[0] - L * T[0], P[1] + L * n[1] - L * T[1])])
    pol = math.degrees(math.atan2(ry * s, rx * c))
    w = pie(cx, cy, lim, pol + 12) if side > 0 else pie(cx, cy, pol - 12, lim)
    return I(cutp, w)

def rcut(cx, cy, rx, ry, sx, sy, rot, t, side, lim, L=4000, dx=0, dy=0, deep=False):
    """zone à retirer pour finir un rond épais : la coupe va du point du bord extérieur (paramètre t)
    au point correspondant du bord intérieur. Les deux coins restent francs, même quand le trait est très épais.
    side=+1 garde la suite dans le sens direct ; lim borne la zone retirée de l'autre côté (angle polaire)."""
    tr = math.radians(t); c, s = math.cos(tr), math.sin(tr)
    # la coupe suit la perpendiculaire à la ligne médiane du trait (ellipse à mi-épaisseur)
    mx, my = rx - sx / 2, ry - sy / 2
    M = (cx + mx * c, cy + my * s)
    nm = (my * c, mx * s); l = math.hypot(*nm); d = (-nm[0] / l, -nm[1] / l)
    P = (M[0] - d[0] * sx, M[1] - d[1] * sx)                 # côté extérieur
    Q = (M[0] + d[0] * sx, M[1] + d[1] * sx)                 # côté intérieur
    A = (P[0] - d[0] * L, P[1] - d[1] * L); B = (P[0] + d[0] * L, P[1] + d[1] * L)
    T = (-rx * s * side, ry * c * side); lt = math.hypot(*T); T = (T[0] / lt, T[1] / lt)
    cutp = poly([A, B, (B[0] - T[0] * L, B[1] - T[1] * L), (A[0] - T[0] * L, A[1] - T[1] * L)])
    # deep : la zone retirée va jusqu'au bord intérieur (sinon, dans les blancs très plats, il reste un crochet)
    pols = [math.degrees(math.atan2(p[1] - cy, p[0] - cx)) for p in ((P, M, Q) if deep else (P, M))]
    if side > 0:
        hi = max(pols) if max(pols) - min(pols) < 180 else min(pols) + 360
        w = pie(cx, cy, lim, hi + 12)
    else:
        lo_ = min(pols) if max(pols) - min(pols) < 180 else max(pols) - 360
        w = pie(cx, cy, lo_ - 12, lim)
    return I(cutp, w)

def icut(cx, cy, rx, ry, sx, sy, t, side, lim, L=4000):
    """comme rcut, mais la coupe part d'équerre du bord intérieur (paramètre t) : dans un blanc très plat,
    une coupe qui le frôle laisse un fil ou un crochet ; d'équerre, jamais."""
    tr = math.radians(t); c, s = math.cos(tr), math.sin(tr)
    rxi, ryi = rx - sx, ry - sy
    Qi = (cx + rxi * c, cy + ryi * s)
    n = (c / rxi, s / ryi); l = math.hypot(*n); n = (n[0] / l, n[1] / l)
    # point du bord extérieur sur la normale
    ox, oy = Qi[0] - cx, Qi[1] - cy
    a_ = (n[0] / rx) ** 2 + (n[1] / ry) ** 2; b_ = 2 * (ox * n[0] / rx ** 2 + oy * n[1] / ry ** 2); c_ = (ox / rx) ** 2 + (oy / ry) ** 2 - 1
    k = (-b_ + math.sqrt(max(0.0, b_ * b_ - 4 * a_ * c_))) / (2 * a_)
    P = (Qi[0] + n[0] * k, Qi[1] + n[1] * k)
    A = (P[0] + n[0] * L, P[1] + n[1] * L); B = (P[0] - n[0] * L, P[1] - n[1] * L)
    T = (-rx * s * side, ry * c * side); lt = math.hypot(*T); T = (T[0] / lt, T[1] / lt)
    cutp = poly([A, B, (B[0] - T[0] * L, B[1] - T[1] * L), (A[0] - T[0] * L, A[1] - T[1] * L)])
    pols = [math.degrees(math.atan2(p[1] - cy, p[0] - cx)) for p in (P, Qi)]
    if side > 0:
        hi = max(pols) if max(pols) - min(pols) < 180 else min(pols) + 360
        w = pie(cx, cy, lim, hi + 12)
    else:
        lo_ = min(pols) if max(pols) - min(pols) < 180 else max(pols) - 360
        w = pie(cx, cy, lo_ - 12, lim)
    return I(cutp, w)

def bracket(cx, cy, rx, ry, xs, ys, toward, k=0.5):
    """raccord tangent entre le bord extérieur d'un rond (ellipse droite cx, cy, rx, ry) et le coin (xs, ys) d'un fût.
    Quand le coin du fût dépasse à peine du rond (moins de k fût), il fait une petite dent : on la comble par une
    droite qui part du coin et touche le rond. toward = -1 si le rond est à gauche du fût, +1 s'il est à droite.
    Rend None si la dent est assez haute pour se lire comme un bout de fût."""
    u = (xs - cx) / rx
    if abs(u) >= 1: return None
    h = ry * math.sqrt(1 - u * u); low = ys < cy
    yj = cy - h if low else cy + h
    if abs(yj - ys) >= k * ST or (yj - ys) * (1 if low else -1) <= 0: return None
    def f(t):
        tx, ty = cx + rx * math.cos(t), cy + ry * math.sin(t)
        return (tx - xs) * (ry * math.cos(t)) - (ty - ys) * (-rx * math.sin(t))
    tj = math.atan2((yj - cy) / ry, (xs - cx) / rx); te = -math.pi / 2 if low else math.pi / 2
    n = 400; a = tj; fa = f(a); T = None
    for i in range(1, n + 1):
        b = tj + (te - tj) * i / n; fb = f(b)
        if fa * fb <= 0:
            for _ in range(60):
                m = (a + b) / 2; fm = f(m)
                if fa * fm <= 0: b, fb = m, fm
                else: a, fa = m, fm
            T = (cx + rx * math.cos(a), cy + ry * math.sin(a)); break
        a, fa = b, fb
    if T is None: return None
    e = -toward * 3
    return poly([(xs, ys), T, (xs, yj), (xs + e, yj), (xs + e, ys)])

def tparam(ry, dy):
    """paramètre (degrés, côté gauche, sous le centre) du point d'une ellipse situé dy sous son centre"""
    return 180 + math.degrees(math.asin(max(-1, min(1, dy / ry))))

def halfplane(p, q, R=6000):
    """tout ce qui est à droite de la droite orientée p → q"""
    dx, dy = q[0] - p[0], q[1] - p[1]; l = math.hypot(dx, dy); ux, uy = dx / l, dy / l; nx, ny = uy, -ux
    a = (p[0] - ux * R, p[1] - uy * R); b = (p[0] + ux * R, p[1] + uy * R)
    return poly([a, b, (b[0] + nx * R, b[1] + ny * R), (a[0] + nx * R, a[1] + ny * R)])

def dserif(xe, ye, xo, yo, t, left=True, right=True):
    """empattement en coin posé au bout d'une diagonale (de (xe, ye) vers (xo, yo), épaisseur horizontale t) :
    ses deux flancs suivent les bords du trait, il n'y a donc aucun cran entre le trait et l'empattement"""
    sgn = 1 if yo > ye else -1
    def xc(y): return xe + (xo - xe) * (y - ye) / (yo - ye)
    e = max(10, round(SH * 0.2)); l = W if left else 0; r = W if right else 0
    yS = ye + sgn * SH
    xl0, xr0, xlS, xrS = xc(ye) - t / 2, xc(ye) + t / 2, xc(yS) - t / 2, xc(yS) + t / 2
    pts = [(xl0 - l, ye), (xr0 + r, ye)] + ([(xr0 + r, ye + sgn * e)] if right else []) + [(xrS, yS), (xlS, yS)] \
          + ([(xl0 - l, ye + sgn * e)] if left else [])
    return poly(pts)

def head(x0, x1, top, join=None):
    """tête de plume : coin en biais vers la gauche (vintage), arêtes nettes (futur).
    join : hauteur de l'arche au bord droit du fût ; si l'écart est petit, la tête s'y raccorde sans marche"""
    a = round(W * 0.95); d = round(SH * 1.6); yr = top + 16
    if join is not None and yr - join < 40: yr = join
    return poly([(x0 - a - 10, top - round(SH * 0.73)), (x0 + 6, top + 8), (x1, yr),
                 (x1, top - d + 10), (x0, top - d), (x0 - a - 10, top - round(SH * 1.1))])

def kick(x0, x1, y=0):
    """départ vers la droite au pied (d, u, a) : la lettre avance"""
    return poly([(x0, y + round(SH * 1.15)), (x0, y), (x1 + W, y), (x1 + W, y + max(10, round(SH * 0.2))), (x1, y + SH)])

def spur(x0, x1, y=0):
    """éperon à gauche sous le fût (b) : posé sur la ligne, bout coupé net comme un empattement"""
    e = max(10, round(SH * 0.2)); xt = x0 - round(W * 0.7)
    return poly([(xt, y), (x1, y), (x1, y + 30), (x0, y + round(SH * 1.35)), (xt, y + e)])

def ear(x0, y, join=None):
    """oreille en haut à droite (q, g) : bout coupé à plat dessus et sur le côté, aucune pointe.
    join : hauteur du rond au bord gauche du fût ; s'il arrive juste sous le départ de l'oreille, elle part de lui (pas de marche)"""
    xt = x0 + ST + round(W * 0.75); e2 = max(12, round(SH * 0.35)); f = round(e2 * 0.7); ys = y - 24
    if join is not None and 0 < ys - join < 0.5 * ST: ys = join
    return poly([(x0, ys), (xt - f, y + 24), (xt, y + 24), (xt, y + 24 - e2), (x0 + ST, y - 60), (x0, min(ys, y - 60))])

def dot(cx, cy, r=None):
    r = r or round(ST * 0.62 + 4)
    return ellipse(cx, cy, r, r)

def hook_r(x0, y, h, reach):
    """crochet en bas à droite (l, t) : finit coupé net"""
    o = ellipse(x0 + ST + reach, y + h, reach + ST, h + OV)
    i = ellipse(x0 + ST + reach, y + h + 4, reach, h + OV - TH)
    return I(D(o, i), rect(x0, y - OV - 5, x0 + ST + reach, y + h))

# ---------- registre ----------
GLYPHS = {}; UNI = {}
def reg(name, ch=None):
    def deco(f):
        GLYPHS[name] = f
        if ch: UNI[name] = ch
        return f
    return deco

def side(k):
    """approche selon le bord : S fût à empattement, P fût nu, O rond, D diagonale, K coup de pied, ou un nombre"""
    if isinstance(k, (int, float)): return k
    return {'S': S_STEM - W, 'P': S_STEM, 'O': S_STEM * 0.62, 'D': S_STEM * 0.28,
            'K': S_STEM - W * 0.7, 'T': S_STEM * 0.45}[k]

def out(p, l='S', r='S'): return p, round(side(l)), round(side(r))

# ---------- fabrication ----------
VERSION = '1.000'
WIN_ASC, WIN_DESC = 1060, 360          # les mêmes pour toute la famille (la 090 monte à 1047)
def build(outf, style, weight, glyphs, cmap_names, fea=None):
    from fontTools.pens.t2CharStringPen import T2CharStringPen
    from fontTools.pens.boundsPen import BoundsPen
    order = ['.notdef', 'space'] + [g[0] for g in glyphs if g[0] not in ('.notdef', 'space')]
    cs = {}; hmtx = {}
    nd = T2CharStringPen(500, None); D(rect(50, 0, 450, CAP), rect(50 + TH, TH, 450 - TH, CAP - TH)).draw(nd)
    cs['.notdef'] = nd.getCharString(); hmtx['.notdef'] = (500, 50)
    sp = round(250 + 0.4 * ST); cs['space'] = T2CharStringPen(sp, None).getCharString(); hmtx['space'] = (sp, 0)
    for name, path, lsb, rsb in glyphs:
        if name in ('.notdef', 'space'): continue
        if path is None or path.bounds is None or path.bounds == (0, 0, 0, 0):
            cs[name] = T2CharStringPen(sp, None).getCharString(); hmtx[name] = (sp, 0); continue
        b = path.bounds
        adv = round(lsb + (b[2] - b[0]) + rsb); dx = lsb - b[0]
        if name.startswith('uni03'): adv = 0; dx = 0
        pen = T2CharStringPen(adv, None)
        path.draw(TransformPen(pen, (1, 0, 0, 1, round(dx), 0)))
        cs[name] = pen.getCharString(); hmtx[name] = (adv, round(b[0] + round(dx)))
    fb = FontBuilder(UPM, isTTF=False)
    fb.setupGlyphOrder(order)
    cmap = {ord(' '): 'space'}
    for n, ch in cmap_names.items():
        if n in cs: cmap[ord(ch)] = n
    fb.setupCharacterMap(cmap)
    psn = f'{PSFAM}-{style}'; full = f'{FAMILY} {style}'
    cr = '© 2026 LaFleurStudio. All rights reserved.'
    fb.setupCFF(psn, {'FullName': full, 'FamilyName': full, 'Weight': style, 'Copyright': '(c) 2026 LaFleurStudio. All rights reserved.',
                      'Notice': f'{FAMILY} by LaFleurStudio.'}, cs, {})
    fb.setupHorizontalMetrics(hmtx)
    fb.setupHorizontalHeader(ascent=950, descent=-300)
    lic = ('Free for personal use. Commercial use requires prior written permission from LaFleurStudio '
           '(free or paid, decided case by case): info@lafleurstudio.ch. Usage personnel gratuit ; usage commercial '
           'sur autorisation écrite de LaFleurStudio.')
    fb.setupNameTable({'copyright': cr, 'familyName': full, 'styleName': 'Regular',
        'uniqueFontIdentifier': f'{VERSION};LFST;{psn}', 'fullName': full, 'version': f'Version {VERSION}', 'psName': psn,
        'manufacturer': 'LaFleurStudio', 'designer': 'Jonathan Kern', 'vendorURL': 'https://jonlekern.github.io/Fonts/',
        'licenseDescription': lic, 'licenseInfoURL': f'https://github.com/Jonlekern/Fonts/blob/main/{SLUG}/LICENCE.txt',
        'typographicFamily': FAMILY, 'typographicSubfamily': style}, mac=False)
    fb.setupOS2(sTypoAscender=950, sTypoDescender=-300, sTypoLineGap=0, usWinAscent=WIN_ASC, usWinDescent=WIN_DESC,
                sCapHeight=CAP, usWeightClass=weight, sxHeight=XH, version=4, achVendID='LFST', fsSelection=0x40 | 0x80)
    fb.setupPost()
    if fea:
        from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
        addOpenTypeFeaturesFromString(fb.font, fea)
    gs = fb.font.getGlyphSet(); ys = []
    for n_ in fb.font.getGlyphOrder():
        bp = BoundsPen(gs); gs[n_].draw(bp)
        if bp.bounds: ys += [bp.bounds[1], bp.bounds[3]]
    assert max(ys) <= WIN_ASC and -min(ys) <= WIN_DESC, ('hors des métriques win', max(ys), min(ys))
    from fontTools.ttLib.tables.O_S_2f_2 import Panose
    fb.font['OS/2'].recalcUnicodeRanges(fb.font)
    cps = set(cmap)
    cpr = 0
    if 0xE9 in cps: cpr |= 1 << 0              # Latin 1
    if 0x10D in cps and 0x171 in cps: cpr |= 1 << 1   # Latin 2
    if 0x11F in cps and 0x15F in cps: cpr |= 1 << 4   # turc
    if 0x113 in cps and 0x12B in cps: cpr |= 1 << 7   # balte
    cpr |= 1 << 29                              # Mac Roman
    fb.font['OS/2'].ulCodePageRange1 = cpr; fb.font['OS/2'].ulCodePageRange2 = 0
    fb.font['head'].macStyle = 0; fb.font['head'].fontRevision = float(VERSION)
    fb.font['OS/2'].usDefaultChar = 0; fb.font['OS/2'].usBreakChar = 32
    fb.save(outf)

def clean(p, amin=60):
    """simplifie et retire les miettes (contours d'aire < amin)"""
    p = P() if p is None else p
    try:
        p.simplify(fix_winding=True, clockwise=False)
    except Exception:
        return p
    rp = RecordingPen(); p.draw(rp); out_ = P(); pen = out_.getPen(); cur = []; keep = []
    for op, a in rp.value:
        if op == 'moveTo': cur = [(op, a)]
        elif op in ('closePath', 'endPath'):
            cur.append((op, a)); keep.append(cur); cur = []
        else: cur.append((op, a))
    def area(c):
        pts = [a[-1] for op, a in c if a]
        return abs(sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts))) / 2) if len(pts) > 2 else 0
    for c in keep:
        if area(c) < amin: continue
        for op, a in c: getattr(pen, op)(*a)
    return out_
