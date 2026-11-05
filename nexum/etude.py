# Nexum, étape 1 : étude des angles du LAFLEURSTUDIO de l'essai Jalousia.
# Chaque trait est simplifié en segments droits (Ramer-Douglas-Peucker),
# puis on mesure l'angle de chaque segment.
# Angle : 0 = horizontal, 90 = vertical ; + = monte vers la droite.
import math, sys, json
import numpy as np
import os
_ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _ICI)
import jalousia as essai

TOL = 20.0
MINLEN = 40.0

def rdp(P, tol):
    if len(P) < 3:
        return [0, len(P) - 1]
    a, b = P[0], P[-1]
    d = b - a; L = np.linalg.norm(d)
    if L < 1e-9:
        dist = np.linalg.norm(P - a, axis=1)
    else:
        n = np.array([-d[1], d[0]]) / L
        dist = np.abs((P - a) @ n)
    i = int(np.argmax(dist))
    if dist[i] > tol:
        left = rdp(P[:i + 1], tol)
        right = rdp(P[i:], tol)
        return left[:-1] + [j + i for j in right]
    return [0, len(P) - 1]

def angle(p, q):
    a = math.degrees(math.atan2(q[1] - p[1], q[0] - p[0]))
    if a > 90: a -= 180
    if a <= -90: a += 180
    return a

def study(word='LAFLEURSTUDIO'):
    out = {}
    for ch in dict.fromkeys(word):
        segs = []
        for si, s in enumerate(essai.G[ch]):
            P = essai.cr(s)
            idx = rdp(P, TOL)
            pts = [P[i] for i in idx]
            for p, q in zip(pts, pts[1:]):
                L = float(np.linalg.norm(q - p))
                segs.append(dict(stroke=si, p=[float(p[0]), float(p[1])], q=[float(q[0]), float(q[1])],
                                 length=L, angle=angle(p, q), short=L < MINLEN))
        out[ch] = segs
    return out

if __name__ == '__main__':
    res = study()
    json.dump(res, open('etude.json', 'w'), indent=1)
    allang = []
    for ch, segs in res.items():
        line = []
        for s in segs:
            if s['short']: continue
            a = s['angle']
            line.append(f"{a:6.1f}({s['length']:.0f})")
            allang.append((a, s['length'], ch))
        print(ch, ' '.join(line))
    print('segments:', len(allang))
    # histogramme pondéré par la longueur, sur |angle| replié (fûts = penche depuis la verticale)
    A = np.array([abs(a) for a, _, _ in allang]); W = np.array([l for _, l, _ in allang])
    for lo in range(0, 91, 5):
        m = (A >= lo) & (A < lo + 5)
        print(f'{lo:2d}-{lo+5:2d}° ', '#' * int(W[m].sum() / 100), f'{int(m.sum())} seg')
