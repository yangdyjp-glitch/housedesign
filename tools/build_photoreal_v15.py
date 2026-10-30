"""Photographic presentation sibling of v14; preserve architecture and all 27 placements."""
from pathlib import Path
from mathutils import Vector,Matrix
import bpy,bmesh,json,hashlib,math,ast,sys
ROOT=Path(r'D:\AI-Yang.cn\HomeDesign');BASE=ROOT/'06_blender/home-main-v14.blend';DEST=ROOT/'06_blender/home-v14-photoreal-v15.blend';ASSETS=ROOT/'08_assets/photoreal-v15'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert Path(bpy.data.filepath).resolve()==BASE.resolve()
assert not DEST.exists() or '--replace-draft' in sys.argv
d=json.loads((ROOT/'02_geometry/geometry-master-v14.json').read_text(encoding='utf-8'));scene=bpy.context.scene
assert scene['home_design_revision']==14 and scene['home_design_geometry_sha256']==sha(ROOT/'02_geometry/geometry-master-v14.json')
furniture={o['source_id']:o for o in scene.objects if o.get('home_design_role')=='furniture'};assert len(furniture)==27
before={k:dict(position=list(o.location),rotation=list(o.rotation_euler)) for k,o in furniture.items()}
collection=bpy.data.collections.new('v15 写实材质与软包细节 · 不改布局');scene.collection.children.link(collection)
def image(asset,suffix,data=False):
    paths=list((ASSETS/asset).glob('*'+suffix+'*'))
    assert len(paths)==1,(asset,suffix,paths)
    im=bpy.data.images.load(str(paths[0]),check_existing=True)
    if data:im.colorspace_settings.name='Non-Color'
    return im
def texture_node(nodes,im,name):
    n=nodes.new('ShaderNodeTexImage');n.image=im;n.label=name;n.interpolation='Linear';return n
floor_images={k:image('wood_floor','_'+k+'_2k',k!='diff') for k in ['diff','rough','nor_gl']}
fabric_images={k:image('poly_wool_herringbone','_'+k+'_2k',k!='diff') for k in ['diff','rough','nor_gl']}

floor=bpy.data.materials.new('V15 · 实拍纹理浅橡木地板');floor.use_nodes=True;n=floor.node_tree.nodes;l=floor.node_tree.links;p=n.get('Principled BSDF')
tex=texture_node(n,floor_images['diff'],'CC0实拍木纹');uv=n.new('ShaderNodeTexCoord');l.new(uv.outputs['UV'],tex.inputs['Vector'])
bw=n.new('ShaderNodeRGBToBW');l.new(tex.outputs['Color'],bw.inputs[0]);ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.05;ramp.color_ramp.elements[0].color=(.36,.33,.27,1);ramp.color_ramp.elements[1].position=.55;ramp.color_ramp.elements[1].color=(.78,.74,.66,1);l.new(bw.outputs[0],ramp.inputs[0]);l.new(ramp.outputs[0],p.inputs['Base Color'])
rough=texture_node(n,floor_images['rough'],'真实微表面粗糙度');l.new(uv.outputs['UV'],rough.inputs['Vector']);remap=n.new('ShaderNodeMapRange');remap.inputs['To Min'].default_value=.38;remap.inputs['To Max'].default_value=.65;l.new(rough.outputs[0],remap.inputs['Value']);l.new(remap.outputs[0],p.inputs['Roughness'])
nor=texture_node(n,floor_images['nor_gl'],'地板接缝与木纹微法线');l.new(uv.outputs['UV'],nor.inputs['Vector']);nm=n.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.38;l.new(nor.outputs[0],nm.inputs['Color']);l.new(nm.outputs[0],p.inputs['Normal']);p.inputs['Specular IOR Level'].default_value=.3
for ob in scene.objects:
    if ob.type!='MESH':continue
    changed=False
    for slot in ob.material_slots:
        if slot.material and slot.material.name in ['R01 · 浅木地板','V10 · 浅木地面外观占位']:slot.material=floor;changed=True
    if changed:
        uvmap=ob.data.uv_layers.active or ob.data.uv_layers.new(name='real_floor_scale_1_7m')
        for poly in ob.data.polygons:
            for index in poly.loop_indices:
                point=ob.matrix_world@ob.data.vertices[ob.data.loops[index].vertex_index].co;uvmap.data[index].uv=(point.x/1.7,-point.y/1.7)

