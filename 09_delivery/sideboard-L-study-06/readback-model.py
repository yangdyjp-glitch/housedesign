from pathlib import Path
import bpy,json
from mathutils import Vector
OUT=Path('D:/AI-Yang.cn/HomeDesign/09_delivery/sideboard-L-study-06')
bpy.ops.wm.open_mainfile(filepath=str(OUT/'按批注L形餐岛-独立试排.blend'))
bpy.context.view_layer.update();o=bpy.data.objects['actual-L-dining-top-06']
v=[o.matrix_world@Vector(p) for p in o.bound_box]
bounds=dict(u=[min(p.x for p in v)*1000,max(p.x for p in v)*1000],v=[-max(p.y for p in v)*1000,-min(p.y for p in v)*1000],z=[min(p.z for p in v)*1000,max(p.z for p in v)*1000])
for key,expected in [('u',[1350,2850]),('v',[300,1850]),('z',[720,750])]:assert max(abs(a-b) for a,b in zip(bounds[key],expected))<.1
probes=[]
for u,v,wanted in [(1500,600,True),(2200,1500,True),(2200,600,False)]:
    result=bpy.context.scene.ray_cast(bpy.context.evaluated_depsgraph_get(),Vector((u/1000,-v/1000,1)),Vector((0,0,-1)))
    hit_L=result[0] and result[4].original==o
    assert bool(hit_L)==wanted
    probes.append(dict(u=u,v=v,L_tabletop_hit=bool(hit_L)))
opaque=[ob.name for ob in bpy.context.scene.objects if ob.name.startswith('right-opaque-')]
chair_seats=[ob.name for ob in bpy.context.scene.objects if ob.name.endswith('-seat') and ('chair' in ob.name)]
assert len(chair_seats)==4 and len(opaque)==4
report=dict(source='actual saved detached06 Blender file reopened',table_bounds_mm=bounds,
    L_shape_probes=probes,opaque_doors=opaque,chair_count=4,
    limits='verifies modeled contour and counts only; no human, appliance or field certification')
(OUT/'model-readback.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
