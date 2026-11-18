from pathlib import Path
import bpy,bmesh,json,math,hashlib
from mathutils import Vector

ROOT=Path('D:/AI-Yang.cn/HomeDesign');OLD=ROOT/'09_delivery/sideboard-U-study-09';OUT=ROOT/'09_delivery/sideboard-U-study-10'
OUT.mkdir(parents=True,exist_ok=True)
spec=json.loads((OLD/'U-layout-parameters.json').read_text(encoding='utf-8'));baseline=spec['main_baseline_sha256']
assert baseline=={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in baseline}
bpy.ops.wm.open_mainfile(filepath=str(OLD/'同色等高U形餐岛-完整下拉上柜.blend'));scene=bpy.context.scene;scene.frame_set(1)
white=bpy.data.materials['clean warm white'];oak=bpy.data.materials['pale oak'];wood=bpy.data.materials['walnut']
sage=bpy.data.materials['sage woven seats'];navy=bpy.data.materials['navy woven seats']
def box(name,u,v,z,w,d,h,m,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=((u+w/2)/1000,-(v+d/2)/1000,(z+h/2)/1000))
    o=bpy.context.object;o.name=name;o.dimensions=(w/1000,d/1000,h/1000);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
    if bevel:
        b=o.modifiers.new('soft edge','BEVEL');b.width=bevel/1000;b.segments=4;o.modifiers.new('weighted normal','WEIGHTED_NORMAL')
    return o
def cyl(name,u,v,z,r,h,m):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=r/1000,depth=h/1000,location=(u/1000,-v/1000,(z+h/2)/1000));o=bpy.context.object;o.name=name;o.data.materials.append(m);return o
def parent_keep(o,p):
    bpy.context.view_layer.update();mw=o.matrix_world.copy();o.parent=p;o.matrix_parent_inverse=p.matrix_world.inverted();o.matrix_world=mw;bpy.context.view_layer.update()
def rounded(points,r=60):
    out=[]
    for i,p in enumerate(points):
        a=Vector(p)-Vector(points[i-1]);a.normalize();b=Vector(points[(i+1)%len(points)])-Vector(p);b.normalize()
        rr=3 if p[1]==0 else (5 if p[0] in (1200,3400) and p[1]<=800 else r)
        c=Vector(p)-a*rr+b*rr;t=Vector(p)-a*rr-c;start=math.atan2(t.y,t.x);turn=math.pi/2*(1 if a.x*b.y-a.y*b.x>0 else -1)
        for j in range(10):
            ang=start+turn*j/9;out.append((c.x+rr*math.cos(ang),c.y+rr*math.sin(ang)))
    return out
def prism(name,points,z,h,m):
    n=len(points);verts=[(u/1000,-v/1000,zz/1000) for zz in (z,z+h) for u,v in points]
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(mesh);bm.free()
    o=bpy.data.objects.new(name,mesh);scene.collection.objects.link(o);o.data.materials.append(m);return o

for o in list(scene.objects):
    if o.name.startswith(('continuous-U-top-','hidden-U-arm-','offset-U-round-','offset-U-support-',
        'connection-fixed-','base-vertical-at-join-','left-fridge-buffer-fixed-front',
        'lower-solid-door','lower-front-storage-shelf','outside-living-chair-1-')):
        bpy.data.objects.remove(o,do_unlink=True)
    elif o.name.startswith('base-vertical') and o.location.x<2.0:bpy.data.objects.remove(o,do_unlink=True)
# The far living-end chair is retained and moved400 toward the new start; the fridge-near chair becomes a stool.
for o in scene.objects:
    if o.name.startswith('outside-living-chair-2-'):o.location.x-=.4
    elif o.name.startswith('outside-kitchen-chair-3-'):o.location.x+=.2
poly=[(1200,0),(3400,0),(3400,800),(1650,800),(1650,1400),(2600,1400),(2600,2000),(1200,2000)]
top=prism('continuous-U-top-start1200-end2600-10',rounded(poly),850,30,oak)
b=top.modifiers.new('soft arris','BEVEL');b.width=.003;b.segments=3;top.modifiers.new('weighted normal','WEIGHTED_NORMAL')
box('fixed-root-support-10',1200,238,98,450,542,752,white)
box('fixed-root-front-10',1203,781,83,444,19,764,white,3)
for u in (1200,1632):box('base-root-vertical-10',u,238,80,18,542,770,white)
for u in (1650,2175):box('accessible-lower-door-10',u+3,781,83,519,19,764,white,3)
for z in (315,565):box('lower-working-shelf-10',1650,238,z,1050,542,18,white)
box('hidden-crossarm-steel-10',1240,650,815,300,1220,30,wood,3)
box('hidden-longarm-steel-10',1500,1880,815,1030,60,30,wood,3)
support_points=[(1750,1960),(2380,1960)]
for u,v in support_points:cyl('slim-U-leg-10',u,v,0,30,850,wood)

