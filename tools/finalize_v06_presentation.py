"""Finalize the render-only sibling .blend without touching the current main model."""
from pathlib import Path
import bpy
ROOT=Path(r'D:\AI-Yang.cn\HomeDesign')
path=ROOT/'06_blender'/'home-v06-presentation-v01.blend'
assert Path(bpy.data.filepath).resolve()==path.resolve()
bpy.data.collections['04 家具 · 整件选择 · 100mm'].hide_viewport=True
bpy.data.collections['08 写实表现 · 按原家具零件生成'].hide_viewport=False
scene=bpy.context.scene
scene.camera=bpy.data.objects['办公区 · 沙发后双人桌']
scene.render.filepath=str(ROOT/'07_renders'/'v06-realistic-v01'/'office-cycles.png')
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_perspective='CAMERA'
            area.spaces.active.overlay.show_overlays=False
            area.spaces.active.shading.type='MATERIAL'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(path))
print('PRESENTATION_FINALIZED '+str(path))
