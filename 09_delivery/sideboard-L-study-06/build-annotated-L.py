from pathlib import Path
import bpy, json, math, hashlib
from mathutils import Vector

ROOT=Path('D:/AI-Yang.cn/HomeDesign');OUT=ROOT/'09_delivery/sideboard-L-study-06';OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'09_delivery/sideboard-L-study-05/无玻璃餐边柜-L尺寸修订.blend'))
scene=bpy.context.scene
white=bpy.data.materials['clean warm white'];oak=bpy.data.materials['pale oak'];wood=bpy.data.materials['walnut']
sage=bpy.data.materials['sage woven seats'];navy=bpy.data.materials['navy woven seats']
def box(name,u,v,z,w,d,h,mat,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=((u+w/2)/1000,-(v+d/2)/1000,(z+h/2)/1000))
    o=bpy.context.object;o.name=name;o.dimensions=(w/1000,d/1000,h/1000)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat)
    if bevel:
        b=o.modifiers.new('soft edge','BEVEL');b.width=bevel/1000;b.segments=4;o.modifiers.new('normal','WEIGHTED_NORMAL')
    return o
def cyl(name,u,v,z,r,h,mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=40,radius=r/1000,depth=h/1000,location=(u/1000,-v/1000,(z+h/2)/1000))
    o=bpy.context.object;o.name=name;o.data.materials.append(mat);return o

for o in list(scene.objects):
    if o.name.startswith(('chair05-','L-dining-return','slim-table-support','hidden-connection-steel',
                          'lower-carcass-05','counter-05','left-solid-base-door-05','three-drawer-bank-',
                          'fixed-L-connection-05','rear-counter-bridge-')):
        bpy.data.objects.remove(o,do_unlink=True)
    elif o.name=='compact-cup-machine' or o.name.startswith('cup'):
        o.location.x-=.780

# Compound L tabletop. u follows wall living->kitchen; v projects leftwards into room.
# Shape is the user's blue footprint, rather than a straight table attached to a wall run.
poly=[(1350,300),(1700,300),(1700,1250),(2850,1250),(2850,1850),(1350,1850)]
def rounded(points,r=60):
    result=[]
    for i,p in enumerate(points):
        prev=points[i-1];nxt=points[(i+1)%len(points)]
        incoming=Vector((p[0]-prev[0],p[1]-prev[1]));incoming.normalize()
        outgoing=Vector((nxt[0]-p[0],nxt[1]-p[1]));outgoing.normalize()
        c=Vector(p)-incoming*r+outgoing*r;t=Vector(p)-incoming*r-c
        start=math.atan2(t.y,t.x);turn=math.pi/2*(1 if incoming.x*outgoing.y-incoming.y*outgoing.x>0 else -1)
        for n in range(9):
            a=start+turn*n/8;result.append((c.x+r*math.cos(a),c.y+r*math.sin(a)))
    return result
outline=rounded(poly)
verts=[(u/1000,-v/1000,z) for z in [.720,.750] for u,v in outline];n=len(outline)
faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
mesh=bpy.data.meshes.new('true-L-top-mesh');mesh.from_pydata(verts,[],faces);mesh.update()
o=bpy.data.objects.new('actual-L-dining-top-06',mesh);scene.collection.objects.link(o);o.data.materials.append(oak)
import bmesh
bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(mesh);bm.free()
b=o.modifiers.new('soft tabletop edge','BEVEL');b.width=.003;b.segments=3;o.modifiers.new('normal','WEIGHTED_NORMAL')
# Three real storage zones, a narrow fixed connection and the existing four stages.
box('lower-storage-left-fixed-filler-06',1200,0,80,150,430,780,white,4)
box('fixed-counter-connection-06',1350,0,80,350,430,640,white,4)
box('counter-rear-bridge-06',1350,0,720,350,280,140,white,4)
box('counter-rear-top-06',1350,0,860,350,300,20,oak,4)
box('lower-storage-working-run-06',1700,0,80,1700,430,780,white,5)
box('working-counter-06',1700,0,860,1700,450,20,oak,5)
for u in [1700,2200]:box('lower-solid-door-06',u+3,431,83,494,19,774,white,3)
for i in range(3):box('three-horizontal-drawer-06',2720,431,100+i*245,660,19,237,white,3)
for u in [1800,2730]:cyl('L-leg-support-06',u,1640,0,50,720,wood)
box('concealed-cross-arm-support-06',1410,300,690,180,1450,25,wood,3)

