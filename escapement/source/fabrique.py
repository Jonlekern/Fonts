# La fabrique d'Escapement : une graisse (droite ou italique) -> OTF + WOFF2.
import os, math
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.otlLib.builder import buildStatTable
from fontTools.ttLib import TTFont
from mesures import mesures, NOMS, GRAISSES
from pieces import transforme
from glyphes import tous, nom, TOUTES_CAPS, NOMS_CHIFFRES
from lettres import ESSAI_MIN, PLUS_MIN, CAPS_TOUTES
from accents import ACCENTUEES, COMBINANTS
import crenage

FAMILLE = 'Escapement'
PENTE = 10                       # degrés
LICENCE = 'Free for personal use. Commercial use requires prior written permission from LaFleurStudio'
ASC, DESC = 950, -250            # lignes de texte : 1,2 em


def lisse(p):
    """Contour en unités entières, sans point en double ni segment de moins de 2 unités (les petites marches)."""
    rp = RecordingPen(); p.draw(rp); out = []; cur = []
    R = lambda q: (round(q[0]), round(q[1]))
    for op, a in rp.value:
        if op == 'moveTo':
            cur = [('moveTo', (R(a[0]),))]
        elif op == 'lineTo':
            q = R(a[0]); prev = cur[-1][1][-1]
            dx, dy = abs(q[0] - prev[0]), abs(q[1] - prev[1])
            if 0 < dy <= 2 and dx >= 10:
                q = (q[0], prev[1])
            elif 0 < dx <= 2 and dy >= 10:
                q = (prev[0], q[1])
            if abs(q[0] - prev[0]) + abs(q[1] - prev[1]) >= 2:
                cur.append(('lineTo', (q,)))
        elif op == 'curveTo':
            cur.append(('curveTo', tuple(R(q) for q in a)))
        elif op in ('closePath', 'endPath'):
            if len(cur) > 2:
                first = cur[0][1][0]; last = cur[-1][1][-1]
                if cur[-1][0] == 'lineTo' and abs(last[0] - first[0]) + abs(last[1] - first[1]) < 2:
                    cur.pop()
                out.extend(cur); out.append(('closePath', ()))
            cur = []
    return out


def penche(p):
    k = math.tan(math.radians(PENTE))
    return transforme(p, (1, 0, k, 1, -k * 250, 0))


def _classe(noms):
    return '[' + ' '.join(noms) + ']'


