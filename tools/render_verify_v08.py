"""Read back the saved v08 model and render the two amended areas."""
from pathlib import Path
import bpy,json,hashlib
ROOT=Path(r'D:\AI-Yang.cn\HomeDesign');OUT=ROOT/'07_renders/v08-selected';OUT.mkdir(parents=True,exist_ok=True)
MODEL=ROOT/'06_blender/home-main-v08.blend';assert Path(bpy.data.filepath).resolve()==MODEL.resolve()
raw=(ROOT/'02_geometry/geometry-master-v08.json').read_bytes();d=json.loads(raw);scene=bpy.context.scene
assert scene['home_design_revision']==8 and scene['home_design_geometry_sha256']==hashlib.sha256(raw).hexdigest()
assert scene['home_design_style_sha256']==hashlib.sha256((ROOT/'05_style/modern-japanese-v04.json').read_bytes()).hexdigest()
ff={o['source_id']:o for o in scene.objects if o.get('home_design_role')=='furniture'};assert len(ff)==21
bpy.context.view_layer.update();rows=[]
for g in d['furnitureObjects']:
    ob=ff[g['id']];assert abs(ob.location.x*1000-g['x'])<.01 and abs(-ob.location.y*1000-g['z'])<.01
    assert list(ob['dimensions_mm'])==[g['dimensionsMm'][k] for k in ['length','width','height']]
    assert ob['movement_step_mm']==100 and not ob.hide_select
    rows.append(dict(id=g['id'],x=g['x'],z=g['z'],dimensions_mm=list(ob['dimensions_mm'])))
cab=ff['tv-high'];pts=[cab.matrix_world@v.co for v in cab.data.vertices]
assert abs(max(p.z for p in pts)*1000-2750)<.03 and cab['ceiling_gap_mm']==0
assert cab['niche_top_mm']-cab['niche_bottom_mm']==200
assert bpy.data.materials['V08 · 柔和奶黄色下柜']['selected_srgb_hex']=='#F1DDAE'
assert sum(o.get('home_design_role')=='wall' for o in scene.objects)==60
assert sum(o.get('home_design_role')=='glass' for o in scene.objects)==12
new={o['source_id']:o for o in scene.objects if o.get('assembly')=='balcony-window'};assert len(new)==27
assert len([o for o in new.values() if o.get('home_design_role')=='glass'])==5
assert len([o for o in new.values() if o.get('home_design_role')=='window_frame'])==20
assert len([o for o in new.values() if o.get('home_design_role')=='insect_screen_concept'])==2
window=d['features']['balconyWindow'];assert window['centralMullions']==0 and window['modelOpeningMm']['width']==5675
assert len([o for o in new.values() if o.get('window_role')=='fixed-large-centre'])==1
assert all(o.hide_render for o in scene.objects if o.get('home_design_role')=='baseline_window_reference')
for key in ['balcony-glass-central','balcony-glass-left-bottom','balcony-glass-right-bottom','balcony-glass-left-upper','balcony-glass-right-upper']:assert key in new
report=dict(saved_model_reopened=True,revision=8,geometry_sha256=scene['home_design_geometry_sha256'],style_sha256=scene['home_design_style_sha256'],
    furniture=rows,all_21_positions_preserved=True,architecture=dict(wall_sources=60,glass=12,window_parts=22),
    cabinet=dict(selection='C amended',lower='#F1DDAE',upper='cream',niche='walnut',ceiling_gap_mm=0,niche_clear_height_mm=200,top_mm=2750),window=window)
(ROOT/'logs/model-v08-readback.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for dev in prefs.devices:dev.use=dev.type!='CPU'
scene.cycles.device='GPU';scene.cycles.samples=128;scene.cycles.use_denoising=True
scene.render.resolution_x=1800;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
views={'cabinet-milk-yellow':'v08 · 奶黄与奶油白通顶长柜','balcony-window':'v08 · 阳台中央整块玻璃'};records=[]
for name,cam in views.items():
    scene.camera=bpy.data.objects[cam];scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
    records.append(dict(view=name,path=scene.render.filepath,mode='Blender Cycles 128 samples, OptiX, full architecture'))
report['renders']=records
(ROOT/'logs/v08-render-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('V08_RENDER_VERIFIED '+json.dumps(dict(furniture=21,glass=12,cabinet_ceiling_gap_mm=0,views=len(records))))