def woven(oldname,label):
    old=bpy.data.materials[oldname];mat=old.copy();mat.name='V15 · '+label;n=mat.node_tree.nodes;l=mat.node_tree.links;p=n.get('Principled BSDF');color=tuple(p.inputs['Base Color'].default_value)
    for socket in ['Base Color','Normal','Roughness']:
        for link in list(p.inputs[socket].links):l.remove(link)
    coord=n.new('ShaderNodeTexCoord');scale=n.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs[3].default_value=1/.3;l.new(coord.outputs['Object'],scale.inputs[0])
    diffuse=texture_node(n,fabric_images['diff'],'0.3米实拍细织物');diffuse.projection='BOX';diffuse.projection_blend=.25;l.new(scale.outputs[0],diffuse.inputs[0]);bw=n.new('ShaderNodeRGBToBW');l.new(diffuse.outputs[0],bw.inputs[0])
    remap=n.new('ShaderNodeMapRange');remap.inputs['To Min'].default_value=.76;remap.inputs['To Max'].default_value=1.10;l.new(bw.outputs[0],remap.inputs['Value'])
    tint=n.new('ShaderNodeMixRGB');tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1;tint.inputs[1].default_value=color;l.new(remap.outputs[0],tint.inputs[2]);l.new(tint.outputs[0],p.inputs['Base Color'])
    bump=n.new('ShaderNodeBump');bump.inputs['Distance'].default_value=.00045;bump.inputs['Strength'].default_value=.30;l.new(bw.outputs[0],bump.inputs['Height']);l.new(bump.outputs[0],p.inputs['Normal'])
    rough=texture_node(n,fabric_images['rough'],'织物粗糙度');rough.projection='BOX';rough.projection_blend=.25;l.new(scale.outputs[0],rough.inputs[0]);rr=n.new('ShaderNodeMapRange');rr.inputs['To Min'].default_value=.72;rr.inputs['To Max'].default_value=.96;l.new(rough.outputs[0],rr.inputs[0]);l.new(rr.outputs[0],p.inputs['Roughness']);p.inputs['Sheen Weight'].default_value=.30;p.inputs['Sheen Roughness'].default_value=.65
    return mat
fabric_map={name:woven(name,label) for name,label in [('V10 · 细织棉麻感米灰','米灰细织实拍纹理'),('V10 · 沙发浅灰支撑织物','浅灰框体织物'),('J02 · 低饱和苔绿色织物','苔绿细织物'),('J02 · 深蓝色织物','深蓝织物'),('R01 · 米灰亚麻混纺','旧灰米织物')] if name in bpy.data.materials}
for ob in scene.objects:
    for slot in ob.material_slots:
        if slot.material and slot.material.name in fabric_map:slot.material=fabric_map[slot.material.name]

# Add restrained micro-roughness to painted surfaces without changing the selected colors.
for name in ['V10 · 干净暖白平整哑光','V10 · 暖白顶面','V08 · 柔和奶黄色下柜','R01 · 暖白哑光柜门','V12 · cabinet']:
    mat=bpy.data.materials.get(name)
    if not mat:continue
    n=mat.node_tree.nodes;l=mat.node_tree.links;p=n.get('Principled BSDF');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=950;noise.inputs['Detail'].default_value=2;bump=n.new('ShaderNodeBump');bump.inputs['Distance'].default_value=.00008;bump.inputs['Strength'].default_value=.14;l.new(noise.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],p.inputs['Normal']);p.inputs['Roughness'].default_value=.68 if '柜' in name or 'cabinet' in name else .82

