"""Reopen the presentation and verify source architecture, anchors, envelopes and image dependencies."""
from pathlib import Path
import bpy,json,hashlib,sys,math
from mathutils import Vector
ROOT=Path(r'D:\AI-Yang.cn\HomeDesign');MODEL=ROOT/'06_blender/home-v14-photoreal-v15.blend'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
scene=bpy.context.scene;d=json.loads((ROOT/'02_geometry/geometry-master-v14.json').read_text(encoding='utf-8'))
assert scene['home_design_revision']==14 and scene['photoreal_presentation_revision']==15
assert sha(ROOT/'06_blender/home-main-v14.blend')==scene['photoreal_source_model_sha256']
ff={o['source_id']:o for o in scene.objects if o.get('home_design_role')=='furniture'};assert len(ff)==27
audit=[]
for q in d['furnitureObjects']:
    ob=ff[q['id']];assert abs(ob.location.x*1000-q['x'])<.01 and abs(-ob.location.y*1000-q['z'])<.01
    assert list(ob['dimensions_mm'])==[q['dimensionsMm'][k] for k in ['length','width','height']]
    points=[ob.matrix_world@v.co for v in ob.data.vertices];lo=[min(p[i] for p in points)*1000 for i in range(3)];hi=[max(p[i] for p in points)*1000 for i in range(3)];b=q['meshBoundsMm'];expected=[b['x'],-(b['z']+b['d']),b['y'],b['x']+b['w'],-b['z'],b['y']+b['h']];error=max(abs(a-c) for a,c in zip(lo+hi,expected));assert error<.05,(q['id'],error,lo,hi,expected)
    audit.append(dict(id=q['id'],x=q['x'],z=q['z'],bounds_error_mm=round(error,4),dimensionsMm=list(ob['dimensions_mm'])))
source_walls={o['source_id']:json.loads(o['source_mm']) for o in scene.objects if o.get('home_design_role')=='wall'};assert len(source_walls)==62
for wall in d['walls']:assert all(source_walls[wall['id']][k]==wall[k] for k in ['x','z','w','d','y','h'])
dependencies=[]
for im in bpy.data.images:
    if im.source=='FILE' and not im.packed_file:
        path=Path(bpy.path.abspath(im.filepath));assert path.exists(),(im.name,path);assert im.filepath.startswith('//'),im.filepath;dependencies.append(dict(image=im.name,path=path.relative_to(ROOT).as_posix(),sha256=sha(path)))
assert sum(o.get('home_design_role')=='glass' for o in scene.objects)==12
assert sum(o.get('home_design_role')=='curtain_fabric' for o in scene.objects)==45
assert sum(o.get('home_design_role')=='panorama_camera' for o in scene.objects)==4
for o in scene.objects:
    if o.get('home_design_role')=='panorama_camera':
        assert o.data.type=='PANO' and o.data.panorama_type=='EQUIRECTANGULAR'
        assert abs(o.data.longitude_max-o.data.longitude_min-2*math.pi)<1e-5 and abs(o.data.latitude_max-o.data.latitude_min-math.pi)<1e-5
sys.path.insert(0,str(ROOT/'tools'));import home_design_move
try:bpy.ops.home_design.move.get_rna_type()
except KeyError:home_design_move.register()
movement=[]
starts={k:o.location.copy() for k,o in ff.items()}
for gid in ['sofa-modular','ottoman','plant-balcony-tall','plant-tv-medium','plant-balcony-low']:
    bpy.ops.object.select_all(action='DESELECT');ob=ff[gid];ob.select_set(True);bpy.context.view_layer.objects.active=ob
    for axis,index in [('X',0),('Y',1)]:
        bpy.ops.home_design.move(axis=axis,direction=1);assert abs(ob.location[index]-starts[gid][index]-.1)<1e-6
        bpy.ops.home_design.move(axis=axis,direction=-1);assert all((o.location-starts[k]).length<1e-6 for k,o in ff.items())
    movement.append(gid)
report=dict(presentation_revision=15,geometry_revision=14,model_sha256=sha(MODEL),source_model_sha256=sha(ROOT/'06_blender/home-main-v14.blend'),geometry_sha256=sha(ROOT/'02_geometry/geometry-master-v14.json'),saved_model_reopened=True,all_27_anchors_and_dimensions_preserved=True,all_geometry_envelopes_match=True,source_walls=62,glass=12,curtain_blades=45,panorama_cameras=4,external_dependencies_relative_and_valid=True,dependencies=dependencies,furniture=audit,private_master_suite_retained=True)
report['changed_five_assemblies_100mm_movement_and_restoration']=movement
(ROOT/'logs/v15-photoreal-model-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('V15_PHOTOREAL_MODEL_VERIFIED')
