import sys, os
from PIL import Image, ImageDraw, ImageFont
dossier, out = sys.argv[1], sys.argv[2]
textes = [
    ('Français', 'Ça brûle ! Où êtes-vous, cœur ? Noël à l’île, été.'),
    ('Deutsch', 'Größe, Straße, Übermaß — GROẞE ÄRGER.'),
    ('Español', '¿Qué tal, señor Muñoz? ¡Año nuevo, ESPAÑA!'),
    ('Português', 'São João, coração e ação. AÇÚCAR, MÃE.'),
    ('Íslenska', 'Þú ert ðað, Ægir! Ég sá Ölfusá.'),
    ('Dansk / Norsk', 'Høj sø, Århus, Øresund, Æblegrød.'),
    ('Signes', '€ £ $ ¥ ¢ ¤ © ® ™ § ¶ ° ± × ÷ − ¬ • † ‡ ‰ « » ‹ › „ ‚ ¡ ¿ ª º ¹ ² ³ ¼ ½ ¾ µ ƒ ¦'),
]
graisses = ['Hairline', 'Regular', 'Black']
L = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 24)
h_l = 100
im = Image.new('RGB', (3300, 60 + len(textes) * len(graisses) * h_l + len(textes) * 30), (0, 0, 0)); d = ImageDraw.Draw(im)
y = 20
for nom, t in textes:
    d.text((20, y), nom, font=L, fill=(255, 210, 60)); y += 30
    for g in graisses:
        F = ImageFont.truetype(os.path.join(dossier, f'Nexum-{g}.ttf'), 64, layout_engine=ImageFont.Layout.RAQM)
        d.text((40, y), t, font=F, fill=(238, 238, 238)); y += h_l
im.save(out); print(im.size)
