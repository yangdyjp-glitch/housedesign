"""Continue the existing rounded Japanese model, retaining full architectural sources."""
from pathlib import Path
from mathutils import Vector, Matrix
import bpy, bmesh, json, hashlib, math, sys, ast

ROOT=Path(r'D:\AI-Yang.cn\HomeDesign')
SOURCE=ROOT/'06_blender/home-v06-japanese-v02.blend'
DEST=ROOT/'06_blender/home-main-v07.blend'
assert Path(bpy.data.filepath).resolve()==SOURCE.resolve()
assert not DEST.exists() or '--replace-draft' in sys.argv, 'Existing v07 requires explicit draft replacement.'
raw=(ROOT/'02_geometry/geometry-master-v07.json').read_bytes();DATA=json.loads(raw)
style_raw=(ROOT/'05_style/modern-japanese-v03.json').read_bytes();STYLE=json.loads(style_raw)
assert hashlib.sha256(raw).hexdigest()==STYLE['geometry_sha256']
scene=bpy.context.scene
assert scene['home_design_revision']==6
target=bpy.data.collections['04 家具 · 整件选择 · 100mm']
existing={o['source_id']:o for o in scene.objects if o.get('home_design_role')=='furniture'}
assert len(existing)==14
# Reuse only the reviewed profile function, never the old script's top-level mutations.
tree=ast.parse((ROOT/'tools/render_modern_japanese_v02.py').read_text(encoding='utf-8'))
node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='profile_mesh')
exec(compile(ast.Module(body=[node],type_ignores=[]),'profile_mesh','exec'))

mats={
 'wood':bpy.data.materials['R01 · 浅橡木细纹'], 'cabinet':bpy.data.materials['R01 · 暖白哑光柜门'],
 'fabric':bpy.data.materials['R01 · 米灰亚麻混纺'], 'fabric-dark':bpy.data.materials['R01 · 沙发框体织物'],
 'metal':bpy.data.materials['R01 · 深灰细砂金属'], 'screen':bpy.data.materials['R01 · 关闭的黑玻璃屏幕'],
 'book':bpy.data.materials['R01 · 灰绿书脊'], 'sage':bpy.data.materials['J02 · 低饱和苔绿色织物'],
 'navy':bpy.data.materials['J02 · 深蓝书脊']}
for key in DATA['furnitureMaterials']:
    if key in mats:continue
    rec=DATA['furnitureMaterials'][key]
    m=bpy.data.materials.new('V07 · '+key);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=rec['color'];p.inputs['Roughness'].default_value=rec['roughness']
    if key.startswith('foliage'):p.inputs['Subsurface Weight'].default_value=.06
    mats[key]=m

