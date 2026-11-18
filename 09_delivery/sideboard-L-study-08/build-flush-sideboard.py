from pathlib import Path
import bpy, bmesh, json, math, hashlib
from mathutils import Vector

ROOT = Path('D:/AI-Yang.cn/HomeDesign')
OUT = ROOT / '09_delivery/sideboard-L-study-08'
OUT.mkdir(parents=True, exist_ok=True)
baseline_files = ['06_blender/home-main-v19.blend','06_blender/active-model.json',
    '02_geometry/geometry-master-v19.json','05_style/modern-japanese-v19.json','06_blender/active-presentation.json']
baseline = {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in baseline_files}

# Local millimetres: u follows the selected wall, living -> kitchen; v projects into dining room.
poly = [(1600,650),(2050,650),(2050,1400),(2400,1400),(2400,2000),(1600,2000)]
chairs = [
    dict(id='outside-living-chair-1',u=1230,v=860,w=520,d=480,face='plus-u',role='daily'),
    dict(id='outside-living-chair-2',u=1230,v=1460,w=520,d=480,face='plus-u',role='daily'),
    dict(id='outside-kitchen-chair-3',u=2250,v=1460,w=520,d=480,face='minus-u',role='daily'),
]
spec = dict(date='2026-11-06', status='independent08; flush-front cabinet and redesigned compact L',
    user_confirmed=['L内侧只作取物，椅子放外侧','三把常用，第四把备用，优先保留通道',
                    '餐边柜与冰箱门面齐平，允许重新设计L餐岛尺寸和座位分布'],
    designer_proposal=True, main_model_modified=False,v20_started=False,units='mm',
    coordinate_mapping='u=global z-6090-72.5; v=3082-global x; Blender=(u,-v,height)/1000',
    source_wall='v19/lower-narrow-left-end',wall_length=3545,room_width=3082,measurements_provisional=True,
    opposite_existing_cabinet_depth=400,
    fridge=dict(zone=[0,1200],body=[920,750,1850],bbox=dict(u=140,v=50,w=920,d=750),
                front_plane_v=800, selected_model=None, type='ordinary two vertical doors',
                ventilation_and_full_door_sweep='unverified until a model is selected; 140 side zones are not certified installation clearances'),
    sideboard=dict(wall_range=[1200,3400],width=2200,overall_depth=800,height=2750,
        former_base_depth=450,base_depth_increase=350,front_plane_v=800,
        upper_usable_depth=350,upper_back_plane_v=450,upper_door_front_v=800,
        closed_thin_band_depth=220,closed_thin_front_v=770,
        counter_height=880,niche_height=600,niche_back_plane_v=450,niche_usable_depth=332,
        upper_stages=[dict(name='base',z=[0,880]),dict(name='open-niche',z=[880,1480]),
                      dict(name='closed-thin-flap',z=[1480,1730]),dict(name='upper',z=[1730,2700])],
        ceiling_closure=[2700,2750],doors='opaque; no glass',horizontal_drawer_count=3,
        drawer_bank_wall_range=[2700,3400],drawer_front_width=694,drawer_box_depth=550,
        upper_storage_rule='350-deep accessible storage at the front, closed rear service void; not 800-deep high shelves',
        connection=dict(wall_range=[1600,2050],table_recess_v=[650,800],lower_fixed_height=720,
                        rule='fixed load-bearing module, not an operable door; tabletop replaces the front150 of counter at this joint'),
        left_400_module='fixed panel and fridge-side buffer; not advertised as an accessible cupboard behind the chairs',
        original_reference_retained=['four stages','slim closed flap band','three horizontal drawers','dark walnut middle','light opaque doors','handleless']),
    dining_L=dict(outline=poly,corner_radius=60,height=750,thickness=30,
        short_arm_overall=[1350,450],short_arm_clear_projection=[1200,450],long_arm=[800,600],
        overall_bbox=dict(u=[1600,2400],v=[650,2000]),
        offset_support=dict(u=2020,v=1900,diameter=100),
        note='compact true L: two chairs at living-facing short arm, one at kitchen-facing free end; no chair along outer long-edge corridor'),
    chairs=chairs,full_chair_size=[520,480,850],extra_pullout=250,
    spare_chair=dict(count=1,visible_in_default=False,stored_location_mm=None,
                     rule='spare stored separately; no imaginary cabinet garage or unverified deployment position'),
    clearances=dict(inner_retrieval_closed_front=600,outer_continuous_furniture_gap=682,
        kitchen_end_chair_back_to_boundary=702.5,kitchen_end_chair_pulled250_to_boundary=452.5,
        living_end_chair_back_to_fridge_u_end=170,between_living_chairs=120,
        obsolete07_outer832=False),
    evaluation=dict(layout='compact trade-off, not generous circulation',
        no_chair_in_retrieval_strip=True,outer_long_edge_has_no_chair=True,
        retrieval='600 applies only between closed cabinet front and inner L edge; open doors/drawers need local use, not simultaneous walking',
        drawers='700-wide drawer bank is beyond L free end u2400; 550 extension still needs a person-use check near end chair',
        fridge='body no-overlap verified, door sweep and ventilation not certified',
        aesthetic='front800 creates a quiet aligned elevation; walnut niche and recess keep depth readable',
        unknowns=['site dimensions','selected refrigerator installation manual','chair model and human movement','drawer/door hardware','ceiling finished level']),
    main_baseline_sha256=baseline)
