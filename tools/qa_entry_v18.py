"""Check only changed entry furniture envelopes; collect existing spherical QA views."""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];d=json.loads((ROOT/'02_geometry/geometry-master-v18.json').read_text(encoding='utf-8'));changed={'tv-high','entry-shoe-cabinet','entry-piano-bench'}
parts=[p for p in d['furniture'] if p['parent'] in changed];other=[p for p in d['furniture'] if p['parent'] not in changed]+d['walls']+d['glass']+d['doorParts'];hits=[]
def overlaps(a,b):return all(min(a[k]+a[v],b[k]+b[v])-max(a[k],b[k])>.1 for k,v in [('x','w'),('z','d'),('y','h')])
for a in parts:
    for b in other:
        if overlaps(a,b):hits.append([a['id'],b['id']])
for a in parts:
    for b in parts:
        if a['parent']<b['parent'] and overlaps(a,b):hits.append([a['id'],b['id']])
assert not hits,hits
report=dict(revision=18,changed_assemblies=sorted(changed),actual_part_boxes_vs_other_furniture_source_walls_glass_and_closed_kitchen_door_intersections=hits,entry_door_swing_not_known=True,cabinet_end_to_provisional_opening_mm=35,construction_accuracy_not_claimed=True)
(ROOT/'logs/v18-entry-clearance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
caps=json.loads((ROOT/'logs/v18-spherical-view-captures.json').read_text());sheet=Image.new('RGB',(1600,1212),'#ecebe5');pen=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
for i,q in enumerate(caps):
    with Image.open(ROOT/q['file']) as im:tile=im.resize((400,275))
    x=(i%4)*400;y=(i//4)*303;sheet.paste(tile,(x,y));pen.text((x+6,y+278),q['id']+' / '+q['name'],fill='#202821',font=font)
sheet.save(ROOT/'logs/v18-spherical-qa-contact.png');print('V18_ENTRY_ENVELOPES_CLEAR',len(parts),len(caps))
