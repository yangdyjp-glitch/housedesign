"""Integrate the owner's master-suite concept without certifying site feasibility."""
from pathlib import Path
import copy, hashlib, json

ROOT = Path(__file__).resolve().parents[1]
def write(rel, value):
    (ROOT / rel).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

old = json.loads((ROOT / '02_geometry/geometry-master-v13.json').read_text(encoding='utf-8'))
d = copy.deepcopy(old)
d.update(title='房屋主模型 · 主卧主卫扩展概念', revision=14, project_revision='v14-master-suite-concept')
d['compatiblePlacementRevisions'].append(13)
d['placementBaselinesByRevision']['13'] = {q['id']:dict(x=q['x'], z=q['z']) for q in old['furnitureObjects']}
d['previousPlacements'] = d['placementBaselinesByRevision']['13']
d['assumptions'] = [s for s in d['assumptions'] if not any(k in s for k in ['主卧参考图仅做', '本轮公共区渲染不执行主卫改墙'])]
d['assumptions'] += [
    'v14按用户要求将扩展主卫接入方案主模型；不是施工许可或结构、湿区、排水认证。原v13完整保留。',
    '新增段与原主卫合并，入口向内依次洗手台、马桶、淋浴；无浴缸。向原主卧延伸800为设计试排值，净宽1472、原长2014仍待实测。',
    '保留直侧门，门洞800、概念通行约720；为容纳门洞，原主卧入口右侧墙局部向图下退200，形成私用小门厅。原主卧公共门洞保留。',
    '2米床垫以2150×2150床架占位，头北脚南；图左600深衣柜。床右贴墙、左侧717、床尾754为当前模型值，属于单侧上下床方案。',
    '马桶在原卫浴范围内靠左侧墙布置，排水口位置未知，未据此生成已接通管线。原服务凸块和低窗保留。',
    '新增床、衣柜、洗手台组合和马桶代理可悬停看尺寸、按100毫米试排；洁具移动只是方案操作，不代表排水可随意迁移。',
]
retired_ids = {'upper-right-bottom-1', 'upper-right-bottom-lintel-1', 'upper-right-bottom-end', 'right-small-left-end'}
d['retiredWallsV14'] = [q for q in d['walls'] if q['id'] in retired_ids]
assert len(d['retiredWallsV14']) == 4
d['walls'] = [q for q in d['walls'] if q['id'] not in retired_ids]
def wall(ident,x,z,w,dep,y=0,h=2750):
    d['walls'].append(dict(id=ident,x=x,z=z,w=w,d=dep,y=y,h=h,kind='internal',confidence='concept-unverified',source='v14 owner concept; dimensions by designer trial'))
wall('v14-master-head-wall',8645,3976,2150,120)
wall('v14-bath-left-top-jamb',9203,4096,120,40)
wall('v14-bath-left-door-header',9203,4136,120,800,2100,650)
wall('v14-bath-left-bottom',9203,4936,120,2094)
wall('v14-master-foyer-return',8236,4776,120,320)
wall('v14-master-foyer-front',8236,4976,1087,120)
d['retiredOpeningsV14']=[q for q in d['openings'] if q['wall']=='upper-right-bottom' and q['start']==9724]
d['openings']=[q for q in d['openings'] if q not in d['retiredOpeningsV14']]
d['openings'].append(dict(wall='v14-bath-left',axis='z',c=9203,start=4136,end=4936,sill=0,top=2100,type='door',confidence='concept-unverified'))

# Retire only finishes on the changed partitions. All public furniture remains byte-for-byte identical.
retired_details = {'v10-skirting-master-public-right','v10-skirting-joint-master-public-right','v10-skirting-main-bath-side','v10-skirting-joint-main-bath-side'}
d['retiredDetailsV14'] = [p for p in d['detailParts'] if p['id'] in retired_details]
d['detailParts'] = [p for p in d['detailParts'] if p['id'] not in retired_details]
d['bathParts'] = []
def fixed(ident,x,z,w,dep,y,h,mat,shape='box',**extra):
    collidable=extra.pop('collidable',False)
    p=dict(id=ident,x=x,z=z,w=w,d=dep,y=y,h=h,kind='finish',material=mat,shape=shape,collidable=collidable,**extra)
    d['bathParts'].append(p); return p
