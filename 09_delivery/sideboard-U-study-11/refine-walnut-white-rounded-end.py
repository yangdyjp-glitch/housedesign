from pathlib import Path
import bpy,bmesh,json,math,hashlib,shutil
from mathutils import Vector

ROOT=Path('D:/AI-Yang.cn/HomeDesign');OUT=ROOT/'09_delivery/sideboard-U-study-11'
base=OUT/'短连接-长餐面-U餐岛独立11.blend'
spec=json.loads((OUT/'U-layout-parameters.json').read_text(encoding='utf-8'));baseline=spec['main_baseline_sha256']
assert baseline=={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in baseline}
bpy.ops.wm.open_mainfile(filepath=str(base));scene=bpy.context.scene;scene.frame_set(1);bpy.context.view_layer.update()
walnut=bpy.data.materials['walnut'];white=bpy.data.materials['clean warm white']
# Reuse the selected walnut finish throughout the niche, band and complete U tabletop.
for o in scene.objects:
 if o.type!='MESH':continue
 for slot in o.material_slots:
  if slot.material and slot.material.name=='pale oak':slot.material=walnut
fridge=bpy.data.materials.new('white refrigerator enamel');fridge.use_nodes=True;p=fridge.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.90,.92,.91,1);p.inputs['Roughness'].default_value=.27;p.inputs['Metallic'].default_value=.05
for o in scene.objects:
 if o.type=='MESH' and o.name.startswith(('fridge-body','fridge-two-door','fridge-pull')):
  o.data.materials.clear();o.data.materials.append(fridge)

def span_u(o,a,b):
 bpy.context.view_layer.update();mw=o.matrix_world.copy();old=o.dimensions.x;o.dimensions.x=(b-a)/1000
 mw.translation.x=(a+b)/2000;o.matrix_world=mw
 # Restore the requested scale after replacing the world translation, including parented door meshes.
 o.dimensions.x=(b-a)/1000;bpy.context.view_layer.update()
def move_u(o,delta):
 bpy.context.view_layer.update();mw=o.matrix_world.copy();mw.translation.x+=delta/1000;o.matrix_world=mw;bpy.context.view_layer.update()
def prism(name,points,z,h,m):
 n=len(points);verts=[(u/1000,-v/1000,zz/1000) for zz in (z,z+h) for u,v in points]
 faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
 o=bpy.data.objects.new(name,me);scene.collection.objects.link(o);o.data.materials.append(m);be=o.modifiers.new('soft arris','BEVEL');be.width=.002;be.segments=3;o.modifiers.new('weighted normals','WEIGHTED_NORMAL');return o
def rounded(points):
 out=[]
 for i,p in enumerate(points):
  a=Vector(p)-Vector(points[i-1]);a.normalize();b=Vector(points[(i+1)%len(points)])-Vector(p);b.normalize()
  r=3 if p[1]==0 else (100 if p==(3400,800) else 60)
  c=Vector(p)-a*r+b*r;t=Vector(p)-a*r-c;st=math.atan2(t.y,t.x);turn=math.pi/2*(1 if a.x*b.y-a.y*b.x>0 else -1)
  for j in range(17):
   q=st+turn*j/16;out.append((c.x+r*math.cos(q),c.y+r*math.sin(q)))
 return out

# Keep the original2200 outer width. Reserve the last100 as a fixed R100 curved end,
# reduce the last upper storage module600->500 and the drawer bank700->600.
# This is a rounded end skin, not a new600-wide tall closed column.
for nm in ['right-end-lower-09','right-end-upper-09']:
 if nm in bpy.data.objects:bpy.data.objects.remove(bpy.data.objects[nm],do_unlink=True)
for nm in ['base-back','base-floor','base-plinth','sideboard-ceiling-closure','continuous-oak-niche-back-09','continuous-slim-band-body-09']:
 if nm in bpy.data.objects:span_u(bpy.data.objects[nm],1200,3300)
for o in list(scene.objects):
 n=o.name
 if n.startswith('continuous-U-top-'):bpy.data.objects.remove(o,do_unlink=True)
 elif n=='slim-flap-4-09':span_u(o,2803,3297)
 elif n=='complete-upper-door-4-09':span_u(o,2803,3297)
 elif n=='upper-door-low-pull-4-09':move_u(o,-100)
 elif n=='upper-4-back-09' or n.startswith('upper-4-horizontal-09'):span_u(o,2818,3282)
 elif n.startswith('pulldown-4-tray') or n.startswith('pulldown-4-front-rail'):span_u(o,2850,3250)
 elif n=='pulldown-4-handle':span_u(o,2890,3210)
 elif n.startswith('pulldown-4-side-mechanism'):
  if o.matrix_world.translation.x>3.0:move_u(o,-100)
 elif n.startswith('horizontal-drawer-front'):span_u(o,2703,3297)
 elif n.startswith('horizontal-drawer-box'):span_u(o,2721,3279)
 elif n=='niche-led-profile-09':span_u(o,1200,3300)

