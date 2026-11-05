# Nexum, étape 2 (traits droits, sharp) : chaque trait de l'essai devient une suite de segments
# dont les angles sont pris dans les 8 règles, coins pointus (onglet), bouts coupés net.
import sys, math
import numpy as np
from PIL import Image, ImageDraw
import os
_ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _ICI)
import jalousia as essai
from etude import rdp

RULES = [0, 4, 8, 15, 40, 67, 77, 88]
import os
TOL = float(os.environ.get('TOL', 45))
MINSEG = float(os.environ.get('MINSEG', 70))
TIP = float(os.environ.get('TIP', 3.0))
R = 16.0

def merge_short(pts):
    pts = [np.array(p, float) for p in pts]
    changed = True
    while changed and len(pts) > 2:
        changed = False
        for i in range(len(pts) - 1):
            if np.linalg.norm(pts[i + 1] - pts[i]) < MINSEG:
                if i == 0:
                    del pts[1]
                elif i == len(pts) - 2:
                    del pts[-2]
                else:
                    m = (pts[i] + pts[i + 1]) / 2
                    pts[i] = m; del pts[i + 1]
                changed = True
                break
    return pts

def snap_dir(d):
    th = math.degrees(math.atan2(d[1], d[0]))
    left = abs(th) > 90
    a = th
    if a > 90: a -= 180
    if a <= -90: a += 180
    s = 1 if a >= 0 else -1
    b = min(RULES, key=lambda r: abs(abs(a) - r)) * s
    if left: b += 180
    r = math.radians(b)
    return np.array([math.cos(r), math.sin(r)]), b % 180

def straighten(stroke):
    P = essai.cr(stroke)
    pts = [P[i] for i in rdp(P, TOL)]
    pts = merge_short(pts)
    if len(pts) < 2:
        return pts
    # directions imposées ; segments consécutifs de même direction fusionnés
    segd = [snap_dir(q - p) for p, q in zip(pts, pts[1:])]
    orig = [pts[0]]; D = []
    for i, (u, key) in enumerate(segd):
        if D and abs(D[-1][1] - key) < 1e-6 and D[-1][0] @ u > 0:
            orig[-1] = pts[i + 1]
        else:
            D.append((u, key)); orig.append(pts[i + 1])
    D = [u for u, _ in D]
    n = len(D)
    # moindres carrés : v0 (2) + longueurs (n) pour coller aux sommets d'origine
    rows, rhs = [], []
    for k in range(n + 1):
        for ax in (0, 1):
            row = np.zeros(2 + n)
            row[ax] = 1
            for j in range(k):
                row[2 + j] = D[j][ax]
            rows.append(row); rhs.append(orig[k][ax])
    sol, *_ = np.linalg.lstsq(np.array(rows), np.array(rhs), rcond=None)
    v = [sol[:2]]
    for j in range(n):
        L = max(sol[2 + j], 20.0)
        v.append(v[-1] + D[j] * L)
    return v

def outline_quads(V, cap0='tip', cap1='tip', r=R, miter_limit=8.0):
    """Quadrilatères des segments, joints en onglet.
    Bouts : 'tip' = pointe, 'T' = prolongé de r (posé sur un autre trait)."""
    V = [np.array(p, float) for p in V]
    n = len(V) - 1
    U = [(V[i + 1] - V[i]) / np.linalg.norm(V[i + 1] - V[i]) for i in range(n)]
    N = [np.array([-u[1], u[0]]) for u in U]
    if cap0 == 'T': V[0] = V[0] - U[0] * r * 0.8
    if cap1 == 'T': V[-1] = V[-1] + U[-1] * r * 0.8
    def joint(i):
        if i == 0:
            return N[0] * r, -N[0] * r
        if i == n:
            return N[-1] * r, -N[-1] * r
        m = N[i - 1] + N[i]
        if np.linalg.norm(m) < 1e-9:
            m = U[i - 1]
        m = m / np.linalg.norm(m)
        L = min(r / max(m @ N[i], 1e-6), miter_limit * r)
        return m * L, -m * L
    J = [joint(i) for i in range(n + 1)]
    quads = []
    for i in range(n):
        a, b = V[i], V[i + 1]
        quads.append([a + J[i][0], b + J[i + 1][0], b + J[i + 1][1], a + J[i][1]])
    if TIP > 0 and cap0 == 'tip':
        t0 = min(TIP * r, 0.45 * np.linalg.norm(V[1] - V[0]))
        q = quads[0]; a = V[0] + U[0] * t0
        quads[0] = [a + J[0][0], q[1], q[2], a + J[0][1]]
        quads.append([V[0], a + J[0][0], a + J[0][1]])
    if TIP > 0 and cap1 == 'tip':
        t1 = min(TIP * r, 0.45 * np.linalg.norm(V[-1] - V[-2]))
        q = quads[n - 1]; b = V[-1] - U[-1] * t1
        quads[n - 1] = [q[0], b + J[n][0], b + J[n][1], q[3]]
        quads.append([b + J[n][0], V[-1], b + J[n][1]])
    return quads

