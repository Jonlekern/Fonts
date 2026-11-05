import sys, os, json, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFont
import triche, complet, accents
core = json.load(open('gf_core.json'))
anciens = set(triche.glyphes(triche.regles(100)).keys()) | set(".,:;!?'\"‘’“”«»‹›-–—()[]/\\|&@#*+=%_…· ")
nouveaux = [chr(c) for c in core if chr(c) not in anciens and not unicodedata.category(chr(c)).startswith('M') and c != 0xA0]
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 30)
for p in [int(a) for a in sys.argv[1:]] or [100, 900]:
    R = triche.regles(p); G = complet.complet(R)
    rows = []
    for i in range(0, len(nouveaux), 18):
        t = ''.join(nouveaux[i:i + 18])
        fn = f'tmp-pc.png'; accents.render_poly(t, fn, G, R, k=0.16)
        rows.append(Image.open(fn).convert('RGB'))
    W = max(r.width for r in rows)
    sheet = Image.new('RGB', (W, sum(r.height for r in rows) + 10), (0, 0, 0))
    y = 0
    for r in rows: sheet.paste(r, (0, y)); y += r.height
    ImageDraw.Draw(sheet).text((10, 5), str(p), font=F, fill=(255, 210, 60))
    sheet.save(f'complet-{p}.png'); print(p, sheet.size, len(nouveaux), 'caractères')
os.remove('tmp-pc.png')
