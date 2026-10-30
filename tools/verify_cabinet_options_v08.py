"""Read back each saved proposal, bind option style hashes, leave active main intact."""
from pathlib import Path
import bpy,json,hashlib
ROOT=Path(r'D:\AI-Yang.cn\HomeDesign')
PARAM=ROOT/'05_style/cabinet-options-v08';OUT=ROOT/'07_renders/v08-cabinet-options'
main=ROOT/'06_blender/home-main-v07.blend';before=hashlib.sha256(main.read_bytes()).hexdigest()
manifest=json.loads((OUT/'cycles-manifest.json').read_text(encoding='utf-8'))
base=json.loads((ROOT/'02_geometry/geometry-master-v07.json').read_text(encoding='utf-8'))
expected={g['id']:g for g in base['furnitureObjects']}
rows=[]
for opt in manifest['options']:
    path=Path(opt['blend']);bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;raw=Path(opt['geometry']).read_bytes();data=json.loads(raw)
    assert scene['home_design_geometry_sha256']==hashlib.sha256(raw).hexdigest()
    ff={o['source_id']:o for o in scene.objects if o.get('home_design_role')=='furniture'}
    assert len(ff)==21
    assert sum(o.get('home_design_role')=='wall' for o in scene.objects)==60
    assert sum(o.get('home_design_role')=='glass' for o in scene.objects)==8
    for gid,ob in ff.items():
        g=expected[gid]
        assert abs(ob.location.x*1000-g['x'])<.01 and abs(-ob.location.y*1000-g['z'])<.01
        if gid!='tv-high':assert list(ob['dimensions_mm'])==[g['dimensionsMm'][k] for k in ['length','width','height']]
    ob=ff['tv-high'];assert list(ob['dimensions_mm'])==[4500,400,2750]
    bpy.context.view_layer.update();points=[ob.matrix_world@v.co for v in ob.data.vertices]
    top=max(p.z for p in points)*1000;assert abs(top-2750)<.001
    assert abs(min(p.x for p in points))<.001 and abs(max(p.x for p in points)*1000-400)<.001
    pp=[p for p in data['furniture'] if p['parent']=='tv-high']
    sides=[p for p in pp if p['id'].endswith(('niche-side-a','niche-side-b','niche-back'))]
    assert len(sides)==3 and all(p['y']==1200 and p['h']==200 for p in sides)
    style=dict(status='unselected',option=opt['id'],name=opt['name'],base_style='05_style/modern-japanese-v03.json',
        geometry_sha256=scene['home_design_geometry_sha256'],front_srgb_hex=opt['color_hex'],description=opt['description'],cabinet_height_mm=2750,ceiling_gap_mm=0)
    style_path=PARAM/('option-'+opt['id'].lower()+'-style.json')
    style_path.write_text(json.dumps(style,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    scene['home_design_style_file']=style_path.relative_to(ROOT).as_posix();scene['home_design_style_sha256']=hashlib.sha256(style_path.read_bytes()).hexdigest()
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(path))
    bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
    assert bpy.context.scene['home_design_style_sha256']==hashlib.sha256(style_path.read_bytes()).hexdigest()
    rows.append(dict(option=opt['id'],saved_reopened=True,geometry_sha256=hashlib.sha256(raw).hexdigest(),style_sha256=bpy.context.scene['home_design_style_sha256'],
        cabinet_top_mm=round(top,4),ceiling_gap_mm=round(2750-top,4),niche_bottom_mm=1200,niche_top_mm=1400,other_20_placements_and_dimensions_unchanged=True))
assert hashlib.sha256(main.read_bytes()).hexdigest()==before
(ROOT/'logs/cabinet-options-v08-readback.json').write_text(json.dumps(dict(options=rows,active_main_sha256=before,active_main_unchanged=True),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('CABINET_OPTIONS_READBACK_OK',len(rows))
