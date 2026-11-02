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

if __name__ == '__main__':
    render(sys.argv[1] if len(sys.argv) > 1 else 'LAFLEURSTUDIO', sys.argv[2] if len(sys.argv) > 2 else 'techno.png')
