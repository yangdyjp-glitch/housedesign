"""Read the preserved latest layout, send construction through MCP, then read it back."""
from pathlib import Path
import asyncio, hashlib, json, os, sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT=Path(__file__).resolve().parents[1]
MODEL=ROOT/'02_geometry/geometry-master.json'
TARGET=ROOT/'06_blender/home-main-v05.blend'

def prepare():
    data=json.loads(MODEL.read_text(encoding='utf-8'))
    data['provenance']['blender_axis_mapping']='(plan x, -plan z, height) -> (Blender X, Blender Y, Blender Z); mm / 1000'
    data['provenance']['geographic_orientation']='unknown; -Y follows downward direction in the source plan, keeping top views unmirrored'
    note='底板厚160 mm仅为显示占位；不代表楼板结构尺寸。'
    if note not in data['assumptions']:data['assumptions'].append(note)
    raw=(json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    MODEL.write_bytes(raw);(ROOT/'02_geometry/geometry-master-v05.json').write_bytes(raw)
    sha=hashlib.sha256(raw).hexdigest()
    body=(ROOT/'tools/build_blender_model.py').read_text(encoding='utf-8')
    code='import json\nDATA=json.loads('+repr(json.dumps(data,ensure_ascii=False))+')\nSOURCE_SHA='+repr(sha)+'\nOUTPUT='+repr(TARGET.as_posix())+'\n'+body
    (ROOT/'logs/model-import-code.py').write_text(code,encoding='utf-8')
    return data,sha,code

VERIFY='''import bpy, json
bpy.ops.wm.open_mainfile(filepath=OUTPUT_PLACEHOLDER,load_ui=False,use_scripts=False)
assert bpy.context.scene['home_design_geometry_sha256']==SHA_PLACEHOLDER
expected=json.loads(EXPECTED_PLACEHOLDER)
found={obj['source_id']:obj for obj in bpy.context.scene.objects if obj.get('home_design_role')=='furniture'}
assert len(found)==13
placements=[]
for row in expected:
    obj=found[row['id']]
    actual=[round(obj.location.x*1000,3),round(-obj.location.y*1000,3)]
    assert actual==[row['x'],row['z']], [row['id'],actual]
    assert obj.type=='MESH'
    placements.append(dict(id=row['id'],x_mm=actual[0],z_mm=actual[1],parts=obj['part_count']))
assert sum(o['part_count'] for o in found.values())==175
assert len([o for o in bpy.context.scene.objects if o.get('home_design_role')=='wall'])==60
assert len([o for o in bpy.context.scene.objects if o.get('home_design_role')=='glass'])==8
print('MODEL_READBACK_OK '+json.dumps(dict(file=bpy.data.filepath,units=bpy.context.scene.unit_settings.system,source_sha256=bpy.context.scene['home_design_geometry_sha256'],placements=placements)))
'''

async def main():
    if TARGET.exists():
        raise FileExistsError('v05 model already exists. Preserve it and choose a new explicit version path before importing again.')
    data,sha,code=prepare()
    env=dict(os.environ,DISABLE_TELEMETRY='true',BLENDER_MCP_SAFE_MODE='1',BLENDERMCP_NO_UPDATE_CHECK='1',PYTHONUTF8='1')
    params=StdioServerParameters(command=sys.executable,args=[str(ROOT/'tools/mcp_launch.py')],env=env)
    evidence=[]
    verify=VERIFY.replace('OUTPUT_PLACEHOLDER',repr(TARGET.as_posix())).replace('SHA_PLACEHOLDER',repr(sha)).replace('EXPECTED_PLACEHOLDER',repr(json.dumps(data['furnitureObjects'],ensure_ascii=False)))
    with (ROOT/'logs/model-import-stderr.log').open('w',encoding='utf-8') as err:
        async with stdio_client(params,errlog=err) as (read,write):
            async with ClientSession(read,write) as session:
                await session.initialize()
                for phase,payload in [('import',code),('reopen_validate',verify)]:
                    result=await session.call_tool('execute_blender_code',{'code':payload,'user_prompt':'沿用当前户型和最新家具位置，接入Blender主模型'})
                    row=dict(phase=phase,response=result.model_dump(mode='json'));evidence.append(row)
                    print(json.dumps(row,ensure_ascii=True),flush=True)
                    if result.isError:raise RuntimeError('Model import failed')
    (ROOT/'logs/model-import-readback.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8')
    assert 'MODEL_READBACK_OK' in json.dumps(evidence)

if __name__=='__main__':asyncio.run(main())
