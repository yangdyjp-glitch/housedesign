from pathlib import Path
from copy import deepcopy
import json,hashlib,shutil
ROOT=Path(r'D:\AI-Yang.cn\HomeDesign');SOURCE=ROOT/'02_geometry/geometry-master-v09.json';DEST=ROOT/'02_geometry/geometry-master-v10.json'
assert not DEST.exists()
raw=SOURCE.read_bytes();d=json.loads(raw);old=deepcopy(d)
live=json.loads((ROOT/'logs/v10-input-live-state.json').read_text(encoding='utf-8'))['live'];assert live['revision']==9
for p in live['positions']:
    g=next(g for g in d['furnitureObjects'] if g['id']==p['id']);assert abs(p['rotation'])<1e-6
    assert abs(p['x']-g['x'])<.01 and abs(p['z']-g['z'])<.01,'Reconcile latest live edits before presentation changes.'
d.update(revision=10,project_revision=10,title='房屋主模型 · 暖白浅木与公共区细节深化')
d['placementBaselinesByRevision']['9']={g['id']:dict(x=g['x'],z=g['z']) for g in old['furnitureObjects']}
d['previousPlacements']=d['placementBaselinesByRevision']['9'];d['compatiblePlacementRevisions']=[4,5,6,7,8,9]
answers=[
 '常驻3人，两大一小，目前是毛坯，这部分预算一共10万人民币做硬装，包含柜子，但不包含家具和灯具',
 '更干净的暖白墙＋浅木，减少整体黄感，突出绿色和深蓝',
 '细织布或者棉麻，无家具',
 '更重氛围：间接光和台灯为主，接受明显的明暗层次',
 '这个暂时不定',
 '门墙尽量同面，隐藏门套和踢脚线，愿意增加细节施工投入',
 '平整哑光，主要靠光影、家具和柜体形成层次',
 '直线为骨架，桌角、墙角和柜体外露端部做柔和圆弧']
interview_path=ROOT/'01_brief/detail-interview-v10.json';interview=json.loads(interview_path.read_text(encoding='utf-8'))
for q,a in zip(interview['questions'],answers):q['answer']=a
interview.update(status='answered-in-design-development',storage_inventory_status='deferred by homeowner; no exact storage quantities assumed',public_hard_finish_budget_rmb=100000,
    included_in_budget=['public hard finishes','built-in cabinets'],excluded_from_budget=['loose furniture','lighting fixtures'],household=dict(adults=2,children=1),site='bare shell',existing_furniture='none purchased')
