# SHEARLINE : fabrique une graisse.  python3 shr_fab.py <Epreuve|Tirage|Aplat> <dossier> [italic]
#   Regular = la Fraktur ; Italic = les mêmes lettres, les capitales deviennent des lettrines
import sys, os, math, hashlib, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.agl import AGL2UV
from fontTools.ttLib import TTFont
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from shr_core import *
from shr_lower import Wt, lower, ligatures, LIGS
from shr_caps import caps, lettrine
from shr_signs import digits, signs, DN
from shr_marks import extras, accented, SPACING, MARK_OF, mark_x, top_of, GAP_L, GAP_C
from shr_clean import clean

FAMILY = 'SHEARLINE'; SLUG = 'shearline'; VERSION = '1.000'; UPM = 1000
WEIGHTS = {'Epreuve': ('Épreuve', 60, 11, 300), 'Tirage': ('Tirage', 92, 13, 600), 'Aplat': ('Aplat', 128, 15, 900)}
TYPO_ASC, TYPO_DESC = 1000, -300
WIN_ASC, WIN_DESC = 1100, 360
NAMES_EXTRA = {'onesuperior': 0xB9, 'twosuperior': 0xB2, 'threesuperior': 0xB3, 'Dcroat': 0x110, 'brokenbar': 0xA6, 'longs': 0x17F}
MODES = {'ss01': 'latin', 'ss02': 'patri', 'ss03': 'pattee', 'ss04': 'none'}
CAPS = [chr(i) for i in range(65, 91)]
CAPX = ['AE', 'OE', 'Oslash', 'Eth', 'Dcroat', 'Thorn', 'Lslash', 'Hbar', 'uni1E9E']

def unicode_of(n):
    if n in NAMES_EXTRA: return NAMES_EXTRA[n]
    if '.' in n or '_' in n: return None
    if n.startswith('uni') and len(n) == 7: return int(n[3:], 16)
    return AGL2UV.get(n)

def is_cap(n):
    if n in CAPS or n in CAPX: return True
    if n.startswith('uni') and len(n) == 7:
        try: c = chr(int(n[3:], 16))
        except ValueError: return False
        return c.isupper()
    return False

def letters_all(w, mode):
    """lettres, lettres en plus, accentuées et ligatures pour un mode de croix"""
    Gl = lower(w, mode); Gc = caps(w, mode)
    G = dict(Gl); G.update(Gc); G.update(extras(w, Gl, Gc)); G.update(ligatures(w, Gl))
    return G

def sig(p):
    rp = RecordingPen(); p.draw(rp); return hashlib.md5(repr([(op, [tuple(round(v, 1) for v in q) for q in a]) for op, a in rp.value]).encode()).hexdigest()

