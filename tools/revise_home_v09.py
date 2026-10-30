"""Add a conceptual bypass glass slider at the homeowner's marked dining/kitchen line."""
from pathlib import Path
from copy import deepcopy
import json,hashlib,shutil
ROOT=Path(r'D:\AI-Yang.cn\HomeDesign');SOURCE=ROOT/'02_geometry/geometry-master-v08.json';DEST=ROOT/'02_geometry/geometry-master-v09.json'
assert not DEST.exists(),'Preserve previously published revisions.'
raw=SOURCE.read_bytes();d=json.loads(raw);old=deepcopy(d)
live=json.loads((ROOT/'logs/v09-input-live-state.json').read_text(encoding='utf-8'))['live'];assert live['revision']==8
for p in live['positions']:
    g=next(g for g in d['furnitureObjects'] if g['id']==p['id']);assert abs(p['rotation'])<1e-6
    dx=p['x']-g['x'];dz=p['z']-g['z']
    for part in d['furniture']:
        if part['parent']==g['id']:part['x']+=dx;part['z']+=dz
    g['x']=p['x'];g['z']=p['z'];g['meshBoundsMm']['x']+=dx;g['meshBoundsMm']['z']+=dz
d.update(revision=9,project_revision=9,title='房屋主模型 · 奶黄通顶柜与餐厨玻璃推拉门')
d['placementBaselinesByRevision']['8']={g['id']:dict(x=g['x'],z=g['z']) for g in old['furnitureObjects']}
d['previousPlacements']=d['placementBaselinesByRevision']['8'];d['compatiblePlacementRevisions']=[4,5,6,7,8]
photo=Path(r'C:\Users\ADMINI~1\AppData\Local\Temp\codex-clipboard-bf8cd265-267d-49b0-bea3-1a3cd1b6ac8f.png')
archive=ROOT/'00_sources/v09-dining-kitchen-door-markup.png';shutil.copy2(photo,archive)
leftwall=next(w for w in d['walls'] if w['id']=='left-short-partition-end');rightwall=next(w for w in d['walls'] if w['id']=='front-facade-0')
x=leftwall['x']+leftwall['w'];end=rightwall['x'];z=leftwall['z'];width=end-x;totalheight=2750
assert (x,end,z,width)==(1391,3082,9635,1691)
jamb=25;inside=x+jamb;innerend=end-jamb;innerwidth=width-2*jamb;overlap=40;leafwidth=(innerwidth+overlap)/2;travel=innerwidth-leafwidth
rows=[]
def box(suffix,xx,zz,w,dep,y,h,leaf=None,glass=False):
    p=dict(id='kitchen-slider-'+suffix,kind='door-glass' if glass else 'door-frame',shape='box',x=xx,z=zz,w=w,d=dep,y=y,h=h,
        material='door-glass' if glass else 'door-frame',assembly='kitchen-slider',source_refs=['v09-user-door-intent','v08-existing-opening','v09-proposed-door-system'])
    if leaf:p['movingLeaf']=leaf
    rows.append(p)
box('jamb-left',x,z,jamb,120,0,totalheight);box('jamb-right',end-jamb,z,jamb,120,0,totalheight)
box('overhead-track',inside,z,innerwidth,120,2350,75)
box('transom-top',inside,z,innerwidth,120,2725,25)
box('upper-fixed-glass',inside,z+55,innerwidth,10,2425,300,glass=True)
for name,a,zz in [('left',inside,z+17),('right',innerend-leafwidth,z+77)]:
    box(name+'-stile-left',a,zz,28,36,8,2342,leaf=name)
    box(name+'-stile-right',a+leafwidth-28,zz,28,36,8,2342,leaf=name)
    box(name+'-rail-bottom',a+28,zz,leafwidth-56,36,8,40,leaf=name)
    box(name+'-rail-top',a+28,zz,leafwidth-56,36,2322,28,leaf=name)
    box(name+'-glass',a+28,zz+13,leafwidth-56,10,48,2274,leaf=name,glass=True)
    hx=a+leafwidth-21 if name=='left' else a+7
    hz=zz-10 if name=='left' else zz+36
    box(name+'-pull',hx,hz,14,10 if name=='left' else 7,1000,250,leaf=name)
