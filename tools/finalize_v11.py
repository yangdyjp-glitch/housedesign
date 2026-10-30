"""Publish the checked low-tea revision before the subsequent reference-driven design."""
from pathlib import Path
from itertools import combinations
from PIL import Image
import json,hashlib,shutil,zipfile,math,html
ROOT=Path(r'D:\AI-Yang.cn\HomeDesign')
def read(rel):return json.loads((ROOT/rel).read_text(encoding='utf-8'))
def write(rel,value):(ROOT/rel).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
G=ROOT/'02_geometry/geometry-master-v11.json';S=ROOT/'05_style/modern-japanese-v07.json';d=read(G.relative_to(ROOT));s=read(S.relative_to(ROOT));sha=digest(G);ssha=digest(S)
build=read('logs/model-v11-build.json');back=read('logs/model-v11-readback.json');render=read('logs/v11-render-verification.json');widget=read('logs/widget-v11-verification.json');live=read('logs/v11-live-state.json');old=read('02_geometry/geometry-master-v10.json')
assert all(q['geometry_sha256']==sha for q in [s,build,back,render])
assert all(q['style_sha256']==ssha for q in [build,back,render])
assert build['base_model_sha256']==digest(ROOT/'06_blender/home-main-v10.blend')=='e0cf9b40f2bbe494e549b6dab411713866c84f26043c61295081a491327efa00'
assert build['existing_21_meshes_preserved'] and build['latest_user_widget_positions_applied']
assert back['saved_model_reopened'] and back['furniture_count']==24 and render['draft'] is False
assert widget['dimensionTooltips']==24 and len(widget['nudged'])==24 and widget['balconyTeaFurniture']==3 and not widget['runtimeErrors']
assert widget['canvasDrag100mm'] and widget['undo'] and widget['oldStateMigrationWithoutDoubleOffsets'] and widget['latestUserPlacementsBakedWithoutDoubleOffsets'] and not widget['mobileOverflow']
assert widget['slidingDoorToggle'] and widget['doorClosingCollisionGuard']
current=live[-1]['live'];assert live[-1]['phase']=='activated' and current['revision']==11 and current['geometry_sha256']==sha and len(current['positions'])==24
assert 'V11_LIVE_TEA_MOVEMENT_DOOR_LIGHTS_VERIFIED' in json.dumps(read('logs/v11-live-operator.json'))
groups={q['id']:q for q in d['furnitureObjects']}
for p in current['positions']:
    q=groups[p['id']];assert abs(p['x']-q['x'])<.05 and abs(p['z']-q['z'])<.05 and abs(p['rotation'])<1e-6
tea=d['features']['balconyTeaSet'];assert (tea['tableHeightMm'],tea['chairSeatHeightMm'],tea['chairSizeMm'][-1])==(380,230,580)
for key in ['walls','glass','windowParts','doorParts','detailParts']:assert old[key]==d[key],key
def overlap(a,b):return all(a[k]<b[k]+b[n]-.01 and a[k]+a[n]>b[k]+.01 for k,n in [('x','w'),('z','d'),('y','h')])
fw=[(p['id'],w['id']) for p in d['furniture'] for w in d['walls'] if overlap(p,w)]
ff=[(a['id'],b['id']) for a,b in combinations(d['furniture'],2) if a['parent']!=b['parent'] and overlap(a,b)]
fd=[(p['id'],f['id']) for p in d['detailParts'] if p.get('collidable') for f in d['furniture'] if overlap(p,f)]
assert not fw and not ff and not fd,(fw,ff,fd)
door={}
for opened in [False,True]:
    pp=[dict(p,x=p['x']+(800.5 if opened and p.get('movingLeaf')=='left' else 0)) for p in d['doorParts']]
    contacts=[(p['id'],f['id']) for p in pp for f in d['furniture'] if overlap(p,f)]
    assert not contacts;door['open' if opened else 'closed']=contacts
