from pathlib import Path
import asyncio,json,os,sys
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
from activate_model_v07 import unpack
ROOT=Path(__file__).resolve().parents[1]
async def main():
    params=StdioServerParameters(command=sys.executable,args=[str(ROOT/'tools/mcp_launch.py')],env=dict(os.environ,DISABLE_TELEMETRY='true',BLENDER_MCP_SAFE_MODE='1',BLENDERMCP_NO_UPDATE_CHECK='1',PYTHONUTF8='1'))
    with (ROOT/'logs/v13-input-mcp-stderr.txt').open('w',encoding='utf-8') as err:
        async with stdio_client(params,errlog=err) as (reader,writer):
            async with ClientSession(reader,writer) as session:
                await session.initialize();catalog=await session.list_tools();names=[t.name for t in catalog.tools];assert 'execute_blender_code' in names
                code="""import bpy,json
scene=bpy.context.scene
cam=next(o.data for o in scene.objects if o.type=='CAMERA')
props=dict(panorama_type=str(cam.panorama_type),latitude_min=cam.latitude_min,latitude_max=cam.latitude_max,longitude_min=cam.longitude_min,longitude_max=cam.longitude_max)
print('LIVE_STATE '+json.dumps(dict(file=bpy.data.filepath,dirty=bpy.data.is_dirty,managed=bool(scene.get('HomeDesign_ManagedSession')),revision=scene.get('home_design_revision'),geometry_sha256=scene.get('home_design_geometry_sha256'),positions=[dict(id=o['source_id'],x=round(o.location.x*1000,3),z=round(-o.location.y*1000,3),rotation=round(o.rotation_euler.z,6),dimensions=list(o['dimensions_mm'])) for o in scene.objects if o.get('home_design_role')=='furniture'],camera_api=props,units=dict(system=scene.unit_settings.system,scale=scene.unit_settings.scale_length))))"""
                result=await session.call_tool('execute_blender_code',{'code':code,'user_prompt':'制作四区360全景前核对当前模型、最新家具位置和实际全景相机属性'})
                payload=result.model_dump(mode='json')
                (ROOT/'logs/v13-input-mcp-raw.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
                state=unpack(payload);assert state and state['managed'] and state['revision']==12, payload
                (ROOT/'logs/v13-input-live-state.json').write_text(json.dumps(dict(tools=names,live=state),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
                print(json.dumps(dict(revision=state['revision'],camera_api=state['camera_api'],positions=state['positions']),ensure_ascii=False))
if __name__=='__main__':asyncio.run(main())
