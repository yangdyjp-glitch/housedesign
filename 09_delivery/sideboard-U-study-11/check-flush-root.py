from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
ROOT=Path('D:/AI-Yang.cn/HomeDesign');OUT=ROOT/'09_delivery/sideboard-U-study-11'
p=json.loads((OUT/'U-layout-parameters.json').read_text(encoding='utf-8'))
p['user_confirmed'].append('根部与置物台齐平，取消凸起小台阶及盖条')
p['flush_root']=dict(owner_confirmed=True,top_height=880,step_height=0,continuous_mesh=True,raised_cover_strip=False)
blend=OUT/'短连接长餐台-胡桃白冰箱圆边-独立11.blend'
bpy.ops.wm.open_mainfile(filepath=str(blend));scene=bpy.context.scene;scene.frame_set(1);bpy.context.view_layer.update()
tops=[o for o in scene.objects if o.name.startswith('continuous-walnut-U-top-')]
assert len(tops)==1
top=tops[0];levels=sorted(set(round((top.matrix_world@v.co).z*1000,3) for v in top.data.vertices))
assert levels==[850,880]
assert top.data.materials[0].name=='walnut'
assert not any(o.name.startswith('counter-') for o in scene.objects)
scene['parameters']=json.dumps(p,ensure_ascii=False);scene['root_junction']='one coplanar U at880; zero step, no raised cover strip'
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
(OUT/'U-layout-parameters.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf-8')
record=json.loads((OUT/'finish-model-readback.json').read_text(encoding='utf-8'))
record['flush_root']=dict(top_mesh_count=1,raw_mesh_vertex_height_levels_mm=levels,step_height_mm=0,material=top.data.materials[0].name,no_separate_counter_tops=True)
record['latest_blend_sha256']=hashlib.sha256(blend.read_bytes()).hexdigest()
assert record['baseline_after']=={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in record['baseline_after']}
(OUT/'finish-model-readback.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print('FLUSH_ROOT_VERIFIED',json.dumps(record['flush_root']))
