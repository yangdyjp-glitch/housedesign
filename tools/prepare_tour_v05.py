from pathlib import Path
import json,hashlib,struct
from PIL import Image
R=Path(__file__).resolve().parents[1];O=R/'07_renders/vr-tour-v05';D=R/'09_delivery/vr-tour-v05';D.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
c=json.loads((R/'07_renders/vr-tour-v04/tour-config.json').read_text(encoding='utf8'));proof=json.loads((R/'logs/v19-metadata-confirmation.json').read_text(encoding='utf8'));assert proof['visual_fingerprint_before']==proof['visual_fingerprint_after']
c.update(title='现代日式 · 深木绿蓝 · 四区360°',revision=19,presentationRevision=19,geometry='02_geometry/geometry-master-v19.json',model='06_blender/home-main-v19.blend',modelSha256=sha(R/'06_blender/home-main-v19.blend'),renderSource='v19 same-layout native full spheres + built-in imagegen photographic concept, no upscaling; final native ceiling skin placement separately checked',imagegenPrompts='07_renders/vr-tour-v05/imagegen-prompts-actual.json',geometricPrecision='Main model defines geometry; generated material, light and exterior remain conceptual',entryRevision=18,renderSourceModel=proof['render_source_model'],renderSourceModelSha256=proof['render_source_model_sha256'],metadataConfirmation='logs/v19-metadata-confirmation.json',preRepairRenderVisualFingerprint=proof['visual_fingerprint_after'],ceilingRepair='logs/v19-ceiling-repair.json',finalNativeAnchors='logs/v19-final-panorama-anchors.json')
records=[]
for scene in c['panoramas']:
 ident=scene['id'];src=O/(ident+'-ai-final.png');dst=O/(ident+'-day.jpg')
 with Image.open(src) as im:
  w,h=im.size;assert w==h*2 and w>=1536;im.convert('RGB').save(dst,quality=96,subsampling=0,optimize=True)
 xml=f'<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"><rdf:Description rdf:about="" xmlns:GPano="http://ns.google.com/photos/1.0/panorama/" GPano:ProjectionType="equirectangular" GPano:UsePanoramaViewer="True" GPano:CroppedAreaImageWidthPixels="{w}" GPano:CroppedAreaImageHeightPixels="{h}" GPano:FullPanoWidthPixels="{w}" GPano:FullPanoHeightPixels="{h}" GPano:CroppedAreaLeftPixels="0" GPano:CroppedAreaTopPixels="0"/></rdf:RDF></x:xmpmeta>'
 payload=b'http://ns.adobe.com/xap/1.0/\0'+xml.encode();raw=dst.read_bytes();dst.write_bytes(raw[:2]+b'\xff\xe1'+struct.pack('>H',len(payload)+2)+payload+raw[2:]);scene['image']=dst.relative_to(R).as_posix()
 records.append(dict(id=ident,source=src.relative_to(R).as_posix(),source_sha256=sha(src),image=scene['image'],sha256=sha(dst),resolution=[w,h],upscaled=False))
sizes={tuple(v['resolution']) for v in records};c['nativeImageResolutions']=[list(v) for v in sizes];c['nativeImageResolution']=list(next(iter(sizes))) if len(sizes)==1 else None
(O/'tour-config.json').write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n',encoding='utf8');(O/'export-manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
t=(R/'09_delivery/vr-tour-v04/viewer.template.html').read_text(encoding='utf8');t=t.replace('当前v18方案已改为进门右侧鞋柜、左侧钢琴键挂板与换鞋凳。','当前方案采用暖白浅木、深木绿蓝，电视墙留白，书柜到顶，餐厅弧背四椅与柔光吊灯。家具保持现位。中央空调风口与检修尚处协调阶段，未作为确定设备画入全景。');(D/'viewer.template.html').write_text(t,encoding='utf8')
print('V05_TOUR_READY',len(records),c['nativeImageResolutions'])
