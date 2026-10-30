"""Apply the user's six furniture changes to the preserved latest layout (mm)."""
from pathlib import Path
from copy import deepcopy
import hashlib, json, math, shutil

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'02_geometry/geometry-master-v05.json'
OUT=ROOT/'02_geometry/geometry-master-v06.json'
if OUT.exists():raise FileExistsError('Preserve v06; choose a new version for subsequent edits')
data=json.loads(BASE.read_text(encoding='utf-8'))
old=deepcopy(data['furnitureObjects'])
changed={'tv-high','television','sofa-modular','side-table','double-desk','office-chair-2','dining-table','dining-chair-1','dining-chair-2'}
objects=[o for o in data['furnitureObjects'] if o['id'] not in changed]
parts=[p for p in data['furniture'] if p['parent'] not in changed]

def obj(id,name,zone,scheme,x,z,w,d,h,detail,facing=None,label=False,rotate=0,dimensions=None):
    row=dict(id=id,name=name,zone=zone,scheme=scheme,x=x,z=z,w=w,d=d,h=h,detail=detail,label=label,labelRotate=rotate,
             placement_source='user furniture revision v06; previous manual positions retained unless affected by resized assembly')
    if facing:row['facing']=facing
    if dimensions:row['dimensionsMm']=dict(zip(['length','width','height'],dimensions))
    objects.append(row);return id

def b(parent,tag,x,z,w,d,y,h,material='wood',shape='box'):
    assert min(w,d,h)>0
    parts.append(dict(id=parent+'-'+tag,parent=parent,kind='furniture',shape=shape,x=x,z=z,w=w,d=d,y=y,h=h,material=material))
def cyl(parent,tag,cx,cz,r,y,h,material='metal'):
    b(parent,tag,cx-r,cz-r,2*r,2*r,y,h,material,'cylinder')
def cabinet(parent,tag,x,z,w,d,y,h,doors=2):
    b(parent,tag+'-body',x,z,w,d,y,h,'cabinet')
    b(parent,tag+'-top',x,z,w,d,y+h-20,20,'wood')
    for i in range(doors):
        zz=z+i*d/doors
        b(parent,tag+f'-door-{i}',x+w-18,zz+4,18,d/doors-8,y+4,h-28,'cabinet')
        b(parent,tag+f'-handle-{i}',x+w-3,zz+d/doors/2-45,3,90,y+h*.62,10,'metal')

# A 16:9 true-85-inch screen in a generic, rounded installation envelope.
q=obj('television','85英寸电视','red','A',30,2450,70,1900,1100,
      '85英寸16:9屏幕，机身按1900×70×1100 mm示意；挂装下沿600 mm，中心1150 mm；实际外壳依所选型号核对。',
      'positive-x',dimensions=(1900,70,1100))
b(q,'body',30,2450,65,1900,600,1100,'metal')
screen_w=85*25.4*16/math.sqrt(16**2+9**2);screen_h=screen_w*9/16
b(q,'screen',95,2450+(1900-screen_w)/2,5,screen_w,600+(1100-screen_h)/2,screen_h,'screen')

# Continuous 4500 mm entry storage meets the existing low cabinet at z=5000.
q=obj('tv-high','入户至电视通长立柜','red','A',0,5000,400,4500,2400,
      '沿左墙由入户端接到电视低柜：4500×400×2400 mm。靠门端约1m宽置物格，离地1200–1400 mm，净高200 mm、净深380 mm。',
      'positive-x',label=True,rotate=-90,dimensions=(4500,400,2400))
cabinet(q,'main',0,5000,400,3500,60,2340,7)
cabinet(q,'entry-lower',0,8500,400,1000,60,1140,2)
cabinet(q,'entry-upper',0,8500,400,1000,1400,1000,2)
b(q,'entry-niche-back',0,8500,20,1000,1200,200,'wood')
b(q,'entry-niche-side-a',20,8500,380,20,1200,200,'wood')
b(q,'entry-niche-side-b',20,9480,380,20,1200,200,'wood')
b(q,'plinth',40,5040,320,4420,0,60,'metal')
b(q,'niche-tray',210,8800,130,260,1200,18,'wood')

# Keep the existing sofa back at x=4800 and its southern end at z=4300.
# Length grows northward; the chaise is at the image's upper end and extends toward TV.
q=obj('sofa-modular','贵妃组合沙发','blue','B',2900,1300,1900,3000,850,
      '总长3000 mm、常规位进深950 mm、上端贵妃位进深1900 mm、高850 mm、坐高430 mm。贵妃位位于平面图上端，朝电视伸出。',
      'negative-x',True,dimensions=(3000,1900,850))
