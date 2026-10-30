"""Reference-driven entry, TV wall, cove and curtain proposal; preserve the user's living layout."""
from pathlib import Path
from copy import deepcopy
from itertools import combinations
import json,hashlib,math,sys
ROOT=Path(r'D:\AI-Yang.cn\HomeDesign');SOURCE=ROOT/'02_geometry/geometry-master-v11.json';DEST=ROOT/'02_geometry/geometry-master-v12.json'
assert not DEST.exists() or '--replace-draft' in sys.argv
old=json.loads(SOURCE.read_text(encoding='utf-8'));d=deepcopy(old)
d.update(revision=12,project_revision=12,title='房屋主模型 · 门厅与电视墙、弧光与梦幻帘')
d['placementBaselinesByRevision']['11']={p['id']:dict(x=p['x'],z=p['z']) for p in old['furnitureObjects']}
d['compatiblePlacementRevisions']=[4,5,6,7,8,9,10,11]
d['previousPlacements']=d['placementBaselinesByRevision']['11']
rebuild=['entry-shoe-cabinet','tv-low'];remove=['entry-return-cabinet']
d['furniture']=[p for p in d['furniture'] if p['parent'] not in rebuild+remove]
d['furnitureObjects']=[p for p in d['furnitureObjects'] if p['id'] not in remove]
for q in d['furnitureObjects']:
    if q['id'].startswith('balcony-tea-'):
        q['z']+=100;q['meshBoundsMm']['z']+=100
for p in d['furniture']:
    if p['parent'].startswith('balcony-tea-'):p['z']+=100
new=[]
def add(gid,suffix,x,z,w,dep,y,h,mat,**kw):
    p=dict(id='v12-'+gid+'-'+suffix,parent=gid,kind='furniture',shape='rounded_box',x=x,z=z,w=w,d=dep,y=y,h=h,material=mat);p.update(kw);new.append(p)
gid='entry-shoe-cabinet';x,z=0,10818
add(gid,'upper',0,z,1271,350,1600,1150,'cabinet',bevelMm=1)
for i,xx in enumerate([0,635.5]):add(gid,'upper-door-'+str(i),xx+2,z-0+0,631.5,18,1604,1142,'cabinet',bevelMm=1)
add(gid,'bench-back',0,z+330,801,20,450,1150,'wood',bevelMm=1)
add(gid,'bench-body',0,z,801,350,160,260,'cabinet',radiusMm=24)
add(gid,'bench-seat',0,z,801,350,420,30,'fabric',radiusMm=28)
add(gid,'right-low',821,z,450,350,160,1040,'cabinet',bevelMm=1)
add(gid,'right-high',821,z,450,350,1400,200,'cabinet',bevelMm=1)
add(gid,'right-back',821,z+330,450,20,1200,200,'wood',bevelMm=1)
add(gid,'niche-bottom',821,z,450,350,1182,18,'wood',bevelMm=1)
for k,xx in enumerate([821,1253]):add(gid,'right-side-'+str(k),xx,z,18,350,160,1440,'cabinet',bevelMm=1)
for i,xx in enumerate([130,310,490,670]):add(gid,'fold-hook-'+str(i),xx,z+310,28,20,1320,150,'wood',radiusMm=6)
add(gid,'base-rear',100,z+310,1071,40,0,160,'wood',bevelMm=1)
gid='tv-low';x,z=0,1800
add(gid,'floating-body',0,z,400,2700,180,252,'wood',radiusMm=22)
add(gid,'floating-top',0,z,400,2700,432,18,'wood',radiusMm=22)
for k in range(5):add(gid,'front-seam-'+str(k),399,z+450*(k+1)-1,1,2,190,230,'metal',bevelMm=0)
add(gid,'end-stone-box',0,4500,400,500,0,450,'stone',radiusMm=22)
add(gid,'service-door',399,4520,1,460,30,390,'stone',bevelMm=0)
d['furniture']+=new
def bounds(parts):
    lo={k:min(p[k] for p in parts) for k in ['x','z','y']};return dict(**lo,w=max(p['x']+p['w'] for p in parts)-lo['x'],d=max(p['z']+p['d'] for p in parts)-lo['z'],h=max(p['y']+p['h'] for p in parts)-lo['y'])
