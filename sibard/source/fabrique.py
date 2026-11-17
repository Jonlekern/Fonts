# La fabrique de Sibard : les polices fixes (OTF) et la police variable (Graisse + Vitesse).
import os, math
import numpy as np
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.otlLib.builder import buildStatTable
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables import ttProgram
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphCoordinates
from fontTools.cu2qu import curves_to_quadratic
from mesures import mesures, NOMS, GRAISSES, PENTE, CAP, X
from glyphes import table, tous, dessine, nom, COMBINANTS, CARONS, place_caron
from fontTools.ttLib.tables._g_l_y_f import GlyphComponent
import crenage

FAMILLE = 'Sibard'
VERSION = '1.000'
LICENCE = 'Free for personal use. Commercial use requires prior written permission from LaFleurStudio'
ASC, DESC = 960, -260
MAITRES = (300, 400, 650, 900, 1000)          # les graisses dessinées de la variable
TAN = math.tan(math.radians(PENTE))
# dans la variable, les logiciels cherchent « Regular » à 400 et « Bold » à 700 : ces deux arrêts gardent leur nom courant
NOMS_VAR = {**NOMS, 400: 'Regular', 700: 'Bold'}


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
        elif op == 'qCurveTo':
            cur.append(('qCurveTo', tuple(R(q) for q in a)))
        elif op in ('closePath', 'endPath'):
            if len(cur) > 2:
                first = cur[0][1][0]; last = cur[-1][1][-1]
                if cur[-1][0] == 'lineTo' and abs(last[0] - first[0]) + abs(last[1] - first[1]) < 2:
                    cur.pop()
                out.extend(cur); out.append(('closePath', ()))
            cur = []
    return out


def _classe(noms):
    return '[' + ' '.join(noms) + ']'


def code_gdef(glyphs):
    marques = [nom(c) for c in COMBINANTS]
    bases = [g for g in glyphs if g not in marques and g != '.notdef']
    return 'table GDEF {\n  GlyphClassDef ' + _classe(bases) + ', , ' + _classe(marques) + ', ;\n} GDEF;'


def code_kern(tables):
    """Le crénage par familles. tables : une table {(gauche, droite): valeur} par graisse dessinée ;
    toutes sortent les mêmes paires (0 s'il le faut), pour que la variable puisse glisser de l'une à l'autre."""
    _, gauche, droite = crenage.table(500)
    cles = sorted(set(k for t in tables for k in t))
    cl = lambda pre, fam: f'@{pre}_' + fam.replace('.', '_')
    tete = [f"{cl('kG', fam)} = [{' '.join(gl)}];" for fam, gl in gauche.items()] + \
           [f"{cl('kD', fam)} = [{' '.join(gl)}];" for fam, gl in droite.items()]
    out = []
    for t in tables:
        L = list(tete) + ['feature kern {']
        for a, b in cles:
            L.append(f"  pos {cl('kG', a)} {cl('kD', b)} {t.get((a, b), 0)};")
        L.append('} kern;')
        out.append('\n'.join(L))
    return out


def _noms(style, italique, ps, variable=False):
    fam = FAMILLE if variable else f'{FAMILLE} {style}'
    return {'copyright': '© 2026 LaFleurStudio. All rights reserved.', 'familyName': fam,
            'styleName': 'Italic' if italique else 'Regular', 'uniqueFontIdentifier': f'{VERSION};LFST;{ps}',
            'fullName': fam + (' Italic' if italique else ''), 'version': f'Version {VERSION}',
            'psName': ps, 'manufacturer': 'LaFleurStudio', 'designer': 'Jonathan Kern',
            'vendorURL': 'https://jonlekern.github.io/Fonts/', 'licenseDescription': LICENCE,
            'licenseInfoURL': 'https://github.com/Jonlekern/Fonts/blob/main/epoque/LICENCE.txt',
            'typographicFamily': FAMILLE, 'typographicSubfamily': ('Regular' if variable else style) + (' Italic' if italique else '')}


