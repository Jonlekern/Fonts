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
SOEURS = {   # (côté gauche, côté droit) ; None = pas de crénage de ce côté
    'Б': ('B', 'B'), 'Г': ('E', 'F'), 'Д': ('H', 'H'), 'Ж': ('X', 'K'), 'И': ('H', 'H'), 'Й': ('H', 'H'),
    'Л': ('J', 'H'), 'П': ('H', 'H'), 'У': ('Y', 'Y'), 'Ф': ('O', 'O'), 'Ц': ('H', 'H'), 'Ч': ('U', 'H'),
    'Ш': ('H', 'H'), 'Щ': ('H', 'H'), 'Ъ': ('T', 'B'), 'Ы': ('H', 'H'), 'Ь': ('H', 'B'), 'Э': (None, 'O'),
    'Ю': ('H', 'O'), 'Я': (None, 'H'),
    # minuscules à épaule carrée : côté droit du u (le n a une épaule ronde)
    'б': (None, 'o'), 'в': ('n', 'o'), 'г': ('n', 'r'), 'д': ('n', 'u'), 'ж': ('x', 'x'), 'з': (None, None),
    'и': ('n', 'u'), 'й': ('n', 'u'), 'к': ('k', 'k'), 'л': (None, 'u'), 'м': ('n', 'u'), 'н': ('n', 'u'),
    'п': ('n', 'u'), 'т': (None, None), 'ф': ('o', 'o'), 'ц': ('n', 'u'), 'ч': ('u', 'u'), 'ш': ('n', 'u'),
    'щ': ('n', 'u'), 'ъ': (None, 'o'), 'ы': ('n', 'u'), 'ь': ('n', 'o'), 'э': ('o', 'o'), 'ю': ('n', 'o'),
    'я': (None, 'u'),
    '№': ('N', None), '₽': (None, 'P'),
}
VOYELLES = 'аеёиоуыэюяАЕЁИОУЫЭЮЯ'     # celles qui peuvent porter l'accent tonique


def gardes(cmap):
    """SHKVAL sert à écrire le russe : on garde le russe, l'ASCII, et ce qui n'est ni une lettre ni un accent."""
    out = []
    for u in cmap:
        c = chr(u); cat = unicodedata.category(c)
        if 0x0400 <= u <= 0x04FF or u < 0x7F or u == 0x0301 or not (cat.startswith('L') or cat in ('Mn', 'Sk')):
            out.append(u)
    return sorted(out)


def nom_glyphe(c):
    return f'uni{ord(c):04X}'


def russes():
    return [c for c in LETTRES if len(c) == 1 and (0x0410 <= ord(c) <= 0x044F or c in 'Ёё№₽')]


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
            if 0 < dy <= 2 and dx >= 10:                     # bord presque plat : on le met à plat
                q = (q[0], prev[1])
            elif 0 < dx <= 2 and dy >= 10:                   # bord presque droit : on le met droit
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
    from fontTools.pens.boundsPen import BoundsPen
    bp = BoundsPen(None)
    for op, a in ops:
        getattr(bp, op)(*a)
    font['hmtx'].metrics[nom] = (w, round(bp.bounds[0]) if bp.bounds else 0)     # approche = vrai bord gauche


def hauteurs_windows():
    """Les mêmes hauteurs Windows pour toute la famille : la lettre la plus haute et la plus basse des 18 fichiers."""
    haut = bas = 0
    for gg in GRAISSES:
        for it in (False, True):
            h = TTFont(chemin(gg, it))['head']; haut = max(haut, h.yMax); bas = min(bas, h.yMin)
    return haut, -bas


