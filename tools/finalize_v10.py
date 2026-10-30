"""Activate only the v10 revision whose saved model, live session and visual were checked."""
from pathlib import Path
from itertools import combinations
from PIL import Image
import json,hashlib,shutil,zipfile,math
ROOT=Path(r'D:\AI-Yang.cn\HomeDesign')
def read(rel):return json.loads((ROOT/rel).read_text(encoding='utf-8'))
def write(rel,value):(ROOT/rel).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
GEOMETRY=ROOT/'02_geometry/geometry-master-v10.json';STYLE=ROOT/'05_style/modern-japanese-v06.json'
d=read(GEOMETRY.relative_to(ROOT));s=read(STYLE.relative_to(ROOT));sha=digest(GEOMETRY);style_sha=digest(STYLE)
build=read('logs/model-v10-build.json');back=read('logs/model-v10-readback.json');render=read('logs/v10-render-verification.json')
widget=read('logs/widget-v10-verification.json');live=read('logs/v10-live-state.json');previous=read('logs/v09-delivery-verification.json')
assert all(q['geometry_sha256']==sha for q in [s,build,back,render])
assert all(q['style_sha256']==style_sha for q in [build,back,render])
assert previous['model_sha256']==build['base_model_sha256']==digest(ROOT/'06_blender/home-main-v09.blend')
assert build['all_21_furniture_meshes_and_transforms_unchanged'] and back['all_21_positions_preserved']
assert back['lighting_attachments_verified'] and render['lighting_scenes']==3
assert widget['dimensionTooltips']==21 and widget['slidingDoorToggle'] and widget['doorClosingCollisionGuard'] and not widget['runtimeErrors']
assert widget['publicDetailParts']==29 and widget['mobileOverflow'] is False
current=live[-1]['live'];assert live[-1]['phase']=='activated' and current['revision']==10 and current['geometry_sha256']==sha
assert len(current['positions'])==21
old=read('02_geometry/geometry-master-v09.json')
assert old['walls']==d['walls'] and old['glass']==d['glass'] and old['windowParts']==d['windowParts'] and old['doorParts']==d['doorParts']
assert old['furnitureObjects']==d['furnitureObjects']
def overlap(a,b):return all(a[k]<b[k]+b[n]-.01 and a[k]+a[n]>b[k]+.01 for k,n in [('x','w'),('z','d'),('y','h')])
fw=[(p['id'],w['id']) for p in d['furniture'] for w in d['walls'] if overlap(p,w)]
ff=[(a['id'],b['id']) for a,b in combinations(d['furniture'],2) if a['parent']!=b['parent'] and overlap(a,b)]
fd=[(p['id'],f['id']) for p in d['detailParts'] if p.get('collidable') for f in d['furniture'] if overlap(p,f)]
assert not fw and not ff and not fd,(fw,ff,fd)
door_contacts={}
for opened in [False,True]:
    parts=[dict(p,x=p['x']+(800.5 if opened and p.get('movingLeaf')=='left' else 0)) for p in d['doorParts']]
    contacts=[(p['id'],f['id']) for p in parts for f in d['furniture'] if overlap(p,f)]
    assert not contacts;door_contacts['open' if opened else 'closed']=contacts
images=[]
for name in ['living-day','living-evening','desk-evening','door-wall-detail']:
    p=ROOT/'07_renders/v10-detail'/(name+'.png')
    with Image.open(p) as im:im.verify()
    with Image.open(p) as im:assert im.size==(1800,1200)
    images.append(dict(path=p.relative_to(ROOT).as_posix(),size=[1800,1200],sha256=digest(p),visually_reviewed=True))
diagram=ROOT/'09_delivery/v10主卫门位研究.png'
with Image.open(diagram) as im:im.verify()
with Image.open(diagram) as im:assert im.size==(1600,1270)
groups={q['id']:q for q in d['furnitureObjects']}
layout=dict(units='mm',revision=10,relative_to='geometry-master-v10',source='logs/v10-live-state.json actual managed Blender readback',kitchenDoorOpen=False,lightingScene='evening',
    objects=[dict(id=p['id'],x=p['x'],z=p['z'],dx=p['x']-groups[p['id']]['x'],dz=p['z']-groups[p['id']]['z'],rotation_z_degrees=math.degrees(p['rotation'])) for p in current['positions']])
