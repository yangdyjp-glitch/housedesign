"""Build a reversible design sibling of v18; no boundary or furniture-origin changes."""
from pathlib import Path
import bpy,bmesh,json,hashlib,math,ast
from mathutils import Vector,Matrix
R=Path(r'D:/AI-Yang.cn/HomeDesign');DEST=R/'06_blender/home-main-v19.blend'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert Path(bpy.data.filepath).resolve()==(R/'06_blender/home-main-v18.blend').resolve()
d=json.loads((R/'02_geometry/geometry-master-v19.json').read_text(encoding='utf8'));s=bpy.context.scene
ff={o['source_id']:o for o in s.objects if o.get('home_design_role')=='furniture'};assert len(ff)==28
target=bpy.data.collections.new('v19 · 暖白深木与分层光');s.collection.children.link(target)
def mat(name,color,rough=.7):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;return m
def named(prefix):return bpy.data.materials.get(prefix) or next(m for m in bpy.data.materials if m.name.startswith(prefix+'.'))
mats={'wood':named('V10 · 减黄浅橡木'),'fabric':named('V15 · 米灰细织实拍纹理'),'fabric-dark':named('V15 · 浅灰框体织物'),'sage':named('V15 · 苔绿细织物'),'navy':named('V15 · 深蓝织物'),'cabinet':named('R01 · 暖白哑光柜门')}
for key in ['walnut','metal','book','screen','ceramic','soil','foliage','foliage-light','paper','art-sage','art-navy','wall-finish']:
 rec=d['furnitureMaterials'][key];mats[key]=mat('V19 · '+key,rec['color'][:3],rec['roughness'])
# Subtle directional grain in dark walnut: small-scale details instead of flat brown proxy.
wn=mats['walnut'].node_tree;n=wn.nodes;tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=6;tex.inputs['Detail'].default_value=2
tc=n.new('ShaderNodeTexCoord');mapping=n.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(20,2,3);wn.links.new(tc.outputs['Generated'],mapping.inputs[0]);wn.links.new(mapping.outputs[0],tex.inputs['Vector'])
ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.065,.035,.021,1);ramp.color_ramp.elements[1].color=(.18,.105,.068,1);wn.links.new(tex.outputs['Fac'],ramp.inputs[0]);wn.links.new(ramp.outputs['Color'],n.get('Principled BSDF').inputs['Base Color'])
for script,name in [('render_modern_japanese_v02.py','profile_mesh'),('update_blender_v07.py','mesh_part')]:
 tree=ast.parse((R/'tools'/script).read_text(encoding='utf8'));node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name);exec(compile(ast.Module(body=[node],type_ignores=[]),name,'exec'))
def make(p):
 if not p.get('planProfileLocalMm'):return mesh_part(p)
 profile=p['planProfileLocalMm'];verts=[((p['x']+a)/1000,-(p['z']+b)/1000,yy/1000) for yy in [p['y'],p['y']+p['h']] for a,b in profile];nn=len(profile)
 faces=[tuple(reversed(range(nn))),tuple(range(nn,nn*2))]+[(i,(i+1)%nn,(i+1)%nn+nn,i+nn) for i in range(nn)]
 mesh=bpy.data.meshes.new(p['id']);mesh.from_pydata(verts,[],faces);mesh.materials.append(mats[p['material']]);mesh.update();o=bpy.data.objects.new(p['id'],mesh);target.objects.link(o)
 bevel=o.modifiers.new('薄靠背触边圆润','BEVEL');bevel.width=.003;bevel.segments=3;o.modifiers.new('法线','WEIGHTED_NORMAL');return o