REACH = 200.0  # un bout à moins de REACH d'un autre trait (dans sa direction) va s'y poser
BACK = 10.0    # on ne raccourcit pas un trait qui dépasse (croisements voulus)

def connect(strokes):
    S = [dict(p=[np.array(v, float) for v in st], caps=['tip', 'tip']) for st in strokes if len(st) >= 2]
    corners = []
    for i, st in enumerate(S):
        for e in (0, 1):
            P = st['p']
            p = P[-1] if e else P[0]
            u = (P[-1] - P[-2]) if e else (P[0] - P[1])
            u = u / np.linalg.norm(u)
            best = None
            for j, o in enumerate(S):
                if j == i: continue
                Q = o['p']
                for k in range(len(Q) - 1):
                    a, b = Q[k], Q[k + 1]
                    d = b - a
                    M = np.array([[u[0], -d[0]], [u[1], -d[1]]])
                    if abs(np.linalg.det(M)) < 1e-9: continue
                    t, sg = np.linalg.solve(M, a - p)
                    if -BACK <= t <= REACH and -0.06 <= sg <= 1.06:
                        if best is None or abs(t) < abs(best[0]):
                            best = (t, j, k, sg)
            if best is None: continue
            t, j, k, sg = best
            hit = p + u * t
            Q = S[j]['p']
            if (k == 0 and sg < 0.12 and np.linalg.norm(Q[0] - hit) < 30):
                corners.append((i, e, j, 0, hit))
            elif (k == len(Q) - 2 and sg > 0.88 and np.linalg.norm(Q[-1] - hit) < 30):
                corners.append((i, e, j, 1, hit))
            else:
                if e: P[-1] = hit
                else: P[0] = hit
                st['caps'][e] = 'T'
    # coins : les deux bouts vont au même point, puis on soude les deux traits
    for i, e, j, f, hit in corners:
        for (si, ei) in ((i, e), (j, f)):
            if ei: S[si]['p'][-1] = hit.copy()
            else: S[si]['p'][0] = hit.copy()
    merged = True
    while merged:
        merged = False
        for i in range(len(S)):
            for j in range(len(S)):
                if i == j: continue
                A, B = S[i], S[j]
                for ea in (0, 1):
                    for eb in (0, 1):
                        pa = A['p'][-1] if ea else A['p'][0]
                        pb = B['p'][-1] if eb else B['p'][0]
                        if np.linalg.norm(pa - pb) < 1e-6 and A['caps'][ea] == 'tip' and B['caps'][eb] == 'tip':
                            Ap = A['p'] if ea else A['p'][::-1]
                            Ac = A['caps'] if ea else A['caps'][::-1]
                            Bp = B['p'] if not eb else B['p'][::-1]
                            Bc = B['caps'] if not eb else B['caps'][::-1]
                            S[i] = dict(p=list(Ap) + list(Bp[1:]), caps=[Ac[0], Bc[1]])
                            del S[j]
                            merged = True
                            break
                    if merged: break
                if merged: break
            if merged: break
    return S

G2s = {ch: connect([straighten(s) for s in strokes]) for ch, strokes in essai.G.items()}
G2 = {ch: [st['p'] for st in v] for ch, v in G2s.items()}

def dens(pts, step=10.0):
    P = np.array(pts, float)
    out = [P[0]]
    for p, q in zip(P, P[1:]):
        k = max(int(np.linalg.norm(q - p) / step), 1)
        for t in np.linspace(0, 1, k + 1)[1:]:
            out.append(p * (1 - t) + q * t)
    return np.array(out)

def render(word, out, k=0.3, ss=3):
    G0, cr0 = essai.G, essai.cr
    essai.G, essai.cr = G2, lambda s, n=20: dens(s)
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
        for st in G2s[ch]:
            for q in outline_quads(st['p'], *st['caps']):
                d.polygon([((x + ox + 300) * K, (top - y) * K) for x, y in q], fill=238)
    img.resize((W // ss, H // ss), Image.LANCZOS).convert('RGB').save(out)

if __name__ == '__main__':
    render(sys.argv[1] if len(sys.argv) > 1 else 'LAFLEURSTUDIO', sys.argv[2] if len(sys.argv) > 2 else 'droit.png')
    for ch in dict.fromkeys('LAFLEURSTUDIO'):
        segs = []
        for V in G2[ch]:
            for p, q in zip(V, V[1:]):
                a = math.degrees(math.atan2(q[1] - p[1], q[0] - p[0]))
                if a > 90: a -= 180
                if a <= -90: a += 180
                segs.append(round(a))
        print(ch, segs)
