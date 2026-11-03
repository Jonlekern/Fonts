# Fûsard 032 aux normes : jeu GF Latin Core complet, 9 graisses.
# Accents combinants placés automatiquement (mark/mkmk), i et j sans point sous un accent (ccmp),
# ș ț roumains (locl), chiffres minuscules (onum), crénage par familles de lettres,
# hauteurs de ligne identiques dans les 9 graisses.
import sys, os, math, json, unicodedata
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import triche, complet, droit
import fusard as techno
import build_family as B
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.misc.timeTools import timestampNow
from fontTools.agl import UV2AGL
from fontTools.ttLib import TTFont

SC = B.SC
VERSION = 0.302
ICI = os.path.dirname(os.path.abspath(__file__))
CORE = json.load(open(os.path.join(ICI, 'gf_core.json')))
# en plus du GF Latin Core : le reste du jeu Windows (Latin-1 et Windows-1252)
EXTRA = [0xB1, 0xAC, 0xAD, 0xA6, 0xA4, 0xB9, 0xB2, 0xB3, 0xBC, 0xBD, 0xBE, 0xB5, 0x192, 0x2020, 0x2021, 0x2030]
CORE = sorted(set(CORE) | set(EXTRA))
H, X, ASC = 1000.0, techno.XH, techno.ASC

def nom_glyphe(cp):
    if cp in UV2AGL and UV2AGL[cp] not in ('dotlessj',):
        return UV2AGL[cp]
    return 'uni%04X' % cp

MARQUES_HAUT = [0x300, 0x301, 0x302, 0x303, 0x304, 0x306, 0x307, 0x308, 0x30A, 0x30B, 0x30C]
MARQUES_BAS = [0x326, 0x327, 0x328]

def base_de(ch):
    d = unicodedata.normalize('NFD', ch)
    return d[0]

def traits(R):
    """Traits de tous les glyphes de la graisse : nom -> (unicode ou None, traits, rôle)."""
    C = complet.complet(R)
    ov = R['ov']; ovl = ov * X / 1000.0
    maj = techno.build_chiffres_maj(ov)
    k = (R['rv'] - 16) / (110 - 16)
    hacc = 200 * (1 + 0.35 * k)
    y_min = X + ovl + 60
    def prep(sts):
        sts = [dict(p=[np.array([x * R['sx'], y]) for x, y in st['p']], caps=list(st['caps']),
                    detail=st.get('detail', False)) for st in sts]
        return triche.couper_biais(sts, ov) if R['poids'] >= 500 else sts
    out = {}
    for cp in CORE:
        ch = chr(cp)
        n = nom_glyphe(cp)
        if unicodedata.category(ch).startswith('M'):
            continue
        if ch in '  ':
            out[n] = (cp, None, 'espace'); continue
        if ch in '0123456789':
            out[n] = (cp, prep(maj[ch]), 'base'); continue
        out[n] = (cp, C[ch], 'base')
    for c in '0123456789':
        out[nom_glyphe(ord(c)) + '.onum'] = (None, C[c], 'base')
    # accents combinants : dessinés autour de x = 0, en haut des minuscules ou sous la ligne
    noms_m = {0x300: 'grave', 0x301: 'aigu', 0x302: 'circonflexe', 0x303: 'tilde', 0x304: 'macron', 0x306: 'breve',
              0x307: 'point', 0x308: 'trema', 0x30A: 'rond', 0x30B: 'double', 0x30C: 'caron'}
    for cp in MARQUES_HAUT:
        out[nom_glyphe(cp)] = (cp, complet.det(complet.forme(noms_m[cp], 0.0, y_min, hacc)), 'marque')
    out[nom_glyphe(0x326)] = (0x326, complet.det(complet.virgule_dessous(0.0)), 'marque')
    out[nom_glyphe(0x327)] = (0x327, complet.det(complet.cedille(40.0)), 'marque')
    out[nom_glyphe(0x328)] = (0x328, complet.det(complet.ogonek(-60.0)), 'marque')
    return out, dict(y_min=y_min, y_maj=H + ov + 50, y_asc=ASC + ovl + 60, hacc=hacc)

