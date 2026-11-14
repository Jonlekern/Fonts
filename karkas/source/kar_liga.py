# KARKAS : les liaisons. Un dessin par groupe de lettres, fabriqué avec les pièces des lettres.
from kar_core import *
from kar_letters import letter, LM, RM, Gl, RU, wedge

AZ = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
# groupes de trois : chaînes de fûts partagés (les groupes autour du T sont dans TRI_T)
TRI_S = ('AND ANN ANE ANA ANO AUR AUD AME AMO AMA AMB AMP ANK ANC ANG DAN DON DUR DUN DOU DAM HAN HON HUM HOU HOM HAR HAB HAU HUN '
         'JOU JAM JOB MAN MON MOU MAR MOR MUR MAL MAG MOD MME MMA NNE NNA NOU NOM NOR NOB NAL NAR NDE NDR NDA NDO NUM NUL '
         'OUR OUN OUL OUP OUB OUV OUC OUE OUG OME OMM OMB OMP ONE ONN OND ONG ONC ONA ONO UNE UND UNA UNG UNC UNK UME UMB UMP '
         'QUE QUA QUO VAN VOU VAL VAR VOL VOR WOR WAR WAL WAN WON OHN AHN UHR').split()
TRI_T = ('ATA ATE ATO ATU ATR ATH ETA ETE ETO ETR ETH ITA ITE ITO ITU ITH ITR ITY OTA OTE OTH OTR UTA UTE UTO UTR UTH '
         'NTA NTE NTO NTR NTH NTS RTA RTE RTH RTO RTS STA STE STO STU STR STY STI ATI ETI ITI NTI RTI OTI UTI CTE CTU CTO CTA '
         'PTE PTA LTA LTE LTO FTE FTA XTE XTR YTE').split()
TRI_RU = ('СТА СТО СТИ СТЕ СТР СТВ ЕТС АТЬ ИТЬ ЕТЬ ОТО ЕТЕ ИТЕ АТА ОТА НТА АТО НИЕ НОМ НОВ НОЕ НОС ИНО ИМО ИНЕ АНО АНЕ ОНО ОНЕ ЛИН ЛАН ЛОН ЛЕН ИЛО АЛО ИЛИ МОС МОН МИН МАН ПОМ ПОН ПАН ПИЛ ПОЛ ПАЛ ШИЛ ШИН ИНГ АНГ ОНГ'.split())
NOI = {'L': 'IL', 'C': 'IC', 'P': 'IP'}       # lettres qu'on ne loge pas (LI ressemblerait à U, CI à O, PI à R)

def shared(w, s, y0=0, y1=CAP, inks=None):
    """chaîne de fûts partagés : le fût droit d'une lettre est le fût gauche de la suivante"""
    S = w.S; x = 0; parts = []
    for i, ch in enumerate(s):
        g = inks[i] if inks and inks.get(i) else letter(ch, w, y0, y1); parts.append(mv(g.ink, x))
        if i < len(s) - 1: parts.append(mv(wedge(ch, w, y0, y1, 'R'), x) if wedge(ch, w, y0, y1, 'R') else None)
        if i > 0: parts.append(mv(wedge(ch, w, y0, y1, 'L'), x) if wedge(ch, w, y0, y1, 'L') else None)
        x += g.w - S
    return Gl(U(*parts), x + S, s[0] in LM, s[-1] in RM)

def small(ch, w, y0, y1):
    return letter(ch, w, y0, y1, nest=True)

