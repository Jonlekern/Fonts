# L'accueil, en léger : chaque police des cartes réduite aux seules lettres que la page affiche.
#   python3 outils/accueil.py
# À relancer après chaque changement de carte (nouvelle police, nouveau nom, nouvel exemple).
# Les versions réduites vont dans shared/accueil/ ; index.html pointe dessus. Les pages des polices et les téléchargements gardent les fichiers complets.
import os, re, sys, glob, json, subprocess, socket, threading, http.server, functools, tempfile
from fontTools.ttLib import TTFont
from fontTools import subset

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(ROOT, 'shared', 'accueil'); IDX = os.path.join(ROOT, 'index.html')
toujours = set(' 0123456789.,:;·–—-?!’\'"«»()')           # une marge : ponctuation et chiffres, pour qu'un petit changement de texte ne casse rien

def textes():
    """lance un petit serveur et le navigateur, rend {pile de polices|graisse|style: caractères}"""
    s = socket.socket(); s.bind(('127.0.0.1', 0)); port = s.getsockname()[1]; s.close()
    class Silence(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    h = functools.partial(Silence, directory=ROOT)
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', port), h); threading.Thread(target=srv.serve_forever, daemon=True).start()
    with tempfile.TemporaryDirectory() as td:
        f = os.path.join(td, 't.json')
        subprocess.run(['node', os.path.join(ROOT, 'outils', 'accueil-textes.js'), f, f'http://127.0.0.1:{port}/'], check=True)
        srv.shutdown(); return json.load(open(f))

def source(url):
    """le fichier complet derrière une url de l'accueil (complet ou déjà réduit)"""
    if url.startswith('shared/accueil/'):
        c = glob.glob(os.path.join(ROOT, '*', 'fonts', 'woff2', os.path.basename(url)))
        assert len(c) == 1, ('source introuvable', url, c); return os.path.relpath(c[0], ROOT)
    return url

def main():
    html = open(IDX).read(); T = textes(); os.makedirs(OUT, exist_ok=True)
    faces = re.findall(r'@font-face\{font-family:"([^"]+)";[^}]*?src:url\(([^)]+)\)', html)
    avant = apres = 0; fait = {}
    for fam, url in faces:
        src = source(url)
        chars = set(toujours)
        for k, v in T.items():
            pile = [x.strip().strip('"\'') for x in k.split('|')[0].split(',')]
            if fam in pile: chars |= set(v)
        chars |= {c.upper() for c in chars} | {c.lower() for c in chars}
        dst = os.path.join(OUT, os.path.basename(src))
        if dst not in fait:
            f = TTFont(os.path.join(ROOT, src)); n0 = os.path.getsize(os.path.join(ROOT, src))
            o = subset.Options(); o.layout_features = ['*']; o.name_IDs = ['*']; o.name_languages = ['*']; o.notdef_outline = True; o.glyph_names = True; o.flavor = 'woff2'; o.drop_tables = []
            s = subset.Subsetter(o); s.populate(unicodes=[ord(c) for c in chars]); s.subset(f)
            subset.save_font(f, dst, o); n1 = os.path.getsize(dst); fait[dst] = 1
            if n1 >= n0:                                      # rien à gagner : on garde le fichier complet
                os.remove(dst); n1 = n0; dst_url = src
            else: dst_url = os.path.relpath(dst, ROOT)
            avant += n0; apres += n1; fait[dst] = dst_url
            print(f'{n0/1e3:7.0f} Ko → {n1/1e3:6.0f} Ko  {len(chars):3d} car.  {src}')
        html = html.replace(f'src:url({url})', f'src:url({fait[dst]})')
    open(IDX, 'w').write(html)
    print(f'polices de l\'accueil : {avant/1e6:.2f} Mo → {apres/1e6:.2f} Mo')

if __name__ == '__main__': main()
