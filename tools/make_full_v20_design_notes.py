from pathlib import Path
import json,math,html
R=Path('D:/AI-Yang.cn/HomeDesign');OUT=R/'09_delivery/v20-complete';OUT.mkdir(exist_ok=True)
d=json.loads((R/'02_geometry/geometry-master-v20-complete.json').read_text(encoding='utf8'));q=d['features']['fullImplementationV20']
def svg_start(w,h,title):return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{title}"><style>text{{font-family:Microsoft YaHei,sans-serif;fill:#354139}}.note{{font-size:14px}}.dim{{font-size:16px}}.title{{font-size:22px}}.wall{{fill:#a4aaa2}}.thin{{stroke:#737f74;fill:none;stroke-width:1.2}}.accent{{stroke:#66826d;fill:none;stroke-width:2}}</style><rect width="100%" height="100%" fill="#fafaf5"/>'
def label(x,y,text,cls='dim'):return f'<text x="{x}" y="{y}" class="{cls}">{html.escape(str(text))}</text>'
def poly(points,fill='#afb4aa',stroke='none',sw=1):return '<polygon points="'+' '.join(f'{x:.2f},{z:.2f}' for x,z in points)+f'" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
def planp(p):return [(p['x']+x,p['z']+z) for x,z in p['planProfileLocalMm']] if p.get('planProfileLocalMm') else [(p['x'],p['z']),(p['x']+p['w'],p['z']),(p['x']+p['w'],p['z']+p['d']),(p['x'],p['z']+p['d'])]

# Reflected ceiling coordination plan: positions come from the same master JSON.
sc=.061;ox=65;oz=70;pts=lambda pp:[(ox+x*sc,oz+z*sc) for x,z in pp]
s=svg_start(1050,930,'v20全屋顶面及中央空调协调设计');s+=label(40,35,'v20 顶面与空调协调｜上南下北','title')
s+=poly(pts(d['floor']),'#f0f0e8','#9fa99d')
for w in d['walls']:
    if w['y']<1200:s+=poly(pts(planp(w)),'#b1b8af')
for x,z,w,dep,name in [(3500,4900,4500,1000,'公共设备带'),(6050,5170,1300,650,'可拆检修面')]:
    s+=f'<rect x="{ox+x*sc}" y="{oz+z*sc}" width="{w*sc}" height="{dep*sc}" fill="#e4eadf" stroke="#66826d" stroke-dasharray="4 3"/>'
    s+=label(ox+x*sc+5,oz+z*sc+22,name,'note')
for p in d['ceilingParts']:
    if any(k in p['id'] for k in ['supply-recess','return-recess']) or p['id'].endswith('supply-face') or p['id'].endswith('return-face'):
        s+=poly(pts(planp(p)),'#536c5d')
for x,z,text in [(2000,2800,'客厅／阳台 · 完成面2750'),(8150,2500,'主卧 · 暂定2750'),(5350,7900,'客卧'),(8500,8200,'次卧'),(1000,8000,'餐厅'),(1200,11300,'厨房')]:s+=label(ox+x*sc,oz+z*sc,text,'note')
tx=770;s+=label(tx,125,'机电协调暂拟','title')
for i,t in enumerate(['连续顶面：2750 mm','公共设备带：2600 mm','公共送风面：2000 × 60','回风面：1700 × 100','检修面：1300 × 650','设备轮廓：1200 × 550 × 230','仅作可拆装空间占位','私区给出送回风候选位置','梁底、机型、负荷、凝水未定','不将封闭空腔计作收纳']):s+=label(tx,170+i*36,t,'note')
s+=label(40,888,'公共区灯光分回路：窗帘槽／柜内／办公／餐吊灯／功能补光；3000 K氛围、3500 K任务为设计目标。','note')+'</svg>'
(OUT/'顶面空调协调.svg').write_text(s,encoding='utf8')

# Master suite plan: both leaf poses, original bed position and new alignment line.
s=svg_start(1100,770,'主卫墙线对齐与双折门方案');s+=label(35,36,'主卫墙线对齐｜保留床位，斜向内折门','title')
origin=(7100,3300);scale=.175
def bp(points):return [(45+(x-origin[0])*scale,70+(z-origin[1])*scale) for x,z in points]
for w in d['walls']:
    if w['y']<1200 and w['x']+w['w']>7100 and w['z']+w['d']>3300 and w['z']<7100:s+=poly(bp(planp(w)),'#a8afa5')
