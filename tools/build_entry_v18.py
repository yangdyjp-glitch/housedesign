"""Preserve the live source, inherit selected realism, and rebuild only entry storage."""
from pathlib import Path
import bpy,bmesh,ast,json,hashlib,math
from mathutils import Vector,Matrix
ROOT=Path(r'D:/AI-Yang.cn/HomeDesign');BASE=ROOT/'06_blender/home-live-before-v18-20261103.blend';DEST=ROOT/'06_blender/home-main-v18.blend'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert Path(bpy.data.filepath).resolve()==BASE.resolve()
d=json.loads((ROOT/'02_geometry/geometry-master-v18.json').read_text(encoding='utf-8'));old=json.loads((ROOT/'02_geometry/geometry-master-v14.json').read_text(encoding='utf-8'));s=bpy.context.scene
ff={o['source_id']:o for o in s.objects if o.get('home_design_role')=='furniture'};assert len(ff)==27
for q in old['furnitureObjects']:
    o=ff[q['id']];pts=[o.matrix_world@v.co for v in o.data.vertices];lo=[min(p[i] for p in pts)*1000 for i in range(3)];hi=[max(p[i] for p in pts)*1000 for i in range(3)];b=q['meshBoundsMm'];expect=[b['x'],-b['z']-b['d'],b['y'],b['x']+b['w'],-b['z'],b['y']+b['h']];assert max(abs(a-b) for a,b in zip(lo+hi,expect))<.05,q['id']
target=bpy.data.collections.new('v18 · 右鞋柜 左钢琴键换鞋区');s.collection.children.link(target)
with bpy.data.libraries.load(str(ROOT/'06_blender/home-v16-reference-anchor.blend'),link=False) as (src,out):
    names=list(src.materials);out.materials=list(names);out.worlds=[n for n in src.worlds if n.startswith('V15')];out.objects=[n for n in src.objects if n.startswith(('sofa-modular','ottoman','plant-balcony-tall','plant-tv-medium','plant-balcony-low','V16 · 参考图斜向柔和日光'))]
loaded=dict(zip(names,out.materials));assert out.worlds;s.world=out.worlds[0]
fabric={'V10 · 细织棉麻感米灰':'V15 · 米灰细织实拍纹理','V10 · 沙发浅灰支撑织物':'V15 · 浅灰框体织物','J02 · 低饱和苔绿色织物':'V15 · 苔绿细织物','J02 · 深蓝色织物':'V15 · 深蓝织物','R01 · 米灰亚麻混纺':'V15 · 旧灰米织物'}
floor=loaded['V15 · 实拍纹理浅橡木地板']
for o in list(s.objects):
    floor_changed=False
    for slot in o.material_slots:
        if not slot.material:continue
        name=slot.material.name
        if name in ['R01 · 浅木地板','V10 · 浅木地面外观占位']:slot.material=floor;floor_changed=True
        elif name in fabric:slot.material=loaded[fabric[name]]
        elif name in loaded:slot.material=loaded[name]
    if floor_changed and o.type=='MESH':
        uv=o.data.uv_layers.active or o.data.uv_layers.new(name='oak_1_7m')
        for poly in o.data.polygons:
            for i in poly.loop_indices:
                p=o.matrix_world@o.data.vertices[o.data.loops[i].vertex_index].co;uv.data[i].uv=(p.x/1.7,-p.y/1.7)
for o in out.objects:
    target.objects.link(o);o.hide_set(False)
    gid=o.get('source_id')
    if gid in ff:
        previous=ff[gid];props=dict(previous.items())
        for k,v in props.items():o[k]=v
        bpy.data.objects.remove(previous,do_unlink=True);ff[gid]=o
for gid in ['tv-high','entry-shoe-cabinet']:bpy.data.objects.remove(ff.pop(gid),do_unlink=True)
old_niche_light=bpy.data.objects.get('入户置物格内灯带')
if old_niche_light:
    old_niche_light.location.z+=.4;old_niche_light.name='v18 · 换鞋上柜底部灯带';old_niche_light['entry_v18_relocated_from_old_niche']=True
for script,name in [('render_modern_japanese_v02.py','profile_mesh'),('update_blender_v07.py','mesh_part')]:
    tree=ast.parse((ROOT/'tools'/script).read_text(encoding='utf-8'));node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name);exec(compile(ast.Module(body=[node],type_ignores=[]),name,'exec'))
