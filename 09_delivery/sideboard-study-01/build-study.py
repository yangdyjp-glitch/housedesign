from pathlib import Path
import json, hashlib, shutil, struct, html

ROOT = Path('D:/AI-Yang.cn/HomeDesign')
OUT = ROOT / '09_delivery/sideboard-study-01'
OUT.mkdir(parents=True, exist_ok=True)
BASELINE = {
    '06_blender/home-main-v19.blend': '04f55222258c1a866e84b9eff3b7987e48f399ca520789ba458b3fa16d4dc214',
    '06_blender/active-model.json': '52766c728b10a878baddff725d50a81dd796543efd14c877b7c70601d2a6342f',
    '02_geometry/geometry-master-v19.json': '44d4cd19f7a90b9c1bf24f958a50f66db46bffba5e0ddfe147cc49543ae7aa9d',
    '05_style/modern-japanese-v19.json': '387f6be47a1aeaf64a0e58d178fe5507c9ab5cf9cf26c19f7dfaa4b16b092b4c',
    '06_blender/active-presentation.json': '4f967c49e33cb02e893de5344a452258fe34c14354ae9ec4582004c8ca684e97',
}

SCHEMES = [
    dict(id='A', name='暖白 × 胡桃木', mood='干净温润，最贴合当前整体', width=3400, height=2750,
         coffee=1600, display=500, counter=880, niche=620, flap=240, upper=960,
         base='#efede7', back='#6f4c39', dark='#674630', upperColor='#f1efe9', displayBack='#e5e0d5',
         materials='暖白哑光门板、棕灰胡桃木壁龛与薄柜、浅暖灰哑光石英石；展示格用低铁玻璃及细暖灰金属框。',
         baseLayout='操作区左800双开门＋右800三抽；右侧500展示柜下方封闭。',
         tradeoff='适合延续现有风格，深木增加层次；木色集中在凹位，避免整面偏暗。',
         lights=['L1 壁龛工作光1600 mm','L2 展示层板3 × 约460 mm','L3 操作柜低位光1600 mm'],
         modules=[('余量/收口',50),('冰箱模块',1200),('操作收纳',1600),('玻璃展示',500),('余量/收口',50)]),
    dict(id='B', name='灰苔绿 × 浅橡木', mood='最鲜明的自然日式，柔和有生气', width=3400, height=2750,
         coffee=2100, display=0, counter=900, niche=650, flap=250, upper=900,
         base='#8e9d8b', back='#c9b18d', dark='#bfa581', upperColor='#f1efe9', displayBack='#c9b18d',
         materials='低饱和灰苔绿下柜、暖白上柜、浅橡木壁龛及薄柜、浅灰白哑光石英石；取消玻璃展示，减少视觉碎片。',
         baseLayout='2100操作区分为700三抽＋700双开门＋600收纳及100固定圆弧端；柜内可调层板。',
         tradeoff='台面最长、封闭容量最大；绿色成为局部主角，与原绿色餐椅相呼应。',
         lights=['L1 壁龛工作光2100 mm','L2 圆弧木背板局部柔洗光，与工作光分控','L3 操作柜低位光约2000 mm'],
         modules=[('余量/收口',50),('冰箱模块',1200),('操作收纳',2100),('余量/收口',50)]),
    dict(id='C', name='浅木 × 深蓝展示', mood='层次最鲜明，保留轻盈留白', width=3400, height=2750,
         coffee=1500, display=600, counter=880, niche=650, flap=220, upper=950,
         base='#cfb590', back='#e9e6dd', dark='#36546a', upperColor='#f1efe9', displayBack='#36546a',
         materials='浅橡木下柜、暖白上柜、浅暖灰石英石壁龛；薄柜和600展示格背板使用低饱和深蓝，金属框用暖灰。',
         baseLayout='操作区750双开门＋750三抽；600展示格下方保留封闭收纳，展示占比控制在整柜约18%。',
         tradeoff='蓝色集中成一条细竖带及薄柜，适合希望餐厅辨识度更强的情况；少量展示，避免酒柜化。',
         lights=['L1 壁龛工作光1500 mm','L2 展示格侧后方竖向光约1250 mm，层板采用透光玻璃','L3 操作及展示柜低位光2100 mm'],
         modules=[('余量/收口',50),('冰箱模块',1200),('操作收纳',1500),('玻璃展示',600),('余量/收口',50)]),
]