# Use flat optical glass: Fresnel reflections plus transmission, without bending single-plane openings.
glass=bpy.data.materials['R01 · 实体透明玻璃'];n=glass.node_tree.nodes;l=glass.node_tree.links;n.clear();out=n.new('ShaderNodeOutputMaterial');trans=n.new('ShaderNodeBsdfTransparent');trans.inputs[0].default_value=(.99,.995,.995,1);gloss=n.new('ShaderNodeBsdfGlossy');gloss.inputs['Color'].default_value=(.96,.98,1,1);gloss.inputs['Roughness'].default_value=.012
# Symmetric Schlick reflectance: a transparent two-face slab must not use an
# inverted inside-glass IOR without a corresponding refraction ray. That creates
# an artificial critical-angle circular cutoff on the back face.
geo=n.new('ShaderNodeNewGeometry');dot=n.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';l.new(geo.outputs['True Normal'],dot.inputs[0]);l.new(geo.outputs['Incoming'],dot.inputs[1]);absolute=n.new('ShaderNodeMath');absolute.operation='ABSOLUTE';l.new(dot.outputs['Value'],absolute.inputs[0]);one_minus=n.new('ShaderNodeMath');one_minus.operation='SUBTRACT';one_minus.inputs[0].default_value=1;l.new(absolute.outputs[0],one_minus.inputs[1]);power=n.new('ShaderNodeMath');power.operation='POWER';power.inputs[1].default_value=5;l.new(one_minus.outputs[0],power.inputs[0]);fres=n.new('ShaderNodeMath');fres.operation='MULTIPLY_ADD';fres.inputs[1].default_value=.96;fres.inputs[2].default_value=.04;l.new(power.outputs[0],fres.inputs[0]);l.new(geo.outputs['True Normal'],gloss.inputs['Normal']);mix=n.new('ShaderNodeMixShader');l.new(fres.outputs[0],mix.inputs[0]);l.new(trans.outputs[0],mix.inputs[1]);l.new(gloss.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],out.inputs[0]);glass['presentation_glass_model']='symmetric Schlick, geometric flat normals, no artificial back-face total-internal-reflection cutoff'

# Rebuild only the two upholstered assemblies, keeping their source envelopes and anchors.
for script,name in [('render_modern_japanese_v02.py','profile_mesh'),('update_blender_v07.py','mesh_part')]:
    tree=ast.parse((ROOT/'tools'/script).read_text(encoding='utf-8'));node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name);exec(compile(ast.Module(body=[node],type_ignores=[]),name,'exec'))
