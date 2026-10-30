from pathlib import Path
from mathutils import Vector,Matrix
import bpy,bmesh,json,hashlib,ast,math,sys
ROOT=Path(r'D:\AI-Yang.cn\HomeDesign');SOURCE=ROOT/'06_blender/home-main-v10.blend';DEST=ROOT/'06_blender/home-main-v11.blend'
assert Path(bpy.data.filepath).resolve()==SOURCE.resolve()
assert not DEST.exists() or '--replace-draft' in sys.argv
raw=(ROOT/'02_geometry/geometry-master-v11.json').read_bytes();d=json.loads(raw)
sr=(ROOT/'05_style/modern-japanese-v07.json').read_bytes();s=json.loads(sr);sha=hashlib.sha256(raw).hexdigest();assert sha==s['geometry_sha256']
scene=bpy.context.scene;assert scene['home_design_revision']==10
existing={o['source_id']:o for o in scene.objects if o.get('home_design_role')=='furniture'};assert len(existing)==21
before={i:hashlib.sha256(str([tuple(v.co) for v in o.data.vertices]).encode()).hexdigest() for i,o in existing.items()}
target=bpy.data.collections['04 家具 · 整件选择 · 100mm']
tree=ast.parse((ROOT/'tools/render_modern_japanese_v02.py').read_text(encoding='utf-8'));node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='profile_mesh');exec(compile(ast.Module(body=[node],type_ignores=[]),'profile_mesh','exec'))
tree=ast.parse((ROOT/'tools/update_blender_v07.py').read_text(encoding='utf-8'));node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='mesh_part')
mats={'wood':bpy.data.materials['V10 · 减黄浅橡木'],'sage':bpy.data.materials['J02 · 低饱和苔绿色织物'],'fabric':bpy.data.materials['V10 · 细织棉麻感米灰'],
    'walnut':bpy.data.materials['V08 · 温润胡桃木置物格'],'ceramic':bpy.data.materials['V07 · ceramic']}
exec(compile(ast.Module(body=[node],type_ignores=[]),'mesh_part','exec'))
for group in d['furnitureObjects']:
    gid=group['id'];pp=[p for p in d['furniture'] if p['parent']==gid]
    if gid in existing:
        ob=existing[gid];ob.location.x=group['x']/1000;ob.location.y=-group['z']/1000
    else:
        children=[mesh_part(p) for p in pp];bpy.ops.object.select_all(action='DESELECT')
        for ob in children:
            ob.select_set(True);bpy.context.view_layer.objects.active=ob
            for mod in list(ob.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.context.view_layer.objects.active=children[0];bpy.ops.object.join();ob=bpy.context.view_layer.objects.active
        bpy.context.view_layer.update();world=[ob.matrix_world@v.co for v in ob.data.vertices];anchor=Vector((group['x']/1000,-group['z']/1000,0))
        ob.matrix_world=Matrix.Identity(4);ob.location=anchor
        for v,p in zip(ob.data.vertices,world):v.co=p-anchor
        bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
    ob.name=gid+' | '+group['name']
    for key,value in dict(home_design_role='furniture',source_id=gid,display_name=group['name'],zone=group['zone'],scheme=group['scheme'],part_count=len(pp),
        import_x_mm=group['x'],import_z_mm=group['z'],movement_step_mm=100,dimensions_mm=[group['dimensionsMm'][k] for k in ['length','width','height']],
        dimension_note=group['detail'],part_source_mm=json.dumps(pp,ensure_ascii=False),style_revision='modern-japanese-v07',base_height_mm=group['baseHeightMm']).items():ob[key]=value
    ob.lock_location[2]=True;ob.lock_rotation[0]=True;ob.lock_rotation[1]=True;ob.hide_select=False
ff={o['source_id']:o for o in scene.objects if o.get('home_design_role')=='furniture'};assert len(ff)==24
assert all(hashlib.sha256(str([tuple(v.co) for v in ff[i].data.vertices]).encode()).hexdigest()==digest for i,digest in before.items())
bpy.context.view_layer.update();audit=[]
for group in d['furnitureObjects']:
    ob=ff[group['id']];pts=[ob.matrix_world@v.co for v in ob.data.vertices];lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)];b=group['meshBoundsMm']
    expected=[b['x']/1000,-(b['z']+b['d'])/1000,b['y']/1000,(b['x']+b['w'])/1000,-b['z']/1000,(b['y']+b['h'])/1000]
    error=max(abs(a-b) for a,b in zip(lo+hi,expected))*1000;assert error<.05,(group['id'],error,lo,hi,expected)
    audit.append(dict(id=group['id'],x=group['x'],z=group['z'],dimensions_mm=list(ob['dimensions_mm']),mesh_bounds_error_mm=error))
