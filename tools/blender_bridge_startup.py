"""Initialize a managed GUI/event-loop Blender session for the official addon."""
import addon_utils, bpy, json, os

os.environ['BLENDERMCP_NO_UPDATE_CHECK']='1'
addon_utils.enable('blender_mcp',default_set=False,persistent=True)
addon_utils.enable('home_design_move',default_set=False,persistent=True)
addon=bpy.context.preferences.addons.get('blender_mcp')
if addon:addon.preferences.telemetry_consent=False
scene=bpy.context.scene
scene['HomeDesign_ManagedSession']=True
scene.blendermcp_auto_start_server=True
scene.blendermcp_port=9876
for key in ['blendermcp_use_polyhaven','blendermcp_use_hyper3d','blendermcp_use_sketchfab','blendermcp_use_tripo','blendermcp_use_meshy','blendermcp_use_polypizza','blendermcp_use_hunyuan3d']:
    if hasattr(scene,key):setattr(scene,key,False)
print('HOMEDESIGN_BRIDGE_STARTUP '+json.dumps(dict(background=bpy.app.background,port=9876,telemetry=False)))
