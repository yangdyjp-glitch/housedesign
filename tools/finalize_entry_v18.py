"""Promote the verified v18 model and publish the coordinated entry/public-area delivery."""
from pathlib import Path
from datetime import datetime
import json,hashlib,shutil,zipfile,html
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];DATE=datetime.now().date().isoformat()
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
def write(p,v):(ROOT/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
d=read('02_geometry/geometry-master-v18.json');audit=read('logs/v18-model-verification.json');tour=read('07_renders/vr-tour-v04/tour-config.json');vr=read('logs/vr-tour-v04-verification.json');widget=read('logs/v18-widget-verification.json')
assert vr['status']=='passed' and widget['status']=='passed' and len(d['furnitureObjects'])==28
assert audit['model_sha256']==tour['modelSha256']==sha('06_blender/home-main-v18.blend')
assert audit['geometry_sha256']==sha('02_geometry/geometry-master-v18.json')
for report in ['logs/v18-perspectives.json','logs/v18-panorama-anchors.json']:assert read(report)['model_sha256']==audit['model_sha256']
raw=read('logs/v18-native-mcp-verification.json');native=json.loads(raw['result'].split('Code executed successfully: ',1)[1]) if 'result' in raw else raw
assert native['revision']==18 and native['all_28_positions_match'];native['model_sha256']=audit['model_sha256'];write('logs/v18-native-mcp-verification.json',native)
p=dict(presentation_revision=18,geometry_revision=18,base_architecture_revision=14,model='06_blender/home-main-v18.blend',model_sha256=audit['model_sha256'],geometry='02_geometry/geometry-master-v18.json',geometry_sha256=audit['geometry_sha256'],style='05_style/modern-japanese-v18.json',style_sha256=sha('05_style/modern-japanese-v18.json'),tour='09_delivery/vr-tour-v04/打开360全景漫游.html',method='Same verified native v18 main model + built-in imagegen photographic concept treatment',resolution=tour['nativeImageResolution'],upscaled=False,native_anchor_resolution=[4096,2048],view_count=4,projection='monoscopic equirectangular 360x180',placement_snapshot='03_layout/widget-layout-v18-initial.json',source_layout_furniture_count=28,native_anchors_match_latest_placements=True,ai_image_details_are_conceptual=True,exterior_is_illustrative=True,main_editable_model_preserved=True,previous_native_8k_tour='09_delivery/vr-tour-v02/打开360全景漫游.html',perspective_gallery='09_delivery/v18-entry/index.html',entry=d['features']['entryV18'])
a=read('06_blender/active-model.json');a.update(revision=18,filename='home-main-v18.blend',geometry=p['geometry'],geometry_sha256=p['geometry_sha256'],style=p['style'],style_sha256=p['style_sha256'],style_revision='modern-japanese-v18-entry',previous_active_filename='home-main-v14.blend',furniture_count=28,live_session_verified=True,model_sha256=p['model_sha256'],panorama_tour=p['tour'],panorama_resolution=p['resolution'],panorama_model_revision=18,panorama_presentation_revision=18,current_perspective_renders=p['perspective_gallery'],interactive_model='09_delivery/house-v18-preview.html',photoreal_presentation=p,latest_layout_snapshot=p['placement_snapshot'],latest_presentation_geometry=p['geometry'],entry=d['features']['entryV18'],wall_alignment_v17=d['features']['pendingWallAlignmentV17'],panorama_master_suite_note='v14 suite boundaries retained; v17 front-wall alignment still awaits a workable door decision. Public four points use the current v18 entry and placements.')
write('06_blender/active-model.json',a);write('06_blender/active-presentation.json',p);shutil.copy2(ROOT/p['geometry'],ROOT/'02_geometry/geometry-master.json')
write('03_layout/blender-layout-v18.json',dict(revision=18,model=p['model'],model_sha256=p['model_sha256'],verified_native_mcp=True,moveStepMm=100,positions=[dict(id=q['id'],x=q['x'],z=q['z']) for q in d['furnitureObjects']]))
c=read('01_brief/current-design-constraints.json');c['updated_date']=DATE;c['entry_v18']=d['features']['entryV18'];c['wall_alignment_v17']=d['features']['pendingWallAlignmentV17'];c['panorama_delivery'].update(version=18,presentation_revision=18,current_master_revision=18,resolution=p['resolution'],latest_placement_snapshot=p['placement_snapshot'],status='Current v18 right-shoe/left-piano-bench model, photographic four-point concept preview; original native dimensions retained');write('01_brief/current-design-constraints.json',c)
gallery=ROOT/'09_delivery/v18-entry';gallery.mkdir(parents=True,exist_ok=True)
labels={'entry-left':'左侧 · 钢琴键挂板与换鞋凳','entry-right':'右侧 · 通顶鞋柜','living':'客厅','dining':'餐厅与门厅关系','balcony':'阳台低茶席'};figures=[]
for ident,label in labels.items():
    src=ROOT/'07_renders/v18-entry'/(ident+'-realistic.png');dst=gallery/src.name;shutil.copy2(src,dst)
    with Image.open(dst) as im:w,h=im.size
    figures.append(f'<figure><a href="{dst.name}"><img src="{dst.name}" width="{w}" height="{h}" alt="{html.escape(label)}" loading="lazy"></a><figcaption>{html.escape(label)}</figcaption></figure>')
gallery_html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>门厅调整 · 四区效果图</title><style>body{margin:0;background:#f5f3ed;color:#283a32;font:16px/1.7 system-ui,"Microsoft YaHei",sans-serif}main{max-width:1200px;margin:auto;padding:24px}h1{font-size:28px;font-weight:500}nav{display:flex;gap:24px;flex-wrap:wrap}a{color:inherit}section{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px}figure{margin:0}img{display:block;width:100%;height:auto}figcaption{padding:8px 0}p{max-width:68em}footer{padding:24px 0;color:#69746d;font-size:13px}@media(max-width:640px){section{grid-template-columns:1fr}main{padding:18px}}</style><main><nav><a href="../index.html">首页</a><a href="../vr-tour-v04/打开360全景漫游.html">360°全景</a><a href="../house-v18-preview.html">调整家具</a></nav><h1>右侧收鞋，左侧换鞋与临挂</h1><p>右手通顶鞋柜；左手把通长柜末端整合成换鞋凳与浅木钢琴键挂板，上方继续收纳。延续暖白、浅木和奶黄柜，保留入口转身位置。</p><section>'''+''.join(figures)+'''</section><footer>方案效果图 · AI辅助表现。材质、光影、植物与窗景为设计示意；精确尺寸以主模型与现场为准。尺寸暂拟：鞋柜1271×350×2750 mm，换鞋区1000×400 mm，座高450 mm。</footer></main></html>'''
(gallery/'index.html').write_text(gallery_html,encoding='utf-8')
note=f'''# 门厅调整 v18

{DATE}。按从图左入户、向图右走进住宅时的左右关系执行；方位仍是上南下北、左东右西。

| 区域 | 本轮布置 | 暂拟模型尺寸 |
|---|---|---|
| 进门右手，图下短墙 | 全宽通顶鞋柜，两列封闭柜门；离地1200–1400留随手格，底部留常穿鞋位 | 1271宽×350深×2750高，底空160 mm |
| 进门左手，通长柜入口端 | 1000长换鞋凳、米灰细织软垫；背后浅木钢琴键挂板，上柜连到顶 | 1000长×400深，座高450，上柜底1800、总高2750 mm |
| 临挂 | 木条收平形成连续面，四个键展开示意；挂点放两端，避免占满座位背后 | 20列×3段，开键最大前伸不超凳体投影 |

右侧鞋柜取消原内置换鞋凳、挂钩，专门收鞋物；左侧整合进已有400深柜体末端，没有再在门口加一段L形立柜。通长柜闭合中段从4500缩为3500长，末端1000换成功能凹位，上柜仍连贯。原置物格灯带已移到换鞋上柜底部；原镜面保留。钢琴键借鉴[独立翻折木挂钩原理](https://www.peruse.be/piano)，并非已选品牌或照搬产品尺寸。

鞋柜内部层板、鞋量、长靴格与外套数量继续待物品清单，不假设能容纳固定双数。钢琴键目前是可编辑的收平／展开造型，不含点击翻折动画；五金、固定、额定荷载和防夹节点未选。鞋柜、通长柜和换鞋组合均能整件100 mm移动、悬停显示长宽高；换鞋组合的2750含上柜，座高单列450。

## 查看

- [本轮五张效果图](v18-entry/index.html)：门厅左右两侧、客厅、餐厅、阳台。
- [新版四区360°](vr-tour-v04/打开360全景漫游.html)：基于当前v18完整模型，固定点环视；实际原生{p['resolution'][0]}×{p['resolution'][1]}，未放大冒充4K／8K。
- [可移动家具模型](house-v18-preview.html)：28件；保留旧状态迁移，沙发3100/1400、脚凳3200/4450、茶几2550/2850，单位mm。
- 主模型：`06_blender/home-main-v18.blend`；几何和风格以`active-model.json`为入口。

原生模型与AI效果分开留存。木纹、光影、软包、窗景和细小挂键接缝可能有表现差异，精确家具和建筑以实体模型为准。主卫扩展概念延续v14；此前墙面收回200以对齐书柜的请求仍待门口取舍，此次未改变床或主卫门洞。

## 已核与待核

原生重开核验28件实际坐标与包络、62墙源、12片玻璃；实际Blender和交互视图三件变更家具100 mm移动复位通过。旧家具快照重复迁移不叠加偏移。鞋柜仍在原1271×350占地，换鞋区在原400深通长柜占地内；入户门开向、门框和真实净宽未测，柜端距图示洞口上沿35 mm是模型余量，不作为安装收口尺寸。隐藏踢脚、上柜固定、柜门开启及挂衣后使用按现场和产品再核。后续仍不以预算约束设计。
'''
(ROOT/'09_delivery/v18门厅调整说明.md').write_text(note,encoding='utf-8')
(ROOT/'09_delivery/vr-tour-v04/摄影感全景说明.md').write_text(f'''# v18 四区摄影感全景

当前右手鞋柜、左手钢琴键换鞋区已接入同版主模型。四张原生4096×2048完整球面图经内置imagegen表现，交付原生{p['resolution'][0]}×{p['resolution'][1]}，没有上采样。提示词见`07_renders/vr-tour-v04/imagegen-prompts.json`；模型、图片与SHA见本目录来源记录。窗外及AI细节为示意，少量接缝、极点和细部差异不能当施工节点。单眼固定四点环视，桌面离线与触控模拟通过；未在实体手机或头显实测。
''',encoding='utf-8')
usage=ROOT/'09_delivery/vr-tour-v04/使用说明.txt'
if '本版对应v18门厅调整' not in usage.read_text(encoding='utf-8'):
    with usage.open('a',encoding='utf-8') as f:f.write(f'\n本版对应v18门厅调整，以模型球面基准及内置imagegen制作摄影感概念图，原生{p["resolution"][0]}×{p["resolution"][1]}，未放大；细部及窗景为示意。\n')
brief=ROOT/'01_brief/project-brief.md';text=brief.read_text(encoding='utf-8');marker='## 当前 v18 门厅调整';section=f'''{marker}（{DATE}）

活动主模型与表现统一为v18、28件家具。进门右手短墙为1271×350×2750鞋柜，左手通长柜入口末端1000×400、座450换鞋区，背后钢琴键挂板，上柜到顶；原家具最新位置保留。入口为`09_delivery/v18-entry/index.html`、`vr-tour-v04/打开360全景漫游.html`及`house-v18-preview.html`。下文v14／v16作为对应历史阶段；当前以`active-model.json`为准。v17主卫墙对齐仍待可用门口安排，未动床与门。

''';brief.write_text(text.replace('## 已有资料与范围',section+'## 已有资料与范围') if marker not in text else text,encoding='utf-8')
for rel,title,body in [('01_brief/decisions.md','v18 入户左右分工', '用户直接要求进门右侧鞋柜、左侧换鞋凳，凳后钢琴键挂物。按真实进门方向应用，尺寸与三段木条／四键展开为本轮设计拟定。沿用暖白浅木、奶黄柜与既有公共区位置，不按预算筛选。'),('01_brief/assumptions.md','v18 补充','门厅左右是沿入户行进方向，不是看图片的左右。鞋柜1271×350×2750，凳1000×400／座450均为拟定尺寸；入口开向及真实收口待核。钢琴键只表现折叠挂钩原理，未认证承载／防夹。v17主卫墙对齐未收到门口取舍，不自动采用斜角门或移动床。'),('logs/project-status.md','当前 v18 门厅与四区摄影感交付','主模型、几何、风格和交互入口已切至v18，28件。右侧通顶鞋柜、左侧钢琴键换鞋区；旧27件中25件外观／位置不动，两柜重建，新增一件换鞋组合。五张摄影感透视图及四点全景已更新，同版原生基准留档。主卫沿用v14概念，v17墙对齐仍待门口方案；后续无预算限制。下文旧“当前”段落为历史状态，最新以active-model和active-presentation为准。')]:
    path=ROOT/rel;old=path.read_text(encoding='utf-8');heading='## '+title
    if heading not in old:
        first,rest=old.split('\n',1);path.write_text(first+'\n\n'+heading+'（'+DATE+'）\n\n'+body+'\n'+rest,encoding='utf-8')
pack=ROOT/'09_delivery/v18-门厅与四区全景.zip';items=[gallery,ROOT/'09_delivery/vr-tour-v04',ROOT/'09_delivery/vr-tour-v04-预览'];files=[ROOT/'09_delivery/house-v18-preview.html',ROOT/'09_delivery/house-v18-fragment.html',ROOT/'09_delivery/v18门厅调整说明.md']
for folder in items:files.extend(p for p in folder.rglob('*') if p.is_file())
with zipfile.ZipFile(pack,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for path in files:z.write(path,path.relative_to(ROOT/'09_delivery'))
with zipfile.ZipFile(pack) as z:assert z.testzip() is None
assert pack.stat().st_size<100*1024*1024
report=dict(revision=18,date=DATE,model_sha256=p['model_sha256'],geometry_sha256=p['geometry_sha256'],style_sha256=p['style_sha256'],furniture_count=28,native_reopen_and_envelopes=True,native_mcp_moves_restored=True,widget_verified=True,vr_tests=len(vr['tests']),imagegen_mode='built-in image_gen',outputs='logs/v18-imagegen-outputs.json',gallery=p['perspective_gallery'],tour=p['tour'],package=pack.relative_to(ROOT).as_posix(),package_bytes=pack.stat().st_size,package_sha256=sha(pack.relative_to(ROOT)),main_model_not_embedded_in_viewing_zip=True,master_bath_wall_alignment_pending=True,physical_headset_tested=False)
write('logs/v18-delivery-verification.json',report);print('V18_DELIVERY_PROMOTED',28,p['resolution'],pack.stat().st_size)
