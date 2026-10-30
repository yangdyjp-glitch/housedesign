"""Publish only the verified reference-driven public-area proposal."""
from pathlib import Path
from itertools import combinations
from PIL import Image
import json,hashlib,shutil,zipfile,math,html
ROOT=Path(r'D:\AI-Yang.cn\HomeDesign')
def read(rel):return json.loads((ROOT/rel).read_text(encoding='utf-8'))
def write(rel,value):(ROOT/rel).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
G=ROOT/'02_geometry/geometry-master-v12.json';S=ROOT/'05_style/modern-japanese-v08.json';d=read(G.relative_to(ROOT));s=read(S.relative_to(ROOT));sha=digest(G);ssha=digest(S)
build=read('logs/model-v12-build.json');back=read('logs/model-v12-readback.json');render=read('logs/v12-render-verification.json');widget=read('logs/widget-v12-verification.json');live=read('logs/v12-live-state.json');old=read('02_geometry/geometry-master-v11.json');previous=read('logs/v11-delivery-verification.json')
assert all(q['geometry_sha256']==sha for q in [s,build,back,render])
assert all(q['style_sha256']==ssha for q in [build,back,render])
assert build['base_model_sha256']==previous['model_sha256']==digest(ROOT/'06_blender/home-main-v11.blend')
assert build['furniture_count']==23 and build['preserved_meshes']==21 and build['latest_living_positions_preserved']
assert back['saved_model_reopened'] and len(render['renders'])==6 and not render['draft']
assert widget['dimensionTooltips']==23 and len(widget['nudged'])==23 and not widget['runtimeErrors']
assert widget['curtainModes']==3 and widget['curtainActivityZoneGuard'] and widget['oldStateMigrationWithoutDoubleOffsets'] and not widget['mobileOverflow']
assert widget['slidingDoorToggle'] and widget['doorClosingCollisionGuard']
current=live[-1]['live'];assert live[-1]['phase']=='activated' and current['revision']==12 and current['geometry_sha256']==sha and len(current['positions'])==23
assert 'V12_LIVE_TEA_MOVEMENT_DOOR_LIGHTS_VERIFIED' in json.dumps(read('logs/v12-live-operator.json'))
groups={q['id']:q for q in d['furnitureObjects']};oldgroups={q['id']:q for q in old['furnitureObjects']}
for p in current['positions']:
    q=groups[p['id']];assert abs(p['x']-q['x'])<.05 and abs(p['z']-q['z'])<.05 and abs(p['rotation'])<1e-6
for gid in ['sofa-modular','ottoman','side-table']:
    assert (groups[gid]['x'],groups[gid]['z'])==(oldgroups[gid]['x'],oldgroups[gid]['z'])
for key in ['walls','glass','windowParts','doorParts','detailParts']:assert old[key]==d[key],key
assert len(d['referenceParts'])==11 and len(d['curtainParts'])==45 and 'entry-return-cabinet' not in groups
source=ROOT/d['features']['referenceRefinement']['source'];original=Path(r'C:\Users\Administrator\Desktop\装修\门厅与客厅与灯光设计拆解.pdf')
assert digest(source)==digest(original)==d['features']['referenceRefinement']['source_sha256']
assert d['features']['publicRefinement']['budget']['considered'] is False
def overlap(a,b):return all(a[k]<b[k]+b[n]-.01 and a[k]+a[n]>b[k]+.01 for k,n in [('x','w'),('z','d'),('y','h')])
fw=[(p['id'],w['id']) for p in d['furniture'] for w in d['walls'] if overlap(p,w)]
ff=[(a['id'],b['id']) for a,b in combinations(d['furniture'],2) if a['parent']!=b['parent'] and overlap(a,b)]
fd=[(p['id'],f['id']) for p in d['detailParts']+d['referenceParts'] if p.get('collidable') for f in d['furniture'] if overlap(p,f)]
fc=[p['id'] for p in d['furniture'] if overlap(p,d['features']['referenceRefinement']['curtain']['reservedSweepMm'])]
assert not fw and not ff and not fd and not fc,(fw,ff,fd,fc)
door={}
for opened in [False,True]:
    pp=[dict(p,x=p['x']+(800.5 if opened and p.get('movingLeaf')=='left' else 0)) for p in d['doorParts']]
    contacts=[(p['id'],f['id']) for p in pp for f in d['furniture'] if overlap(p,f)]
    assert not contacts;door['open' if opened else 'closed']=contacts
images=[];views=['living-day','dining-evening','balcony-day','entry-evening','tv-evening','curtain-evening']
def inspect(path,size):
    with Image.open(path) as im:assert im.format=='PNG';im.verify()
    with Image.open(path) as im:assert im.size==size,(str(path),im.size,size)
