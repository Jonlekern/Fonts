# 1400 « trichée » : là où la 1400 casse, on reprend la 1200 (Trenta) épaissie à l'horizontale seulement
import sys, re, pathops
from fontTools.ttLib import TTFont
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

SRC, F1400, LOG1400, F1200, OUT = sys.argv[1:6]
code = open('build_clebard.py').read().split("def holes_area")[0]
ns = {}; sys.argv = ['x', SRC, '/dev/null', '1.4', '1400']; exec(code, ns)
topo, components, offset, bounds, grow, contours, area = (ns[k] for k in ('topo', 'components', 'offset', 'bounds', 'grow', 'contours', 'area'))
GX14, gs = ns['GX'], ns['gs']
GX12 = 17.5; DX = GX14 - GX12            # 19 de chaque côté : fûts 1200 -> 1400
DY = DX / 4                               # un soupçon vertical (rapport d'ellipse raisonnable), recalé ensuite
KY = 729 / (729 + 2 * DY)

need = sorted(set(re.findall(r'^  (?:NON RÉSOLU )?(\S+?)(?::| *$)', open(LOG1400).read(), re.M)))
need = [n for n in need if n in gs]
f12 = TTFont(F1200); g12 = f12.getGlyphSet()
f = TTFont(F1400); cs = f['CFF '].cff.topDictIndex[0].CharStrings
g14 = f.getGlyphSet()
def white(gset, n, dx):
    """blanc intérieur : trous + creux fermés par un disque de 60"""
    p = pathops.Path(); gset[n].draw(TransformPen(p.getPen(glyphSet=gset), (1, 0, 0, 1, -dx, 0))); p.simplify(fix_winding=True)
    if not bounds(p): return 0
    try: w = ns['diff'](offset(offset(p, 60, 60), -60, -60), p)
    except pathops.PathOpsError: return 0
    return sum(abs(area(c)) for c in contours(w)) if bounds(w) else 0
extra = []
for n in f.getGlyphOrder():
    if n in need or n not in g12: continue
    w12 = white(g12, n, GX12)
    if w12 > 3000 and white(g14, n, GX14) < 0.5 * w12: extra.append(n)
print('blancs bouchés en 1400 :', len(extra), ' '.join(extra[:40]))
need = sorted(set(need) | set(extra))
done, fails = [], []
for n in need:
    G12 = pathops.Path(); g12[n].draw(TransformPen(G12.getPen(glyphSet=g12), (1, 0, 0, 1, -GX12, 0))); G12.simplify(fix_winding=True)
    if not bounds(G12): continue
    t12 = topo(G12)
    C = None
    for fx in (1.0, 0.75, 0.5):
        try: c_ = offset(G12, DX * fx, DY * fx)
        except pathops.PathOpsError: continue
        if topo(c_) == t12: C, used = c_, fx; break
    if C is None:                          # rien ne tient : on garde la 1200 telle quelle
        fails.append(n); C, used = G12, 0.0
    adv = f['hmtx'][n][0]
    t2 = T2CharStringPen(adv, None)
    C.draw(TransformPen(t2, (1, 0, 0, 729 / (729 + 2 * DY * used), GX14, DY * used * 729 / (729 + 2 * DY * used))))
    cs[n] = t2.getCharString(private=cs[n].private, globalSubrs=cs[n].globalSubrs)
    done.append(n)
gs2 = f.getGlyphSet()
for n in done:
    bp = BoundsPen(gs2); gs2[n].draw(bp)
    f['hmtx'][n] = (f['hmtx'][n][0], round(bp.bounds[0]) if bp.bounds else 0)
f.save(OUT)
print('repris de la 1200 épaissie', len(done) - len(fails), '| 1200 telle quelle', len(fails), ':', ' '.join(fails))
