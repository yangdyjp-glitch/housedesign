from pathlib import Path
import asyncio,json,os,sys
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
from activate_model_v07 import unpack
ROOT=Path(__file__).resolve().parents[1]
async def main():
    params=StdioServerParameters(command=sys.executable,args=[str(ROOT/'tools/mcp_launch.py')],env=dict(os.environ,DISABLE_TELEMETRY='true',BLENDER_MCP_SAFE_MODE='1',BLENDERMCP_NO_UPDATE_CHECK='1',PYTHONUTF8='1'))
    with (ROOT/'logs/v11-input-mcp-stderr.txt').open('w',encoding='utf-8') as err:
        async with stdio_client(params,errlog=err) as (read,write):
            async with ClientSession(read,write) as session:
                await session.initialize();catalog=await session.list_tools();names=[t.name for t in catalog.tools];assert 'execute_blender_code' in names
                code="""import bpy,json
print('LIVE_STATE '+json.dumps(dict(file=bpy.data.filepath,dirty=bpy.data.is_dirty,managed=bool(bpy.context.scene.get('HomeDesign_ManagedSession')),revision=bpy.context.scene.get('home_design_revision'),geometry_sha256=bpy.context.scene.get('home_design_geometry_sha256'),positions=[dict(id=o['source_id'],x=round(o.location.x*1000,3),z=round(-o.location.y*1000,3),rotation=round(o.rotation_euler.z,6),dimensions=list(o['dimensions_mm'])) for o in bpy.context.scene.objects if o.get('home_design_role')=='furniture'],camera_names=[o.name for o in bpy.context.scene.objects if o.type=='CAMERA'])))"""
                result=await session.call_tool('execute_blender_code',{'code':code,'user_prompt':'增加阳台茶桌茶椅前，核对主模型和最新家具位置，接续聊天内手动移动'})
                state=unpack(result.model_dump(mode='json'));assert state and state['managed'] and state['revision']==10
                (ROOT/'logs/v11-input-live-state.json').write_text(json.dumps(dict(tools=names,live=state),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
                print(json.dumps(dict(revision=state['revision'],positions=state['positions'],camera_names=state['camera_names']),ensure_ascii=False))
if __name__=='__main__':asyncio.run(main())