DATA = {
    'study_id':'sideboard-study-01', 'date':'2026-11-05', 'status':'three independent unselected design proposals',
    'not_merged_into_master':True, 'v20_triggered':False, 'units':'mm',
    'brief':{'wall':'餐桌后方、客卫外侧，用户最新红框墙','fridge':'普通左右对开的双门冰箱，未指定型号','scope':'只做柜体设计及参数，每套同视角全开灯与全关灯；不改当前家具'},
    'wall':{'source':'geometry-master-v19.json / lower-narrow-left-end','x':3082,'z':6090,'length':3545,'height':2750,'dimensions_status':'模型暂拟，非现场实测','cabinet_length':3400,'remaining_total':145,'nominal_end_allowance_each':72.5},
    'fridge':{'appliance_envelope':[920,750,1850],'envelope_order':'W,D,H','is_product_selection':False,
              'module_width':1200,'side_panel_thickness':18,'clear_opening_width':1164,'clear_opening_height':2200,
              'surround_side_depth':700,'depth_to_closed_appliance_front':800,'rear_gap_assumption':50,'door_projection_past_surround':100,
              'side_gaps_each_at_920_width':122,'top_gap_at_1850_height':350,
              'approach':'普通冰箱半围合，保留外露机门；非全嵌门板冰箱、非零嵌承诺。散热通道不封死，顶柜自2200以上开始；机型说明书决定最终净空和开门包络。'},
    'common_parameters':{'base_depth':450,'upper_depth':320,'flap_depth':250,'ceiling_scribe_height':50,'plinth_height':80,'plinth_recess':60,'counter_thickness':20,'panel_thickness':18,
                         'counter_edge_radius':40,'door_reveal_target':2,'exposed_end_fixed_curve_radius':70,
                         'lighting_cct_kelvin':3000,'lighting_cri_target':90,'lighting_control':'工作、展示/局部洗墙、低位三组独立调光；不可见灯点；驱动器可检修',
                         'lighting_render_comparison':'左全关，右全开；关闭全部人工照明时保留相同自然光，非日夜替换'},
    'schemes':SCHEMES,
    'fit_review':{'table_current_bounds':{'x':2282,'z':7300,'w':800,'d':1600},'opposite_cabinet_projection':400,
                  'main_cabinet_front_x':2632,'known_table_overlap_depth':450,
                  'simple_move_cannot_be_claimed_solved':True,
                  'work_access_test':{'room_width':3082,'opposite_cabinet':400,'chair':450,'table':800,'service_gap_target':900,'sideboard':450,'remainder':82},
                  'interpretation':'现桌贴墙，新柜与桌确定重叠。仅横移不能同时获得宽松椅后通行及柜前工作区；后续须独立研究餐桌朝向/位置、对侧柜范围、取物关系及冰箱开门，不在本次改主模型。900为设计试算，非规范结论。'},
    'sources':[
        {'title':'伊莱克斯ESE6600B-B官方规格','url':'https://www.electrolux.com.cn/appliances/refrigerators/ese6600b-b/','use':'911W×746D×1780H、90度开门深1205，仅为普通对开体量实例，不是已选产品'},
        {'title':'博世KAN系列官方说明书','url':'https://media3.bosch-home.com/Documents/8001142358_B.pdf','use':'说明普通机型可要求两侧100、顶部300等较大散热空隙；不能把零嵌尺寸套用到普通机型'},
        {'title':'ERCO餐厨照明设计','url':'https://www.erco.com/en_us/knowledge/fundamentals/the-best-light-for-living-and-working-learning-path-2/cooking-and-dining/','use':'暖白可调光、区分工作与氛围，控制柜面反射眩光'},
    ],
    'master_sha256_before':BASELINE,
    'image_generation':{'tool':'built-in image_gen','type':'photorealistic concept comparison diptychs','exact_dimensions_governed_by':'JSON parameters and SVG elevations, not inferred pixels','ai_images_are_not_shop_drawings':True},
}

