"""Separate right-hand shoes and left-hand piano-hook seating, using the actual entry direction."""
from pathlib import Path
import copy,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
def write(p,v):(ROOT/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
old=read('02_geometry/presentation-layout-v16.json');d=copy.deepcopy(old)
d.update(title='房屋主模型 · 入户右鞋柜与左侧钢琴键换鞋区',revision=18,project_revision='v18-entry-piano',presentation_snapshot_only=False)
d['compatiblePlacementRevisions']=sorted(set(d.get('compatiblePlacementRevisions',[])+[14,16]))
for rev,path in [(14,'02_geometry/geometry-master-v14.json'),(16,'02_geometry/presentation-layout-v16.json')]:d['placementBaselinesByRevision'][str(rev)]={q['id']:dict(x=q['x'],z=q['z']) for q in read(path)['furnitureObjects']}
d['previousPlacements']=d['placementBaselinesByRevision']['14']
d['furniture']=[p for p in d['furniture'] if p['parent']!='entry-shoe-cabinet' and not(p['parent']=='tv-high' and (p['z']>=8500 or p['id']=='tv-high-niche-tray'))]
for p in d['furniture']:
    if p['parent']=='tv-high' and p['z']+p['d']>8500:p['d']=8500-p['z']
tv=next(q for q in d['furnitureObjects'] if q['id']=='tv-high');tv.update(d=3500,dimensionsMm=dict(length=3500,width=400,height=2750),detail='通长柜中段保留奶黄下柜与奶油白上柜；入户端1000毫米改为独立钢琴键换鞋区，上柜仍连续到顶。');tv['meshBoundsMm']['d']=3500
def part(ident,parent,x,z,w,dep,y,h,mat,**extra):
    p=dict(id=ident,parent=parent,kind='furniture',shape='rounded_box',x=x,z=z,w=w,d=dep,y=y,h=h,material=mat,bevelMm=1,**extra);d['furniture'].append(p);return p
gid='entry-shoe-cabinet';z=10818;w=1271
part('v18-shoe-lower-body',gid,0,z+20,w,330,160,1040,'cabinet')
part('v18-shoe-upper-body',gid,0,z+20,w,330,1400,1350,'cabinet')
for i in range(2):
    x=2+i*w/2;dw=w/2-4
    part(f'v18-shoe-lower-door-{i}',gid,x,z-0.0,dw,18,164,1034,'cabinet')
    part(f'v18-shoe-upper-door-{i}',gid,x,z,dw,18,1404,1342,'cabinet')
part('v18-shoe-niche-back',gid,0,z+330,w,20,1200,200,'wood')
part('v18-shoe-niche-bottom',gid,0,z,w,350,1182,18,'wood')
part('v18-shoe-niche-top',gid,0,z,w,350,1400,18,'wood')
part('v18-shoe-bottom-support',gid,60,z+310,w-120,40,0,160,'wood')
q=next(q for q in d['furnitureObjects'] if q['id']==gid);q.update(name='入户右侧通顶鞋柜',zone='entry',scheme='right-shoes-left-bench',detail='按从图左入户向图右行走：右手为图下短墙。1271宽×350深×2750高；底部留空160，1200–1400高随手格，其余封闭鞋物收纳。内部层板与容量待物品清单及实样。',placement_source='user2026-11-03 direction + retained provisional entry footprint')
gid='entry-piano-bench';z=8500
part('v18-bench-back-substrate',gid,0,z,24,1000,450,1350,'wood')
part('v18-bench-base',gid,0,z,400,1000,160,260,'cabinet')
part('v18-bench-seat',gid,0,z,400,1000,420,30,'fabric',radiusMm=25)
part('v18-bench-support',gid,0,z+70,50,860,0,160,'wood')
part('v18-bench-upper',gid,0,z,400,1000,1800,950,'cabinet')
for i in range(2):part(f'v18-bench-upper-door-{i}',gid,382,z+2+i*500,18,496,1804,942,'cabinet')
# Three bands of vertical timber keys; selected end keys are shown folded out.
# Side profile is exact editable geometry, not a keyboard graphic or fixed pegs.
opened={(1,1),(2,2),(17,1),(18,2)}
for i in range(20):
    zz=z+5+i*50
    for band,(yy,hh) in enumerate([(520,350),(874,350),(1228,350)]):
        if (i,band) in opened:
            part(f'v18-piano-key-{i}-{band}',gid,24,zz,120,40,yy+110,134,'wood',sideProfileLocalMm=[[0,120],[108,0],[120,14],[12,134]],pianoKey=True,keyOpen=True)
        else:part(f'v18-piano-key-{i}-{band}',gid,24,zz,22,40,yy,hh,'wood',pianoKey=True,keyOpen=False)
pp=[p for p in d['furniture'] if p['parent']==gid];lo=[min(p[k] for p in pp) for k in ['x','z','y']];hi=[max(p[a]+p[b] for p in pp) for a,b in [('x','w'),('z','d'),('y','h')]]
d['furnitureObjects'].append(dict(id=gid,name='入户左侧换鞋凳与钢琴键挂区',zone='entry',scheme='right-shoes-left-bench',x=0,z=z,w=400,d=1000,h=2750,visualHeight=2750,baseHeightMm=0,label=True,labelRotate=0,dimensionsMm=dict(length=1000,width=400,height=2750),meshBoundsMm=dict(zip(['x','z','y','w','d','h'],lo+[hi[i]-lo[i] for i in range(3)])),detail='从入户门走入后的左手侧，整合进通长柜靠入口末端；1000长×400深，座高450，总高2750含上柜及挂板。浅木钢琴键可收平，4键展开示意，其余收起；开键不超出凳体投影。不是黑白琴键、普通固定挂钩或承重认证。',placement_source='user2026-11-03; integrated into existing cabinet footprint'))
entry=dict(status='applied-concept',direction='Enter from plan left at x0,z10150, heading +x; right is +z/north/image-bottom, left is -z/south/image-top',right=dict(id='entry-shoe-cabinet',wall='left-step-return-end',widthMm=1271,depthMm=350,heightMm=2750,bottomGapMm=160,keyNicheHeightMm=[1200,1400]),left=dict(id=gid,integratedCabinetEndZ=[8500,9500],lengthMm=1000,depthMm=400,seatHeightMm=450,totalHeightMm=2750,pianoKeyRows=3,pianoKeyColumns=20,keysOpenForIllustration=4,keysBeyondBenchProjection=False),entryOpeningPlanZ=[9535,10765],cabinetEndGapToOpeningMm=35,openingAndSwingVerified=False,no_new_floor_footprint=True,reference='https://www.peruse.be/piano',referenceUse='foldable timber-key principle only; no exact product selection or copied dimensions')
d['features']['entryV18']=entry;d['features']['referenceRefinement']['entry'].update(layout='Right short-wall closed shoe cabinet; left existing cabinet end becomes bench/piano-key wall, upper storage continuous',benchWidthMm=1000,benchHeightMm=450)
d['features']['pendingWallAlignmentV17']=dict(request='主卫朝走廊墙面以书柜墙为基准收回200mm',status='pending door arrangement; no owner choice received',options=['diagonal doorway, full swing still requires verification','keep straight door, adjust bed/head partition'],currentMainWallsRemainV14=True)
d['assumptions'] += ['v18按进门实际方向区分左右：右侧图下短墙改整面鞋柜，左侧利用通长柜最靠入口1000mm做换鞋与钢琴键挂板，不新增柜体占地。','钢琴键为可翻折木条挂钩意向，4键展开示意；五金、固定、额定荷载及防夹需选品和节点，未做机械承重仿真。','v17主卫墙对齐仍待门口取舍；此次未擅自改变床位或门洞。']
d['style']='modern-japanese-v18-entry';d['provenance'].update(revision=18,baseline='02_geometry/presentation-layout-v16.json',baseline_sha256=sha(ROOT/'02_geometry/presentation-layout-v16.json'),layout='v16 latest furniture preserved except the two entry storage assemblies; one integrated bench group added')
assert len(d['furnitureObjects'])==28 and len(d['walls'])==62
write('02_geometry/geometry-master-v18.json',d)
s=read('05_style/modern-japanese-v10.json');s.update(version='v18-entry-piano',geometry_base='02_geometry/geometry-master-v18.json',geometry_sha256=sha(ROOT/'02_geometry/geometry-master-v18.json'));s['designer_decisions']['entry_v18']=entry;s['selected_visual_reference']='00_sources/photographic-style-reference-v16.png';write('05_style/modern-japanese-v18.json',s)
write('03_layout/widget-layout-v18-initial.json',dict(revision=18,moveStepMm=100,furniturePositions=[dict(id=q['id'],x=q['x'],z=q['z'],dx=0,dz=0) for q in d['furnitureObjects']],curtainMode='privacy',masterBathDoorOpen=False,masterShowerOpen=False))
print('V18_ENTRY_GEOMETRY_READY',len(d['furnitureObjects']))
