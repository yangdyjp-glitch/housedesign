from pathlib import Path
from html import escape
from html.parser import HTMLParser
import json, hashlib, struct, xml.etree.ElementTree as ET

OUT=Path('D:/AI-Yang.cn/HomeDesign/09_delivery/sideboard-L-study-03')
ROOT=Path('D:/AI-Yang.cn/HomeDesign')
BASELINE={
 '06_blender/home-main-v19.blend':'04f55222258c1a866e84b9eff3b7987e48f399ca520789ba458b3fa16d4dc214',
 '06_blender/active-model.json':'52766c728b10a878baddff725d50a81dd796543efd14c877b7c70601d2a6342f',
 '02_geometry/geometry-master-v19.json':'44d4cd19f7a90b9c1bf24f958a50f66db46bffba5e0ddfe147cc49543ae7aa9d',
 '05_style/modern-japanese-v19.json':'387f6be47a1aeaf64a0e58d178fe5507c9ab5cf9cf26c19f7dfaa4b16b092b4c',
 '06_blender/active-presentation.json':'4f967c49e33cb02e893de5344a452258fe34c14354ae9ec4582004c8ca684e97',
}
schemes=[
 dict(id='A',title='暖白框景与浅木餐面',idea='一整片上柜＋胡桃木壁龛＋低位L餐面，保留完整餐边柜。',
      upper='1500宽封闭上柜（600＋900）＋700宽玻璃展示；柜底1500、柜顶2100。',
      lower='450宽左侧餐具柜＋700宽右侧三抽；中间750为固定连接，邻椅300为固定侧段，不画成被餐桌卡住的活动抽屉。',
      material='暖白上、下柜；胡桃木壁龛；浅橡木圆角餐面；少量绿蓝织物。',
      fridge='同墙色通风检修面整理上方，取消高位储物门。保留通风容积及可拆面，开孔率、风路和侧距必须按实际冰箱校核，未认定普通机均可围合。',
      niche=620,upperBottom=1500,upperTop=2100,lights='上柜底工作光＋700展示格柔光＋纸布感餐吊灯，三组分控。'),
 dict(id='B',title='曲面石餐面与非对称展示柜',idea='横向封闭上柜连接右侧竖向展示体，曲面餐岛形成主角。',
      upper='1500宽封闭上柜，1500–2100；右700竖柜中段880–1700展示、下段封闭、上段低频收纳。',
      lower='450深下柜和餐具抽屉保留；最右700作为独立餐具展示竖柜，下方封闭收纳，不再额外堆放咖啡机。',
      material='暖白上柜、低饱和灰苔绿下柜及玻璃框、哑光浅暖灰石餐面、胡桃木餐椅。',
      fridge='取消整个冰箱上方柜盒，冰箱独立靠墙，顶部是连续开放的墙面；没有夹在两个柜体之间的黑槽，也不假装普通冰箱可零缝封装。',
      niche=620,upperBottom=1500,upperTop=2100,lights='上柜底工作光＋竖柜展示光＋柔光餐吊灯，三组分控。'),
 dict(id='C',title='深木上柜与浅色餐岛',idea='连续木纹上柜与半透展示门形成整体，白色下柜和轻薄餐岛托住深木体量。',
      upper='1500宽封闭木门上柜＋700半透玻璃展示；柜底1450、柜顶2100，分格与木纹连续。',
      lower='450深封闭下柜、餐具三抽和独立L连接模块；收纳功能不被装饰格或整片挡门替代。',
      material='棕灰胡桃木上柜、暖白下柜和壁龛背板、浅暖灰石/浅木餐面，绿色和深蓝用于小物及织物。',
      fridge='普通对开门冰箱仍在客厅端、L外侧；上方不设日常储物。采用开放顶部时不做柜盒；如采用同色通风面，须先核实际散热条件。',
      niche=570,upperBottom=1450,upperTop=2100,lights='壁龛工作光＋半透展示内光＋餐吊灯；灯点隐藏，三组分控。'),
]

