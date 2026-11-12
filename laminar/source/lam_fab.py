# LAMINAR : fabrique une graisse.  python3 lam_fab.py <num> <dossier> [italic]
#   Regular = sobre ; Italic = vitesse (les lettres restent droites, trois lignes les traversent)
import sys, os, math, unicodedata as ud
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.agl import AGL2UV
from fontTools.ttLib import TTFont
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from lam_core import *
from lam_letters import letters
from lam_digits import digits, DN
from lam_signs import signs
from lam_marks import extras, accented, LOWER_EXTRA, SPACING, MARK_OF, mark_x, GAP_UP, GAP_SC
from lam_liga import ligs, LIGA, DLIG
from lam_speed import speed

FAMILY = 'LAMINAR'; SLUG = 'laminar'; VERSION = '1.000'; UPM = 1000
WEIGHTS = {'030': (58, 12, 300), '060': (118, 16, 600), '090': (190, 20, 900)}
TYPO_ASC, TYPO_DESC = 1000, -280
WIN_ASC, WIN_DESC = 1080, 300
NAMES_EXTRA = {'onesuperior': 0xB9, 'twosuperior': 0xB2, 'threesuperior': 0xB3, 'Dcroat': 0x110, 'uni2116': 0x2116, 'brokenbar': 0xA6}
CAPS = [chr(i) for i in range(65, 91)]

def unicode_of(n):
    if n in NAMES_EXTRA: return NAMES_EXTRA[n]
    if '.' in n or '_' in n: return None
    if n.startswith('uni') and len(n) == 7: return int(n[3:], 16)
    return AGL2UV.get(n)

def lig_name(pair, lower):
    return '_'.join(ch.lower() if lower else ch for ch in pair)