def mesh_part(p):
    w,dep,h=[p[k]/1000 for k in ['w','d','h']]
    x,y,z=p['x']/1000,-(p['z']+p['d'])/1000,p['y']/1000
    shape=p.get('shape','box')
    if shape in ['box','rounded_box']:
        r=p.get('radiusMm',0)/1000
        mesh=profile_mesh(p['id'],w,dep,h,[r]*4)
    else:
        n=32;verts=[];faces=[]
        if shape=='leaf':
            flip=p.get('leafFlip',1);steps=10
            for j in range(steps+1):
                t=j/steps;s=math.sin(math.pi*t)
                verts += [(w/2-w/2*s,dep/2-flip*dep/2*s,h*t),
                          (w/2,dep/2+dep*.09*s,h*t+.008*s),
                          (w/2+w/2*s,dep/2+flip*dep/2*s,h*t)]
            for j in range(steps):
                for i in range(2):
                    a=j*3+i;faces.append((a,a+1,a+4,a+3))
        elif shape=='branch':
            conv=lambda q:Vector((q[0]/1000,dep-q[2]/1000,q[1]/1000))
            a,b=conv(p['startLocal']),conv(p['endLocal']);axis=(b-a).normalized()
            u=axis.cross(Vector((0,0,1))).normalized();v=axis.cross(u).normalized();rr=p['radiusMm']/1000
            for point in [a,b]:
                for i in range(n):
                    vv=point+rr*(u*math.cos(2*math.pi*i/n)+v*math.sin(2*math.pi*i/n));verts.append(tuple(vv))
            faces=[tuple(reversed(range(n))),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
        elif shape=='ellipsoid':
            rows=12
            verts=[(w/2,dep/2,0)]
            for j in range(1,rows):
                lat=-math.pi/2+math.pi*j/rows
                for i in range(n):
                    a=2*math.pi*i/n
                    verts.append((w/2+w/2*math.cos(lat)*math.cos(a),dep/2+dep/2*math.cos(lat)*math.sin(a),h/2+h/2*math.sin(lat)))
            top=len(verts);verts.append((w/2,dep/2,h))
            faces += [(0,1+(i+1)%n,1+i) for i in range(n)]
            for j in range(rows-2):
                off=1+j*n;nxt=off+n
                faces += [(off+i,off+(i+1)%n,nxt+(i+1)%n,nxt+i) for i in range(n)]
            faces += [(top,1+(rows-2)*n+i,1+(rows-2)*n+(i+1)%n) for i in range(n)]
        else:
            for k in range(2):
                radius=p.get('bottomScale',1) if shape=='frustum' and k==0 else p.get('topScale',1) if shape=='frustum' else 1
                for i in range(n):
                    a=2*math.pi*i/n
                    if p.get('axis')=='x':point=(k*w,dep/2+math.cos(a)*dep/2,z*0+h/2+math.sin(a)*h/2)
                    else:point=(w/2+math.cos(a)*w/2*radius,dep/2+math.sin(a)*dep/2*radius,k*h)
                    verts.append(point)
            faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
            faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
        mesh=bpy.data.meshes.new(p['id']);mesh.from_pydata(verts,[],faces);mesh.update()
        for poly in mesh.polygons:poly.use_smooth=shape in ['ellipsoid','leaf'] or len(poly.vertices)==4
    mesh.materials.append(mats[p['material']])
    ob=bpy.data.objects.new(p['id'],mesh);target.objects.link(ob);ob.location=(x,y,z)
    if shape in ['box','rounded_box']:
        # Keep the original external bounds; small material edge rounding only.
        mod=ob.modifiers.new('触边圆润','BEVEL');mod.width=min(p.get('bevelMm',3)/1000,min(w,dep,h)*.25);mod.segments=3
        mod.harden_normals=True
        ob.modifiers.new('表面法线','WEIGHTED_NORMAL')
    ob['source_part_id']=p['id'];ob['source_mm']=json.dumps(p,ensure_ascii=False)
    return ob

for group in DATA['furnitureObjects']:
    gid=group['id'];pp=[p for p in DATA['furniture'] if p['parent']==gid]
    if gid in existing and gid!='double-desk':
        ob=existing[gid]
        if gid in ['sofa-modular','side-table','ottoman']:ob.location.y-=.5
    else:
        if gid in existing:bpy.data.objects.remove(existing[gid],do_unlink=True)
        children=[mesh_part(p) for p in pp]
        bpy.ops.object.select_all(action='DESELECT')
        for ob in children:
            ob.select_set(True);bpy.context.view_layer.objects.active=ob
            for mod in list(ob.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.context.view_layer.objects.active=children[0];bpy.ops.object.join()
        ob=bpy.context.view_layer.objects.active
        bpy.context.view_layer.update()
        world=[ob.matrix_world@v.co for v in ob.data.vertices];anchor=Vector((group['x']/1000,-group['z']/1000,0))
        ob.matrix_world=Matrix.Identity(4);ob.location=anchor
        for vertex,point in zip(ob.data.vertices,world):vertex.co=point-anchor
        bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
    ob.name=gid+' | '+group['name']
    ob['home_design_role']='furniture';ob['source_id']=gid;ob['display_name']=group['name']
    ob['zone']=group['zone'];ob['scheme']=group['scheme'];ob['part_count']=len(pp)
    ob['import_x_mm']=group['x'];ob['import_z_mm']=group['z'];ob['movement_step_mm']=100
    ob['dimensions_mm']=[group['dimensionsMm'][k] for k in ['length','width','height']]
    ob['dimension_note']=group['detail'];ob['part_source_mm']=json.dumps(pp,ensure_ascii=False)
    ob['style_revision']='modern-japanese-v03';ob['base_height_mm']=group['baseHeightMm']
    if group.get('movementGroup'):ob['movement_group']=group['movementGroup']
    ob.lock_location[2]=True;ob.lock_rotation[0]=True;ob.lock_rotation[1]=True
    ob.hide_select=False

bpy.context.view_layer.update()
furniture={o['source_id']:o for o in scene.objects if o.get('home_design_role')=='furniture'}
assert len(furniture)==21
audit=[]
for group in DATA['furnitureObjects']:
    ob=furniture[group['id']];pts=[ob.matrix_world@v.co for v in ob.data.vertices]
    lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
    b=group['meshBoundsMm'];elo=[b['x']/1000,-(b['z']+b['d'])/1000,b['y']/1000];ehi=[(b['x']+b['w'])/1000,-b['z']/1000,(b['y']+b['h'])/1000]
    error=max(abs(a-b) for a,b in zip(lo+hi,elo+ehi))*1000
    assert error<.03,(group['id'],error,lo,hi,elo,ehi)
    audit.append(dict(id=group['id'],position_mm=[group['x'],group['z']],mesh_bounds_error_mm=round(error,6),dimensions_mm=list(ob['dimensions_mm'])))

# Load the locally updated movement operator; includes linked washer/dryer movement.
sys.path.insert(0,str(ROOT/'tools'))
import home_design_move
for cls in reversed(home_design_move.CLASSES):
    registered=cls.bl_rna_get_subclass_py(cls.__name__,None)
    if registered:
        try:bpy.utils.unregister_class(registered)
        except RuntimeError:pass
try:home_design_move.register()
except ValueError:pass
movement=[]
for gid,ob in furniture.items():
    bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
    starts={i:o.location.copy() for i,o in furniture.items()}
    for axis,index in [('X',0),('Y',1)]:
        bpy.ops.home_design.move(axis=axis,direction=1)
        assert abs(ob.location[index]-starts[gid][index]-.1)<1e-6
        if ob.get('movement_group'):
            other=furniture['dryer' if gid=='washer' else 'washer']
            assert abs(other.location[index]-starts[other['source_id']][index]-.1)<1e-6
        bpy.ops.home_design.move(axis=axis,direction=-1)
        assert all((o.location-starts[i]).length<1e-6 for i,o in furniture.items())
    movement.append(gid)

scene.name='v07 · 现代日式 · 绿植角与单屏办公'
scene['home_design_revision']=7;scene['home_design_geometry_sha256']=STYLE['geometry_sha256']
scene['home_design_style_sha256']=hashlib.sha256(style_raw).hexdigest();scene['home_design_style_revision']='modern-japanese-v03'
scene['home_design_style_file']='05_style/modern-japanese-v03.json';scene['home_design_compass']='上南、下北、左东、右西（用户图示）'
scene['home_design_geometry_status']=DATA['geometry_status'];scene['home_design_assumptions']=json.dumps(DATA['assumptions'],ensure_ascii=False)
scene['home_design_selected_schemes']='85寸电视 / 北移500mm贵妃组合 / 四椅靠墙餐桌 / 双人桌一把椅一台34寸屏 / L形入户立柜 / 阳台绿植与叠放洗烘'
scene['home_design_monitor_count']=1
scene['home_design_project_root']=ROOT.as_posix()
bpy.ops.home_design.export_layout()

# Add two new eye-level viewpoints. Architecture stays complete in the saved main model.
camera_coll=bpy.data.collections['10 写实表现 · 人眼视角']
def camera(name,position,lookat,lens):
    data=bpy.data.cameras.new(name);data.type='PERSP';data.lens=lens;data.sensor_width=36;data.clip_start=.02
    ob=bpy.data.objects.new(name,data);camera_coll.objects.link(ob);ob.location=position
    ob.rotation_euler=(Vector(lookat)-ob.location).to_track_quat('-Z','Y').to_euler();return ob
camera('v07 · 阳台植物与洗烘',(3.7,-4.85,1.7),(3.5,-.25,1.05),19)
camera('v07 · 入户L形柜',(1.95,-8.7,1.6),(.62,-10.6,1.15),23)
camera('v07 · 电视右侧绿植',(4.2,-3.6,1.65),(.65,-1.45,1.0),25)
office=bpy.data.objects['办公区细节 · 双工位单椅']
office.location=(6.6,-5.3,1.7);office.rotation_euler=(Vector((5.65,-2.9,1.03))-office.location).to_track_quat('-Z','Y').to_euler();office.data.lens=27
scene.camera=bpy.data.objects['v07 · 电视右侧绿植']
scene.cycles.samples=96;scene.cycles.use_denoising=True;scene.cycles.device='GPU'
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for device in prefs.devices:device.use=device.type!='CPU'
scene.render.resolution_x=1800;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
bpy.ops.object.select_all(action='DESELECT');furniture['sofa-modular'].select_set(True);bpy.context.view_layer.objects.active=furniture['sofa-modular']
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(DEST))
(ROOT/'logs/model-v07-build.json').write_text(json.dumps(dict(model=str(DEST),geometry_sha256=STYLE['geometry_sha256'],furniture=audit,movement_100mm=movement,linked_laundry_movement=True,architecture_preserved=True),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('MODEL_V07_BUILT '+json.dumps(dict(furniture=len(furniture),movement=len(movement),parts=len(DATA['furniture']))))