fixed('v14-bath-floor-main',9323,4096,1472,2463,2.5,3,'bath-tile')
fixed('v14-bath-floor-service-side',9603,6559,1192,351,2.5,3,'bath-tile')
fixed('v14-bedroom-floor',7328,1072,3467,2904,2,2,'wood')
fixed('v14-bedroom-foyer-floor',8356,4096,847,880,2,2,'wood')
fixed('v14-shower-zone-floor-main',9323,6010,1472,549,6,3,'shower-tile')
fixed('v14-shower-zone-floor-service-side',9603,6559,1192,351,6,3,'shower-tile')
# Shower screen has a left fixed pane and a right sliding pane; 700mm conceptual access when opened.
fixed('v14-shower-track',9323,5990,1472,50,2100,25,'metal')
fixed('v14-shower-fixed-glass',9323,6004,736,10,15,2085,'bath-glass',collidable=True)
fixed('v14-shower-moving-glass',10059,6019,736,10,15,2085,'bath-glass',collidable=True,slidingPanel=True,openPlan=dict(x=9359,z=6019,w=736,d=10))
fixed('v14-shower-handle',10100,5994,16,30,1000,300,'metal',collidable=True,slidingPanel=True,openPlan=dict(x=9400,z=5994,w=16,d=30))
fixed('v14-shower-drain-provisional',10455,6810,280,24,10,3,'metal')
fixed('v14-shower-bar',10745,6460,20,20,900,1200,'metal')
fixed('v14-shower-mixer',10710,6390,55,160,1030,45,'metal')
fixed('v14-shower-arm',10480,6455,280,22,2100,22,'metal')
fixed('v14-shower-head',10430,6390,180,180,2070,25,'metal','cylinder')
# 800mm raw side opening; closed leaf 760, with conceptual 720mm finished passage.
fixed('v14-bath-door-jamb-top',9203,4136,120,20,0,2100,'wall-finish')
fixed('v14-bath-door-jamb-bottom',9203,4916,120,20,0,2100,'wall-finish')
fixed('v14-bath-door-leaf',9203,4156,40,760,6,2088,'wall-finish',collidable=True,swingLeaf=True,openPlan=dict(x=8443,z=4156,w=760,d=40))
fixed('v14-bath-door-handle',9179,4800,30,90,960,12,'metal',collidable=True,swingLeaf=True,openPlan=dict(x=8469,z=4132,w=90,d=30))

def part(ident,parent,x,z,w,dep,y,h,mat,shape='box',**extra):
    p=dict(id=ident,parent=parent,kind='furniture',shape=shape,x=x,z=z,w=w,d=dep,y=y,h=h,material=mat,**extra)
    d['furniture'].append(p);return p
def group(ident,name,x,z,w,dep,h,detail):
    pp=[p for p in d['furniture'] if p['parent']==ident]
    low=[min(p[k] for p in pp) for k in ['x','z','y']]
    high=[max(p[a]+p[b] for p in pp) for a,b in [('x','w'),('z','d'),('y','h')]]
    q=dict(id=ident,name=name,zone='master-suite',scheme='用户批注接续',x=x,z=z,w=w,d=dep,h=h,detail=detail,label=True,labelRotate=0,placement_source='user markup + v14 designer dimensional trial',visualHeight=h,baseHeightMm=0,meshBoundsMm=dict(zip(['x','z','y','w','d','h'],low+[high[i]-low[i] for i in range(3)])),dimensionsMm=dict(length=max(w,dep),width=min(w,dep),height=h))
    d['furnitureObjects'].append(q)

