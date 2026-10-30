"""User-directed layout changes. Geometry is a reversible scheme, in millimetres."""
from pathlib import Path
from copy import deepcopy
import hashlib, json, math, shutil, sys

ROOT=Path(r'D:\AI-Yang.cn\HomeDesign')
OLD=ROOT/'02_geometry/geometry-master-v06.json'
DEST=ROOT/'02_geometry/geometry-master-v07.json'
assert not DEST.exists() or '--replace-draft' in sys.argv, 'Existing v07 requires an explicit draft replacement.'
d=json.loads(OLD.read_text(encoding='utf-8'))
old=deepcopy(d)
style=json.loads((ROOT/'05_style/modern-japanese-v02.json').read_text(encoding='utf-8'))
sources=[]
for name,path in [
 ('v07-placement-annotation.png',r'C:\Users\ADMINI~1\AppData\Local\Temp\codex-clipboard-0a3a07aa-e4d3-45d4-9e69-d9d994e7d261.png'),
 ('v07-user-compass.png',r'C:\Users\ADMINI~1\AppData\Local\Temp\codex-clipboard-d9641bb2-63d3-4d62-b189-7d9b25ab8b08.png')]:
    target=ROOT/'00_sources'/name;target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(path,target)
    sources.append(dict(path=target.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(target.read_bytes()).hexdigest(),evidence='user placement/compass annotation; pixels are not measured dimensions'))

d['revision']=7;d['project_revision']=7
d['title']='房屋主模型 · 绿植角 / 入户L柜 / 阳台洗烘 / 34寸单屏'
d['compatiblePlacementRevisions']=[6]
d['previousPlacements']={g['id']:dict(x=g['x'],z=g['z']) for g in old['furnitureObjects']}
d['placementBaselinesByRevision']={'4':old['previousPlacements'],'5':old['previousPlacements'],'6':d['previousPlacements']}
d['compatiblePlacementRevisions']=[4,5,6]
d['provenance'].update(revision=7,baseline=OLD.relative_to(ROOT).as_posix(),baseline_sha256=hashlib.sha256(OLD.read_bytes()).hexdigest(),
    layout='user: entry L cabinets, balcony laundry/plants, northward living move, 34 inch single monitor, green corner extends to TV right',
    geographic_orientation='user diagram: up south, down north, left east, right west; not a surveyed bearing',sources=sources)
d['assumptions']=[s for s in d['assumptions'] if '无方位信息' not in s and '入口位置、' not in s]
d['assumptions'] += [
 '用户方位图：上南下北、左东右西；向北移动即向图片下方、平面z增加。不是实测地理方位。',
 '沙发、茶几及配套脚凳按设计建议同向下移500mm，避免茶几与原位脚凳重叠；其余既有家具位置继承。',
 '入户L形立柜深350mm、高2400mm；短边921mm，长边1533mm含350mm封闭盲角，不把盲角记为可直接存取空间。入口局部净宽921mm，门扇开向及精确洞口仍待核。',
 '阳台洗烘按下洗上烘叠放，单机通用包络600宽×650深×850高mm，中间30mm安装件占位。前面朝图左，后方50mm仅为方案预留，最终按具体型号安装图深化。',
 '34英寸按超宽单屏占位，机壳约810长×90深×370高mm，参考官方尺寸但未选购具体产品；桌体仍为2400×700×750mm。',
 '三盆落地绿植从阳台左侧延伸到电视右侧，尺寸为含叶冠包络的约值；小绿植、台灯、笔筒和杯子随桌体整体移动。',
 '脚凳移后到客卫前墙局部最小距离470mm，不视为主通道；主通行沿电视柜与脚凳左侧，宽2600mm。办公椅后408mm既有局部净距继续待体验。']

groups={g['id']:g for g in d['furnitureObjects']}
for gid in ['sofa-modular','side-table','ottoman']:
    groups[gid]['z']+=500
    groups[gid]['placement_source']='v07: north/image down +500 mm; ottoman follows to avoid overlap with coffee table'
    for p in d['furniture']:
        if p['parent']==gid:p['z']+=500

def part(gid,suffix,x,z,w,dep,y,h,mat,shape='box',**kw):
    p=dict(id=gid+'-'+suffix,parent=gid,kind='furniture',shape=shape,x=x,z=z,w=w,d=dep,y=y,h=h,material=mat,**kw)
    d['furniture'].append(p);return p

