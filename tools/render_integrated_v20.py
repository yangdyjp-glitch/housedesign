from pathlib import Path
import bpy,json,hashlib,time,math
from mathutils import Vector
R=Path('D:/AI-Yang.cn/HomeDesign');OUT=R/'07_renders/v20-integrated-native';OUT.mkdir(exist_ok=True)
MODEL=R/'06_blender/home-main-v20.blend';bpy.ops.wm.open_mainfile(filepath=str(MODEL));s=bpy.context.scene
assert s['home_design_revision']==20
pref=bpy.context.preferences.addons['cycles'].preferences
try:
 pref.compute_device_type='OPTIX';pref.get_devices()
 for device in pref.devices:device.use=device.type!='CPU'
 s.cycles.device='GPU';s.cycles.denoiser='OPTIX'
except Exception:s.cycles.device='CPU';s.cycles.denoiser='OPENIMAGEDENOISE'
s.render.engine='CYCLES';s.cycles.samples=48;s.cycles.use_denoising=True;s.cycles.adaptive_threshold=.05;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
def camera(name,pos,target,lens):
 bpy.ops.object.camera_add(location=pos);o=bpy.context.object;o.name=name;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=lens;return o.name
dining=camera('v20 · 餐岛与餐边柜',(0.63,-9.55,2.10),(2.25,-8.00,1.05),16)
office=camera('v20 · 办公半墙与阳台入口',(6.48,-5.55,1.75),(5.65,-3.00,.90),25)
overview=camera('v20 · 整合观察副本',(16,-20,17),(5.4,-6.1,.40),32);bpy.data.objects[overview].data.type='ORTHO';bpy.data.objects[overview].data.ortho_scale=17.8
bpy.data.objects['v13 · 360 餐厅'].location=(.77,-8.85,1.60)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'06_blender/home-v20-render-source.blend'))
views=[('living','v11 · 客厅至阳台',2100,1400,0),('dining',dining,2100,1400,2),('balcony','v11 · 阳台茶席',2100,1400,0),('entry','v18 · 左手钢琴键换鞋',1400,1800,0),('office',office,2100,1400,0)]
views += [(key+'-pano','v13 · 360 '+label,4096,2048,0) for key,label in [('living','客厅'),('dining','餐厅'),('balcony','阳台'),('entry','门厅')]]
records=[]
for ident,cam,rx,ry,mode in views:
 s.camera=bpy.data.objects[cam];s['lighting_scene_v19']=mode;s.update_tag();s.frame_set(1);bpy.context.view_layer.update();s.view_settings.exposure=(.4 if ident.startswith('entry') else .8) if mode==0 else 1.0;s.render.resolution_x=rx;s.render.resolution_y=ry
 s.render.filepath=str(OUT/f'{ident}-native.png');start=time.time();bpy.ops.render.render(write_still=True)
 records.append({'id':ident,'path':Path(s.render.filepath).relative_to(R).as_posix(),'resolution':[rx,ry],'seconds':round(time.time()-start,1),'lightingMode':mode});print('V20_NATIVE_IMAGE',ident,flush=True)
 (R/'09_delivery/main-integration-v20/渲染记录.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
# Observation-only shortened walls; never save these changes to the complete model.
for o in s.objects:
 if o.get('finished_plane_mm')==2750:o.hide_render=True
 if o.name.startswith('表现用顶面'):o.hide_render=True
 if o.get('home_design_role') in ['wall','glass','window_frame'] and o.type=='MESH':
  pts=[o.matrix_world@v.co for v in o.data.vertices]
  if pts and min(v.z for v in pts)>=1.2:o.hide_render=True
  else:
   o.data=o.data.copy();inv=o.matrix_world.inverted()
   for v in o.data.vertices:
    q=o.matrix_world@v.co;q.z=min(q.z,1.2);v.co=inv@q
s.camera=bpy.data.objects[overview];s['lighting_scene_v19']=0;s.update_tag();s.frame_set(1);bpy.context.view_layer.update();s.view_settings.exposure=.8;s.render.resolution_x=2200;s.render.resolution_y=1800;s.render.filepath=str(OUT/'overview-observation.png');bpy.ops.render.render(write_still=True)
records.append({'id':'overview-observation','path':Path(s.render.filepath).relative_to(R).as_posix(),'resolution':[2200,1800],'note':'ceiling hidden and walls shortened in observation only; complete master untouched'})
(R/'09_delivery/main-integration-v20/渲染记录.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
print('V20_NATIVE_SET_COMPLETE',len(records),flush=True)
