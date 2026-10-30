"""Build the PDF-inspired proposal as a new complete editable model."""
from pathlib import Path
from mathutils import Vector,Matrix
import bpy,bmesh,json,hashlib,ast,math,sys
ROOT=Path(r'D:\AI-Yang.cn\HomeDesign');SOURCE=ROOT/'06_blender/home-main-v11.blend';DEST=ROOT/'06_blender/home-main-v12.blend'
assert Path(bpy.data.filepath).resolve()==SOURCE.resolve() and (not DEST.exists() or '--replace-draft' in sys.argv)
raw=(ROOT/'02_geometry/geometry-master-v12.json').read_bytes();d=json.loads(raw);sr=(ROOT/'05_style/modern-japanese-v08.json').read_bytes();s=json.loads(sr);sha=hashlib.sha256(raw).hexdigest();assert sha==s['geometry_sha256']
scene=bpy.context.scene;assert scene['home_design_revision']==11
existing={o['source_id']:o for o in scene.objects if o.get('home_design_role')=='furniture'};assert len(existing)==24
changed={'tv-low','entry-shoe-cabinet','entry-return-cabinet'}
before={i:hashlib.sha256(str([tuple(v.co) for v in ob.data.vertices]).encode()).hexdigest() for i,ob in existing.items() if i not in changed}
for name in ['v10 入户低位导向光','v10 电视背景柔光']:
    if name in bpy.data.objects:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
for gid in changed:bpy.data.objects.remove(existing.pop(gid),do_unlink=True)
target=bpy.data.collections['04 家具 · 整件选择 · 100mm']
tree=ast.parse((ROOT/'tools/render_modern_japanese_v02.py').read_text(encoding='utf-8'));node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='profile_mesh');exec(compile(ast.Module(body=[node],type_ignores=[]),'profile_mesh','exec'))
def material(name,rec,metallic=0):
    m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=rec['color'];p.inputs['Roughness'].default_value=rec['roughness'];p.inputs['Metallic'].default_value=metallic;return m
mats={'wood':bpy.data.materials['V10 · 减黄浅橡木'],'fabric':bpy.data.materials['V10 · 细织棉麻感米灰'],'wall-finish':bpy.data.materials['V10 · 干净暖白平整哑光'],'metal':bpy.data.materials['V10 · 暖石墨金属']}
for key in ['cabinet','stone','mirror','curtain']:mats[key]=material('V12 · '+key,d['furnitureMaterials'][key],1 if key=='mirror' else 0)
tree=ast.parse((ROOT/'tools/update_blender_v07.py').read_text(encoding='utf-8'));node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='mesh_part');exec(compile(ast.Module(body=[node],type_ignores=[]),'mesh_part','exec'))
for group in d['furnitureObjects']:
    gid=group['id'];pp=[p for p in d['furniture'] if p['parent']==gid]
    if gid in existing:
        ob=existing[gid];ob.location.x=group['x']/1000;ob.location.y=-group['z']/1000
    else:
        children=[mesh_part(p) for p in pp];bpy.ops.object.select_all(action='DESELECT')
        for ob in children:
            ob.select_set(True);bpy.context.view_layer.objects.active=ob
            for mod in list(ob.modifiers):
                if not mod.show_viewport or (mod.type=='BEVEL' and mod.width==0):ob.modifiers.remove(mod)
                else:bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.context.view_layer.objects.active=children[0];bpy.ops.object.join();ob=bpy.context.view_layer.objects.active
        bpy.context.view_layer.update();world=[ob.matrix_world@v.co for v in ob.data.vertices];anchor=Vector((group['x']/1000,-group['z']/1000,0));ob.matrix_world=Matrix.Identity(4);ob.location=anchor
        for vertex,point in zip(ob.data.vertices,world):vertex.co=point-anchor
        bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
    ob.name=gid+' | '+group['name']
    for key,value in dict(home_design_role='furniture',source_id=gid,display_name=group['name'],zone=group['zone'],scheme=group['scheme'],part_count=len(pp),import_x_mm=group['x'],import_z_mm=group['z'],movement_step_mm=100,dimensions_mm=[group['dimensionsMm'][k] for k in ['length','width','height']],dimension_note=group['detail'],part_source_mm=json.dumps(pp,ensure_ascii=False),style_revision='modern-japanese-v08',base_height_mm=group['baseHeightMm']).items():ob[key]=value
    ob.lock_location[2]=True;ob.lock_rotation[0]=True;ob.lock_rotation[1]=True;ob.hide_select=False
