from pathlib import Path
import bpy,json,hashlib,time,math
from mathutils import Vector
R=Path('D:/AI-Yang.cn/HomeDesign');OUT=R/'07_renders/v20-complete-native';OUT.mkdir(exist_ok=True)
MODEL=R/'06_blender/home-main-v20-complete.blend';bpy.ops.wm.open_mainfile(filepath=str(MODEL));s=bpy.context.scene
pref=bpy.context.preferences.addons['cycles'].preferences
pref.compute_device_type='OPTIX';pref.get_devices()
for device in pref.devices:device.use=device.type!='CPU'
s.cycles.device='GPU';s.cycles.denoiser='OPTIX';s.render.engine='CYCLES';s.cycles.samples=48;s.cycles.use_denoising=True;s.cycles.adaptive_threshold=.05;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
def camera(name,pos,target,lens=24,ortho=None):
    bpy.ops.object.camera_add(location=pos);o=bpy.context.object;o.name=name;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=lens
    if ortho:o.data.type='ORTHO';o.data.ortho_scale=ortho
    return o.name
dining=camera('v20 full · 餐岛与餐边柜',(.63,-9.55,2.10),(2.25,-8,1.05),16)
office=camera('v20 full · 办公半墙',(6.48,-5.55,1.75),(5.65,-3,.9),25)
ceiling=camera('v20 full · 连续顶与服务带',(2.5,-7.0,1.60),(5.7,-5.40,2.48),18)
laundry=camera('v20 full · 阳台洗烘高柜',(4.65,-1.75,1.55),(6.8,-.48,1.4),24)
overview=camera('v20 full · 去顶观察',(16,-20,17),(5.4,-6.1,.4),32,17.8)
bath=camera('v20 full · 主卫门墙观察',(12,-8.0,11),(8.7,-4.7,.5),28,6.5)
bpy.data.objects['v13 · 360 餐厅'].location=(.77,-8.85,1.6)
s['photoreal_presentation_status']='same-version native anchors'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'06_blender/home-v20-complete-render-source.blend'))
views=[('living','v11 · 客厅至阳台',2100,1400,0),('living-evening','v11 · 客厅至阳台',2100,1400,1),('dining',dining,2100,1400,2),('balcony','v11 · 阳台茶席',2100,1400,0),('entry','v18 · 左手钢琴键换鞋',1400,1800,0),('office',office,2100,1400,1),('ceiling',ceiling,2100,1400,3),('laundry',laundry,1600,1800,0)]
views += [(key+'-pano','v13 · 360 '+label,4096,2048,0) for key,label in [('living','客厅'),('dining','餐厅'),('balcony','阳台'),('entry','门厅')]]
records=[]
def render(ident,cam,rx,ry,mode):
    s.camera=bpy.data.objects[cam];s['lighting_scene_v19']=mode;s.update_tag();s.frame_set(1);bpy.context.view_layer.update();s.view_settings.exposure=(.4 if ident.startswith('entry') else .8) if mode==0 else 1.0;s.render.resolution_x=rx;s.render.resolution_y=ry;s.render.filepath=str(OUT/f'{ident}-native.png');start=time.time();bpy.ops.render.render(write_still=True)
    records.append(dict(id=ident,path=Path(s.render.filepath).relative_to(R).as_posix(),resolution=[rx,ry],seconds=round(time.time()-start,1),lightingMode=mode));(R/'09_delivery/v20-complete/渲染记录.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8');print('V20_FULL_NATIVE_IMAGE',ident,flush=True)
for row in views:render(*row)
# Temporary observation only, not saved to either complete source model.
for o in s.objects:
    if o.get('ceilingElement') or o.get('home_design_role')=='mep_coordination_envelope':o.hide_render=True
    if o.get('home_design_role') in ['wall_visual_union','wall_finish_proposal','wall','glass','window_frame'] and o.type=='MESH':
        pts=[o.matrix_world@v.co for v in o.data.vertices]
        if pts and min(v.z for v in pts)>=1.2:o.hide_render=True
        else:
            o.data=o.data.copy();inv=o.matrix_world.inverted()
            for v in o.data.vertices:
                pt=o.matrix_world@v.co;pt.z=min(pt.z,1.2);v.co=inv@pt
render('overview-observation',overview,2200,1800,0)
render('bath-aligned-closed-observation',bath,1800,1800,0)
ctrl=next(o for o in s.objects if o.get('home_design_role')=='bath_door_control' and not o.get('retired_in_phase'))
ctrl['open_ratio']=1.;ctrl.update_tag();s.update_tag();s.frame_set(2);bpy.context.view_layer.update();render('bath-aligned-open-observation',bath,1800,1800,0)
print('V20_FULL_NATIVE_SET_COMPLETE',len(records),flush=True)
