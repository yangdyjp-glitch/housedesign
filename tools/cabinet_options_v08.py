"""Three unselected cabinet proposals, based on v07, preserving the active model."""
from pathlib import Path
from copy import deepcopy
from mathutils import Vector, Matrix
import bpy, bmesh, json, math, hashlib, ast, sys
ROOT=Path(r'D:\AI-Yang.cn\HomeDesign')
BASE=ROOT/'06_blender/home-main-v07.blend'
OUT=ROOT/'07_renders/v08-cabinet-options'
PARAM=ROOT/'05_style/cabinet-options-v08'
OUT.mkdir(parents=True,exist_ok=True);PARAM.mkdir(parents=True,exist_ok=True)
assert Path(bpy.data.filepath).resolve()==BASE.resolve()
scene=bpy.context.scene
base_raw=(ROOT/'02_geometry/geometry-master-v07.json').read_bytes();base=json.loads(base_raw)
assert scene['home_design_geometry_sha256']==hashlib.sha256(base_raw).hexdigest()
baseline_active_sha=hashlib.sha256(BASE.read_bytes()).hexdigest()
group=next(g for g in base['furnitureObjects'] if g['id']=='tv-high')
assert (group['x'],group['z'],group['d'],group['w'])==(0,5000,4500,400)
furniture={o['source_id']:o for o in scene.objects if o.get('home_design_role')=='furniture'}
others={i:(tuple(o.location),hashlib.sha256(bytes(str([tuple(v.co) for v in o.data.vertices]),'utf-8')).hexdigest()) for i,o in furniture.items() if i!='tv-high'}
tree=ast.parse((ROOT/'tools/render_modern_japanese_v02.py').read_text(encoding='utf-8'))
node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='profile_mesh')
exec(compile(ast.Module(body=[node],type_ignores=[]),'profile_mesh','exec'))
target=bpy.data.collections['04 家具 · 整件选择 · 100mm']
oak=bpy.data.materials['R01 · 浅橡木细纹'];white=bpy.data.materials['R01 · 暖白哑光柜门']
navy=bpy.data.materials['J02 · 深蓝书脊'];metal=bpy.data.materials['R01 · 深灰细砂金属']
def tolinear(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
def material(name,hexcode):
    m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF')
    rgb=[tolinear(int(hexcode[i:i+2],16)/255) for i in [1,3,5]]
    p.inputs['Base Color'].default_value=(*rgb,1);p.inputs['Roughness'].default_value=.63
    m['proposal_srgb_hex']=hexcode;return m
sand=material('A · 沙灰哑光','#B8AA96')
sage=material('B · 灰橄榄绿哑光','#7C8974')
blue=material('C · 深雾蓝哑光','#344D65')
walnut=material('C · 温润胡桃木','#74523A')
n=walnut.node_tree.nodes;l=walnut.node_tree.links
tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=5;tex.inputs['Detail'].default_value=2
coord=n.new('ShaderNodeTexCoord');mapping=n.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(12,.45,3)
l.new(coord.outputs['Object'],mapping.inputs[0]);l.new(mapping.outputs[0],tex.inputs['Vector'])
ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.055,.025,.012,1);ramp.color_ramp.elements[1].color=(.21,.105,.047,1)
l.new(tex.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],n.get('Principled BSDF').inputs['Base Color'])

options=[dict(id='A',slug='sand-oak',name='沙灰＋浅橡木',front=sand,trim=oak,hex='#B8AA96',description='暖沙灰平板门，隐藏式开启；木色仅用于置物格和细节，平静柔和。'),
 dict(id='B',slug='sage-oak',name='灰橄榄绿＋浅木端柜',front=sage,trim=oak,hex='#7C8974',description='灰绿门板搭配约650mm浅木端柜与细木色内嵌拉手；电视端R80弧形端头，呼应绿植与圆角家具。'),
 dict(id='C',slug='navy-walnut',name='深蓝下柜＋奶油白上柜＋胡桃木',front=blue,trim=walnut,hex='#344D65',description='深蓝集中在下部，奶油白上柜减轻压迫，胡桃木置物格形成更明确的对比。')]

