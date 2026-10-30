from pathlib import Path
import asyncio, json, os, sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'06_blender/validation/2m-cube-roundtrip.blend'
TARGET.parent.mkdir(parents=True,exist_ok=True)
CREATE='''import bpy, json
if not bpy.context.scene.get('HomeDesign_ManagedSession'):
    raise RuntimeError('Only the task-managed scratch session may be used')
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.context.scene.unit_settings.system='METRIC'
bpy.context.scene.unit_settings.scale_length=1.0
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0,0,1))
cube=bpy.context.object
cube.name='MCP_TEST_2M'
mat=bpy.data.materials.new('MCP_TEST_BLUE')
mat.diffuse_color=(0.22,0.45,0.7,1)
mat.use_nodes=True
mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(0.22,0.45,0.7,1)
cube.data.materials.append(mat)
bpy.ops.wm.save_as_mainfile(filepath=TARGET_PLACEHOLDER)
print(json.dumps(dict(saved=bpy.data.filepath,dimensions=list(cube.dimensions),material=cube.data.materials[0].name)))
'''.replace('TARGET_PLACEHOLDER',repr(TARGET.as_posix()))
REOPEN='''import bpy, json
bpy.ops.wm.open_mainfile(filepath=TARGET_PLACEHOLDER,load_ui=False,use_scripts=False)
cube=bpy.data.objects['MCP_TEST_2M']
dimensions=[round(v,6) for v in cube.dimensions]
assert dimensions==[2.0,2.0,2.0], dimensions
assert cube.data.materials[0].name=='MCP_TEST_BLUE'
assert bpy.context.scene.unit_settings.system=='METRIC'
print('ROUNDTRIP_OK '+json.dumps(dict(file=bpy.data.filepath,dimensions_m=dimensions,material=cube.data.materials[0].name,baseColor=list(cube.data.materials[0].diffuse_color),blender=bpy.app.version_string)))
'''.replace('TARGET_PLACEHOLDER',repr(TARGET.as_posix()))

async def main():
    env=dict(os.environ,DISABLE_TELEMETRY='true',BLENDER_MCP_SAFE_MODE='1',BLENDERMCP_NO_UPDATE_CHECK='1',PYTHONUTF8='1')
    params=StdioServerParameters(command=sys.executable,args=[str(ROOT/'tools/mcp_launch.py')],env=env)
    evidence=[]
    with (ROOT/'logs/mcp-roundtrip-stderr.log').open('w',encoding='utf-8') as err:
        async with stdio_client(params,errlog=err) as (read,write):
            async with ClientSession(read,write) as session:
                await session.initialize()
                for phase,code in [('create_save',CREATE),('reopen_read',REOPEN)]:
                    result=await session.call_tool('execute_blender_code',{'code':code,'user_prompt':'本机测试：创建2米立方体、赋材质、保存并重开验证'})
                    row=dict(phase=phase,response=result.model_dump(mode='json'))
                    evidence.append(row)
                    print(json.dumps(row,ensure_ascii=True))
                    if result.isError:raise RuntimeError('MCP test failed')
    (ROOT/'logs/mcp-roundtrip.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8')
    assert 'ROUNDTRIP_OK' in json.dumps(evidence)
    assert TARGET.is_file()

if __name__=='__main__':asyncio.run(main())