mats={'wood':loaded['V10 · 减黄浅橡木'],'fabric':loaded['V15 · 米灰细织实拍纹理'],'cabinet':loaded['R01 · 暖白哑光柜门'],'butter':loaded['V08 · 柔和奶黄色下柜'],'walnut':loaded['V08 · 胡桃木置物格'] if 'V08 · 胡桃木置物格' in loaded else next(v for k,v in loaded.items() if '胡桃' in k),'navy':loaded['V15 · 深蓝织物']}
def make(p):
    if not p.get('sideProfileLocalMm'):return mesh_part(p)
    prof=p['sideProfileLocalMm'];vertices=[((p['x']+a)/1000,-(p['z']+z)/1000,(p['y']+b)/1000) for z in [0,p['d']] for a,b in prof];n=len(prof);faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];m=bpy.data.meshes.new(p['id']);m.from_pydata(vertices,[],faces);m.materials.append(mats[p['material']]);m.update();o=bpy.data.objects.new(p['id'],m);target.objects.link(o);return o
for gid in ['tv-high','entry-shoe-cabinet','entry-piano-bench']:
    pieces=[make(p) for p in d['furniture'] if p['parent']==gid];bpy.ops.object.select_all(action='DESELECT')
    for o in pieces:
        o.select_set(True);bpy.context.view_layer.objects.active=o
        for mod in list(o.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.context.view_layer.objects.active=pieces[0];bpy.ops.object.join();o=bpy.context.object;bpy.context.view_layer.update();points=[o.matrix_world@v.co for v in o.data.vertices];q=next(q for q in d['furnitureObjects'] if q['id']==gid);anchor=Vector((q['x']/1000,-q['z']/1000,0));o.matrix_world=Matrix.Identity(4);o.location=anchor
    for v,p in zip(o.data.vertices,points):v.co=p-anchor
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();ff[gid]=o
for q in d['furnitureObjects']:
    o=ff[q['id']];o.location.x=q['x']/1000;o.location.y=-q['z']/1000;o.name=q['id']+' | '+q['name'];o.lock_location[2]=True;o.lock_rotation[0]=True;o.lock_rotation[1]=True
    props=dict(home_design_role='furniture',source_id=q['id'],display_name=q['name'],zone=q['zone'],scheme=q['scheme'],import_x_mm=q['x'],import_z_mm=q['z'],movement_step_mm=100,dimensions_mm=[q['dimensionsMm'][k] for k in ['length','width','height']],dimension_note=q['detail'],part_source_mm=json.dumps([p for p in d['furniture'] if p['parent']==q['id']],ensure_ascii=False),style_revision='modern-japanese-v18-entry',base_height_mm=0)
    for k,v in props.items():o[k]=v
def camera(name,pos,aim,lens):
    data=bpy.data.cameras.new(name);data.lens=lens;data.clip_start=.02;o=bpy.data.objects.new(name,data);target.objects.link(o);o.location=pos;o.rotation_euler=(Vector(aim)-o.location).to_track_quat('-Z','Y').to_euler();o['home_design_role']='entry_camera'
camera('v18 · 右手鞋柜',(.70,-9.10,1.5),(.635,-11.1,1.38),20)
camera('v18 · 左手钢琴键换鞋',(1.10,-10.05,1.6),(.16,-9.0,1.2),24)
for name,energy in [('主光',0),('补光',0),('阳台柔和日光',80),('入户侧开口日光',65)]:
    o=bpy.data.objects.get(name)
    if o:o.data.animation_data_clear();o.data.energy=energy;o.data.color=(1,.98,.94)
for im in bpy.data.images:
    if im.source=='FILE' and im.filepath and not im.packed_file:im.filepath=bpy.path.relpath(bpy.path.abspath(im.filepath),start=str(DEST.parent))
s.view_settings.driver_remove('exposure');s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=.8;s['lighting_scene']=0;s.update_tag();s.frame_set(s.frame_current);bpy.context.view_layer.update()
s.name='v18 · 入户右鞋柜 左钢琴键换鞋区';s['home_design_revision']=18;s['photoreal_presentation_revision']=18;s['home_design_geometry_sha256']=sha(ROOT/'02_geometry/geometry-master-v18.json');s['home_design_style_sha256']=sha(ROOT/'05_style/modern-japanese-v18.json');s['home_design_geometry_file']='02_geometry/geometry-master-v18.json';s['home_design_style_file']='05_style/modern-japanese-v18.json';s['entry_v18']=json.dumps(d['features']['entryV18'],ensure_ascii=False);s['wall_alignment_v17_status']='pending door decision, no geometry change'
s.camera=bpy.data.objects['v18 · 左手钢琴键换鞋'];bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(DEST))
report=dict(revision=18,source_live_model_sha256=sha(BASE),model_sha256=sha(DEST),geometry_sha256=s['home_design_geometry_sha256'],style_sha256=s['home_design_style_sha256'],furniture_count=len(ff),right='entry-shoe-cabinet',left='entry-piano-bench',piano_keys=60,shown_open=4,entry_door_not_relocated=True,wall_alignment_pending=True)
(ROOT/'logs/v18-build.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('V18_MODEL_SAVED',len(ff))
