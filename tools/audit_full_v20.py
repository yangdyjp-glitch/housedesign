from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector
R=Path('D:/AI-Yang.cn/HomeDesign');OUT=R/'09_delivery/v20-complete'
bpy.ops.wm.open_mainfile(filepath=str(R/'06_blender/home-main-v20-complete.blend'));s=bpy.context.scene
d=json.loads((R/'02_geometry/geometry-master-v20-complete.json').read_text(encoding='utf8'))
ctrl=next(o for o in s.objects if o.get('home_design_role')=='bath_door_control' and not o.get('retired_in_phase'))
leaves=sorted([o for o in s.objects if str(o.get('source_id','')).startswith('v20f-bath-bifold-leaf') and not o.get('retired_in_phase')],key=lambda o:o['source_id'])
poses=[]
for i in range(13):
    t=i/12;ctrl['open_ratio']=t;ctrl.update_tag();s.update_tag();s.frame_set(i+1);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();le=[]
    for o in leaves:
        e=o.evaluated_get(deps);pts=[e.matrix_world@v.co for v in e.data.vertices];le.append(dict(id=o['source_id'],rotation=list(e.rotation_euler),drivers=[dict(type=f.driver.type,expression=f.driver.expression,valid=f.driver.is_valid) for f in o.animation_data.drivers],boundsMm=[min(p.x for p in pts)*1000,min(-p.y for p in pts)*1000,max(p.x for p in pts)*1000,max(-p.y for p in pts)*1000]))
    poses.append(dict(ratio=t,leaves=le))
curtains=[]
for o in s.objects:
    if o.get('home_design_role')=='curtain_fabric' and o.animation_data:
        curtains.append(dict(name=o.name,drivers=[dict(path=f.data_path,index=f.array_index,expression=f.driver.expression) for f in o.animation_data.drivers]))
report=dict(doorPoses=poses,curtainDrivers=curtains[:2]+curtains[-2:],pendants=[dict(name=o.name,hidden=o.hide_render,archive=bool(o.get('retired_in_phase')),source=o.get('source_id')) for o in s.objects if 'pendant' in str(o.get('source_id',''))],lightPositions=[dict(name=o.name,pos=list(o.location)) for o in s.objects if o.type=='LIGHT' and 3.5<o.location.x<8 and 4.9<-o.location.y<5.9],roles={})
for o in s.objects:
    if o.get('retired_in_phase'):continue
    k=str(o.get('home_design_role','none'));report['roles'][k]=report['roles'].get(k,0)+1
(OUT/'中间姿态审计.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k!='doorPoses'},ensure_ascii=False))
print('DOOR_LAST_POSE',poses[-1])