bid='master-bed'
part('v14-bed-base',bid,8645,1826,2150,2150,100,220,'wood','rounded_box',radiusMm=45)
part('v14-bed-mattress',bid,8720,1876,2000,2000,320,240,'fabric','rounded_box',radiusMm=50)
part('v14-bed-headboard',bid,8645,3896,2150,80,100,950,'fabric','rounded_box',radiusMm=35)
part('v14-bed-quilt',bid,8720,1876,2000,1370,560,50,'sage','rounded_box',radiusMm=35)
for i in range(2):part('v14-bed-pillow-'+str(i+1),bid,8830+i*950,3376,800,420,560,130,'fabric','rounded_box',radiusMm=100)
group(bid,'主卧2米床',8645,1826,2150,2150,1050,'床垫2000宽；头北脚南。床架暂拟2150×2150；右侧贴墙，单侧上下床。')
wid='master-wardrobe'
part('v14-wardrobe-plinth',wid,7328,1272,580,2500,0,80,'shadow')
part('v14-wardrobe-body',wid,7328,1272,575,2500,80,2620,'wood')
for i in range(5):part('v14-wardrobe-front-'+str(i+1),wid,7903,1274+i*500,25,496,80,2620,'cabinet')
part('v14-wardrobe-top-scribe',wid,7328,1272,600,2500,2700,50,'cabinet')
group(wid,'主卧通顶衣柜',7328,1272,600,2500,2750,'图左600深、2500长、暂定2750通顶；柜门面向床，内部收纳清单待定。')
vid='master-vanity'
part('v14-vanity-body',vid,10345,4196,450,800,250,540,'wood','rounded_box',radiusMm=25)
part('v14-vanity-top',vid,10345,4196,450,800,790,30,'stone','rounded_box',radiusMm=25)
part('v14-vanity-bowl',vid,10390,4321,360,550,820,110,'ceramic','ellipsoid')
part('v14-vanity-basin-inset',vid,10415,4361,280,470,912,3,'basin-inset','ellipsoid')
part('v14-vanity-tap-column',vid,10740,4536,22,22,820,230,'metal','cylinder')
part('v14-vanity-tap-arm',vid,10620,4536,140,22,1030,22,'metal')
part('v14-vanity-mirror',vid,10779,4216,16,760,1130,1000,'mirror')
group(vid,'主卫洗手台与镜',10345,4196,450,800,2130,'入口右侧800长×450深，台面高820；悬停总高含镜面2130。给排水与实样未定。')
tid='master-toilet'
part('v14-wc-foot',tid,9403,5370,420,360,0,260,'ceramic','ellipsoid')
part('v14-wc-bowl',tid,9453,5350,550,400,240,180,'ceramic','ellipsoid')
part('v14-wc-seat',tid,9463,5360,530,380,410,35,'ceramic','ellipsoid')
part('v14-wc-tank',tid,9323,5350,150,400,400,400,'ceramic','rounded_box',radiusMm=30)
group(tid,'主卫马桶',9323,5350,680,400,800,'位于原主卫范围内，靠左侧墙、面向右；排污口未知，100mm移动仅用于方案试排。')

for key,color,rough in [('bath-tile',[.70,.71,.67,1],.65),('shower-tile',[.56,.61,.56,1],.72),('bath-glass',[.76,.87,.86,1],.06),('basin-inset',[.62,.66,.64,1],.35),('wall-finish',[.89,.88,.84,1],.82),('shadow',[.10,.11,.10,1],.8)]:
    d['furnitureMaterials'][key]=dict(color=color,roughness=rough)

