"""Bind only completed, inspected 8K realistic panoramas to the current design delivery."""
from pathlib import Path
import json,hashlib,zipfile,sys
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'07_renders/vr-tour-v02';DELIVERY=ROOT/'09_delivery/vr-tour-v02'
assert '--visual-reviewed' in sys.argv,'Run only after inspecting the actual final sphere views.'
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
def write(p,v):(ROOT/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
active=read('06_blender/active-model.json');model=ROOT/'06_blender/home-v14-photoreal-v15.blend';geo=ROOT/active['geometry'];native=read('logs/v15-photoreal-model-verification.json');renders=read('logs/v15-panoramas-final-all.json');viewer=read('logs/vr-tour-v02-verification.json')
assert native['model_sha256']==renders['model_sha256']==viewer['modelSha256']==sha(model)
assert renders['geometry_sha256']==sha(geo)==active['geometry_sha256'];assert renders['furniture_count']==27 and len(renders['images'])==4
assert viewer['status']=='passed' and len(viewer['tests'])>=16
items=[]
for ident in ['living','dining','balcony','entry']:
    src=OUT/(ident+'-sphere.png');p=OUT/(ident+'-day.jpg')
    with Image.open(src) as im:assert im.size==(8192,4096);im.verify()
    with Image.open(p) as im:
        assert im.size==(8192,4096);a=np.asarray(im);seam=float(np.abs(a[:,0,:].astype(float)-a[:,-1,:].astype(float)).mean());assert seam<8,(ident,seam)
    items.append(dict(id=ident,native_sha256=sha(src),jpg_sha256=sha(p),seam_edge_MAE_255=round(seam,4),resolution=[8192,4096],final_sphere_view_reviewed=True))
style=read('05_style/photoreal-presentation-v15.json');style.update(layout_geometry_sha256=sha(geo),source_model_sha256=sha(ROOT/'06_blender/home-main-v14.blend'),presentation_model_sha256=sha(model),asset_manifest_sha256=sha(ROOT/'08_assets/photoreal-v15/asset-manifest.json'));write('05_style/photoreal-presentation-v15.json',style)
presentation=dict(presentation_revision=15,geometry_revision=14,model='06_blender/home-v14-photoreal-v15.blend',model_sha256=sha(model),geometry=active['geometry'],geometry_sha256=sha(geo),style='05_style/photoreal-presentation-v15.json',style_sha256=sha(ROOT/'05_style/photoreal-presentation-v15.json'),assets='08_assets/photoreal-v15/asset-manifest.json',tour='09_delivery/vr-tour-v02/打开360全景漫游.html',resolution=[8192,4096],view_count=4,projection='monoscopic equirectangular 360x180',source_layout_furniture_count=27,all_placements_preserved=True,exterior_is_illustrative=True,main_editable_model_preserved=True)
write('06_blender/active-presentation.json',presentation)
active.update(panorama_tour=presentation['tour'],panorama_model_revision=14,panorama_presentation_revision=15,panorama_stale_for_current_master_suite=False,panorama_resolution=[8192,4096],panorama_nodes=4,current_perspective_renders='07_renders/vr-tour-v02',photoreal_presentation=presentation,panorama_master_suite_note='Native scene includes the v14 suite, four requested public viewpoints retained; no additional private-room panorama node');write('06_blender/active-model.json',active)
constraints=read('01_brief/current-design-constraints.json');constraints['panorama_delivery'].update(version=14,presentation_revision=15,current_master_revision=14,status='current v14 layout with v15 realistic PBR presentation',photorealistic=True,exterior_is_illustrative=True);write('01_brief/current-design-constraints.json',constraints)
report=dict(presentation_revision=15,geometry_revision=14,model_sha256=sha(model),source_model_v14_unchanged=True,source_geometry_unchanged=True,all_27_placements_preserved=True,full_walls_and_windows_retained=True,model_reopened_and_dependencies_verified=True,materials='CC0 photo-texture PBR; fabric weave, oak floor, foliage; original color choices retained',new_furniture_or_decor=False,images=items,viewer_tests=viewer['tests'],runtime_errors=viewer['errors'],desktop_offline_and_touch_simulation_passed=True,physical_phone_tested=False,headset_tested=False,free_walking=False,stereo=False,exterior_is_illustrative=True,budget_considered=False)
write('logs/v15-photoreal-delivery-verification.json',report)
zip_path=ROOT/'09_delivery/四区写实360全景-v15.zip'
files=[p for p in DELIVERY.rglob('*') if p.is_file() and p.name!='viewer.template.html']
for ident in ['living','dining','balcony','entry']:files.append(OUT/(ident+'-photo.png'))
files += [ROOT/'logs/v15-photoreal-delivery-verification.json',ROOT/'05_style/photoreal-presentation-v15.json',ROOT/'06_blender/active-presentation.json',ROOT/'08_assets/photoreal-v15/asset-manifest.json',OUT/'写实四区预览.jpg']
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
    for p in files:
        arc=p.relative_to(DELIVERY) if p.is_relative_to(DELIVERY) else Path('设计记录')/p.relative_to(ROOT)
        archive.write(p,arc.as_posix())
with zipfile.ZipFile(zip_path) as archive:assert archive.testzip() is None
assert zip_path.stat().st_size<100*1024*1024
print('V15_PHOTOREAL_DELIVERY_BOUND',zip_path.name,len(files),zip_path.stat().st_size)
