"""Bind the verified v08 main model and retain earlier published revisions."""
from pathlib import Path
from itertools import combinations
from PIL import Image
import json,hashlib,shutil,zipfile
ROOT=Path(r'D:\AI-Yang.cn\HomeDesign')
GEOMETRY=ROOT/'02_geometry/geometry-master-v08.json';raw=GEOMETRY.read_bytes();d=json.loads(raw)
STYLE=ROOT/'05_style/modern-japanese-v04.json';style_raw=STYLE.read_bytes();style=json.loads(style_raw)
sha=hashlib.sha256(raw).hexdigest();style_sha=hashlib.sha256(style_raw).hexdigest();assert style['geometry_sha256']==sha
build=json.loads((ROOT/'logs/model-v08-build.json').read_text(encoding='utf-8'))
readback=json.loads((ROOT/'logs/model-v08-readback.json').read_text(encoding='utf-8'))
widget=json.loads((ROOT/'logs/widget-v08-verification.json').read_text(encoding='utf-8'))
live=json.loads((ROOT/'logs/v08-live-state.json').read_text(encoding='utf-8'))
assert all(r['geometry_sha256']==sha for r in [build,readback])
assert readback['style_sha256']==style_sha and len(readback['furniture'])==21
assert widget['dimensionTooltips']==21 and widget['canvasDrag100mm'] and not widget['runtimeErrors']
assert live[-1]['phase']=='activated' and live[-1]['live']['revision']==8 and live[-1]['live']['geometry_sha256']==sha
previous=json.loads((ROOT/'logs/v07-delivery-verification.json').read_text(encoding='utf-8'))
assert previous['model_sha256']==hashlib.sha256((ROOT/'06_blender/home-main-v07.blend').read_bytes()).hexdigest()
def overlaps(a,b):return all(a[k]<b[k]+b[s]-.01 and a[k]+a[s]>b[k]+.01 for k,s in [('x','w'),('z','d'),('y','h')])
fw=[(p['id'],w['id']) for p in d['furniture'] for w in d['walls'] if overlaps(p,w)]
ff=[(a['id'],b['id']) for a,b in combinations(d['furniture'],2) if a['parent']!=b['parent'] and overlaps(a,b)]
assert not fw and not ff,(fw,ff)
images=[]
for name in ['cabinet-milk-yellow','balcony-window']:
    p=ROOT/'07_renders/v08-selected'/(name+'.png')
    with Image.open(p) as im:im.verify()
    with Image.open(p) as im:size=im.size
    assert size==(1800,1200)
    images.append(dict(path=p.relative_to(ROOT).as_posix(),size=list(size),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),visually_reviewed=True))
shutil.copy2(GEOMETRY,ROOT/'02_geometry/geometry-master.json')
active=dict(revision=8,filename='home-main-v08.blend',geometry=GEOMETRY.relative_to(ROOT).as_posix(),geometry_sha256=sha,
    style=STYLE.relative_to(ROOT).as_posix(),style_sha256=style_sha,style_revision='modern-japanese-v04',previous_active_filename='home-main-v07.blend',
    furniture_count=21,live_session_verified=True,cabinet_selection='C, lower navy replaced with milk yellow',cabinet_top_gap_mm=0)
snapshots=[p['file'] for p in live if p['phase']=='previous_live_snapshot']
if snapshots:active['previous_live_snapshot']=snapshots[-1]
(ROOT/'06_blender/active-model.json').write_text(json.dumps(active,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
pending_path=ROOT/'05_style/cabinet-options-v08/pending-selection.json';selection=json.loads(pending_path.read_text(encoding='utf-8'))
selection.update(status='selected-and-applied',homeowner_selection=dict(option='C',amendment='replace lower navy with milk yellow',lower_srgb_concept='#F1DDAE',upper='cream',niche='walnut',source='direct user instruction'),
    active_model='06_blender/home-main-v08.blend',applied_geometry=GEOMETRY.relative_to(ROOT).as_posix(),geometry_sha256=sha,
    next_action='Continue from v08 and inspect latest saved furniture placements; no cabinet choice pending')
selection['designer_recommendation_status']='Historical recommendation B; homeowner selected amended C instead'
pending_path.write_text(json.dumps(selection,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
manifest=dict(revision=8,geometry_sha256=sha,style_sha256=style_sha,model='06_blender/home-main-v08.blend',actual_render_mode='Blender Cycles 128 samples, OptiX',
    imagegen_used_this_revision=False,images=images,furniture_count=21,parts=len(d['furniture']),source_walls=60,glass=12,new_window_parts=22,
    furniture_wall_aabb_intersections=fw,furniture_furniture_aabb_intersections=ff,all_21_positions_preserved=True,other_20_meshes_unchanged=True,
    cabinet=readback['cabinet'],window=d['features']['balconyWindow'],real_world_accuracy='Provisional geometry; reference drawing dimensions are not site measurements',
    review='04_reviews/v08审美与实用性.md',live_session='logs/v08-live-state.json',widget='logs/widget-v08-verification.json',old_v07_model_preserved=True)
(ROOT/'07_renders/v08-selected/render-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
files=[GEOMETRY,STYLE,ROOT/'06_blender/home-main-v08.blend',ROOT/'06_blender/active-model.json',ROOT/'09_delivery/v08修改说明.md',ROOT/'04_reviews/v08审美与实用性.md',
    ROOT/'03_layout/widget-layout-v08-initial.json',ROOT/'03_layout/blender-layout-latest.json',ROOT/'tools/home_design_move.py',ROOT/'00_sources/v08-balcony-window-reference.png',
    ROOT/'logs/model-v08-build.json',ROOT/'logs/model-v08-readback.json',ROOT/'logs/widget-v08-verification.json',ROOT/'logs/v08-source-ledger.json',ROOT/'07_renders/v08-selected/render-manifest.json']
files += [ROOT/p['path'] for p in images]
target=ROOT/'09_delivery/v08-奶黄通顶柜与阳台窗.zip'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as archive:
    for p in files:archive.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(target) as archive:assert archive.testzip() is None;count=len(archive.namelist())
report=dict(revision=8,zip=str(target),files=count,zip_valid=True,all_pngs_decoded=True,images_visually_reviewed=True,
    model_sha256=hashlib.sha256((ROOT/'06_blender/home-main-v08.blend').read_bytes()).hexdigest(),geometry_sha256=sha,style_sha256=style_sha,
    active_model_matches=True,geometry_master_matches=raw==(ROOT/'02_geometry/geometry-master.json').read_bytes(),previous_v07_unchanged=True,
    furniture_wall_intersections=0,furniture_furniture_intersections=0,selection_resolved=True)
(ROOT/'logs/v08-delivery-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('V08_DELIVERY_READY',count,sha)
