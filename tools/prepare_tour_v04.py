"""Package the v18 entry revision at actual native generated resolution, without upscaling."""
from pathlib import Path
import json,hashlib,struct
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'07_renders/vr-tour-v04';DEL=ROOT/'09_delivery/vr-tour-v04';DEL.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
c=json.loads((ROOT/'07_renders/vr-tour-v03/tour-config.json').read_text(encoding='utf-8'))
c.update(title='右鞋柜 · 左钢琴键换鞋区 · 四区360°',revision=18,presentationRevision=18,baseArchitectureRevision=14,geometry='02_geometry/geometry-master-v18.json',model='06_blender/home-main-v18.blend',modelSha256=sha(ROOT/'06_blender/home-main-v18.blend'),minimumPanoramaWidth=1536,renderSource='Verified v18 native4096x2048 full spherical anchors + built-in imagegen photographic concept treatment; no upscaling',imagegenPrompts='07_renders/vr-tour-v04/imagegen-prompts.json',geometricPrecision='Editable v18 model is authoritative for exact geometry; AI details, sunlight and exterior are conceptual',entryRevision=18)
records=[]
for scene in c['panoramas']:
    ident=scene['id'];src=OUT/(ident+'-ai-final.png');dest=OUT/(ident+'-day.jpg')
    if ident=='entry':scene.update(initialYawDeg=-90,initialPitchDeg=-12,initialFovDeg=95)
    with Image.open(src) as im:
        w,h=im.size;assert w==2*h and w>=1536;im.convert('RGB').save(dest,quality=96,subsampling=0,optimize=True)
    xml=f'<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"><rdf:Description rdf:about="" xmlns:GPano="http://ns.google.com/photos/1.0/panorama/" GPano:ProjectionType="equirectangular" GPano:UsePanoramaViewer="True" GPano:CroppedAreaImageWidthPixels="{w}" GPano:CroppedAreaImageHeightPixels="{h}" GPano:FullPanoWidthPixels="{w}" GPano:FullPanoHeightPixels="{h}" GPano:CroppedAreaLeftPixels="0" GPano:CroppedAreaTopPixels="0"/></rdf:RDF></x:xmpmeta>'
    payload=b'http://ns.adobe.com/xap/1.0/\0'+xml.encode();data=dest.read_bytes();dest.write_bytes(data[:2]+b'\xff\xe1'+struct.pack('>H',len(payload)+2)+payload+data[2:]);scene['image']=dest.relative_to(ROOT).as_posix()
    records.append(dict(id=ident,source=src.relative_to(ROOT).as_posix(),source_sha256=sha(src),image=scene['image'],sha256=sha(dest),resolution=[w,h],upscaled=False))
sizes={tuple(q['resolution']) for q in records};c['nativeImageResolutions']=[list(v) for v in sorted(sizes)];c['nativeImageResolution']=list(next(iter(sizes))) if len(sizes)==1 else None
(OUT/'tour-config.json').write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');(OUT/'export-manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
t=(ROOT/'09_delivery/vr-tour-v03/viewer.template.html').read_text(encoding='utf-8')
t=t.replace('沿用v14建筑及最新手动家具位置，以当前模型的完整球面图为基准，使用所选参考图细化摄影感与光影。原生图为1774×887，放大清晰度低于旧8K模型版；没有放大冒充高清。AI细节和窗外仅作设计示意，不代替模型或现场照片。','当前v18方案已改为进门右侧鞋柜、左侧钢琴键挂板与换鞋凳。全景以同版模型完整球面图为基准，按所选参考图细化摄影感与光影。下方显示实际原生尺寸，没有放大冒充高清；AI细节和窗外为设计示意，精确尺寸以模型和现场为准。')
(DEL/'viewer.template.html').write_text(t,encoding='utf-8')
print('V04_SPHERES_READY',len(records),c['nativeImageResolutions'])
