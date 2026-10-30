"""Carry the verified v12 scene forward; merge three new user offsets and add four panorama cameras."""
from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector
ROOT=Path(r'D:\AI-Yang.cn\HomeDesign')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
base=ROOT/'06_blender/home-main-v12.blend';assert Path(bpy.data.filepath).resolve()==base.resolve()
prior=json.loads((ROOT/'logs/v12-delivery-verification.json').read_text(encoding='utf-8'));assert sha(base)==prior['model_sha256']
G=ROOT/'02_geometry/geometry-master-v13.json';S=ROOT/'05_style/modern-japanese-v09.json';d=json.loads(G.read_text(encoding='utf-8'));old=json.loads((ROOT/'02_geometry/geometry-master-v12.json').read_text(encoding='utf-8'))
s=bpy.context.scene;assert s['home_design_revision']==12 and s['home_design_geometry_sha256']==sha(ROOT/'02_geometry/geometry-master-v12.json')
ff={o['source_id']:o for o in s.objects if o.get('home_design_role')=='furniture'};assert len(ff)==23
oldff={q['id']:q for q in old['furnitureObjects']};changes=[]
for q in d['furnitureObjects']:
    ob=ff[q['id']];prev=oldff[q['id']];assert abs(ob.location.x*1000-prev['x'])<.01 and abs(-ob.location.y*1000-prev['z'])<.01
    dx,dz=q['x']-prev['x'],q['z']-prev['z']
    if dx or dz:ob.location.x+=dx/1000;ob.location.y-=dz/1000;changes.append(dict(id=q['id'],dx=dx,dz=dz))
assert len(changes)==3
s['home_design_revision']=13;s['home_design_geometry_sha256']=sha(G);s['home_design_style_sha256']=sha(S);s['home_design_style_revision']='modern-japanese-v09';s['home_design_geometry_path']=G.as_posix();s['home_design_style_path']=S.as_posix()
for textname,path in [('geometry-master-v13.json',G),('modern-japanese-v09.json',S)]:
    t=bpy.data.texts.new(textname);t.write(path.read_text(encoding='utf-8'))
points=[('living','客厅',1800,4500,1600),('dining','餐厅',1100,8000,1600),('balcony','阳台',2050,850,1600),('entry','门厅',635,10100,1600)]
for ident,label,x,z,y in points:
    data=bpy.data.cameras.new('v13-pano-'+ident);data.type='PANO';data.panorama_type='EQUIRECTANGULAR';data.latitude_min=-math.pi/2;data.latitude_max=math.pi/2;data.longitude_min=-math.pi;data.longitude_max=math.pi;data.clip_start=.03;data.clip_end=100
    ob=bpy.data.objects.new('v13 · 360 '+label,data);s.collection.objects.link(ob);ob.location=(x/1000,-z/1000,y/1000);ob.rotation_euler=Vector((1,0,0)).to_track_quat('-Z','Y').to_euler();ob['home_design_role']='panorama_camera';ob['panorama_id']=ident;ob['eye_height_mm']=y;ob['heading_at_image_center_deg']=0
s.camera=bpy.data.objects['v13 · 360 客厅'];s['lighting_scene']=0;s.update_tag();s.frame_set(s.frame_current);bpy.context.view_layer.update()
assert all(abs(ff[q['id']].location.x*1000-q['x'])<.01 and abs(-ff[q['id']].location.y*1000-q['z'])<.01 for q in d['furnitureObjects'])
report=dict(revision=13,base_model_sha256=sha(base),geometry_sha256=sha(G),style_sha256=sha(S),furniture_count=len(ff),furniture_meshes_preserved=23,changes=changes,source_walls=sum(o.get('home_design_role')=='wall' for o in s.objects),window_glass=sum(o.get('home_design_role')=='glass' for o in s.objects),curtain_blades=sum(o.get('home_design_role')=='curtain_fabric' for o in s.objects),panorama_cameras=[dict(id=i,label=l,plan_position_mm=[x,z],eye_height_mm=y,heading_at_image_center_deg=0) for i,l,x,z,y in points],projection='Cycles equirectangular 360 by 180, monoscopic; native no AI repaint',private_boundaries_changed=False)
assert report['source_walls']==60 and report['window_glass']==12 and report['curtain_blades']==45
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'06_blender/home-main-v13.blend'))
(ROOT/'logs/model-v13-build.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('V13_MODEL_SAVED',report['geometry_sha256'])
