# ISOSLAB : fabrique une graisse. python3 fabrique.py <fût> <nom> <poids> <sortie.otf>
import sys, os, json, math, unicodedata as ud
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.agl import UV2AGL, AGL2UV
from iso_core import *
from iso_caps import build
from iso_lower import build_lower, XH, ASC, DESC
from iso_signs import build_signs, build_marks, mv, sc, MARK_OF
from iso_digits import build_digits, build_figure_signs

FAMILY = 'ISOSLAB'; SLUG = 'isoslab'; VERSION = '1.000'; UPM = 1000
TYPO_ASC, TYPO_DESC = 960, -260
WIN_ASC, WIN_DESC = 1070, 300

def clean(p, amin=40):
    try: p.simplify(fix_winding=True, clockwise=False)
    except Exception: return p
    rp = RecordingPen(); p.draw(rp); out = P(); pen = out.getPen(); cur = []; keep = []
    for op, a in rp.value:
        if op == 'moveTo': cur = [(op, a)]
        elif op in ('closePath', 'endPath'): cur.append((op, a)); keep.append(cur); cur = []
        else: cur.append((op, a))
    def area(c):
        pts = [a[-1] for op, a in c if a]
        return abs(sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts))) / 2) if len(pts) > 2 else 0
    for c in keep:
        if area(c) < amin: continue
        for op, a in c: getattr(pen, op)(*a)
    return out