def accent_tonique(f, italique, k, dx):
    """L'aigu combinant (U+0301) se pose centré sur les voyelles russes : points d'accroche (GPOS mark) + GDEF."""
    from fontTools.ttLib import newTable
    from fontTools.ttLib.tables import otTables as ot
    from fontTools.otlLib.builder import buildMarkBasePos, buildAnchor
    from fontTools.pens.recordingPen import RecordingPen
    cm = f.getBestCmap(); acc = cm[0x0301]
    rp = RecordingPen(); f.getGlyphSet()[acc].draw(rp)
    pts = [q for op, a in rp.value for q in a]
    yb = min(y for x, y in pts); bas = [x for x, y in pts if abs(y - yb) < 1]
    marque = {acc: (0, buildAnchor(round((min(bas) + max(bas)) / 2), round(yb)))}
    bases = {}
    for v in VOYELLES:
        n = cm[ord(v)]; w = f['hmtx'][n][0]
        y = round(yb) if v.islower() else round(yb) + 110            # les capitales : 110 u plus haut, comme Ă
        x = w / 2 + (k * y + dx if italique else 0)                    # le milieu de la lettre, à cette hauteur
        bases[n] = {0: buildAnchor(round(x), y)}
    st = buildMarkBasePos(marque, bases, f.getReverseGlyphMap())
    lk = ot.Lookup(); lk.LookupType = 4; lk.LookupFlag = 0; lk.SubTable = st; lk.SubTableCount = len(st)
    gp = f['GPOS'].table
    gp.LookupList.Lookup.append(lk); gp.LookupList.LookupCount = len(gp.LookupList.Lookup)
    fe = ot.Feature(); fe.FeatureParams = None; fe.LookupListIndex = [len(gp.LookupList.Lookup) - 1]; fe.LookupCount = 1
    fr = ot.FeatureRecord(); fr.FeatureTag = 'mark'; fr.Feature = fe
    gp.FeatureList.FeatureRecord.append(fr); gp.FeatureList.FeatureCount = len(gp.FeatureList.FeatureRecord)
    i = len(gp.FeatureList.FeatureRecord) - 1
    for sr in gp.ScriptList.ScriptRecord:
        for ls in [sr.Script.DefaultLangSys] + [l.LangSys for l in sr.Script.LangSysRecord]:
            if ls is not None:
                ls.FeatureIndex.append(i); ls.FeatureCount = len(ls.FeatureIndex)
    gdef = newTable('GDEF'); gdef.table = ot.GDEF(); gdef.table.Version = 0x00010000
    cd = ot.GlyphClassDef(); cd.classDefs = {n: 1 for n in f.getGlyphOrder() if n != '.notdef'}; cd.classDefs[acc] = 3
    gdef.table.GlyphClassDef = cd
    for attr in ('AttachList', 'LigCaretList', 'MarkAttachClassDef'):
        setattr(gdef.table, attr, None)
    f['GDEF'] = gdef


def par_alphabet(f):
    """Le crénage et l'accent tonique déclarés aussi pour le cyrillique et le latin, pas seulement par défaut."""
    import copy
    from fontTools.ttLib.tables import otTables as ot
    sl = f['GPOS'].table.ScriptList
    dflt = next(sr for sr in sl.ScriptRecord if sr.ScriptTag == 'DFLT')
    for tag in ('cyrl', 'latn'):
        if any(sr.ScriptTag == tag for sr in sl.ScriptRecord):
            continue
        sr = ot.ScriptRecord(); sr.ScriptTag = tag; sr.Script = ot.Script()
        sr.Script.DefaultLangSys = copy.deepcopy(dflt.Script.DefaultLangSys)
        sr.Script.LangSysRecord = []; sr.Script.LangSysCount = 0
        sl.ScriptRecord.append(sr)
    sl.ScriptRecord.sort(key=lambda r: r.ScriptTag); sl.ScriptCount = len(sl.ScriptRecord)


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
                if droite is not None and droite in cov:
                    cov.append(n); st.ClassDef1.classDefs[n] = st.ClassDef1.classDefs.get(droite, 0)
                if gauche is not None and gauche in st.ClassDef2.classDefs:
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

    accent_tonique(f, italique, k, dx)
    par_alphabet(f)

    os.makedirs(os.path.join(sortie, 'otf'), exist_ok=True); os.makedirs(os.path.join(sortie, 'woff2'), exist_ok=True)
    out = os.path.join(sortie, 'otf', f'{ps}.otf'); f.save(out)
    w2 = TTFont(out); w2.flavor = 'woff2'; w2.save(os.path.join(sortie, 'woff2', f'{ps}.woff2'))
    return out