# New straight inner end panel for the last500 module, behind its complete opaque door.
bpy.ops.mesh.primitive_cube_add(size=1,location=(3.291,-.615,2.215));side=bpy.context.object;side.name='upper-4-inner-right-side-11';side.dimensions=(.018,.330,.970);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);side.data.materials.append(white)
cap=[(3300,0),(3400,0),(3400,700)]+[(3300+100*math.cos(math.radians(a)),700+100*math.sin(math.radians(a))) for a in range(0,91,5)]+[(3300,0)]
# Remove consecutive duplicate points to keep the raw mesh manifold.
cap2=[]
for pt in cap:
 if not cap2 or math.dist(pt,cap2[-1])>.001:cap2.append(pt)
if math.dist(cap2[0],cap2[-1])<.001:cap2.pop()
lo=prism('rounded-right-end-lower-R100-11',cap2,0,850,white)
hi=prism('rounded-right-end-upper-R100-11',cap2,880,1870,white)
top=prism('continuous-walnut-U-top-rounded-right-R100-11',rounded([tuple(q) for q in spec['dining_U']['outline']]),850,30,walnut)
light=bpy.data.objects.get('artificial-niche')
if light:
 light.location.x=2.25;light.data.size=1.95;light.rotation_euler=(Vector((2.25,-.66,1.02))-light.location).to_track_quat('-Z','Y').to_euler()
spec['user_confirmed']+=['置物区与桌面统一胡桃木色','冰箱白色','右侧柜体圆边']
spec['colour_rule']='matte walnut throughout tabletop, niche lining and closed thin flap; clean-white refrigerator; warm-white opaque cabinets with rounded right end'
spec['finish_revision']='owner walnut/white/R100 steering after initial short-link-long-table study'
spec['sideboard'].update(niche_clear_width_to_end_panel=2100,niche_full_width=2100,thin_band_full_width=2100,drawer_bank_wall_range=[2700,3300],drawer_front_width=594,
 complete_upper_modules=[dict(u=1200,w=600),dict(u=1800,w=500),dict(u=2300,w=500),dict(u=2800,w=500)],
 rounded_right_end=dict(radius=100,fixed_width=100,wall_range=[3300,3400],height=2750,colour='warm white',additional_overall_width=0,status='designer proposal; fixed curved end, not counted as storage; field verification pending'))
spec['dining_U'].update(material='matte walnut, same slot throughout',continuous_object=top.name,right_wall_counter_end_radius=100)
spec['fridge']['finish']='clean white; existing ordinary two-door concept, no product selected'
spec['pull_down']['modules_nominal_widths']=[600,500,500,500];spec['pull_down']['pending'].append('last module reduced to500 for fixed R100 end; actual hardware and movement recheck')
scene['parameters']=json.dumps(spec,ensure_ascii=False);scene['proposal']='Independent11 owner walnut, white refrigerator, fixed R100 cabinet end; main v19 unchanged'
for state in ['OFF','ON']:
 for o in scene.objects:
  if o.type=='LIGHT' and o.name.startswith('artificial-'):o.hide_render=(state=='OFF')
 scene.render.filepath=str(OUT/f'胡桃白冰箱圆边-{state}-实体参考.png');bpy.ops.render.render(write_still=True)
name=top.name;lower=lo.name;upper=hi.name
blend=OUT/'短连接长餐台-胡桃白冰箱圆边-独立11.blend';bpy.ops.wm.save_as_mainfile(filepath=str(blend))
(OUT/'U-layout-parameters.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2),encoding='utf-8')
bpy.ops.wm.open_mainfile(filepath=str(blend));scene=bpy.context.scene;scene.frame_set(1);bpy.context.view_layer.update()
def bounds(o):
 p=[o.matrix_world@Vector(q) for q in o.bound_box];return dict(u=[round(min(q.x for q in p)*1000,2),round(max(q.x for q in p)*1000,2)],v=[round(-max(q.y for q in p)*1000,2),round(-min(q.y for q in p)*1000,2)],h=[round(min(q.z for q in p)*1000,2),round(max(q.z for q in p)*1000,2)])
def manifold(o):
 bm=bmesh.new();bm.from_mesh(o.data);ok=all(e.is_manifold for e in bm.edges);bm.free();return ok
record=dict(saved_reopened=True,style='walnut/white-fridge/R100 right end',top=bounds(bpy.data.objects[name]),top_manifold=manifold(bpy.data.objects[name]),
 rounded_ends={n:dict(bounds=bounds(bpy.data.objects[n]),manifold=manifold(bpy.data.objects[n])) for n in [lower,upper]},
 last_upper_door=bounds(bpy.data.objects['complete-upper-door-4-09']),drawers={o.name:bounds(o) for o in scene.objects if o.name.startswith('horizontal-drawer-front')},
 visible_seat_count=len([o for o in scene.objects if o.type=='MESH' and '-seat' in o.name and not o.hide_render]),
 fridge_materials={o.name:[s.material.name for s in o.material_slots] for o in scene.objects if o.name.startswith(('fridge-body','fridge-two-door'))},
 baseline_after={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in baseline})
assert record['top']['h']==[850,880] and record['top_manifold'] and record['visible_seat_count']==0
assert record['last_upper_door']['u']==[2803,3297]
assert all(v['manifold'] for v in record['rounded_ends'].values()) and all(v['u']==[2703,3297] for v in record['drawers'].values())
assert record['baseline_after']==baseline
(OUT/'finish-model-readback.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print('WALNUT_WHITE_ROUNDED_END_COMPLETE',json.dumps(record,ensure_ascii=False))
