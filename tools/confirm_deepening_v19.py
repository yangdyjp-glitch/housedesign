"""Bind late preference answers without changing any render-visible data."""
from pathlib import Path
import bpy,json,hashlib,struct
R=Path(r'D:/AI-Yang.cn/HomeDesign');s=bpy.context.scene;DEST=R/'06_blender/home-main-v19.blend'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def visual():
 h=hashlib.sha256()
 for o in sorted(s.objects,key=lambda o:o.name):
  h.update(o.name.encode());h.update(o.type.encode());h.update(str(o.hide_render).encode());h.update(struct.pack('16d',*[v for row in o.matrix_world for v in row]))
  if o.type=='MESH':
   for v in o.data.vertices:h.update(struct.pack('3f',*v.co))
   for p in o.data.polygons:h.update(str(tuple(p.vertices)).encode())
   for m in o.data.materials:h.update((m.name if m else '').encode())
  elif o.type=='LIGHT':h.update(str((o.data.type,o.data.energy,tuple(o.data.color))).encode())
  elif o.type=='CAMERA':h.update(str((o.data.type,o.data.lens,tuple(o.rotation_euler))).encode())
 return h.hexdigest()
before=visual();render_sha=sha(DEST);d=json.loads((R/'02_geometry/geometry-master-v19.json').read_text(encoding='utf8'))
s['home_design_geometry_sha256']=sha(R/'02_geometry/geometry-master-v19.json');s['home_design_style_sha256']=sha(R/'05_style/modern-japanese-v19.json');s['design_deepening_v19']=json.dumps(d['features']['deepeningV19'],ensure_ascii=False)
s['owner_confirmed_current_positions_v19']=True;s['ac_coordination_stage']='unselected equipment, schematic candidate zones only'
after=visual();assert after==before
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(DEST))
record=dict(render_source_model='06_blender/home-v19-render-source.blend',render_source_model_sha256=render_sha,active_model='06_blender/home-main-v19.blend',active_model_sha256=sha(DEST),visual_fingerprint_before=before,visual_fingerprint_after=after,only_scene_metadata_updated=True,all_objects_meshes_material_slots_cameras_lights_unchanged=True,user_confirmed_positions_retained=True,ac_equipment_not_selected=True)
(R/'logs/v19-metadata-confirmation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for name in ['v19-perspectives.json','v19-panorama-anchors.json']:
 p=R/'logs'/name;a=json.loads(p.read_text(encoding='utf8'));assert a['model_sha256']==render_sha;a['render_source_model']='06_blender/home-v19-render-source.blend';a['compatible_active_model_sha256']=record['active_model_sha256'];a['visual_fingerprint']=before;a['metadata_confirmation']='logs/v19-metadata-confirmation.json';p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('V19_METADATA_CONFIRMED_VISUAL_DATA_UNCHANGED',before[:16],flush=True)
