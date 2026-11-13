# Les lettres russes de ШКВАЛ, construites avec les pièces et les mesures d'Overshoot.
# Chaque lettre : fonction(graisse) -> (contour, chasse).
from functools import lru_cache
from mesures import mesures, police, points
from pieces import glyphe, rect, union, coupe, transforme, decale, miroir, renverse, moins

LETTRES = {}


def lettre_def(*cars):
    def enr(fn):
        for c in cars:
            LETTRES[c] = fn
        return fn
    return enr


@lru_cache(None)
def lettre(c, g):
    return LETTRES[c](g) if LETTRES[c].__code__.co_argcount == 1 else LETTRES[c](g, c)


def chasse(g, nom):
    return police(g)['hmtx'][nom][0]


def copie(nom):
    fn = lambda g: (glyphe(police(g), nom), chasse(g, nom))
    fn.latin = nom                                  # lettre reprise telle quelle du latin
    return fn


def copies():
    return {c: fn.latin for c, fn in LETTRES.items() if hasattr(fn, 'latin')}


# ---- reprises du latin ----
for c, n in (('А', 'A'), ('В', 'B'), ('Е', 'E'), ('К', 'K'), ('М', 'M'), ('Н', 'H'), ('О', 'O'), ('Р', 'P'), ('С', 'C'),
             ('Т', 'T'), ('Х', 'X'), ('а', 'a'), ('е', 'e'), ('о', 'o'), ('р', 'p'), ('с', 'c'), ('у', 'y'), ('х', 'x')):
    LETTRES[c] = copie(n)


@lettre_def('Я')
def ya(g):
    f = police(g); w = chasse(g, 'R')
    return miroir(glyphe(f, 'R'), w), w


@lettre_def('И')
def i_cap(g):
    f = police(g); w = chasse(g, 'N')
    return miroir(glyphe(f, 'N'), w), w


# ---- capitales construites ----
@lettre_def('Ш')
def sha(g):
    m = mesures(g); S, b, W, a = m['fut_cap'], m['barre_cap'], m['chasse_M'], m['approche_cap']
    c = (W - 2 * a - 3 * S) / 2
    futs = [rect(a + i * (S + c), 0, a + i * (S + c) + S, m['cap']) for i in range(3)]
    return union(*futs, rect(a, 0, W - a, b)), W


@lettre_def('Г')
def ghe(g):
    return renverse(glyphe(police(g), 'L'), mesures(g)['cap']), chasse(g, 'L')


def el_crochet(g):
    """Л avec le crochet du J d'Overshoot comme jambe gauche (bout coupé à l'horizontale)."""
    f = police(g); m = mesures(g); S, b, cap = m['fut_cap'], m['barre_cap'], m['cap']
    xs = sorted({x for x, y in points(f, 'J') if y == cap})
    xg, xd = xs[0], xs[-1]
    xr = xd + m['contre_H'] + S
    return union(glyphe(f, 'J'), rect(xg, cap - b, xr, cap), rect(xr - S, 0, xr, cap)), round(xr + m['approche_cap'])


def el_diagonale(g):
    """Л avec une jambe gauche en diagonale, à la pente et à l'épaisseur de la jambe du A."""
    f = police(g); m = mesures(g); S, b, cap = m['fut_cap'], m['barre_cap'], m['cap']
    pa = points(f, 'A')
    bas = sorted(x for x, y in pa if y == 0)[:2]                 # pied gauche du A
    haut = min(x for x, y in pa if y == cap)                     # haut de la diagonale gauche
    ep = bas[1] - bas[0]; pente = (haut - bas[0]) / cap
    x0 = bas[0]; xt = x0 + pente * cap
    jambe = Path_poly([(x0, 0), (x0 + ep, 0), (xt + ep, cap), (xt, cap)])
    xr = xt + ep + m['contre_H'] + S
    return union(jambe, rect(xt, cap - b, xr, cap), rect(xr - S, 0, xr, cap)), round(xr + m['approche_cap'])


def Path_poly(pts):
    from pathops import Path
    p = Path(); pen = p.getPen(); pen.moveTo(pts[0])
    for q in pts[1:]:
        pen.lineTo(q)
    pen.closePath()
    return p


VARIANTES = {'Л': {'crochet': el_crochet, 'diagonale': el_diagonale}}
CHOIX = {'Л': 'crochet'}


@lettre_def('Л')
def el(g):
    return VARIANTES['Л'][CHOIX['Л']](g)