for gid,color in [('master-bed','#b3c5ae'),('master-vanity','#d5c5aa'),('master-toilet','#e9e7df')]:
    p=next(q for q in d['furnitureObjects'] if q['id']==gid);s+=poly(bp(planp(p)),color,'#899387')
for p in [x for x in d['bathParts'] if 'bifoldPanel' in x]:
    s+=poly(bp(planp(p)),'#627d6b')
    pose={**p,**p['openPlan']};s+=poly(bp(planp(pose)),'#adbeca','#5d7484')
line=bp([(7188,4896),(9323,4896)]);s+=f'<path d="M {line[0][0]} {line[0][1]} L {line[1][0]} {line[1][1]}" stroke="#ba8e67" stroke-width="2" stroke-dasharray="5 4"/>'
cx,cz=bp([(8480,4400)])[0];s+=f'<circle cx="{cx}" cy="{cz}" r="{250*scale}" fill="none" stroke="#66826d" stroke-dasharray="4 3"/>'
for x,z,t in [(7400,3700,'书柜墙基准'),(9400,3500,'2 m床 · 原位'),(10350,4600,'洗手台'),(9470,5530,'马桶'),(9550,6510,'淋浴'),(7700,5200,'收回200 · 模型差值'),(7900,4500,'Ø500站位试排')]:
    xx,zz=bp([(x,z)])[0];s+=label(xx,zz,t,'note')
for i,t in enumerate(['墙面基准：z4896 mm，前后齐平','原直门的空间不足，采用斜向双折门提案','毛洞860；两扇各约406；厚40；竖边R20','净开口暂拟735，实际按门系统核定','绿色：关闭；灰蓝：折叠开启','61个动作采样，7个原生驱动姿态回读','未移动床、衣柜、台盆和马桶','原湿区、排水、结构及门密封继续待核']):s+=label(750,130+i*45,t,'note')
s+='</svg>';(OUT/'主卫门墙对齐.svg').write_text(s,encoding='utf8')

# Build-up detail plate, intentionally dimensioned as design nodes rather than shop drawings.
s=svg_start(1100,650,'门墙同面与极窄收口节点设计');s+=label(35,38,'门墙与收口｜实体节点的设计口径','title')
s+=label(45,95,'同面门横剖（示意）','dim')
s+='<rect x="45" y="160" width="300" height="150" fill="#d7dacd"/><rect x="45" y="145" width="300" height="16" fill="#f0efe7"/><rect x="360" y="145" width="300" height="50" fill="#ecebe3"/>'
s+='<rect x="337" y="179" width="15" height="90" fill="#788175"/><rect x="315" y="185" width="22" height="80" fill="#c5ae89"/><path d="M45 145H660" class="accent"/>'
for x,y,t in [(55,345,'墙饰面与门外表面同平面'),(55,380,'门厚40 · 可见周边缝4'),(55,415,'隐框退入完成面12.5以内'),(55,450,'18基层／12×30框截面为节点提案')]:s+=label(x,y,t,'note')
s+=label(750,95,'隐藏踢脚竖剖','dim')
s+='<path d="M750 140H850V410H860V430H858V530H750Z" fill="#d7dacd"/><rect x="850" y="410" width="10" height="20" fill="#6b7769"/><path d="M720 530H940" class="thin"/>'
for i,t in enumerate(['上方墙面齐平','4 mm影缝','58 mm内退踢脚','凹入8 mm','转角顺接，不贴凸出压条']):s+=label(885,170+i*66,t,'note')
s+=label(45,580,'圆弧层级：桌及餐柜R70–100；局部墙角R60–80；立柜固定端R40–50；可触门边约R2。','note')
s+=label(45,612,'节点随选定材料系统、墙顶公差与门五金深化；实体表达不等于结构开槽或施工认证。','note')+'</svg>'
(OUT/'门墙收口节点.svg').write_text(s,encoding='utf8')

