from pathlib import Path
import bpy, bmesh, json, math, hashlib
from mathutils import Vector

ROOT=Path('D:/AI-Yang.cn/HomeDesign');OLD=ROOT/'09_delivery/sideboard-L-study-08';OUT=ROOT/'09_delivery/sideboard-U-study-09'
OUT.mkdir(parents=True,exist_ok=True)
spec=json.loads((OLD/'L-layout-parameters.json').read_text(encoding='utf-8'))
baseline=spec['main_baseline_sha256']
assert baseline=={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in baseline}
bpy.ops.wm.open_mainfile(filepath=str(OLD/'齐平餐边柜-外端三椅L餐岛.blend'))
scene=bpy.context.scene
white=bpy.data.materials['clean warm white'];oak=bpy.data.materials['pale oak'];wood=bpy.data.materials['walnut']
sage=bpy.data.materials['sage woven seats'];navy=bpy.data.materials['navy woven seats'];metal=bpy.data.materials['graphite appliance']
def box(name,u,v,z,w,d,h,m,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=((u+w/2)/1000,-(v+d/2)/1000,(z+h/2)/1000))
    o=bpy.context.object;o.name=name;o.dimensions=(w/1000,d/1000,h/1000)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
    if bevel:
        b=o.modifiers.new('edge radius','BEVEL');b.width=bevel/1000;b.segments=4;o.modifiers.new('weighted normal','WEIGHTED_NORMAL')
    return o
def cyl(name,u,v,z,r,h,m):
    bpy.ops.mesh.primitive_cylinder_add(vertices=40,radius=r/1000,depth=h/1000,location=(u/1000,-v/1000,(z+h/2)/1000))
    o=bpy.context.object;o.name=name;o.data.materials.append(m);return o
def parent_keep(o,parent):
    bpy.context.view_layer.update()
    mw=o.matrix_world.copy();o.parent=parent;o.matrix_parent_inverse=parent.matrix_world.inverted();o.matrix_world=mw
    bpy.context.view_layer.update()
def rounded(points,r=60):
    out=[]
    for i,p in enumerate(points):
        a=Vector(p)-Vector(points[i-1]);a.normalize();b=Vector(points[(i+1)%len(points)])-Vector(p);b.normalize()
        rr=3 if p[1]==0 else (5 if p[0] in (1200,3400) else r)
        c=Vector(p)-a*rr+b*rr;t=Vector(p)-a*rr-c
        start=math.atan2(t.y,t.x);turn=math.pi/2*(1 if a.x*b.y-a.y*b.x>0 else -1)
        for j in range(10):
            ang=start+turn*j/9;out.append((c.x+rr*math.cos(ang),c.y+rr*math.sin(ang)))
    return out
def prism(name,points,z,h,m):
    n=len(points);verts=[(u/1000,-v/1000,zz/1000) for zz in (z,z+h) for u,v in points]
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(mesh);bm.free()
    o=bpy.data.objects.new(name,mesh);scene.collection.objects.link(o);o.data.materials.append(m);return o

remove_prefix=('counter-','actual-compact-L-top','connection-end-','connection-lower-','connection-rear-',
    'walnut-niche-back','closed-slim-','upper-usable-','upper-solid-','right-solid-upper-',
    'hidden-connection-','L-recessed-','L-pedestal-','niche-led-profile','outside-living-chair-','outside-kitchen-chair-')
for o in list(scene.objects):
    if o.name.startswith(remove_prefix):bpy.data.objects.remove(o,do_unlink=True)
    elif o.name=='sideboard-right-end':bpy.data.objects.remove(o,do_unlink=True)

# Actual overlay-door carcass ends at780; do not duplicate outer faces at3400/800.
box('right-end-lower-09',3382,0,0,18,780,850,white,3)
box('right-end-upper-09',3382,0,880,18,780,1820,white,3)
for nm in ('base-back','base-floor','base-plinth'):
    o=bpy.data.objects[nm];o.dimensions.x=2.182;o.location.x=(1200+2182/2)/1000

# Same880 top everywhere. Base edges end850 under a30-thick continuous U, with no old750 step.
for o in scene.objects:
    if o.name.startswith(('base-back','base-vertical')):
        o.dimensions.z=.770;o.location.z=(80+770/2)/1000
    elif o.name.startswith(('left-fridge-buffer-fixed-front','lower-solid-door')):
        o.dimensions.z=.764;o.location.z=(83+764/2)/1000
    elif o.name=='connection-fixed-front':
        o.dimensions.z=.764;o.location.z=(83+764/2)/1000
