"""Bind verified sources and package v07. Never rewrite previous published revisions."""
from pathlib import Path
from itertools import combinations
from PIL import Image
import hashlib,json,shutil,zipfile
ROOT=Path(r'D:\AI-Yang.cn\HomeDesign')
GEOMETRY=ROOT/'02_geometry/geometry-master-v07.json';raw=GEOMETRY.read_bytes();d=json.loads(raw)
STYLE=ROOT/'05_style/modern-japanese-v03.json';style_raw=STYLE.read_bytes();style=json.loads(style_raw)
sha=hashlib.sha256(raw).hexdigest();assert style['geometry_sha256']==sha
readback=json.loads((ROOT/'logs/model-v07-readback.json').read_text(encoding='utf-8'))
widget=json.loads((ROOT/'logs/widget-v07-verification.json').read_text(encoding='utf-8'))
assert len(readback['furniture'])==21 and widget['dimensionTooltips']==21 and widget['canvasDrag100mm']
build=json.loads((ROOT/'logs/model-v07-build.json').read_text(encoding='utf-8'));assert build['geometry_sha256']==sha
live=json.loads((ROOT/'logs/v07-live-state.json').read_text(encoding='utf-8'));assert live[-1]['phase']=='activated' and live[-1]['live']['revision']==7
def overlaps(a,b):
    return all(a[k]<b[k]+b[s]-.01 and a[k]+a[s]>b[k]+.01 for k,s in [('x','w'),('z','d'),('y','h')])
fw=[(p['id'],w['id']) for p in d['furniture'] for w in d['walls'] if overlaps(p,w)]
ff=[(a['id'],b['id']) for a,b in combinations(d['furniture'],2) if a['parent']!=b['parent'] and overlaps(a,b)]
assert not fw and not ff,(fw,ff)
pngs=[]
for name in ['green-corner','balcony-laundry','desk-single-34','entry-cabinets-cutaway','overview-cutaway']:
    p=ROOT/'07_renders/v07-layout'/(name+'.png')
    with Image.open(p) as im:im.verify()
    with Image.open(p) as im:dimensions=im.size
    pngs.append(dict(path=p.relative_to(ROOT).as_posix(),size=list(dimensions),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),visually_reviewed=True))
shutil.copy2(GEOMETRY,ROOT/'02_geometry/geometry-master.json')
active=dict(revision=7,filename='home-main-v07.blend',geometry=GEOMETRY.relative_to(ROOT).as_posix(),geometry_sha256=sha,
    style=STYLE.relative_to(ROOT).as_posix(),style_sha256=hashlib.sha256(style_raw).hexdigest(),style_revision='modern-japanese-v03',
    previous_active_filename='home-v06-japanese-v02.blend',furniture_count=21,live_session_verified=True,
    previous_live_snapshot='home-v06-live-before-v07-20261030T225536404927.blend')
(ROOT/'06_blender/active-model.json').write_text(json.dumps(active,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
manifest=dict(revision=7,geometry_sha256=sha,style_sha256=active['style_sha256'],actual_render_mode='Blender Cycles 96 samples, OptiX',
    imagegen_used_this_revision=False,images=pngs,model='06_blender/home-main-v07.blend',
    furniture_count=21,parts=344,source_walls=60,glass=8,furniture_wall_aabb_intersections=fw,furniture_furniture_aabb_intersections=ff,
    real_world_accuracy='source model consistency only; dimensions and products provisional',
    render_review='04_reviews/v07审美与实用性.md',live_session='logs/v07-live-state.json',widget='logs/widget-v07-verification.json',
    live_operator_note='MCP safe mode forbids module reload/registration; used existing operator with both laundry devices selected, verified movement and restoration. Updated installed add-on tested separately in new background process supports automatic movement_group linking. No safe mode setting changed.')
(ROOT/'07_renders/v07-layout/render-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
files=[GEOMETRY,STYLE,ROOT/'06_blender/home-main-v07.blend',ROOT/'06_blender/active-model.json',ROOT/'09_delivery/v07修改说明.md',ROOT/'04_reviews/v07审美与实用性.md',
 ROOT/'03_layout/widget-layout-v07-initial.json',ROOT/'03_layout/blender-layout-latest.json',ROOT/'tools/home_design_move.py',
 ROOT/'logs/model-v07-build.json',ROOT/'logs/model-v07-readback.json',ROOT/'logs/widget-v07-verification.json',ROOT/'logs/v07-source-ledger.json',ROOT/'07_renders/v07-layout/render-manifest.json']
files += [ROOT/p['path'] for p in pngs]
target=ROOT/'09_delivery/v07-绿植入户洗烘与单屏办公.zip'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as archive:
    for p in files:archive.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(target) as archive:assert archive.testzip() is None;count=len(archive.namelist())
(ROOT/'logs/v07-delivery-verification.json').write_text(json.dumps(dict(zip=str(target),files=count,zip_valid=True,all_pngs_decoded=True,
    model_sha256=hashlib.sha256((ROOT/'06_blender/home-main-v07.blend').read_bytes()).hexdigest(),geometry_sha256=sha,
    active_model_matches=True,geometry_master_matches=raw==(ROOT/'02_geometry/geometry-master.json').read_bytes()),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('V07_DELIVERY_READY',count,sha)
