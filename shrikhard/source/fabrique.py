# Fabrique une version fixe de Shrikhard : largeur, hauteur, droite ou penchée.
import copy, os, sys
import numpy as np
from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates
import shrikhard as S

SOURCE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'original', 'Shrikhand-Regular.ttf')


CARONS = {'Lcaron': 'L', 'lcaron': 'l', 'dcaron': 'd', 'tcaron': 't'}
MATHS = ['plus', 'minus', 'multiply', 'divide', 'equal', 'notequal', 'less', 'greater', 'lessequal',
         'greaterequal', 'plusminus', 'approxequal', 'logicalnot']


def _ajoute(f, base, nom, coords, ends, on, modele, avance):
    gl = copy.deepcopy(modele)
    gl.coordinates = GlyphCoordinates([tuple(map(float, p)) for p in coords])
    gl.endPtsOfContours = list(ends)
    gl.flags = bytearray(1 if o else 0 for o in on)
    gl.numberOfContours = len(ends)
    f['glyf'].glyphs[nom] = gl
    f.setGlyphOrder(f.getGlyphOrder() + [nom]); f['glyf'].glyphOrder = f.getGlyphOrder()
    f['hmtx'][nom] = (avance, 0)
    base[nom] = (np.array(coords, float), list(ends), np.array(on, bool), gl)


def carons(f, base):
    """Ľ ľ ď ť : la lettre et son caron vertical en deux pièces (le caron n'est ni une virgule ni un ˇ)."""
    from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphComponent
    for n, lettre in CARONS.items():
        coords, ends, on, gl = base[n]
        c = list(S._contours(coords, ends))
        pieces = {f'{lettre}.caron': [x for i, x in enumerate(c) if i != 1], f'caronvertical.{lettre}': [c[1]]}
        av = f['hmtx'][n][0]
        for nom, cs in pieces.items():
            pts, fin, ons, k = [], [], [], 0
            for a, b in cs:
                pts += list(coords[a:b]); ons += list(on[a:b]); k += b - a; fin.append(k - 1)
            _ajoute(f, base, nom, pts, fin, ons, gl, av)
        comp = Glyph(); comp.numberOfContours = -1; comp.components = []
        for i, nom in enumerate(pieces):
            gc = GlyphComponent(); gc.glyphName = nom; gc.x = gc.y = 0
            gc.flags = 0x204 if i == 0 else 0x4          # la lettre donne ses mesures au tout
            comp.components.append(gc)
        f['glyf'].glyphs[n] = comp
        base[n] = (np.zeros((0, 2)), [], np.zeros(0, bool), comp)


def reglages(f, base):
    """Ce que fontbakery demande, réglé à la source (avant l'élargissement, donc dans toutes les versions)."""
    hm = f['hmtx']
    # les signes mathématiques ont tous la même chasse
    w = max(hm[n][0] for n in MATHS if n in hm.metrics)
    for n in MATHS:
        if n in hm.metrics:
            d = (w - hm[n][0]) / 2
            c, e, o, g = base[n]
            base[n] = (c + np.array([d, 0]), e, o, g)
            hm[n] = (w, hm[n][1])
    # l'espace insécable a la chasse de l'espace
    cm = f.getBestCmap()
    hm[cm[0xA0]] = hm[cm[0x20]]
    # pas de trait d'union conditionnel
    for t in f['cmap'].tables:
        t.cmap.pop(0xAD, None)
    # GDEF : les accents seuls sont des lettres (classe 1), pas des marques
    cd = f['GDEF'].table.GlyphClassDef.classDefs
    for n, k in list(cd.items()):
        if k == 3 and hm[n][0] > 0:
            cd[n] = 1


def guillemets_bas(f, base):
    """„ : dans Shrikhand il n'a qu'une virgule ; on en met deux, écartées comme dans “ ”. Et ‚ „ prennent la chasse de la virgule."""
    c, e, on, gl = base['quotesinglbase']
    ecart = 228
    coords = np.concatenate([c, c + np.array([ecart, 0])])
    ends = list(e) + [x + len(c) for x in e]
    ons = np.concatenate([on, on])
    new = copy.deepcopy(gl)
    new.coordinates = GlyphCoordinates([tuple(map(float, p)) for p in coords])
    new.endPtsOfContours = ends; new.flags = bytearray(1 if o else 0 for o in ons); new.numberOfContours = len(ends)
    base['quotedblbase'] = (coords, ends, ons, new)
    # ‚ avait une chasse de 600 (celle d'un tiret) : il reprend celle de la virgule
    f['hmtx']['quotesinglbase'] = f['hmtx']['comma']
    f['hmtx']['quotedblbase'] = (f['hmtx']['comma'][0] + ecart, 0)


def prepare(source=SOURCE):
    f = S.latin(source)
    base = S.redresse(f)
    guillemets_bas(f, base)
    carons(f, base)
    reglages(f, base)
    for n, b in base.items():            # la police porte maintenant les glyphes décomposés
        f['glyf'].glyphs[n] = b[3]
    # on retire les glyphes que plus rien n'atteint (l'ancien caron d'Ľ, la virgule combinante)
    from fontTools.subset import Subsetter, Options
    o = Options(); o.layout_features = ['*']; o.name_IDs = ['*']; o.glyph_names = True
    o.notdef_outline = True; o.hinting = False; o.layout_scripts = ['DFLT', 'latn']
    sub = Subsetter(o); sub.populate(unicodes=f.getBestCmap().keys()); sub.subset(f)
    for n in list(base):
        if n not in f['glyf'].glyphs:
            del base[n]
    mes = {n: S.mesures(*b) for n, b in base.items() if len(b[0])}
    return f, base, mes