for q in d['furnitureObjects']:
    if q['id']=='entry-shoe-cabinet':q.update(name='入户一字鞋柜与换鞋位',x=0,z=10818,w=1271,d=350,h=2750,labelRotate=0,scheme='reference-entry-01',facing='negative-z',detail='短墙一字柜；通顶上柜，801宽座面高450，底部留空160；右侧1200–1400高随手格。原L形长边取消，主要通行段约1271，镜面局部1254。')
    elif q['id']=='tv-low':q.update(name='悬空电视柜与设备端柜',detail='长3200，深400，总高450；主体270高、离地180，末端500长浅石色落地设备盒，内部设备及散热待定。')
    if q['id'] in rebuild:
        q['meshBoundsMm']=bounds([p for p in new if p['parent']==q['id']]);q['dimensionsMm']=dict(length=max(q['w'],q['d']),width=min(q['w'],q['d']),height=q['h']);q['baseHeightMm']=0;q['visualHeight']=q['h']
refs=[]
def finish(suffix,x,z,w,dep,y,h,mat,**kw):
    p=dict(id='v12-'+suffix,kind='reference-finish',shape='rounded_box',x=x,z=z,w=w,d=dep,y=y,h=h,material=mat,collidable=False);p.update(kw);refs.append(p)
finish('entry-mirror',1254,9800,16,600,500,1600,'mirror',collidable=True,radiusMm=8)
finish('tv-background',4,1800,16,3200,500,1870,'wall-finish')
finish('tv-frame-left',4,1800,46,40,480,1890,'wood',radiusMm=12)
finish('tv-frame-right',4,4960,46,40,480,1890,'wood',radiusMm=12)
finish('tv-frame-top',4,1800,46,3200,2370,60,'wood',radiusMm=12)
for i,zz in enumerate([4800,4860]):finish('tv-fine-line-'+str(i),21,zz,4,3,600,1600,'metal')
finish('curtain-pelmet',853,0,5675,220,2500,20,'wall-finish')
finish('curtain-track',853,65,5675,30,2480,20,'metal')
finish('curved-cove',853,220,5675,180,2520,198,'wall-finish',shape='curved-cove',radiusMm=180,shellThicknessMm=18)
finish('cove-light-lip',853,365,5675,20,2700,18,'wall-finish')
d['referenceParts']=refs
curtains=[];n=45;start,width=853,5675
for i in range(n):
    centre=start+(i+.5)*width/n
    curtains.append(dict(id='v12-curtain-'+str(i+1),kind='curtain',shape='fabric-blade',x=centre-66,z=72,w=132,d=16,y=20,h=2460,material='curtain',closedCentreX=centre,openCentreX=start+12+i*12,centreZ=80,openRotationDegrees=90,closedRotationDegrees=0,openPlan=dict(x=start+4+i*12,z=14,w=16,d=132),collidable=False))
d['curtainParts']=curtains
def color(hexcode):
    a=[int(hexcode[k:k+2],16)/255 for k in [1,3,5]];return [v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in a]+[1]
