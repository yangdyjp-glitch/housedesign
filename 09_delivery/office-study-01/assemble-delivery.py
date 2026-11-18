from pathlib import Path
import json, shutil, html

ROOT=Path('D:/AI-Yang.cn/HomeDesign')
OUT=ROOT/'09_delivery/office-study-01'
(OUT/'references').mkdir(exist_ok=True)
for src,name in [
 ('C:/Users/ADMINI~1/AppData/Local/Temp/codex-clipboard-903a779d-f9b1-4aa2-a34a-106b6b5a6b1e.png','办公高台参考.png'),
 ('C:/Users/ADMINI~1/AppData/Local/Temp/codex-clipboard-b78b33d0-75bd-4fb7-96a9-2700c111291e.png','位置批注.png')]:
 shutil.copy2(src,OUT/'references'/name)

p=json.loads((OUT/'设计参数.json').read_text(encoding='utf-8'))
# A 30 mm overlap at the high-ledge corner is a join allowance, not additional overall width.
p['common']['shortReturn'].update({'x':5270,'widthX':730,'overlapWithLongLedge':30,'nominalExposedReturnBeyondLongLedge':700})
p['variants'][2]['support']='matching ivory rounded posts with a concealed dark under-top frame'
(OUT/'设计参数.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf-8')

svg=['''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1240 920" role="img" aria-labelledby="title desc"><title id="title">办公区平面与高台参数</title><desc id="desc">沿用v19桌椅位置，新增等高L形高台，三套方案共用尺寸。</desc><defs><marker id="arrow" markerWidth="7" markerHeight="7" refX="3.5" refY="3.5" orient="auto-start-reverse"><path d="M0,0 L7,3.5 L0,7" fill="none" stroke="#60716b"/></marker></defs><style>text{font-family:'Microsoft YaHei','Noto Sans CJK SC',sans-serif;fill:#243831} .small{font-size:16px;fill:#65736c} .dim{stroke:#60716b;stroke-width:1.2;marker-start:url(#arrow);marker-end:url(#arrow)} .guide{stroke:#99a69e;stroke-dasharray:5 5;fill:none}</style><rect width="1240" height="920" fill="#faf9f5"/><text x="48" y="52" font-size="29" font-weight="700">办公区｜平面与高台关系</text><text x="48" y="84" class="small">尺寸单位 mm · 现有模型 v19 · 新高台尺寸为设计提案，现场待核</text>''']
def X(x):return 48+(x-3000)*.17
def Y(z):return 145+(z-1100)*.17
def rect(x,z,w,d,fill,rx=4,stroke='none'):
 svg.append(f'<rect x="{X(x):.1f}" y="{Y(z):.1f}" width="{w*.17:.1f}" height="{d*.17:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}"/>')
def text(x,z,s,size=16,anchor='start'):
 svg.append(f'<text x="{X(x):.1f}" y="{Y(z):.1f}" font-size="{size}" text-anchor="{anchor}">{html.escape(s)}</text>')
def dim(x1,z1,x2,z2,label,offset=0):
 ax,ay,bx,by=X(x1),Y(z1),X(x2),Y(z2)
 svg.append(f'<path class="dim" d="M{ax},{ay} L{bx},{by}"/>')
 if abs(ay-by)<1:svg.append(f'<text x="{(ax+bx)/2}" y="{ay-10-offset}" font-size="15" text-anchor="middle">{label}</text>')
 else:svg.append(f'<text x="{ax-10}" y="{(ay+by)/2}" font-size="15" text-anchor="middle" transform="rotate(-90 {ax-10} {(ay+by)/2})">{label}</text>')

