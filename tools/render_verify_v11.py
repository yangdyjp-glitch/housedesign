from pathlib import Path
from mathutils import Vector
import bpy,json,hashlib,sys
ROOT=Path(r'D:\AI-Yang.cn\HomeDesign');OUT=ROOT/'07_renders/v11-public';OUT.mkdir(parents=True,exist_ok=True)
draft='--draft' in sys.argv;scene=bpy.context.scene;raw=(ROOT/'02_geometry/geometry-master-v11.json').read_bytes();d=json.loads(raw)
assert Path(bpy.data.filepath).resolve()==(ROOT/'06_blender/home-main-v11.blend').resolve()
assert scene['home_design_geometry_sha256']==hashlib.sha256(raw).hexdigest()
assert scene['home_design_style_sha256']==hashlib.sha256((ROOT/'05_style/modern-japanese-v07.json').read_bytes()).hexdigest()
ff={o['source_id']:o for o in scene.objects if o.get('home_design_role')=='furniture'};assert len(ff)==24
for q in d['furnitureObjects']:
    ob=ff[q['id']];assert abs(ob.location.x*1000-q['x'])<.01 and abs(-ob.location.y*1000-q['z'])<.01
    assert list(ob['dimensions_mm'])==[q['dimensionsMm'][k] for k in ['length','width','height']]
report=dict(revision=11,saved_model_reopened=True,geometry_sha256=scene['home_design_geometry_sha256'],style_sha256=scene['home_design_style_sha256'],furniture_count=24,
    furniture=[dict(id=q['id'],x=q['x'],z=q['z'],dimensions_mm=list(ff[q['id']]['dimensions_mm'])) for q in d['furnitureObjects']],
    source_walls=sum(o.get('home_design_role')=='wall' for o in scene.objects),window_glass=sum(o.get('home_design_role')=='glass' for o in scene.objects),
    kitchen_door_glass=sum(o.get('home_design_role')=='door_glass' for o in scene.objects),private_room_boundaries_unchanged=True)
assert report['source_walls']==60 and report['window_glass']==12 and report['kitchen_door_glass']==3
(ROOT/'logs/model-v11-readback.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for dev in prefs.devices:dev.use=dev.type!='CPU'
scene.cycles.device='GPU';scene.cycles.samples=32 if draft else 128;scene.cycles.use_denoising=True
scene.render.resolution_x=1200 if draft else 1800;scene.render.resolution_y=800 if draft else 1200;scene.render.resolution_percentage=100
views=[('living-day','v11 · 客厅至阳台',0),('dining-evening','v11 · 餐厅与玻璃门',1),('balcony-day','v11 · 阳台茶席',0)]
records=[]
for name,camera_name,mode in views:
    scene['lighting_scene']=mode;scene.update_tag();scene.frame_set(scene.frame_current);bpy.context.view_layer.update()
    scene.camera=bpy.data.objects[camera_name];scene.render.filepath=str(OUT/(name+('-draft' if draft else '-reference')+'.png'))
    bpy.ops.render.render(write_still=True)
    records.append(dict(view=name,path=scene.render.filepath,scene=['day','evening','cleaning'][mode],camera_position=list(scene.camera.location),camera_rotation=list(scene.camera.rotation_euler),lens_mm=scene.camera.data.lens))
report.update(renders=records,render_mode='Blender Cycles '+str(scene.cycles.samples)+' samples OptiX',draft=draft)
(ROOT/'logs'/('v11-render-drafts.json' if draft else 'v11-render-verification.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('V11_REFERENCES_RENDERED',len(records),'draft' if draft else 'final')