chairs=[
 dict(id='short-arm-chair',u=980,v=1360,w=520,d=480,face='plus-u',role='daily'),
 dict(id='inside-chair-1',u=1710,v=880,w=480,d=520,face='plus-v',role='daily'),
 dict(id='inside-chair-2',u=2310,v=880,w=480,d=520,face='plus-v',role='daily'),
 dict(id='outside-chair-4',u=2010,v=1700,w=480,d=520,face='minus-v',role='fourth-seat-trial'),
]
for i,c in enumerate(chairs):
    u,v,w,d=c['u'],c['v'],c['w'],c['d'];name=c['id']
    box(name+'-seat',u,v,430,w,d,40,sage if i<2 else navy,24)
    if c['face']=='plus-u':box(name+'-back',u,v+20,650,30,d-40,200,wood,12)
    elif c['face']=='plus-v':box(name+'-back',u+20,v,650,w-40,30,200,wood,12)
    else:box(name+'-back',u+20,v+d-30,650,w-40,30,200,wood,12)
    for a in [u+40,u+w-40]:
        for b in [v+40,v+d-40]:cyl(name+'-leg',a,b,0,14,430,wood)

# Move a small dining light to follow the long arm; this does not imply a selected fixture.
for o in scene.objects:
    if o.name.startswith('pendant-') or o.name=='Artificial pendant':o.location.x-=.150;o.location.y-=.500
camera=scene.camera
camera.location=(4.2,-3.9,3.25);camera.rotation_euler=(Vector((1.75,-.95,1.15))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type='PERSP';camera.data.lens=42
scene.render.resolution_x=1600;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
scene.cycles.samples=8;scene['proposal']='User annotated L footprint; no glass doors; four-seat circulation trial only; main v19 unchanged'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'按批注L形餐岛-独立试排.blend'))
scene.render.filepath=str(OUT/'L形餐岛-实体关系参考.png');bpy.ops.render.render(write_still=True)

def intersect(a,b):
    return max(0,min(a['u']+a['w'],b['u']+b['w'])-max(a['u'],b['u']))*max(0,min(a['v']+a['d'],b['v']+b['d'])-max(a['v'],b['v']))
for i,a in enumerate(chairs):
    for b in chairs[i+1:]:assert intersect(a,b)==0
fridge=dict(u=140,v=50,w=920,d=750)
assert all(intersect(c,fridge)==0 for c in chairs)
spec=dict(date='2026-11-05',status='independent shape/seating study; user has not selected seating mode',
    main_model_modified=False,v20_started=False,units='mm',source_wall='v19/lower-narrow-left-end',
    coordinate_mapping='u=global z-6090-72.5; v=3082-global x',
    user_markup='yellow=wall sideboard; red=fridge at living end; blue=compound L top',
    wall_length=3545,room_width=3082,opposite_existing_cabinet_depth=400,
    fridge=dict(zone=[0,1200],body=[920,750,1850],bbox=fridge,selected_model=None),
    sideboard=dict(wall_range=[1200,3400],width=2200,lower_depth=450,upper_depth=350,thin_depth=220,
                   counter_height=880,doors='opaque; no glass',four_stages_retained=True),
    dining_L=dict(outline=poly,corner_radius=60,short_arm=[1550,350],long_arm=[1500,600],height=750,thickness=30,
                  overall_bbox=dict(u=[1350,2850],v=[300,1850]),connection='first150 overlaps450deep wall cabinet; fixed350wide stem'),
    chairs=chairs,full_chair_size=[520,480,850],extra_pullout=250,
    clearances=dict(outer_walkway_with_three_daily_seats=832,outer_walkway_with_four_seated=462,
                    outer_walkway_fourth_pulled250=212,free_end_to_kitchen_boundary=622.5,
                    inner_table_edge_to_cabinet=800,inside_occupied_chair_back_to_cabinet=430,
                    inside_chair_pulled250_to_cabinet=180),
    verdict='L form fits as furniture. Four permanent occupied seats leave only462 at main passage with opposite cabinet retained. Three daily plus a temporary fourth is a conditional designer alternative, not an accepted owner decision.',
    options=['Keep opposite cabinet: three daily seats maintain832; fourth seat temporarily narrows passage to462',
             'Four permanent seats: requires extra plan change. Removing opposite400deep cabinet in the matching strip would give862 when seated; not authorized or applied'],
    limitations=['Selected wall/room sizes still provisional','Kitchen turn only622.5, not a generous entry apron',
                 'Actual fridge hinge/drawer sweep and ventilation unverified',
                 '520x480 are assumed full chair envelopes; human movement and knee space not certified',
                 'Chair pullout and lower drawer access cannot all be simultaneous',
                 'Opposite long cabinet and entry bench retained; no removal applied'])