summary='''# v20 实装完整版

启动依据：业主2026-11-06明确“实装v20”。完整模型另存为`06_blender/home-main-v20-complete.blend`，此前v20整合版和全部独立研究保留。

| 原待办 | 已加入模型的内容 | 保留的待核条件 |
|---|---|---|
| 吊顶／空调 | 全屋2750暂定完成面，公共2600设备带、送回风面与可拆检修面；私区候选风口／设备空间 | 结构／梁底、机型、负荷、风量静压及凝水；没有假定现场机型已选 |
| 门墙／收口 | 三处同面门的隐框、基层及4周缝；局部58踢脚＋4影缝／8内退；门边触边柔化 | 具体门系统与材料收口公差；未推断结构可开槽 |
| 收纳 | 走廊柜、鞋柜、书柜的填充代理改为空腔、分格、可调层板与五金意向；餐柜抽盒／薄柜内部补齐 | 物品数量尚未确定；固定圆端、后部服务空腔与机电占位不算储物 |
| 圆弧 | 走廊柜固定端R50、鞋柜外端R40、外露墙端R60、门边小圆角；原餐柜R100保留 | 封边和门五金的实际工艺 |
| 地毯／洗烘 | 3600×3000×8低绒地毯；开放洗烘高柜／上柜下拉；帘右止点6428，与新柜侧隔40 | 机型散热、叠放件、供排水、帘实际扫动与维护路径 |
| 主卫 | 走廊面从5096收至4896，与书柜墙线对齐；860斜向双折门提案，床及洁具原位；台盆—马桶—淋浴保留 | 门系统／密封和业主偏好、扩湿区与排水条件。门提案可逆，不伪称业主已选 |
| 实体／表现 | 同版完整模型、可移动视图、四区摄影概念与四点全景；原生图作为几何基准 | AI织物、木纹、光影及窗景为概念，不是测量或照明计算 |

## 家具与材质

原26个家具整组的原点及朝向保持，新增地毯和洗烘高柜，共28组。沙发、茶几、脚凳、书桌和椅子未执行旧200试移。餐椅继续暂不摆。办公B胡桃木为临时预览，A/C候选不叠放。新柜随鼠标可看尺寸，100 mm步进；洗烘柜与两机联动。

暖白和浅橡木主导；胡桃用于U餐岛／置物带与办公压顶，奶黄只留走廊下柜，绿色与深蓝留给少量织物和小物。电视墙继续留白。全屋柜体不强行统一一款。

## 收纳口径

- 走廊柜：六模块；五组可调格＋高位清洁格。主储物层板有效深约332；首模块高处双层下拉为设计意向。
- 鞋柜：双仓，净宽约608.5／558.5、层板有效深304；下方五层可调，柜顶零开放缝。右端50固定R40封板不计储物。
- 书柜：开放格和北端平移门关系保留；封闭部分改为空腔／可调层板。椅后408局部紧凑仍在。
- 餐边柜：四段式、全宽开放置物、完整上柜双层下拉、三横抽保留。三抽内部暂拟约526×534×148；柜深800中的后部封闭空腔不虚算容量。
- 洗烘柜：外包约668×720×2750，设备正面开放；上柜实际储物深约314，两个下拉托盘。底部不另加密闭地台，设备后方和上后方留通风／检修关系。

收纳格数是可调整设计，不等于业主已确定物品清单；没有用某个鞋数或书数冒充容量验收。

## 灯光与顶面

客厅无中心主灯。窗帘槽、书柜、入口随手位、办公台灯和压顶、餐边置物带、餐吊灯、功能补光分回路；保留白天／氛围／用餐／清洁／观影五场景。氛围目标3000 K、工作目标3500 K。餐灯暂底1500、距880台面620。以上是设计目标，不是实测照度或灯具采购参数。

公共检修面1300×650与候选机身轮廓分开保存，机身为不渲染的协调线框。柜体到顶区避开公共低设备带。顶面协调图给出私区候选设备关系，未扩展厨房／卧室家具装修。

## 核对与使用边界

主卫门61个解析中间姿态及7个原生驱动姿态匹配，代理门板、墙体及床／洁具间未检出重叠；含一个直径500的站位试排。这个结果不等于真实门五金、防夹、隔音、防水或无障碍认证。门机制仅参考内折系统的基本组织，未选产品。

系统原理参考：[Häfele Roomflex 官方资料](https://files.hafele.co.uk/catalogfiles/www/16a9-151.pdf)。本项目的860洞口、40厚门、R20竖边及行程均为自有几何提案，未套用为该品牌的安装参数。

完整模型与去顶／低墙观察图分开保存。移动后的布局需要重新烘焙全景。100 mm是移动步长，户型精度仍取决于现场核对。
'''
(OUT/'实装说明.md').write_text(summary,encoding='utf8')
params=dict(phase='full-v20-design',storage=q['storage'],workingDrawingStatus='design nodes and coordination, not certified shop drawings',palette=['clean warm white','pale oak','limited walnut','milk-yellow corridor lower','sage and navy accents'])
(OUT/'交付参数摘要.json').write_text(json.dumps(params,ensure_ascii=False,indent=2),encoding='utf8')
print('V20_FULL_DESIGN_NOTES_READY')