images=[]
for view in ['living-day','dining-evening','balcony-day']:
    p=ROOT/'07_renders/v11-public'/(view+'-reference.png')
    with Image.open(p) as im:im.verify()
    with Image.open(p) as im:assert im.size==(1800,1200)
    images.append(dict(kind='Blender Cycles geometry reference',view=view,path=p.relative_to(ROOT).as_posix(),size=[1800,1200],sha256=digest(p),visually_reviewed=True))
prompts=read('07_renders/v11-public/imagegen-prompts-low-v02.json')
for item in prompts['outputs']:
    p=ROOT/item['project'];original=Path(item['original']);assert digest(p)==digest(original)
    with Image.open(p) as im:im.verify()
    with Image.open(p) as im:assert im.size==(1536,1024)
    images.append(dict(kind='built-in imagegen realistic concept',view=item['name'],path=item['project'],original=str(original),size=[1536,1024],sha256=digest(p),visually_reviewed=True,reuse_reason=item.get('reused_reason')))
layout=dict(units='mm',revision=11,relative_to='geometry-master-v11',source='logs/v11-live-state.json actual managed Blender readback',kitchenDoorOpen=False,lightingScene='day',objects=[dict(id=p['id'],x=p['x'],z=p['z'],dx=0,dz=0,rotation_z_degrees=math.degrees(p['rotation'])) for p in current['positions']])
write('03_layout/blender-layout-v11.json',layout);write('03_layout/blender-layout-latest.json',layout)
shutil.copy2(G,ROOT/'02_geometry/geometry-master.json')
active=dict(revision=11,filename='home-main-v11.blend',geometry=G.relative_to(ROOT).as_posix(),geometry_sha256=sha,style=S.relative_to(ROOT).as_posix(),style_sha256=ssha,style_revision='modern-japanese-v07',previous_active_filename='home-main-v10.blend',furniture_count=24,live_session_verified=True,cabinet_selection='C, lower navy replaced with milk yellow',cabinet_top_gap_mm=0,kitchen_sliding_door=True,door_default_open=False,public_details=29,lighting_scenes=['day','evening','cleaning'],default_lighting_scene='day',balcony_tea_set=tea,budget_considered=False,master_bath_study_only=True,private_room_boundaries_changed=False)
write('06_blender/active-model.json',active)
selection=read('05_style/cabinet-options-v08/pending-selection.json');selection.update(active_model='06_blender/home-main-v11.blend',next_action='Continue from v11 low tea furniture and latest placements; cabinet C with milk yellow remains applied');write('05_style/cabinet-options-v08/pending-selection.json',selection)
manifest=dict(revision=11,model='06_blender/home-main-v11.blend',model_sha256=digest(ROOT/'06_blender/home-main-v11.blend'),geometry_sha256=sha,style_sha256=ssha,images=images,prompts=['07_renders/v11-public/imagegen-prompts-low-v02.json','07_renders/v11-public/imagegen-prompts.json'],furniture_count=24,tea_set=tea,old_21_meshes_preserved=True,latest_user_positions_preserved=True,private_room_boundaries_changed=False,source_walls=60,window_glass=12,kitchen_door_glass=3,public_detail_parts=29,budget_considered=False,geometry_collisions=dict(furniture_wall=fw,furniture_furniture=ff,public_doors=fd,kitchen_door=door),review='04_reviews/v11审美与实用性.md',delivery_note='09_delivery/v11矮茶席与公共区效果说明.md',native_render_mode='Blender Cycles 128 samples OptiX',imagegen_mode='built-in image_gen',limitations=['AI exterior is invented; plant leaf type and fine soft upholstery may differ across views','Native model is dimensional concept, not site measurement or construction certification','Entry L cabinet is v11 baseline; new user PDF reference will be developed separately as v12'])
write('07_renders/v11-public/render-manifest.json',manifest)
cards=[]
for title,file in [('阳台 · 矮茶席','balcony-realistic-low-v02.png'),('客厅 · 暖白浅木','living-realistic-low-v02.png'),('餐厅 · 晚间氛围','dining-realistic-v01.png')]:
    cards.append('<figure><img src="'+file+'" alt="'+title+'"><figcaption>'+title+'</figcaption></figure>')