def make(st, style, weight, outf):
    w = Wt(st); C = build(w); L = build_lower(w); S = build_signs(w, C, L); M = build_marks(w)
    u = 16 + 0.12 * w.CW                     # unité d'approche
    K = {'S': 0.95, 'P': 1.6, 'O': 1.0, 'D': 0.45, 'T': 0.85, 'Q': 0.7}
    SIDES = {
        'A': 'DD', 'B': 'SO', 'C': 'OT', 'D': 'SO', 'E': 'ST', 'F': 'ST', 'G': 'OS', 'H': 'SS', 'I': 'SS', 'J': 'TS', 'K': 'SD',
        'L': 'ST', 'M': 'SS', 'N': 'SS', 'O': 'OO', 'P': 'SO', 'Q': 'OO', 'R': 'SS', 'S': 'OO', 'T': 'TT', 'U': 'SS', 'V': 'DD',
        'W': 'DD', 'X': 'DD', 'Y': 'DD', 'Z': 'TT',
        'a': 'OS', 'b': 'SO', 'c': 'OT', 'd': 'OS', 'e': 'OO', 'f': 'QQ', 'g': 'OS', 'h': 'SS', 'i': 'SS', 'j': 'TS', 'k': 'SD',
        'l': 'SS', 'm': 'SS', 'n': 'SS', 'o': 'OO', 'p': 'SO', 'q': 'OS', 'r': 'ST', 's': 'OO', 't': 'TT', 'u': 'SS', 'v': 'DD',
        'w': 'DD', 'x': 'DD', 'y': 'DD', 'z': 'TT',
        'AE': 'DT', 'OE': 'OT', 'ae': 'OO', 'oe': 'OO', 'Oslash': 'OO', 'oslash': 'OO', 'Eth': 'SO', 'Dcroat': 'SO', 'dcroat': 'OS',
        'Hbar': 'SS', 'hbar': 'SS', 'Lslash': 'ST', 'lslash': 'SS', 'Thorn': 'SO', 'thorn': 'SO', 'germandbls': 'SO', 'uni1E9E': 'SO',
        'eth': 'OO', 'dotlessi': 'SS', 'uni0237': 'TS'}
    def sides(n):
        sd = SIDES.get(n)
        if sd: return K[sd[0]] * u, K[sd[1]] * u
        return 0.9 * u, 0.9 * u
    glyphs = {}                               # nom → (chemin, approche g, approche d)
    for n, p in C.items():
        if len(n) == 1: glyphs[n] = (p,) + sides(n)
    for n, p in L.items(): glyphs[n] = (p,) + sides(n)
    for n, p in S.items():
        if n == 'uni2605': continue
        glyphs[n] = (p,) + sides(n)
    glyphs['uni2605'] = (C['star'], 0.7 * u, 0.7 * u)
    Dg, fw = build_digits(w, 'drop'); tab = fw + 2 * 0.75 * u                 # chiffres tabulaires : tous la même chasse
    for n, p in Dg.items():
        b = p.bounds; e = (tab - (b[2] - b[0])) / 2; glyphs[n] = (p, e, e)
    for n, p in build_figure_signs(w, Dg, fw, C, sc, mv, pbar).items(): glyphs[n] = (p, 0.7 * u, 0.7 * u)
    # réglages fins de la ponctuation
    for n, k in (('period', 0.8), ('comma', 0.8), ('colon', 0.8), ('semicolon', 0.8), ('ellipsis', 0.8), ('quotesingle', 0.9), ('quotedbl', 0.9),
                 ('quoteleft', 0.8), ('quoteright', 0.8), ('quotedblleft', 0.8), ('quotedblright', 0.8), ('quotesinglbase', 0.8), ('quotedblbase', 0.8),
                 ('hyphen', 0.7), ('endash', 0.5), ('emdash', 0.4), ('slash', 0.3), ('backslash', 0.3), ('parenleft', 1.2), ('parenright', 1.2),
                 ('bracketleft', 1.3), ('bracketright', 1.3), ('braceleft', 1.0), ('braceright', 1.0), ('exclam', 1.0), ('question', 0.8)):
        if n in glyphs: glyphs[n] = (glyphs[n][0], k * u, k * u)
    for n in ('parenright', 'bracketright', 'braceright'):
        if n in glyphs: p, l, r = glyphs[n]; glyphs[n] = (p, r * 0.6, l)
    for n in ('parenleft', 'bracketleft', 'braceleft'):
        if n in glyphs: p, l, r = glyphs[n]; glyphs[n] = (p, l, r * 0.6)
    MATH = ('plus', 'uni2212', 'equal', 'multiply', 'divide', 'less', 'greater', 'asciitilde')
    mw = max(glyphs[n][0].bounds[2] - glyphs[n][0].bounds[0] for n in MATH)
    for n in MATH:
        p = glyphs[n][0]; ww = p.bounds[2] - p.bounds[0]; e = (mw - ww) / 2 + 0.9 * u; glyphs[n] = (p, e, e)
    # accents isolés (avec chasse) et combinants (chasse nulle)
    SPACING = {'grave': 0x60, 'acute': 0xB4, 'dieresis': 0xA8, 'macron': 0xAF, 'cedilla': 0xB8, 'circumflex': 0x2C6, 'caron': 0x2C7,
               'breve': 0x2D8, 'dotaccent': 0x2D9, 'ring': 0x2DA, 'ogonek': 0x2DB, 'tilde': 0x2DC, 'hungarumlaut': 0x2DD}
    for n in SPACING:
        p = M[n]; b = p.bounds
        if n in ('cedilla', 'ogonek'): q = p
        else: q = mv(p, 0, XH + 70)
        glyphs[n] = (q, 0.6 * u, 0.6 * u)
    COMB = {}
    for cp, n in MARK_OF.items():
        nm = 'uni%04X' % cp; COMB[cp] = nm
        p = M[n] if n not in ('cedilla', 'ogonek', 'commabelow') else M[n]
        q = p if n in ('cedilla', 'ogonek', 'commabelow') else mv(p, 0, XH + 70)
        glyphs[nm] = (q, 0, 0)
    # lettres accentuées
    CAPS = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    def center(n, p):
        b = p.bounds; c = (b[0] + b[2]) / 2
        if n in ('a', 'd', 'u', 'q', 'g'): c -= 0.35 * w.SX       # le coup de pied à droite décale le centre optique
        if n in ('n', 'h', 'r', 'b', 'p', 'k'): c += 0.10 * w.SX
        return c
    comps = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'composites.json')))
    for cp in comps:
        ch = chr(cp); dec = ud.normalize('NFD', ch); base = dec[0]; marks = [ord(m) for m in dec[1:]]
        bn = base
        above = [m for m in marks if m not in (0x326, 0x327, 0x328)]
        if base == 'i' and above: bn = 'dotlessi'
        if base == 'j' and above: bn = 'uni0237'
        if bn not in glyphs: print('base manquante', ch); continue
        p, l, r = glyphs[bn]; isc = base in CAPS; widen = False
        out = p; b0 = p.bounds; cx = center(bn, p); ytop = b0[3]
        for m in marks:
            mn = MARK_OF[m]
            if m in (0x326,) and base in 'gG' and not isc:
                mk = M['commaturned']; out = U(out, mv(mk, cx, ytop + 60)); continue
            if m == 0x327 and base in 'gG' and not isc:
                mk = M['commaturned']; out = U(out, mv(mk, cx, ytop + 60)); continue
            if m in (0x326, 0x327):
                mk = M['commabelow' if m == 0x326 or base in 'GKLNRgklnr' else 'cedilla']
                xb = cx
                if base in 'KLNRklnr' or base == 'r': xb = (b0[0] + b0[0] + w.ST * 2 + w.SX) / 2 if base in 'KLNRklnr' else cx
                out = U(out, mv(mk, xb, 0)); continue
            if m == 0x328:
                xa = b0[2] - 0.55 * w.ST - (0.9 * w.SX if base in 'AaUuIiEe' and base not in 'Ee' else 0)
                if base in 'Ee': xa = b0[2] - 0.75 * w.ST
                if base in 'Ii': xa = (b0[0] + b0[2]) / 2 + 0.2 * w.ST
                out = U(out, mv(M['ogonek'], xa, 0)); continue
            if m == 0x30C and base in 'dltL':                      # ď ľ ť Ľ : apostrophe à droite
                ap = sc(S['quoteright'], 0.85); ba = ap.bounds
                if base == 'd': xr, yt = b0[2] + 25, ASC
                elif base == 'l': xr, yt = b0[0] + w.SX + w.ST + 30, ASC
                elif base == 't': xr, yt = b0[0] + 0.28 * 2 * w.ST + w.ST + 40, XH + round(0.22 * XH) + 40
                else: xr, yt = b0[0] + w.SX + w.ST + 60, CAP
                out = U(out, mv(ap, xr - ba[0], yt - ba[3])); widen = True; continue
            mk = M[mn + ('.cap' if isc else '')]; mb = mk.bounds
            gap = 40 if isc else (45 if bn in 'lhkbdt' else 60)
            out = U(out, mv(mk, cx, ytop + gap - mb[1])); ytop = ytop + gap + (mb[3] - mb[1])
        name = 'uni%04X' % cp
        # la largeur suit la lettre de base (même approche, mêmes bords)
        bb = out.bounds; l2 = l - (b0[0] - bb[0]); r2 = r - (bb[2] - b0[2])      # l'accent peut déborder, la chasse ne bouge pas
        if widen: r2 = 0.6 * u                                             # ď ľ ť : l'apostrophe a sa place
        glyphs[name] = (out, l2, r2)
    glyphs['uni00A0'] = None
    return glyphs, w

