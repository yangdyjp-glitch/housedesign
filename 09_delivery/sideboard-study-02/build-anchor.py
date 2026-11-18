from pathlib import Path
import bpy, math, json, hashlib
from mathutils import Vector

OUT=Path('D:/AI-Yang.cn/HomeDesign/09_delivery/sideboard-study-02')
OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
scene.unit_settings.system='METRIC'
scene.render.engine='CYCLES'
scene.cycles.samples=20
scene.cycles.use_denoising=True
scene.render.resolution_x=1600
scene.render.resolution_y=1200
scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('Soft daylight')
scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.78,.82,.87,1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.45
scene.view_settings.view_transform='AgX'
scene.render.image_settings.file_format='PNG'

def mat(name,color,rough=.6,metal=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
    return m
white=mat('clean warm white',(.83,.82,.77));oak=mat('pale oak',(.57,.43,.27));wood=mat('walnut',(.22,.135,.08))
floor=mat('oak floor',(.57,.46,.34));grey=mat('refrigerator metal',(.15,.17,.18),.32,.6)
dark=mat('door reveal',(.028,.034,.032));green=mat('sage woven seats',(.31,.40,.30));navy=mat('navy woven seats',(.09,.16,.22))

def box(name,x,y,z,w,d,h,material,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=((x+w/2)/1000,(y+d/2)/1000,(z+h/2)/1000))
    o=bpy.context.object;o.name=name;o.dimensions=(w/1000,d/1000,h/1000)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(material)
    if bevel:
        mod=o.modifiers.new('soft edge','BEVEL');mod.width=bevel/1000;mod.segments=5
        o.modifiers.new('weighted normals','WEIGHTED_NORMAL')
    return o

def cyl(name,x,y,z,r,h,material):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=r/1000,depth=h/1000,location=(x/1000,y/1000,(z+h/2)/1000))
    o=bpy.context.object;o.name=name;o.data.materials.append(material)
    mod=o.modifiers.new('round edge','BEVEL');mod.width=.005;mod.segments=3
    o.modifiers.new('weighted normals','WEIGHTED_NORMAL')
    return o

def look(o,at): o.rotation_euler=(Vector(at)-o.location).to_track_quat('-Z','Y').to_euler()
def area(name,loc,at,energy,size,color=(1,1,1)):
    bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name
    o.data.energy=energy;o.data.shape='DISK';o.data.size=size;o.data.color=color;look(o,at);return o

# Local x follows wall from living towards kitchen. Local y projects into dining room.
box('Independent study platform',-600,-450,-40,4700,3900,40,floor,5)
box('Provisional wall, no structural edit',-72.5,-120,0,3545,120,2750,white)
# Fridge is outside the L, at the living-room end. Body remains ordinary exposed two-door equipment.
box('fridge-body',140,50,30,920,710,1820,grey,12)
box('fridge-left-door',145,760,35,452,40,1810,grey,8)
box('fridge-right-door',603,760,35,452,40,1810,grey,8)
box('fridge-reveal',597,798,35,6,3,1810,dark)
box('fridge-surround-left',0,0,0,18,700,2750,white)
box('fridge-surround-right',1182,0,0,18,700,2750,white)
box('fixed-service-face-not-storage',0,682,2200,1200,18,550,white)
box('closed-ceiling-cap',0,0,2732,1200,700,18,white)
# A physically open louvred fascia screens the ventilation void, without sealing it.
for i in range(14):
    box('vent-louvre-%02d'%i,18,675,1850+i*25,1164,25,12,white,2)
for xx in (18,1060):
    for i in range(8):
        box('side-breathing-screen',xx+i*15,685,20,6,15,1820,white,1)
# Shallow low cabinet. Table connection is FIXED, no doors trapped by the tabletop.
box('low-cabinet-base',1200,0,80,1650,280,640,white,7)
box('low-cabinet-top',1200,0,720,1650,300,30,oak,10)
box('drawer-before-return',1220,282,105,410,18,590,white,3)
box('fixed-table-connection-panel',1650,283,80,750,17,640,oak,4)
# Daily dining-height L return:1400 projection from 300-deep cabinet, width750.
box('L-dining-return-1400x750',1650,300,720,750,1400,30,oak,65)
cyl('slim-table-support',2025,1510,0,80,720,wood)
box('hidden-connection-steel',1725,220,695,600,900,20,grey,5)
# Compact appliance spot beyond occupied chair band; only this end becomes450deep/900high.
box('coffee-end-base',2850,0,80,550,450,800,white,12)
box('coffee-end-counter',2850,0,880,550,450,20,oak,12)
box('coffee-machine-placeholder',2950,100,900,240,280,330,grey,14)
cyl('cup',3260,320,900,40,75,white)
box('reachable-floating-shelf',1350,0,1390,1450,180,28,wood,8)
# Large calm art plane rather than a small glass wine cabinet.
box('art-frame',2320,0,1620,750,35,660,wood,5)
box('art-ground',2340,35,1640,710,2,620,white)
cyl('art-disk',2500,42,1770,1,1,green)  # Color accents are intentionally minimal in proxy.