# A dimensioned diagnostic plan. This remains independent from house-structure.html.
svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1500 1320">',
 '<style>text{font-family:Microsoft YaHei,Arial,sans-serif;fill:#2d3a32}.small{font-size:27px}.label{font-size:35px}.m{stroke:#778571;stroke-width:3;fill:none}.old-layout{display:none}</style>',
 '<rect width="1500" height="1320" fill="#faf9f5"/>',
 '<text x="60" y="60" font-size="36">冰箱在客厅端、L餐岛外侧｜独立提案平面</text>',
 '<text x="60" y="105" class="small">单位mm；上为所选柜墙，左通客厅，右通餐厨门；两大一小常住，四椅配置。</text>']
scale=.32;ox=120;oy=180
def rect(x,y,w,d,fill,stroke='#697762',dash='',cls=''):
    svg.append(f'<rect class="{cls}" x="{ox+(x+72.5)*scale}" y="{oy+y*scale}" width="{w*scale}" height="{d*scale}" fill="{fill}" stroke="{stroke}" stroke-width="2" '+(f'stroke-dasharray="{dash}" ' if dash else '')+'/>')
def txt(x,y,t,size=24):
    svg.append(f'<text x="{ox+(x+72.5)*scale}" y="{oy+y*scale}" font-size="{size}">{escape(t)}</text>')
rect(-72.5,-60,3545,60,'#879080')
rect(-72.5,0,3545,3082,'#fffefa')
rect(-72.5,2682,3545,400,'#e6d8c1')
rect(-72.5,1700,3545,982,'#dfe9d8',stroke='#cad8c2')
rect(0,0,1200,800,'#9aa6a3')
rect(140,50,920,750,'#66736f')
rect(1200,0,2200,450,'#e6d8c1')
rect(1200,0,2200,350,'none',stroke='#748695',dash='8 6')
rect(1650,300,750,1400,'#cfb48e')
for side,xx,face in [('客厅侧',1350,1),('餐厨侧',2250,-1)]:
    for i,yy in enumerate((450,1250)):
        rect(xx,yy,450,450,'#b1c4a6' if i==0 else '#a7b8c5')
        pullx=xx-250 if face==1 else xx+250
        rect(pullx,yy,450,450,'none',stroke='#a87864',dash='6 5')
        txt(xx+60,yy+270,'椅',21)
rect(1650,300,750,150,'#b09470')
rect(1137.5,0,1600,800,'none',stroke='#ba6c61',dash='10 8',cls='old-layout')
txt(150,320,'冰箱',27);txt(150,430,'在L形外侧',23)
txt(2600,270,'餐边柜',26)
txt(1790,1050,'L餐面',26);txt(1750,1160,'1400×750',22)
txt(600,2250,'连续绕行约982',30)
txt(50,2940,'对侧通长柜／换鞋段深400（现有）',25)
# Door group at kitchen boundary, on plan right, blue segment1691long.
dx=ox+(3472.5+72.5)*scale
svg.append(f'<path d="M{dx} {oy}V{oy+1691*scale}" stroke="#87aaba" stroke-width="10"/>')
svg.append(f'<text transform="translate({dx+40},{oy+140}) rotate(90)" font-size="24">餐厨推拉门组1691，净开口另核</text>')
svg.append('<text x="60" y="1210" class="small">实色椅：坐姿占位，前部150插入桌下；棕虚线：再向外拉250的试算包络。</text>')
svg.append('<text x="60" y="1250" class="small">餐厨端坐姿后约772.5；拉椅后约522.5，不能宣称四椅拉开时仍有宽松通道。</text>')
svg.append('<text x="60" y="1290" class="small">该图是设计叠加研究；v19原家具未移动，冰箱开门、实际坐姿和墙长需按现场及产品复核。</text></svg>')
svg='\n'.join(svg)
(OUT/'L餐岛位置与净空.svg').write_text(svg,encoding='utf-8')