# Carry the accepted style into the interactive geometry as well as the Blender copy.
for p in d['furniture']:
    if p['id'] in style['designer_decisions']['table_corner_radii_mm']:
        p.update(shape='rounded_box',radiusMm=style['designer_decisions']['table_corner_radii_mm'][p['id']])
    if p['id'] in ['office-chair-1-seat','office-chair-1-back','dining-chair-1-seat','dining-chair-2-seat']:p['material']='sage'
    if p['id']=='tv-high-niche-tray':p['material']='navy'
book_ids=[p for p in d['furniture'] if p['id'].startswith('bookcase-book-')]
for i,p in enumerate(book_ids):
    if i in [3,13,23,33]:p['material']='navy'
for wall in d['walls']:
    if wall['id'] in style['designer_decisions']['wall_finish_profiles_mm']:
        # Convert world XY order to plan x,z order.
        r=style['designer_decisions']['wall_finish_profiles_mm'][wall['id']]
        wall['planCornerRadiiMm']=[r[3],r[2],r[1],r[0]]
for name,z,mat in [('green',2920,'sage'),('navy',4100,'navy')]:
    part('sofa-modular','pillow-'+name,4390,z,160,380,430,380,mat,'rounded_box',radiusMm=60,bevelMm=70)

# One monitor and one set of input devices; keep the two-person desk itself.
d['furniture']=[p for p in d['furniture'] if not(p['parent']=='double-desk' and any(t in p['id'] for t in ['monitor','keyboard','mouse']))]
part('double-desk','monitor-base-34',5360,2480,250,260,750,20,'metal','rounded_box',radiusMm=55)
part('double-desk','monitor-stand-34',5405,2580,45,60,770,210,'metal')
part('double-desk','monitor-body-34',5380,2195,87,810,900,370,'metal','rounded_box',radiusMm=8)
part('double-desk','monitor-screen-34',5467,2207,3,786,912,346,'screen')
part('double-desk','keyboard-single',5740,2380,145,440,750,16,'metal','rounded_box',radiusMm=12)
part('double-desk','mouse-single',5825,2890,75,55,750,25,'metal','ellipsoid')
part('double-desk','lamp-base',5390,3200,160,160,750,22,'navy','cylinder')
part('double-desk','lamp-stem',5458,3268,24,24,772,315,'metal','cylinder')
part('double-desk','lamp-shade',5385,3195,170,170,1087,90,'navy','frustum',bottomScale=1,topScale=.45)
part('double-desk','pen-cup',5510,3440,85,85,750,110,'ceramic','cylinder')
for i,(xx,zz) in enumerate([(5535,3465),(5565,3480),(5548,3498)]):
    part('double-desk','pen-'+str(i),xx,zz,8,8,840,70+i*8,'wood','cylinder')
part('double-desk','water-cup',5750,3320,90,90,750,110,'ceramic','cylinder')
part('double-desk','plant-pot',5410,3860,190,190,750,160,'ceramic','frustum',bottomScale=.75)
part('double-desk','plant-soil',5420,3870,170,170,905,8,'soil','cylinder')
for i,(xx,zz,yy,ww,dd,hh) in enumerate([(5390,3880,910,120,190,230),(5490,3835,910,130,130,170),(5470,3965,910,120,100,210),(5400,3950,910,90,150,160)]):
    part('double-desk','plant-leaf-'+str(i),xx,zz,ww,dd,yy,hh,'foliage','leaf',leafFlip=(-1)**i)
groups['double-desk'].update(detail='2400×700×750mm圆角双人桌，暂放一椅；仅一台34英寸超宽屏、单套键鼠，配台灯、笔筒、水杯和小绿植。',monitorCount=1,monitorDiagonalInches=34,visualHeight=1270)

def group(gid,name,x,z,w,dep,h,detail,**kw):
    g=dict(id=gid,name=name,zone='v07',scheme='user-amendment',x=x,z=z,w=w,d=dep,h=h,label=True,labelRotate=0,
        dimensionsMm=dict(length=max(w,dep),width=min(w,dep),height=h),detail=detail,
        placement_source='user annotation/text; dimensions are designer proposals')
    g.update(kw)
    d['furnitureObjects'].append(g);groups[gid]=g;return g

# The corner belongs to the long side. Its last 350 mm is a closed blind return.
group('entry-shoe-cabinet','入户鞋柜',921,9635,350,1533,2400,'长1533×深350×高2400mm；靠墙立柜，末端350mm封闭盲角；有效门面长1183mm。',facing='negative-x',labelRotate=-90)
part('entry-shoe-cabinet','body',941,9635,330,1533,80,2300,'cabinet')
part('entry-shoe-cabinet','top',921,9635,350,1533,2380,20,'wood')
part('entry-shoe-cabinet','plinth',951,9655,300,1493,0,80,'wood')
for i in range(3):
    zz=9635+i*1183/3
    part('entry-shoe-cabinet','door-'+str(i),921,zz+2,20,1183/3-4,80,2300,'cabinet')
    part('entry-shoe-cabinet','pull-'+str(i),916+5,zz+1183/3-20,3,3,1050,180,'wood')