refs=''.join('<figure><img loading="lazy" src="'+q+'-reference.png" alt="实体参考"><figcaption>'+q+' · 实体参考</figcaption></figure>' for q in ['living-day','dining-evening','balcony-day'])
gallery='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>v11 矮茶席与公共区效果</title><style>body{margin:0;background:#f4f2ed;color:#283127;font:16px/1.7 system-ui,"Microsoft Yahei",sans-serif}main{max-width:1200px;margin:auto;padding:28px 18px}h1{font-size:28px}p{max-width:850px}figure{margin:28px 0;background:white;border-radius:16px;overflow:hidden}img{display:block;width:100%;height:auto}figcaption{padding:12px 18px}summary{cursor:pointer;padding:16px;background:#e5e6da;border-radius:10px}a{color:#426544}</style><main><h1>阳台矮茶席 · 客厅 · 餐厅</h1><p>矮圆桌直径700、高380mm；两把矮茶椅座面230、总高580mm。暖白、浅木、米灰，灰绿与深蓝点色。以下为实景风格概念效果，窗外景色为示意。</p>'+''.join(cards)+'<details><summary>查看同版模型实体参考图</summary>'+refs+'</details><p><a href="../../09_delivery/house-v11-preview.html">打开可移动模型</a> · 家具悬停看长宽高，100mm移动。</p><p>后续门厅、电视墙、灯光、窗帘将按新PDF另作v12，入户L柜在本版仍保留供比较。</p></main></html>'
(ROOT/'07_renders/v11-public/查看效果.html').write_text(gallery,encoding='utf-8')
files=[G,S,ROOT/'06_blender/home-main-v11.blend',ROOT/'06_blender/active-model.json',ROOT/'09_delivery/v11矮茶席与公共区效果说明.md',ROOT/'04_reviews/v11审美与实用性.md',ROOT/'03_layout/widget-layout-v10-user-latest.json',ROOT/'03_layout/widget-layout-v11-initial.json',ROOT/'03_layout/blender-layout-v11.json',ROOT/'09_delivery/house-v11-preview.html',ROOT/'tools/home_design_move.py',ROOT/'07_renders/v11-public/查看效果.html',ROOT/'07_renders/v11-public/render-manifest.json',ROOT/'07_renders/v11-public/imagegen-prompts.json',ROOT/'07_renders/v11-public/imagegen-prompts-low-v02.json']
files += [ROOT/q['path'] for q in images]+[ROOT/p for p in ['logs/model-v11-build.json','logs/model-v11-readback.json','logs/v11-source-ledger.json','logs/v11-render-verification.json','logs/widget-v11-verification.json','logs/v11-live-state.json','logs/v11-live-operator.json']]
target=ROOT/'09_delivery/v11-矮茶席与公共区效果.zip'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as archive:
    for p in files:archive.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(target) as archive:assert archive.testzip() is None;count=len(archive.namelist())
write('logs/v11-delivery-verification.json',dict(revision=11,zip=str(target),files=count,zip_valid=True,model_sha256=digest(ROOT/'06_blender/home-main-v11.blend'),geometry_sha256=sha,style_sha256=ssha,previous_v10_unchanged=True,active_model_matches=True,geometry_master_matches=True,images_visually_reviewed=True,furniture_count=24,tea_height_mm=380,tea_seat_height_mm=230,low_chair_height_mm=580,private_room_boundaries_unchanged=True,all_21_old_meshes_preserved=True,live_movement_door_lighting_verified=True,budget_considered=False))
print('V11_DELIVERY_READY',count,sha)