def unicode_of(n):
    if n.startswith('uni') and len(n) == 7: return int(n[3:], 16)
    if n in ('Dcroat',): return 0x110
    if n in ('onesuperior', 'twosuperior', 'threesuperior'): return {'onesuperior': 0xB9, 'twosuperior': 0xB2, 'threesuperior': 0xB3}[n]
    if n in AGL2UV: return AGL2UV[n]
    if len(n) == 1: return ord(n)
    return None

def write(outf, style, weight, glyphs, w):
    order = ['.notdef', 'space', 'uni00A0'] + sorted([n for n in glyphs if n != 'uni00A0'], key=lambda n: (unicode_of(n) or 0x10FFFF, n))
    cs = {}; hmtx = {}
    nd = T2CharStringPen(500, None); D(rect(50, 0, 450, CAP), rect(50 + w.TH, w.TH, 450 - w.TH, CAP - w.TH)).draw(nd)
    cs['.notdef'] = nd.getCharString(); hmtx['.notdef'] = (500, 50)
    sp = round(180 + 0.35 * w.ST)
    for n in ('space', 'uni00A0'):
        cs[n] = T2CharStringPen(sp, None).getCharString(); hmtx[n] = (sp, 0)
    cmap = {0x20: 'space', 0xA0: 'uni00A0'}
    for n in order[3:]:
        p, l, r = glyphs[n]; p = clean(p); b = p.bounds
        adv = round(l + (b[2] - b[0]) + r); dx = round(l - b[0])
        if n.startswith('uni03') and len(n) == 7: adv, dx = 0, 0
        pen = T2CharStringPen(adv, None); p.draw(TransformPen(pen, (1, 0, 0, 1, dx, 0)))
        cs[n] = pen.getCharString(); hmtx[n] = (adv, round(b[0] + dx))
        cp = unicode_of(n)
        if cp: cmap[cp] = n
    fb = FontBuilder(UPM, isTTF=False); fb.setupGlyphOrder(order); fb.setupCharacterMap(cmap)
    psn = f'{FAMILY}-{style}'; full = f'{FAMILY} {style}'
    fb.setupCFF(psn, {'FullName': full, 'FamilyName': full, 'Weight': style, 'Copyright': '(c) 2026 LaFleurStudio. All rights reserved.',
                      'Notice': f'{FAMILY} by LaFleurStudio.'}, cs, {})
    fb.setupHorizontalMetrics(hmtx); fb.setupHorizontalHeader(ascent=TYPO_ASC, descent=TYPO_DESC)
    lic = ('Free for personal use. Commercial use requires prior written permission from LaFleurStudio '
           '(free or paid, decided case by case): info@lafleurstudio.ch. Usage personnel gratuit ; usage commercial '
           'sur autorisation écrite de LaFleurStudio.')
    fb.setupNameTable({'copyright': '© 2026 LaFleurStudio. All rights reserved.', 'familyName': full, 'styleName': 'Regular',
        'uniqueFontIdentifier': f'{VERSION};LFST;{psn}', 'fullName': full, 'version': f'Version {VERSION}', 'psName': psn,
        'manufacturer': 'LaFleurStudio', 'designer': 'Jonathan Kern', 'vendorURL': 'https://jonlekern.github.io/Fonts/',
        'licenseDescription': lic, 'licenseInfoURL': f'https://github.com/Jonlekern/Fonts/blob/main/{SLUG}/LICENCE.txt',
        'typographicFamily': FAMILY, 'typographicSubfamily': style}, mac=False)
    fb.setupOS2(sTypoAscender=TYPO_ASC, sTypoDescender=TYPO_DESC, sTypoLineGap=0, usWinAscent=WIN_ASC, usWinDescent=WIN_DESC,
                sCapHeight=CAP, usWeightClass=weight, sxHeight=XH, version=4, achVendID='LFST', fsSelection=0x40 | 0x80)
    fb.setupPost()
    gs = fb.font.getGlyphSet(); ys = []
    for n_ in fb.font.getGlyphOrder():
        bp = BoundsPen(gs); gs[n_].draw(bp)
        if bp.bounds: ys += [bp.bounds[1], bp.bounds[3]]
    assert max(ys) <= WIN_ASC and -min(ys) <= WIN_DESC, ('hors des métriques win', max(ys), min(ys))
    fb.font['OS/2'].recalcUnicodeRanges(fb.font)
    cps = set(cmap); cpr = 0
    if 0xE9 in cps: cpr |= 1 << 0
    if 0x10D in cps and 0x171 in cps: cpr |= 1 << 1
    if 0x11F in cps and 0x15F in cps: cpr |= 1 << 4
    if 0x113 in cps and 0x12B in cps: cpr |= 1 << 7
    cpr |= 1 << 29
    fb.font['OS/2'].ulCodePageRange1 = cpr; fb.font['OS/2'].ulCodePageRange2 = 0
    fb.font['head'].macStyle = 0; fb.font['head'].fontRevision = float(VERSION)
    fb.font['OS/2'].usDefaultChar = 0; fb.font['OS/2'].usBreakChar = 32
    fb.save(outf)
    return max(ys), min(ys), len(order)