rect(3100,1400,1900,3000,'#ebe8df',12)
rect(4750,1400,250,3000,'#d7d4ca',9)
text(3600,2900,'现有贵妃沙发',22)
text(3600,3120,'背高850',16)
rect(5100,1800,200,2600,'#927453',6)
rect(5270,1800,730,200,'#927453',6)
rect(5300,2000,700,2400,'#dfc9a7',9)
text(5630,3680,'办公桌',17,'middle')
text(5630,3860,'H750',16,'middle')
rect(5380,2195,90,810,'#28343c',2)
text(5510,2140,'34寸 ×1',14)
rect(5870,2320,560,560,'#9aa98f',15)
text(6150,2625,'椅',17,'middle')
rect(6838,1176,350,3600,'#d7dcd5',2)
text(7020,3600,'原书柜',17,'middle')
svg.append(f'<path class="guide" d="M{X(6430)},{Y(2320)} V{Y(3070)} M{X(6838)},{Y(2320)} V{Y(3070)}"/>')
dim(6430,3050,6838,3050,'408')
text(6080,3280,'椅后仍紧，不能当作舒适通道',14)
dim(5100,1640,6000,1640,'高台横向总长900')
dim(5050,1800,5050,4400,'长边高台2600')
dim(5300,4560,6000,4560,'桌深700')
text(4500,4810,'← 面向电视／图左 · 图上为阳台方向',16)
svg.append('''<path d="M840,130 V800" stroke="#d7ded6"/><text x="890" y="170" font-size="22" font-weight="700">横向剖面</text><path d="M885,490 H1190" stroke="#708078"/><rect x="903" y="320" width="40" height="6" rx="2" fill="#927453"/><rect x="943" y="360" width="140" height="6" rx="2" fill="#dfc9a7"/><rect x="909" y="326" width="7" height="164" fill="#927453"/><rect x="1065" y="366" width="7" height="124" fill="#927453"/><path class="dim" d="M1110,320 V490"/><text x="1123" y="410" font-size="17">950</text><path class="dim" d="M1170,360 V490"/><text x="1181" y="440" font-size="17">750</text><path class="dim" d="M980,320 V360"/><text x="995" y="345" font-size="16">200高差</text><circle cx="940" cy="328" r="3" fill="#cfac65"/><path d="M938,331 L980,380 L942,380 Z" fill="#edddb4" opacity=".6"/><text x="890" y="270" class="small">高台只作置物／遮线</text><text x="890" y="296" class="small">显示器和键盘放在750桌面</text><text x="890" y="540" class="small">高台下沿藏光，坐姿不见灯珠</text><text x="890" y="575" class="small">两条高台同色、同高、同边型</text><text x="890" y="620" font-size="19" font-weight="700">共用尺寸</text><text x="890" y="653" class="small">工作台：2400 ×700 ×750</text><text x="890" y="684" class="small">长高台：2600 ×200 ×950</text><text x="890" y="715" class="small">短高台：900 ×200 ×950</text><text x="890" y="746" class="small">组合占地：2600 ×900</text><text x="48" y="857" class="small">高台与沙发背留100清洁缝；比原桌向阳台多伸200。桌椅、沙发、书柜坐标保留。</text><text x="48" y="885" class="small">剖面为关系图；灯槽、暗钢支撑、板厚与收口需在选定方案后继续深化。</text></svg>''')
(OUT/'办公区尺寸与高台关系.svg').write_text(''.join(svg),encoding='utf-8')

