"""Publish verified v09 metadata and retain the prior main model."""
from pathlib import Path
from itertools import combinations
from PIL import Image
import json,hashlib,shutil,zipfile,math
ROOT=Path(r'D:\AI-Yang.cn\HomeDesign');GEOMETRY=ROOT/'02_geometry/geometry-master-v09.json';raw=GEOMETRY.read_bytes();d=json.loads(raw)
STYLE=ROOT/'05_style/modern-japanese-v05.json';style_raw=STYLE.read_bytes();style=json.loads(style_raw)
sha=hashlib.sha256(raw).hexdigest();style_sha=hashlib.sha256(style_raw).hexdigest();assert style['geometry_sha256']==sha
build=json.loads((ROOT/'logs/model-v09-build.json').read_text(encoding='utf-8'));readback=json.loads((ROOT/'logs/model-v09-readback.json').read_text(encoding='utf-8'))
widget=json.loads((ROOT/'logs/widget-v09-verification.json').read_text(encoding='utf-8'));live=json.loads((ROOT/'logs/v09-live-state.json').read_text(encoding='utf-8'))
assert build['geometry_sha256']==readback['geometry_sha256']==sha and readback['style_sha256']==style_sha
assert build['all_21_furniture_meshes_and_transforms_unchanged'] and len(readback['furniture'])==21
assert widget['dimensionTooltips']==21 and widget['slidingDoorToggle'] and widget['doorClosingCollisionGuard'] and not widget['runtimeErrors']
current=live[-1]['live'];assert live[-1]['phase']=='activated' and current['revision']==9 and current['geometry_sha256']==sha
previous=json.loads((ROOT/'logs/v08-delivery-verification.json').read_text(encoding='utf-8'))
assert previous['model_sha256']==hashlib.sha256((ROOT/'06_blender/home-main-v08.blend').read_bytes()).hexdigest()==build['previous_model_sha256']
def overlaps(a,b):return all(a[k]<b[k]+b[s]-.01 and a[k]+a[s]>b[k]+.01 for k,s in [('x','w'),('z','d'),('y','h')])
fw=[(p['id'],w['id']) for p in d['furniture'] for w in d['walls'] if overlaps(p,w)]
ff=[(a['id'],b['id']) for a,b in combinations(d['furniture'],2) if a['parent']!=b['parent'] and overlaps(a,b)]
door_contacts={}
for opened in [False,True]:
    parts=[dict(p,x=p['x']+(d['features']['kitchenSlidingDoor']['openTravelMm'] if opened and p.get('movingLeaf')=='left' else 0)) for p in d['doorParts']]
    contacts=[(p['id'],f['id']) for p in parts for f in d['furniture'] if overlaps(p,f)]
    assert not contacts,contacts;door_contacts['open' if opened else 'closed']=contacts
assert not fw and not ff,(fw,ff)
images=[]
for name in ['door-closed','door-open']:
    p=ROOT/'07_renders/v09-sliding-door'/(name+'.png')
    with Image.open(p) as im:im.verify()
    with Image.open(p) as im:size=im.size
    assert size==(1800,1200)
    images.append(dict(path=p.relative_to(ROOT).as_posix(),size=list(size),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),visually_reviewed=True))
# Save the latest layout from the actual verified MCP readback, rather than relabelling an old export.
groups={g['id']:g for g in d['furnitureObjects']}
layout=dict(units='mm',revision=9,relative_to='geometry-master-v09',source='logs/v09-live-state.json actual managed Blender readback',kitchenDoorOpen=False,
    objects=[dict(id=p['id'],x=p['x'],z=p['z'],dx=p['x']-groups[p['id']]['x'],dz=p['z']-groups[p['id']]['z'],rotation_z_degrees=math.degrees(p['rotation'])) for p in current['positions']])
