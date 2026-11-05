# Nexum, graisses 100 à 900 : même squelette que la Hairline, avec les règles de triche optique :
# 1. contraste : horizontales plus fines que les verticales (diagonales entre les deux)
# 2. pièges à encre : les traits s'amincissent là où ils se croisent
# 3. détails (petites croix) plus fins
# 4. pointes plus courtes, proportionnées à l'épaisseur
# 5. lettres élargies pour garder les contreformes ouvertes
# 6. croisement en biais (< 40°) : le trait s'arrête dans l'autre, sans dépasser
# 7. à partir de 700 : U, panse ronde et fût qui traverse sous la ligne ; u, fond plat qui traverse le fût
# 8. à partir de 600 : A en Ā, les traits s'arrêtent sous la barre du haut, A étiré jusqu'aux pointes
# 9. à partir de 700 : E et F, croix du haut plus courte et fine
import sys, os, math
_ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _ICI)
import numpy as np
from PIL import Image, ImageDraw
import jalousia as essai
import droit
import nexum as techno

REGLES = dict(rv=110.0,        # demi-épaisseur des verticales (trait 220 = 22 % des capitales)
              horiz=0.70,      # 1. horizontales à 70 % des verticales
              piege=0.80,      # 2. aux croisements, 80 % sur une demi-épaisseur de part et d'autre
              detail=0.55,     # 3. petites croix à 55 %
              pointe=1.5,      # 4. pointe longue de 1,5 demi-épaisseur
              sx=1.18,         # 5. lettres élargies de 18 %
              ov=320.0, gap=230.0, poids=900)

def regles(poids):
    """Règles pour une graisse de 100 (Hairline) à 900 : tout passe en douceur de l'une à l'autre."""
    t = (poids - 100) / 800.0
    k = t ** 1.4                                   # progression de l'épaisseur
    return dict(rv=16 + (110 - 16) * k, horiz=1 - 0.30 * k, piege=1 - 0.20 * k, detail=1 - 0.45 * k,
                pointe=3.0 - 1.5 * k, sx=1 + 0.18 * k, ov=210 + 110 * k, gap=284 - 54 * k, poids=poids)

def densifier(P, step=12.0, coin=20.0):
    """Points rapprochés ; garde les coins vifs (virage > coin degrés)."""
    P = [np.array(p, float) for p in P]
    coins = set()
    for i in range(1, len(P) - 1):
        u1 = P[i] - P[i - 1]; u2 = P[i + 1] - P[i]
        c = np.dot(u1, u2) / (np.linalg.norm(u1) * np.linalg.norm(u2) + 1e-9)
        if math.degrees(math.acos(np.clip(c, -1, 1))) > coin:
            coins.add(i)
    out, flags = [P[0]], [False]
    for i in range(len(P) - 1):
        a, b = P[i], P[i + 1]
        k = max(int(np.linalg.norm(b - a) / step), 1)
        for t in np.linspace(0, 1, k + 1)[1:]:
            out.append(a * (1 - t) + b * t); flags.append(False)
        flags[-1] = (i + 1) in coins
    return out, flags

def croisements(strokes):
    """Points où deux traits différents se croisent."""
    pts = []
    segs = [[(np.array(a, float), np.array(b, float)) for a, b in zip(st['p'], st['p'][1:])] for st in strokes]
    for i in range(len(segs)):
        for j in range(i + 1, len(segs)):
            for a, b in segs[i]:
                for c, d in segs[j]:
                    M = np.array([b - a, c - d]).T
                    if abs(np.linalg.det(M)) < 1e-9: continue
                    t, s = np.linalg.solve(M, c - a)
                    if 0.03 <= t <= 0.97 and 0.03 <= s <= 0.97:   # vrai croisement, pas un sommet
                        u1 = (b - a) / np.linalg.norm(b - a); u2 = (d - c) / np.linalg.norm(d - c)
                        angle = math.degrees(math.acos(min(1.0, abs(float(u1 @ u2)))))
                        if angle > 45:                                   # croisement franc seulement
                            pts.append(a + (b - a) * t)
    return pts

def est_detail(st, ov):
    return bool(st.get('detail'))       # les petites croix, marquées dans le dessin

