from pathlib import Path
import bpy, json, math, hashlib
from mathutils import Vector

ROOT=Path('D:/AI-Yang.cn/HomeDesign')
OUT=ROOT/'09_delivery/sideboard-L-study-05';OUT.mkdir(parents=True,exist_ok=True)
SOURCE=ROOT/'09_delivery/sideboard-L-study-04/四段式餐边柜-L独立提案.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene=bpy.context.scene
white=bpy.data.materials['clean warm white'];oak=bpy.data.materials['pale oak'];walnut=bpy.data.materials['walnut']
green=bpy.data.materials['sage woven seats'];navy=bpy.data.materials['navy woven seats']

def box(name,x,y,z,w,d,h,mat,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=((x+w/2)/1000,-(y+d/2)/1000,(z+h/2)/1000))
    o=bpy.context.object;o.name=name;o.dimensions=(w/1000,d/1000,h/1000)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat)
    if bevel:
        b=o.modifiers.new('soft edge','BEVEL');b.width=bevel/1000;b.segments=4
        o.modifiers.new('normal','WEIGHTED_NORMAL')
    return o
def cyl(name,x,y,z,r,h,mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=r/1000,depth=h/1000,location=(x/1000,-y/1000,(z+h/2)/1000))
    o=bpy.context.object;o.name=name;o.data.materials.append(mat);return o

# Frozen house is never opened. Only the detached study04 is edited into a sibling.
for o in list(scene.objects):
    if o.name.startswith(('chair-','functional-lower-','left-lower-','right-accessible-drawer-',
                          'side-fixed-panel-','fixed-connection-','glass-display-','glass-column-',
                          'L-connection-','raised-back-','left-dining-storage-door')):
        bpy.data.objects.remove(o,do_unlink=True)
        continue
    # Remove forward breathing fins on fridge's right; retain its verified required space as unsealed air.
    if o.name.startswith('side-breathing-screen') and o.location.x>1:
        bpy.data.objects.remove(o,do_unlink=True)
        continue
    if o.name=='fridge-surround-right':
        o.dimensions.y=.450;o.location.y=-.225
        bpy.context.view_layer.objects.active=o;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if o.name.startswith(('L-dining-return','slim-table-support','hidden-connection-steel','pendant-')) or o.name=='Artificial pendant':
        o.location.x+=.250

# Actual lower storage and a fixed table-connection segment. Drawer access needs the adjacent chair moved.
for x,w in [(1200,700),(2650,750)]:
    box('lower-carcass-05',x,0,80,w,430,780,white,5)
    box('counter-05',x,0,860,w,450,20,oak,5)
for x in [1200,1550]:box('left-solid-base-door-05',x+3,431,83,344,19,774,white,2)
for i in range(3):box('three-drawer-bank-chair-clearance-required',2670,431,100+i*245,710,19,237,white,2)
box('fixed-L-connection-05',1900,0,80,750,430,640,white,5)
box('rear-counter-bridge-05',1900,0,720,750,300,160,white,3)
box('rear-counter-bridge-top-05',1900,0,860,750,300,20,oak,3)

# Latest owner instruction supersedes the former glass-display reference in ALL three styling candidates.
box('right-closed-cabinet-back-05',2700,0,880,700,18,1820,white)
for x in [2700,3382]:box('right-closed-cabinet-side-05',x,0,880,18,330,1820,white)
for z in [880,1250,1600,1950,2200,2682]:box('right-closed-cabinet-shelf-05',2718,18,z,664,312,18,white)
for x in [2700,3050]:
    box('right-opaque-door-05',x+3,331,883,344,19,1314,white,3)
    box('right-opaque-top-door-05',x+3,331,2203,344,19,494,white,3)

chairs=[]
for label,x,face in [('fridge',1530,1),('kitchen',2500,-1)]:
    for i,y in enumerate([550,1150]):
        ident=f'chair05-{label}-{i+1}';mat=green if i==0 else navy
        box(ident+'-seat',x,y,430,520,480,40,mat,22)
        box(ident+'-back',x if face==1 else x+490,y+20,650,30,440,200,walnut,12)
        for lx in [x+45,x+475]:
            for ly in [y+45,y+435]:cyl(ident+'-leg',lx,ly,0,14,430,walnut)
        chairs.append(dict(id=ident,x=x,y=y,w=520,d=480,facing_x=face))

scene['proposal_status']='Independent study05; no glass doors; dining fit conditional; not main v19 or v20'
scene['chair_proxy']='520 full depth x480 width;150 inserted under top;250 extra pull-out trial'
scene['lower_drawer_access']='Move adjacent chair before opening; no claim of all storage simultaneously usable at four seats'
def bounds_mm(o):
    vs=[o.matrix_world@Vector(v) for v in o.bound_box]
    return dict(x=[round(min(v.x for v in vs)*1000,3),round(max(v.x for v in vs)*1000,3)],
                y_depth=[round(-max(v.y for v in vs)*1000,3),round(-min(v.y for v in vs)*1000,3)],
                height=[round(min(v.z for v in vs)*1000,3),round(max(v.z for v in vs)*1000,3)])
