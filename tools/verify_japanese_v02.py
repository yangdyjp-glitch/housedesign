"""Read back the saved style model and verify placements, shapes and movement."""
from pathlib import Path
from mathutils import Vector
import bpy, hashlib, json, math
ROOT=Path(r'D:\AI-Yang.cn\HomeDesign')
MODEL=ROOT/'06_blender/home-v06-japanese-v02.blend'
assert Path(bpy.data.filepath).resolve()==MODEL.resolve()
data=json.loads((ROOT/'02_geometry/geometry-master-v06.json').read_text(encoding='utf-8'))
style_raw=(ROOT/'05_style/modern-japanese-v02.json').read_bytes()
style=json.loads(style_raw)
assert bpy.context.scene['home_design_style_sha256']==hashlib.sha256(style_raw).hexdigest()
assert bpy.context.scene['home_design_geometry_sha256']==style['geometry_sha256']
furniture={o['source_id']:o for o in bpy.context.scene.objects if o.get('home_design_role')=='furniture'}
assert len(furniture)==14
assert sum(o.get('home_design_role')=='wall' for o in bpy.context.scene.objects)==60
assert sum(o.get('home_design_role')=='glass' for o in bpy.context.scene.objects)==8
assert sum(o.get('home_design_role')=='wall_finish_proposal' for o in bpy.context.scene.objects)==4
rows=[]
for group in data['furnitureObjects']:
    ob=furniture[group['id']]
    assert abs(ob.location.x*1000-group['x'])<0.001
    assert abs(-ob.location.y*1000-group['z'])<0.001
    assert list(ob['dimensions_mm'])==[group['dimensionsMm'][k] for k in ['length','width','height']]
    assert ob.get('movement_step_mm')==100 and not ob.hide_select
    rows.append(dict(id=group['id'],location_mm=[round(ob.location.x*1000,3),round(-ob.location.y*1000,3)],dimensions_mm=list(ob['dimensions_mm']),selectable=True))
supports=[]
for group in ['side-table','dining-table','double-desk']:
    top=next(p for p in data['furniture'] if p['id']==group+'-top')
    radius=style['designer_decisions']['table_corner_radii_mm'][top['id']]
    for leg in [p for p in data['furniture'] if p['parent']==group and '-leg-' in p['id']]:
        for xx in [leg['x'],leg['x']+leg['w']]:
            for zz in [leg['z'],leg['z']+leg['d']]:
                x,z=xx-top['x'],zz-top['z']
                cx=max(radius,min(top['w']-radius,x));cz=max(radius,min(top['d']-radius,z))
                assert math.hypot(x-cx,z-cz)<=radius+0.001,(leg['id'],x,z)
        supports.append(dict(id=leg['id'],inside_rounded_top=True))
report=dict(saved_model_reopened=True,model=str(MODEL),geometry_base_sha256=style['geometry_sha256'],
            style_sha256=hashlib.sha256(style_raw).hexdigest(),furniture=rows,wall_baseline_count=60,glass_count=8,
            curved_finish_profiles=4,table_leg_checks=supports,major_furniture_count=14,
            movement_tests='Actual X/Y 100 mm operator test and restoration on all 14 assemblies: see japanese-v02-render.json',
            physical_dimensions_note='source model consistency, not site measurement accuracy')
(ROOT/'logs/japanese-v02-readback.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('STYLE_V02_VERIFIED '+json.dumps(dict(furniture=14,walls=60,glass=8,curves=4,leg_supports=len(supports))))
