# nettoyage des contours (union, petits contours, points alignés)
import math
from fontTools.pens.recordingPen import RecordingPen
from ball_geom import P

def clean(p, amin=12):
    try: p.simplify(fix_winding=True, clockwise=False)
    except Exception: return p
    rp = RecordingPen(); p.draw(rp); out = P(); pen = out.getPen(); cur = []; keep = []
    for op, a in rp.value:
        if op == 'moveTo': cur = [(op, a)]
        elif op in ('closePath', 'endPath'): cur.append((op, a)); keep.append(cur); cur = []
        else: cur.append((op, a))
    def area(c):
        pts = [a[-1] for op, a in c if a]
        return abs(sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts))) / 2) if len(pts) > 2 else 0
    def straighten(c):
        if not all(op in ('moveTo', 'lineTo', 'closePath', 'endPath') for op, a in c):
            changed = True
            while changed:
                changed = False
                for i in range(1, len(c) - 1):
                    op, a = c[i]
                    if op != 'lineTo' or c[i + 1][0] != 'lineTo': continue
                    p0 = c[i - 1][1][-1]; p1 = a[0]; p2 = c[i + 1][1][0]
                    ux, uy = p1[0] - p0[0], p1[1] - p0[1]; vx, vy = p2[0] - p1[0], p2[1] - p1[1]
                    lu, lv = math.hypot(ux, uy), math.hypot(vx, vy)
                    if lu and lv and abs(ux * vy - uy * vx) / (lu * lv) < 1e-3 and ux * vx + uy * vy > 0:
                        del c[i]; changed = True; break
            return c
        pts = [a[0] for op, a in c if op in ('moveTo', 'lineTo')]
        if len(pts) > 1 and pts[0] == pts[-1]: pts = pts[:-1]
        changed = True
        while changed and len(pts) > 3:
            changed = False
            for i in range(len(pts)):
                p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % len(pts)]
                ux, uy = p1[0] - p0[0], p1[1] - p0[1]; vx, vy = p2[0] - p1[0], p2[1] - p1[1]
                lu, lv = math.hypot(ux, uy), math.hypot(vx, vy)
                if lu == 0 or (lv and abs(ux * vy - uy * vx) / (lu * lv) < 1e-3 and ux * vx + uy * vy > 0):
                    del pts[i]; changed = True; break
        return [('moveTo', (pts[0],))] + [('lineTo', (p,)) for p in pts[1:]] + [('closePath', ())]
    for c in keep:
        if area(c) < amin: continue
        for op, a in straighten(c): getattr(pen, op)(*a)
    return out