suite=dict(status='applied-to-concept-model; site feasibility unverified',source='00_sources/master-bath-expansion-markup-01.png',source_sha256=sha(ROOT/'00_sources/master-bath-expansion-markup-01.png'),ownerConfirmed=['新增段与原主卫合并','洗手台—马桶—淋浴；干湿分离；无浴缸','床垫2000宽；头北脚南；图左衣柜'],bathRectMm=dict(x=9323,z=4096,w=1472,d=2814),extensionMm=800,wallThicknessMm=120,door=dict(rawOpeningMm=800,leafMm=760,conceptClearOpeningMm=720,openingZ=[4136,4936],swing='outwards into private foyer, south/top hinge',hingePlanMm=[9203,4156],defaultOpen=False,frameProductSelected=False),foyer=dict(stepIntoHallMm=200,newFrontOuterZ=5096,previousFrontOuterZ=4896,referenceBandToGuestFrontMm=1049,referenceBandIsNotCertifiedClearance=True),shower=dict(depthMm=900,widthMm=1472,screenZ=6010,defaultOpen=False,slidingTravelMm=700,clearOpeningConceptMm=700,serviceBlockRetained=True),bed=dict(mattressWidthMm=2000,framePlanMm=[2150,2150],head='north / image bottom',feet='south / image top',wardrobeGapMm=717,footGapMm=754,rightSideGapMm=0,singleSideAccess=True),constructionStatus='Not approved for construction; original wet boundary, lower-storey use, structure, drains, window and finished sizes remain unverified',publicFurnitureUnchanged=23,budgetConsidered=False)
d['features']['masterSuite']=suite
d['features']['publicRefinement']['publicFloorPolygon']=[[0,0],[7188,0],[7188,4896],[8236,4896],[8236,5096],[9203,5096],[9203,6145],[4759,6145],[4759,6090],[3082,6090],[3082,9635],[0,9635]]
for r in d['rooms']:
    if r['id']=='upper-right':r.update(x=8270,z=2600,detail='2米床头北脚南；左侧600深衣柜。扩卫后床尾约754、柜床间717，右侧贴墙。尺寸待核。')
    if r['id']=='small-right':r.update(x=10025,z=5720,detail='扩展主卫约1472×2814：洗手台—马桶—淋浴；干湿分离，无浴缸。扩卫允许性及排水未核。')
d['dimensions'].append(dict(a=[11095,4096],b=[11095,6910],label='2814*'))
d['style']='modern-japanese-v10'
d['provenance']['v14_master_suite']=dict(previous_geometry_sha256=sha(ROOT/'02_geometry/geometry-master-v13.json'),public_objects_preserved=23,source='user markup and confirmed sequence; 800/200 are designer trials')
d['provenance'].update(revision=14,baseline='02_geometry/geometry-master-v13.json',baseline_sha256=sha(ROOT/'02_geometry/geometry-master-v13.json'),layout='v13 public 23 objects unchanged; owner master-suite concept with provisional 800mm extension and 200mm foyer step')
assert d['furnitureObjects'][:23]==old['furnitureObjects'] and all(p in d['furniture'] for p in old['furniture'])
assert len(d['walls'])==62 and len(d['furnitureObjects'])==27
write('02_geometry/geometry-master-v14.json',d)
s=json.loads((ROOT/'05_style/modern-japanese-v09.json').read_text(encoding='utf-8'))
s.update(version='v14-style-v10',geometry_base='02_geometry/geometry-master-v14.json',geometry_sha256=sha(ROOT/'02_geometry/geometry-master-v14.json'))
s['designer_decisions']['master_suite']=suite
s['designer_decisions']['public_refinement']=copy.deepcopy(d['features']['publicRefinement'])
s['designer_decisions']['balcony_tea_set']=copy.deepcopy(d['features']['balconyTeaSet'])
s['designer_decisions']['wall_scope']='公共区弧形饰面沿用；v14仅主卧/主卫及局部门口按已确认关系做概念调整，非结构认证'
s['locked']=['公共区23件家具当前位置、网格与既选材质','阳台落地窗、主卧飘窗及外墙保留','85寸电视；34寸单屏办公；四椅靠墙餐桌；矮茶席','主卫新增段与原主卫合并；洗手台—马桶—淋浴；无浴缸','2米床垫头北脚南，图左衣柜']
write('05_style/modern-japanese-v10.json',s)
print('V14_GEOMETRY_READY',len(d['walls']),len(d['furnitureObjects']))