# Third daily place: a backless400-dia counter stool completely below the600-wide dining rail at rest.
stool=bpy.data.objects.new('tuck-under-stool-10',None);scene.collection.objects.link(stool)
parts=[cyl('tuck-under-stool-seat-10',2200,1780,560,200,40,sage)]
for ang in (45,135,225,315):
    a=math.radians(ang);parts.append(cyl('tuck-under-stool-leg-10',2200+140*math.cos(a),1780+140*math.sin(a),0,14,560,wood))
bpy.ops.mesh.primitive_torus_add(major_segments=48,minor_segments=12,location=(2.2,-1.78,.21),major_radius=.16,minor_radius=.012)
o=bpy.context.object;o.name='tuck-under-stool-footrest-10';o.data.materials.append(wood);parts.append(o)
for p in parts:parent_keep(p,stool)
stool['mode']='stored at frame1; daily meal-use pulled outward300 at frame90; fourth chair remains spare offscene'
stool.location=(0,0,0);stool.keyframe_insert(data_path='location',frame=1);stool.keyframe_insert(data_path='location',frame=60)
stool.location=(0,-.3,0);stool.keyframe_insert(data_path='location',frame=90)
for fc in stool.animation_data.action.fcurves:
    for point in fc.keyframe_points:point.interpolation='LINEAR'

# Latest steering: study cabinetry and U shape only. Latent seat candidates are retained, not placed/approved.
seat_archive=bpy.data.collections.new('椅凳留档-本轮暂不排');scene.collection.children.link(seat_archive)
for o in list(scene.objects):
    if o.name.startswith(('outside-living-chair-2-','outside-kitchen-chair-3-','tuck-under-stool-')):
        for col in list(o.users_collection):col.objects.unlink(o)
        seat_archive.objects.link(o);o.hide_render=True;o.hide_set(True)

# Modelled90-degree fridge-door demonstration only; no claim of manufacturer full-drawer or120-degree access.
right_door=max([o for o in scene.objects if o.name.startswith('fridge-two-door')],key=lambda o:o.location.x)
hinge=bpy.data.objects.new('fridge-right-hinge-study-10',None);scene.collection.objects.link(hinge);hinge.location=(1.06,-.8,0)
parent_keep(right_door,hinge)
for o in list(scene.objects):
    if o.name.startswith('fridge-pull') and o.location.x>.60:parent_keep(o,hinge)
hinge.rotation_euler.z=0;hinge.keyframe_insert(data_path='rotation_euler',frame=1);hinge.keyframe_insert(data_path='rotation_euler',frame=90)
hinge.rotation_euler.z=math.pi/2;hinge.keyframe_insert(data_path='rotation_euler',frame=120)
scene.frame_end=120;scene.frame_set(1)
chairs=[dict(id='outside-living-chair-2',u=830,v=1460,w=520,d=480,face='plus-u',seat_height=600),
        dict(id='outside-kitchen-chair-3',u=2450,v=1460,w=520,d=480,face='minus-u',seat_height=600)]
spec.update(date='2026-11-06',status='independent10; cabinetry and U shape only; seating deferred by latest owner steering',
    user_confirmed=spec['user_confirmed']+['岛台从红框靠冰箱的柜段端头开始','蓝色餐臂再延长一点','目前先不考虑凳子问题'],
    seating_status='deferred; no seats shown in current renders or floor study; latent meshes/poses are not approved placements',
    source_annotation='references/业主红起点蓝延长批注.png',chairs=chairs,
    third_daily_stool=dict(type='backless round counter stool',diameter=400,seat_height=600,footrest_height=210,
        stored_centre=[2200,1780],dining_centre=[2200,2080],stored_bbox=dict(u=[2000,2400],v=[1580,1980]),
        dining_seat_bbox=dict(u=[2000,2400],v=[1880,2280]),fully_within_table_footprint_when_stored=True,
        storage_is_not_a_fourth_spare=True,body_envelope_not_certified=True),
    designer_dimensions=dict(root_shift_toward_fridge=400,far_end_extension=200,
        former_root=1600,new_root=1200,former_far_end=2400,new_far_end=2600,former_long_arm=800,new_long_arm=1400))