def elevation(s):
    o=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 3900 3000"><rect width="3900" height="3000" fill="#faf9f5"/><style>text{font-family:Microsoft YaHei,Arial,sans-serif;fill:#334133;font-size:42px}</style>']
    def b(x,z,w,h,col): o.append(f'<rect x="{200+x}" y="{2600-z-h}" width="{w}" height="{h}" fill="{col}" stroke="#7e8c77" stroke-width="3"/>')
    b(0,0,1200,1850,'#697673')
    b(1200,80,2200,780,'#e3dfd5');b(1200,860,2200,20,'#cfb48e')
    b(1200,880,2200,s['niche'],'#bfa689')
    b(1200,s['upperBottom'],1500,s['upperTop']-s['upperBottom'],'#eeeae2')
    b(2700,s['upperBottom'],700,s['upperTop']-s['upperBottom'],'#bbcec6')
    b(1650,0,750,720,'#e8dfcf');b(1650,720,750,30,'#cfb48e')
    o.append(f'<text x="200" y="100">{s["id"]} 餐边柜与L餐岛｜尺寸原则，非加工图</text>')
    o.append('<text x="280" y="2820">冰箱区1200</text><text x="1600" y="2820">真正餐边柜2200</text>')
    o.append(f'<text x="1500" y="2900">下柜450深／上柜350深／操作台880高</text>')
    o.append(f'<text x="200" y="220">上柜{s["upperBottom"]}–{s["upperTop"]}；中部净高{s["niche"]}；餐面750</text>')
    o.append('</svg>');return '\n'.join(o)
for s in schemes: (OUT/f'{s["id"]}-功能立面.svg').write_text(elevation(s),encoding='utf-8')

refs=[
 {'title':'Norm／Reform PROFILE','url':'https://www.reformcph.com/us/kitchens/collections/profile-norm-architects','take':'借鉴连续线条、克制分缝和木材质感；不是把厨房尺寸照搬到餐厅。'},
 {'title':'Cesar Tangram','url':'https://www.cesar.it/it/collezioni/cucine/tangram/','take':'借鉴曲面与直线体量连成一件家具的处理；不照搬大岛台、灶具、水槽和夸张石纹。'},
 {'title':'Fifth Avenue餐台连接案例／Cosentino','url':'https://www.cosentino.com/inspiration/projects/a-perfectly-crafted-dining-table-integration/','take':'借鉴高低两种家具在接口上形成整体；本案以880操作台接750餐面。'},
 {'title':'Kesseböhmer iMove','url':'https://www.kesseboehmer.com/en/storage-solutions/kitchen/wall-units/imove','take':'较高的餐边上柜可研究单层下拉篮；不是在冰箱顶部生搬一个机构。'},
 {'title':'Häfele iMove规格实例','url':'https://hafelehome.com.my/products/imove','take':'所列600/900门宽、净宽562–568/862–868、净高最低480用于可行性初查；实际深度、运动轨迹和载荷仍须按所选安装图核对。'},
 {'title':'普通对开冰箱安装限制实例','url':'https://media3.bosch-home.com/Documents/8001142358_B.pdf','take':'普通机型的通风、侧距和上方空间不能用一块实心封板取消。具体按最终机型，不将旧型号要求冒充所有冰箱的标准。'},
]
cards=[]
for s in schemes:
    rows=''.join(f'<tr><th>{k}</th><td>{escape(s[v])}</td></tr>' for k,v in [('上柜与展示','upper'),('下柜与收纳','lower'),('材质与体量','material'),('冰箱上方','fridge'),('灯光','lights')])
    cards.append(f'<section class="card" id="{s["id"]}"><span class="tag">修订{s["id"]}</span><h2>{s["title"]}</h2><p>{s["idea"]}</p><a href="{s["id"]}-开关灯对照.png"><img src="{s["id"]}-开关灯对照.png" alt="{s["id"]}完整餐边柜与L餐岛，左全关灯、右全开灯"></a><p class="caption">左全关／右全开。日光与家具保持相同；图像为独立设计表现，非主模型实装。</p><table>{rows}</table><details><summary>尺寸立面</summary><img src="{s["id"]}-功能立面.svg" alt="功能立面"></details></section>')
