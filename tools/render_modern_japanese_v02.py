"""Apply the homeowner's modern Japanese / curved-edge brief to a sibling scene."""
from pathlib import Path
from mathutils import Vector, Matrix
import bpy
import hashlib
import json
import math
import sys

ROOT=Path(r'D:\AI-Yang.cn\HomeDesign')
OUT=ROOT/'07_renders/v06-japanese-v02'
OUT.mkdir(parents=True,exist_ok=True)
BASE=ROOT/'06_blender/home-v06-presentation-v01.blend'
DEST=ROOT/'06_blender/home-v06-japanese-v02.blend'
DATA=json.loads((ROOT/'02_geometry/geometry-master-v06.json').read_text(encoding='utf-8'))
style_raw=(ROOT/'05_style/modern-japanese-v02.json').read_bytes()
STYLE=json.loads(style_raw)
scene=bpy.context.scene
assert Path(bpy.data.filepath).resolve()==BASE.resolve()
assert scene['home_design_geometry_sha256']==STYLE['geometry_sha256']
assert hashlib.sha256((ROOT/'02_geometry/geometry-master-v06.json').read_bytes()).hexdigest()==STYLE['geometry_sha256']
draft='--draft' in sys.argv
only=next((s.split('=',1)[1] for s in sys.argv if s.startswith('--view=')),None)
decisions=STYLE['designer_decisions']
parts={o['source_part_id']:o for o in scene.objects if o.get('source_part_id')}
assert len(parts)==206
baseline={o['source_id']:o for o in scene.objects if o.get('home_design_role')=='furniture'}
assert len(baseline)==14
surfaces=bpy.data.collections['08 写实表现 · 按原家具零件生成']
detail=bpy.data.collections['09 写实表现 · 灯光和饰面建议']

def material(name,color,roughness=0.85):
    mat=bpy.data.materials.new(name)
    mat.use_nodes=True
    p=mat.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=roughness
    p.inputs['Sheen Weight'].default_value=0.20
    noise=mat.node_tree.nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value=400
    noise.inputs['Detail'].default_value=2
    bump=mat.node_tree.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value=0.22
    bump.inputs['Distance'].default_value=0.00055
    mat.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height'])
    mat.node_tree.links.new(bump.outputs['Normal'],p.inputs['Normal'])
    return mat

sage=material('J02 · 低饱和苔绿色织物',(0.17,0.245,0.16))
navy=material('J02 · 深蓝色织物',(0.018,0.045,0.083))
navy_book=material('J02 · 深蓝书脊',(0.026,0.06,0.105))
for part_id in ['office-chair-1-seat','office-chair-1-back']:
    ob=parts[part_id]
    ob.data.materials.clear();ob.data.materials.append(sage)
for ob in [parts['dining-chair-1-seat'],parts['dining-chair-2-seat']]:
    ob.data.materials.clear();ob.data.materials.append(sage)
parts['tv-high-niche-tray'].data.materials.clear()
parts['tv-high-niche-tray'].data.materials.append(navy_book)
for index,ob in enumerate(o for k,o in parts.items() if k.startswith('bookcase-book-')):
    if index in [3,13,23,33]:
        ob.data.materials.clear();ob.data.materials.append(navy_book)

# Door fronts and the old proxy carcasses shared one plane. Recess the hidden
# carcass behind the doors before joining, avoiding coincident surfaces.
for part_id,ob in parts.items():
    if not part_id.endswith('-body'):continue
    p=json.loads(ob['source_mm'])
    if p['parent'] not in ['tv-low','tv-high','bookcase']:continue
    width=p['w']/1000
    for vertex in ob.data.vertices:
        if p['parent']=='bookcase' and abs(vertex.co.x)<1e-7:vertex.co.x+=0.020
        elif p['parent']!='bookcase' and abs(vertex.co.x-width)<1e-7:vertex.co.x-=0.020
        if abs(vertex.co.z-p['h']/1000)<1e-7:vertex.co.z-=0.020
    ob.data.update()