changed=d['features']['deepeningV19']['changedFurniture']
for gid in changed:
 bpy.data.objects.remove(ff.pop(gid),do_unlink=True);pp=[p for p in d['furniture'] if p['parent']==gid];pieces=[make(p) for p in pp];bpy.ops.object.select_all(action='DESELECT')
 for o in pieces:
  o.select_set(True);bpy.context.view_layer.objects.active=o
  for mod in list(o.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
 bpy.context.view_layer.objects.active=pieces[0];bpy.ops.object.join();o=bpy.context.object;bpy.context.view_layer.update();pts=[o.matrix_world@v.co for v in o.data.vertices];q=next(q for q in d['furnitureObjects'] if q['id']==gid);anchor=Vector((q['x']/1000,-q['z']/1000,0));o.matrix_world=Matrix.Identity(4);o.location=anchor
 for v,p in zip(o.data.vertices,pts):v.co=p-anchor
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();ff[gid]=o
for q in d['furnitureObjects']:
 o=ff[q['id']];o.name=q['id']+' | '+q['name'];o.location.x=q['x']/1000;o.location.y=-q['z']/1000;o.lock_location[2]=True;o.lock_rotation[0]=True;o.lock_rotation[1]=True
 for k,v in dict(home_design_role='furniture',source_id=q['id'],display_name=q['name'],zone=q['zone'],scheme=q['scheme'],import_x_mm=q['x'],import_z_mm=q['z'],movement_step_mm=100,dimensions_mm=[q['dimensionsMm'][k] for k in ['length','width','height']],dimension_note=q['detail'],part_source_mm=json.dumps([p for p in d['furniture'] if p['parent']==q['id']],ensure_ascii=False),style_revision='modern-japanese-v19',base_height_mm=q.get('baseHeightMm',0)).items():o[k]=v
for o in list(s.objects):
 if o.get('source_id','').startswith('v12-tv-'):bpy.data.objects.remove(o,do_unlink=True)
 elif o.name in ['v10-living-cove-lip','v10-hall-cove-lip']:bpy.data.objects.remove(o,do_unlink=True)
for p in [p for p in d['referenceParts'] if p['id'].startswith('v19-')]:
 o=make(p);o['home_design_role']='reference_finish_detail';o['source_id']=p['id']
# Actual finished ceiling skin, concept level only. Equipment void remains undetermined.
ceiling=bpy.data.objects.get('v10 公共区暖白顶面');assert ceiling
ceiling.name='v19 · 连续吊顶完成面2750暂定';solid=ceiling.modifiers.new('18mm效果模型面层 非结构厚度','SOLIDIFY');solid.thickness=.018;solid.offset=-1 if ceiling.data.polygons[0].normal.z<0 else 1
ceiling['finished_plane_mm']=2750;ceiling['structure_and_ac_void_unknown']=True
# Remove prior public proposal lights; retain master-suite lighting and actual daylight rigs.
for o in list(s.objects):
 if o.type=='LIGHT' and o.get('home_design_role')!='master_suite_lighting' and o.data.type!='SUN' and o.name not in ['阳台柔和日光','入户侧开口日光']:
  bpy.data.objects.remove(o,do_unlink=True)
# Retire old glowing strip proxies: corrected light positions are generated below.
for o in list(s.objects):
 if o.type=='MESH' and o.get('home_design_role')!='furniture' and any(w in o.name for w in ['灯带','灯珠']):o.hide_render=True;o['retired_lighting_v19']=True
s['lighting_scene_v19']=0
def driven_energy(data,values):
 data.animation_data_clear();f=data.driver_add('energy');dr=f.driver;v=dr.variables.new();v.name='mode';v.type='SINGLE_PROP';v.targets[0].id_type='SCENE';v.targets[0].id=s;v.targets[0].data_path='["lighting_scene_v19"]';dr.expression='('+','.join(str(v) for v in values)+')[min(4,max(0,int(mode)))]'
def area(name,pos,aim,values,size,sizey=None,circuit='',warm=True):
 data=bpy.data.lights.new(name,'AREA');data.shape='RECTANGLE' if sizey else 'DISK';data.size=size
 if sizey:data.size_y=sizey
 data.color=(1,.86,.68) if warm else (1,.95,.86);data.energy=values[0];driven_energy(data,values);o=bpy.data.objects.new(name,data);target.objects.link(o);o.location=pos;o.rotation_euler=(Vector(aim)-o.location).to_track_quat('-Z','Y').to_euler();o['home_design_role']='v19_lighting';o['circuit']=circuit;o['render_energy_not_watts']=True;return o
area('v19 窗帘槽向上反射',(3.6905,-.375,2.725),(3.6905,-.375,3.2),[8,35,18,40,5],5.4,.018,'curtain')
area('v19 帘头柔洗',(3.6905,-.18,2.47),(3.6905,-.08,1.5),[0,12,4,14,0],5.4,.025,'curtain')
for yy in [1.24,2.12]:area('v19 书柜选层光 '+str(yy),(6.88,-2.976,yy),(7.15,-2.976,yy-.35),[.5,5,2,6,.4],.018,1.90,'bookcase')
area('v19 换鞋挂板上方柔光',(.26,-9,1.785),(.10,-9,.8),[1,8,4,12,1],.018,.94,'entry')
area('v19 鞋柜随手格柔光',(.635,-10.86,1.387),(.635,-11.11,1.22),[1,4,2,5,.3],1.1,.012,'entry')
area('v19 鞋柜底部引导',(.635,-10.86,.145),(.635,-10.4,.0),[0,1.5,1,2,.7],1.1,.012,'entry')
area('v19 桌灯工作光',(5.47,-3.28,1.085),(5.8,-3.3,.75),[2,12,3,14,0],.13,None,'office',False)
area('v19 餐桌柔光吊灯',(2.682,-8.1,1.55),(2.682,-8.1,.75),[4,30,50,55,0],.3,.54,'dining')
# No central living main light. Small recessed points cover cleaning and passage, separately dimmed.
for i,(x,z) in enumerate([(1.25,2.5),(5.9,2.5),(1.3,5.6),(5.4,5.6),(1.4,7.5),(1.4,9.0),(.65,10.15)]):area('v19 嵌入功能光 '+str(i),(x,-z,2.735),(x,-z,0),[2,5 if i>3 else 1,4 if i>3 else 0,35,0],.09,None,'general',False)
# Visible diffuse pendant, no bare brilliant light source.
shade=bpy.data.objects.get('v19-dining-pendant-shade');shade['lighting_circuit']='dining'
paper=mats['paper'].copy();paper.name='V19 · 纸布柔光灯罩';p=paper.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(1,.83,.60,1);p.inputs['Emission Strength'].default_value=.45;shade.data.materials.clear();shade.data.materials.append(paper)
for o in s.objects:
 if o.type=='LIGHT' and o.data.type=='SUN':driven_energy(o.data,[1.6,0,.08,.3,0])
 elif o.name in ['阳台柔和日光','入户侧开口日光']:driven_energy(o.data,[80 if o.name.startswith('阳台') else 65,0,5,25,0])
if s.world and s.world.use_nodes:
 back=s.world.node_tree.nodes.get('Background')
 if back:
  back.inputs['Strength'].default_value=.3
  f=back.inputs['Strength'].driver_add('default_value');v=f.driver.variables.new();v.name='mode';v.type='SINGLE_PROP';v.targets[0].id_type='SCENE';v.targets[0].id=s;v.targets[0].data_path='["lighting_scene_v19"]';f.driver.expression='(0.3,0.015,0.05,0.15,0.008)[min(4,max(0,int(mode)))]'
for im in bpy.data.images:
 if im.source=='FILE' and im.filepath and not im.packed_file:im.filepath=bpy.path.relpath(bpy.path.abspath(im.filepath),start=str(DEST.parent))
s.name='v19 · 自然现代日式深化';s['home_design_revision']=19;s['home_design_geometry_file']='02_geometry/geometry-master-v19.json';s['home_design_geometry_sha256']=sha(R/'02_geometry/geometry-master-v19.json');s['home_design_style_file']='05_style/modern-japanese-v19.json';s['home_design_style_sha256']=sha(R/'05_style/modern-japanese-v19.json');s['design_deepening_v19']=json.dumps(d['features']['deepeningV19'],ensure_ascii=False);s['photoreal_presentation_revision']=19
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=.8;s.camera=bpy.data.objects['v11 · 客厅至阳台'];s.update_tag();s.frame_set(s.frame_current);bpy.context.view_layer.update()
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(DEST))
report=dict(revision=19,source_model='06_blender/home-main-v18.blend',source_sha256=sha(R/'06_blender/home-main-v18.blend'),model_sha256=sha(DEST),geometry_sha256=s['home_design_geometry_sha256'],style_sha256=s['home_design_style_sha256'],furniture_count=len(ff),changed=changed,placement_changes=0,ceiling=d['features']['deepeningV19']['ceiling'],lighting_scenes=['day','evening','dining','cleaning','viewing'])
(R/'logs/v19-build.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print('V19_MODEL_SAVED',len(ff),flush=True)
