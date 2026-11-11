# ISOCIRCLE : fabrique une graisse, pleine + construction.  python3 fabrique.py <num> <dossier>
import sys, os, json, math, unicodedata as ud
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.agl import AGL2UV
from fontTools.ttLib import TTFont
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from geo_core import *
from geo_lower import build_lower
from geo_caps import build_caps
from geo_signs import build_signs
from geo_marks import build_extras, build_accented, SPACING, MARK_OF
from geo_digits import build_digits, build_variants, build_figure_signs, DN

FAMILY = 'ISOCIRCLE'; SLUG = 'isocircle'; VERSION = '1.000'; UPM = 1000
WEIGHTS = {'030': (44, 300), '040': (62, 400), '050': (84, 500), '070': (112, 700), '090': (142, 900)}
TYPO_ASC, TYPO_DESC = 960, -260
WIN_ASC, WIN_DESC = 1000, 280                 # mêmes valeurs dans toute la famille
NAMES_EXTRA = {'onesuperior': 0xB9, 'twosuperior': 0xB2, 'threesuperior': 0xB3, 'Dcroat': 0x110}

def glyph_set(w):
    G = build_lower(w); G.update(build_caps(w)); G.update(build_signs(w, G)); G.update(build_extras(w, G))
    A = build_accented(w, G, G); G.update(build_digits(w)); V = build_variants(w, G); G.update(V); G.update(build_figure_signs(w, G))
    for n in list(A):
        if n.startswith('_sp_'): G[n[4:]] = A[n]
        else: G[n] = A[n]
    # lettres accentuées sur les variantes : à á … (ss01), ğ ġ ģ (ss02)
    G2 = dict(G); G2['a'] = V['a.ss01']; G2['g'] = V['g.ss02']
    A2 = build_accented(w, G2, G)
    for n, g in A2.items():
        if not n.startswith('uni') or len(n) != 7: continue
        cp = int(n[3:], 16)
        if 0x300 <= cp < 0x370: continue
        base = ud.normalize('NFD', chr(cp))[0]
        if base == 'a': G[n + '.ss01'] = g
        if base == 'g': G[n + '.ss02'] = g
    return G

def unicode_of(n):
    if n in NAMES_EXTRA: return NAMES_EXTRA[n]
    if '.' in n: return None
    if n.startswith('uni') and len(n) == 7: return int(n[3:], 16)
    if n in AGL2UV: return AGL2UV[n]
    return None

def clean(p, amin=12):
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

def outlines(num, construction):
    st, wt = WEIGHTS[num]; filets = construction and num not in ('030', '040')
    w = Wt(st, num, wt, filets); G = glyph_set(w); out = {}
    pad = round(0.62 * w.SBS)
    for n, g in G.items():
        if n.startswith('uni03') and len(n) == 7:                          # accents combinants : chasse nulle, posés sur la lettre d'avant
            ink = D(g.alt if (construction and g.alt is not None) else g.ink, *(g.cuts if construction else []))
            out[n] = (xf(ink, (1, 0, 0, 1, -w.R, 0)), 0); continue
        p, adv = finish(g, w, joints=construction)
        if n in DN or n == 'zero.zero':                                    # chiffres tabulaires : tous la même chasse
            p = xf(p, (1, 0, 0, 1, pad, 0)); adv += 2 * pad
            if filets: p = U(p, construction_lines(w, adv))
        out[n] = (p, adv)
    # espaces : vides (les logiciels ne dessinent pas l'encre d'un espace)
    for n in ('space', 'uni00A0'):
        if n in out: out[n] = (P(), out[n][1])
    # signes de calcul : tous la même chasse, centrés
    MATH = [n for n in ('plus', 'uni2212', 'multiply', 'divide', 'equal', 'less', 'greater') if n in out]
    mw = max(out[n][1] for n in MATH)
    for n in MATH:
        p, adv = out[n]; d = (mw - adv) / 2; p = xf(p, (1, 0, 0, 1, d, 0))
        if filets: p = U(p, construction_lines(w, mw))
        out[n] = (p, mw)
    return out, w

def construction_lines(w, adv):
    h = w.HL; return U(*[rect(0, y - h / 2, adv, y + h / 2) for y in (0, XH, CAP, DESC)])

