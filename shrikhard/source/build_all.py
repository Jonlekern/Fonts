# Fabrique toute la famille Shrikhard, en une commande :
#   python3 source/build_all.py
# Sortie : fonts/variable/ (le curseur Hauteur), fonts/ttf/ (les fixes) et fonts/woff2/.
import os, sys, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables import ttProgram
from fontTools.otlLib.builder import buildStatTable
from fontTools.ttLib.tables._f_v_a_r import NamedInstance
import fabrique as F
import shrikhard as S

ICI = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(ICI, '..', 'fonts')
VERSION = '1.000'
FAMILLE = 'Shrikhard'

# Le curseur Hauteur, de haut en bas : on descend la piste du Lauberhorn jusqu'à la ligne d'arrivée.
ARRETS = [(20, 'Start'), (0, 'Regular'), (-20, 'Hundschopf'), (-40, 'Kernen-S'),
          (-60, 'Haneggschuss'), (-80, 'Ziel-S'), (-100, 'Ziel')]

COPYRIGHT = ('Copyright (c) 2015 Jonny Pinhorn (jonpinhorn.typedesign@gmail.com). '
             'Modifications (Shrikhard) 2026 LaFleurStudio.')
LICENCE = ('This Font Software is licensed under the SIL Open Font License, Version 1.1. '
           'This license is available with a FAQ at: https://openfontlicense.org')


def noms(f, style, ps):
    nm = f['name']
    nm.names = []
    italique = 'Italic' in style
    base = {
        0: COPYRIGHT, 1: FAMILLE, 2: 'Italic' if italique else 'Regular',
        3: f'{VERSION};LFST;{ps}', 4: f'{FAMILLE} {style}' if style != 'Regular' else FAMILLE,
        5: f'Version {VERSION}', 6: ps, 8: 'LaFleurStudio',
        9: 'LaFleurStudio, based on Shrikhand by Jonny Pinhorn',
        10: 'Shrikhard is a modified version of Shrikhand (SIL Open Font License 1.1).',
        11: 'https://jonlekern.github.io/Fonts/', 13: LICENCE, 14: 'https://openfontlicense.org',
    }
    for i, v in base.items():
        nm.setName(v, i, 3, 1, 0x409)


def finitions(f, italique):
    os2 = f['OS/2']
    os2.usWeightClass = 400
    os2.achVendID = 'LFST'
    os2.fsSelection = (os2.fsSelection & ~0b1100001) | (1 if italique else 1 << 6) | (1 << 7)
    f['head'].macStyle = 2 if italique else 0
    f['head'].fontRevision = float(VERSION)
    f['post'].italicAngle = -S.PENTE if italique else 0
    f['post'].underlineThickness = 120
    f['post'].underlinePosition = -82
    for t in ('fpgm', 'cvt ', 'DSIG', 'hdmx', 'LTSH', 'VDMX'):
        if t in f:
            del f[t]
    prep = newTable('prep'); prep.program = ttProgram.Program()
    prep.program.fromAssembly(['PUSHW[ ]', '511', 'SCANCTRL[ ]', 'PUSHB[ ]', '4', 'SCANTYPE[ ]'])
    f['prep'] = prep
    gasp = newTable('gasp'); gasp.version = 1; gasp.gaspRange = {0xFFFF: 15}
    f['gasp'] = gasp
    os2.recalcAvgCharWidth(f)


def stat(f, italique, variable):
    haut = {'tag': 'HAUT', 'name': 'Hauteur',
            'values': [dict(value=v, name=n, **({'flags': 2} if v == 0 else {})) for v, n in ARRETS]
            if variable else [{'value': 0, 'name': 'Regular', 'flags': 2}]}
    poids = {'tag': 'wght', 'name': 'Weight', 'values': [{'value': 400, 'name': 'Regular', 'flags': 2}]}
    ital = {'tag': 'ital', 'name': 'Italic',
            'values': [{'value': 1, 'name': 'Italic'}] if italique
            else [{'value': 0, 'name': 'Roman', 'flags': 2, 'linkedValue': 1}]}
    buildStatTable(f, [haut, poids, ital], elidedFallbackName=2, macNames=False)


def instances(f, italique):
    fvar = f['fvar']
    fvar.axes[0].axisNameID = f['name'].addName('Hauteur', platforms=((3, 1, 0x409),))
    fvar.instances = []
    for v, n in ARRETS:
        nom = n if not italique else ('Italic' if n == 'Regular' else f'{n} Italic')
        i = NamedInstance()
        i.subfamilyNameID = f['name'].addName(nom, platforms=((3, 1, 0x409),), minNameID=256)
        court = n.replace('-', '').replace(' ', '')
        ps = f'{FAMILLE}-' + (('Italic' if n == 'Regular' else court + 'Italic') if italique else court)
        i.postscriptNameID = f['name'].addName(ps, platforms=((3, 1, 0x409),))
        i.coordinates = {'HAUT': v, 'wght': 400}
        fvar.instances.append(i)


def avar(f):
    """La progression du curseur est linéaire : on l'écrit quand même dans une table avar."""
    a = newTable('avar')
    a.segments = {ax.axisTag: {-1.0: -1.0, 0.0: 0.0, 1.0: 1.0} for ax in f['fvar'].axes}
    f['avar'] = a


def sauve(f, nom):
    dossier = 'variable' if '[' in nom else 'ttf'          # les variables à part, comme Guépard
    for d in (dossier, 'woff2'):
        os.makedirs(os.path.join(SORTIE, d), exist_ok=True)
    f.save(os.path.join(SORTIE, dossier, nom + '.ttf'))
    w = TTFont(os.path.join(SORTIE, dossier, nom + '.ttf')); w.flavor = 'woff2'
    w.save(os.path.join(SORTIE, 'woff2', nom + '.woff2'))


def main():
    f, base, mes = F.prepare()
    for italique in (False, True):
        style = 'Italic' if italique else 'Regular'
        # la fixe, à la hauteur 0
        st = F.statique(f, base, mes, italique=italique)
        noms(st, style, f'{FAMILLE}-{style}'); finitions(st, italique); stat(st, italique, False)
        sauve(st, f'{FAMILLE}-{style}')
        # la variable, avec le curseur Hauteur
        vf = F.variable(f, base, mes, italique=italique)
        noms(vf, style, f'{FAMILLE}-{style}'); finitions(vf, italique)
        vf['name'].setName(FAMILLE + ('Italic' if italique else ''), 25, 3, 1, 0x409)
        instances(vf, italique); stat(vf, italique, True); avar(vf)
        sauve(vf, f"{FAMILLE}{'-Italic' if italique else ''}[HAUT]")
        print(style, 'ok')


def archive():
    """Shrikhard.zip : les deux variables, les deux fixes et la licence."""
    racine = os.path.join(ICI, '..')
    with zipfile.ZipFile(os.path.join(racine, 'Shrikhard.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
        for n in ('Shrikhard[HAUT].ttf', 'Shrikhard-Italic[HAUT].ttf'):
            z.write(os.path.join(SORTIE, 'variable', n), n)
        for n in ('Shrikhard-Regular.ttf', 'Shrikhard-Italic.ttf'):
            z.write(os.path.join(SORTIE, 'ttf', n), 'fixes/' + n)
        z.write(os.path.join(racine, 'OFL.txt'), 'OFL.txt')


if __name__ == '__main__':
    main()
    archive()
