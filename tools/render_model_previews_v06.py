"""Render observation copies from the saved main model without saving geometry changes."""
from pathlib import Path
import bpy, hashlib, json

ROOT=Path(r'D:\AI-Yang.cn\HomeDesign')
raw=(ROOT/'02_geometry/geometry-master.json').read_bytes()
scene=bpy.context.scene
assert scene['home_design_geometry_sha256']==hashlib.sha256(raw).hexdigest()
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
try:
    prefs=bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type='OPTIX';prefs.get_devices()
    for device in prefs.devices:device.use=device.type!='CPU'
    scene.cycles.device='GPU'
except Exception as error:
    print('GPU_FALLBACK '+str(error));scene.cycles.device='CPU'
scene.render.image_settings.file_format='PNG'
scene.render.film_transparent=False
evidence=[]
for view in ['top','axonometric']:
    top=view=='top'
    scene.camera=bpy.data.objects['相机 · 正交顶视' if top else '相机 · 正交轴测']
    bpy.data.collections['01 墙体 · 高度及墙厚待核'].hide_render=not top
    bpy.data.collections['06 低墙观察副本 · 不用于几何核验'].hide_render=top
    bpy.data.collections['05 房间标记 · 仅观察用'].hide_render=not top
    scene.render.resolution_x=1400 if top else 1700
    scene.render.resolution_y=1560 if top else 1300
    scene.render.filepath=str(ROOT/'07_renders'/('model-v06-'+view+'.png'))
    bpy.ops.render.render(write_still=True)
    evidence.append(dict(view=view,file=scene.render.filepath,projection='ORTHO',full_walls=top,
                         source_sha256=scene['home_design_geometry_sha256'],scene_saved=False))
(ROOT/'logs/model-v06-preview-render.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8')
print('PREVIEWS_DONE '+json.dumps(evidence,ensure_ascii=True))
