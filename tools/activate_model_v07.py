"""Discover the existing local MCP, read live placement first, then load v07 if consistent."""
from pathlib import Path
import asyncio, json, os, sys, re
from datetime import datetime
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
ROOT=Path(__file__).resolve().parents[1]
def unpack(value):
    if isinstance(value,dict):
        for child in value.values():
            out=unpack(child)
            if out:return out
    elif isinstance(value,list):
        for child in value:
            out=unpack(child)
            if out:return out
    elif isinstance(value,str):
        try:
            parsed=json.loads(value)
            if not isinstance(parsed,str):
                out=unpack(parsed)
                if out:return out
        except ValueError:pass
        found=re.search(r'LIVE_STATE (\{[^\n]*\})',value)
        if found:return json.loads(found.group(1))
    return None
async def main():
    env=dict(os.environ,DISABLE_TELEMETRY='true',BLENDER_MCP_SAFE_MODE='1',BLENDERMCP_NO_UPDATE_CHECK='1',PYTHONUTF8='1')
    params=StdioServerParameters(command=sys.executable,args=[str(ROOT/'tools/mcp_launch.py')],env=env)
    evidence=[]
    with (ROOT/'logs/v07-mcp-stderr.txt').open('w',encoding='utf-8') as err:
        async with stdio_client(params,errlog=err) as (read,write):
            async with ClientSession(read,write) as session:
                await session.initialize();catalog=await session.list_tools()
                names=[t.name for t in catalog.tools]
                assert 'execute_blender_code' in names and 'get_scene_info' in names
                code="""import bpy,json
print('LIVE_STATE '+json.dumps(dict(file=bpy.data.filepath,dirty=bpy.data.is_dirty,managed=bool(bpy.context.scene.get('HomeDesign_ManagedSession')),revision=bpy.context.scene.get('home_design_revision'),positions=[dict(id=o['source_id'],x=round(o.location.x*1000,3),z=round(-o.location.y*1000,3)) for o in bpy.context.scene.objects if o.get('home_design_role')=='furniture'])))"""
                before=await session.call_tool('execute_blender_code',{'code':code,'user_prompt':'读取当前模型与家具位置，避免丢失手动调整'})
                payload=before.model_dump(mode='json');live=unpack(payload);assert live and not before.isError,payload
                evidence.append(dict(phase='inspect',tools=names,live=live,response=payload))
                (ROOT/'logs/v07-live-state.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8')
                print(json.dumps(live,ensure_ascii=True),flush=True)
                if '--inspect-only' in sys.argv:return
                assert live['managed'],'Only the managed project session may be loaded'
                rev=live['revision'];assert rev in [6,7],f'Unexpected live model revision: {rev}; preserve current session'
                expected=json.loads((ROOT/f'02_geometry/geometry-master-v{rev:02d}.json').read_text(encoding='utf-8'))
                rows={g['id']:g for g in expected['furnitureObjects']}
                assert len(live['positions'])==len(rows)
                assert all(abs(p['x']-rows[p['id']]['x'])<.01 and abs(p['z']-rows[p['id']]['z'])<.01 for p in live['positions']), 'Live positions changed; preserve session'
                if live['dirty']:
                    snapshot=ROOT/'06_blender'/('home-v06-live-before-v07-'+datetime.now().strftime('%Y%m%dT%H%M%S%f')+'.blend')
                    backup=await session.call_tool('execute_blender_code',{'code':'import bpy\nbpy.ops.wm.save_as_mainfile(filepath='+repr(snapshot.as_posix())+',copy=True)\nprint("LIVE_SNAPSHOT_SAVED")','user_prompt':'加载新版前另存当前未保存场景，保留所有现场修改'})
                    assert not backup.isError and 'LIVE_SNAPSHOT_SAVED' in backup.model_dump_json() and snapshot.exists()
                    evidence.append(dict(phase='previous_live_snapshot',file=str(snapshot)))
                load="import bpy\nbpy.ops.wm.open_mainfile(filepath="+repr((ROOT/'06_blender/home-main-v07.blend').as_posix())+",load_ui=False,use_scripts=False)\nprint('V07_ACTIVE')"
                result=await session.call_tool('execute_blender_code',{'code':load,'user_prompt':'把已核验的新布局接入当前主模型，保留旧版本'})
                assert not result.isError and 'V07_ACTIVE' in result.model_dump_json()
                refresh="""import bpy
ff={o['source_id']:o for o in bpy.context.scene.objects if o.get('home_design_role')=='furniture'}
bpy.ops.object.select_all(action='DESELECT')
ob=ff['washer'];ob.select_set(True);ff['dryer'].select_set(True);bpy.context.view_layer.objects.active=ob
a=ob.location.x;b=ff['dryer'].location.x
bpy.ops.home_design.move(axis='X',direction=-1)
assert abs(ob.location.x-a+.1)<1e-6 and abs(ff['dryer'].location.x-b+.1)<1e-6
bpy.ops.home_design.move(axis='X',direction=1)
assert abs(ob.location.x-a)<1e-6 and abs(ff['dryer'].location.x-b)<1e-6
bpy.ops.object.select_all(action='DESELECT');ff['sofa-modular'].select_set(True);bpy.context.view_layer.objects.active=ff['sofa-modular']
print('LIVE_MOVEMENT_VERIFIED')"""
                tested=await session.call_tool('execute_blender_code',{'code':refresh,'user_prompt':'用已有移动面板实测两台选中洗烘设备的100毫米移动，并恢复原位'})
                (ROOT/'logs/v07-live-operator.json').write_text(tested.model_dump_json(indent=2),encoding='utf-8')
                assert not tested.isError and 'LIVE_MOVEMENT_VERIFIED' in tested.model_dump_json()
                after=await session.call_tool('execute_blender_code',{'code':code,'user_prompt':'回读活动主模型及21件家具的位置'})
                current=unpack(after.model_dump(mode='json'));assert current['revision']==7 and len(current['positions'])==21
                evidence.append(dict(phase='activated',live=current,response=after.model_dump(mode='json')))
                (ROOT/'logs/v07-live-state.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8')
                print('V07_ACTIVE_VERIFIED')
if __name__=='__main__':asyncio.run(main())
