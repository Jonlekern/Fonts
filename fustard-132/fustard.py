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
    return out

def S(*pts):
    return dict(p=path(pts), caps=['tip', 'tip'])

H = 1000

def build(ov=70.0):
    f = ov / 70.0
    G = {}
    G['L'] = [S((0, H + ov), (0, -ov)),
              S((-150, H), (330, H)),
              S((-ov, 0), (560, 0))]
    # A : celui de la version sharp, gardé tel quel
    G['A'] = arrondi.G3s['A']
    G['F'] = [S((120, H + ov), (120, -ov)),
              S((0, H), (560, H)),
              S((560 - 30 * f, H + 90 * f), (560 - 30 * f, H - 110 * f)),
              S((120 - ov, 520), (440, 520)),
              S((-30, 0), (290, 0))]
    G['E'] = [S((0, H + ov), (0, -ov)),
              S((-ov, H), (540, H)),
              S((540 - 30 * f, H + 90 * f), (540 - 30 * f, H - 110 * f)),
              S((-ov, 510), (420, 510)),
              S((-ov, 0), (560, 0))]
    xr = 560
    yb = (xr - 360) * T67
    G['U'] = [S((-60, H), (260, H)),
              S((100, H + ov), (100, 0, 130), (360, 0, 150), (xr + ov * C67, yb + ov * S67)),
              S((xr, H + ov), (xr, 0)),
              S((xr - 80, H), (xr + 180, H))]
    xl = 260 + 480 / T67
    G['R'] = [S((0, H + ov), (0, 0)),
              S((-ov, H), (480, H, 240), (480, 480, 240), (-ov, 480)),
              S((-ov + 30 * f, 480 + 80 * f), (-ov + 30 * f, 480 - 80 * f)),
              S((260 - ov * C67, 480 + ov * S67), (xl + ov * C67, -ov * S67)),
              S((xl - 110, 0), (xl + 150, 0))]
    G['S'] = [S((560, H), (40, H, 160), (40, 700, 120), (520, 220, 170), (520, 0, 170), (0, 0)),
              S((560 - 30 * f, H + 90 * f), (560 - 30 * f, H - 110 * f)),
              S((30 * f, 110 * f), (30 * f, -90 * f))]
    G['T'] = [S((0, H), (700, H)),
              S((350, H + ov), (350, -ov)),
              S((200, 0), (500, 0))]
    r2 = math.sqrt(0.5)
    G['D'] = [S((0, H + ov), (0, -ov)),
              S((-ov * r2, H + ov * r2), (520, H - 520 - ov * r2 + 0.0, 220), (520, 0, 220), (-ov, 0))]
    G['I'] = [S((0, H + ov), (0, -ov)),
              S((-200, H), (200, H)),
              S((-220, 0), (220, 0))]
    G['O'] = arrondi.ogive(over=ov)

    # ---- le reste de l'alphabet ----
    def croix_haut(x, y):   # petite croix verticale en bout de barre (E, F, S)
        return S((x, y + 90 * f), (x, y - 110 * f))
    def croix_bas(x, y):
        return S((x, y + 110 * f), (x, y - 90 * f))
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
              S((-ov + 30 * f, 440 + 80 * f), (-ov + 30 * f, 440 - 80 * f)),
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
    Ov = arrondi.ogive(over=ov)
    cxq, hq, wq = 315.0, 507.5, 245.0
    aq = (hq * hq - wq * wq) / (2 * wq); rq = aq + wq; cyq = 502.5
    phq = math.atan2(hq, aq)
    t0, t1 = math.pi - phq - ov / rq, math.pi + phq + 520 / rq
    queue = [np.array([cxq + aq + rq * math.cos(t), cyq + rq * math.sin(t)]) for t in np.linspace(t0, t1, 120)]
    tc = t1 - 30 * f / rq
    xc, yc_ = cxq + aq + rq * math.cos(tc), cyq + rq * math.sin(tc)
    G['Q'] = [dict(p=queue, caps=['tip', 'tip']), Ov[1], S((xc, yc_ + 55 * f), (xc, yc_ - 45 * f))]   # croix moitié plus courte
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
    return G

OV_CHOISI = 210.0   # niveau 2 (croisements x3), choisi
G = build(OV_CHOISI)
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
    top, bot = 1380, -420
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

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'alphabet':
        planche(sys.argv[2] if len(sys.argv) > 2 else 'alphabet.png')
    else:
        render(sys.argv[1] if len(sys.argv) > 1 else 'LAFLEURSTUDIO', sys.argv[2] if len(sys.argv) > 2 else 'fustard-132.png')
