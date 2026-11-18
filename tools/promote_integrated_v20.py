from pathlib import Path
import json,hashlib,re,shutil
from datetime import datetime
R=Path('D:/AI-Yang.cn/HomeDesign');OUT=R/'09_delivery/main-integration-v20';DATE=datetime.now().date().isoformat()
VIZ=Path('C:/Users/Administrator/.codex/visualizations/2026/10/29/01a187d1-69cc-73a1-805e-834e8e8bb476/house-structure.html')
def read(p):return json.loads((R/p).read_text(encoding='utf-8-sig'))
def write(p,v):
 path=R/p;temp=path.with_suffix(path.suffix+'.v20-write');temp.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');temp.replace(path)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
proof=read('09_delivery/main-integration-v20/最终交付核对.json');assert proof['status']=='passed'
before=read('09_delivery/main-integration-v20/合并前版本.json')
assert sha(R/'06_blender/active-model.json')==before['baseline']['06_blender/active-model.json']
assert sha(R/'06_blender/active-presentation.json')==before['baseline']['06_blender/active-presentation.json']
if VIZ.exists():
 text=VIZ.read_text(encoding='utf-8');match=re.search(r'<script type="application/json" id="house-data-v1">([\s\S]*?)</script>',text);assert match
 old=json.loads(match.group(1));assert old['revision']==19
 expected={q['id']:(q['x'],q['z']) for q in read('02_geometry/geometry-master-v19.json')['furnitureObjects']}
 assert {q['id']:(q['x'],q['z']) for q in old['furnitureObjects']}==expected
 shutil.copy2(VIZ,OUT/'previous-main-fragment-v19.html')
shutil.copy2(R/'09_delivery/index.html',OUT/'previous-home-index-v19.html')
g=read('02_geometry/geometry-master-v20.json');cfg=read('09_delivery/vr-tour-v06/漫游机位与来源.json')
p={'presentation_revision':20,'geometry_revision':20,'base_architecture_revision':14,'model':'06_blender/home-main-v20.blend','model_sha256':proof['modelSha256'],'geometry':'02_geometry/geometry-master-v20.json','geometry_sha256':proof['geometrySha256'],'style':'05_style/modern-japanese-v20.json','style_sha256':proof['styleSha256'],'tour':'09_delivery/vr-tour-v06/打开360全景漫游.html','resolution':[1774,887],'upscaled':False,'native_anchor_resolution':[4096,2048],'view_count':4,'projection':'monoscopic equirectangular360x180','method':'same-model native full spheres + built-in image_gen photographic concepts','placement_snapshot':'03_layout/widget-layout-v20-initial.json','source_layout_furniture_count':26,'all_unaffected_positions_retained':True,'retired_dining_objects':['dining-table']+[f'dining-chair-{i}' for i in range(1,5)],'ai_image_details_are_conceptual':True,'exterior_is_illustrative':True,'main_editable_model_preserved':True,'perspective_gallery':'09_delivery/main-integration-v20/index.html','render_source_model':'06_blender/home-v20-render-source.blend','render_source_model_sha256':sha(R/'06_blender/home-v20-render-source.blend'),'metadata_confirmation':'09_delivery/main-integration-v20/表现元数据一致性.json','office_variant':'B','office_variant_status':'temporary preview; homeowner material choice pending','browser_visual_qa':False,'headset_tested':False}
a=before['activeModel'];a.update(revision=20,filename='home-main-v20.blend',geometry=p['geometry'],geometry_sha256=p['geometry_sha256'],style=p['style'],style_sha256=p['style_sha256'],style_revision='modern-japanese-v20',previous_active_filename='home-main-v19.blend',furniture_count=26,model_sha256=p['model_sha256'],live_session_verified=False,saved_native_file_verified=True,panorama_tour=p['tour'],panorama_resolution=p['resolution'],panorama_model_revision=20,panorama_presentation_revision=20,current_perspective_renders=p['perspective_gallery'],interactive_model='09_delivery/house-v20-preview.html',photoreal_presentation=p,latest_layout_snapshot=p['placement_snapshot'],latest_presentation_geometry=p['geometry'],completed_integration_v20=g['features']['completedIntegrationV20'],wider_v20_refinement_status='pending design details; this integration does not claim all earlier v20 items complete')
write('06_blender/active-model.json',a);write('06_blender/active-presentation.json',p);shutil.copy2(R/p['geometry'],R/'02_geometry/geometry-master.json')
layout={'revision':20,'units':'mm','model':p['model'],'model_sha256':p['model_sha256'],'verified_saved_native_file':True,'live_mcp_connected':False,'moveStepMm':100,'positions':[dict(id=q['id'],x=q['x'],z=q['z']) for q in g['furnitureObjects']]}
write('03_layout/blender-layout-v20.json',layout);write('03_layout/blender-layout-latest.json',{'revision':20,'units':'mm','relative_to':'geometry-master-v20','objects':[dict(id=q['id'],x=q['x'],z=q['z'],dx=0,dz=0,rotation_z_degrees=0) for q in g['furnitureObjects']]})
VIZ.write_text((R/'09_delivery/house-v20-fragment.html').read_text(encoding='utf-8'),encoding='utf-8')
home=R/'09_delivery/index.html';text=home.read_text(encoding='utf-8').replace('v19-deepening/index.html','main-integration-v20/index.html').replace('查看四区深化与日夜效果图','查看餐岛与办公区整合后的四区效果').replace('vr-tour-v05/','vr-tour-v06/').replace('house-v19-preview.html','house-v20-preview.html').replace('vr-tour-v05-预览/living.png','main-integration-v20/photos/living.png');home.write_text(text,encoding='utf-8')
c=read('01_brief/current-design-constraints.json');c['updated_date']=DATE;c['completed_design_integration']={'source_instruction':'设计完成后，全部都加到主模型中','default':'Integrate completed designs into master, interactive model and same-version presentations; preserve history. Later explicit independent-only instructions take precedence.','active_model_revision':20,'dining_study':'11','office_study':'02','office_material':'B temporary preview; not homeowner-finalized','wider_v20_detail_work':'pending; not implied complete by revision20'};c['panorama_delivery'].update(version=20,presentation_revision=20,current_master_revision=20,resolution=[1774,887],latest_placement_snapshot=p['placement_snapshot'],status='v20 completed dining11/office02 integration, photographic four-point panoramas');write('01_brief/current-design-constraints.json',c)
proof['promotedToActive']=True;proof['activeModelMetadataMatches']=read('06_blender/active-model.json')['model_sha256']==sha(R/'06_blender/home-main-v20.blend');proof['activeInlineFragmentSha256']=sha(VIZ);write('09_delivery/main-integration-v20/最终交付核对.json',proof)
assert proof['activeModelMetadataMatches']
print('V20_MASTER_AND_PRESENTATIONS_ACTIVE',26,flush=True)