def construire(poids, style, sortie):
    R = triche.regles(poids)
    SB = R['gap'] * SC / 2; GAP = 2 * SB
    T, Y = traits(R)
    order = ['.notdef'] + list(T.keys())
    cmap = {cp: n for n, (cp, _, _) in T.items() if cp is not None}
    glyphs, adv, encre, ancres = {}, {}, {}, {}
    nd = B.notdef(R)
    path = B.contours(nd, R); x0, y0, x1, y1 = path.bounds
    glyphs['.notdef'] = B.glyphe_ttf(path, SB - x0); adv['.notdef'] = round(x1 - x0 + 2 * SB)
    esp = round(380 + 0.4 * (R['rv'] - 16))
    for n, (cp, st, role) in T.items():
        if role == 'espace':
            glyphs[n] = TTGlyphPen(None).glyph(); adv[n] = esp; continue
        path = B.contours(st, R)
        x0, y0, x1, y1 = path.bounds
        if role == 'marque':
            glyphs[n] = B.glyphe_ttf(path, 0.0); adv[n] = 0
            continue
        dx = SB - x0
        glyphs[n] = B.glyphe_ttf(path, dx); adv[n] = round(x1 - x0 + 2 * SB)
        encre[n] = (st, dx, x1 - x0, y0, y1)
        # ancres : centre de l'encre en haut, centre en bas
        P = np.vstack([np.array(s['p']) for s in st])
        cx = (P[:, 0].min() + P[:, 0].max()) / 2 * SC + dx
        ch = chr(cp) if cp else ''
        if ch and ch.isalpha():
            haut = Y['y_maj'] if ch.isupper() else (Y['y_asc'] if ch in 'bdfhklt' else Y['y_min'])
            if ch in 'ıȷ': haut = Y['y_min']
            nfd = unicodedata.normalize('NFD', ch)
            if len(nfd) > 1 and any(ord(m) in MARQUES_HAUT for m in nfd[1:]):
                haut += Y['hacc'] + 70            # lettre déjà accentuée : l'accent suivant se pose au-dessus
            bas_x = cx
            ancres[n] = (round(cx), round(haut * SC), round(bas_x), 0)
    # --- crénage par familles : chaque lettre accentuée suit sa lettre de base ---
    r_ink = R['rv'] * SC
    repr_ = {}
    for n, (cp, st, role) in T.items():
        if role != 'base' or n not in encre: continue
        ch = chr(cp) if cp else None
        b = base_de(ch) if ch else None
        rep = nom_glyphe(ord(b)) if (b and b != ch and ord(b) in cmap) else n
        if n.endswith('.onum'): rep = n
        repr_.setdefault(rep, []).append(n)
    profils = {rep: B.profil(encre[rep][0], encre[rep][1] - SB, r_ink) for rep in repr_ if rep in encre}
    classes = {rep: f'@k_{i}' for i, rep in enumerate(sorted(profils))}
    paires = []
    for a in profils:
        pa = profils[a]; wa = encre[a][2]
        for b in profils:
            pb = profils[b]; need = -1e9
            for kb, (l, h) in pb.items():
                if kb in pa:
                    need = max(need, pa[kb][1] - l + GAP)
            need = max(need, wa - B.INTR)
            kern = int(round((need - (wa + GAP)) / 10.0)) * 10
            if kern <= -20:
                paires.append((a, b, kern))
    # --- police ---
    fb = FontBuilder(1000, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyphs)
    gl = fb.font['glyf']; lsb = {}
    for n in order:
        g = gl[n]
        if g.numberOfContours:
            g.recalcBounds(gl); lsb[n] = g.xMin
        else:
            lsb[n] = 0
    fb.setupHorizontalMetrics({n: (adv[n], lsb[n]) for n in order})
    fb.setupHorizontalHeader(ascent=1200, descent=-420)      # remis à l'identique pour les 9 graisses ensuite
    fam = 'Fûsard 032'; ps = 'Fusard032-' + style.replace(' ', ''); regular = (style == 'Regular')
    fb.setupNameTable({
        'copyright': '© 2026 LaFleurStudio. All rights reserved.',
        'familyName': fam if regular else f'{fam} {style}', 'styleName': 'Regular',
        'typographicFamily': fam, 'typographicSubfamily': style,
        'uniqueFontIdentifier': f'LaFleurStudio: {fam} {style}: {VERSION:.3f}',
        'fullName': f'{fam} {style}', 'psName': ps,
        'version': f'Version {VERSION:.3f}', 'manufacturer': 'LaFleurStudio', 'designer': 'LaFleurStudio',
        'vendorURL': 'https://jonlekern.github.io/Fonts/',
        'licenseDescription': ('Free for personal use. Commercial use requires prior written permission from '
                               'LaFleurStudio (free or paid, decided case by case): info@lafleurstudio.ch. '
                               'Usage personnel gratuit ; usage commercial sur autorisation écrite de LaFleurStudio.'),
        'licenseInfoURL': 'https://github.com/Jonlekern/Fonts/blob/main/fusard-032/LICENCE.txt',
    })
    fb.setupOS2(version=4, sTypoAscender=1200, sTypoDescender=-420, sTypoLineGap=0, usWinAscent=1200, usWinDescent=420,
                sxHeight=round(X * SC), sCapHeight=round(H * SC), achVendID='LFST', fsType=0,
                fsSelection=0x40 | 0x80, usWeightClass=poids, ulCodePageRange1=(1 | 2 | 16 | 128),
                usDefaultChar=0, usBreakChar=32, usMaxContext=2)
    fb.setupPost()
    fb.setupHead(unitsPerEm=1000, fontRevision=VERSION, created=timestampNow(), modified=timestampNow())
    # --- fonctions OpenType ---
    haut = [nom_glyphe(c) for c in MARQUES_HAUT]; bas = [nom_glyphe(c) for c in MARQUES_BAS]
    fea = 'languagesystem DFLT dflt;\nlanguagesystem latn dflt;\nlanguagesystem latn ROM;\nlanguagesystem latn MOL;\n'
    fea += f"@HAUT = [{' '.join(haut)}];\n@BAS = [{' '.join(bas)}];\n"
    fea += 'lookup SANSPOINT { sub i by dotlessi; sub j by uni0237; } SANSPOINT;\n'
    fea += "feature ccmp { sub [i j]' lookup SANSPOINT @HAUT; } ccmp;\n"
    fea += ('feature locl { script latn; language ROM; sub Scedilla by uni0218; sub scedilla by uni0219; '
            'language MOL; sub Scedilla by uni0218; sub scedilla by uni0219; } locl;\n')
    fea += 'feature onum {\n' + ''.join(f'  sub {nom_glyphe(ord(c))} by {nom_glyphe(ord(c))}.onum;\n' for c in '0123456789') + '} onum;\n'
    ym = round(Y['y_min'] * SC)
    fea += f'markClass @HAUT <anchor 0 {ym}> @MH;\nmarkClass @BAS <anchor 0 0> @MB;\n'
    fea += 'feature mark {\n'
    for n, (ax, ay, bx, by) in ancres.items():
        fea += f'  pos base {n} <anchor {ax} {ay}> mark @MH <anchor {bx} {by}> mark @MB;\n'
    fea += '} mark;\n'
    pile = round((Y['y_min'] + Y['hacc'] + 70) * SC)
    fea += 'feature mkmk {\n' + ''.join(f'  pos mark {m} <anchor 0 {pile}> mark @MH;\n' for m in haut) + '} mkmk;\n'
    for rep, c in classes.items():
        fea += f"{c} = [{' '.join(repr_[rep])}];\n"
    fea += 'feature kern {\n' + ''.join(f'  pos {classes[a]} {classes[b]} {k};\n' for a, b, k in paires) + '} kern;\n'
    addOpenTypeFeaturesFromString(fb.font, fea)
    fb.font['OS/2'].recalcUnicodeRanges(fb.font)
    fb.save(sortie)
    return len(order), len(paires)