def _commun(fb, poids, italique, larg, noms):
    m = mesures(poids)
    fb.setupHorizontalMetrics(larg)
    fb.setupHorizontalHeader(ascent=ASC, descent=DESC)
    fb.setupNameTable(noms, mac=False)
    fs = (1 << 7) | ((1 << 0) if italique else (1 << 6))
    fb.setupOS2(sTypoAscender=ASC, sTypoDescender=DESC, sTypoLineGap=0, usWinAscent=ASC, usWinDescent=-DESC,
                sxHeight=m['x'], sCapHeight=m['cap'], usWeightClass=poids, achVendID='LFST', fsType=4,
                fsSelection=fs, version=4, ulCodePageRange1=1, sFamilyClass=0)
    fb.setupPost(italicAngle=-PENTE if italique else 0, underlinePosition=-150, underlineThickness=60)
    f = fb.font
    f['head'].macStyle = 2 if italique else 0
    f['hhea'].caretSlopeRise = 1000 if italique else 1
    f['hhea'].caretSlopeRun = round(1000 * TAN) if italique else 0
    return f


NOTDEF = [[(50, 0), (50, 700), (450, 700), (450, 0)], [(100, 50), (400, 50), (400, 650), (100, 650)]]


def fixe(poids, italique, sortie, kern_fea):
    """Une police fixe : contours fusionnés, OTF + WOFF2."""
    style = NOMS[poids]
    g = {k: v for k, v in tous(poids, 1.0 if italique else 0.0).items() if k != 'caron.alt'}     # le caron à part ne sert qu'à la variable
    ordre = ['.notdef'] + list(g)
    cmap = {code: n for n, (_, _, code) in g.items() if code}
    cs, larg = {}, {}
    pen = T2CharStringPen(500, None)
    for c in NOTDEF:
        pen.moveTo(c[0]); [pen.lineTo(p) for p in c[1:]]; pen.closePath()
    cs['.notdef'] = pen.getCharString(); larg['.notdef'] = (500, 50)
    for n, (p, ch, _) in g.items():
        ops = lisse(p) if list(p.contours) else []
        pen = T2CharStringPen(round(ch), None); bp = BoundsPen(None)
        for op, a in ops:
            getattr(pen, op)(*a); getattr(bp, op)(*a)
        cs[n] = pen.getCharString()
        larg[n] = (round(ch), round(bp.bounds[0]) if bp.bounds else 0)
    it = 'Italic' if italique else ''
    ps = f'{FAMILLE}-{style}{it}'
    fb = FontBuilder(1000, isTTF=False)
    fb.setupGlyphOrder(ordre); fb.setupCharacterMap(cmap)
    noms = _noms(style, italique, ps)
    fb.setupCFF(ps, {'FullName': noms['fullName'], 'FamilyName': FAMILLE, 'Weight': style,
                     'Copyright': 'Copyright 2026 LaFleurStudio. All rights reserved.', 'Notice': 'Sibard by LaFleurStudio',
                     'ItalicAngle': -PENTE if italique else 0}, cs, {})
    f = _commun(fb, poids, italique, larg, noms)
    fea = 'languagesystem DFLT dflt;\nlanguagesystem latn dflt;\n' + code_gdef(ordre) + '\n' + kern_fea
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
    """Les mêmes hauteurs Windows pour toute la famille."""
    haut = bas = 0
    fichiers = [os.path.join(sortie, 'otf', x) for x in os.listdir(os.path.join(sortie, 'otf')) if x.endswith('.otf')]
    for x in fichiers:
        h = TTFont(x)['head']; haut = max(haut, h.yMax); bas = min(bas, h.yMin)
    for x in fichiers:
        f = TTFont(x); f['OS/2'].usWinAscent, f['OS/2'].usWinDescent = haut, -bas; f.save(x)
        w = TTFont(x); w.flavor = 'woff2'
        w.save(os.path.join(sortie, 'woff2', os.path.basename(x)[:-4] + '.woff2'))
    return haut, -bas


# ------------------------------------------------------------------ la variable

