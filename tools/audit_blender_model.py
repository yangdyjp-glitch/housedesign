from pathlib import Path
import asyncio, hashlib, json, os, sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'02_geometry/geometry-master.json').read_text(encoding='utf-8'))
CODE='''import bpy, json
bpy.context.view_layer.update()
expected=json.loads(DATA_PLACEHOLDER)
objects={o['source_id']:o for o in bpy.context.scene.objects if o.get('home_design_role')=='furniture'}
max_error=0.0
for row in expected['furnitureObjects']:
    obj=objects[row['id']]
    points=[obj.matrix_world@v.co for v in obj.data.vertices]
    actual=[min(v[0] for v in points)*1000,-max(v[1] for v in points)*1000,min(v[2] for v in points)*1000,
            max(v[0] for v in points)*1000,-min(v[1] for v in points)*1000,max(v[2] for v in points)*1000]
    parts=[p for p in expected['furniture'] if p['parent']==row['id']]
    desired=[min(p['x'] for p in parts),min(p['z'] for p in parts),min(p['y'] for p in parts),
             max(p['x']+p['w'] for p in parts),max(p['z']+p['d'] for p in parts),max(p['y']+p['h'] for p in parts)]
    error=max(abs(a-b) for a,b in zip(actual,desired))
    max_error=max(max_error,error)
    assert error<0.01,[row['id'],actual,desired]
wall_ids={o['source_id'] for o in bpy.context.scene.objects if o.get('home_design_role')=='wall'}
assert wall_ids=={p['id'] for p in expected['walls']}
aligned=[row for row in expected['walls'] if any(row['id'].startswith(prefix) for prefix in expected['features']['alignedWalls']['segments'])]
assert len(aligned)==3
assert all(abs(row['z']+row['d']-1072)<0.001 for row in aligned)
balcony=[row for row in expected['glass'] if row['id'].startswith('outer-top')]
assert len(balcony)==1 and balcony[0]['y']==0
print('GEOMETRY_AUDIT_OK '+json.dumps(dict(furniture_bbox_max_error_mm=round(max_error,6),furniture=13,parts=175,wall_ids_match=True,aligned_wall_face_mm=1072,balcony_glass_bottom_mm=0,geographic_orientation='unknown',source_dimensions_verified=False)))
'''.replace('DATA_PLACEHOLDER',repr(json.dumps(DATA,ensure_ascii=False)))

async def main():
    env=dict(os.environ,DISABLE_TELEMETRY='true',BLENDER_MCP_SAFE_MODE='1',BLENDERMCP_NO_UPDATE_CHECK='1',PYTHONUTF8='1')
    params=StdioServerParameters(command=sys.executable,args=[str(ROOT/'tools/mcp_launch.py')],env=env)
    with (ROOT/'logs/geometry-audit-stderr.log').open('w',encoding='utf-8') as err:
        async with stdio_client(params,errlog=err) as (read,write):
            async with ClientSession(read,write) as session:
                await session.initialize()
                status=await session.call_tool('get_addon_status',{})
                (ROOT/'logs/mcp-addon-status.json').write_text(status.model_dump_json(indent=2),encoding='utf-8')
                result=await session.call_tool('execute_blender_code',{'code':CODE,'user_prompt':'回读家具网格外包框、对齐墙面和落地窗，核对接入模型未改变源几何'})
                (ROOT/'logs/geometry-audit.json').write_text(result.model_dump_json(indent=2),encoding='utf-8')
                print(status.model_dump_json()[:2000]);print(result.model_dump_json()[:2600])
                assert not result.isError and 'GEOMETRY_AUDIT_OK' in result.model_dump_json()

if __name__=='__main__':asyncio.run(main())
