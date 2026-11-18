from pathlib import Path
import bpy,json
from mathutils import Vector

ROOT=Path('D:/AI-Yang.cn/HomeDesign');OLD=ROOT/'09_delivery/sideboard-L-study-06';OUT=ROOT/'09_delivery/sideboard-L-study-07'
OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(OLD/'按批注L形餐岛-独立试排.blend'))
scene=bpy.context.scene
spare=bpy.data.collections.new('备用椅-启用位置留档-收纳点待定');scene.collection.children.link(spare)
hidden=[]
for o in list(scene.objects):
    if o.name.startswith('outside-chair-4-'):
        for c in list(o.users_collection):c.objects.unlink(o)
        spare.objects.link(o);o.hide_render=True;o.hide_set(True);o['deployment_status']='Stored spare; latent coordinates record guest-use position, NOT physical storage position'
        hidden.append(o.name)
assert len(hidden)==6
visible=[o.name for o in scene.objects if o.name.endswith('-seat') and 'chair' in o.name and not o.hide_render]
assert len(visible)==3
scene['seating_owner_confirmed']='三把常用，第四把备用，优先保留通道'
scene['spare_storage_location']='TBD; never assume it remains on the main passage or fits a cabinet'
scene['proposal']='Independent L study07, confirmed seating mode only; style and dimensions not finally selected; main v19 unchanged'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'L形餐岛-三常用一备用.blend'))
scene.render.filepath=str(OUT/'三椅日常-实体关系参考.png');bpy.ops.render.render(write_still=True)
spec=json.loads((OLD/'L-layout-parameters.json').read_text(encoding='utf-8'))
spec.update(status='owner confirmed seating mode: three daily and one stored spare; independent proposal',
    seating_mode_confirmed=True,owner_reply='三把常用，第四把备用，优先保留通道',
    active_seating='three-daily',daily_visible_chair_ids=[c['id'] for c in spec['chairs'] if c['role']=='daily'],
    spare_chair=dict(id='outside-chair-4',stored_location_mm=None,visible_in_default=False,
                    deployment_pose_only=next(c for c in spec['chairs'] if c['id']=='outside-chair-4'),
                    recommendation='consider folding or stackable chair; exact model and storage place unselected',
                    storage_rule='store away from main passage; hiding in default is not proof of cabinet storage'),
    verdict='Owner selected three daily plus one stored spare. Default modeled outer furniture clearance832; fourth deployed temporarily reduces it to462. Opposite cabinet and bench remain.',
    options=['Confirmed: three daily seats, spare stored away; main furniture clearance832',
             'Guest-use only: deploy fourth to recorded outside position; passage reduces to462 and needs yielding, not a permanent arrangement'],
    main_model_modified=False,v20_started=False)
for c in spec['chairs']:
    c['visible_by_default']=c['role']=='daily'
    if c['id']=='outside-chair-4':c['role']='stored-spare-guest-deployment-only'
(OUT/'L-layout-parameters.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2),encoding='utf-8')
bpy.ops.wm.open_mainfile(filepath=str(OUT/'L形餐岛-三常用一备用.blend'))
readback=dict(source='saved independent07 reopened',visible_seat_count=len([o for o in bpy.context.scene.objects if o.name.endswith('-seat') and 'chair' in o.name and not o.hide_render]),
              spare_parts_hidden=[o.name for o in bpy.context.scene.objects if o.name.startswith('outside-chair-4-') and o.hide_render],
              storage_location_unselected=True,main_model_modified=False)
assert readback['visible_seat_count']==3 and len(readback['spare_parts_hidden'])==6
(OUT/'model-readback.json').write_text(json.dumps(readback,ensure_ascii=False,indent=2),encoding='utf-8')

# Default plan, same orientation as owner's marked plan. This is a dimension drawing, not an AI room.
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE_NEXT'
scene.render.resolution_x=1300;scene.render.resolution_y=1700;scene.render.resolution_percentage=100
scene.view_settings.view_transform='Standard';scene.world=bpy.data.worlds.new('diagram');scene.world.color=(1,1,1)
def mat(name,col):
    m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;n.clear();e=n.new('ShaderNodeEmission');e.inputs[0].default_value=(*col,1);o=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(e.outputs[0],o.inputs['Surface']);return m
ink=mat('ink',(.016,.03,.022));muted=mat('muted',(.07,.10,.08));paper=mat('paper',(.97,.96,.94))
cab=mat('cabinet',(.95,.78,.30));fridge=mat('fridge',(.70,.24,.17));table=mat('L table',(.25,.55,.84));seat=mat('seat',(.48,.65,.43));route=mat('route',(.68,.83,.63));oldcab=mat('existing cabinet',(.64,.69,.63))
font=bpy.data.fonts.load('C:/Windows/Fonts/msyh.ttc')
def rect(x,y,w,h,m,z=0):
    bpy.ops.mesh.primitive_plane_add(size=1,location=((x+w/2)/1000,(y-h/2)/1000,z));o=bpy.context.object;o.scale=(w/1000,h/1000,1);o.data.materials.append(m)
def label(t,x,y,size=88,m=ink):
    c=bpy.data.curves.new('label','FONT');c.body=t;c.font=font;c.size=size/1000;o=bpy.data.objects.new('label',c);scene.collection.objects.link(o);o.location=(x/1000,y/1000,.10);o.data.materials.append(m)
px=250;py=0
def r(u,v,w,d,m,z=.02):rect(px+3082-v-d,py-u,d,w,m,z)
rect(px,72.5,3082,3545,paper)
r(-72.5,2682,3545,400,oldcab);r(-72.5,1850,3545,832,route,.01)
r(1200,0,2200,450,cab);r(140,50,920,750,fridge)
r(1350,300,350,1550,table,.03);r(1700,1250,1150,600,table,.03)
for c in spec['chairs']:
    if c['visible_by_default']:r(c['u'],c['v'],c['w'],c['d'],seat,.04)
label('三把常用，第四把备用',px,920,135)
label('优先保留入户—客厅通道｜座位模式已确认',px,670,86,muted)
label('餐边柜实门，L轮廓及柜体尺寸沿用独立06',px,435,83,muted)
label('冰箱',px+2350,-620,105);label('餐边柜',px+2655,-2190,95);label('实门',px+2700,-2400,95)
label('主通道',px+495,-2100,103);label('约832',px+495,-2290,112)
label('L餐面',px+1300,-2420,100);label('600宽',px+1275,-2600,85)
label('柜前到桌沿800',px+1870,-3050,84);label('门前转弯约623',px+1210,-3325,87)
r(3472.5,0,10,1691,oldcab,.05);label('餐厨门组1691／净开口另核',px+1380,-3670,79)
label('备用椅平时另收，收纳点待定；不占桌外主通道。',px,-4000,84)
label('来客启用第四把时，此处会缩至约462，需要临时让行。',px,-4200,81,muted)
label('单位mm，仍为模型暂拟；主模型v19及现有家具不变。',px,-4400,81,muted)
bpy.ops.object.camera_add(location=(1.8,-1.65,15));c=bpy.context.object;c.rotation_euler=(Vector((1.8,-1.65,0))-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=5.85;scene.camera=c
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/'三常用一备用-默认平面.png');bpy.ops.render.render(write_still=True)
print(json.dumps(readback,ensure_ascii=False))