def _points_compatibles(versions):
    """versions : les contours d'un même glyphe dans chaque master (même structure). Rend, pour chaque master,
    (coordonnées, drapeaux, fins de contours) avec exactement les mêmes points partout."""
    n = len(versions)
    coords = [[] for _ in range(n)]; flags = []; fins = []
    for ic in range(len(versions[0])):
        cont = [v[ic] for v in versions]
        pts = [[np.asarray(c[0][1], float)] for c in cont]; fl = [1]
        for iseg in range(1, len(cont[0])):
            segs = [c[iseg] for c in cont]
            cur = [p[-1] for p in pts]
            fin = [np.asarray(s[-1], float) for s in segs]
            nul = all(np.hypot(*(f - c)) < 0.01 for f, c in zip(fin, cur))
            droit = segs[0][0] == 'l' or all(
                np.hypot(*(np.asarray(s[1], float) - c)) < 0.01 and np.hypot(*(np.asarray(s[2], float) - f)) < 0.01
                for s, c, f in zip(segs, cur, fin))
            if nul:
                continue
            if droit:
                for i in range(n):
                    pts[i].append(fin[i])
                fl.append(1)
            else:
                cub = [[tuple(cur[i]), tuple(segs[i][1]), tuple(segs[i][2]), tuple(fin[i])] for i in range(n)]
                quad = curves_to_quadratic(cub, [1.0] * n)
                for i in range(n):
                    for q in quad[i][1:-1]:
                        pts[i].append(np.asarray(q, float))
                    pts[i].append(fin[i])
                fl.extend([0] * (len(quad[0]) - 2) + [1])
        # le dernier point rejoint le premier : on l'enlève s'il est en double partout
        if len(fl) > 1 and fl[-1] == 1 and all(np.hypot(*(p[-1] - p[0])) < 0.01 for p in pts):
            for p in pts:
                p.pop()
            fl.pop()
        if len(fl) < 3:
            continue
        for i in range(n):
            coords[i].extend(pts[i])
        flags.extend(fl); fins.append(len(flags) - 1)
    return coords, flags, fins


def _glyphe(coords, flags, fins):
    g = Glyph()
    if not fins:
        g.numberOfContours = 0
        return g
    g.numberOfContours = len(fins)
    g.endPtsOfContours = list(fins)
    g.coordinates = GlyphCoordinates([(round(float(x)), round(float(y))) for x, y in coords])
    fl = bytearray(flags)
    if len(fins) > 1:
        fl[0] |= 0x40                      # les contours se recouvrent : remplissage plein (OVERLAP_SIMPLE)
    g.flags = fl
    g.program = ttProgram.Program(); g.program.fromBytecode(b'')
    return g


def masters(kern_feas):
    """Les masters de la variable : 4 graisses × 2 vitesses, tous avec les mêmes points."""
    lieux = [(p, v) for p in MAITRES for v in (0.0, 1.0)]
    noms_g = list(table())
    ordre = ['.notdef'] + noms_g
    cmap = {code: n for n, (_, code) in table().items() if code}
    glyfs = [dict() for _ in lieux]; largs = [dict() for _ in lieux]
    for n in noms_g:
        if n in CARONS:              # ď ľ ť Ľ : la lettre et le caron vertical, en deux pièces
            for i, (p, v) in enumerate(lieux):
                x, y, ch = place_caron(n, p, v)
                g = Glyph(); g.numberOfContours = -1; g.components = []
                for nomc, cx, cy in ((nom(CARONS[n]), 0, 0), ('caron.alt', round(x), round(y))):
                    c = GlyphComponent(); c.glyphName = nomc; c.x, c.y = cx, cy; c.flags = 0x4
                    g.components.append(c)
                glyfs[i][n] = g; largs[i][n] = (round(ch), 0)
            continue
        vs = [dessine(n, p, v) for p, v in lieux]
        coords, flags, fins = _points_compatibles([cs for cs, _ in vs])
        for i, (_, ch) in enumerate(vs):
            g = _glyphe(coords[i], flags, fins)
            glyfs[i][n] = g
            xmin = min((x for x, _ in g.coordinates), default=0) if fins else 0
            largs[i][n] = (round(ch), xmin)
    polices = []
    for i, (p, v) in enumerate(lieux):
        nd = Glyph(); nd.numberOfContours = 2; nd.endPtsOfContours = [3, 7]
        nd.coordinates = GlyphCoordinates(NOTDEF[0] + NOTDEF[1]); nd.flags = bytearray([1] * 8)
        nd.program = ttProgram.Program(); nd.program.fromBytecode(b'')
        gl = {'.notdef': nd, **glyfs[i]}; la = {'.notdef': (500, 50), **largs[i]}
        fb = FontBuilder(1000, isTTF=True)
        fb.setupGlyphOrder(ordre); fb.setupCharacterMap(cmap)
        fb.setupGlyf(gl)
        for n_ in CARONS:
            gl[n_].recalcBounds(fb.font['glyf']); la[n_] = (la[n_][0], gl[n_].xMin)
        f = _commun(fb, 400, False, la, _noms('Regular', False, f'{FAMILLE}-Regular', variable=True))
        f['OS/2'].usWeightClass = 400
        fb.setupDummyDSIG if False else None
        fea = 'languagesystem DFLT dflt;\nlanguagesystem latn dflt;\n' + code_gdef(ordre) + '\n' + kern_feas[MAITRES.index(p)]
        addOpenTypeFeaturesFromString(f, fea)
        f['OS/2'].recalcUnicodeRanges(f); f['OS/2'].recalcCodePageRanges(f); f['OS/2'].recalcAvgCharWidth(f)
        polices.append(((p, v), f))
    return polices


