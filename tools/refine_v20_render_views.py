import bpy,json,time
from pathlib import Path
from mathutils import Vector
R=Path('D:/AI-Yang.cn/HomeDesign');OUT=R/'07_renders/v20-integrated-native';manifest=R/'09_delivery/main-integration-v20/渲染记录.json'
bpy.ops.wm.open_mainfile(filepath=str(R/'06_blender/home-v20-render-source.blend'));s=bpy.context.scene
pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='OPTIX';pref.get_devices()
for device in pref.devices:device.use=device.type!='CPU'
s.cycles.device='GPU';s.cycles.denoiser='OPTIX'
cam=bpy.data.objects['v20 · 餐岛与餐边柜'];cam.location=(.63,-9.55,2.10);cam.rotation_euler=(Vector((2.25,-8.00,1.05))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=16
bpy.data.objects['v13 · 360 餐厅'].location=(.77,-8.85,1.60)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'06_blender/home-v20-render-source.blend'))
records=json.loads(manifest.read_text(encoding='utf-8'))
for ident,name,w,h,mode in [('dining','v20 · 餐岛与餐边柜',2100,1400,0),('dining-pano','v13 · 360 餐厅',4096,2048,0),('overview-observation','v20 · 整合观察副本',2200,1800,0)]:
 if ident=='overview-observation':
  for o in s.objects:
   if o.get('finished_plane_mm')==2750 or o.name.startswith('表现用顶面'):o.hide_render=True
   if o.get('home_design_role') in ['wall','glass','window_frame'] and o.type=='MESH':
    pts=[o.matrix_world@v.co for v in o.data.vertices]
    if min(v.z for v in pts)>=1.2:o.hide_render=True
    else:
     o.data=o.data.copy();inv=o.matrix_world.inverted()
     for v in o.data.vertices:
      q=o.matrix_world@v.co;q.z=min(q.z,1.2);v.co=inv@q
 s.camera=bpy.data.objects[name];s['lighting_scene_v19']=mode;s.update_tag();s.frame_set(1);bpy.context.view_layer.update();s.view_settings.exposure=.8;s.render.resolution_x=w;s.render.resolution_y=h;s.render.filepath=str(OUT/f'{ident}-native.png' if ident!='overview-observation' else OUT/'overview-observation.png');start=time.time();bpy.ops.render.render(write_still=True)
 for rec in records:
  if rec['id']==ident:rec.update(path=Path(s.render.filepath).relative_to(R).as_posix(),resolution=[w,h],lightingMode=mode,camera=list(s.camera.location),seconds=round(time.time()-start,1))
 manifest.write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8');print('V20_REFINED_VIEW',ident,flush=True)
print('V20_REFINED_VIEWS_COMPLETE',flush=True)
