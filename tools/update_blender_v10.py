"""Public finish overlay and switchable lighting; furniture and structural sources stay intact."""
from pathlib import Path
from mathutils import Vector
import bpy,json,hashlib,ast,math,sys
ROOT=Path(r'D:\AI-Yang.cn\HomeDesign');SOURCE=ROOT/'06_blender/home-main-v09.blend';DEST=ROOT/'06_blender/home-main-v10.blend'
assert Path(bpy.data.filepath).resolve()==SOURCE.resolve() and (not DEST.exists() or '--replace-draft' in sys.argv)
raw=(ROOT/'02_geometry/geometry-master-v10.json').read_bytes();d=json.loads(raw);style_raw=(ROOT/'05_style/modern-japanese-v06.json').read_bytes();s=json.loads(style_raw)
assert s['geometry_sha256']==hashlib.sha256(raw).hexdigest()
scene=bpy.context.scene;assert scene['home_design_revision']==9
furn={o['source_id']:o for o in scene.objects if o.get('home_design_role')=='furniture'}
before={i:(tuple(o.location),tuple(o.rotation_euler),hashlib.sha256(str([tuple(v.co) for v in o.data.vertices]).encode()).hexdigest()) for i,o in furn.items()}
def rgb(code):
    c=[int(code[i:i+2],16)/255 for i in [1,3,5]]
    return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in c)+(1,)
def simple(name,code,rough=.75):
    m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=rgb(code);p.inputs['Roughness'].default_value=rough;m['concept_srgb']=code;return m
wall=simple('V10 · 干净暖白平整哑光','#F3F1EA',.86);ceiling=simple('V10 · 暖白顶面','#F6F4EF',.85)
shadow=simple('V10 · 极窄阴缝','#666A62',.8);skirting=simple('V10 · 同墙色内嵌踢脚','#EEEDE7',.72);metal=simple('V10 · 暖石墨金属','#424743',.56)
oak=bpy.data.materials['R01 · 浅橡木细纹'].copy();oak.name='V10 · 减黄浅橡木'
for node in oak.node_tree.nodes:
    if node.type=='VALTORGB':node.color_ramp.elements[0].color=rgb('#BDB19B');node.color_ramp.elements[-1].color=rgb('#E3D8C5')
oak['concept_srgb']='#D6C6AC'
fabric=bpy.data.materials['R01 · 米灰亚麻混纺'].copy();fabric.name='V10 · 细织棉麻感米灰';fabric.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=rgb('#D8D5CC')
fabric.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.78
for node in fabric.node_tree.nodes:
    if node.type=='TEX_NOISE':node.inputs['Scale'].default_value=650;node.inputs['Detail'].default_value=2
    if node.type=='BUMP':node.inputs['Strength'].default_value=.10;node.inputs['Distance'].default_value=.0003
body=bpy.data.materials['R01 · 沙发框体织物'].copy();body.name='V10 · 沙发浅灰支撑织物';body.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=rgb('#BEBDB5')
replace={'R01 · 浅橡木细纹':oak,'R01 · 米灰亚麻混纺':fabric,'R01 · 沙发框体织物':body,'R01 · 深灰细砂金属':metal}
for ob in furn.values():
    for slot in ob.material_slots:
        if slot.material and slot.material.name in replace:slot.material=replace[slot.material.name]
for ob in scene.objects:
    if ob.get('home_design_role') in ['window_frame','door_frame']:
        for slot in ob.material_slots:slot.material=metal
poly=d['features']['publicRefinement']['publicFloorPolygon']
def inside(x,z):
    result=False
    for a,b in zip(poly,poly[1:]+poly[:1]):
        if (a[1]>z)!=(b[1]>z) and x<(b[0]-a[0])*(z-a[1])/(b[1]-a[1])+a[0]:result=not result
    return result or (0<=x<=1271 and 9635<=z<=11168)
for ob in scene.objects:
    if ob.get('home_design_role')=='wall_visual_union':
        ob.data.materials.append(wall);index=len(ob.data.materials)-1
        for face in ob.data.polygons:
            point=ob.matrix_world@(face.center+face.normal*.02)
            if inside(point.x*1000,-point.y*1000):face.material_index=index
    elif ob.get('home_design_role')=='wall_finish_proposal':
        ob.data.materials.clear();ob.data.materials.append(wall)
