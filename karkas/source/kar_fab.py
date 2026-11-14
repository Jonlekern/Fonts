# KARKAS : fabrique une graisse.  python3 kar_fab.py M300 <dossier>
import sys, os, math, unicodedata as ud
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.agl import UV2AGL
from fontTools.ttLib import TTFont
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.otlLib.builder import buildStatTable
from kar_core import *
from kar_letters import letter, LM, RM, Gl, RU
from kar_liga import groups, draw, shared, AZ
from kar_signs import digits, signs, marks, accented, extras, TOP, BOT, SPACING, MGAP
from kar_charset import CHARSET

FAMILY = 'KARKAS'; SLUG = 'karkas'; VERSION = '1.000'
TYPO_ASC, TYPO_DESC = 1000, -200
WIN_ASC, WIN_DESC = 1000, 200
ACC_R = [0xC9, 0xC8, 0xCA, 0xCB, 0xC0, 0xC2, 0xC4, 0xD4, 0xD6, 0xD9, 0xDB, 0xDC, 0xC7]     # lettres accentuées qui reçoivent un fût partagé
ORN = 'LTFPJY'

def gname(cp):
    if 65 <= cp <= 90: return chr(cp)
    n = {0xB9: 'onesuperior', 0xB2: 'twosuperior', 0xB3: 'threesuperior'}.get(cp) or UV2AGL.get(cp)
    simple = {'space', 'period', 'comma', 'colon', 'semicolon', 'ellipsis', 'periodcentered', 'bullet', 'exclam', 'exclamdown', 'question',
              'questiondown', 'quotesingle', 'quotedbl', 'quoteright', 'quoteleft', 'quotesinglbase', 'quotedblright', 'quotedblleft',
              'quotedblbase', 'hyphen', 'endash', 'emdash', 'underscore', 'parenleft', 'parenright', 'bracketleft', 'bracketright',
              'braceleft', 'braceright', 'slash', 'backslash', 'bar', 'brokenbar', 'plus', 'equal', 'multiply', 'divide', 'less', 'greater',
              'guilsinglleft', 'guilsinglright', 'guillemotleft', 'guillemotright', 'asterisk', 'numbersign', 'percent', 'perthousand',
              'degree', 'ampersand', 'at', 'dollar', 'cent', 'sterling', 'yen', 'Euro', 'section', 'paragraph', 'dagger', 'onesuperior',
              'twosuperior', 'threesuperior', 'onequarter', 'onehalf', 'threequarters', 'trademark', 'copyright', 'registered',
              'asciicircum', 'asciitilde', 'zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine'}
    return n if n in simple else f'uni{cp:04X}'

def ornament(w, ch):
    S, B, CT, W = w.S, w.B, w.CT, w.W; H = CAP; g = letter(ch, w); cl = max(0.18 * CT, 18)
    def lz(x0, x1, yc):
        a = (x1 - x0) / 2 - cl; return losange((x0 + x1) / 2, yc, a, 2.3 * a)
    if ch == 'L': o = lz(S, g.w, 0.50 * H)
    elif ch == 'T': o = U(lz(0, (W - S) / 2, 0.46 * H), lz((W + S) / 2, W, 0.46 * H))
    elif ch == 'F': o = lz(S, g.w, 0.34 * H)
    elif ch == 'P': o = lz(S, W, 0.34 * H)
    elif ch == 'J': o = lz(0, g.w - S, 0.58 * H)
    elif ch == 'Y': o = U(lz(0, (W - S) / 2, 0.24 * H), lz((W + S) / 2, W, 0.24 * H))
    return Gl(U(g.ink, o), g.w)