refhtml=''.join(f'<li><a href="{r["url"]}">{r["title"]}</a>：{r["take"]}</li>' for r in refs)
page='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>完整餐边柜＋L餐岛｜独立修订方案</title><style>*{box-sizing:border-box}body{margin:0;background:#f4f3ee;color:#2e3b32;font:16px/1.85 "Microsoft YaHei",system-ui,sans-serif}main{max-width:1240px;margin:auto;padding:40px 28px}h1{font-size:clamp(29px,4vw,44px);line-height:1.35}h2{font-size:28px;font-weight:550}.card{padding:25px;margin:28px 0;border:1px solid #dbe0d3;background:#fffefa;border-radius:16px}img{width:100%;display:block;border-radius:8px}.caption{font-size:14px;color:#78806f}a{color:#486b54;text-underline-offset:4px}.tag{letter-spacing:.15em;color:#708366;font-size:13px}.note{padding:18px 22px;border-left:4px solid #91a182;background:#e9ede2}.warning{border-color:#b78767;background:#f4eadd}nav{display:flex;gap:12px;flex-wrap:wrap;margin:24px 0}nav a{padding:8px 20px;border:1px solid #cdd8c5;border-radius:25px;text-decoration:none}table{border-collapse:collapse;width:100%;margin:20px 0}th,td{text-align:left;vertical-align:top;padding:12px;border-bottom:1px solid #e3e7dc}th{width:130px;font-weight:500;color:#748068}summary{cursor:pointer;color:#486b54;padding:12px 0}li{margin:8px 0}.plan svg{width:100%;height:auto}footer{font-size:13px;color:#7a8374}@media(max-width:600px){main{padding:22px 14px}.card{padding:15px}th,td{display:block;width:100%;padding:7px 0}th{border:0}h2{font-size:23px}}</style></head><body><main>
<span class="tag">INDEPENDENT STUDY · 2026.11.05</span><h1>完整餐边柜，与L餐岛连成一体</h1>
<div class="note"><strong>本轮纠正：餐边柜必须保留。</strong><br>上柜、操作壁龛、餐具下柜与展示区都有；只处理冰箱上方不实用的高柜。冰箱固定在靠客厅端、位于L形之外，餐岛从其右侧柜段伸出。三个候选均未选定，v19及家具、VR不变，未启动v20。</div>
<nav><a href="#A">A 暖白框景</a><a href="#B">B 曲面石岛</a><a href="#C">C 深木上柜</a><a href="#plan">尺寸与使用</a></nav>
'''+'\n'.join(cards)+'''
<section class="card" id="plan"><h2>尺寸与使用关系</h2><p>所选墙模型长3545，总宽按3400：冰箱区1200＋真正餐边柜2200。2750为现有模型暂定完成面，不是实测净高。</p>
<table><tr><th>真正的餐边柜</th><td>下柜深450、台面高880；上柜深350。A/B柜底1500、柜顶2100，操作区净高620；C柜底1450、柜顶2100，净高570。盘碟和大件放在深下柜，较高上柜研究单层下拉篮。</td></tr><tr><th>L餐面</th><td>1400×750、高750、桌下约720；在750宽固定连接段穿接，高低差130。餐面后150插接进450深柜段，柜外实际伸出1250。连接区不设会被餐桌卡住的活动抽屉。</td></tr><tr><th>座位</th><td>四把常规餐椅，两侧各二，端头不设座。椅前150进入桌下为坐姿假设，拉椅另预留250试算，未用物体原点假装活动空间充分。</td></tr><tr><th>收纳可达性</th><td>右端700主抽屉段、左端450柜、上柜及展示区是真正收纳；中间750连接和邻椅300固定面不计作可直接开启收纳。靠餐面位置的上柜取物需要在椅位空出时从侧方操作，不宣称满座时所有柜门同时方便开启。</td></tr><tr><th>灯光</th><td>工作、展示、餐吊灯三组独立控制，3000K、Ra≥90为选型目标。隐藏铝槽配扩散罩，避免灯点与亮台面反射；驱动器留检修位置。</td></tr></table>
<div class="note warning">外侧连续绕行约982；餐厨端坐姿后约772.5，拉椅250后约522.5。后者仍局促，不能把这套图当成四人拉椅与厨房通行同时宽松的证明。冰箱门、柜门和实际坐姿要按选型再核。</div>
<label><input type="checkbox" id="old">显示v19现有餐桌虚线，仅作对照</label><div class="plan">'''+svg+'''</div>
<p>此处只提出新连接关系，未自动移动主模型餐桌。入户侧、对侧400深通长柜和餐厨推拉门继续以现模型为背景；实际门组净开口另核。</p></section>
<section class="card"><h2>红区与蓝区分别怎样处理</h2><p><strong>冰箱上方高柜：</strong>不再把2200以上区域算成日常储物，A用同色通风检修面整理；B取消整个上方柜盒；C按选定冰箱研究开放顶部或通风检修面。真正的餐边上柜在右侧保留，不能把取消冰箱顶柜扩大成取消整个餐边柜。</p><p><strong>原裸露空洞：</strong>空间不是为了装饰而必须保留的黑槽；普通冰箱确有通风需求，需用开放顶部或经机型验证的通风构造解决。视觉收整不等于拿实心板封死。若今后要求极小安装缝，应以相应机型重新推柜尺寸。</p><p><strong>上柜够不到：</strong>按1500–2100设计的餐边上柜可研究单层下拉系统，600和900模块仅完成尺寸初查，实际拉出/下降轨迹、净深及开门角需核安装图；不承诺随便装一个篮子就能解决所有高位。</p></section>
<section class="card"><h2>查阅的真实设计参考</h2><ul>'''+refhtml+'''</ul><p class="caption">以上是设计语言或产品原理参考，均非业主已选定产品，不作采购推荐。图片为内置imagegen概念表现，精确尺寸以参数和关系草模为依据；可见细分缝及比例可能有偏差。</p><p><a href="layout-parameters.json">完整布局参数</a> · <a href="generation-prompts.json">出图提示词与来源</a> · <a href="餐边柜与L餐岛-独立草模.blend">独立关系草模</a></p></section>
<footer>旧三套方案及取消上柜的中间方向均已标记未采用。未融合主模型，未代替现场量尺或加工图。</footer></main><script>document.getElementById('old').addEventListener('change',function(){document.querySelectorAll('.old-layout').forEach(e=>e.style.display=this.checked?'block':'none')})</script></body></html>'''
(OUT/'餐边柜与L餐岛三套修订.html').write_text(page,encoding='utf-8')
spec=json.loads((OUT/'layout-parameters.json').read_text(encoding='utf-8'))
spec.update({'schemes':schemes,'reference_sources':refs,'master_before':BASELINE,'master_unchanged':True,'not_v20':True})
images=[]
for s in schemes:
    p=OUT/f'{s["id"]}-开关灯对照.png'
    if p.exists():
        b=p.read_bytes();assert b[:8]==b'\x89PNG\r\n\x1a\n';w,h=struct.unpack('>II',b[16:24])
        images.append({'scheme':s['id'],'file':p.name,'width':w,'height':h,'sha256':hashlib.sha256(b).hexdigest()})
after={k:hashlib.sha256((ROOT/k).read_bytes()).hexdigest() for k in BASELINE};assert after==BASELINE
spec['master_after']=after;spec['images']=images
(OUT/'layout-parameters.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2),encoding='utf-8')
for p in OUT.glob('*.svg'): ET.parse(p)
(OUT/'verification.json').write_text(json.dumps({'master_unchanged':True,'images':images,'svg_xml_valid':True,'browser_preview':'not attempted; file URL policy disallows it','scope':'standalone concepts, no master or VR changes'},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'images':len(images),'master_unchanged':True,'output':str(OUT)},ensure_ascii=False))
