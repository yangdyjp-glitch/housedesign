"""Implement the authorised v20 detail package as a sibling of the integrated master.
All dimensions are design proposals in mm, not field or engineering certification.
Run with the bundled Blender, in background; no edits to historical masters.
"""
from pathlib import Path
import bpy, bmesh, json, math, hashlib, copy, ast
from mathutils import Vector, Matrix

R = Path('D:/AI-Yang.cn/HomeDesign')
OUT = R/'09_delivery/v20-complete'
OUT.mkdir(exist_ok=True)
G = R/'02_geometry/geometry-master-v20-complete.json'
S = R/'05_style/modern-japanese-v20-complete.json'
MODEL = R/'06_blender/home-main-v20-complete.blend'
BASE = R/'06_blender/home-main-v20.blend'
def load(p): return json.loads((R/p).read_text(encoding='utf-8-sig'))
def write(p, v): Path(p).write_text(json.dumps(v, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
base = load('02_geometry/geometry-master-v20.json')
d = copy.deepcopy(base)
baseline = {p:sha(R/p) for p in ['06_blender/home-main-v20.blend','02_geometry/geometry-master-v20.json','05_style/modern-japanese-v20.json','06_blender/active-model.json','06_blender/active-presentation.json']}
write(OUT/'实施前版本.json',dict(hashes=baseline,active=load('06_blender/active-model.json'),presentation=load('06_blender/active-presentation.json'),liveLayout='Live Blender was a clean v19 with identical retained furniture positions; saved integrated v20 is the merge base.'))

def box(ident, x,z,w,dep,y,h,material='cabinet',parent=None,**kw):
    p=dict(id=ident,x=x,z=z,w=w,d=dep,y=y,h=h,material=material,shape='box',kind='furniture' if parent else 'finish',collidable=False)
    p.update(kw)
    if parent: p['parent']=parent
    return p
def prof(ident, points,y,h,material='wall-finish',parent=None,**kw):
    xs=[p[0] for p in points];zs=[p[1] for p in points];x=min(xs);z=min(zs)
    return box(ident,x,z,max(xs)-x,max(zs)-z,y,h,material,parent,planProfileLocalMm=[[a-x,b-z] for a,b in points],**kw)
def add(p, array='furniture'): d[array].append(p); return p
def frame_x(gid, stem, x,z,dep,length,y,h, shelf_heights=(),divisions=1, back=6, material='cabinet'):
    # Cabinet fronts face decreasing x; carcass really is hollow.
    add(box(stem+'-back',x+dep-back,z,back,length,y,h,material,gid))
    for j in range(divisions+1):
        zz=z+(length-18)*j/divisions
        add(box(stem+f'-side-{j}',x,zz,dep-back,18,y,h,material,gid,interior=True))
    for k,yy in enumerate([y,y+h-18]+list(shelf_heights)):
        add(box(stem+f'-shelf-{k}',x+8,z+18,dep-back-16,length-36,yy,18,material,gid,interior=True,adjustable=k>1))

# Replace filled proxy bodies with actual cabinet construction, retaining door rhythm.
oldlen=len(d['furniture'])
d['furniture']=[p for p in d['furniture'] if p['id'] not in ['tv-high-main-carcass','tv-high-main-upper-carcass','v18-shoe-lower-body','v18-shoe-upper-body']]
for p in d['furniture']:
    if p.get('parent')=='tv-high' and '-door-' in p['id']:
        p['cabinetDoor']=True; p['bevelMm']=2
        if p['id'].endswith('-0'): p['z']=5082;p['d']=497.3333333333
    if p.get('parent')=='entry-shoe-cabinet' and '-door-' in p['id']:
        p['cabinetDoor']=True;p['bevelMm']=2
        if p['id'].endswith('-1'):p['w']=581.5
frame_x('tv-high','v20f-hall',18,5080,360,3420,60,2670,divisions=6)
for j in range(6):
    z=5080+j*(3420-18)/6+20
    # Last module is tall cleaning storage, with removable upper shelves.
    levels=[360,700,1030,1510,1870,2230,2580] if j<5 else [2350,2580]
    for k,yy in enumerate(levels):
        add(box(f'v20f-hall-module-{j}-adjustable-{k}',30,z,332,528,yy,18,'wood','tv-high',interior=True,adjustable=True))
    for yy in [250,1050,1450,2480]:
        add(box(f'v20f-hall-hinge-{j}-{yy}',340,z+5,35,16,yy,45,'metal','tv-high',interior=True))
# Fixed rounded end stays within the original 400 x 3500 plan footprint.
end=box('v20f-hall-curved-fixed-end',0,5000,400,80,60,2690,'cabinet','tv-high',shapeNote='R50 exposed end, fixed panel, not storage',radiusMm=0,planCornerRadiiMm=[0,50,0,0])
end['shape']='rounded_box';add(end)
for k,yy in enumerate([2160,2440]):
    add(box(f'v20f-hall-lowering-tray-{k}',70,5150,260,420,yy,18,'wood','tv-high',interior=True,loweringStorage=True))
for zz in [5135,5580]:add(box(f'v20f-hall-lowering-arm-{zz}',90,zz,18,12,1900,600,'metal','tv-high',interior=True))

# Shoe cabinet: two real bays, adjustable shelves and a fixed R40 outer return.
gid='entry-shoe-cabinet'
for yy,hh in [(160,1040),(1418,1332)]:
    add(box(f'v20f-shoe-back-{yy}',0,11162,1221,6,yy,hh,'cabinet',gid,interior=True))
    for xx in [0,626.5,1203]:add(box(f'v20f-shoe-side-{yy}-{xx}',xx,10838,18,324,yy,hh,'cabinet',gid,interior=True))
    levels=[yy,yy+hh-18]+([340,530,720,910,1100] if yy==160 else [1750,2110,2470])
    for k,y in enumerate(levels):
        for j,(x,w) in enumerate([(18,608.5),(644.5,558.5)]):
            add(box(f'v20f-shoe-shelf-{yy}-{k}-{j}',x,10848,w,304,y,18,'wood',gid,interior=True,adjustable=k>1))
    p=box(f'v20f-shoe-R40-end-{yy}',1221,10818,50,350,yy,hh,'cabinet',gid,planCornerRadiiMm=[0,40,0,0]);p['shape']='rounded_box';add(p)

# Bookcase: preserve open-bay geometry / sliding north module; replace only filled bodies.
filled={'v19-book-balcony-body','v19-book-base-body','v19-book-upper-body'}
d['furniture']=[p for p in d['furniture'] if not(p.get('parent')=='bookcase' and p.get('sourceObject') in filled)]
frame_x('bookcase','v20f-book-south',6858,1176,330,800,0,2750,[380,780,1180,1580,1980,2380],divisions=2)
frame_x('bookcase','v20f-book-base',6858,1976,330,2000,0,780,[380],divisions=4)
frame_x('bookcase','v20f-book-upper',6858,1976,330,2000,2150,600,[],divisions=4)
for p in d['furniture']:
    if p.get('parent')=='bookcase' and ('door' in p.get('sourceObject','').lower() or 'sliding leaf' in p.get('sourceObject','').lower()):p['cabinetDoor']=True;p['bevelMm']=2

# Dining stays as the accepted U11 silhouette. Hollow three drawer boxes / thin shelf band.
for p in d['furniture']:
    if p.get('parent')=='dining-sideboard-island' and any(k in p.get('sourceObject','') for k in ['-door-','flap-','drawer-front']):p['cabinetDoor']=True;p['bevelMm']=2
replace=[p for p in d['furniture'] if p.get('parent')=='dining-sideboard-island' and p.get('sourceObject','').startswith(('horizontal-drawer-box','continuous-slim-band-body'))]
d['furniture']=[p for p in d['furniture'] if p not in replace]
for p in replace:
    if p['sourceObject'].startswith('horizontal'):
        x,z,w,dep,y,h=[p[k] for k in ['x','z','w','d','y','h']]
        for suffix,args in [('base',(x,z,w,dep,y,12)),('back',(x+w-12,z,12,dep,y,h)),('side-a',(x,z,w,12,y,h)),('side-b',(x,z+dep-12,w,12,y,h))]:
            add(box(p['id']+'-'+suffix,*args,'walnut','dining-sideboard-island',interior=True))
    else:frame_x('dining-sideboard-island','v20f-dining-thin-band',2301,7362.5,201,2100,1480,250,[],divisions=4,material='walnut')

# Low, bound woven rug; every retained piece stays at its current origin.
add(box('v20f-rug-face',1950,1600,3000,3600,0,8,'rug','living-rug',radiusMm=70,bevelMm=1))
d['furniture'][-1]['shape']='rounded_box'
def group(gid,name,x,z,w,dep,h,dims,detail,zone):
    return dict(id=gid,name=name,x=x,z=z,w=w,d=dep,h=h,visualHeight=h,label=False,zone=zone,scheme='v20-full-detail',dimensionsMm=dict(zip(['length','width','height'],dims)),detail=detail)
d['furnitureObjects'].append(group('living-rug','客厅低绒织纹地毯',1950,1600,3000,3600,8,[3600,3000,8],'低绒暖灰米色，薄包边、R70；覆盖茶几与沙发前脚，延至脚凳下。尺寸为设计建议。','living'))

# Open-front laundry surround: keep washer/dryer position; stop curtain before its side.
gid='laundry-enclosure'
for zz in [145,795]:
    add(box(f'v20f-laundry-side-{zz}',6468,zz,720,18,0,2750,'cabinet',gid,bevelMm=3))
for yy in [1775,2732]:add(box(f'v20f-laundry-horizontal-{yy}',6468,163,720,632,yy,18,'cabinet',gid,interior=True))
# Effective storage depth 350; 352 mm rear service void is excluded from capacity.
add(box('v20f-laundry-upper-back',6812,163,6,632,1793,939,'cabinet',gid,interior=True))
for k,yy in enumerate([2200,2470]):add(box(f'v20f-laundry-lowering-tray-{k}',6500,193,280,572,yy,18,'wood',gid,interior=True))
for zz in [175,777]:add(box(f'v20f-laundry-lowering-arm-{zz}',6500,zz,260,12,1900,650,'metal',gid,interior=True))
for j in range(2):add(box(f'v20f-laundry-upper-door-{j}',6468,167+j*312,18,306,1797,899,'cabinet',gid,cabinetDoor=True,bevelMm=2))
add(box('v20f-laundry-top-scribe',6468,145,18,668,2700,50,'cabinet',gid))
# High rear transfer grille; no front door encloses the machines during operation.
for j in range(5):add(box(f'v20f-laundry-rear-grille-{j}',7166,185,20,590,1840+j*48,18,'cabinet',gid,ventilation=True))
d['furnitureObjects'].append(group(gid,'阳台开放式洗烘高柜',6468,145,720,668,2750,[668,720,2750],'下部敞开洗烘位，上柜净深约314、双层下拉；后部为空调/管线无关的设备检修通风保留空腔，不计收纳。整柜与两机联动100 mm。','balcony'))
for q in d['furnitureObjects']:
    if q['id'] in ['washer','dryer',gid]:q['movementGroup']='laundry-stack'
c=d['features']['referenceRefinement']['curtain'];oldEnd=c['reservedSweepMm']['x']+c['reservedSweepMm']['w'];newEnd=6428
c['reservedSweepMm']['w']=newEnd-c['reservedSweepMm']['x'];c['rightEndMm']=newEnd;c['rightEndStopReason']='reserve 40mm from new laundry frame x6468; original 10mm plan-depth relationship no longer overlaps in x'
n=len(d['curtainParts']);start=c['reservedSweepMm']['x'];span=newEnd-start
for i,p in enumerate(d['curtainParts']):
    p['closedCentreX']=start+span*(i+.5)/n;p['x']=p['closedCentreX']-p['w']/2
for p in d['referenceParts']:
    if p['id'] in ['v12-curtain-pelmet','v12-curtain-track','v12-curved-cove','v12-cove-light-lip']:p['w']=span

# Align the master-bath corridor face to z4896, and use a diagonal inward bifold.
wmap={p['id']:p for p in d['walls']}
wmap['v14-master-foyer-front'].update(z=4776,d=120)
wmap['v14-master-foyer-return'].update(d=120)
wmap['v14-bath-left-bottom'].update(z=4896,d=7030-4896)
H=(9203.,4096.);E=(8523.,4776.);u=Vector((-2**-.5,2**-.5));normal=Vector((2**-.5,2**-.5));diag=(Vector(E)-Vector(H)).length
def at(t):return Vector(H)+t*u
def strip(a,b,width):
    a=Vector(a);b=Vector(b);v=(b-a).normalized();n=Vector((v.y,-v.x));return [list(a),list(b),list(b+n*width),list(a+n*width)]
def wall_profile(row,points):
    xs=[p[0] for p in points];zs=[p[1] for p in points];row.update(x=min(xs),z=min(zs),w=max(xs)-min(xs),d=max(zs)-min(zs),planProfileLocalMm=[[a-min(xs),b-min(zs)] for a,b in points],shape='profile',finishGeometry=True)
wall_profile(wmap['v14-bath-left-top-jamb'],strip(at(0),at(50),120))
wall_profile(wmap['v14-bath-left-door-header'],strip(at(50),at(910),120))
row=dict(id='v20f-bath-diagonal-bottom-jamb',y=0,h=2750,kind='internal',confidence='design-proposal-unverified')
wall_profile(row,strip(at(910),at(diag),120));d['walls'].append(row)
d['openings']=[p for p in d['openings'] if p['wall']!='v14-bath-left']
d['openings'].append(dict(wall='v20f-bath-diagonal',axis='diagonal',startPlanMm=list(at(50)),endPlanMm=list(at(910)),sill=0,top=2100,type='door',rawWidthMm=860,confidence='design-proposal-unverified'))
d['bathParts']=[p for p in d['bathParts'] if not p['id'].startswith('v14-bath-door-') and p['id']!='v14-bedroom-foyer-floor']
add(prof('v20f-foyer-floor',[[7328,3976],[8645,3976],[8645,4096],[9203,4096],[8523,4776],[7328,4776]],2,2,'wood'), 'bathParts')
add(prof('v20f-bath-extension-floor',[[9203,4096],[9323,4096],[9323,4896],[8523,4896],[8523,4776]],2.5,3,'bath-tile'),'bathParts')
hinge=at(70);L=410.
def bifold_points(panel,t):
    theta=t*math.pi/2;A=hinge+L*(math.cos(theta)*u+math.sin(theta)*normal);B=hinge+2*L*math.cos(theta)*u
    aa,bb=(hinge,A) if panel==0 else (A,B)
    if panel==1:
        shift=42*math.sin(theta)*(math.cos(theta)*normal+math.sin(theta)*u)
        aa=aa+shift;bb=bb+shift
    v=(bb-aa).normalized();nn=Vector((v.y,-v.x));aa=aa+v*2;bb=bb-v*2
    # Rounded R20 vertical stiles clear the adjoining leaf through the folding sweep.
    points=[]
    for cc,start in [(aa+v*20,math.pi/2),(bb-v*20,-math.pi/2)]:
        for j in range(13):
            angle=start+j*math.pi/12;points.append(list(cc+v*(20*math.cos(angle))+nn*(20*math.sin(angle))))
    return points
for i in range(2):
    p=prof(f'v20f-bath-bifold-leaf-{i}',bifold_points(i,0),6,2088,'wall-finish',collidable=True,swingLeaf=True,bifoldPanel=i,bevelMm=2)
    op=prof('open',bifold_points(i,1),6,2088)
    p['openPlan']={k:op[k] for k in ['x','z','w','d','planProfileLocalMm']};add(p,'bathParts')
for side,t in [('hinge',50),('latch',910)]:
    add(prof('v20f-bath-frame-'+side,strip(at(t),at(t+12),110),0,2100,'metal'),'bathParts')
add(prof('v20f-bath-top-track',strip(at(50),at(910),60),2100,35,'metal'),'bathParts')
ms=d['features']['masterSuite'];ms['door']=dict(type='diagonal inward bifold, opaque warm-white',status='designer implementation proposal; owner preference may override',rawOpeningMm=860,leafMm=820,leafCount=2,individualPanelMm=406,thicknessMm=40,stileRadiusMm=20,conceptClearOpeningMm=735,hingePlanMm=list(hinge),basisU=list(u),basisN=list(normal),halfSpanMm=L,openingStartMm=list(at(50)),openingEndMm=list(at(910)),swing='folds inward; balcony/bed furniture unchanged',defaultOpen=False,frameProductSelected=False)
ms['foyer'].update(stepIntoHallMm=0,newFrontOuterZ=4896,previousFrontOuterZ=5096,referenceBandToGuestFrontMm=1249)
ms['bathExtensionPocketMm']=[list(H),list(E),[9323,4776],[9323,4096]]
ms['doorApproachTrial']=dict(centerMm=[8480,4400],radiusMm=250,meaning='single-person circular proxy, not accessibility certification')
d['features']['pendingWallAlignmentV17']=dict(status='implemented as v20 designer proposal',referencePlaneZMm=4896,mainBathFrontPlaneZMm=4896,changeMm=-200,door='diagonal inward bifold',bedMoved=False)
d['features']['publicRefinement']['publicFloorPolygon']=[[0,0],[7188,0],[7188,4896],[9203,4896],[9203,6145],[4759,6145],[4759,6090],[3082,6090],[3082,9635],[0,9635]]

# Public flush-door construction, replacing the old black rectangular proxy backings.
doors=[('master-public',7370,4896,866,2180,False),('guest-bath-public',3812,5970,947,2100,True),('guest-room-public',4943,6145,868,2100,True)]
d['detailParts']=[p for p in d['detailParts'] if not(p['id'].startswith('v10-') and ('reveal' in p['id'] or 'skirting' in p['id']))]
for name,x,z,w,h,plus in doors:
    z0=z if plus else z-40
    frameZ=z+12.5 if plus else z-92.5
    for tag,xx,ww,yy,hh in [('a',x,4,0,h),('b',x+w-4,4,0,h),('head',x, w,h-4,4)]:
        add(box('v20f-'+name+'-reveal-'+tag,xx,z-.25,ww,.5,yy,hh,'shadow'), 'detailParts')
    # Concealed 12 x 30 frame, 18 mm backing and 3 mm finishing edge.
    for side,xx in [('a',x-12),('b',x+w)]:
        add(box('v20f-'+name+'-hidden-frame-'+side,xx,frameZ,12,80,0,h,'metal'), 'detailParts')
        add(box('v20f-'+name+'-backing-'+side,xx-18 if side=='a' else xx+12,frameZ+8,18,65,0,h,'wood'), 'detailParts')
    add(box('v20f-'+name+'-hidden-head',x-12,frameZ, w+24,80,h,12,'metal'),'detailParts')
    add(box('v20f-'+name+'-floor-joint',x,z-1.5,w,3,0,1,'shadow'),'detailParts')
for p in d['detailParts']:
    if '-public-leaf' in p['id']:p['bevelMm']=2

# Recessed skirting is built into the proposed finish, within the wall envelope.
skirting_walls={'lower-narrow-top-0':'zmin','lower-centre-top-0':'zmin','lower-centre-top-end':'zmin','v14-master-foyer-front':'zmax'}
for ident,face in list(skirting_walls.items()):
    if ident not in wmap:del skirting_walls[ident];continue
    p=wmap[ident];p['finishBaseRecessMm']=dict(face=face,height=58,joint=4,recess=8,finishLayer=12.5)
    add(box('v20f-skirting-'+ident,p['x'],p['z']+(p['d']-10 if face=='zmax' else 8),p['w'],2,0,58,'skirting'),'detailParts')
    add(box('v20f-base-joint-'+ident,p['x'],p['z']+(p['d']-12 if face=='zmax' else 10),p['w'],2,58,4,'shadow'),'detailParts')
wmap['retained-central-right-end']['planCornerRadiiMm']=[0,0,0,60]

# Full-home finish plane + explicit public service band / quiet narrow AC faces.
d['ceilingParts']=[]
band=[3500,4900,4500,1000]
add(box('v20f-service-band',*band,2600,150,'wall-finish',ceilingElement=True),'ceilingParts')
add(box('v20f-living-supply-recess',3700,4899,2000,2,2630,60,'shadow',ceilingElement=True),'ceilingParts')
for j in range(3):add(box(f'v20f-living-supply-blade-{j}',3708,4895,1984,8,2635+j*18,6,'cabinet',ceilingElement=True),'ceilingParts')
add(box('v20f-public-return-recess',5800,5780,1700,100,2598,3,'shadow',ceilingElement=True),'ceilingParts')
for j in range(6):add(box(f'v20f-public-return-blade-{j}',5808,5783+j*16,1684,8,2595,6,'cabinet',ceilingElement=True),'ceilingParts')
# Hatch seams are actual small recess lines, with a detachable larger face for removal.
for tag,x,z,w,dep in [('a',6050,5170,1300,3),('b',6050,5817,1300,3),('c',6050,5170,3,650),('d',7347,5170,3,650)]:
    add(box('v20f-public-access-'+tag,x,z,w,dep,2599,1,'shadow',ceilingElement=True),'ceilingParts')
private_ac=[('master',7600,1300,1200,400),('guest',5000,6410,1200,350),('secondary',7800,7170,1400,350)]
for name,x,z,w,dep in private_ac:
    for ident,zz,dd in [('supply',z,40),('return',z+dep-80,80)]:
        add(box(f'v20f-{name}-{ident}-face',x,zz,w,dd,2748,2,'cabinet',ceilingElement=True),'ceilingParts')
    for xx in [x+w+50,x+w+648]:add(box(f'v20f-{name}-access-{xx}',xx,z,2,600,2749,1,'shadow',ceilingElement=True),'ceilingParts')
for i,(x,z) in enumerate([(1250,2500),(5900,2500),(1300,5600),(5400,5600),(1400,7500),(1400,9000),(650,10150)]):
    y=2594 if 3500<x<8000 and 4900<z<5900 else 2744
    p=box(f'v20f-recessed-light-trim-{i}',x-29,z-29,58,58,y,5,'cabinet',ceilingElement=True);p['shape']='cylinder';add(p,'ceilingParts')

storage=[dict(id='tv-high',description='六模块，五组可调层板＋一高位清洁模块；首模块高处双层下拉',usableDepthMm=332,adjustable=True),dict(id='entry-shoe-cabinet',description='双仓五层可调鞋位／上方三层可调；右端R40固定封板不计收纳',clearWidthsMm=[608.5,558.5],usableDepthMm=304,adjustable=True),dict(id='bookcase',description='保留开放六格及北端平移门；封闭块改真实空腔、可调层板',usableDepthMm=306,adjustable=True),dict(id='dining-sideboard-island',description='保留四段式／完整上柜双层下拉；三横抽补齐抽盒底板与侧板',drawerInternalMm=[526,534,148],upperEffectiveDepthMm=313,backServiceVoidIsStorage=False),dict(id='laundry-enclosure',description='敞开设备位；上柜双层下拉，后部服务空腔不计收纳',upperUsefulDepthMm=314,adjustable=True)]
details=dict(authorization='实装v20',label='v20 实装完整版',phase='full-design-implementation',finishedCeilingMm=2750,serviceBandFinishMm=2600,structureHeightMm=None,beamBottomMm=None,acUnitModel=None,acStatus='coordinated design locations / proxy service envelopes; engineer and manufacturer verification pending',acPublic=dict(bandPlanMm=band,supplyFaceMm=[3700,4895,2000,8,2630,60],returnFaceMm=[5800,5780,1700,100,2600],accessPanelMm=[6050,5170,1300,650],unitEnvelopeMm=[6100,5250,1200,550,2780,230],renderedEquipment=False),privateAC=private_ac,storage=storage,doorWall=dict(flushDoorCount=3,leafThicknessMm=40,perimeterJointMm=4,hiddenFrameMm=[12,30],backingMm=18,skirtingMm=dict(height=58,joint=4,recess=8),constructionSystemUnselected=True),curve=dict(skeleton='straight',hallFixedEndR50=True,shoeEndR40=True,wallExposedR60=True,touchEdgesR2=True,existingDiningR100=True,officeCap='B R45 provisional'),laundry=dict(framePlanMm=[6468,145,720,668],openMachineFront=True,machinesMoved=False,curtainRightEndMm=6428,curtainToFrameGapMm=40,frontServiceAreaMm=[5488,170,980,600],specificMachineVentilationUnknown=True),rug=dict(sizeMm=[3600,3000,8],positionMm=[1950,1600],lowPile=True),masterBath=ms,positions='26 retained origins unchanged; two added assemblies only',officeMaterial='B temporary preview; owner final choice pending',seating='dining chairs remain deferred',lighting=dict(circuits=['curtain','bookcase','entry','office','office-ledge','dining','dining-niche','general'],modes=['day','evening','dining','cleaning','viewing'],ambientCctTargetK=3000,taskCctTargetK=3500,cctAreDesignTargets=True,photometricCalculation=False),constructionStatus='design package, not certified construction drawings')
d['features']['fullImplementationV20']=details
d['features']['deepeningV19']['laundryUnchangedPendingEquipmentCoordination']=False
d['features']['deepeningV19']['laundryCurtainGapMm']=40
d['features']['completedIntegrationV20']['scope']='retained dining11 and office02; remaining detail package implemented as sibling v20-complete'
d.update(title='v20 实装完整版',project_revision='v20-full-20261106',style='modern-japanese-v20-complete',implementationPhase='full-design',presentation_snapshot_only=False)
d['furnitureMaterials']['rug']=dict(color=[.56,.53,.46,1],roughness=.95)
d['furnitureMaterials']['walnut']=dict(color=[.085,.040,.020,1],roughness=.55)
d['furnitureMaterials']['skirting']=dict(color=[.78,.78,.72,1],roughness=.75)
d['assumptions'] += ['v20已获明确启动；2750顶面、2600设备带及风口均为设计暂拟，不代表梁高或机型已确定。','主卫走廊面已按z4896齐平，斜向内折双扇门为可逆设计提案；保持床及洁具位置，具体门系统、密封和净开口待核。','洗烘敞开位保持两机原位；帘右止点收至6428，40间隔是模型值，不代表厂家安装要求。','收纳内格为可调设计，不假定业主物品数量；固定弧端与封闭机电空腔不算可用容量。']

# Build native details on the saved integrated master.
bpy.ops.wm.open_mainfile(filepath=str(BASE));s=bpy.context.scene;s.frame_set(1)
target=bpy.data.collections.new('v20 完整实装 · 细部与协调');s.collection.children.link(target)
archive=bpy.data.collections.new('v20 整合版被替换细节 · 隐藏留档');s.collection.children.link(archive);archive.hide_render=True;archive.hide_viewport=True
def retire(o):
    for co in list(o.users_collection):co.objects.unlink(o)
    archive.objects.link(o);o['retired_in_phase']='v20-complete'
    if o.get('home_design_role')=='furniture':o['home_design_role']='retired_furniture'
def named(prefix):return bpy.data.materials.get(prefix) or next((m for m in bpy.data.materials if m.name.startswith(prefix+'.')),None)
mats={'wood':named('V10 · 减黄浅橡木'),'walnut':named('V19 · walnut'),'cabinet':named('R01 · 暖白哑光柜门'),'wall-finish':named('V10 · 干净暖白平整哑光'),'butter':named('V07 · butter')}
for k,rec in d['furnitureMaterials'].items():
    if mats.get(k):continue
    m=named('V19 · '+k) or named('V14 · '+k) or named('V07 · '+k)
    if not m:
        m=bpy.data.materials.new('V20F · '+k);m.use_nodes=True;p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=rec['color'];p.inputs['Roughness'].default_value=rec.get('roughness',.7)
    mats[k]=m
# Deeper brown walnut is local to the full implementation; old masters retain their materials.
walnut=mats['walnut'].copy();walnut.name='V20F · 深胡桃木细纹'
for node in walnut.node_tree.nodes:
    if node.type=='VALTORGB':
        node.color_ramp.elements[0].color=(.026,.011,.006,1)
        node.color_ramp.elements[-1].color=(.105,.052,.028,1)
mats['walnut']=walnut
for script,name in [('render_modern_japanese_v02.py','profile_mesh'),('update_blender_v07.py','mesh_part'),('render_modern_japanese_v02.py','rect_subtract')]:
    tree=ast.parse((R/'tools'/script).read_text(encoding='utf8'));node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name);exec(compile(ast.Module(body=[node],type_ignores=[]),name,'exec'))
def make(p):
    if p.get('shape')=='mesh':
        verts=[((p['x']+v[0])/1000,-(p['z']+v[2])/1000,(p['y']+v[1])/1000) for v in p['localVerticesMm']];faces=p['meshFaces']
    elif p.get('planProfileLocalMm'):
        profile=p['planProfileLocalMm'];n=len(profile);verts=[((p['x']+a)/1000,-(p['z']+b)/1000,yy/1000) for yy in [p['y'],p['y']+p['h']] for a,b in profile];faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    elif p.get('planCornerRadiiMm'):
        # Explicit profile avoids generic modifier limits on large plan radii.
        radii=p['planCornerRadiiMm'];points=[]
        for (cx,cz,start),rr in zip([(radii[0],radii[0],math.pi),(p['w']-radii[1],radii[1],1.5*math.pi),(p['w']-radii[2],p['d']-radii[2],0),(radii[3],p['d']-radii[3],.5*math.pi)],radii):
            if not rr:points.append([cx,cz]);continue
            for j in range(13):points.append([cx+rr*math.cos(start+j*math.pi/24),cz+rr*math.sin(start+j*math.pi/24)])
        return make({**p,'planProfileLocalMm':points})
    else:return mesh_part(p)
    me=bpy.data.meshes.new(p['id']);me.from_pydata(verts,[],faces);me.materials.append(mats[p['material']]);me.update();o=bpy.data.objects.new(p['id'],me);target.objects.link(o)
    if p.get('bevelMm'):
        mod=o.modifiers.new('柔化触边','BEVEL');mod.width=p['bevelMm']/1000;mod.segments=3
    return o
def join(items,name):
    bpy.ops.object.select_all(action='DESELECT')
    for o in items:
        o.hide_set(False);o.select_set(True);bpy.context.view_layer.objects.active=o
        for mod in list(o.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.context.view_layer.objects.active=items[0];bpy.ops.object.join();o=bpy.context.object;o.name=name
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();return o
ff={o['source_id']:o for o in s.objects if o.get('home_design_role')=='furniture'}
before={k:dict(location=list(o.location),rotation=list(o.rotation_euler),mesh=len(o.data.vertices)) for k,o in ff.items()}
changed=['tv-high','entry-shoe-cabinet','bookcase','dining-sideboard-island','laundry-enclosure','living-rug']
for q in d['furnitureObjects']:
    gid=q['id']
    if gid in changed:
        if gid in ff:retire(ff[gid])
        pp=[p for p in d['furniture'] if p['parent']==gid];o=join([make(p) for p in pp],gid+' | '+q['name'])
        bpy.context.view_layer.update();world=[o.matrix_world@v.co for v in o.data.vertices];anchor=Vector((q['x']/1000,-q['z']/1000,0));o.matrix_world=Matrix.Identity(4);o.location=anchor
        for v,point in zip(o.data.vertices,world):v.co=point-anchor
        for key,v in dict(home_design_role='furniture',source_id=gid,display_name=q['name'],zone=q['zone'],scheme=q['scheme'],import_x_mm=q['x'],import_z_mm=q['z'],movement_step_mm=100,dimensions_mm=[q['dimensionsMm'][k] for k in ['length','width','height']],dimension_note=q['detail'],part_source_mm=json.dumps(pp,ensure_ascii=False),style_revision='modern-japanese-v20-complete').items():o[key]=v
        ff[gid]=o;o.lock_location[2]=True;o.lock_rotation[0]=o.lock_rotation[1]=True
    if q.get('movementGroup'):ff[gid]['movement_group']=q['movementGroup']
    pts=[ff[gid].matrix_world@v.co for v in ff[gid].data.vertices];lo=[min(v[i] for v in pts)*1000 for i in range(3)];hi=[max(v[i] for v in pts)*1000 for i in range(3)]
    q['meshBoundsMm']=dict(x=round(lo[0],3),z=round(-hi[1],3),y=round(lo[2],3),w=round(hi[0]-lo[0],3),d=round(hi[1]-lo[1],3),h=round(hi[2]-lo[2],3))
    if gid in before:assert max(abs(ff[gid].location[i]-before[gid]['location'][i]) for i in range(3))<1e-6
for gid in ['office-divider','double-desk']:
    for slot in ff[gid].material_slots:
        if slot.material and 'walnut' in slot.material.name.lower():slot.material=mats['walnut']

# Regenerate source walls and clean display union; curved / recessed finish pieces separate.
oldwalls=[o for o in s.objects if o.get('home_design_role') in ['wall','wall_visual_union','wall_finish_proposal']]
for o in oldwalls:retire(o)
custom={p['id'] for p in d['walls'] if p.get('planProfileLocalMm') or p.get('planCornerRadiiMm') or p.get('finishBaseRecessMm')}
sty=load('05_style/modern-japanese-v20.json')
profiles=sty.get('designer_decisions',{}).get('wall_finish_profiles_mm',{})
for ident,radii in profiles.items():
    if ident in wmap:wmap[ident]['planCornerRadiiMm']=radii;custom.add(ident)
for p in d['walls']:
    o=make({**p,'material':'wall-finish','shape':'box'});o['source_id']=p['id'];o['home_design_role']='wall';o.hide_select=True;o.hide_render=True;o.hide_set(True)
    if p['id'] in custom:
        pieces=[];recess=p.get('finishBaseRecessMm')
        if recess:
            thick=recess['finishLayer'];front=recess['face']=='zmin'
            core={**p,'id':p['id']+'-core','z':p['z']+thick if front else p['z'],'d':p['d']-thick,'material':'wall-finish','shape':'box'};pieces.append(make(core))
            for suffix,yy,hh,offset,mat in [('face',62,2688,0,'wall-finish'),('kick',0,58,8,'skirting'),('joint',58,4,10,'shadow')]:
                z=p['z']+offset if front else p['z']+p['d']-thick
                dep=thick-offset
                if not front:z+=0
                pieces.append(make(box(p['id']+'-'+suffix,p['x'],z,p['w'],dep,yy,hh,mat)))
        else:pieces=[make({**p,'id':p['id']+'-finish','material':'wall-finish','shape':'box','bevelMm':1})]
        ob=join(pieces,'v20f finish '+p['id']);ob['home_design_role']='wall_finish_proposal';ob['source_wall_id']=p['id'];ob['finish_geometry_only']=True
boxes=[([p['x']/1000,-(p['z']+p['d'])/1000,p['y']/1000],[(p['x']+p['w'])/1000,-p['z']/1000,(p['y']+p['h'])/1000]) for p in d['walls']]
verts=[];faces=[]
for i,(lo,hi) in enumerate(boxes):
    if d['walls'][i]['id'] in custom:continue
    for axis in range(3):
        aa,bb=[k for k in range(3) if k!=axis]
        for positive in [False,True]:
            plane=hi[axis] if positive else lo[axis];rects=[(lo[aa],lo[bb],hi[aa],hi[bb])]
            for j,(ol,oh) in enumerate(boxes):
                if i==j:continue
                hidden=(ol[axis]<=plane+1e-8 and oh[axis]>plane+1e-8) if positive else (ol[axis]<plane-1e-8 and oh[axis]>=plane-1e-8)
                duplicate=(abs(oh[axis]-plane)<1e-8 and ol[axis]<plane-1e-8 and j<i) if positive else (abs(ol[axis]-plane)<1e-8 and oh[axis]>plane+1e-8 and j<i)
                if hidden or duplicate:rects=[r2 for r1 in rects for r2 in rect_subtract(r1,(ol[aa],ol[bb],oh[aa],oh[bb]))]
            for a,b,c,e in rects:
                quad=[]
                for va,vb in [(a,b),(c,b),(c,e),(a,e)]:
                    point=[0.,0.,0.];point[axis]=plane;point[aa]=va;point[bb]=vb;quad.append(tuple(point))
                normal3=(Vector(quad[1])-Vector(quad[0])).cross(Vector(quad[2])-Vector(quad[0]))
                if (normal3[axis]>0)!=positive:quad.reverse()
                off=len(verts);verts+=quad;faces.append(tuple(range(off,off+4)))
me=bpy.data.meshes.new('v20 完整墙体并集');me.from_pydata(verts,[],faces);me.materials.append(mats['wall-finish']);me.update();ob=bpy.data.objects.new('v20 · 完整墙体与对齐主卫',me);target.objects.link(ob);ob['home_design_role']='wall_visual_union';ob['source_wall_count']=len(d['walls'])

# Replace actual fixed detail meshes and animated bathroom doors, keeping unrelated fixtures.
new_arrays=['detailParts','bathParts','referenceParts']
old_ids={p['id'] for key in new_arrays for p in base[key]}
for o in list(s.objects):
    sid=o.get('source_id',o.name)
    if sid=='v20-dining-pendant':continue
    if sid in old_ids or o.name in old_ids or o.get('home_design_role')=='bath_door_control':retire(o)
ctrl=bpy.data.objects.new('v20 主卫双折门 · 0闭1开',None);target.objects.link(ctrl);ctrl['home_design_role']='bath_door_control';ctrl['open_ratio']=0.;ctrl.id_properties_ui('open_ratio').update(min=0.,max=1.)
def drive(obj,path,index,expr):
    dr=obj.driver_add(path,index).driver;v=dr.variables.new();v.name='a';v.type='SINGLE_PROP';v.targets[0].id=ctrl;v.targets[0].data_path='["open_ratio"]';dr.expression=expr
for key in new_arrays:
    for p in d[key]:
        if key=='referenceParts' and p.get('sourceStudy')=='dining':continue # Pendant is a joined existing native object.
        if p.get('bifoldPanel') is not None:
            # Leaf local x follows panel direction; rotate / slide analytically with the fold.
            panel=p['bifoldPanel'];a,b=(hinge,hinge+u*410) if panel==0 else (hinge+u*410,hinge+u*820)
            o=make(prof(p['id'],bifold_points(panel,0),p['y'],p['h'],'wall-finish',bevelMm=2))
            # Analytic drivers transform world-anchored closed mesh about its start pivot.
            pivot=Vector((a.x/1000,-a.y/1000,0));o.data.transform(Matrix.Translation(-pivot));o.location=pivot
            if panel==0:drive(o,'rotation_euler',2,'a*pi/2')
            else:
                drive(o,'rotation_euler',2,'-a*pi/2')
                drive(o,'location',0,f'{hinge.x/1000}+0.410*(-0.7071067811865476*cos(a*pi/2)+0.7071067811865476*sin(a*pi/2))+0.042*sin(a*pi/2)*(0.7071067811865476*cos(a*pi/2)-0.7071067811865476*sin(a*pi/2))')
                drive(o,'location',1,f'{-hinge.y/1000}-0.410*(0.7071067811865476*cos(a*pi/2)+0.7071067811865476*sin(a*pi/2))-0.042*sin(a*pi/2)*(0.7071067811865476*cos(a*pi/2)+0.7071067811865476*sin(a*pi/2))')
        elif p['id']=='v12-curved-cove':
            # Preserve genuine R180 mesh from source; clip its rightmost vertices to new stop.
            original=next((o for o in archive.objects if o.get('source_id')==p['id'] or o.name==p['id']),None)
            if original:
                o=original.copy();o.data=original.data.copy();target.objects.link(o)
                for v in o.data.vertices:
                    pt=o.matrix_world@v.co
                    if pt.x>newEnd/1000:pt.x=newEnd/1000;v.co=o.matrix_world.inverted()@pt
            else:o=make(p)
        else:o=make(p)
        o['source_id']=p['id'];o['home_design_role']='master_suite_detail' if key=='bathParts' else 'reference_finish_detail' if key=='referenceParts' else 'public_finish_detail';o.hide_select=True
        # Preserve the shower controller as installed; this only regenerates the mesh.
        if p.get('slidingPanel'):
            control=next(o for o in s.objects if o.get('home_design_role')=='shower_control')
            f=o.driver_add('location',0).driver;v=f.variables.new();v.name='opened';v.type='SINGLE_PROP';v.targets[0].id=control;v.targets[0].data_path='["open_ratio"]';f.expression=str(p['x']/1000)+'-opened*.700'

# Reposition only the curtain blades' CLOSED target; retain left collection poses.
for p in d['curtainParts']:
    o=next(o for o in s.objects if o.get('source_id')==p['id'])
    o['closed_centre_x_mm']=p['closedCentreX']
    # Existing driver convention is retained; replace all old closed centre constants.
    if o.animation_data:
        old=next(v for v in base['curtainParts'] if v['id']==p['id'])
        for fc in o.animation_data.drivers:
            if fc.data_path=='location' and fc.array_index==0:
                fc.driver.expression=fc.driver.expression.replace(str(old['closedCentreX']/1000),str(p['closedCentreX']/1000))

# Retire old ceilings, then model a complete finish plane with a real lower service zone.
for o in list(s.objects):
    if o.name.startswith('表现用顶面') or o.get('finished_plane_mm')==2750:retire(o)
floor=d['floor']
def inside(x,z):
    hit=False
    for i,p in enumerate(floor):
        q=floor[i-1]
        if (p[1]>z)!=(q[1]>z) and x<(q[0]-p[0])*(z-p[1])/(q[1]-p[1])+p[0]:hit=not hit
    return hit
xs=sorted({p[0] for p in floor}|{3500,8000});zs=sorted({p[1] for p in floor}|{4900,5900})
v=[];f=[]
for x0,x1 in zip(xs,xs[1:]):
    for z0,z1 in zip(zs,zs[1:]):
        cx=(x0+x1)/2;cz=(z0+z1)/2
        if not inside(cx,cz) or (3500<cx<8000 and 4900<cz<5900):continue
        k=len(v);v.extend([(x0/1000,-z0/1000,2.75),(x1/1000,-z0/1000,2.75),(x1/1000,-z1/1000,2.75),(x0/1000,-z1/1000,2.75)]);f.append((k,k+1,k+2,k+3))
me=bpy.data.meshes.new('v20 全屋吊顶完成面');me.from_pydata(v,[],f);me.materials.append(mats['wall-finish']);me.update();roof=bpy.data.objects.new('v20 全屋2750完成顶 · 暂定',me);target.objects.link(roof);roof['home_design_role']='ceiling_finish';roof['finished_plane_mm']=2750;roof['ceilingElement']=True
sol=roof.modifiers.new('18mm表现面层','SOLIDIFY');sol.thickness=.018;sol.offset=-1
for p in d['ceilingParts']:
    o=make(p);o['source_id']=p['id'];o['home_design_role']='ceiling_coordination';o['ceilingElement']=True;o['designer_proposal']=True
for o in s.objects:
    if o.type=='LIGHT' and 3.5<o.location.x<8 and 4.9<-o.location.y<5.9 and o.location.z<2.76:o.location.z=2.585
# Above-ceiling unit / service envelope is wire only and excluded from rendering.
for name,x,z,w,dep,y,h in [('public',6100,5250,1200,550,2780,230)]+[(a,x,z,w,dep,2780,230) for a,x,z,w,dep in private_ac]:
    p=box('v20f-'+name+'-AC-envelope',x,z,w,dep,y,h,'cabinet');o=make(p);o.display_type='WIRE';o.hide_render=True;o['home_design_role']='mep_coordination_envelope';o['equipment_model_unselected']=True
# Low relief rug yarn: physically small bump, never a high pile displacement.
rm=mats['rug'];nt=rm.node_tree;tex=nt.nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=850;tex.inputs['Detail'].default_value=1;bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.18;bump.inputs['Distance'].default_value=.0008;nt.links.new(tex.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED').inputs['Normal'])

write(G,d);sty['version']='v20-full-implementation';sty['geometry_base']=G.relative_to(R).as_posix();sty['geometry_sha256']=sha(G);sty['designer_decisions']['full_implementation_v20']=details;write(S,sty)
s.name='v20 实装完整版 · 暖白浅木与深木';s['home_design_revision']=20;s['home_design_implementation_phase']='full-design';s['home_design_geometry_file']=G.relative_to(R).as_posix();s['home_design_geometry_sha256']=sha(G);s['home_design_style_file']=S.relative_to(R).as_posix();s['home_design_style_sha256']=sha(S);s['full_implementation_v20']=json.dumps(details,ensure_ascii=False);s['photoreal_presentation_revision']=20;s['photoreal_presentation_status']='rerender pending for v20-complete';s['lighting_scene_v19']=0
bpy.context.view_layer.update();bpy.ops.object.select_all(action='DESELECT');ff['office-divider'].select_set(True);bpy.context.view_layer.objects.active=ff['office-divider'];bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(MODEL))
bpy.ops.wm.open_mainfile(filepath=str(MODEL));s=bpy.context.scene;ff={o['source_id']:o for o in s.objects if o.get('home_design_role')=='furniture'}
assert len(ff)==28
checks=[]
for q in d['furnitureObjects']:
    o=ff[q['id']];assert abs(o.location.x*1000-q['x'])<.01 and abs(-o.location.y*1000-q['z'])<.01
    orig=o.location.copy();o.location.x+=.1;bpy.context.view_layer.update();assert abs(o.location.x-orig.x-.1)<1e-6;o.location=orig
    checks.append(dict(id=q['id'],origin=[q['x'],q['z']],move100AndRestore=True,bounds=q['meshBoundsMm']))
assert all(sha(R/p)==v for p,v in baseline.items())
assert sum(o.get('home_design_role')=='wall' and o.get('retired_in_phase') is None for o in s.objects)==len(d['walls'])
write(OUT/'主模型回读.json',dict(status='passed',phase='full-design-implementation',modelSha256=sha(MODEL),geometrySha256=sha(G),styleSha256=sha(S),furnitureCount=28,retainedOrigins=26,retainedOriginChanges=0,added=['living-rug','laundry-enclosure'],changedFurniture=changed,wallSourceCount=len(d['walls']),glassCount=sum(o.get('home_design_role')=='glass' for o in s.objects),furnitureChecks=checks,oldFilesUnchanged=True,fullCeilingsPreserved=True,bathFrontAlignedZ=4896,bathDoor='diagonal inward bifold designer proposal',equipmentAndSiteUnverified=True))
write(OUT/'设计参数.json',details)
print('V20_COMPLETE_MODEL_SAVED',len(ff),len(d['walls']),flush=True)