b(q,'back',4660,1300,140,3000,280,570,'fabric-dark')
b(q,'main-base',3870,2300,910,1980,100,190,'fabric-dark')
b(q,'chaise-base',2920,1320,1740,960,100,190,'fabric-dark')
b(q,'chaise-cushion',2900,1440,1760,850,290,140,'fabric')
b(q,'chaise-back-cushion',4550,1450,110,820,430,350,'fabric')
for i in range(2):
    zz=2310+i*925
    b(q,f'seat-{i}',3850,zz,800,905,290,140,'fabric')
    b(q,f'back-cushion-{i}',4550,zz+4,110,897,430,350,'fabric')
b(q,'north-arm',2900,1300,1900,140,280,350,'fabric')
b(q,'south-arm',3850,4160,950,140,280,350,'fabric')
for x,z in [(2970,1370),(4670,1370),(2970,2200),(3920,2370),(3920,4170),(4670,4170)]:
    b(q,f'foot-{x}-{z}',x,z,55,55,0,100,'metal')

q=obj('side-table','长方茶几','blue','B',2650,2750,700,1400,400,
      '配3000 mm组合沙发的1400×700×400 mm茶几；与常规沙发前沿留500 mm，与贵妃位端面留450 mm。',
      label=True,rotate=-90,dimensions=(1400,700,400))
b(q,'top',2650,2750,700,1400,370,30,'wood')
b(q,'lower-shelf',2690,2790,620,1320,110,20,'cabinet')
for x in [2690,3270]:
    for z in [2790,4070]:b(q,f'leg-{x}-{z}',x,z,40,40,0,370,'metal')

q=obj('double-desk','双人办公桌','green','B',5300,2000,700,2400,750,
      '建议桌体2400×700×750 mm，每席宽1200 mm。保留双工位布置，暂仅保留1把办公椅；含显示器示意总高1300 mm。',
      'negative-x',True,-90,dimensions=(2400,700,750))
b(q,'top',5300,2000,700,2400,720,30,'wood')
for x in [5340,5910]:
    for z in [2040,4310]:b(q,f'leg-{x}-{z}',x,z,50,50,0,720,'metal')
b(q,'rail',5340,2040,40,2320,645,55,'metal')
for i,cz in enumerate([2600,3800],1):
    cyl(q,f'monitor-base-{i}',5500,cz,110,750,20)
    b(q,f'monitor-stand-{i}',5430,cz-22,45,44,770,235,'metal')
    b(q,f'monitor-body-{i}',5400,cz-250,45,500,970,330,'metal')
    b(q,f'monitor-screen-{i}',5445,cz-238,3,476,982,306,'screen')
    b(q,f'keyboard-{i}',5760,cz-220,140,440,750,16,'metal')
    cyl(q,f'mouse-{i}',5870,cz+310,35,750,20)

q=obj('dining-table','四人靠墙餐桌','ink','B',2282,7300,800,1600,750,
      '1600×800×750 mm；长边仍靠客卫外墙，外侧两椅、桌两端各一椅，共4张，取消卡座。',
      label=True,rotate=-90,dimensions=(1600,800,750))
b(q,'top',2282,7300,800,1600,720,30)
for x in [2332,2982]:
    for z in [7350,8800]:b(q,f'leg-{x}-{z}',x,z,50,50,0,720)

def dining_chair(number,x,z,facing):
    q=obj(f'dining-chair-{number}',f'餐椅{number}','ink','B',x,z,450,450,850,
          '四人餐桌的活动餐椅，座高420 mm；不设靠墙侧座位。',facing,dimensions=(450,450,850))
    b(q,'seat',x,z,450,450,420,40,'fabric')
    if facing=='positive-x':b(q,'back',x,z,55,450,460,390)
    elif facing=='positive-z':b(q,'back',x,z,450,55,460,390)
    else:b(q,'back',x,z+395,450,55,460,390)
    for xx in [x+20,x+380]:
        for zz in [z+20,z+380]:b(q,f'leg-{xx}-{zz}',xx,zz,50,50,0,420)
dining_chair(1,1832,7550,'positive-x')
dining_chair(2,1832,8200,'positive-x')
dining_chair(3,2457,6850,'positive-z')
dining_chair(4,2457,8900,'negative-z')