def esc(s): return html.escape(str(s))

def elevation(s):
    # All geometry in mm, deterministically drawn independently from AI views.
    out=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 4250 3450" role="img">',
         '<defs><pattern id="vents" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M0 10H20" stroke="#7b7c78" stroke-width="4"/></pattern></defs>',
         '<rect width="4250" height="3450" fill="#faf9f5"/>',
         '<style>text{font-family:Microsoft YaHei,Arial,sans-serif;fill:#303832}.dim{stroke:#70786d;stroke-width:3;fill:none}.join{stroke:#7a8076;stroke-width:2}</style>']
    x0,y0=240,300
    def box(x,y,w,h,fill,stroke='#777f73'):
        out.append(f'<rect x="{x+x0}" y="{y0+2750-y-h}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="3"/>')
    def text(x,y,t,size=37,anchor='middle'):
        out.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}">{esc(t)}</text>')
    text(240,100,f'{s["id"]}  {s["name"]}｜独立立面参数，非加工图',54,'start')
    text(240,165,'单位 mm · 2750为模型暂拟完成面 · 左靠客厅，右靠餐厨门',32,'start')
    box(0,0,3400,2750,'#ebe8df')
    box(0,0,50,2750,s['upperColor']); box(3350,0,50,2750,s['upperColor'])
    box(50,0,1200,2200,'#646a65')
    box(68,0,1164,2200,'#515952')
    box(190,0,920,1850,'#414747')
    box(648,0,4,1850,'#171f1d')
    box(68,1850,1164,350,'url(#vents)')
    box(50,2200,1200,500,s['upperColor'])
    box(649,2200,2,500,'#a5a79c')
    box(0,2700,3400,50,s['upperColor'])
    cx=1250; cw=s['coffee']; ch=s['counter']; n=s['niche']; f=s['flap']; u=s['upper']
    box(cx,0,cw,80,'#73776d'); box(cx,80,cw,ch-100,s['base']); box(cx,ch-20,cw,20,'#d8d5cc')
    box(cx,ch,cw,n,s['back']); box(cx,ch+n,cw,f,s['dark']); box(cx,ch+n+f,cw,u,s['upperColor'])
    # Upper divisions and horizontal flap divisions follow module widths.
    steps=5 if s['id']=='B' else (4 if s['id']=='A' else 3)
    for i in range(1,steps): box(cx+cw*i/steps-1,ch+n+f,2,u,'#a5a79c')
    for i in range(1,(3 if s['id']=='B' else 2)): box(cx+cw*i/(3 if s['id']=='B' else 2)-1,ch+n,2,f,'#a5a79c')
    if s['id']=='B':
        for dx in [700,1400,2000]: box(cx+dx,80,2,ch-100,'#6c7f69')
        drawer_x,drawer_w=cx,700
    else:
        split=cw/2
        box(cx+split,80,2,ch-100,'#8b8d80'); box(cx+split/2,80,2,ch-100,'#8b8d80')
        drawer_x,drawer_w=cx+split,split
    for i in [1,2]: box(drawer_x,80+(ch-100)*i/3,drawer_w,2,'#8b8d80')
    if s['display']:
        dx=cx+cw; dw=s['display']
        box(dx,0,dw,80,'#73776d'); box(dx,80,dw,ch-80,s['base'])
        box(dx,ch,dw,2200-ch,s['displayBack']); box(dx+16,ch+16,dw-32,2200-ch-32,'#d5e1dc80')
        for i in range(1,4): box(dx+18,ch+(2200-ch)*i/4,dw-36,9,'#aabfb7')
        box(dx,2200,dw,500,s['upperColor'])
    # Labelled widths.
    cursor=0
    for label,w in s['modules']:
        if w>50:
            text(x0+cursor+w/2,3230,f'{label} {w}',35)
        cursor+=w
    out.append(f'<path class="dim" d="M{x0} 3300H{x0+3400}M{x0} 3265V3335M{x0+3400} 3265V3335"/>')
    text(x0+1700,3400,'总宽3400（含两端各50收口/调整带）',38)
    text(x0+650,3110,'冰箱机身920×750×1850',31)
    text(x0+650,3160,'洞口净1164宽 / 2200高',31)
    text(x0+cw/2+1250,3110,'台面深450 / 上柜深320 / 薄柜深250',33)
    # Height annotations at right.
    dimx=3840
    top=2750
    segments=[('顶部收口',50),('上柜',u),('薄柜',f),('操作净高',n),('台面完成高',ch)]
    for label,h in segments:
        y1=y0+2750-top; y2=y1+h
        out.append(f'<path class="dim" d="M{dimx} {y1}V{y2}M{dimx-18} {y1}H{dimx+18}M{dimx-18} {y2}H{dimx+18}"/>')
        text(dimx+45,(y1+y2)/2+12,f'{label} {h}',31,'start')
        top-=h
    out.append('</svg>')
    return '\n'.join(out)

