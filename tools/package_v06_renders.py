"""Validate final image assets and produce a portable, local review package."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import zipfile
from PIL import Image

ROOT=Path(r'D:\AI-Yang.cn\HomeDesign')
OUT=ROOT/'07_renders'/'v06-realistic-v01'
EXPECTED='fea1569ed8142ca0eff6872dec83569a62130520e643880d84a3bdf624584b4b'
assert hashlib.sha256((ROOT/'02_geometry/geometry-master-v06.json').read_bytes()).hexdigest()==EXPECTED
assert hashlib.sha256((ROOT/'02_geometry/geometry-master.json').read_bytes()).hexdigest()==EXPECTED
active=json.loads((ROOT/'06_blender/active-model.json').read_text(encoding='utf-8'))
assert active['filename']=='home-main-v06.blend'
physical=json.loads((ROOT/'logs/v06-material-render.json').read_text(encoding='utf-8'))
assert physical['furniture_count']==14 and physical['parts']==206
assert max(row['bounds_error_mm'] for row in physical['furniture_audit'])<0.001
originals={
    'office':'exec-21415363-4c10-470f-846e-5dcad66c8322.png',
    'living':'exec-501e6a21-2fa2-4917-a15f-9e47aed08d4c.png',
    'dining':'exec-09784dbb-22f9-4332-a1a7-d943551b3559.png',
}
generated=Path(r'C:\Users\Administrator\.codex\generated_images\01a187d1-69cc-73a1-805e-834e8e8bb476')
images=[]
for view in ['living','office','dining','office-detail']:
    kinds=['cycles']+(['photoreal-v01'] if view!='office-detail' else [])
    for kind in kinds:
        path=OUT/f'{view}-{kind}.png'
        with Image.open(path) as im:im.verify()
        with Image.open(path) as im:size=im.size;mode=im.mode
        sha=hashlib.sha256(path.read_bytes()).hexdigest()
        row=dict(view=view,kind=kind,file=str(path),width=size[0],height=size[1],color_mode=mode,sha256=sha,visually_inspected=True)
        if kind=='photoreal-v01':
            original=generated/originals[view]
            assert sha==hashlib.sha256(original.read_bytes()).hexdigest()
            row.update(mode='built-in imagegen; local reference image edit',original=str(original),
                       reference=str(OUT/f'{view}-cycles.png'),prompt_file=str(OUT/f'{view}-imagegen-prompt.txt'),
                       reference_role='actual v06 Cycles render: architecture, placement, camera and composition anchor')
        else:row.update(mode='Blender 4.5.15 LTS Cycles; OptiX; 128 samples; 1800x1200',geometry_anchor=EXPECTED)
        images.append(row)

manifest=dict(created_utc=datetime.now(timezone.utc).isoformat(),revision='v06 material study v01',
              skills=['home-design-director','interior-design-visualizer','imagegen'],
              actual_generation_mode='four local Cycles physical renders, then three built-in imagegen reference edits',
              source_geometry_sha256=EXPECTED,current_main_model=str(ROOT/'06_blender/home-main-v06.blend'),
              presentation_copy=str(ROOT/'06_blender/home-v06-presentation-v01.blend'),
              canonical_model_and_interactive_layout_unchanged=True,
              images=images,
              qa=dict(physical_furniture_count=14,physical_parts=206,
                      max_native_bounds_error_mm=max(r['bounds_error_mm'] for r in physical['furniture_audit']),
                      photographed_critical_relations='visually compared against the corresponding saved Cycles view',
                      checks=['L chaise at balcony end','desk behind sofa; single office chair','two workstations face TV',
                              '85-inch TV wall composition','continuous tall-to-low cabinet connection',
                              'four dining chairs, table long edge against wall; no bench','entry-end narrow niche'],
                      targeted_imagegen_corrections=0,
                      limits=['AI material/atmosphere images do not certify exact dimensions',
                              'AI fine seams, small styling objects and the blurred exterior are illustrative',
                              'use geometry and Cycles images for exact dimensions and furniture positions',
                              'net height, entrance opening and unclosed sketch dimensions remain provisional',
                              '408 mm office-chair/bookcase gap retained; no layout relocation for rendering']))
(OUT/'render-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')

cards=[]
for view,title,caption in [
    ('living','电视墙与通长收纳','85英寸电视 · 入口端窄置物格 · 连续高低柜'),
    ('office','客厅与沙发后办公区','阳台端贵妃位 · 双人桌暂放一椅 · 书柜'),
    ('dining','靠墙四人餐厅','1600×800餐桌 · 四把独立餐椅 · 无卡座')]:
    cards.append(f'<section id="{view}"><h2>{title}</h2><p>{caption}</p>'
                 f'<figure><a href="{view}-photoreal-v01.png"><img src="{view}-photoreal-v01.png" alt="{title}写实效果"></a><figcaption>写实效果 · 材质与光线表现</figcaption></figure>'
                 f'<details><summary>查看同视角实体渲染</summary><figure><a href="{view}-cycles.png"><img loading="lazy" src="{view}-cycles.png" alt="{title}实体渲染"></a><figcaption>Blender Cycles · 沿用v06模型的尺寸和位置</figcaption></figure></details></section>')
html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>v06 · 家居材质渲染</title><style>
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#f5f2ed;color:#383b37;font:16px/1.7 "Microsoft YaHei",sans-serif}main{max-width:1180px;margin:auto;padding:38px 24px}header{padding:12px 0 32px;border-bottom:1px solid #d6d2c8}small{letter-spacing:.13em;color:#767b72}h1{font-size:clamp(26px,4vw,44px);line-height:1.3;margin:.5em 0}h2{font-size:26px;margin:0}p{color:#73766e}nav{display:flex;flex-wrap:wrap;gap:20px}a{color:#4a6253;text-underline-offset:5px}section{margin-top:46px}section>p{margin:4px 0 20px}figure{margin:0}img{width:100%;height:auto;display:block;border-radius:8px;background:#ded8cf}figcaption{font-size:14px;color:#72776c;padding:10px 0 18px}summary{cursor:pointer;padding:12px 0;color:#4a6253}details[open]{padding-bottom:12px}footer{padding-top:38px;margin-top:30px;border-top:1px solid #d6d2c8;font-size:14px;color:#73766e}
</style><main><header><small>HOME DESIGN / V06 / MATERIAL STUDY 01</small><h1>浅橡木、暖白与米灰布艺</h1><p>沿用当前家具布局，呈现客厅、办公区、电视收纳与餐厅的材质和光线。</p><nav><a href="#living">电视与收纳</a><a href="#office">客厅与办公</a><a href="#dining">四人餐厅</a><a href="#office-detail">办公细节</a></nav></header>'''+''.join(cards)+'''
<section id="office-detail"><h2>双工位，暂放一把椅子</h2><p>2400长 × 700深 × 750桌高，单位mm。现有家具位置保留。</p><figure><a href="office-detail-cycles.png"><img loading="lazy" src="office-detail-cycles.png" alt="办公区单椅实体渲染"></a><figcaption>Blender Cycles 实体渲染</figcaption></figure></section>
<footer>写实效果由实体模型渲染图经图像表现细化，材质、细小物件和窗外景观为示意；精确摆放与尺寸以v06实体模型为准。<br>原主模型和100mm交互移动功能保持原状。<br><a href="渲染说明.txt">渲染说明</a> · <a href="render-manifest.json">版本与出图记录</a></footer></main></html>'''
(OUT/'查看效果.html').write_text(html,encoding='utf-8')

package=ROOT/'09_delivery'/'v06-实体渲染与写实效果-v01.zip'
files=[OUT/'查看效果.html',OUT/'渲染说明.txt',OUT/'render-manifest.json']
files += [Path(r['file']) for r in images]
files += [OUT/f'{v}-imagegen-prompt.txt' for v in ['living','office','dining']]
files += [ROOT/'06_blender/home-v06-presentation-v01.blend',ROOT/'02_geometry/geometry-master-v06.json',ROOT/'logs/v06-material-render.json']
with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
    for path in files:
        if path.parent==OUT:arc=Path('图集')/path.name
        elif path.suffix=='.blend':arc=Path('模型')/path.name
        else:arc=Path('核对记录')/path.name
        archive.write(path,arc.as_posix())
with zipfile.ZipFile(package) as archive:
    assert archive.testzip() is None
print(json.dumps(dict(images_verified=len(images),imagegen_copies_identical=True,zip=str(package),bytes=package.stat().st_size,
                      max_native_bounds_error_mm=manifest['qa']['max_native_bounds_error_mm'],active_main_model=active['filename']),ensure_ascii=False))
