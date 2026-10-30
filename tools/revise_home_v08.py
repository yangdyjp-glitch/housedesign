"""Apply selected C cabinet with butter yellow, and source-led balcony fenestration."""
from pathlib import Path
from copy import deepcopy
import json,hashlib,shutil
ROOT=Path(r'D:\AI-Yang.cn\HomeDesign')
SOURCE=ROOT/'02_geometry/geometry-master-v07.json';DEST=ROOT/'02_geometry/geometry-master-v08.json'
assert not DEST.exists(),'Create a new main revision, preserve v07.'
raw=SOURCE.read_bytes();d=json.loads(raw);old=deepcopy(d)
live=json.loads((ROOT/'logs/v08-input-live-state.json').read_text(encoding='utf-8'))['live']
assert live['revision']==7
for p in live['positions']:
    g=next(g for g in d['furnitureObjects'] if g['id']==p['id'])
    assert abs(p['rotation'])<.00001, 'Rotated live furniture needs explicit transformed geometry.'
    dx=p['x']-g['x'];dz=p['z']-g['z']
    for part in d['furniture']:
        if part['parent']==g['id']:part['x']+=dx;part['z']+=dz
    g['x']=p['x'];g['z']=p['z'];g['meshBoundsMm']['x']+=dx;g['meshBoundsMm']['z']+=dz
d['revision']=8;d['project_revision']=8
d['title']='房屋主模型 · 奶黄通顶柜 / 阳台中间大玻璃两侧开启'
d['placementBaselinesByRevision']['7']={g['id']:dict(x=g['x'],z=g['z']) for g in old['furnitureObjects']}
d['previousPlacements']=d['placementBaselinesByRevision']['7'];d['compatiblePlacementRevisions']=[4,5,6,7]

# C is selected, with the homeowner's new lower-front colour.
candidate=json.loads((ROOT/'05_style/cabinet-options-v08/option-c-geometry.json').read_text(encoding='utf-8'))
mapping={'C · 深雾蓝哑光':'butter','C · 温润胡桃木':'walnut','R01 · 暖白哑光柜门':'cabinet','J02 · 深蓝书脊':'navy','R01 · 深灰细砂金属':'metal'}
cab=next(g for g in d['furnitureObjects'] if g['id']=='tv-high')
pp=[]
for source in candidate['furniture']:
    if source['parent']!='tv-high':continue
    p=deepcopy(source);p['material']=mapping[p['material']];p['x']+=cab['x'];p['z']+=cab['z']-5000
    if p['id']=='tv-high-main-carcass':
        p['h']=1140;pp.append(p)
        top=deepcopy(p);top.update(id='tv-high-main-upper-carcass',y=1200,h=1530,material='cabinet');pp.append(top)
    else:pp.append(p)
d['furniture']=[p for p in d['furniture'] if p['parent']!='tv-high']+pp
cab.update(h=2750,visualHeight=2750,name='奶黄与奶油白通顶长柜',detail='第三种上下分色：1200mm以下奶黄色，上部奶油白，胡桃木浅置物格。柜顶2750mm与模型天花贴合，浅格净高200mm、离地1200–1400。',
    dimensionsMm=dict(length=4500,width=400,height=2750),placement_source='v08: latest live v07 position retained; homeowner selected C and replaced navy with milk yellow')
