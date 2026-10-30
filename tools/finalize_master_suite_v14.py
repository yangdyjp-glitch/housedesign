"""Bind checked v14 deliveries, preserving old versions and explicit uncertainty."""
from pathlib import Path
import hashlib,json,copy,zipfile,math
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def read(rel):return json.loads((ROOT/rel).read_text(encoding='utf-8'))
def write(rel,value):(ROOT/rel).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
d=read('02_geometry/geometry-master-v14.json');old=read('02_geometry/geometry-master-v13.json');style=read('05_style/modern-japanese-v10.json')
assert d['furnitureObjects'][:23]==old['furnitureObjects'] and d['furniture'][:len(old['furniture'])]==old['furniture'] and d['glass']==old['glass']
assert d['windowParts']==old['windowParts'] and d['doorParts']==old['doorParts'] and d['curtainParts']==old['curtainParts']
build=read('logs/model-v14-build.json');native=read('logs/v14-model-readback.json');widget=read('logs/widget-v14-verification.json');live=read('logs/v14-live-state.json')[-1]['live']
assert live['revision']==14 and len(live['positions'])==27 and live['geometry_sha256']==sha(ROOT/'02_geometry/geometry-master-v14.json')
assert native['geometry_sha256']==live['geometry_sha256']==style['geometry_sha256']==build['geometry_sha256']
assert widget['revision']==14 and widget['dimensionTooltips']==27 and len(widget['nudged'])==27 and not widget['runtimeErrors']
old_digest=read('logs/v13-delivery-verification.json')['model_sha256'];assert sha(ROOT/'06_blender/home-main-v13.blend')==old_digest
def overlap(a,b):return all(a[k]<b[k]+b[s]-.01 and a[k]+a[s]>b[k]+.01 for k,s in [('x','w'),('z','d'),('y','h')])
new=[p for p in d['furniture'] if p['parent'].startswith('master-')]
hits=[dict(part=p['id'],wall=w['id']) for p in new for w in d['walls'] if overlap(p,w)];assert not hits,hits
# The whole door sweep is checked against wall boxes and furniture AABBs using an OBB separating-axis test.
def rect_poly(p):return [(p['x'],p['z']),(p['x']+p['w'],p['z']),(p['x']+p['w'],p['z']+p['d']),(p['x'],p['z']+p['d'])]
def intersects(poly,other):
    for points in [poly,other]:
        for i,a in enumerate(points):
            b=points[(i+1)%4];axis=(-(b[1]-a[1]),b[0]-a[0]);length=math.hypot(*axis)
            if not length:continue
            axis=(axis[0]/length,axis[1]/length);aa=[x*axis[0]+z*axis[1] for x,z in poly];bb=[x*axis[0]+z*axis[1] for x,z in other]
            if max(aa)<=min(bb)+.01 or max(bb)<=min(aa)+.01:return False
    return True
leaf=next(p for p in d['bathParts'] if p['id']=='v14-bath-door-leaf');hx,hz=d['features']['masterSuite']['door']['hingePlanMm'];sweep_hits=[]
for degrees in range(91):
    a=-math.radians(degrees);c,s=math.cos(a),math.sin(a);poly=[(hx+(x-hx)*c+(z-hz)*s,hz-(x-hx)*s+(z-hz)*c) for x,z in rect_poly(leaf)]
    for q in d['walls']+d['furniture']:
        if q['y']>=leaf['y']+leaf['h'] or q['y']+q['h']<=leaf['y']:continue
        if intersects(poly,rect_poly(q)):sweep_hits.append(dict(degrees=degrees,id=q['id']))
assert not sweep_hits,sweep_hits
renders=[]
for p in sorted((ROOT/'07_renders/v14-master-suite').glob('*.png')):
    with Image.open(p) as im:im.verify()
    renders.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)))
assert len(renders)==6
with Image.open(ROOT/'09_delivery/v14-master-suite/主卧主卫调整平面.png') as im:im.verify()
active=read('06_blender/active-model.json');active.update(revision=14,filename='home-main-v14.blend',geometry='02_geometry/geometry-master-v14.json',geometry_sha256=sha(ROOT/'02_geometry/geometry-master-v14.json'),style='05_style/modern-japanese-v10.json',style_sha256=sha(ROOT/'05_style/modern-japanese-v10.json'),style_revision='modern-japanese-v10',previous_active_filename='home-main-v13.blend',furniture_count=27,live_session_verified=True,public_details=25,master_bath_study_only=False,master_bath_concept_applied=True,private_room_boundaries_changed=True,construction_approval_status='unverified; concept model only',master_suite=d['features']['masterSuite'],model_sha256=sha(ROOT/'06_blender/home-main-v14.blend'),panorama_model_revision=13,panorama_stale_for_current_master_suite=True,current_perspective_renders='07_renders/v14-master-suite',interactive_model='09_delivery/house-v14-preview.html')
write('06_blender/active-model.json',active)
(ROOT/'02_geometry/geometry-master.json').write_bytes((ROOT/'02_geometry/geometry-master-v14.json').read_bytes())
constraints=read('01_brief/current-design-constraints.json');constraints['master_suite']=dict(applied_model_revision=14,status='concept model; site feasibility unverified',brief=d['features']['masterSuite']);constraints['panorama_delivery']['current_master_revision']=14;constraints['panorama_delivery']['status']='historical v13; not re-rendered for v14 master-suite';write('01_brief/current-design-constraints.json',constraints)
write('03_layout/widget-layout-v14-initial.json',dict(revision=14,moveStepMm=100,furniturePositions=[dict(id=q['id'],x=q['x'],z=q['z'],dx=0,dz=0) for q in d['furnitureObjects']],masterBathDoorOpen=False,masterShowerOpen=False))
fragment=ROOT/'09_delivery/house-v14-fragment.html';host=Path(r'C:\Users\Administrator\.codex\visualizations\2026\10\29\01a187d1-69cc-73a1-805e-834e8e8bb476\house-structure.html');assert sha(fragment)==sha(host)
report=dict(revision=14,model_sha256=active['model_sha256'],geometry_sha256=active['geometry_sha256'],style_sha256=active['style_sha256'],saved_model_reopened=True,mcp_active_verified=True,public_objects_preserved=23,total_objects=27,new_object_wall_collisions=hits,door_sweep_wall_and_furniture_collisions=sweep_hits,door_sweep_sample_count=91,external_glass_window_parts_and_kitchen_door_unchanged=True,old_v13_model_unchanged=True,widget=widget,interactive_sha256=sha(fragment),native_renders=renders,render_geometry_unchanged_by_final_metadata_update=True,all_six_renders_visually_reviewed=True,plan_visually_reviewed=True,full_walls_in_saved_model=True,cutaway_observation_only=True,source_uncertainty_preserved=True,construction_certification=False,panorama_revision=13,panorama_updated=False,budget_considered=False)
write('logs/v14-delivery-verification.json',report);print('V14_DELIVERY_BOUND',active['model_sha256'])
