"""Independent, geometry-preserving presentation copy of the approved v06 model."""
from pathlib import Path
import bpy
import hashlib
import json
import math
import sys
from mathutils import Vector

ROOT = Path(r'D:\AI-Yang.cn\HomeDesign')
OUT = ROOT / '07_renders' / 'v06-realistic-v01'
OUT.mkdir(parents=True, exist_ok=True)
SOURCE = ROOT / '06_blender' / 'home-main-v06.blend'
raw = (ROOT / '02_geometry' / 'geometry-master-v06.json').read_bytes()
DATA = json.loads(raw)
SHA = hashlib.sha256(raw).hexdigest()
scene = bpy.context.scene
assert scene['home_design_geometry_sha256'] == SHA
assert Path(bpy.data.filepath).resolve() == SOURCE.resolve()
draft = '--draft' in sys.argv
only = next((arg.split('=', 1)[1] for arg in sys.argv if arg.startswith('--view=')), None)

def coll(name):
    c = bpy.data.collections.new(name)
    scene.collection.children.link(c)
    return c

surface = coll('08 写实表现 · 按原家具零件生成')
detail = coll('09 写实表现 · 灯光和饰面建议')
camera_coll = coll('10 写实表现 · 人眼视角')
bpy.data.collections['04 家具 · 整件选择 · 100mm'].hide_render = True
bpy.data.collections['05 房间标记 · 仅观察用'].hide_render = True
bpy.data.collections['06 低墙观察副本 · 不用于几何核验'].hide_render = True
bpy.data.collections['01 墙体 · 高度及墙厚待核'].hide_render = False
for obj in list(bpy.data.objects):
    if obj.type == 'LIGHT':
        obj.hide_render = True

