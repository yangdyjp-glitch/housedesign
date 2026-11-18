from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote
import json,hashlib
from PIL import Image
root=Path('D:/AI-Yang.cn/HomeDesign');out=root/'09_delivery/sideboard-U-study-09'
spec=json.loads((out/'U-layout-parameters.json').read_text(encoding='utf-8'))
rb=json.loads((out/'model-readback.json').read_text(encoding='utf-8'))
audit=json.loads((out/'native-audit.json').read_text(encoding='utf-8'))
class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        for k,v in attrs:
            if k in ('href','src') and v and not v.startswith(('#','http:','https:')):self.links.append(v)
p=Links();p.feed((out/'同色等高U形餐岛与下拉收纳.html').read_text(encoding='utf-8'))
missing=[v for v in p.links if v!='verification.json' and not (out/unquote(v)).resolve().is_file()]
assert not missing,missing
images={}
for name in ('同色等高U形-开关灯概念对照.png','U形等高-实体关系参考.png','下拉收纳-实体原理示意.png','同色等高U形-尺寸平面.png'):
    with Image.open(out/name) as im:
        assert im.format=='PNG';images[name]=dict(width=im.width,height=im.height,bytes=(out/name).stat().st_size);im.verify()
hashes={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in spec['main_baseline_sha256']}
assert hashes==spec['main_baseline_sha256']==rb['main_baseline_sha256_after']
assert rb['top']['h']==[850,880] and rb['top_material']=='pale oak'
assert rb['seat_count']==3 and all(v['h'][1]==600 for v in rb['seats'].values())
assert rb['upper_complete_door_count']==4 and rb['upper_tray_count']==8
assert rb['no_old_right_tall_column'] and rb['old_table_step_removed']
assert spec['sideboard']['right_tall_column_removed'] and spec['sideboard']['niche_full_width']==2200
assert audit['single_connected_U_mesh'] and audit['watertight_raw_top_mesh'] and audit['one_top_material']
result=dict(date='2026-11-06',scope='independent09',main_model_unchanged=True,v20_started=False,
    frozen_main_files=hashes,model_checks=rb,native_mesh_and_animation_audit='native-audit.json',images=images,
    offline_html_links_valid=True,browser_visual_preview_performed=False,
    visual_review=dict(method='direct inspection of saved native closed/open references, exact plan, and saved photographic diptych',
       passed=['one880-height continuous U','same pale-oak top/lining/band','right niche remains open','four complete upper doors without top-right split','three external counter chairs with footrests','same furnishings OFF/ON','daylight remains in OFF'],
       known_concept_limits=['coffee machine front is a generic proxy, not a selected product','thin-band flap joints are subtler in AI than the editable model','wood sample, fabric and luminous output remain conceptual'],
       no_numeric_aesthetic_score=True),
    practical_review=dict(result='compact independent study, not construction or full movement approval',
       inner_closed_gap=600,outer_furniture_gap=682,seat_height=600,table_underside_above_seat=250,
       pulldown_source_check='manufacturer basic envelope and access principle; no exact hardware order',
       pending=['real sweep and payload','side-access station by connecting arm','human reach','chair selection and pullout','fridge full opening','actual site dimensions']),
    ai_tool='built-in image_gen',prompt='generation-prompt.json',sources=spec['pull_down']['sources'])
(out/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(result='passed',main_files_unchanged=len(hashes),images=len(images),html_links=len(p.links),top_height=880,seat_height=600)))
