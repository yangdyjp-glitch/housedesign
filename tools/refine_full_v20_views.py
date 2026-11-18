from pathlib import Path
import bpy,json,time
from mathutils import Vector
R=Path('D:/AI-Yang.cn/HomeDesign');OUT=R/'07_renders/v20-complete-native'
bpy.ops.wm.open_mainfile(filepath=str(R/'06_blender/home-v20-complete-render-source.blend'));s=bpy.context.scene
pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='OPTIX';pref.get_devices()
for device in pref.devices:device.use=device.type!='CPU'
s.cycles.device='GPU';s.cycles.denoiser='OPTIX';s.cycles.samples=48
c=bpy.data.objects['v20 full · 连续顶与服务带'];c.location=(2.0,-5.1,1.65);c.rotation_euler=(Vector((5.7,-5.4,2.45))-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=18
bpy.ops.object.camera_add(location=(.65,-9.9,1.55));shoe=bpy.context.object;shoe.name='v20 full · 右手鞋柜';shoe.rotation_euler=(Vector((.65,-11.0,1.3))-shoe.location).to_track_quat('-Z','Y').to_euler();shoe.data.lens=19
bpy.ops.wm.save_as_mainfile(filepath=str(R/'06_blender/home-v20-complete-render-source.blend'))
records=json.loads((R/'09_delivery/v20-complete/渲染记录.json').read_text(encoding='utf8'))
for ident,cam,rx,ry,mode in [('ceiling',c,2100,1400,3),('entry-shoe',shoe,1400,1800,0)]:
    s.camera=cam;s['lighting_scene_v19']=mode;s.update_tag();s.frame_set(1);bpy.context.view_layer.update();s.view_settings.exposure=.7;s.render.resolution_x=rx;s.render.resolution_y=ry;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.filepath=str(OUT/f'{ident}-native.png');start=time.time();bpy.ops.render.render(write_still=True)
    records=[x for x in records if x['id']!=ident];records.append(dict(id=ident,path=Path(s.render.filepath).relative_to(R).as_posix(),resolution=[rx,ry],lightingMode=mode,seconds=round(time.time()-start,1),reason='camera moved out of fridge proxy; no geometry change' if ident=='ceiling' else 'right shoe cabinet counterpart to left bench view'))
(R/'09_delivery/v20-complete/渲染记录.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8')
print('V20_FULL_REFINED_VIEWS_COMPLETE',flush=True)