GRAISSES = B.GRAISSES

def metriques_communes(fichiers):
    """Mêmes hauteurs de ligne pour toute la famille : le plus haut et le plus bas de tous les glyphes."""
    hi, lo = 0, 0
    for f in fichiers:
        t = TTFont(f); gl = t['glyf']
        for n in t.getGlyphOrder():
            g = gl[n]
            if g.numberOfContours:
                g.recalcBounds(gl); hi = max(hi, g.yMax); lo = min(lo, g.yMin)
    asc, desc = int(math.ceil(hi / 10) * 10), int(math.floor(lo / 10) * 10)
    for f in fichiers:
        t = TTFont(f)
        t['hhea'].ascent, t['hhea'].descent, t['hhea'].lineGap = asc, desc, 0
        o = t['OS/2']
        o.sTypoAscender, o.sTypoDescender, o.sTypoLineGap = asc, desc, 0
        o.usWinAscent, o.usWinDescent = asc, -desc
        t.save(f)
    return asc, desc

if __name__ == '__main__':
    dossier = sys.argv[1] if len(sys.argv) > 1 else 'fonts'
    os.makedirs(dossier, exist_ok=True)
    faits = []
    for p, style in GRAISSES:
        f = os.path.join(dossier, 'Fusard032-' + style.replace(' ', '') + '.ttf')
        n, k = construire(p, style, f)
        print(f'{f} : {n} glyphes, {k} paires de familles', flush=True)
        faits.append(f)
    print('hauteurs de ligne communes :', metriques_communes(faits))