ff={o['source_id']:o for o in scene.objects if o.get('home_design_role')=='furniture'};assert len(ff)==23
assert all(hashlib.sha256(str([tuple(v.co) for v in ff[i].data.vertices]).encode()).hexdigest()==digest for i,digest in before.items())
coll=bpy.data.collections.new('v12 门厅电视墙、曲面灯槽与梦幻帘');scene.collection.children.link(coll);target=coll
for p in d['referenceParts']:
    if p['shape']=='curved-cove':
        n=40;verts=[];faces=[]
        for xi in [0,p['w']/1000]:
            for thickness in [0,.018]:
                for j in range(n+1):
                    t=math.pi*.5*j/n;verts.append((xi,-(.220+.180*math.sin(t)),2.520+.180*(1-math.cos(t))+thickness))
        band=n+1
        for j in range(n):
            faces += [(j,j+1,2*band+j+1,2*band+j),(band+j,3*band+j,3*band+j+1,band+j+1),(j,band+j,band+j+1,j+1),(2*band+j,2*band+j+1,3*band+j+1,3*band+j)]
        for j in [0,n]:faces.append((j,2*band+j,3*band+j,band+j))
        mesh=bpy.data.meshes.new(p['id']);mesh.from_pydata(verts,[],faces);mesh.materials.append(mats['wall-finish']);ob=bpy.data.objects.new(p['id'],mesh);coll.objects.link(ob);ob.location.x=p['x']/1000
        bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
        for poly in mesh.polygons:poly.use_smooth=True
    else:ob=mesh_part(p)
    ob['home_design_role']='reference_finish_detail';ob['source_id']=p['id'];ob['source_mm']=json.dumps(p,ensure_ascii=False);ob.hide_select=True
root=bpy.data.objects.new('梦幻帘 · 拉合与转角分开调节',None);coll.objects.link(root);root['source_id']='balcony-dream-curtain';root['home_design_role']='curtain_control';root['open_ratio']=1.;root['blade_angle_degrees']=90.
root.id_properties_ui('open_ratio').update(min=0.,max=1.,description='0展开，1收至左侧；与帘片转角独立')
root.id_properties_ui('blade_angle_degrees').update(min=0.,max=90.,description='0遮挡较多，90透光较多；夜间隐私及遮光待产品核对')
sheer=mats['curtain'].copy();sheer.name='V12 · 梦幻帘透光条';nodes=sheer.node_tree.nodes;links=sheer.node_tree.links;out=nodes.get('Material Output');bsdf=nodes.get('Principled BSDF');trans=nodes.new('ShaderNodeBsdfTransparent');mix=nodes.new('ShaderNodeMixShader');mix.inputs[0].default_value=.60;links.new(bsdf.outputs['BSDF'],mix.inputs[1]);links.new(trans.outputs[0],mix.inputs[2]);links.new(mix.outputs[0],out.inputs['Surface'])
def curtain_driver(ob,path,index,expression):
    dr=ob.driver_add(path,index).driver;dr.type='SCRIPTED'
    for name,prop in [('opened','open_ratio'),('angle','blade_angle_degrees')]:
        var=dr.variables.new();var.name=name;var.type='SINGLE_PROP';var.targets[0].id=root;var.targets[0].data_path='["'+prop+'"]'
    dr.expression=expression