coll=bpy.data.collections.new('v10 公共区材质与同面收口 · 概念');scene.collection.children.link(coll)
floor=bpy.data.materials['R01 · 浅木地板'].copy();floor.name='V10 · 浅木地面外观占位'
for node in floor.node_tree.nodes:
    if node.type=='VALTORGB':node.color_ramp.elements[0].color=rgb('#C7BEAC');node.color_ramp.elements[-1].color=rgb('#E5DECE')
def surface(name,points,level,mat,up):
    verts=[(x/1000,-z/1000,level) for x,z in points];indices=list(range(len(verts)))
    if up:indices.reverse()
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],[indices]);mesh.materials.append(mat);ob=bpy.data.objects.new(name,mesh);coll.objects.link(ob);ob['home_design_role']='public_finish_overlay';ob.hide_select=True;return ob
surface('v10 公共区浅木外观 · 地面产品待选',poly,.0012,floor,True)
surface('v10 公共区暖白顶面',poly,2.7498,ceiling,False)
entrypoly=[[0,9635],[1271,9635],[1271,11168],[0,11168]];surface('v10 入户地面外观',entrypoly,.0012,floor,True)
tree=ast.parse((ROOT/'tools/render_modern_japanese_v02.py').read_text(encoding='utf-8'));node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='profile_mesh')
exec(compile(ast.Module(body=[node],type_ignores=[]),'profile_mesh','exec'))
mats={'wall-finish':wall,'shadow':shadow,'skirting':skirting,'metal':metal}
for p in d['detailParts']:
    mesh=profile_mesh(p['id'],p['w']/1000,p['d']/1000,p['h']/1000,[0]*4)
    for face in mesh.polygons:face.use_smooth=False
    mesh.materials.append(mats[p['material']]);ob=bpy.data.objects.new(p['id'],mesh);coll.objects.link(ob);ob.location=(p['x']/1000,-(p['z']+p['d'])/1000,p['y']/1000)
    ob['source_id']=p['id'];ob['home_design_role']='public_finish_detail';ob['source_mm']=json.dumps(p,ensure_ascii=False);ob.hide_select=True
    if p['id'].endswith('-handle'):
        bevel=ob.modifiers.new('触边圆润','BEVEL');bevel.width=.003;bevel.segments=3;bevel.harden_normals=True;ob.modifiers.new('面法线','WEIGHTED_NORMAL')

# Rendering controls express scenes, not an electrical load or a photometric calculation.
scene['lighting_scene']=1;scene.id_properties_ui('lighting_scene').update(min=0,max=2,description='0日间 / 1氛围晚间 / 2明亮清洁；灯具与照度待深化')
def driver(owner,path,values):
    dr=owner.driver_add(path).driver;dr.type='SCRIPTED';var=dr.variables.new();var.name='mode';var.type='SINGLE_PROP';var.targets[0].id_type='SCENE';var.targets[0].id=scene;var.targets[0].data_path='["lighting_scene"]'
    dr.expression=f'{values[0]} if mode < 0.5 else ({values[1]} if mode < 1.5 else {values[2]})'
old_lights=[ob for ob in scene.objects if ob.type=='LIGHT']
for ob in old_lights:
    original=ob.data.energy
    if ob.location.z>3 or ob.name in ['阳台整面日光','入户侧开口日光']:
        if ob.name=='阳台整面日光':ob.data.color=(.96,.98,1)
        driver(ob.data,'energy',(original,original*.003,original*.003))
    elif '置物格' in ob.name:
        ob.data.color=(1,.92,.79);driver(ob.data,'energy',(.8,1.7,2))
    else:
        ob.data.color=(1,.94,.85);driver(ob.data,'energy',(5,0,original))
