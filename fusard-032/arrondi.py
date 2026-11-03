# Fûsard-032, étape 3 (sharp + arrondis) : les lettres rondes (D, U, S, R) gardent leurs segments
# aux angles des règles, mais chaque coin devient un arc tangent (courbe continue) ;
# le O est une ogive : deux arcs de cercle qui se croisent en pointe.
import sys, math
import numpy as np
from PIL import Image, ImageDraw
import os
_ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _ICI)
import jalousia as essai
import droit

ROUND = {'U': [1], 'R': [1], 'S': [0], 'D': [1]}
F_SHARED, F_END = 0.5, 0.85

def fillet(V, nseg=18):
    V = [np.array(p, float) for p in V]
    n = len(V)
    if n < 3:
        return V
    L = [np.linalg.norm(V[i + 1] - V[i]) for i in range(n - 1)]
    out = [V[0]]
    for i in range(1, n - 1):
        a, b, c = V[i - 1], V[i], V[i + 1]
        u1 = (b - a) / L[i - 1]; u2 = (c - b) / L[i]
        cosT = np.clip(u1 @ u2, -1, 1)
        turn = math.acos(cosT)            # angle de virage
        if turn < 1e-3:
            out.append(b); continue
        fp = F_END if i - 1 == 0 else F_SHARED
        fn = F_END if i + 1 == n - 1 else F_SHARED
        t = min(fp * L[i - 1], fn * L[i])
        rad = t / math.tan(turn / 2)
        p1 = b - u1 * t; p2 = b + u2 * t
        nrm = np.array([-u1[1], u1[0]])
        if u1[0] * u2[1] - u1[1] * u2[0] < 0: nrm = -nrm
        ctr = p1 + nrm * rad
        a1 = math.atan2(*(p1 - ctr)[::-1]); a2 = math.atan2(*(p2 - ctr)[::-1])
        da = (a2 - a1 + math.pi) % (2 * math.pi) - math.pi
        for k in range(nseg + 1):
            ang = a1 + da * k / nseg
            out.append(ctr + rad * np.array([math.cos(ang), math.sin(ang)]))
    out.append(V[-1])
    # retirer les points en double
    clean = [out[0]]
    for p in out[1:]:
        if np.linalg.norm(p - clean[-1]) > 1e-6:
            clean.append(p)
    return clean

def ogive(cx=315.0, top=1010.0, bot=-5.0, w=245.0, over=70.0, nseg=60):
    cy = (top + bot) / 2; h = (top - bot) / 2
    a = (h * h - w * w) / (2 * w); rho = a + w
    phi = math.atan2(h, a)          # angle du sommet vu du centre
    d = over / rho
    left, right = [], []
    for k in range(nseg + 1):
        t = (math.pi - phi - d) + (2 * phi + 2 * d) * k / nseg
        left.append(np.array([cx + a + rho * math.cos(t), cy + rho * math.sin(t)]))
        t2 = (phi + d) - (2 * phi + 2 * d) * k / nseg
        right.append(np.array([cx - a + rho * math.cos(t2), cy + rho * math.sin(t2)]))
    return [dict(p=left, caps=['tip', 'tip']), dict(p=right, caps=['tip', 'tip'])]

def build():
    G3s = {}
    for ch, strokes in essai.G.items():
        if ch == 'O':
            G3s[ch] = ogive(); continue
        st = [droit.straighten(s) for s in strokes]
        for i in ROUND.get(ch, []):
            st[i] = fillet(st[i])
        G3s[ch] = droit.connect(st)
    return G3s

G3s = build()
G3 = {ch: [s['p'] for s in v] for ch, v in G3s.items()}

def render(word, out, k=0.3, ss=3):
    G0, cr0 = essai.G, essai.cr
    essai.G, essai.cr = G3, lambda s, n=20: droit.dens(s)
    try:
        xs, end = essai.layout(word)
    finally:
        essai.G, essai.cr = G0, cr0
    K = k * ss
    top, bot = 1250, -350
    W = int((end + 600) * K); H = int((top - bot) * K)
    img = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(img)
    for ch, ox in zip(word, xs):
        for st in G3s[ch]:
            for q in droit.outline_quads(st['p'], *st['caps']):
                d.polygon([((x + ox + 300) * K, (top - y) * K) for x, y in q], fill=238)
    img.resize((W // ss, H // ss), Image.LANCZOS).convert('RGB').save(out)

if __name__ == '__main__':
    render(sys.argv[1] if len(sys.argv) > 1 else 'LAFLEURSTUDIO', sys.argv[2] if len(sys.argv) > 2 else 'arrondi.png')
