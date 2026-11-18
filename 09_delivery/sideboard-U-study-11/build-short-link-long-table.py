from pathlib import Path
import bpy,bmesh,json,math,hashlib,shutil
from mathutils import Vector

ROOT=Path('D:/AI-Yang.cn/HomeDesign');OLD=ROOT/'09_delivery/sideboard-U-study-10';OUT=ROOT/'09_delivery/sideboard-U-study-11'
OUT.mkdir(parents=True,exist_ok=True);(OUT/'references').mkdir(exist_ok=True)
shutil.copy2('C:/Users/ADMINI~1/AppData/Local/Temp/codex-clipboard-e8fe211f-fa03-46d8-b455-48cfb268ebfc.png',OUT/'references/业主短连接长餐面批注.png')
spec=json.loads((OLD/'U-layout-parameters.json').read_text(encoding='utf-8'))
baseline=spec['main_baseline_sha256'];assert baseline=={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in baseline}
sourceblend=OLD/'端头起步-加长U餐岛-暂不排椅凳.blend'
bpy.ops.wm.open_mainfile(filepath=str(sourceblend));scene=bpy.context.scene;scene.frame_set(1)
oak=bpy.data.materials['pale oak'];wood=bpy.data.materials['walnut']
def box(name,u,v,z,w,d,h,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=((u+w/2)/1000,-(v+d/2)/1000,(z+h/2)/1000));o=bpy.context.object;o.name=name;o.dimensions=(w/1000,d/1000,h/1000);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m);return o
def cyl(name,u,v,z,r,h,m):
 bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=r/1000,depth=h/1000,location=(u/1000,-v/1000,(z+h/2)/1000));o=bpy.context.object;o.name=name;o.data.materials.append(m);return o
def rounded(points,r=60):
 result=[]
 for i,p in enumerate(points):
  a=Vector(p)-Vector(points[i-1]);a.normalize();b=Vector(points[(i+1)%len(points)])-Vector(p);b.normalize()
  rr=3 if p[1]==0 else (5 if p[1]==800 and p[0]==3400 else r)
  c=Vector(p)-a*rr+b*rr;t=Vector(p)-a*rr-c;start=math.atan2(t.y,t.x);turn=math.pi/2*(1 if a.x*b.y-a.y*b.x>0 else -1)
  for j in range(10):
   ang=start+turn*j/9;result.append((c.x+rr*math.cos(ang),c.y+rr*math.sin(ang)))
 return result
def prism(name,points,z,h,m):
 n=len(points);verts=[(u/1000,-v/1000,zz/1000) for zz in (z,z+h) for u,v in points]
 faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(mesh);bm.free()
 o=bpy.data.objects.new(name,mesh);scene.collection.objects.link(o);o.data.materials.append(m);return o

for o in list(scene.objects):
 if o.name.startswith(('continuous-U-top-','hidden-crossarm-steel-10','hidden-longarm-steel-10','slim-U-leg-10')):bpy.data.objects.remove(o,do_unlink=True)
# Cabinet plane and fridge remain fixed. 600 internal retrieval depth is retained.
# The long dining rail extends 200 at EACH end to protect the kitchen-end turn.
poly=[(1200,0),(3400,0),(3400,800),(1550,800),(1550,1400),(2800,1400),(2800,1950),(1000,1950),(1000,1400),(1200,1400)]
top=prism('continuous-U-top-short-link-long-table-11',rounded(poly),850,30,oak)
be=top.modifiers.new('soft arris','BEVEL');be.width=.003;be.segments=3;top.modifiers.new('weighted normal','WEIGHTED_NORMAL')
box('hidden-crossarm-steel-11',1240,650,815,230,1100,30,wood)
box('hidden-dining-rail-steel-11',1100,1545,815,1600,60,30,wood)
supports=[(1280,1575),(2600,1575)]
for u,v in supports:cyl('inset-dining-leg-11',u,v,0,30,850,wood)
# Lamp remains the selected paper shade; move125 across the table to its new transverse centre.
for o in scene.objects:
 if o.name.startswith(('pendant-stem','pendant-paper-shade','artificial-pendant')):o.location.y-=.125

spec.update(date='2026-11-06',status='independent11: smaller red connection, longer blue dining rail; seats still deferred',main_model_modified=False,v20_started=False,
 source_annotation='references/业主短连接长餐面批注.png',source_study='sideboard-U-study-10',source_blend_sha256=hashlib.sha256(sourceblend.read_bytes()).hexdigest())
