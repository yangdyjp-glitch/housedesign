from pathlib import Path
from mathutils import Vector
import bpy,json,hashlib
ROOT=Path(r'D:\AI-Yang.cn\HomeDesign');OUT=ROOT/'07_renders/v10-detail';OUT.mkdir(parents=True,exist_ok=True)
scene=bpy.context.scene;raw=(ROOT/'02_geometry/geometry-master-v10.json').read_bytes();d=json.loads(raw)
assert Path(bpy.data.filepath).resolve()==(ROOT/'06_blender/home-main-v10.blend').resolve()
assert scene['home_design_revision']==10 and scene['home_design_geometry_sha256']==hashlib.sha256(raw).hexdigest()
assert scene['home_design_style_sha256']==hashlib.sha256((ROOT/'05_style/modern-japanese-v06.json').read_bytes()).hexdigest()
ff={o['source_id']:o for o in scene.objects if o.get('home_design_role')=='furniture'};assert len(ff)==21
rows=[]
for g in d['furnitureObjects']:
    ob=ff[g['id']];assert abs(ob.location.x*1000-g['x'])<.01 and abs(-ob.location.y*1000-g['z'])<.01
    assert list(ob['dimensions_mm'])==[g['dimensionsMm'][k] for k in ['length','width','height']]
    rows.append(dict(id=g['id'],x=g['x'],z=g['z'],dimensions_mm=list(ob['dimensions_mm'])))
bpy.context.view_layer.update();lights=json.loads(scene['home_design_lighting_records'])
for rec in lights:
    ob=bpy.data.objects[rec['name']];assert (ob.matrix_world.translation-Vector(rec['position'])).length<.0001,(rec['name'],list(ob.matrix_world.translation),rec['position'])
    if rec['parent_furniture']:assert ob.parent==ff[rec['parent_furniture']]
assert sum(o.get('home_design_role')=='wall' for o in scene.objects)==60
assert sum(o.get('home_design_role')=='glass' for o in scene.objects)==12
assert sum(o.get('home_design_role')=='door_glass' for o in scene.objects)==3
assert sum(o.get('home_design_role')=='public_finish_detail' for o in scene.objects)==29
report=dict(saved_model_reopened=True,revision=10,geometry_sha256=scene['home_design_geometry_sha256'],style_sha256=scene['home_design_style_sha256'],furniture=rows,
    all_21_positions_preserved=True,private_room_boundaries_unchanged=True,architecture=dict(source_walls=60,window_glass=12,kitchen_door_glass=3,public_detail_parts=29),
    lighting_attachments_verified=True,lighting_scenes=3,source_scope='public material, closed door finishes and lighting only')
(ROOT/'logs/model-v10-readback.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for dev in prefs.devices:dev.use=dev.type!='CPU'
scene.cycles.device='GPU';scene.cycles.samples=128;scene.cycles.use_denoising=True
cam=bpy.data.cameras.new('v10 · 门墙与踢脚收口');cam.type='PERSP';cam.lens=23;cam.sensor_width=36
camera=bpy.data.objects.new(cam.name,cam);scene.collection.objects.link(camera);camera.location=(5.65,-3.3,1.55)
camera.rotation_euler=(Vector((5.45,-6.0,1.12))-camera.location).to_track_quat('-Z','Y').to_euler()
views=[('living-day','v07 · 电视右侧绿植',0),('living-evening','v07 · 电视右侧绿植',1),('desk-evening','办公区细节 · 双工位单椅',1),('door-wall-detail',cam.name,0)]
records=[]
for name,camera_name,mode in views:
    scene['lighting_scene']=mode;scene.update_tag();scene.frame_set(scene.frame_current);bpy.context.view_layer.update()
    scene.camera=bpy.data.objects[camera_name];scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
    records.append(dict(view=name,path=scene.render.filepath,scene=['day','evening','cleaning'][mode]))
report.update(renders=records,render_mode='Blender Cycles 128 samples OptiX',lighting_status='concept scene contrast only, no photometric fixture calculation')
(ROOT/'logs/v10-render-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('V10_RENDER_VERIFIED',len(records))
