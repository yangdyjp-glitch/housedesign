"""Bake the latest user widget placements, add a compact two-chair balcony tea set."""
from pathlib import Path
from copy import deepcopy
from itertools import combinations
import json,hashlib,sys
ROOT=Path(r'D:\AI-Yang.cn\HomeDesign');SOURCE=ROOT/'02_geometry/geometry-master-v10.json';DEST=ROOT/'02_geometry/geometry-master-v11.json'
assert not DEST.exists() or '--replace-draft' in sys.argv,'Preserve an existing revision.'
old=json.loads(SOURCE.read_text(encoding='utf-8'));d=deepcopy(old)
live=json.loads((ROOT/'logs/v11-input-live-state.json').read_text(encoding='utf-8'))['live'];assert live['revision']==10
widget_moves={'sofa-modular':(3100,1200),'ottoman':(3200,4250),'side-table':(2550,2450)}
live_by={p['id']:p for p in live['positions']};latest=[];moves={}
for q in d['furnitureObjects']:
    p=live_by[q['id']];assert abs(p['rotation'])<1e-6
    wx,wz=widget_moves.get(q['id'],(q['x'],q['z']))
    live_changed=abs(p['x']-q['x'])>.01 or abs(p['z']-q['z'])>.01
    widget_changed=wx!=q['x'] or wz!=q['z']
    if live_changed and widget_changed:assert abs(p['x']-wx)<.01 and abs(p['z']-wz)<.01,'Conflicting edits require reconciliation.'
    x,z=(p['x'],p['z']) if live_changed else (wx,wz)
    latest.append(dict(id=q['id'],x=x,z=z,dx=x-q['x'],dz=z-q['z']))
    dx,dz=x-q['x'],z-q['z'];moves[q['id']]=(dx,dz)
    q['x'],q['z']=x,z;q['meshBoundsMm']['x']+=dx;q['meshBoundsMm']['z']+=dz
for p in d['furniture']:
    dx,dz=moves[p['parent']];p['x']+=dx;p['z']+=dz
snapshot=dict(revision=10,units='mm',source='latest received in-conversation widget snapshot; unchanged entries cross-checked against live Blender',furniturePositions=latest,kitchenDoorOpen=False)
(ROOT/'03_layout/widget-layout-v10-user-latest.json').write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
d.update(revision=11,project_revision=11,title='房屋主模型 · 阳台茶席与公共区实景')
d['placementBaselinesByRevision']['10']={p['id']:dict(x=p['x'],z=p['z']) for p in latest}
d['previousPlacements']=d['placementBaselinesByRevision']['10'];d['compatiblePlacementRevisions']=[4,5,6,7,8,9,10]
new=[]
def add(gid,suffix,x,z,w,dep,y,h,mat,shape='rounded_box',**kw):
    p=dict(id=gid+'-'+suffix,parent=gid,kind='furniture',shape=shape,x=x,z=z,w=w,d=dep,y=y,h=h,material=mat)
    p.update(kw);new.append(p)
gid='balcony-tea-table';x,z=3300,170
add(gid,'top',x,z,700,700,355,25,'wood','cylinder')
add(gid,'support',x+110,z+110,480,480,335,20,'wood','cylinder')
add(gid,'stem',x+295,z+295,110,110,35,300,'wood','frustum',bottomScale=1.45,topScale=1)
add(gid,'base',x+130,z+130,440,440,0,35,'wood','cylinder')
add(gid,'tray',x+210,z+205,280,290,380,16,'walnut',radiusMm=30)
add(gid,'teapot',x+280,z+245,140,140,396,95,'ceramic','ellipsoid')
add(gid,'lid',x+312,z+277,76,76,482,12,'ceramic','cylinder')
for i,zz in enumerate([z+230,z+395]):add(gid,'cup-'+str(i),x+222,zz,65,65,396,55,'ceramic','cylinder')
for gid,x,face in [('balcony-tea-chair-1',2580,'+x'),('balcony-tea-chair-2',4160,'-x')]:
    z=220
    def chair(suffix,xx,zz,w,dep,y,h,mat,shape='rounded_box',**kw):
        if face=='-x':xx=560-xx-w
        add(gid,suffix,x+xx,z+zz,w,dep,y,h,mat,shape,**kw)
    chair('seat',40,30,480,540,170,60,'sage',radiusMm=70)
    chair('back',0,0,70,600,300,280,'fabric','ellipsoid')
    chair('back-support',25,25,40,550,220,120,'wood',radiusMm=18)
    for i,zz in enumerate([0,568]):
        chair('arm-'+str(i),85,zz,360,32,350,38,'wood',radiusMm=15)
        for j,xx in enumerate([100,410]):chair('arm-post-'+str(i)+str(j),xx,zz,32,32,210,140,'wood',radiusMm=12)
    for i,xx in enumerate([75,445]):
        for j,zz in enumerate([50,515]):chair('leg-'+str(i)+str(j),xx,zz,35,35,0,180,'wood','frustum',bottomScale=.8,topScale=1)
    for j,zz in enumerate([45,520]):chair('rail-'+str(j),70,zz,410,35,140,35,'wood',radiusMm=10)
d['furniture']+=new
def bounds(parts):
    lo={k:min(p[k] for p in parts) for k in ['x','z','y']}
    return dict(**lo,w=max(p['x']+p['w'] for p in parts)-lo['x'],d=max(p['z']+p['d'] for p in parts)-lo['z'],h=max(p['y']+p['h'] for p in parts)-lo['y'])
