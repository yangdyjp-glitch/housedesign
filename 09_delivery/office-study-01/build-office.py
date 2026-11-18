import bpy, json, math, hashlib, random
from pathlib import Path
from mathutils import Vector

ROOT=Path('D:/AI-Yang.cn/HomeDesign')
OUT=ROOT/'09_delivery/office-study-01'
OUT.mkdir(parents=True,exist_ok=True)
SOURCE=ROOT/'02_geometry/geometry-master-v19.json'
G=json.loads(SOURCE.read_text(encoding='utf-8-sig'))
BASE_FILES=['06_blender/home-main-v19.blend','06_blender/active-model.json','02_geometry/geometry-master-v19.json','05_style/modern-japanese-v19.json','06_blender/active-presentation.json']
before={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in BASE_FILES}
common={
 'units':'mm','status':'independent proposals; not applied to main v19; v20 not started',
 'sourceGeometry':'02_geometry/geometry-master-v19.json','sourceSha256':before[BASE_FILES[2]],
 'axisMapping':'main plan (x,z,height) mm -> Blender (x/1000,-z/1000,height/1000) m',
 'workingTop':{'x':5300,'z':2000,'widthX':700,'lengthZ':2400,'topHeight':750,'thickness':30,'planCornerRadius':60},
 'longLedge':{'x':5100,'z':1800,'widthX':200,'lengthZ':2600,'topHeight':950},
 'shortReturn':{'x':5270,'z':1800,'widthX':730,'lengthZ':200,'topHeight':950,'fullLengthIncludingLongLedge':900,'overlapWithLongLedge':30,'nominalExposedReturnBeyondLongLedge':700},
 'overallFootprint':{'x':5100,'z':1800,'widthX':900,'lengthZ':2600},
 'sofaBackMaxX':5000,'sofaToLedgeGap':100,'ledgeToWorkingTopHeightDifference':200,
 'chairUnchanged':{'id':'office-chair-1','origin':[5900,2335],'meshBounds':{'x':5870,'z':2320,'w':560,'d':560,'h':950}},
 'bookcaseFrontX':6838,'chairRearFurnitureGap':408,'deskEdgeToBookcaseGap':838,
 'monitor':{'count':1,'diagonalInches':34,'conceptBodyMm':[810,87,370],'placement':'on seated 750 mm desktop, never on raised ledge','facing':'positive-x, user faces negative-x toward TV'},
 'commonLighting':{'ledgeStripCctK':3000,'taskLampSuggestedCctK':[3500,4000],'ambientCctK':3000,'independentCircuits':['concealed ledge light','adjustable task lamp','existing ambient/cove'], 'targetWorkplaneLux':[300,500],'luxStatus':'design target, not measured or photometrically calculated'},
 'assumptions':['950 high ledge is a designer proposal, not a measured requirement','100 gap behind sofa needs end access or removable ledge for cleaning','408 chair rear furniture gap is inherited; not an approved occupied circulation route','no new rear partition or overhead cabinet; existing bookcase and bedroom boundary retained','all top supports and wiring are design intent, no structural certification','OFF means all artificial lighting off with same daylight retained; monitor screen also non-emissive'],
}
variants=[
 {'id':'A','title':'浅木薄片','ledgeThickness':30,'ledgeRadius':35,'ledgeFinish':'pale natural oak matte','desktopFinish':'pale natural oak matte','accent':'sage textile chair, small navy lamp','support':'three slim pale-oak supports at sofa edge, one rounded end panel','storage':'one shallow suspended drawer at unused end, 500 x 400 x 100; no drawer across primary knee zone','design':'the quietest continuation of pale oak and warm-white room; thin L ledge with recessed light line'},
 {'id':'B','title':'深木框景','ledgeThickness':45,'ledgeRadius':45,'ledgeFinish':'matte smoked walnut','desktopFinish':'pale natural oak matte','accent':'muted sage end cabinet, navy task lamp','support':'walnut portal supports, sage storage body under short return','storage':'short-return shallow cabinet 500 x 200 x 720 overall; for small objects, not deep A4 files','design':'dark walnut outlines the whole raised L, sage closed end cabinet balances depth without a new wall'},
 {'id':'C','title':'奶油圆弧','ledgeThickness':35,'ledgeRadius':80,'ledgeFinish':'matte warm-ivory solid surface','desktopFinish':'pale natural oak matte','accent':'navy shallow drawer and ivory supports, green plant','support':'matching ivory rounded posts with a concealed dark under-top frame','storage':'one navy suspended drawer 500 x 400 x 100 at unused end','design':'a smooth ivory ribbon with large rounded exposed ends contrasts with the pale-wood seated worktop'},
]
(OUT/'设计参数.json').write_text(json.dumps({'common':common,'variants':variants,'baselineHashes':before},ensure_ascii=False,indent=2),encoding='utf-8')