box('connection-fixed-support-09',1600,238,98,450,542,752,white)
box('base-vertical-at-join-09',2032,238,80,18,542,770,white)
poly=[(1200,0),(3400,0),(3400,800),(2050,800),(2050,1400),(2400,1400),(2400,2000),(1600,2000),(1600,800),(1200,800)]
top=prism('continuous-U-top-880-09',rounded(poly),850,30,oak)
b=top.modifiers.new('soft arris','BEVEL');b.width=.003;b.segments=3;top.modifiers.new('weighted normal','WEIGHTED_NORMAL')
box('hidden-U-arm-support-09',1640,650,815,300,1220,30,wood,3)
cyl('offset-U-round-support-09',2020,1900,0,50,820,wood)
cyl('offset-U-support-plate-09',2020,1900,820,90,30,wood)

# Red-marked tall door is removed: the same open niche now continues through all2200.
# Pale oak unifies the U top, niche lining and thin closed band. White cabinet fronts remain.
box('continuous-oak-niche-back-09',1200,450,880,2182,18,600,oak)
box('continuous-slim-band-body-09',1200,580,1480,2182,201,250,oak)
modules=[dict(u=1200,w=600),dict(u=1800,w=500),dict(u=2300,w=500),dict(u=2800,w=600)]
for i,m in enumerate(modules):
    u,w=m['u'],m['w'];idx=i+1
    box(f'slim-flap-{idx}-09',u+3,781,1483,w-6,19,244,oak,3)
    # Four complete upper doors, no separate2203-2700 high door. True open carcass panels inside.
    for a in (u,u+w-18):
        if a!=3382:box(f'upper-{idx}-side-09',a,450,1730,18,330,970,white)
    box(f'upper-{idx}-back-09',u+18,450,1748,w-36,18,934,white)
    for z in (1730,2682):box(f'upper-{idx}-horizontal-09',u+18,468,z,w-36,312,18,white)
    door=box(f'complete-upper-door-{idx}-09',u+3,781,1733,w-6,19,964,white,3)
    hinge=bpy.data.objects.new(f'upper-door-hinge-{idx}-09',None);scene.collection.objects.link(hinge);hinge.location=(u/1000,-.8,1.733)
    parent_keep(door,hinge)
    # Low-position recessed pull, not a new independent top cupboard handle.
    pull=box(f'upper-door-low-pull-{idx}-09',u+w-55,801,1755,22,4,70,wood,2);parent_keep(pull,hinge)
    assembly=bpy.data.objects.new(f'pulldown-assembly-{idx}-09',None);scene.collection.objects.link(assembly)
    assembly['status']='schematic pull-down principle, not manufacturer-certified kinematics'
    parts=[]
    for z in (1890,2114):
        parts.append(box(f'pulldown-{idx}-tray',u+50,500,z,w-100,267,15,oak,3))
        parts.append(box(f'pulldown-{idx}-front-rail',u+50,752,z+15,w-100,15,65,metal,3))
    for a in (u+28,u+w-43):
        parts.append(box(f'pulldown-{idx}-side-mechanism',a,500,1850,15,267,565,metal,3))
    parts.append(box(f'pulldown-{idx}-handle',u+90,775,1770,w-180,18,22,wood,5))
    for p in parts:parent_keep(p,assembly)
    if i==3:
        hinge.rotation_euler.z=0;hinge.keyframe_insert(data_path='rotation_euler',frame=1)
        hinge.rotation_euler.z=math.radians(-100);hinge.keyframe_insert(data_path='rotation_euler',frame=30)
        hinge.keyframe_insert(data_path='rotation_euler',frame=60)
        assembly.location=(0,0,0);assembly.keyframe_insert(data_path='location',frame=1);assembly.keyframe_insert(data_path='location',frame=30)
        assembly.location=(0,-.385,0);assembly.keyframe_insert(data_path='location',frame=45)
        assembly.location=(0,-.385,-.385);assembly.keyframe_insert(data_path='location',frame=60)
        for action in (hinge.animation_data.action,assembly.animation_data.action):
            for fc in action.fcurves:
                for point in fc.keyframe_points:point.interpolation='LINEAR'

