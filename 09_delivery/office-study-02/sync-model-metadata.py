import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path('D:/AI-Yang.cn/HomeDesign')
OUT=ROOT/'09_delivery/office-study-02'
p=json.loads((OUT/'设计参数.json').read_text(encoding='utf-8'))
records=[]
for vid in ['A','B','C']:
 model=OUT/vid/f'办公区-{vid}-近端半墙远端敞开-独立02.blend'
 bpy.ops.wm.open_mainfile(filepath=str(model))
 bpy.context.scene['parameters']=json.dumps(p,ensure_ascii=False)
 bpy.context.scene.frame_set(1)
 bpy.ops.wm.save_as_mainfile(filepath=str(model))
 bpy.ops.wm.open_mainfile(filepath=str(model))
 sc=bpy.context.scene
 assert json.loads(sc['parameters'])==p
 cap=next(o for o in sc.objects if o.get('source_id')=='near-halfwall-cap')
 xyz=[cap.matrix_world@Vector(v) for v in cap.bound_box]
 assert round(max(v.z for v in xyz)*1000)==950
 assert round(max(v.x for v in xyz)*1000)==6835
 assert not any(o.get('source_id')=='short-raised-return' for o in sc.objects)
 assert not any(o.name.startswith('Sage shallow end storage') for o in sc.objects)
 assert sum(o.get('source_part')=='double-desk-monitor-screen-34' for o in sc.objects)==1
 records.append({'variant':vid,'path':str(model),'sha256':hashlib.sha256(model.read_bytes()).hexdigest(),'parametersReopenedMatch':True})
 assert {f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in p['baselineHashes']}==p['baselineHashes']
(OUT/'元数据回读.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
print('OFFICE02_METADATA_REOPENED_MAIN_UNCHANGED')