lightcoll=bpy.data.collections.new('v10 分层照明 · 三场景');scene.collection.children.link(lightcoll)
records=[]
def light(name,position,target,energies,size,shape='RECTANGLE',parent=None,cct=3000):
    data=bpy.data.lights.new(name,'AREA');data.shape=shape;data.size=size[0]
    if shape=='RECTANGLE':data.size_y=size[1]
    data.color=(1,.92,.80) if cct<=3000 else (1,.96,.90);data['target_cct_kelvin']=cct
    ob=bpy.data.objects.new(name,data);lightcoll.objects.link(ob);ob.location=position;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
    if parent:
        bpy.context.view_layer.update();world=ob.matrix_world.copy();ob.parent=furn[parent];ob.matrix_world=world
    driver(data,'energy',energies);ob['home_design_role']='lighting_proposal';ob['lighting_values_status']='relative Cycles energy only; no fixture selected'
    records.append(dict(name=name,position=list(position),target=list(target),relative_energies=list(energies),cct_intent=cct,parent_furniture=parent));return ob
light('v10 客厅顶面反射光',(7.045,-2.975,2.715),(7.045,-2.975,2.75),(12,90,100),(.08,2.6))
light('v10 通道顶面反射光',(6.15,-5.275,2.715),(6.15,-5.275,2.75),(12,100,120),(5,.08))
for yy in [.79,1.59,2.37]:light('v10 书柜层板光 '+str(yy),(6.89,-2.976,yy),(7.13,-2.976,yy-.12),(.5,3,4),(.05,1.9),parent='bookcase')
light('v10 电视背景柔光',(.022,-3.4,1.1),(-.03,-3.4,1.1),(.2,.7,.7),(.8,1.6),parent='television')
light('v10 桌灯工作光',(5.47,-3.27,1.077),(5.65,-3.25,.75),(1.5,7,8),(.13,.13),parent='double-desk',cct=3500)
light('v10 餐桌任务光位待选灯具',(2.682,-8.1,2.68),(2.682,-8.1,.75),(4,24,35),(.85,.35),cct=3500)
light('v10 入户低位导向光',(.91,-10.0,.12),(.35,-10.0,.0),(.1,.7,.8),(.03,.6),parent='entry-shoe-cabinet',cct=2700)
if scene.world and scene.world.use_nodes:
    bg=next((n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND'),None)
    if bg:driver(bg.inputs['Strength'],'default_value',(.45,.025,.025))
driver(scene.view_settings,'exposure',(1.05,.4,.65))
scene.update_tag();scene.frame_set(scene.frame_current);bpy.context.view_layer.update()
assert all((tuple(furn[i].location),tuple(furn[i].rotation_euler),hashlib.sha256(str([tuple(v.co) for v in furn[i].data.vertices]).encode()).hexdigest())==v for i,v in before.items())
assert len(furn)==21 and sum(o.get('home_design_role')=='wall' for o in scene.objects)==60
assert sum(o.get('home_design_role')=='glass' for o in scene.objects)==12
scene.name='v10 · 暖白浅木与氛围照明';scene['home_design_revision']=10;scene['home_design_geometry_sha256']=s['geometry_sha256']
scene['home_design_style_revision']='modern-japanese-v06';scene['home_design_style_file']='05_style/modern-japanese-v06.json';scene['home_design_style_sha256']=hashlib.sha256(style_raw).hexdigest()
scene['home_design_assumptions']=json.dumps(d['assumptions'],ensure_ascii=False);scene['home_design_public_details']=json.dumps(d['features']['publicRefinement'],ensure_ascii=False)
scene['home_design_budget_rmb']=100000;scene['home_design_budget_scope']='公共区硬装含柜，不含家具灯具；分配目标不是报价'
scene['home_design_lighting_records']=json.dumps(records,ensure_ascii=False)
scene.camera=bpy.data.objects['v07 · 电视右侧绿植']
scene.cycles.samples=96;scene.cycles.use_denoising=True;prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for dev in prefs.devices:dev.use=dev.type!='CPU'
scene.cycles.device='GPU';scene.render.resolution_x=1800;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(DEST))
report=dict(revision=10,geometry_sha256=s['geometry_sha256'],style_sha256=scene['home_design_style_sha256'],all_21_furniture_meshes_and_transforms_unchanged=True,
    furniture_count=21,wall_sources=60,window_glass=12,kitchen_door_glass=3,detail_parts=len(d['detailParts']),lighting=records,lighting_scenes=3,
    private_room_boundaries_unchanged=True,base_model_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),default_lighting_scene='evening')
(ROOT/'logs/model-v10-build.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('MODEL_V10_BUILT '+json.dumps(dict(furniture=21,detail_parts=len(d['detailParts']),light_groups=len(records))))
