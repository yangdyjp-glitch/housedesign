from pathlib import Path
import json,hashlib,math
from copy import deepcopy
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'07_renders/vr-tour-v01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
points=[('living','客厅',[1800,4500],[4200,3000],1050),('dining','餐厅',[1100,8000],[2680,8100],1050),('balcony','阳台',[2050,850],[3650,620],800),('entry','门厅',[635,10100],[635,11000],1200)]
scenes=[]
for ident,label,pos,target,h in points:
    dx,dz=target[0]-pos[0],target[1]-pos[1]
    scenes.append(dict(id=ident,label=label,image=f'07_renders/vr-tour-v01/{ident}-day.jpg',positionPlanMm=pos,eyeHeightMm=1600,initialYawDeg=math.degrees(math.atan2(dz,dx)),initialPitchDeg=math.degrees(math.atan2(h-1600,math.hypot(dx,dz))),initialFovDeg=60,headingAtImageCenterDeg=0))
cfg=dict(title='暖白浅木 · 四区360°全景漫游',revision=13,geometry='02_geometry/geometry-master-v13.json',model='06_blender/home-main-v13.blend',modelSha256=sha(ROOT/'06_blender/home-main-v13.blend'),defaultScene='living',northPlanDirection='down',panoramas=scenes,renderSource='Blender Cycles, native equirectangular, no AI repaint',scope='Four fixed standing viewpoints; mono 360x180, not stereoscopic or free walking')
(OUT/'tour-config.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
draft=deepcopy(cfg);draft['title']='全景校对 · 低清试图'
for sc in draft['panoramas']:sc['image']=sc['image'].replace('-day.jpg','-draft.png')
(OUT/'tour-config-draft.json').write_text(json.dumps(draft,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('VR_CONFIGS_READY')