def nest(w, a, b, y0=0, y1=CAP):
    """a grande, b logée dans son creux"""
    S, B, g, W = w.S, w.B, w.g, w.W; h = y1 - y0; yb = y0 + round(0.68 * h); x = S + g
    if a == 'L':
        s = small(b, w, y0 + B + g, y1)
        return Gl(U(rect(0, y0, S, y1), rect(0, y0, x + s.w, y0 + B), mv(s.ink, x)), x + s.w, True, False)
    if a == 'C':
        s = small(b, w, y0 + B + g, y1 - B - g)
        return Gl(U(rect(0, y0, S, y1), rect(0, y0, x + s.w, y0 + B), rect(0, y1 - B, x + s.w, y1), mv(s.ink, x)), x + s.w, True, False)
    if a == 'Г':
        s = small(b, w, y0, y1 - B - g)
        return Gl(U(rect(0, y0, S, y1), rect(0, y1 - B, x + s.w, y1), mv(s.ink, x)), x + s.w, True, False)
    if a == 'F':
        s = small(b, w, y0, yb - B / 2 - g)
        return Gl(U(rect(0, y0, S, y1), rect(0, y1 - B, x + s.w, y1), rect(0, yb - B / 2, x + s.w, yb + B / 2), mv(s.ink, x)), x + s.w, True, False)
    if a == 'P':
        s = small(b, w, y0, yb - B / 2 - g); r = x + s.w
        return Gl(U(rect(0, y0, S, y1), rect(0, y1 - B, r, y1), rect(0, yb - B / 2, r, yb + B / 2), rect(r - S, yb - B / 2, r, y1), mv(s.ink, x)), r, True, False)
    raise KeyError(a)

def tee(w, a, b, y0=0, y1=CAP):
    """T avec une lettre logée sous chaque bras (a avant, b après ; '' = rien)"""
    S, B, g, W = w.S, w.B, w.g, w.W; x = 0; parts = []
    if a:
        s = small(a, w, y0, y1 - B - g); parts.append(s.ink); x = s.w + g
    else: x = (W - S) / 2
    parts.append(rect(x, y0, x + S, y1)); xs = x; x += S
    if b:
        s = small(b, w, y0, y1 - B - g); parts.append(mv(s.ink, x + g)); x += g + s.w
    else: x += (W - S) / 2
    parts.append(rect(0, y1 - B, x, y1))
    return Gl(U(*parts), x, False, False)

def stack(w, ch, y0=0, y1=CAP):
    """lettre double : deux étages"""
    g = w.g; ym = (y0 + y1) / 2
    a = small(ch, w, ym + g / 2, y1); b = small(ch, w, y0, ym - g / 2)
    return Gl(U(a.ink, b.ink), a.w, False, False)

def groups():
    """nom du groupe -> (sorte, lettres)"""
    L = {}
    for alpha, tee_, nests in ((AZ, 'T', 'LCFP'), (RU.replace('Й', ''), 'Т', 'Г')):       # le Й garde sa brève : pas de liaison
        for a in alpha:
            for b in alpha:
                if a in RM and b in LM and a != b: L[a + b] = ('share', a + b)
        for a in nests:
            for b in alpha:
                if b != a and b not in NOI.get(a, '')[:1] and a + b not in L: L[a + b] = ('nest', a + b)
        for b in alpha:
            if b != tee_:
                L[tee_ + b] = ('tee', ('', b)); L[b + tee_] = ('tee', (b, ''))
        for ch in alpha: L[ch + ch] = ('stack', ch)
    for t in TRI_S:
        if t[0] in RM and t[1] in RM and t[1] in LM and t[2] in LM and t[0] != t[1] != t[2]: L[t] = ('share', t)
    for t in TRI_T:
        assert t[1] == 'T' and 'T' not in (t[0], t[2]), t
        L[t] = ('tee', (t[0], t[2]))
    for t in TRI_RU:
        if t[1] == 'Т': L[t] = ('tee', (t[0], t[2]))
        elif t[0] in RM and t[1] in RM and t[1] in LM and t[2] in LM and t[0] != t[1] != t[2]: L[t] = ('share', t)
    return L

def draw(w, kind, arg):
    if kind == 'share': return shared(w, arg)
    if kind == 'nest': return nest(w, arg[0], arg[1])
    if kind == 'tee': return tee(w, arg[0], arg[1])
    if kind == 'stack': return stack(w, arg)

def segment(text, G=None):
    """découpe un mot comme le fera la police : le plus long groupe d'abord"""
    G = G or groups(); out = []; i = 0
    while i < len(text):
        for n in (3, 2):
            if text[i:i + n] in G: out.append(text[i:i + n]); i += n; break
        else: out.append(text[i]); i += 1
    return out