interview_path.write_text(json.dumps(interview,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rgba(code):
    c=[int(code[i:i+2],16)/255 for i in [1,3,5]]
    return [v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in c]+[1]
palette=dict(wall='#F3F1EA',ceiling='#F6F4EF',oak='#D6C6AC',fabric='#D8D5CC',sage='#71816A',navy='#243C55',graphite='#424743',milk='#F1DDAE')
for key,color in [('wood',palette['oak']),('fabric',palette['fabric']),('fabric-dark','#BEBDB5'),('metal',palette['graphite'])]:
    d['furnitureMaterials'][key].update(color=rgba(color),roughness=.68 if 'fabric' in key else .58,conceptSRGB=color)
rows=[]
def part(suffix,x,z,w,dep,y,h,material='wall-finish',collidable=False):
    rows.append(dict(id='v10-'+suffix,kind='finish',shape='box',x=x,z=z,w=w,d=dep,y=y,h=h,material=material,collidable=collidable,assembly='public-detail-v10'))
doors=[]
for name,start,end,face,height,side in [('master-public',7370,8236,4896,2180,1),('guest-bath-public',3812,4759,5970,2100,-1),('guest-room-public',4943,5811,6145,2100,-1)]:
    zz=face-40 if side==1 else face
    part(name+'-reveal',start,face-2 if side==1 else face+1,end-start,1,0,height,'shadow')
    part(name+'-leaf',start+4,zz,end-start-8,40,6,height-10,'wall-finish',True)
    part(name+'-handle',end-160,face if side==1 else face-30,100,30,960,12,'metal')
    doors.append(dict(id=name,start=start,end=end,publicFaceZ=face,top=height,visualRevealMm=4,leafDepthMm=40,
        finish='same matte warm white as public wall',swing='not inferred; closed visual finish proposal only',hardware='slim graphite lever with softened touch edges'))
# Flush skirting is represented on finish faces only; this is not a structural wall-chasing instruction.
for name,x,z,w,dep in [('dining-wall',3081.8,6090,1,3545),('bath-front-left',3082,5969.8,730,1),('bath-front-right',4755,5969.8,4,1),
 ('guest-front-left',4879,6144.8,64,1),('guest-front-right',5811,6144.8,1393,1),('master-public-left',7328,4895.2,42,1),
 ('master-public-right',8236,4895.2,967,1),('main-bath-side',9202.8,4896,1,1249),('living-short-end',7187.8,1072,1,104)]:
    part('skirting-'+name,x,z,w,dep,0,58,'skirting')
    part('skirting-joint-'+name,x,z,w,dep,58,4,'shadow')
# Two local, straight ceiling coves; avoid an all-round decorative dropped ceiling.
part('living-cove-lip',6970,1550,150,2850,2600,100)
part('hall-cove-lip',3500,5200,5300,150,2600,100)
d['detailParts']=rows
public_poly=[[0,0],[7188,0],[7188,4896],[9203,4896],[9203,6145],[4759,6145],[4759,6090],[3082,6090],[3082,9635],[0,9635]]
detail=dict(palette=palette,publicFloorPolygon=public_poly,floorStatus='Existing pale-wood appearance retained as a concept and desaturated; actual flooring product unselected',
    wall='flat matte warm white, no feature wall or heavy texture',wood='one pale oak family on main timber furniture; walnut retained only as existing cabinet accent',
    fabric='fine woven linen-look greige, no new upholstery product selected',doors=doors,
    skirting=dict(visualHeightMm=58,visualTopJointMm=4,intent='flush warm-white skirting, coordinated with concealed door frame',
        construction='reserve within finish build-up before floor and paint; no assumption of structural wall cutting; final profile/depth and movement joints by selected system'),
    joints=dict(doorVisualRevealMm=4,cabinetCeiling='matching scribe retained; no open top gap',status='concept geometry, not order dimensions'),
    curves='existing table R100/R70 and wall R50–80 retained; straight lines remain the main structure; handle touch edges softened',
    storage=dict(status='inventory deferred by homeowner',intent='retain closed storage plus limited display, use adjustable shelves; no fixed counts or final internal dividers'),
    lighting=dict(preference='indirect atmosphere plus existing desk lamp; retained usable general/task circuits',conceptCCT=dict(indirect=3000,task=3500,night=2700),
        circuits=['living ceiling bounce','hall ceiling bounce','TV background','bookcase shelf light','entry niche/low guide','desk task','dining task','general clean-up'],
        sceneNames=['day','evening','cleaning'],renderEnergyStatus='relative rendering controls, not luminaire wattage or verified illumination calculations'),
    budget=dict(totalRMB=100000,scope='public hard finishes and built-in cabinets only',excludes=['loose furniture','light fixtures'],
        controlTargetsRMB=dict(cabinetry=33000,flooring=15000,wallCeiling=16000,doorsWindowsHardware=21000,electricalPreparation=7000,contingency=8000),
        status='allocation targets, not quotations; region, quantities and product systems unconfirmed; balcony glazing included in doors/windows allowance'))
d['features']['publicRefinement']=detail
d['assumptions'] += ['用户已回答深化：两大一小、毛坯；公共区硬装预算100000元含柜，不含家具和灯具。',
 '暖白浅木、平整哑光墙、细织布/棉麻感、氛围间接光、门墙同面和隐藏门套/踢脚线已选；精确色号、地面产品、五金和照度未定。',
 '收纳物品数量由用户暂缓；保留现有柜体占地，内部以可调层板方向深化，不假定固定数量。',
 '公共门同面饰面仅在原有3处洞口关闭展示，沿用原门高，不抬梁或统一扩大门洞；具体开向待核。',
 '踢脚线58高/4顶缝、门缝4和局部直线灯槽为本轮可视化提案，实际型材、找平层、伸缩/检修及安装条件需配套深化，不表示可开槽结构墙。',
 '主卧参考图仅做可借鉴性研究，主卧及主卫边界、排水与家具尚未改动。']
d['provenance'].update(revision=10,baseline=SOURCE.relative_to(ROOT).as_posix(),baseline_sha256=hashlib.sha256(raw).hexdigest(),
    layout='all 21 live furniture placements retained',new_user_decisions=answers)
DEST.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
style=json.loads((ROOT/'05_style/modern-japanese-v05.json').read_text(encoding='utf-8'))
style.update(version='v10-style-v06',geometry_base=DEST.relative_to(ROOT).as_posix(),geometry_sha256=hashlib.sha256(DEST.read_bytes()).hexdigest())
style['homeowner_decisions']+=answers;style['designer_decisions']['public_refinement']=detail
style['designer_decisions']['palette'].update(warm_white=palette['wall'],pale_oak=palette['oak'],oatmeal=palette['fabric'])
style['designer_decisions']['lighting']='indirect-led evening scene, separate usable task and cleaning circuits; CCT/outputs conceptual'
(ROOT/'05_style/modern-japanese-v06.json').write_text(json.dumps(style,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'03_layout/widget-layout-v10-initial.json').write_text(json.dumps(dict(revision=10,units='mm',furniturePositions=[dict(id=g['id'],x=g['x'],z=g['z'],dx=0,dz=0) for g in d['furnitureObjects']],kitchenDoorOpen=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
photo=Path(r'C:\Users\ADMINI~1\AppData\Local\Temp\codex-clipboard-6b89c10b-5988-4f50-b0c1-beef1acf1cec.png')
shutil.copy2(photo,ROOT/'00_sources/v10-master-suite-reference.png')
(ROOT/'logs/v10-source-ledger.json').write_text(json.dumps(dict(geometry_sha256=style['geometry_sha256'],interview='01_brief/detail-interview-v10.json',public_details=detail,
    bedroom_reference='00_sources/v10-master-suite-reference.png',bedroom_status='feasibility study only, no boundary or drain edits',sources=[
        'https://www.mohurd.gov.cn/gongkai/zc/wjk/art/2023/art_17339_775528.html',
        'https://www.eclisse.com/en/support/product/syntesis-baseboard/',
        'https://www.erco.com/en_us/living/']),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('V10_GEOMETRY_READY',len(rows),len(d['furnitureObjects']),style['geometry_sha256'])