def build(w):
    """nom -> (encre placée, chasse) ; cmap ; listes pour les fonctionnalités"""
    SB = w.SB; out = {}; cmap = {}; info = {'liga': [], 'ss01': [], 'ss02': [], 'anc': {}, 'caret': {}, 'marks': [], 'digits': []}
    def put(n, g, sb=None, adv=None):
        sb = SB if sb is None else sb
        out[n] = (mv(g.ink, sb), round(g.w + 2 * sb) if adv is None else adv)
    L = {ch: letter(ch, w) for ch in AZ}
    for ch in AZ:
        put(ch, L[ch]); cmap[ord(ch)] = ch
        info['anc'][ch] = (round(SB + (w.S / 2 if ch == 'L' else L[ch].w / 2)), round(SB + L[ch].w / 2))
    for ch in RU:
        g = letter(ch, w); L[ch] = g; n = gname(ord(ch)); put(n, g); cmap[ord(ch)] = n; cmap[ord(ch.lower())] = n
    M_ = marks(w); yo = letter('Е', w); n = gname(0x401)
    put(n, Gl(U(yo.ink, mv(M_[0x308], yo.w / 2, CAP + MGAP)), yo.w)); cmap[0x401] = n; cmap[0x451] = n
    ik = bounds(M_[0x306]); n = gname(0x419); gi = L['Й']
    put(n, Gl(U(gi.ink, mv(M_[0x306], gi.w / 2, CAP + MGAP)), gi.w)); cmap[0x419] = n; cmap[0x439] = n
    for n, g in digits(w).items(): put(n, g); info['digits'].append(n)
    psb = round(0.6 * SB)
    for n, g in signs(w).items():
        if getattr(g, 'raw', False): out[n] = (g.ink, round(g.w))
        else: put(n, g, psb if n in ('period', 'comma', 'colon', 'semicolon', 'ellipsis', 'quotesingle', 'quotedbl', 'quoteright', 'quoteleft', 'quotedblright', 'quotedblleft', 'quotesinglbase', 'quotedblbase', 'exclam', 'exclamdown') else SB)
    X = extras(w)
    for cp, g in X.items(): put(gname(cp), g)
    base = lambda b: L[b] if b in L else X[ord(b)]
    cps = [ord(c) for c in CHARSET]
    A = accented(w, [ord(chr(c).upper()) if len(chr(c).upper()) == 1 else c for c in cps], base)
    for cp, g in A.items(): put(gname(cp), g)
    M = marks(w)
    for cp, p in M.items():
        n = f'uni{cp:04X}'; out[n] = (mv(p, 0, CAP + MGAP) if cp in TOP else p, 0); info['marks'].append(n)
    for scp, mcp in SPACING.items():
        p = M[mcp]; b = bounds(p); out[gname(scp)] = (mv(p, SB - b[0], CAP + MGAP if mcp in TOP else 0), round(b[2] - b[0] + 2 * SB))
    out['space'] = (P(), round(0.80 * w.W)); out['uni00A0'] = out['space']
    names = set(out)
    for c in cps:
        ch = chr(c); n = gname(c)
        if n in names: cmap[c] = n; continue
        up = ch.upper()
        if len(up) == 1 and gname(ord(up)) in names: cmap[c] = gname(ord(up))
    cmap[0xDF] = gname(0x1E9E); cmap[0x131] = 'I'; cmap[0x237] = 'J'; cmap[0x2020] = 'dagger'
    missing = [hex(c) for c in cps if c not in cmap]
    assert not missing, missing
    # les liaisons
    G = groups()
    for nm, (kind, arg) in G.items():
        g = draw(w, kind, arg); comp = [gname(ord(c)) for c in nm]; n = '_'.join(comp); put(n, g); info['liga'].append((n, comp))
        info['caret'][n] = [round(out[n][1] * (i + 1) / len(nm)) for i in range(len(nm) - 1)]
    for a in sorted(RM & set(AZ)):
        for cp in ACC_R:
            b = ud.normalize('NFD', chr(cp))[0]
            if b not in LM or b == a: continue
            dx = getattr(A[cp], 'dx', 0); gb = Gl(mv(A[cp].ink, -dx), L[b].w)
            g0 = shared(w, a + b, inks={1: gb}); bb = bounds(g0.ink); g = Gl(mv(g0.ink, -min(0, bb[0])), max(g0.w, bb[2]) - min(0, bb[0]))
            n = f'{a}_{gname(cp)}'; put(n, g); info['liga'].append((n, [a, gname(cp)])); info['caret'][n] = [round(out[n][1] / 2)]
    for ch in sorted(RM & LM):
        gn = gname(ord(ch)); n = f'{gn}_{gn}.ss01'; put(n, shared(w, ch + ch)); info['ss01'].append((f'{gn}_{gn}', n))
    for ch in ORN:
        n = f'{ch}.orn'; put(n, ornament(w, ch)); info['ss02'].append((ch, n))
    return out, cmap, info

