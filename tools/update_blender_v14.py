"""Continue v13, preserving all 23 public furniture meshes and positions."""
from pathlib import Path
import ast, bpy, bmesh, hashlib, json, math, sys
from mathutils import Vector, Matrix
ROOT=Path(r'D:\AI-Yang.cn\HomeDesign')
BASE=ROOT/'06_blender/home-main-v13.blend'; DEST=ROOT/'06_blender/home-main-v14.blend'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert Path(bpy.data.filepath).resolve()==BASE.resolve()
assert not DEST.exists() or '--replace-draft' in sys.argv
G=ROOT/'02_geometry/geometry-master-v14.json'; S=ROOT/'05_style/modern-japanese-v10.json'
d=json.loads(G.read_text(encoding='utf-8')); style=json.loads(S.read_text(encoding='utf-8'))
assert sha(G)==style['geometry_sha256']
scene=bpy.context.scene; assert scene['home_design_revision']==13
existing={o['source_id']:o for o in scene.objects if o.get('home_design_role')=='furniture'}
assert len(existing)==23
def mesh_digest(o):return hashlib.sha256(str([tuple(v.co) for v in o.data.vertices]).encode()).hexdigest()
before={k:dict(position=list(o.location),rotation=list(o.rotation_euler),mesh=mesh_digest(o)) for k,o in existing.items()}
for script,name in [('render_modern_japanese_v02.py','profile_mesh'),('update_blender_v07.py','mesh_part')]:
    tree=ast.parse((ROOT/'tools'/script).read_text(encoding='utf-8'));node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name);exec(compile(ast.Module(body=[node],type_ignores=[]),name,'exec'))
mats={'wood':bpy.data.materials['V10 · 减黄浅橡木'],'fabric':bpy.data.materials['V10 · 细织棉麻感米灰'],'wall-finish':bpy.data.materials['V10 · 干净暖白平整哑光'],'metal':bpy.data.materials['V10 · 暖石墨金属'],'sage':bpy.data.materials['J02 · 低饱和苔绿色织物']}
for key in ['cabinet','shadow','stone','ceramic','mirror','bath-tile','shower-tile','bath-glass','basin-inset']:
    rec=d['furnitureMaterials'][key];m=bpy.data.materials.new('V14 · '+key);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=rec['color'];p.inputs['Roughness'].default_value=rec['roughness']
    if key=='mirror':p.inputs['Metallic'].default_value=1
    if key=='bath-glass':p.inputs['Transmission Weight'].default_value=1;p.inputs['IOR'].default_value=1.45
    mats[key]=m
target=bpy.data.collections.new('v14 主卧与合并主卫 · 条件性概念');scene.collection.children.link(target)
# Remove retired source objects and the old display union. Historical v13 retains the exact originals.
retired={p['id'] for p in d['retiredWallsV14']}|{p['id'] for p in d['retiredDetailsV14']}
for ob in list(scene.objects):
    if ob.get('source_id') in retired or ob.get('home_design_role')=='wall_visual_union':bpy.data.objects.remove(ob,do_unlink=True)
for q in d['walls']:
    if not q['id'].startswith('v14-'):continue
    ob=mesh_part(dict(q,material='wall-finish',shape='box'));ob['home_design_role']='wall';ob['source_id']=q['id'];ob.hide_select=True;ob.hide_render=True;ob.hide_set(True)
# Rebuild the full-height union using the reviewed box subtraction algorithm.
tree=ast.parse((ROOT/'tools/render_modern_japanese_v02.py').read_text(encoding='utf-8'))
node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='rect_subtract');exec(compile(ast.Module(body=[node],type_ignores=[]),'rect_subtract','exec'))
boxes=[([r['x']/1000,-(r['z']+r['d'])/1000,r['y']/1000],[(r['x']+r['w'])/1000,-r['z']/1000,(r['y']+r['h'])/1000]) for r in d['walls']]
vertices=[];faces=[]
for i,(lo,hi) in enumerate(boxes):
    if d['walls'][i]['id'] in style['designer_decisions']['wall_finish_profiles_mm']:continue
    for axis in range(3):
        u,v=[k for k in range(3) if k!=axis]
        for positive in [False,True]:
            plane=hi[axis] if positive else lo[axis];rectangles=[(lo[u],lo[v],hi[u],hi[v])]
            for j,(ol,oh) in enumerate(boxes):
                if i==j:continue
                hidden=(ol[axis]<=plane+1e-8 and oh[axis]>plane+1e-8) if positive else (ol[axis]<plane-1e-8 and oh[axis]>=plane-1e-8)
                duplicate=(abs(oh[axis]-plane)<1e-8 and ol[axis]<plane-1e-8 and j<i) if positive else (abs(ol[axis]-plane)<1e-8 and oh[axis]>plane+1e-8 and j<i)
                if hidden or duplicate:rectangles=[rr for r in rectangles for rr in rect_subtract(r,(ol[u],ol[v],oh[u],oh[v]))]
            for a,b,c,e in rectangles:
                quad=[]
                for uu,vv in [(a,b),(c,b),(c,e),(a,e)]:
                    point=[0.]*3;point[axis]=plane;point[u]=uu;point[v]=vv;quad.append(tuple(point))
                normal=(Vector(quad[1])-Vector(quad[0])).cross(Vector(quad[2])-Vector(quad[0]))
                if (normal[axis]>0)!=positive:quad.reverse()
                offset=len(vertices);vertices.extend(quad);faces.append(tuple(range(offset,offset+4)))
