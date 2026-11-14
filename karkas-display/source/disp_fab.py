# KARKAS DISPLAY : fabrique une graisse en quatre styles.  python3 disp_fab.py M300 <dossier>
#   Regular     = Tournant : les liaisons de KARKAS, et une liaison sur deux passe en étages (deux lettres l'une sur l'autre)
#   Italic      = Bande : le même, creusé en blanc dans un bandeau noir
#   Bold        = Bloc : les lettres se rangent par colonnes de trois étages
#   Bold Italic = Bloc dans la bande
# Les lettres et les règles viennent de ../../karkas/source (kar_*.py).
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', '..', 'karkas', 'source'))
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.ttLib import TTFont
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.otlLib.builder import buildStatTable
from kar_core import *
from kar_letters import letter, LM, RM, Gl, RU
from kar_liga import groups, AZ, shared
from kar_signs import TOP, BOT, MGAP
import kar_fab
from kar_fab import build, clean, kerning, gname, TYPO_ASC, TYPO_DESC, WIN_ASC, WIN_DESC

FAMILY = 'KARKAS Display'; PS = 'KARKASDisplay'; SLUG = 'karkas-display'; VERSION = '1.000'
BAND = (-190, 990)                       # le bandeau : presque toute la hauteur de ligne ; il reste un joint entre deux lignes
STYLES = {'Regular': ('', 'Tournant'), 'Italic': ('Italic', 'Bande'), 'Bold': ('Bold', 'Bloc'), 'Bold Italic': ('BoldItalic', 'Bloc Bande')}
CHAR = {gname(ord(c)): c for c in AZ + RU}

def etage(w, a, b):
    """deux lettres l'une sur l'autre (a en haut), centrées"""
    g = w.g; ym = CAP / 2
    A = letter(a, w, ym + g / 2, CAP, nest=True); B = letter(b, w, 0, ym - g / 2, nest=True); ww = max(A.w, B.w)
    return Gl(U(mv(A.ink, (ww - A.w) / 2), mv(B.ink, (ww - B.w) / 2)), ww)

def alt_of(w, chars, kind):
    """l'autre dessin d'un groupe : en étages"""
    if len(chars) == 2 and kind != 'stack': return etage(w, chars[0], chars[1])
    if len(chars) == 2:                                   # lettre double : côte à côte (fût partagé si elle a deux fûts)
        a = chars[0]
        if a in RM and a in LM: return shared(w, a + a)
        g = letter(a, w); return Gl(U(g.ink, mv(g.ink, g.w + w.g)), 2 * g.w + w.g)
    g = letter(chars[0], w); e = etage(w, chars[1], chars[2])
    return Gl(U(g.ink, mv(e.ink, g.w + w.g)), g.w + w.g + e.w)

def tournant(w):
    out, cmap, info = build(w); G = groups(); alts = []
    for n, comp in list(info['liga']):
        if not all(c in CHAR for c in comp): continue
        chars = ''.join(CHAR[c] for c in comp); g = alt_of(w, chars, G[chars][0]); m = n + '.et'
        out[m] = (mv(g.ink, w.SB), round(g.w + 2 * w.SB)); alts.append((n, m))
        info['caret'][m] = [round(out[m][1] * (i + 1) / len(comp)) for i in range(len(comp) - 1)]
    info['alts'] = alts
    return out, cmap, info

def bloc_wt(w):
    """le trait du mot-bloc : plus fin que la graisse, pour que les lettres tiennent sur un tiers de hauteur.
    Rend la graisse de toute la police (lettres entières, chiffres, signes), celle des lettres en colonne, et la largeur de colonne."""
    S = max(15, round(0.62 * w.S)); B = max(14, round(0.62 * w.B)); col = round(1.12 * w.W)
    return Wt(w.nom, S, B, w.CT, w.wclass), Wt(w.nom, S, B, col - 2 * S, w.wclass), col