spec['dining_U'].update(outline=poly,continuous_object=top.name,outside_dining_arm=[1400,600],
    connecting_arm_outside_cabinet=[1200,450],support_legs=dict(diameter=60,centres=support_points),
    inner_clear_length=950,root_at_living_end_of_sideboard=True)
spec['sideboard']['connection']=dict(wall_range=[1200,1650],fixed_support_top=850,rule='corner support, not counted as an operable blind cupboard')
spec['sideboard'].pop('left_400_module',None)
spec['sideboard']['original_reference_retained']=['four stages','slim closed flap band','three horizontal drawers','light opaque doors','hidden pulls; current middle colour pale oak']
spec['clearances']=dict(inner_retrieval_closed_front=600,inner_retrieval_clear_length=950,
    outer_furniture_gap_without_seats=682,free_table_end_to_kitchen_boundary_without_seats=872.5,
    fridge_closed_front_to_table_root_u=140,fridge90_proxy_door_tip_v=1257,fridge_full_sweep_unverified=True,
    seating_clearances='not assessed this round; no seating layout adopted')
spec['evaluation'].update(layout='root and rail revised; seats intentionally excluded from current shape study',
    no_chair_in_retrieval_strip=True,fridge='90-degree right door proxy clear; actual full opening and drawers require chosen model',
    retrieval='U inside closed-front600 by950; no seats. Adjacent upper pull-down side-access still pending.',
    drawers='rail ends2600, drawer bank begins2700;100 longitudinal separation alone does not certify simultaneous access',
    meal_mode='deferred by latest owner; do not treat hidden stool/chair poses as current approved layout')