def variable(sortie, kern_feas):
    from fontTools.designspaceLib import DesignSpaceDocument, AxisDescriptor, SourceDescriptor, InstanceDescriptor
    from fontTools import varLib
    ds = DesignSpaceDocument()
    a = AxisDescriptor(); a.tag = 'wght'; a.name = 'Weight'; a.minimum, a.default, a.maximum = 300, 400, 1000; ds.addAxis(a)
    b = AxisDescriptor(); b.tag = 'VITE'; b.name = 'Vitesse'; b.minimum, b.default, b.maximum = 0, 0, 100; ds.addAxis(b)
    for (p, v), f in masters(kern_feas):
        s = SourceDescriptor(); s.font = f; s.location = {'Weight': p, 'Vitesse': v * 100}; s.name = f'm{p}_{int(v)}'
        ds.addSource(s)
    for v, suf in ((0, ''), (100, ' Course')):
        for p in GRAISSES:
            i = InstanceDescriptor()
            base = NOMS_VAR[p]
            i.styleName = (base + suf) if not (p == 400 and suf) else 'Course'
            i.familyName = FAMILLE
            i.postScriptFontName = f"{FAMILLE}-{i.styleName.replace(' ', '')}"
            i.location = {'Weight': p, 'Vitesse': v}
            ds.addInstance(i)
    vf, _, _ = varLib.build(ds, exclude=['STAT'])
    # les noms des axes, la table STAT, avar, le lissage
    buildStatTable(vf, [
        {'tag': 'wght', 'name': 'Weight', 'values': [dict(value=p, name=NOMS_VAR[p], **({'flags': 2} if p == 400 else {})) for p in GRAISSES]},
        {'tag': 'VITE', 'name': 'Vitesse', 'values': [{'value': 0, 'name': 'Normal', 'flags': 2}, {'value': 100, 'name': 'Course'}]},
    ], elidedFallbackName=2, macNames=False)
    av = newTable('avar'); av.segments = {ax.axisTag: {-1.0: -1.0, 0.0: 0.0, 1.0: 1.0} for ax in vf['fvar'].axes}; vf['avar'] = av
    prep = newTable('prep'); prep.program = ttProgram.Program()
    prep.program.fromAssembly(['PUSHW[ ]', '511', 'SCANCTRL[ ]', 'PUSHB[ ]', '4', 'SCANTYPE[ ]']); vf['prep'] = prep
    gasp = newTable('gasp'); gasp.version = 1; gasp.gaspRange = {0xFFFF: 15}; vf['gasp'] = gasp
    vf['name'].setName(FAMILLE, 25, 3, 1, 0x409)
    os.makedirs(os.path.join(sortie, 'variable'), exist_ok=True); os.makedirs(os.path.join(sortie, 'woff2'), exist_ok=True)
    out = os.path.join(sortie, 'variable', f'{FAMILLE}[VITE,wght].ttf'); vf.save(out)
    w = TTFont(out); w.flavor = 'woff2'; w.save(os.path.join(sortie, 'woff2', f'{FAMILLE}[VITE,wght].woff2'))
    return out