(OUT/'L-layout-parameters.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2),encoding='utf-8')

bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
def mat(name,col,rough=.55,metal=0):
    m=bpy.data.materials.new(name);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1)
    p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
    return m
white=mat('clean warm white',(.80,.78,.71));oak=mat('pale oak',(.59,.43,.25))
wood=mat('walnut',(.16,.083,.037));sage=mat('sage woven seats',(.30,.41,.25))
navy=mat('navy woven seats',(.035,.095,.16));graphite=mat('graphite appliance',(.13,.14,.14),.28,.45)
gap=mat('recess and reveal',(.045,.037,.027));wall=mat('warm white wall',(.84,.82,.76))
floor=mat('pale oak floor',(.64,.52,.36));diffuse=mat('paper light shade',(.83,.78,.64))
def box(name,u,v,z,w,d,h,m,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=((u+w/2)/1000,-(v+d/2)/1000,(z+h/2)/1000))
    o=bpy.context.object;o.name=name;o.dimensions=(w/1000,d/1000,h/1000)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
    if bevel:
        b=o.modifiers.new('edge radius','BEVEL');b.width=bevel/1000;b.segments=4
        o.modifiers.new('weighted normals','WEIGHTED_NORMAL')
    return o
def cyl(name,u,v,z,r,h,m):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=r/1000,depth=h/1000,location=(u/1000,-v/1000,(z+h/2)/1000))
    o=bpy.context.object;o.name=name;o.data.materials.append(m);return o
def rounded_outline(points,r):
    result=[]
    for i,p in enumerate(points):
        prev=points[i-1];nxt=points[(i+1)%len(points)]
        a=Vector((p[0]-prev[0],p[1]-prev[1]));a.normalize()
        b=Vector((nxt[0]-p[0],nxt[1]-p[1]));b.normalize()
        c=Vector(p)-a*r+b*r;t=Vector(p)-a*r-c
        start=math.atan2(t.y,t.x);turn=math.pi/2*(1 if a.x*b.y-a.y*b.x>0 else -1)
        for j in range(10):
            angle=start+turn*j/9;result.append((c.x+r*math.cos(angle),c.y+r*math.sin(angle)))
    return result
def prism(name,points,z,h,m):
    n=len(points);verts=[(u/1000,-v/1000,zz/1000) for zz in (z,z+h) for u,v in points]
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(mesh);bm.free()
    o=bpy.data.objects.new(name,mesh);scene.collection.objects.link(o);o.data.materials.append(m);return o

box('wall',-150,-120,0,3750,120,2850,wall)
box('floor',-1000,0,-40,5800,3800,40,floor)
# Existing ordinary fridge, door face800. Surround is ventilation/service finish, not high storage.
box('fridge-body',140,50,0,920,710,1850,graphite,8)
for a in (140,603):box('fridge-two-door',a,760,30,457,40,1810,graphite,5)
box('fridge-centre-reveal',598,800,30,5,1,1810,gap)
for a in (543,613):box('fridge-pull',a,801,680,18,20,430,graphite,5)
box('left-end-panel',0,0,0,24,800,2750,white,4)
box('fridge-right-side-panel',1176,0,0,24,800,2750,white,4)
box('fridge-upper-service-dark-back',24,250,1900,1152,20,800,gap)
for z in range(1910,2700,38):box('fridge-upper-removable-louvre',24,770,z,1152,30,22,white,2)
box('fridge-ceiling-closure',0,0,2700,1200,800,50,white)

