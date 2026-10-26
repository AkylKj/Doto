"""Build variable TTF, Regular TTF and WOFF2 from the edited UFO sources."""
from pathlib import Path
import subprocess
import sys
import os
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.otlLib.builder import buildStatTable

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault('SOURCE_DATE_EPOCH', '1792972800')
subprocess.run([sys.executable, str(ROOT/'scripts/add_cyrillic.py')], check=True)
out = ROOT/'fonts/cyrillic'
out.mkdir(parents=True, exist_ok=True)
variable = out/'DotoCyrillic[ROND,wght].ttf'
subprocess.run([sys.executable, '-m', 'fontmake', '-m', str(ROOT/'sources/Doto.designspace'),
                '-o', 'variable', '--output-path', str(variable)], check=True, cwd=ROOT)
font = TTFont(variable)
# Give this independent derivative an installation-safe family and PS name.
for n in font['name'].names:
    text = n.toUnicode()
    if 'Doto' in text and n.nameID in {1,3,4,6,16,21,25}:
        text = text.replace('Doto', 'DotoCyrillic' if n.nameID in {3,6,25} else 'Doto Cyrillic')
        n.string = text.encode(n.getEncoding())
buildStatTable(font, [
    dict(tag='ROND', name='Roundness', values=[dict(value=0,name='Square',flags=2),dict(value=100,name='Round')]),
    dict(tag='wght', name='Weight', values=[dict(value=w,name=n,flags=2 if w==400 else 0) for w,n in zip(range(100,901,100),['Thin','ExtraLight','Light','Regular','Medium','SemiBold','Bold','ExtraBold','Black'])])
])
font['head'].fontRevision = 1.001
font['name'].setName('Version 1.001',5,3,1,0x409)
font.save(variable)
regular = instantiateVariableFont(font, {'wght':400,'ROND':0}, inplace=False, updateFontNames=True)
regular.save(out/'DotoCyrillic-Regular.ttf')
for path in [variable,out/'DotoCyrillic-Regular.ttf']:
    f = TTFont(path)
    f.flavor = 'woff2'
    f.save(path.with_suffix('.woff2'))
print('Built four Cyrillic font files in fonts/cyrillic')