def bloc(w):
    """lettres en tiers (.t .m .b) et en moitiés (.h1 .h2), toutes de la largeur de la colonne"""
    wf, bw, col = bloc_wt(w); out, cmap, info = build(wf); gb = round(0.5 * w.g) + 10; adv = col + 2 * wf.SB
    for n in [n for n in out if '_' in n or n.endswith('.orn')]: del out[n]
    info['liga'] = []; info['ss01'] = []; info['ss02'] = []; info['zones'] = {}
    h3 = (CAP - 2 * gb) / 3; h2 = (CAP - gb) / 2
    Z = {'t': (CAP - h3, CAP), 'm': (h3 + gb, CAP - h3 - gb), 'b': (0, h3), 'h1': (CAP - h2, CAP), 'h2': (0, h2)}
    for ch in AZ:
        for suf, (y0, y1) in Z.items():
            g = letter(ch, bw, y0, y1, nest=True, fw=col)
            out[f'{ch}.{suf}'] = (mv(g.ink, wf.SB), adv if suf in ('b', 'h2') else 0); info['zones'][f'{ch}.{suf}'] = (suf, adv)
    info['bloc'] = (gb, h3, h2)
    return out, cmap, info

def bande(out, info, w):
    """chaque signe creusé en blanc dans son morceau de bandeau"""
    y0, y1 = BAND; res = {}; marks = set(info['marks']); zones = info.get('zones', {})
    o = 10                                # les bandeaux de deux signes voisins se chevauchent : pas de fil clair entre eux
    gb, h3, h2 = info.get('bloc', (0, 0, 0))
    def slab(xa, ya, xb, yb):
        # le morceau de bandeau d'un signe, avec deux languettes qui passent sous les voisins ; elles s'arrêtent avant le bord
        # du haut et du bas, pour que le bord du bandeau reste net à l'écran
        return U(rect(xa, ya, xb, yb), rect(xa - o, ya + 3, xb + o, yb - 3))
    for n, (p, adv) in out.items():
        if n in marks or n in ('space', 'uni00A0'): res[n] = (p, adv); continue       # l'espace reste vide : chaque mot est sa propre dalle
        if n == 'underscore': res[n] = (slab(0, y0, adv, y1), adv); continue        # le tiret bas : un morceau de bandeau plein, pour relier deux mots
        if n in zones:
            suf, a = zones[n]
            v = 5                               # même chose entre deux étages
            ya, yb = {'t': (CAP - h3 - gb / 2 - v, y1), 'm': (h3 + gb / 2 - v, CAP - h3 - gb / 2 + v), 'b': (y0, h3 + gb / 2 + v), 'h1': (CAP / 2 - v, y1), 'h2': (y0, CAP / 2 + v)}[suf]
            res[n] = (D(slab(0, ya, a, yb), p), adv)
        else:
            b = p.bounds
            assert not b or (b[0] >= o + 2 and b[2] <= adv - o - 2), ('encre trop près du bord pour le bandeau', n, b, adv)
            res[n] = (D(slab(0, y0, adv, y1), p), adv)
    return res