def mat(name,color,wood=False,emission=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 n=m.node_tree.nodes;p=n.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=.55
 if wood:
  tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=5;tex.inputs['Detail'].default_value=2
  co=n.new('ShaderNodeTexCoord');mapping=n.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(18,.7,5)
  ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.25;ramp.color_ramp.elements[0].color=(*(c*.68 for c in color),1);ramp.color_ramp.elements[1].color=(*(min(c*1.16,1) for c in color),1)
  m.node_tree.links.new(co.outputs['Generated'],mapping.inputs[0]);m.node_tree.links.new(mapping.outputs[0],tex.inputs['Vector']);m.node_tree.links.new(tex.outputs['Fac'],ramp.inputs[0]);m.node_tree.links.new(ramp.outputs['Color'],p.inputs['Base Color'])
 if emission:
  p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emission
 return m

def tag(o,kind):
 o['source_id']=kind;o['proposal']='office-study-01';return o

def box(name,x,z,y,w,d,h,material,r=2):
 bpy.ops.mesh.primitive_cube_add(size=1,location=((x+w/2)/1000,-(z+d/2)/1000,(y+h/2)/1000))
 o=bpy.context.object;o.name=name;o.dimensions=(w/1000,d/1000,h/1000);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(material)
 if r:
  mod=o.modifiers.new('Soft edges','BEVEL');mod.width=min(r,w/2,d/2,h/2)/1000;mod.segments=3
  o.modifiers.new('Normals','WEIGHTED_NORMAL')
 return o

def top(name,x,z,y,w,d,h,r,material,kind):
 r=min(r,w/2-1,d/2-1);verts=[]
 for cx,cz,a in [(x+w-r,z+r,-90),(x+w-r,z+d-r,0),(x+r,z+d-r,90),(x+r,z+r,180)]:
  for i in range(13):
   t=math.radians(a+90*i/12);verts.append(((cx+r*math.cos(t))/1000,-(cz+r*math.sin(t))/1000,y/1000))
 n=len(verts);verts+= [(a,b,(y+h)/1000) for a,b,_ in verts]
 faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);o.data.materials.append(material)
 # Plan axes are mirrored in Blender; recalculate all normals consistently.
 bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT');o.select_set(False)
 be=o.modifiers.new('Edge ease','BEVEL');be.width=.002;be.segments=2;o.modifiers.new('Normals','WEIGHTED_NORMAL');tag(o,kind);return o

def cyl(name,x,z,y,w,d,h,material,ellipsoid=False):
 loc=((x+w/2)/1000,-(z+d/2)/1000,(y+h/2)/1000)
 if ellipsoid:
  bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,location=loc);o=bpy.context.object;o.scale=(w/2000,d/2000,h/2000)
 else:
  bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=1,depth=1,location=loc);o=bpy.context.object;o.scale=(w/2000,d/2000,h/1000)
 o.name=name;o.data.materials.append(material)
 for p in o.data.polygons:p.use_smooth=True
 return o

def light(name,typ,loc,power,size=1,target=None,color=(1,.83,.64)):
 ld=bpy.data.lights.new(name,typ);ld.energy=power;ld.color=color
 if typ=='AREA':ld.shape='DISK';ld.size=size
 o=bpy.data.objects.new(name,ld);bpy.context.collection.objects.link(o);o.location=loc
 if target:o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
 return o