def base_mat(name, color, roughness=0.7, metallic=0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Roughness'].default_value = roughness
    p.inputs['Metallic'].default_value = metallic
    return m

def texture(m, scale, strength=0.1, distance=0.0003):
    n = m.node_tree.nodes
    l = m.node_tree.links
    tex = n.new('ShaderNodeTexNoise')
    tex.inputs['Scale'].default_value = scale
    tex.inputs['Detail'].default_value = 2.0
    bump = n.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = strength
    bump.inputs['Distance'].default_value = distance
    l.new(tex.outputs['Fac'], bump.inputs['Height'])
    l.new(bump.outputs['Normal'], n.get('Principled BSDF').inputs['Normal'])
    return tex

def wood(name, dark, light, floor=False):
    m = base_mat(name, light, 0.57)
    n = m.node_tree.nodes
    l = m.node_tree.links
    coord = n.new('ShaderNodeTexCoord')
    mapping = n.new('ShaderNodeVectorMath')
    mapping.operation = 'MULTIPLY'
    mapping.inputs[1].default_value = (15.0, 0.7, 3.0)
    l.new(coord.outputs['Object'], mapping.inputs[0])
    noise = n.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 3.5
    noise.inputs['Detail'].default_value = 3.0
    noise.inputs['Roughness'].default_value = 0.65
    l.new(mapping.outputs[0], noise.inputs['Vector'])
    ramp = n.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.18
    ramp.color_ramp.elements[0].color = (*dark, 1)
    ramp.color_ramp.elements[1].position = 0.82
    ramp.color_ramp.elements[1].color = (*light, 1)
    l.new(noise.outputs['Fac'], ramp.inputs[0])
    p = n.get('Principled BSDF')
    l.new(ramp.outputs[0], p.inputs['Base Color'])
    bump = n.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.11
    bump.inputs['Distance'].default_value = 0.00022
    l.new(noise.outputs['Fac'], bump.inputs['Height'])
    l.new(bump.outputs['Normal'], p.inputs['Normal'])
    if floor:
        brick = n.new('ShaderNodeTexBrick')
        brick.inputs['Color1'].default_value = (0.63, 0.56, 0.44, 1)
        brick.inputs['Color2'].default_value = (0.45, 0.37, 0.27, 1)
        brick.inputs['Mortar'].default_value = (0.29, 0.25, 0.19, 1)
        brick.inputs['Scale'].default_value = 1
        brick.inputs['Mortar Size'].default_value = 0.001
        brick.inputs['Mortar Smooth'].default_value = 0.0005
        brick.inputs['Brick Width'].default_value = 1.6
        brick.inputs['Row Height'].default_value = 0.18
        l.new(coord.outputs['Object'], brick.inputs['Vector'])
        mix = n.new('ShaderNodeMixRGB')
        mix.blend_type = 'MULTIPLY'
        mix.inputs[0].default_value = 0.34
        l.new(ramp.outputs[0], mix.inputs[1])
        l.new(brick.outputs['Color'], mix.inputs[2])
        l.new(mix.outputs[0], p.inputs['Base Color'])
    return m

white = base_mat('R01 · 暖白哑光柜门', (0.72, 0.70, 0.64), 0.64)
texture(white, 220, 0.06, 0.00012)
oak = wood('R01 · 浅橡木细纹', (0.41, 0.29, 0.17), (0.65, 0.51, 0.33))
fabric = base_mat('R01 · 米灰亚麻混纺', (0.44, 0.415, 0.365), 0.92)
fabric.node_tree.nodes.get('Principled BSDF').inputs['Sheen Weight'].default_value = 0.23
texture(fabric, 410, 0.27, 0.00065)
fabric_dark = base_mat('R01 · 沙发框体织物', (0.33, 0.315, 0.28), 0.94)
texture(fabric_dark, 370, 0.23, 0.0006)
metal = base_mat('R01 · 深灰细砂金属', (0.075, 0.085, 0.086), 0.34, 0.65)
screen = base_mat('R01 · 关闭的黑玻璃屏幕', (0.007, 0.012, 0.016), 0.16, 0.15)
screen.node_tree.nodes.get('Principled BSDF').inputs['Coat Weight'].default_value = 0.35
books = base_mat('R01 · 灰绿书脊', (0.22, 0.31, 0.28), 0.83)
wall = base_mat('R01 · 暖白细肌理墙面', (0.77, 0.75, 0.70), 0.87)
texture(wall, 260, 0.10, 0.00035)
floor = wood('R01 · 浅木地板', (0.47, 0.37, 0.24), (0.70, 0.59, 0.43), True)
glass = base_mat('R01 · 实体透明玻璃', (0.96, 0.985, 1.0), 0.035)
glass.node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value = 1
glass.node_tree.nodes.get('Principled BSDF').inputs['IOR'].default_value = 1.46
window_frame = base_mat('R01 · 窗框暖灰铝材', (0.15, 0.165, 0.16), 0.4, 0.65)
ceiling_mat = base_mat('R01 · 哑白顶面', (0.82, 0.815, 0.78), 0.9)
mats = dict(wood=oak, cabinet=white, fabric=fabric, **{'fabric-dark': fabric_dark},
            metal=metal, screen=screen, book=books)

def mesh_obj(name, vertices, faces, collection, mat):
    mesh = bpy.data.meshes.new(name + ' mesh')
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    ob = bpy.data.objects.new(name, mesh)
    collection.objects.link(ob)
    ob.data.materials.append(mat)
    return ob

def bevel(ob, amount, segments=3):
    mod = ob.modifiers.new('圆润边缘 · 保留外包络', 'BEVEL')
    mod.width = amount
    mod.segments = segments
    mod.affect = 'EDGES'
    mod.harden_normals = True
    normals = ob.modifiers.new('面法线', 'WEIGHTED_NORMAL')
    normals.keep_sharp = True

def box(name, x, y, z, w, d, h, mat, collection=detail, rounded=0):
    # World metres. Local object coordinates give procedural grain a physical scale.
    v = [(0,0,0),(w,0,0),(w,d,0),(0,d,0),(0,0,h),(w,0,h),(w,d,h),(0,d,h)]
    f = [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    ob = mesh_obj(name, v, f, collection, mat)
    ob.location = (x,y,z)
    if rounded:
        is_fabric = mat in [fabric, fabric_dark]
        if is_fabric:
            for polygon in ob.data.polygons:
                polygon.use_smooth = True
        bevel(ob, rounded, 6 if is_fabric else 3)
    return ob

roots = {}
for group in DATA['furnitureObjects']:
    root = bpy.data.objects.new('写实家具 · ' + group['name'], None)
    surface.objects.link(root)
    root['source_id'] = group['id']
    root['dimensions_mm'] = [group['dimensionsMm'][k] for k in ['length','width','height']]
    root['home_design_role'] = 'presentation_furniture'
    roots[group['id']] = root

for p in DATA['furniture']:
    x, y, z = p['x']/1000, -(p['z']+p['d'])/1000, p.get('y',0)/1000
    w, d, h = p['w']/1000, p['d']/1000, p['h']/1000
    mat = mats[p['material']]
    if p.get('shape') == 'cylinder':
        count = 48
        vertices = [(w/2+w/2*math.cos(2*math.pi*i/count),
                     d/2+d/2*math.sin(2*math.pi*i/count), lev)
                    for lev in [0,h] for i in range(count)]
        faces = [tuple(reversed(range(count))), tuple(range(count,count*2))]
        faces += [(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)]
        ob = mesh_obj(p['id'],vertices,faces,surface,mat)
        ob.location=(x,y,z)
        for poly in ob.data.polygons:
            poly.use_smooth = len(poly.vertices)==4
        bevel(ob,min(0.003,min(w,d,h)/5))
    else:
        amount = min(0.048,min(w,d,h)*0.40) if p['material'] in ['fabric','fabric-dark'] else min(0.004,min(w,d,h)/5)
        ob=box(p['id'],x,y,z,w,d,h,mat,surface,amount)
    ob.parent=roots[p['parent']]
    ob['source_part_id']=p['id']
    ob['source_mm']=json.dumps(p,ensure_ascii=False)

for ob in bpy.data.collections['01 墙体 · 高度及墙厚待核'].objects:
    ob.data.materials.clear()
    ob.data.materials.append(wall)
    bevel(ob,0.0015,2)
for ob in bpy.data.collections['02 地面'].objects:
    ob.data.materials.clear()
    ob.data.materials.append(floor)
for ob in bpy.data.collections['03 玻璃 · 阳台落地窗及主卧飘窗'].objects:
    ob.data.materials.clear()
    ob.data.materials.append(glass)

# This roof is only a lighting/display cap. It does not amend the measured geometry.
ceiling = mesh_obj('表现用顶面 · 暂定净高2750',
                   [(x/1000,-z/1000,2.75) for x,z in DATA['floor']],
                   [tuple(range(len(DATA['floor'])))],detail,ceiling_mat)
ceiling['home_design_role']='presentation_only'
ceiling['provisional_height_mm']=2750

# Thin frame members sit inside the existing opening, with no opening enlargement.
for p in DATA['glass']:
    x,y,z=p['x']/1000,-(p['z']+p['d'])/1000,p.get('y',0)/1000
    w,d,h=p['w']/1000,p['d']/1000,p['h']/1000
    if w>d:
        xx=x;yy=y+d/2-0.022
        for x0 in [x,x+w-0.035]:
            box('表现窗框 '+p['id'],x0,yy,z,0.035,0.044,h,window_frame,rounded=0.002)
        for z0 in [z,z+h-0.035]:
            box('表现窗框 '+p['id'],xx,yy,z0,w,0.044,0.035,window_frame,rounded=0.002)
        if p['id']=='outer-top-glass-0':
            for t in [1/3,2/3]:
                box('阳台细窗梃',x+w*t-0.014,yy,z,0.028,0.044,h,window_frame,rounded=0.002)
    else:
        xx=x+w/2-0.022
        for y0 in [y,y+d-0.035]:
            box('表现窗框 '+p['id'],xx,y0,z,0.044,0.035,h,window_frame,rounded=0.002)
        for z0 in [z,z+h-0.035]:
            box('表现窗框 '+p['id'],xx,y,z0,0.044,d,0.035,window_frame,rounded=0.002)

def light(name,location,target,power,size,color=(1,1,1),size_y=None):
    data=bpy.data.lights.new(name,'AREA')
    data.energy=power
    data.color=color
    data.shape='RECTANGLE' if size_y else 'DISK'
    data.size=size
    if size_y:data.size_y=size_y
    obj=bpy.data.objects.new(name,data)
    detail.objects.link(obj)
    obj.location=location
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
    obj.visible_camera=False
    obj.visible_glossy=False
    obj.visible_transmission=False
    return obj

world=bpy.data.worlds.new('R01 · 日光环境')
world.use_nodes=True
world.node_tree.nodes.get('Background').inputs[0].default_value=(0.78,0.86,1.0,1)
world.node_tree.nodes.get('Background').inputs[1].default_value=0.6
scene.world=world
light('阳台柔和日光',(3.65,0.7,1.65),(3.65,-4.5,0.85),1450,5.5,(1.0,0.94,0.83),2.1)
light('入户侧开口日光',(-0.7,-10.1,1.45),(2,-8,0.8),400,1.15,(0.84,0.91,1),1.9)

led=base_mat('R01 · 3000K灯带',(1,0.74,0.44),0.5)
lp=led.node_tree.nodes.get('Principled BSDF')
lp.inputs['Emission Color'].default_value=(1,0.74,0.44,1)
lp.inputs['Emission Strength'].default_value=3
for x,y in [(1.15,-2.5),(3.3,-2.5),(5.9,-2.5),(1.3,-5.6),(5.4,-5.6),(1.4,-7.5),(1.4,-9.0)]:
    # Small flush downlight; no pendant or new furniture.
    box('表现嵌入灯',x-0.027,y-0.027,2.742,0.054,0.054,0.006,led)
    light('3000K柔和顶灯',(x,y,2.735),(x,y,0),35,0.16,(1,0.83,0.63))
box('入户置物格内灯带',0.26,-9.48,1.386,0.012,0.96,0.008,led)
light('置物格内部照明',(0.28,-9,1.38),(0.1,-9,1.21),3.5,0.85,(1,0.78,0.49),0.05)

def camera(name,position,target,lens):
    data=bpy.data.cameras.new(name)
    data.type='PERSP';data.lens=lens;data.sensor_width=36
    data.clip_start=0.02;data.clip_end=200
    obj=bpy.data.objects.new(name,data)
    camera_coll.objects.link(obj)
    obj.location=position
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
    data.dof.use_dof=False
    return obj

views={
    'living':camera('客厅 · 电视与贵妃沙发',(6.15,-0.45,1.65),(2.25,-3.75,1.12),23),
    'office':camera('办公区 · 沙发后双人桌',(0.8,-4.95,1.6),(5.2,-2.6,1.15),24),
    'office-detail':camera('办公区细节 · 双工位单椅',(5.05,-5.45,1.68),(6.08,-2.9,1.1),23),
    'dining':camera('餐厅 · 四椅与入户通长柜',(1.55,-5.35,1.65),(1.5,-8.45,1.08),24),
}
scene.render.engine='CYCLES'
scene.cycles.samples=32 if draft else 128
scene.cycles.use_denoising=True
scene.cycles.max_bounces=10
scene.cycles.transmission_bounces=8
scene.cycles.transparent_max_bounces=8
try:
    prefs=bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type='OPTIX'
    prefs.get_devices()
    for device in prefs.devices:device.use=device.type!='CPU'
    scene.cycles.device='GPU'
except Exception as error:
    print('GPU_FALLBACK '+str(error))
scene.render.resolution_x=1200 if draft else 1800
scene.render.resolution_y=800 if draft else 1200
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.image_settings.color_mode='RGB'
scene.render.film_transparent=False
scene.view_settings.view_transform='AgX'
scene.view_settings.look='AgX - Medium High Contrast'
scene.view_settings.exposure=0.5
scene.render.image_settings.color_depth='8'
scene['render_source_model']=str(SOURCE)
scene['render_style_status']='warm oak / warm white / greige material study, not a homeowner final style selection'
scene['render_original_furniture_geometry_preserved']=True

# Audit presentation part coordinates against the source. Baked source remains intact.
bpy.context.view_layer.update()
audit=[]
for group in DATA['furnitureObjects']:
    objects=[ob for ob in surface.objects if ob.parent==roots[group['id']]]
    points=[ob.matrix_world@Vector(v) for ob in objects for v in ob.bound_box]
    lo=[min(p[i] for p in points) for i in range(3)]
    hi=[max(p[i] for p in points) for i in range(3)]
    source_parts=[p for p in DATA['furniture'] if p['parent']==group['id']]
    expected_lo=[min(p['x'] for p in source_parts)/1000,
                 -max(p['z']+p['d'] for p in source_parts)/1000,
                 min(p.get('y',0) for p in source_parts)/1000]
    expected_hi=[max(p['x']+p['w'] for p in source_parts)/1000,
                 -min(p['z'] for p in source_parts)/1000,
                 max(p.get('y',0)+p['h'] for p in source_parts)/1000]
    error=max(abs(a-b) for a,b in zip(lo+hi,expected_lo+expected_hi))
    assert error<0.00001,(group['id'],error)
    audit.append(dict(id=group['id'],parts=len(objects),bounds_error_mm=round(error*1000,6)))

if not draft:
    scene.camera=views['living']
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'06_blender'/'home-v06-presentation-v01.blend'))
records=[]
for key,cam in views.items():
    if only and only!=key:continue
    scene.camera=cam
    path=OUT/(key+('-draft' if draft else '-cycles')+'.png')
    scene.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
    records.append(dict(view=key,path=str(path),camera_position=list(cam.location),lens=cam.data.lens))
report=dict(mode='local Blender Cycles',draft=draft,source_sha256=SHA,rendered=records,
            furniture_audit=audit,furniture_count=len(audit),parts=sum(a['parts'] for a in audit),
            source_main_model_unchanged=True,presentation_only_additions=['ceiling cap','window profiles','flush lights','niche light'],
            style='warm white cabinetry, pale oak, greige woven upholstery, soft daylight')
(ROOT/'logs'/('v06-material-draft.json' if draft else 'v06-material-render.json')).write_text(
    json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('MATERIAL_RENDER_DONE '+json.dumps(dict(draft=draft,views=[r['view'] for r in records],parts=report['parts'])))
