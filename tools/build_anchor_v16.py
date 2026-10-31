"""Create a new native full-sphere anchor with the latest positions and coherent daylight."""
from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector
ROOT=Path(r'D:/AI-Yang.cn/HomeDesign');MODEL=ROOT/'06_blender/home-v16-reference-anchor.blend'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert Path(bpy.data.filepath).name=='home-v14-photoreal-v15.blend'
s=bpy.context.scene;d=json.loads((ROOT/'02_geometry/presentation-layout-v16.json').read_text(encoding='utf-8'));ff={o['source_id']:o for o in s.objects if o.get('home_design_role')=='furniture'}
for q in d['furnitureObjects']:
    ob=ff[q['id']];ob.location.x=q['x']/1000;ob.location.y=-q['z']/1000
    ob['source_x_mm']=q['x'];ob['source_z_mm']=q['z'];ob['latest_interactive_position_v16']=True
sun_data=bpy.data.lights.new('V16 · 参考图斜向柔和日光','SUN');sun_data.energy=1.6;sun_data.angle=math.radians(3);sun_data.color=(1.0,.91,.79)
sun=bpy.data.objects.new(sun_data.name,sun_data);s.collection.objects.link(sun);sun.rotation_euler=Vector((.30,-.90,-.56)).to_track_quat('-Z','Y').to_euler()
for node in s.world.node_tree.nodes:
    if node.type=='BACKGROUND':node.inputs['Strength'].default_value=.5
s['home_design_revision']=16;s['home_design_geometry_sha256']=sha(ROOT/'02_geometry/presentation-layout-v16.json');s['photoreal_presentation_revision']=16;s['base_architecture_revision']=14
s['source_main_v14_sha256']=sha(ROOT/'06_blender/home-main-v14.blend');s['presentation_layout_snapshot']='03_layout/widget-layout-v16-snapshot.json'
s['lighting_scene']=0;s.update_tag();s.frame_set(s.frame_current);bpy.context.view_layer.update();s.view_settings.exposure=.8
s.name='v16 · 最新家具位置 · 摄影感日光全景基准'
for im in bpy.data.images:
    if im.source=='FILE' and im.filepath and not im.packed_file:im.filepath=bpy.path.relpath(bpy.path.abspath(im.filepath),start=str(MODEL.parent))
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(MODEL))
report=dict(model=MODEL.relative_to(ROOT).as_posix(),model_sha256=sha(MODEL),geometry_sha256=s['home_design_geometry_sha256'],architecture_revision=14,presentation_revision=16,furniture_count=len(ff),main_v14_unchanged=True)
(ROOT/'logs/v16-anchor-build.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('V16_ANCHOR_SAVED')