for view in views:
    p=ROOT/'07_renders/v12-reference'/(view+'-reference.png');size=(1200,1800) if view=='entry-evening' else (1800,1200);inspect(p,size)
    images.append(dict(kind='Blender Cycles geometry reference',view=view,path=p.relative_to(ROOT).as_posix(),size=list(size),sha256=digest(p),visually_reviewed=True))
prompts=read('07_renders/v12-reference/imagegen-prompts.json');assert prompts['geometry_sha256']==sha and len(prompts['outputs'])==6
for item in prompts['outputs']:
    p=ROOT/item['project'];original=Path(item['original']);assert digest(p)==digest(original);size=(1024,1536) if item['view']=='entry-evening' else (1536,1024);inspect(p,size)
    images.append(dict(kind='built-in imagegen realistic concept',view=item['view'],path=item['project'],original=str(original),size=list(size),sha256=digest(p),visually_reviewed=True))
layout=dict(units='mm',revision=12,relative_to='geometry-master-v12',source='logs/v12-live-state.json actual managed Blender readback',kitchenDoorOpen=False,curtainMode='open',lightingScene='day',objects=[dict(id=p['id'],x=p['x'],z=p['z'],dx=0,dz=0,rotation_z_degrees=math.degrees(p['rotation'])) for p in current['positions']])
write('03_layout/blender-layout-v12.json',layout);write('03_layout/blender-layout-latest.json',layout);shutil.copy2(G,ROOT/'02_geometry/geometry-master.json')
active=dict(revision=12,filename='home-main-v12.blend',geometry=G.relative_to(ROOT).as_posix(),geometry_sha256=sha,style=S.relative_to(ROOT).as_posix(),style_sha256=ssha,style_revision='modern-japanese-v08',previous_active_filename='home-main-v11.blend',furniture_count=23,live_session_verified=True,cabinet_selection='C, lower navy replaced with milk yellow',cabinet_top_gap_mm=0,kitchen_sliding_door=True,door_default_open=False,public_details=29,reference_details=11,curtain_blades=45,curtain_default='open',curtain_translation_and_rotation_separate=True,lighting_scenes=['day','evening','cleaning','viewing'],default_lighting_scene='day',reference_pdf='00_sources/entry-tv-lighting-curtain-reference.pdf',entry_clear_width_mm=1271,entry_mirror_local_clear_width_mm=1254,balcony_tea_set=d['features']['balconyTeaSet'],budget_considered=False,master_bath_study_only=True,private_room_boundaries_changed=False)
write('06_blender/active-model.json',active)
selection=read('05_style/cabinet-options-v08/pending-selection.json');selection.update(active_model='06_blender/home-main-v12.blend',next_action='Continue from v12 reference-driven entry, TV wall, cove and dream curtain; keep latest user living placements and cabinet C milk-yellow selection');write('05_style/cabinet-options-v08/pending-selection.json',selection)
manifest=dict(revision=12,model='06_blender/home-main-v12.blend',model_sha256=digest(ROOT/'06_blender/home-main-v12.blend'),geometry_sha256=sha,style_sha256=ssha,images=images,prompts='07_renders/v12-reference/imagegen-prompts.json',reference_pdf=d['features']['referenceRefinement'],furniture_count=23,preserved_meshes=21,rebuild=['tv-low','entry-shoe-cabinet'],removed=['entry-return-cabinet'],latest_user_living_positions_preserved=True,tea_shift_mm=100,private_room_boundaries_changed=False,budget_considered=False,source_walls=60,window_glass=12,kitchen_door_glass=3,public_detail_parts=29,reference_parts=11,curtain_blades=45,geometry_collisions=dict(furniture_wall=fw,furniture_furniture=ff,fixed_finishes=fd,curtain_reserved=fc,kitchen_door=door),native_render_mode='Blender Cycles 128 samples OptiX',imagegen_mode='built-in image_gen',saved_model_metadata_refreshed_after_renders=True,metadata_refresh_changed_geometry_or_lighting=False,review='04_reviews/v12审美与实用性.md',delivery_note='09_delivery/v12门厅电视墙灯光窗帘说明.md',limitations=['All dimensions provisional; entry door hinge, site net width and equipment unknown','Curtain motor/product, night privacy and blackout not verified; local curtain sweep-to-laundry envelope only10mm','AI exterior, plant leaves, fine folds, reflections and a small day-view ceiling-edge addition are illustrative; not written back','Lighting is relative render staging, not measured illuminance, fixture selection or construction approval'])
write('07_renders/v12-reference/render-manifest.json',manifest)
titles={'entry-evening':'门厅 · 一字柜与换鞋位','tv-evening':'电视墙 · 留白与悬空柜','living-day':'客厅 · 日间','curtain-evening':'客厅 · 梦幻帘晚间','dining-evening':'餐厅 · 四椅靠墙','balcony-day':'阳台 · 矮茶席'}
cards=[]
for view in ['entry-evening','tv-evening','living-day','curtain-evening','dining-evening','balcony-day']:
    cards.append('<figure'+(' class="portrait"' if view=='entry-evening' else '')+'><img loading="lazy" src="'+view+'-realistic-v01.png" alt="'+titles[view]+'"><figcaption>'+titles[view]+'</figcaption></figure>')