def build(key, italic):
    name, W, t, wc = WEIGHTS[key]; w = Wt(name, W, t, wc)
    G = letters_all(w, 'mix')
    Dg, DW = digits(w); Sg = signs(w, lower(w), caps(w), Dg)
    G.update(Dg); G.update(Sg)
    apos = Sg['quoteright']
    A = accented(w, G, apos)
    sp = {}
    for n, g in A.items():
        if n.startswith('_sp_'): sp[n[4:]] = g
        else: G[n] = g
    G.update(sp)
    # variantes de croix : seulement les glyphes qui changent
    VAR = {}
    for ss, mode in MODES.items():
        Gm = letters_all(w, mode); Am = accented(w, dict(G, **Gm), apos)
        Gm.update({n: g for n, g in Am.items() if not n.startswith('_sp_') and not (0x300 <= int(n[3:], 16) < 0x370 if n.startswith('uni') and len(n) == 7 else False)})
        for n, g in Gm.items():
            if n in G and sig(g) != sig(G[n]): VAR[f'{n}.{ss}'] = g
    G.update(VAR)
    # ancres des accents (dans le repère du dessin, avant placement)
    anc_draw = {}
    for n, g in G.items():
        base = n.split('.')[0]
        if base in ('space',) or (base.startswith('uni') and len(base) == 7 and 0x300 <= int(base[3:], 16) < 0x370): continue
        if len(base) == 1 and base.isalpha() or base in ('dotlessi', 'uni0237'):
            cap = base.isupper()
            x = mark_x(base, G[base], w) if not cap else 0.5 * (bounds(G[base])[0] + bounds(G[base])[2])
            anc_draw[n] = (x, top_of(base, G[base], cap) + (GAP_C if cap else GAP_L), x if base not in 'KLNRklnr' else 0.0)
    # lettrines : ss05 en romain, par défaut en italique
    LET = {}
    for n in list(G):
        if is_cap(n.split('.')[0]): LET[n] = lettrine(w, G[n])
    if italic:
        for n, g in LET.items(): G[n] = g
    else:
        for n, g in LET.items():
            if '.' not in n: G[n + '.ss05'] = g
    # placement : approche à partir de la lettre sans croix, les croix débordent à moitié
    Gn = letters_all(w, 'none'); out = {}; anc = {}
    hw_ = 0.4 * w.W                                    # ſ et f : l'approche suit le fût, le crochet déborde à droite
    for n_ in ('longs', 'f'): Gn[n_] = rect(-hw_, 0, hw_ + 0.12 * w.s, XH)
    over = bounds(G['longs'])[2] - (hw_ + 0.12 * w.s)          # ce que le crochet du ſ dépasse
    bl = bounds(Gn['longs_longs']); Gn['longs_longs'] = rect(bl[0], 0, bl[2] - over, XH)
    for n, g in G.items():
        base = n.split('.')[0]
        if base.startswith('uni') and len(base) == 7 and 0x300 <= int(base[3:], 16) < 0x370 and n not in sp:
            out[n] = (g, 0); continue
        if n in DN:
            pad = 0.5 * w.SB; b = bounds(g); out[n] = (mv(g, pad + (DW - (b[2] - b[0])) / 2 - b[0]), DW + 2 * pad); continue
        b = bounds(g)
        ref = Gn.get(base) if (base in Gn and not (italic and is_cap(base)) and not n.endswith('.ss05')) else None
        if ref is not None:
            rb = bounds(ref); oL = max(0, rb[0] - b[0]); oR = max(0, b[2] - rb[2])
            lsb = w.SB + 0.5 * oL; adv = (rb[2] - rb[0]) + 2 * w.SB + 0.5 * (oL + oR); dx = lsb - b[0]
        else:
            dx = w.SB - b[0]; adv = (b[2] - b[0]) + 2 * w.SB
        out[n] = (mv(g, dx), adv)
        if n in anc_draw and not (italic and is_cap(base)) and not n.endswith('.ss05'):
            a = anc_draw[n]; anc[n] = (round(a[0] + dx), round(a[1]), round(a[2] + dx))
    out['space'] = (P(), round(0.55 * w.s)); out['uni00A0'] = out['space']
    MATH = [n for n in ('plus', 'uni2212', 'multiply', 'divide', 'equal', 'less', 'greater') if n in out]
    mw = max(out[n][1] for n in MATH)
    for n in MATH:
        p, adv = out[n]; out[n] = (mv(p, (mw - adv) / 2), mw)
    return out, w, anc

TOPM = [0x300, 0x301, 0x302, 0x303, 0x304, 0x306, 0x307, 0x308, 0x30A, 0x30B, 0x30C]
BOTM = [0x326, 0x327, 0x328]
FNAMES = {'ss01': 'Croix latines', 'ss02': 'Croix patriarcales', 'ss03': 'Croix pattées', 'ss04': 'Sans croix', 'ss05': 'Lettrines', 'ss06': 's moderne'}

def features(order, italic):
    go = set(order); fea = []
    letters_ = [n for n in order if '.' not in n and (len(n) == 1 and n.isalpha() or n in ('longs', 'dotlessi', 'uni0237', 'germandbls', 'ae', 'oe', 'oslash', 'eth', 'thorn', 'lslash', 'dcroat', 'hbar') + tuple(CAPX)
                                                    or (n.startswith('uni') and len(n) == 7 and chr(int(n[3:], 16)).isalpha()) or '_' in n)]
    fea.append(f"@LET = [{' '.join(letters_)}];")
    fea.append("lookup LONGS { sub s' @LET by longs; } LONGS;")                  # ſ au début et au milieu du mot, s rond à la fin
    fea.append("lookup SS06 { sub longs by s; } SS06;")
    fea.append('lookup LIGA {'); fea += [f"  sub {a} {b} by {n};" for n, (a, b) in LIGS.items() if n in go]; fea.append('} LIGA;')
    feats = ['feature calt { lookup LONGS; } calt;', f'feature ss06 {{ featureNames {{ name "{FNAMES["ss06"]}"; }}; lookup SS06; }} ss06;',
             'feature liga { lookup LIGA; } liga;']
    for ss in ('ss01', 'ss02', 'ss03', 'ss04', 'ss05'):
        pairs = [(n[:-5], n) for n in order if n.endswith('.' + ss) and n[:-5] in go]
        if not pairs: continue
        fea.append(f'lookup {ss.upper()} {{'); fea += [f'  sub {a} by {b};' for a, b in pairs]; fea.append(f'}} {ss.upper()};')
        feats.append(f'feature {ss} {{ featureNames {{ name "{FNAMES[ss]}"; }}; lookup {ss.upper()}; }} {ss};')
    return '\n'.join(fea + feats) + '\n'

