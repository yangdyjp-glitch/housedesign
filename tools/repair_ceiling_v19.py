"""Keep the visible ceiling finish at 2750; place model thickness above it."""
from pathlib import Path
import bpy,json,hashlib
R=Path(r'D:/AI-Yang.cn/HomeDesign');s=bpy.context.scene;dest=R/'06_blender/home-main-v19.blend'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
o=next(o for o in s.objects if o.get('finished_plane_mm')==2750);mod=next(m for m in o.modifiers if m.type=='SOLIDIFY')
def bounds():
 bpy.context.view_layer.update();e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());z=[(e.matrix_world@v.co).z*1000 for v in e.data.vertices];return [min(z),max(z)]
before=bounds();oldsha=sha(dest);mod.offset=-1 if o.data.polygons[0].normal.z<0 else 1;o['finish_skin_on_void_side']=True;after=bounds();assert abs(after[0]-2750)<1
for light in [v for v in s.objects if v.type=='LIGHT' and v.get('circuit')=='general']:assert light.location.z*1000<after[0]
s['ceiling_final_repair_v19']='18mm skin moved above nominal finish, keep light emitters below finished plane';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(dest))
rec=dict(revision=19,before_active_model_sha256=oldsha,active_model_sha256=sha(dest),before_finish_skin_bounds_mm=before,final_finish_skin_bounds_mm=after,repair='18 mm visual skin moved to the void side of the existing nominal2750mm finish; all furniture positions, walls, glass and cameras unchanged',ai_concept_anchors='07_renders/v19-deepening',ai_anchor_ceiling_difference_mm=18,ai_anchor_exact_source_model='06_blender/home-v19-render-source.blend',final_native_renders='07_renders/v19-final-native',finished_height_is_still_provisional=True)
(R/'logs/v19-ceiling-repair.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print('V19_CEILING_REPAIRED',after,flush=True)
