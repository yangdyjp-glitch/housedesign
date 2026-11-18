"""Merge the audited dining11 and office02 objects; keep v19 immutable."""
import bpy,bmesh,json,math,hashlib,copy
from pathlib import Path
from mathutils import Matrix,Vector

R=Path('D:/AI-Yang.cn/HomeDesign');OUT=R/'09_delivery/main-integration-v20';OUT.mkdir(exist_ok=True)
OFFICE='B' # Provisional design preview until homeowner chooses A/B/C.
if '--office' in __import__('sys').argv:OFFICE=__import__('sys').argv[__import__('sys').argv.index('--office')+1]
assert OFFICE in ['A','B','C']
def load(p):return json.loads((R/p).read_text(encoding='utf-8-sig'))
def write(p,d):(R/p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
base=load('02_geometry/geometry-master-v19.json');d=copy.deepcopy(base)
oldactive=load('06_blender/active-model.json')
baseline={p:sha(p) for p in ['06_blender/home-main-v19.blend','02_geometry/geometry-master-v19.json','05_style/modern-japanese-v19.json','06_blender/active-model.json','06_blender/active-presentation.json']}
write('09_delivery/main-integration-v20/合并前版本.json',{'baseline':baseline,'activeModel':oldactive,'activePresentation':load('06_blender/active-presentation.json'),'layoutSource':'03_layout/widget-layout-v19-initial.json','liveLayoutSurface':'no attached model tab or running Blender bridge; latest saved model/snapshot used'})
ds=load('09_delivery/sideboard-U-study-11/U-layout-parameters.json');os=load('09_delivery/office-study-02/设计参数.json')
variant=next(v for v in os['variants'] if v['id']==OFFICE)
T=Matrix(((0,1,0,3.082),(-1,0,0,-6.1625),(0,0,1,0),(0,0,0,1)))

def material_key(m,group):
 n=m.name.lower() if m else ''
 if 'walnut' in n:return 'walnut'
 if 'pale oak' in n:return 'wood'
 if 'white refrigerator' in n or 'appliance' in n:return 'appliance'
 if 'ivory' in n:return 'ivory'
 if 'warm white' in n:return 'cabinet'
 if 'sage' in n:return 'sage'
 if 'navy' in n:return 'navy'
 if 'green' in n or 'leaf' in n:return 'foliage'
 if 'soil' in n:return 'soil'
 if 'screen' in n:return 'screen'
 if any(k in n for k in ['metal','steel','reveal','recess']):return 'metal'
 if 'paper' in n:return 'paper'
 if 'ceramic' in n or 'porcelain' in n:return 'ceramic'
 if 'diffuser' in n or 'led' in n:return 'paper'
 if 'book' in n:return 'book'
 return 'cabinet'

def select_group(kind,o):
 if o.type!='MESH' or o.hide_render:return None
 n=o.name;sid=o.get('source_id','')
 if kind=='dining':
  if n in ['wall','floor']:return None
  if n.startswith(('outside-','tuck-under-')):return None
  if n.startswith(('pendant-stem','pendant-paper-shade')):return 'dining-pendant'
  if n.startswith(('fridge-body','fridge-two-door','fridge-centre-reveal','fridge-pull')):return 'refrigerator'
  return 'dining-sideboard-island'
 if sid=='bookcase' or sid.startswith('bookcase-sliding'):return 'bookcase'
 if sid=='double-desk' or sid=='working-top' or n.startswith(('Desk support','Desk right end support','Hidden desktop','Removable cable','Shallow end drawer','Shallow drawer reveal')):return 'double-desk'
 if sid in ['long-raised-ledge','ledge-support','near-halfwall-solid-body','near-halfwall-cap','long-ledge-light','near-halfwall-light']:return 'office-divider'
 return None

parts=[];snapshots=[];sourceCounts={};sourceFiles={}
for kind,path,transform in [('dining','09_delivery/sideboard-U-study-11/短连接长餐台-胡桃白冰箱圆边-独立11.blend',T),('office',f'09_delivery/office-study-02/{OFFICE}/办公区-{OFFICE}-近端半墙远端敞开-独立02.blend',Matrix.Identity(4))]:
 sourceFiles[kind]={'path':path,'sha256':sha(path)}
 bpy.ops.wm.open_mainfile(filepath=str(R/path));sc=bpy.context.scene;sc.frame_set(1);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
 selected=[(o,select_group(kind,o)) for o in list(sc.objects) if select_group(kind,o)]
 copied=[];counts={}
 for i,(o,group) in enumerate(selected):
  world=transform@o.matrix_world;key=material_key(o.data.materials[0] if o.data.materials else None,group)
  raw=[world@v.co for v in o.data.vertices];xyz=[[q.x*1000,q.z*1000,-q.y*1000] for q in raw]
  lo=[min(q[j] for q in xyz) for j in range(3)];hi=[max(q[j] for q in xyz) for j in range(3)]
  ident=f'v20-{kind}-{i:03d}'
  rec={'id':ident,'parent':group,'kind':'reference-finish' if group=='dining-pendant' else 'furniture','shape':'mesh','x':round(lo[0],3),'z':round(lo[2],3),'y':round(lo[1],3),'w':round(hi[0]-lo[0],3),'d':round(hi[2]-lo[2],3),'h':round(hi[1]-lo[1],3),'material':key,'localVerticesMm':[[round(q[j]-lo[j],3) for j in range(3)] for q in xyz],'meshFaces':[list(f.vertices) for f in o.data.polygons],'sourceObject':o.name,'sourceStudy':kind}
  parts.append(rec)
  me=bpy.data.meshes.new_from_object(o.evaluated_get(deps));me.transform(world)
  obj=bpy.data.objects.new(ident,me);obj['integration_group']=group;obj['integration_source']=o.name;obj['integration_material_key']=key;copied.append(obj);counts[group]=counts.get(group,0)+1
 snapshot=OUT/f'{kind}-frozen-components.blend';bpy.data.libraries.write(str(snapshot),set(copied),path_remap='RELATIVE_ALL',fake_user=True)
 snapshots.append(snapshot);sourceCounts[kind]=counts

# Generate the exact same plan-space furniture data used by the interactive view.
retiredIds=['dining-table']+[f'dining-chair-{i}' for i in range(1,5)]
replacedIds=['double-desk','bookcase']
d['retiredFurnitureV20']={'objects':[q for q in d['furnitureObjects'] if q['id'] in retiredIds],'parts':[q for q in d['furniture'] if q['parent'] in retiredIds+replacedIds]}
d['furnitureObjects']=[q for q in d['furnitureObjects'] if q['id'] not in retiredIds]
d['furniture']=[p for p in d['furniture'] if p['parent'] not in retiredIds+replacedIds]+[p for p in parts if p['parent']!='dining-pendant']
d['retiredReferenceV20']=[p for p in d['referenceParts'] if p['id'].startswith(('v19-dining-art','v19-dining-pendant'))]
d['referenceParts']=[p for p in d['referenceParts'] if not p['id'].startswith(('v19-dining-art','v19-dining-pendant'))]+[p for p in parts if p['parent']=='dining-pendant']
for p in d['referenceParts']:
 if p.get('parent')=='dining-pendant':p.pop('parent');p['collidable']=False
d['furnitureMaterials']['ivory']={'color':[.84,.83,.76,1],'roughness':.55}
def groupq(gid,name,x,z,w,dep,h,dimensions,detail,label=True):
 return dict(id=gid,name=name,zone='dining' if gid.startswith(('dining','refrigerator')) else 'office',scheme='integrated-completed-designs-v20',x=x,z=z,w=w,d=dep,h=h,visualHeight=h,label=label,labelRotate=90 if dep>w else 0,dimensionsMm=dict(zip(['length','width','height'],dimensions)),detail=detail)
d['furnitureObjects'] += [
 groupq('refrigerator','白色双开门冰箱',2282,6302.5,750,920,1850,[920,750,1850],'920×750×1850为常规双开门代理；与柜门面齐平，位于客厅端、U餐岛以外。具体机型、散热和全开待核。'),
 groupq('dining-sideboard-island','餐边柜与U餐岛组合',1132,6162.5,1950,3400,2750,[3400,1950,2750],'整组含冰箱围板；柜段2200×800×2750，餐面1800×550×880，内侧取物净深600，胡桃木连续齐平台面、白色实门、R100圆端；椅凳暂不摆。'),
 groupq('office-divider','沙发背高台与近端半墙',5100,2000,1735,2600,950,[2600,1735,950],'L形整组包络；长高台2400×200×950，近端半墙长1735、墙身120、压顶200，接到右书柜；阳台端敞开。材质暂用'+variant['title']+'。')]
for q in d['furnitureObjects']:
 if q['id']=='double-desk':q['detail']='2400×700×750圆角工作面，面向电视；一台34寸显示器、一把椅子及常用品。沙发背高台与近端半墙作为独立整组。'
 if q['id']=='bookcase':q['detail']+=' 北端800模块改为平移实门接口提案，避开近端半墙；五金未选。'
d.update(revision=20,title='餐岛与沙发后办公区已并入主模型',project_revision='v20-completed-design-integration',style='modern-japanese-v20')
d['compatiblePlacementRevisions']=sorted(set(d.get('compatiblePlacementRevisions',[])+[19]))
d['placementBaselinesByRevision']['19']={q['id']:{'x':q['x'],'z':q['z']} for q in base['furnitureObjects']}
d['features']['completedIntegrationV20']={'authorization':'设计完成后，全部都加到主模型中','diningSource':sourceFiles['dining'],'officeSource':sourceFiles['office'],'officeVariant':OFFICE,'officeVariantStatus':'temporary designer preview; choice pending','retiredFurnitureIds':retiredIds,'seating':'deferred by owner; old four chairs archived, not deployed','scope':'completed dining11 and office02 only; wider v20 construction/MEP refinement remains pending','sourceCounts':sourceCounts,'mainAxisMapping':'(global x,global z,height) mm -> Blender(x,-z,height)/1000','diningMapping':'global x=3082-v; global z=6162.5+u','positions':'every unaffected furniture origin preserved; replaced dining programme uses latest independent11 coordinates'}
d['assumptions']+=['用户本轮授权完成设计全部并入主模型；合并已完成餐边柜11和办公区02，不把尚未完成的v20机电/节点当作完成。','办公材质先采用B作可逆临时预览，待业主A/B/C选择；近端半墙接书柜与阳台端进入已经明确。','餐椅暂缓，旧四椅和原餐桌退役留档，不继续在新餐岛内部摆椅。','主模型中的下拉篮、冰箱门和书柜平移门保存闭合静态形态；动态原理研究另见对应独立方案，未宣称主模型带有全部机构动画。']
d['provenance'].update(revision=20,baseline='02_geometry/geometry-master-v19.json',baseline_sha256=baseline['02_geometry/geometry-master-v19.json'],layout='completed dining11 replaces old table/chairs; office02 applied; all unaffected origins retained')

# Reopen main, retire only replaced objects, append native frozen source geometry.
bpy.ops.wm.open_mainfile(filepath=str(R/'06_blender/home-main-v19.blend'));s=bpy.context.scene;s.frame_set(1)
target=bpy.data.collections.new('v20 · 已完成餐岛与办公区');s.collection.children.link(target)
archive=bpy.data.collections.new('v19 · 被替换家具留档（隐藏）');s.collection.children.link(archive);archive.hide_render=True;archive.hide_viewport=True
original={o['source_id']:o for o in s.objects if o.get('home_design_role')=='furniture'}
for gid in retiredIds+replacedIds:
 o=original[gid]
 for co in list(o.users_collection):co.objects.unlink(o)
 archive.objects.link(o);o['home_design_role']='retired_furniture';o['retired_in_revision']=20
for o in list(s.objects):
 if o.get('source_id','').startswith(('v19-dining-art','v19-dining-pendant')) or (o.type=='LIGHT' and o.get('circuit')=='dining'):
  for co in list(o.users_collection):co.objects.unlink(o)
  archive.objects.link(o);o['retired_in_revision']=20

def named(prefix):return bpy.data.materials.get(prefix) or next((m for m in bpy.data.materials if m.name.startswith(prefix+'.')),None)
native={'wood':named('V10 · 减黄浅橡木'),'walnut':named('V19 · walnut'),'cabinet':named('R01 · 暖白哑光柜门')}
groups={}
for snap in snapshots:
 with bpy.data.libraries.load(str(snap),link=False) as (a,b):b.objects=list(a.objects)
 for o in b.objects:
  if not o:continue
  target.objects.link(o)
  group=o['integration_group'];groups.setdefault(group,[]).append(o)
  key=o['integration_material_key']
  if key in native and native[key]:
   o.data.materials.clear();o.data.materials.append(native[key])

def join_group(gid,objects,q=None):
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=bpy.context.object
 if q:
  anchor=Vector((q['x']/1000,-q['z']/1000,0));o.data.transform(Matrix.Translation(-anchor));o.location=anchor
  o.name=gid+' | '+q['name'];o['home_design_role']='furniture';o['source_id']=gid;o['display_name']=q['name'];o['zone']=q['zone'];o['scheme']=q['scheme'];o['import_x_mm']=q['x'];o['import_z_mm']=q['z'];o['movement_step_mm']=100;o['dimensions_mm']=[q['dimensionsMm'][k] for k in ['length','width','height']];o['dimension_note']=q['detail'];o['part_source_mm']=json.dumps([p for p in d['furniture'] if p['parent']==gid],ensure_ascii=False);o['style_revision']='modern-japanese-v20';o.lock_location[2]=True;o.lock_rotation[0]=o.lock_rotation[1]=True
 else:o['home_design_role']='reference_finish_detail';o['source_id']='v20-dining-pendant'
 return o
qmap={q['id']:q for q in d['furnitureObjects']}
created={gid:join_group(gid,oo,qmap.get(gid)) for gid,oo in groups.items()}
ff={o['source_id']:o for o in s.objects if o.get('home_design_role')=='furniture'};assert len(ff)==26
bpy.context.view_layer.update()
def actual_bounds(o):
 p=[o.matrix_world@v.co for v in o.data.vertices];a=[min(q[i] for q in p)*1000 for i in range(3)];b=[max(q[i] for q in p)*1000 for i in range(3)]
 return dict(x=round(a[0],3),z=round(-b[1],3),y=round(a[2],3),w=round(b[0]-a[0],3),d=round(b[1]-a[1],3),h=round(b[2]-a[2],3))
for q in d['furnitureObjects']:
 if q['id'] in groups:q['meshBoundsMm']=actual_bounds(ff[q['id']])
 if q['id'] not in retiredIds+replacedIds+['refrigerator','dining-sideboard-island','office-divider']:
  prev=next(p for p in base['furnitureObjects'] if p['id']==q['id']);assert (q['x'],q['z'])==(prev['x'],prev['z'])
for o in s.objects:
 if o.get('home_design_role')=='furniture':o['style_revision']='modern-japanese-v20'

# New local light circuits follow the existing five-scene controller.
def driven_energy(ld,values):
 f=ld.driver_add('energy');v=f.driver.variables.new();v.name='mode';v.type='SINGLE_PROP';v.targets[0].id_type='SCENE';v.targets[0].id=s;v.targets[0].data_path='["lighting_scene_v19"]';f.driver.expression='('+','.join(map(str,values))+')[min(4,max(0,int(mode)))]'
def area(name,pos,aim,values,size,sizey,circuit):
 ld=bpy.data.lights.new(name,'AREA');ld.shape='RECTANGLE';ld.size=size;ld.size_y=sizey;ld.color=(1,.86,.68);driven_energy(ld,values);o=bpy.data.objects.new(name,ld);target.objects.link(o);o.location=pos;o.rotation_euler=(Vector(aim)-o.location).to_track_quat('-Z','Y').to_euler();o['home_design_role']='v20_lighting';o['circuit']=circuit;return o
area('v20 餐边柜置物带柔光',(2.30,-8.4125,1.455),(2.51,-8.4125,1.00),[2,18,20,24,0],.012,1.95,'dining-niche')
area('v20 新餐台纸灯',(1.407,-8.0625,1.50),(1.407,-8.0625,.88),[4,30,45,50,0],.38,.38,'dining')
area('v20 沙发背高台内缘',(5.29,-3.2,.895),(5.62,-3.2,.75),[1,10,3,14,0],.012,2.25,'office-ledge')
area('v20 近端半墙内缘',(5.65,-4.425,.895),(5.65,-4.05,.75),[.5,6,1,8,0],.6,.012,'office-ledge')
for material in bpy.data.materials:
 if not material.name.startswith('Warm strip diffuser') or not material.use_nodes:continue
 bsdf=material.node_tree.nodes.get('Principled BSDF')
 if not bsdf:continue
 strength=bsdf.inputs['Emission Strength'];strength.default_value=0
 fc=strength.driver_add('default_value');v=fc.driver.variables.new();v.name='mode';v.type='SINGLE_PROP';v.targets[0].id_type='SCENE';v.targets[0].id=s;v.targets[0].data_path='["lighting_scene_v19"]';fc.driver.expression='(0,3,1,4,0)[min(4,max(0,int(mode)))]'

write('02_geometry/geometry-master-v20.json',d)
sty=load('05_style/modern-japanese-v19.json');sty.update(version='v20-completed-design-integration',geometry_base='02_geometry/geometry-master-v20.json',geometry_sha256=sha('02_geometry/geometry-master-v20.json'));sty['designer_decisions']['completed_integration_v20']=d['features']['completedIntegrationV20'];write('05_style/modern-japanese-v20.json',sty)
s.name='v20 · 餐岛与办公区整合';s['home_design_revision']=20;s['home_design_geometry_file']='02_geometry/geometry-master-v20.json';s['home_design_geometry_sha256']=sha('02_geometry/geometry-master-v20.json');s['home_design_style_file']='05_style/modern-japanese-v20.json';s['home_design_style_sha256']=sha('05_style/modern-japanese-v20.json');s['completed_integration_v20']=json.dumps(d['features']['completedIntegrationV20'],ensure_ascii=False);s['photoreal_presentation_revision']=19;s['presentation_stale_after_geometry_revision']=20;s['lighting_scene_v19']=0
for im in bpy.data.images:
 if im.source=='FILE' and im.filepath and not im.packed_file:im.filepath=bpy.path.relpath(bpy.path.abspath(im.filepath),start=str(R/'06_blender'))
MODEL=R/'06_blender/home-main-v20.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(MODEL))
bpy.ops.wm.open_mainfile(filepath=str(MODEL));s=bpy.context.scene;ff={o['source_id']:o for o in s.objects if o.get('home_design_role')=='furniture'};checks=[]
for q in d['furnitureObjects']:
 o=ff[q['id']];assert abs(o.location.x*1000-q['x'])<.01 and abs(-o.location.y*1000-q['z'])<.01
 b=actual_bounds(o);expected=q['meshBoundsMm'];assert max(abs(b[k]-expected[k]) for k in b)<.06,(q['id'],b,expected)
 orig=o.location.copy();o.location.x+=.1;bpy.context.view_layer.update();assert abs(o.location.x-orig.x-.1)<1e-6;o.location=orig
 checks.append({'id':q['id'],'origin':[q['x'],q['z']],'bounds':b,'move100AndRestore':True})
assert sum(o.get('home_design_role')=='wall' for o in s.objects)==62
assert sum(o.get('home_design_role')=='glass' for o in s.objects)==12
assert d['walls']==base['walls'] and d['glass']==base['glass']
assert all(sha(p)==h for p,h in baseline.items())
write('03_layout/widget-layout-v20-initial.json',{'revision':20,'moveStepMm':100,'furniturePositions':[dict(id=q['id'],x=q['x'],z=q['z'],dx=0,dz=0) for q in d['furnitureObjects']],'curtainMode':'open','masterBathDoorOpen':False,'masterShowerOpen':False})
write('09_delivery/main-integration-v20/主模型回读.json',{'status':'passed','revision':20,'officeVariant':OFFICE,'officeVariantStatus':'provisional','modelSha256':sha('06_blender/home-main-v20.blend'),'furnitureCount':len(ff),'savedReopened':True,'objects':checks,'walls':62,'glass':12,'architectureUnchanged':True,'v19Unchanged':True,'sourceCounts':sourceCounts,'retiredIds':retiredIds,'sourceFiles':sourceFiles})
print('V20_COMPLETED_DESIGNS_MERGED',len(ff),'OFFICE',OFFICE,flush=True)