bpy.context.view_layer.update()
actual_table=bounds_mm(bpy.data.objects['L-dining-return-1400x750'])
assert max(abs(a-b) for a,b in zip(actual_table['x'],[1900,2650]))<.1
assert max(abs(a-b) for a,b in zip(actual_table['y_depth'],[300,1700]))<.1
actual_panel=bounds_mm(bpy.data.objects['fridge-surround-right'])
assert actual_panel['y_depth'][1]<450.1
actual_closed=[o.name for o in scene.objects if o.name.startswith('right-opaque-')]
assert len(actual_closed)==4
(OUT/'geometry-readback.json').write_text(json.dumps(dict(table=actual_table,right_panel=actual_panel,opaque_doors=actual_closed,
    model='无玻璃餐边柜-L尺寸修订.blend',kind='actual detached Blender object bounds; main model unchanged'),ensure_ascii=False,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'无玻璃餐边柜-L尺寸修订.blend'))

def overlap(a,b):
    return max(0,min(a['x']+a['w'],b['x']+b['w'])-max(a['x'],b['x']))*max(0,min(a['y']+a['d'],b['y']+b['d'])-max(a['y'],b['y']))
old_chair=dict(x=1350-250,y=450,w=450,d=450)
old_panel=dict(x=1182,y=0,w=18,d=700)
assert overlap(old_chair,old_panel)>0
fridge=dict(x=140,y=50,w=920,d=750)
new_panel=dict(x=1182,y=0,w=18,d=450)
for c in chairs:
    pulled=dict(c);pulled['x']+=-250 if c['facing_x']==1 else 250
    assert overlap(pulled,fridge)==0 and overlap(pulled,new_panel)==0
    assert pulled['x']+pulled['w']<=3472.5

spec=dict(date='2026-11-05',status='independent dimension-led revision, three styling candidates remain unselected',
    units='mm',source_wall='geometry-master-v19.json/lower-narrow-left-end',wall_length=3545,
    dining_width=3082,opposite_cabinet_depth=400,wall_span_offset=72.5,run_width=3400,
    run=dict(fridge_zone=[0,1200],sideboard=[1200,3400]),
    latest_owner_requirement='No glass sideboard doors; applies to A/B/C. Retain four stages, three drawers, opaque fronts; supersedes glass detail from original reference.',
    table=dict(size=[1400,750,750],x=[1900,2650],y=[300,1700],connection_shift_towards_kitchen=250,embedded_mm=150),
    chairs=chairs,chair_full_size=[520,480,850],under_table_insertion=150,extra_pullout_trial=250,
    fridge=dict(body=[920,750,1850],box=fridge,right_side_panel_depth=450,ventilation='Actual model clearances, free area and doors still unverified; no universal zero-gap claim'),
    measured_clearances=dict(table_end_bypass=982,table_edge_to_fridge_body=840,
        table_edge_to_kitchen_boundary=822.5,occupied_chair_back_to_fridge=470,
        occupied_chair_back_to_kitchen_boundary=452.5,extra250pullout_fridge=220,extra250pullout_kitchen=202.5),
    old_issue=dict(fridge_side_chair_back_to700deep_panel=150,pullout250_collision=True,overlap_mm2=overlap(old_chair,old_panel)),
    verdict='1400x750 tabletop fits current provisional room. Original four-chair placement has a deterministic pull-out clash. Corrected L connection and shorter fridge-side panel allow the assumed compact four chairs, but not simultaneous passage behind pulled chairs.',
    limits=['Wall/dining dimensions are provisional, not field survey','Full chair envelope selected520x480, actual product must be checked',
            'Keep main passage at table free end; side clearances are seating space, not walking lanes',
            'Three lower drawers and part of lower storage need adjacent chair moved before access',
            'Refrigerator door/drawer sweep, real ventilation, kitchen door net opening and human body trials not yet validated',
            'No glass sideboard doors; dining-kitchen glass sliding door and balcony glazing remain outside this change'],
    main_model_modified=False,v20_started=False,
    sources=[dict(title='IKEA dining guide',url='https://www.ikea.com/sg/en/rooms/dining/dining-room-guide-pub21ad8080/',use='800 table-edge clearance and600 seating width as design guidance, not local mandatory standard')])
