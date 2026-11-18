from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote
import json,hashlib
from PIL import Image
root=Path('D:/AI-Yang.cn/HomeDesign');out=root/'09_delivery/sideboard-U-study-10'
spec=json.loads((out/'U-layout-parameters.json').read_text(encoding='utf-8'));rb=json.loads((out/'model-readback.json').read_text(encoding='utf-8'))
class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        for k,v in attrs:
            if k in ('href','src') and v and not v.startswith(('#','http:','https:')):self.links.append(v)
p=Links();p.feed((out/'端头起步与餐臂加长.html').read_text(encoding='utf-8'))
assert all(v=='verification.json' or (out/unquote(v)).resolve().is_file() for v in p.links)
images={}
for name in ('端头起步加长U-开关灯概念对照.png','端头起步加长U-实体关系参考.png','冰箱右门90度-几何试排.png','端头起步加长U-前后尺寸对照.png'):
    with Image.open(out/name) as im:
        assert im.format=='PNG';images[name]=dict(width=im.width,height=im.height,bytes=(out/name).stat().st_size);im.verify()
hashes={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in spec['main_baseline_sha256']}
assert hashes==spec['main_baseline_sha256']==rb['main_baseline_sha256_after']
assert rb['visible_seat_count']==0 and rb['default_frame']==1
assert rb['raw_top_manifold'] and rb['top']['h']==[850,880]
assert spec['designer_dimensions']['new_root']==1200 and spec['designer_dimensions']['new_far_end']==2600
assert spec['dining_U']['outside_dining_arm']==[1400,600] and spec['dining_U']['inner_clear_length']==950
assert 3472.5-2600==spec['clearances']['free_table_end_to_kitchen_boundary_without_seats']==872.5
assert rb['fridge90_proxy']['u'][1]<1200
result=dict(date='2026-11-06',scope='independent10 cabinetry/U shape only; latest seating deferral respected',
    main_model_unchanged=True,v20_started=False,frozen_main_files=hashes,
    saved_native_model_reopened=True,visible_seats=0,latent_seat_meshes_not_approved=True,
    geometry_checks=dict(root1200=True,far_end2600=True,continuous880_top=True,watertight_raw_top=True,
        inner600_by950=True,no_seat_assessment_claimed=True,fridge90_proxy_only=True),
    images=images,offline_html_links_valid=True,browser_visual_preview_performed=False,
    visual_review=dict(method='direct saved image inspection: native shape, plan comparison, proxy-open and selected diptych',
        passed=['root begins at fridge-end cabinet edge','outer arm extended','open U and same pale oak','no seating','full-width niche and complete uppers retained','OFF/ON same furnishings'],
        limits=['one focused correction addressed apparent raised root seam; fine join line remains conceptual','countertop height and continuity authoritative in native model','generic appliance proxy; no selected coffee machine'],
        correction='correction-prompt.json',no_numeric_aesthetic_score=True),
    practical_review=dict(outer_unseated_gap=682,table_end_to_boundary_unseated=872.5,
        seating_deferred=True,fridge_full_sweep_unverified=True,
        pending=['real site dimensions','fridge full opening and drawers','later seating and body envelopes','upper pull-down station and selected mechanism','support engineering']),
    ai_tool='built-in image_gen',prompts=['generation-prompt.json','correction-prompt.json'])
(out/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(result='passed',frozen_main_files=len(hashes),visible_seats=0,image_count=len(images),root=1200,far_end=2600)))