def contour_trait(st, X, R):
    """Morceaux de polygone d'un trait à épaisseur variable."""
    rv, ov = R['rv'], R['ov']
    rh = rv * R['horiz']
    P, coin = densifier(st['p'])
    caps = st['caps']
    n = len(P)
    U = [(P[i + 1] - P[i]) / (np.linalg.norm(P[i + 1] - P[i]) + 1e-9) for i in range(n - 1)]
    # rayon selon la direction (1)
    def r_dir(u):
        s = abs(u[1])
        return rh + (rv - rh) * s ** 2
    tang = [U[0]] + [(U[i - 1] + U[i]) / 2 for i in range(1, n - 1)] + [U[-1]]
    r = np.array([r_dir(t / (np.linalg.norm(t) + 1e-9)) for t in tang])
    if est_detail(st, ov):
        r *= R['detail']                                            # (3)
    for c in X:                                                     # (2)
        dist = np.array([np.linalg.norm(p - c) for p in P])
        f = 1 - (1 - R['piege']) * np.clip(1 - dist / (1.0 * rv), 0, 1)
        r = r * f
    # bouts : pointe (4) ou prolongé
    s = np.concatenate([[0], np.cumsum([np.linalg.norm(P[i + 1] - P[i]) for i in range(n - 1)])])
    L = s[-1]
    tl = R['pointe'] * rv
    if caps[0] == 'tip':
        r = r * np.clip(s / min(tl, 0.45 * L), 0, 1)
    if caps[1] == 'tip':
        r = r * np.clip((L - s) / min(tl, 0.45 * L), 0, 1)
    if caps[0] == 'T':
        P[0] = P[0] - U[0] * r[0] * 0.8
    if caps[1] == 'T':
        P[-1] = P[-1] + U[-1] * r[-1] * 0.8
    polys = []
    N = [np.array([-u[1], u[0]]) for u in U]
    for i in range(n - 1):
        a, b = P[i], P[i + 1]
        polys.append([a + N[i] * r[i], b + N[i] * r[i + 1], b - N[i] * r[i + 1], a - N[i] * r[i]])
    for i in range(n):
        if r[i] > 1 and not coin[i] and not (i < 3 and caps[0] in 'TB') and not (i > n - 4 and caps[1] in 'TB'):
            polys.append([P[i] + r[i] * np.array([math.cos(t), math.sin(t)]) for t in np.linspace(0, 2 * math.pi, 16, endpoint=False)])
    for i in range(1, n - 1):
        p = P[i]; n1, n2 = N[i - 1], N[i]
        polys.append([p + n1 * r[i], p + n2 * r[i], p - n2 * r[i], p - n1 * r[i]])
        if coin[i]:
            for sgn in (1, -1):
                a1 = p + sgn * n1 * r[i]; a2 = p + sgn * n2 * r[i]
                M = np.array([U[i - 1], -U[i]]).T
                if abs(np.linalg.det(M)) < 1e-9: continue
                t, _ = np.linalg.solve(M, a2 - a1)
                m = a1 + U[i - 1] * t
                if np.linalg.norm(m - p) < 8 * r[i]:
                    polys.append([p, a1, m, a2])
    return polys

def couper_biais(sts, ov):
    """6. Un bout qui dépasse après un croisement en biais (< 45°) s'arrête dans l'autre trait."""
    for i, st in enumerate(sts):
        for fin in (0, 1):
            P = st['p']
            a, b = (P[1], P[0]) if fin == 0 else (P[-2], P[-1])   # segment qui va vers le bout
            u = (b - a) / np.linalg.norm(b - a)
            meilleur = None
            for j, o in enumerate(sts):
                if j == i: continue
                for k_, (c, d) in enumerate(zip(o['p'], o['p'][1:])):
                    v = (d - c) / (np.linalg.norm(d - c) + 1e-9)
                    angle = math.degrees(math.acos(min(1.0, abs(float(u @ v)))))
                    if angle >= 40: continue          # 45° (D) garde son croisement
                    M = np.array([b - a, c - d]).T
                    if abs(np.linalg.det(M)) < 1e-9: continue
                    t, s_ = np.linalg.solve(M, c - a)
                    reste = (1 - t) * np.linalg.norm(b - a)
                    if 0 < t < 1 and -0.02 <= s_ <= 1.02 and reste <= ov * 1.3:
                        # l'autre trait doit continuer des deux côtés (cas du U) ;
                        # si le croisement est près de son bout aussi, c'est un X voulu (haut du A) : on garde
                        x = a + (b - a) * t
                        Q = [np.array(q, float) for q in o['p']]
                        L = np.cumsum([0] + [np.linalg.norm(Q[k + 1] - Q[k]) for k in range(len(Q) - 1)])
                        sx_ = L[k_] + np.linalg.norm(x - c)
                        if min(sx_, L[-1] - sx_) <= ov * 2.0:
                            continue
                        if meilleur is None or reste < meilleur[0]:
                            meilleur = (reste, x)
            if meilleur:
                if fin == 0: P[0] = meilleur[1]
                else: P[-1] = meilleur[1]
                st['caps'][fin] = 'B'   # bout franc, sans dépassement
    return sts

def A_barre(A, R):
    """8. A à partir de 600 : Ā, les deux traits s'arrêtent net sous la barre du haut (plus de croix au-dessus),
    et le A est étiré en hauteur : le haut de sa barre arrive au niveau des pointes des autres lettres."""
    H = 1000.0
    rh = R['rv'] * R['horiz']
    etire = (H + R['ov'] - rh) / H
    A = [dict(st, p=[np.array([p[0], p[1] * etire if p[1] > 0 else p[1]]) for p in st['p']]) for st in A]
    H = H * etire
    out = []
    for st in A:
        P = [np.array(p, float) for p in st['p']]
        if len(P) == 2 and abs(P[1][1] - P[0][1]) > 500:            # un des deux grands traits
            haut, bas = (1, 0) if P[1][1] > P[0][1] else (0, 1)
            a, b = P[bas], P[haut]
            t = (H - a[1]) / (b[1] - a[1])
            P[haut] = a + (b - a) * t
            caps = list(st['caps']); caps[haut] = 'B'
            out.append(dict(st, p=P, caps=caps))
        else:
            out.append(st)
    return out