def build(num):
    S, h, wc = WEIGHTS[num]; w = Wt(num, S, h, wc)
    cc, cs = C(w, CAP), C(w, SC, sc=True)
    Gc, Gs = letters(cc), letters(cs)
    Gc.update(extras(cc, Gc)); Gs.update(extras(cs, Gs))
    Dg, DW = digits(cc)
    Sg = signs(w, cc, Gc, Gs, Dg, DW)
    A = accented(cc, cs, Gc, Gs, Sg['quoteright'].ink)
    out = {}; cof = {}; anc = {}
    def anchor(n, g, c_, B):
        l = sb_of(w, c_, g.sides[0]) - g.x0
        anc[n] = (round(mark_x(B, g, c_) + l), c_.H + (GAP_UP if not c_.sc else GAP_SC), round(c_.S / 2 + l) if B in 'KLNR' else round(mark_x(B, g, c_) + l))
    for ch in CAPS:
        out[ch] = place(Gc[ch], w, cc); cof[ch] = 'w'; anchor(ch, Gc[ch], cc, ch)
        out[ch.lower()] = place(Gs[ch], w, cs); cof[ch.lower()] = 'w'; anchor(ch.lower(), Gs[ch], cs, ch)
    for n in ('AE', 'OE', 'Oslash', 'Eth', 'Dcroat', 'Thorn', 'Lslash', 'Hbar', 'uni1E9E'):
        out[n] = place(Gc[n], w, cc); cof[n] = 'w'
    for ln, cn in LOWER_EXTRA.items():
        out[ln] = place(Gs[cn], w, cs); cof[ln] = 'w'
    pad = round(0.55 * w.SB)
    for n in DN:
        out[n] = (mv(Dg[n], pad), DW + 2 * pad); cof[n] = 'w'
    out['zero.zero'] = None
    del out['zero.zero']
    for n, g in Sg.items():
        nn = 'uni2116' if n == 'numero' else n
        out[nn] = place(g, w, cc)
    cof['ampersand'] = 'w'
    for n, g in A.items():
        if n.startswith('_sp_'): out[n[4:]] = place(g, w, cc); continue
        cp = int(n[3:], 16)
        if 0x300 <= cp < 0x370:
            out[n] = (g.ink, 0); cof[n] = 'm'; continue
        up = chr(cp).isupper(); out[n] = place(g, w, cc if up else cs); cof[n] = 'w'
    for lw, G_, c_ in ((False, Gc, cc), (True, Gs, cs)):
        L = ligs(c_, G_)
        for pair, g in L.items():
            nm = lig_name(pair, lw); out[nm] = place(g, w, c_); cof[nm] = 'w'; CARET[nm] = round(out[nm][1] / 2)
    out['space'] = (P(), round(0.24 * CAP)); out['uni00A0'] = out['space']
    MATH = [n for n in ('plus', 'uni2212', 'multiply', 'divide', 'equal', 'less', 'greater') if n in out]
    mw = max(out[n][1] for n in MATH)
    for n in MATH:
        p, adv = out[n]; out[n] = (mv(p, (mw - adv) / 2), mw)
    return out, cof, w, anc

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
    def straighten(c):
        if not all(op in ('moveTo', 'lineTo', 'closePath', 'endPath') for op, a in c):
            changed = True
            while changed:
                changed = False
                for i in range(1, len(c) - 1):
                    op, a = c[i]
                    if op != 'lineTo' or c[i + 1][0] != 'lineTo': continue
                    p0 = c[i - 1][1][-1]; p1 = a[0]; p2 = c[i + 1][1][0]
                    ux, uy = p1[0] - p0[0], p1[1] - p0[1]; vx, vy = p2[0] - p1[0], p2[1] - p1[1]
                    lu, lv = math.hypot(ux, uy), math.hypot(vx, vy)
                    if lu and lv and abs(ux * vy - uy * vx) / (lu * lv) < 1e-3 and ux * vx + uy * vy > 0:
                        del c[i]; changed = True; break
            return c
        pts = [a[0] for op, a in c if op in ('moveTo', 'lineTo')]
        if len(pts) > 1 and pts[0] == pts[-1]: pts = pts[:-1]
        changed = True
        while changed and len(pts) > 3:
            changed = False
            for i in range(len(pts)):
                p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % len(pts)]
                ux, uy = p1[0] - p0[0], p1[1] - p0[1]; vx, vy = p2[0] - p1[0], p2[1] - p1[1]
                lu, lv = math.hypot(ux, uy), math.hypot(vx, vy)
                if lu == 0 or (lv and abs(ux * vy - uy * vx) / (lu * lv) < 1e-3 and ux * vx + uy * vy > 0):
                    del pts[i]; changed = True; break
        return [('moveTo', (pts[0],))] + [('lineTo', (p,)) for p in pts[1:]] + [('closePath', ())]
    for c in keep:
        if area(c) < amin: continue
        for op, a in straighten(c): getattr(pen, op)(*a)
    return out

POS = ('init', 'fina', 'isol')
STASH = {}; CARET = {}
def vitesse(out, cof, w, anc):
    """variantes : défaut = au milieu du mot ; .init .fina .isol ; .b* lignes derrière (ss01) ; .p .pt traîne seule (ss02)"""
    import lam_speed
    V = {}; A2 = {}
    for n, (p, adv) in out.items():
        if cof.get(n) != 'w': V[n] = (p, adv); continue
        def put(nm, pos, mode):
            V[nm] = speed(p, adv, w, pos, mode)
            if n in anc: a = anc[n]; dx = lam_speed.LAST_DX[0]; A2[nm] = (round(a[0] + dx), a[1], round(a[2] + dx))
        put(n, 'med', 'cut')
        for pos in POS: put(f'{n}.{pos}', pos, 'cut')
        put(f'{n}.b', 'med', 'behind')
        for pos in POS: put(f'{n}.b{pos}', pos, 'behind')
        put(f'{n}.p', 'med', 'trail'); put(f'{n}.pt', 'init', 'trail')
    anc.clear(); anc.update(A2)
    return V