part('entry-shoe-cabinet','blind-return',921,10818,20,350,80,2300,'wood')
group('entry-return-cabinet','入户转角储物柜',0,10818,921,350,2400,'长921×深350×高2400mm；朝入户过道开门，与右侧鞋柜连为L形。',facing='negative-z')
part('entry-return-cabinet','body',0,10838,921,330,80,2300,'cabinet')
part('entry-return-cabinet','top',0,10818,921,350,2380,20,'wood')
part('entry-return-cabinet','plinth',20,10848,881,300,0,80,'wood')
for i in range(2):
    xx=i*921/2
    part('entry-return-cabinet','door-'+str(i),xx+2,10818,921/2-4,20,80,2300,'cabinet')

# Three grouped potted plants. Sizes include foliage, not just the pot.
for gid,name,x,z,size,height,pot in [
 ('plant-balcony-tall','阳台高绿植',150,120,700,1500,330),
 ('plant-tv-medium','电视右侧绿植',100,1030,550,1000,280),
 ('plant-balcony-low','阳台矮绿植',1100,200,500,650,220)]:
    group(gid,name,x,z,size,size,height,'含盆器及叶冠的方案包络，非具体品种实测；与阳台和电视右侧空位组合。',label=False)
    cx=x+size/2;cz=z+size/2
    part(gid,'pot',cx-pot/2,cz-pot/2,pot,pot,0,pot,'ceramic','frustum',bottomScale=.76)
    part(gid,'soil',cx-pot*.45,cz-pot*.45,pot*.9,pot*.9,pot-8,8,'soil','cylinder')
    part(gid,'stem',cx-12,cz-12,24,24,pot,height-pot-100,'wood','cylinder')
    # Pairs of flat elliptical leaves at staggered levels; leave the centre open.
    for i in range(14):
        angle=i*2.39996;level=pot+(height-pot)*(.12+.70*(i/13))
        ww=size*(.22+.03*(i%3));dd=size*(.24+.03*((i+1)%3));hh=(height-pot)*.23
        r=size*.25;lx=cx+math.cos(angle)*r-ww/2;lz=cz+math.sin(angle)*r-dd/2
        part(gid,'leaf-'+str(i),lx,lz,ww,dd,level,hh,'foliage' if i%3 else 'foliage-light','leaf',leafFlip=(-1)**i)
        start=[cx,level-40,cz];end=[lx+ww/2,level,lz+dd/2]
        bx=min(start[0],end[0])-3;bz=min(start[2],end[2])-3;by=level-43
        part(gid,'branch-'+str(i),bx,bz,abs(start[0]-end[0])+6,abs(start[2]-end[2])+6,by,46,'wood','branch',
            startLocal=[start[0]-bx,start[1]-by,start[2]-bz],endLocal=[end[0]-bx,end[1]-by,end[2]-bz],radiusMm=3)
    part(gid,'top-leaf',cx-size*.12,cz-size*.12,size*.24,size*.24,height-(height-pot)*.22,(height-pot)*.22,'foliage','leaf',leafFlip=1)

# Lower washer, upper dryer, opening toward negative plan x (left).
for gid,name,base in [('washer','阳台洗衣机',0),('dryer','阳台烘干机',880)]:
    group(gid,name,6488,170,650,600,850,'600宽×650深×850高mm占位；正面朝图左，后部预留50mm。下洗上烘，具体型号及安装条件待核。',
        facing='negative-x',baseHeightMm=base,visualHeight=base+850,movementGroup='laundry-stack',label=False,
        dimensionsMm=dict(length=600,width=650,height=850))
    part(gid,'body',6528,170,610,600,base+15,835,'appliance','rounded_box',radiusMm=5,bevelMm=5)
    part(gid,'feet',6550,190,550,560,base,15,'metal')
    part(gid,'door-ring',6493,230,35,480,base+175,480,'metal','cylinder',axis='x')
    part(gid,'door-glass',6489,268,6,404,base+213,404,'screen','cylinder',axis='x')
    part(gid,'door-inner',6488,295,1,350,base+240,350,'drum','cylinder',axis='x')
    part(gid,'control-strip',6525,185,3,570,base+717,90,'cabinet')
    part(gid,'display',6523,230,2,150,base+742,42,'screen')
    part(gid,'dial',6513,600,12,54,base+735,54,'metal','cylinder',axis='x')
