from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import hashlib, json, struct, xml.etree.ElementTree as ET, zipfile, zlib

OUT=Path(__file__).parent
ROOT=OUT.parent.parent
baseline={
 '06_blender/home-main-v19.blend':'04f55222258c1a866e84b9eff3b7987e48f399ca520789ba458b3fa16d4dc214',
 '06_blender/active-model.json':'52766c728b10a878baddff725d50a81dd796543efd14c877b7c70601d2a6342f',
 '02_geometry/geometry-master-v19.json':'44d4cd19f7a90b9c1bf24f958a50f66db46bffba5e0ddfe147cc49543ae7aa9d',
 '05_style/modern-japanese-v19.json':'387f6be47a1aeaf64a0e58d178fe5507c9ab5cf9cf26c19f7dfaa4b16b092b4c',
 '06_blender/active-presentation.json':'4f967c49e33cb02e893de5344a452258fe34c14354ae9ec4582004c8ca684e97',
}
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
after={k:digest(ROOT/k) for k in baseline}
assert after==baseline, 'Main baseline unexpectedly changed'
images=[]
for k in 'ABC':
    p=OUT/f'{k}-开关灯对照.png'
    data=p.read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n'
    w,h,depth,colour,comp,filt,interlace=struct.unpack('>IIBBBBB',data[16:29])
    cursor=8;compressed=[];ended=False
    while cursor<len(data):
        n=struct.unpack('>I',data[cursor:cursor+4])[0]
        kind=data[cursor+4:cursor+8];body=data[cursor+8:cursor+8+n]
        crc=struct.unpack('>I',data[cursor+8+n:cursor+12+n])[0]
        assert zlib.crc32(kind+body)&0xffffffff==crc
        if kind==b'IDAT':compressed.append(body)
        if kind==b'IEND':ended=True
        cursor+=12+n
    raw=zlib.decompress(b''.join(compressed))
    assert ended and raw and w>0 and h>0
    if interlace==0:
        channels={0:1,2:3,3:1,4:2,6:4}[colour]
        assert len(raw)==h*(1+(w*channels*depth+7)//8)
    images.append(dict(scheme=k,file=p.name,width=w,height=h,sha256=digest(p),native_size=True))
assert len({i['sha256'] for i in images})==3
svgs=list(OUT.glob('*.svg'))
for p in svgs: ET.parse(p)
class Links(HTMLParser):
    def __init__(self): super().__init__();self.local=[]
    def handle_starttag(self,tag,attrs):
        for key,value in attrs:
            if key not in ('src','href') or not value or value.startswith('#'):continue
            if urlsplit(value).scheme:continue
            self.local.append(unquote(value.split('#')[0]))
html=OUT/'四段式餐边柜三套修订.html'
parser=Links();parser.feed(html.read_text(encoding='utf-8'))
missing=[v for v in parser.local if not (OUT/v).exists()]
assert not missing, missing
references=[]
for p in (OUT/'references').glob('*.jpg'):
    source=OUT.parent/'sideboard-study-01/references'/p.name
    assert digest(p)==digest(source)
    references.append(dict(file='references/'+p.name,sha256=digest(p),unchanged=True))
assert len(references)==3
manifest=json.loads((OUT/'generation-prompts.json').read_text(encoding='utf-8'))
for k in 'ABC':
    manifest['variants'][k]['status']='generated and visually reviewed; standalone concept, not main implementation'
    manifest['variants'][k]['refinement_record']='generation-refinements.json' if k in 'BC' else None
(OUT/'generation-prompts.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
spec=json.loads((OUT/'design-parameters.json').read_text(encoding='utf-8'))
spec['images']=images;spec['main_baseline_sha256']=after
(OUT/'design-parameters.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2),encoding='utf-8')
report=dict(date='2026-11-05',scope='three standalone candidates, no accepted variant, no v20',
            master_unchanged=True,main_sha256=after,images=images,owner_references=references,
            svg_xml_valid=[p.name for p in svgs],html_local_links=len(parser.local),missing_local_links=missing,
            browser_preview='not used; local-file browser navigation was policy-disallowed; offline inspection only',
            visual_review={'reviewer':'same assistant, no independent expert claim',
                'four_stages_and_slim_flap_band':'visible in all three final boards',
                'glass_display_and_three_horizontal_drawers':'visible in all three final boards',
                'fridge_outside_L_at_left_and_four_chairs':'visible in all three final boards',
                'OFF_ON':'physical fixtures retained; B missing unlit pendant corrected; only lighting changes intended',
                'C_fridge_service_face':'full-height ventilation face corrected; not claimed validated installation',
                'limitations':['AI proportions and door seams can drift; use dimensions for design intent',
                               'A side daylight environment does not establish actual new window',
                               'Upper pull-down and flap travel unverified until hardware is selected',
                               'Fridge ventilation/opening unverified until actual model selected',
                               'Kitchen-end chair pull-out leaves about522.5mm; still tight']})
(OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
files=[p for p in OUT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.py','.blend1')]
package=OUT.parent/'四段式餐边柜与L餐岛-三套独立修订04.zip'
assert not package.exists(),'Versioned package already exists; do not overwrite silently'
with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
    for p in files:z.write(p,p.relative_to(OUT))
with zipfile.ZipFile(package) as z:assert z.testzip() is None
print(json.dumps(dict(images=images,main_unchanged=True,local_links_valid=True,zip_files=len(files),package=str(package)),ensure_ascii=False))
