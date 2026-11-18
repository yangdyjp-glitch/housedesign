from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote
import json, hashlib
from PIL import Image

root=Path('D:/AI-Yang.cn/HomeDesign');out=root/'09_delivery/sideboard-L-study-08'
spec=json.loads((out/'L-layout-parameters.json').read_text(encoding='utf-8'))
readback=json.loads((out/'model-readback.json').read_text(encoding='utf-8'))
class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        for k,v in attrs:
            if k in ('href','src') and v and not v.startswith(('#','http:','https:')):self.links.append(v)
p=Links();p.feed((out/'齐平餐边柜与外端三椅.html').read_text(encoding='utf-8'))
missing=[v for v in p.links if v!='verification.json' and not (out/unquote(v)).resolve().exists()]
assert not missing,missing
image_info={}
for name in ('齐平柜-开关灯概念对照.png','齐平柜与外端三椅-实体关系参考.png','齐平柜-三椅全外置尺寸图.png'):
    path=out/name
    with Image.open(path) as im:
        image_info[name]=dict(format=im.format,width=im.width,height=im.height,bytes=path.stat().st_size)
        assert im.format=='PNG';im.verify()
current={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in spec['main_baseline_sha256']}
assert current==spec['main_baseline_sha256']
assert current==readback['main_baseline_sha256_after']
assert readback['visible_chair_count']==3 and readback['inner_strip_contains_no_chairs']
assert all(c['v']+c['d']<=2000 for c in spec['chairs'])
assert 3082-400-2000==spec['clearances']['outer_continuous_furniture_gap']==682
assert 1400-800==spec['clearances']['inner_retrieval_closed_front']==600
assert 3472.5-(2250+520)==spec['clearances']['kitchen_end_chair_back_to_boundary']==702.5
for key in ('fridge_doors','cabinet_front','upper_front'):
    assert all(b['v'][1]==800 for b in readback[key])
result=dict(date='2026-11-06',scope='independent08',main_model_unchanged=True,v20_started=False,
    frozen_main_files=current,checks=dict(saved_native_model_reopened=True,three_visible_chairs=True,
    three_chairs_at_two_exterior_ends=True,no_chairs_in_retrieval_notch=True,no_chairs_on_outer_long_edge=True,
    fridge_cabinet_upper_fronts_v800=True,cabinet_width2200_includes_end_panel=True,
    numeric_clearances_checked=True,images_decode=True,offline_html_links_valid=True),images=image_info,
    visual_review=dict(method='direct inspection of saved native reference, plan, and selected generated diptych',
        first_ai_draft='rejected: two chairs were placed on outer long edge, contrary to geometry',
        correction='one targeted correction; selected image has two sage living-end chairs and one navy kitchen-end chair',
        strengths=['aligned opaque elevation','four-stage hierarchy retained','empty inner notch','actual compact L and warm oak/walnut','same furnishings in OFF/ON'],
        limitations=['photographic image is a concept, not a pixel-accurate CAD view','coffee machine front details remain a generic appliance proxy','actual oak, fabric, light output and outdoor daylight unselected'],
        no_unfounded_scores=True),
    practical_review=dict(result='compact provisional plan, no circulation approval',
        outer_gap=682,inner_closed_gap=600,end_chair_back_gap=702.5,end_pullout250_gap=452.5,
        retained_opposite_cabinet=True,retained_entry_bench=True,spare_storage_unselected=True,
        pending=['real survey','fridge manual and full door sweep','drawer and human access together','structural support and fixing design']),
    browser_visual_preview_performed=False,
    ai_tool='built-in image_gen',generation_prompt='generation-prompt.json',correction_prompt='correction-prompt.json')
(out/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
assert (out/'verification.json').is_file()
print(json.dumps(dict(result='passed',images=image_info,main_files_unchanged=len(current),html_links=len(p.links)),ensure_ascii=False))