def clean(p, amin=12):
    try: p.simplify(fix_winding=True, clockwise=False)
    except Exception: return p
    rp = RecordingPen(); p.draw(rp); out = P(); pen = out.getPen(); cur = []; keep = []
    for op, a in rp.value:
        if op == 'moveTo': cur = [a[0]]
        elif op == 'lineTo': cur.append(a[0])
        elif op in ('closePath', 'endPath'): keep.append(cur); cur = []
    def area(pts): return abs(sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts))) / 2) if len(pts) > 2 else 0
    for pts in keep:
        pts = [(round(x), round(y)) for x, y in pts]
        if len(pts) > 1 and pts[0] == pts[-1]: pts = pts[:-1]
        changed = True
        while changed and len(pts) > 3:
            changed = False
            for i in range(len(pts)):
                p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % len(pts)]
                ux, uy = p1[0] - p0[0], p1[1] - p0[1]; vx, vy = p2[0] - p1[0], p2[1] - p1[1]
                lu, lv = math.hypot(ux, uy), math.hypot(vx, vy)
                if lu == 0 or lv == 0 or (abs(ux * vy - uy * vx) / (lu * lv) < 2e-3 and ux * vx + uy * vy > 0):
                    del pts[i]; changed = True; break
        if area(pts) < amin: continue
        pen.moveTo(pts[0])
        for q in pts[1:]: pen.lineTo(q)
        pen.closePath()
    return out

# ---- crénage par profils
def profile(p, adv):
    rp = RecordingPen(); p.draw(rp); segs = []; cur = st = None
    for op, a in rp.value:
        if op == 'moveTo': cur = st = a[0]
        elif op == 'lineTo': segs.append((cur, a[0])); cur = a[0]
        elif op == 'closePath':
            if cur != st: segs.append((cur, st))
    Lp, Rp = [], []
    for y in range(-155, 1000, 10):
        xs = [x0 + (y - a) * (x1 - x0) / (b - a) for (x0, a), (x1, b) in segs if (a <= y < b) or (b <= y < a)]
        Lp.append(round(min(xs)) if xs else None); Rp.append(round(adv - max(xs)) if xs else None)
    return tuple(Lp), tuple(Rp)

def kerning(glyphs, w, info):
    dig = set(info['digits'])
    skip = set(info['marks']) | {'space', 'uni00A0', 'underscore'} | dig | {n for n, (p, a) in glyphs.items() if a == glyphs['zero'][1] and '_' not in n and len(n) > 1}
    LC, RC = {}, {}
    for n, (p, adv) in glyphs.items():
        if n in skip or not p.bounds: continue
        l, r = profile(p, adv); LC.setdefault(l, []).append(n); RC.setdefault(r, []).append(n)
    gmin = w.g + 4; lines = []; npairs = 0
    lcl = {k: f'@L{i}' for i, k in enumerate(LC)}; rcl = {k: f'@R{i}' for i, k in enumerate(RC)}
    for k, c in lcl.items(): lines.append(f'{c} = [{" ".join(sorted(LC[k]))}];')
    for k, c in rcl.items(): lines.append(f'{c} = [{" ".join(sorted(RC[k]))}];')
    lines.append('feature kern {')
    for r, rn in rcl.items():
        for l, ln in lcl.items():
            if all(n in dig for n in RC[r]) and all(n in dig for n in LC[l]): continue
            gaps = [a + b for a, b in zip(r, l) if a is not None and b is not None]
            if not gaps: continue
            m = min(gaps); mean = sum(gaps) / len(gaps)
            k = -min(0.6 * (mean - w.G), m - gmin, 0.7 * w.W)
            if k <= -6: lines.append(f'  pos {rn} {ln} {round(k)};'); npairs += 1
    lines.append('} kern;')
    return '\n'.join(lines) + '\n', npairs

