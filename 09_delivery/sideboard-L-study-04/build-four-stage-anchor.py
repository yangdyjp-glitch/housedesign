from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
OUT=Path('D:/AI-Yang.cn/HomeDesign/09_delivery/sideboard-L-study-04');OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath='D:/AI-Yang.cn/HomeDesign/09_delivery/sideboard-L-study-03/餐边柜与L餐岛-独立草模.blend')
for o in list(bpy.context.scene.objects):
    if o.name.startswith(('upper-','display-','niche-')) or o.name=='Artificial cabinet task':
        bpy.data.objects.remove(o,do_unlink=True)
white=bpy.data.materials['clean warm white'];wood=bpy.data.materials['walnut'];oak=bpy.data.materials['pale oak']
def box(name,x,y,z,w,d,h,mat,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=((x+w/2)/1000,-(y+d/2)/1000,(z+h/2)/1000))
    o=bpy.context.object;o.name=name;o.dimensions=(w/1000,d/1000,h/1000)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat)
    if bevel:
        b=o.modifiers.new('soft edge','BEVEL');b.width=bevel/1000;b.segments=4;o.modifiers.new('normal','WEIGHTED_NORMAL')
    return o
# The original THREE homeowner references govern this four-stage composition.
# Stage4:lower880; Stage3:open600; Stage2:thin250; Stage1:upper970+50closure.
box('stage3-walnut-work-niche',1200,0,880,1500,15,600,wood)
box('stage2-thin-cabinet',1200,0,1480,1500,205,250,wood,4)
for x,w in [(1200,600),(1800,900)]:
    box('stage2-flap-front',x+3,206,1483,w-6,14,244,wood,3)
box('stage1-upper-carcass',1200,0,1730,1500,330,970,white,4)
for x,w in [(1200,600),(1800,900)]:
    box('stage1-upper-closed-door',x+3,331,1733,w-6,19,964,white,3)
box('ceiling-matched-top-closure',1200,0,2700,2200,350,50,white)
# One glass display door / closed three-drawer lower bank; not a second wine wall.
box('glass-display-back',2700,0,880,700,18,1320,wood)
for x in [2700,3382]: box('glass-display-fixed-frame',x,335,880,18,15,1320,wood,2)
for z in [880,2182]: box('glass-display-fixed-frame',2700,335,z,700,15,18,wood,2)
for z in [1170,1480,1800]: box('glass-display-shelf',2718,20,z,664,315,12,white,2)
box('glass-column-upper-closed-cap',2700,0,2200,700,350,500,white,3)
bpy.ops.object.light_add(type='AREA',location=(1.95,-.22,1.46));o=bpy.context.object;o.name='Artificial under-thin-cabinet task'
o.data.energy=38;o.data.shape='RECTANGLE';o.data.size=1.4;o.data.size_y=.04;o.data.color=(1,.72,.46)
o.rotation_euler=(Vector((2,-.24,.89))-o.location).to_track_quat('-Z','Y').to_euler()
scene=bpy.context.scene;scene.render.filepath=str(OUT/'四段式餐边柜-L关系草模.png')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'四段式餐边柜-L独立提案.blend'))
bpy.ops.render.render(write_still=True)
spec=json.loads(Path('D:/AI-Yang.cn/HomeDesign/09_delivery/sideboard-L-study-03/layout-parameters.json').read_text(encoding='utf-8'))
spec['feedback_correction']='Original three references restored: four stages, slim flap cabinet, one glass showcase, three horizontal drawers, upper shallower than lower, deep middle/light fronts, handleless; retain L and fridge outside at living end.'
spec['sideboard'].update({'upper_bottom':1730,'upper_top':2700,'upper_height':970,'niche_clear_height':600,'thin_cabinet_bottom':1480,'thin_cabinet_height':250,'thin_cabinet_depth':220,'ceiling_closure_height':50})
spec['review']['high_storage']='No daily overhead fridge storage. Sideboard upper600/900 modules use selected pull-down hardware for lower working shelves; highest stock is low-frequency, not claimed hand-reachable. Actual lift trajectory/product still unverified.'
spec['review']['original_stool_bay']='Not included: owner cancelled banquette, requested four dining chairs and L table. Loose-chair plan does not automatically create an800x400stool garage.'
spec['source_model']='standalone four-stage concept; not main v19; source03 is intermediate'
spec['blend_sha256']=hashlib.sha256((OUT/'四段式餐边柜-L独立提案.blend').read_bytes()).hexdigest()
(OUT/'design-parameters.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2),encoding='utf-8')
print('FOUR_STAGE_READY')