def build_parts(opt):
    rows=[]
    def box(suffix,x,z,w,d,y,h,mat,radii=None):
        p=dict(id='tv-high-'+suffix,parent='tv-high',kind='furniture',shape='box',x=x,z=z,w=w,d=d,y=y,h=h,material=mat.name)
        if radii:p.update(shape='profile',worldXYCornerRadiiMm=radii)
        rows.append(p)
    front=opt['front'];trim=opt['trim'];upper=white if opt['id']=='C' else front
    start=5080 if opt['id']=='B' else 5000
    if opt['id']=='B':box('rounded-end',0,5000,400,80,0,2750,trim,[0,0,80,0])
    box('main-carcass',0,start,380,8500-start,60,2670,front)
    box('upper-top',0,start,380,9500-start,2730,20,upper)
    box('plinth',40,start+10,320,9490-start,0,60,front if opt['id']!='A' else metal)
    # Front seal reaches the ceiling. No decorative open shadow gap at the top.
    box('ceiling-scribe',382,start,18,9500-start,2700,50,upper)
    lower_top=1200 if opt['id']=='C' else 2100
    width=(8500-start)/6
    for i in range(6):
        z=start+i*width
        face_lower=trim if opt['id']=='B' and i==0 else front
        face_upper=trim if opt['id']=='B' and i==0 else upper
        box('main-lower-door-'+str(i),382,z+2,18,width-4,64,lower_top-66,face_lower)
        box('main-upper-door-'+str(i),382,z+2,18,width-4,lower_top+2,2698-(lower_top+2),face_upper)
        if opt['id']=='B':box('inset-oak-pull-'+str(i),399,z+width-14,1,10,780,440,trim)
    box('entry-lower-carcass',0,8500,380,1000,60,1120,front)
    box('niche-base',0,8500,400,1000,1180,20,trim)
    box('niche-ceiling',0,8500,400,1000,1400,20,trim)
    box('niche-back',0,8500,20,1000,1200,200,trim)
    box('niche-side-a',20,8500,380,20,1200,200,trim)
    box('niche-side-b',20,9480,380,20,1200,200,trim)
    box('entry-upper-carcass',0,8500,380,1000,1420,1310,upper)
    for i in range(2):
        z=8500+i*500
        box('entry-lower-door-'+str(i),382,z+2,18,496,64,1114,front)
        box('entry-upper-door-'+str(i),382,z+2,18,496,1422,1276,upper)
        if opt['id']=='B':box('entry-inset-pull-'+str(i),399,z+486,1,10,780,320,trim)
    box('niche-tray',210,8800,130,260,1200,18,navy)
    return rows

