from pathlib import Path
import asyncio,json,os,sys
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
from activate_model_v07 import unpack
ROOT=Path(__file__).resolve().parents[1]
async def main():
    params=StdioServerParameters(command=sys.executable,args=[str(ROOT/'tools/mcp_launch.py')],env=dict(os.environ,DISABLE_TELEMETRY='true',BLENDER_MCP_SAFE_MODE='1',BLENDERMCP_NO_UPDATE_CHECK='1',PYTHONUTF8='1'))
    with (ROOT/'logs/v10-input-mcp-stderr.txt').open('w',encoding='utf-8') as err:
        async with stdio_client(params,errlog=err) as (read,write):
            async with ClientSession(read,write) as session:
                await session.initialize();catalog=await session.list_tools();names=[t.name for t in catalog.tools];assert 'execute_blender_code' in names
                code="""import bpy,json
print('LIVE_STATE '+json.dumps(dict(file=bpy.data.filepath,dirty=bpy.data.is_dirty,managed=bool(bpy.context.scene.get('HomeDesign_ManagedSession')),revision=bpy.context.scene.get('home_design_revision'),positions=[dict(id=o['source_id'],x=round(o.location.x*1000,3),z=round(-o.location.y*1000,3),rotation=round(o.rotation_euler.z,6)) for o in bpy.context.scene.objects if o.get('home_design_role')=='furniture'],materials=[dict(name=m.name,nodes=[dict(name=n.name,type=n.type) for n in m.node_tree.nodes] if m.use_nodes else [],links=[dict(from_node=l.from_node.name,to_node=l.to_node.name,to_socket=l.to_socket.name) for l in m.node_tree.links] if m.use_nodes else []) for m in bpy.data.materials if m.name.startswith(('R01','J02','V08'))],lights=[dict(name=o.name,type=o.data.type,energy=o.data.energy,color=list(o.data.color),position=list(o.location)) for o in bpy.context.scene.objects if o.type=='LIGHT'],ceilings=[dict(name=o.name,dimensions=list(o.dimensions),position=list(o.location)) for o in bpy.context.scene.objects if o.name.startswith('表现用顶面')])))"""
                result=await session.call_tool('execute_blender_code',{'code':code,'user_prompt':'按已回答的暖白浅木及氛围灯光偏好深化前，读取当前家具位置与材质灯光'})
                state=unpack(result.model_dump(mode='json'));assert state and state['managed'] and state['revision']==9
                (ROOT/'logs/v10-input-live-state.json').write_text(json.dumps(dict(tools=names,live=state),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
                print(json.dumps(dict(revision=state['revision'],furniture=len(state['positions']),materials=state['materials'],lights=state['lights'],ceilings=state['ceilings']),ensure_ascii=False))
if __name__=='__main__':asyncio.run(main())
