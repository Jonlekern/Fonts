# BALLASTLINE : à partir des dessins de BARYCENTRE-032, fabrique les 4 styles d'une graisse.
#   Regular = la serif ; Italic = la ligne de flottaison ; Bold = le lest ; Bold Italic = les deux. ss01 : points en plomb.
#   python3 ball_fab.py <source.otf> <num> <dossier>
import sys, os, math, unicodedata as ud
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.ttLib import TTFont
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.otlLib.builder import buildStatTable
from ball_core import *

FAMILY = 'BALLASTLINE'; SLUG = 'ballastline'; VERSION = '1.000'
WIN_ASC, WIN_DESC = 1000, 560
DOTS = {'i', 'j', 'period', 'comma', 'colon', 'semicolon', 'exclam', 'exclamdown', 'question', 'questiondown', 'ellipsis'}

def kind(n, cm_rev):
    cp = cm_rev.get(n)
    if cp is None: return 'other'
    if 0x300 <= cp < 0x370: return 'mark'
    if cp in (0x20, 0xA0): return 'space'
    c = ud.category(chr(cp))
    if c[0] in 'LN': return 'letter'
    return 'sign'

def lest_for(p, sw, desc_letter, cap=False):
    fs, y0 = feet(p)
    if not fs: return P()
    a, c = max(fs, key=lambda q: (round((q[1] - q[0]) / 8), -q[0]))
    cx = (a + c) / 2; th = max(8, 0.16 * sw); L = 34 if desc_letter else (44 if cap else 70); r = (0.30 * sw + 14) if cap else (0.42 * sw + 16)
    return U(rect(cx - th / 2, y0 - L, cx + th / 2, y0 + 8), drop(cx, y0 - L + 4, r))

def build(src, num):
    t, G = load(src); sw = stem_w(G); cm = t.getBestCmap(); rev = {v: k for k, v in cm.items()}
    # ss01 : points en plomb
    V = {}
    for n in DOTS:
        if n not in G: continue
        p, a = G[n]; ymin = XH + 20 if n in ('i', 'j') else -400
        if n in ('exclam', 'question'): ymin = -400
        q = plumb_dots(p, sw, ymin) if n not in ('exclam', 'question', 'exclamdown', 'questiondown') else plumb_small(p, sw)
        V[n + '.ss01'] = (q, a)
    base = dict(G); base.update(V)
    MATH = [n for n in ('plus', 'minus', 'uni2212', 'multiply', 'divide', 'equal', 'less', 'greater') if n in base]
    mw = max(base[n][1] for n in MATH)
    for n in MATH:                                   # signes de calcul : tous la même chasse, centrés
        p, a = base[n]; base[n] = (mv(p, (mw - a) / 2), mw)
    styles = {}
    for st in ('Regular', 'Italic', 'Bold', 'Bold Italic'):
        out = {}
        for n, (p, a) in base.items():
            k = kind(n.split('.')[0], rev) if '.' not in n or n.endswith('.ss01') else 'other'
            if n.endswith('.ss01'): k = kind(n[:-5], rev)
            q = p
            nb = n.split('.')[0]; cap = rev.get(nb) is not None and chr(rev[nb]).isupper()
            if st in ('Bold', 'Bold Italic') and k == 'letter':
                b = bounds(p); lst = lest_for(p, sw, b[1] < -40, cap)
                q = U(p, lst)
            if st in ('Italic', 'Bold Italic') and k in ('letter', 'sign') and n != '.notdef':
                fl = flottaison(p, a)
                if st == 'Bold Italic' and k == 'letter':
                    b = bounds(p); lst = lest_for(p, sw, b[1] < -40, cap)
                    fl = U(fl, D(lst, rect(-10, WL[0], a + 10, 3000)))
                q = fl
            out[n] = (q, a)
        styles[st] = out
    return t, styles, sw

def plumb_small(p, sw):
    """! ? ¡ ¿ : le point devient un petit plomb (le contour le plus bas, ou le plus haut pour ¡ ¿)"""
    from fontTools.pens.recordingPen import RecordingPen
    rp = RecordingPen(); p.draw(rp); parts = []; cur = []
    for op, a in rp.value:
        cur.append((op, a))
        if op in ('closePath', 'endPath'):
            q = P(); pen = q.getPen()
            for o, aa in cur: getattr(pen, o)(*aa)
            parts.append(q); cur = []
    if len(parts) < 2: return p
    parts.sort(key=lambda q: (bounds(q)[3] - bounds(q)[1]))
    dot = parts[0]; b = bounds(dot); r = 0.5 * (b[2] - b[0]); cx = 0.5 * (b[0] + b[2])
    return U(*parts[1:], drop(cx, b[3] + 0.6 * r, 0.82 * r))