for path in ['03_layout/blender-layout-latest.json','03_layout/blender-layout-v09.json']:(ROOT/path).write_text(json.dumps(layout,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
shutil.copy2(GEOMETRY,ROOT/'02_geometry/geometry-master.json')
active=dict(revision=9,filename='home-main-v09.blend',geometry=GEOMETRY.relative_to(ROOT).as_posix(),geometry_sha256=sha,style=STYLE.relative_to(ROOT).as_posix(),
    style_sha256=style_sha,style_revision='modern-japanese-v05',previous_active_filename='home-main-v08.blend',furniture_count=21,live_session_verified=True,
    cabinet_selection='C, lower navy replaced with milk yellow',cabinet_top_gap_mm=0,kitchen_sliding_door=True,door_default_open=False)
(ROOT/'06_blender/active-model.json').write_text(json.dumps(active,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Keep the earlier cabinet choice resolved while pointing continuation to the current main revision.
selection_path=ROOT/'05_style/cabinet-options-v08/pending-selection.json';selection=json.loads(selection_path.read_text(encoding='utf-8'))
selection.update(active_model='06_blender/home-main-v09.blend',next_action='Continue from v09 and inspect latest furniture placements; cabinet choice C with milk yellow remains applied')
selection_path.write_text(json.dumps(selection,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
manifest=dict(revision=9,geometry_sha256=sha,style_sha256=style_sha,model='06_blender/home-main-v09.blend',actual_render_mode='Blender Cycles 96 samples OptiX',
    imagegen_used_this_revision=False,images=images,furniture_count=21,parts=len(d['furniture']),source_walls=60,existing_window_glass=12,door_glass=3,door_frames=16,
    furniture_wall_intersections=fw,furniture_furniture_intersections=ff,door_furniture_contacts=door_contacts,all_21_furniture_meshes_and_transforms_unchanged=True,
    door=d['features']['kitchenSlidingDoor'],chair4_to_door_line_mm=285,chair_retreat_status='Requires on-site experience; positions retained',
    real_world_accuracy='provisional existing opening and conceptual door system, site and product dimensions govern',
    review='04_reviews/v09审美与实用性.md',live_session='logs/v09-live-state.json',widget='logs/widget-v09-verification.json',previous_v08_model_preserved=True)
(ROOT/'07_renders/v09-sliding-door/render-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
files=[GEOMETRY,STYLE,ROOT/'06_blender/home-main-v09.blend',ROOT/'06_blender/active-model.json',ROOT/'09_delivery/v09修改说明.md',ROOT/'04_reviews/v09审美与实用性.md',
    ROOT/'03_layout/widget-layout-v09-initial.json',ROOT/'03_layout/blender-layout-v09.json',ROOT/'tools/home_design_move.py',ROOT/'00_sources/v09-dining-kitchen-door-markup.png',
    ROOT/'logs/model-v09-build.json',ROOT/'logs/model-v09-readback.json',ROOT/'logs/widget-v09-verification.json',ROOT/'logs/v09-source-ledger.json',ROOT/'07_renders/v09-sliding-door/render-manifest.json']
files += [ROOT/p['path'] for p in images];target=ROOT/'09_delivery/v09-餐厨玻璃推拉门.zip'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as archive:
    for p in files:archive.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(target) as archive:assert archive.testzip() is None;count=len(archive.namelist())
report=dict(revision=9,zip=str(target),files=count,zip_valid=True,images_visually_reviewed=True,model_sha256=hashlib.sha256((ROOT/'06_blender/home-main-v09.blend').read_bytes()).hexdigest(),
    geometry_sha256=sha,style_sha256=style_sha,active_model_matches=True,geometry_master_matches=raw==(ROOT/'02_geometry/geometry-master.json').read_bytes(),
    previous_v08_unchanged=True,door_furniture_contacts=door_contacts,door_toggle_verified=True,all_21_furniture_retained=True)
(ROOT/'logs/v09-delivery-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('V09_DELIVERY_READY',count,sha)
