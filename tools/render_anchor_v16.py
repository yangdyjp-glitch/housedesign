"""Reopen and verify the anchor, render four genuine full-sphere geometric references."""
from pathlib import Path
import bpy,json,hashlib,sys,time,math
ROOT=Path(r'D:/AI-Yang.cn/HomeDesign');MODEL=ROOT/'06_blender/home-v16-reference-anchor.blend';OUT=ROOT/'07_renders/vr-tour-v03';OUT.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
s=bpy.context.scene;d=json.loads((ROOT/'02_geometry/presentation-layout-v16.json').read_text(encoding='utf-8'));assert s['home_design_revision']==16
ff={o['source_id']:o for o in s.objects if o.get('home_design_role')=='furniture'};assert len(ff)==27;bounds=[]
for q in d['furnitureObjects']:
    ob=ff[q['id']];assert abs(ob.location.x*1000-q['x'])<.01 and abs(-ob.location.y*1000-q['z'])<.01
    pts=[ob.matrix_world@v.co for v in ob.data.vertices];lo=[min(p[i] for p in pts)*1000 for i in range(3)];hi=[max(p[i] for p in pts)*1000 for i in range(3)];b=q['meshBoundsMm'];expected=[b['x'],-b['z']-b['d'],b['y'],b['x']+b['w'],-b['z'],b['y']+b['h']];error=max(abs(a-c) for a,c in zip(lo+hi,expected));assert error<.05,(q['id'],error);bounds.append(dict(id=q['id'],x=q['x'],z=q['z'],actual_bounds_error_mm=round(error,4)))
assert sum(o.get('home_design_role')=='wall' for o in s.objects)==62 and sum(o.get('home_design_role')=='glass' for o in s.objects)==12
for im in bpy.data.images:
    if im.source=='FILE' and not im.packed_file:assert Path(bpy.path.abspath(im.filepath)).exists(),im.filepath
(ROOT/'logs/v16-native-layout-verification.json').write_text(json.dumps(dict(reopened=True,geometry_sha256=sha(ROOT/'02_geometry/presentation-layout-v16.json'),model_sha256=sha(MODEL),all_27_anchors_and_envelopes_match=True,walls=62,glass=12,furniture=bounds),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for dev in prefs.devices:dev.use=dev.type!='CPU'
s.cycles.device='GPU';s.cycles.samples=96;s.cycles.adaptive_threshold=.03;s.cycles.use_denoising=True;s.cycles.denoiser='OPTIX';s.render.resolution_percentage=100;s.render.resolution_x=4096;s.render.resolution_y=2048
views=[('living','客厅'),('dining','餐厅'),('balcony','阳台'),('entry','门厅')]
if '--only' in sys.argv:views=[q for q in views if q[0]==sys.argv[sys.argv.index('--only')+1]]
images=[]
for ident,label in views:
    s.camera=bpy.data.objects['v13 · 360 '+label];assert s.camera.data.type=='PANO' and s.camera.data.panorama_type=='EQUIRECTANGULAR'
    assert abs(s.camera.data.longitude_max-s.camera.data.longitude_min-2*math.pi)<1e-5
    s.view_settings.exposure=.4 if ident=='entry' else .8;s.render.filepath=str(OUT/(ident+'-anchor.png'));start=time.time();bpy.ops.render.render(write_still=True)
    images.append(dict(id=ident,path=Path(s.render.filepath).relative_to(ROOT).as_posix(),sha256=sha(Path(s.render.filepath)),seconds=round(time.time()-start,1),resolution=[4096,2048]));print('V16_ANCHOR_READY',ident,flush=True)
(ROOT/'logs/v16-anchor-renders.json').write_text(json.dumps(dict(model_sha256=sha(MODEL),geometry_sha256=sha(ROOT/'02_geometry/presentation-layout-v16.json'),images=images),ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('V16_ANCHORS_COMPLETE',len(images))