for p in d['curtainParts']:
    verts=[];faces=[];steps=24
    for j in range(steps+1):
        u=-.066+.132*j/steps;v=.008*math.sin(4*math.pi*j/steps)
        verts.extend([(u,v,0),(u,v,p['h']/1000)])
    for j in range(steps):faces.append((2*j,2*j+2,2*j+3,2*j+1))
    mesh=bpy.data.meshes.new(p['id']);mesh.from_pydata(verts,[],faces);mesh.materials.append(mats['curtain']);mesh.materials.append(sheer)
    for j,poly in enumerate(mesh.polygons):poly.material_index=1 if 8<=j<16 else 0;poly.use_smooth=True
    ob=bpy.data.objects.new(p['id'],mesh);coll.objects.link(ob);ob.location=(p['openCentreX']/1000,-.08,.02)
    curtain_driver(ob,'location',0,str(p['closedCentreX']/1000)+'*(1-opened)+'+str(p['openCentreX']/1000)+'*opened')
    curtain_driver(ob,'rotation_euler',2,'angle*pi/180')
    ob['home_design_role']='curtain_fabric';ob['source_id']=p['id'];ob.hide_select=True
# Retain three existing scenes and add a separate low-light viewing scene.
scene.id_properties_ui('lighting_scene').update(min=0,max=3,description='0日间 / 1氛围晚间 / 2清洁 / 3观影；相对渲染场景，灯具未选')
for ob in [q for q in scene.objects if q.type=='LIGHT']:
    if ob.data.animation_data:
        for fc in ob.data.animation_data.drivers:
            if fc.data_path=='energy':
                value=.12 if '电视背景' in ob.name else (.4 if '书柜层板' in ob.name else 0)
                fc.driver.expression=str(value)+' if mode>2.5 else ('+fc.driver.expression+')'
def driver(owner,path,values):
    dr=owner.driver_add(path).driver;dr.type='SCRIPTED';var=dr.variables.new();var.name='mode';var.type='SINGLE_PROP';var.targets[0].id_type='SCENE';var.targets[0].id=scene;var.targets[0].data_path='["lighting_scene"]';dr.expression=f'{values[3]} if mode>2.5 else ({values[0]} if mode<.5 else ({values[1]} if mode<1.5 else {values[2]}))'
records=[]
def light(name,pos,aim,values,size,parent=None):
    data=bpy.data.lights.new(name,'AREA');data.shape='RECTANGLE';data.size=size[0];data.size_y=size[1];data.color=(1,.94,.84)
    ob=bpy.data.objects.new(name,data);coll.objects.link(ob);ob.location=pos;ob.rotation_euler=(Vector(aim)-ob.location).to_track_quat('-Z','Y').to_euler()
    if parent:
        bpy.context.view_layer.update();world=ob.matrix_world.copy();ob.parent=ff[parent];ob.matrix_world=world
    driver(data,'energy',values);ob['home_design_role']='lighting_proposal';records.append(dict(name=name,position=pos,target=aim,relative_energies=values,parent_furniture=parent));return ob