def features(order, info, style):
    go = set(order); f = ['languagesystem DFLT dflt; languagesystem latn dflt; languagesystem cyrl dflt;']
    feats = []
    if 'Bold' not in style:
        lig = sorted(info['liga'], key=lambda x: (-len(x[1]), x[0]))
        f.append('lookup LIGA {'); f += [f'  sub {" ".join(s)} by {n};' for n, s in lig]; f.append('} LIGA;')
        D_ = [a for a, b in info['alts']]; A_ = [b for a, b in info['alts']]
        sep = [n for n in order if n not in set(D_) and n not in set(A_) and n not in set(info['marks']) and n != '.notdef']
        f.append(f'@DEF = [{" ".join(D_)}]; @ALT = [{" ".join(A_)}]; @SEP = [{" ".join(sep)}];')
        # une liaison sur deux passe en étages : après une liaison normale (même à quelques signes de distance), la suivante tourne
        f.append("lookup TOURNE { " + ' '.join("sub @DEF " + "@SEP " * k + "@DEF' by @ALT;" for k in range(7)) + " } TOURNE;")
        f.append('lookup SS01 {'); f += [f'  sub {a} by {b};' for a, b in info['ss01']]; f.append('} SS01;')
        f.append('lookup SS02 {'); f += [f'  sub {a} by {b};' for a, b in info['ss02']]; f.append('} SS02;')
        f.append('lookup SS03 { sub @DEF by @ALT; } SS03;')
        feats = ['feature liga { lookup LIGA; } liga;', 'feature calt { lookup TOURNE; } calt;',
                 'feature ss01 { featureNames { name "Lettres doubles : fût partagé"; }; lookup SS01; } ss01;',
                 'feature ss02 { featureNames { name "Losanges dans les creux"; }; lookup SS02; } ss02;',
                 'feature ss03 { featureNames { name "Toutes les liaisons en étages"; }; lookup SS03; } ss03;']
    else:
        cl = lambda s: ' '.join(f'{c}.{s}' for c in AZ)
        f.append(f'@U = [{" ".join(AZ)}]; @T = [{cl("t")}]; @M = [{cl("m")}]; @B = [{cl("b")}]; @H1 = [{cl("h1")}]; @H2 = [{cl("h2")}];')
        f.append("lookup CYCLE { sub @T @U' by @M; sub @M @U' by @B; sub @U' by @T; } CYCLE;")           # haut, milieu, bas, et on recommence
        f.append("lookup RESTE2 { ignore sub @M' @B; sub @M' by @H2; } RESTE2;")                         # il reste deux lettres : deux moitiés
        f.append("lookup RESTE2H { sub @T' @H2 by @H1; } RESTE2H;")
        f.append("lookup RESTE1 { ignore sub @T' @M; sub @T' by @U; } RESTE1;")                          # il reste une lettre : elle garde toute la hauteur
        feats = ['feature calt { lookup CYCLE; lookup RESTE2; lookup RESTE2H; lookup RESTE1; } calt;']
    tm = [f'uni{c:04X}' for c in TOP]; bm = [f'uni{c:04X}' for c in BOT]
    g = [f'markClass [{" ".join(tm)}] <anchor 0 {CAP + MGAP}> @TOP;', f'markClass [{" ".join(bm)}] <anchor 0 0> @BOT;', 'feature mark {']
    for n, (x, xb) in info['anc'].items(): g.append(f'  pos base {n} <anchor {x} {CAP + MGAP}> mark @TOP <anchor {xb} 0> mark @BOT;')
    g.append('} mark;')
    ligs = [n for n, s in info['liga']] + [b for a, b in info['ss01']] + [b for a, b in info.get('alts', [])]
    sl = set(ligs); sm = set(info['marks'])
    d = ['table GDEF {', f'  GlyphClassDef [{" ".join(n for n in order if n not in sl and n not in sm and n != ".notdef")}], [{" ".join(ligs)}], [{" ".join(info["marks"])}], ;']
    for n in ligs:
        c = info['caret'].get(n) or info['caret'][n.split('.')[0]]
        d.append(f'  LigatureCaretByPos {n} {" ".join(str(v) for v in c)};')
    d.append('} GDEF;')
    return '\n'.join(f + feats) + '\n', '\n'.join(g) + '\n', '\n'.join(d) + '\n'

