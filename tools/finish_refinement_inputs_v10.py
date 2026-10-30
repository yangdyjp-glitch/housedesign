from pathlib import Path
import json,hashlib
ROOT=Path(r'D:\AI-Yang.cn\HomeDesign')
p=ROOT/'02_geometry/geometry-master-v10.json';d=json.loads(p.read_text(encoding='utf-8'))
for door in d['features']['publicRefinement']['doors']:
    row=next(q for q in d['detailParts'] if q['id']=='v10-'+door['id']+'-reveal')
    face=door['publicFaceZ'];row['d']=1;row['z']=face-2 if door['id']=='master-public' else face+1
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');sha=hashlib.sha256(p.read_bytes()).hexdigest()
for rel in ['05_style/modern-japanese-v06.json','logs/v10-source-ledger.json']:
    f=ROOT/rel;record=json.loads(f.read_text(encoding='utf-8'));record['geometry_sha256']=sha;f.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
record=dict(status='concept door-position study, not construction confirmation',homeowner_priority='master bathroom internal arrangement and doorway',
    mattress_width_mm=2000,trial_bed_outer_size_mm=[2150,2150],trial_bed_outer_size_status='designer clearance-test envelope, not selected product',
    master_bedroom_model_inner_mm=[3467,3704],master_bathroom_model_inner_mm=[1472,2014],
    homeowner_site_measurement='暂时不清楚',drain_position='unknown',bath_width_source_conflict='2040-related handwritten dimension conflicts with fitted 1472 width',
    wet_area_boundary_changed=False,main_model_private_boundaries_changed=False,
    concept_a='retain existing opening; study bedroom-side sliding leaf parking and sealing, with no wall-pocket assumed',
    concept_b='study a small shift of the shared-wall opening only if wall and head conditions permit; reserve a wider vanity wall section',
    unresolved=['actual internal width and length','drain/riser and waterproof boundary','wall and lintel structure','bed-frame and bedside furniture envelopes','door parking, sealing and privacy'],
    applicable_rule_source='https://www.mohurd.gov.cn/gongkai/zc/wjk/art/2023/art_17339_775528.html')
(ROOT/'01_brief/master-bath-feasibility-v10.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('V10_INPUTS_BOUND',sha)