def features(order, info, anc):
    go = set(order); f = []
    lig = sorted(info['liga'], key=lambda x: (-len(x[1]), x[0]))
    f.append('languagesystem DFLT dflt; languagesystem latn dflt; languagesystem cyrl dflt;')
    f.append('lookup LIGA {'); f += [f'  sub {" ".join(s)} by {n};' for n, s in lig if n in go and all(c in go for c in s)]; f.append('} LIGA;')
    f.append('lookup SS01 {'); f += [f'  sub {a} by {b};' for a, b in info['ss01']]; f.append('} SS01;')
    f.append('lookup SS02 {'); f += [f'  sub {a} by {b};' for a, b in info['ss02']]; f.append('} SS02;')
    f += ['feature liga { lookup LIGA; } liga;',
          'feature ss01 { featureNames { name "Lettres doubles : fût partagé"; }; lookup SS01; } ss01;',
          'feature ss02 { featureNames { name "Losanges dans les creux"; }; lookup SS02; } ss02;']
    tm = [f'uni{c:04X}' for c in TOP]; bm = [f'uni{c:04X}' for c in BOT]
    g = [f'markClass [{" ".join(tm)}] <anchor 0 {CAP + MGAP}> @TOP;', f'markClass [{" ".join(bm)}] <anchor 0 0> @BOT;', 'feature mark {']
    for n, (x, xb) in anc.items(): g.append(f'  pos base {n} <anchor {x} {CAP + MGAP}> mark @TOP <anchor {xb} 0> mark @BOT;')
    g.append('} mark;')
    ligs = [n for n, s in info['liga']] + [b for a, b in info['ss01']]
    d = ['table GDEF {', f'  GlyphClassDef [{" ".join(n for n in order if n not in set(ligs) and n not in set(info["marks"]) and n != ".notdef")}], [{" ".join(ligs)}], [{" ".join(info["marks"])}], ;']
    for n in ligs:
        c = info['caret'].get(n) or info['caret'][n.split('.')[0]]
        d.append(f'  LigatureCaretByPos {n} {" ".join(str(v) for v in c)};')
    d.append('} GDEF;')
    return '\n'.join(f) + '\n', '\n'.join(g) + '\n', '\n'.join(d) + '\n'

