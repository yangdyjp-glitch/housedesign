"""Publish the checked four-point native panorama tour, keep previous revisions intact."""
from pathlib import Path
from PIL import Image
import json,hashlib,math,zipfile,shutil
ROOT=Path(__file__).resolve().parents[1]
def read(rel):return json.loads((ROOT/rel).read_text(encoding='utf-8'))
def write(rel,v):(ROOT/rel).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
G=ROOT/'02_geometry/geometry-master-v13.json';S=ROOT/'05_style/modern-japanese-v09.json';M=ROOT/'06_blender/home-main-v13.blend';g=read(G.relative_to(ROOT));s=read(S.relative_to(ROOT));build=read('logs/model-v13-build.json');back=read('logs/model-v13-readback.json');renders=read('logs/v13-panorama-final-all.json');ledger=read('logs/v13-source-ledger.json');widget=read('logs/widget-v13-verification.json');live=read('logs/v13-live-state.json')[-1]['live'];cfg=read('07_renders/vr-tour-v01/tour-config.json');export=read('07_renders/vr-tour-v01/panorama-export-manifest.json');viewer=read('09_delivery/vr-tour-v01/viewer-manifest.json');qa=read('logs/vr-tour-v01-verification.json');visual=read('logs/v13-panorama-visual-review.json')
assert all(q['geometry_sha256']==sha(G) for q in [build,back,renders,s])
assert all(q['style_sha256']==sha(S) for q in [build,back,renders])
assert sha(M)==back['model_sha256']==renders['model_sha256']==cfg['modelSha256']
assert build['base_model_sha256']==read('logs/v12-delivery-verification.json')['model_sha256']==sha(ROOT/'06_blender/home-main-v12.blend')
assert renders['saved_model_reopened'] and not renders['draft'] and len(renders['renders'])==4
assert live['revision']==13 and live['geometry_sha256']==sha(G) and len(live['panorama_cameras'])==4 and len(live['positions'])==23
assert read('logs/v13-final-live-readback.json')['matched']
rows={q['id']:q for q in g['furnitureObjects']}
assert all(abs(p['x']-rows[p['id']]['x'])<.01 and abs(p['z']-rows[p['id']]['z'])<.01 for p in live['positions'])
assert len(export['images'])==len(viewer['panoramas'])==4 and visual['all_four_final_panoramas_reviewed']
assert not widget['runtimeErrors']
assert viewer['geometrySha256']==sha(G) and sha(ROOT/'09_delivery/vr-tour-v01/打开360全景漫游.html')==viewer['html']['sha256']
assert qa['status']=='passed',qa
for image in export['images']:
    p=ROOT/image['viewer_jpeg'];assert sha(p)==image['viewer_jpeg_sha256']
    with Image.open(p) as im:assert im.size==(8192,4096);im.verify()
    q=next(v for v in viewer['panoramas'] if v['id']==image['id']);assert q['sha256']==sha(p)
    assert sha(ROOT/'09_delivery/vr-tour-v01'/q['file'])==sha(p)
layout=dict(units='mm',revision=13,relative_to='geometry-master-v13',source='logs/v13-live-state.json actual managed Blender readback; three new widget offsets consumed once',kitchenDoorOpen=False,curtainMode='open',lightingScene='day',objects=[dict(id=p['id'],x=p['x'],z=p['z'],dx=0,dz=0,rotation_z_degrees=math.degrees(p['rotation'])) for p in live['positions']])
write('03_layout/blender-layout-v13.json',layout);write('03_layout/blender-layout-latest.json',layout)
write('03_layout/widget-layout-v13-initial.json',dict(revision=13,units='mm',furniturePositions=[dict(id=q['id'],x=q['x'],z=q['z'],dx=0,dz=0) for q in g['furnitureObjects']],kitchenDoorOpen=False,curtainMode='open'))
active=read('06_blender/active-model.json');assert active['revision'] in [12,13];active.update(revision=13,filename='home-main-v13.blend',geometry=G.relative_to(ROOT).as_posix(),geometry_sha256=sha(G),style=S.relative_to(ROOT).as_posix(),style_sha256=sha(S),style_revision='modern-japanese-v09',previous_active_filename='home-main-v12.blend',model_sha256=sha(M),live_session_verified=True,balcony_tea_set=g['features']['balconyTeaSet'],panorama_tour='09_delivery/vr-tour-v01/打开360全景漫游.html',panorama_nodes=4,panorama_resolution=[8192,4096],panorama_projection='monoscopic equirectangular 360x180');write('06_blender/active-model.json',active);shutil.copy2(G,ROOT/'02_geometry/geometry-master.json')
selection=read('05_style/cabinet-options-v08/pending-selection.json');selection.update(active_model='06_blender/home-main-v13.blend',next_action='Continue from v13 native panorama model, preserve latest sofa3100/1300 ottoman3200/4350 coffee2550/2650 and v12 entry/TV/cove/curtain refinements');write('05_style/cabinet-options-v08/pending-selection.json',selection)
brief=ROOT/'01_brief/project-brief.md';text=brief.read_text(encoding='utf-8');old='当前主模型为v12：`06_blender/home-main-v12.blend`、`02_geometry/geometry-master-v12.json`与`05_style/modern-japanese-v08.json`配套。';new='当前主模型为v13：`06_blender/home-main-v13.blend`、`02_geometry/geometry-master-v13.json`与`05_style/modern-japanese-v09.json`配套。本轮接续三件新位置，加入四台1600mm眼高的全景相机；四区8K单眼360×180全景及离线漫游见`09_delivery/vr-tour-v01/打开360全景漫游.html`。原v12及其效果留档。';assert old in text or new in text
text=text.replace(old,new).replace('沙发3100/1200、脚凳3200/4250、茶几2550/2450为最新交互x/z毫米坐标','沙发3100/1300、脚凳3200/4350、茶几2550/2650为最新交互x/z毫米坐标');brief.write_text(text,encoding='utf-8')
note='''\n## v13 四区360°全景漫游\n\n用户要求餐厅、门厅、客厅、阳台可以360度全方位观察。使用同一版原生Blender模型渲染四张8192×4096、完整360×180的单眼全景；离线查看器支持拖动、缩放、上下观察、热点/地图切换及全屏。四点眼高1600mm为展示设定。没有AI补画或替换墙窗、家具。\n\n本轮收到旧revision10快照的新三件位置，只消费沙发+100、脚凳+100、茶几+200mm的z增量；完整23件与v12入口/茶席/帘保持，兼容旧10和12状态且不重复偏移。新位置分别3100/1300、3200/4350、2550/2650。原v12文件不变。\n\n全景是固定点环视与节点切换，不支持自由走动或双眼立体。桌面Chrome与触控模拟已验证，未在实体手机或头显实测。未深化的窗外/厨房等保持模型占位；实测和既有净空问题继续保留。\n'''
for rel in ['01_brief/decisions.md','01_brief/assumptions.md']:
    p=ROOT/rel;body=p.read_text(encoding='utf-8');p.write_text(body+note if '## v13 四区360°全景漫游' not in body else body,encoding='utf-8')