def profile_mesh(name,w,d,h,radii):
    # Four plan radii, world XY: BL, BR, TR, TL. Positive, tangent, within bbox.
    assert all(r>=0 for r in radii)
    assert radii[0]+radii[1]<=w+1e-8 and radii[2]+radii[3]<=w+1e-8
    assert radii[0]+radii[3]<=d+1e-8 and radii[1]+radii[2]<=d+1e-8
    points=[]
    corners=[(radii[0],radii[0],180),(w-radii[1],radii[1],270),
             (w-radii[2],d-radii[2],0),(radii[3],d-radii[3],90)]
    for index,(cx,cy,start) in enumerate(corners):
        radius=radii[index]
        candidates=[(cx+radius*math.cos(math.radians(start+i*90/20)),
                     cy+radius*math.sin(math.radians(start+i*90/20))) for i in range(21)] if radius else [(cx,cy)]
        for p in candidates:
            if not points or math.dist(points[-1],p)>1e-9:points.append(p)
    if math.dist(points[-1],points[0])<1e-9:points.pop()
    n=len(points)
    vertices=[(x,y,z) for z in [0,h] for x,y in points]
    faces=[tuple(reversed(range(n))),tuple(range(n,n*2))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    mesh=bpy.data.meshes.new(name+' · 弧形轮廓')
    mesh.from_pydata(vertices,[],faces);mesh.update()
    for p in mesh.polygons:p.use_smooth=len(p.vertices)==4
    return mesh

def edge_bevel(ob,width):
    mod=ob.modifiers.new('触边柔化','BEVEL');mod.width=width;mod.segments=3;mod.harden_normals=True
    normal=ob.modifiers.new('弧面法线','WEIGHTED_NORMAL');normal.keep_sharp=True

table_records=[]
for part_id,radius_mm in decisions['table_corner_radii_mm'].items():
    assert part_id in parts,part_id
    ob=parts[part_id]
    p=json.loads(ob['source_mm'])
    w,d,h=[p[k]/1000 for k in ['w','d','h']]
    old_materials=list(ob.data.materials)
    for mod in list(ob.modifiers):ob.modifiers.remove(mod)
    ob.data=profile_mesh(part_id,w,d,h,[radius_mm/1000]*4)
    for mat in old_materials:ob.data.materials.append(mat)
    edge_bevel(ob,0.003)
    ob['style_corner_radius_mm']=radius_mm
    table_records.append(dict(part=part_id,corner_radius_mm=radius_mm,bounds_mm=[p['w'],p['d'],p['h']]))

# Two small soft accessories belong to the existing sofa assembly, not extra furniture.
sofa_root=parts['sofa-modular-back'].parent
accessories=[]
for label,planz,mat in [('green',2420,sage),('navy',3600,navy)]:
    w,d,h=0.16,0.38,0.38
    mesh=bpy.data.meshes.new('抱枕 '+label)
    v=[(0,0,0),(w,0,0),(w,d,0),(0,d,0),(0,0,h),(w,0,h),(w,d,h),(0,d,h)]
    f=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    mesh.from_pydata(v,[],f);mesh.materials.append(mat)
    for p in mesh.polygons:p.use_smooth=True
    ob=bpy.data.objects.new('sofa-pillow-'+label,mesh);surfaces.objects.link(ob)
    ob.location=(4.39,-(planz/1000+d),0.43);ob.parent=sofa_root
    mod=ob.modifiers.new('柔软枕角','BEVEL');mod.width=0.074;mod.segments=8;mod.harden_normals=True
    ob.modifiers.new('织物法线','WEIGHTED_NORMAL')
    ob['home_design_role']='sofa_accessory';ob['style_source']='homeowner allowed green/navy accent, designer placement'
    accessories.append(ob.name)

curves=bpy.data.collections.new('11 弧形饰面意向 · 墙基线备查保留')
scene.collection.children.link(curves)
wall_records=[]
for source_id,radii_mm in decisions['wall_finish_profiles_mm'].items():
    original=next(o for o in scene.objects if o.get('home_design_role')=='wall' and o.get('source_id')==source_id)
    p=json.loads(original['source_mm'])
    mesh=profile_mesh('饰面 '+source_id,p['w']/1000,p['d']/1000,p['h']/1000,[r/1000 for r in radii_mm])
    for polygon in mesh.polygons:polygon.use_smooth=False
    for mat in original.data.materials:mesh.materials.append(mat)
    ob=bpy.data.objects.new('弧形饰面 '+source_id,mesh);curves.objects.link(ob)
    ob.location=(p['x']/1000,-(p['z']+p['d'])/1000,p.get('y',0)/1000)
    mod=ob.modifiers.new('饰面收口柔化','BEVEL');mod.width=0.001;mod.segments=2
    ob['home_design_role']='wall_finish_proposal';ob['source_wall_id']=source_id
    ob['plan_radii_mm']=radii_mm;ob['construction_status']=decisions['wall_construction_status']
    ob.hide_select=True
    original.hide_render=True;original.hide_set(True)
    wall_records.append(dict(wall=source_id,corner_radii_mm=radii_mm,baseline_retained=True,finish_inside_baseline_bbox=True))

# Remove coincident outer faces at overlapping wall boxes in the display union.
# The original 60 full wall references remain intact; door/window voids are unchanged.
def rect_subtract(rect,cut):
    x0,y0,x1,y1=rect;a0,b0,a1,b1=cut
    ix0,iy0,ix1,iy1=max(x0,a0),max(y0,b0),min(x1,a1),min(y1,b1)
    if ix1-ix0<1e-8 or iy1-iy0<1e-8:return [rect]
    candidates=[(x0,y0,ix0,y1),(ix1,y0,x1,y1),(ix0,y0,ix1,iy0),(ix0,iy1,ix1,y1)]
    return [r for r in candidates if r[2]-r[0]>1e-8 and r[3]-r[1]>1e-8]
boxes=[]
for row in DATA['walls']:
    boxes.append(([row['x']/1000,-(row['z']+row['d'])/1000,row.get('y',0)/1000],
                  [(row['x']+row['w'])/1000,-row['z']/1000,(row.get('y',0)+row['h'])/1000]))
vertices=[];faces=[]
for i,(lo,hi) in enumerate(boxes):
    if DATA['walls'][i]['id'] in decisions['wall_finish_profiles_mm']:continue
    for axis in range(3):
        u,v=[k for k in range(3) if k!=axis]
        for positive in [False,True]:
            plane=hi[axis] if positive else lo[axis]
            rectangles=[(lo[u],lo[v],hi[u],hi[v])]
            for j,(other_lo,other_hi) in enumerate(boxes):
                if i==j:continue
                if positive:
                    hidden=other_lo[axis]<=plane+1e-8 and other_hi[axis]>plane+1e-8
                    duplicate=abs(other_hi[axis]-plane)<1e-8 and other_lo[axis]<plane-1e-8 and j<i
                else:
                    hidden=other_lo[axis]<plane-1e-8 and other_hi[axis]>=plane-1e-8
                    duplicate=abs(other_lo[axis]-plane)<1e-8 and other_hi[axis]>plane+1e-8 and j<i
                if hidden or duplicate:
                    cut=(other_lo[u],other_lo[v],other_hi[u],other_hi[v])
                    rectangles=[r2 for r in rectangles for r2 in rect_subtract(r,cut)]
            for a,b,c,d in rectangles:
                quad=[]
                for uu,vv in [(a,b),(c,b),(c,d),(a,d)]:
                    point=[0.0]*3;point[axis]=plane;point[u]=uu;point[v]=vv
                    quad.append(tuple(point))
                normal=(Vector(quad[1])-Vector(quad[0])).cross(Vector(quad[2])-Vector(quad[0]))
                if (normal[axis]>0)!=positive:quad.reverse()
                offset=len(vertices);vertices.extend(quad);faces.append(tuple(range(offset,offset+4)))
mesh=bpy.data.meshes.new('墙体显示并集 · 去除重合面')
mesh.from_pydata(vertices,[],faces);mesh.update()
wall_mat=next(o for o in scene.objects if o.get('home_design_role')=='wall').data.materials[0]
mesh.materials.append(wall_mat)
union=bpy.data.objects.new('墙体显示并集 · 完整高度与开口',mesh);curves.objects.link(union)
union['home_design_role']='wall_visual_union';union['source_wall_count']=60
union['display_note']='axis aligned source box union, four curved finish profiles rendered separately'
union.hide_select=True
for ob in scene.objects:
    if ob.get('home_design_role')=='wall':ob.hide_render=True;ob.hide_set(True)

# Retain original furniture as hidden archival references. Visible furniture is 14 complete selectable meshes.
archive=bpy.data.collections.new('12 家具矩形基线 · 隐藏备查')
scene.collection.children.link(archive)
archive.hide_render=True;archive.hide_viewport=True
target=bpy.data.collections['04 家具 · 整件选择 · 100mm']
target.hide_render=False;target.hide_viewport=False
for ob in baseline.values():
    archive.objects.link(ob)
    for c in list(ob.users_collection):
        if c!=archive:c.objects.unlink(ob)
    ob['home_design_role']='baseline_furniture_reference';ob.hide_select=True
bpy.context.view_layer.update()
audit=[]
for group in DATA['furnitureObjects']:
    root=next(o for o in surfaces.objects if o.get('source_id')==group['id'])
    children=[o for o in surfaces.objects if o.parent==root]
    assert children
    bpy.ops.object.select_all(action='DESELECT')
    for ob in children:
        ob.hide_set(False);ob.select_set(True)
        bpy.context.view_layer.objects.active=ob
        for mod in list(ob.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.context.view_layer.objects.active=children[0]
    bpy.ops.object.join()
    ob=bpy.context.view_layer.objects.active
    world_vertices=[ob.matrix_world@v.co for v in ob.data.vertices]
    anchor=Vector((group['x']/1000,-group['z']/1000,0))
    ob.parent=None;ob.matrix_world=Matrix.Identity(4);ob.location=anchor
    for vertex,point in zip(ob.data.vertices,world_vertices):vertex.co=point-anchor
    for key,value in baseline[group['id']].items():ob[key]=value
    ob['home_design_role']='furniture';ob['style_revision']='modern-japanese-v02'
    ob['part_count']=len(children);ob['movement_step_mm']=100
    ob.name=group['id']+' | '+group['name']+' · 日式圆角'
    ob.lock_location[2]=True;ob.lock_rotation[0]=True;ob.lock_rotation[1]=True
    target.objects.link(ob)
    for c in list(ob.users_collection):
        if c!=target:c.objects.unlink(ob)
    bpy.data.objects.remove(root,do_unlink=True)
    bpy.context.view_layer.update()
    expected=[p for p in DATA['furniture'] if p['parent']==group['id']]
    points=[ob.matrix_world@v.co for v in ob.data.vertices]
    lo=[min(v[i] for v in points) for i in range(3)];hi=[max(v[i] for v in points) for i in range(3)]
    elo=[min(p['x'] for p in expected)/1000,-max(p['z']+p['d'] for p in expected)/1000,min(p.get('y',0) for p in expected)/1000]
    ehi=[max(p['x']+p['w'] for p in expected)/1000,-min(p['z'] for p in expected)/1000,max(p.get('y',0)+p['h'] for p in expected)/1000]
    error=max(abs(a-b) for a,b in zip(lo+hi,elo+ehi))*1000
    assert error<0.02,(group['id'],error)
    audit.append(dict(id=group['id'],parts=len(children),bounds_error_mm=round(error,6),position_mm=[group['x'],group['z']]))

# Exercise the actual existing 100 mm movement operator on every new assembly, then restore.
sys.path.insert(0,str(ROOT/'tools'))
import home_design_move
try:
    bpy.ops.home_design.move.get_rna_type()
except KeyError:
    home_design_move.register()
movement=[]
for ob in target.objects:
    bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
    start=ob.location.copy()
    for axis,index in [('X',0),('Y',1)]:
        bpy.ops.home_design.move(axis=axis,direction=1)
        assert abs(ob.location[index]-start[index]-0.1)<1e-6
        bpy.ops.home_design.move(axis=axis,direction=-1)
        assert (ob.location-start).length<1e-6
    movement.append(dict(id=ob['source_id'],x_step_mm=100,y_step_mm=100,restored=True))

scene.name='v06 · 现代日式简约 · 圆角与暖色'
scene['home_design_style_revision']='modern-japanese-v02'
scene['home_design_style_file']='05_style/modern-japanese-v02.json'
scene['home_design_style_sha256']=hashlib.sha256(style_raw).hexdigest()
scene['render_style_status']='homeowner selected modern Japanese minimal, warm, rounded tables/wall corners; green and navy allowed'
scene['render_original_furniture_geometry_preserved']=False
scene['render_furniture_placements_and_envelopes_preserved']=True
scene['render_geometry_note']='tables have true rounded XY profiles; wall finish proposals within baseline envelopes; rectangular source references retained hidden'
scene.camera=bpy.data.objects['办公区 · 沙发后双人桌']
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_perspective='CAMERA'
            area.spaces.active.overlay.show_overlays=False
            area.spaces.active.shading.type='MATERIAL'
scene.cycles.samples=32 if draft else 128
prefs=bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type='OPTIX';prefs.get_devices()
for device in prefs.devices:device.use=device.type!='CPU'
scene.cycles.device='GPU'
scene.render.resolution_x=1200 if draft else 1800
scene.render.resolution_y=800 if draft else 1200
scene.render.filepath=str(OUT/'office-cycles.png')
if not draft:
    bpy.ops.object.select_all(action='DESELECT')
    sofa=next(o for o in target.objects if o.get('source_id')=='sofa-modular')
    sofa.select_set(True);bpy.context.view_layer.objects.active=sofa
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(DEST))
views={'living':'客厅 · 电视与贵妃沙发','office':'办公区 · 沙发后双人桌',
       'office-detail':'办公区细节 · 双工位单椅','dining':'餐厅 · 四椅与入户通长柜'}
records=[]
if '--diagnose' in sys.argv:
    scene.camera=bpy.data.objects[views['dining']]
    bpy.context.view_layer.update()
    frame=scene.camera.data.view_frame(scene=scene)
    rays=[]
    for px,py in [(750,260),(290,405),(12,380),(620,380),(1050,400)]:
        vx=min(v.x for v in frame)+(max(v.x for v in frame)-min(v.x for v in frame))*px/1200
        vy=max(v.y for v in frame)-(max(v.y for v in frame)-min(v.y for v in frame))*py/800
        direction=scene.camera.matrix_world.to_3x3()@Vector((vx,vy,frame[0].z)).normalized()
        hit,location,normal,index,obj,matrix=scene.ray_cast(bpy.context.evaluated_depsgraph_get(),scene.camera.location,direction)
        data=dict(pixel=[px,py],hit=hit)
        if hit:
            evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
            material_index=evaluated.data.polygons[index].material_index
            mat=obj.data.materials[material_index] if obj.data.materials else None
            data.update(object=obj.name,role=obj.get('home_design_role'),material=mat.name if mat else None,
                        material_index=material_index,normal=list(normal),location=list(location),
                        color=list(mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value) if mat else None)
        rays.append(data)
    (ROOT/'logs/japanese-v02-ray-diagnosis.json').write_text(json.dumps(rays,ensure_ascii=False,indent=2),encoding='utf-8')
    print('DIAGNOSIS_DONE')
    raise SystemExit(0)
for name,cam in views.items():
    if only and name!=only:continue
    scene.camera=bpy.data.objects[cam]
    scene.render.filepath=str(OUT/(name+('-draft' if draft else '-cycles')+'.png'))
    bpy.ops.render.render(write_still=True)
    records.append(dict(view=name,path=scene.render.filepath,camera_position=list(scene.camera.location),lens=scene.camera.data.lens))
report=dict(mode='Blender Cycles',draft=draft,source_geometry_sha256=STYLE['geometry_sha256'],
            style_sha256=scene['home_design_style_sha256'],file=str(DEST),
            tables=table_records,wall_finish_proposals=wall_records,furniture=audit,
            movement_100mm=movement,major_furniture_count=len(audit),source_parts=206,sofa_accessories=accessories,
            all_envelopes_and_placements_preserved=True,rendered=records,baseline_main_unchanged=True)
(ROOT/'logs'/('japanese-v02-draft.json' if draft else 'japanese-v02-render.json')).write_text(
    json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('JAPANESE_V02_DONE '+json.dumps(dict(draft=draft,furniture=len(audit),views=list(views),source_parts=206,style_accessories=2)))