def write(nom, outd):
    w = WEIGHTS[nom]; res = []
    base = {False: tournant(w), True: bloc(w)}; wts = {False: w, True: bloc_wt(w)[0]}
    for style, (suf, sub) in STYLES.items():
        it, bo = 'Italic' in style, 'Bold' in style
        gl, cmap, info = base[bo]
        if it: gl = bande(gl, info, w)
        fam = f'{FAMILY} {nom}'; full = fam + ('' if style == 'Regular' else ' ' + style); psn = f'{PS}-{nom}{suf}'
        uni = {n: min(c for c, m in cmap.items() if m == n) for n in set(cmap.values())}
        order = ['.notdef'] + sorted(uni, key=lambda n: uni[n]) + sorted(n for n in gl if n not in uni)
        cs, hmtx = {}, {}; S = wts[bo].S; ys = []; cleaned = {}
        nd = T2CharStringPen(500, None); D(rect(50, 0, 450, CAP), rect(50 + S, S, 450 - S, CAP - S)).draw(nd)
        cs['.notdef'] = nd.getCharString(); hmtx['.notdef'] = (500, 50)
        for n in order[1:]:
            p, adv = gl[n]; p = clean(p); b = p.bounds; cleaned[n] = (p, adv)
            pen = T2CharStringPen(round(adv), None); p.draw(pen); cs[n] = pen.getCharString()
            hmtx[n] = (round(adv), round(b[0]) if b and b != (0, 0, 0, 0) else 0)
            if b and b != (0, 0, 0, 0): ys += [b[1], b[3]]
        assert max(ys) <= WIN_ASC and -min(ys) <= WIN_DESC, ('hors des métriques win', max(ys), min(ys))
        fb = FontBuilder(UPM, isTTF=False); fb.setupGlyphOrder(order); fb.setupCharacterMap(cmap)
        fb.setupCFF(psn, {'FullName': full, 'FamilyName': fam, 'Weight': style, 'Copyright': '(c) 2026 LaFleurStudio. All rights reserved.',
                          'Notice': f'{FAMILY} by LaFleurStudio.', 'ItalicAngle': 0}, cs, {})
        fb.setupHorizontalMetrics(hmtx); fb.setupHorizontalHeader(ascent=TYPO_ASC, descent=TYPO_DESC)
        lic = ('Free for personal use. Commercial use requires prior written permission from LaFleurStudio '
               '(free or paid, decided case by case): info@lafleurstudio.ch. Usage personnel gratuit ; usage commercial '
               'sur autorisation écrite de LaFleurStudio.')
        nm = {'copyright': '© 2026 LaFleurStudio. All rights reserved.', 'familyName': fam, 'styleName': style,
              'uniqueFontIdentifier': f'{VERSION};LFST;{psn}', 'fullName': full, 'version': f'Version {VERSION}', 'psName': psn,
              'manufacturer': 'LaFleurStudio', 'designer': 'Jonathan Kern', 'vendorURL': 'https://jonlekern.github.io/Fonts/',
              'licenseDescription': lic, 'licenseInfoURL': f'https://github.com/Jonlekern/Fonts/blob/main/{SLUG}/LICENCE.txt',
              'typographicFamily': fam, 'typographicSubfamily': sub}
        fb.setupNameTable(nm, mac=False)
        fb.setupOS2(sTypoAscender=TYPO_ASC, sTypoDescender=TYPO_DESC, sTypoLineGap=0, usWinAscent=WIN_ASC, usWinDescent=WIN_DESC,
                    sCapHeight=CAP, usWeightClass=w.wclass, sxHeight=CAP, version=4, achVendID='LFST',
                    fsSelection=(0x20 if bo else 0) | (0x01 if it else 0) | (0x40 if style == 'Regular' else 0) | 0x80)
        fb.setupPost(italicAngle=0)
        fb.font['OS/2'].recalcUnicodeRanges(fb.font)
        cps = set(cmap); cpr = 1 << 29
        if 0xE9 in cps: cpr |= 1 << 0
        if 0x10D in cps and 0x171 in cps: cpr |= 1 << 1
        if 0x11F in cps and 0x15F in cps: cpr |= 1 << 4
        if 0x113 in cps and 0x12B in cps: cpr |= 1 << 7
        fb.font['OS/2'].ulCodePageRange1 = cpr; fb.font['OS/2'].ulCodePageRange2 = 0
        fb.font['head'].macStyle = (1 if bo else 0) | (2 if it else 0); fb.font['head'].fontRevision = float(VERSION)
        fb.font['OS/2'].usDefaultChar = 0; fb.font['OS/2'].usBreakChar = 32
        outf = os.path.join(outd, psn + '.otf'); fb.save(outf)
        ft = TTFont(outf); fs, fm, fd = features(order, info, style)
        addOpenTypeFeaturesFromString(ft, fs, tables=['GSUB', 'name'])
        kf, npairs = kerning({n: v for n, v in cleaned.items() if not n.endswith('.et')}, w, info) if style == 'Regular' else ('', 0)      # bande et bloc : jamais de crénage (le bandeau et les colonnes restent réguliers)
        if not kf: kf = 'feature kern { pos quoteright quoteright -2; } kern;\n'      # une paire sans effet visible : les logiciels attendent une table de crénage
        addOpenTypeFeaturesFromString(ft, kf + fm + fd, tables=['GPOS', 'GDEF'])
        buildStatTable(ft, [dict(tag='wght', name='Weight', values=[dict(value=w.wclass, name=nom, flags=0)]),
                            dict(tag='ital', name='Italic', values=[dict(value=1, name='Italic', flags=0) if it else dict(value=0, name='Roman', flags=0x2, linkedValue=1)])],
                       locations=None, elidedFallbackName=2, macNames=False)
        ft.save(outf); res.append((style, len(order), npairs))
    return res

if __name__ == '__main__':
    nom, outd = sys.argv[1], sys.argv[2]; os.makedirs(outd, exist_ok=True)
    print(nom, write(nom, outd))