def code_calt(glyphs):
    """La règle du début de phrase (calt) et ss01 (toutes les capitales en version Overshoot)."""
    caps = [nom(c) for c in TOUTES_CAPS]
    ovs = [n + '.ovs' for n in caps]
    lettres = [nom(c) for c in ESSAI_MIN + PLUS_MIN + ''.join(ACCENTUEES)] + caps + ovs + NOMS_CHIFFRES
    lettres = [n for n in lettres if n in glyphs]
    mins = [nom(c) for c in ESSAI_MIN + PLUS_MIN + ''.join(c for c in ACCENTUEES if c.islower())]
    esp = [nom(' '), nom(' ')]
    milieu = lettres + [nom(c) for c in ',:;-–—'] + ['quoteright', 'quotesingle']
    ouvrants = esp + [nom(c) for c in '(«“‘"\'[-–—/']
    # les abréviations (FR, DE, EN, IT) : après elles, pas de version Overshoot
    abrev = ['M', 'Mme', 'Mlle', 'MM', 'Dr', 'Pr', 'St', 'Ste', 'Me', 'etc', 'cf', 'vol', 'chap', 'env',
             'usw', 'bzw', 'ca', 'Nr', 'Fr', 'Hr', 'Prof', 'Str', 'vgl', 'evtl', 'inkl',
             'Mr', 'Mrs', 'Ms', 'vs', 'No', 'Sig', 'Dott', 'ecc', 'pag']
    L = []
    L.append(f'@CAP = {_classe(caps)};')
    L.append(f'@CAP_OVS = {_classe(ovs)};')
    L.append(f'@LETTRE = {_classe(lettres)};')
    L.append(f'@MIN = {_classe(mins)};')
    L.append(f'@CHIFFRE = {_classe(NOMS_CHIFFRES)};')
    L.append(f'@ESP = {_classe(esp)};')
    L.append(f'@MILIEU = {_classe(milieu)};')
    L.append(f'@AVANT = {_classe(ouvrants)};')
    L.append('lookup OVS { sub @CAP by @CAP_OVS; } OVS;')
    L.append('feature calt {')
    L.append('  lookup DEBUT {')
    L.append("    ignore sub @LETTRE @CAP';")                      # dans un mot (McDonald, l'Europe…)
    L.append("    ignore sub [hyphen quoteright quotesingle] @CAP';")
    L.append("    ignore sub @CAP' @CAP;")                          # des capitales qui se suivent : un sigle, un titre
    L.append("    ignore sub @MILIEU @ESP @CAP';")                   # en plein milieu de la phrase
    L.append("    ignore sub @CHIFFRE period @ESP @CAP';")            # am 1. August
    L.append("    ignore sub @AVANT [@CAP @CAP_OVS] period @ESP @CAP';")   # les initiales : C. F. Ramuz
    L.append("    ignore sub @CAP_OVS period @ESP @CAP';")              # … même en début de texte
    L.append("    ignore sub @AVANT @MIN period @ESP @CAP';")         # z. B., d. h., u. a., p.
    for a in abrev:
        seq = ' '.join(nom(c) for c in a)
        L.append(f"    ignore sub @AVANT {seq} period @ESP @CAP';")
        if a[0].isupper():          # l'abréviation elle-même en début de phrase : sa capitale est déjà en version Overshoot
            seq2 = ' '.join([nom(a[0]) + '.ovs'] + [nom(c) for c in a[1:]])
            L.append(f"    ignore sub {seq2} period @ESP @CAP';")
    L.append("    sub @CAP' lookup OVS;")
    L.append('  } DEBUT;')
    L.append('} calt;')
    L.append('feature ss01 {')
    L.append('  featureNames { name "Overshoot capitals"; };')
    L.append('  sub @CAP by @CAP_OVS;')
    L.append('} ss01;')
    L.append('feature tnum {')
    L.append('  sub ' + _classe(NOMS_CHIFFRES) + ' by ' + _classe([n + '.tf' for n in NOMS_CHIFFRES]) + ';')
    L.append('} tnum;')
    return '\n'.join(L)


def code_gdef(glyphs):
    marques = [nom(c) for c in COMBINANTS]
    bases = [g for g in glyphs if g not in marques and g != '.notdef']
    return ('table GDEF {\n  GlyphClassDef ' + _classe(bases) + ', , ' + _classe(marques) + ', ;\n} GDEF;')


