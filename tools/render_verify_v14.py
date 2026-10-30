"""Reopen and render six native views; the saved main model keeps full walls."""
from pathlib import Path
import ast,bpy,json,hashlib,sys
from mathutils import Vector
ROOT=Path(r'D:\AI-Yang.cn\HomeDesign');OUT=ROOT/'07_renders/v14-master-suite';OUT.mkdir(parents=True,exist_ok=True)
scene=bpy.context.scene;d=json.loads((ROOT/'02_geometry/geometry-master-v14.json').read_text(encoding='utf-8'))
assert scene['home_design_revision']==14 and scene['home_design_geometry_sha256']==hashlib.sha256((ROOT/'02_geometry/geometry-master-v14.json').read_bytes()).hexdigest()
ff={o['source_id']:o for o in scene.objects if o.get('home_design_role')=='furniture'};assert len(ff)==27
audit=[]
for q in d['furnitureObjects']:
    ob=ff[q['id']];assert abs(ob.location.x*1000-q['x'])<.01 and abs(-ob.location.y*1000-q['z'])<.01
    assert list(ob['dimensions_mm'])==[q['dimensionsMm'][k] for k in ['length','width','height']]
    audit.append(dict(id=q['id'],x=q['x'],z=q['z'],dimensionsMm=list(ob['dimensions_mm'])))
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for dev in prefs.devices:dev.use=dev.type!='CPU'
scene.cycles.device='GPU';scene.cycles.samples=96;scene.cycles.use_denoising=True;scene.render.resolution_percentage=100
views=[('master-bath','v14 · 主卫由外向内',0,1200,1800),('living-day','v11 · 客厅至阳台',0,1800,1200),('dining-evening','v11 · 餐厅与玻璃门',1,1800,1200),('balcony-day','v11 · 阳台茶席',0,1800,1200),('entry-evening','v12 · 门厅一字柜',1,1200,1800),('master-suite-cutaway','v14 · 主卧主卫剖切观察',0,1500,1800)]
if '--only' in sys.argv:views=[r for r in views if r[0]==sys.argv[sys.argv.index('--only')+1]]
if '--verify-only' in sys.argv:views=[]
records=[]
for ident,cam,mode,rx,ry in views:
    hidden=[];temporary=[]
    scene.camera=bpy.data.objects[cam];scene['lighting_scene']=mode;scene.render.resolution_x=rx;scene.render.resolution_y=ry
    if ident=='master-suite-cutaway':
        # Explicit observation-only low walls; do not save these changes.
        for ob in scene.objects:
            if ob.get('home_design_role') in ['wall_visual_union','wall_finish_proposal'] or ('顶面' in ob.name or '天花' in ob.name or 'ceiling' in ob.name.lower()):
                if not ob.hide_render:hidden.append(ob);ob.hide_render=True
        for p in d['walls']:
            if p['y']>=1000:continue
            h=min(1000,p['y']+p['h'])-p['y']
            bpy.ops.mesh.primitive_cube_add(size=1,location=((p['x']+p['w']/2)/1000,-(p['z']+p['d']/2)/1000,(p['y']+h/2)/1000));ob=bpy.context.object;ob.name='观察低墙 '+p['id'];ob.dimensions=(p['w']/1000,p['d']/1000,h/1000);ob.data.materials.append(bpy.data.materials['V10 · 干净暖白平整哑光']);temporary.append(ob)
        # Cutaway daylight fill is an observation aid, never a committed luminaire.
        data=bpy.data.lights.new('剖切观察补光','AREA');data.energy=150;data.shape='DISK';data.size=5;ob=bpy.data.objects.new('剖切观察补光',data);scene.collection.objects.link(ob);ob.location=(9,-4,7);temporary.append(ob)
    scene.update_tag();scene.frame_set(scene.frame_current);bpy.context.view_layer.update();scene.render.filepath=str(OUT/(ident+'.png'));bpy.ops.render.render(write_still=True)
    records.append(dict(view=ident,path=scene.render.filepath,camera=cam,lighting_scene=mode,resolution=[rx,ry],observation_cutaway=ident.endswith('cutaway')))
    for ob in temporary:bpy.data.objects.remove(ob,do_unlink=True)
    for ob in hidden:ob.hide_render=False
report=dict(revision=14,saved_model_reopened=True,furniture=audit,source_walls=sum(o.get('home_design_role')=='wall' for o in scene.objects),window_glass=sum(o.get('home_design_role')=='glass' for o in scene.objects),curtain_blades=sum(o.get('home_design_role')=='curtain_fabric' for o in scene.objects),renders=records,render_mode='native Cycles 96 samples OptiX; no AI repaint',full_walls_in_saved_model=True,construction_certification=False)
report.update(geometry_sha256=scene['home_design_geometry_sha256'],style_sha256=scene['home_design_style_sha256'],model_sha256=hashlib.sha256((ROOT/'06_blender/home-main-v14.blend').read_bytes()).hexdigest())
name='v14-model-readback.json' if not views else 'v14-render-'+('all' if len(views)>1 else views[0][0])+'.json'
(ROOT/'logs'/name).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('V14_RENDER_COMPLETE',len(records))
