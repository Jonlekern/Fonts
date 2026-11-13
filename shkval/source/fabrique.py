# La fabrique de SHKVAL : on part du fichier Overshoot (droit ou italique), on garde tout le latin tel quel,
# on ajoute les 66 lettres russes, le crénage, les noms, la STAT, et on règle ce que fontbakery demande.
import os, unicodedata
from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.otlLib.builder import buildStatTable
from mesures import chemin, GRAISSES, NOMS, penche
from cyrillique import LETTRES, lettre, copies
from pieces import transforme

POIDS = dict(zip(GRAISSES, range(100, 1000, 100)))
LICENCE = 'Free for personal use. Commercial use requires prior written permission from LaFleurStudio'

# Pour le crénage : chaque lettre russe se comporte comme une lettre latine sœur, côté gauche et côté droit.
SOEURS = {
    'Б': ('B', 'B'), 'Г': ('E', 'F'), 'Д': ('H', 'H'), 'Ж': ('X', 'K'), 'И': ('H', 'H'), 'Й': ('H', 'H'),
    'Л': ('J', 'H'), 'П': ('H', 'H'), 'У': ('Y', 'Y'), 'Ф': ('O', 'O'), 'Ц': ('H', 'H'), 'Ч': ('U', 'H'),
    'Ш': ('H', 'H'), 'Щ': ('H', 'H'), 'Ъ': ('T', 'B'), 'Ы': ('H', 'H'), 'Ь': ('H', 'B'), 'Э': ('O', 'O'),
    'Ю': ('H', 'O'), 'Я': ('H', 'H'),
    'б': ('o', 'o'), 'в': ('n', 'o'), 'г': ('n', 'r'), 'д': ('n', 'n'), 'ж': ('x', 'x'), 'з': ('o', 'o'),
    'и': ('n', 'n'), 'й': ('n', 'n'), 'к': ('k', 'k'), 'л': ('n', 'n'), 'м': ('n', 'n'), 'н': ('n', 'n'),
    'п': ('n', 'n'), 'т': ('x', 'x'), 'ф': ('o', 'o'), 'ц': ('n', 'n'), 'ч': ('u', 'n'), 'ш': ('n', 'n'),
    'щ': ('n', 'n'), 'ъ': ('x', 'o'), 'ы': ('n', 'n'), 'ь': ('n', 'o'), 'э': ('o', 'o'), 'ю': ('n', 'o'),
    'я': ('n', 'n'),
}


def gardes(cmap):
    """SHKVAL sert à écrire le russe : on garde le russe, l'ASCII, et ce qui n'est ni une lettre ni un accent."""
    out = []
    for u in cmap:
        c = chr(u); cat = unicodedata.category(c)
        if 0x0400 <= u <= 0x04FF or u < 0x7F or not (cat.startswith('L') or cat in ('Mn', 'Sk')):
            out.append(u)
    return sorted(out)


def nom_glyphe(c):
    return f'uni{ord(c):04X}'


def russes():
    return [c for c in LETTRES if len(c) == 1 and (0x0410 <= ord(c) <= 0x044F or c in 'Ёё')]


def lisse(p):
    """Contour en unités entières, sans point en double ni segment de moins de 2 unités (les petites marches)."""
    rp = RecordingPen(); p.draw(rp); out = []; cur = []
    R = lambda q: (round(q[0]), round(q[1]))
    for op, a in rp.value:
        if op == 'moveTo':
            cur = [('moveTo', (R(a[0]),))]
        elif op == 'lineTo':
            q = R(a[0]); prev = cur[-1][1][-1]
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


def _cs(ops, w, top, gsubrs):
    pen = T2CharStringPen(w, None)
    for op, a in ops:
        getattr(pen, op)(*a)
    return pen.getCharString(private=top.Private, globalSubrs=gsubrs)


def _dessin(font, nom):
    rp = RecordingPen(); font.getGlyphSet()[nom].draw(rp)
    return rp.value


def ajoute_glyphe(font, nom, ops, w):
    cff = font['CFF '].cff; top = cff.topDictIndex[0]; cs = top.CharStrings
    t2 = _cs(ops, w, top, cff.GlobalSubrs)
    if nom in cs:
        cs[nom] = t2
    elif cs.charStringsAreIndexed:
        cs.charStringsIndex.append(t2); cs.charStrings[nom] = len(cs.charStringsIndex) - 1
    else:
        cs.charStrings[nom] = t2
    if nom not in top.charset:
        top.charset.append(nom)
    xs = [q[0] for op, a in ops for q in a]
    font['hmtx'].metrics[nom] = (w, min(xs) if xs else 0)


def hauteurs_windows():
    """Les mêmes hauteurs Windows pour toute la famille : la lettre la plus haute et la plus basse des 18 fichiers."""
    haut = bas = 0
    for gg in GRAISSES:
        for it in (False, True):
            h = TTFont(chemin(gg, it))['head']; haut = max(haut, h.yMax); bas = min(bas, h.yMin)
    return haut, -bas


