# КИНОВАРЬ : fabrique une graisse.  python3 kin_fab.py Zaglavie <dossier>
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', '..', 'karkas', 'source'))
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.ttLib import TTFont
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.otlLib.builder import buildStatTable
from kin_letters import *
from kin_signs import digits, signs
from kar_fab import clean, kerning                     # contours propres et crénage par profils : les mêmes outils que KARKAS

FAMILY = 'KINOVAR'; SLUG = 'kinovar'; VERSION = '1.000'; UPM = 1000
TYPO_ASC, TYPO_DESC = 960, -240
WIN_ASC, WIN_DESC = 1000, 260
CP = {'exclam': 0x21, 'quotedbl': 0x22, 'numbersign': 0x23, 'dollar': 0x24, 'percent': 0x25, 'ampersand': 0x26, 'quotesingle': 0x27, 'parenleft': 0x28,
      'parenright': 0x29, 'asterisk': 0x2A, 'plus': 0x2B, 'comma': 0x2C, 'hyphen': 0x2D, 'period': 0x2E, 'slash': 0x2F, 'colon': 0x3A, 'semicolon': 0x3B,
      'less': 0x3C, 'equal': 0x3D, 'greater': 0x3E, 'question': 0x3F, 'at': 0x40, 'bracketleft': 0x5B, 'backslash': 0x5C, 'bracketright': 0x5D,
      'asciicircum': 0x5E, 'underscore': 0x5F, 'grave': 0x60, 'braceleft': 0x7B, 'bar': 0x7C, 'braceright': 0x7D, 'asciitilde': 0x7E, 'exclamdown': 0xA1,
      'cent': 0xA2, 'sterling': 0xA3, 'yen': 0xA5, 'section': 0xA7, 'copyright': 0xA9, 'guillemotleft': 0xAB, 'registered': 0xAE, 'degree': 0xB0,
      'paragraph': 0xB6, 'periodcentered': 0xB7, 'guillemotright': 0xBB, 'questiondown': 0xBF, 'multiply': 0xD7, 'divide': 0xF7, 'acutecomb': 0x301,
      'endash': 0x2013, 'emdash': 0x2014, 'quoteleft': 0x2018, 'quoteright': 0x2019, 'quotesinglbase': 0x201A, 'quotedblleft': 0x201C,
      'quotedblright': 0x201D, 'quotedblbase': 0x201E, 'bullet': 0x2022, 'ellipsis': 0x2026, 'guilsinglleft': 0x2039, 'guilsinglright': 0x203A,
      'Euro': 0x20AC, 'uni20BD': 0x20BD, 'uni2116': 0x2116, 'trademark': 0x2122, 'uni2212': 0x2212}
DN = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
MODERNES = 'ИЙНЧ'                                      # ss01 : ces lettres comme on les écrit aujourd'hui

def nom(ch): return ch if ch.isascii() else f'uni{ord(ch):04X}'

def build(w):
    out = {}; cmap = {}; anc = {}; ss01 = []
    ws = w.petit()
    def place(n, ch, p, ww, wt, top):
        sd = SIDES.get(TWIN.get(ch, ch), 'SS') if ch not in TWIN else SIDES.get(TWIN[ch], 'SS')
        if ch in SIDES: sd = SIDES[ch]
        f = {'S': 1.0, 'O': 0.62, 'D': 0.36}; l = round(wt.SB * f[sd[0]]); r = round(wt.SB * f[sd[1]])
        out[n] = (mv(p, l), round(ww + l + r)); anc[n] = (round(l + ww / 2), top)
    for ch in RU + AZ:
        for cap in (True, False):
            wt = w if cap else ws; y1 = H if cap else SC; c = ch if cap else ch.lower(); n = nom(c)
            p, ww = letter(ch, wt, 0, y1); place(n, ch, p, ww, wt, y1); cmap[ord(c)] = n
            if ch in MODERNES:
                p, ww = letter(ch, wt, 0, y1, moderne=True); place(n + '.ss01', ch, p, ww, wt, y1); ss01.append((n, n + '.ss01'))
    for cap in (True, False):                              # Ё : le Е et deux points en losange
        wt = w if cap else ws; y1 = H if cap else SC; c = 'Ё' if cap else 'ё'; n = nom(c)
        p, ww = letter('Е', wt, 0, y1); a = round(0.50 * wt.S) + 8; xc = ww * 0.46; g = a + round(0.06 * H)
        p = U(p, losange(xc - g, y1 + 0.13 * H, a, a), losange(xc + g, y1 + 0.13 * H, a, a)); place(n, 'Е', p, ww, wt, y1 + 0.13 * H + a); cmap[ord(c)] = n
    for n, (p, dw) in digits(w).items():
        sb = round(0.5 * w.SB); out[n] = (mv(p, sb), round(dw + 2 * sb)); cmap[0x30 + DN.index(n)] = n
    Sg = signs(w)
    for n, (p, ww) in Sg.items():
        if n == 'acutecomb': out['uni0301'] = (mv(p, -0.045 * H, 0), 0); cmap[0x301] = 'uni0301'; continue
        sb = round(0.45 * w.SB); out[n] = (mv(p, sb), round(ww + 2 * sb)); cmap[CP[n]] = n
    MATH = ['plus', 'uni2212', 'equal', 'multiply', 'divide', 'less', 'greater']      # les signes de calcul : tous de la même chasse
    mw = max(out[n][1] for n in MATH)
    for n in MATH: p, a = out[n]; out[n] = (mv(p, (mw - a) / 2), mw)
    out['space'] = (P(), round(0.30 * H)); cmap[0x20] = 'space'; out['uni00A0'] = out['space']; cmap[0xA0] = 'uni00A0'
    return out, cmap, anc, ss01

