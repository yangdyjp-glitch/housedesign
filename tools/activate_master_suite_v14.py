"""Inspect and preserve the managed live layout before switching to v14."""
from pathlib import Path
from datetime import datetime
import asyncio,json,os,sys
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
from activate_model_v07 import unpack
ROOT=Path(__file__).resolve().parents[1]
async def main():
    env=dict(os.environ,DISABLE_TELEMETRY='true',BLENDER_MCP_SAFE_MODE='1',BLENDERMCP_NO_UPDATE_CHECK='1',PYTHONUTF8='1')
    params=StdioServerParameters(command=sys.executable,args=[str(ROOT/'tools/mcp_launch.py')],env=env);evidence=[]
    with (ROOT/'logs/v14-mcp-stderr.txt').open('w',encoding='utf-8') as err:
      async with stdio_client(params,errlog=err) as (reader,writer):
       async with ClientSession(reader,writer) as session:
        await session.initialize();catalog=await session.list_tools();names=[t.name for t in catalog.tools];assert 'execute_blender_code' in names
        read="""import bpy,json
s=bpy.context.scene
print('LIVE_STATE '+json.dumps(dict(file=bpy.data.filepath,dirty=bpy.data.is_dirty,managed=bool(s.get('HomeDesign_ManagedSession')),revision=s.get('home_design_revision'),geometry_sha256=s.get('home_design_geometry_sha256'),positions=[dict(id=o['source_id'],x=round(o.location.x*1000,3),z=round(-o.location.y*1000,3),rotation=round(o.rotation_euler.z,7),dimensions=list(o['dimensions_mm'])) for o in s.objects if o.get('home_design_role')=='furniture'],source_walls=sum(o.get('home_design_role')=='wall' for o in s.objects),window_glass=sum(o.get('home_design_role')=='glass' for o in s.objects))))"""
        async def call(code,prompt):
            result=await session.call_tool('execute_blender_code',dict(code=code,user_prompt=prompt));assert not result.isError,result.model_dump_json();return result
        result=await call(read,'接入主卫扩展概念前，检查当前家具位置与版本');live=unpack(result.model_dump(mode='json'));assert live and live['managed'] and live['revision'] in [13,14]
        expected=json.loads((ROOT/f"02_geometry/geometry-master-v{live['revision']:02d}.json").read_text(encoding='utf-8'));rows={q['id']:q for q in expected['furnitureObjects']}
        assert len(live['positions'])==len(rows) and all(abs(p['rotation'])<1e-6 and abs(p['x']-rows[p['id']]['x'])<.01 and abs(p['z']-rows[p['id']]['z'])<.01 for p in live['positions']),'Retain changed live layout for reconciliation.'
        evidence.append(dict(phase='inspect',tools=names,live=live))
        if live['dirty']:
            snap=ROOT/'06_blender'/('home-live-before-v14-'+datetime.now().strftime('%Y%m%dT%H%M%S%f')+'.blend')
            await call('import bpy\nbpy.ops.wm.save_as_mainfile(filepath='+repr(snap.as_posix())+',copy=True)\nprint("LIVE_SNAPSHOT_SAVED")','保留加载前未保存场景副本');assert snap.exists();evidence.append(dict(phase='snapshot',path=str(snap)))
        await call('import bpy\nbpy.ops.wm.open_mainfile(filepath='+repr((ROOT/'06_blender/home-main-v14.blend').as_posix())+',load_ui=False,use_scripts=False)\nprint("V14_ACTIVE")','接入保留公共区家具位置的新版主卧主卫概念模型')
        test="""import bpy,math
s=bpy.context.scene
ff={o['source_id']:o for o in s.objects if o.get('home_design_role')=='furniture'}
assert len(ff)==27
starts={k:o.location.copy() for k,o in ff.items()}
for gid in ['master-bed','master-wardrobe','master-vanity','master-toilet']:
 bpy.ops.object.select_all(action='DESELECT');ob=ff[gid];ob.select_set(True);bpy.context.view_layer.objects.active=ob
 for axis,index in [('X',0),('Y',1)]:
  bpy.ops.home_design.move(axis=axis,direction=1);assert abs(ob.location[index]-starts[gid][index]-.1)<1e-6
  bpy.ops.home_design.move(axis=axis,direction=-1);assert all((o.location-starts[k]).length<1e-6 for k,o in ff.items())
door=bpy.data.objects['主卫侧门 · 向私用门厅开启'];screen=bpy.data.objects['主卫淋浴隔断 · 移门']
door['open_ratio']=1.;screen['open_ratio']=1.;door.update_tag();screen.update_tag();s.frame_set(s.frame_current);bpy.context.view_layer.update()
assert abs(door.rotation_euler.z+math.pi/2)<1e-5
pane=bpy.data.objects['v14-shower-moving-glass'];assert abs(pane.location.x-9.359)<1e-5
door['open_ratio']=0.;screen['open_ratio']=0.;door.update_tag();screen.update_tag();s.frame_set(s.frame_current);bpy.context.view_layer.update()
assert abs(door.rotation_euler.z)<1e-6 and abs(pane.location.x-10.059)<1e-5
print('V14_FOUR_NEW_OBJECTS_100MM_AND_DOORS_VERIFIED')"""
        result=await call(test,'实测新增四件100毫米移动并复位，主卫门与淋浴隔断开合并复位');assert 'V14_FOUR_NEW_OBJECTS_100MM_AND_DOORS_VERIFIED' in result.model_dump_json();(ROOT/'logs/v14-live-operator.json').write_text(result.model_dump_json(indent=2),encoding='utf-8')
        result=await call(read,'回读接入后的全部27件家具、62墙源与12片外窗玻璃');current=unpack(result.model_dump(mode='json'));rows={q['id']:q for q in json.loads((ROOT/'02_geometry/geometry-master-v14.json').read_text(encoding='utf-8'))['furnitureObjects']}
        assert current and current['revision']==14 and current['source_walls']==62 and current['window_glass']==12
        assert len(current['positions'])==27 and all(abs(p['x']-rows[p['id']]['x'])<.01 and abs(p['z']-rows[p['id']]['z'])<.01 for p in current['positions'])
        evidence.append(dict(phase='activated',live=current));(ROOT/'logs/v14-live-state.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');(ROOT/'03_layout/blender-layout-v14.json').write_text(json.dumps(current,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('V14_ACTIVE_VERIFIED')
if __name__=='__main__':asyncio.run(main())
