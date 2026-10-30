"""Publish native-rendered panoramas as high-quality, Photo Sphere tagged JPEG files."""
from pathlib import Path
import json,hashlib,struct,sys
from PIL import Image
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'07_renders/vr-tour-v01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
records=[]
for ident in ['living','dining','balcony','entry']:
    src=OUT/(ident+'-day.png');dest=OUT/(ident+'-day.jpg')
    if not src.exists():
        assert '--ready-only' in sys.argv,src
        continue
    with Image.open(src) as im:im.verify()
    with Image.open(src) as im:
        assert im.size==(8192,4096);im.convert('RGB').save(dest,quality=92,subsampling=0,optimize=True)
    xml='''<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"><rdf:Description rdf:about="" xmlns:GPano="http://ns.google.com/photos/1.0/panorama/" GPano:ProjectionType="equirectangular" GPano:UsePanoramaViewer="True" GPano:CroppedAreaImageWidthPixels="8192" GPano:CroppedAreaImageHeightPixels="4096" GPano:FullPanoWidthPixels="8192" GPano:FullPanoHeightPixels="4096" GPano:CroppedAreaLeftPixels="0" GPano:CroppedAreaTopPixels="0"/></rdf:RDF></x:xmpmeta>'''
    ET.fromstring(xml);payload=b'http://ns.adobe.com/xap/1.0/\x00'+xml.encode('utf-8');jpeg=dest.read_bytes();assert jpeg[:2]==b'\xff\xd8';dest.write_bytes(jpeg[:2]+b'\xff\xe1'+struct.pack('>H',len(payload)+2)+payload+jpeg[2:])
    with Image.open(dest) as im:
        assert im.size==(8192,4096);assert any('ProjectionType' in str(data) for marker,data in im.applist if marker=='APP1');im.verify()
    records.append(dict(id=ident,native_png=src.relative_to(ROOT).as_posix(),native_png_sha256=sha(src),viewer_jpeg=dest.relative_to(ROOT).as_posix(),viewer_jpeg_sha256=sha(dest),pixels=[8192,4096],jpeg_quality=92,chroma_subsampling='4:4:4',bytes=dest.stat().st_size,gpano='equirectangular, full 360x180',geographic_heading_invented=False))
if len(records)==4:
    report=dict(revision=13,source='Blender Cycles native spherical renders; JPEG encoding only; no AI repaint or geometry warp',projection='monoscopic equirectangular',metadata_reference='https://developers.google.com/streetview/spherical-metadata',images=records)
    (OUT/'panorama-export-manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(exported=[r['id'] for r in records],bytes=[r['bytes'] for r in records]),ensure_ascii=False))