# Three external counter-height chairs. Footprint retained; seat600, tabletop880, clear underside250.
for i,c in enumerate(spec['chairs']):
    u,v,w,d=c['u'],c['v'],c['w'],c['d'];name=c['id'];m=sage if i<2 else navy
    box(name+'-seat',u,v,560,w,d,40,m,24)
    bu=u if c['face']=='plus-u' else u+w-30
    box(name+'-back',bu,v+20,780,30,d-40,200,wood,12)
    for a in (u+40,u+w-40):
        for bb in (v+40,v+d-40):cyl(name+'-leg',a,bb,0,14,560,wood)
    # Foot bar near front of sitting direction, same chair footprint.
    fu=u+w-40 if c['face']=='plus-u' else u+40
    box(name+'-footrest',fu-12,v+40,210,24,d-80,24,wood,6)

box('niche-led-profile-09',1200,735,1472,2200,14,8,white)
niche=bpy.data.objects['artificial-niche'];niche.location.x=2.3;niche.data.size=2.05;niche.data.energy=45
niche.rotation_euler=(Vector((2.3,-.66,1.02))-niche.location).to_track_quat('-Z','Y').to_euler()
for i,o in enumerate(sorted([o for o in scene.objects if o.name.startswith('ceramic-cup')],key=lambda o:o.name)):
    o.location.x=(3000+i*120)/1000
