from pathlib import Path
import json,html

ROOT=Path('D:/AI-Yang.cn/HomeDesign')
OUT=ROOT/'09_delivery/office-study-02'
def save(name,data):
 (OUT/name).write_text(data,encoding='utf-8')

p=json.loads((OUT/'设计参数.json').read_text(encoding='utf-8'))
for v in p['variants']:
 if v['id']=='A':v.update(support='slim pale-oak ledge and desktop supports; full near-end warm-white halfwall',storage='near-end shallow oak desktop drawer retained; no balcony-end cabinet')
 if v['id']=='B':v.update(accent='sage textile chair and navy task lamp',support='walnut ledge and desktop supports; full near-end warm-white halfwall',storage='no new end cabinet or drawer; right bookcase retained')
 if v['id']=='C':v.update(support='ivory ledge supports and concealed desktop frame; full near-end warm-white halfwall',storage='near-end shallow navy desktop drawer retained; no balcony-end cabinet')
p['common']['commonLighting']['independentCircuits']=['long ledge and near halfwall concealed light','adjustable task lamp','existing ambient/cove']
p['common']['commonLighting']['noFarEndStrip']=True
save('设计参数.json',json.dumps(p,ensure_ascii=False,indent=2))

svg=['''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 1030" role="img" aria-labelledby="title desc"><title id="title">办公区近端半墙与阳台端入口</title><desc id="desc">图上为阳台端，完全敞开；图下为实体半墙，延伸到右书柜。尺寸为设计提案，毫米。</desc><defs><marker id="arr" markerWidth="7" markerHeight="7" refX="3.5" refY="3.5" orient="auto-start-reverse"><path d="M0,0 L7,3.5 L0,7" fill="none" stroke="#53685e"/></marker><marker id="entry" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#448b76"/></marker></defs><style>text{font-family:'Microsoft YaHei','Noto Sans CJK SC',sans-serif;fill:#243b32}.note{font-size:17px;fill:#61766a}.dim{stroke:#53685e;stroke-width:1.2;marker-start:url(#arr);marker-end:url(#arr)}.guide{stroke:#9fafa4;stroke-dasharray:5 5;fill:none}</style><rect width="1440" height="1030" fill="#f8f8f1"/><text x="48" y="55" font-size="30" font-weight="700">近端半墙接书柜，阳台端进入</text><text x="48" y="90" class="note">本轮纠正：红框做实体半墙；蓝框内家具横杆／端柜取消。上南、下北、左东、右西。</text>''']
S=.16
def X(x):return 52+(x-3000)*S
def Y(z):return 195+(z-1100)*S
def rect(x,z,w,d,color,r=4,stroke='none'):
 svg.append(f'<rect x="{X(x):.2f}" y="{Y(z):.2f}" width="{w*S:.2f}" height="{d*S:.2f}" rx="{r}" fill="{color}" stroke="{stroke}"/>')
def txt(x,z,t,size=17,anchor='start',fill=None):
 svg.append(f'<text x="{X(x):.2f}" y="{Y(z):.2f}" font-size="{size}" text-anchor="{anchor}"'+(f' style="fill:{fill}"' if fill else '')+f'>{html.escape(t)}</text>')
def dim(x1,z1,x2,z2,label,vertical=False):
 a,b,c,d=X(x1),Y(z1),X(x2),Y(z2)
 svg.append(f'<path class="dim" d="M{a},{b} L{c},{d}"/>')
 if vertical:svg.append(f'<text x="{a-12}" y="{(b+d)/2}" font-size="16" text-anchor="middle" transform="rotate(-90 {a-12} {(b+d)/2})">{label}</text>')
 else:svg.append(f'<text x="{(a+c)/2}" y="{b-12}" font-size="16" text-anchor="middle">{label}</text>')
