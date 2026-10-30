from pathlib import Path
import bpy,json
ROOT=Path(r'D:\AI-Yang.cn\HomeDesign')
scene=bpy.context.scene
report=dict(materials=[m.name for m in bpy.data.materials],lights=[dict(name=o.name,type=o.data.type,energy=o.data.energy,position=list(o.location),rotation=list(o.rotation_euler)) for o in scene.objects if o.type=='LIGHT'],objects=[dict(name=o.name,role=o.get('home_design_role'),vertices=len(o.data.vertices) if o.type=='MESH' else None) for o in scene.objects if o.get('home_design_role') in ['wall_visual_union','public_finish_overlay','render_environment','ceiling']],assets=[])
for ident in ['potted_plant_01','potted_plant_02']:
    p=ROOT/f'08_assets/photoreal-v15/{ident}/{ident}_1k.blend'
    with bpy.data.libraries.load(str(p),link=False) as (source,target):
        report['assets'].append(dict(id=ident,objects=list(source.objects),collections=list(source.collections)))
(ROOT/'logs/v15-input-inspection.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('V15_INPUTS_INSPECTED')
