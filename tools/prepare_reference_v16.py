"""Snapshot latest interactive positions and the user's selected photographic style."""
from pathlib import Path
import json,hashlib,shutil,copy
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):(ROOT/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
src=Path('C:/Users/Administrator/AppData/Local/Temp/codex-clipboard-e2ece7a1-4750-45ba-ae06-6c8454eafe04.png')
dest=ROOT/'00_sources/photographic-style-reference-v16.png';shutil.copy2(src,dest)
base=ROOT/'02_geometry/geometry-master-v14.json';d=json.loads(base.read_text(encoding='utf-8'))
changes={'sofa-modular':(3100,1400),'ottoman':(3200,4450),'side-table':(2550,2850)}
records=[]
for q in d['furnitureObjects']:
    x,z=changes.get(q['id'],(q['x'],q['z']));dx=x-q['x'];dz=z-q['z']
    records.append(dict(id=q['id'],x=x,z=z,dx_from_v14=dx,dz_from_v14=dz))
    if dx or dz:
        q['x']=x;q['z']=z;q['meshBoundsMm']['x']+=dx;q['meshBoundsMm']['z']+=dz
        for p in d['furniture']:
            if p['parent']==q['id']:p['x']+=dx;p['z']+=dz
d.update(revision=16,title='v16 全景表现布局快照 · v14建筑与最新手动家具位置',base_architecture_revision=14,base_geometry_sha256=sha(base),presentation_snapshot_only=True)
d['assumptions'].append('v16全景读取最新交互状态：沙发3100/1400、脚凳3200/4450、茶几2550/2850；其余24件位置不变。主编辑文件仍为v14，表现快照独立保存。')
write('02_geometry/presentation-layout-v16.json',d)
write('03_layout/widget-layout-v16-snapshot.json',dict(source='Latest house-structure interactive snapshot received in this conversation, revision14',date='2026-10-31',base_revision=14,furniture_count=27,positions=records,curtain_state_in_editor='privacy',daylight_presentation_curtains='open, following the user selected photographic reference; editor state is not modified'))
intent=dict(presentation_revision=16,architecture_revision=14,request=['VR使用这一套图的风格','不仅仅是色彩和材质，主要是这个图的真实感和光影'],reference=dest.relative_to(ROOT).as_posix(),reference_sha256=sha(dest),style='restrained modern Japanese, photographic architectural interior, textured pale oak and greige linen',primary_goal='photographic realism and physically coherent oblique daylight, contact shadows, natural reflections; not merely a color/material change',method='Native full-sphere architectural anchors, built-in imagegen enhancement locked to the anchors, inspect in spherical viewer',geometry='02_geometry/presentation-layout-v16.json',geometry_sha256=sha(ROOT/'02_geometry/presentation-layout-v16.json'),placement_source='03_layout/widget-layout-v16-snapshot.json',locks=['All walls and openings','85inch TV','single34inch monitor and one office chair','one desk behind sofa facing TV','four dining chairs and table against wall','two low tea chairs and one low round tea table','milk-yellow lower and cream upper cabinets, walnut niche','no new rug, pendant, artwork or furniture'],exterior_is_illustrative=True,budget_considered=False)
write('05_style/photographic-reference-v16.json',intent)
print('V16_REFERENCE_AND_27_POSITIONS_SNAPSHOTTED')
