"""Apply the selected amended C cabinet and source-referenced balcony window."""
from pathlib import Path
from mathutils import Vector, Matrix
import bpy, bmesh, json, hashlib, ast, sys, math

ROOT=Path(r'D:\AI-Yang.cn\HomeDesign')
SOURCE=ROOT/'06_blender/home-main-v07.blend'
DEST=ROOT/'06_blender/home-main-v08.blend'
assert Path(bpy.data.filepath).resolve()==SOURCE.resolve()
assert not DEST.exists() or '--replace-draft' in sys.argv,'Preserve every published main revision.'
raw=(ROOT/'02_geometry/geometry-master-v08.json').read_bytes();data=json.loads(raw)
style_raw=(ROOT/'05_style/modern-japanese-v04.json').read_bytes();style=json.loads(style_raw)
assert style['geometry_sha256']==hashlib.sha256(raw).hexdigest()
scene=bpy.context.scene
assert scene['home_design_revision']==7
baseline_file_sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
furniture={o['source_id']:o for o in scene.objects if o.get('home_design_role')=='furniture'}
assert len(furniture)==21
others={i:(tuple(o.location),tuple(o.rotation_euler),hashlib.sha256(str([tuple(v.co) for v in o.data.vertices]).encode()).hexdigest()) for i,o in furniture.items() if i!='tv-high'}
tree=ast.parse((ROOT/'tools/render_modern_japanese_v02.py').read_text(encoding='utf-8'))
node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='profile_mesh')
exec(compile(ast.Module(body=[node],type_ignores=[]),'profile_mesh','exec'))

def material(name,key):
    rec=data['furnitureMaterials'][key]
    m=bpy.data.materials.new(name);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=rec['color'];p.inputs['Roughness'].default_value=rec['roughness']
    if 'proposal_srgb_hex' in rec:m['selected_srgb_hex']=rec['proposal_srgb_hex']
    return m
mats={'cabinet':bpy.data.materials['R01 · 暖白哑光柜门'],'navy':bpy.data.materials['J02 · 深蓝书脊'],'metal':bpy.data.materials['R01 · 深灰细砂金属']}
mats['butter']=material('V08 · 柔和奶黄色下柜','butter')
mats['walnut']=material('V08 · 温润胡桃木置物格','walnut')
n=mats['walnut'].node_tree.nodes;l=mats['walnut'].node_tree.links
tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=5;tex.inputs['Detail'].default_value=2
coord=n.new('ShaderNodeTexCoord');mapping=n.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(12,.45,3)
l.new(coord.outputs['Object'],mapping.inputs[0]);l.new(mapping.outputs[0],tex.inputs['Vector'])
ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.055,.025,.012,1);ramp.color_ramp.elements[1].color=(.21,.105,.047,1)
l.new(tex.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],n.get('Principled BSDF').inputs['Base Color'])
target=bpy.data.collections['04 家具 · 整件选择 · 100mm']
group=next(g for g in data['furnitureObjects'] if g['id']=='tv-high')
parts=[p for p in data['furniture'] if p['parent']=='tv-high']
bpy.data.objects.remove(furniture['tv-high'],do_unlink=True)

def make_part(p,collection,mat,bevel=0):
    radii=[r/1000 for r in p.get('worldXYCornerRadiiMm',[0]*4)]
    mesh=profile_mesh(p['id'],p['w']/1000,p['d']/1000,p['h']/1000,radii)
    if not any(radii):
        for face in mesh.polygons:face.use_smooth=False
    mesh.materials.append(mat)
    ob=bpy.data.objects.new(p['id'],mesh);collection.objects.link(ob)
    ob.location=(p['x']/1000,-(p['z']+p['d'])/1000,p['y']/1000)
    if bevel:
        mod=ob.modifiers.new('细微触边','BEVEL');mod.width=min(bevel,min(p[k] for k in ['w','d','h'])/4000);mod.segments=2;mod.harden_normals=True
        ob.modifiers.new('细面法线','WEIGHTED_NORMAL')
    ob['source_id']=p['id'];ob['source_mm']=json.dumps(p,ensure_ascii=False)
    return ob

