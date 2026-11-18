from pathlib import Path
from html import escape
from html.parser import HTMLParser
import hashlib, json, struct, xml.etree.ElementTree as ET

OUT = Path(__file__).parent
ROOT = OUT.parent.parent
schemes = [
    dict(id='A', title='胡桃木框景 · 浅木餐面',
         form='以胡桃木框住操作壁龛和夹层薄柜，浅木餐面从框景下方伸出；右端细框玻璃柜收住立面。',
         finish='暖白哑光上、下柜＋胡桃木中段＋浅橡木餐面；绿、蓝只用于餐椅软包和小物。',
         fridge='冰箱上方不设储物门，研究同墙色百叶通风检修面；风路、开孔面积和侧距须按最终机型设计。',
         light='纸布感椭圆餐吊灯＋薄柜底工作灯＋玻璃柜内柔光。'),
    dict(id='B', title='圆弧端柜 · 石质餐岛',
         form='直线四段式柜体接圆弧展示端，浅石色餐面和椭圆支座形成雕塑感；不是另加一座大岛台。',
         finish='暖白上柜＋灰苔绿下柜和玻璃框＋胡桃木中段＋浅暖灰哑光石材餐面。',
         fridge='冰箱独立在客厅端，取消整个上方柜盒，顶部是开放的连续墙面；不保留被柜盒框出的黑色横洞。',
         light='克制的柔光餐吊灯＋薄柜底工作灯＋圆弧展示端柔光。'),
    dict(id='C', title='细木线框 · 半透展示',
         form='以连续木纹薄柜、细木餐面边和长向分缝统一柜桌；右端半透玻璃只露出少量深蓝背景。',
         finish='暖白门板＋棕灰胡桃木中段和细边＋浅木餐面＋窄铜色玻璃框；少量深蓝、绿色。',
         fridge='冰箱上方研究同墙色微孔通风检修面，不画成高位储物门；散热条件未选型验证。',
         light='细薄陶瓷/乳白玻璃餐吊灯＋薄柜底工作灯＋半透展示内光。'),
]
reference_features = [
    dict(file='ae7a83a2335cdb941f832e14710fbfd.jpg', title='图一：四段式结构',
         adopted='下柜、操作留空、夹层翻门薄柜、上柜都保留；右端三横抽。',
         adapted='参考中的高度、深度不直接抄数值，改成适合本案的880台面、600留空、250薄柜。'),
    dict(file='b3bec9257e67a128c2de5a02b6679c2.jpg', title='图二：深度层次与玻璃门',
         adopted='上柜350、下柜450，薄柜220；保留局部玻璃展示和隐藏电源的思路。',
         adapted='电源位置按最终小电器确定；薄柜翻门在上柜下方开启，限位、五金和净空需做节点验证。'),
    dict(file='2ea8021416ab025ed07355ded1dabe9.jpg', title='图三：抽屉与免拉手',
         adopted='右端700宽三横抽；中部深木色、门板浅色；下柜斜切拉手，上柜下口留手位。',
         adapted='不增加400×800凳子车库：用户已取消卡座，并要求四椅及L形餐面，此处不挤占抽屉和活动区。'),
]
sources = [
    ('Norm / Reform PROFILE', 'https://www.reformcph.com/us/kitchens/collections/profile-norm-architects', '连续线条、克制分缝和木材质感。'),
    ('Cesar Tangram', 'https://www.cesar.it/it/collezioni/cucine/tangram/', '圆弧和直线柜体连接成整体的形式。'),
    ('Cosentino 餐台连接案例', 'https://www.cosentino.com/inspiration/projects/a-perfectly-crafted-dining-table-integration/', '高低两种台面在连接处形成家具整体。'),
    ('Kesseböhmer iMove', 'https://www.kesseboehmer.com/en/storage-solutions/kitchen/wall-units/imove', '餐边上柜下拉取物的机构原理；不等于已选定该五金。'),
    ('Häfele iMove 规格实例', 'https://hafelehome.com.my/products/imove', '600/900门宽模块的净宽初查；实际深度、运动轨迹和载荷仍需按安装图核对。'),
    ('普通冰箱安装限制实例', 'https://media3.bosch-home.com/Documents/8001142358_B.pdf', '证明普通冰箱不能任意封死散热空间；具体以最终机型为准，不把实例当通用标准。'),
]

# Deterministic front elevation. Images show finish intent; this drawing carries the stage dimensions.
svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1500 1120">',
       '<rect width="1500" height="1120" fill="#faf9f5"/>',
       '<style>text{font-family:Microsoft YaHei,Arial,sans-serif;fill:#344235}.s{font-size:21px}.m{font-size:25px}</style>',
       '<text x="45" y="48" font-size="32">三套共用的四段式结构｜单位 mm</text>',
       '<text x="45" y="84" class="s">层高2750、墙长3545仍为模型暂拟值；不是加工图。</text>']
