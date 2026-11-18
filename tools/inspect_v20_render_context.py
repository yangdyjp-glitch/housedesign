import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path('D:/AI-Yang.cn/HomeDesign');bpy.ops.wm.open_mainfile(filepath=str(R/'06_blender/home-main-v20.blend'));s=bpy.context.scene;items=[]
for o in s.objects:
 if o.type!='MESH' or o.hide_render or any(c.hide_render for c in o.users_collection):continue
 p=[o.matrix_world@v.co for v in o.data.vertices];lo=[min(v[i] for v in p) for i in range(3)];hi=[max(v[i] for v in p) for i in range(3)]
 if lo[2]>2.6 and (hi[0]-lo[0])*(hi[1]-lo[1])>1:items.append({'name':o.name,'role':o.get('home_design_role'),'lo':lo,'hi':hi,'finishedPlane':o.get('finished_plane_mm')})
f=next(o for o in s.objects if o.get('home_design_role')=='furniture' and o.get('source_id')=='dining-sideboard-island')
mats=[]
for m in f.data.materials:
 if m:
  p=m.node_tree.nodes.get('Principled BSDF') if m.use_nodes else None
  mats.append({'name':m.name,'color':list(p.inputs['Base Color'].default_value) if p else None,'linkedBase':bool(p.inputs['Base Color'].is_linked) if p else None})
(R/'09_delivery/main-integration-v20/观察视角排查.json').write_text(json.dumps({'overheadMeshes':items,'diningMaterials':mats},ensure_ascii=False,indent=2),encoding='utf-8')
print('V20_RENDER_CONTEXT_AUDITED')