TOPM = [0x300, 0x301, 0x302, 0x303, 0x304, 0x306, 0x307, 0x308, 0x30A, 0x30B, 0x30C]
BOTM = [0x326, 0x327, 0x328]
def features(order, cof, italic, anc=None):
    go = set(order); fea = []
    def ex(pairs): return [(a, b) for a, b in pairs if a in go and b in go]
    li = [(lig_name(p, lw), p if not lw else p.lower()) for p in LIGA for lw in (False, True)]
    dl = [(lig_name(p, lw), p if not lw else p.lower()) for p in DLIG for lw in (False, True)]
    fea.append('lookup LIGA {'); fea += [f'  sub {" ".join(s)} by {n};' for n, s in li if n in go]; fea.append('} LIGA;')
    fea.append('lookup DLIG {'); fea += [f'  sub {" ".join(s)} by {n};' for n, s in dl if n in go]; fea.append('} DLIG;')
    feat = ['feature liga { lookup LIGA; } liga;', 'feature dlig { lookup DLIG; } dlig;']
    if italic:
        W = [n for n in order if cof.get(n) == 'w']
        cls = lambda suf: ' '.join(f'{n}{suf}' for n in W)
        fea.append(f'@W = [{cls("")}];')
        for pos in POS: fea.append(f'@W_{pos} = [{cls("." + pos)}];')
        fea.append('@ANY = [@W @W_init @W_fina @W_isol];')
        fea.append('lookup ISOL { ignore sub @ANY @W\'; ignore sub @W\' @ANY; sub @W\' by @W_isol; } ISOL;')
        fea.append('lookup INIT { ignore sub @ANY @W\'; sub @W\' by @W_init; } INIT;')
        fea.append('lookup FINA { ignore sub @W\' @ANY; sub @W\' by @W_fina; } FINA;')
        fea.append(f'lookup SS01 {{ sub @W by [{cls(".b")}]; sub @W_init by [{cls(".binit")}]; sub @W_fina by [{cls(".bfina")}]; sub @W_isol by [{cls(".bisol")}]; }} SS01;')
        fea.append(f'lookup SS02 {{ sub @W by [{cls(".p")}]; sub @W_init by [{cls(".pt")}]; sub @W_fina by [{cls(".p")}]; sub @W_isol by [{cls(".pt")}]; }} SS02;')
        feat += ['feature calt { lookup ISOL; lookup INIT; lookup FINA; } calt;',
                 'feature ss01 { featureNames { name "Lignes derrière les lettres"; }; lookup SS01; } ss01;',
                 'feature ss02 { featureNames { name "Traîne seule"; }; lookup SS02; } ss02;']
    gp = []
    if anc:
        tm = [f'uni{c:04X}' for c in TOPM if f'uni{c:04X}' in go]; bm = [f'uni{c:04X}' for c in BOTM if f'uni{c:04X}' in go]
        gp.append(f'markClass [{" ".join(tm)}] <anchor 0 0> @TOP;')
        gp.append(f'markClass [{" ".join(bm)}] <anchor 0 0> @BOT;')
        gp.append('feature mark {')
        for n, (x, y, xb) in anc.items():
            if n in go: gp.append(f'  pos base {n} <anchor {x} {y}> mark @TOP <anchor {xb} 0> mark @BOT;')
        gp.append('} mark;')
    ligs_ = [n for n in order if '_' in n and '.' not in n]
    if ligs_:
        gp.append('table GDEF {')
        for n in ligs_: gp.append(f'  LigatureCaretByPos {n} {CARET[n]};')
        gp.append('} GDEF;')
    return '\n'.join(fea + feat) + '\n', '\n'.join(gp) + '\n'

