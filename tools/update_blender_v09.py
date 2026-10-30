"""Add the marked fixed door assembly without changing the existing house or furniture."""
from pathlib import Path
from mathutils import Vector
import bpy,json,hashlib,math,ast
ROOT=Path(r'D:\AI-Yang.cn\HomeDesign');SOURCE=ROOT/'06_blender/home-main-v08.blend';DEST=ROOT/'06_blender/home-main-v09.blend'
assert Path(bpy.data.filepath).resolve()==SOURCE.resolve() and not DEST.exists()
raw=(ROOT/'02_geometry/geometry-master-v09.json').read_bytes();d=json.loads(raw)
style_raw=(ROOT/'05_style/modern-japanese-v05.json').read_bytes();style=json.loads(style_raw);assert style['geometry_sha256']==hashlib.sha256(raw).hexdigest()
scene=bpy.context.scene;assert scene['home_design_revision']==8
prior_sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
ff={o['source_id']:o for o in scene.objects if o.get('home_design_role')=='furniture'};assert len(ff)==21
before={i:(tuple(o.location),tuple(o.rotation_euler),hashlib.sha256(str([tuple(v.co) for v in o.data.vertices]).encode()).hexdigest()) for i,o in ff.items()}
tree=ast.parse((ROOT/'tools/render_modern_japanese_v02.py').read_text(encoding='utf-8'));node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='profile_mesh')
exec(compile(ast.Module(body=[node],type_ignores=[]),'profile_mesh','exec'))
coll=bpy.data.collections.new('v09 餐厨玻璃推拉门 · 原位开启');scene.collection.children.link(coll)
root=bpy.data.objects.new('kitchen-slider | 餐厨玻璃推拉门',None);coll.objects.link(root);root.empty_display_type='CUBE';root.empty_display_size=.1
root['home_design_role']='door_assembly';root['source_id']='kitchen-slider';root['dimensions_mm']=[1691,120,2750]
root['open_ratio']=0.0;root.id_properties_ui('open_ratio').update(min=0,max=1,soft_min=0,soft_max=1,description='开启比例：0关闭，1左扇向右叠放；约800.5mm净开口，尺寸待实测')
root['source_mm']=json.dumps(d['features']['kitchenSlidingDoor'],ensure_ascii=False)
root['note']='Fixed architectural assembly; the opening control is not a free furniture move.'
leaves={}
for side in ['left','right']:
    leaf=bpy.data.objects.new('kitchen-slider-'+side+' | '+('活动左扇' if side=='left' else '右轨门扇'),None);coll.objects.link(leaf);leaf.parent=root
    leaf['home_design_role']='door_leaf';leaf['source_id']='kitchen-slider-'+side;leaf.empty_display_size=.05;leaves[side]=leaf
driver=leaves['left'].driver_add('location',0).driver;driver.type='SCRIPTED'
var=driver.variables.new();var.name='open_ratio';var.type='SINGLE_PROP';var.targets[0].id=root;var.targets[0].data_path='["open_ratio"]'
driver.expression='open_ratio * '+repr(d['features']['kitchenSlidingDoor']['openTravelMm']/1000)
frame=bpy.data.materials['R01 · 窗框暖灰铝材'];glass=bpy.data.materials['R01 · 实体透明玻璃']
parts={}
for p in d['doorParts']:
    mesh=profile_mesh(p['id'],p['w']/1000,p['d']/1000,p['h']/1000,[0]*4)
    for face in mesh.polygons:face.use_smooth=False
    mesh.materials.append(glass if p['kind']=='door-glass' else frame)
    ob=bpy.data.objects.new(p['id'],mesh);coll.objects.link(ob);ob.location=(p['x']/1000,-(p['z']+p['d'])/1000,p['y']/1000)
    ob.parent=leaves[p['movingLeaf']] if p.get('movingLeaf') else root
    ob['home_design_role']='door_glass' if p['kind']=='door-glass' else 'door_frame';ob['source_id']=p['id'];ob['assembly']='kitchen-slider';ob['source_mm']=json.dumps(p,ensure_ascii=False)
    if p.get('movingLeaf'):ob['moving_leaf']=p['movingLeaf']
    if p['kind']!='door-glass':
        bevel=ob.modifiers.new('细微触边','BEVEL');bevel.width=.0005;bevel.segments=2;bevel.harden_normals=True;ob.modifiers.new('平面法线','WEIGHTED_NORMAL')
    parts[p['id']]=ob
