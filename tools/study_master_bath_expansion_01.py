"""Conditional dimensional study of the homeowner's annotated master-suite idea.

Writes independent study artifacts only. Does not edit or activate any main model.
"""
from pathlib import Path
from html import escape
from PIL import Image
import json,hashlib,shutil,sys,math
ROOT=Path(r'D:\AI-Yang.cn\HomeDesign')
SRC=Path(r'C:\Users\ADMINI~1\AppData\Local\Temp\codex-clipboard-b128f33d-2238-41a1-95cb-994298629a90.png')
OUT=ROOT/'09_delivery/master-suite-study-01';OUT.mkdir(parents=True,exist_ok=True)
archive=ROOT/'00_sources/master-bath-expansion-markup-01.png'
if archive.exists():assert archive.read_bytes()==SRC.read_bytes()
else:shutil.copy2(SRC,archive)
graw=(ROOT/'02_geometry/geometry-master-v10.json').read_bytes();g=json.loads(graw)
model=ROOT/'06_blender/home-main-v10.blend';active=(ROOT/'06_blender/active-model.json').read_bytes()
base_hash=hashlib.sha256(model.read_bytes()).hexdigest()
room_w,room_l=3467,3704
wall=120;bath_w,bath_l=1472,2014
bed_w,bed_l,cab_d=2150,2150,600
extension=800;head=room_l-extension;wet_start=head+wall;old_wet_start=room_l+wall;wet_end=old_wet_start+bath_l
door_span=860;door_start=wet_start+50;door_end=door_start+door_span
angled='--angled' in sys.argv;corner_borrow=700;corner_span=math.hypot(corner_borrow,680)
table=[dict(extension_mm=e,foot_clearance_mm=room_l-e-bed_l,private_sidewall_span_mm=e-wall) for e in [700,800,1000]]
record=dict(status='conditional dimensional and functional study, not a selected or construction-ready layout',
    user_markup=archive.relative_to(ROOT).as_posix(),user_markup_sha256=hashlib.sha256(SRC.read_bytes()).hexdigest(),
    source_geometry='02_geometry/geometry-master-v10.json',source_geometry_sha256=hashlib.sha256(graw).hexdigest(),
    interpretation='new grey area connected to existing master bath, pending user clarification; if grey box alone, full three-fixture sequence is not supported',
    user_requirements=['2m mattress width','head north, feet south; north is image bottom','wardrobe along image left wall','entry on image left side of expanded bath','vanity then toilet then shower','dry-wet separation','no bathtub','ignore budget'],
    model_dimensions_mm=dict(bedroom=[room_w,room_l],original_bath=[bath_w,bath_l],wall_thickness=wall),
    dimension_status='all underlying room, bath, wall and window data remain provisional; original 2040 dimension conflict unresolved',
    designer_trial_mm=dict(extension=extension,new_bath_inner=[bath_w,bath_l+extension],bed_outer=[bed_w,bed_l],wardrobe_depth=cab_d,
        foot_clearance=room_l-extension-bed_l,bed_side_to_cabinet=room_w-cab_d-bed_w,right_bed_side_clearance=0,
        private_sidewall_span=extension-wall,trial_side_door_opening_span=door_span,
        side_door_end_beyond_old_bedroom_boundary=door_end-room_l,
        trial_vanity=[800,450],trial_shower_depth=900,toilet_zone_depth=914),
    extension_tradeoff=table,
    independent_geometry=dict(room_local_origin_global_mm=[7328,1072],blue_wall=[1317,head,2150,wall],bed=[1317,head-bed_l,bed_w,bed_l],
        wardrobe=[0,200,cab_d,2500],new_bath_inner=[1995,wet_start,bath_w,bath_l+extension],
        side_door_requiring_entry_boundary_restudy=[1875,door_start,wall,door_span],
        vanity=[3017,wet_start+100,450,800],toilet_trial=[1995,4278,680,400],shower=[1995,4938,bath_w,900],
        existing_service_block=[1995,5487,280,351]),
    unresolved=['whether the marked grey area joins the original bath','original approved wet-area boundary and lower-floor room use','wall and lintel structure',
        'actual bath width and length','toilet outlet and riser position','entry pocket and public corridor if side door crosses old boundary','bed two-sided access',
        'mirror, window, glass partition and service-block interaction'],
    rule_sources=['https://www.mohurd.gov.cn/gongkai/zc/wjk/art/2023/art_17339_775528.html','https://gf.cabr-fire.com/article-70096.htm'],
    angled_entry_alternative=dict(status='unselected design alternative only',borrow_from_entry_corner_mm=corner_borrow,diagonal_span_mm=round(corner_span,1),trial_rough_opening_mm=860,
        finished_clear_width='must be determined with chosen frame and leaf; not equal to 860 rough opening',
        main_bedroom_entry_preserved=True,public_corridor_not_extended_in_this_alternative=True,door_operation_and_wall_junctions='not finalized'),
    original_model_modified=False,active_revision=10,original_model_sha256=base_hash)
