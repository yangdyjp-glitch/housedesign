from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote,urlparse
import xml.etree.ElementTree as ET
import hashlib,json
from PIL import Image

ROOT=Path('D:/AI-Yang.cn/HomeDesign');OUT=ROOT/'09_delivery/office-study-02'
class Links(HTMLParser):
 def __init__(self):super().__init__();self.targets=[]
 def handle_starttag(self,tag,attrs):
  for k,v in attrs:
   if k in ['src','href']:self.targets.append(v)

page=OUT/'办公区半墙与敞开端-三套修正版.html'
h=Links();h.feed(page.read_text(encoding='utf-8'))
links=[]
for target in h.targets:
 if urlparse(target).scheme or target.startswith('#'):continue
 p=page.parent/unquote(target.split('#')[0])
 links.append({'target':target,'exists':p.is_file()})
assert all(r['exists'] for r in links),[r for r in links if not r['exists']]
ET.parse(OUT/'半墙与阳台入口尺寸.svg')
images=[]
for p in OUT.glob('*/*.png'):
 with Image.open(p) as im:im.verify()
 with Image.open(p) as im:
  images.append({'path':str(p.relative_to(OUT)),'format':im.format,'pixels':list(im.size),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
for v in ['A','B','C']:
 path=OUT/v/f'{v}-半墙修正-开关灯对照.png'
 assert path.is_file() and any(r['path'].replace('\\','/')==f'{v}/{path.name}' for r in images)
 blend=OUT/v/f'办公区-{v}-近端半墙远端敞开-独立02.blend'
 assert blend.read_bytes()[:7]==b'BLENDER'
for path in OUT.rglob('*.json'):json.loads(path.read_text(encoding='utf-8-sig'))
p=json.loads((OUT/'设计参数.json').read_text(encoding='utf-8'))
after={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in p['baselineHashes']}
assert after==p['baselineHashes']
readback=json.loads((OUT/'模型回读.json').read_text(encoding='utf-8'))
assert len(readback['records'])==3 and readback['mainUnchanged']
meta=json.loads((OUT/'元数据回读.json').read_text(encoding='utf-8'))
assert len(meta)==3 and all(r['parametersReopenedMatch'] for r in meta)
for r in meta:assert hashlib.sha256(Path(r['path']).read_bytes()).hexdigest()==r['sha256']
result={'status':'passed','localLinks':links,'images':images,'nativeModelsSavedReopened':3,'nearHalfwallCap':[1735,200,950],'solidBodyThickness':120,'farReturns':0,'farEndCabinets':0,'ownerConfirmedEndpoint':'right bookcase, entry from balcony','mainBefore':p['baselineHashes'],'mainAfter':after,'mainUnchanged':True,'browserVisualQA':'not performed; offline link check, XML parse and raster visual inspection only','imageMode':'built-in image_gen; photographic concepts, not metric evidence'}
(OUT/'交付检查.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'status':'passed','links':len(links),'rasters':len(images),'models':3,'mainUnchanged':True},ensure_ascii=False))