refs=''.join('<figure'+(' class="portrait"' if v=='entry-evening' else '')+'><img loading="lazy" src="'+v+'-reference.png" alt="实体参考"><figcaption>'+titles[v]+' · 实体参考</figcaption></figure>' for v in views)
gallery='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>v12 门厅电视墙灯光窗帘</title><style>body{margin:0;background:#f4f2ed;color:#283127;font:16px/1.7 system-ui,"Microsoft Yahei",sans-serif}main{max-width:1200px;margin:auto;padding:28px 18px}h1{font-size:28px}p{max-width:850px}figure{margin:28px 0;background:white;border-radius:16px;overflow:hidden}figure.portrait{max-width:600px;margin:28px auto}img{display:block;width:100%;height:auto}figcaption{padding:12px 18px}summary{cursor:pointer;padding:16px;background:#e5e6da;border-radius:10px}a{color:#426544}</style><main><h1>轻门厅 · 留白电视墙 · 弧光梦幻帘</h1><p>依据用户PDF参考调整。入口取消L形长边，镜位局部横向余量约1254mm；暖白浅木，奶黄柜保留。矮茶桌高380、茶椅座高230mm。尺寸为当前模型提案。</p>'+''.join(cards)+'<details><summary>查看同版模型实体参考图</summary>'+refs+'</details><p><a href="../../09_delivery/house-v12-preview.html">打开可移动模型</a> · 23件家具悬停看长宽高，100mm移动；梦幻帘三状态。</p><p>以上为内置imagegen实景风格概念效果。外景、植物叶型、帘面微褶和反射为示意，精确几何以实体模型为准。具体帘系统、门开向、灯具与节点待深化。</p></main></html>'
(ROOT/'07_renders/v12-reference/查看效果.html').write_text(gallery,encoding='utf-8')
files=[G,S,ROOT/'06_blender/home-main-v12.blend',ROOT/'06_blender/active-model.json',ROOT/'09_delivery/v12门厅电视墙灯光窗帘说明.md',ROOT/'04_reviews/v12审美与实用性.md',ROOT/'03_layout/widget-layout-v11-initial.json',ROOT/'03_layout/widget-layout-v12-initial.json',ROOT/'03_layout/blender-layout-v12.json',ROOT/'09_delivery/house-v12-preview.html',ROOT/'tools/home_design_move.py',source,ROOT/'01_brief/current-design-constraints.json',ROOT/'01_brief/project-brief.md',ROOT/'01_brief/assumptions.md',ROOT/'01_brief/decisions.md',ROOT/'logs/project-status.md',ROOT/'07_renders/v12-reference/查看效果.html',ROOT/'07_renders/v12-reference/render-manifest.json',ROOT/'07_renders/v12-reference/imagegen-prompts.json']
files += [ROOT/q['path'] for q in images]+[ROOT/p for p in ['logs/model-v12-build.json','logs/model-v12-readback.json','logs/v12-source-ledger.json','logs/v12-render-verification.json','logs/widget-v12-verification.json','logs/v12-live-state.json','logs/v12-live-operator.json']]+list((ROOT/'00_sources/reference-pages-v12').glob('page-*.png'))
target=ROOT/'09_delivery/v12-门厅电视墙灯光窗帘与矮茶席.zip'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as archive:
    for p in files:archive.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(target) as archive:assert archive.testzip() is None;count=len(archive.namelist())
report=dict(revision=12,zip=str(target),files=count,zip_valid=True,model_sha256=digest(ROOT/'06_blender/home-main-v12.blend'),geometry_sha256=sha,style_sha256=ssha,previous_v11_unchanged=True,active_model_matches=True,geometry_master_matches=G.read_bytes()==(ROOT/'02_geometry/geometry-master.json').read_bytes(),images_visually_reviewed=True,image_count=12,furniture_count=23,preserved_meshes=21,entry_local_width_mm=1254,curtain_states_verified=3,lighting_scenes_verified=4,private_room_boundaries_unchanged=True,latest_user_living_positions_preserved=True,live_movement_door_curtain_lighting_verified=True,budget_considered=False)
write('logs/v12-delivery-verification.json',report);print('V12_DELIVERY_READY',count,sha)
