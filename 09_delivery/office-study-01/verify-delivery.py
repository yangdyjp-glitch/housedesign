from pathlib import Path
import json, hashlib, xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit
from PIL import Image

ROOT=Path('D:/AI-Yang.cn/HomeDesign')
OUT=ROOT/'09_delivery/office-study-01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
review={
 'date':'2026-11-06','reviewMethod':'same native camera; manual visual checks on saved imagegen images, independent qualitative aesthetic and practical checks',
 'proposalOnly':True,'selectedOption':None,'recommendedByDesigner':'B','mainApplied':False,
 'aestheticBasis':['natural modern Japanese','warm white and pale oak with limited walnut/green/navy','open sofa-back work area and coherent raised L ledge'],
 'aestheticDimensions':{'colorHarmony':1,'contemporaryCharacter':1,'composition':1,'visualHierarchy':1,'visibleAccessibility':1,'visibleUsability':1},
 'aestheticScoring':'qualitative only; equal dimensions, no invented expert or objective score',
 'variants':[
  {'id':'A','firstImpression':'quiet, light, continuous pale wood','visibleEvidence':'slim pale-wood L, sage chair and navy props; long and short raised ledges share finish; artificial under-ledge glow absent in corrected OFF panel','tradeoff':'most pale wood; reduce warm-strip brightness to avoid overall yellow cast','correction':'removed remaining OFF short-return light glow and replaced technical title','remainingDrift':['low inner apron added by imagegen compared with open-support proxy','task-lamp lit state less explicit than B/C; use separate lighting circuit in design','AI background window and outdoor scenery are atmosphere only']},
  {'id':'B','firstImpression':'clear walnut outline, sage storage, layered warm light','visibleEvidence':'dark L at same proposed height, pale desktop and sage shallow end cabinet; one screen/one chair; extra mouse removed','tradeoff':'strongest visible boundary, avoid extending dark veneer into a full rear wall','correction':'removed duplicated mouse and added Chinese title','remainingDrift':['right ON label was dropped during correction; board and page explicitly define left OFF/right ON','imagegen adds low inner apron and stylises supports/cabinet division','AI balcony-window segmentation and scenery not measured']},
  {'id':'C','firstImpression':'soft ivory ribbon, restrained navy accent','visibleEvidence':'broad rounded ivory ends, lower oak desktop, navy near-end drawer; lamp and L lights clearly OFF/ON','tradeoff':'more finish interfaces; detail ivory/oak joint and service access','correction':'replaced technical title with Chinese title','remainingDrift':['ivory return visually blends with sunlit surroundings; height verified only in native model','drawer appearance and support form simplified by imagegen','AI window/outdoor context not authoritative']}
 ],
 'practicalReview':{'geometryVersion':19,'deskMm':[2400,700,750],'longLedgeMm':[2600,200,950],'shortLedgeMm':[900,200,950],'bothLedgeTopHeightsMm':950,'deskAndLedgeDifferenceMm':200,'monitorCount':1,'monitorInches':34,'chairCount':1,'chairRearFurnitureGapMm':408,'deskEdgeToBookcaseMm':838,'sofaToLedgeMm':100,'chairGapResult':'tight, not accepted as occupied circulation width','unchangedExistingPlacements':['sofa-modular','double-desk','office-chair-1','bookcase'],'remainingChecks':['selected chair pullback and bookcase doors','actual finish samples','raised-ledge support/frame connection','cleaning access in 100mm sofa gap','lamp glare at seated monitor position and measured workplane illuminance']},
 'imageAuthority':'concept appearance only; exact footprint/heights come from parameter SVG and saved native models','browserVisualQA':'not performed; offline link/XML checks only',
 'webReferences':[{'title':'OSHA workstation environment','url':'https://www.osha.gov/etools/computer-workstations/workstation-environment','usedFor':'diffuse lighting, glare control and balancing screen/background brightness'}, {'title':'OSHA monitors','url':'https://www.osha.gov/etools/computer-workstations/components/monitors','usedFor':'viewing distance and adjusting monitor top height; not local construction certification'}]
}
(OUT/'审查与图像差异.json').write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf-8')

