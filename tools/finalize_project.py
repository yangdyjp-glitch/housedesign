"""Write measured provenance, dependency locks, status and user handoff records."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, subprocess, sys

ROOT=Path(__file__).resolve().parents[1]
NOW=datetime.now(timezone.utc).isoformat()
def digest(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def save(path,value):
    (ROOT/path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
data=json.loads((ROOT/'02_geometry/geometry-master.json').read_text(encoding='utf-8'))
sha=digest(ROOT/'02_geometry/geometry-master.json')
sources=json.loads((ROOT/'logs/vendor-audit/skill-sources.json').read_text(encoding='utf-8'))
registration=json.loads((ROOT/'logs/mcp-registration.json').read_text(encoding='utf-8'))
roles={'房型.jpg':'原手绘测量图','codex-clipboard-9cd2d453-b333-4021-b37e-41631362d66d.png':'用户删除墙体标记',
       'codex-clipboard-df1537cd-add6-4258-8426-21e02c517ef3.png':'房间用途、窗型和墙面对齐说明',
       'codex-clipboard-dd3840b3-08e9-4dcc-bd35-cda470532299.png':'五个功能区域标记'}
images=[dict(id=p.name,path=str(p.relative_to(ROOT)),role=roles.get(p.name,'source'),sha256=digest(p)) for p in (ROOT/'00_source/original').iterdir() if p.is_file()]
ledger=dict(created=NOW,geometry_file='02_geometry/geometry-master-v05.json',geometry_sha256=sha,units='mm',
            source_dimensions_verified=False,source_images=images,
            baseline=dict(path='02_geometry/geometry-baseline-v04.json',sha256=digest(ROOT/'02_geometry/geometry-baseline-v04.json'),status='existing sketch reconstruction; preserve unverified dimensions'),
            current_layout=dict(path='03_layout/widget-layout-v04-latest.json',sha256=digest(ROOT/'03_layout/widget-layout-v04-latest.json'),status='latest user widget placement snapshot'),
            measurements=data['measurements'],
            walls=[dict(id=row['id'],baseline_id=row['id'],status='草图复原或拟合；未逐段完成实测校准',confidence=row.get('confidence','provisional')) for row in data['walls']],
            furniture=[dict(id=row['id'],name=row['name'],x_mm=row['x'],z_mm=row['z'],scheme=row['scheme'],
                            position_source='latest widget snapshot',size_source='previous accepted schematic option; not a measured product',source_id=row['id']) for row in data['furnitureObjects']],
            fixed_provisional_values=dict(wall_height_mm=2750,external_wall_mm=240,internal_wall_mm=[120,168],bay_seat_height_mm=500,display_slab_mm=160),
            unresolved=['外轮廓总长不闭合','部分手写尺寸含糊','入口、梁柱、墙体性质和净高待核','办公椅与书柜局部净距408mm待评审'],
            validation_scope='Exact transfer of the existing digital model and user placements; not verification of the real building')
save('02_geometry/source-ledger.json',ledger)

dependencies={}
for envname in ['mcp-env','design-env']:
    python=ROOT/'tools/runtime'/envname/'Scripts/python.exe'
    command="import importlib.metadata as m,json,sys; print(json.dumps({'python':sys.version,'packages':sorted([{'name':d.metadata['Name'],'version':d.version} for d in m.distributions()],key=lambda x:x['name'].lower())}))"
    result=subprocess.run([str(python),'-X','utf8','-c',command],capture_output=True,text=True,encoding='utf-8',check=True)
    info=json.loads(result.stdout);info['interpreter']=str(python);dependencies[envname]=info
    (ROOT/'logs'/('requirements-'+envname+'-locked.txt')).write_text('\n'.join(p['name']+'=='+p['version'] for p in info['packages'])+'\n',encoding='utf-8')
save('logs/dependency-versions.json',dependencies)
functional=dict(observed_at=NOW,static_python_files=43,
                tests=[dict(skill='xiong-interior-design',entry='scripts/test_geometry_utils.py',passed=32,failed=0),
                       dict(skill='xiong-interior-design',entry='scripts/test_export_reference_dxf.py',passed=6,failed=0,note='ezdxf font discovery emitted an unrelated non-TrueType mstmc.ttf warning; all assertions passed')],
                optional_not_run=['moodboard PDF rendering','xiong browser annotator and viewer integration','all other upstream script entrypoints'],
                session_skill_discovery='pending next normal Codex session; no new thread or app restart forced')
save('logs/skill-functional-tests.json',functional)
upstream=Path.home()/'.codex/skills/xiong-interior-design/references/upstream-provenance.json'
meta=json.loads(upstream.read_text(encoding='utf-8'));meta['executed_vendor_scripts']=functional['tests'];upstream.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

test=json.loads((ROOT/'logs/imagegen-test.json').read_text(encoding='utf-8'))
test['prompt']='Create a single realistic architectural interior image for a software environment connectivity test. This is a wholly fictional, generic room, unrelated to any real home, drawing or private project. A small peaceful reading nook with warm off-white walls, one pale oak desk, one beige chair, a book and a potted plant beside a tall window. Daylight, soft shadows, normal eye-level architectural photography, straight vertical lines, natural proportions, refined but simple. No people, no logos, no text, no floorplan or technical drawing. Landscape composition.'
test['inspection']='Saved PNG opened and visually inspected; coherent desk/chair/window scene, no private project input.'
save('logs/imagegen-test.json',test)
save('logs/preview-inspection.json',dict(inspected_at=NOW,views=[
 dict(path='07_renders/model-v05-top.png',projection='ORTHO',inspection='Room adjacency matches source plan; latest furniture placement retained; desk behind sofa facing TV; no mirrored top view; full walls retained.'),
 dict(path='07_renders/model-v05-axonometric.png',projection='ORTHO',inspection='Furniture readable; office bookcase gap visibly tight as already flagged; 450mm wall observation proxies only; original full-height walls not saved as cutaway.')]))

original=Path(r'C:\Users\Administrator\Documents\WeChat Files\ArcherYang\FileStorage\File\2026-10\Home_Design_Codex_HANDOFF.md')
checks=dict(handoff_unchanged=digest(original)==digest(ROOT/'Home_Design_Codex_HANDOFF.md'),
            baseline_original_unchanged=digest(Path(r'D:\AI-Yang.cn\outputs\house-structure\house-model.json'))==digest(ROOT/'02_geometry/geometry-baseline-v04.json'),
            prior_codex_settings_preserved=registration['unrelated_settings_preserved'],source_images=len(images),
            source_geometry_sha256=sha)
assert all(checks[k] for k in ['handoff_unchanged','baseline_original_unchanged','prior_codex_settings_preserved'])
save('logs/preservation-checks.json',checks)
outputs=['06_blender/home-main-v05.blend','06_blender/validation/2m-cube-roundtrip.blend',
         '07_renders/model-v05-top.png','07_renders/model-v05-axonometric.png','07_renders/environment-test-fictional.png']
save('09_delivery/delivery-manifest.json',dict(created=NOW,geometry_sha256=sha,outputs=[dict(path=p,size_bytes=(ROOT/p).stat().st_size,sha256=digest(ROOT/p)) for p in outputs]))

licenses={'interior-design-expert':'MIT','moodboard-aesthetic-iteration':'MIT 代码 / CC BY 4.0 文档，保留 Gu Jun 署名',
          'interior-designer':'MIT','xiong-interior-design':'MIT','interior-design-visualizer':'上游根目录未找到明确 LICENSE；未宣称许可状态'}
skillrows='\n'.join('| '+s['name']+' | `'+s['commit'][:12]+'` | '+licenses[s['name']]+' | 已安装，文件/元数据校验通过；会话识别待验证 |' for s in sources)
report=f'''# 安装与接入验证报告

记录时间：{NOW}。用户授权：“按文件搭建环境，并接入现有模型”。项目：`D:/AI-Yang.cn/HomeDesign`。

本机工具连接、图像测试和模型迁移已实测完成。新安装技能与原生 MCP 工具目录尚未在本轮会话中重新发现，因此不报告“全部配置成功”。原始交接文件及既有模型已保留。

## 实际环境

| 项目 | 实测版本与状态 |
|---|---|
| Codex CLI | 0.163.0-alpha.10.2；配置目录 `C:/Users/Administrator/.codex` |
| Blender | 4.5.15 LTS，官方 Windows x64 ZIP，构建 `5afeabba6097`；便携安装，无需改全局 PATH |
| uv | 0.13.6，构建 `329bf9448`，Windows x64 |
| Python | 3.12.14；使用 Codex 运行时创建两个独立 venv，未改动 PATH 中的 LibreOffice Python |
| GPU | NVIDIA GeForce RTX 4070 Ti；预览已用 Cycles/OptiX 实际渲染 |
| MCP 服务包 | mcp-for-blender 2.2.6；mcp SDK 1.30.0；httpx 0.28.1 |
| Blender addon | 上游自报版本1.8，协议15，与服务端期望15一致；不能与Python包版本混为一谈 |
| 家具移动 addon | 本项目 Home Design 1.0.0；整件对象、100 mm步进及原生撤销已调用验证 |

Blender 来源为[官方4.5下载目录](https://download.blender.org/release/Blender4.5/)，使用官方 `.sha256` 核验398,649,826字节ZIP；uv来自[官方0.13.6发布页](https://github.com/astral-sh/uv/releases/tag/0.13.6)，亦核验官方SHA256。精确哈希和下载URL见 `logs/runtime-install.json`。

Blender 可执行文件：`tools/runtime/blender/blender-4.5.15-windows-x64/blender.exe`。

MCP与设计依赖分别位于 `tools/runtime/mcp-env`、`tools/runtime/design-env`。全部实际版本见 `logs/dependency-versions.json` 及两个 `requirements-*-locked.txt`。设计依赖包括 Pillow12.3.0、ezdxf1.4.5、websocket-client1.9.2、fpdf2 2.9.0、PyYAML6.0.3。

## 技能逐项状态

全部安装在 `C:/Users/Administrator/.codex/skills/`，通过内置 skill-installer 取得固定提交至审核区，再将已审阅的相同字节复制到目标目录并写入本地适配入口。保留 `references/upstream-SKILL.md`、来源JSON及上游许可；未改原仓库。

| 技能 | 固定提交 | 许可记录 | 当前状态 |
|---|---|---|---|
{skillrows}
| home-design-director | 本地创建 | 本项目通用协调规则 | skill-creator建立，文件/引用/提示校验通过；会话识别待验证 |

本地适配去掉不可用的Claude/Stability工具声明，图像任务交给内置imagegen，三维任务交给已实测MCP；美国商业/ADA示例不作为本住宅的默认标准；审美评分标记为主观辅助；既有用户选择和阶段授权无需重复确认。

六份SKILL均经过真实读取、YAML解析、名称/描述、引用路径、界面提示和内置quick_validate校验。结果见 `logs/skill-validation.json`。未通过新会话发现前，不能把技能列为“已被当前会话加载”。

43个Python文件完成语法及导入清单扫描，并检查网络、进程和清理调用。xiong的几何与DXF两个测试入口实际运行，共 **38项通过**。其他上游脚本、浏览器批注/查看器和审美PDF尚未逐项调用；这些可选子能力暂不列为已实测可用。上游脚本的独立schema和SHA批准约束未被伪造或跳过；当前迁移使用本项目已检查的转换代码。

## MCP：已连接且通过建模测试

配置位于 `C:/Users/Administrator/.codex/config.toml`，新增服务器名 `blender`。使用绝对路径指向项目隔离Python与 `tools/mcp_launch.py`，启动超时90秒、工具超时180秒。精确登记内容和无关设置比较结果见 `logs/mcp-registration.json`。

修改前备份：`{registration['backup']}`。原有code-review、codex_app、cua_repl、fastctx和node_repl设置均与备份逐项一致；未启用或停用它们。

本轮通过真实MCP SDK stdio客户端发现9个上游工具并逐次调用，不是只检查配置文件。执行如下验证：

1. 读取Blender默认场景并完成协议15握手。
2. 创建2m立方体MCP_TEST_2M，指定MCP_TEST_BLUE材质，保存至 `06_blender/validation/2m-cube-roundtrip.blend`。
3. 重新打开该文件，读回尺寸 `[2.0,2.0,2.0]` m和材质名称/颜色，断言通过。
4. 通过MCP导入当前住宅，保存主模型，重开逐件核对13件家具位置和来源哈希。
5. 调用全部家具在X/Y方向移动100mm并移回，测试原生撤销及位置JSON保存/回读。

测试脚本为 `tools/probe_mcp.py`、`mcp_roundtrip.py`、`import_existing_model.py`、`test_furniture_movement.py` 和 `audit_blender_model.py`；真实响应保存在同名用途的logs JSON中。导入脚本现在拒绝覆盖已有v05，后续改动应另存新版本。

实际连接设置 `DISABLE_TELEMETRY=true`、`BLENDER_MCP_SAFE_MODE=1`，只监听本机9876。`get_addon_status`实际读回telemetry_consent=false，素材库/外部生成器均off。未配置外部图像API Key或额外账户。

上游addon需要GUI事件循环，明确拒绝 `blender -b` 实时服务器；本项目启动器按需开启隐藏窗口并复用连接。离线预览另用隔离后台进程，从已保存模型只读渲染。MCP参考来源：[上游仓库](https://github.com/ahujasid/mcp-for-blender)，[PyPI固定版本](https://pypi.org/project/mcp-for-blender/2.2.6/)。

当前Codex原生工具目录未在本轮热加载新登记条目。重新启动Codex后须确认 `blender` 工具和6个技能被发现；本次SDK实际连通通过与这项会话发现状态分别记录。没有代替用户关闭当前聊天或创建新聊天。

## 现有模型接入

- 主模型：`06_blender/home-main-v05.blend`；源几何SHA256：`{sha}`。
- 13件可整件选择的家具，175个组成零件保留来源；60个墙体网格，8片玻璃。最近7件移动位置按widget快照继承，逐件读回一致。
- 坐标：项目mm；Blender m；`(图面x,-图面z,高度)/1000`。方向不作地理推断；顶视图与原图左右关系一致。
- 实际家具网格外包框与输入数据最大复制误差0.000381mm，属于数字转换核对，**不是房屋测量精度**。
- 已核对红框墙室内侧共面1072mm、阳台玻璃下缘0mm；主卧飘窗及已删除墙关系沿用。
- 最新局部办公净距408mm保留，不擅自调回旧位置。外轮廓不闭合、墙厚/净高/入口等待核状态保留，详见 `01_brief/assumptions.md` 和 `02_geometry/source-ledger.json`。
- `model-v05-top.png`保留全墙，`model-v05-axonometric.png`只用低墙观察副本。两图已打开目检；主模型全墙未被替换。家具的浅木/暖白等是沿用的材质示意，没有新风格批准。

打开入口为 `09_delivery/打开房屋模型.cmd`，已验证能启动并找到本项目窗口；测试未把窗口显示到前台。家具操作见 `09_delivery/使用说明.md`。原交互页面不自动与Blender双向同步，不能重复叠加已烘焙位置的旧偏移。

## ImageGen：内置模式已测试

已生成一张完全虚构、非私人房间PNG，无真实户型或照片输入，1536×1024。原输出保留并复制到 `07_renders/environment-test-fictional.png`，核验签名、尺寸、SHA并打开目检通过。它是环境测试，不是本住宅的设计方案。完整提示词、实际输出和核验结果见 `logs/imagegen-test.json`。

## 错误与恢复记录

- GitHub匿名API返回403，git HTTPS部分请求连接超时；改从官方GitHub页面读取currentOid，并用内置安装器从codeload取得固定提交。保留初次失败记录。
- 大型技能仓库在Windows普通临时路径解压超长失败；使用extended-length临时路径与反斜杠子路径后，内置安装器完成，未修改系统长路径策略。
- Codex CLI添加服务器时顺带规范化node_repl设置。比较发现后保留尝试副本，恢复原配置字节，仅追加blender段，逐项比较原设置通过。
- 内置技能辅助脚本默认GBK，首次中文校验读取失败；对校验进程启用UTF-8，并把协调技能界面文件转为UTF-8后六项全部通过。
- 首次几何审计按逻辑墙ID全等查找，实际网格ID带 `-end` 后缀，断言未匹配。修正索引解析后共面检查通过；正式几何未因此修改，失败响应留档。
- ezdxf测试扫描系统字体时提示mstmc.ttf不是标准字体，6项DXF测试仍全部通过；未改变系统字体。

若后续连接未发现，先重新启动Codex并查看MCP目录，再看 `logs/blender-bridge.log`。启动器会按需打开已保存的本项目模型；不要同时运行多个客户端争用同一端口。

若需撤销本次配置，可停用blender服务器和两个新增Blender addon；配置备份仍在用户目录。全量恢复备份前应先比较本次之后的其他修改，避免覆盖用户后续配置。技能原始来源、副本、固定SHA和依赖版本均保留，可按报告定位；不自动清理用户原有内容。

## 仍待完成的验证或资料

1. 在后续正常Codex会话确认6个技能和原生blender工具可被识别。当前状态：**已安装/已登记，待会话发现验证**。
2. 可选PDF、浏览器批注器及其余上游脚本只有实际需要并测试后才启用，不将未测子能力称为全部可用。
3. 住宅尺寸闭合、净高、入口、墙体性质、预算和风格等未知资料仍待后续设计阶段核对。本次不扩大其他房间装修范围。
'''
(ROOT/'logs/installation-report.md').write_text(report,encoding='utf-8')
manifest_path=ROOT/'logs/skill-install-manifest.json'
prior=json.loads(manifest_path.read_text(encoding='utf-8'))
before_path=ROOT/'logs/skill-install-manifest-before-functional-tests.json'
if not before_path.exists():before_path.write_bytes(manifest_path.read_bytes())
byname={row['name']:row for row in prior}
allnames=[row['name'] for row in json.loads((ROOT/'logs/skill-validation.json').read_text(encoding='utf-8'))]
current=[]
for name in allnames:
    folder=Path.home()/'.codex/skills'/name
    row=byname.get(name,dict(name=name,path=str(folder),commit=None,origin='local skill-creator',python_files=[]))
    row['files']=[dict(path=str(p.relative_to(folder)),sha256=digest(p)) for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    row['file_count']=len(row['files']);row['manifest_updated_at']=NOW
    current.append(row)
save('logs/skill-install-manifest.json',current)
save('logs/model-launcher-check.json',dict(verified=True,result='Managed Blender GUI window found by process id and GHOST_WindowClass',shown_in_test=False,mode='open_model.py --check'))
print(json.dumps(dict(project=str(ROOT),geometry_sha256=sha,source_images=len(images),preservation_checks=checks,
                     skills_installed=6,skill_session_discovery='pending',mcp_roundtrip='passed',imagegen='passed',editable_model=str(ROOT/'06_blender/home-main-v05.blend')),ensure_ascii=True))

if __name__=='__main__':pass