@lettre_def('Д')
def de(g):
    """Д : une boîte (deux fûts, barre du haut, barre du bas) sur deux jambages coupés à l'horizontale."""
    m = mesures(g); S, b, cap, a = m['fut_cap'], m['barre_cap'], m['cap'], m['approche_cap']
    xr = a + S + m['contre_H'] + S
    dj = m['jambage']
    forme = union(rect(a, -dj, a + S, cap), rect(xr - S, -dj, xr, cap), rect(a, cap - b, xr, cap), rect(a, 0, xr, b))
    return forme, round(xr + a)


@lettre_def('Б')
def be(g):
    f = police(g); m = mesures(g); S, b, cap, a = m['fut_cap'], m['barre_cap'], m['cap'], m['approche_cap']
    y_bas = min(y for x, y in points(f, 'P') if y > 0 and x == a + S)     # bas de la boucle du P
    boucle = decale(coupe(glyphe(f, 'P'), 0, y_bas, chasse(g, 'P'), cap), 0, -y_bas)
    bras = max(x for x, y in points(f, 'L'))                               # bout du bras du L / Г
    return union(rect(a, 0, a + S, cap), boucle, rect(a, cap - b, bras, cap)), chasse(g, 'P')


@lettre_def('Ж')
def zhe(g):
    f = police(g); m = mesures(g); S, a = m['fut_cap'], m['approche_cap']
    wk = chasse(g, 'K')
    bout = max(x for x, y in points(f, 'K'))
    bras = coupe(glyphe(f, 'K'), a + S, -10, wk, 800)
    x0 = (wk - bout) + bout - (a + S)                 # gauche du fût central
    gauche = transforme(bras, (-1, 0, 0, 1, x0 + a + S, 0))
    droite = decale(bras, x0 - a)
    return union(gauche, rect(x0, 0, x0 + S, m['cap']), droite), round(x0 + S + bout - (a + S) + (wk - bout))


@lettre_def('Ю')
def yu(g):
    f = police(g); m = mesures(g); S, a = m['fut_cap'], m['approche_cap']
    o = glyphe(f, 'O'); ox0 = o.bounds[0]
    G = round(0.3 * m['contre_H'])
    dx = a + S + G - ox0
    y0, y1 = m['barre_H']
    return union(rect(a, 0, a + S, m['cap']), rect(a + S - 1, y0, a + S + G + S / 2, y1), decale(o, dx)), round(dx + chasse(g, 'O'))


LETTRES['Ё'] = copie('uni00CB')
LETTRES['З'] = copie('three')


@lettre_def('Й')
def i_bref(g):
    f = police(g); p, w = lettre('И', g)
    breve = coupe(glyphe(f, 'uni0102'), -100, 760, 3000, 1200)      # la brève des capitales, prise sur Ă
    return union(p, decale(breve, w / 2 - chasse(g, 'A') / 2)), w


@lettre_def('П')
def pe(g):
    m = mesures(g); S, b, cap, a = m['fut_cap'], m['barre_cap'], m['cap'], m['approche_cap']
    xr = a + S + m['contre_H'] + S
    return union(rect(a, 0, a + S, cap), rect(xr - S, 0, xr, cap), rect(a, cap - b, xr, cap)), round(xr + a)


def _boite_bas(g, futs, jambage):
    """Ц, Щ : des fûts, la barre du bas, et le dernier fût qui descend en jambage."""
    m = mesures(g); S, b, cap, a = m['fut_cap'], m['barre_cap'], m['cap'], m['approche_cap']
    c = m['contre_H'] if futs == 2 else (m['chasse_M'] - 2 * a - 3 * S) / 2
    xs = [a + i * (S + c) for i in range(futs)]
    formes = [rect(x, 0, x + S, cap) for x in xs] + [rect(a, 0, xs[-1] + S, b)]
    if jambage:
        formes.append(rect(xs[-1], -m['jambage'], xs[-1] + S, 0))
    return union(*formes), round(xs[-1] + S + a)


@lettre_def('Ц')
def tse(g):
    return _boite_bas(g, 2, True)


@lettre_def('Щ')
def shcha(g):
    return _boite_bas(g, 3, True)


@lettre_def('Ч')
def che(g):
    """Ч : le coin bas-gauche arrondi du U, remonté à la hauteur de la barre du H ; la barre file droit jusqu'au fût."""
    f = police(g); m = mesures(g); cap = m['cap']
    xs = sorted({x for x, y in points(f, 'U') if y == cap})
    return _che(glyphe(f, 'U'), xs, m['barre_H'][0] + 7, cap), chasse(g, 'U')


