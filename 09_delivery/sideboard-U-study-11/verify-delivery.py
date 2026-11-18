from pathlib import Path
from PIL import Image
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json,hashlib

ROOT=Path('D:/AI-Yang.cn/HomeDesign');OUT=ROOT/'09_delivery/sideboard-U-study-11'
spec=json.loads((OUT/'U-layout-parameters.json').read_text(encoding='utf-8'))
record=json.loads((OUT/'finish-model-readback.json').read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert record['baseline_after']=={p:sha(ROOT/p) for p in record['baseline_after']}
assert record['flush_root']['raw_mesh_vertex_height_levels_mm']==[850,880]
assert record['flush_root']['step_height_mm']==0 and record['flush_root']['material']=='walnut'
assert all('white refrigerator enamel' in v for v in record['fridge_materials'].values())
assert spec['dining_U']['outside_dining_arm']==[1800,550]
assert spec['dining_U']['inner_clear_width']==600 and record['visible_seat_count']==0
assert record['latest_blend_sha256']==sha(OUT/'短连接长餐台-胡桃白冰箱圆边-独立11.blend')
images=[]
for name in ['短连接长餐台-开关灯概念对照.png','胡桃白冰箱圆边-ON-实体参考.png','胡桃白冰箱圆边-OFF-实体参考.png','短连接长餐面-前后尺寸对照.png']:
 p=OUT/name
 with Image.open(p) as im:
  info=dict(file=name,size=list(im.size),format=im.format,sha256=sha(p));im.verify()
 images.append(info)
result=dict(date='2026-11-06',status='verified independent proposal; not applied to main',
 current_model='短连接长餐台-胡桃白冰箱圆边-独立11.blend',images=images,
 native_checks=dict(reopened=True,tabletop=[1800,550,880],connector_width=350,connector_total_projection=1150,inner_retrieval=600,root_step=0,right_end_radius=100,cabinet_overall_width=2200,visible_seats=0,main_baseline_unchanged=True),
 visual_review=dict(method='direct inspection of saved native ON/OFF and final photographic board',
 aesthetic=['walnut niche and table unified','white refrigerator and warm-white cabinets create lighter background','right vertical end rounded','long dining rail visually dominant over narrow connector','same daylight and furnishings OFF/ON'],
 geometry_authority='parameters and native model, not AI image pixels',
 concept_limits=['life-end200 overhang and support inset visually simplified by imagegen','some flap/reveal lines simplified','materials and light output are conceptual, not selected products or photometry'],
 numeric_aesthetic_score=None),
 pending=['real site dimensions','fridge product/full opening/ventilation','drawer and pull-down use station after last module reduction','seat/body envelopes and occupied passages','support frame design'],
 raw_model_readback='finish-model-readback.json',browser_visual_preview_performed=False)
(OUT/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
class Links(HTMLParser):
 def __init__(self):super().__init__();self.targets=[]
 def handle_starttag(self,tag,attrs):
  self.targets.extend(v for k,v in attrs if k in ['href','src'])
parser=Links();parser.feed((OUT/'短连接与长餐台.html').read_text(encoding='utf-8'))
missing=[]
for t in parser.targets:
 u=urlsplit(t)
 if u.scheme or not u.path:continue
 if not (OUT/unquote(u.path)).is_file():missing.append(t)
assert not missing,missing
result['offline_html_links_checked']=len(parser.targets);result['missing_local_links']=missing
(OUT/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(main_unchanged=True,root_step_mm=0,photos=[i['size'] for i in images],links_checked=len(parser.targets),missing=missing),ensure_ascii=False))
