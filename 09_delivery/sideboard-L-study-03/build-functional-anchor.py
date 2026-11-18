from pathlib import Path
import bpy, json, hashlib

OUT=Path('D:/AI-Yang.cn/HomeDesign/09_delivery/sideboard-L-study-03')
OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath='D:/AI-Yang.cn/HomeDesign/09_delivery/sideboard-study-02/L-餐岛独立关系草模.blend')
scene=bpy.context.scene
for n in ['low-cabinet-base','low-cabinet-top','drawer-before-return','fixed-table-connection-panel',
          'coffee-end-base','coffee-end-counter','coffee-machine-placeholder','cup',
          'reachable-floating-shelf','art-frame','art-ground','art-disk','Artificial shelf task']:
    o=bpy.data.objects.get(n)
    if o: bpy.data.objects.remove(o,do_unlink=True)
white=bpy.data.materials['clean warm white'];oak=bpy.data.materials['pale oak'];wood=bpy.data.materials['walnut']
grey=bpy.data.materials['refrigerator metal']

def box(name,x,y,z,w,d,h,mat,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=((x+w/2)/1000,-(y+d/2)/1000,(z+h/2)/1000))
    o=bpy.context.object;o.name=name;o.dimensions=(w/1000,d/1000,h/1000)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat)
    if bevel:
        b=o.modifiers.new('soft-edge','BEVEL');b.width=bevel/1000;b.segments=4
        o.modifiers.new('weighted-normal','WEIGHTED_NORMAL')
    return o

# Lower storage remains real. Only the table-connection module is fixed.
for x,w in [(1200,450),(2400,1000)]:
    box('functional-lower-carcass',x,0,80,w,430,780,white,7)
    box('functional-lower-counter',x,0,860,w,450,20,oak,8)
box('L-connection-fixed-carcass',1650,0,80,750,430,640,white,5)
box('L-connection-fixed-front-no-doors',1650,430,80,750,20,640,oak,4)
box('raised-back-bridge',1650,0,720,750,280,140,white,3)
box('raised-back-counter',1650,0,860,750,300,20,oak,8)
box('left-dining-storage-door',1220,431,100,410,19,735,white,4)
for i in range(3):
    box('right-accessible-drawer-%s'%i,2720,431,100+i*245,660,19,237,white,4)
box('side-fixed-panel-near-chair',2400,431,80,300,19,780,white,3)
box('niche-wood-backing',1200,0,880,2200,15,620,wood)

# Usable upper cabinet, only to2100mm, no above-fridge storage claim.
box('upper-cabinet-carcass',1200,0,1500,2200,330,600,white,5)
for xx,w in [(1200,600),(1800,900)]:
    box('upper-closed-storage-front',xx+3,331,1503,w-6,19,594,white,3)
# A modest glass display, separate from closed plate storage.
box('display-inner-back',2718,330,1518,664,4,564,wood)
for i in range(2): box('display-shelf',2718,335,1680+i*180,664,14,8,white,1)
for xx in [2700,3382]: box('display-door-frame',xx,335,1500,18,15,600,wood,2)
for zz in [1500,2082]: box('display-door-frame',2700,335,zz,700,15,18,wood,2)
box('compact-cup-machine',2930,90,880,230,280,330,grey,13)
for xx in [3220,3320]:
    bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=.035,depth=.07,location=(xx/1000,-.34,.915))
    bpy.context.object.name='ceramic-cup';bpy.context.object.data.materials.append(white)
# Under-upper task source.
from mathutils import Vector
bpy.ops.object.light_add(type='AREA',location=(2.3,-.34,1.48));o=bpy.context.object;o.name='Artificial cabinet task'
o.data.energy=45;o.data.shape='RECTANGLE';o.data.size=1.9;o.data.size_y=.05;o.data.color=(1,.72,.46)
o.rotation_euler=(Vector((2.3,-.20,.9))-o.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath=str(OUT/'functional-L-anchor.png')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'餐边柜与L餐岛-独立草模.blend'))
bpy.ops.render.render(write_still=True)
spec={
 'date':'2026-11-05','status':'three standalone candidates; not selected; master v19 unchanged',
 'feedback_correction':'Retain substantial sideboard with lower storage, serving counter, middle niche and upper cabinets; do not replace it with a shallow console.',
 'hard_constraints':['Fridge at living-room end of selected wall','Fridge outside L; island starts from cabinet on its right','4 ordinary-height dining chairs','Full-on/off views','Do not merge into master'],
 'wall_length':3545,'overall_width':3400,'ceiling_provisional':2750,
 'fridge_zone_width':1200,'fridge_body':[920,750,1850],
 'sideboard':{'width':2200,'lower_depth':450,'upper_depth':350,'counter_height':880,'niche_clear_height':620,'upper_bottom':1500,'upper_top':2100,'upper_height':600,'closed_upper_modules':[600,900],'display_upper_width':700,'lower_independently_accessible_drawer_width':700,'left_lower_storage_width':450,'fixed_connection_width':750,'fixed_near_chair_panel_width':300},
 'L_dining':{'top_size':[1400,750],'top_height':750,'top_local_y':[300,1700],'embedded_connection_mm':150,'exposed_projection_from450base':1250,'base_step_height':130,'table_to_fridge_zone_along_wall':450,'seats':4,'knee_underside_height':720},
 'review':{'continuous_bypass_to_opposite_cab':982,'kitchen_end_occupied_chair_gap':772.5,'kitchen_end_with250pullout':522.5,'storage_connection_has_no_opening_front':True,'upper_access_near_table_requires_unoccupied_chair_position':True,'plate_storage':'450 deep lower drawer bank; upper closed modules350 deep, net sizes depend on hardware','fridge_screen':'If using ordinary appliance, screened ventilation is conditional on actual instructions and free area. No sealed filler or false universal zero-embedding claim.','high_storage':'No daily storage above fridge. Upper cabinet1500–2100: specify pull-down basket where height needs help, not a claim of hand reach.'},
 'source_model':'independent study only, never main v19','blend_sha256':hashlib.sha256((OUT/'餐边柜与L餐岛-独立草模.blend').read_bytes()).hexdigest(),
}
(OUT/'layout-parameters.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2),encoding='utf-8')
print('FUNCTIONAL_SIDEB0ARD_READY')