scale=.29; ox=80; oy=930
def box(x,z,w,h,col,stroke='#7f897c'):
    svg.append(f'<rect x="{ox+x*scale}" y="{oy-(z+h)*scale}" width="{w*scale}" height="{h*scale}" fill="{col}" stroke="{stroke}" stroke-width="1.5"/>')
def label(x,z,txt,size=22):
    svg.append(f'<text x="{ox+x*scale}" y="{oy-z*scale}" font-size="{size}">{escape(txt)}</text>')
box(140,0,920,1850,'#87918b');label(290,950,'冰箱',26)
label(95,2120,'上方非日常储物',19);label(110,1990,'通风构造另核',19)
box(1200,80,2200,780,'#eeebe3');box(1200,860,2200,20,'#d2b68c')
box(1200,880,1500,600,'#c6aa89')
box(1200,1480,1500,250,'#805f48')
box(1200,1730,1500,970,'#f1eee6')
box(1200,2700,2200,50,'#d8d7ce')
box(2700,880,700,1320,'#bdc8ba');box(2700,2200,700,500,'#f1eee6')
for z in (1140,1470,1800): box(2700,z,700,18,'#977c5e')
for z in (340,600): box(2700,z,700,3,'#8a8172')
box(1800,1480,4,250,'#5f4838');box(1800,1730,4,970,'#b1b0a5')
box(1650,720,750,30,'#d2b68c');box(1650,80,750,640,'#e0d2bf')
for z,txt in [(2210,'① 上柜 970'),(1600,'② 薄柜 250'),(1170,'③ 留空 600'),(410,'④ 下柜至台面 880')]:
    label(3460,z,txt,23)
label(2800,1510,'玻璃',20);label(2770,1340,'展示门',20)
label(2770,440,'三横抽',20)
label(1650,530,'餐面连接段',18)
svg += ['<text x="85" y="983" class="m">冰箱区1200</text><text x="475" y="983" class="m">餐边柜2200（主操作段1500＋展示端700）</text>',
        '<text x="85" y="1025" class="s">深度：下柜450 ／ 上柜350 ／ 薄柜220；收顶50；操作台880与餐面750高低连接。</text>',
        '<text x="85" y="1065" class="s">冰箱上方开放或通风检修面为候选做法；不能用实心板封死散热空间。</text></svg>']
(OUT/'四段式功能立面.svg').write_text('\n'.join(svg),encoding='utf-8')

# Independent plan, wall direction horizontal: living end left, kitchen end right.
plan=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1500 1320">',
      '<rect width="1500" height="1320" fill="#faf9f5"/><style>text{font-family:Microsoft YaHei,Arial,sans-serif;fill:#344235}</style>',
      '<text x="60" y="60" font-size="34">L餐面与四椅｜冰箱在客厅端、L形外侧</text>',
      '<text x="60" y="105" font-size="25">单位mm；上为柜墙，左通客厅，右通餐厨门。为独立试排，非主模型已移动。</text>']
