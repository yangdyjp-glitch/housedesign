"""Bind inspected photographic panoramas without overstating native image resolution."""
from pathlib import Path
import hashlib,json,shutil,zipfile,sys
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[1];assert '--visual-reviewed' in sys.argv
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
def write(p,v):(ROOT/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
active=read('06_blender/active-model.json');native=read('logs/v16-native-layout-verification.json');viewer=read('logs/vr-tour-v03-verification.json');model=ROOT/'06_blender/home-v16-reference-anchor.blend';geo=ROOT/'02_geometry/presentation-layout-v16.json'
assert sha(ROOT/'06_blender'/active['filename'])==active['model_sha256'];assert sha(ROOT/'02_geometry/geometry-master-v14.json')==active['geometry_sha256']
assert native['model_sha256']==viewer['modelSha256']==sha(model) and native['geometry_sha256']==sha(geo)
assert viewer['status']=='passed' and len(viewer['tests'])==16 and not viewer['errors']
old=read('02_geometry/geometry-master-v14.json');new=read('02_geometry/presentation-layout-v16.json');assert old['walls']==new['walls'] and old['floor']==new['floor']
images=[]
for ident in ['living','dining','balcony','entry']:
    p=ROOT/'07_renders/vr-tour-v03'/(ident+'-day.jpg')
    with Image.open(p) as im:
        assert im.size==(1774,887);a=np.asarray(im).astype(float)
    images.append(dict(id=ident,image=p.relative_to(ROOT).as_posix(),sha256=sha(p),native_resolution=[1774,887],upscaled=False,seam_edge_mae_255=round(float(abs(a[:,0]-a[:,-1]).mean()),4),sphere_and_poles_visually_reviewed=True))
style=read('05_style/photographic-reference-v16.json');style.update(anchor_model=model.relative_to(ROOT).as_posix(),anchor_model_sha256=sha(model),native_generated_resolution=[1774,887],upscaled=False,output_manifest='07_renders/vr-tour-v03/imagegen-outputs.json',final_prompt_set='07_renders/vr-tour-v03/imagegen-final-prompts.json',correction_prompt_set='07_renders/vr-tour-v03/correction-prompts.json',tour='09_delivery/vr-tour-v03/打开360全景漫游.html');write('05_style/photographic-reference-v16.json',style)
previous=ROOT/'06_blender/presentation-v15-record.json'
if not previous.exists():shutil.copy2(ROOT/'06_blender/active-presentation.json',previous)
p=dict(presentation_revision=16,geometry_revision=16,base_architecture_revision=14,model=model.relative_to(ROOT).as_posix(),model_sha256=sha(model),geometry=geo.relative_to(ROOT).as_posix(),geometry_sha256=sha(geo),style='05_style/photographic-reference-v16.json',style_sha256=sha(ROOT/'05_style/photographic-reference-v16.json'),tour=style['tour'],method='Native verified geometry anchors + built-in imagegen photographic light and realism treatment',resolution=[1774,887],upscaled=False,native_anchor_resolution=[4096,2048],view_count=4,projection='monoscopic equirectangular 360x180',placement_snapshot='03_layout/widget-layout-v16-snapshot.json',source_layout_furniture_count=27,native_anchors_match_latest_placements=True,ai_image_details_are_conceptual=True,exterior_is_illustrative=True,main_editable_model_preserved=True,previous_native_8k_tour='09_delivery/vr-tour-v02/打开360全景漫游.html')
write('06_blender/active-presentation.json',p)
active.update(photoreal_presentation=p,panorama_tour=p['tour'],panorama_model_revision=16,panorama_presentation_revision=16,panorama_resolution=p['resolution'],panorama_nodes=4,current_perspective_renders='09_delivery/vr-tour-v03-预览',latest_layout_snapshot=p['placement_snapshot'],latest_presentation_geometry=p['geometry'],panorama_stale_for_current_master_suite=False,panorama_master_suite_note='v14 suite retained in the native anchor; latest public furniture positions supplied by the interactive snapshot, four public views only')
write('06_blender/active-model.json',active)
c=read('01_brief/current-design-constraints.json');c['panorama_delivery'].update(version=16,presentation_revision=16,current_master_revision=14,base_architecture_revision=14,status='Selected-reference photographic light and realism preview, native AI resolution honestly retained',resolution=[1774,887],upscaled=False,ai_assisted=True,photorealistic=True,exterior_is_illustrative=True,latest_placement_snapshot=p['placement_snapshot']);write('01_brief/current-design-constraints.json',c)
report=dict(presentation_revision=16,base_architecture_revision=14,model_sha256=sha(model),geometry_sha256=sha(geo),source_v14_unchanged=True,latest_27_native_placements_verified=True,ai_image_details_are_conceptual=True,method=p['method'],images=images,full_sphere_capture_count=len(read('logs/v16-spherical-view-captures.json')),viewer_tests=viewer['tests'],runtime_errors=viewer['errors'],headset_tested=False,physical_phone_tested=False,free_walking=False,stereo=False,exterior_is_illustrative=True,light_is_design_atmosphere_not_site_sun_study=True,known_limits=['Native generated images are1774x887, below previous8K; no upscale','Some edge/nadir joins and AI material/foliage differences remain'],budget_considered=False)
write('logs/v16-photographic-delivery-verification.json',report)
delivery=ROOT/'09_delivery/vr-tour-v03';files=[q for q in delivery.rglob('*') if q.is_file() and q.name!='viewer.template.html']
files += list((ROOT/'09_delivery/vr-tour-v03-预览').glob('*.png'))
files += [ROOT/'07_renders/vr-tour-v03/摄影感四区预览.jpg',ROOT/'05_style/photographic-reference-v16.json',ROOT/'06_blender/active-presentation.json',ROOT/'logs/v16-photographic-delivery-verification.json',ROOT/'07_renders/vr-tour-v03/imagegen-final-prompts.json',ROOT/'07_renders/vr-tour-v03/correction-prompts.json',ROOT/'07_renders/vr-tour-v03/imagegen-outputs.json']
zip_path=ROOT/'09_delivery/四区摄影感360全景-v16.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for q in files:z.write(q,(q.relative_to(delivery) if q.is_relative_to(delivery) else Path('设计记录')/q.relative_to(ROOT)).as_posix())
with zipfile.ZipFile(zip_path) as z:assert z.testzip() is None
assert zip_path.stat().st_size<100*1024*1024
print('V16_PHOTOGRAPHIC_TOUR_BOUND',len(images),'native1774x887',zip_path.stat().st_size)