(OUT/'fit-and-solid-doors.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2),encoding='utf-8')

# Technical drawing from the same coordinates, not an AI room illustration.
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE_NEXT'
scene.render.resolution_x=2400;scene.render.resolution_y=1520;scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('diagram world');scene.world.color=(1,1,1)
scene.view_settings.view_transform='Standard'
def emission(name,col):
    m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True
    n=m.node_tree.nodes;n.clear();e=n.new('ShaderNodeEmission');e.inputs[0].default_value=(*col,1);o=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(e.outputs[0],o.inputs['Surface']);return m
paper=emission('paper',(0.96,.955,.93));ink=emission('ink',(.018,.035,.025))
muted=emission('muted',(.08,.11,.09));cab=emission('cab',(.81,.76,.65));fr=emission('fridge',(.43,.49,.47))
tablemat=emission('table',(.72,.58,.40));chairmat=emission('chair',(.53,.67,.51));pullmat=emission('pull',(.71,.80,.68))
bad=emission('bad',(.70,.23,.16));main=emission('passage',(.79,.87,.76));wallmat=emission('wall',(.40,.45,.39))
font=bpy.data.fonts.load('C:/Windows/Fonts/msyh.ttc')
def rect(name,x,y,w,h,mat,z=0):
    bpy.ops.mesh.primitive_plane_add(size=1,location=((x+w/2)/1000,(y-h/2)/1000,z));o=bpy.context.object;o.name=name;o.scale=(w/1000,h/1000,1);o.data.materials.append(mat)
def text(t,x,y,size=90,mat=ink):
    c=bpy.data.curves.new('label','FONT');c.body=t;c.font=font;c.size=size/1000
    o=bpy.data.objects.new('label',c);scene.collection.objects.link(o);o.location=(x/1000,y/1000,.08);o.data.materials.append(mat)
def plan(origin,new):
    px,py=origin
    rect('floor',px,py,3545,3082,paper)
    rect('main bypass',px,py-1700,3545,982,main,.01)
    rect('wall',px,py+60,3545,60,wallmat,.02)
    rect('opposite cabinet',px,py-2682,3545,400,cab,.02)
    off=72.5
    rect('fridge',px+off+140,py-50,920,750,fr,.03)
    rect('fridge-side-panel',px+off+1182,py,18,450 if new else 700,bad if not new else wallmat,.04)
    rect('sideboard',px+off+1200,py,2200,450,cab,.03)
    xx=1900 if new else 1650
    rect('L dining top',px+off+xx,py-300,750,1400,tablemat,.035)
    cs=chairs if new else [dict(x=x,y=y,w=450,d=450,facing_x=f) for x,f in [(1350,1),(2250,-1)] for y in [450,1250]]
    for c in cs:
        shifted=c['x']+(-250 if c['facing_x']==1 else 250)
        rect('pullout',px+off+shifted,py-c['y'],c['w'],c['d'],pullmat,.04)
        rect('chair',px+off+c['x'],py-c['y'],c['w'],c['d'],chairmat,.05)
    text('冰箱',px+off+280,py-430,105)
    text('餐边柜 2200',px+off+1700,py-210,95)
    text('1400×750',px+off+xx+70,py-1030,85)
    text('桌端主通道约 982',px+650,py-2240,115)
    text('对侧现有柜／换鞋区深 400',px+340,py-2950,92)
    if new:
        text('桌沿至门端 823',px+off+2675,py-2000,80)
        text('桌沿至冰箱 840',px+off+1100,py-1850,82)
    else:
        rect('clash',px+off+1125,py-400,145,360,bad,.06)
        text('此椅后退会碰侧板',px+90,py-1250,96,bad)
plan((350,0),False);plan((4600,0),True)
text('1400×750 桌面能放；四椅位置需要修正',350,1050,165)
text('当前模型暂拟尺寸：餐厅横向 3082，所选柜墙 3545｜单位 mm',350,790,100,muted)
text('旧摆法：冰箱旁椅子拉出有碰撞',350,340,118,bad)
text('修订试排：连接向餐厨端移 250',4600,340,118)
text('实色为坐姿；浅绿为额外拉椅250。新试排用完整外包520深×480宽餐椅。',350,-3450,104,muted)
text('新试排椅后：冰箱侧约470／门侧约453；拉椅后约220／203，不能从椅背后通行。',350,-3670,100,muted)
text('冰箱右侧板缩至450深；主通行走桌端982。部分下柜取物仍需先移开邻椅。',350,-3890,100,muted)
text('玻璃柜门全部取消，改实门；主模型v19与全部现有家具位置不变。',350,-4110,105)
bpy.ops.object.camera_add(location=(4.25,-1.45,15))
cam=bpy.context.object;cam.rotation_euler=(0,0,0);cam.rotation_euler=(Vector((4.25,-1.45,0))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO';cam.data.ortho_scale=9.0;scene.camera=cam
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/'餐桌尺寸与四椅修订对照.png')
bpy.ops.render.render(write_still=True)
print(json.dumps({'output':str(OUT),'verdict':spec['verdict'],'clearances':spec['measured_clearances']},ensure_ascii=False))