if not angled:(OUT/'study-data.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

W,H=1700,1370
svg=[f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs><pattern id="added" width="13" height="13" patternUnits="userSpaceOnUse"><path d="M0 13L13 0" stroke="#d9d1c2" stroke-width="1"/></pattern>
<pattern id="shower" width="16" height="16" patternUnits="userSpaceOnUse"><path d="M0 16L16 0" stroke="#cddfe2" stroke-width="1"/></pattern>
<marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M1 1L7 4L1 7" fill="none" stroke="#53625a" stroke-width="1.4"/></marker></defs>
<rect width="1700" height="1370" fill="#faf9f5"/>
<g font-family="Microsoft YaHei, sans-serif" fill="#303b36">
<text x="60" y="64" font-size="34" font-weight="500">主卧／主卫调整 · 先核对空间关系</text>
<text x="60" y="105" font-size="21" fill="#667167">条件试排：灰框新增段与原主卫连通；2米床头北脚南，左侧衣柜，卫浴由外向里三段组织。</text>
<path d="M830 150V1235" stroke="#dedfd8"/>
''']
def text(x,y,label,size=21,fill='#303b36',anchor='start'):
    svg.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}">{escape(label)}</text>')
scale=.14;ox,oy=112,255
def pt(x,y):return ox+x*scale,oy+y*scale
def rect(x,y,w,h,fill,stroke=None,dash=False,width=2,rx=0):
    a,b=pt(x,y);svg.append(f'<rect x="{a:.2f}" y="{b:.2f}" width="{w*scale:.2f}" height="{h*scale:.2f}" rx="{rx}" fill="{fill}"'+(f' stroke="{stroke}" stroke-width="{width}"' if stroke else '')+(' stroke-dasharray="8 5"' if dash else '')+'/>')
def line(x1,y1,x2,y2,color='#7b8279',width=2,dash=False,arrow=False):
    a,b=pt(x1,y1);c,d=pt(x2,y2);svg.append(f'<path d="M{a:.2f} {b:.2f}L{c:.2f} {d:.2f}" fill="none" stroke="{color}" stroke-width="{width}"'+(' stroke-dasharray="7 5"' if dash else '')+(' marker-end="url(#arrow)"' if arrow else '')+'/>')
def label(x,y,t,size=20,color='#303b36',anchor='middle'):
    a,b=pt(x,y);text(a,b,t,size,color,anchor)
text(60,168,'布局关系试排' if not angled else '设计微调：转角门口',27)
text(60,202,'示例向卧室内延长800 mm，并非从批注像素测得。',20,'#667167')
# Bedroom and existing bath remain distinguishable from the proposed expansion.
rect(0,0,room_w,room_l,'#f0ede3')
rect(1995,old_wet_start,bath_w,bath_l,'#ebefea')
rect(1995,wet_start,bath_w,old_wet_start-wet_start,'#eee7d8')
rect(1995,wet_start,bath_w,old_wet_start-wet_start,'url(#added)')
if angled:
    poly=[pt(1995,wet_start),pt(1995-corner_borrow,3704),pt(1995,3704)]
    pts=' '.join(f'{x:.2f},{y:.2f}' for x,y in poly)
    svg.append(f'<polygon points="{pts}" fill="#eee7d8"/><polygon points="{pts}" fill="url(#added)"/>')
for a,b in [((0,0),(3467,0)),((0,0),(0,3704)),((3467,0),(3467,5838)),((1995,3824),(1995,5838)),((1995,5838),(3467,5838)),((0,3764),(42,3764)),((908,3764),(1995,3764))]:line(*a,*b,width=7)
# The old bedroom/bathroom boundary remains explicitly visible as a reference.
line(1995,3764,3467,3764,'#aaab9e',2,True)
if not angled:line(1995,wet_start,1995,old_wet_start,'#9c9a8e',5)
else:line(1995,3704,1995,old_wet_start,'#9c9a8e',5)
# Bay opening along south, bathroom low window on image right.
line(521,0,2996,0,'#8ba8b2',7)
label(1758,-155,'南／飘窗侧',19,'#58737d')
line(3467,4053,3467,4922,'#8ba8b2',7)
label(3650,4490,'原窗',18,'#58737d')
# 2m mattress is shown within a larger assumed frame, head on the lower edge.
rect(1317,head-bed_l,bed_w,bed_l,'#dbe4d7','#6c8871',False,2,6)
rect(1392,head-bed_l+75,2000,2000,'#e5ebe0','#9ba993',True,1,5)
rect(1392,head-290,920,190,'#f6f5ed','#a4ac9c',False,1,6)
rect(2392,head-290,920,190,'#f6f5ed','#a4ac9c',False,1,6)
label(2392,1770,'2.0 m床垫',25)
label(2392,2000,'床架暂按2150 × 2150',17,'#667167')
line(2392,1450,2392,1120,'#53625a',2,False,True)
label(2392,2320,'床头在图下方／北',18,'#53625a')
rect(0,200,cab_d,2500,'#f1e5ba','#c4a455',False,2)
label(300,1300,'衣柜',22)
label(300,1540,'深600*',17,'#7e754c')
rect(1317,head,2150,wall,'#67a5bc','#4a92ad',False,2)
label(2392,head+265,'新增床头隔墙',18,'#387990')
# Clearance marks.
line(600,1690,1317,1690,'#8a9685',1.5)
label(960,1570,'717*',18)
line(3050,0,3050,754,'#8a9685',1.5)
label(2870,400,'754*',18)
label(1730,500,'床尾通行',18,'#667167')
# The trial doorway is intentionally highlighted where it crosses the old boundary.
if not angled:
    line(1935,door_start,1935,door_end,'#b86c5b',7)
    line(1830,door_start,2050,door_start,'#b86c5b',2)
    line(1830,door_end,2050,door_end,'#b86c5b',2)
    label(1625,3415,'侧门需联动',18,'#a05e50','end')
    label(1625,3625,'入门区边界',18,'#a05e50','end')
    line(1710,3530,1895,3530,'#b86c5b',1.5)
else:
    line(1995,wet_start,1995-corner_borrow,3704,'#b86c5b',7)
    label(1020,3345,'斜角入卫',18,'#a05e50','end')
    label(1020,3555,'门系统另核',17,'#a05e50','end')
    line(1100,3445,1570,3445,'#b86c5b',1.5)
label(1080,4080,'保留主卧入口',17,'#667167')
label(1120,4310,'虚线为旧边界',17,'#8a8d81')
# Three functional zones are a conditional layout, not approved fixture positions.
rect(3017,wet_start+100,450,800,'#e0d5bb','#968e7b',False,1.5,5)
rect(3120,wet_start+260,260,470,'#faf9f5','#a5a494',False,1,8)
label(2480,3450,'洗手台',20)
label(2480,3655,'800×450*',17,'#667167')
rect(1995,4278,680,400,'#faf9f5','#9aaba0',False,1.5,17)
rect(1995,4278,150,400,'#dddeda','#9aaba0',False,1,2)
label(3070,4440,'马桶',20)
label(3070,4660,'位置待排水核对',16,'#667167')
rect(1995,4938,bath_w,900,'#e2edef')
rect(1995,4938,bath_w,900,'url(#shower)')
line(1995,4938,3467,4938,'#7eabb9',3,True)
label(2731,5290,'独立淋浴',22)
label(2731,5520,'深900*',18,'#58737d')
rect(1995,5487,280,351,'#d2d4cc','#939b90',True,1)
label(1890,5735,'原管井？',16,'#667167','end')
label(3640,5490,'玻璃隔断',17,'#58737d','start')
label(2731,6085,'净宽暂拟1472*，总深2814*',20,'#53625a')
# Right side: exact arithmetic from the provisional model; not a universal standard.
text(890,168,'两个主要卡点',27)
text(890,212,'① 床尾通行与侧门宽度互相挤占' if not angled else '① 用转角斜边研究门宽，保留床尾通行',23)
text(890,250,'主卧暂拟进深3704，床架暂按长2150。',20,'#667167')
headers=[('向卧室延长',905),('床尾余量',1130),('新侧墙可用段',1345)]
for t,x in headers:text(x,304,t,20,'#667167')
for i,row in enumerate(table):
    y=356+i*59
    if row['extension_mm']==800:svg.append(f'<rect x="890" y="{y-31}" width="720" height="47" fill="#ecefe5"/>')
    text(925,y,str(row['extension_mm'])+' mm',23)
    text(1150,y,str(row['foot_clearance_mm'])+' mm',23)
    text(1380,y,str(row['private_sidewall_span_mm'])+' mm',23)
if not angled:
    text(890,546,'图中示例：延长800，侧墙净段仅约680。',21)
    text(890,583,'860宽门洞试排会跨过旧卧室边界约230。',21)
    text(890,620,'门框、门垛和公共通道须一起调整，不能硬塞。',20,'#9a6654')
else:
    text(890,546,'沿入门侧借约700，斜边可研究到约976。',21)
    text(890,583,'试排860门洞；成品净宽还要扣门框与门扇。',21)
    text(890,620,'门扇动作、隔墙节点和入口活动区仍需一起核对。',20,'#9a6654')
text(890,700,'② 2米床＋左侧衣柜，更接近单侧上下床',23)
text(890,740,'3467 − 600柜深 − 2150床宽 = 717 mm。',21)
text(890,779,'床若贴右墙，右侧净空为0；两位成人使用不理想。',20,'#667167')
text(890,818,'若要双侧通行，需要改衣柜位置或缩短柜段。',20,'#667167')
text(890,908,'卫浴序列可以这样组织',25)
text(890,950,'洗手台放入口段，马桶居中，尽端以玻璃分出淋浴。',20)
text(890,989,'马桶与淋浴尽量留在原卫浴范围；不设浴缸。',20)
text(890,1028,'图中洁具位置仅为包络试排，未认定可移排水。',20,'#667167')
text(890,1118,'新增段进入原卧室，能否作为卫浴须先核原批准图。',20,'#946849')
text(890,1157,'下层用途、原结构及防水范围未核，不能当施工方案。',20,'#946849')
text(60,1236,'* 所有尺寸为现有模型与试排值。主卫宽度与原图2040相关标注仍有冲突；弧墙、门窗及洁具系统需按实测深化。',20,'#667167')
text(60,1279,'如只使用上方灰框而不合并原主卫，图示新增小段不足以容纳“台盆—马桶—独立淋浴”完整序列。',20,'#667167')
text(60,1322,'本图为独立设计研究；正式v10主模型、公共区最新家具位置均未改动。',20,'#667167')
svg.append('</g></svg>')
target=OUT/('主卧主卫-斜角入口备选.svg' if angled else '主卧主卫-布局核对.svg');target.write_text(''.join(svg),encoding='utf-8')
assert hashlib.sha256(model.read_bytes()).hexdigest()==base_hash and active==(ROOT/'06_blender/active-model.json').read_bytes()
print('MASTER_SUITE_STUDY_READY',str(target))