# 800-deep external envelope; practical storage is front-loaded, rear cavity not counted as storage.
box('base-back',1200,220,80,2200,18,780,white)
box('base-plinth',1200,80,0,2200,660,80,wood)
for u in (1200,1582,2682):box('base-vertical',u,238,80,18,542,780,white)
box('connection-end-low-vertical',2032,238,80,18,542,640,white)
box('connection-end-rear-vertical',2032,238,720,18,412,140,white)
box('base-floor',1200,238,80,2200,542,18,white)
box('left-fridge-buffer-fixed-front',1203,781,83,394,19,774,white,3)
box('connection-fixed-front',1603,781,83,444,19,634,white,3)
# Join is cut down to720 in the front150; never intersect a full-height880 carcass with the dining top.
box('connection-lower-support',1600,650,98,450,130,622,white)
box('connection-rear-counter-body',1600,238,98,450,412,762,white)
for u in (2050,2375):box('lower-solid-door',u+3,781,83,319,19,774,white,3)
for z in (315,565):box('lower-front-storage-shelf',2050,238,z,650,542,18,white)
for i in range(3):
    z=99+i*250
    box('horizontal-drawer-front',2703,781,z,694,19,242,white,3)
    box('horizontal-drawer-box',2721,231,z+18,658,550,160,oak,3)
# Counter excluding the front150 join slot. Body panels/tops retain their actual thickness.
for name,u,w,d in [('left',1200,400,800),('rear-at-table',1600,450,650),('working',2050,1350,800)]:
    box('counter-'+name,u,0,860,w,d,20,oak,4)
box('walnut-niche-back',1200,450,880,1600,18,600,wood)
box('closed-slim-band-body',1200,550,1480,1600,201,250,wood)
for u in (1200,2000):box('closed-slim-flap-front',u+3,751,1483,794,19,244,wood,3)
box('upper-usable-350-deep',1200,450,1730,1600,330,970,white)
for u in (1200,2000):box('upper-solid-door',u+3,781,1733,794,19,964,white,3)
box('right-solid-upper-body',2800,450,880,600,330,1820,white)
for z,h in ((883,1314),(2203,494)):box('right-solid-upper-door',2803,781,z,594,19,h,white,3)
box('sideboard-right-end',3382,0,0,18,800,2750,white,4)
box('sideboard-ceiling-closure',1200,0,2700,2200,800,50,white)

top=prism('actual-compact-L-top-08',rounded_outline(poly,60),720,30,oak)
b=top.modifiers.new('soft tabletop arris','BEVEL');b.width=.003;b.segments=3
top.modifiers.new('weighted normals','WEIGHTED_NORMAL')
# Wall-supported short arm plus one inset pedestal, clear of end sitter's knees.
box('hidden-connection-steel',1640,650,685,300,1220,30,wood,3)
cyl('L-recessed-round-pedestal',2020,1900,0,50,690,wood)
cyl('L-pedestal-top-plate',2020,1900,690,90,30,wood)
for i,c in enumerate(chairs):
    u,v,w,d=c['u'],c['v'],c['w'],c['d'];name=c['id'];seatmat=sage if i<2 else navy
    box(name+'-seat',u,v,430,w,d,40,seatmat,24)
    bu=u if c['face']=='plus-u' else u+w-30
    box(name+'-back',bu,v+20,650,30,d-40,200,wood,12)
    for a in (u+40,u+w-40):
        for b in (v+40,v+d-40):cyl(name+'-leg',a,b,0,14,430,wood)

# Modest worktop objects retained to explain scale; these are not selected appliances.
box('coffee-machine-body',2400,475,880,270,290,350,graphite,12)
box('coffee-machine-drip-tray',2410,710,890,250,75,18,graphite,3)
for u in (2140,2250):cyl('ceramic-cup',u,700,880,38,85,white)
cyl('small-tray',1470,660,880,100,15,wood)
def area(name,loc,target,power,size,col):
    bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.data.color=col;return o