d['furnitureMaterials']['stone']=dict(name='quiet-warm-greige-stone-intent',color=color('#D8D5CD'),roughness=.8)
d['furnitureMaterials']['mirror']=dict(name='entry-mirror',color=[.65,.7,.69,1],roughness=.05)
d['furnitureMaterials']['curtain']=dict(name='warm-white-dream-curtain',color=color('#F2F0E9'),roughness=.95)
tea=d['features']['balconyTeaSet'];tea['footprintMm']['z']+=100;tea.update(windowGapMm=270,sofaGapMm=230,reason_for_100mm_shift='reserve the new curtain blade envelope without changing the latest user sofa or coffee-table positions')
d['features']['referenceRefinement']=dict(source='00_sources/entry-tv-lighting-curtain-reference.pdf',source_sha256=hashlib.sha256((ROOT/'00_sources/entry-tv-lighting-curtain-reference.pdf').read_bytes()).hexdigest(),pages=dict(entry=[5,6,7,8],tv=[1,2,3,4],lighting=[9,10,12],curtain=[10,11,12]),reference_policy='borrow functions and proportions; source dimensions, devices, brand choices, automation and construction claims are not user instructions',entry=dict(oldClearWidthMm=921,clearWidthMm=1271,localMirrorClearWidthMm=1254,gainAtMirrorMm=333,removedFurnitureId='entry-return-cabinet',layout='single short-wall cabinet, open bench and hooks, upper closed storage, side full-length mirror',benchWidthMm=801,benchHeightMm=450,bottomGapMm=160,mainStorage='existing tv-high entry end; user inventory still deferred'),tv=dict(screenInches=85,floatingBottomMm=180,floatingBodyHeightMm=270,endBoxLengthMm=500,screenMountingUnchanged=True),curvedCove=dict(radiusMm=180,source='design proposal; not measured from PDF',lowerEdgeHeightMm=2520,topSlotMm=32),curtain=dict(type='warm-white dream curtain; translation and blade rotation are distinct',default='open',collection='single left stack to keep laundry side free',modelBladeCount=45,bladeWidthMm=132,trackHeightMm=2500,hemHeightMm=20,reservedSweepMm=dict(x=853,z=0,w=5675,d=160,y=20,h=2480),nightPrivacy='unverified; not equivalent to blackout',productAndMotorUnselected=True),lighting=dict(scenes=['day','evening','cleaning','viewing'],layers=['general direct','ceiling cove','curtain wash','cabinet niche','task lamps','entry guide'],valuesAre='relative rendering controls, not luminaire watts or photometric results'),privateBoundariesChanged=False,budgetConsidered=False)
d['features']['removedEntryLongLeg']=True
d['assumptions']+=['v12按用户PDF参考调整门厅、电视墙、灯光和窗帘；案例尺寸、品牌、100寸电视和水培挂画不直接复制。', '入户取消原L形长边，把一字鞋柜/换鞋位放在图下短墙；通道横向1271，镜面局部1254均为模型值，入户门开向及实际净宽未核。','梦幻帘模型采用单侧左收、45片通用代理；闭合、转角和夜间隐私须按最终系统验证，不等同全遮光。','新茶席整体往图下100mm，给帘片留位；用户沙发、脚凳与客厅茶几最新位置不改。','曲面反光槽R180、低边2520、帘盒和灯光分路为设计提案；实际净高、空调风口、检修及灯具未定。']
d['provenance'].update(revision=12,baseline=SOURCE.relative_to(ROOT).as_posix(),baseline_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),new_user_decisions=['鞋柜放在入口显小，需要评估','门厅、电视墙、灯光和窗帘参考用户PDF'],designer_decisions=d['features']['referenceRefinement'])
def overlaps(a,b):return all(a[k]<b[k]+b[n]-.01 and a[k]+a[n]>b[k]+.01 for k,n in [('x','w'),('z','d'),('y','h')])
ff=[(a['id'],b['id']) for a,b in combinations(d['furniture'],2) if a['parent']!=b['parent'] and overlaps(a,b)]
fw=[(a['id'],b['id']) for a in d['furniture'] for b in d['walls'] if overlaps(a,b)]
fc=[(a['id'],b['id']) for a in d['furniture'] for b in refs if b.get('collidable') and overlaps(a,b)]
assert not ff and not fw and not fc,(ff,fw,fc)
DEST.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');sha=hashlib.sha256(DEST.read_bytes()).hexdigest()
s=json.loads((ROOT/'05_style/modern-japanese-v07.json').read_text(encoding='utf-8'));s.update(version='v12-style-v08',geometry_base=DEST.relative_to(ROOT).as_posix(),geometry_sha256=sha);s['designer_decisions']['reference_refinement']=d['features']['referenceRefinement'];s['homeowner_decisions']+=['门厅、电视墙、灯光和窗帘参考用户PDF']
(ROOT/'05_style/modern-japanese-v08.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'03_layout/widget-layout-v12-initial.json').write_text(json.dumps(dict(revision=12,units='mm',furniturePositions=[dict(id=q['id'],x=q['x'],z=q['z'],dx=0,dz=0) for q in d['furnitureObjects']],kitchenDoorOpen=False,curtainOpen=True),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'logs/v12-source-ledger.json').write_text(json.dumps(dict(revision=12,geometry_sha256=sha,source=d['features']['referenceRefinement'],rebuildFurnitureIds=rebuild,removedFurnitureIds=remove,teaShiftMm=100,latestUserLivingPlacementsPreserved=True,furnitureCount=len(d['furnitureObjects']),ff=ff,fw=fw,fc=fc),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('V12_GEOMETRY_READY',len(d['furnitureObjects']),sha)
