# Fûsard 032 : fabrique le fichier de police (TTF) à partir des traits dessinés dans fusard.py.
# Traits -> contours (union skia-pathops), approche par boîtes + crénage calculé sur les profils,
# chiffres majuscules par défaut, chiffres minuscules via « onum » (chiffres elzéviriens).
import sys, os, math
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fusard as techno, droit
import pathops
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.reverseContourPen import ReverseContourPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString

SC = 0.7                      # unités de dessin -> unités de police (majuscules à 700)
UPM = 1000
SB = 100                      # approche de chaque côté (écart d'encre par défaut : 200)
GAP = 2 * SB
INTR = 84                     # une lettre peut glisser sous sa voisine de 84 au plus
BAND = 14

NOMS = {
    '0': 'zero', '1': 'one', '2': 'two', '3': 'three', '4': 'four', '5': 'five', '6': 'six',
    '7': 'seven', '8': 'eight', '9': 'nine',
    '.': 'period', ',': 'comma', ':': 'colon', ';': 'semicolon', '!': 'exclam', '?': 'question',
    "'": 'quotesingle', '"': 'quotedbl', '‘': 'quoteleft', '’': 'quoteright',
    '“': 'quotedblleft', '”': 'quotedblright', '«': 'guillemotleft', '»': 'guillemotright',
    '‹': 'guilsinglleft', '›': 'guilsinglright', '-': 'hyphen', '–': 'endash', '—': 'emdash',
    '(': 'parenleft', ')': 'parenright', '[': 'bracketleft', ']': 'bracketright', '/': 'slash',
    '\\': 'backslash', '|': 'bar', '&': 'ampersand', '@': 'at', '#': 'numbersign', '*': 'asterisk',
    '+': 'plus', '=': 'equal', '%': 'percent', '_': 'underscore', '…': 'ellipsis', '·': 'periodcentered',
}

def nom(ch):
    if ch.isascii() and ch.isalpha():
        return ch
    return NOMS[ch]

def contours(strokes):
    """Union de tous les morceaux de traits, en unités de police."""
    p = pathops.Path()
    for st in strokes:
        for q in droit.outline_quads(st['p'], *st['caps']):
            pts = [(float(x) * SC, float(y) * SC) for x, y in q]
            p.moveTo(*pts[0])
            for pt in pts[1:]:
                p.lineTo(*pt)
            p.close()
    return pathops.simplify(p, fix_winding=True, keep_starting_points=False)

def profil(strokes, dx):
    """Bord gauche et droit de l'encre par bande horizontale (unités de police)."""
    r = droit.R * SC
    bands = {}
    for st in strokes:
        for x, y in droit.dens(st['p'], step=8.0):
            x = x * SC + dx; y = y * SC
            b = int(math.floor(y / BAND))
            for bb in (b - 1, b, b + 1):
                lo, hi = bands.get(bb, (1e9, -1e9))
                bands[bb] = (min(lo, x - r), max(hi, x + r))
    return bands

def glyphe_ttf(path, dx):
    rec = RecordingPen()
    path.draw(rec)
    pen = TTGlyphPen(None)
    # pathops donne les contours extérieurs dans le sens trigo : TrueType veut le sens horaire
    rp = ReverseContourPen(pen)
    for op, args in rec.value:
        args = [(round(x + dx), round(y)) for x, y in args]
        getattr(rp, op)(*args)
    return pen.glyph()

def notdef():
    w, h = 420, 700
    st = [techno.S((0, 0), (w / SC, 0)), techno.S((w / SC, 0), (w / SC, h / SC)),
          techno.S((w / SC, h / SC), (0, h / SC)), techno.S((0, h / SC), (0, 0))]
    for s in st:
        s['caps'] = ['T', 'T']
    return st