def U_gras(ov):
    """7. U des graisses 700 et plus : panse ronde, le fût descend sous la ligne et la traverse."""
    S = techno.S; H = 1000.0; xr = 560.0
    panse = S((100, H + ov), (100, 0, 230), (xr, 0, 230), (xr, 520)); panse['caps'][1] = 'B'
    return [S((-60, H), (260, H)), S((xr - 80, H), (xr + 180, H)), panse, S((xr, H + ov), (xr, -ov))]

def u_gras(ov):
    """7. u des graisses 700 et plus : fond plat qui traverse le fût, croix en bas à droite."""
    S = techno.S; X = techno.XH; xr = 440.0
    return [S((-60, X), (200, X)), S((xr - 80, X), (xr + 140, X)),
            S((100, X + ov), (100, 0, 110), (xr + ov, 0)), S((xr, X + ov), (xr, -ov))]

def EF_court(G, R):
    """9. E et F à partir de 700 : la croix en bout de barre du haut, raccourcie (60 % en haut, 50 % en bas) et fine."""
    f = R['ov'] / 70.0; H = techno.H
    out = {}
    for ch in 'EF':
        sts = list(G[ch]); x = sts[2]['p'][0][0]
        sts[2] = dict(techno.S((x, H + techno.PC() * f * 0.6), (x, H - 110 * f * 0.5)), detail=True)
        out[ch] = sts
    return out

def glyphes(R):
    G = techno.build(R['ov'])
    G.update(techno.build_lc(R['ov'] * techno.XH / 1000.0))   # minuscules, croisements en proportion
    if R.get('poids', 900) >= 600:
        G['A'] = A_barre(G['A'], R)
    if R.get('poids', 900) >= 700:
        G['U'] = U_gras(R['ov'])
        G['u'] = u_gras(R['ov'] * techno.XH / 1000.0)
    if R.get('poids', 900) >= 700:
        G.update(EF_court(G, R))
    out = {}
    for ch, strokes in G.items():
        sts = [dict(p=[np.array([x * R['sx'], y]) for x, y in st['p']], caps=list(st['caps']), detail=st.get('detail', False)) for st in strokes]
        out[ch] = couper_biais(sts, R['ov']) if R.get('poids', 900) >= 500 else sts   # 6. à partir de 500
    return out

def render(word, out, R=REGLES, k=0.3, ss=3, triche=True):
    G = glyphes(R)
    GP = {ch: [st['p'] for st in v] for ch, v in G.items()}
    sauve = (essai.G, essai.cr, essai.GAP, essai.R)
    essai.G, essai.cr, essai.GAP, essai.R = GP, (lambda s, n=20: droit.dens(s)), R['gap'], R['rv']
    try:
        xs, end = essai.layout(word)
    finally:
        essai.G, essai.cr, essai.GAP, essai.R = sauve
    K = k * ss
    top, bot = 1500, -560
    W = int((end + 700) * K); H = int((top - bot) * K)
    img = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(img)
    for ch, ox in zip(word, xs):
        X = croisements(G[ch])
        for st in G[ch]:
            for q in contour_trait(st, X, R):
                d.polygon([((x + ox + 350) * K, (top - y) * K) for x, y in q], fill=238)
    img.resize((W // ss, H // ss), Image.LANCZOS).convert('RGB').save(out)

def planche_graisses(out, mot='LAFLEURSTUDIO', k=0.22):
    """Le mot dans les 9 graisses, de 100 à 900."""
    from PIL import ImageFont
    try:
        F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 34)
    except OSError:
        F = ImageFont.load_default()
    rows = []
    for p in range(100, 1000, 100):
        fn = out + f'.{p}.png'
        render(mot, fn, R=regles(p), k=k)
        im = Image.open(fn).convert('RGB'); ImageDraw.Draw(im).text((12, 8), str(p), font=F, fill=(255, 210, 60))
        rows.append(im); os.remove(fn)
    W = max(r.width for r in rows)
    sheet = Image.new('RGB', (W, sum(r.height for r in rows)), (0, 0, 0))
    y = 0
    for r in rows:
        sheet.paste(r, (0, y)); y += r.height
    sheet.save(out)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'graisses':
        planche_graisses(sys.argv[2] if len(sys.argv) > 2 else 'graisses.png')
    else:
        render(sys.argv[2] if len(sys.argv) > 2 else 'LAFLEURSTUDIO', sys.argv[1] if len(sys.argv) > 1 else 'nexum-900.png')