spec['user_confirmed']+=['红色连接段再短一点，只留内部取物空间','蓝色餐面再长一点，作为用餐桌面']
spec['dining_U'].update(outline=poly,continuous_object=top.name,connecting_arm_outside_cabinet=[1150,350],visible_connector_before_dining_rail=[600,350],
 outside_dining_arm=[1800,550],dining_rail_range_u=[1000,2800],dining_rail_range_v=[1400,1950],inner_clear_width=600,inner_clear_length=1250,
 root_at_living_end_of_sideboard=True,living_end_dining_overhang=200,support_legs=dict(diameter=60,centres=supports,outer_edge_to_centre=375,outer_edge_to_leg_face=345))
spec['designer_dimensions']=dict(former_connector_width=450,new_connector_width=350,former_outer_projection=1200,new_outer_projection=1150,red_projection_shortening=50,
 former_dining_arm=[1400,600],new_dining_arm=[1800,550],dining_extension_living_end=200,dining_extension_kitchen_end=200,inner_retrieval_depth_retained=600,
 height_retained=880,normal_low_dining_table=False,reason='550-deep single-side high dining rail; avoid shrinking the already tight600 retrieval band')
spec['clearances']=dict(inner_retrieval_closed_front=600,inner_retrieval_clear_length=1250,outer_furniture_gap_without_seats=732,
 free_table_end_to_kitchen_boundary_without_seats=672.5,fridge_closed_front_to_connector_root_u=140,
 fridge90_proxy_door_tip_v=1257,fridge90_proxy_tip_to_new_blue_inner_edge=143,fridge_full_sweep_unverified=True,seating_clearances='deferred, not approved by unoccupied gaps')
spec['evaluation'].update(layout='narrower/shorter connecting arm, two-ended extension of long dining rail',
 retrieval='600 nominal closed-front depth retained; single-person retrieval only, not a cooking aisle; rounded inner corner is a local restriction',
 drawers='new dining end2800 overlaps first100 of2700–3400 drawer bank; drawer access needs chosen hardware and standing-zone check',
 dining='1800x550 at880 high; narrow single-side dining rail, not a low750 table or a two-sided550-wide dining table',
 meal_mode='three daily/one spare retained as future programme, exact seats and body envelopes deferred by user',
 fridge='native90-degree right-door proxy checked only; blue extension does not certify product full opening',
 support='legs recessed345 from outer edge to leg face; structural design and chosen seats still pending')
spec['colour_rule']='same pale oak continuous U top, niche and thin flap; warm-white opaque cabinetry, no glass doors; seating deferred'
spec['lighting_update']=dict(pendant_shift_v=125,pendant_plan_centre=[1900,1675],same_paper_shade=True,niche_strip_retained=True,off='all artificial light objects off, daylight retained')
scene['parameters']=json.dumps(spec,ensure_ascii=False);scene['proposal']='Independent11; reduced connection and longer narrow dining rail; main v19 unchanged; no seats placed'
artificial=[o for o in scene.objects if o.type=='LIGHT' and o.name.startswith('artificial-')]
assert len(artificial)>=2
for state in ['OFF','ON']:
 for o in artificial:o.hide_render=(state=='OFF')
 scene.render.filepath=str(OUT/f'短连接长餐面-{state}-实体参考.png');bpy.ops.render.render(write_still=True)
