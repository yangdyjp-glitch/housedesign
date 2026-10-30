"""Native perspective and full-sphere images from the same locked v14-layout presentation."""
from pathlib import Path
import bpy,json,hashlib,sys,math,time
ROOT=Path(r'D:\AI-Yang.cn\HomeDesign');MODEL=ROOT/'06_blender/home-v14-photoreal-v15.blend';OUT=ROOT/'07_renders/vr-tour-v02';OUT.mkdir(parents=True,exist_ok=True)
draft='--draft' in sys.argv;pano='--pano' in sys.argv
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert Path(bpy.data.filepath).resolve()==MODEL.resolve();scene=bpy.context.scene;assert scene['home_design_revision']==14 and scene['photoreal_presentation_revision']==15
d=json.loads((ROOT/'02_geometry/geometry-master-v14.json').read_text(encoding='utf-8'));ff={o['source_id']:o for o in scene.objects if o.get('home_design_role')=='furniture'};assert len(ff)==27
for q in d['furnitureObjects']:
    ob=ff[q['id']];assert abs(ob.location.x*1000-q['x'])<.01 and abs(-ob.location.y*1000-q['z'])<.01
for im in bpy.data.images:
    if im.source=='FILE' and not im.packed_file:assert Path(bpy.path.abspath(im.filepath)).exists(),(im.name,im.filepath)
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for dev in prefs.devices:dev.use=dev.type!='CPU'
scene.render.engine='CYCLES';scene.cycles.device='GPU';scene.cycles.samples=48 if draft else (128 if pano else 256);scene.cycles.use_adaptive_sampling=True;scene.cycles.adaptive_threshold=.045 if draft else (.028 if pano else .018);scene.cycles.use_denoising=True;scene.cycles.denoiser='OPTIX'
scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.render.image_settings.color_depth='8'
views=[('living','客厅','v11 · 客厅至阳台'),('dining','餐厅','v11 · 餐厅与玻璃门'),('balcony','阳台','v11 · 阳台茶席'),('entry','门厅','v12 · 门厅一字柜')]
if '--only' in sys.argv:views=[v for v in views if v[0]==sys.argv[sys.argv.index('--only')+1]]
records=[]
for ident,label,perspective in views:
    scene['lighting_scene']=0;scene.view_settings.exposure=1.1 if ident=='entry' else 1.5;scene.update_tag();scene.frame_set(scene.frame_current);bpy.context.view_layer.update();scene.camera=bpy.data.objects['v13 · 360 '+label if pano else perspective]
    if pano:
        assert scene.camera.data.type=='PANO' and scene.camera.data.panorama_type=='EQUIRECTANGULAR';scene.render.resolution_x=2048 if draft else 8192;scene.render.resolution_y=scene.render.resolution_x//2
    else:scene.render.resolution_x=(800 if draft else 1400) if ident=='entry' else (1200 if draft else 2100);scene.render.resolution_y=(1200 if draft else 2100) if ident=='entry' else (800 if draft else 1400)
    file=OUT/(ident+('-sphere' if pano else '-photo')+('-draft' if draft else '')+'.png');scene.render.filepath=str(file);start=time.time();bpy.ops.render.render(write_still=True)
    records.append(dict(id=ident,label=label,path=file.relative_to(ROOT).as_posix(),sha256=sha(file),seconds=round(time.time()-start,1),resolution=[scene.render.resolution_x,scene.render.resolution_y],camera=scene.camera.name,eye_height_mm=round(scene.camera.location.z*1000),position_plan_mm=[round(scene.camera.location.x*1000),round(-scene.camera.location.y*1000)],exposure=scene.view_settings.exposure));print('V15_IMAGE_READY',ident,records[-1]['seconds'],flush=True)
report=dict(presentation_revision=15,geometry_revision=14,model_sha256=sha(MODEL),geometry_sha256=sha(ROOT/'02_geometry/geometry-master-v14.json'),furniture_count=27,full_walls=True,window_glass=sum(o.get('home_design_role')=='glass' for o in scene.objects),source_walls=sum(o.get('home_design_role')=='wall' for o in scene.objects),pano=pano,draft=draft,render_mode='Cycles OptiX, '+str(scene.cycles.samples)+' max samples; adaptive; GPU denoised',exterior_is_illustrative=True,images=records)
name='v15-'+('panoramas' if pano else 'perspectives')+('-draft' if draft else '-final')+'-'+(views[0][0] if len(views)==1 else 'all')+'.json';(ROOT/'logs'/name).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('V15_RENDER_COMPLETE',len(records))
