from pathlib import Path
import bpy,json,hashlib
R=Path('D:/AI-Yang.cn/HomeDesign');OUT=R/'09_delivery/v20-complete'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def fingerprint():
    rows=[]
    for o in bpy.context.scene.objects:
        if o.type=='MESH':rows.append((o.name,list(o.matrix_world),[list(v.co) for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons],[m.name if m else '' for m in o.data.materials]))
        elif o.type=='LIGHT':rows.append((o.name,list(o.matrix_world),o.data.type,o.data.energy,list(o.data.color)))
    return hashlib.sha256(str(rows).encode()).hexdigest()
records=[]
for name in ['home-main-v20-complete.blend','home-v20-complete-render-source.blend']:
    path=R/'06_blender'/name;bpy.ops.wm.open_mainfile(filepath=str(path));before=fingerprint();old=sha(path);s=bpy.context.scene
    s['photoreal_presentation_status']='same-version v20 full implementation photographic concepts and native anchors'
    s['home_design_geometry_path']=str(R/'02_geometry/geometry-master-v20-complete.json');s['home_design_style_path']=str(R/'05_style/modern-japanese-v20-complete.json')
    s['home_design_style_revision']='modern-japanese-v20-complete';s['photoreal_presentation_revision']=20;s['home_design_gallery']='09_delivery/v20-complete/index.html';s['home_design_panorama']='09_delivery/vr-tour-v07/打开360全景漫游.html';s['wider_v20_refinement_status']='design entities implemented; equipment, materials and field conditions unverified'
    if 'presentation_stale_after_geometry_revision' in s:del s['presentation_stale_after_geometry_revision']
    assert fingerprint()==before
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path));assert fingerprint()==before
    records.append(dict(model=name,beforeSha256=old,afterSha256=sha(path),geometryAndMaterialsFingerprint=before,visibleDataUnchanged=True))
audit=json.loads((OUT/'主模型回读.json').read_text(encoding='utf8'));audit['modelSha256AtGeometryVerification']=audit['modelSha256'];audit['modelSha256']=sha(R/'06_blender/home-main-v20-complete.blend');audit['metadataOnlyFinalization']=True
(OUT/'主模型回读.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf8');(OUT/'表现元数据一致性.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8')
print('V20_FULL_METADATA_FINALIZED_WITH_UNCHANGED_GEOMETRY',flush=True)