scene.world=bpy.data.worlds.new('soft daylight');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.76,.80,.85,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.4
area('daylight',(0,-3.2,3.7),(1.8,-.6,1),450,3.4,(1,.88,.72))
area('fill',(4,-2.2,2.6),(2,-1,1),140,3,(1,.96,.90))
lamp=area('artificial-niche',(2,-.71,1.47),(2,-.65,.95),35,1.4,(1,.70,.43))
bulb=area('artificial-pendant',(1.9,-1.55,1.55),(1.9,-1.55,.75),35,.4,(1,.77,.52))
cyl('pendant-stem',1900,1550,1750,4,1000,wood)
bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,radius=.22,location=(1.9,-1.55,1.65))
o=bpy.context.object;o.name='pendant-paper-shade';o.scale.z=.48;o.data.materials.append(diffuse)
box('niche-led-profile',1200,735,1472,1600,14,8,white)

bpy.ops.object.camera_add(location=(4.5,-4.8,3.25));cam=bpy.context.object
cam.rotation_euler=(Vector((1.75,-1.05,1.3))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.lens=43;scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True
scene.render.resolution_x=1800;scene.render.resolution_y=1350;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG'
scene['proposal']='Independent08 flush-front800, three exterior end seats; main v19 untouched'
scene['retrieval_strip_mm']=600;scene['outer_furniture_gap_mm']=682
scene['spare_chair']='one stored elsewhere, location unselected; no fourth physical chair on default floor'
scene['parameters']=json.dumps(spec,ensure_ascii=False)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'齐平餐边柜-外端三椅L餐岛.blend'))
scene.render.filepath=str(OUT/'齐平柜与外端三椅-实体关系参考.png');bpy.ops.render.render(write_still=True)

# Reopen the saved editable model and derive real object bounds rather than trusting only parameters.
bpy.ops.wm.open_mainfile(filepath=str(OUT/'齐平餐边柜-外端三椅L餐岛.blend'))
def bounds(o):
    pts=[o.matrix_world@Vector(v) for v in o.bound_box]
    return dict(u=[round(min(p.x for p in pts)*1000,3),round(max(p.x for p in pts)*1000,3)],
                v=[round(-max(p.y for p in pts)*1000,3),round(-min(p.y for p in pts)*1000,3)],
                h=[round(min(p.z for p in pts)*1000,3),round(max(p.z for p in pts)*1000,3)])
seats=[o for o in bpy.context.scene.objects if o.name.endswith('-seat')]
readback=dict(source='saved08 reopened',visible_chair_count=len(seats),chairs={o.name:bounds(o) for o in seats},
    dining_top=bounds(bpy.data.objects['actual-compact-L-top-08']),
    fridge_doors=[bounds(o) for o in bpy.context.scene.objects if o.name.startswith('fridge-two-door')],
    cabinet_front=[bounds(o) for o in bpy.context.scene.objects if o.name.startswith('horizontal-drawer-front')],
    upper_front=[bounds(o) for o in bpy.context.scene.objects if o.name.startswith('upper-solid-door')],
    inner_strip_contains_no_chairs=all(not(c['u']+c['w']>2050 and c['u']<2400 and c['v']<1400 and c['v']+c['d']>800) for c in chairs),
    main_baseline_sha256_after={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in baseline_files})
assert len(seats)==3 and readback['inner_strip_contains_no_chairs']
assert baseline==readback['main_baseline_sha256_after']
assert all(abs(b['v'][1]-800)<.001 for b in readback['cabinet_front']+readback['upper_front']+readback['fridge_doors'])
for i,a in enumerate(chairs):
    for b in chairs[i+1:]:
        assert max(a['u'],b['u'])>=min(a['u']+a['w'],b['u']+b['w']) or max(a['v'],b['v'])>=min(a['v']+a['d'],b['v']+b['d'])
    f=spec['fridge']['bbox']
    assert max(a['u'],f['u'])>=min(a['u']+a['w'],f['u']+f['w']) or max(a['v'],f['v'])>=min(a['v']+a['d'],f['v']+f['d'])
(OUT/'model-readback.json').write_text(json.dumps(readback,ensure_ascii=False,indent=2),encoding='utf-8')