def pose(value):
    root['open_ratio']=float(value);root.update_tag();scene.frame_set(scene.frame_current);bpy.context.view_layer.update()
pose(0)
audit=[]
for p in d['doorParts']:
    ob=parts[p['id']];pts=[ob.matrix_world@v.co for v in ob.data.vertices];lo=[min(v[i] for v in pts) for i in range(3)];hi=[max(v[i] for v in pts) for i in range(3)]
    expected=[p['x']/1000,-(p['z']+p['d'])/1000,p['y']/1000,(p['x']+p['w'])/1000,-p['z']/1000,(p['y']+p['h'])/1000]
    error=max(abs(a-b) for a,b in zip(lo+hi,expected))*1000;assert error<.01,(p['id'],error)
    audit.append(dict(id=p['id'],bounds_error_mm=error))
pose(1);assert abs(leaves['left'].matrix_world.translation.x-.8005)<1e-6
pose(0);assert abs(leaves['left'].matrix_world.translation.x)<1e-6
assert all((tuple(ff[i].location),tuple(ff[i].rotation_euler),hashlib.sha256(str([tuple(v.co) for v in ff[i].data.vertices]).encode()).hexdigest())==value for i,value in before.items())
assert sum(o.get('home_design_role')=='wall' for o in scene.objects)==60
assert sum(o.get('home_design_role')=='glass' for o in scene.objects)==12
assert sum(o.get('home_design_role')=='door_glass' for o in scene.objects)==3
scene.name='v09 · 餐厨玻璃推拉门'
scene['home_design_revision']=9;scene['home_design_geometry_sha256']=style['geometry_sha256'];scene['home_design_style_sha256']=hashlib.sha256(style_raw).hexdigest()
scene['home_design_style_revision']='modern-japanese-v05';scene['home_design_style_file']='05_style/modern-japanese-v05.json';scene['home_design_assumptions']=json.dumps(d['assumptions'],ensure_ascii=False)
scene['home_design_kitchen_sliding_door']=json.dumps(d['features']['kitchenSlidingDoor'],ensure_ascii=False)
cam=bpy.data.cameras.new('v09 · 厨房看餐厅玻璃门');cam.type='PERSP';cam.lens=21;cam.sensor_width=36;cam.clip_start=.02
camera=bpy.data.objects.new(cam.name,cam);bpy.data.collections['10 写实表现 · 人眼视角'].objects.link(camera)
camera.location=(2.2365,-12.15,1.50);camera.rotation_euler=(Vector((2.2365,-9.695,1.375))-camera.location).to_track_quat('-Z','Y').to_euler();scene.camera=camera
scene.cycles.samples=96;scene.cycles.use_denoising=True;prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for dev in prefs.devices:dev.use=dev.type!='CPU'
scene.cycles.device='GPU';scene.render.resolution_x=1800;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
bpy.ops.object.select_all(action='DESELECT');root.select_set(True);bpy.context.view_layer.objects.active=root
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(DEST))
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==prior_sha
report=dict(revision=9,model=str(DEST),geometry_sha256=style['geometry_sha256'],style_sha256=scene['home_design_style_sha256'],door_parts=audit,
    all_21_furniture_meshes_and_transforms_unchanged=True,wall_sources=60,existing_window_glass=12,door_glass=3,door_frames=16,opening_motion_tested=True,default_open=False,
    opening=d['features']['kitchenSlidingDoor'],previous_model_sha256=prior_sha)
(ROOT/'logs/model-v09-build.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('MODEL_V09_BUILT '+json.dumps(dict(furniture=21,door_parts=len(parts),door_motion_verified=True)))