def _che(u, xs, h, haut):
    """Coupe le U remonté au milieu, et prolonge sa barre du bas, à son épaisseur exacte, jusqu'au fût droit."""
    cx = round((xs[0] + xs[3]) / 2)
    u = decale(u, 0, h)
    _, y0, _, y1 = coupe(u, cx - 0.5, -500, cx + 0.5, haut).bounds          # le bas du U, mesuré au milieu
    return union(coupe(u, -100, 0, cx, haut), rect(cx - 1, y0, xs[2] + 1, y1), rect(xs[2], 0, xs[3], haut))


def _boucle_bas(g):
    """La boucle du P descendue sur la ligne (pour Б, Ь, Ъ, Ы), sans le fût."""
    f = police(g); m = mesures(g); S, cap, a = m['fut_cap'], m['cap'], m['approche_cap']
    y_bas = min(y for x, y in points(f, 'P') if y > 0 and x == a + S)
    return decale(coupe(glyphe(f, 'P'), a + S - 1, y_bas, chasse(g, 'P'), cap), 0, -y_bas)


@lettre_def('Ь')
def soft(g):
    m = mesures(g); S, a = m['fut_cap'], m['approche_cap']
    return union(rect(a, 0, a + S, m['cap']), _boucle_bas(g)), chasse(g, 'P')


@lettre_def('Ъ')
def hard(g):
    f = police(g); m = mesures(g); S, b, cap, a = m['fut_cap'], m['barre_cap'], m['cap'], m['approche_cap']
    xt = sorted({x for x, y in points(f, 'T') if y == cap})
    bras = min(x for x, y in points(f, 'T') if 0 < y < cap and x > xt[0]) - xt[0]   # longueur du bras du T
    p, w = soft(g)
    return union(rect(a, cap - b, a + bras + S, cap), decale(p, bras)), w + round(bras)


@lettre_def('Ы')
def yery(g):
    m = mesures(g); S, a = m['fut_cap'], m['approche_cap']
    p, w = soft(g)
    x = w + a
    return union(p, rect(x, 0, x + S, m['cap'])), round(x + S + a)


@lettre_def('Ф')
def ef(g):
    """Ф : un fût et deux boucles du P, l'une retournée, centrées en hauteur."""
    m = mesures(g); S, cap, a = m['fut_cap'], m['cap'], m['approche_cap']
    bo = _boucle_bas(g); x0, y0, x1, y1 = bo.bounds
    dy = (cap - (y1 - y0)) / 2 - y0
    droite = decale(bo, 0, dy)                              # part du bord droit du fût d'origine (a + S)
    larg = x1 - (a + S)
    gauche = transforme(droite, (-1, 0, 0, 1, 2 * (a + S) - S, 0))   # retournée autour du fût
    forme = union(gauche, rect(a, 0, a + S, cap), droite)
    dx = a - forme.bounds[0]
    return decale(forme, dx), round(2 * larg + S + 2 * a)


@lettre_def('Э')
def e_rev(g):
    f = police(g); m = mesures(g); w = chasse(g, 'C'); b = m['barre_cap']
    pc = points(f, 'C')
    dedans = max(x for x, y in pc if y == 365 and x < w / 2)                # paroi intérieure gauche du C
    y0, y1 = m['barre_H']
    c = miroir(glyphe(f, 'C'), w)
    return union(c, rect(round(0.3 * w), (y0 + y1) / 2 - b / 2, w - dedans + 5, (y0 + y1) / 2 + b / 2)), w


@lettre_def('У')
def u_cyr(g):
    """У : les traits du y d'Overshoot (mêmes pentes), posés sur la ligne et montés à la hauteur des capitales.
    La jambe droite descend jusqu'en bas, coupée à l'horizontale ; le bras gauche s'arrête net sur elle."""
    f = police(g); m = mesures(g); cap, X = m['cap'], m['x']
    py = points(f, 'y'); pv = points(f, 'V')
    hy = sorted({x for x, y in py if y == X}); hv = sorted({x for x, y in pv if y == cap})
    B = min(y for x, y in py); t0, t1 = sorted(x for x, y in py if y == B)
    xb, yb = min(((x, y) for x, y in py if 0 <= y < 30), key=lambda p: p[0])   # bas du bras gauche
    kL = (xb - hy[0]) / (X - yb); kR = (hy[3] - t1) / (X - B)
    H = 2000
    gauche = Path_poly([(hy[0], X), (hy[1], X), (hy[1] + kL * (X + H), -H), (hy[0] + kL * (X + H), -H)])
    droite = Path_poly([(hy[2], X), (hy[3], X), (t1, B), (t0, B)])
    dehors = Path_poly([(hy[3] + kR * H, X + H), (hy[3] + 5000, X + H), (hy[3] + 5000, B - H), (t1 - kR * H, B - H)])
    forme = coupe(union(moins(gauche, dehors), droite), -3000, B, 5000, X)
    sx = (hv[3] - hv[2]) / (hy[3] - hy[2]); sy = cap / (X - B)
    gv = chasse(g, 'V')
    p = transforme(forme, (sx, 0, 0, sy, hv[0] - sx * hy[0], -B * sy))
    return p, round(hv[0] + sx * (hy[3] - hy[0]) + (gv - hv[3]))