def write(nom_, outf):
    w = WEIGHTS[nom_]; gl, cmap, anc, ss01 = build(w)
    psn = f'{FAMILY}-{nom_}'; fam = f'{FAMILY} {nom_}'
    uni = {n: min(c for c, m in cmap.items() if m == n) for n in set(cmap.values())}
    order = ['.notdef'] + sorted(uni, key=lambda n: uni[n]) + sorted(n for n in gl if n not in uni)
    cs, hmtx = {}, {}; ys = []; cleaned = {}
    nd = T2CharStringPen(500, None); D(rect(60, 0, 440, H), rect(60 + w.h * 2, w.h * 2, 440 - w.h * 2, H - w.h * 2)).draw(nd)
    cs['.notdef'] = nd.getCharString(); hmtx['.notdef'] = (500, 60)
    for n in order[1:]:
        p, adv = gl[n]; p = clean(p); b = p.bounds; cleaned[n] = (p, adv)
        pen = T2CharStringPen(round(adv), None); p.draw(pen); cs[n] = pen.getCharString()
        hmtx[n] = (round(adv), round(b[0]) if b and b != (0, 0, 0, 0) else 0)
        if b and b != (0, 0, 0, 0): ys += [b[1], b[3]]
    assert max(ys) <= WIN_ASC and -min(ys) <= WIN_DESC, ('hors des métriques win', max(ys), min(ys))
    fb = FontBuilder(UPM, isTTF=False); fb.setupGlyphOrder(order); fb.setupCharacterMap(cmap)
    fb.setupCFF(psn, {'FullName': fam, 'FamilyName': FAMILY, 'Weight': nom_, 'Copyright': '(c) 2026 LaFleurStudio. All rights reserved.',
                      'Notice': f'{FAMILY} by LaFleurStudio.', 'ItalicAngle': 0}, cs, {})
    fb.setupHorizontalMetrics(hmtx); fb.setupHorizontalHeader(ascent=TYPO_ASC, descent=TYPO_DESC)
    lic = ('Free for personal use. Commercial use requires prior written permission from LaFleurStudio '
           '(free or paid, decided case by case): info@lafleurstudio.ch. Usage personnel gratuit ; usage commercial '
           'sur autorisation écrite de LaFleurStudio.')
    nm = {'copyright': '© 2026 LaFleurStudio. All rights reserved.', 'familyName': fam, 'styleName': 'Regular',
          'uniqueFontIdentifier': f'{VERSION};LFST;{psn}', 'fullName': fam, 'version': f'Version {VERSION}', 'psName': psn,
          'manufacturer': 'LaFleurStudio', 'designer': 'Jonathan Kern', 'vendorURL': 'https://jonlekern.github.io/Fonts/',
          'licenseDescription': lic, 'licenseInfoURL': f'https://github.com/Jonlekern/Fonts/blob/main/{SLUG}/LICENCE.txt',
          'typographicFamily': FAMILY, 'typographicSubfamily': nom_}
    fb.setupNameTable(nm, mac=False)
    fb.setupOS2(sTypoAscender=TYPO_ASC, sTypoDescender=TYPO_DESC, sTypoLineGap=0, usWinAscent=WIN_ASC, usWinDescent=WIN_DESC,
                sCapHeight=H, usWeightClass=w.wclass, sxHeight=SC, version=4, achVendID='LFST', fsSelection=0x40 | 0x80)
    fb.setupPost(italicAngle=0)
    fb.font['OS/2'].recalcUnicodeRanges(fb.font)
    fb.font['OS/2'].ulCodePageRange1 = (1 << 0) | (1 << 2) | (1 << 29); fb.font['OS/2'].ulCodePageRange2 = 0     # latin 1, cyrillique
    fb.font['head'].macStyle = 0; fb.font['head'].fontRevision = float(VERSION)
    fb.font['OS/2'].usDefaultChar = 0; fb.font['OS/2'].usBreakChar = 32
    fb.save(outf)
    ft = TTFont(outf)
    fs = ['languagesystem DFLT dflt; languagesystem latn dflt; languagesystem cyrl dflt;',
          'feature ss01 { featureNames { name "И, Н, Ч modernes"; }; ' + ' '.join(f'sub {a} by {b};' for a, b in ss01) + ' } ss01;']
    addOpenTypeFeaturesFromString(ft, '\n'.join(fs) + '\n', tables=['GSUB', 'name'])
    info = {'marks': ['uni0301'], 'digits': DN}
    kf, npairs = kerning(cleaned, w, info)
    gp = ['markClass [uni0301] <anchor 0 0> @TOP;', 'feature mark {'] + [f'  pos base {n} <anchor {x} {round(y + 30)}> mark @TOP;' for n, (x, y) in anc.items()] + ['} mark;']
    gd = ['table GDEF {', f'  GlyphClassDef [{" ".join(n for n in order if n not in ("uni0301", ".notdef"))}], , [uni0301], ;', '} GDEF;']
    addOpenTypeFeaturesFromString(ft, kf + '\n'.join(gp + gd) + '\n', tables=['GPOS', 'GDEF'])
    buildStatTable(ft, [dict(tag='wght', name='Weight', values=[dict(value=w.wclass, name=nom_, flags=0)])], locations=None, elidedFallbackName=2, macNames=False)
    ft.save(outf)
    return len(order), npairs, round(max(ys)), round(min(ys))

if __name__ == '__main__':
    nom_, outd = sys.argv[1], sys.argv[2]; os.makedirs(outd, exist_ok=True)
    print(nom_, write(nom_, os.path.join(outd, f'{FAMILY}-{nom_}.otf')))