rect(3100,1400,1900,3000,'#e7e4da',12)
rect(4750,1400,250,3000,'#d3d3c7',10)
txt(3570,3020,'现有贵妃沙发',22)
txt(3570,3220,'背高850',16)
rect(5100,2000,200,2400,'#725642',8)
rect(5300,2000,700,2400,'#d5bd97',10)
txt(5660,3580,'办公桌',18,'middle')
txt(5660,3750,'H750',16,'middle')
rect(5380,2195,87,810,'#283741',2)
txt(5520,2100,'34寸 ×1',15)
rect(5870,2320,560,560,'#9eae96',12)
txt(6150,2640,'椅',18,'middle')
rect(6838,1176,350,3600,'#d8dfd4',2)
txt(7010,3350,'书柜',17,'middle')
rect(6838,3976,350,800,'#b8c8bd',2)
rect(5100,4440,1735,120,'#a25040',1)
rect(5100,4400,1735,200,'none',5,'#a25040')
txt(5920,4830,'实体半墙接至右书柜',19,'middle','#a25040')
svg.append(f'<path d="M{X(6400)},{Y(1700)} V{Y(2200)}" stroke="#448b76" stroke-width="5" marker-end="url(#entry)"/>')
txt(6170,1500,'阳台端进入',19,'middle','#448b76')
txt(6000,1800,'无横台／栏杆／端柜',16,'middle','#448b76')
dim(5050,2000,5050,4400,'长高台2400',True)
dim(5100,5060,6835,5060,'半墙压顶长1735')
dim(5300,4220,6000,4220,'桌深700')
dim(6430,3060,6838,3060,'408')
txt(6050,3320,'椅后局部仍紧',15)
txt(3510,5270,'图左方向是电视；所有桌椅、沙发、书柜坐标沿用v19',17)
svg.append('''<path d="M825,155 V940" stroke="#d7ded4"/><text x="880" y="185" font-size="23" font-weight="700">近端半墙立面关系</text><rect x="888" y="355" width="350" height="200" fill="#edece2" stroke="#d5d7cc"/><rect x="880" y="340" width="367" height="15" rx="5" fill="#725642"/><rect x="1248" y="236" width="84" height="319" fill="#d8dfd4"/><text x="1290" y="221" class="note" text-anchor="middle">右书柜</text><path d="M870,555 H1340" stroke="#61766a"/><path class="dim" d="M1358,340 V555"/><text x="1370" y="458" font-size="17">950</text><text x="895" y="385" font-size="18">暖白实心墙身 · 落地封闭</text><text x="895" y="420" class="note">墙身厚120；压顶深200</text><text x="895" y="455" class="note">压顶与沙发背高台同色、同高</text><text x="895" y="490" class="note">到书柜留3 mm饰面接缝</text><text x="880" y="605" font-size="21" font-weight="700">保留直线骨架，外露端柔化</text><text x="880" y="643" class="note">A 浅木：压顶30厚／R35</text><text x="880" y="676" class="note">B 胡桃：压顶45厚／R45</text><text x="880" y="709" class="note">C 奶油：压顶35厚／R80</text><text x="880" y="760" font-size="20" font-weight="700">相接书柜的开门协调</text><text x="880" y="797" class="note">北端800模块示意改为平移实门</text><text x="880" y="830" class="note">避免平开门扫过新增半墙</text><text x="880" y="863" class="note">独立模型1—40帧可查看滑移</text><text x="48" y="972" class="note">所有新增尺寸为设计师暂拟，非现场实测；椅后408不是舒适通行净宽，实际起身、后退与收纳动作仍需选型核对。</text><text x="48" y="1002" class="note">图中深木仅用于区分部件；三套具体材质见效果图。独立提案02，不融合主模型、不启动v20。</text></svg>''')
save('半墙与阳台入口尺寸.svg',''.join(svg).replace('图中深木仅用于区分部件；三套具体材质见效果图。','图中红色只标记半墙位置，非实际饰面；三套材质见效果图。'))

