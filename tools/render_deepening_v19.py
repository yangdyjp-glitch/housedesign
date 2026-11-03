"""Reopen, audit actual native envelopes, then render the selected view set."""
from pathlib import Path
import bpy,json,hashlib,sys,time,math
R=Path(r'D:/AI-Yang.cn/HomeDesign');MODEL=R/'06_blender/home-main-v19.blend';OUT=R/('07_renders/v19-final-native' if '--final' in sys.argv else '07_renders/v19-deepening');OUT.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
s=bpy.context.scene;d=json.loads((R/'02_geometry/geometry-master-v19.json').read_text(encoding='utf8'));assert s['home_design_revision']==19
assert s['home_design_geometry_sha256']==sha(R/'02_geometry/geometry-master-v19.json')
ff={o['source_id']:o for o in s.objects if o.get('home_design_role')=='furniture'};assert len(ff)==28;audits=[]
for q in d['furnitureObjects']:
 o=ff[q['id']];assert abs(o.location.x*1000-q['x'])<.01 and abs(-o.location.y*1000-q['z'])<.01
 pts=[o.matrix_world@v.co for v in o.data.vertices];lo=[min(p[i] for p in pts)*1000 for i in range(3)];hi=[max(p[i] for p in pts)*1000 for i in range(3)];b=q['meshBoundsMm'];expect=[b['x'],-b['z']-b['d'],b['y'],b['x']+b['w'],-b['z'],b['y']+b['h']];err=max(abs(a-b) for a,b in zip(lo+hi,expect));assert err<.05,(q['id'],err)
 audits.append(dict(id=q['id'],x=q['x'],z=q['z'],bounds_error_mm=round(err,4)))
assert sum(o.get('home_design_role')=='wall' for o in s.objects)==62 and sum(o.get('home_design_role')=='glass' for o in s.objects)==12
assert not any(o.get('source_id','').startswith('v12-tv-') for o in s.objects)
for im in bpy.data.images:
 if im.source=='FILE' and not im.packed_file:assert Path(bpy.path.abspath(im.filepath)).exists(),im.filepath
move_tests=[]
for gid in d['features']['deepeningV19']['changedFurniture']:
 o=ff[gid];orig=o.location.copy();o.location.x+=.1;bpy.context.view_layer.update();assert abs((o.location.x-orig.x)*1000-100)<.001;o.location=orig;bpy.context.view_layer.update();move_tests.append(gid)
audit=dict(revision=19,model_sha256=sha(MODEL),geometry_sha256=sha(R/'02_geometry/geometry-master-v19.json'),reopened=True,furniture=audits,all_28_positions_and_actual_envelopes_match=True,walls=62,glass=12,changed_furniture_100mm_move_restore=move_tests,ceiling_provisional=True,placement_changes=0)
ce=next(o for o in s.objects if o.get('finished_plane_mm')==2750);ev=ce.evaluated_get(bpy.context.evaluated_depsgraph_get());zz=[(ev.matrix_world@v.co).z*1000 for v in ev.data.vertices];audit['ceiling_skin_bounds_mm']=[min(zz),max(zz)];assert abs(min(zz)-2750)<1
audit['general_light_emitters_below_finish']=all(o.location.z*1000<min(zz) for o in s.objects if o.type=='LIGHT' and o.get('circuit')=='general');assert audit['general_light_emitters_below_finish']
(R/'logs/v19-model-verification.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print('V19_NATIVE_AUDIT_PASSED',len(audits),flush=True)
if '--audit-only' in sys.argv:raise SystemExit(0)
pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='OPTIX';pref.get_devices()
for dev in pref.devices:dev.use=dev.type!='CPU'
s.cycles.device='GPU';s.cycles.samples=64;s.cycles.use_denoising=True;s.cycles.denoiser='OPTIX';s.cycles.adaptive_threshold=.04;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
views=[('entry-left','v18 · 左手钢琴键换鞋',1200,1800,0),('entry-right','v18 · 右手鞋柜',1200,1800,0),('living','v11 · 客厅至阳台',2100,1400,0),('dining','v11 · 餐厅与玻璃门',2100,1400,0),('balcony','v11 · 阳台茶席',2100,1400,0),('living-night','v11 · 客厅至阳台',2100,1400,1),('dining-night','v11 · 餐厅与玻璃门',2100,1400,2)]
pano='--pano' in sys.argv
if pano:views=[(i,'v13 · 360 '+label,4096,2048,0) for i,label in [('living','客厅'),('dining','餐厅'),('balcony','阳台'),('entry','门厅')]]
if '--final' in sys.argv and not pano:views.append(('living-clean','v11 · 客厅至阳台',2100,1400,3))
if '--only' in sys.argv:views=[v for v in views if v[0]==sys.argv[sys.argv.index('--only')+1]]
records=[]
for ident,cam,rx,ry,mode in views:
 s.camera=bpy.data.objects[cam];s['lighting_scene_v19']=mode;s.update_tag();s.frame_set(s.frame_current);bpy.context.view_layer.update();s.view_settings.exposure=(.4 if ident.startswith('entry') else .8) if mode==0 else 1.0;s.render.resolution_x=rx;s.render.resolution_y=ry
 if '--draft' in sys.argv:s.render.resolution_percentage=40;s.cycles.samples=32
 if pano:assert s.camera.data.type=='PANO' and abs(s.camera.data.longitude_max-s.camera.data.longitude_min-2*math.pi)<1e-5
 s.render.filepath=str(OUT/(ident+('-anchor' if pano else '-native')+('-draft' if '--draft' in sys.argv else '')+'.png'));t=time.time();bpy.ops.render.render(write_still=True);records.append(dict(id=ident,path=Path(s.render.filepath).relative_to(R).as_posix(),sha256=sha(Path(s.render.filepath)),resolution=[int(rx*s.render.resolution_percentage/100),int(ry*s.render.resolution_percentage/100)],mode=mode,seconds=round(time.time()-t,1)));print('V19_IMAGE_READY',ident,flush=True)
suffix=('-final' if '--final' in sys.argv else '')+('-panorama-anchors' if pano else '-perspectives')
if '--draft' in sys.argv:suffix+='-draft'
(R/('logs/v19'+suffix+'.json')).write_text(json.dumps(dict(model_sha256=sha(MODEL),geometry_sha256=s['home_design_geometry_sha256'],images=records),ensure_ascii=False,indent=2)+'\n',encoding='utf8');print('V19_RENDER_SET_COMPLETE',len(records),flush=True)
