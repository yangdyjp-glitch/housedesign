"""Isolated axis-colored scene: establish native equirectangular UV orientation."""
from pathlib import Path
import bpy,math,json
from mathutils import Vector
ROOT=Path(r'D:\AI-Yang.cn\HomeDesign');OUT=ROOT/'07_renders/vr-tour-v01';OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=4
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type!='CPU'
s.cycles.device='GPU'
colors=[('plus-x',(4,0,0),(1,0,0,1)),('minus-x',(-4,0,0),(0,1,1,1)),('plus-y',(0,4,0),(0,1,0,1)),('minus-y',(0,-4,0),(1,0,1,1)),('plus-z',(0,0,4),(0,0,1,1)),('minus-z',(0,0,-4),(1,1,0,1))]
for name,loc,color in colors:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=.7,location=loc);o=bpy.context.object;o.name=name
    m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;n.clear();e=n.new('ShaderNodeEmission');e.inputs[0].default_value=color;out=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(e.outputs[0],out.inputs[0]);o.data.materials.append(m)
bpy.ops.object.camera_add(location=(0,0,0));cam=bpy.context.object;cam.rotation_euler=Vector((1,0,0)).to_track_quat('-Z','Y').to_euler();cam.data.type='PANO';cam.data.panorama_type='EQUIRECTANGULAR';cam.data.latitude_min=-math.pi/2;cam.data.latitude_max=math.pi/2;cam.data.longitude_min=-math.pi;cam.data.longitude_max=math.pi;s.camera=cam
s.render.resolution_x=1024;s.render.resolution_y=512;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.filepath=str(OUT/'axis-calibration.png');s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=0;s.world=bpy.data.worlds.new('black');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(0,0,0,1)
bpy.ops.render.render(write_still=True)
(ROOT/'logs/v13-panorama-calibration.json').write_text(json.dumps(dict(camera_forward_world=[1,0,0],camera_matrix=[list(r) for r in cam.matrix_world],camera_panorama=cam.data.panorama_type,devices=[dict(name=d.name,type=d.type,use=d.use) for d in prefs.devices],image=s.render.filepath),indent=2)+'\n',encoding='utf-8')
print('PANORAMA_CALIBRATION_READY')
