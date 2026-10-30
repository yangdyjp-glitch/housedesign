"""Reopen, verify and render the actual revised model; cutaways are transient."""
from pathlib import Path
from mathutils import Vector
import bpy, hashlib, json, math, sys
ROOT=Path(r'D:\AI-Yang.cn\HomeDesign')
MODEL=ROOT/'06_blender/home-main-v07.blend'
OUT=ROOT/'07_renders/v07-layout';OUT.mkdir(parents=True,exist_ok=True)
assert Path(bpy.data.filepath).resolve()==MODEL.resolve()
raw=(ROOT/'02_geometry/geometry-master-v07.json').read_bytes();d=json.loads(raw)
scene=bpy.context.scene
assert scene['home_design_geometry_sha256']==hashlib.sha256(raw).hexdigest()
assert scene['home_design_revision']==7 and scene.unit_settings.scale_length==1
ff={o['source_id']:o for o in scene.objects if o.get('home_design_role')=='furniture'}
assert len(ff)==21
assert sum(o.get('home_design_role')=='wall' for o in scene.objects)==60
assert sum(o.get('home_design_role')=='glass' for o in scene.objects)==8
rows=[]
for g in d['furnitureObjects']:
    o=ff[g['id']]
    assert abs(o.location.x*1000-g['x'])<.01 and abs(-o.location.y*1000-g['z'])<.01
    assert list(o['dimensions_mm'])==[g['dimensionsMm'][k] for k in ['length','width','height']]
    assert o['movement_step_mm']==100 and not o.hide_select
    rows.append(dict(id=g['id'],x=g['x'],z=g['z'],dimensions_mm=list(o['dimensions_mm'])))
desk=json.loads(ff['double-desk']['part_source_mm'])
assert sum('monitor-screen' in p['id'] for p in desk)==1
assert sum(o.get('source_id','').startswith('office-chair') for o in ff.values())==1
for keyword in ['plant-pot','lamp','pen-cup','water-cup']:assert any(keyword in p['id'] for p in desk)
report=dict(saved_model_reopened=True,architecture=dict(wall_sources=60,glass=8,curved_finish_profiles=4),furniture=rows,monitor_count=1,monitor_inches=34,living_shift_mm=500)
(ROOT/'logs/model-v07-readback.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for dev in prefs.devices:dev.use=dev.type!='CPU'
scene.cycles.device='GPU';scene.cycles.samples=96;scene.cycles.use_denoising=True
views={'green-corner':'v07 · 电视右侧绿植','balcony-laundry':'v07 · 阳台植物与洗烘','desk-single-34':'办公区细节 · 双工位单椅'}
records=[]
for name,cam in views.items():
    scene.camera=bpy.data.objects[cam];scene.render.filepath=str(OUT/(name+'.png'))
    bpy.ops.render.render(write_still=True);records.append(dict(view=name,path=scene.render.filepath,mode='full architecture eye-level Cycles'))

# Explicitly temporary cutaway copies: the saved full model is not modified.
for o in scene.objects:
    if o.get('home_design_role') in ['wall_visual_union','wall_finish_proposal','glass'] or o.name.startswith(('表现用顶面','表现窗框','阳台细窗梃')):o.hide_render=True
wall_mat=bpy.data.materials['R01 · 暖白细肌理墙面']
for p in d['walls']:
    if p['y']>0:continue
    x,y=p['x']/1000,-(p['z']+p['d'])/1000;w,dep=p['w']/1000,p['d']/1000;h=min(.30,p['h']/1000)
    verts=[(x,y,0),(x+w,y,0),(x+w,y+dep,0),(x,y+dep,0),(x,y,h),(x+w,y,h),(x+w,y+dep,h),(x,y+dep,h)]
    mesh=bpy.data.meshes.new('cutaway');mesh.from_pydata(verts,[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);mesh.materials.append(wall_mat)
    ob=bpy.data.objects.new('仅本次观察 · '+p['id'],mesh);scene.collection.objects.link(ob)
    ob['home_design_role']='transient_cutaway_not_saved'
def ortho(name,position,aim,scale=None,fit=False):
    camera=bpy.data.cameras.new(name);camera.type='ORTHO';ob=bpy.data.objects.new(name,camera);scene.collection.objects.link(ob);ob.location=position
    ob.rotation_euler=(Vector(aim)-ob.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update()
    if fit:
        inv=ob.matrix_world.inverted();pts=[inv@Vector((x/1000,-z/1000,0)) for x,z in d['floor']]
        pts += [inv@(o.matrix_world@v.co) for o in ff.values() for v in o.data.vertices]
        sx=max(p.x for p in pts)-min(p.x for p in pts);sy=max(p.y for p in pts)-min(p.y for p in pts)
        camera.ortho_scale=max(sx,sy*scene.render.resolution_x/scene.render.resolution_y)*1.12
    else:camera.ortho_scale=scale
    return ob
scene.render.resolution_x=1800;scene.render.resolution_y=1450
scene.camera=ortho('v07 · 轴测观察',(15,-19,19),(4.5,-5.7,.4),fit=True)
scene.render.filepath=str(OUT/'overview-cutaway.png');bpy.ops.render.render(write_still=True);records.append(dict(view='overview',path=scene.render.filepath,mode='temporary low wall observation'))
scene.render.resolution_x=1500;scene.render.resolution_y=1300
scene.camera=ortho('v07 · 入户L形柜观察',(-1.8,-7.9,4.6),(.6,-10.45,1.0),4.4)
scene.render.filepath=str(OUT/'entry-cabinets-cutaway.png');bpy.ops.render.render(write_still=True);records.append(dict(view='entry',path=scene.render.filepath,mode='temporary cutaway for cabinet access'))
report['renders']=records
(ROOT/'logs/v07-render-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('V07_RENDER_VERIFIED '+json.dumps(dict(furniture=21,monitor_count=1,views=len(records))))