def create_cabinet(parts,opt):
    old=next(o for o in scene.objects if o.get('home_design_role')=='furniture' and o.get('source_id')=='tv-high')
    bpy.data.objects.remove(old,do_unlink=True)
    children=[]
    for p in parts:
        radii=[r/1000 for r in p.get('worldXYCornerRadiiMm',[0]*4)]
        mesh=profile_mesh(p['id'],p['w']/1000,p['d']/1000,p['h']/1000,radii)
        mesh.materials.append(bpy.data.materials[p['material']])
        ob=bpy.data.objects.new(p['id'],mesh);target.objects.link(ob)
        ob.location=(p['x']/1000,-(p['z']+p['d'])/1000,p['y']/1000)
        bevel=ob.modifiers.new('柔化触边','BEVEL');bevel.width=.0015;bevel.segments=2;bevel.harden_normals=True
        ob.modifiers.new('细面法线','WEIGHTED_NORMAL');children.append(ob)
    bpy.ops.object.select_all(action='DESELECT')
    for ob in children:
        ob.select_set(True);bpy.context.view_layer.objects.active=ob
        for mod in list(ob.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.context.view_layer.objects.active=children[0];bpy.ops.object.join();ob=bpy.context.view_layer.objects.active
    bpy.context.view_layer.update();pts=[ob.matrix_world@v.co for v in ob.data.vertices];anchor=Vector((0,-5,0))
    ob.matrix_world=Matrix.Identity(4);ob.location=anchor
    for v,point in zip(ob.data.vertices,pts):v.co=point-anchor
    ob.name='tv-high | 候选'+opt['id']+' · '+opt['name']
    ob['home_design_role']='furniture';ob['source_id']='tv-high';ob['display_name']='走廊通顶长柜 · 候选'+opt['id']
    ob['dimensions_mm']=[4500,400,2750];ob['movement_step_mm']=100;ob['import_x_mm']=0;ob['import_z_mm']=5000
    ob['part_count']=len(parts);ob['part_source_mm']=json.dumps(parts,ensure_ascii=False);ob['proposal_status']='unselected comparison, not the active main model'
    ob.lock_location[2]=True;ob.lock_rotation[0]=True;ob.lock_rotation[1]=True
    bpy.context.view_layer.update();pts=[ob.matrix_world@v.co for v in ob.data.vertices]
    assert abs(min(v.z for v in pts))<1e-6 and abs(max(v.z for v in pts)-2.75)<1e-6
    assert abs(min(v.y for v in pts)+9.5)<1e-6 and abs(max(v.y for v in pts)+5)<1e-6
    assert abs(max(v.x for v in pts)-.4)<1e-6
    assert all((tuple(o.location),hashlib.sha256(bytes(str([tuple(v.co) for v in o.data.vertices]),'utf-8')).hexdigest())==others[i] for i,o in furniture.items() if i!='tv-high')
    return ob

cam_data=bpy.data.cameras.new('走廊长柜 · 同机位比较');cam_data.type='PERSP';cam_data.lens=18;cam_data.sensor_width=36
camera=bpy.data.objects.new(cam_data.name,cam_data);scene.collection.objects.link(camera)
camera.location=(2.85,-7.2,1.52);camera.rotation_euler=(Vector((.18,-7.25,1.385))-camera.location).to_track_quat('-Z','Y').to_euler()
scene.camera=camera
scene.cycles.samples=48 if '--draft' in sys.argv else 128;scene.cycles.use_denoising=True
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for device in prefs.devices:device.use=device.type!='CPU'
scene.cycles.device='GPU';scene.render.resolution_x=1800;scene.render.resolution_y=1200
scene.render.resolution_percentage=100;scene.view_settings.exposure=.2
reports=[]
only=next((x.split('=',1)[1] for x in sys.argv if x.startswith('--option=')),None)
for opt in options:
    if only and opt['id']!=only:continue
    parts=build_parts(opt);cab=create_cabinet(parts,opt)
    proposal=deepcopy(base)
    proposal['title']='走廊长柜候选'+opt['id']+' · '+opt['name']
    proposal['proposal_status']='Unselected cabinet-only comparison; main v07 retained'
    proposal['proposal_revision']='v08-cabinet-options'
    proposal['furniture']=[p for p in proposal['furniture'] if p['parent']!='tv-high']+parts
    for key in {p['material'] for p in parts}:
        shader=bpy.data.materials[key].node_tree.nodes.get('Principled BSDF')
        proposal['furnitureMaterials'][key]=dict(name=key,color=list(shader.inputs['Base Color'].default_value),roughness=shader.inputs['Roughness'].default_value)
    g=next(g for g in proposal['furnitureObjects'] if g['id']=='tv-high')
    g.update(h=2750,visualHeight=2750,dimensionsMm=dict(length=4500,width=400,height=2750),detail=opt['description'],proposal=opt['id'])
    g['meshBoundsMm']['h']=2750
    proposal['source_baseline_sha256']=hashlib.sha256(base_raw).hexdigest()
    geom_path=PARAM/('option-'+opt['id'].lower()+'-geometry.json')
    geom_path.write_text(json.dumps(proposal,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    scene['home_design_geometry_sha256']=hashlib.sha256(geom_path.read_bytes()).hexdigest()
    scene['home_design_option_status']='unselected';scene['home_design_option_id']=opt['id'];scene['home_design_option_geometry']=geom_path.relative_to(ROOT).as_posix()
    scene['home_design_base_geometry_sha256']=hashlib.sha256(base_raw).hexdigest()
    style_path=PARAM/('option-'+opt['id'].lower()+'-style.json')
    style_record=dict(status='unselected',option=opt['id'],name=opt['name'],base_style='05_style/modern-japanese-v03.json',
        geometry_sha256=scene['home_design_geometry_sha256'],front_srgb_hex=opt['hex'],description=opt['description'],cabinet_height_mm=2750,ceiling_gap_mm=0)
    style_path.write_text(json.dumps(style_record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    scene['home_design_style_file']=style_path.relative_to(ROOT).as_posix()
    scene['home_design_style_sha256']=hashlib.sha256(style_path.read_bytes()).hexdigest()
    destination=ROOT/'06_blender'/('cabinet-option-'+opt['id'].lower()+'-'+opt['slug']+'.blend')
    png=OUT/('option-'+opt['id'].lower()+'-cycles.png')
    scene.render.filepath=str(png)
    if '--draft' not in sys.argv:
        bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(destination))
    bpy.ops.render.render(write_still=True)
    reports.append(dict(id=opt['id'],name=opt['name'],color_hex=opt['hex'],description=opt['description'],png=str(png),blend=str(destination),geometry=str(geom_path),
        geometry_sha256=scene['home_design_geometry_sha256'],ceiling_height_mm=2750,cabinet_top_mm=2750,top_gap_mm=0,niche_bottom_mm=1200,niche_top_mm=1400,
        other_20_furniture_meshes_and_positions_unchanged=True,active_main_not_modified=True,camera_position=list(camera.location),camera_lens=18))
assert hashlib.sha256(BASE.read_bytes()).hexdigest()==baseline_active_sha
(OUT/('draft-manifest.json' if '--draft' in sys.argv else 'cycles-manifest.json')).write_text(json.dumps(dict(status='three unselected options',base_model=str(BASE),base_sha256=baseline_active_sha,options=reports),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('CABINET_OPTIONS_DONE '+json.dumps(dict(options=[o['id'] for o in reports],main_unchanged=True)))