target=collection;mats={'fabric':fabric_map['V10 · 细织棉麻感米灰'],'fabric-dark':fabric_map['V10 · 沙发浅灰支撑织物'],'sage':fabric_map['J02 · 低饱和苔绿色织物'],'navy':fabric_map['J02 · 深蓝色织物'],'metal':bpy.data.materials['V10 · 暖石墨金属'],'ceramic':bpy.data.materials['V07 · ceramic'],'soil':bpy.data.materials['V07 · soil']}
soft_records=[]
for gid in ['sofa-modular','ottoman']:
    old=furniture[gid];props=dict(old.items());pieces=[]
    for row in [q for q in d['furniture'] if q['parent']==gid]:
        p=dict(row);soft=p['material']!='metal'
        if soft:
            p['shape']='box';p['bevelMm']=0;ob=mesh_part(p)
            for mod in list(ob.modifiers):ob.modifiers.remove(mod)
            bevel=ob.modifiers.new('软包全边圆润','BEVEL');bevel.width=min(.045,min(p[k]/1000 for k in ['w','d','h'])*.40);bevel.segments=7;bevel.harden_normals=True
            bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=bevel.name)
            for f in ob.data.polygons:f.use_smooth=True
            normal=ob.modifiers.new('软包面法线','WEIGHTED_NORMAL');normal.keep_sharp=True;bpy.ops.object.modifier_apply(modifier=normal.name)
            soft_records.append(dict(part=p['id'],edge_radius_mm=min(45,min(p[k] for k in ['w','d','h'])*.4)))
        else:ob=mesh_part(p)
        pieces.append(ob)
    bpy.ops.object.select_all(action='DESELECT')
    for ob in pieces:
        ob.select_set(True);bpy.context.view_layer.objects.active=ob
        for mod in list(ob.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.context.view_layer.objects.active=pieces[0];bpy.ops.object.join();ob=bpy.context.view_layer.objects.active;bpy.context.view_layer.update();points=[ob.matrix_world@v.co for v in ob.data.vertices];anchor=old.location.copy();ob.matrix_world=Matrix.Identity(4);ob.location=anchor
    for v,point in zip(ob.data.vertices,points):v.co=point-anchor
    for k,v in props.items():ob[k]=v
    ob.name=old.name+' · 实体软包';ob.lock_location[2]=True;ob.lock_rotation[0]=True;ob.lock_rotation[1]=True;bpy.data.objects.remove(old,do_unlink=True);furniture[gid]=ob

# Photographic foliage replaces the three visual proxies inside their original maximum envelopes.
plant_records=[];imported={}
for ident in ['potted_plant_01','potted_plant_02']:
    asset=ASSETS/ident/(ident+'_1k.blend')
    with bpy.data.libraries.load(str(asset),link=False) as (source,out):out.objects=list(source.objects)
    imported[ident]=out.objects
    for ob in out.objects:
        collection.objects.link(ob);ob.hide_render=True;ob.hide_set(True)
for index,(gid,asset) in enumerate([('plant-balcony-tall','potted_plant_01'),('plant-tv-medium','potted_plant_02'),('plant-balcony-low','potted_plant_02')]):
    group=next(q for q in d['furnitureObjects'] if q['id']==gid);old=furniture[gid];parts=[]
    for source in imported[asset]:
        if source.type!='MESH' or not any(t in source.name for t in ['leaves','stem']):continue
        ob=source.copy();ob.data=source.data.copy();collection.objects.link(ob);ob.hide_render=False;ob.hide_set(False);ob.parent=None;parts.append(ob)
    bpy.ops.object.select_all(action='DESELECT')
    for ob in parts:ob.select_set(True);bpy.context.view_layer.objects.active=ob
    bpy.ops.object.join();ob=bpy.context.view_layer.objects.active;bpy.context.view_layer.update();points=[ob.matrix_world@v.co for v in ob.data.vertices]
    # Orient variants while fitting the complete rendered mesh inside the same source box.
    angle=index*.63;rot=Matrix.Rotation(angle,4,'Z');points=[rot@p for p in points];lo=[min(p[i] for p in points) for i in range(3)];hi=[max(p[i] for p in points) for i in range(3)]
    bounds=group['meshBoundsMm'];widths=[bounds['w']/1000,bounds['d']/1000,(bounds['y']+bounds['h'])/1000];xlo=(bounds['x']-group['x'])/1000;ylo=-(bounds['z']+bounds['d']-group['z'])/1000;pot_parts=[p for p in d['furniture'] if p['parent']==gid and p['material'] in ['ceramic','soil']];bottom=max(p['y']+p['h'] for p in pot_parts)/1000;anchor=old.location.copy();ob.matrix_world=Matrix.Identity(4);ob.location=anchor
    for vertex,point in zip(ob.data.vertices,points):vertex.co=(xlo+(point.x-lo[0])/(hi[0]-lo[0])*widths[0],ylo+(point.y-lo[1])/(hi[1]-lo[1])*widths[1],bottom+(point.z-lo[2])/(hi[2]-lo[2])*(widths[2]-bottom))
    # Retain the original simple warm-white planters; only foliage gains photographic detail.
    originals=[mesh_part(p) for p in pot_parts];bpy.ops.object.select_all(action='DESELECT');ob.select_set(True)
    for item in originals:
        item.select_set(True);bpy.context.view_layer.objects.active=item
        for mod in list(item.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.context.view_layer.objects.active=ob;bpy.ops.object.join();bpy.context.view_layer.update()
    for k,v in old.items():ob[k]=v
    ob.name=old.name+' · 写实叶片';ob['render_asset_source']='https://polyhaven.com/a/'+asset;ob.lock_location[2]=True;ob.lock_rotation[0]=True;ob.lock_rotation[1]=True;bpy.data.objects.remove(old,do_unlink=True);furniture[gid]=ob;plant_records.append(dict(id=gid,source=asset,fit_actual_source_mesh_bounds_mm=bounds,nominal_size_labels_preserved=True,visual_species_not_selected_product=True))
for items in imported.values():
    for ob in items:bpy.data.objects.remove(ob,do_unlink=True)
for im in bpy.data.images:
    if im.source=='FILE' and ('potted_plant_' in im.name or 'potted_plant_' in im.filepath):
        asset='potted_plant_01' if 'potted_plant_01' in im.name or 'potted_plant_01' in im.filepath else 'potted_plant_02';candidate=ASSETS/asset/'textures'/Path(im.filepath.replace('\\','/')).name
        if candidate.exists():im.filepath=str(candidate);im.reload()

# Natural lighting and photographic exterior. It is a visualization environment, not the user's actual view.
world=bpy.data.worlds.new('V15 · 自然公园环境光 · 窗外示意');world.use_nodes=True;scene.world=world;n=world.node_tree.nodes;l=world.node_tree.links;n.clear();out=n.new('ShaderNodeOutputWorld');bg=n.new('ShaderNodeBackground');bg.inputs['Strength'].default_value=.7;env=n.new('ShaderNodeTexEnvironment');env.image=bpy.data.images.load(str(ASSETS/'green_point_park/green_point_park_4k.exr'),check_existing=True);tex=n.new('ShaderNodeTexCoord');mapping=n.new('ShaderNodeMapping');mapping.inputs['Rotation'].default_value[2]=math.radians(132);l.new(tex.outputs['Generated'],mapping.inputs[0]);l.new(mapping.outputs[0],env.inputs[0]);l.new(env.outputs[0],bg.inputs['Color']);l.new(bg.outputs[0],out.inputs[0])
for name,energy in [('主光',0),('补光',0),('阳台柔和日光',80),('入户侧开口日光',65)]:
    ob=bpy.data.objects.get(name)
    if ob:
        ob.data.animation_data_clear();ob.data.energy=energy;ob.data.color=(1,.98,.94)
scene.view_settings.driver_remove('exposure');scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=1.5
scene['lighting_scene']=0;scene.update_tag();scene.frame_set(scene.frame_current);bpy.context.view_layer.update()
scene.cycles.samples=256;scene.cycles.use_adaptive_sampling=True;scene.cycles.adaptive_threshold=.015;scene.cycles.use_denoising=True;scene.cycles.max_bounces=12;scene.cycles.diffuse_bounces=6;scene.cycles.glossy_bounces=6;scene.cycles.transparent_max_bounces=16
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.render.image_settings.color_depth='8'
for gid,rec in before.items():
    ob=furniture[gid];assert list(ob.location)==rec['position'] and list(ob.rotation_euler)==rec['rotation']
for ob in scene.objects:
    if ob.get('home_design_role') in ['wall_visual_union','wall_finish_proposal']:assert not ob.hide_render
assert sum(o.get('home_design_role')=='furniture' for o in scene.objects)==27
assert sum(o.get('home_design_role')=='wall' for o in scene.objects)==62 and sum(o.get('home_design_role')=='glass' for o in scene.objects)==12
for im in bpy.data.images:
    if im.source=='FILE' and im.filepath and not im.packed_file:im.filepath=bpy.path.relpath(bpy.path.abspath(im.filepath),start=str(DEST.parent))
scene['photoreal_presentation_revision']=15;scene['photoreal_source_model_sha256']=sha(BASE);scene['photoreal_asset_manifest']='08_assets/photoreal-v15/asset-manifest.json';scene['photoreal_exterior_is_illustrative']=True;scene.name='v14布局 · v15写实PBR全景表现';scene.camera=bpy.data.objects['v11 · 客厅至阳台'];scene.render.resolution_x=1800;scene.render.resolution_y=1200
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(DEST))
report=dict(presentation_revision=15,geometry_revision=14,source_geometry_sha256=scene['home_design_geometry_sha256'],source_model_sha256=sha(BASE),presentation_model_sha256=sha(DEST),furniture_count=27,all_27_placements_and_orientations_preserved=True,full_walls_and_all_windows_preserved=True,sofa_soft_parts=soft_records,plants=plant_records,assets_manifest_sha256=sha(ASSETS/'asset-manifest.json'),exterior='CC0 photographic HDRI only; illustrative scenery, actual site unknown',render='Cycles path-traced native full sphere, no AI sphere repaint',external_textures_relative=True)
(ROOT/'logs/v15-photoreal-build.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('V15_PHOTOREAL_SAVED')
