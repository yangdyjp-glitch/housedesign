"""Inspect managed live v09, preserve unsaved state, and activate verified v10."""
from pathlib import Path
import asyncio,json,os,sys,ast
from datetime import datetime
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
ROOT=Path(__file__).resolve().parents[1]
tree=ast.parse((ROOT/'tools/activate_model_v07.py').read_text(encoding='utf-8'))
import re
node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='unpack')
exec(compile(ast.Module(body=[node],type_ignores=[]),'unpack','exec'))
async def main():
    env=dict(os.environ,DISABLE_TELEMETRY='true',BLENDER_MCP_SAFE_MODE='1',BLENDERMCP_NO_UPDATE_CHECK='1',PYTHONUTF8='1')
    params=StdioServerParameters(command=sys.executable,args=[str(ROOT/'tools/mcp_launch.py')],env=env);evidence=[]
    with (ROOT/'logs/v10-mcp-stderr.txt').open('w',encoding='utf-8') as err:
        async with stdio_client(params,errlog=err) as (read,write):
            async with ClientSession(read,write) as session:
                await session.initialize();catalog=await session.list_tools();names=[t.name for t in catalog.tools]
                assert 'execute_blender_code' in names and 'get_scene_info' in names
                code="""import bpy,json
print('LIVE_STATE '+json.dumps(dict(file=bpy.data.filepath,dirty=bpy.data.is_dirty,managed=bool(bpy.context.scene.get('HomeDesign_ManagedSession')),revision=bpy.context.scene.get('home_design_revision'),geometry_sha256=bpy.context.scene.get('home_design_geometry_sha256'),positions=[dict(id=o['source_id'],x=round(o.location.x*1000,3),z=round(-o.location.y*1000,3),rotation=round(o.rotation_euler.z,7),dimensions=list(o['dimensions_mm'])) for o in bpy.context.scene.objects if o.get('home_design_role')=='furniture'])))"""
                result=await session.call_tool('execute_blender_code',{'code':code,'user_prompt':'接入公共区暖白浅木与门墙细节前，回读当前家具位置'})
                live=unpack(result.model_dump(mode='json'));assert live and not result.isError,result.model_dump_json()
                assert live['managed'] and live['revision'] in [9,10]
                expected=json.loads((ROOT/f"02_geometry/geometry-master-v{live['revision']:02d}.json").read_text(encoding='utf-8'));rows={g['id']:g for g in expected['furnitureObjects']}
                assert len(live['positions'])==21
                assert all(abs(p['rotation'])<1e-6 and abs(p['x']-rows[p['id']]['x'])<.01 and abs(p['z']-rows[p['id']]['z'])<.01 for p in live['positions']),'Live furniture changed: preserve and reconcile before loading.'
                evidence.append(dict(phase='inspect',tools=names,live=live))
                if live['dirty']:
                    snapshot=ROOT/'06_blender'/('home-v09-live-before-v10-'+datetime.now().strftime('%Y%m%dT%H%M%S%f')+'.blend')
                    result=await session.call_tool('execute_blender_code',{'code':'import bpy\nbpy.ops.wm.save_as_mainfile(filepath='+repr(snapshot.as_posix())+',copy=True)\nprint("LIVE_SNAPSHOT_SAVED")','user_prompt':'保留加载前未保存场景的可恢复副本'})
                    assert not result.isError and 'LIVE_SNAPSHOT_SAVED' in result.model_dump_json() and snapshot.exists()
                    evidence.append(dict(phase='previous_live_snapshot',file=str(snapshot)))
                result=await session.call_tool('execute_blender_code',{'code':"import bpy\nbpy.ops.wm.open_mainfile(filepath="+repr((ROOT/'06_blender/home-main-v10.blend').as_posix())+",load_ui=False,use_scripts=False)\nprint('V10_ACTIVE')",'user_prompt':'把已核验的公共区材质、同面门墙和分层照明接入现有主模型'})
                assert not result.isError and 'V10_ACTIVE' in result.model_dump_json(),result.model_dump_json()
                movement="""import bpy
root=next(o for o in bpy.context.scene.objects if o.get('source_id')=='kitchen-slider')
leaf=next(o for o in bpy.context.scene.objects if o.get('source_id')=='kitchen-slider-left')
assert root['open_ratio']==0
root['open_ratio']=1.0;root.update_tag();bpy.context.scene.frame_set(bpy.context.scene.frame_current);bpy.context.view_layer.update()
assert abs(leaf.matrix_world.translation.x-.8005)<1e-6
root['open_ratio']=0.0;root.update_tag();bpy.context.scene.frame_set(bpy.context.scene.frame_current);bpy.context.view_layer.update()
assert abs(leaf.matrix_world.translation.x)<1e-6
bpy.ops.object.select_all(action='DESELECT');root.select_set(True);bpy.context.view_layer.objects.active=root
scene=bpy.context.scene
energies=[]
for mode in [0,1,2]:
    scene['lighting_scene']=mode;scene.update_tag();scene.frame_set(scene.frame_current);bpy.context.view_layer.update()
    energies.append(bpy.data.objects['v10 客厅顶面反射光'].data.energy)
assert all(abs(a-b)<.001 for a,b in zip(energies,[12,90,100])),energies
scene['lighting_scene']=1;scene.update_tag();scene.frame_set(scene.frame_current);bpy.context.view_layer.update()
assert len([o for o in scene.objects if o.get('home_design_role')=='public_finish_detail'])==29
print('V10_LIVE_DOOR_AND_LIGHTS_VERIFIED')"""
                result=await session.call_tool('execute_blender_code',{'code':movement,'user_prompt':'实测玻璃门开合及三种照明场景，恢复门关闭和晚间照明'})
                assert not result.isError and 'V10_LIVE_DOOR_AND_LIGHTS_VERIFIED' in result.model_dump_json(),result.model_dump_json()
                (ROOT/'logs/v10-live-operator.json').write_text(result.model_dump_json(indent=2),encoding='utf-8')
                result=await session.call_tool('execute_blender_code',{'code':code,'user_prompt':'回读已接入的主模型版本、来源与全部21件家具的位置'})
                current=unpack(result.model_dump(mode='json'));assert current and current['revision']==10 and len(current['positions'])==21
                target=json.loads((ROOT/'02_geometry/geometry-master-v10.json').read_text(encoding='utf-8'));rows={g['id']:g for g in target['furnitureObjects']}
                assert all(abs(p['x']-rows[p['id']]['x'])<.01 and abs(p['z']-rows[p['id']]['z'])<.01 for p in current['positions'])
                evidence.append(dict(phase='activated',live=current))
                (ROOT/'logs/v10-live-state.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
                print('V10_ACTIVE_VERIFIED',len(current['positions']))
if __name__=='__main__':asyncio.run(main())
