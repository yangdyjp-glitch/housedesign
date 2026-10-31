"""Package AI-assisted photographic full spheres honestly at their native resolution."""
from pathlib import Path
import json,hashlib,struct
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'07_renders/vr-tour-v03';DEL=ROOT/'09_delivery/vr-tour-v03';DEL.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
c=json.loads((ROOT/'07_renders/vr-tour-v02/tour-config.json').read_text(encoding='utf-8'))
c.update(title='参考图摄影感 · 四区360°全景',revision=16,presentationRevision=16,baseArchitectureRevision=14,geometry='02_geometry/presentation-layout-v16.json',model='06_blender/home-v16-reference-anchor.blend',modelSha256=sha(ROOT/'06_blender/home-v16-reference-anchor.blend'),minimumPanoramaWidth=1536,renderSource='Native verified 4096x2048 spherical layout anchors + built-in imagegen photographic light/texture enhancement; native generated resolution 1774x887, no upscale',reference='00_sources/photographic-style-reference-v16.png',imagegenPrompts='07_renders/vr-tour-v03/imagegen-final-prompts.json',nativeImageResolution=[1774,887],exterior='Illustrative distant treetops and skyline, not actual site photographs',geometricPrecision='Native anchors verified against the latest layout snapshot; generated photo details are conceptual and do not replace editable model geometry')
records=[]
for scene in c['panoramas']:
    ident=scene['id'];src=OUT/(ident+'-ai-final.png');dest=OUT/(ident+'-day.jpg')
    with Image.open(src) as im:
        w,h=im.size;assert w==h*2 and w>=1536;im.convert('RGB').save(dest,quality=96,subsampling=0,optimize=True)
    xml=f'<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"><rdf:Description rdf:about="" xmlns:GPano="http://ns.google.com/photos/1.0/panorama/" GPano:ProjectionType="equirectangular" GPano:UsePanoramaViewer="True" GPano:CroppedAreaImageWidthPixels="{w}" GPano:CroppedAreaImageHeightPixels="{h}" GPano:FullPanoWidthPixels="{w}" GPano:FullPanoHeightPixels="{h}" GPano:CroppedAreaLeftPixels="0" GPano:CroppedAreaTopPixels="0"/></rdf:RDF></x:xmpmeta>'
    payload=b'http://ns.adobe.com/xap/1.0/\0'+xml.encode();data=dest.read_bytes();dest.write_bytes(data[:2]+b'\xff\xe1'+struct.pack('>H',len(payload)+2)+payload+data[2:]);scene['image']=dest.relative_to(ROOT).as_posix()
    if ident=='living':scene.update(initialYawDeg=-50,initialPitchDeg=-10,initialFovDeg=70)
    records.append(dict(id=ident,source=src.relative_to(ROOT).as_posix(),source_sha256=sha(src),image=scene['image'],sha256=sha(dest),resolution=[w,h],upscaled=False))
(OUT/'tour-config.json').write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'export-manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
t=(ROOT/'09_delivery/vr-tour-v02/viewer.template.html').read_text(encoding='utf-8')
t=t.replace('现代日式 · 暖白浅木 · 写实全景','现代日式 · 摄影感光影全景').replace('写实方案渲染 · 窗外为环境示意','摄影感预览 · AI辅助表现 · 窗景示意')
t=t.replace('页面和图片全部在本机，无需联网。全景按最新v14布局制作，已细化纹理、软包和光影；窗外为示意环境，并非你家实际窗景。','页面和图片全部在本机，无需联网。沿用v14建筑及最新手动家具位置，以当前模型的完整球面图为基准，使用所选参考图细化摄影感与光影。原生图为1774×887，放大清晰度低于旧8K模型版；没有放大冒充高清。AI细节和窗外仅作设计示意，不代替模型或现场照片。')
t=t.replace("'· '+Math.round(image.naturalWidth/1024)+'K原图'","'· '+image.naturalWidth+' × '+image.naturalHeight")
(DEL/'viewer.template.html').write_text(t,encoding='utf-8')
print('V03_NATIVE_PHOTOGRAPHIC_SPHERES_READY',len(records),[1774,887])
