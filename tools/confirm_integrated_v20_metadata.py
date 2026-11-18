import bpy,json,hashlib
from pathlib import Path
R=Path('D:/AI-Yang.cn/HomeDesign');OUT=R/'09_delivery/main-integration-v20'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def fingerprint(scene):
 data=[]
 for o in sorted(scene.objects,key=lambda x:x.name):
  rec=[o.name,o.type,list(round(x,7) for row in o.matrix_world for x in row),o.hide_render,[c.name for c in o.users_collection]]
  if o.type=='MESH':rec += [[list(round(x,7) for x in v.co) for v in o.data.vertices],[[list(p.vertices),p.material_index] for p in o.data.polygons],[m.name if m else None for m in o.data.materials]]
  if o.type=='LIGHT':rec += [o.data.type,list(o.data.color),o.data.energy]
  data.append(rec)
 return hashlib.sha256(json.dumps(data,separators=(',',':')).encode()).hexdigest()
records=[]
for name in ['home-main-v20.blend','home-v20-render-source.blend']:
 path=R/'06_blender'/name;bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();before=fingerprint(s);beforehash=sha(path)
 s['photoreal_presentation_revision']=20
 if 'presentation_stale_after_geometry_revision' in s:del s['presentation_stale_after_geometry_revision']
 s['current_gallery']='09_delivery/main-integration-v20/index.html';s['current_panorama']='09_delivery/vr-tour-v06/打开360全景漫游.html';s['current_interactive_model']='09_delivery/house-v20-preview.html';s['wider_v20_refinement_status']='MEP/construction details and unresolved bath doorway remain pending; completed dining11/office02 are integrated'
 bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.scene.frame_set(1);bpy.context.view_layer.update();after=fingerprint(bpy.context.scene);assert before==after
 records.append({'file':path.relative_to(R).as_posix(),'beforeSha256':beforehash,'afterSha256':sha(path),'beforeVisualFingerprint':before,'afterVisualFingerprint':after,'renderVisibleDataUnchanged':True})
p=OUT/'主模型回读.json';report=json.loads(p.read_text(encoding='utf-8'));report['modelSha256']=sha(R/'06_blender/home-main-v20.blend');report['presentationMetadataConfirmed']=True;p.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'表现元数据一致性.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8');print('V20_METADATA_CONFIRMED_WITH_IDENTICAL_VISUAL_DATA')