def gpos_extra(order, anc, carets):
    go = set(order); gp = []
    tm = [f'uni{c:04X}' for c in TOPM if f'uni{c:04X}' in go]; bm = [f'uni{c:04X}' for c in BOTM if f'uni{c:04X}' in go]
    gp.append(f'markClass [{" ".join(tm)}] <anchor 0 0> @TOP;'); gp.append(f'markClass [{" ".join(bm)}] <anchor 0 0> @BOT;')
    gp.append('feature mark {')
    for n, (x, y, xb) in anc.items():
        if n in go: gp.append(f'  pos base {n} <anchor {x} {y}> mark @TOP <anchor {xb} 0> mark @BOT;')
    gp.append('} mark;')
    gdef = ['table GDEF {'] + [f'  LigatureCaretByPos {n} {c};' for n, c in carets.items() if n in go] + ['} GDEF;']
    return '\n'.join(gp) + '\n', '\n'.join(gdef) + '\n'

def write(key, outf, italic=False):
    name, W, t, wc = WEIGHTS[key]; gl, w, anc = build(key, italic)
    style = 'Italic' if italic else 'Regular'
    fam = f'{FAMILY} {name}'; full = fam + (' Italic' if italic else ''); psn = f'{FAMILY}-{key}' + ('Italic' if italic else '')
    base = sorted([n for n in gl if '.' not in n], key=lambda n: (unicode_of(n) or 0x10FFFF, n))
    order = ['.notdef'] + base + sorted(n for n in gl if '.' in n)
    cs, hmtx, cmap = {}, {}, {}
    nd = T2CharStringPen(500, None); D(rect(50, 0, 450, CAP), rect(50 + W * 0.6, W * 0.6, 450 - W * 0.6, CAP - W * 0.6)).draw(nd)
    cs['.notdef'] = nd.getCharString(); hmtx['.notdef'] = (500, 50)
    ys = []
    for n in order[1:]:
        p, adv = gl[n]; p = clean(p); b = p.bounds
        pen = T2CharStringPen(round(adv), None); p.draw(pen); cs[n] = pen.getCharString()
        hmtx[n] = (round(adv), round(b[0]) if b and b != (0, 0, 0, 0) else 0)
        if b and b != (0, 0, 0, 0): ys += [b[1], b[3]]
        cp = unicode_of(n)
        if cp: cmap[cp] = n
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
          'typographicFamily': fam, 'typographicSubfamily': style}
    fb.setupNameTable(nm, mac=False)
    fb.setupOS2(sTypoAscender=TYPO_ASC, sTypoDescender=TYPO_DESC, sTypoLineGap=0, usWinAscent=WIN_ASC, usWinDescent=WIN_DESC,
                sCapHeight=CAP, usWeightClass=wc, sxHeight=XH, version=4, achVendID='LFST', fsSelection=(0x01 if italic else 0x40) | 0x80)
    fb.setupPost(italicAngle=0)
    fb.font['OS/2'].recalcUnicodeRanges(fb.font)
    cps = set(cmap); cpr = 0
    if 0xE9 in cps: cpr |= 1 << 0
    if 0x10D in cps and 0x171 in cps: cpr |= 1 << 1
    if 0x11F in cps and 0x15F in cps: cpr |= 1 << 4
    if 0x113 in cps and 0x12B in cps: cpr |= 1 << 7
    cpr |= 1 << 29
    fb.font['OS/2'].ulCodePageRange1 = cpr; fb.font['OS/2'].ulCodePageRange2 = 0
    fb.font['head'].macStyle = 2 if italic else 0; fb.font['head'].fontRevision = float(VERSION)
    fb.font['OS/2'].usDefaultChar = 0; fb.font['OS/2'].usBreakChar = 32
    fb.save(outf)
    ft = TTFont(outf); addOpenTypeFeaturesFromString(ft, features(order, italic), tables=['GSUB', 'name']); ft.save(outf)
    from fontTools.otlLib.builder import buildStatTable
    ft = TTFont(outf)
    buildStatTable(ft, [dict(tag='wght', name='Weight', values=[dict(value=wc, name=name, flags=0)]),
                        dict(tag='ital', name='Italic', values=[dict(value=1, name='Italic', flags=0) if italic else dict(value=0, name='Roman', flags=0x2, linkedValue=1)])],
                   locations=None, elidedFallbackName=2, macNames=False)
    ft.save(outf)
    carets = {n: round(gl[n][1] / 2) for n in LIGS if n in gl}
    gp, gdef = gpos_extra(order, anc, carets)
    import shr_kshim, shr_kern
    shr_kshim.ST = round(0.77 * W); shr_kern.CAP = CAP
    k = shr_kern.kern_font(outf, extra=gp)
    ft = TTFont(outf); addOpenTypeFeaturesFromString(ft, gdef, tables=['GDEF']); ft.save(outf)
    return len(order), round(max(ys)), round(min(ys)), k

if __name__ == '__main__':
    key, outd = sys.argv[1], sys.argv[2]; it = len(sys.argv) > 3 and sys.argv[3] == 'italic'; os.makedirs(outd, exist_ok=True)
    p = os.path.join(outd, f'{FAMILY}-{key}{"Italic" if it else ""}.otf')
    print(key, 'italic' if it else 'regular', write(key, p, it))