chairs=[]
for side,xx,face in [('living',1350,1),('kitchen',2250,-1)]:
    for i,yy in enumerate((450,1250)):
        midx=xx+225;midy=yy+225
        ident=f'chair-{side}-{i+1}'
        box(ident+'-seat',xx,yy,430,450,450,40,green if i==0 else navy,40)
        backx=xx if face==1 else xx+420
        box(ident+'-back',backx,yy+15,680,30,420,140,wood,20)
        for lx in (xx+45,xx+375):
            for ly in (yy+45,yy+375): cyl(ident+'-leg',lx,ly,0,15,430,wood)
        chairs.append(dict(id=ident,x=xx,y=yy,w=450,d=450,facing_x=face,occupied_overlap_under_table=150))
# Architectural pendant, never a bar-height seat arrangement.
cyl('pendant-canopy',2025,1050,2715,65,35,white)
cyl('pendant-cord',2025,1050,1770,4,945,dark)
bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,radius=1,location=(2.025,1.05,1.67))
shade=bpy.context.object;shade.name='soft paper pendant';shade.scale=(.30,.18,.11);shade.data.materials.append(white)
area('Natural window daylight',(-1.4,2.1,3.6),(1.5,.3,1.2),800,4)
area('Artificial pendant',(2.025,1.05,1.55),(2.025,1.05,.75),45,.5,(1,.72,.46))
area('Artificial shelf task',(2.05,.20,1.37),(2.0,.12,.9),35,1.3,(1,.72,.46))
# View from the dining side with the living-end fridge visibly on the LEFT.
# Logical positive depth is mapped to Blender negative Y only for this study.
for obj in list(scene.objects):
    obj.location.y=-obj.location.y
    if obj.type=='MESH': obj.scale.y=-obj.scale.y
look(bpy.data.objects['Natural window daylight'],(1.5,-.3,1.2))
look(bpy.data.objects['Artificial pendant'],(2.025,-1.05,.75))
look(bpy.data.objects['Artificial shelf task'],(2.0,-.12,.9))
bpy.ops.object.camera_add(location=(5.1,-6.0,3.4))
cam=bpy.context.object;cam.name='study three-quarter camera';cam.data.type='ORTHO';cam.data.ortho_scale=5.1
look(cam,(1.72,-.72,1.20));scene.camera=cam
scene.render.filepath=str(OUT/'L-geometry-anchor.png')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'L-餐岛独立关系草模.blend'))
bpy.ops.render.render(write_still=True)
data={
 'date':'2026-11-05','status':'independent proposal, not owner selected, no v19 merge',
 'coordinates':'local x=global z-6090-72.5; local y=3082-global x; mm',
 'source_wall':'geometry-master-v19.json / lower-narrow-left-end','wall_length':3545,'cabinet_span':3400,'height_provisional':2750,
 'fridge':{'zone':[0,1200],'appliance':[920,750,1850],'front_from_wall':800,'outside_L':True,'position':'living end','upper_region':'ventilated removable fixed service fascia, no overhead storage doors','ventilation_status':'screen opening, free area, manufacturer approval and exact model still unverified; no zero-embedding claim'},
 'low_cabinet':{'x':[1200,3400],'depth':300,'height':750,'coffee_only':{'x':[2850,3400],'depth':450,'height':900}},
 'dining_return':{'x':[1650,2400],'y':[300,1700],'size':[1400,750,750],'near_fridge_buffer':450,'seats':4,'chair_arrangement':'two on each long side, no end seat','base_under_join':'fixed connection, no cupboard door blocked by table'},
 'chairs':chairs,'room_width':3082,'opposite_cabinet_depth':400,
 'clearance':{'bypass_at_table_free_end':982,'kitchen_end_occupied_chair_to_wall':772.5,'pullout_trial_extra':250,'kitchen_end_after_pullout':522.5,'not_all_actions_simultaneous':True},
 'original_master_sha256':'04f55222258c1a866e84b9eff3b7987e48f399ca520789ba458b3fa16d4dc214',
 'limitations':['Widths are provisional model data, not survey','Chair150mm overlap is normal under-table insertion in this proposal, not hidden collision clearance','Pulled chair leaves only522.5mm kitchen end; cannot claim generous simultaneous passage','Appliance hinge angle and drawer extraction unknown; must verify actual model','Observation platform and cut-away viewpoint are not entire apartment reconstruction'],
 'model_sha256':hashlib.sha256((OUT/'L-餐岛独立关系草模.blend').read_bytes()).hexdigest(),
}
(OUT/'layout-parameters.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('STUDY_ANCHOR_READY '+str(OUT))
