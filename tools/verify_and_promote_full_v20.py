from pathlib import Path
from urllib.parse import unquote,urlsplit
from datetime import date
import json,hashlib,re,shutil,copy,math,xml.etree.ElementTree as ET
from PIL import Image,ImageStat
R=Path('D:/AI-Yang.cn/HomeDesign');OUT=R/'09_delivery/v20-complete';TOUR=R/'09_delivery/vr-tour-v07'
VIZ=Path('C:/Users/Administrator/.codex/visualizations/2026/10/29/01a187d1-69cc-73a1-805e-834e8e8bb476/house-structure.html')
def load(p):return json.loads((R/p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,data):
    path=R/p;tmp=path.with_suffix(path.suffix+'.full-v20-write');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');tmp.replace(path)
before=load('09_delivery/v20-complete/实施前版本.json')
for path,digest in before['hashes'].items():assert sha(R/path)==digest,path+' changed since start'
g=load('02_geometry/geometry-master-v20-complete.json');audit=load('09_delivery/v20-complete/主模型回读.json')
for f in ['主模型回读.json','实体与动作核对.json','交互逻辑核对.json','全景逻辑核对.json','现场Blender会话核对.json','原生移动面板联动核对.json']:
    assert load('09_delivery/v20-complete/'+f)['status']=='passed',f
model=R/'06_blender/home-main-v20-complete.blend';geometry=R/'02_geometry/geometry-master-v20-complete.json';style=R/'05_style/modern-japanese-v20-complete.json'
assert audit['modelSha256']==sha(model) and audit['geometrySha256']==sha(geometry) and audit['styleSha256']==sha(style)
assert len(g['furnitureObjects'])==28
base=load('02_geometry/geometry-master-v20.json');positions={q['id']:(q['x'],q['z']) for q in g['furnitureObjects']}
assert all(positions[q['id']]==(q['x'],q['z']) for q in base['furnitureObjects'])
images=load('09_delivery/v20-complete/图像交付清单.json');assert len(images)==8
for row in images:
    p=R/row['deliveryPath'];assert sha(p)==row['sha256']==sha(R/row['path'])
    with Image.open(p) as im:assert list(im.size)==row['resolution'];im.verify()
native=load('09_delivery/v20-complete/渲染记录.json');assert len(native)==16
for row in native:
    with Image.open(R/row['path']) as im:assert list(im.size)==row['resolution'];im.verify()
tour=(TOUR/'打开360全景漫游.html').read_text(encoding='utf8');cfg=json.loads(re.search(r'<script id="tour-data" type="application/json">([\s\S]*?)</script>',tour).group(1))
assert cfg['modelSha256']==sha(model) and cfg['geometrySha256']==sha(geometry) and len(cfg['panoramas'])==4
fragment=(R/'09_delivery/house-v20-complete-fragment.html').read_text(encoding='utf8');assert len(fragment.encode())<1_000_000
view=json.loads(re.search(r'<script type="application/json" id="house-data-v1">([\s\S]*?)</script>',fragment).group(1));assert view['implementationPhase']=='full-design' and len(view['furnitureObjects'])==28
links=[]
for path in [OUT/'index.html',R/'09_delivery/house-v20-complete-preview.html']:
    for ref in re.findall(r'(?:href|src)="([^"]+)"',path.read_text(encoding='utf8')):
        if ref.startswith(('http:','https:','data:','#')):continue
        target=(path.parent/unquote(urlsplit(ref).path)).resolve();assert target.is_file(),(path,ref);links.append(str(target))
for name in ['顶面空调协调.svg','主卫门墙对齐.svg','门墙收口节点.svg']:ET.parse(OUT/name)
# Record both the reserved separation and the actual conservative blade envelope.
curt=g['curtainParts'];frame=next(q for q in g['furnitureObjects'] if q['id']=='laundry-enclosure');actualGap=frame['x']-max(p['closedCentreX']+math.hypot(p['w']/2,p['d']/2) for p in curt)
assert actualGap>35
pr=load('09_delivery/v20-complete/实体与动作核对.json');pr['curtainReservedSideGapMm']=pr.pop('curtainLaundrySideGapMm');pr['curtainActualRotationEnvelopeGapMm']=round(actualGap,3);write('09_delivery/v20-complete/实体与动作核对.json',pr)
seams=[]
for row in [r for r in images if r['kind']=='pano']:
    with Image.open(R/row['path']) as im:
        im=im.convert('RGB');w,h=im.size;vals=[abs(a-b) for y in range(h) for a,b in zip(im.getpixel((0,y)),im.getpixel((w-1,y)))];seams.append(dict(id=row['id'],edgeMeanAbsoluteDifference=round(sum(vals)/len(vals),3),note='descriptive pixel comparison only; not headset or seamlessness certification'))
write('09_delivery/v20-complete/图像目检.json',dict(status='reviewed',photographicViews=8,nativeViews=16,savedPhotographicFilesOpened=True,sourceMethod='built-in image_gen anchored to same-version native renders',corrections=['dining panorama pendant restored and invented exterior seating removed','balcony close/photo and sphere: extra tea-area rug removed','entry sphere: invented external furniture / washer reflection removed'],remainingConceptualDifferences=['wood/cloth/plant microdetail','illustrative distant view and daylight','small perspective, reflection and prop variations'],edgeStatistics=seams,browserVisualQA=False,headsetTested=False))

# Promote only after the concrete saved model and all deliveries pass.
if VIZ.exists():shutil.copy2(VIZ,OUT/'previous-main-fragment-v20-integration.html')
shutil.copy2(R/'09_delivery/index.html',OUT/'previous-home-index-v20-integration.html')
p=dict(presentation_revision=20,geometry_revision=20,implementation_phase='full-design',base_architecture_revision=14,model=model.relative_to(R).as_posix(),model_sha256=sha(model),geometry=geometry.relative_to(R).as_posix(),geometry_sha256=sha(geometry),style=style.relative_to(R).as_posix(),style_sha256=sha(style),tour='09_delivery/vr-tour-v07/打开360全景漫游.html',resolution=images[1]['resolution'],upscaled=False,native_anchor_resolution=[4096,2048],view_count=4,projection='monoscopic equirectangular360x180',method='same-model native spheres + built-in image_gen photographic concepts',placement_snapshot='03_layout/widget-layout-v20-complete-initial.json',source_layout_furniture_count=28,all_unaffected_positions_retained=True,ai_image_details_are_conceptual=True,exterior_is_illustrative=True,perspective_gallery='09_delivery/v20-complete/index.html',render_source_model='06_blender/home-v20-complete-render-source.blend',render_source_model_sha256=sha(R/'06_blender/home-v20-complete-render-source.blend'),metadata_confirmation='09_delivery/v20-complete/表现元数据一致性.json',office_variant='B',office_variant_status='temporary preview; homeowner material choice pending',browser_visual_qa=False,headset_tested=False)
a=copy.deepcopy(before['active']);a.update(revision=20,implementation_phase='full-design',display_version='v20实装完整版',filename=model.name,geometry=p['geometry'],geometry_sha256=p['geometry_sha256'],style=p['style'],style_sha256=p['style_sha256'],style_revision='modern-japanese-v20-complete',previous_active_filename='home-main-v20.blend',furniture_count=28,model_sha256=p['model_sha256'],live_session_verified=True,saved_native_file_verified=True,panorama_tour=p['tour'],panorama_resolution=p['resolution'],panorama_model_revision=20,panorama_presentation_revision=20,current_perspective_renders=p['perspective_gallery'],interactive_model='09_delivery/house-v20-complete-preview.html',photoreal_presentation=p,latest_layout_snapshot=p['placement_snapshot'],latest_presentation_geometry=p['geometry'],full_implementation_v20=g['features']['fullImplementationV20'],master_suite=g['features']['masterSuite'],wall_alignment_v17=g['features']['pendingWallAlignmentV17'],deepening_v19=g['features']['deepeningV19'],public_details=len(g['detailParts']),reference_details=len(g['referenceParts']),source_wall_count_current=len(g['walls']),lighting_scenes=['day','evening','dining','cleaning','viewing'],wider_v20_refinement_status='design entities implemented; selected equipment and field verification remain open',panorama_master_suite_note='v20 corridor plane aligned to z4896; diagonal inward bifold is the reversible design proposal; public four views regenerated from v20-complete.')
write('06_blender/active-model.json',a);write('06_blender/active-presentation.json',p);shutil.copy2(geometry,R/'02_geometry/geometry-master.json')
layout=dict(revision=20,implementationPhase='full-design',moveStepMm=100,modelContentVersion='v20-full-20261106',furniturePositions=[dict(id=q['id'],x=q['x'],z=q['z'],dx=0,dz=0) for q in g['furnitureObjects']])
write(p['placement_snapshot'],layout);write('03_layout/blender-layout-v20-complete.json',dict(revision=20,implementationPhase='full-design',model=p['model'],model_sha256=p['model_sha256'],verified_saved_native_file=True,live_mcp_connected=True,moveStepMm=100,positions=[dict(id=q['id'],x=q['x'],z=q['z']) for q in g['furnitureObjects']]))
write('03_layout/blender-layout-latest.json',dict(revision=20,implementationPhase='full-design',units='mm',relative_to='geometry-master-v20-complete',objects=[dict(id=q['id'],x=q['x'],z=q['z'],dx=0,dz=0,rotation_z_degrees=0) for q in g['furnitureObjects']]))
VIZ.write_text(fragment,encoding='utf8')
home=R/'09_delivery/index.html';text=home.read_text(encoding='utf8').replace('main-integration-v20/index.html','v20-complete/index.html').replace('main-integration-v20/photos/living.png','v20-complete/photos/living.png').replace('vr-tour-v06/','vr-tour-v07/').replace('house-v20-preview.html','house-v20-complete-preview.html').replace('查看餐岛与办公区整合后的四区效果','查看v20实装后的四区效果与细节');home.write_text(text,encoding='utf8')
c=load('01_brief/current-design-constraints.json');c['updated_date']=date.today().isoformat();c['v20_activation']=dict(instruction='实装v20',status='implemented in design model',activeModel=p['model'],geometry=p['geometry'],publicFurnitureOriginChanges=0,doorProposal='diagonal inward bifold',officeMaterial='B provisional',equipmentAndFieldConditions='unverified')
c['completed_design_integration']['wider_v20_detail_work']='full design geometry and coordinated presentations implemented';c['panorama_delivery'].update(version=20,presentation_revision=20,current_master_revision=20,resolution=p['resolution'],latest_placement_snapshot=p['placement_snapshot'],status='v20 full implementation four-point photographic concepts');write('01_brief/current-design-constraints.json',c)
report=dict(status='passed',promotedToActive=True,implementationPhase='full-design',modelSha256=sha(model),geometrySha256=sha(geometry),styleSha256=sha(style),furnitureCount=28,retainedOriginsChanged=0,localLinksChecked=len(links),photographicImagesChecked=8,nativeImagesChecked=16,spheres=4,oldModelGeometryAndStylePreserved=True,activeInlineSha256=sha(VIZ),nativeAndInteractiveAndPanoramaLogicPassed=True,liveBlenderMoveVerified=True,realBrowserVisualQA=False,headsetTested=False,actualCurtainRotationGapMm=round(actualGap,3))
assert sha(R/'02_geometry/geometry-master.json')==sha(geometry) and sha(VIZ)==sha(R/'09_delivery/house-v20-complete-fragment.html')
for path,digest in before['hashes'].items():
    if not path.startswith('06_blender/active-'):assert sha(R/path)==digest,path
write('09_delivery/v20-complete/最终交付核对.json',report)
print('V20_FULL_IMPLEMENTATION_ACTIVE',json.dumps(report,ensure_ascii=False))
