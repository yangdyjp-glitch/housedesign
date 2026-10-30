from pathlib import Path
import bpy,json,hashlib
ROOT=Path(r'D:\AI-Yang.cn\HomeDesign');OUT=ROOT/'07_renders/v09-sliding-door';OUT.mkdir(parents=True,exist_ok=True)
assert Path(bpy.data.filepath).resolve()==(ROOT/'06_blender/home-main-v09.blend').resolve()
scene=bpy.context.scene;raw=(ROOT/'02_geometry/geometry-master-v09.json').read_bytes();d=json.loads(raw)
assert scene['home_design_revision']==9 and scene['home_design_geometry_sha256']==hashlib.sha256(raw).hexdigest()
assert scene['home_design_style_sha256']==hashlib.sha256((ROOT/'05_style/modern-japanese-v05.json').read_bytes()).hexdigest()
ff={o['source_id']:o for o in scene.objects if o.get('home_design_role')=='furniture'};assert len(ff)==21
rows=[]
for g in d['furnitureObjects']:
    o=ff[g['id']];assert abs(o.location.x*1000-g['x'])<.01 and abs(-o.location.y*1000-g['z'])<.01
    assert list(o['dimensions_mm'])==[g['dimensionsMm'][k] for k in ['length','width','height']]
    rows.append(dict(id=g['id'],x=g['x'],z=g['z'],dimensions_mm=list(o['dimensions_mm'])))
assert sum(o.get('home_design_role')=='wall' for o in scene.objects)==60
assert sum(o.get('home_design_role')=='glass' for o in scene.objects)==12
assert sum(o.get('home_design_role')=='door_glass' for o in scene.objects)==3
assert sum(o.get('home_design_role')=='door_frame' for o in scene.objects)==16
root=next(o for o in scene.objects if o.get('source_id')=='kitchen-slider');assert root['open_ratio']==0
report=dict(saved_model_reopened=True,revision=9,geometry_sha256=scene['home_design_geometry_sha256'],style_sha256=scene['home_design_style_sha256'],
    furniture=rows,architecture=dict(source_walls=60,window_glass=12,door_glass=3,door_frames=16),door=d['features']['kitchenSlidingDoor'])
(ROOT/'logs/model-v09-readback.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for dev in prefs.devices:dev.use=dev.type!='CPU'
scene.cycles.device='GPU';scene.cycles.samples=96;scene.cycles.use_denoising=True
scene.camera=bpy.data.objects['v09 · 厨房看餐厅玻璃门'];records=[]
for name,value in [('door-closed',0),('door-open',1)]:
    root['open_ratio']=float(value);root.update_tag();scene.frame_set(scene.frame_current);bpy.context.view_layer.update()
    moving=bpy.data.objects['kitchen-slider-left | 活动左扇'];assert abs(moving.matrix_world.translation.x-value*.8005)<1e-6
    scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True);records.append(dict(view=name,path=scene.render.filepath,open_ratio=value))
report['renders']=records;report['render_mode']='Blender Cycles 96 samples OptiX, same camera, full architecture, unsaved pose change only'
(ROOT/'logs/v09-render-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('V09_RENDER_VERIFIED '+json.dumps(dict(views=2,furniture=21,door_motion_verified=True)))
