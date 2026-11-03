"""Verify the saved unified main model and render public perspectives / true spheres."""
from pathlib import Path
import bpy,json,hashlib,sys,time,math
ROOT=Path(r'D:/AI-Yang.cn/HomeDesign');MODEL=ROOT/'06_blender/home-main-v18.blend';OUT=ROOT/'07_renders/v18-entry';OUT.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
s=bpy.context.scene;d=json.loads((ROOT/'02_geometry/geometry-master-v18.json').read_text(encoding='utf-8'));assert s['home_design_revision']==18
ff={o['source_id']:o for o in s.objects if o.get('home_design_role')=='furniture'};assert len(ff)==28;audits=[]
for q in d['furnitureObjects']:
    o=ff[q['id']];assert abs(o.location.x*1000-q['x'])<.01 and abs(-o.location.y*1000-q['z'])<.01
    pts=[o.matrix_world@v.co for v in o.data.vertices];lo=[min(p[i] for p in pts)*1000 for i in range(3)];hi=[max(p[i] for p in pts)*1000 for i in range(3)];b=q['meshBoundsMm'];expected=[b['x'],-b['z']-b['d'],b['y'],b['x']+b['w'],-b['z'],b['y']+b['h']];e=max(abs(a-b) for a,b in zip(lo+hi,expected));assert e<.05,(q['id'],e)
    audits.append(dict(id=q['id'],x=q['x'],z=q['z'],bounds_error_mm=round(e,4)))
assert sum(o.get('home_design_role')=='wall' for o in s.objects)==62 and sum(o.get('home_design_role')=='glass' for o in s.objects)==12
for im in bpy.data.images:
    if im.source=='FILE' and not im.packed_file:assert Path(bpy.path.abspath(im.filepath)).exists(),im.filepath
native=dict(revision=18,model_sha256=sha(MODEL),geometry_sha256=sha(ROOT/'02_geometry/geometry-master-v18.json'),reopened=True,furniture=audits,all_28_positions_and_actual_envelopes_match=True,walls=62,glass=12,curtain_blades=sum(o.get('home_design_role')=='curtain_fabric' for o in s.objects),entry_sides=d['features']['entryV18'])
(ROOT/'logs/v18-model-verification.json').write_text(json.dumps(native,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for v in prefs.devices:v.use=v.type!='CPU'
s.cycles.device='GPU';s.cycles.samples=128;s.cycles.use_denoising=True;s.cycles.denoiser='OPTIX';s.cycles.adaptive_threshold=.025;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
views=[('entry-left','v18 · 左手钢琴键换鞋',1200,1800),('entry-right','v18 · 右手鞋柜',1200,1800),('living','v11 · 客厅至阳台',2100,1400),('dining','v11 · 餐厅与玻璃门',2100,1400),('balcony','v11 · 阳台茶席',2100,1400)]
pano='--pano' in sys.argv
if pano:views=[(i,'v13 · 360 '+label,4096,2048) for i,label in [('living','客厅'),('dining','餐厅'),('balcony','阳台'),('entry','门厅')]]
if '--only' in sys.argv:views=[v for v in views if v[0]==sys.argv[sys.argv.index('--only')+1]]
records=[]
for ident,cam,rx,ry in views:
    s.camera=bpy.data.objects[cam];s.view_settings.exposure=.4 if ident.startswith('entry') else .8;s.render.resolution_x=rx;s.render.resolution_y=ry
    if pano:assert s.camera.data.type=='PANO' and abs(s.camera.data.longitude_max-s.camera.data.longitude_min-2*math.pi)<1e-5
    s.render.filepath=str(OUT/(ident+('-anchor' if pano else '-native')+'.png'));start=time.time();bpy.ops.render.render(write_still=True);records.append(dict(id=ident,path=Path(s.render.filepath).relative_to(ROOT).as_posix(),sha256=sha(Path(s.render.filepath)),resolution=[rx,ry],seconds=round(time.time()-start,1)));print('V18_IMAGE_READY',ident,flush=True)
name='v18-panorama-anchors.json' if pano else 'v18-perspectives.json';(ROOT/'logs'/name).write_text(json.dumps(dict(model_sha256=sha(MODEL),geometry_sha256=s['home_design_geometry_sha256'],images=records),ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('V18_RENDERS_COMPLETE',len(records))
