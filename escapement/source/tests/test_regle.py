# La règle du début de phrase, vérifiée avec HarfBuzz sur le vrai fichier (construit par build_all.py).
import os, glob
import pytest
import uharfbuzz as hb

FICHIER = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', 'fonts', 'otf', 'Escapement-Albula.otf'))


def ovs(texte, features=None):
    """Les lettres du texte qui sortent en version de début de phrase."""
    blob = hb.Blob.from_file_path(FICHIER); face = hb.Face(blob); font = hb.Font(face)
    buf = hb.Buffer(); buf.add_str(texte); buf.guess_segment_properties()
    hb.shape(font, buf, features or {})
    noms = [font.glyph_to_string(i.codepoint) for i in buf.glyph_infos]
    return ''.join(texte[i.cluster] for i, n in zip(buf.glyph_infos, noms) if n.endswith('.ovs'))


@pytest.mark.parametrize('texte,attendu', [
    ('Le matin.', 'L'),
    ('Il pleut. On reste.', 'IO'),
    ('Oui ! Non ? Peut-être… Jamais.', 'ONPJ'),
    ('« Bonjour », dit-il.', 'B'),
    ('Elle rit, M. Rossier regarde.', 'E'),
    ('Voir Mme. Dupont demain.', 'V'),
    ('C. F. Ramuz écrit.', 'C'),
    ('Am 1. August feiern wir.', 'A'),
    ('Das ist z. B. Bern. Dann gehen wir.', 'DD'),
    ('Mr. Smith is here. He waits.', 'MH'),
    ('UNESCO et ONU. Le reste.', 'L'),
    ('ZÜRICH ET BERNE', ''),
    ('À Genève. Ça va.', 'ÀÇ'),
    ('le McDonald de Jean-Pierre', ''),
    ('il dit : Oui.', ''),
])
def test_debut_de_phrase(texte, attendu):
    assert ovs(texte) == attendu


def test_ss01_tout_en_overshoot():
    assert ovs('Le Mans', {'ss01': True}) == 'LM'


def test_sans_calt():
    assert ovs('Le matin. On part.', {'calt': False}) == ''


def test_tnum():
    blob = hb.Blob.from_file_path(FICHIER); face = hb.Face(blob); font = hb.Font(face)
    buf = hb.Buffer(); buf.add_str('1290'); buf.guess_segment_properties()
    hb.shape(font, buf, {'tnum': True})
    assert all(font.glyph_to_string(i.codepoint).endswith('.tf') for i in buf.glyph_infos)
    assert len({p.x_advance for p in buf.glyph_positions}) == 1