# Owner-plan orientation, cabinet at right. Pure dimension drawing generated from the same coordinates.
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE_NEXT';scene.render.resolution_x=1500;scene.render.resolution_y=1800
scene.view_settings.view_transform='Standard';scene.world=bpy.data.worlds.new('diagram');scene.world.color=(1,1,1)
def em(name,col):
    m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;n.clear()
    e=n.new('ShaderNodeEmission');e.inputs[0].default_value=(*col,1);o=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(e.outputs[0],o.inputs['Surface']);return m
ink=em('ink',(.015,.03,.023));muted=em('muted',(.08,.11,.09));paper=em('paper',(.98,.97,.94))
cab=em('cab yellow',(.94,.77,.3));fridge=em('fridge red',(.70,.24,.17));table=em('L blue',(.25,.55,.84))
seat=em('chair sage',(.4,.6,.35));route=em('route green',(.70,.84,.64));existing=em('old cabinets',(.61,.65,.61))
inside=em('inside retrieval',(.86,.85,.69));warn=em('compact note',(.45,.10,.04))
font=bpy.data.fonts.load('C:/Windows/Fonts/msyh.ttc')
def rect(x,y,w,h,m,z=0):
    bpy.ops.mesh.primitive_plane_add(size=1,location=((x+w/2)/1000,(y-h/2)/1000,z))
    o=bpy.context.object;o.scale=(w/1000,h/1000,1);o.data.materials.append(m)
def label(t,x,y,size=85,m=ink):
    c=bpy.data.curves.new('label','FONT');c.body=t;c.font=font;c.size=size/1000
    o=bpy.data.objects.new('label',c);scene.collection.objects.link(o);o.location=(x/1000,y/1000,.1);o.data.materials.append(m)
px=350
def r(u,v,w,d,m,z=.02):rect(px+3082-v-d,-u,d,w,m,z)
rect(px,72.5,3082,3545,paper)
r(-72.5,2682,3545,400,existing);r(-72.5,2000,3545,682,route,.01)
r(1200,0,2200,800,cab);r(140,50,920,750,fridge)
r(2050,800,350,600,inside,.025)
r(1600,650,450,1350,table,.03);r(2050,1400,350,600,table,.03)
for c in chairs:r(c['u'],c['v'],c['w'],c['d'],seat,.04)
# Simple chair backs clarify direction; the four-piece chair projection is not a person envelope.
for c in chairs:
    r(c['u'] if c['face']=='plus-u' else c['u']+c['w']-30,c['v']+20,30,c['d']-40,ink,.05)
r(3472.5,0,10,1691,existing,.05)
label('柜体与冰箱门面齐平',px,1030,150)
label('紧凑L餐岛｜两把在客厅端，一把在厨房端',px,790,91)
label('L内侧不摆椅子；对侧通长柜与换鞋区保留',px,585,87,muted)
label('客厅端',px+1200,260,98)
label('冰箱',px+2375,-600,106)
label('外侧通道',px+440,-2050,89);label('约682',px+465,-2220,102)
label('1200',px+1370,-1900,86);label('600',px+1850,-2310,80)
label('取物',px+1850,-2470,80);label('非座位',px+1820,-2610,70,muted)
label('实门柜',px+2420,-2100,102);label('深800',px+2420,-2275,102)
label('三横抽',px+2420,-3070,90)
label('端椅后约703',px+1300,-3220,83)
label('餐厨门组1691／实际净开口另核',px+1180,-3700,79,muted)
label('柜段2200 × 深800 × 高2750；冰箱门前平面为800。',px,-4020,83)
label('短臂外包1350×450；长臂800×600；餐高750。',px,-4220,83)
label('682为家具净距；端椅额外拉250时，门前局部约453。',px,-4420,81,warn)
label('尺寸为模型暂拟；备用椅另收。独立试排，主模型v19不变。',px,-4620,80,muted)
bpy.ops.object.camera_add(location=(1.95,-1.65,15));cam=bpy.context.object
cam.rotation_euler=(Vector((1.95,-1.65,0))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO';cam.data.ortho_scale=6.1;scene.camera=cam
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/'齐平柜-三椅全外置尺寸图.png')
bpy.ops.render.render(write_still=True)
print(json.dumps({'output':str(OUT),'readback':'passed','chair_count':len(seats),'main_unchanged':True},ensure_ascii=False))