for gid,name,x,z,w,dep,h,face in [('balcony-tea-table','阳台矮圆茶桌',3300,170,700,700,380,None),('balcony-tea-chair-1','阳台矮茶椅1',2580,220,560,600,580,'+x'),('balcony-tea-chair-2','阳台矮茶椅2',4160,220,560,600,580,'-x')]:
    pp=[p for p in new if p['parent']==gid];b=bounds(pp)
    d['furnitureObjects'].append(dict(id=gid,name=name,type='round-tea-table' if face is None else 'low-armchair',zone='balcony',scheme='tea-01',x=x,z=z,w=w,d=dep,h=h,
        baseHeightMm=0,visualHeight=b['h'],dimensionsMm=dict(length=max(w,dep),width=min(w,dep),height=h),meshBoundsMm=b,
        detail='矮圆茶桌，桌体高380；茶盘与一壶两杯随桌移动' if face is None else '矮式扶手茶椅，沿窗相对；座面高约230',label=face is None,labelRotate=0,face=face))
tea=dict(type='low round pedestal tea table with two opposing low lounge tea chairs',tableDiameterMm=700,tableHeightMm=380,chairCount=2,chairSizeMm=[600,560,580],
    chairSeatHeightMm=230,designer_selected_dimensions=True,orientation='chairs oppose along plan x, parallel to balcony glazing',
    footprintMm=dict(x=2580,z=170,w=2140,d=700),windowGapMm=170,sofaGapMm=330,
    pullBackTrialMm=300,washerFrontClearZone=dict(x=5488,z=170,w=1000,d=600),
    rightChairWithPullbackToWasherBodyMm=1468,teaware='one small pot and two cups on one tray',
    furnitureIds=['balcony-tea-table','balcony-tea-chair-1','balcony-tea-chair-2'],siteAccuracy='concept dimensions, actual window opening and equipment governs')
d['features']['balconyTeaSet']=tea
d['features']['publicRefinement']['budget']=dict(considered=False,source='01_brief/current-design-constraints.json',historical_record='v10 allocation superseded for subsequent design')
d['assumptions']=[a for a in d['assumptions'] if '预算100000' not in a]
d['assumptions']+=['后续所有设计不考虑预算；旧10万元及分配不再作为约束。',
    'v11继承用户最新聊天内位置：沙发3100/1200、脚凳3200/4250、茶几2550/2450，不重复叠加旧500mm移动。',
    '用户进一步要求矮茶桌和矮茶椅，设计拟定阳台直径700、高380矮圆茶桌，两把座面高230、总高580矮茶椅，沿窗左右相对；均可按100mm单独移动，茶具随桌整体移动。',
    '阳台茶桌距窗线170、茶桌至沙发最近330为模型包络距离，不作为主通道；操作主要沿两椅外侧，右侧洗烘留独立操作区。',
    '主卫新增段与原主卫合并已由用户确认范围；结构、用途、排水及尺寸未核，本轮公共区渲染不执行主卫改墙。']
d['provenance'].update(revision=11,baseline=SOURCE.relative_to(ROOT).as_posix(),baseline_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),layout_source='03_layout/widget-layout-v10-user-latest.json',new_user_decisions=['阳台增加茶桌茶椅，餐厅客厅阳台实景渲染','茶桌换成矮茶桌，茶椅同理','主卫新增段与原主卫合并范围确认'],designer_decisions=tea)
def overlaps(a,b):return all(a[k]<b[k]+b[n]-.01 and a[k]+a[n]>b[k]+.01 for k,n in [('x','w'),('z','d'),('y','h')])
collisions=[(a['id'],b['id']) for a,b in combinations(d['furniture'],2) if a['parent']!=b['parent'] and overlaps(a,b)]
walls=[(a['id'],b['id']) for a in d['furniture'] for b in d['walls'] if overlaps(a,b)]
assert not collisions and not walls,(collisions,walls)
DEST.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');sha=hashlib.sha256(DEST.read_bytes()).hexdigest()
style=json.loads((ROOT/'05_style/modern-japanese-v06.json').read_text(encoding='utf-8'))
style.update(version='v11-style-v07',geometry_base=DEST.relative_to(ROOT).as_posix(),geometry_sha256=sha)
style['homeowner_decisions']+=['之后的所有内容不考虑预算，只考虑设计','阳台上再加一个茶桌和茶椅，然后把餐厅、客厅、阳台进行实景渲染','茶桌换成矮茶桌，茶椅同理']
style['designer_decisions']['balcony_tea_set']=tea;style['designer_decisions']['public_refinement']['budget']=d['features']['publicRefinement']['budget']
(ROOT/'05_style/modern-japanese-v07.json').write_text(json.dumps(style,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'03_layout/widget-layout-v11-initial.json').write_text(json.dumps(dict(revision=11,units='mm',furniturePositions=[dict(id=q['id'],x=q['x'],z=q['z'],dx=0,dz=0) for q in d['furnitureObjects']],kitchenDoorOpen=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'logs/v11-source-ledger.json').write_text(json.dumps(dict(revision=11,geometry_sha256=sha,prior_model='06_blender/home-main-v10.blend',widget_snapshot=snapshot,
    live_input='logs/v11-input-live-state.json',new_parts=len(new),tea_set=tea,existing_furniture_meshes_rebuilt=False,collisions=collisions,wall_collisions=walls,budget_considered=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('V11_GEOMETRY_READY',len(d['furnitureObjects']),len(new),sha)
