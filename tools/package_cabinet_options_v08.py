from pathlib import Path
from PIL import Image
import hashlib,json,shutil,zipfile
ROOT=Path(r'D:\AI-Yang.cn\HomeDesign');OUT=ROOT/'07_renders/v08-cabinet-options'
raw_paths={
 'A':r'C:\Users\Administrator\.codex\generated_images\01a187d1-69cc-73a1-805e-834e8e8bb476\exec-20978cba-1a8e-461a-a63d-833bdc358d23.png',
 'B':r'C:\Users\Administrator\.codex\generated_images\01a187d1-69cc-73a1-805e-834e8e8bb476\exec-07ffb33d-2d6d-4828-b9be-cc54bdf45e58.png',
 'C':r'C:\Users\Administrator\.codex\generated_images\01a187d1-69cc-73a1-805e-834e8e8bb476\exec-21d3a18a-0a1e-44c9-a166-5dcfabb6b2ac.png'}
images=[]
for option,raw in raw_paths.items():
    source=Path(raw);dest=OUT/('option-'+option.lower()+'-photoreal.png');shutil.copy2(source,dest)
    assert source.read_bytes()==dest.read_bytes()
    for kind,path in [('imagegen',dest),('Cycles',OUT/('option-'+option.lower()+'-cycles.png'))]:
        with Image.open(path) as im:im.verify()
        with Image.open(path) as im:size=im.size
        images.append(dict(option=option,kind=kind,path=path.relative_to(ROOT).as_posix(),dimensions=list(size),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),raw_source=str(source) if kind=='imagegen' else None))
manifest=json.loads((OUT/'cycles-manifest.json').read_text(encoding='utf-8'))
manifest.update(images=images,imagegen_mode='built-in',imagegen_calls=3,correction_calls=0,prompt_file='imagegen-prompts.json',
 selection_status='awaiting homeowner choice A / B / C',designer_recommendation='B, not homeowner selection',
 fixed_conditions=['4500x400 footprint and 21 furniture positions retained','corridor cabinet top 2750mm, zero ceiling gap','single 1200-1400mm niche preserved','remaining cabinets may have different finishes'],
 geometry_readback='logs/cabinet-options-v08-readback.json',
 visual_review=dict(top_joint='all three show matching scribe reaching ceiling',niche='one shallow niche at left in all three',
   A='sand-grey fronts and oak niche retained',B='olive fronts, one closed pale oak end bay and round end retained',C='cream upper and navy lower retained; walnut niche retained',
   differences='AI adjusted exterior foliage/reflections and fine surface grain. In B the prominence of slim inset pulls differs from the native image. Use Cycles/model for joints and dimensions.'))
(OUT/'render-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
pending=dict(status='awaiting-color-and-style-choice',scope='tv-high corridor cabinet beside TV only',
    homeowner_fixed_requirement='top meets ceiling, zero open gap; cabinet styles across home need not match',
    baseline_active_model='06_blender/home-main-v07.blend',option_manifest='07_renders/v08-cabinet-options/render-manifest.json',
    options=[dict(id=o['id'],name=o['name'],blend=o['blend'],geometry=o['geometry']) for o in manifest['options']],
    designer_recommendation='B',homeowner_selection=None,next_action='apply chosen finish and full-height cabinet to next main-model revision; preserve latest manual furniture positions')
(ROOT/'05_style/cabinet-options-v08/pending-selection.json').write_text(json.dumps(pending,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
files=[OUT/'render-manifest.json',OUT/'cycles-manifest.json',OUT/'imagegen-prompts.json',ROOT/'09_delivery/走廊通顶柜三套方案.md',ROOT/'04_reviews/走廊通顶柜候选复核.md',ROOT/'logs/cabinet-options-v08-readback.json',ROOT/'05_style/cabinet-options-v08/pending-selection.json']
files += [ROOT/i['path'] for i in images]
for o in manifest['options']:
    files += [Path(o['blend']),Path(o['geometry']),ROOT/'05_style/cabinet-options-v08'/('option-'+o['id'].lower()+'-style.json')]
dest=ROOT/'09_delivery/走廊通顶柜-三套候选方案.zip'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as archive:
    for file in files:archive.write(file,file.relative_to(ROOT).as_posix())
with zipfile.ZipFile(dest) as archive:assert archive.testzip() is None
print('CABINET_OPTIONS_SAVED',len(images),'images',str(dest))
