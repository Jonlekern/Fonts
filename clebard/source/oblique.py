# Italique penchée (oblique) d'une police finie : chaque contour est incliné autour de la mi-hauteur des minuscules,
# les chasses ne bougent pas, le crénage reste valable ; ancres des accents (GPOS mark) inclinées aussi.
import math, sys
from fontTools.ttLib import TTFont
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib.tables import otTables

def shear_fn(angle, y0):
    t = math.tan(math.radians(angle))
    return t, (lambda x, y: (x + (y - y0) * t, y))

def walk_anchors(obj, fn):
    from fontTools.ttLib.tables.otBase import BaseTable
    if isinstance(obj, otTables.Anchor):
        x, y = fn(obj.XCoordinate, obj.YCoordinate); obj.XCoordinate = round(x); return
    if isinstance(obj, list):
        for o in obj: walk_anchors(o, fn)
    elif isinstance(obj, BaseTable):
        for v in list(vars(obj).values()): walk_anchors(v, fn)

def make(src, dst, angle, style_it, ps_it):
    """style_it : nom du style italique (ex. « Krypton Italic ») ; ps_it : suffixe PostScript (ex. « KryptonItalic »)"""
    f = TTFont(src)
    y0 = f['OS/2'].sxHeight / 2 if getattr(f['OS/2'], 'sxHeight', 0) else 250
    t, fn = shear_fn(angle, y0)
    m = (1, 0, t, 1, -y0 * t, 0)
    gs = f.getGlyphSet(); hm = f['hmtx']
    if 'CFF ' in f:
        cff = f['CFF '].cff; td = cff.topDictIndex[0]; cs = td.CharStrings
        new = {}
        for g in f.getGlyphOrder():
            adv = hm[g][0]
            nom = getattr(td.Private, 'nominalWidthX', 0) or 0
            pen = T2CharStringPen(adv - nom, None)
            gs[g].draw(TransformPen(pen, m))
            c = pen.getCharString(private=td.Private, globalSubrs=td.GlobalSubrs)
            new[g] = c
        for g, c in new.items():
            cs[g] = c
        td.ItalicAngle = -angle
        # bornes
        for g in f.getGlyphOrder():
            bp = BoundsPen(f.getGlyphSet()); f.getGlyphSet()[g].draw(bp)
            hm[g] = (hm[g][0], round(bp.bounds[0]) if bp.bounds else 0)
    else:
        glyf = f['glyf']
        for g in f.getGlyphOrder():
            gl = glyf[g]
            if gl.isComposite():
                for c in gl.components:
                    c.x = round(c.x + c.y * t)
            elif gl.numberOfContours > 0:
                coords = gl.coordinates
                for i in range(len(coords)):
                    x, y = coords[i]; coords[i] = (round(x + (y - y0) * t), y)
            if hasattr(gl, 'program'):
                from fontTools.ttLib.tables import ttProgram
                gl.program = ttProgram.Program(); gl.program.fromBytecode(b'')
        for g in f.getGlyphOrder():
            gl = glyf[g]; gl.recalcBounds(glyf)
            hm[g] = (hm[g][0], gl.xMin if hasattr(gl, 'xMin') and gl.numberOfContours != 0 else 0)
        for tag in ('fpgm', 'cvt ', 'hdmx', 'LTSH', 'VDMX'):
            if tag in f: del f[tag]
    if 'GPOS' in f:
        walk_anchors(f['GPOS'].table, fn)
    f['post'].italicAngle = -angle
    f['hhea'].caretSlopeRise = 1000; f['hhea'].caretSlopeRun = round(1000 * t)
    f['head'].macStyle |= 0b10
    os2 = f['OS/2']; os2.fsSelection = (os2.fsSelection | 0x01) & ~0x40
    # noms
    n = f['name']
    fam16 = n.getDebugName(16) or n.getDebugName(1)
    old6 = n.getDebugName(6); fam_ps = old6.split('-')[0]
    psn = f'{fam_ps}-{ps_it}'; full = f'{fam16} {style_it}'
    old2 = n.getDebugName(2) or 'Regular'
    sub2 = 'Bold Italic' if old2 == 'Bold' else 'Italic'
    for r in list(n.names):
        nid = r.nameID
        if nid == 2: r.string = sub2
        elif nid == 3: r.string = r.toUnicode().replace(old6, psn)
        elif nid == 4: r.string = full
        elif nid == 6: r.string = psn
        elif nid == 17: r.string = style_it
        elif nid == 1:
            r.string = r.toUnicode()          # famille RIBBI inchangée (la graisse reste dans le nom 1)
    if 'CFF ' in f:
        cff = f['CFF '].cff; td = cff.topDictIndex[0]
        cff.fontNames = [psn]
        td.FullName = full.encode('ascii', 'ignore').decode()
    if 'STAT' in f: del f['STAT']
    f.save(dst)
    return dst

if __name__ == '__main__':
    make(sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4], sys.argv[5])