assert sum(o.get('home_design_role')=='wall' for o in scene.objects)==60
assert sum(o.get('home_design_role')=='glass' for o in scene.objects)==12
assert sum(o.get('home_design_role')=='public_finish_detail' for o in scene.objects)==29
coll=bpy.data.collections['10 写实表现 · 人眼视角']
def camera(name,pos,look,lens):
    data=bpy.data.cameras.new(name);data.type='PERSP';data.lens=lens;data.sensor_width=36;data.clip_start=.02
    ob=bpy.data.objects.new(name,data);coll.objects.link(ob);ob.location=pos;ob.rotation_euler=(Vector(look)-ob.location).to_track_quat('-Z','Y').to_euler();return ob
camera('v11 · 客厅至阳台',(1.4,-7.1,1.65),(2.5,-2.4,1.0),20)
camera('v11 · 餐厅与玻璃门',(1.45,-6.1,1.65),(1.95,-8.4,1.0),22)
camera('v11 · 阳台茶席',(5.6,-2.3,1.9),(3.5,-.4,.60),23)
scene.name='v11 · 阳台茶席与公共区实景';scene['home_design_revision']=11;scene['home_design_geometry_sha256']=sha
scene['home_design_style_sha256']=hashlib.sha256(sr).hexdigest();scene['home_design_style_revision']='modern-japanese-v07';scene['home_design_style_file']='05_style/modern-japanese-v07.json'
scene['home_design_assumptions']=json.dumps(d['assumptions'],ensure_ascii=False);scene['home_design_balcony_tea_set']=json.dumps(d['features']['balconyTeaSet'],ensure_ascii=False)
scene['home_design_budget_considered']=False;scene['home_design_budget_scope']='用户已取消后续预算约束，仅考虑设计'
if 'home_design_budget_rmb' in scene:del scene['home_design_budget_rmb']
scene['lighting_scene']=0;scene.update_tag();scene.frame_set(scene.frame_current);bpy.context.view_layer.update()
scene.camera=bpy.data.objects['v11 · 客厅至阳台'];scene.cycles.samples=128;scene.cycles.use_denoising=True
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for dev in prefs.devices:dev.use=dev.type!='CPU'
scene.cycles.device='GPU';scene.render.resolution_x=1800;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
bpy.ops.object.select_all(action='DESELECT');ff['balcony-tea-table'].select_set(True);bpy.context.view_layer.objects.active=ff['balcony-tea-table']
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(DEST))
report=dict(revision=11,geometry_sha256=sha,style_sha256=scene['home_design_style_sha256'],base_model_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    furniture=audit,furniture_count=24,existing_21_meshes_preserved=True,latest_user_widget_positions_applied=True,source_walls=60,window_glass=12,kitchen_door_glass=3,public_detail_parts=29,
    added_furniture_ids=d['features']['balconyTeaSet']['furnitureIds'],private_room_boundaries_unchanged=True,budget_considered=False)
(ROOT/'logs/model-v11-build.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('MODEL_V11_BUILT',len(ff))
