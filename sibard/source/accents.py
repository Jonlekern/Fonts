# Les accents de Sibard et les lettres accentuées (le jeu d'Escapement).
import unicodedata
from tuyaux import Tuyau as T
from dessin import D, point, decale
from minuscules import MINUSCULES, _signe
from capitales import CAPITALES
from signes import P, ef, eg, virgule

# les lettres accentuées du jeu
JEU = ('ÀÁÂÃÄÅÇÈÉÊËÌÍÎÏÑÒÓÔÕÖÙÚÛÜÝàáâãäåçèéêëìíîïñòóôõöùúûüýÿĀāĂăĄąĆćĊċČčĎďĒēĖėĘęĚěĞğĠġĢģĪīĮįİĶķĹĺĻļĽľŃńŅņŇň'
       'ŐőŔŕŘřŚśŞşŠšŤťŪūŮůŰűŲųŴŵŶŷŸŹźŻżŽžȘșȚțẀẁẂẃẄẅỲỳ')
NOMS = {'̀': 'grave', '́': 'acute', '̂': 'circumflex', '̃': 'tilde', '̄': 'macron', '̆': 'breve', '̇': 'dotaccent',
        '̈': 'dieresis', '̊': 'ring', '̋': 'hungarumlaut', '̌': 'caron', '̦': 'commaaccent', '̧': 'cedilla', '̨': 'ogonek'}
ESPACANTS = {'`': 'grave', '´': 'acute', 'ˆ': 'circumflex', 'ˇ': 'caron', '¨': 'dieresis', '¯': 'macron', '˘': 'breve',
             '˙': 'dotaccent', '˚': 'ring', '˜': 'tilde', '˝': 'hungarumlaut', '¸': 'cedilla', '˛': 'ogonek'}
DESSOUS = {'commaaccent', 'cedilla', 'ogonek'}


def accent(nom, d, cx, y):
    """Les tuyaux d'un accent posé sur (cx, y) : y est le bas de l'accent (ou la ligne de base pour ceux du dessous)."""
    g = eg(d) * 0.8; f = ef(d) * 1.25
    if nom == 'grave':
        return [P([(cx - 70, y + 150), (cx + 30, y)], d, g, k=[1, 0.1], debut='h')]
    if nom == 'acute':
        return [P([(cx + 70, y + 150), (cx - 30, y)], d, g, k=[1, 0.1], debut='h')]
    if nom == 'hungarumlaut':
        return [P([(cx + 70 + dx, y + 150), (cx - 30 + dx, y)], d, g * 0.85, k=[1, 0.1], debut='h') for dx in (-75, 75)]
    if nom == 'circumflex':
        return [P([(cx - 100, y), (cx, y + 130), (cx + 100, y)], d, (g * 0.8, f), r=d.c * 0.3, debut='h', fin='h')]
    if nom == 'caron':
        return [P([(cx - 100, y + 130), (cx, y), (cx + 100, y + 130)], d, (g * 0.8, f), r=d.c * 0.3, debut='h', fin='h')]
    if nom == 'tilde':
        return [P([(cx - 110, y + 20), (cx - 40, y + 110), (cx + 40, y + 20), (cx + 110, y + 110)], d, f * 1.2, r=40)]
    if nom == 'macron':
        return [P([(cx - 100, y + 50), (cx + 100, y + 50)], d, f * 1.2)]
    if nom == 'breve':
        return [P([(cx - 90, y + 125), (cx - 90, y + 25), (cx + 90, y + 25), (cx + 90, y + 125)], d, f, r=80)]
    if nom == 'dotaccent':
        s = d.Fm * 0.85
        return [point(cx, y + s / 2 + 10, s)]
    if nom == 'dieresis':
        s = d.Fm * 0.8
        return [point(cx - s * 0.5 - 40, y + s / 2 + 10, s), point(cx + s * 0.5 + 40, y + s / 2 + 10, s)]
    if nom == 'ring':
        return [P([(cx - 55, y + 20), (cx - 55, y + 130), (cx + 55, y + 130), (cx + 55, y + 20)], d, f, r=55, ferme=True)]
    if nom == 'cedilla':
        return [P([(cx + 10, y + 6), (cx + 10, y - 60), (cx + 70, y - 60), (cx + 70, y - 150), (cx - 50, y - 150)], d, f, r=38, k=[1, 1, 1, 1, 0.2], fin='v')]
    if nom == 'ogonek':
        return [P([(cx + 20, y + 6), (cx - 50, y - 70), (cx - 50, y - 150), (cx + 60, y - 150)], d, f, r=44, k=[1, 1, 1, 0.2], fin='v')]
    if nom == 'commaaccent':
        from dessin import reduit
        t, _ = virgule(d)
        s = d.Fm * 1.02; e = 0.55
        return reduit(t, e, cx - (d.L + s / 2 + 10) * e, y - 44 - s * e)
    raise KeyError(nom)


def _decompose(c):
    n = unicodedata.normalize('NFD', c)
    base, marques = n[0], [NOMS[x] for x in n[1:]]
    if c in 'ĢĶĻŅŖȘȚģķļņŗșțŞŢşţ' and marques == ['cedilla'] and c not in 'ŞşÇç':
        marques = ['commaaccent']
    return base, marques


def accentuee(c, d):
    """La lettre accentuée : la lettre, plus son accent (ou ses accents) à la bonne hauteur."""
    base, marques = _decompose(c)
    if base == 'i' and any(m not in DESSOUS for m in marques):
        base = 'ı'
    if base == 'j' and any(m not in DESSOUS for m in marques):
        base = 'ȷ'
    table = {**MINUSCULES, **CAPITALES}
    t, ch = table[base](d)
    xs = [p[0] for u in t if not getattr(u, 'hors', False) for p in u.pts]
    cx = (min(xs) + max(xs)) / 2 + (d.F * 0.15 if max(xs) - min(xs) > 1 else 0)
    haut = d.cap if base.isupper() else (d.asc if base in 'bdfhklt' else d.x)
    for mq in marques:
        if c in 'ďľťĽ' and mq == 'caron':          # le caron vertical : une goutte à droite de la lettre
            x = max(xs) + (d.Fd / 2 if base != 'L' else -60) + 34
            t.append(_signe(P([(x + 44, d.asc if base != 'L' else d.cap), (x, (d.asc if base != 'L' else d.cap) - 190)], d, eg(d) * 0.8, k=[1, 0], debut='h')))
            if base in 'dt':
                ch += 60
            continue
        if mq in DESSOUS:
            x = cx
            if mq == 'ogonek':
                x = max(xs) - (0 if base in 'AaUu' else d.F * 0.6)
            if mq == 'commaaccent' and base == 'g':        # le ģ porte sa virgule en haut, retournée
                t.extend(_signe(u) for u in accent('acute', d, cx, d.x + 60))
                continue
            t.extend(_signe(u) for u in accent(mq, d, x, 0 if mq != 'commaaccent' else 0))
        else:
            t.extend(_signe(u) for u in accent(mq, d, cx, haut + 56))
    return t, ch


def espacant(nom, d):
    """L'accent seul, avec sa chasse."""
    cx = d.L + 130
    t = accent(nom, d, cx, d.x + 56 if nom not in DESSOUS else 0)
    return t, 2 * d.L + 260


ACCENTUEES = {c: (lambda d, c=c: accentuee(c, d)) for c in JEU}
