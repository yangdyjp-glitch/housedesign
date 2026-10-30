"""Encode panoramas and bind the realistic tour to v14 layout / v15 presentation."""
from pathlib import Path
import json,hashlib,struct,sys,copy
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'07_renders/vr-tour-v02';draft='--draft' in sys.argv;ready='--ready-only' in sys.argv
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
config=json.loads((ROOT/'07_renders/vr-tour-v01/tour-config.json').read_text(encoding='utf-8'));config.update(title='现代日式 · 四区写实360°全景',revision=14,presentationRevision=15,geometry='02_geometry/geometry-master-v14.json',model='06_blender/home-v14-photoreal-v15.blend',modelSha256=sha(ROOT/'06_blender/home-v14-photoreal-v15.blend'),renderSource='Native Cycles PBR photoreal presentation, true equirectangular; v14 layout, v15 material and foliage detail',exterior='CC0 photographic HDRI used as illustrative scenery and natural light, not the actual site view',materialSources='08_assets/photoreal-v15/asset-manifest.json')
records=[]
for scene in config['panoramas']:
    ident=scene['id'];src=OUT/(ident+'-sphere'+('-draft' if draft else '')+'.png')
    if not src.exists():
        assert ready,src
        continue
    if src.stat().st_mtime < (ROOT/'06_blender/home-v14-photoreal-v15.blend').stat().st_mtime:
        assert ready,('Stale render from an earlier presentation trial',src)
        continue
    if draft:scene['image']=src.relative_to(ROOT).as_posix();continue
    dest=OUT/(ident+'-day.jpg')
    with Image.open(src) as im:
        assert im.size==(8192,4096);im.convert('RGB').save(dest,quality=94,subsampling=0,optimize=True)
    xml='<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"><rdf:Description rdf:about="" xmlns:GPano="http://ns.google.com/photos/1.0/panorama/" GPano:ProjectionType="equirectangular" GPano:UsePanoramaViewer="True" GPano:CroppedAreaImageWidthPixels="8192" GPano:CroppedAreaImageHeightPixels="4096" GPano:FullPanoWidthPixels="8192" GPano:FullPanoHeightPixels="4096" GPano:CroppedAreaLeftPixels="0" GPano:CroppedAreaTopPixels="0"/></rdf:RDF></x:xmpmeta>'
    payload=b'http://ns.adobe.com/xap/1.0/\0'+xml.encode();data=dest.read_bytes();dest.write_bytes(data[:2]+b'\xff\xe1'+struct.pack('>H',len(payload)+2)+payload+data[2:]);scene['image']=dest.relative_to(ROOT).as_posix()
    records.append(dict(id=ident,png=src.relative_to(ROOT).as_posix(),png_sha256=sha(src),jpg=scene['image'],jpg_sha256=sha(dest),width=8192,height=4096,jpeg_quality=94))
name='tour-config-draft.json' if draft else 'tour-config.json'
if draft or len(records)==4:(OUT/name).write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if len(records)==4:(OUT/'panorama-export-manifest.json').write_text(json.dumps(dict(presentation_revision=15,geometry_revision=14,images=records),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('V02_CONFIG_READY' if draft else 'V02_PANORAMAS_EXPORTED',len(records))