def write(src, num, outd):
    t, styles, sw = build(src, num)
    order = t.getGlyphOrder() + sorted(n for n in styles['Regular'] if n.endswith('.ss01'))
    cm = t.getBestCmap(); wc = t['OS/2'].usWeightClass
    lic = t['name'].getDebugName(13)
    files = []
    for st, gl in styles.items():
        it, bo = 'Italic' in st, 'Bold' in st
        fam = f'{FAMILY} {num}'; full = fam + ('' if st == 'Regular' else ' ' + st)
        psn = f'{FAMILY}-{num}' + {'Regular': '', 'Italic': 'Italic', 'Bold': 'Bold', 'Bold Italic': 'BoldItalic'}[st]
        sub = {'Regular': 'Regular', 'Italic': 'Flottaison', 'Bold': 'Lest', 'Bold Italic': 'Lest Flottaison'}[st]
        cs, hmtx = {}, {}; ys = []
        for n in order:
            p, a = gl[n]
            from ball_clean import clean
            p = clean(p); b = p.bounds
            pen = T2CharStringPen(round(a), None); p.draw(pen); cs[n] = pen.getCharString()
            hmtx[n] = (round(a), round(b[0]) if b and b != (0, 0, 0, 0) else 0)
            if b and b != (0, 0, 0, 0): ys += [b[1], b[3]]
        assert max(ys) <= WIN_ASC and -min(ys) <= WIN_DESC, ('hors des métriques win', max(ys), min(ys))
        fb = FontBuilder(1000, isTTF=False); fb.setupGlyphOrder(order); fb.setupCharacterMap(cm)
        fb.setupCFF(psn, {'FullName': full, 'FamilyName': fam, 'Weight': st, 'Copyright': '(c) 2026 LaFleurStudio. All rights reserved.',
                          'Notice': f'{FAMILY} by LaFleurStudio.', 'ItalicAngle': 0}, cs, {})
        fb.setupHorizontalMetrics(hmtx)
        o2 = t['OS/2']
        fb.setupHorizontalHeader(ascent=o2.sTypoAscender, descent=o2.sTypoDescender)
        nm = {'copyright': '© 2026 LaFleurStudio. All rights reserved.', 'familyName': fam, 'styleName': st,
              'uniqueFontIdentifier': f'{VERSION};LFST;{psn}', 'fullName': full, 'version': f'Version {VERSION}', 'psName': psn,
              'manufacturer': 'LaFleurStudio', 'designer': 'Jonathan Kern', 'vendorURL': 'https://jonlekern.github.io/Fonts/',
              'licenseDescription': lic, 'licenseInfoURL': f'https://github.com/Jonlekern/Fonts/blob/main/{SLUG}/LICENCE.txt',
              'typographicFamily': fam, 'typographicSubfamily': sub}
        fb.setupNameTable(nm, mac=False)
        fb.setupOS2(sTypoAscender=o2.sTypoAscender, sTypoDescender=o2.sTypoDescender, sTypoLineGap=o2.sTypoLineGap,
                    usWinAscent=WIN_ASC, usWinDescent=WIN_DESC, sCapHeight=o2.sCapHeight, sxHeight=o2.sxHeight, usWeightClass=wc,
                    version=4, achVendID='LFST', fsSelection=(0x20 if bo else 0) | (0x01 if it else 0) | (0x40 if st == 'Regular' else 0) | 0x80,
                    ulCodePageRange1=o2.ulCodePageRange1, ulCodePageRange2=0)
        fb.setupPost(italicAngle=0)
        fb.font['OS/2'].recalcUnicodeRanges(fb.font)
        cps = set(cm); cpr = 0
        if 0xE9 in cps: cpr |= 1 << 0
        if 0x10D in cps and 0x171 in cps: cpr |= 1 << 1
        if 0x11F in cps and 0x15F in cps: cpr |= 1 << 4
        if 0x113 in cps and 0x12B in cps: cpr |= 1 << 7
        cpr |= 1 << 29
        fb.font['OS/2'].ulCodePageRange1 = cpr; fb.font['OS/2'].ulCodePageRange2 = 0
        fb.font['head'].macStyle = (1 if bo else 0) | (2 if it else 0); fb.font['head'].fontRevision = float(VERSION)
        fb.font['OS/2'].usDefaultChar = 0; fb.font['OS/2'].usBreakChar = 32
        outf = os.path.join(outd, psn + '.otf'); fb.save(outf)
        ft = TTFont(outf)
        dots = [n for n in order if n.endswith('.ss01')]
        fea = 'feature ss01 { featureNames { name "Points en plomb"; }; ' + ' '.join(f'sub {n[:-5]} by {n};' for n in dots) + ' } ss01;\n'
        addOpenTypeFeaturesFromString(ft, fea, tables=['GSUB', 'name'])
        if not it:
            ft['GPOS'] = t['GPOS']                                   # le crénage d'origine (mêmes noms de glyphes)
        else:                                                         # flottaison : jamais de crénage entre deux glyphes à bande
            addOpenTypeFeaturesFromString(ft, 'feature kern { pos space [quoteleft quotedblleft] 10; pos [quoteright quotedblright] space 10; } kern;\n', tables=['GPOS'])
        buildStatTable(ft, [dict(tag='wght', name='Weight', values=[dict(value=wc, name=num, flags=0)]),
                            dict(tag='ital', name='Italic', values=[dict(value=1, name='Italic', flags=0) if it else dict(value=0, name='Roman', flags=0x2, linkedValue=1)])],
                       locations=None, elidedFallbackName=2, macNames=False)
        ft.save(outf); files.append((outf, round(min(ys)), round(max(ys))))
    return files

if __name__ == '__main__':
    src, num, outd = sys.argv[1:4]; os.makedirs(outd, exist_ok=True)
    for f in write(src, num, outd): print(f)