if __name__ == '__main__':
    st, name, weight, outf = int(sys.argv[1]), sys.argv[2], int(sys.argv[3]), sys.argv[4]
    g, w = make(st, name, weight, outf)
    hi, lo, n = write(outf, name, weight, g, w)
    import iso_kshim, iso_kern
    iso_kshim.ST = st; iso_kern.CAP = CAP
    letters = [n for n in g if (len(n) == 1 and n.isalpha()) or (n.startswith('uni') and len(n) == 7 and chr(int(n[3:], 16)).isalpha())]
    letters += [n for n in ('AE', 'OE', 'ae', 'oe', 'Oslash', 'oslash', 'Eth', 'eth', 'Thorn', 'thorn', 'germandbls', 'dotlessi', 'Lslash', 'lslash', 'Dcroat', 'dcroat', 'Hbar', 'hbar') if n in g]
    calt = '@LET = [' + ' '.join(sorted(set(letters))) + '];' + '''
feature calt {
  ignore sub @LET V' S';
  ignore sub V' S' @LET;
  sub V' S' by V_S;
  ignore sub @LET v' s';
  ignore sub v' s' @LET;
  sub v' s' by V_S;
} calt;'''
    k = iso_kern.kern_font(outf)
    from fontTools.ttLib import TTFont
    from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
    ft = TTFont(outf); addOpenTypeFeaturesFromString(ft, calt, tables=['GSUB']); ft.save(outf)
    print(f'{name}: {n} glyphes, haut {hi:.0f}, bas {lo:.0f}, {k} paires')
