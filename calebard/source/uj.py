"""Calebard : U moins large (−200 en Black) et queue du J plus courte (−450 en Black).
Les montants sont proportionnels dans chaque graisse. Dans Goofy et Extra Goofy, les glyphes touchés sont refaits avec build_goofy.py / build_extra_goofy.py depuis le nouveau Black.
usage : uj.py <dossier ttf source> <dossier ttf sortie>"""
import sys, math, os
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.boundsPen import BoundsPen

SRC, OUT = (sys.argv[1:3] + [None, None])[:2] if __name__ == '__main__' else (None, None)
REF_U, REF_J = 200 / 2509, 450 / 1174          # choix faits sur le Black : U −200 sur 2509, queue J −450 sur 1174
WEIGHTS = ['Hairline', 'Thin', 'Light', 'Regular', 'Medium', 'Bold', 'ExtraBold', 'SuperBold', 'Black', 'ExtraBlack', 'ExtremeBlack']

def center_x(g):
    """x du milieu : le point « sur la courbe » le plus bas (bas du bol)."""
    on = [p for p, fl in zip(g.coordinates, g.flags) if fl & 1]
    low = min(y for _, y in on); pts = [x for x, y in on if y == low]
    assert len(pts) == 1, pts
    return pts[0]

def zone(x, cx, half):
    tol = 0.25 * half
    return 'mid' if abs(x - cx) <= tol else ('right' if x > cx else 'left')

def shift(z, d): return {'left': 0, 'mid': -d / 2, 'right': -d}[z]

def process(path, outpath):
    f = TTFont(path); glyf, hmtx = f['glyf'], f['hmtx']
    info = {}
    for base, ref in (('U', 'U'), ('J', 'J'), ('J.ss01', 'J')):
        g = glyf[base]; c = g.coordinates; cx = center_x(g)
        xs = [x for x, _ in c]; half = cx - min(xs)
        if ref == 'U': d = round(REF_U * (max(xs) - min(xs)))
        elif base == 'J': d = round(REF_J * half)
        else: d = info['J'][2]                      # J.ss01 : même raccourci que le J
        new = []
        for x, y in c:
            z = 'mid' if abs(x - cx) <= 1 else ('right' if x > cx else 'left')
            new.append((x + shift(z, d), y))
        # contrôle : les points de contrôle restent du bon côté du milieu
        ncx = cx - d / 2
        for (x, y), (nx, ny) in zip(c, new):
            if abs(x - cx) > 1: assert (nx - ncx) * (x - cx) > 0, (path, base, x, y)
        for i, p in enumerate(new): c[i] = (round(p[0]), p[1])
        g.recalcBounds(glyf)
        hmtx[base] = (hmtx[base][0] - d, hmtx[base][1])
        info[base] = (cx, half, d)
    touched = set(info)
    for n in f.getGlyphOrder():
        g = glyf[n]
        if not g.isComposite(): continue
        names = [k.glyphName for k in g.components]
        if names[0] in info:
            cx, half, d = info[names[0]]
            for k in g.components[1:]:
                bp = BoundsPen(f.getGlyphSet()); f.getGlyphSet()[k.glyphName].draw(bp)
                mc = (bp.bounds[0] + bp.bounds[2]) / 2 + k.x if bp.bounds else k.x
                k.x = round(k.x + shift(zone(mc, cx, half), d))
            hmtx[n] = (hmtx[n][0] - d, hmtx[n][1]); touched.add(n)
        elif names[-1] in info and any(m in info for m in names):   # IJ, LJ, NJ : le J est à la fin
            hmtx[n] = (hmtx[n][0] - info[names[-1]][2], hmtx[n][1]); touched.add(n)
        g.recalcBounds(glyf)
    # ancres des accents (GPOS mark)
    for lk in f['GPOS'].table.LookupList.Lookup:
        if lk.LookupType != 4: continue
        for st in lk.SubTable:
            bc = st.BaseCoverage.glyphs
            for n in touched:
                if n not in bc: continue
                base = n if n in info else glyf[n].components[0].glyphName
                if base not in info: continue
                cx, half, d = info[base]
                for a in st.BaseArray.BaseRecord[bc.index(n)].BaseAnchor:
                    if a is not None: a.XCoordinate = round(a.XCoordinate + shift(zone(a.XCoordinate, cx, half), d))
    f['OS/2'].recalcAvgCharWidth(f)
    f.save(outpath)
    return info, touched

def redo_fun(fresh_path, fun_path, outpath, touched, info):
    """Copie dans Goofy / Extra Goofy les glyphes touchés, refaits par le script d'origine depuis le nouveau Black."""
    A = TTFont(fresh_path); F = TTFont(fun_path); glyf, hmtx = F['glyf'], F['hmtx']
    sfx = ('', '.goofy', '.eg1', '.eg2', '.eg3', '.eg4', '.eg5')
    names = [n + x for n in touched for x in sfx if n + x in F.getGlyphOrder()]
    for n in names:
        glyf[n] = A['glyf'][n]; hmtx[n] = A['hmtx'][n]
    for lk in F['GPOS'].table.LookupList.Lookup:
        if lk.LookupType != 4: continue
        for st in lk.SubTable:
            bc = st.BaseCoverage.glyphs
            for name in bc:
                n = name.split('.goofy')[0].split('.eg')[0]
                if n not in touched: continue
                base = n if n in info else A['glyf'][n].components[0].glyphName if A['glyf'][n].isComposite() else None
                if base not in info: continue
                cx, half, d = info[base]
                for a in st.BaseArray.BaseRecord[bc.index(name)].BaseAnchor:
                    if a is not None: a.XCoordinate = round(a.XCoordinate + shift(zone(a.XCoordinate, cx, half), d))
    F['OS/2'].recalcAvgCharWidth(F)
    F.save(outpath)
    return len(names)

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for w in WEIGHTS:
        info, touched = process(f'{SRC}/Calebard-{w}.ttf', f'{OUT}/Calebard-{w}.ttf')
        if w == 'Black': black_info, black_touched = info, touched
        print(w, {k: v[2] for k, v in info.items()}, len(touched))
    import subprocess, tempfile
    here = os.path.dirname(os.path.abspath(__file__))
    for fun, script in (('Goofy', 'build_goofy.py'), ('ExtraGoofy', 'build_extra_goofy.py')):
        tmp = os.path.join(tempfile.mkdtemp(), 'fresh.ttf')
        subprocess.run([sys.executable, os.path.join(here, script), f'{OUT}/Calebard-Black.ttf', tmp], check=True, capture_output=True)
        print(fun, redo_fun(tmp, f'{SRC}/Calebard-{fun}.ttf', f'{OUT}/Calebard-{fun}.ttf', black_touched, black_info), 'glyphes refaits')
