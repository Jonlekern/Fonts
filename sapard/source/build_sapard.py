# Fabrique les fichiers Sapard (TTF + WOFF2) : 9 graisses, chacune en droit et en italique 16°.
#   python build_sapard.py <dossier_sortie>
import sys, os, math
import pathops
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.roundingPen import RoundingPen
from fontTools.pens.reverseContourPen import ReverseContourPen
from fontTools.pens.areaPen import AreaPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen
from fontTools.agl import UV2AGL
from fontTools.ttLib import TTFont
import fl

FAMILY = 'Sapard'
VERSION = 1.0
ITALIC_ANGLE = 16
ASC, DESC = 960, -260

def gname(ch):
    cp = ord(ch)
    if ch == ' ': return 'space'
    return UV2AGL.get(cp, 'uni%04X' % cp)

def clean(path, dx, shear):
    """Place le dessin (décalage dx, pente), arrondit, recolle, enlève les miettes."""
    t = math.tan(math.radians(shear)) if shear else 0.0
    y0 = fl.XH/2
    moved = pathops.Path()
    path.draw(RoundingPen(TransformPen(moved.getPen(), (1, 0, t, 1, dx - t*y0, 0))))
    moved = pathops.simplify(moved, fix_winding=True)
    out = pathops.Path(); pen = out.getPen()
    for c in moved.contours:
        a = AreaPen(); c.draw(a)
        if abs(a.value) >= 4: c.draw(pen)
    return out

def ttglyph(path):
    a = AreaPen(); path.draw(a)
    pen = TTGlyphPen(None)
    # TrueType : contours extérieurs dans le sens des aiguilles d'une montre
    path.draw(ReverseContourPen(pen) if a.value > 0 else pen)
    return pen.glyph()

def notdef():
    pen = TTGlyphPen(None)
    for pts in ([(50, 0), (50, 700), (450, 700), (450, 0)], [(100, 50), (400, 50), (400, 650), (100, 650)]):
        pen.moveTo(pts[0])
        for p in pts[1:]: pen.lineTo(p)
        pen.closePath()
    return pen.glyph()

def style_names(style, italic):
    if style in ('Regular', 'Bold', 'Italic', 'Bold Italic'): return FAMILY, style
    if italic: return f'{FAMILY} {style.replace(" Italic", "")}', 'Italic'
    return f'{FAMILY} {style}', 'Regular'

def build(name, weight, f, wx, italic, outdir):
    fl.set_weight(f, wx)
    shear = ITALIC_ANGLE if italic else 0
    style = (f'{name} Italic' if name != 'Regular' else 'Italic') if italic else name
    order = ['.notdef']; cmap = {}; glyphs = {'.notdef': notdef()}; hm = {'.notdef': (500, 50)}
    ymin, ymax = 0, 0
    for ch in sorted(fl.G, key=lambda c: (ord(c))):
        p, w, l, r = fl.G[ch]
        gn = gname(ch)
        path = clean(p, l, shear)
        g = ttglyph(path)
        bp = BoundsPen(None); path.draw(bp)
        adv = int(round(l + w + r))
        if bp.bounds:
            x0, y0, x1, y1 = bp.bounds
            ymin = min(ymin, y0); ymax = max(ymax, y1)
            hm[gn] = (adv, int(round(x0)))
        else:
            hm[gn] = (adv, 0)
        order.append(gn); glyphs[gn] = g; cmap[ord(ch)] = gn
    cmap[0x00A0] = 'space'
    fb = FontBuilder(1000, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyphs)
    fb.setupHorizontalMetrics(hm)
    run = int(round(math.tan(math.radians(shear))*1000)) if italic else 0
    fb.setupHorizontalHeader(ascent=ASC, descent=DESC, lineGap=0,
                             caretSlopeRise=1000 if italic else 1, caretSlopeRun=run)
    n1, n2 = style_names(style, italic)
    ps = f'{FAMILY}-{style.replace(" ", "")}'
    fb.setupNameTable({
        'copyright': 'Copyright 2026 LaFleurStudio, with Reserved Font Name "Sapard".',
        'familyName': n1, 'styleName': n2,
        'uniqueFontIdentifier': f'{VERSION:.3f};LFST;{ps}',
        'fullName': f'{FAMILY} {style}', 'psName': ps,
        'version': f'Version {VERSION:.3f}',
        'manufacturer': 'LaFleurStudio', 'designer': 'LaFleurStudio',
        'vendorURL': 'https://jonlekern.github.io/Fonts/',
        'licenseDescription': 'This Font Software is licensed under the SIL Open Font License, Version 1.1. This license is available with a FAQ at: https://openfontlicense.org',
        'licenseInfoURL': 'https://openfontlicense.org',
        'typographicFamily': FAMILY, 'typographicSubfamily': style,
    })
    fs = 0x80                                   # USE_TYPO_METRICS
    if italic: fs |= 0x01
    if weight == 700: fs |= 0x20
    if weight == 400 and not italic: fs |= 0x40
    fb.setupOS2(version=4, usWeightClass=weight, usWidthClass=5, achVendID='LFST', fsSelection=fs, fsType=0,
                sTypoAscender=ASC, sTypoDescender=DESC, sTypoLineGap=0,
                usWinAscent=int(math.ceil(max(ymax, ASC))), usWinDescent=int(math.ceil(max(-ymin, -DESC))),
                sxHeight=fl.XH, sCapHeight=fl.H, yStrikeoutPosition=int(fl.H*fl.MID), yStrikeoutSize=50,
                ulCodePageRange1=1)
    fb.setupPost(italicAngle=-shear if italic else 0, underlinePosition=-120, underlineThickness=50)
    fb.font['head'].macStyle = (1 if weight == 700 else 0) | (2 if italic else 0)
    fb.font['head'].fontRevision = VERSION
    fn = f'{FAMILY}-{style.replace(" ", "")}'
    os.makedirs(f'{outdir}/ttf', exist_ok=True); os.makedirs(f'{outdir}/woff2', exist_ok=True)
    fb.font.save(f'{outdir}/ttf/{fn}.ttf')
    w2 = TTFont(f'{outdir}/ttf/{fn}.ttf'); w2.flavor = 'woff2'; w2.save(f'{outdir}/woff2/{fn}.woff2')
    return fn

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'out'
    for name, weight, f, wx in fl.WEIGHTS:
        for italic in (False, True):
            print(build(name, weight, f, wx, italic, out))