readback=[]
for v in variants:
 bpy.ops.wm.read_factory_settings(use_empty=True)
 sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
 sc['proposalStatus']='INDEPENDENT DESIGN OPTIONS; main v19 untouched';sc['geometrySourceSha256']=before[BASE_FILES[2]];sc['axisMapping']=common['axisMapping']
 mats={'wood':mat('Pale oak',(.69,.51,.31),True),'walnut':mat('Walnut',(.24,.12,.065),True),'cabinet':mat('Warm white',(.84,.82,.75)),'fabric':mat('Linen',(.75,.72,.64)),'fabric-dark':mat('Fabric base',(.64,.62,.56)),'sage':mat('Sage',(.32,.46,.36)),'navy':mat('Navy',(.055,.12,.20)),'metal':mat('Dark metal',(.08,.085,.08)),'ceramic':mat('Ceramic',(.85,.83,.76)),'foliage':mat('Leaf green',(.12,.26,.10)),'soil':mat('Soil',(.06,.045,.025)),'screen':mat('Dark screen',(.018,.024,.03)),'book':mat('Book',(.54,.46,.35))}
 ivory=mat('Ivory solid surface',(.84,.83,.76));ledge=mats['wood'] if v['id']=='A' else mats['walnut'] if v['id']=='B' else ivory
 floor=mat('Pale floor',(.65,.53,.37),True);wall=mat('Matte warm white wall',(.85,.84,.79))
 box('Floor observation crop',1800,-300,-70,5900,6500,70,floor,0)
 for z in range(0,6500,190):box('Floor joint',1800,z,-.5,5900,1,1,mats['walnut'],0)
 # Existing sofa and bookcase, in their v19 positions. No new walls at the short desk end.
 for f in G['furniture']:
  parent=f.get('parent','');ident=f['id']
  keep=parent in ['sofa-modular','office-chair-1','bookcase'] or (parent=='double-desk' and not ('-top' in ident or '-leg-' in ident or ident.endswith('-rail') or 'cable-tray' in ident))
  if not keep:continue
  ma=mats.get(f.get('material'),mats['wood']);s=f.get('shape','box');args=(ident,f['x'],f['z'],f.get('y',0),f['w'],f['d'],f['h'],ma)
  if s in ['cylinder','frustum','ellipsoid','leaf']:o=cyl(*args,ellipsoid=s in ['ellipsoid','leaf'])
  else:o=box(*args,r=min(f.get('bevelMm',f.get('radiusMm',2)),30))
  o['source_id']=parent;o['source_part']=ident
 # Soft architectural background is a cropped observation context, not a main architecture edit.
 box('Existing bedroom-wall context',7188,1100,0,150,3900,2750,wall)
 for x in [2300,6650]:box('Window jamb context',x,0,0,65,65,2650,mats['metal'])
 box('Window head context',2300,0,2580,4415,65,65,mats['metal'])
 box('Window sill context',2300,0,0,4415,65,65,mats['metal'])
 box('Window side rail context',2850,0,0,45,65,2650,mats['metal'])
 # Working plane is unchanged. Short return goes 200 mm toward balcony, not into chair clearance.
 top('Seated desktop 2400x700 H750',5300,2000,720,700,2400,30,60,mats['wood'],'working-top')
 th=v['ledgeThickness'];rr=v['ledgeRadius']
 top('Long raised ledge 2600x200 H950',5100,1800,950-th,200,2600,th,rr,ledge,'long-raised-ledge')
 top('Short raised return to same H950',5270,1800,950-th,730,200,th,rr,ledge,'short-raised-return')
 # Under-top concealed frame; no unsupported free-floating concept top.
 for zz in [1840,3075,4330]:box('Ledge support',5120,zz,0,55,45,950-th,ledge,6)
 for zz in [2060,4280]:box('Desk support',5420,zz,0,45,45,720,ledge,6)
 box('Desk right end support',5920,4290,0,45,45,720,ledge,6)
 box('Hidden desktop longitudinal frame',5350,2040,670,35,2320,45,mats['metal'],2)
 if v['id']=='B':
  box('Sage shallow end storage',5480,1810,40,500,180,680,mats['sage'],10)
  box('Sage shallow end storage door',5484,1980,44,492,18,672,mats['sage'],3)
 else:
  dm=mats['wood'] if v['id']=='A' else mats['navy']
  box('Shallow end drawer',5550,3800,620,400,500,100,dm,12)
  box('Shallow drawer reveal',5945,3804,626,3,492,3,mats['metal'],0)
 # Dark removable wiring channel facing the working side, separated from lighting service.
 box('Removable cable channel',5305,3060,655,90,1160,40,mats['metal'],3)
 glow=mat('Warm strip diffuser',(1,.78,.52))
 strips=[box('Recessed long strip',5280,2050,950-th-8,9,2270,8,glow,1),box('Recessed return strip',5360,1978,950-th-8,550,9,8,glow,1)]
 p=glow.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(1,.69,.35,1)
 daylight=light('Daylight soft window','AREA',(4.7,.6,3.5),700,4.5,(5.3,-3,0),(.93,.96,1))
 sun=light('Daylight sun','SUN',(3,1,6),1.6,target=(6,-5,0),color=(1,.92,.78));sun.data.angle=.10
 artificial=[light('Ledge indirect soft','AREA',(5.3,-3.1,.90),20,2,(5.7,-3.1,.75)),light('Task lamp','POINT',(5.47,-3.28,1.075),12,.3,color=(1,.94,.83)),light('Ambient reflected','AREA',(5.8,-2.8,2.5),90,3,(5.4,-3,.5))]
 bpy.ops.object.camera_add(location=(6.6,-5.9,2.7));cam=bpy.context.object;cam.name='Office same-view comparison';cam.rotation_euler=(Vector((5.3,-2.9,.80))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='PERSP';cam.data.lens=37;cam.data.clip_end=100;sc.camera=cam
 sc.world=bpy.data.worlds.new('Daylight world');sc.world.use_nodes=True;sc.world.node_tree.nodes.get('Background').inputs[0].default_value=(.76,.80,.87,1);sc.world.node_tree.nodes.get('Background').inputs[1].default_value=.35
 sc.render.engine='CYCLES';sc.cycles.samples=16;sc.cycles.use_denoising=True;sc.render.resolution_x=1600;sc.render.resolution_y=1300;sc.render.resolution_percentage=100
 sc.view_settings.view_transform='AgX'
 folder=OUT/v['id'];folder.mkdir(exist_ok=True)
 for state in ['OFF','ON']:
  for l in artificial:l.hide_render=(state=='OFF')
  p.inputs['Emission Strength'].default_value=3 if state=='ON' else 0
  sc.render.filepath=str(folder/f'{v["id"]}-{state}-native.png');bpy.ops.render.render(write_still=True)
 blend=folder/f'办公区-{v["id"]}-独立提案.blend';bpy.ops.wm.save_as_mainfile(filepath=str(blend))
 bpy.ops.wm.open_mainfile(filepath=str(blend))
 rows=[]
 for o in bpy.context.scene.objects:
  if o.get('source_id') not in ['working-top','long-raised-ledge','short-raised-return']:continue
  points=[o.matrix_world@Vector(q) for q in o.bound_box];rows.append({'name':o.name,'part':o['source_id'],'minX':round(min(q.x for q in points)*1000),'maxX':round(max(q.x for q in points)*1000),'minPlanZ':round(-max(q.y for q in points)*1000),'maxPlanZ':round(-min(q.y for q in points)*1000),'topHeight':round(max(q.z for q in points)*1000)})
 readback.append({'variant':v['id'],'parts':rows,'monitorScreenParts':sum(o.get('source_part','')=='double-desk-monitor-screen-34' for o in bpy.context.scene.objects),'chairSourceGroupCount':len(set(o.get('source_id') for o in bpy.context.scene.objects if o.get('source_id')=='office-chair-1'))})

after={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in BASE_FILES}
verification={'savedReopenedModels':readback,'baselineHashesBefore':before,'baselineHashesAfter':after,'mainUnchanged':before==after,'liveBlenderMcp':'unavailable; independent verified headless runtime used','sceneKind':'isolated furniture proposals with cropped existing context, not whole-house architectural models'}
(OUT/'核对记录.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2),encoding='utf-8')
assert verification['mainUnchanged']
assert all(r['monitorScreenParts']==1 and r['chairSourceGroupCount']==1 for r in readback)
assert all(next(p['topHeight'] for p in r['parts'] if p['part']=='working-top')==750 for r in readback)
assert all(all(p['topHeight']==950 for p in r['parts'] if 'raised' in p['part']) for r in readback)
print('OFFICE_STUDY_COMPLETE',json.dumps(readback))