styles='''*{box-sizing:border-box}body{margin:0;background:#f7f6f1;color:#24342f;font:16px/1.85 "Microsoft YaHei",sans-serif}main{max-width:1260px;margin:auto;padding:46px 30px 90px}header{padding-bottom:30px;border-bottom:1px solid #cfd8ce}.eyebrow{letter-spacing:.16em;color:#6f7e6f;font-size:13px}h1{font-size:38px;line-height:1.35;margin:14px 0}h2{font-size:25px;margin:0 0 14px}h3{font-size:20px;margin:22px 0 8px}.lead{max-width:960px;color:#59685e}.tags{display:flex;gap:12px;flex-wrap:wrap}.tags span{background:#e5eadf;border-radius:22px;padding:3px 16px;font-size:14px}section{margin-top:36px;padding:30px;background:#fffefb;border:1px solid #d9dfd4;border-radius:24px}.figure{width:100%;height:auto;border-radius:16px;display:block}a{color:#365f50;text-underline-offset:4px}table{width:100%;border-collapse:collapse}td,th{padding:13px 16px;border-bottom:1px solid #e2e5db;text-align:left;vertical-align:top}th{color:#596a5b;font-size:14px}.hint{font-size:14px;color:#727e73}.grid{display:grid;grid-template-columns:1fr 1fr;gap:28px}.swatches{display:flex;gap:10px;margin:20px 0;flex-wrap:wrap}.swatches span{display:inline-flex;align-items:center;font-size:14px}.swatches i{display:inline-block;width:20px;height:20px;border:1px solid #d3d5cb;border-radius:50%;margin-right:7px}.links{display:flex;gap:18px;flex-wrap:wrap;font-size:14px}details{margin:16px 0}summary{cursor:pointer;color:#52705c}.recommend{border-left:4px solid #8da47e;padding-left:17px}.status{color:#6d7c6d;font-size:14px}@media(max-width:750px){main{padding:25px 16px 70px}section{padding:20px 16px;border-radius:18px}.grid{grid-template-columns:1fr}h1{font-size:29px}table{font-size:13px}td,th{padding:9px 7px}}'''
head='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>沙发后办公区｜三套独立设计</title><style>'''+styles+'''</style><main><header><div class="eyebrow">HOME OFFICE / STUDY 01 · 2026.11.06</div><h1>沙发背后，一张桌与两道高台</h1><p class="lead">提取参考照片的低矮L形高台，取消红框里的新墙与吊柜。用桌面的高低关系、材质和藏光形成层次，让办公区融入自然现代日式的客厅。三套均为独立设计，暂未选定或融合主模型。</p><div class="tags"><span>面向电视</span><span>34寸屏 ×1</span><span>办公椅 ×1</span><span>两边高台统一950高</span><span>主模型保留v19</span></div></header>'''
cards=[
 ('A','浅木薄片','最轻盈、最容易融入现有空间。用一条细长的浅木L高台整理沙发背面，视觉上保持开放。','两边高台与桌面均用同色哑光浅橡木，搭配灰绿座椅、深蓝台灯；用不同厚度与高差形成层次。','高台厚30，外露平面圆角R35；桌面厚30、R60。空置端一只500×400×100浅抽，主工位膝部不设横抽。','高台底内侧沿长短两边连续藏光。浅木反光更柔，工作灯可独立开启；开灯时避免把整块木面照成黄色。','木色面积较大，实样应选低黄度浅橡木，避免地板与桌面两种木纹同时过于醒目。',[('#c9b38d','浅木'),('#eeeee5','暖白'),('#8e9e83','灰绿'),('#253d52','深蓝')]),
 ('B','深木框景','风格层次最鲜明。这套更贴合你希望在浅木基底里加入深木、绿色和蓝色的方向。','深胡桃木只用在两边高台和支撑，低桌面保持浅木；短边下设置灰绿浅端柜，深蓝保留在台灯和软装中。','高台厚45，外露平面圆角R45；桌面厚30、R60。短边下浅端柜约500×200×720，只收小物与线材，不作为深文件柜。','灯带藏进深木下口，点亮后形成清楚但克制的暖光边。工作灯不与氛围灯捆绑；白天可完全关掉高台灯。','深木会增强边界感；建议维持开放支撑，不把沙发背整面封成深木墙板。',[('#644735','深胡桃'),('#cab38f','浅木'),('#85967e','灰绿'),('#253d52','深蓝')]),
 ('C','奶油圆弧','轮廓最柔和。用奶油白高台包住浅木工作面，以较大的端部弧线呼应圆角桌和弧形墙角。','两边高台均为哑光暖白实体面材，桌面为浅木；末端一只小深蓝悬抽，绿植与原沙发绿蓝软装呼应。','高台厚35，外露平面圆角R80；桌面厚30、R60。深蓝浅抽约500×400×100；大圆弧集中在端头，直边仍是骨架。','灯光主要擦过高台内缘和下方木面，避免亮白高台产生刺眼高光。桌面灯维持3500–4000K可调，氛围灯3000K。','面材与木作交界需要留可控的细缝，避免追求无缝而失去检修和材料伸缩空间。',[('#ece9df','奶油白'),('#cab38f','浅木'),('#253d52','深蓝'),('#85967e','绿色')]),
]
body=[head]
for vid,title,intro,materials,dimtext,lighting,tradeoff,swatches in cards:
 body.append(f'<section id="{vid}"><div class="eyebrow">OPTION {vid}</div><h2>{vid}｜{title}</h2><p>{intro}</p><a href="{vid}/{vid}-开关灯对照.png"><img class="figure" src="{vid}/{vid}-开关灯对照.png" alt="{vid} {title}，左全关灯，右全开灯"></a><p class="hint">左：全关灯，保留自然光。右：本方案高台藏光、工作灯及环境灯开启。均为摄影感概念图。</p><div class="swatches">'+''.join(f'<span><i style="background:{c}"></i>{s}</span>' for c,s in swatches)+f'</div><div class="grid"><div><h3>材料与造型</h3><p>{materials}</p><p>{dimtext}</p></div><div><h3>灯光与取舍</h3><p>{lighting}</p><p>{tradeoff}</p></div></div><div class="links"><a href="{vid}/{vid}-开关灯对照.png">打开完整对照图</a><a href="{vid}/办公区-{vid}-独立提案.blend">独立三维提案</a><a href="{vid}/generation-prompt.json">本套生成提示词</a></div><details><summary>查看同版尺寸模型参考</summary><div class="grid"><img class="figure" src="{vid}/{vid}-OFF-native.png" alt="{vid}原生尺寸参考关灯"><img class="figure" src="{vid}/{vid}-ON-native.png" alt="{vid}原生尺寸参考开灯"></div></details></section>')