# ---- minuscules ----
@lettre_def('к')
def ka(g):
    return coupe(glyphe(police(g), 'k'), -50, -50, 2000, mesures(g)['x']), chasse(g, 'k')


@lettre_def('ш')
def sha_min(g):
    m = mesures(g); s, b, W, a = m['fut_min'], m['barre_min'], m['chasse_m'], m['approche_min']
    c = (W - 2 * a - 3 * s) / 2
    futs = [rect(a + i * (s + c), 0, a + i * (s + c) + s, m['x']) for i in range(3)]
    return union(*futs, rect(a, 0, W - a, b)), W


def petite_cap(g, c):
    """Petite capitale : la capitale réduite à la hauteur des minuscules, fûts à l'épaisseur des minuscules."""
    m = mesures(g); sx = m['fut_min'] / m['fut_cap']; sy = m['x'] / m['cap']
    p, w = lettre(c, g)
    a, am = m['approche_cap'], m['approche_min']
    return transforme(p, (sx, 0, 0, sy, am - a * sx, 0)), round(sx * (w - a) + am)


@lettre_def('в')
def ve(g):
    return petite_cap(g, 'В')


@lettre_def('л')
def el_min(g):
    return petite_cap(g, 'Л')


# ---- les autres minuscules ----
LETTRES['ё'] = copie('uni00EB')


def _min(g):
    m = mesures(g)
    return m, m['fut_min'], m['barre_min'], m['x'], m['approche_min'], contre_n(g)


def contre_n(g):
    xs = sorted({x for x, y in points(police(g), 'n') if y == 0})
    return xs[2] - xs[1]


def barre_min_y(g):
    """La barre des minuscules (н, ю) : la barre du H ramenée à la hauteur des minuscules."""
    m = mesures(g); y0, y1 = m['barre_H']; c = (y0 + y1) / 2 * m['x'] / m['cap']
    return c - m['barre_min'] / 2, c + m['barre_min'] / 2


@lettre_def('н')
def en_min(g):
    m, s, b, x, a, cn = _min(g); xr = a + s + cn + s
    y0, y1 = barre_min_y(g)
    return union(rect(a, 0, a + s, x), rect(xr - s, 0, xr, x), rect(a, y0, xr, y1)), round(xr + a)


@lettre_def('п')
def pe_min(g):
    m, s, b, x, a, cn = _min(g); xr = a + s + cn + s
    return union(rect(a, 0, a + s, x), rect(xr - s, 0, xr, x), rect(a, x - b, xr, x)), round(xr + a)


@lettre_def('г')
def ghe_min(g):
    m, s, b, x, a, cn = _min(g)
    bout = max(px for px, py in points(police(g), 'r'))
    return union(rect(a, 0, a + s, x), rect(a, x - b, bout, x)), chasse(g, 'r')


@lettre_def('т')
def te_min(g):
    m, s, b, x, a, cn = _min(g)
    f = police(g); xt = sorted({px for px, py in points(f, 'T') if py == m['cap']})
    bras = (min(px for px, py in points(f, 'T') if 0 < py < m['cap'] and px > xt[0]) - xt[0]) * s / m['fut_cap']
    lt = xt[0]
    return union(rect(lt, x - b, lt + 2 * bras + s, x), rect(lt + bras, 0, lt + bras + s, x)), round(2 * lt + 2 * bras + s)


@lettre_def('д')
def de_min(g):
    m, s, b, x, a, cn = _min(g); xr = a + s + cn + s; dj = m['jambage']
    return union(rect(a, -dj, a + s, x), rect(xr - s, -dj, xr, x), rect(a, x - b, xr, x), rect(a, 0, xr, b)), round(xr + a)