style='''*{box-sizing:border-box}body{margin:0;background:#f7f7f0;color:#273d33;font:16px/1.9 "Microsoft YaHei",sans-serif}main{max-width:1300px;margin:auto;padding:44px 28px 80px}header{border-bottom:1px solid #d2dacc;padding-bottom:25px}h1{font-size:36px;line-height:1.4;margin:8px 0 20px}h2{font-size:25px;margin:0 0 12px}h3{font-size:19px;margin:16px 0 6px}.eyebrow{letter-spacing:.12em;font-size:13px;color:#788a79}.lead{max-width:1000px;color:#647666}section{background:#fffef9;border:1px solid #dce2d4;border-radius:22px;padding:28px;margin-top:28px}img{display:block;width:100%;height:auto;border-radius:13px}.hint{font-size:14px;color:#728071}.links,.tags{display:flex;flex-wrap:wrap;gap:12px}.tags span{padding:2px 13px;border-radius:18px;background:#e7ede1;font-size:14px}.links{font-size:14px;margin-top:16px}a{color:#416e5b;text-underline-offset:4px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:28px}td,th{text-align:left;vertical-align:top;border-bottom:1px solid #e2e6d9;padding:11px}table{width:100%;border-collapse:collapse}summary{cursor:pointer;color:#54765e}details{margin-top:18px}.recommend{border-left:4px solid #8da07e;padding-left:17px}@media(max-width:700px){main{padding:24px 14px 60px}section{padding:20px 15px}.grid{grid-template-columns:1fr}h1{font-size:27px}table{font-size:13px}td,th{padding:8px 6px}}'''
page=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>办公区半墙与敞开端｜三套修正版</title><style>'+style+'</style><main><header><div class="eyebrow">HOME OFFICE / STUDY 02 · 2026.11.06</div><h1>半墙接书柜，从阳台端进入</h1><p class="lead">按最新批注修正三套办公区设计：近端补上落地实体半墙，一直接到右侧书柜；顶部与沙发背长高台统一。阳台端取消横向高台、家具栏杆和端柜，留作办公区入口。沿用三套材质方向，均未选定或融合主模型。</p><div class="tags"><span>近端实体半墙</span><span>阳台端敞开</span><span>桌高750／墙顶950</span><span>一屏一椅</span><span>主模型保留v19</span></div></header>']
cards=[
 ('A','浅木薄片','浅橡木长高台与压顶，厚30、R35；暖白实体半墙。浅木桌面与灰绿座椅延续自然基底，近端浅木抽屉保留。','三套中轮廓最轻，木色应选低黄度实样，避免与地板一起泛黄。'),
 ('B','深木框景','胡桃木长高台与压顶，厚45、R45；暖白实体半墙。浅木办公面保留，绿色在座椅、深蓝在台灯和软装中点到为止；原阳台端灰绿柜删除。','深木线条最明确，与既有暖白、浅木、绿蓝搭配最有层次。半墙墙身保持暖白，避免把办公区围成深木盒子。'),
 ('C','奶油圆弧','奶油白实体面材长高台与压顶，厚35、R80；暖白实体半墙，浅木桌面，近端深蓝浅抽保留。','整体最柔和，端头弧度更明显。白色台面与墙身应靠材质和细缝区分，不用更黄的色差制造层次。')
]
for vid,title,desc,review in cards:
 page.append(f'<section id="{vid}"><div class="eyebrow">OPTION {vid}</div><h2>{vid}｜{title}</h2><p>{desc}</p><a href="{vid}/{vid}-半墙修正-开关灯对照.png"><img src="{vid}/{vid}-半墙修正-开关灯对照.png" alt="{title}，左全关灯，右全开灯，近端半墙接书柜、阳台端敞开"></a><p class="hint">左：全关灯、保留自然光。右：本方案高台藏光、工作灯、环境间接光开启。摄影感概念表现；半墙外侧整段洗墙光属于表现差异，实体灯槽以内侧桌面段为准。几何以尺寸图和独立模型为准。</p><p>{review}</p><div class="links"><a href="{vid}/{vid}-半墙修正-开关灯对照.png">完整对照图</a><a href="{vid}/办公区-{vid}-近端半墙远端敞开-独立02.blend">独立三维模型</a></div><details><summary>查看同版实体参考</summary><div class="grid"><img src="{vid}/{vid}-OFF-半墙敞开端实体参考.png" alt="{vid}实体关灯"><img src="{vid}/{vid}-ON-半墙敞开端实体参考.png" alt="{vid}实体开灯"></div></details></section>')