def _place(n, b, f):
    """Au bout du curseur, le caron vertical garde sa place à droite de sa lettre."""
    if not n.startswith('caronvertical.'):
        return (0.0, 1.0)
    av = f['hmtx'][n][0]
    x0, x1 = b[0][:, 0].min(), b[0][:, 0].max()
    return (max(0.0, min(0.9, x0 / av)), max(0.1, min(1.0, x1 / av)))


def statique(f, base, mes, sx=S.LARGEUR, sy=1.0, italique=False, force_y=1.0, ligne=False, force_x=1.0):
    g = copy.deepcopy(f)
    glyf, hmtx = g['glyf'], g['hmtx']
    for n, b in base.items():
        coords, ends, on, gl = b
        new = copy.deepcopy(gl)
        if not gl.isComposite() and len(coords):
            c = (S.trait(b, round(f['hmtx'][n][0] * sx), S.version(b, mes[n], sx, 0.6, force_y=0.25), _place(n, b, f)) if ligne
                 else S.version(b, mes[n], sx, sy, force_x=force_x, force_y=force_y))
            c = S.penche(c, italique)
            new.coordinates = GlyphCoordinates([tuple(map(float, p)) for p in np.round(c)])
        glyf[n] = new
    for n in base:
        new = glyf[n]; adv = hmtx[n][0]
        new.recalcBounds(glyf)
        hmtx[n] = (round(adv * sx), getattr(new, 'xMin', 0))
    # les carets des ligatures, à parts égales
    from fontTools.otlLib.builder import buildLigCaretList
    ligs = {'f_f': 2, 'fi': 2, 'fl': 2, 'f_f_i': 3, 'f_f_l': 3}
    carets = {n: [round(hmtx[n][0] * k / p) for k in range(1, p)] for n, p in ligs.items() if n in hmtx.metrics}
    g['GDEF'].table.LigCaretList = buildLigCaretList(carets, {}, g.getReverseGlyphMap())
    # le crénage suit la largeur
    if 'GPOS' in g:
        for lk in g['GPOS'].table.LookupList.Lookup:
            for st in lk.SubTable:
                st = getattr(st, 'ExtSubTable', st)
                for vr in _valeurs(st):
                    for a in ('XAdvance', 'XPlacement'):
                        if getattr(vr, a, None):
                            setattr(vr, a, round(getattr(vr, a) * sx))
    g['post'].italicAngle = -S.PENTE if italique else 0
    g['hhea'].caretSlopeRise, g['hhea'].caretSlopeRun = (1000, round(1000 * S.TAN)) if italique else (1, 0)
    return g


def _valeurs(st):
    if st.LookupType != 2:
        return
    if st.Format == 1:
        for ps in st.PairSet or []:
            for pv in ps.PairValueRecord:
                for v in (pv.Value1, pv.Value2):
                    if v is not None: yield v
    else:
        for c1 in st.Class1Record:
            for c2 in c1.Class2Record:
                for v in (c2.Value1, c2.Value2):
                    if v is not None: yield v


# Le curseur Hauteur (HAUT) : -100 = il ne reste qu'un trait, 0 = la hauteur de l'original élargi.
MAITRES = [  # (valeur du curseur, échelle verticale, part de l'épaisseur rendue aux traits horizontaux)
    (-100, None, None),          # il ne reste qu'un trait
    (-40, 0.60, 0.25),
    (-20, 0.80, 0.25),
    (0, 1.00, 1.0),
    (20, 1.20, 1.0),
]


def variable(f, base, mes, italique=False, maitres=MAITRES):
    from fontTools.designspaceLib import DesignSpaceDocument, AxisDescriptor, SourceDescriptor
    from fontTools import varLib
    ds = DesignSpaceDocument()
    ax = AxisDescriptor(); ax.tag = 'HAUT'; ax.name = 'Hauteur'
    ax.minimum, ax.default, ax.maximum = maitres[0][0], 0, maitres[-1][0]
    ax.map = [(v, v) for v, _, _ in maitres]       # progression linéaire, dite explicitement (avar)
    ds.addAxis(ax)
    # une graisse fixe (400) déclarée comme axe : les logiciels y retrouvent leur « Regular »
    gr = AxisDescriptor(); gr.tag = 'wght'; gr.name = 'Weight'
    gr.minimum = gr.default = gr.maximum = 400
    ds.addAxis(gr)
    for v, sy, fy in maitres:
        s = SourceDescriptor(); s.font = statique(f, base, mes, sy=sy or 1, italique=italique, force_y=fy or 0, ligne=sy is None)
        s.location = {'Hauteur': v, 'Weight': 400}; s.name = f'h{v}'
        ds.addSource(s)
    vf, _, _ = varLib.build(ds, exclude=['STAT'])
    return vf