def _boite_bas_min(g, futs):
    m, s, b, x, a, cn = _min(g)
    c = cn if futs == 2 else (m['chasse_m'] - 2 * a - 3 * s) / 2
    xs = [a + i * (s + c) for i in range(futs)]
    formes = [rect(px, 0, px + s, x) for px in xs] + [rect(a, 0, xs[-1] + s, b), rect(xs[-1], -m['jambage'], xs[-1] + s, 0)]
    return union(*formes), round(xs[-1] + s + a)


@lettre_def('ц')
def tse_min(g):
    return _boite_bas_min(g, 2)


@lettre_def('щ')
def shcha_min(g):
    return _boite_bas_min(g, 3)


@lettre_def('ж')
def zhe_min(g):
    f = police(g); m, s, b, x, a, cn = _min(g)
    wk = chasse(g, 'k'); bout = max(px for px, py in points(f, 'k'))
    bras = coupe(glyphe(f, 'k'), a + s, -10, wk, x)
    x0 = (wk - bout) + bout - (a + s)
    gauche = transforme(bras, (-1, 0, 0, 1, x0 + a + s, 0))
    droite = decale(bras, x0 - a)
    return union(gauche, rect(x0, 0, x0 + s, x), droite), round(x0 + s + bout - (a + s) + (wk - bout))


@lettre_def('ч')
def che_min(g):
    f = police(g); m, s, b, x, a, cn = _min(g)
    xs = sorted({px for px, py in points(f, 'u') if py == x})
    y0, _ = barre_min_y(g)
    return _che(glyphe(f, 'u'), xs, round(y0) + 7, x), chasse(g, 'u')


@lettre_def('б')
def be_min(g):
    f = police(g); m, s, b, x, a, cn = _min(g)
    o = glyphe(f, 'o'); ox0, _, ox1, _ = o.bounds
    haut = max(py for px, py in points(f, 'l'))                         # hauteur des montantes (l)
    bras = ox0 + 0.85 * (ox1 - ox0)
    ep = min(b, 0.62 * (haut - o.bounds[3]))          # le bras reste au-dessus de la boucle, avec un vrai blanc dessous
    return union(o, rect(ox0, 300, ox0 + s, haut), rect(ox0, haut - ep, bras, haut)), chasse(g, 'o')


@lettre_def('э')
def e_rev_min(g):
    f = police(g); m, s, b, x, a, cn = _min(g); w = chasse(g, 'c')
    dedans = max(px for px, py in points(f, 'c') if py == 300 and px < w / 2)
    return union(miroir(glyphe(f, 'c'), w), rect(round(0.3 * w), 300 - b / 2, w - dedans + 5, 300 + b / 2)), w


@lettre_def('ю')
def yu_min(g):
    f = police(g); m, s, b, x, a, cn = _min(g)
    o = glyphe(f, 'o'); G = round(0.3 * cn)
    dx = a + s + G - o.bounds[0]
    y0, y1 = barre_min_y(g)
    return union(rect(a, 0, a + s, x), rect(a + s - 1, y0, a + s + G + s / 2, y1), decale(o, dx)), round(dx + chasse(g, 'o'))


@lettre_def('й')
def i_bref_min(g):
    f = police(g); p, w = lettre('и', g)
    br = glyphe(f, 'breve'); bx0, _, bx1, _ = br.bounds
    return union(p, decale(br, w / 2 - (bx0 + bx1) / 2)), w


for _c, _cap in (('з', 'З'), ('и', 'И'), ('м', 'М'), ('ь', 'Ь'), ('ъ', 'Ъ'), ('ы', 'Ы'), ('я', 'Я')):
    LETTRES[_c] = (lambda C: (lambda g: petite_cap(g, C)))(_cap)


@lettre_def('ф')
def ef_min(g):
    """ф : le fût monte comme le l et descend comme le p ; la boucle du b de chaque côté."""
    f = police(g); m, s, b, x, a, cn = _min(g)
    haut = max(py for px, py in points(f, 'l')); bas = min(py for px, py in points(f, 'p'))
    boucle = coupe(glyphe(f, 'b'), a + s - 1, -50, chasse(g, 'b'), x + 50)
    larg = boucle.bounds[2] - (a + s)
    gauche = transforme(boucle, (-1, 0, 0, 1, 2 * (a + s) - s, 0))
    forme = union(gauche, rect(a, bas, a + s, haut), boucle)
    dx = a - forme.bounds[0]
    return decale(forme, dx), round(2 * larg + s + 2 * a)