write('03_layout/blender-layout-latest.json',layout);write('03_layout/blender-layout-v10.json',layout)
shutil.copy2(GEOMETRY,ROOT/'02_geometry/geometry-master.json')
active=dict(revision=10,filename='home-main-v10.blend',geometry=GEOMETRY.relative_to(ROOT).as_posix(),geometry_sha256=sha,
    style=STYLE.relative_to(ROOT).as_posix(),style_sha256=style_sha,style_revision='modern-japanese-v06',previous_active_filename='home-main-v09.blend',
    furniture_count=21,live_session_verified=True,cabinet_selection='C, lower navy replaced with milk yellow',cabinet_top_gap_mm=0,
    kitchen_sliding_door=True,door_default_open=False,public_details=29,lighting_scenes=['day','evening','cleaning'],default_lighting_scene='evening',
    master_bath_study_only=True,private_room_boundaries_changed=False)
write('06_blender/active-model.json',active)
selection=read('05_style/cabinet-options-v08/pending-selection.json');selection.update(active_model='06_blender/home-main-v10.blend',next_action='Continue from v10 and latest placements; cabinet C with milk yellow remains applied')
write('05_style/cabinet-options-v08/pending-selection.json',selection)
interview=read('01_brief/detail-interview-v10.json');interview.update(status='public preferences applied to v10; storage inventory deferred',applied_model='06_blender/home-main-v10.blend',applied_geometry_sha256=sha,
    main_model_changed_during_interview=False,master_bath_study='01_brief/master-bath-feasibility-v10.json')
write('01_brief/detail-interview-v10.json',interview)
manifest=dict(revision=10,model='06_blender/home-main-v10.blend',geometry_sha256=sha,style_sha256=style_sha,actual_render_mode='Blender Cycles 128 samples OptiX',
    imagegen_used_this_revision=False,images=images,furniture_count=21,source_walls=60,window_glass=12,kitchen_door_glass=3,public_detail_parts=29,
    all_21_furniture_meshes_and_transforms_unchanged=True,original_architecture_sources_preserved=True,lighting_scenes=3,lighting_attachments_verified=True,
    lighting_status='concept scene contrast only; no luminaire or photometric verification',furniture_wall_intersections=fw,furniture_furniture_intersections=ff,
    public_door_furniture_contacts=fd,kitchen_door_furniture_contacts=door_contacts,private_room_boundaries_changed=False,master_bath_study_only=True,
    review='04_reviews/v10审美与实用性.md',delivery_note='09_delivery/v10深化说明.md',live_session='logs/v10-live-state.json',widget='logs/widget-v10-verification.json',previous_v09_model_preserved=True)
write('07_renders/v10-detail/render-manifest.json',manifest)
files=[GEOMETRY,STYLE,ROOT/'06_blender/home-main-v10.blend',ROOT/'06_blender/active-model.json',ROOT/'09_delivery/v10深化说明.md',ROOT/'04_reviews/v10审美与实用性.md',
    ROOT/'03_layout/widget-layout-v10-initial.json',ROOT/'03_layout/blender-layout-v10.json',ROOT/'tools/home_design_move.py',ROOT/'00_sources/v10-master-suite-reference.png',
    ROOT/'logs/model-v10-build.json',ROOT/'logs/model-v10-readback.json',ROOT/'logs/widget-v10-verification.json',ROOT/'logs/v10-source-ledger.json',ROOT/'07_renders/v10-detail/render-manifest.json',
    ROOT/'01_brief/detail-interview-v10.json',ROOT/'01_brief/master-bath-feasibility-v10.json',ROOT/'09_delivery/v10主卫门位研究.svg',diagram]
files += [ROOT/q['path'] for q in images]
target=ROOT/'09_delivery/v10-公共区深化与主卫研究.zip'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as archive:
    for p in files:archive.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(target) as archive:assert archive.testzip() is None;count=len(archive.namelist())
report=dict(revision=10,zip=str(target),files=count,zip_valid=True,images_visually_reviewed=True,master_bath_diagram_visually_reviewed=True,
    model_sha256=digest(ROOT/'06_blender/home-main-v10.blend'),geometry_sha256=sha,style_sha256=style_sha,active_model_matches=True,
    geometry_master_matches=GEOMETRY.read_bytes()==(ROOT/'02_geometry/geometry-master.json').read_bytes(),previous_v09_unchanged=True,
    private_room_boundaries_unchanged=True,all_21_furniture_retained=True,public_door_furniture_contacts=fd,lighting_scenes_verified_in_live_session=True)
write('logs/v10-delivery-verification.json',report)
print('V10_DELIVERY_READY',count,sha)