(OUT/'L-layout-parameters.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2),encoding='utf-8')

# Native diagram, same orientation as owner's annotated crop: cabinet on right, L projecting left then down.
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE_NEXT'
scene.render.resolution_x=2300;scene.render.resolution_y=1650;scene.render.resolution_percentage=100
scene.view_settings.view_transform='Standard';scene.world=bpy.data.worlds.new('diagram');scene.world.color=(1,1,1)
def mat(name,col):
    m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;n.clear();e=n.new('ShaderNodeEmission');e.inputs[0].default_value=(*col,1);o=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(e.outputs[0],o.inputs['Surface']);return m
ink=mat('ink',(.016,.03,.022));muted=mat('muted',(.08,.11,.09));paper=mat('paper',(.96,.955,.94))
yellow=mat('sideboard yellow',(.95,.77,.23));red=mat('fridge red',(.70,.24,.17));blue=mat('island blue',(.25,.55,.84))
seat=mat('seat sage',(.48,.65,.43));navymat=mat('fourth navy',(.08,.18,.33));green=mat('route',(.69,.83,.64));grey=mat('existing',(.66,.70,.65));warn=mat('warning',(.5,.04,.025))
font=bpy.data.fonts.load('C:/Windows/Fonts/msyh.ttc')
def rect(x,y,w,h,m,z=0):
    bpy.ops.mesh.primitive_plane_add(size=1,location=((x+w/2)/1000,(y-h/2)/1000,z));o=bpy.context.object;o.scale=(w/1000,h/1000,1);o.data.materials.append(m)
def label(t,x,y,size=95,m=ink):
    c=bpy.data.curves.new('label','FONT');c.body=t;c.font=font;c.size=size/1000;o=bpy.data.objects.new('label',c);scene.collection.objects.link(o);o.location=(x/1000,y/1000,.10);o.data.materials.append(m)
def panel(px,py,four):
    def r(u,v,w,d,m,z=.02):rect(px+3082-v-d,py-u,w=d,h=w,m=m,z=z)
    rect(px,py+72.5,3082,3545,paper)
    r(-72.5,2682,3545,400,grey)
    r(-72.5,1850,3545,832,green,.01)
    r(1200,0,2200,450,yellow)
    r(140,50,920,750,red)
    r(1350,300,350,1550,blue,.03);r(1700,1250,1150,600,blue,.03)
    for c in chairs:
        if c['role']=='fourth-seat-trial' and not four:continue
        r(c['u'],c['v'],c['w'],c['d'],navymat if c['role']=='fourth-seat-trial' else seat,.04)
    label('冰箱',px+2350,py-620,100)
    label('餐边柜',px+2655,py-2200,100)
    label('实门',px+2700,py-2400,100)
    label('L 餐面',px+1300,py-2420,100)
    label('600宽',px+1280,py-2600,85)
    label('通道832' if not four else '此处仅462',px+450,py-2200,100,m=ink if not four else warn)
    label('柜前到桌沿800',px+1880,py-3050,82)
    r(3472.5,0,10,1691,grey,.05)
    label('餐厨门组1691／净开口另核',px+1380,py-3680,85)
    label('桌端至门边界约623',px+1210,py-3330,90)
panel(350,0,False);panel(4200,0,True)
label('按你的蓝色轮廓：真正转折的 L 形餐岛',350,1080,150)
label('黄色：实门餐边柜  红色：冰箱  蓝色：L餐面  绿色／深蓝：餐椅',350,805,100,muted)
label('三把在用：对侧原柜保留',350,350,120)
label('第四把也入座：外侧通道受挤',4200,350,120)
label('同一套L形：长边1500×600，连接短臂1550×350，餐面统一高750；不是两张直桌。',350,-4060,98)
label('左图是三人使用情景，并非已替业主取消第四把椅子；右图保留四人试排供比较。',350,-4300,95,muted)
label('四把常摆如需约800以上外通道，须另改对侧400深柜；本轮没有移除该柜或换鞋凳。',350,-4530,95,muted)
label('尺寸仍属模型暂拟；餐厨转弯、冰箱开门、人体活动和柜门取物需继续核对。主模型v19不变。',350,-4760,94,muted)
bpy.ops.object.camera_add(location=(3.95,-1.65,15));cam=bpy.context.object;cam.rotation_euler=(Vector((3.95,-1.65,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=9.1;scene.camera=cam
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/'按批注L形餐岛-三人四人对照.png');bpy.ops.render.render(write_still=True)
print(json.dumps(dict(output=str(OUT),clearances=spec['clearances']),ensure_ascii=False))