box('small-guide-left',inside+travel+14,z+12,20,46,0,8)
box('small-guide-right',innerend-42,z+72,20,46,0,8)
d['doorParts']=rows
door=dict(id='kitchen-slider',name='餐厨玻璃推拉门',type='two-leaf-bypass-overhead-slider',location='red-marked junction between dining and kitchen',
    x=x,z=z,widthMm=width,depthMm=120,totalHeightMm=2750,slidingLeafTopMm=2350,upperFixedGlass=True,
    openingSide='left opens, both leaves stack right',openTravelMm=travel,clearOpeningProvisionalMm=travel,
    leafWidthMm=leafwidth,overlapMm=overlap,jambWidthMm=jamb,track='overhead double track, local floor guides only',
    finish='existing warm dark-grey thin frame and clear glass',defaultOpen=False,frameSystemIsConcept=True,
    sourceReference=archive.relative_to(ROOT).as_posix(),sourceSHA256=hashlib.sha256(archive.read_bytes()).hexdigest(),
    modelOpeningSource=['left-short-partition-end interior edge x1391','front-facade-0 left edge x3082','z9635 existing kitchen boundary'],
    dimensionStatus='Existing model fit, unmeasured on site; two-leaf configuration, height, top light, tracks and finish are designer proposals')
d['features']['kitchenSlidingDoor']=door
d['assumptions'] += ['用户要求红框餐厨交界增加玻璃推拉门；位置来源为本轮批注，未要求拆改任何原墙。',
    '门位按旧模型左短墙内边1391至前外墙起点3082、z9635布置，总宽1691为拟合值。双扇错位吊轨、暖灰细框、左扇右移叠放及上部固定玻璃均为本轮设计细化。',
    '门组总高2750随暂定净高，门扇顶2350、上方固定玻璃补到顶；开启约800.5净宽是模型包络值，实际轨道/拉手/限位和产品会影响通行净宽。',
    '门框25、扇框28、玻璃显示10、轨道120×75及小地导是概念外观包络，不作为产品五金或结构规格；吊轨基层与固定、墙顶/地面及门系统密封须深化。']
d['provenance'].update(revision=9,baseline=SOURCE.relative_to(ROOT).as_posix(),baseline_sha256=hashlib.sha256(raw).hexdigest(),
    layout='21 latest live furniture positions retained; no furniture movement requested',new_user_decisions=['glass sliding door at marked dining/kitchen boundary'])
DEST.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
style=json.loads((ROOT/'05_style/modern-japanese-v04.json').read_text(encoding='utf-8'))
style.update(version='v09-style-v05',geometry_base=DEST.relative_to(ROOT).as_posix(),geometry_sha256=hashlib.sha256(DEST.read_bytes()).hexdigest())
style['homeowner_decisions']+=['餐厨红框位置增加玻璃推拉门']
style['designer_decisions']['kitchen_sliding_door']=door
(ROOT/'05_style/modern-japanese-v05.json').write_text(json.dumps(style,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'03_layout/widget-layout-v09-initial.json').write_text(json.dumps(dict(revision=9,units='mm',furniturePositions=[dict(id=g['id'],x=g['x'],z=g['z'],dx=0,dz=0) for g in d['furnitureObjects']],kitchenDoorOpen=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
ledger=dict(reference=str(archive),source_sha256=door['sourceSHA256'],geometry_sha256=style['geometry_sha256'],furniture_positions='logs/v09-input-live-state.json',door=door,
    source_ledger=[dict(id='v09-user-door-intent',type='user_instruction',locator='current user request and red-marked image',artifact=str(archive)),
        dict(id='v08-existing-opening',type='prior_provisional_geometry',artifact=SOURCE.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(raw).hexdigest()),
        dict(id='v09-proposed-door-system',type='designer_proposal',locator='double bypass slider in existing gap; not product engineering')])
(ROOT/'logs/v09-source-ledger.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('V09_GEOMETRY_READY',len(rows),door['widthMm'],door['clearOpeningProvisionalMm'])