part('washer','stacking-kit',6528,170,610,600,850,30,'cabinet')
groups['dryer']['label']=True;groups['dryer']['labelRotate']=-90

for key,col,rough in [('sage',[.17,.245,.16,1],.9),('navy',[.018,.045,.083,1],.7),('foliage',[.075,.19,.05,1],.48),('foliage-light',[.15,.29,.08,1],.53),('soil',[.075,.047,.025,1],1),('ceramic',[.68,.64,.55,1],.7),('appliance',[.76,.75,.70,1],.35),('drum',[.09,.12,.13,1],.35)]:
    d['furnitureMaterials'][key]=dict(name=key,color=col,roughness=rough)
for g in d['furnitureObjects']:
    pp=[p for p in d['furniture'] if p['parent']==g['id']]
    lo=[min(p[k] for p in pp) for k in ['x','z','y']]
    hi=[max(p[k]+p[s] for p in pp) for k,s in [('x','w'),('z','d'),('y','h')]]
    g['meshBoundsMm']=dict(x=lo[0],z=lo[1],y=lo[2],w=hi[0]-lo[0],d=hi[1]-lo[1],h=hi[2]-lo[2])
    g['visualHeight']=hi[2]
    g.setdefault('baseHeightMm',lo[2])

f=d['features']['furnishing']
f.update(movableObjectIds=[g['id'] for g in d['furnitureObjects']],monitorCount=1,monitorDiagonalInches=34,
    livingNorthShiftMm=500,greenCorner='balcony left + TV right toward balcony',entryCabinetDepthMm=350,
    laundry=dict(configuration='washer below dryer',front='negative-plan-x',singleEnvelopeMm=[600,650,850],stackKitMm=30))
f['currentReview'].update(sofaToDeskMm=500,ottomanToBathFrontMm=470,mainAisleBesideOttomanMm=2600)
f.pop('initialClearances',None)
f['selectedSchemes']=[dict(zone=z,option=o,name=n) for z,o,n in [('red','A','电视低柜与入户通长立柜'),('blue','B','贵妃组合沙发与加大茶几'),('green','B','双人桌单屏一椅'),('yellow','A','高柜与开放书架'),('ink','B','四人餐桌靠墙，无卡座')]]
d['features']['entrance']['orientation_status']='user diagram confirmed up south/down north/left east/right west; exact door opening and swing unverified'
d['features']['compass']=dict(top='南',bottom='北',left='东',right='西',source=sources[1]['path'])
d['style']=dict(revision='modern-japanese-v03',tableCornerRadiiMm=style['designer_decisions']['table_corner_radii_mm'],wallFinishProfilesMm=style['designer_decisions']['wall_finish_profiles_mm'])
DEST.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
style.update(version='v07-style-v03',geometry_base='02_geometry/geometry-master-v07.json',geometry_sha256=hashlib.sha256(DEST.read_bytes()).hexdigest())
style['locked']=['既有墙窗和房间关系','沙发/茶几/脚凳北移500mm，其余既有坐标继承','85寸电视','双人桌一把椅子、一台34寸屏','餐桌四椅、长边靠墙','植物角、入户L形立柜、右上洗烘位置按用户标注']
style['designer_decisions']['v07_additions']='暖白浅木L形立柜；三盆高低错落的绿植连成电视右侧与阳台角；暖白洗烘叠放；桌面常用品控制数量。'
(ROOT/'05_style/modern-japanese-v03.json').write_text(json.dumps(style,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'03_layout/widget-layout-v07-initial.json').write_text(json.dumps(dict(revision=7,units='mm',furniturePositions=[dict(id=g['id'],x=g['x'],z=g['z'],dx=0,dz=0) for g in d['furnitureObjects']]),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
ledger=dict(revision=7,source_annotations=sources,user_direction='north=image down; user compass',
    designer_dimensions_provisional=True,measured_cad=False,desk_monitor_reference='https://www.delltechnologies.com/asset/en-us/products/electronics-and-accessories/technical-support/dell-34-curved-gaming-monitor-s3422dwg-product-data-sheet.pdf',
    laundry_references=['https://www.bosch-home.co.uk/supportdetail/product/WGG24409GB/01','https://www.bosch-home.co.uk/supportdetail/product/WQG24509GB/09'],
    product_selection='generic envelopes referenced to official typical dimensions, no particular model selected or installation certified',
    geometry_sha256=style['geometry_sha256'],furniture=len(d['furnitureObjects']),parts=len(d['furniture']))
(ROOT/'logs/v07-source-ledger.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('V07_GEOMETRY_CREATED',len(d['furnitureObjects']),len(d['furniture']),style['geometry_sha256'])