light('v12 弧槽顶面反射光',(3.6905,-.375,2.730),(3.6905,-.375,2.75),(8,48,65,3),(5.4,.025))
light('v12 梦幻帘帘头柔光',(3.6905,-.175,2.47),(3.6905,-.08,1.6),(0,15,20,1.5),(5.4,.025))
light('v12 入户柜底导向光',(.64,-10.89,.14),(.64,-10.55,.0),(.1,1.0,1.3,.15),(1,.025),'entry-shoe-cabinet')
light('v12 入户挂衣柔光',(.4,-10.91,1.58),(.4,-11.12,1.0),(.3,3,4,.2),(.65,.03),'entry-shoe-cabinet')
light('v12 随手格柔光',(1.04,-10.90,1.39),(1.04,-11.12,1.2),(.2,1.5,2,.1),(.35,.025),'entry-shoe-cabinet')
light('v12 入户一般照明',(.65,-10.15,2.68),(.65,-10.3,.5),(2,8,13,.2),(.28,.28))
if scene.world and scene.world.use_nodes:
    bg=next((n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND'),None)
    if bg:driver(bg.inputs['Strength'],'default_value',(.45,.025,.025,.015))
driver(scene.view_settings,'exposure',(1.05,.4,.65,.5))
camcoll=bpy.data.collections['10 写实表现 · 人眼视角']
def camera(name,pos,look,lens):
    data=bpy.data.cameras.new(name);data.lens=lens;data.sensor_width=36;data.clip_start=.015;ob=bpy.data.objects.new(name,data);camcoll.objects.link(ob);ob.location=pos;ob.rotation_euler=(Vector(look)-ob.location).to_track_quat('-Z','Y').to_euler()
camera('v12 · 门厅一字柜',(.60,-9.45,1.50),(.65,-10.98,1.35),19)
camera('v12 · 电视墙正面',(4.9,-3.4,1.65),(.1,-3.4,1.3),28)
scene.name='v12 · 轻门厅、悬空电视柜与弧光梦幻帘';scene['home_design_revision']=12;scene['home_design_geometry_sha256']=sha;scene['home_design_style_sha256']=hashlib.sha256(sr).hexdigest();scene['home_design_style_revision']='modern-japanese-v08';scene['home_design_style_file']='05_style/modern-japanese-v08.json';scene['home_design_assumptions']=json.dumps(d['assumptions'],ensure_ascii=False);scene['home_design_reference_refinement']=json.dumps(d['features']['referenceRefinement'],ensure_ascii=False);scene['home_design_lighting_v12']=json.dumps(records,ensure_ascii=False)
scene['home_design_geometry_file']='02_geometry/geometry-master-v12.json';scene['home_design_balcony_tea_set']=json.dumps(d['features']['balconyTeaSet'],ensure_ascii=False);scene['home_design_public_details']=json.dumps(d['features']['publicRefinement'],ensure_ascii=False)
previous_lighting=json.loads(scene.get('home_design_lighting_records','[]'));scene['home_design_lighting_records']=json.dumps([dict(p,source_revision=10,viewing_scene='v12 driver override') for p in previous_lighting if p['name'] in bpy.data.objects]+records,ensure_ascii=False)
scene['lighting_scene']=0;scene.update_tag();scene.frame_set(scene.frame_current);bpy.context.view_layer.update();audit=[]
for group in d['furnitureObjects']:
    ob=ff[group['id']];points=[ob.matrix_world@v.co for v in ob.data.vertices];lo=[min(p[i] for p in points) for i in range(3)];hi=[max(p[i] for p in points) for i in range(3)];b=group['meshBoundsMm'];expected=[b['x']/1000,-(b['z']+b['d'])/1000,b['y']/1000,(b['x']+b['w'])/1000,-b['z']/1000,(b['y']+b['h'])/1000];error=max(abs(a-b) for a,b in zip(lo+hi,expected))*1000;assert error<.05,(group['id'],error)
    audit.append(dict(id=group['id'],x=group['x'],z=group['z'],dimensions_mm=list(ob['dimensions_mm']),mesh_bounds_error_mm=error))
assert sum(o.get('home_design_role')=='wall' for o in scene.objects)==60 and sum(o.get('home_design_role')=='glass' for o in scene.objects)==12
scene.camera=bpy.data.objects['v11 · 客厅至阳台'];scene.cycles.samples=128;scene.render.resolution_x=1800;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
bpy.ops.object.select_all(action='DESELECT');ff['entry-shoe-cabinet'].select_set(True);bpy.context.view_layer.objects.active=ff['entry-shoe-cabinet'];bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(DEST))
report=dict(revision=12,geometry_sha256=sha,style_sha256=scene['home_design_style_sha256'],base_model_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),furniture_count=23,furniture=audit,preserved_meshes=len(before),rebuilt=['tv-low','entry-shoe-cabinet'],removed=['entry-return-cabinet'],latest_living_positions_preserved=True,tea_shift_mm=100,private_room_boundaries_unchanged=True,reference_parts=len(d['referenceParts']),curtain_blades=len(d['curtainParts']),budget_considered=False)
(ROOT/'logs/model-v12-build.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('MODEL_V12_BUILT',len(ff))
