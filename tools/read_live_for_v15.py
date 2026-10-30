from pathlib import Path
import json,asyncio,os,sys
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
from activate_model_v07 import unpack
ROOT=Path(__file__).resolve().parents[1]
async def main():
  env=dict(os.environ,DISABLE_TELEMETRY='true',BLENDER_MCP_SAFE_MODE='1',BLENDERMCP_NO_UPDATE_CHECK='1',PYTHONUTF8='1')
  with (ROOT/'logs/v15-input-mcp-stderr.txt').open('w',encoding='utf-8') as err:
    async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(ROOT/'tools/mcp_launch.py')],env=env),errlog=err) as (reader,writer):
      async with ClientSession(reader,writer) as session:
        await session.initialize();names=[t.name for t in (await session.list_tools()).tools];assert 'execute_blender_code' in names
        code="""import bpy,json
s=bpy.context.scene
print('LIVE_STATE '+json.dumps(dict(file=bpy.data.filepath,revision=s.get('home_design_revision'),dirty=bpy.data.is_dirty,geometry_sha256=s.get('home_design_geometry_sha256'),positions=[dict(id=o['source_id'],x=round(o.location.x*1000,3),z=round(-o.location.y*1000,3),rotation=round(o.rotation_euler.z,7)) for o in s.objects if o.get('home_design_role')=='furniture'])))"""
        r=await session.call_tool('execute_blender_code',dict(code=code,user_prompt='写实全景制作前回读最新27件家具位置，避免覆盖手动调整'));assert not r.isError
        live=unpack(r.model_dump(mode='json'));assert live and live['revision']==14
        d=json.loads((ROOT/'02_geometry/geometry-master-v14.json').read_text(encoding='utf-8'));rows={q['id']:q for q in d['furnitureObjects']};assert len(live['positions'])==27
        assert all(abs(p['x']-rows[p['id']]['x'])<.01 and abs(p['z']-rows[p['id']]['z'])<.01 and abs(p['rotation'])<1e-6 for p in live['positions']),'Live layout changed; reconcile before rendering.'
        (ROOT/'logs/v15-source-live-layout.json').write_text(json.dumps(dict(tools=names,live=live),ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('V15_LATEST_LAYOUT_VERIFIED')
if __name__=='__main__':asyncio.run(main())