children=[make_part(p,target,mats[p['material']],.0015) for p in parts]
bpy.ops.object.select_all(action='DESELECT')
for ob in children:
    ob.select_set(True);bpy.context.view_layer.objects.active=ob
    for mod in list(ob.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.context.view_layer.objects.active=children[0];bpy.ops.object.join();cab=bpy.context.view_layer.objects.active
bpy.context.view_layer.update();world=[cab.matrix_world@v.co for v in cab.data.vertices];anchor=Vector((group['x']/1000,-group['z']/1000,0))
cab.matrix_world=Matrix.Identity(4);cab.location=anchor
for vertex,point in zip(cab.data.vertices,world):vertex.co=point-anchor
bm=bmesh.new();bm.from_mesh(cab.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(cab.data);bm.free()
cab.name='tv-high | '+group['name']
for key,value in dict(home_design_role='furniture',source_id='tv-high',display_name=group['name'],zone=group['zone'],scheme=group['scheme'],part_count=len(parts),
    import_x_mm=group['x'],import_z_mm=group['z'],movement_step_mm=100,dimensions_mm=[4500,400,2750],dimension_note=group['detail'],
    part_source_mm=json.dumps(parts,ensure_ascii=False),style_revision='modern-japanese-v04',base_height_mm=0,
    cabinet_selection='C amended by homeowner: milk yellow lower, cream upper, walnut niche',ceiling_gap_mm=0,niche_bottom_mm=1200,niche_top_mm=1400).items():cab[key]=value
cab.lock_location[2]=True;cab.lock_rotation[0]=True;cab.lock_rotation[1]=True;cab.hide_select=False

# Archive the superseded glass and cosmetic thirds. Original source files stay intact.
archive=bpy.data.collections.new('v07 阳台窗旧构件 · 隐藏参考');scene.collection.children.link(archive)
old=[]
for ob in list(scene.objects):
    if (ob.get('home_design_role')=='glass' and ob.get('source_id')=='outer-top-glass-0') or ob.name.startswith(('表现窗框 outer-top-glass-0','阳台细窗梃')):
        old.append(ob.name)
        for coll in list(ob.users_collection):coll.objects.unlink(ob)
        archive.objects.link(ob);ob['home_design_role']='baseline_window_reference';ob.hide_render=True;ob.hide_set(True);ob.hide_select=True
assert len(old)>=3,old
archive.hide_render=True;archive.hide_viewport=True
window=bpy.data.collections.new('v08 阳台窗 · 中央整玻与两侧上开扇');scene.collection.children.link(window)
glassmat=bpy.data.materials['R01 · 实体透明玻璃'];framemat=bpy.data.materials['R01 · 窗框暖灰铝材']
screen=bpy.data.materials.new('V08 · 纱网外观占位');screen.use_nodes=True
nodes=screen.node_tree.nodes;links=screen.node_tree.links;nodes.clear()
out=nodes.new('ShaderNodeOutputMaterial');mix=nodes.new('ShaderNodeMixShader');transparent=nodes.new('ShaderNodeBsdfTransparent');wire=nodes.new('ShaderNodeBsdfDiffuse');wire.inputs['Color'].default_value=(.16,.17,.15,1);wire.inputs['Roughness'].default_value=.6
coord=nodes.new('ShaderNodeTexCoord');waves=[]
for axis in ['X','Z']:
    wave=nodes.new('ShaderNodeTexWave');wave.wave_type='BANDS';wave.bands_direction=axis;wave.inputs['Scale'].default_value=200;wave.inputs['Distortion'].default_value=0;wave.inputs['Detail'].default_value=0
    links.new(coord.outputs['Object'],wave.inputs['Vector']);thin=nodes.new('ShaderNodeMath');thin.operation='LESS_THAN';thin.inputs[1].default_value=.035;links.new(wave.outputs['Fac'],thin.inputs[0]);waves.append(thin)
grid=nodes.new('ShaderNodeMath');grid.operation='MAXIMUM';links.new(waves[0].outputs[0],grid.inputs[0]);links.new(waves[1].outputs[0],grid.inputs[1]);links.new(grid.outputs[0],mix.inputs[0]);links.new(transparent.outputs[0],mix.inputs[1]);links.new(wire.outputs[0],mix.inputs[2]);links.new(mix.outputs[0],out.inputs[0])
screen['status']='Reference-hatch interpretation only; mesh product and opening direction unverified'
for p in data['glass']:
    if p.get('assembly')!='balcony-window':continue
    ob=make_part(p,window,glassmat);ob['home_design_role']='glass';ob['window_role']=p['windowRole'];ob['assembly']='balcony-window';ob.hide_select=True
for p in data['windowParts']:
    ob=make_part(p,window,screen if p['kind']=='window-screen' else framemat,.0005 if p['kind']=='window-frame' else 0)
    ob['home_design_role']='insect_screen_concept' if p['kind']=='window-screen' else 'window_frame';ob['assembly']='balcony-window';ob.hide_select=True

bpy.context.view_layer.update()
ff={o['source_id']:o for o in scene.objects if o.get('home_design_role')=='furniture'}
audits=[]
for g in data['furnitureObjects']:
    ob=ff[g['id']];pts=[ob.matrix_world@v.co for v in ob.data.vertices]
    lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)];b=g['meshBoundsMm']
    expected=[b['x']/1000,-(b['z']+b['d'])/1000,b['y']/1000,(b['x']+b['w'])/1000,-b['z']/1000,(b['y']+b['h'])/1000]
    error=max(abs(a-b) for a,b in zip(lo+hi,expected))*1000;assert error<.03,(g['id'],error)
    assert abs(ob.location.x*1000-g['x'])<.01 and abs(-ob.location.y*1000-g['z'])<.01
    audits.append(dict(id=g['id'],position_mm=[g['x'],g['z']],dimensions_mm=list(ob['dimensions_mm']),mesh_bounds_error_mm=error))