body.append('''<section><h2>三套共用的尺度</h2><p>以下均为本轮暂拟参数。长向沿沙发背、横向由沙发指向书柜；高台是家具的一部分，不向上增加隔墙或吊柜。</p><table><thead><tr><th>部件</th><th>长 ×深 ×高 / mm</th><th>使用方式</th></tr></thead><tbody><tr><td>办公桌</td><td>2400 ×700 ×750</td><td>沿用当前桌面坐标与双人桌比例，现阶段只摆一椅、一屏</td></tr><tr><td>沙发背长高台</td><td>2600 ×200 ×950</td><td>置物、理线；高于桌面200，高于现沙发背100</td></tr><tr><td>阳台端短高台</td><td>900 ×200 ×950</td><td>含长高台转角宽度，与长边同色、同高、同边型</td></tr><tr><td>整组占地</td><td>2600 ×900</td><td>不含椅；比原桌增加一条200宽高台及200深短端</td></tr><tr><td>显示器</td><td>34寸，单屏</td><td>约810宽的比例占位，继续放在750工作面，配可调支架</td></tr></tbody></table><img class="figure" src="办公区尺寸与高台关系.svg" alt="办公区平面和高台关系参数图"><div class="links"><a href="办公区尺寸与高台关系.svg">打开矢量尺寸图</a><a href="设计参数.json">完整参数</a></div></section>
<section><h2>灯光、线路与收口</h2><div class="grid"><div><h3>三路独立控制</h3><p>高台长短两边均藏3000K可调光线性灯，铝槽内退、漫射罩遮住灯珠；坐在桌前和沙发上都应看不到直接光源。独立台灯建议3500–4000K可调，显色指数Ra≥90作为选型目标。环境光沿用四区方案的柔和间接光。</p><p>工作面照度先以约300–500 lx为设计目标，后续按所选灯具配光及现场测量校核；效果图亮度不代表实际照度。晚间保留低亮度环境补光，减少屏幕与周围的突兀明暗反差。</p></div><div><h3>把日常细节藏好</h3><p>强弱电分区走线，桌下设可拆理线槽，线从支撑内下行；灯带电源与连接件留可检修位置。屏幕支架和走线不占高台置物面；长高台用内藏框架配多点支撑，跨度和连接须在深化时校核。</p><p>桌沿做触摸可感的软边，外露转角按各套R值控制。大曲线留在端头，细缝收口与材质交接保持直、少、连续。高台与沙发背之间留100清洁缝，并安排端头吸尘或可拆清洁方式。</p></div></div><p class="hint">眩光与布灯原则参考 <a href="https://www.osha.gov/etools/computer-workstations/workstation-environment">OSHA：电脑工作区照明环境</a>；显示器距离和高度按 <a href="https://www.osha.gov/etools/computer-workstations/components/monitors">OSHA：显示器设置</a>继续结合使用者调整。以上是设计建议，并非对本住宅作规范认证。</p></section>
<section><h2>审美与实用性分开判断</h2><p class="recommend"><strong>我更倾向B。</strong>深木高台与灰绿端柜给这块区域一个清楚的形象，同时保留浅木桌面和暖白环境。A最轻盈，C的圆弧最明显，三套的选择取决于你希望办公区成为点缀还是更有存在感。</p><p>审美评审统一看色彩、现代性、构图、视觉层次，以及可达性／可用性的视觉表达，六项等权；不把主观分数当作尺度验收。开关灯同机位用于比较，窗外景观和微小材质细节属于概念表现。</p><p>实用性审查以v19的网格包络为依据：椅后至书柜约408，桌边至书柜约838。前者仍紧凑，不能按舒适通行带理解。本轮按你此前要求保留桌椅和沙发位置；选定方案后，仍须核对坐下、起身、后退和书柜开门的动作。高台深200只供小物，主办公面700深保留。</p><p class="status">状态：三套均为候选方案，未应用到主模型、未启动v20、未更新原VR。独立Blender模型已保存并重开核对桌高750／两边高台950、单屏单椅，五项主模型文件前后校验一致。概念图不替代尺寸图和现场复尺。</p><details><summary>交付与核对记录</summary><div class="links"><a href="核对记录.json">模型核对记录</a><a href="审查与图像差异.json">逐图审查与差异</a><a href="references/办公高台参考.png">业主造型参考</a><a href="references/位置批注.png">业主位置批注</a></div></details></section></main></html>''')
(OUT/'办公区三套独立方案.html').write_text(''.join(body),encoding='utf-8')
print('DELIVERY_PAGE_WRITTEN')