order=['tv-low','tv-high','television','sofa-modular','ottoman','side-table','double-desk','office-chair-1','bookcase','dining-table']+[f'dining-chair-{i}' for i in range(1,5)]
objects.sort(key=lambda o:order.index(o['id']))
for o in objects:
    pp=[p for p in parts if p['parent']==o['id']]
    x0=min(p['x'] for p in pp);x1=max(p['x']+p['w'] for p in pp)
    z0=min(p['z'] for p in pp);z1=max(p['z']+p['d'] for p in pp)
    y0=min(p['y'] for p in pp);y1=max(p['y']+p['h'] for p in pp)
    o['visualHeight']=y1;o['baseHeightMm']=y0
    o['meshBoundsMm']=dict(x=x0,z=z0,y=y0,w=x1-x0,d=z1-z0,h=y1-y0)
    if 'dimensionsMm' not in o:
        o['dimensionsMm']=dict(length=max(x1-x0,z1-z0),width=min(x1-x0,z1-z0),height=y1-y0)
data.update(title='房屋主模型 · 85英寸与贵妃沙发 · 家具悬停尺寸',revision=6,project_revision=6,furniture=parts,furnitureObjects=objects)
data['previousPlacements']={o['id']:dict(x=o['x'],z=o['z']) for o in old}
data['compatiblePlacementRevisions']=[4,5]
data['features']['entrance']=dict(plan_side='lower-left',approximate_point=[0,10150],opening_width_confirmed=False,
    source='user: balcony taken as south implies entrance northeast / lower-left in this image',
    orientation_status='conditional diagram convention; surveyed geographic orientation not verified')
features=data['features']['furnishing']
features.update(moveStepMm=100,hoverDimensions=True,officeChairCount=1,diningChairCount=4,
    televisionDiagonalInches=85,sofaChaiseEnd='plan-top',diningTableAgainstWall=True,
    currentReview=dict(localOfficeGapMm=408,sofaToCoffeeTableMm=500,chaiseToCoffeeTableMm=450,
                       leftDiningAisleMm=1432,positionsPreservedUnlessResized=True),
    continuousCabinet=dict(lengthMm=4500,depthMm=400,heightMm=2400,startPlanZ=5000,endPlanZ=9500,
                           nicheBottomMm=1200,nicheTopMm=1400,nicheClearHeightMm=200,nicheClearDepthMm=380,nicheClearLengthMm=960))
for s in features['selectedSchemes']:
    if s['zone']=='red':s['name']='电视低柜＋入户通长立柜'
    if s['zone']=='blue':s['name']='上端贵妃组合沙发＋长方茶几'
    if s['zone']=='green':s['name']='双工位桌体，暂放一椅'
    if s['zone']=='ink':s['name']='靠墙加大餐桌，四椅，无卡座'
data['provenance'].update(baseline='02_geometry/geometry-master-v05.json',baseline_sha256=hashlib.sha256(BASE.read_bytes()).hexdigest(),
                        layout='user six furniture amendments; widget positions from preceding turn',revision=6)
data['assumptions']=[s for s in data['assumptions'] if not s.startswith('家具采用用户所选')]
data['assumptions'] += ['v06家具尺寸为本次配套设计建议；85英寸指屏幕对角线，机壳1900×70×1100 mm为通用示意。',
  '入户端按用户明确的图片左下侧定位；通长柜先延伸至现有左下洞口上沿附近，柜长4500 mm为拟定尺寸，门宽与精确洞口仍待核。',
  '通长柜靠门端置物格按离地1200–1400 mm理解，净高200 mm。',
  '家具悬停显示长、宽、高；办公桌显示桌体高度750 mm，显示器总高另行注明；电视高度不包含离地安装高度。']
raw=(json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
OUT.write_bytes(raw)
(ROOT/'02_geometry/geometry-master.json').write_bytes(raw)
record=dict(revision=6,geometry_sha256=hashlib.sha256(raw).hexdigest(),objects=len(objects),parts=len(parts),
            furniture=[dict(id=o['id'],name=o['name'],dimensions=o['dimensionsMm']) for o in objects],
            sources=dict(tv='https://www.samsung.com.cn/tvs/qled-tv/qn85d-85-inch-neo-qled-4k-tizen-os-smart-tv-qa85qn82dajxxz/',
                         dining='https://www.ikea.cn/cn/zh/cat/yi-zhuo-si-yi-36212/'),
            design_status='schematic furniture update, not a product order or measured construction drawing')
(ROOT/'logs/furniture-v06-revision.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,ensure_ascii=True))