assert all((tuple(ff[i].location),tuple(ff[i].rotation_euler),hashlib.sha256(str([tuple(v.co) for v in ff[i].data.vertices]).encode()).hexdigest())==value for i,value in others.items())
assert sum(o.get('home_design_role')=='wall' for o in scene.objects)==60
assert sum(o.get('home_design_role')=='glass' for o in scene.objects)==12
assert len([o for o in scene.objects if o.get('assembly')=='balcony-window'])==27

scene.name='v08 · 奶黄通顶长柜与阳台整玻'
scene['home_design_revision']=8;scene['home_design_geometry_sha256']=style['geometry_sha256'];scene['home_design_style_sha256']=hashlib.sha256(style_raw).hexdigest()
scene['home_design_style_revision']='modern-japanese-v04';scene['home_design_style_file']='05_style/modern-japanese-v04.json'
scene['home_design_assumptions']=json.dumps(data['assumptions'],ensure_ascii=False)
scene['home_design_balcony_window']=json.dumps(data['features']['balconyWindow'],ensure_ascii=False)
scene['home_design_cabinet_selection']='C / lower navy changed to soft milk yellow #F1DDAE / cream upper / walnut niche / full ceiling height'
scene['home_design_selected_schemes']=scene['home_design_selected_schemes']+' / 奶黄下柜奶油白上柜通顶 / 阳台中央整玻两侧上开下固'

sys.path.insert(0,str(ROOT/'tools'));import home_design_move
for cls in reversed(home_design_move.CLASSES):
    registered=cls.bl_rna_get_subclass_py(cls.__name__,None)
    if registered:
        try:bpy.utils.unregister_class(registered)
        except RuntimeError:pass
try:home_design_move.register()
except ValueError:pass
movement=[]
for gid in ['tv-high','washer']:
    bpy.ops.object.select_all(action='DESELECT');ob=ff[gid];ob.select_set(True);bpy.context.view_layer.objects.active=ob
    starts={i:o.location.copy() for i,o in ff.items()}
    bpy.ops.home_design.move(axis='X',direction=1);assert abs(ob.location.x-starts[gid].x-.1)<1e-6
    if gid=='washer':assert abs(ff['dryer'].location.x-starts['dryer'].x-.1)<1e-6
    bpy.ops.home_design.move(axis='X',direction=-1);assert all((o.location-starts[i]).length<1e-6 for i,o in ff.items());movement.append(gid)
bpy.ops.home_design.export_layout()

camera_coll=bpy.data.collections['10 写实表现 · 人眼视角']
def camera(name,position,lookat,lens):
    cam=bpy.data.cameras.new(name);cam.type='PERSP';cam.lens=lens;cam.sensor_width=36;cam.clip_start=.02
    ob=bpy.data.objects.new(name,cam);camera_coll.objects.link(ob);ob.location=position;ob.rotation_euler=(Vector(lookat)-ob.location).to_track_quat('-Z','Y').to_euler();return ob
cabcam=camera('v08 · 奶黄与奶油白通顶长柜',(2.85,-7.2,1.52),(.18,-7.25,1.385),18)
camera('v08 · 阳台中央整块玻璃',(3.6905,-4.75,1.50),(3.6905,.12,1.135),18)
scene.camera=cabcam;scene.cycles.samples=96;scene.cycles.use_denoising=True
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for dev in prefs.devices:dev.use=dev.type!='CPU'
scene.cycles.device='GPU';scene.render.resolution_x=1800;scene.render.resolution_y=1200;scene.render.resolution_percentage=100;scene.view_settings.exposure=.2
bpy.ops.object.select_all(action='DESELECT');cab.select_set(True);bpy.context.view_layer.objects.active=cab
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(DEST))
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==baseline_file_sha
report=dict(model=str(DEST),revision=8,geometry_sha256=style['geometry_sha256'],style_sha256=scene['home_design_style_sha256'],furniture=audits,
    other_20_meshes_positions_unchanged=True,all_21_positions_preserved=True,source_walls_preserved=60,glass=12,new_window_parts=22,
    superseded_window_parts_archived=old,cabinet=dict(option='C amended',lower_srgb='#F1DDAE',upper='cream',niche='walnut',height_mm=2750,ceiling_gap_mm=0,niche_bottom_mm=1200,niche_top_mm=1400),
    window=data['features']['balconyWindow'],movement_100mm=movement,linked_laundry_movement=True)
(ROOT/'logs/model-v08-build.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('MODEL_V08_BUILT '+json.dumps(dict(furniture=21,glass=12,window_parts=22,cabinet_top_mm=2750,positions_unchanged=True)))