cam=scene.camera;cam.location=(4.7,-4.85,3.65)
cam.rotation_euler=(Vector((1.8,-1.03,1.3))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=43
scene.render.resolution_x=1800;scene.render.resolution_y=1350;scene.cycles.samples=16
scene.frame_start=1;scene.frame_end=60;scene.frame_set(1)
scene['proposal']='Independent09; one continuous880-high pale-oak U; full-width open niche; full upper doors with pull-down storage'
scene['animation_note']='Frame1 closed; frame60 right600 module illustrative deployment; not a real product sweep certification'
scene['seating_height_mm']=600;scene['table_height_mm']=880
spec.update(date='2026-11-06',status='independent09; owner-selected U, same colour880-high surfaces, full uppers with pull-down access',
    user_confirmed=spec['user_confirmed']+['置物台与餐岛等高880','整个置物区与餐岛呈U字型、统一颜色',
       '红框处延续置物区样式','蓝框不可用高位区取消独立分格','保留完整上柜，配下拉收纳，让高处也能取物'],
    full_chair_size=[520,480,980],chair_seat_height=600,chair_footrest_height=210,
    colour_rule='continuous U tabletop, niche back and closed thin band pale oak; upper/lower opaque fronts warm white; walnut chair frames and sage/navy seats retained',
    supersedes=['08 height750 versus880 step','08 right closed tall column','08 separate right high cupboard'],
    source_annotation='references/业主U形与收纳批注.png')
spec.pop('dining_L',None)
spec['dining_U']=dict(outline=poly,top_height=880,top_underside=850,thickness=30,
    continuous_object='continuous-U-top-880-09',island_corner_radius=60,
    wall_side=[2200,800],connecting_arm_outside_cabinet=[1200,450],outside_dining_arm=[800,600],
    inward_opening='kitchen end; unequal U legs inherited to protect entry turn',inner_clear_width=600,
    material='pale oak; same material slot throughout',cabinet_table_step=0)
spec['sideboard'].update(niche_full_width=2200,right_tall_column_removed=True,thin_band_full_width=2200,
    niche_clear_width_to_end_panel=2182,closed_thin_front_v=800,
    complete_upper_modules=modules,upper_clear_inside_depth=313,upper_clear_inside_height=934,
    upper_storage_rule='only movable trays carry stored items; no separate unreachable fixed top shelf or independent high door',
    connection=dict(wall_range=[1600,2050],fixed_support_top=850,rule='support and front loading zone, not a fake operable blind cupboard'))
spec['pull_down']=dict(owner_confirmed=True,modules_nominal_widths=[600,500,500,600],
    installation_concept='two moving trays per module, full upper doors; no fixed high storage layer',
    reference='iMove-type 500/600 double tray; no specific order selected',
    internal_depth=313,internal_height=934,schematic_forward_translation=385,schematic_down_translation=385,
    closed_tray_levels=[1890,2114],illustrative_deployed_tray_levels=[1505,1729],
    animation_frames=dict(closed=1,right_door_open=30,right_basket_forward=45,right_basket_deployed=60),
    verified='basic cabinet envelope compared with manufacturer guidance; not installation approval',
    pending=['specific hardware revision','mount position and payload clearance','actual stroke and swept volume','user reach and side-access station beside connecting arm','upper door opening and lighting profiles'],
    sources=[dict(url='https://www.kesseboehmer.com/en/storage-solutions/kitchen/wall-units/imove',checked='2026-11-06',fact='pulls contents down and forward; double from710 cabinet height'),
             dict(url='https://shop.hettich.com/pl_EN/Further-products/Interior-Fittings/Wall-unit-interior-fittings/iMove-Double,-2-tier,-565-mm,-Silber/p/9207569',checked='2026-11-06',fact='example600 nominal, inside562–568, product depth267 and height565; min inside height710'),
             dict(url='https://kesseboehmer.world/download/iMove-EN.pdf',checked='2026-11-06',fact='500/600 nominal and minimum270 inside depth in example hinged configuration; historical brochure, not a current order specification')])
spec['evaluation'].update(aesthetic='continuous pale-oak U and full-width illuminated niche; no separate high right door',
    retrieval='inner600 is closed-front furniture gap only; basket deployed is a temporary retrieval operation, not a through route',
    no_unreachable_storage_promised='all upper stored items assigned to moving trays; product selection and reach still pending')
scene['parameters']=json.dumps(spec,ensure_ascii=False)
(OUT/'U-layout-parameters.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'同色等高U形餐岛-完整下拉上柜.blend'))
scene.render.filepath=str(OUT/'U形等高-实体关系参考.png');bpy.ops.render.render(write_still=True)
scene.frame_set(60);scene.render.filepath=str(OUT/'下拉收纳-实体原理示意.png');bpy.ops.render.render(write_still=True)

# Read the saved CLOSED default, not the unsaved demonstration frame.
bpy.ops.wm.open_mainfile(filepath=str(OUT/'同色等高U形餐岛-完整下拉上柜.blend'))
scene=bpy.context.scene
def bbox(o):
    pts=[o.matrix_world@Vector(v) for v in o.bound_box]
    return dict(u=[round(min(p.x for p in pts)*1000,3),round(max(p.x for p in pts)*1000,3)],
      v=[round(-max(p.y for p in pts)*1000,3),round(-min(p.y for p in pts)*1000,3)],
      h=[round(min(p.z for p in pts)*1000,3),round(max(p.z for p in pts)*1000,3)])
seats=[o for o in scene.objects if o.name.endswith('-seat')]
readback=dict(source='saved independent09 reopened',default_frame=scene.frame_current,
    top=bbox(bpy.data.objects['continuous-U-top-880-09']),top_material=bpy.data.objects['continuous-U-top-880-09'].data.materials[0].name,
    seat_count=len(seats),seats={o.name:bbox(o) for o in seats},
    upper_complete_door_count=len([o for o in scene.objects if o.name.startswith('complete-upper-door-')]),
    upper_door_bounds=[bbox(bpy.data.objects[f'complete-upper-door-{i+1}-09']) for i in range(4)],
    no_old_right_tall_column=not any(o.name.startswith('right-solid-upper-') for o in scene.objects),
    open_niche=bbox(bpy.data.objects['continuous-oak-niche-back-09']),
    old_table_step_removed=not any(o.name.startswith('actual-compact-L-top') for o in scene.objects),
    upper_tray_count=len([o for o in scene.objects if '-tray' in o.name and o.name.startswith('pulldown-')]),
    main_baseline_sha256_after={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in baseline})
assert readback['default_frame']==1 and len(seats)==3
assert readback['top']['h']==[850,880] and all(b['h'][1]==600 for b in readback['seats'].values())
assert readback['upper_complete_door_count']==4 and readback['upper_tray_count']==8
assert all(b['v']==[781,800] and b['h']==[1733,2697] for b in readback['upper_door_bounds'])
assert readback['no_old_right_tall_column'] and readback['old_table_step_removed']
assert readback['main_baseline_sha256_after']==baseline
(OUT/'model-readback.json').write_text(json.dumps(readback,ensure_ascii=False,indent=2),encoding='utf-8')

# Exact top-down U drawing, owner orientation: selected wall on right.
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE_NEXT'
scene.render.resolution_x=1500;scene.render.resolution_y=1800;scene.view_settings.view_transform='Standard'
scene.world=bpy.data.worlds.new('diagram');scene.world.color=(1,1,1)
def em(name,col):
    m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;n.clear()
    e=n.new('ShaderNodeEmission');e.inputs[0].default_value=(*col,1);o=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(e.outputs[0],o.inputs['Surface']);return m
ink=em('ink',(.015,.03,.023));muted=em('muted',(.08,.11,.09));paper=em('paper',(.98,.97,.94))
topmat=em('one pale oak U',(.84,.66,.40));fridge=em('fridge',(.70,.24,.17));seatmat=em('chairs',(.4,.6,.35))
route=em('outer route',(.70,.84,.64));existing=em('retained original cabinets',(.61,.65,.61));inside=em('retrieval',(.91,.89,.78))
font=bpy.data.fonts.load('C:/Windows/Fonts/msyh.ttc')
def rect(x,y,w,h,m,z=0):
    bpy.ops.mesh.primitive_plane_add(size=1,location=((x+w/2)/1000,(y-h/2)/1000,z));o=bpy.context.object;o.scale=(w/1000,h/1000,1);o.data.materials.append(m)
def label(t,x,y,size=85,m=ink):
    c=bpy.data.curves.new('label','FONT');c.body=t;c.font=font;c.size=size/1000
    o=bpy.data.objects.new('label',c);scene.collection.objects.link(o);o.location=(x/1000,y/1000,.1);o.data.materials.append(m)
px=350
def r(u,v,w,d,m,z=.02):rect(px+3082-v-d,-u,d,w,m,z)
rect(px,72.5,3082,3545,paper);r(-72.5,2682,3545,400,existing)
r(-72.5,2000,3545,682,route,.01);r(140,50,920,750,fridge)
r(2050,800,350,600,inside,.02)
r(1200,0,2200,800,topmat,.03);r(1600,800,450,1200,topmat,.03);r(2050,1400,350,600,topmat,.03)
for c in spec['chairs']:
    r(c['u'],c['v'],c['w'],c['d'],seatmat,.04)
    r(c['u'] if c['face']=='plus-u' else c['u']+c['w']-30,c['v']+20,30,c['d']-40,ink,.05)
label('同色、等高的 U 形餐岛',px,1030,145)
label('置物台＋连接臂＋外侧餐臂，统一高880',px,790,93)
label('红框区开放延续到右端；上柜整门＋下拉收纳',px,585,85,muted)
label('客厅端',px+1200,260,98);label('冰箱',px+2375,-600,105)
label('外通道',px+450,-2050,93);label('约682',px+465,-2220,102)
label('同色台面',px+1280,-1900,83);label('600',px+1850,-2280,86)
label('取物区',px+1825,-2440,78);label('不放椅子',px+1800,-2590,72,muted)
label('连续置物台',px+2340,-2050,91);label('长2200',px+2400,-2230,95)
label('全段深800',px+2350,-2410,91);label('三横抽',px+2420,-3070,90)
label('端椅后约703',px+1300,-3220,83)
r(3472.5,0,10,1691,existing,.05);label('餐厨门组1691／净开口另核',px+1200,-3700,80,muted)
label('中高椅：座600、带脚踏；桌底净高850，座上净空250。',px,-4020,81)
label('U内侧闭门取物宽600；下拉操作时不作为通路。',px,-4220,83)
label('平面尺寸沿用紧凑08，门端拉椅250后局部约453。',px,-4420,82,muted)
label('单位mm、模型暂拟。备用椅另收；主模型v19不变。',px,-4620,82,muted)
bpy.ops.object.camera_add(location=(1.95,-1.65,15));cam=bpy.context.object
cam.rotation_euler=(Vector((1.95,-1.65,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=6.1;scene.camera=cam
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/'同色等高U形-尺寸平面.png');bpy.ops.render.render(write_still=True)
print(json.dumps(dict(saved=str(OUT),readback='passed',top_height=880,seat_height=600,main_unchanged=True),ensure_ascii=False))