constraints=read('01_brief/current-design-constraints.json');constraints['panorama_delivery']=dict(source_instruction='把餐厅、门厅、客厅、阳台制作成可以360度全方位观察的VR影像',scope_zh=['餐厅','门厅','客厅','阳台'],version=13,projection='monoscopic equirectangular 360x180',nodes=4,resolution=[8192,4096],viewer='offline browser, mouse/touch/keyboard; fixed nodes, no 6DOF or stereo claim');write('01_brief/current-design-constraints.json',constraints)
status=ROOT/'logs/project-status.md';body=status.read_text(encoding='utf-8');body=body.replace('## 当前：v12 门厅减量、悬空电视柜、曲面反光槽与梦幻帘','## 历史：v12 门厅减量、悬空电视柜、曲面反光槽与梦幻帘');intro='''## 当前：v13 餐厅、门厅、客厅、阳台8K全景漫游\n\n四张同版Cycles原生8K、192采样360×180单眼全景已完成并逐图目检，离线漫游支持拖动/缩放/四点热点切换/地图/全屏/原图下载；原图有GPano球面标签。最终桌面及浏览器触控模拟、完整球面方向/接缝、离线/无外链、4096纹理上限降采样等通过。没有AI补画、自由行走、双眼视差或头显实测声明。\n\n活动主模型`06_blender/home-main-v13.blend`、几何v13、风格v09；23件家具保留，合并新快照三件增量后为沙发3100/1300、脚凳3200/4350、茶几2550/2650。MCP回读和100mm移动复位、交互旧状态迁移与320px核验通过。原v12哈希不变，私人边界未改。交付入口`09_delivery/vr-tour-v01/打开360全景漫游.html`；可移动模型入口`09_delivery/house-v13-preview.html`。\n\n'''
if '## 当前：v13 ' not in body:body=body.replace('## 历史：v12 ',intro+'## 历史：v12 ',1)
status.write_text(body,encoding='utf-8')
files=list((ROOT/'09_delivery/vr-tour-v01').rglob('*'));files=[p for p in files if p.is_file() and p.name!='viewer.template.html']
files+=[M,G,S,ROOT/'06_blender/active-model.json',ROOT/'03_layout/blender-layout-v13.json',ROOT/'03_layout/widget-layout-v13-initial.json',ROOT/'09_delivery/house-v13-preview.html',ROOT/'04_reviews/v13全景审查.md',ROOT/'09_delivery/v13全景漫游说明.md']
files+=[ROOT/rel for rel in ['07_renders/vr-tour-v01/tour-config.json','07_renders/vr-tour-v01/panorama-export-manifest.json','logs/model-v13-build.json','logs/model-v13-readback.json','logs/v13-source-ledger.json','logs/v13-live-state.json','logs/v13-live-operator.json','logs/widget-v13-verification.json','logs/v13-panorama-final-all.json','logs/vr-tour-v01-verification.json','logs/v13-panorama-visual-review.json','01_brief/current-design-constraints.json']]
files+=list((ROOT/'09_delivery/vr-tour-v01-预览').glob('*.png'))
files+=[ROOT/rel for rel in ['tools/render_panorama_v13.py','tools/export_panorama_v13.py','tools/configure_panorama_v13.py','logs/v13-final-live-readback.json']]
files+=list((ROOT/'logs').glob('vr-tour-v01-final-*.png'))
target=ROOT/'09_delivery/v13-餐厅门厅客厅阳台360全景漫游.zip'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as archive:
    for p in files:archive.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(target) as archive:assert archive.testzip() is None;count=len(archive.namelist())
report=dict(revision=13,model_sha256=sha(M),geometry_sha256=sha(G),style_sha256=sha(S),old_v12_unchanged=True,panorama_count=4,panorama_resolution=[8192,4096],projection='monoscopic 360x180',camera_eye_height_mm=1600,final_images_visually_reviewed=True,viewer_offline_verified=True,viewer_qa='logs/vr-tour-v01-verification.json',live_session_verified=True,widget_verified=True,furniture_count=23,new_user_offsets_consumed_once=True,private_boundaries_unchanged=True,budget_considered=False,zip=str(target),zip_valid=True,files=count,bytes=target.stat().st_size)
write('logs/v13-delivery-verification.json',report);print('V13_PANORAMA_DELIVERY_READY',count,target.stat().st_size)
