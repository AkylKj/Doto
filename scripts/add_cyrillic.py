"""Generate Russian glyphs in all four UFO masters. Licensed under OFL-1.1."""
from pathlib import Path
import copy
import plistlib
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
# Each row is one 100-unit grid step. Five columns leave a full cell sidebearing.
# Existing Latin lookalikes reuse their original outlines exactly.
ALIASES = dict(zip('АВЕКМНОРСТХавекорсух',
                   ['A','B','E','K','M','H','O','P','C','T','X','a','B','e','k','o','p','c','y','x']))
# Cyrillic в is deliberately drawn below, not a Latin small b.
ALIASES.pop('в')
ALIASES.pop('к')
UPPER = {
'Б':'11111/10000/10000/11110/10001/10001/11110',
'Г':'11111/10000/10000/10000/10000/10000/10000',
'Д':'00110/01010/01010/01010/01010/10010/11111/10001',
'Ж':'10101/10101/01110/00100/01110/10101/10101',
'З':'01110/10001/00001/00110/00001/10001/01110',
'И':'10001/10001/10011/10101/11001/10001/10001',
'Л':'00111/01001/01001/01001/01001/01001/10001',
'П':'11111/10001/10001/10001/10001/10001/10001',
'У':'10001/10001/10001/01111/00001/10001/01110',
'Ф':'00100/01110/10101/10101/10101/01110/00100',
'Ц':'10001/10001/10001/10001/10001/10001/11111/00001',
'Ч':'10001/10001/10001/01111/00001/00001/00001',
'Ш':'10101/10101/10101/10101/10101/10101/11111',
'Щ':'10101/10101/10101/10101/10101/10101/11111/00001',
'Ъ':'11000/01000/01000/01110/01001/01001/01110',
'Ы':'10001/10001/10001/11101/10011/10011/11101',
'Ь':'10000/10000/10000/11110/10001/10001/11110',
'Э':'01110/10001/00001/00111/00001/10001/01110',
'Ю':'10010/10101/10101/11101/10101/10101/10010',
'Я':'01111/10001/10001/01111/00101/01001/10001',
'№':'100010/110101/101010/100000/100111/100000/100000',
'₽':'01110/01001/01001/01110/11100/01000/01000',
}
LOWER = {
'к':'10001/10010/11100/10010/10001',
'б':'00111/01000/11110/10001/10001/10001/01110',
'в':'11110/10001/11110/10001/11110',
'г':'11110/10000/10000/10000/10000',
'д':'00110/01010/01010/10010/11111/10001',
'ж':'10101/01110/00100/01110/10101',
'з':'11110/00001/00110/00001/11110',
'и':'10001/10011/10101/11001/10001',
'л':'00111/01001/01001/01001/10001',
'м':'10001/11011/10101/10001/10001',
'н':'10001/10001/11111/10001/10001',
'п':'11111/10001/10001/10001/10001',
'т':'11111/00100/00100/00100/00100',
'ф':'00100/01110/10101/10101/01110/00100/00100',
'ц':'10001/10001/10001/10001/11111/00001',
'ч':'10001/10001/01111/00001/00001',
'ш':'10101/10101/10101/10101/11111',
'щ':'10101/10101/10101/10101/11111/00001',
'ъ':'11000/01000/01110/01001/01110',
'ы':'10001/10001/11101/10011/11101',
'ь':'10000/10000/11110/10001/11110',
'э':'01110/10001/00111/10001/01110',
'ю':'10010/10101/11101/10101/10010',
'я':'01111/10001/01111/01001/10001',
}
REQUIRED = set(range(0x410, 0x450)) | {0x401, 0x451, 0x2116, 0x20BD}

def glyph_name(ch):
    return f'uni{ord(ch):04X}'

def grid(pattern, top):
    return [(50 + x * 100, top - y * 100)
            for y, row in enumerate(pattern.split('/'))
            for x, bit in enumerate(row) if bit == '1']