for s in SCHEMES:
    assert sum(w for _,w in s['modules'])==3400
    assert s['counter']+s['niche']+s['flap']+s['upper']+50==2750
    (OUT/f'{s["id"]}-参数立面.svg').write_text(elevation(s),encoding='utf-8')

# Diagnostic plan: the master is never edited. This overlay makes the conflict explicit.
plan='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1160 1120">
<defs><pattern id="overlap" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="10" stroke="#ad5649" stroke-width="4"/></pattern></defs>
<rect width="1160" height="1120" fill="#faf9f5"/><style>text{font-family:Microsoft YaHei,Arial,sans-serif;fill:#303832;font-size:23px}.plan-label{font-size:85px}</style>
<text x="45" y="50" font-size="32">位置核对｜独立叠加，不修改v19</text>
<text x="45" y="88">上：客厅端　下：餐厨推拉门　左：通长柜　右：用户红框墙</text>
<g transform="translate(105 125) scale(.24)">
<rect x="-100" y="0" width="100" height="3545" fill="#93998d"/>
<rect x="3082" y="0" width="120" height="3545" fill="#93998d"/>
<rect x="0" y="0" width="400" height="3410" fill="#e3cda4" stroke="#9e956f" stroke-width="6"/>
<rect x="2282" y="72.5" width="800" height="1250" fill="#929f9f" fill-opacity=".7" stroke="#586d6c" stroke-width="6"/>
<rect x="2632" y="1322.5" width="450" height="2150" fill="#b4c6ac" fill-opacity=".8" stroke="#718967" stroke-width="6"/>
<rect x="2282" y="1210" width="800" height="1600" fill="#ddc6a3" stroke="#6c604c" stroke-width="8"/>
<rect x="2632" y="1322.5" width="450" height="1487.5" fill="url(#overlap)"/>
<rect x="2282" y="1210" width="800" height="112.5" fill="url(#overlap)"/>
<g fill="#ccd4c7" stroke="#6b7666" stroke-width="6"><rect x="1832" y="1460" width="450" height="450"/><rect x="1832" y="2110" width="450" height="450"/><rect x="2457" y="760" width="450" height="450"/><rect x="2457" y="2810" width="450" height="450"/></g>
<path d="M1391 3545H3082" stroke="#7ba2ae" stroke-width="30"/>
<rect x="2457" y="760" width="450" height="450" fill="url(#overlap)"/>
<g><text class="plan-label" x="25" y="230">深400</text><text class="plan-label" x="2310" y="400">冰箱深800</text><text class="plan-label" x="2650" y="3400">柜深450</text><text class="plan-label" x="2300" y="2050">现餐桌</text></g></g>
<text x="930" y="435" fill="#aa5349">确定重叠</text><text x="930" y="470" fill="#aa5349">450 mm</text>
<text x="45" y="1040">柜体外形可容纳于墙长，但与现有餐桌不可直接叠放；图中未代表已经解决布局。</text>
<text x="45" y="1080">模型长度3545 mm；现场尺寸及冰箱开门仍待核。参数以方案表为准。</text></svg>'''
(OUT/'位置与重叠核对.svg').write_text(plan,encoding='utf-8')

def table_row(k,v): return f'<tr><th>{esc(k)}</th><td>{esc(v)}</td></tr>'
cards=[]
for s in SCHEMES:
    widths='＋'.join(str(w) for _,w in s['modules'])
    rows=''.join(table_row(k,v) for k,v in [
        ('总尺寸','宽3400 × 高2750；常规下柜深450，上柜深320，冰箱门前沿总进深约800'),
        ('横向分段', widths+' mm（从客厅端到餐厨门端）'),
        ('四段高度',f'下柜完成面{s["counter"]}＋操作净高{s["niche"]}＋薄柜{s["flap"]}＋上柜{s["upper"]}＋顶封50 = 2750'),
        ('材料与色彩',s['materials']),('柜内安排',s['baseLayout']),
        ('弧度','台面外露边R40；B的固定端R70、壁龛肩部R120；其余以小圆角和直线为主，不把转角门板做成不可开启的整片'),
        ('照明分组','；'.join(s['lights'])+'；长度为设计意向，铝槽及接线端占位另定。'),
        ('取舍',s['tradeoff'])])
    cards.append(f'''<section id="scheme-{s['id']}" class="card"><div class="eyebrow">独立方案 {s['id']}</div><h2>{esc(s['name'])}</h2><p>{esc(s['mood'])}</p>
<a href="{s['id']}-开关灯对照.png" target="_blank"><img class="render" src="{s['id']}-开关灯对照.png" alt="{s['id']}方案，左全关灯右全开灯" loading="lazy"></a>
<p class="caption">左：全关灯　右：全开灯。同视角、同自然光。图片为AI辅助概念表现；精确分格与尺寸见下方立面。</p>
<table>{rows}</table><details><summary>查看可放大的尺寸立面</summary><a href="{s['id']}-参数立面.svg" target="_blank"><img class="diagram" src="{s['id']}-参数立面.svg" alt="{s['id']}参数立面"></a></details></section>''')

source_html=''.join(f'<li><a href="{esc(x["url"])}" target="_blank" rel="noreferrer">{esc(x["title"])}</a>：{esc(x["use"])}</li>' for x in DATA['sources'])
page='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>餐边柜三套独立方案｜开关灯对照与参数</title>
<style>*{box-sizing:border-box}body{margin:0;background:#f5f4ee;color:#29322b;font:16px/1.85 "Microsoft YaHei",system-ui,sans-serif}main{max-width:1240px;margin:auto;padding:44px 30px 70px}h1{font-size:clamp(27px,4vw,44px);line-height:1.3;margin:10px 0 20px;font-weight:600}h2{font-size:28px;margin:6px 0}p{margin:12px 0}.eyebrow{letter-spacing:.16em;font-size:13px;color:#73806f}.notice{border-left:4px solid #8b9d7e;background:#e9ede3;padding:18px 22px;border-radius:0 12px 12px 0}nav{display:flex;gap:12px;flex-wrap:wrap;margin:25px 0}nav a,.download{display:inline-block;background:white;padding:10px 20px;border:1px solid #d4d9cd;border-radius:24px;color:inherit;text-decoration:none}a{color:#436b58;text-underline-offset:4px}.card{background:#fffefa;border:1px solid #dce1d5;border-radius:18px;padding:25px;margin:30px 0}.render{width:100%;display:block;margin-top:23px;border-radius:10px}.caption{color:#72796f;font-size:14px}table{width:100%;border-collapse:collapse;margin:25px 0}td,th{border-bottom:1px solid #e4e7df;text-align:left;vertical-align:top;padding:13px 12px}th{width:145px;font-weight:500;color:#60715a}summary{cursor:pointer;color:#436b58;padding:12px 0}.diagram{display:block;width:100%;background:#faf9f5;border-radius:10px}ul{padding-left:25px}.warning{border-left-color:#ae7c59;background:#f5ece0}footer{color:#7b8377;font-size:13px}@media(max-width:600px){main{padding:23px 14px}.card{padding:15px}td,th{display:block;width:100%;padding:8px 0}th{border-bottom:0;padding-bottom:0}nav a{padding:8px 14px}h2{font-size:24px}}@media print{body{background:white}.card{break-inside:avoid}details>summary,nav,.download{display:none}details>img{display:block}main{padding:10mm}}</style></head><body><main>
<div class="eyebrow">SIDEBOARD STUDY 01 · 2026.11.05</div><h1>餐边柜，三种表情</h1>
<p>餐厅靠客卫外侧的红框墙。沿用暖白、浅木和局部深木的现代日式底色，分别研究胡桃木、灰苔绿与深蓝展示的比例。</p>
<div class="notice"><strong>本次仅为独立柜体提案，三个方案均未选定、未融合主模型。</strong><br>v19及既有家具位置、效果图、VR保持不变；没有启动“实装v20”。</div>
<nav><a href="#scheme-A">A 暖白胡桃木</a><a href="#scheme-B">B 灰苔绿浅木</a><a href="#scheme-C">C 浅木深蓝</a><a href="#fit">位置与使用</a></nav>
<p>三套均按<strong>总宽3400 × 暂定高2750 mm</strong>；该墙模型长3545 mm，左右外部共余145 mm。标注总宽另含内部两端各50 mm收口调整带，现场完成面校核后重新分配。采用普通左右对开双门冰箱，外露金属机门，未假定为可贴门板的全嵌机。</p>
''' + '\n'.join(cards) + '''
<section class="card"><h2>冰箱及共通细节</h2><table>
<tr><th>冰箱体量</th><td>机身暂按宽920 × 深750 × 高1850。机型未定，属于设计包络，不是“所有常规冰箱”的统一标准。</td></tr>
<tr><th>冰箱模块</th><td>外宽1200；两侧18板，净宽1164；洞口净高2200。按上述包络，左右各122、上方350。无柜底板，冰箱落地。侧围板深700，机门前沿距墙约800，突出围板约100以给铰链开门留出空间。</td></tr>
<tr><th>散热与检修</th><td>普通机型的半围合，顶部350区域不封死，不在冰箱上方假画“零缝隙”。顶柜自2200以上开始。后方暂留50，最终散热通道、侧距、顶距和抽屉取出角度以所选说明书校核；柜体不能封堵机背及底部进排风。</td></tr>
<tr><th>下柜与台面</th><td>下柜深450，台面20厚，板材18，踢脚80高并内退60；柜内净深须扣背板及五金。门缝2 mm是选型目标，施工依材料与系统调整。台面外露边R40；固定外露端局部圆弧，直线为骨架。</td></tr>
<tr><th>操作电器</th><td>图中咖啡机、烧水壶为台面用途示意，没有擅自加入蒸烤箱、微波炉、消毒柜或水槽。电器顶盖开启、接水、线缆弯折及散热随型号复核；620–650净高不代表所有机器都适配。</td></tr>
<tr><th>灯光选型目标</th><td>3000K统一色温，Ra≥90；灯带藏入带扩散罩的铝槽，遮挡坐姿直视，避免台面高光反射。工作、展示/局部洗墙、低位三组分别调光。驱动器置于可检修柜格，灯槽和散热路径分开。</td></tr>
<tr><th>电源与使用</th><td>冰箱电源与台面电源分开安排，插头设在可触及的侧方检修位，不用压在冰箱正后方导致额外突出；具体负荷、保护及插座规格交由实际设备和电气设计确定。</td></tr>
</table></section>
<section class="card" id="fit"><h2>柜体放得下，餐桌关系仍须重排</h2>
<div class="notice warning"><strong>确定冲突：现有餐桌长边直接贴着该墙，下柜450深会与餐桌重叠。</strong><br>冰箱更深，靠客厅端现有端椅也受影响。此次没有移动餐桌或椅子，下面是诊断叠加图。</div>
<img class="diagram" src="位置与重叠核对.svg" alt="现有餐桌与拟议餐边柜重叠诊断">
<p>模型横向宽3082，试算扣除对侧柜400、餐椅450、餐桌800、柜前操作参考带900、新柜450后，仅余82 mm。因此不能把“餐桌向左挪450”当作已经解决：它只是消除实体重叠，还没有腾出取物、拉椅及通行空间。900是本轮设计试算，不是引用规范。</p>
<p>选定柜体方向后，需要另做餐桌朝向与四椅组合、对侧柜局部范围、柜前取物和冰箱开门的协调研究；沿用此次3400外形也不代表会直接覆盖现位。若坚持全部家具原位，该整面落地餐边柜不能按图直接实装。</p></section>
<section class="card"><h2>参考如何转为本项目设计</h2><p>参考图中的四段组织、上浅下深、薄柜、三抽及小面积玻璃展示被转化为以上三套；图片上的60 cm深、92 cm高、400×800凳位等不是强制参数，本次没有照搬凳位，也没有改变现有餐厨推拉门。</p>
<p>建议先比较A与B：A最连贯、B的自然气质更明显；C适合希望餐厅有更鲜明的蓝色标记。三者不以预算排序，均未视为业主已选。</p><ul>''' + source_html + '''</ul>
<p class="caption">效果图由内置image_gen生成，用于材质、比例与开关灯氛围判断。尺寸、模块数量与灯槽位置以参数JSON及立面SVG为设计基准；AI画面的细微分缝、比例或光色可能有偏差，不可按图量尺加工。</p>
<a class="download" href="design-parameters.json">完整参数JSON</a> <a class="download" href="generation-prompts.json">图像提示词与来源</a></section>
<footer>独立方案研究01｜全部单位mm｜原始图、提示词和模型未改动验证随文件保存｜未更新主模型或VR</footer></main></body></html>'''
(OUT/'餐边柜三套方案.html').write_text(page,encoding='utf-8')

after={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in BASELINE}
assert after==BASELINE, 'Master baseline changed; investigate before delivery.'
DATA['master_sha256_after']=after
DATA['master_unchanged_verified']=True
images=[]
for s in SCHEMES:
    path=OUT/f'{s["id"]}-开关灯对照.png'
    if path.exists():
        b=path.read_bytes(); assert b[:8]==b'\x89PNG\r\n\x1a\n'
        w,h=struct.unpack('>II',b[16:24]); images.append({'scheme':s['id'],'file':path.name,'width':w,'height':h,'sha256':hashlib.sha256(b).hexdigest()})
DATA['image_files']=images
(OUT/'design-parameters.json').write_text(json.dumps(DATA,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'verification.json').write_text(json.dumps({'master_files_unchanged':True,'before':BASELINE,'after':after,'dimensions_and_modules_checked':True,'images':images},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'output':str(OUT),'schemes':len(SCHEMES),'images':images,'master_unchanged':True},ensure_ascii=False))
