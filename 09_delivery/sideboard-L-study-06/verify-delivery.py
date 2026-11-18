from pathlib import Path
import json,hashlib,re,struct,zlib
ROOT=Path('D:/AI-Yang.cn/HomeDesign');OUT=ROOT/'09_delivery/sideboard-L-study-06'
base=json.loads((ROOT/'09_delivery/sideboard-L-study-04/design-parameters.json').read_text(encoding='utf-8'))['main_baseline_sha256']
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
after={k:digest(ROOT/k) for k in base};assert after==base
images=[]
for name in ['按批注L形餐岛-三人四人对照.png','L形餐岛-实体关系参考.png','L形餐岛-开关灯概念对照.png']:
    p=OUT/name;b=p.read_bytes();assert b[:8]==b'\x89PNG\r\n\x1a\n'
    w,h=struct.unpack('>II',b[16:24]);pos=8;chunks=[];done=False
    while pos<len(b):
        n=struct.unpack('>I',b[pos:pos+4])[0];kind=b[pos+4:pos+8];body=b[pos+8:pos+8+n]
        crc=struct.unpack('>I',b[pos+8+n:pos+12+n])[0];assert zlib.crc32(kind+body)&0xffffffff==crc
        if kind==b'IDAT':chunks.append(body)
        if kind==b'IEND':done=True
        pos+=12+n
    assert done and zlib.decompress(b''.join(chunks))
    images.append(dict(file=name,width=w,height=h,sha256=digest(p)))
html=(OUT/'按批注L形餐岛试排.html').read_text(encoding='utf-8')
links=[v for v in re.findall(r'(?:src|href)="([^"]+)"',html) if not v.startswith(('http','#'))]
assert all((OUT/p).exists() for p in links)
spec=json.loads((OUT/'L-layout-parameters.json').read_text(encoding='utf-8'))
readback=json.loads((OUT/'model-readback.json').read_text(encoding='utf-8'))
assert readback['chair_count']==4
manifest=json.loads((OUT/'generation-prompt.json').read_text(encoding='utf-8'))
manifest.update(state='generated and visually inspected; floor-only correction recorded separately',refinement='generation-refinement.json',final_output='L形餐岛-开关灯概念对照.png')
(OUT/'generation-prompt.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
report=dict(main_unchanged=True,main_sha256=after,images=images,local_links_valid=len(links),
            model_readback=readback,chair_mode_not_selected=True,
            user_question='Fourth chair permanent or occasional? Pending unless the owner answers; no deletion assumed.',
            audit='same assistant, geometric and aesthetic checks recorded separately',
            geometry_review='Actual saved L outline verified by bounds and positive/negative ray probes; four chairs and opaque doors verified.',
            aesthetic_review='Compound L, four stages, opaque fronts, four chairs, pale oak, dark middle and matching OFF/ON fixtures visually checked.',
            known_limitations=spec['limitations'],
            image_limitations=['AI details and proportions may drift; dimensioned plan is authoritative',
                               'Close concept image does not show full opposite cabinet or establish circulation clearance',
                               'Three seats used in comparison is a scenario, not accepted removal of fourth chair'])
(OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(main_unchanged=True,images=images,links_valid=len(links),four_chairs_preserved=True),ensure_ascii=False))
