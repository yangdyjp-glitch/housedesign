"""Package the verified rounded-edge style model and its current render evidence."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,zipfile
from PIL import Image

ROOT=Path(r'D:\AI-Yang.cn\HomeDesign')
OUT=ROOT/'07_renders/v06-japanese-v02'
readback=json.loads((ROOT/'logs/japanese-v02-readback.json').read_text(encoding='utf-8'))
render=json.loads((ROOT/'logs/japanese-v02-render.json').read_text(encoding='utf-8'))
style_file=ROOT/'05_style/modern-japanese-v02.json'
style_raw=style_file.read_bytes();style=json.loads(style_raw)
style_sha=hashlib.sha256(style_raw).hexdigest()
assert readback['saved_model_reopened'] and readback['major_furniture_count']==14
assert render['major_furniture_count']==14 and len(render['movement_100mm'])==14
assert render['style_sha256']==readback['style_sha256']==style_sha
assert hashlib.sha256((ROOT/'02_geometry/geometry-master.json').read_bytes()).hexdigest()==style['geometry_sha256']
original_dir=Path(r'C:\Users\Administrator\.codex\generated_images\01a187d1-69cc-73a1-805e-834e8e8bb476')
originals={'living':'exec-29876b52-1402-4723-a923-4ab3dae7cb04.png',
           'office':'exec-75b0d6bf-7508-4e11-a914-41d68e5a5b8a.png',
           'dining':'exec-9d3972bd-bf93-46ad-9633-9849ee5dda35.png'}
images=[]
for view in ['office','living','dining','office-detail']:
    for kind in ['cycles']+(['photoreal-v02'] if view!='office-detail' else []):
        path=OUT/f'{view}-{kind}.png'
        with Image.open(path) as im:im.verify()
        with Image.open(path) as im:width,height=im.size;image_format=im.format
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        row=dict(view=view,kind=kind,file=str(path),sha256=digest,width=width,height=height,format=image_format,
                 saved_image_visually_inspected=True)
        if kind=='cycles':row.update(actual_mode='Blender 4.5.15 LTS, Cycles OptiX GPU, 128 samples',geometry_base_sha256=style['geometry_sha256'],style_sha256=style_sha)
        else:
            original=original_dir/originals[view]
            assert digest==hashlib.sha256(original.read_bytes()).hexdigest()
            row.update(actual_mode='built-in imagegen, local reference image edit',original=str(original),
                       reference=str(OUT/f'{view}-cycles.png'),prompt_file=str(OUT/f'{view}-imagegen-prompt.txt'))
        images.append(row)

aesthetic=dict(method='user-text brief + six visual dimensions (0–10), equal weights; design judgment, not measurement',
    target='modern Japanese minimal, warm neutral/oak base, rounded edges, limited sage/navy',
    image_board_status='No separate image moodboard was selected; no image similarity percentage or prior-score delta claimed',
    findings={
      'office':dict(first_impression='温暖、克制、圆润，绿色与深蓝形成小面积焦点',ratings=dict(色调=9,用材=8.5,构图=8.5,新颖度=7.5,视觉冲击力=7.5,现代感=8.5),evidence='R100茶几、两只点色抱枕、单椅双工位、灰绿与深蓝书脊、局部弧形墙端均可见'),
      'living':dict(first_impression='暖白收纳连续，留白平静，圆角桌面柔化前景',ratings=dict(色调=8.5,用材=8.5,构图=8,新颖度=7.5,视觉冲击力=7.5,现代感=8.5),evidence='电视墙和高低柜关系保留；AI版本增加了一个抱枕及少量书本，并显露了更多椅子，属于软装/遮挡表现差异，不能反推几何'),
      'dining':dict(first_impression='浅木与暖白为主，绿色坐垫点缀，弧形墙端清晰',ratings=dict(色调=8.5,用材=8.5,构图=8,新颖度=7.5,视觉冲击力=7,现代感=8.5),evidence='四椅靠墙关系保留，近端桌角与背景墙端为弧形，窄置物格保留深蓝浅托盘')},
    visual_differences='AI loose styling, chair-back upholstery, exterior and exact small radii may vary. Use saved Cycles/model for geometry; photos are style illustrations.')
practical=dict(independent_method='Separate geometry/use review using saved model readback, not aesthetic ratings',
    passed=['14 major furniture placements and physical dimensions preserved','X/Y 100mm operator tests restored all 14 items',
            'all 12 table legs remain within rounded tabletop projections','four visible wall finish profiles stay within baseline wall envelopes',
            'full baseline of 60 walls and 8 glass panes retained','four dining chairs and one office chair retained'],
    retained_issue='Office chair to bookcase local gap remains 408mm; chair retreat and cabinet access still need use testing. No relocation made for rendering.',
    wall_status='Curved finish design intent; structural wall cutting is not authorized or certified; substrate and actual finish build-up need site detailing.',
    baseline_uncertainties='Sketch dimensions not closed; measured height and exact entrance opening remain provisional.')
manifest=dict(created_utc=datetime.now(timezone.utc).isoformat(),version='v06 modern-japanese style v02',
    user_selected_style=True,geometry_base_sha256=style['geometry_sha256'],style_sha256=style_sha,
    model=str(ROOT/'06_blender/home-v06-japanese-v02.blend'),baseline_model_retained=str(ROOT/'06_blender/home-main-v06.blend'),
    actual_workflow='4 local Blender Cycles physical renders + 3 built-in imagegen material refinements',images=images,
    skills=['home-design-director','interior-design-expert','xiong-interior-design','interior-design-visualizer','imagegen','interior-designer','moodboard-aesthetic-iteration'],
    imagegen_correction_calls=0,aesthetic_review=aesthetic,practical_review=practical,
    max_furniture_envelope_error_mm=max(row['bounds_error_mm'] for row in render['furniture']),
    interactive_html='Existing v06 chat widget remains its layout proxy; this update saves the styled, rounded Blender model. No claim of a live two-way sync.')
(OUT/'render-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')

note='''现代日式简约 · 暖色圆角版 v02

用户方向已记录：简约现代日式、暖色主调、桌子尽可能圆角、外露墙角尽可能采用弧线，可使用绿色和深蓝。

这一版的设计
奶油暖白墙面和平整柜门，浅橡木桌面及地板，米灰/燕麦布艺。绿色与深蓝控制在软装小面积点缀，不扩大成深色整墙或大柜面。
茶几1400×700×400、餐桌1600×800×750，桌面平面圆角R100mm；双人桌2400×700×750，平面圆角R70mm。桌面保留直线中段，餐桌长边继续靠墙，保留四椅。
客卫外侧转角、入户短墙端、主卧隔墙外露端头采用约R50–80mm的局部垂直弧形饰面意向；门窗开口和吊顶主线保持原有关系。
弧面位于现有墙体显示包络内，原60段墙体基线仍完整隐藏备查。这是饰面造型表达，不是结构墙削切指令；基层及最终做法按现场深化。
新模型共有14件可整件选择的主要家具，已逐件实测X/Y方向100mm移动并恢复原位。两只抱枕并入沙发整件移动。原尺寸、位置、朝向均接续。
办公椅至书柜408mm的原有局部净距保留，后续仍需体验椅子后退与取物，不为效果图自动移位。

文件
四张 *-cycles.png 是新模型的实际实体材质渲染，1800×1200。
三张 *-photoreal-v02.png 是以内置imagegen按对应实体图细化的风格示意，1536×1024。
office-photoreal-v02.png 为主要风格视角；living为电视方向，dining为餐厅方向。
写实图的抱枕、书本、小摆件、椅背软包和窗外景观可能有图像变化，具体数量、精确圆角及摆放以实体模型/Cycles图为准。living图增加的少量软饰未导回模型。
三份 *-imagegen-prompt.txt 为实际提示词，render-manifest.json 记录原图、参考图、实际模式、文件哈希和审美/实用性检查。

当前造型模型：home-v06-japanese-v02.blend；空间尺寸基线仍为geometry-master-v06.json，另加modern-japanese-v02.json造型与材质参数。
原home-main-v06.blend与v01渲染保留。聊天中的v06交互平面仍用于布局移动，不声称已实时同步本轮造型；后续接续以活动Blender模型、造型参数和最新位置为准。
'''
(OUT/'设计与渲染说明.txt').write_text(note,encoding='utf-8')

cards=[]
for view,title,caption in [('office','暖色现代日式 · 客厅与办公','圆角茶几 · 苔绿与深蓝 · 沙发后双人桌'),('living','电视与连续收纳','暖白柜面 · 浅木台面 · 弧形转角'),('dining','圆角四人餐桌','两张浅绿坐垫 · 靠墙长直边 · 弧形墙端')]:
    cards.append(f'<section><h2>{title}</h2><p>{caption}</p><a href="{view}-photoreal-v02.png"><img src="{view}-photoreal-v02.png" alt="{title}"></a><details><summary>查看实体材质渲染</summary><img loading="lazy" src="{view}-cycles.png" alt="{title}实体渲染"></details></section>')
html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>现代日式 · 暖色圆角 v02</title><style>*{box-sizing:border-box}body{margin:0;background:#f5f1e9;color:#3f443c;font:16px/1.7 "Microsoft YaHei",sans-serif}main{max-width:1160px;padding:40px 24px;margin:auto}h1{font-size:clamp(28px,4vw,42px);line-height:1.3}h2{margin:0;font-size:25px}p,small{color:#737966}header{padding-bottom:30px;border-bottom:1px solid #d4d5c9}section{margin:40px 0}img{width:100%;height:auto;display:block;border-radius:10px}details{padding-top:12px}summary{cursor:pointer;color:#61745a;padding:8px 0}a{color:#435b6b;text-underline-offset:4px}footer{font-size:14px;border-top:1px solid #d4d5c9;padding-top:24px}</style><main><header><small>HOME DESIGN / V06 / STYLE 02</small><h1>暖白、浅木与柔和弧线</h1><p>现代日式简约，绿色和深蓝作小面积点缀。</p></header>'''+''.join(cards)+'''<section><h2>双工位 · 一把椅子</h2><p>2400×700×750mm，沿用原位置，桌角R70mm。</p><img loading="lazy" src="office-detail-cycles.png" alt="单椅双人桌圆角实体渲染"></section><footer>写实图用于风格表现；软饰细节、窗外景观与精确圆角以实体模型为准。<br><a href="设计与渲染说明.txt">设计与渲染说明</a> · <a href="render-manifest.json">出图与核对记录</a></footer></main></html>'''
(OUT/'查看效果.html').write_text(html,encoding='utf-8')

active_path=ROOT/'06_blender/active-model.json'
active=json.loads(active_path.read_text(encoding='utf-8'))
assert active['revision']==6 and active['geometry_sha256']==style['geometry_sha256']
active.update(filename='home-v06-japanese-v02.blend',baseline_filename='home-main-v06.blend',
              style='05_style/modern-japanese-v02.json',style_sha256=style_sha,style_revision='modern-japanese-v02')
active_path.write_text(json.dumps(active,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
package=ROOT/'09_delivery/v06-现代日式暖色圆角-v02.zip'
files=[OUT/'查看效果.html',OUT/'设计与渲染说明.txt',OUT/'render-manifest.json']+[Path(i['file']) for i in images]
files += [OUT/f'{name}-imagegen-prompt.txt' for name in ['office','living','dining']]
files += [ROOT/'06_blender/home-v06-japanese-v02.blend',ROOT/'02_geometry/geometry-master-v06.json',style_file,
          ROOT/'logs/japanese-v02-render.json',ROOT/'logs/japanese-v02-readback.json']
with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
    for p in files:
        folder='图集' if p.parent==OUT else ('模型' if p.suffix=='.blend' else '参数与核对')
        archive.write(p,(Path(folder)/p.name).as_posix())
with zipfile.ZipFile(package) as archive:assert archive.testzip() is None
print(json.dumps(dict(images_verified=len(images),model_reopened=True,furniture=14,style=active['style_revision'],
                      package=str(package),package_bytes=package.stat().st_size),ensure_ascii=True))
