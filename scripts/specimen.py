"""Render every Russian letter using the built font, without system fallback."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
import tempfile
ROOT = Path(__file__).resolve().parents[1]
image = Image.new('RGB',(1560,2500),'#f5f3ed')
d = ImageDraw.Draw(image)
label = ImageFont.load_default(size=24)
rows = ['АБВГДЕЁЖЗИЙКЛМНОП', 'РСТУФХЦЧШЩЪЫЬЭЮЯ',
        'абвгдеёжзийклмноп', 'рстуфхцчшщъыьэюя',
        'Съешь ещё этих мягких булок.', '№ 123 — 500 ₽   мо́ре  Ёё Йй']
for panel,(weight,roundness) in enumerate([(100,0),(400,100),(900,0),(900,100)]):
    y=panel*620+20
    d.text((32,y),f'DOTO CYRILLIC   wght={weight} / ROND={roundness}',font=label,fill='#bc292c')
    f=instantiateVariableFont(TTFont(ROOT/'fonts/cyrillic/DotoCyrillic[ROND,wght].ttf'),{'wght':weight,'ROND':roundness},inplace=False)
    with tempfile.NamedTemporaryFile(suffix='.ttf') as tmp:
        f.save(tmp.name)
        font=ImageFont.truetype(tmp.name,72)
        for i,text in enumerate(rows):
            d.text((32,y+110+i*85),text,font=font,fill='#202020',anchor='ls',language='ru')
image.save(ROOT/'documentation/samples/cyrillic.png')
