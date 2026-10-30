"""Read-only final live placement check; do not reload or write the Blender session."""
from pathlib import Path
import asyncio,json,os,sys
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
from activate_model_v07 import unpack
ROOT=Path(__file__).resolve().parents[1]
async def main():
    env=dict(os.environ,DISABLE_TELEMETRY='true',BLENDER_MCP_SAFE_MODE='1',BLENDERMCP_NO_UPDATE_CHECK='1',PYTHONUTF8='1');params=StdioServerParameters(command=sys.executable,args=[str(ROOT/'tools/mcp_launch.py')],env=env)
    with (ROOT/'logs/v13-final-readback-mcp-stderr.txt').open('w',encoding='utf-8') as err:
        async with stdio_client(params,errlog=err) as (r,w):
            async with ClientSession(r,w) as session:
                await session.initialize();catalog=await session.list_tools();assert any(t.name=='execute_blender_code' for t in catalog.tools)
                code="""import bpy,json
s=bpy.context.scene
print('LIVE_STATE '+json.dumps(dict(file=bpy.data.filepath,dirty=bpy.data.is_dirty,revision=s.get('home_design_revision'),geometry_sha256=s.get('home_design_geometry_sha256'),positions=[dict(id=o['source_id'],x=round(o.location.x*1000,3),z=round(-o.location.y*1000,3),rotation=round(o.rotation_euler.z,7)) for o in s.objects if o.get('home_design_role')=='furniture'])))"""
                result=await session.call_tool('execute_blender_code',{'code':code,'user_prompt':'最终出图后只读核对现场家具位置，没有重载或保存动作'});live=unpack(result.model_dump(mode='json'));assert live and not result.isError,result.model_dump_json();g=json.loads((ROOT/'02_geometry/geometry-master-v13.json').read_text(encoding='utf-8'));rows={p['id']:p for p in g['furnitureObjects']};assert live['revision']==13 and len(live['positions'])==23
                diff=[p for p in live['positions'] if abs(p['x']-rows[p['id']]['x'])>.01 or abs(p['z']-rows[p['id']]['z'])>.01 or abs(p['rotation'])>1e-6]
                report=dict(live=live,differences=diff,matched=not diff,read_only=True);(ROOT/'logs/v13-final-live-readback.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');assert not diff,diff;print('V13_FINAL_LIVE_POSITIONS_MATCH')
if __name__=='__main__':asyncio.run(main())
