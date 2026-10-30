"""Body executed through the real Blender MCP; DATA, SOURCE_SHA and OUTPUT are injected."""
import bpy, json, math
from mathutils import Vector

if not bpy.context.scene.get('HomeDesign_ManagedSession'):
    raise RuntimeError('Refusing to replace an unmanaged scene')
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for existing in list(bpy.context.scene.collection.children):
    bpy.context.scene.collection.children.unlink(existing)
    if existing.users==0:bpy.data.collections.remove(existing)
for mesh in list(bpy.data.meshes):
    if mesh.users==0:bpy.data.meshes.remove(mesh)
scene=bpy.context.scene
scene.name='房屋主模型 v06 · 85英寸与贵妃沙发'
scene.unit_settings.system='METRIC'
scene.unit_settings.scale_length=1.0
scene.unit_settings.length_unit='MILLIMETERS'
scene['home_design_geometry_sha256']=SOURCE_SHA
scene['home_design_project_root']='D:/AI-Yang.cn/HomeDesign'
scene['home_design_geometry_status']=DATA['geometry_status']
scene['home_design_axis_mapping']='plan(x,z),height -> Blender(x,-z,height) / 1000'
scene['home_design_revision']=DATA['revision']
scene['home_design_assumptions']=json.dumps(DATA['assumptions'],ensure_ascii=False)
scene['home_design_move_step_mm']=100
scene['home_design_selected_schemes']='85英寸电视 / 上端贵妃沙发 / 四人靠墙餐桌 / 双人桌一椅 / 入户通长柜'
scene['home_design_office_gap_mm']=408

def collection(name):
    result=bpy.data.collections.new(name);scene.collection.children.link(result);return result
walls_collection=collection('01 墙体 · 高度及墙厚待核')
floor_collection=collection('02 地面')
windows_collection=collection('03 玻璃 · 阳台落地窗及主卧飘窗')
furniture_collection=collection('04 家具 · 整件选择 · 100mm')
labels_collection=collection('05 房间标记 · 仅观察用')
presentation_collection=collection('06 低墙观察副本 · 不用于几何核验')
camera_collection=collection('07 相机与灯光')
presentation_collection.hide_viewport=True
presentation_collection.hide_render=True
labels_collection.hide_render=True

def material(name,color,roughness=0.8):
    result=bpy.data.materials.new(name)
    result.use_nodes=True
    result.diffuse_color=tuple(color)
    shader=result.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value=tuple(color)
    shader.inputs['Roughness'].default_value=roughness
    return result
wall_material=material('墙面 · 中性示意',(0.82,0.81,0.77,1))
floor_material=material('地面 · 中性示意',(0.68,0.64,0.55,1))
glass_material=material('玻璃 · 示意',(0.45,0.68,0.76,0.30),0.15)
glass_material.node_tree.nodes.get('Principled BSDF').inputs['Alpha'].default_value=0.30
glass_material.surface_render_method='DITHERED'
text_material=material('文字',(0.12,0.16,0.18,1))
furniture_materials={}
for key,value in DATA['furnitureMaterials'].items():
    furniture_materials[key]=material(value['name'],value['color'],value['roughness'])

def part_mesh(part,anchor=(0,0,0)):
    x=part['x']/1000-anchor[0]
    y=-(part['z']+part['d'])/1000-anchor[1]
    z=part.get('y',0)/1000-anchor[2]
    w=part['w']/1000;d=part['d']/1000;h=part['h']/1000
    if part.get('shape')=='cylinder':
        count=32;verts=[]
        for level in [z,z+h]:
            for index in range(count):
                angle=2*math.pi*index/count
                verts.append((x+w/2+w/2*math.cos(angle),y+d/2+d/2*math.sin(angle),level))
        faces=[tuple(reversed(range(count))),tuple(range(count,2*count))]
        faces += [(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)]
    else:
        verts=[(x,y,z),(x+w,y,z),(x+w,y+d,z),(x,y+d,z),
               (x,y,z+h),(x+w,y,z+h),(x+w,y+d,z+h),(x,y+d,z+h)]
        faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    return verts,faces

def mesh_object(name,verts,faces,target,mats,indices=None):
    mesh=bpy.data.meshes.new(name+' mesh');mesh.from_pydata(verts,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);target.objects.link(obj)
    for mat in mats:mesh.materials.append(mat)
    if indices:
        for poly,index in zip(mesh.polygons,indices):poly.material_index=index
    return obj

for row in DATA['walls']:
    verts,faces=part_mesh(row)
    obj=mesh_object(row['id'],verts,faces,walls_collection,[wall_material])
    obj['home_design_role']='wall';obj['source_id']=row['id'];obj['confidence']=row.get('confidence','provisional')
    obj['source_mm']=json.dumps(row,ensure_ascii=False)
    obj.hide_select=True
    if row.get('y',0)<450:
        proxy=dict(row);proxy['h']=min(450-row.get('y',0),row['h'])
        verts,faces=part_mesh(proxy)
        low=mesh_object('观察副本 '+row['id'],verts,faces,presentation_collection,[wall_material])
        low['home_design_role']='presentation_only';low.hide_select=True
for row in DATA['glass']:
    verts,faces=part_mesh(row)
    obj=mesh_object(row['id'],verts,faces,windows_collection,[glass_material])
    obj['home_design_role']='glass';obj['source_id']=row['id'];obj['source_mm']=json.dumps(row)
    obj.hide_select=True