mesh=bpy.data.meshes.new('v14完整墙并集');mesh.from_pydata(vertices,[],faces);mesh.materials.append(mats['wall-finish']);mesh.update();union=bpy.data.objects.new('v14 墙体显示并集 · 完整高度与开口',mesh);target.objects.link(union);union['home_design_role']='wall_visual_union';union['source_wall_count']=len(d['walls']);union.hide_select=True

new_ids=[]
for group in d['furnitureObjects']:
    gid=group['id']
    if gid in existing:continue
    pp=[p for p in d['furniture'] if p['parent']==gid];children=[mesh_part(p) for p in pp];bpy.ops.object.select_all(action='DESELECT')
    for ob in children:
        ob.select_set(True);bpy.context.view_layer.objects.active=ob
        for mod in list(ob.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.context.view_layer.objects.active=children[0];bpy.ops.object.join();ob=bpy.context.view_layer.objects.active;bpy.context.view_layer.update()
    world=[ob.matrix_world@v.co for v in ob.data.vertices];anchor=Vector((group['x']/1000,-group['z']/1000,0));ob.matrix_world=Matrix.Identity(4);ob.location=anchor
    for vertex,point in zip(ob.data.vertices,world):vertex.co=point-anchor
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
    ob.name=gid+' | '+group['name']
    for key,value in dict(home_design_role='furniture',source_id=gid,display_name=group['name'],zone=group['zone'],scheme=group['scheme'],part_count=len(pp),import_x_mm=group['x'],import_z_mm=group['z'],movement_step_mm=100,dimensions_mm=[group['dimensionsMm'][k] for k in ['length','width','height']],dimension_note=group['detail'],part_source_mm=json.dumps(pp,ensure_ascii=False),style_revision='modern-japanese-v10',base_height_mm=0).items():ob[key]=value
    ob.lock_location[2]=True;ob.lock_rotation[0]=True;ob.lock_rotation[1]=True;ob.hide_select=False;new_ids.append(gid)

control=bpy.data.objects.new('主卫侧门 · 向私用门厅开启',None);target.objects.link(control);control.location=(9.203,-4.156,0);control['home_design_role']='bath_door_control';control['open_ratio']=0.;control.id_properties_ui('open_ratio').update(min=0.,max=1.,description='向私用门厅开0–90度；暂拟门洞800、通行720，实际系统未选')
screen=bpy.data.objects.new('主卫淋浴隔断 · 移门',None);target.objects.link(screen);screen['home_design_role']='shower_control';screen['open_ratio']=0.;screen.id_properties_ui('open_ratio').update(min=0.,max=1.,description='概念滑移700毫米；型材及净开口待实样')
def drive(ob,path,index,ctrl,expr):
    dr=ob.driver_add(path,index).driver;dr.type='SCRIPTED';var=dr.variables.new();var.name='opened';var.type='SINGLE_PROP';var.targets[0].id=ctrl;var.targets[0].data_path='["open_ratio"]';dr.expression=expr
drive(control,'rotation_euler',2,control,'-opened*pi/2')
for p in d['bathParts']:
    ob=mesh_part(p);ob['source_id']=p['id'];ob['home_design_role']='master_suite_detail';ob.hide_select=True
    if p.get('swingLeaf'):
        bpy.context.view_layer.update();world=ob.matrix_world.copy();ob.parent=control;ob.matrix_world=world
    if p.get('slidingPanel'):drive(ob,'location',0,screen,str(p['x']/1000)+'-opened*.700')
# Dedicated task/general lighting for the previously empty room, linked to the existing scene control.
def light(name,pos,aim,energies,size):
    data=bpy.data.lights.new(name,'AREA');data.shape='RECTANGLE';data.size=size[0];data.size_y=size[1];data.color=(1,.94,.85)
    ob=bpy.data.objects.new(name,data);target.objects.link(ob);ob.location=pos;ob.rotation_euler=(Vector(aim)-ob.location).to_track_quat('-Z','Y').to_euler();ob['home_design_role']='master_suite_lighting'
    dr=data.driver_add('energy').driver;dr.type='SCRIPTED';var=dr.variables.new();var.name='mode';var.type='SINGLE_PROP';var.targets[0].id_type='SCENE';var.targets[0].id=scene;var.targets[0].data_path='["lighting_scene"]';dr.expression=f'{energies[3]} if mode>2.5 else ({energies[0]} if mode<.5 else ({energies[1]} if mode<1.5 else {energies[2]}))'
light('v14 主卫一般光',(10.05,-5.5,2.70),(10.05,-5.5,.6),(24,45,70,4),(.8,1.7))
light('v14 主卫镜前柔光',(10.68,-4.6,2.2),(10.1,-4.6,1.5),(8,12,15,2),(.04,.7))
light('v14 主卧一般光',(8.6,-2.7,2.70),(9,-2.7,.6),(18,25,60,1),(1.2,1.5))
def camera(name,pos,look,lens=24,ortho=None):
    data=bpy.data.cameras.new(name);data.lens=lens;data.clip_start=.02
    if ortho:data.type='ORTHO';data.ortho_scale=ortho
    ob=bpy.data.objects.new(name,data);target.objects.link(ob);ob.location=pos;ob.rotation_euler=(Vector(look)-ob.location).to_track_quat('-Z','Y').to_euler();ob['home_design_role']='master_suite_camera'
camera('v14 · 主卧主卫剖切观察',(14,-9.5,12),(9,-4,.3),ortho=7.9)
camera('v14 · 主卫由外向内',(9.73,-4.18,1.65),(10.0,-6.82,1.15),17)
camera('v14 · 主卧',(8.18,-4.52,1.62),(9.25,-2.35,.9),20)
for k,rec in before.items():
    ob=existing[k];assert list(ob.location)==rec['position'] and list(ob.rotation_euler)==rec['rotation'] and mesh_digest(ob)==rec['mesh']
ff={o['source_id']:o for o in scene.objects if o.get('home_design_role')=='furniture'};assert len(ff)==27
for group in d['furnitureObjects']:
    ob=ff[group['id']];assert abs(ob.location.x*1000-group['x'])<.01 and abs(-ob.location.y*1000-group['z'])<.01
    points=[ob.matrix_world@v.co for v in ob.data.vertices];lo=[min(p[i] for p in points) for i in range(3)];hi=[max(p[i] for p in points) for i in range(3)];b=group['meshBoundsMm'];expected=[b['x']/1000,-(b['z']+b['d'])/1000,b['y']/1000,(b['x']+b['w'])/1000,-b['z']/1000,(b['y']+b['h'])/1000];assert max(abs(a-c) for a,c in zip(lo+hi,expected))<.00005,(group['id'],lo,hi,expected)
scene.name='v14 · 主卧主卫扩展概念 · 待核现场';scene['home_design_revision']=14;scene['home_design_geometry_sha256']=sha(G);scene['home_design_style_sha256']=sha(S);scene['home_design_style_revision']='modern-japanese-v10';scene['home_design_geometry_path']=G.as_posix();scene['home_design_style_path']=S.as_posix();scene['home_design_geometry_file']='02_geometry/geometry-master-v14.json';scene['home_design_style_file']='05_style/modern-japanese-v10.json';scene['home_design_master_suite']=json.dumps(d['features']['masterSuite'],ensure_ascii=False);scene['construction_approval_status']='concept only; wet-area extension, structure, drains and dimensions unverified';scene['home_design_assumptions']=json.dumps(d['assumptions'],ensure_ascii=False)
for name,path in [('geometry-master-v14.json',G),('modern-japanese-v10.json',S)]:t=bpy.data.texts.new(name);t.write(path.read_text(encoding='utf-8'))
scene['lighting_scene']=0;scene.update_tag();scene.frame_set(scene.frame_current);bpy.context.view_layer.update();scene.camera=bpy.data.objects['v14 · 主卫由外向内'];scene.cycles.samples=128;scene.render.resolution_x=1800;scene.render.resolution_y=1200
bpy.ops.object.select_all(action='DESELECT');ff['master-bed'].select_set(True);bpy.context.view_layer.objects.active=ff['master-bed'];bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(DEST))
report=dict(revision=14,base_sha256=sha(BASE),geometry_sha256=sha(G),style_sha256=sha(S),public_furniture_meshes_and_positions_preserved=23,new_furniture=new_ids,source_walls=sum(o.get('home_design_role')=='wall' for o in scene.objects),window_glass=sum(o.get('home_design_role')=='glass' for o in scene.objects),bath_details=len(d['bathParts']),retired_walls=list(retired),source_units='mm',blender_units='m',mapping='(x,-z,height)/1000',construction_status=scene['construction_approval_status'])
assert report['source_walls']==62 and report['window_glass']==12
(ROOT/'logs/model-v14-build.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('V14_MODEL_SAVED',len(ff))