def write(num, outf, italic=False):
    S, h, wc = WEIGHTS[num]; out, cof, w, anc = build(num)
    gl = vitesse(out, cof, w, anc) if italic else out
    style = 'Italic' if italic else 'Regular'
    fam = f'{FAMILY} {num}'; full = fam + (' Italic' if italic else ''); psn = f'{FAMILY}-{num}' + ('Italic' if italic else '')
    base = sorted([n for n in gl if '.' not in n], key=lambda n: (unicode_of(n) or 0x10FFFF, n))
    order = ['.notdef'] + base + sorted(n for n in gl if '.' in n)
    cs, hmtx, cmap = {}, {}, {}
    nd = T2CharStringPen(500, None); D(rect(50, 0, 450, CAP), rect(50 + S, S, 450 - S, CAP - S)).draw(nd)
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
                sCapHeight=CAP, usWeightClass=wc, sxHeight=SC, version=4, achVendID='LFST',
                fsSelection=(0x01 if italic else 0x40) | 0x80)
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
    ft = TTFont(outf); fs, fp = features(order, cof, italic, anc); addOpenTypeFeaturesFromString(ft, fs, tables=['GSUB', 'name'])
    STASH[outf] = fp
    from fontTools.otlLib.builder import buildStatTable
    buildStatTable(ft, [dict(tag='wght', name='Weight', values=[dict(value=wc, name=num, flags=0)]),
                        dict(tag='ital', name='Italic', values=[dict(value=1, name='Italic', flags=0) if italic else dict(value=0, name='Roman', flags=0x2, linkedValue=1)])],
                   locations=None, elidedFallbackName=2, macNames=False)
    ft.save(outf)
    return len(order), round(max(ys)), round(min(ys))

if __name__ == '__main__':
    num, outd = sys.argv[1], sys.argv[2]; it = len(sys.argv) > 3 and sys.argv[3] == 'italic'; os.makedirs(outd, exist_ok=True)
    p = os.path.join(outd, f'{FAMILY}-{num}{"Italic" if it else ""}.otf')
    r = write(num, p, it)
    k = 0
    import lam_kshim, lam_kern
    lam_kshim.ST = WEIGHTS[num][0]; lam_kern.CAP = CAP
    if not it:
        k = lam_kern.kern_font(p, extra=STASH[p].split('table GDEF')[0])
        ft = TTFont(p); addOpenTypeFeaturesFromString(ft, 'table GDEF' + STASH[p].split('table GDEF')[1], tables=['GDEF']); ft.save(p)        # le crénage écrit aussi la feature mark (même table GPOS)
    else:                                    # vitesse : pas de crénage entre lettres (les lignes resteraient coupées) ; seulement lettre ↔ ponctuation
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            tp = os.path.join(td, 'p.otf'); write(num, tp, False); lam_kern.kern_font(tp)
        pairs, mem, NOTL = lam_kern.LAST
        go = set(TTFont(p).getGlyphOrder())
        def side(c, suf):
            return [m + s for m in mem[c] for s in suf if m + s in go] if c not in NOTL else [m for m in mem[c] if m in go]
        L = ('.fina', '.isol', '.bfina', '.bisol', '.p', '.pt'); R = ('.init', '.isol', '.binit', '.bisol', '.pt', '.p')
        kf = ['feature kern {']
        for (a, b), v in pairs.items():
            if a not in NOTL and b not in NOTL: continue          # deux lettres : jamais
            la, rb = side(a, L), side(b, R)
            if la and rb: kf.append(f'  pos [{" ".join(la)}] [{" ".join(rb)}] {v};'); k += 1
        fin = [n for n in go if n.endswith(('.fina', '.isol', '.bfina', '.bisol'))]
        kf.append(f'  pos [{" ".join(sorted(fin))}] [period comma ellipsis] {-round(0.5 * Wt(num, *WEIGHTS[num]).B)};'); k += 1   # le point se rapproche du bout rond des lignes
        kf.append('} kern;')
        ft = TTFont(p); addOpenTypeFeaturesFromString(ft, STASH[p] + '\n'.join(kf) + '\n', tables=['GPOS', 'GDEF']); ft.save(p)
    print(num, 'vitesse' if it else 'sobre', r, k, 'paires')
