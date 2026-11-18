import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path('D:/AI-Yang.cn/HomeDesign');OUT=R/'09_delivery/main-integration-v20';OUT.mkdir(exist_ok=True)
def bounds(o):
 p=[o.matrix_world@Vector(v) for v in o.bound_box]
 return [round(min(q.x for q in p)*1000,2),round(-max(q.y for q in p)*1000,2),round(min(q.z for q in p)*1000,2),round((max(q.x for q in p)-min(q.x for q in p))*1000,2),round((max(q.y for q in p)-min(q.y for q in p))*1000,2),round((max(q.z for q in p)-min(q.z for q in p))*1000,2)]
report={}
sources={'main':R/'06_blender/home-main-v19.blend','dining':R/'09_delivery/sideboard-U-study-11/短连接长餐台-胡桃白冰箱圆边-独立11.blend','office':R/'09_delivery/office-study-02/B/办公区-B-近端半墙远端敞开-独立02.blend'}
for kind,path in sources.items():
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
 objects=[]
 for o in s.objects:
  if kind=='main' and o.get('home_design_role')!='furniture':continue
  if kind!='main' and o.type not in ['MESH','LIGHT','EMPTY']:continue
  rec=dict(name=o.name,type=o.type,role=o.get('home_design_role'),source_id=o.get('source_id'),source_part=o.get('source_part'),hide_render=o.hide_render,parent=o.parent.name if o.parent else None,location=[round(v,4) for v in o.location],bounds=bounds(o) if o.type=='MESH' else None)
  if o.type=='MESH':rec.update(vertices=len(o.data.vertices),polygons=len(o.data.polygons),materials=[m.name for m in o.data.materials])
  objects.append(rec)
 report[kind]=dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),objects=objects,sceneProperties={k:s[k] for k in s.keys() if k in ['home_design_revision','proposalStatus','proposal']})
(OUT/'源模型审计.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('INTEGRATION_AUDIT_COMPLETE',json.dumps({k:{'objects':len(v['objects']),'rawVertices':sum(o.get('vertices',0) for o in v['objects'])} for k,v in report.items()}))