page.append('''<section><h2>这次改在哪里</h2><img src="半墙与阳台入口尺寸.svg" alt="近端半墙接书柜与阳台端敞开示意"><table><thead><tr><th>部件</th><th>暂拟尺寸／mm</th><th>关系</th></tr></thead><tbody><tr><td>原办公桌</td><td>2400×700×750</td><td>位置和朝向保留，一台34寸屏、一把椅子</td></tr><tr><td>沙发背长高台</td><td>2400×200×950</td><td>原向阳台多伸的200取消，端头不再转弯横封</td></tr><tr><td>近端半墙</td><td>长1735；墙身厚120；顶950</td><td>落地实体，连续接到书柜前沿；饰面缝3</td></tr><tr><td>半墙压顶</td><td>1735×200×950（顶标高）</td><td>与长高台同色、同高，板厚随A/B/C方案</td></tr><tr><td>阳台端</td><td>不设新增横向构件</td><td>横台、栏杆、端柜全取消，原固定窗及室外防护构件保留</td></tr><tr><td>书柜相接模块</td><td>原800模块，位置不变</td><td>示意改为双轨平移实门，避免平开扫过半墙</td></tr></tbody></table><p class="hint">新增1735、950、120、200及R值属于设计建议，来源于当前v19模型比例，不是现场实测。桌面仍低于高台200，显示器放在750工作面。</p><div class="links"><a href="半墙与阳台入口尺寸.svg">矢量尺寸图</a><a href="设计参数.json">全部参数</a><a href="references/业主红半墙蓝敞开批注.png">本轮业主批注</a></div></section>
<section><h2>灯光、收口与使用</h2><div class="grid"><div><h3>光沿内缘走，入口不加横线</h3><p>长高台下沿与近端半墙压顶内侧藏3000K柔光；近端只照桌面段，不把灯带横跨阳台端。工作灯、藏光和环境光分路控制。全关灯图保留白天自然光，灯槽及台灯无发光；全开灯图显示本方案全部人工光。</p><p>灯槽内退，扩散罩与线材藏在可检修位置。桌面灯建议可调色温、可调角度，以后结合实际灯具核工作照度及屏幕眩光；图像不作为照度测量。</p></div><div><h3>让半墙与柜体衔接完整</h3><p>近端墙身暖白哑光，压顶随方案变化；墙顶与长高台同高950。书柜前沿留3 mm细缝，相邻北端800模块改平移实门示意。独立模型1—40帧可查看滑移，已核对示意门叶不扫过半墙，具体五金、止挡与取物仍需选型。</p><p>原椅后至书柜约408、桌边至书柜838继续保留。阳台端没有新增遮挡，但原椅后局部仍紧，不能因此称为宽裕通道；坐下、后退及清洁动作留待后续优化，不擅自移动现有桌椅。</p></div></div></section>
<section><h2>方案判断与交付状态</h2><p class="recommend">三套中我仍倾向B：深木压顶把空间边界勾清楚，暖白实体墙保留轻盈感，绿色和深蓝有明确落点。A更安静，C更柔和。本轮确认的是半墙范围与入口方向，尚未替你选择材质方案。</p><p>几何与实用性：三份独立模型已保存重开，回读半墙接至书柜、顶高950，阳台端横台和端柜为零；桌高750、单屏单椅保留。书柜平移门为设计师处理接口的提案，非已定产品。审美与图像：逐图查看摄影感、材质、光影和红／蓝区域是否按批注执行；概念图的木纹、窗景、细部及局部透视不作为毫米级证据。</p><p>范围：独立办公提案02。主模型v19、28件家具坐标、原VR和餐边柜独立11未因本轮变更，未启动v20。未作浏览器视觉验收；交付检查以图片解码、逐图查看和离线链接核对为依据。</p><div class="links"><a href="模型回读.json">几何核对</a><a href="审查与图像差异.json">图像审查</a><a href="出图提示词.json">内置imagegen生成提示词</a><a href="横条残留修正提示词.json">局部修正提示词</a><a href="C/恢复误删沙发扶手提示词.json">C扶手恢复提示词</a><a href="交付检查.json">交付检查</a></div></section></main></html>''')
save('办公区半墙与敞开端-三套修正版.html',''.join(page))
print('OFFICE02_PAGE_READY')