def construire(sortie):
    G = techno.G
    maj = techno.build_chiffres_maj(techno.OV_CHOISI)
    jeu = []   # (nom, unicode ou None, traits)
    jeu.append(('.notdef', None, notdef()))
    jeu.append(('space', 0x20, None))
    for ch in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz':
        jeu.append((ch, ord(ch), G[ch]))
    for ch in '0123456789':
        jeu.append((nom(ch), ord(ch), maj[ch]))                 # majuscules par défaut
    for ch in '0123456789':
        jeu.append((nom(ch) + '.onum', None, G[ch]))          # minuscules
    for ch in NOMS:
        if ch.isdigit(): continue
        jeu.append((nom(ch), ord(ch), G[ch]))

    glyphs, metrics, cmap, encre = {}, {}, {}, {}
    for n, u, st in jeu:
        if st is None:   # espace
            glyphs[n] = TTGlyphPen(None).glyph(); metrics[n] = (380, 0)
            if u: cmap[u] = n
            continue
        path = contours(st)
        xmin, ymin, xmax, ymax = path.bounds
        dx = SB - xmin
        glyphs[n] = glyphe_ttf(path, dx)
        adv = round(xmax - xmin + 2 * SB)
        metrics[n] = (adv, SB)
        encre[n] = (st, dx, xmax - xmin, ymin, ymax)
        if u: cmap[u] = n

    # crénage : on rapproche les paires dont les profils s'emboîtent (A V, L T, etc.)
    profils = {n: profil(e[0], e[1] - SB) for n, e in encre.items() if n != '.notdef'}
    noms = [n for n in profils]
    paires = []
    for a in noms:
        pa = profils[a]; wa = encre[a][2]
        for b in noms:
            pb = profils[b]
            need = -1e9
            for k, (l, h) in pb.items():
                if k in pa:
                    need = max(need, pa[k][1] - l + GAP)
            need = max(need, wa - INTR)
            kern = need - (wa + GAP)
            kern = int(round(kern / 10.0)) * 10
            if kern <= -20:
                paires.append((a, b, kern))

    order = [n for n, _, _ in jeu]
    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyphs)
    gl = fb.font['glyf']
    lsb = {}
    for n in order:
        g = gl[n]
        if g.numberOfContours:
            g.recalcBounds(gl); lsb[n] = g.xMin
        else:
            lsb[n] = 0
    fb.setupHorizontalMetrics({n: (metrics[n][0], lsb[n]) for n in order})
    ymax = max(e[4] for e in encre.values()); ymin = min(e[3] for e in encre.values())
    asc, desc = int(math.ceil(ymax / 10) * 10), int(math.floor(ymin / 10) * 10)
    fb.setupHorizontalHeader(ascent=asc, descent=desc)
    fam = 'Fûsard 032'
    fb.setupNameTable({
        'copyright': '© 2026 LaFleurStudio',
        'familyName': fam + ' Hairline', 'styleName': 'Regular',
        'typographicFamily': fam, 'typographicSubfamily': 'Hairline',
        'uniqueFontIdentifier': 'LaFleurStudio: Fûsard 032 Hairline: 0.100',
        'fullName': fam + ' Hairline', 'psName': 'Fusard032-Hairline',
        'version': 'Version 0.100', 'manufacturer': 'LaFleurStudio', 'designer': 'LaFleurStudio',
    })
    fb.setupOS2(sTypoAscender=850, sTypoDescender=-350, sTypoLineGap=0,
                usWinAscent=asc, usWinDescent=-desc, sxHeight=round(techno.XH * SC),
                sCapHeight=round(1000 * SC), achVendID='LFST', fsType=0, fsSelection=0x40,
                usWeightClass=100, ulCodePageRange1=1)
    fb.setupPost()
    from fontTools.misc.timeTools import timestampNow
    fb.setupHead(unitsPerEm=UPM, fontRevision=0.1, created=timestampNow(), modified=timestampNow())
    fea = []
    fea.append('languagesystem DFLT dflt;\nlanguagesystem latn dflt;\n')
    fea.append('feature onum {\n' + ''.join(f'  sub {nom(c)} by {nom(c)}.onum;\n' for c in '0123456789') + '} onum;\n')
    fea.append('feature kern {\n' + ''.join(f'  pos {a} {b} {k};\n' for a, b, k in paires) + '} kern;\n')
    addOpenTypeFeaturesFromString(fb.font, ''.join(fea))
    fb.save(sortie)
    return len(order), len(paires)

def essai(ttf, out):
    """Image d'essai écrite avec le vrai fichier de police (crénage et « onum » compris)."""
    from PIL import Image, ImageDraw, ImageFont, features
    moteur = ImageFont.Layout.RAQM if features.check('raqm') else ImageFont.Layout.BASIC
    F = ImageFont.truetype(ttf, 110, layout_engine=moteur)
    lignes = [('LAFLEURSTUDIO', []), ('lafleurstudio', []), ('ABCDEFGHIJKLM', []), ('NOPQRSTUVWXYZ', []),
              ('abcdefghijklm', []), ('nopqrstuvwxyz', []),
              ('0123456789', []), ('0123456789  (onum)', ['onum']),
              ('\u00abLAFLEUR STUDIO\u00bb : 132 !', []), ('(la fleur) & @studio #132 ?', [])]
    im = Image.new('RGB', (2600, 175 * len(lignes) + 60), (0, 0, 0)); d = ImageDraw.Draw(im)
    y = 30
    for t, feat in lignes:
        d.text((40, y), t, font=F, fill=(238, 238, 238), features=feat or None)
        y += 175
    im.save(out)

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'Fusard032-Hairline.ttf'
    n, k = construire(out)
    print(f'{out} : {n} glyphes, {k} paires de crénage')
    if len(sys.argv) > 2:
        essai(out, sys.argv[2])