def construit(poids, italique, sortie, kern_fea=None):
    m = mesures(poids); style = NOMS[poids]
    g = tous(poids)
    ordre = ['.notdef'] + list(g)
    cmap = {code: n for n, (_, _, code) in g.items() if code}
    cs, larg = {}, {}
    # .notdef : une boîte
    pen = T2CharStringPen(500, None)
    for op, a in [('moveTo', ((50, 0),)), ('lineTo', ((450, 0),)), ('lineTo', ((450, 700),)), ('lineTo', ((50, 700),)), ('closePath', ()),
                  ('moveTo', ((100, 50),)), ('lineTo', ((100, 650),)), ('lineTo', ((400, 650),)), ('lineTo', ((400, 50),)), ('closePath', ())]:
        getattr(pen, op)(*a)
    cs['.notdef'] = pen.getCharString(); larg['.notdef'] = (500, 50)
    for n, (p, ch, _) in g.items():
        if italique and list(p.contours):
            p = penche(p)
        ops = lisse(p) if list(p.contours) else []
        pen = T2CharStringPen(round(ch), None); bp = BoundsPen(None)
        for op, a in ops:
            getattr(pen, op)(*a); getattr(bp, op)(*a)
        cs[n] = pen.getCharString()
        larg[n] = (round(ch), round(bp.bounds[0]) if bp.bounds else 0)

    it = 'Italic' if italique else ''
    ps = f'{FAMILLE}-{style}{it}'
    fb = FontBuilder(1000, isTTF=False)
    fb.setupGlyphOrder(ordre)
    fb.setupCharacterMap(cmap)
    noms = {'copyright': '© 2026 LaFleurStudio. All rights reserved.', 'familyName': f'{FAMILLE} {style}',
            'styleName': 'Italic' if italique else 'Regular', 'uniqueFontIdentifier': f'1.000;LFST;{ps}',
            'fullName': f'{FAMILLE} {style}' + (' Italic' if italique else ''), 'version': 'Version 1.000',
            'psName': ps, 'manufacturer': 'LaFleurStudio', 'designer': 'Jonathan Kern',
            'vendorURL': 'https://jonlekern.github.io/Fonts/', 'licenseDescription': LICENCE,
            'licenseInfoURL': 'https://github.com/Jonlekern/Fonts/blob/main/escapement/LICENCE.txt',
            'typographicFamily': FAMILLE, 'typographicSubfamily': style + (' Italic' if italique else '')}
    fb.setupCFF(ps, {'FullName': noms['fullName'], 'FamilyName': FAMILLE, 'Weight': style,
                     'Copyright': 'Copyright 2026 LaFleurStudio. All rights reserved.', 'Notice': 'Escapement by LaFleurStudio',
                     'ItalicAngle': -PENTE if italique else 0}, cs, {})
    fb.setupHorizontalMetrics(larg)
    fb.setupHorizontalHeader(ascent=ASC, descent=DESC)
    fb.setupNameTable(noms, mac=False)
    fs = (1 << 7) | ((1 << 0) if italique else (1 << 6))
    fb.setupOS2(sTypoAscender=ASC, sTypoDescender=DESC, sTypoLineGap=0, usWinAscent=ASC, usWinDescent=-DESC,
                sxHeight=m['x'], sCapHeight=m['cap'], usWeightClass=poids, achVendID='LFST', fsType=4,
                fsSelection=fs, version=4, ulCodePageRange1=1, sFamilyClass=0)
    fb.setupPost(italicAngle=-PENTE if italique else 0, underlinePosition=-150, underlineThickness=75)        # la même pour toute la famille
    f = fb.font
    f['head'].macStyle = 2 if italique else 0
    f['hhea'].caretSlopeRise = 1000 if italique else 1
    f['hhea'].caretSlopeRun = round(1000 * math.tan(math.radians(PENTE))) if italique else 0

    fea = code_gdef(ordre) + '\n' + code_calt(set(ordre)) + '\n' + (kern_fea or crenage.fea(poids)[0])
    fea = 'languagesystem DFLT dflt;\nlanguagesystem latn dflt;\n' + fea
    addOpenTypeFeaturesFromString(f, fea)

    f['OS/2'].recalcUnicodeRanges(f); f['OS/2'].recalcCodePageRanges(f); f['OS/2'].recalcAvgCharWidth(f)
    ital = {'value': 1, 'name': 'Italic'} if italique else {'value': 0, 'name': 'Roman', 'flags': 2, 'linkedValue': 1}
    buildStatTable(f, [{'tag': 'wght', 'name': 'Weight', 'values': [{'value': poids, 'name': style}]},
                       {'tag': 'ital', 'name': 'Italic', 'values': [ital]}], elidedFallbackName=2, macNames=False)

    os.makedirs(os.path.join(sortie, 'otf'), exist_ok=True); os.makedirs(os.path.join(sortie, 'woff2'), exist_ok=True)
    out = os.path.join(sortie, 'otf', f'{ps}.otf'); f.save(out)
    f2 = TTFont(out); f2.flavor = 'woff2'; f2.save(os.path.join(sortie, 'woff2', f'{ps}.woff2'))
    return out


def hauteurs_windows(sortie):
    """Les mêmes hauteurs Windows pour toute la famille : la lettre la plus haute et la plus basse des 10 fichiers."""
    haut = bas = 0
    fichiers = [os.path.join(sortie, 'otf', x) for x in os.listdir(os.path.join(sortie, 'otf')) if x.endswith('.otf')]
    for x in fichiers:
        h = TTFont(x)['head']; haut = max(haut, h.yMax); bas = min(bas, h.yMin)
    for x in fichiers:
        f = TTFont(x); f['OS/2'].usWinAscent, f['OS/2'].usWinDescent = haut, -bas; f.save(x)
        w = TTFont(x); w.flavor = 'woff2'
        w.save(os.path.join(sortie, 'woff2', os.path.basename(x)[:-4] + '.woff2'))
    return haut, -bas