ps=.32; px=120; py=180
def pr(x,y,w,d,col,stroke='#7e8d74',dash=''):
    plan.append(f'<rect x="{px+(x+72.5)*ps}" y="{py+y*ps}" width="{w*ps}" height="{d*ps}" fill="{col}" stroke="{stroke}" stroke-width="2"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
def pt(x,y,txt,size=25):
    plan.append(f'<text x="{px+(x+72.5)*ps}" y="{py+y*ps}" font-size="{size}">{escape(txt)}</text>')
pr(-72.5,-60,3545,60,'#8b9582');pr(-72.5,0,3545,3082,'#fffefa')
pr(-72.5,2682,3545,400,'#e5dac5');pr(-72.5,1700,3545,982,'#e0eada')
pr(0,0,1200,800,'#a4afaa');pr(140,50,920,750,'#7f8c86')
pr(1200,0,2200,450,'#e5dac5');pr(1200,0,2200,350,'none','#738795','7 6')
pr(1650,300,750,1400,'#cdb18c');pr(1650,300,750,150,'#b4936f')
for xx,sgn in [(1350,-1),(2250,1)]:
    for yy,col in [(450,'#b0c4a4'),(1250,'#a4b8c4')]:
        pr(xx,yy,450,450,col);pr(xx+250*sgn,yy,450,450,'none','#b47e62','7 6');pt(xx+70,yy+275,'椅',21)
pt(180,330,'冰箱');pt(150,450,'L形外',23);pt(2600,270,'餐边柜')
pt(1750,1060,'L餐面');pt(1735,1180,'1400×750',22)
pt(600,2250,'连续绕行约982',29);pt(50,2940,'对侧现有通长柜／换鞋段深400',25)
dx=px+3545*ps
plan.append(f'<path d="M{dx} {py}V{py+1691*ps}" stroke="#89aebd" stroke-width="9"/>')
plan.append(f'<text transform="translate({dx+40},{py+130}) rotate(90)" font-size="23">餐厨门组1691，实际净开口另核</text>')
plan += ['<text x="60" y="1210" font-size="25">实色：坐姿占位、前150进入桌下；棕虚线：椅子向外拉250后的包络。</text>',
         '<text x="60" y="1250" font-size="25">餐厨端椅后：坐姿约772.5，拉椅后约522.5；后者仍局促。</text>',
         '<text x="60" y="1290" font-size="25">冰箱开门、真实椅型、柜门与通行需在选型和现场尺寸确定后复核。</text></svg>']
(OUT/'L餐岛位置与净空.svg').write_text('\n'.join(plan),encoding='utf-8')

refcards = ''.join(f'<article><a href="references/{r["file"]}"><img src="references/{r["file"]}" alt="{r["title"]}"></a><h3>{r["title"]}</h3><p><b>落实：</b>{r["adopted"]}</p><p><b>调整：</b>{r["adapted"]}</p></article>' for r in reference_features)
cards = ''.join(f'''<section class="card" id="{s['id']}"><p class="tag">方案 {s['id']} · 待选</p><h2>{s['title']}</h2><p>{s['form']}</p>
<a href="{s['id']}-开关灯对照.png"><img src="{s['id']}-开关灯对照.png" alt="方案{s['id']}：左全关灯，右全开灯"></a>
<p class="caption">左：人工灯全关；右：人工灯全开。日光保留，柜体与桌椅相同。概念表现不代替尺寸立面。</p>
<table><tr><th>材质</th><td>{s['finish']}</td></tr><tr><th>灯光</th><td>{s['light']}</td></tr><tr><th>冰箱上方</th><td>{s['fridge']}</td></tr></table></section>''' for s in schemes)
refhtml=''.join(f'<li><a href="{u}">{t}</a>：{d}</li>' for t,u,d in sources)
page='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>四段式餐边柜与L餐岛｜三套独立修订</title><style>
*{box-sizing:border-box}body{margin:0;background:#f5f4ef;color:#2f3b32;font:16px/1.8 "Microsoft YaHei",system-ui,sans-serif}main{max-width:1240px;margin:auto;padding:34px 26px}h1{font-size:clamp(28px,4vw,43px);line-height:1.35}h2{font-size:27px}h3{font-size:19px}.card{background:#fffef9;border:1px solid #dce1d6;border-radius:14px;padding:24px;margin:26px 0}img{display:block;width:100%;height:auto;border-radius:6px}a{color:#4d6b50;text-underline-offset:4px}.tag,.caption{font-size:13px;color:#71816d}.note{padding:18px 22px;background:#e9ede3;border-left:4px solid #8a9e7c}.warn{background:#f3eadf;border-color:#b88d68}nav{display:flex;gap:12px;flex-wrap:wrap;margin:24px 0}nav a{border:1px solid #c7d3bf;border-radius:22px;padding:7px 17px;text-decoration:none}.refs{display:grid;grid-template-columns:repeat(3,1fr);gap:22px}.refs img{height:260px;object-fit:contain;background:#eeeee8}.refs p{font-size:14px}table{width:100%;border-collapse:collapse;margin:18px 0}th,td{border-bottom:1px solid #e4e7dd;text-align:left;padding:11px;vertical-align:top}th{width:155px;color:#6e7c65;font-weight:500}.plan svg{width:100%;height:auto}summary{cursor:pointer;color:#4d6b50}li{margin:9px 0}footer{font-size:13px;color:#7c8675}@media(max-width:640px){main{padding:20px 12px}.card{padding:16px}.refs{grid-template-columns:1fr}.refs img{height:240px}th,td{display:block;width:100%;padding:6px 0}th{border:0}}</style></head><body><main>
<p class="tag">INDEPENDENT STUDY · 04 · 2026.11.05</p><h1>恢复参考中的四段式，<br>让餐边柜与L餐面成为整体</h1>
<div class="note"><b>本轮先纠正遗漏：</b>三张参考中的夹层薄柜、四段式、三横抽、局部玻璃门、上浅下深和免拉手都进入共同设计条件。冰箱仍在客厅端、L形外；餐面从其右侧接出。三套均未选定，主模型v19、家具位置与VR未修改，也未启动v20。</div>
<nav><a href="#references">三图如何落实</a><a href="#A">A 胡桃木框景</a><a href="#B">B 圆弧石岛</a><a href="#C">C 细木半透</a><a href="#dimensions">参数与净空</a></nav>
<section class="card" id="references"><h2>你给的三张图，分别落实在哪里</h2><div class="refs">'''+refcards+'''</div><p>没有照搬参考视频的所有数字和房间。保留构造语言，同时满足本案四椅、L连接和冰箱端位。</p><img src="四段式功能立面.svg" alt="四段式参数立面"></section>
'''+cards+'''
<section class="card" id="dimensions"><h2>共同设计参数</h2><p>单位mm。墙长3545、净高2750是模型暂拟；组合宽3400＝冰箱区1200＋真正餐边柜2200，待现场量尺及机型确认。</p>
<table><tr><th>四段式主操作段</th><td>宽1500：台面高880；操作区净高600；夹层薄柜高250、离地1480–1730；上柜高970、离地1730–2700；顶收口50。</td></tr><tr><th>三个进深</th><td>下柜450，上柜350，薄柜220。三段深度形成层次；板厚、背板和五金另扣，不把外深当作内部净深。</td></tr><tr><th>展示及抽屉</th><td>右端700宽局部玻璃展示，下方三横抽。左端450柜与右端700三抽是可独立使用的下柜收纳；中间750连接和邻椅300固定侧段不计作活动储物。</td></tr><tr><th>L形餐面</th><td>1400×750×高750，面厚30，桌下约720；后部150插接固定柜段，超出450深柜面1250。880操作台与750餐面差130；圆角先按R60研究，承重和桌腿位置需节点深化。</td></tr><tr><th>四把餐椅</th><td>两长边各二，不设端头椅和吧椅。座高约440–460建议范围；示意坐姿以前150进入桌下试算。</td></tr><tr><th>常规双开门冰箱</th><td>先以920×750×1850占位，非已选型号。门体略突出柜侧，开门和抽屉轨迹另核。上方不计日常收纳；通风面并非密封封板。</td></tr><tr><th>较高的上柜</th><td>600＋900两个模块研究下拉取物五金，下拉净深、轨迹、载荷和门板需用选定安装图验证；最高处仅低频储物，不声称所有层板都能徒手够到。冰箱上方不生搬下拉机构。</td></tr><tr><th>薄柜翻门</th><td>两扇600＋900模块。翻起净空、限位和灯槽一起校核，避免抬门碰上方前凸上柜；概念图中的闭门外观不代表五金已验证。</td></tr><tr><th>灯光与电源</th><td>工作、展示、餐吊灯三组分控，3000K、Ra≥90为选型目标，可调光。工作灯藏于薄柜底铝槽加扩散罩；驱动器留检修。电源按最终小电器位置，不裸露长条插线板。</td></tr></table>
<div class="note warn">静态关系：桌端与对侧400深柜之间连续绕行约982。餐厨端椅后坐姿约772.5；再拉椅250后约522.5，仍局促。四人坐、拉椅、冰箱开门及餐厨通行不能仅凭效果图认定都宽松。</div>
<details><summary>展开平面与活动包络</summary><img src="L餐岛位置与净空.svg" alt="L餐面四椅和活动净空"></details>
<p class="caption">这是独立叠加研究，不表示主模型里的餐桌已经移动或餐边柜已经安装。</p></section>
<section class="card"><h2>在线参考补充的是设计语言</h2><ul>'''+refhtml+'''</ul><p>原三图是构造主线，在线参考补充圆弧、框景、材质连接和分缝处理；没有用网图替换用户指定功能。</p>
<p><a href="design-parameters.json">完整参数</a> · <a href="generation-prompts.json">实际出图提示词与参考输入</a> · <a href="四段式餐边柜-L独立提案.blend">独立关系草模</a> · <a href="四段式餐边柜-L关系草模.png">关系草模图</a></p></section>
<footer>图片为内置imagegen设计表现，局部分缝、材质微细节及比例可能偏移；尺寸立面和关系草模为本次设计参数依据。均为待选方案，未融合主模型。01旧方案、02低柜方向和03缺少薄柜的中间稿已被本轮取代。</footer></main></body></html>'''
(OUT/'四段式餐边柜三套修订.html').write_text(page,encoding='utf-8')
spec=json.loads((OUT/'design-parameters.json').read_text(encoding='utf-8'))
spec.update({'reference_features':reference_features,'schemes':schemes,'online_references':[{'title':t,'url':u,'take':d} for t,u,d in sources],
             'fittings_status':'concept only: upper pull-down and thin flap travel need selected hardware drawings',
             'corner_radius_provisional':60,'tool':'built-in imagegen, separate geometry anchor','main_model_modified':False,'v20_started':False})
(OUT/'design-parameters.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'html':str(OUT/'四段式餐边柜三套修订.html'),'schemes':len(schemes),'reference_features':len(reference_features)},ensure_ascii=False))
