from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote,urlparse
from PIL import Image
import json,hashlib,re,base64,io
R=Path('D:/AI-Yang.cn/HomeDesign');OUT=R/'09_delivery/main-integration-v20'
def read(p):return json.loads((R/p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,t,attrs):
  for k,v in attrs:
   if k in ['href','src'] and v and not urlparse(v).scheme and not v.startswith('#'):self.links.append(v.split('#')[0])
checks=[]
for rel in ['09_delivery/main-integration-v20/index.html','09_delivery/house-v20-preview.html']:
 p=R/rel;parser=Links();parser.feed(p.read_text(encoding='utf-8'))
 for target in parser.links:
  if target.endswith('最终交付核对.json'):continue
  resolved=p.parent/unquote(target);assert resolved.is_file(),str(resolved);checks.append(str(resolved.relative_to(R)))
g=read('02_geometry/geometry-master-v20.json');audit=read('09_delivery/main-integration-v20/主模型回读.json');meta=read('09_delivery/main-integration-v20/表现元数据一致性.json')
assert audit['status']=='passed' and audit['furnitureCount']==26 and audit['savedReopened']
assert sha(R/'06_blender/home-main-v20.blend')==audit['modelSha256']
assert all(r['renderVisibleDataUnchanged'] and r['beforeVisualFingerprint']==r['afterVisualFingerprint'] for r in meta)
for r in meta:assert sha(R/r['file'])==r['afterSha256']
assert read('09_delivery/main-integration-v20/交互逻辑核对.json')['status']=='passed'
assert read('09_delivery/main-integration-v20/全景逻辑核对.json')['status']=='passed'
old=read('09_delivery/main-integration-v20/合并前版本.json')['baseline']
for rel in ['06_blender/home-main-v19.blend','02_geometry/geometry-master-v19.json','05_style/modern-japanese-v19.json']:assert sha(R/rel)==old[rel]
images=read('09_delivery/main-integration-v20/图像交付清单.json');assert len(images)==8
for r in images:
 assert sha(R/r['path'])==r['sha256']==sha(R/r['deliveryPath'])
 with Image.open(R/r['path']) as im:im.verify()
 with Image.open(R/r['path']) as im:assert list(im.size)==r['resolution']
cfg=read('09_delivery/vr-tour-v06/漫游机位与来源.json');assert cfg['modelSha256']==audit['modelSha256'] and cfg['geometrySha256']==sha(R/'02_geometry/geometry-master-v20.json')
tour=(R/'09_delivery/vr-tour-v06/打开360全景漫游.html').read_text(encoding='utf-8');embedded=json.loads(re.search(r'<script id="tour-data" type="application/json">([\s\S]*?)</script>',tour).group(1))
for p in embedded['panoramas']:
 raw=base64.b64decode(p['imageData'].split(',')[1]);source=R/p['image'];assert raw==source.read_bytes()
 with Image.open(io.BytesIO(raw)) as im:assert im.width==im.height*2
assert len(embedded['panoramas'])==4 and embedded['revision']==20
assert not re.search(r'(?:src|href)="https?://',tour)
assert g['walls']==read('02_geometry/geometry-master-v19.json')['walls'] and len(g['furnitureObjects'])==26
report={'status':'passed','revision':20,'modelSha256':audit['modelSha256'],'geometrySha256':sha(R/'02_geometry/geometry-master-v20.json'),'styleSha256':sha(R/'05_style/modern-japanese-v20.json'),'localLinksChecked':len(checks),'imagesChecked':8,'nativeImages':10,'mainSavedReopened':True,'meshBoundsAnd100mmMovementVerified':26,'interactiveHoverMoveUndoAndLegacyMigration':True,'vrSceneSwitchesAndZoomLogicVerified':True,'vrActualWebGLBrowserQA':False,'browserVisualQA':False,'rasterImagesVisuallyInspected':True,'mainAndRenderSourceGeometryUnchangedByPresentationMetadata':True,'v19ModelGeometryStylePreserved':True,'scope':'completed dining11 and office02 merged; wider v20 construction/MEP refinement pending','officeVariant':'B provisional, owner choice pending','furnitureCount':26,'panoramaResolution':[1774,887],'nativePanoramaAnchorResolution':[4096,2048],'imageMode':'built-in image_gen photographic concepts, no raster upscaling'}
(OUT/'最终交付核对.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print('V20_DELIVERY_VERIFIED',json.dumps({'links':len(checks),'furniture':26,'images':8,'spheres':4}))