scene['parameters']=json.dumps(spec,ensure_ascii=False);scene['proposal']='Independent10: red-end start and+200 free end, seats hidden/deferred; main unchanged'
scene['animation_note']='1 default stored,60 right-upper pull-down,90 meal stool,120 proxy90-degree fridge door with stool in meal pose; product movements unverified'
(OUT/'U-layout-parameters.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'端头起步-加长U餐岛-暂不排椅凳.blend'))
scene.render.filepath=str(OUT/'端头起步加长U-实体关系参考.png');bpy.ops.render.render(write_still=True)
scene.frame_set(120);scene.render.filepath=str(OUT/'冰箱右门90度-几何试排.png');bpy.ops.render.render(write_still=True)

top_name=top.name;right_door_name=right_door.name
bpy.ops.wm.open_mainfile(filepath=str(OUT/'端头起步-加长U餐岛-暂不排椅凳.blend'));scene=bpy.context.scene
def bounds(o):
    pts=[o.matrix_world@Vector(v) for v in o.bound_box]
    return dict(u=[round(min(p.x for p in pts)*1000,3),round(max(p.x for p in pts)*1000,3)],
      v=[round(-max(p.y for p in pts)*1000,3),round(-min(p.y for p in pts)*1000,3)],
      h=[round(min(p.z for p in pts)*1000,3),round(max(p.z for p in pts)*1000,3)])
seats=[o for o in scene.objects if o.name.endswith('-seat') or o.name=='tuck-under-stool-seat-10']
bm=bmesh.new();bm.from_mesh(bpy.data.objects[top_name].data);manifold=all(e.is_manifold for e in bm.edges);bm.free()
readback=dict(source='saved independent10 reopened',default_frame=scene.frame_current,archived_seat_mesh_count=len(seats),visible_seat_count=len([o for o in seats if not o.hide_render]),
    seats={o.name:bounds(o) for o in seats},top=bounds(bpy.data.objects[top_name]),raw_top_manifold=manifold,
    main_baseline_sha256_after={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in baseline})
assert len(seats)==3 and readback['default_frame']==1 and manifold
assert readback['visible_seat_count']==0
assert all(v['h'][1]==600 for v in readback['seats'].values()) and readback['top']['h']==[850,880]
assert readback['seats']['tuck-under-stool-seat-10']['v']==[1580,1980]
assert readback['main_baseline_sha256_after']==baseline
scene.frame_set(120);bpy.context.view_layer.update();readback['fridge90_proxy']=bounds(bpy.data.objects[right_door_name])
assert readback['fridge90_proxy']['u'][1]<1200 and readback['fridge90_proxy']['v'][1]<1460
for u,v in support_points:assert math.hypot(2200-u,1780-v)>230
(OUT/'model-readback.json').write_text(json.dumps(readback,ensure_ascii=False,indent=2),encoding='utf-8')

# Exact before/after floor diagram; latest owner deferred seats, so none are drawn.
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE_NEXT'
scene.render.resolution_x=2400;scene.render.resolution_y=1650;scene.view_settings.view_transform='Standard';scene.world=bpy.data.worlds.new('diagram');scene.world.color=(1,1,1)
def em(name,col):
    m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;n.clear();e=n.new('ShaderNodeEmission');e.inputs[0].default_value=(*col,1);o=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(e.outputs[0],o.inputs['Surface']);return m
ink=em('ink',(.015,.03,.023));muted=em('muted',(.08,.11,.09));paper=em('paper',(.98,.97,.94));oakmat=em('oak',(.84,.66,.40))
fridge=em('fridge',(.70,.24,.17));seatmat=em('seats',(.4,.6,.35));route=em('route',(.70,.84,.64));existing=em('old cabinet',(.61,.65,.61));warning=em('meal occupied',(.85,.69,.55))
font=bpy.data.fonts.load('C:/Windows/Fonts/msyh.ttc')
def rect(x,y,w,h,m,z=0):
    bpy.ops.mesh.primitive_plane_add(size=1,location=((x+w/2)/1000,(y-h/2)/1000,z));o=bpy.context.object;o.scale=(w/1000,h/1000,1);o.data.materials.append(m)
def label(t,x,y,size=85,m=ink):
    c=bpy.data.curves.new('label','FONT');c.body=t;c.font=font;c.size=size/1000;o=bpy.data.objects.new('label',c);scene.collection.objects.link(o);o.location=(x/1000,y/1000,.1);o.data.materials.append(m)
def panel(px,new):
    def r(u,v,w,d,m,z=.02):rect(px+3082-v-d,-u,d,w,m,z)
    rect(px,72.5,3082,3545,paper);r(-72.5,2682,3545,400,existing)
    r(-72.5,2000,3545,682,route,.01);r(140,50,920,750,fridge)
    root,end=(1200,2600) if new else (1600,2400)
    r(1200,0,2200,800,oakmat,.03);r(root,800,450,1200,oakmat,.03);r(root+450,1400,end-root-450,600,oakmat,.03)
    label('冰箱',px+2370,-600,100);label('端头起步' if new else '原起点内退400',px+1980,-1440,84)
    label('内侧600',px+1860,-2170,87);label('取物长950' if new else '取物长350',px+1780,-2350,82)
    label('外净距682',px+410,-2050,88);label('未排座椅',px+450,-2250,85,m=muted)
    label('长臂1400' if new else '长臂800',px+1180,-1830,84);label('柜深800',px+2440,-2680,88)
    label('台面端后873' if new else '台面端后1073',px+1180,-3290,83)
    r(3472.5,0,10,1691,existing,.05)
panel(300,False);panel(4000,True)
label('从冰箱旁端头起步，餐臂再延长200',300,1050,145)
label('起点前移400：1600→1200；自由端2400→2600；全部台面继续880高、同色。',300,800,96,muted)
label('原09：起点内退，餐臂较短',300,350,110);label('新10：端头起步，外侧餐臂加长',4000,350,110)
label('蓝色餐臂延长200后，长臂外包由800变1400（包含起点前移400）。',300,-3920,98)
label('内侧取物区600×950；新台面端至餐厨边界约873，以上均未排座椅。',300,-4140,98,muted)
label('按最新要求暂不考虑椅凳；冰箱90度只是几何代理，完整开门／抽屉按最终机型核对。',300,-4360,92,muted)
label('单位mm、模型暂拟。本轮只研究柜体与台面形态；主模型v19与现有家具不变。',300,-4580,93,muted)
bpy.ops.object.camera_add(location=(3.8,-1.55,15));cam=bpy.context.object;cam.rotation_euler=(Vector((3.8,-1.55,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=8.65;scene.camera=cam
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/'端头起步加长U-前后尺寸对照.png');bpy.ops.render.render(write_still=True)
print(json.dumps(dict(output=str(OUT),readback='passed',main_unchanged=True),ensure_ascii=False))
