"""Public-area refinement: source-preserving geometry, palette and lighting intent."""
from pathlib import Path
import copy,json,hashlib,math
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads((R/p).read_text(encoding='utf8'))
def write(p,v):(R/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
old=read('02_geometry/geometry-master-v18.json');d=copy.deepcopy(old)
d.update(title='现代日式四区深化 · 暖白浅木与深木绿蓝',revision=19,project_revision='v19-public-refinement',style='modern-japanese-v19',presentation_snapshot_only=False)
d['compatiblePlacementRevisions']=sorted(set(d['compatiblePlacementRevisions']+[18]))
d['placementBaselinesByRevision']['18']={q['id']:dict(x=q['x'],z=q['z']) for q in old['furnitureObjects']}
removed=[p for p in d['referenceParts'] if p['id'].startswith('v12-tv-')]
d['referenceParts']=[p for p in d['referenceParts'] if not p['id'].startswith('v12-tv-')]
d['retiredReferencePartsV19']=removed
d['retiredDetailPartsV19']=[p for p in d.get('detailParts',[]) if p['id'] in ['v10-living-cove-lip','v10-hall-cove-lip']]
d['detailParts']=[p for p in d.get('detailParts',[]) if p['id'] not in ['v10-living-cove-lip','v10-hall-cove-lip']]
ref=d['features']['publicRefinement'];ref['wood']='pale oak as the main timber; dark walnut in bookcase recess and selected table/chair bases, not a matching whole-house suite'
ref['wall']='clean matte warm white; all old decorative TV frames/panel/fine lines removed; one restrained dining artwork'
ref['lighting'].update(preference='full suspended ceiling intent, living no central main luminaire; concealed curtain/cabinet light plus task and cleaning layers',circuits=['curtain cove','bookcase selected shelf lights','entry bench/niche/guide','desk task','dining diffuse pendant','living/hall general cleaning'],sceneNames=['day','evening','dining','cleaning','viewing'])
ref['palette']['walnut']='#665047'
def part(ident,parent,x,z,w,dep,y,h,mat,**extra):
 p=dict(id=ident,parent=parent,kind='furniture',shape='rounded_box',x=x,z=z,w=w,d=dep,y=y,h=h,material=mat,bevelMm=2,**extra);d['furniture'].append(p);return p
# Change visible bases, keeping the existing latest footprint and rounded tops.
for p in d['furniture']:
 if p['parent'] in ['side-table','dining-table','double-desk'] and ('leg-' in p['id'] or p['id']=='double-desk-rail'):p['material']='walnut'
 if p['parent'] in ['sofa-modular','ottoman']:
  if p['material'] in ['fabric','fabric-dark','sage','navy']:p.update(shape='rounded_box',radiusMm=min(45,p['w']/4,p['d']/4),bevelMm=min(45,p['w']/4,p['d']/4,p['h']/4))
part('v19-desk-cable-tray','double-desk',5360,3100,110,1150,665,35,'metal',radiusMm=8)
# Slim chairs: curved back rail instead of the old full-height slab; four seats remain.
for i in range(1,5):
 gid=f'dining-chair-{i}';q=next(q for q in d['furnitureObjects'] if q['id']==gid);x,z=q['x'],q['z'];pp=[p for p in d['furniture'] if p['parent']==gid];oldback=next(p for p in pp if p['id'].endswith('-back'))
 d['furniture']=[p for p in d['furniture'] if p['parent']!=gid]
 part(gid+'-seat',gid,x,z,450,450,420,40,'sage' if i<3 else 'fabric',radiusMm=45,)
 for xx in [x+20,x+390]:
  for zz in [z+20,z+390]:part(f'{gid}-leg-{int(xx)}-{int(zz)}',gid,xx,zz,40,40,0,420,'walnut',radiusMm=10)
 # local U-like bow has its most recessed point at the back, returns 45 mm at the ends.
 curve=[[22+45*(2*t/20-1)**2,450*t/20] for t in range(21)]
 profile=[[a-22,b] for a,b in curve]+[[a,b] for a,b in reversed(curve)]
 if i<3:
  plan=profile;bx,bz=x,z;ww,dd=67,450
  supports=[(x+39,z+20),(x+39,z+400)]
 elif i==3:
  plan=[[b,a] for a,b in profile];bx,bz=x,z;ww,dd=450,67;supports=[(x+20,z+39),(x+400,z+39)]
 else:
  plan=[[b,67-a] for a,b in profile];bx,bz=x,z+383;ww,dd=450,67;supports=[(x+20,z+388),(x+400,z+388)]
 for k,(xx,zz) in enumerate(supports):part(f'{gid}-back-support-{k}',gid,xx,zz,26,26,460,270,'walnut',radiusMm=7)
 part(gid+'-back',gid,bx,bz,ww,dd,680,170,'walnut',planProfileLocalMm=plan)
 q['detail']='四张餐椅保留原位，450×450×850 mm；座高460，细腿、弧形短靠背；两张苔绿、两张米灰细织座面。椅背使用空间仍需解决，造型变薄不等于净空合格。'
# Bookcase: original 800-high closed base remains; reduce display and add real top storage.
d['furniture']=[p for p in d['furniture'] if p['parent']!='bookcase'];gid='bookcase';x,z=6838,1176
for n,zz in [('balcony',z),('hall',z+2800)]:
 part('v19-book-'+n+'-body',gid,x+20,zz,330,800,0,2750,'cabinet')
 for j in range(2):part(f'v19-book-{n}-door-{j}',gid,x,zz+4+j*400,18,392,4,2692,'cabinet')
 part('v19-book-'+n+'-scribe',gid,x,zz,18,800,2700,50,'cabinet')
zz=z+800
part('v19-book-base-body',gid,x+20,zz,330,2000,0,780,'cabinet')
part('v19-book-base-top',gid,x,zz,350,2000,780,20,'wood')
for i in range(4):part(f'v19-book-base-door-{i}',gid,x,zz+4+i*500,18,492,4,772,'cabinet')
part('v19-book-open-back',gid,x+330,zz,20,2000,800,1350,'walnut')
for i,zp in enumerate([zz,zz+991,zz+1982]):part(f'v19-book-partition-{i}',gid,x+12,zp,318,18,800,1350,'wood')
for yy in [800,1250,1700,2130]:part('v19-book-shelf-'+str(yy),gid,x,zz,350,2000,yy,20,'wood')
part('v19-book-upper-body',gid,x+20,zz,330,2000,2150,600,'cabinet')
for i in range(4):part(f'v19-book-upper-door-{i}',gid,x,zz+4+i*500,18,492,2154,542,'cabinet')
part('v19-book-upper-scribe',gid,x,zz,18,2000,2700,50,'cabinet')
# 18 books across six bays; retained empty space is intentional, not capacity proof.
for row,yy in enumerate([820,1270,1720]):
 for col in range(2):
  for j,hh in enumerate([235,270,220]):part(f'v19-book-prop-{row}-{col}-{j}',gid,x+70,zz+100+col*991+j*55,180,38,yy,hh,['book','navy','cabinet'][j])
q=next(q for q in d['furnitureObjects'] if q['id']==gid);q.update(h=2750,visualHeight=2750,dimensionsMm=dict(length=3600,width=350,height=2750),detail='3600长×350深×2750高到顶；原800高封闭底柜保留，中央800–2150深木背板与六格浅木开放层板，2150以上新增封闭储物；两端白色高柜。无裸露顶缝，实际封板/板厚/跨度加强及容量待深化。')
# Fixed decorative/lighting elements, distinct from selectable furniture.
def fixed(ident,x,z,w,dep,y,h,mat,shape='rounded_box',**kw):
 d['referenceParts'].append(dict(id=ident,kind='reference-finish',shape=shape,x=x,z=z,w=w,d=dep,y=y,h=h,material=mat,collidable=False,**kw))
fixed('v19-dining-pendant-shade',2507,7800,350,600,1500,240,'paper',shape='ellipsoid')
fixed('v19-dining-pendant-cord',2680,8098,4,4,1740,1000,'metal')
fixed('v19-dining-pendant-canopy',2632,8050,100,100,2735,15,'wall-finish',radiusMm=30)
# 900-wide along the table wall, 600-high artwork; original abstract blocks, no external artwork.
fixed('v19-dining-art-frame',3058,7650,24,900,1200,600,'walnut')
fixed('v19-dining-art-ground',3055,7662,3,876,1212,576,'paper')
fixed('v19-dining-art-sage',3053,7740,2,330,1280,350,'art-sage',shape='ellipsoid')
fixed('v19-dining-art-navy',3052,8100,2,250,1330,220,'art-navy',shape='ellipsoid')
def lin(c):return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4
for key,hexcol in [('paper','#EEECE3'),('art-sage','#A3AEA0'),('art-navy','#566C80')]:
 d['furnitureMaterials'][key]=dict(color=[lin(int(hexcol[i:i+2],16)/255) for i in [1,3,5]]+[1],roughness=.85,conceptSRGB=hexcol)
# Recalculate exact source-mesh envelope where the source geometry actually changed.
changed=['side-table','dining-table','double-desk','sofa-modular','ottoman','bookcase']+[f'dining-chair-{i}' for i in range(1,5)]
for q in d['furnitureObjects']:
 if q['id'] not in changed:continue
 pp=[p for p in d['furniture'] if p['parent']==q['id']];lo=[min(p[k] for p in pp) for k in ['x','z','y']];hi=[max(p[a]+p[b] for p in pp) for a,b in [('x','w'),('z','d'),('y','h')]]
 q['meshBoundsMm']=dict(zip(['x','z','y','w','d','h'],lo+[hi[i]-lo[i] for i in range(3)]))
latest=dict(atmosphere='natural modern Japanese with deep timber, green and blue accents',ceiling='full-home suspended-ceiling intent; public areas detailed this phase',centralAirConditioning=True,childSpecificDesign=False,tvWall='as clean as possible',livingLighting='no central main luminaire',concealedLightLocations=['curtain','cabinet'],diningLighting='independent diffuse pendant')
ceiling=dict(finishedPlaneMm=2750,status='provisional visual plane inherited, not measured structure or confirmed AC clearance',modelSkinThicknessMm=18,constructionVoidMm=None,structureHeightMm=None,beamBottomMm=None,acUnitModel=None,acUnitPosition=None,acSupplyReturnFinalized=False,intent='coordinate equipment, return, supply and accessible service panels before final ceiling shop drawings',publicModelScope='common matte ceiling plane; other private finishes unchanged')
deep=dict(status='design development concept',userConfirmed=latest,ceiling=ceiling,changedFurniture=changed,allLatestPlacementsPreserved=True,cleanTVWallRemovedIds=[p['id'] for p in removed],bookcase=dict(heightMm=2750,baseClosedHeightMm=800,openBandMm=[800,2150],newClosedTopMm=[2150,2750],openBays=6,displayBooks=18),dining=dict(pendantMm=[600,350,240],pendantBottomMm=1500,tableGapMm=750,artMm=[900,600]),paletteRule='warm white and pale oak dominate; deep walnut limited to recesses and bases, sage/navy in small textile/art areas; milk-yellow corridor lower doors retained',placementChoicePending=False,layoutTrials=[dict(ids=['double-desk','office-chair-1'],dx=-200,dz=0,chairRearGapBeforeMm=408,chairRearGapAfterMm=608,sofaDeskGapAfterMm=100),dict(ids=['dining-table']+[f'dining-chair-{i}' for i in range(1,5)],dx=0,dz=-200,doorEndGapBeforeMm=285,doorEndGapAfterMm=485)],laundryCurtainGapMm=10,laundryUnchangedPendingEquipmentCoordination=True,noBudgetConstraint=True)
d['features']['deepeningV19']=deep
deep['placementDecision']='owner confirmed retain every current position on 2026-11-04; 200mm trials not applied'
deep['layoutTrialsStatus']='not adopted; historical comparison only'
deep['ceiling']['acCoordination']={
 'status':'schematic candidate zones, not equipment or duct sizing',
 'serviceBandPlanMm':[3500,5100,4500,800],
 'supplyCandidatePlanMm':[1000,4810,1900,90],
 'returnCandidatePlanMm':[3900,5800,1800,90],
 'visualIntent':'straight narrow white face at corridor/living transition; keep the main ceiling quiet and access outside tall cabinets',
 'requires':['structure/beam survey','equipment selection and capacity','static pressure and duct routing','condensate route and slope','manufacturer service access','supply/return separation and seated draft check'],
 'diningBranch':'separate branch/zone subject to load and equipment coordination; no invented vent dimensions',
 'source':'designer candidate layout, not HVAC engineering approval'}
d['features']['referenceRefinement']['tv']['background']='plain warm-white paint, old decorative border/panel/fine lines removed v19'
d['assumptions'] += ['v19业主选定自然现代日式+深木绿蓝、全屋吊顶、中央空调、客厅无主灯、窗帘柜体灯槽、餐厅独立光；本轮具体建模仍为四区。','2750为沿用的效果图完成面暂定高度，结构层高、梁底、设备型号及吊顶空腔尚未测定；不凭此给出最终风口、检修口及设备安装尺寸。','业主2026-11-04确认办公桌椅、餐桌四椅均保留现位，200mm试排不应用。中央空调尚未选型，先做吊顶与风口协调示意；10mm帘布与洗烘模型余量尚不足以证明实物运行不碰。']
d['provenance'].update(revision=19,baseline='02_geometry/geometry-master-v18.json',baseline_sha256=sha('02_geometry/geometry-master-v18.json'),layout='all 28 latest absolute positions retained; source styles and fixed detailing changed')
assert len(d['furnitureObjects'])==28 and d['walls']==old['walls'] and d['glass']==old['glass']
assert all((q['x'],q['z'])==(old['furnitureObjects'][i]['x'],old['furnitureObjects'][i]['z']) for i,q in enumerate(d['furnitureObjects']))
write('02_geometry/geometry-master-v19.json',d)
s=read('05_style/modern-japanese-v18.json');s.update(version='v19-public-refinement',geometry_base='02_geometry/geometry-master-v19.json',geometry_sha256=sha('02_geometry/geometry-master-v19.json'));s['designer_decisions']['deepening_v19']=deep
write('05_style/modern-japanese-v19.json',s)
write('03_layout/widget-layout-v19-initial.json',dict(revision=19,moveStepMm=100,furniturePositions=[dict(id=q['id'],x=q['x'],z=q['z'],dx=0,dz=0) for q in d['furnitureObjects']],curtainMode='privacy',masterBathDoorOpen=False,masterShowerOpen=False))
print('V19_DESIGN_PREPARED',len(d['furnitureObjects']),len(d['furniture']),len(removed))
