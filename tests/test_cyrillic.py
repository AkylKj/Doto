"""Coverage, interpolation, shaping and regression checks for Russian support."""
from pathlib import Path
import hashlib
import json
import importlib.util
import itertools
import unicodedata
import xml.etree.ElementTree as ET
import plistlib
import subprocess
import sys
import pytest
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.boundsPen import BoundsPen
import uharfbuzz as hb

ROOT = Path(__file__).resolve().parents[1]
# Independent explicit alphabet: do not import the implementation's coverage set.
ALPHABET = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя'
REQUIRED = set(map(ord, ALPHABET+'№₽'))
VAR = ROOT/'fonts/cyrillic/DotoCyrillic[ROND,wght].ttf'

def shape(path, text, variations=None):
    f = hb.Font(hb.Face(path.read_bytes()))
    if variations:
        f.set_variations(variations)
    b = hb.Buffer()
    b.add_str(text)
    b.guess_segment_properties()
    b.language = 'ru'
    hb.shape(f,b)
    return b.glyph_infos,b.glyph_positions

@pytest.mark.parametrize('path', sorted((ROOT/'fonts/cyrillic').glob('*')))
def test_binary_coverage_and_metrics(path):
    f = TTFont(path)
    cmap = f.getBestCmap()
    assert REQUIRED <= cmap.keys()
    assert f['name'].getDebugName(1).startswith('Doto Cyrillic')
    assert 'Open Font License' in f['name'].getDebugName(13)
    gs = f.getGlyphSet()
    for cp in REQUIRED:
        name = cmap[cp]
        pen = BoundsPen(gs)
        gs[name].draw(pen)
        assert pen.bounds is not None
        x0,y0,x1,y1 = pen.bounds
        assert -1 <= x0 < x1 <= 601
        assert -250 <= y0 < y1 <= 950
        assert f['hmtx'][name][0] == 600
    assert all(f['hmtx'][cmap[cp]][0] == 0 for cp in [0x300,0x301,0x306,0x308])

@pytest.mark.parametrize('weight,roundness', list(itertools.product([100,400,900],[0,67.5,100])))
def test_interpolation_and_shaping(weight,roundness):
    f = instantiateVariableFont(TTFont(VAR), {'wght':weight,'ROND':roundness}, inplace=False)
    gs = f.getGlyphSet()
    for cp in REQUIRED:
        name = f.getBestCmap()[cp]
        p = BoundsPen(gs)
        gs[name].draw(p)
        assert p.bounds and p.bounds[2] > p.bounds[0]
        assert f['hmtx'][name][0] == 600
    for text in [ALPHABET, 'Съешь ещё этих мягких французских булок, да выпей чаю. № 123 — 500 ₽',
                 unicodedata.normalize('NFD','ЁёЙй'), 'мо\u0301ре замо\u0301к ОБЪЕ\u0301КТ']:
        infos,positions = shape(VAR,text,{'wght':weight,'ROND':roundness})
        assert all(i.codepoint != 0 for i in infos)
        assert all(p.x_advance in [0,600] for p in positions)
    # A positioned accent over lowercase must move from its source y=750.
    infos,positions = shape(VAR,'я\u0301',{'wght':weight,'ROND':roundness})
    assert len(infos) == 2
    assert positions[1].x_advance == 0
    assert positions[1].y_offset == -100
    assert positions[1].x_offset == -600


def test_axes():
    f = TTFont(VAR)
    assert {a.axisTag:(a.minValue,a.maxValue) for a in f['fvar'].axes} == {'ROND':(0,100),'wght':(100,900)}
    assert len(f['fvar'].instances) == 9


def test_source_master_compatibility():
    signatures = []
    for ufo in sorted((ROOT/'sources').glob('*.ufo')):
        contents = plistlib.loads((ufo/'glyphs/contents.plist').read_bytes())
        sig = {}
        for cp in REQUIRED:
            name = f'uni{cp:04X}'
            root = ET.parse(ufo/'glyphs'/contents[name]).getroot()
            assert root.find('unicode').get('hex') == f'{cp:04X}'
            sig[name] = [[p.get('type') for p in c] for c in root.findall('outline/contour')]
        signatures.append(sig)
    assert len(signatures) == 4 and all(s == signatures[0] for s in signatures)


def test_generation_is_idempotent():
    def digest():
        return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                for p in (ROOT/'sources').rglob('*') if p.is_file()}
    before = digest()
    subprocess.run([sys.executable,str(ROOT/'scripts/add_cyrillic.py')],check=True)
    assert before == digest()


def test_original_latin_outlines():
    # Snapshot of upstream GLIF hashes, checked in independently of generated glyphs.
    manifest = (ROOT/'tests/upstream-outline-sha256.txt').read_text().splitlines()
    for line in manifest:
        digest,path = line.split('  ',1)
        assert hashlib.sha256(json.dumps([[p.attrib for p in c] for c in ET.parse(ROOT/path).getroot().findall('outline/contour')],sort_keys=True).encode()).hexdigest() == digest