def write(num, construction, outf):
    st, wt = WEIGHTS[num]; gl, w = outlines(num, construction)
    style = 'Bold' if construction else 'Regular'; sub = 'Construction' if construction else 'Regular'
    fam = f'{FAMILY} {num}'; full = f'{fam} Construction' if construction else fam
    psn = f'{FAMILY}-{num}' + ('Construction' if construction else '')
    names = sorted(gl, key=lambda n: (unicode_of(n) or 0x10FFFF, n))
    order = ['.notdef'] + [n for n in names if n != '.notdef']
    cs, hmtx, cmap = {}, {}, {}
    nd = T2CharStringPen(500, None); D(rect(50, 0, 450, CAP), rect(50 + w.ST, w.ST, 450 - w.ST, CAP - w.ST)).draw(nd)
    cs['.notdef'] = nd.getCharString(); hmtx['.notdef'] = (500, 50)
    ys = []
    for n in order[1:]:
        p, adv = gl[n]; p = clean(p); b = p.bounds if p is not None else None
        pen = T2CharStringPen(adv, None); p.draw(pen); cs[n] = pen.getCharString()
        lsb = round(b[0]) if b and b != (0, 0, 0, 0) else 0
        hmtx[n] = (round(adv), lsb)
        if b and b != (0, 0, 0, 0): ys += [b[1], b[3]]
        cp = unicode_of(n)
        if cp: cmap[cp] = n
    assert max(ys) <= WIN_ASC and -min(ys) <= WIN_DESC, ('hors des métriques win', max(ys), min(ys))
    win_asc, win_desc = WIN_ASC, WIN_DESC
    fb = FontBuilder(UPM, isTTF=False); fb.setupGlyphOrder(order); fb.setupCharacterMap(cmap)
    fb.setupCFF(psn, {'FullName': full, 'FamilyName': fam, 'Weight': style, 'Copyright': '(c) 2026 LaFleurStudio. All rights reserved.',
                      'Notice': f'{FAMILY} by LaFleurStudio.'}, cs, {})
    fb.setupHorizontalMetrics(hmtx); fb.setupHorizontalHeader(ascent=TYPO_ASC, descent=TYPO_DESC)
    lic = ('Free for personal use. Commercial use requires prior written permission from LaFleurStudio '
           '(free or paid, decided case by case): info@lafleurstudio.ch. Usage personnel gratuit ; usage commercial '
           'sur autorisation écrite de LaFleurStudio.')
    nm = {'copyright': '© 2026 LaFleurStudio. All rights reserved.', 'familyName': fam, 'styleName': style,
          'uniqueFontIdentifier': f'{VERSION};LFST;{psn}', 'fullName': full, 'version': f'Version {VERSION}', 'psName': psn,
          'manufacturer': 'LaFleurStudio', 'designer': 'Jonathan Kern', 'vendorURL': 'https://jonlekern.github.io/Fonts/',
          'licenseDescription': lic, 'licenseInfoURL': f'https://github.com/Jonlekern/Fonts/blob/main/{SLUG}/LICENCE.txt'}
    nm.update({'typographicFamily': fam, 'typographicSubfamily': sub})
    fb.setupNameTable(nm, mac=False)
    fb.setupOS2(sTypoAscender=TYPO_ASC, sTypoDescender=TYPO_DESC, sTypoLineGap=0, usWinAscent=win_asc, usWinDescent=win_desc,
                sCapHeight=CAP, usWeightClass=wt, sxHeight=XH, version=4, achVendID='LFST',
                fsSelection=(0x20 if construction else 0x40) | 0x80)
    fb.setupPost()
    fb.font['OS/2'].recalcUnicodeRanges(fb.font)
    cps = set(cmap); cpr = 0
    if 0xE9 in cps: cpr |= 1 << 0
    if 0x10D in cps and 0x171 in cps: cpr |= 1 << 1
    if 0x11F in cps and 0x15F in cps: cpr |= 1 << 4
    if 0x113 in cps and 0x12B in cps: cpr |= 1 << 7
    cpr |= 1 << 29
    fb.font['OS/2'].ulCodePageRange1 = cpr; fb.font['OS/2'].ulCodePageRange2 = 0
    fb.font['head'].macStyle = 1 if construction else 0; fb.font['head'].fontRevision = float(VERSION)
    fb.font['OS/2'].usDefaultChar = 0; fb.font['OS/2'].usBreakChar = 32
    fb.save(outf)
    # variantes : ss01 (a), ss02 (g), zero
    go = set(order)
    a_src = ['a'] + [n[:-5] for n in order if n.endswith('.ss01') and n.startswith('uni')]
    g_src = ['g'] + [n[:-5] for n in order if n.endswith('.ss02') and n.startswith('uni')]
    fea = ("feature ss01 { featureNames { name \"a à deux étages\"; }; " + ' '.join(f'sub {n} by {n}.ss01;' for n in a_src if n + '.ss01' in go) + " } ss01;\n"
           "feature ss02 { featureNames { name \"g à deux étages\"; }; " + ' '.join(f'sub {n} by {n if n != "g" else "g"}.ss02;' for n in g_src if n + '.ss02' in go) + " } ss02;\n"
           "feature zero { sub zero by zero.zero; } zero;\n")
    ft = TTFont(outf); addOpenTypeFeaturesFromString(ft, fea, tables=['GSUB', 'name']); ft.save(outf)
    return len(order), win_asc, win_desc

if __name__ == '__main__':
    num, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
    p = os.path.join(out, f'{FAMILY}-{num}.otf'); c = os.path.join(out, f'{FAMILY}-{num}Construction.otf')
    r1 = write(num, False, p); r2 = write(num, True, c)
    import geo_kshim, geo_kern
    geo_kshim.ST = WEIGHTS[num][0]; geo_kern.CAP = CAP
    k = geo_kern.kern_font(p, targets=[(c, num not in ('030', '040'))])
    print(num, 'pleine', r1, 'construction', r2, k, 'paires')