def write(nom, outf):
    w = WEIGHTS[nom]; gl, cmap, info = build(w)
    psn = f'{FAMILY}-{nom}'; fam = f'{FAMILY} {nom}'
    uni = {n: min(c for c, m in cmap.items() if m == n) for n in set(cmap.values())}
    based = sorted(uni, key=lambda n: uni[n])
    order = ['.notdef'] + based + sorted(n for n in gl if n not in uni)
    cs, hmtx = {}, {}; S = w.S
    nd = T2CharStringPen(500, None); D(rect(50, 0, 450, CAP), rect(50 + S, S, 450 - S, CAP - S)).draw(nd)
    cs['.notdef'] = nd.getCharString(); hmtx['.notdef'] = (500, 50)
    ys = []; cleaned = {}
    for n in order[1:]:
        p, adv = gl[n]; p = clean(p); b = p.bounds; cleaned[n] = (p, adv)
        pen = T2CharStringPen(round(adv), None); p.draw(pen); cs[n] = pen.getCharString()
        hmtx[n] = (round(adv), round(b[0]) if b and b != (0, 0, 0, 0) else 0)
        if b and b != (0, 0, 0, 0): ys += [b[1], b[3]]
    assert max(ys) <= WIN_ASC and -min(ys) <= WIN_DESC, ('hors des métriques win', max(ys), min(ys))
    fb = FontBuilder(UPM, isTTF=False); fb.setupGlyphOrder(order); fb.setupCharacterMap(cmap)
    fb.setupCFF(psn, {'FullName': fam, 'FamilyName': FAMILY, 'Weight': nom, 'Copyright': '(c) 2026 LaFleurStudio. All rights reserved.',
                      'Notice': f'{FAMILY} by LaFleurStudio.', 'ItalicAngle': 0}, cs, {})
    fb.setupHorizontalMetrics(hmtx); fb.setupHorizontalHeader(ascent=TYPO_ASC, descent=TYPO_DESC)
    lic = ('Free for personal use. Commercial use requires prior written permission from LaFleurStudio '
           '(free or paid, decided case by case): info@lafleurstudio.ch. Usage personnel gratuit ; usage commercial '
           'sur autorisation écrite de LaFleurStudio.')
    nm = {'copyright': '© 2026 LaFleurStudio. All rights reserved.', 'familyName': fam, 'styleName': 'Regular',
          'uniqueFontIdentifier': f'{VERSION};LFST;{psn}', 'fullName': fam, 'version': f'Version {VERSION}', 'psName': psn,
          'manufacturer': 'LaFleurStudio', 'designer': 'Jonathan Kern', 'vendorURL': 'https://jonlekern.github.io/Fonts/',
          'licenseDescription': lic, 'licenseInfoURL': f'https://github.com/Jonlekern/Fonts/blob/main/{SLUG}/LICENCE.txt',
          'typographicFamily': FAMILY, 'typographicSubfamily': nom}
    fb.setupNameTable(nm, mac=False)
    fb.setupOS2(sTypoAscender=TYPO_ASC, sTypoDescender=TYPO_DESC, sTypoLineGap=0, usWinAscent=WIN_ASC, usWinDescent=WIN_DESC,
                sCapHeight=CAP, usWeightClass=w.wclass, sxHeight=CAP, version=4, achVendID='LFST', fsSelection=0x40 | 0x80)
    fb.setupPost(italicAngle=0)
    fb.font['OS/2'].recalcUnicodeRanges(fb.font)
    cps = set(cmap); cpr = 1 << 29
    if 0xE9 in cps: cpr |= 1 << 0
    if 0x10D in cps and 0x171 in cps: cpr |= 1 << 1
    if 0x11F in cps and 0x15F in cps: cpr |= 1 << 4
    if 0x113 in cps and 0x12B in cps: cpr |= 1 << 7
    fb.font['OS/2'].ulCodePageRange1 = cpr; fb.font['OS/2'].ulCodePageRange2 = 0
    fb.font['head'].macStyle = 0; fb.font['head'].fontRevision = float(VERSION)
    fb.font['OS/2'].usDefaultChar = 0; fb.font['OS/2'].usBreakChar = 32
    fb.save(outf)
    ft = TTFont(outf); fs, fm, fd = features(order, info, info['anc']); kf, npairs = kerning(cleaned, w, info)
    addOpenTypeFeaturesFromString(ft, fs, tables=['GSUB', 'name'])
    addOpenTypeFeaturesFromString(ft, kf + fm + fd, tables=['GPOS', 'GDEF'])
    buildStatTable(ft, [dict(tag='wght', name='Weight', values=[dict(value=w.wclass, name=nom, flags=0)])],
                   locations=None, elidedFallbackName=2, macNames=False)
    ft.save(outf)
    return len(order), len(info['liga']), npairs, round(max(ys)), round(min(ys))

if __name__ == '__main__':
    nom, outd = sys.argv[1], sys.argv[2]; os.makedirs(outd, exist_ok=True)
    print(nom, write(nom, os.path.join(outd, f'{FAMILY}-{nom}.otf')))