points=DATA['floor'];count=len(points)
vertices=[(x/1000,-z/1000,height) for height in [-0.16,0] for x,z in points]
faces=[tuple(range(count)),tuple(reversed(range(count,2*count)))]
faces += [(index,(index+1)%count,(index+1)%count+count,index+count) for index in range(count)]
floor=mesh_object('原户型轮廓 · 总长未闭合',vertices,faces,floor_collection,[floor_material])
floor.hide_select=True;floor['home_design_role']='floor';floor['thickness_mm']=160

for group in DATA['furnitureObjects']:
    pieces=[part for part in DATA['furniture'] if part['parent']==group['id']]
    anchor=(group['x']/1000,-group['z']/1000,0)
    verts=[];faces=[];indices=[];mats=[];keys=[]
    for part in pieces:
        key=part['material']
        if key not in keys:keys.append(key);mats.append(furniture_materials[key])
        index=keys.index(key)
        pv,pf=part_mesh(part,anchor);offset=len(verts)
        verts+=pv;faces += [tuple(offset+i for i in face) for face in pf];indices += [index]*len(pf)
    obj=mesh_object(group['id']+' | '+group['name'],verts,faces,furniture_collection,mats,indices)
    obj.location=anchor
    obj['home_design_role']='furniture';obj['source_id']=group['id'];obj['display_name']=group['name']
    obj['zone']=group['zone'];obj['scheme']=group['scheme'];obj['part_count']=len(pieces)
    obj['import_x_mm']=group['x'];obj['import_z_mm']=group['z'];obj['movement_step_mm']=100
    obj['part_source_mm']=json.dumps(pieces,ensure_ascii=False)
    obj['placement_source']='user furniture revision v06; latest prior widget positions preserved'
    obj['dimensions_mm']=[group['dimensionsMm'][key] for key in ['length','width','height']]
    obj['dimension_note']=group['detail']
    bevel=obj.modifiers.new('示意倒角','BEVEL');bevel.width=0.004;bevel.segments=2
    obj.lock_location[2]=True
    obj.lock_rotation[0]=True;obj.lock_rotation[1]=True

font=bpy.data.fonts.load('C:/Windows/Fonts/msyh.ttc')
for room in DATA['rooms']:
    data=bpy.data.curves.new('标记 '+room['id'],'FONT');data.body=room['name'];data.font=font
    data.size=0.27;data.align_x='CENTER';data.align_y='CENTER';data.materials.append(text_material)
    obj=bpy.data.objects.new('房间 '+room['name'],data);labels_collection.objects.link(obj)
    obj.location=(room['x']/1000,-room['z']/1000,0.025);obj.hide_select=True
    obj['home_design_role']='annotation'

def camera(name,position,target,ortho):
    data=bpy.data.cameras.new(name);data.type='ORTHO';data.ortho_scale=ortho
    obj=bpy.data.objects.new(name,data);camera_collection.objects.link(obj);obj.location=position
    direction=Vector(target)-obj.location;obj.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
    obj['home_design_role']='presentation_camera';return obj
top=camera('相机 · 正交顶视',(5.28,-6.1,25),(5.28,-6.1,0),14.6)
top.rotation_euler=(0,0,0)
iso=camera('相机 · 正交轴测',(5,-20,17),(4.9,-5.8,0),18.8)
scene.camera=top
world=bpy.data.worlds.new('中性环境');world.use_nodes=True
world.node_tree.nodes.get('Background').inputs[0].default_value=(0.8,0.85,0.9,1)
world.node_tree.nodes.get('Background').inputs[1].default_value=0.6
scene.world=world
for name,position,power,size in [('主光',(-3,-3,12),1600,8),('补光',(10,-10,8),950,6)]:
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size
    obj=bpy.data.objects.new(name,data);camera_collection.objects.link(obj);obj.location=position
    obj.rotation_euler=(Vector((5,-6,0))-obj.location).to_track_quat('-Z','Y').to_euler()
scene.render.engine='CYCLES';scene.cycles.samples=24
scene.cycles.use_denoising=True
scene.render.resolution_x=1400;scene.render.resolution_y=1560;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
scene.tool_settings.use_snap=True
scene.tool_settings.snap_elements={'INCREMENT'}
scene.tool_settings.use_snap_grid_absolute=False
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.clip_end=200
            area.spaces.active.region_3d.view_distance=16
            area.spaces.active.region_3d.view_location=(5.1,-6.1,0)
            area.spaces.active.region_3d.view_rotation=top.rotation_euler.to_quaternion()
            area.spaces.active.region_3d.view_perspective='ORTHO'
            area.spaces.active.overlay.grid_scale=0.1
            area.spaces.active.shading.type='MATERIAL'
            area.spaces.active.show_region_ui=True
bpy.ops.object.select_all(action='DESELECT')
sofa=next(obj for obj in furniture_collection.objects if obj['source_id']=='sofa-modular')
sofa.select_set(True);bpy.context.view_layer.objects.active=sofa
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=OUTPUT)
print('MODEL_IMPORTED '+json.dumps(dict(file=bpy.data.filepath,furniture=len(furniture_collection.objects),parts=sum(o['part_count'] for o in furniture_collection.objects),walls=len(walls_collection.objects),glass=len(windows_collection.objects),source_sha256=SOURCE_SHA)))
