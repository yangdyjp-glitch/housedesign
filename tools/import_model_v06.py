from pathlib import Path
import asyncio, hashlib, json, os, sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT=Path(__file__).resolve().parents[1]
RAW=(ROOT/'02_geometry/geometry-master-v06.json').read_bytes()
DATA=json.loads(RAW);SHA=hashlib.sha256(RAW).hexdigest()
TARGET=ROOT/'06_blender/home-main-v06.blend'
CODE='import json\nDATA=json.loads('+repr(json.dumps(DATA,ensure_ascii=False))+')\nSOURCE_SHA='+repr(SHA)+'\nOUTPUT='+repr(TARGET.as_posix())+'\n'+(ROOT/'tools/build_blender_model_v06.py').read_text(encoding='utf-8')
VERIFY='''import bpy,json,math
bpy.context.view_layer.update()
expected=json.loads(EXPECTED_PLACEHOLDER)
assert bpy.context.scene['home_design_geometry_sha256']==SHA_PLACEHOLDER
assert bpy.context.scene['home_design_revision']==6
objects={o['source_id']:o for o in bpy.context.scene.objects if o.get('home_design_role')=='furniture'}
assert len(objects)==14
assert len([o for o in objects if o.startswith('dining-chair-')])==4
assert len([o for o in objects if o.startswith('office-chair-')])==1
report=[];max_error=0.0
for row in expected['furnitureObjects']:
    obj=objects[row['id']]
    assert [round(obj.location.x*1000,3),round(-obj.location.y*1000,3)]==[row['x'],row['z']]
    dimensions=[row['dimensionsMm'][key] for key in ['length','width','height']]
    assert list(obj['dimensions_mm'])==dimensions
    pts=[obj.matrix_world@v.co for v in obj.data.vertices]
    bounds=[min(v.x for v in pts)*1000,-max(v.y for v in pts)*1000,min(v.z for v in pts)*1000,
            max(v.x for v in pts)*1000,-min(v.y for v in pts)*1000,max(v.z for v in pts)*1000]
    b=row['meshBoundsMm'];wanted=[b['x'],b['z'],b['y'],b['x']+b['w'],b['z']+b['d'],b['y']+b['h']]
    error=max(abs(a-bb) for a,bb in zip(bounds,wanted));assert error<0.01,[row['id'],error]
    max_error=max(max_error,error)
    bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
    original=list(obj.location)
    bpy.ops.home_design.move(axis='X',direction=1)
    assert abs(obj.location.x-original[0]-0.1)<0.000001
    bpy.ops.home_design.move(axis='X',direction=-1)
    assert all(abs(obj.location[i]-original[i])<0.000001 for i in range(3))
    report.append(dict(id=row['id'],dimensions_mm=dimensions,step_mm=100))
assert sum(o['part_count'] for o in objects.values())==len(expected['furniture'])
assert len([o for o in bpy.context.scene.objects if o.get('home_design_role')=='wall'])==60
assert len([o for o in bpy.context.scene.objects if o.get('home_design_role')=='glass'])==8
bpy.ops.object.select_all(action='DESELECT');objects['sofa-modular'].select_set(True)
bpy.context.view_layer.objects.active=objects['sofa-modular']
bpy.ops.home_design.export_layout()
bpy.ops.wm.save_as_mainfile(filepath=TARGET_PLACEHOLDER)
print('V06_READBACK_OK '+json.dumps(dict(file=bpy.data.filepath,furniture=14,parts=len(expected['furniture']),max_transfer_error_mm=round(max_error,6),objects=report)))
'''.replace('TARGET_PLACEHOLDER',repr(TARGET.as_posix())).replace('EXPECTED_PLACEHOLDER',repr(json.dumps(DATA,ensure_ascii=False))).replace('SHA_PLACEHOLDER',repr(SHA))

async def main():
    verify_only='--verify-only' in sys.argv
    if TARGET.exists() and not verify_only:raise FileExistsError('Preserve existing v06 model; do not overwrite')
    if verify_only and not TARGET.exists():raise FileNotFoundError('No existing v06 model to verify')
    env=dict(os.environ,DISABLE_TELEMETRY='true',BLENDER_MCP_SAFE_MODE='1',BLENDERMCP_NO_UPDATE_CHECK='1',PYTHONUTF8='1')
    params=StdioServerParameters(command=sys.executable,args=[str(ROOT/'tools/mcp_launch.py')],env=env)
    evidence=[]
    with (ROOT/'logs/model-v06-mcp-stderr.log').open('w',encoding='utf-8') as err:
        async with stdio_client(params,errlog=err) as (read,write):
            async with ClientSession(read,write) as session:
                await session.initialize()
                before=await session.call_tool('get_scene_info',{})
                evidence.append(dict(phase='before',response=before.model_dump(mode='json')))
                phases=[] if verify_only else [('build',CODE,'MODEL_IMPORTED')]
                load='import bpy\nbpy.ops.wm.open_mainfile(filepath='+repr(TARGET.as_posix())+',load_ui=False,use_scripts=False)\nprint("V06_LOADED")'
                phases += [('reopen',load,'V06_LOADED'),('verify',VERIFY,'V06_READBACK_OK')]
                for phase,code,marker in phases:
                    result=await session.call_tool('execute_blender_code',{'code':code,'user_prompt':'按用户六项要求更新家具和长宽高，另存v06并回读验证'})
                    evidence.append(dict(phase=phase,response=result.model_dump(mode='json')))
                    (ROOT/'logs/model-v06-mcp-readback.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8')
                    print(json.dumps(dict(phase=phase,result=result.model_dump(mode='json')),ensure_ascii=True),flush=True)
                    assert not result.isError and marker in result.model_dump_json()
    manifest=dict(revision=6,filename=TARGET.name,geometry='02_geometry/geometry-master-v06.json',geometry_sha256=SHA)
    (ROOT/'06_blender/active-model.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Active main model switched to v06; v05 retained.')

if __name__=='__main__':asyncio.run(main())
