from pathlib import Path
import bpy,json,hashlib,sys
ROOT=Path(r'D:\AI-Yang.cn\HomeDesign');OUT=ROOT/'07_renders/v12-reference';OUT.mkdir(parents=True,exist_ok=True)
draft='--draft' in sys.argv;scene=bpy.context.scene;raw=(ROOT/'02_geometry/geometry-master-v12.json').read_bytes();d=json.loads(raw);assert Path(bpy.data.filepath).resolve()==(ROOT/'06_blender/home-main-v12.blend').resolve();assert scene['home_design_geometry_sha256']==hashlib.sha256(raw).hexdigest()
assert scene['home_design_style_sha256']==hashlib.sha256((ROOT/'05_style/modern-japanese-v08.json').read_bytes()).hexdigest()
ff={o['source_id']:o for o in scene.objects if o.get('home_design_role')=='furniture'};assert len(ff)==23
for q in d['furnitureObjects']:
    ob=ff[q['id']];assert abs(ob.location.x*1000-q['x'])<.01 and abs(-ob.location.y*1000-q['z'])<.01;assert list(ob['dimensions_mm'])==[q['dimensionsMm'][k] for k in ['length','width','height']]
report=dict(revision=12,saved_model_reopened=True,geometry_sha256=scene['home_design_geometry_sha256'],style_sha256=scene['home_design_style_sha256'],furniture_count=23,source_walls=sum(o.get('home_design_role')=='wall' for o in scene.objects),window_glass=sum(o.get('home_design_role')=='glass' for o in scene.objects),curtain_blades=sum(o.get('home_design_role')=='curtain_fabric' for o in scene.objects),reference_parts=sum(o.get('home_design_role')=='reference_finish_detail' for o in scene.objects),furniture=[dict(id=q['id'],x=q['x'],z=q['z'],dimensions_mm=list(ff[q['id']]['dimensions_mm'])) for q in d['furnitureObjects']])
assert report['source_walls']==60 and report['window_glass']==12 and report['curtain_blades']==45
(ROOT/'logs/model-v12-readback.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for dev in prefs.devices:dev.use=dev.type!='CPU'
scene.cycles.device='GPU';scene.cycles.samples=32 if draft else 128;scene.cycles.use_denoising=True;scene.render.resolution_x=1200 if draft else 1800;scene.render.resolution_y=800 if draft else 1200
views=[('living-day','v11 · 客厅至阳台',0,1,90),('dining-evening','v11 · 餐厅与玻璃门',1,1,90),('balcony-day','v11 · 阳台茶席',0,1,90),('entry-evening','v12 · 门厅一字柜',1,1,90),('tv-evening','v12 · 电视墙正面',1,0,60),('curtain-evening','v11 · 客厅至阳台',1,0,0)]
if '--only' in sys.argv:views=[v for v in views if v[0]==sys.argv[sys.argv.index('--only')+1]]
root=bpy.data.objects['梦幻帘 · 拉合与转角分开调节'];records=[]
for name,cam,mode,opened,angle in views:
    scene.render.resolution_x=(800 if draft else 1200) if name=='entry-evening' else (1200 if draft else 1800);scene.render.resolution_y=(1200 if draft else 1800) if name=='entry-evening' else (800 if draft else 1200)
    scene['lighting_scene']=mode;root['open_ratio']=opened;root['blade_angle_degrees']=angle;root.update_tag();scene.update_tag();scene.frame_set(scene.frame_current);bpy.context.view_layer.update();scene.camera=bpy.data.objects[cam];scene.render.filepath=str(OUT/(name+('-draft' if draft else '-reference')+'.png'));bpy.ops.render.render(write_still=True);records.append(dict(view=name,path=scene.render.filepath,scene=mode,curtain_open_ratio=opened,curtain_blade_angle=angle,camera_position=list(scene.camera.location),lens_mm=scene.camera.data.lens))
report.update(renders=records,draft=draft,render_mode='Blender Cycles '+str(scene.cycles.samples)+' samples OptiX')
(ROOT/'logs'/('v12-render-drafts.json' if draft else 'v12-render-verification.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('V12_REFERENCES_RENDERED',len(records),'draft' if draft else 'final')
