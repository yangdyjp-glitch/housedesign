from pathlib import Path
import bpy,json
R=Path(r'D:/AI-Yang.cn/HomeDesign');s=bpy.context.scene
d=json.loads((R/'02_geometry/geometry-master-v18.json').read_text(encoding='utf-8'))
summary={'keys':list(d),'features':list(d['features']),'publicRefinement':d['features'].get('publicRefinement'),'referenceRefinement':d['features'].get('referenceRefinement'),'referenceParts':d.get('referenceParts'),'materials':d['furnitureMaterials'],'chairparts':[p for p in d['furniture'] if p['parent']=='dining-chair-1'],'bookcase':[p for p in d['furniture'] if p['parent']=='bookcase'],'objects':[]}
for o in s.objects:
 if o.type in ['LIGHT','CAMERA'] or o.get('home_design_role') in ['ceiling','reference_detail','furniture'] or any(w in o.name.lower() for w in ['ceiling','顶','cove','v12-tv','灯带','帘']):
  summary['objects'].append(dict(name=o.name,type=o.type,role=o.get('home_design_role'),source_id=o.get('source_id'),location=list(o.location),dimensions=list(o.dimensions),hide_render=o.hide_render,materials=[m.name if m else None for m in o.data.materials] if o.type=='MESH' else [],props={k:str(v)[:1000] for k,v in o.items()},light=dict(type=o.data.type,energy=o.data.energy,color=list(o.data.color),drivers=[a.data_path for a in o.data.animation_data.drivers] if o.data.animation_data else []) if o.type=='LIGHT' else None))
(R/'logs/v19-source-inspection.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print('V19_INSPECTED',len(summary['objects']),flush=True)
