# Les images de la page : élargir sans déformer.
#   python3 source/page_images.py
import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFont
import fabrique as F

ICI = os.path.dirname(os.path.abspath(__file__))
IMAGES = os.path.join(ICI, '..', 'images')
FOND, ENCRE, GRIS, TRAIT = (244, 241, 236), (21, 21, 21), (130, 126, 120), (214, 209, 200)
LAB = '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'
MOT = 'Lauberhorn'


def planche(rangs, sortie, taille=300):
    W, H = 3200, 470
    img = Image.new('RGB', (W, H * len(rangs)), FOND); d = ImageDraw.Draw(img)
    lab = ImageFont.truetype(LAB, 38)
    for i, (titre, police) in enumerate(rangs):
        y = i * H
        if i:
            d.line([(0, y), (W, y)], fill=TRAIT, width=3)
        d.text((100, y + 45), titre.upper(), font=lab, fill=GRIS, spacing=4)
        d.text((100, y + 55), MOT, font=ImageFont.truetype(police, taille), fill=ENCRE)
    img.save(sortie)


def main():
    os.makedirs(IMAGES, exist_ok=True)
    f, base, mes = F.prepare()
    tmp = tempfile.mkdtemp()
    brut = os.path.join(tmp, 'brut.ttf'); bon = os.path.join(tmp, 'bon.ttf')
    F.statique(f, base, mes, italique=True, force_x=0).save(brut)
    F.statique(f, base, mes, italique=True).save(bon)
    planche([("Shrikhand d'origine · fûts à 251", F.SOURCE),
             ('Étirée brute à 129 % · fûts à 324', brut),
             ("Élargie sans déformer · fûts à 251, comme à l'origine", bon)],
            os.path.join(IMAGES, 'elargir.png'))


if __name__ == '__main__':
    main()