def generate():
    for ufo in sorted((ROOT / 'sources').glob('*.ufo')):
        glyphdir = ufo / 'glyphs'
        contents = plistlib.loads((glyphdir / 'contents.plist').read_bytes())
        original = {name: ET.parse(glyphdir / filename).getroot()
                    for name, filename in contents.items()}
        template = original['A'].find('outline/contour')
        xs = [float(p.get('x')) for p in template]
        ys = [float(p.get('y')) for p in template]
        cx, cy = (min(xs)+max(xs))/2, (min(ys)+max(ys))/2
        generated = {}
        for cp in sorted(REQUIRED):
            ch = chr(cp)
            base = {'Ё':'Е','ё':'е','Й':'И','й':'и'}.get(ch, ch)
            if base in ALIASES:
                g = copy.deepcopy(original[ALIASES[base]])
                for node in list(g.findall('unicode')) + list(g.findall('anchor')):
                    g.remove(node)
                for node in g.findall('lib'):
                    g.remove(node)
            else:
                g = ET.Element('glyph', name=glyph_name(ch), format='2')
                ET.SubElement(g, 'advance', width='600')
                outline = ET.SubElement(g, 'outline')
                if base in UPPER:
                    coords = grid(UPPER[base], 650)
                else:
                    coords = grid(LOWER[base], 650 if base == 'б' else 450)
                for x, y in coords:
                    contour = copy.deepcopy(template)
                    for p in contour:
                        p.set('x', str(int(float(p.get('x')) + x-cx)))
                        p.set('y', str(int(float(p.get('y')) + y-cy)))
                    outline.append(contour)
            g.set('name', glyph_name(ch))
            ET.SubElement(g, 'unicode', hex=f'{cp:04X}')
            if ch in 'ЁёЙй':
                top = 850 if ch.isupper() else 650
                accents = [(150,top),(350,top)] if ch in 'Ёё' else [(150,top),(250,top-100),(350,top)]
                for x,y in accents:
                    contour = copy.deepcopy(template)
                    for p in contour:
                        p.set('x', str(int(float(p.get('x')) + x-cx)))
                        p.set('y', str(int(float(p.get('y')) + y-cy)))
                    g.find('outline').append(contour)
            # Explicit positioning for stressed Russian text; marks stay zero width.
            anchor_y = 950 if ch in 'ЁЙ' else 850 if ch.isupper() else 750 if ch in 'ёйб' else 650
            ET.SubElement(g, 'anchor', name='top', x='250', y=str(anchor_y))
            filename = glyph_name(ch) + '.glif'
            ET.indent(g, space='  ')
            (glyphdir / filename).write_bytes(ET.tostring(g, encoding='UTF-8', xml_declaration=True)+b'\n')
            contents[glyph_name(ch)] = filename
            generated[ch] = g
        (glyphdir / 'contents.plist').write_bytes(plistlib.dumps(contents, sort_keys=False))
        # Preserve original Latin features, but classify combining marks correctly.
        feature = (ufo / 'features.fea').read_text().split('# BEGIN RUSSIAN')[0]
        feature = feature.replace('languagesystem latn dflt;', 'languagesystem latn dflt;\nlanguagesystem cyrl dflt;\nlanguagesystem cyrl RUS;') if 'languagesystem cyrl' not in feature else feature
        marks = ['gravecomb','acutecomb','uni0306','uni0308']
        for mark in marks:
            g = original[mark]
            g.find('advance').set('width','0')
            ET.indent(g, space='  ')
            (glyphdir / contents[mark]).write_bytes(ET.tostring(g,encoding='UTF-8',xml_declaration=True)+b'\n')
        import re
        for mark in marks:
            feature = re.sub(r'\\'+mark+r'\b', '', feature)
        feature = re.sub(r'table GDEF \{.*?\} GDEF;', 'table GDEF {\n  GlyphClassDef @GDEF_Simple, , ['+' '.join(marks)+'], ;\n} GDEF;', feature, flags=re.S)
        # Explicit mark rules avoid relying on editor-specific automatic features.
        feature = '\n'.join(line.rstrip() for line in feature.splitlines()).rstrip()
        feature += '\n\n# BEGIN RUSSIAN\n'
        for mark in marks:
            feature += f'markClass {mark} <anchor 250 750> @RU_TOP;\n'
        feature += 'feature mark {\n'
        for ch, g in generated.items():
            a = g.find('anchor')
            feature += f'  pos base {glyph_name(ch)} <anchor 250 {a.get("y")}> mark @RU_TOP;\n'
        feature += '} mark;\n'
        (ufo / 'features.fea').write_text(feature)
        # Generated glyph order must be identical in each master.
        lib_path = ufo / 'lib.plist'
        lib = plistlib.loads(lib_path.read_bytes())
        order = lib.get('public.glyphOrder', list(original))
        lib['public.glyphOrder'] = [n for n in order if n not in {glyph_name(chr(c)) for c in REQUIRED}] + [glyph_name(chr(c)) for c in sorted(REQUIRED)]
        lib_path.write_bytes(plistlib.dumps(lib, sort_keys=False))
    print(f'Generated {len(REQUIRED)} glyphs in four UFO masters.')

if __name__ == '__main__':
    generate()
