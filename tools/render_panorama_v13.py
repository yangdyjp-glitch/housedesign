"""Reopen the saved model and render true 2:1 spherical panoramas without cut walls."""
from pathlib import Path
import bpy,json,hashlib,sys,math,time
ROOT=Path(r'D:\AI-Yang.cn\HomeDesign');OUT=ROOT/'07_renders/vr-tour-v01';OUT.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
draft='--draft' in sys.argv;s=bpy.context.scene;G=ROOT/'02_geometry/geometry-master-v13.json';d=json.loads(G.read_text(encoding='utf-8'));assert Path(bpy.data.filepath).resolve()==(ROOT/'06_blender/home-main-v13.blend').resolve();assert s['home_design_geometry_sha256']==sha(G)
ff={o['source_id']:o for o in s.objects if o.get('home_design_role')=='furniture'};assert len(ff)==23
for q in d['furnitureObjects']:
    ob=ff[q['id']];assert abs(ob.location.x*1000-q['x'])<.01 and abs(-ob.location.y*1000-q['z'])<.01;assert list(ob['dimensions_mm'])==[q['dimensionsMm'][k] for k in ['length','width','height']]
report=dict(revision=13,saved_model_reopened=True,geometry_sha256=sha(G),style_sha256=sha(ROOT/'05_style/modern-japanese-v09.json'),model_sha256=sha(ROOT/'06_blender/home-main-v13.blend'),furniture_count=23,source_walls=sum(o.get('home_design_role')=='wall' for o in s.objects),window_glass=sum(o.get('home_design_role')=='glass' for o in s.objects),curtain_blades=sum(o.get('home_design_role')=='curtain_fabric' for o in s.objects),positions=[dict(id=q['id'],x=q['x'],z=q['z']) for q in d['furnitureObjects']])
assert report['source_walls']==60 and report['window_glass']==12 and report['curtain_blades']==45
(ROOT/'logs/model-v13-readback.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for dev in prefs.devices:dev.use=dev.type!='CPU'
s.render.engine='CYCLES';s.cycles.device='GPU';s.cycles.samples=32 if draft else 192;s.cycles.use_denoising=True;s.render.resolution_x=2048 if draft else 8192;s.render.resolution_y=1024 if draft else 4096;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.color_depth='8'
s['lighting_scene']=0;r=bpy.data.objects['梦幻帘 · 拉合与转角分开调节'];r['open_ratio']=1;r['blade_angle_degrees']=90;r.update_tag();s.update_tag();s.frame_set(s.frame_current);bpy.context.view_layer.update()
views=[('living','客厅'),('dining','餐厅'),('balcony','阳台'),('entry','门厅')]
if '--only' in sys.argv:views=[v for v in views if v[0]==sys.argv[sys.argv.index('--only')+1]]
records=[]
for ident,label in views:
    s.camera=bpy.data.objects['v13 · 360 '+label];cam=s.camera;assert cam.data.type=='PANO' and cam.data.panorama_type=='EQUIRECTANGULAR';assert abs(cam.data.longitude_max-cam.data.longitude_min-2*math.pi)<1e-5 and abs(cam.data.latitude_max-cam.data.latitude_min-math.pi)<1e-5
    dest=OUT/(ident+('-draft.png' if draft else '-day.png'));s.render.filepath=str(dest);start=time.time();bpy.ops.render.render(write_still=True);records.append(dict(id=ident,label=label,path=dest.relative_to(ROOT).as_posix(),seconds=round(time.time()-start,1),position_plan_mm=[round(cam.location.x*1000),round(-cam.location.y*1000)],eye_height_mm=round(cam.location.z*1000),heading_at_image_center_deg=0,resolution=[s.render.resolution_x,s.render.resolution_y],lighting_scene='day',curtain='fully open, blade90'))
report.update(renders=records,draft=draft,render_mode='Cycles '+str(s.cycles.samples)+' samples OptiX',projection='equirectangular 360x180 monoscopic')
suffix=sys.argv[sys.argv.index('--only')+1] if '--only' in sys.argv else 'all'
(ROOT/'logs'/('v13-panorama-'+('draft-' if draft else 'final-')+suffix+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('V13_PANORAMAS_RENDERED',len(records),'draft' if draft else 'final')
