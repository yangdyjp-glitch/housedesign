"""Enable the reviewed addon while preserving existing Blender preferences."""
from pathlib import Path
from datetime import datetime
import addon_utils, bpy, json, shutil

root=Path(r'D:\AI-Yang.cn\HomeDesign')
prefs=Path(bpy.utils.user_resource('CONFIG'))/'userpref.blend'
if prefs.exists():
    backup=root/'logs'/('blender-userpref-before-'+datetime.now().strftime('%Y%m%d-%H%M%S')+'.blend')
    shutil.copy2(prefs,backup)
addon_utils.enable('blender_mcp',default_set=True,persistent=True)
addon=bpy.context.preferences.addons.get('blender_mcp')
if not addon:raise RuntimeError('Addon failed to enable')
addon.preferences.telemetry_consent=False
addon_utils.enable('home_design_move',default_set=True,persistent=True)
bpy.ops.wm.save_userpref()
print('HOMEDESIGN_ADDON_ENABLED '+json.dumps(dict(enabled=True,telemetry=False,preferences=str(prefs))))