cab['meshBoundsMm']['h']=2750
def linear(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
hexcode='#F1DDAE';rgb=[linear(int(hexcode[i:i+2],16)/255) for i in [1,3,5]]
d['furnitureMaterials']['butter']=dict(name='soft-milk-yellow',color=[*rgb,1],roughness=.63,proposal_srgb_hex=hexcode)
d['furnitureMaterials']['walnut']=dict(name='warm-walnut',color=[.15,.075,.035,1],roughness=.57)
d['features']['furnishing']['continuousCabinet'].update(heightMm=2750,style='C amended: milk yellow lower + cream upper + walnut niche',lowerColorHex=hexcode,topGapMm=0)
d['features']['furnishing']['cabinetSelection']=dict(option='C',amendment='navy changed to milk yellow',selectedBy='direct user instruction',upper='cream',lower='milk-yellow',niche='walnut',fullHeight=True)

# The image is a typology and dimension reference, not a measured opening.
photo=Path(r'C:\Users\ADMINI~1\AppData\Local\Temp\codex-clipboard-21d88d92-e934-4ca9-853e-1ed504d8dfe0.png')
archive=ROOT/'00_sources/v08-balcony-window-reference.png';shutil.copy2(photo,archive)
oldglass=next(g for g in d['glass'] if g['id']=='outer-top-glass-0')
x0=oldglass['x'];width=oldglass['w'];height=oldglass['h'];z=oldglass['z'];depth=oldglass['d']
assert (x0,width,height)==(853,5675,2270)
side=700;lower=1000;frame=55;sash=32
left=x0+side;right=x0+width-side
parts=[];panes=[]
def bar(suffix,x,w,y,h,zz=-160,dd=80,material='window-frame'):
    parts.append(dict(id='balcony-'+suffix,kind='window-frame',shape='box',x=x,z=zz,w=w,d=dd,y=y,h=h,material=material,assembly='balcony-window'))
def glass(suffix,x,w,y,h,role):
    panes.append(dict(id='balcony-glass-'+suffix,kind='glass',x=x,z=z,w=w,d=depth,y=y,h=h,confidence='provisional',windowRole=role,assembly='balcony-window'))
bar('outer-left',x0,frame,0,height);bar('outer-right',x0+width-frame,frame,0,height)
bar('outer-bottom',x0+frame,width-2*frame,0,frame);bar('outer-top',x0+frame,width-2*frame,height-frame,frame)
for name,c in [('left',left),('right',right)]:bar('mullion-'+name,c-frame/2,frame,frame,height-2*frame)
glass('central',left+frame/2,right-left-frame,frame,height-2*frame,'fixed-large-centre')
for name,a,b in [('left',x0+frame,left-frame/2),('right',right+frame/2,x0+width-frame)]:
    bar('transom-'+name,a,b-a,lower-frame/2,frame)
    glass(name+'-bottom',a,b-a,frame,lower-frame/2-frame,'fixed-lower-side')
    sy=lower+frame/2;top=height-frame
    bar('sash-'+name+'-left',a,sash,sy,top-sy,-153,66)
    bar('sash-'+name+'-right',b-sash,sash,sy,top-sy,-153,66)
    bar('sash-'+name+'-bottom',a+sash,b-a-2*sash,sy,sash,-153,66)
    bar('sash-'+name+'-top',a+sash,b-a-2*sash,top-sash,sash,-153,66)
    gx=a+sash;gw=b-a-2*sash;gy=sy+sash;gh=top-sy-2*sash
    glass(name+'-upper',gx,gw,gy,gh,'opening-sash-closed-opening-type-unverified')
    parts.append(dict(id='balcony-screen-'+name,kind='window-screen',shape='screen',x=gx,z=-84,w=gw,d=1,y=gy,h=gh,material='window-mesh',assembly='balcony-window',confidence='mesh inferred from reference hatch, product unselected'))
    hx=b-sash/2-6 if name=='left' else a+sash/2-6
    bar('handle-'+name+'-base',hx-3,18,1465,70,-87,12)
    bar('handle-'+name+'-lever',hx,12,1450,100,-75,25)
d['glass']=[g for g in d['glass'] if g['id']!='outer-top-glass-0']+panes
d['windowParts']=parts
d['features']['balconyWindow'].update(type='large-fixed-centre-plus-two-upper-opening-side-sashes-over-fixed-lower-panes',
    sourceReference=archive.relative_to(ROOT).as_posix(),sourceSHA256=hashlib.sha256(archive.read_bytes()).hexdigest(),
    sourceDimensionsMm=dict(totalWidth=6000,totalHeight=2300,leftBay=700,centreBay=4600,rightBay=700,upperSide=1300,lowerSide=1000,rightAnnotation1500='likely handle reference, unverified'),
    modelOpeningMm=dict(x=x0,width=width,height=height,bottom=0,verifiedOnSite=False),
    provisionalLayoutMm=dict(leftBay=700,centreBay=width-1400,rightBay=700,lowerSide=1000,upperSide=height-1000),
    nominalFrameMm=55,nominalSashBorderMm=32,referencePolicy='match type; keep existing provisional opening; side 700 and lower 1000 used as adjustable references; measured site values prevail',
    openingDirection='unverified',sashesShown='closed',centralMullions=0,upperSideScreens='visual inference from hatched reference',glassPaneCount=5)
for room in d['rooms']:
    if room['id']=='balcony':room['detail']='中央整块固定玻璃；两侧上部开启、下部固定。现有模型窗洞5675×2270mm暂定，示例图6000×2300mm仅参考，待现场实测。'
d['assumptions'] += [
 '用户提供阳台窗型：中间整块固定玻璃，两侧上部开启扇、下部固定；图中6000×2300、700/4600/700、1300/1000为参考，用户明确以实际为准。',
 '现有模型阳台窗洞5675×2270mm仍为草图暂定，未用示例尺寸改动外墙；暂按两侧各700、下部1000、中央4275及上部1270适配。',
 '窗框55、扇框32为外观占位，玻璃24厚沿旧显示包络，不是产品型材或玻璃规格；上扇关闭展示，具体开向、纱扇系统与1500标注含义待核。',
 '走廊长柜采用用户所选第三种上下分色，下部深蓝改为奶黄色；上部奶油白及胡桃木置物格沿用。柜顶2750与暂定天花贴合，实际收口按实测净高深化。']
d['provenance'].update(revision=8,baseline=SOURCE.relative_to(ROOT).as_posix(),baseline_sha256=hashlib.sha256(raw).hexdigest(),
    layout='all 21 latest live positions preserved; no further northward movement',new_user_decisions=['reference balcony fenestration, site dimensions govern','cabinet option C, replace lower navy with milk yellow'])
DEST.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
style=json.loads((ROOT/'05_style/modern-japanese-v03.json').read_text(encoding='utf-8'))
style.update(version='v08-style-v04',geometry_base=DEST.relative_to(ROOT).as_posix(),geometry_sha256=hashlib.sha256(DEST.read_bytes()).hexdigest())
style['homeowner_decisions']+=['走廊柜采用第三种设计，深蓝改为奶黄色','走廊柜通顶','阳台窗型按新参考，尺寸以实测为准']
style['designer_decisions']['selected_corridor_cabinet']=dict(derivedFromOption='C',lowerSRGB=hexcode,upper='existing cream',niche='warm walnut',heightMm=2750,lowerSplitMm=1200,topGapMm=0)
style['designer_decisions']['balcony_window']=d['features']['balconyWindow']
(ROOT/'05_style/modern-japanese-v04.json').write_text(json.dumps(style,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'03_layout/widget-layout-v08-initial.json').write_text(json.dumps(dict(revision=8,units='mm',furniturePositions=[dict(id=g['id'],x=g['x'],z=g['z'],dx=0,dz=0) for g in d['furnitureObjects']]),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'logs/v08-source-ledger.json').write_text(json.dumps(dict(reference=str(archive),source_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),window=d['features']['balconyWindow'],cabinet=d['features']['furnishing']['cabinetSelection'],geometry_sha256=style['geometry_sha256'],furniture_positions='v08-input-live-state.json',measuredCAD=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('V08_GEOMETRY_READY',len(d['furnitureObjects']),len(d['furniture']),len(d['glass']),len(parts))