prompts={'tool':'built-in image_gen.imagegen','mode':'sketch-to-render followed by one focused correction per variant','variants':[]}
images=[]
for vid in ['A','B','C']:
 folder=OUT/vid
 for filename in [f'{vid}-OFF-native.png',f'{vid}-ON-native.png',f'{vid}-开关灯对照.png']:
  path=folder/filename
  with Image.open(path) as im:
   entry={'path':str(path),'format':im.format,'size':list(im.size),'bytes':path.stat().st_size,'sha256':sha(path)};im.verify()
  images.append(entry)
 base=json.loads((folder/'generation-prompt.json').read_text(encoding='utf-8'))
 correction=json.loads((folder/'correction-prompt.json').read_text(encoding='utf-8'))
 base['submittedReferences']=[str(folder/f'{vid}-OFF-native.png'),str(folder/f'{vid}-ON-native.png'),'C:/Users/ADMINI~1/AppData/Local/Temp/codex-clipboard-903a779d-f9b1-4aa2-a34a-106b6b5a6b1e.png','C:/Users/ADMINI~1/AppData/Local/Temp/codex-clipboard-b78b33d0-75bd-4fb7-96a9-2700c111291e.png']
 base['archivedOwnerReferences']=[str(OUT/'references/办公高台参考.png'),str(OUT/'references/位置批注.png')]
 (folder/'generation-prompt.json').write_text(json.dumps(base,ensure_ascii=False,indent=2),encoding='utf-8')
 prompts['variants'].append({'id':vid,'generation':base,'correction':correction,'finalImage':str(folder/f'{vid}-开关灯对照.png')})
 (folder/'camera-and-source.json').write_text(json.dumps({'cameraPositionM':[6.6,-5.9,2.7],'targetM':[5.3,-2.9,.8],'lensMm':37,'nativeImageSizePx':[1600,1300],'axis':'main (x,z,height) mm -> Blender (x,-z,height) m /1000','source':str(ROOT/'02_geometry/geometry-master-v19.json'),'sourceSha256':sha(ROOT/'02_geometry/geometry-master-v19.json'),'blendSha256':sha(folder/f'办公区-{vid}-独立提案.blend'),'sourceOwnerReferenceHashes':{p.name:sha(p) for p in (OUT/'references').iterdir()}},ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'出图提示词.json').write_text(json.dumps(prompts,ensure_ascii=False,indent=2),encoding='utf-8')

ET.parse(OUT/'办公区尺寸与高台关系.svg')
class Links(HTMLParser):
 def __init__(self):super().__init__();self.targets=[]
 def handle_starttag(self,tag,attrs):
  for key,value in attrs:
   if key in ['src','href']:self.targets.append(value)
page=OUT/'办公区三套独立方案.html'
parser=Links();parser.feed(page.read_text(encoding='utf-8'))
missing=[]
for t in parser.targets:
 u=urlsplit(t)
 if u.scheme or not u.path:continue
 if not (OUT/unquote(u.path)).is_file():missing.append(t)
assert not missing,missing
native=json.loads((OUT/'核对记录.json').read_text(encoding='utf-8'))
assert native['mainUnchanged']
assert len(native['savedReopenedModels'])==3
final={'images':images,'savedImagesVisuallyInspected':True,'imageViewCounts':{'conceptBoards':3,'conceptViews':6,'nativeReferences':6},'localLinksChecked':len(parser.targets),'missingLinks':missing,'svgXmlValid':True,'nativeModelReadbackPassed':True,'mainUnchangedAtNativeVerification':True,'browserVisualQA':False}
(OUT/'交付检查.json').write_text(json.dumps(final,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'conceptBoards':3,'conceptViews':6,'nativeReferences':6,'localLinksChecked':len(parser.targets),'missingLinks':missing,'mainUnchanged':True,'imageSizes':[x['size'] for x in images if '对照' in x['path']]},ensure_ascii=False))
