from pathlib import Path
import asyncio, json, os, sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT=Path(__file__).resolve().parents[1]
async def main():
    env=dict(os.environ,DISABLE_TELEMETRY='true',BLENDER_MCP_SAFE_MODE='1',BLENDERMCP_NO_UPDATE_CHECK='1',PYTHONUTF8='1')
    params=StdioServerParameters(command=sys.executable,args=[str(ROOT/'tools/mcp_launch.py')],env=env)
    with (ROOT/'logs/mcp-probe-stderr.log').open('w',encoding='utf-8') as err:
        async with stdio_client(params,errlog=err) as (read,write):
            async with ClientSession(read,write) as session:
                init=await session.initialize()
                tools=await session.list_tools()
                result=dict(server=init.model_dump(mode='json'),tools=[t.model_dump(mode='json') for t in tools.tools])
                (ROOT/'logs/mcp-tool-catalog.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
                print(json.dumps(dict(server=init.serverInfo.model_dump(),toolCount=len(tools.tools),tools=[t.name for t in tools.tools]),ensure_ascii=True))
                code_tool=next(t for t in tools.tools if t.name=='execute_blender_code')
                print(json.dumps(code_tool.inputSchema))
                result=await session.call_tool('get_scene_info',{})
                (ROOT/'logs/mcp-scene-probe.json').write_text(result.model_dump_json(indent=2),encoding='utf-8')
                print(result.model_dump_json()[:2500])

if __name__=='__main__':asyncio.run(main())
