from pathlib import Path
import asyncio, json, os, sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT=Path(__file__).resolve().parents[1]
CODE='''import bpy, json
objects=[o for o in bpy.context.scene.objects if o.get('home_design_role')=='furniture']
assert len(objects)==13
report=[]
for obj in objects:
    bpy.ops.object.select_all(action='DESELECT')
    assert not obj.hide_select
    obj.select_set(True);bpy.context.view_layer.objects.active=obj
    start=list(obj.location)
    for axis,index in [('X',0),('Y',1)]:
        before=list(obj.location)
        bpy.ops.home_design.move(axis=axis,direction=1)
        assert abs(obj.location[index]-before[index]-0.1)<0.000001
        bpy.ops.home_design.move(axis=axis,direction=-1)
        assert all(abs(obj.location[i]-before[i])<0.000001 for i in range(3))
    report.append(dict(id=obj['source_id'],step_mm=100,whole_mesh=True,selectable=True,axes=['X','Y']))
bpy.ops.object.select_all(action='DESELECT')
sofa=next(o for o in objects if o['source_id']=='sofa-modular')
sofa.select_set(True);bpy.context.view_layer.objects.active=sofa
baseline=list(sofa.location)
bpy.ops.ed.undo_push(message='HomeDesign 100mm test baseline')
bpy.ops.home_design.move(axis='X',direction=1)
bpy.ops.ed.undo()
sofa=next(o for o in bpy.context.scene.objects if o.get('source_id')=='sofa-modular')
assert all(abs(sofa.location[i]-baseline[i])<0.000001 for i in range(3))
bpy.ops.home_design.export_layout()
print('MOVEMENT_OK '+json.dumps(dict(objects=report,positions_restored=True,native_undo=True,source_model_saved=False)))
'''

async def main():
    env=dict(os.environ,DISABLE_TELEMETRY='true',BLENDER_MCP_SAFE_MODE='1',BLENDERMCP_NO_UPDATE_CHECK='1',PYTHONUTF8='1')
    params=StdioServerParameters(command=sys.executable,args=[str(ROOT/'tools/mcp_launch.py')],env=env)
    with (ROOT/'logs/movement-test-stderr.log').open('w',encoding='utf-8') as err:
        async with stdio_client(params,errlog=err) as (read,write):
            async with ClientSession(read,write) as session:
                await session.initialize()
                result=await session.call_tool('execute_blender_code',{'code':CODE,'user_prompt':'验证全部13件家具可整件选择，并按100mm移动后恢复原位'})
                (ROOT/'logs/furniture-movement-test.json').write_text(result.model_dump_json(indent=2),encoding='utf-8')
                print(result.model_dump_json())
                assert not result.isError
                assert 'MOVEMENT_OK' in result.model_dump_json()
    saved=json.loads((ROOT/'03_layout/blender-layout-latest.json').read_text(encoding='utf-8'))
    original=json.loads((ROOT/'02_geometry/geometry-master.json').read_text(encoding='utf-8'))
    expected={o['id']:(o['x'],o['z']) for o in original['furnitureObjects']}
    assert {o['id']:(o['x'],o['z']) for o in saved['objects']}==expected
    print('EXPORT_READBACK_OK: 13 placements match the current master')

if __name__=='__main__':asyncio.run(main())