def construit(g, italique, sortie):
    nom = NOMS[GRAISSES.index(g)]; it = 'Italic' if italique else ''
    f = TTFont(chemin(g, italique))
    k, dx = penche(g)
    cop = copies()

    # 1. les lettres russes
    neufs = []
    for c in russes():
        n = nom_glyphe(c)
        if c in cop:
            ops = _dessin(f, cop[c]); w = f['hmtx'][cop[c]][0]           # le latin, tel quel (droit ou italique)
        else:
            p, w = lettre(c, g)
            if italique:
                p = transforme(p, (1, 0, k, 1, dx, 0))
            ops = lisse(p)
        ajoute_glyphe(f, n, ops, w); neufs.append((c, n))
    f.setGlyphOrder(f['CFF '].cff.topDictIndex[0].charset)
    for t in f['cmap'].tables:
        if t.isUnicode():
            for c, n in neufs:
                t.cmap[ord(c)] = n

    # 2. le crénage : chaque russe prend les classes de ses sœurs latines
    soeurs = {c: (cop[c], cop[c]) for c in cop}; soeurs.update(SOEURS)
    for lk in f['GPOS'].table.LookupList.Lookup:
        for st in lk.SubTable:
            if st.Format != 2:
                continue
            cov = list(st.Coverage.glyphs)
            for c, n in neufs:
                gauche, droite = soeurs[c]
                if droite in cov:
                    cov.append(n); st.ClassDef1.classDefs[n] = st.ClassDef1.classDefs.get(droite, 0)
                if gauche in st.ClassDef2.classDefs:
                    st.ClassDef2.classDefs[n] = st.ClassDef2.classDefs[gauche]
            st.Coverage.glyphs = sorted(cov, key=f.getGlyphID)

    # 3. ce que fontbakery demande : .notdef dessiné, × à la chasse des signes de maths
    wn = 500
    box = [('moveTo', ((50, 0),)), ('lineTo', ((450, 0),)), ('lineTo', ((450, 730),)), ('lineTo', ((50, 730),)), ('closePath', ()),
           ('moveTo', ((100, 50),)), ('lineTo', ((100, 680),)), ('lineTo', ((400, 680),)), ('lineTo', ((400, 50),)), ('closePath', ())]
    ajoute_glyphe(f, '.notdef', box, wn)
    wp = f['hmtx']['plus'][0]
    for signe in ('multiply', 'less', 'greater', 'minus', 'divide', 'equal', 'plusminus', 'notequal', 'lessequal', 'greaterequal'):
        if signe in f['hmtx'].metrics and f['hmtx'][signe][0] != wp:      # tous les signes de maths à la chasse du +
            wm = f['hmtx'][signe][0]
            rp = RecordingPen(); f.getGlyphSet()[signe].draw(TransformPen(rp, (1, 0, 0, 1, (wp - wm) // 2, 0)))
            ajoute_glyphe(f, signe, rp.value, wp)

    # 4. les noms
    ps = f'SHKVAL-{nom}{it}'
    noms = {0: '© 2026 LaFleurStudio. All rights reserved.', 1: f'SHKVAL {nom}', 2: 'Italic' if italique else 'Regular',
            3: f'1.000;LFST;{ps}', 4: f'SHKVAL {nom}' + (' Italic' if italique else ''), 5: 'Version 1.000', 6: ps,
            8: 'LaFleurStudio', 9: 'Jonathan Kern', 11: 'https://jonlekern.github.io/Fonts/', 13: LICENCE,
            14: 'https://github.com/Jonlekern/Fonts/blob/main/shkval/LICENCE.txt', 16: 'SHKVAL',
            17: nom + (' Italic' if italique else '')}
    f['name'].names = []
    for i, v in noms.items():
        f['name'].setName(v, i, 3, 1, 0x409)
    cff = f['CFF '].cff; top = cff.topDictIndex[0]
    cff.fontNames = [ps]; top.FullName = noms[4]; top.FamilyName = 'SHKVAL'; top.Weight = nom
    top.Copyright = 'Copyright 2026 LaFleurStudio. All rights reserved.'; top.Notice = 'SHKVAL by LaFleurStudio'   # ASCII

    # 5. OS/2 : pages de code et blocs Unicode (latin + cyrillique)
    os2 = f['OS/2']
    os2.recalcUnicodeRanges(f); os2.recalcCodePageRanges(f); os2.recalcAvgCharWidth(f)
    os2.usWinAscent, os2.usWinDescent = hauteurs_windows()

    # 6. la STAT
    ital = {'value': 1, 'name': 'Italic'} if italique else {'value': 0, 'name': 'Roman', 'flags': 2, 'linkedValue': 1}
    buildStatTable(f, [
        {'tag': 'wght', 'name': 'Weight', 'values': [{'value': POIDS[g], 'name': nom}]},
        {'tag': 'ital', 'name': 'Italic', 'values': [ital]},
    ], elidedFallbackName=2, macNames=False)

    # 7. on ne garde que le russe, le latin de base, les chiffres, la ponctuation et les signes
    garde = gardes(f.getBestCmap())
    opt = subset.Options(); opt.name_IDs = ['*']; opt.name_languages = ['*']; opt.layout_features = ['*']
    opt.notdef_outline = True; opt.glyph_names = True; opt.recalc_bounds = True; opt.drop_tables = []
    sub = subset.Subsetter(opt); sub.populate(unicodes=garde); sub.subset(f)
    f['OS/2'].recalcUnicodeRanges(f); f['OS/2'].recalcCodePageRanges(f); f['OS/2'].recalcAvgCharWidth(f)

    os.makedirs(os.path.join(sortie, 'otf'), exist_ok=True); os.makedirs(os.path.join(sortie, 'woff2'), exist_ok=True)
    out = os.path.join(sortie, 'otf', f'{ps}.otf'); f.save(out)
    w2 = TTFont(out); w2.flavor = 'woff2'; w2.save(os.path.join(sortie, 'woff2', f'{ps}.woff2'))
    return out
