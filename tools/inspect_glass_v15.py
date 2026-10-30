from pathlib import Path
import bpy,json
ROOT=Path(r'D:\AI-Yang.cn\HomeDesign');rows=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH' and any(m and m.name=='R01 · 实体透明玻璃' for m in o.data.materials):
  rows.append(dict(name=o.name,role=o.get('home_design_role'),scale=list(o.scale),modifiers=[dict(type=m.type,name=m.name) for m in o.modifiers],faces=[dict(vertices=len(p.vertices),area=p.area,smooth=p.use_smooth,normal=list(p.normal)) for p in o.data.polygons][:15],has_custom_normals=o.data.has_custom_normals,vertices=len(o.data.vertices)))
(ROOT/'logs/v15-glass-inspection.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('GLASS_INSPECTED',len(rows))
