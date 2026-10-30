"""Read and preserve the managed live session before activating the checked panorama model."""
from pathlib import Path
from datetime import datetime
import asyncio,json,os,sys
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
from activate_model_v07 import unpack
ROOT=Path(__file__).resolve().parents[1]
async def main():
    env=dict(os.environ,DISABLE_TELEMETRY='true',BLENDER_MCP_SAFE_MODE='1',BLENDERMCP_NO_UPDATE_CHECK='1',PYTHONUTF8='1');params=StdioServerParameters(command=sys.executable,args=[str(ROOT/'tools/mcp_launch.py')],env=env);evidence=[]
    with (ROOT/'logs/v13-mcp-stderr.txt').open('w',encoding='utf-8') as err:
        async with stdio_client(params,errlog=err) as (reader,writer):
            async with ClientSession(reader,writer) as session:
                await session.initialize();catalog=await session.list_tools();names=[t.name for t in catalog.tools];assert 'execute_blender_code' in names
                code="""import bpy,json
s=bpy.context.scene
print('LIVE_STATE '+json.dumps(dict(file=bpy.data.filepath,dirty=bpy.data.is_dirty,managed=bool(s.get('HomeDesign_ManagedSession')),revision=s.get('home_design_revision'),geometry_sha256=s.get('home_design_geometry_sha256'),positions=[dict(id=o['source_id'],x=round(o.location.x*1000,3),z=round(-o.location.y*1000,3),rotation=round(o.rotation_euler.z,7),dimensions=list(o['dimensions_mm'])) for o in s.objects if o.get('home_design_role')=='furniture'],panorama_cameras=[dict(name=o.name,type=o.data.type,projection=o.data.panorama_type,position=list(o.location)) for o in s.objects if o.get('home_design_role')=='panorama_camera'])))"""
                result=await session.call_tool('execute_blender_code',{'code':code,'user_prompt':'接入360全景版前回读现场模型和全部家具位置，防止丢失手动修改'});live=unpack(result.model_dump(mode='json'));assert live and not result.isError,result.model_dump_json();assert live['managed'] and live['revision'] in [12,13]
                expected=json.loads((ROOT/f"02_geometry/geometry-master-v{live['revision']:02d}.json").read_text(encoding='utf-8'));rows={g['id']:g for g in expected['furnitureObjects']};assert len(live['positions'])==23
                assert all(abs(p['rotation'])<1e-6 and abs(p['x']-rows[p['id']]['x'])<.01 and abs(p['z']-rows[p['id']]['z'])<.01 for p in live['positions']),'Live positions changed; retain session and reconcile.'
                evidence.append(dict(phase='inspect',tools=names,live=live))
                if live['dirty']:
                    snapshot=ROOT/'06_blender'/('home-live-before-v13-'+datetime.now().strftime('%Y%m%dT%H%M%S%f')+'.blend')
                    result=await session.call_tool('execute_blender_code',{'code':'import bpy\nbpy.ops.wm.save_as_mainfile(filepath='+repr(snapshot.as_posix())+',copy=True)\nprint("LIVE_SNAPSHOT_SAVED")','user_prompt':'另存加载前未保存场景，保留可恢复副本'});assert not result.isError and 'LIVE_SNAPSHOT_SAVED' in result.model_dump_json() and snapshot.exists();evidence.append(dict(phase='previous_live_snapshot',file=str(snapshot)))
                result=await session.call_tool('execute_blender_code',{'code':"import bpy\nbpy.ops.wm.open_mainfile(filepath="+repr((ROOT/'06_blender/home-main-v13.blend').as_posix())+",load_ui=False,use_scripts=False)\nprint('V13_ACTIVE')",'user_prompt':'接入已保存核验的360全景模型及三件最新家具位置'});assert not result.isError and 'V13_ACTIVE' in result.model_dump_json(),result.model_dump_json()
                test="""import bpy
s=bpy.context.scene
ff={o['source_id']:o for o in s.objects if o.get('home_design_role')=='furniture'}
starts={k:o.location.copy() for k,o in ff.items()}
for gid in ['sofa-modular','ottoman','side-table']:
    bpy.ops.object.select_all(action='DESELECT');ob=ff[gid];ob.select_set(True);bpy.context.view_layer.objects.active=ob
    bpy.ops.home_design.move(axis='X',direction=1);assert abs(ob.location.x-starts[gid].x-.1)<1e-6
    bpy.ops.home_design.move(axis='X',direction=-1);assert all((o.location-starts[k]).length<1e-6 for k,o in ff.items())
assert len([o for o in s.objects if o.get('home_design_role')=='panorama_camera'])==4
assert s.camera.data.type=='PANO' and s.camera.data.panorama_type=='EQUIRECTANGULAR'
print('V13_LATEST_POSITIONS_MOVEMENT_AND_PANORAMA_VERIFIED')"""
                result=await session.call_tool('execute_blender_code',{'code':test,'user_prompt':'实测三件已移动家具仍可100毫米移动并复位，回读四台360全景相机'});assert not result.isError and 'V13_LATEST_POSITIONS_MOVEMENT_AND_PANORAMA_VERIFIED' in result.model_dump_json(),result.model_dump_json();(ROOT/'logs/v13-live-operator.json').write_text(result.model_dump_json(indent=2),encoding='utf-8')
                result=await session.call_tool('execute_blender_code',{'code':code,'user_prompt':'回读接入后23件家具和四区全景相机'});current=unpack(result.model_dump(mode='json'));assert current and current['revision']==13 and len(current['positions'])==23 and len(current['panorama_cameras'])==4
                target=json.loads((ROOT/'02_geometry/geometry-master-v13.json').read_text(encoding='utf-8'));rows={q['id']:q for q in target['furnitureObjects']};assert all(abs(p['x']-rows[p['id']]['x'])<.01 and abs(p['z']-rows[p['id']]['z'])<.01 for p in current['positions']);evidence.append(dict(phase='activated',live=current));(ROOT/'logs/v13-live-state.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('V13_ACTIVE_VERIFIED')
if __name__=='__main__':asyncio.run(main())