blend=OUT/'短连接-长餐面-U餐岛独立11.blend';bpy.ops.wm.save_as_mainfile(filepath=str(blend));name=top.name
(OUT/'U-layout-parameters.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2),encoding='utf-8')
bpy.ops.wm.open_mainfile(filepath=str(blend));scene=bpy.context.scene;scene.frame_set(1)
def bounds(o):
 pts=[o.matrix_world@Vector(v) for v in o.bound_box]
 return dict(u=[round(min(p.x for p in pts)*1000,3),round(max(p.x for p in pts)*1000,3)],v=[round(-max(p.y for p in pts)*1000,3),round(-min(p.y for p in pts)*1000,3)],h=[round(min(p.z for p in pts)*1000,3),round(max(p.z for p in pts)*1000,3)])
bm=bmesh.new();bm.from_mesh(bpy.data.objects[name].data);manifold=all(e.is_manifold for e in bm.edges);bm.free()
readback=dict(saved_reopened=True,frame=scene.frame_current,top=bounds(bpy.data.objects[name]),raw_top_manifold=manifold,
 visible_seat_count=len([o for o in scene.objects if ('-seat' in o.name or 'tuck-under-stool' in o.name) and o.type=='MESH' and not o.hide_render]),
 supports={o.name:bounds(o) for o in scene.objects if o.name.startswith('inset-dining-leg-11')},main_baseline_sha256_after={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in baseline})
scene.frame_set(120);bpy.context.view_layer.update();door=max([o for o in scene.objects if o.name.startswith('fridge-two-door')],key=lambda o:o.location.x)
readback['fridge90_proxy']=bounds(door);readback['fridge90_to_blue_gap_v']=1400-readback['fridge90_proxy']['v'][1]
assert readback['top']['h']==[850,880] and readback['top']['v']==[0,1950]
assert readback['top']['u']==[1000,3400] and readback['visible_seat_count']==0 and manifold
assert readback['fridge90_to_blue_gap_v']>0 and readback['main_baseline_sha256_after']==baseline
(OUT/'model-readback.json').write_text(json.dumps(readback,ensure_ascii=False,indent=2),encoding='utf-8')

# Exact plan comparison, owner orientation: cabinet on the right.
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE_NEXT'
scene.render.resolution_x=2400;scene.render.resolution_y=1700;scene.view_settings.view_transform='Standard';scene.world=bpy.data.worlds.new('diagram');scene.world.color=(1,1,1)
def em(name,col):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;n.clear();e=n.new('ShaderNodeEmission');e.inputs[0].default_value=(*col,1);o=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(e.outputs[0],o.inputs['Surface']);return m
ink=em('ink',(.015,.03,.023));muted=em('muted',(.10,.13,.11));paper=em('paper',(.98,.97,.94));oakmat=em('oak',(.84,.66,.40));fridge=em('fridge',(.70,.24,.17));route=em('route',(.70,.84,.64));existing=em('existing',(.61,.65,.61));blue=em('dining surface',(.40,.62,.72));red=em('short connector',(.72,.39,.30))
font=bpy.data.fonts.load('C:/Windows/Fonts/msyh.ttc')
def rect(x,y,w,h,m,z=0):
 bpy.ops.mesh.primitive_plane_add(size=1,location=((x+w/2)/1000,(y-h/2)/1000,z));o=bpy.context.object;o.scale=(w/1000,h/1000,1);o.data.materials.append(m)
def label(t,x,y,size=85,m=ink):
 c=bpy.data.curves.new('label','FONT');c.body=t;c.font=font;c.size=size/1000;o=bpy.data.objects.new('label',c);scene.collection.objects.link(o);o.location=(x/1000,y/1000,.1);o.data.materials.append(m)
def panel(px,new):
 def r(u,v,w,d,m,z=.02):rect(px+3082-v-d,-u,d,w,m,z)
 rect(px,72.5,3082,3545,paper);r(-72.5,2682,3545,400,existing)
 vv=1950 if new else 2000;r(-72.5,vv,3545,2682-vv,route,.01)
 r(140,50,920,750,fridge);r(1200,0,2200,800,oakmat,.03)
 r(1200,800,350 if new else 450,600,red,.04)
 r(1000 if new else 1200,1400,1800 if new else 1400,550 if new else 600,blue,.04)
 r(3472.5,0,10,1691,existing,.05)
 label('冰箱',px+2370,-600,100)
 label('内侧净深仍600',px+1800,-2050,83)
 label('连接宽350' if new else '连接宽450',px+1740,-1260,84)
 label('餐面1800×550' if new else '餐面1400×600',px+1020,-1740,84)
 label('外净距732' if new else '外净距682',px+350,-2240,83)
 label('未排座椅',px+390,-2420,83,m=muted)
 label('门前约673' if new else '门前约873',px+1110,-3250,83)
 if new:label('两端各延200',px+980,-2920,82)
panel(300,False);panel(4000,True)
label('连接臂收窄、略缩短，长边成为主要用餐面',300,1030,140)
label('原10与新11：保持内部600取物净深，主模型和现有家具位置不变。',300,780,98,muted)
label('原10：较宽连接臂、短餐面',300,345,110);label('新11：短窄连接、长餐面',4000,345,110)
label('红连接：宽450→350；柜面至外沿总外伸1200→1150，仅缩50，避免压缩内部净深。',300,-3880,93)
label('蓝餐面：1400×600→1800×550；生活端、厨房端各延200，继续同色880高。',300,-4100,93)
label('内侧仅单人取物，不是烹饪过道；本轮不排椅凳，不能把空场净距当作就座后净距。',300,-4320,91,muted)
label('台面仍是880高的窄餐台；现场、冰箱全开门、抽屉站位与座椅动作待后续核对。单位mm。',300,-4540,91,muted)
bpy.ops.object.camera_add(location=(3.8,-1.55,15));cam=bpy.context.object;cam.rotation_euler=(Vector((3.8,-1.55,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=8.65;scene.camera=cam
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/'短连接长餐面-前后尺寸对照.png');bpy.ops.render.render(write_still=True)
print('SHORT_LINK_LONG_TABLE_COMPLETE',json.dumps(readback,ensure_ascii=False))
