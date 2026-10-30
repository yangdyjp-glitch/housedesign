# 安装与接入验证报告

记录时间：2026-10-30T11:20:25.554132+00:00。用户授权：“按文件搭建环境，并接入现有模型”。项目：`D:/AI-Yang.cn/HomeDesign`。

续接提示（2026-10-31）：以下安装过程为历史记录；当前模型已至v10，活动入口以`06_blender/active-model.json`为准，最新设计状态见`logs/project-status.md`。六个住宅技能已在当前会话列表发现并按需读取；原生blender工具目录仍未暴露，实际MCP客户端连接和v10三场景／门开合实测已通过。风格、人数与预算现已确认，现场闭合尺寸和机电条件继续待核。

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
| moodboard-aesthetic-iteration | `478d5ae32806` | MIT 代码 / CC BY 4.0 文档，保留 Gu Jun 署名 | 已安装，文件/元数据校验通过；会话识别待验证 |
| xiong-interior-design | `8d5deb487cdc` | MIT | 已安装，文件/元数据校验通过；会话识别待验证 |
| interior-design-visualizer | `45a2c52be716` | 上游根目录未找到明确 LICENSE；未宣称许可状态 | 已安装，文件/元数据校验通过；会话识别待验证 |
| interior-designer | `9554f15f4c20` | MIT | 已安装，文件/元数据校验通过；会话识别待验证 |
| interior-design-expert | `f49825290077` | MIT | 已安装，文件/元数据校验通过；会话识别待验证 |
| home-design-director | 本地创建 | 本项目通用协调规则 | skill-creator建立，文件/引用/提示校验通过；会话识别待验证 |

本地适配去掉不可用的Claude/Stability工具声明，图像任务交给内置imagegen，三维任务交给已实测MCP；美国商业/ADA示例不作为本住宅的默认标准；审美评分标记为主观辅助；既有用户选择和阶段授权无需重复确认。

六份SKILL均经过真实读取、YAML解析、名称/描述、引用路径、界面提示和内置quick_validate校验。结果见 `logs/skill-validation.json`。未通过新会话发现前，不能把技能列为“已被当前会话加载”。

43个Python文件完成语法及导入清单扫描，并检查网络、进程和清理调用。xiong的几何与DXF两个测试入口实际运行，共 **38项通过**。其他上游脚本、浏览器批注/查看器和审美PDF尚未逐项调用；这些可选子能力暂不列为已实测可用。上游脚本的独立schema和SHA批准约束未被伪造或跳过；当前迁移使用本项目已检查的转换代码。

## MCP：已连接且通过建模测试

配置位于 `C:/Users/Administrator/.codex/config.toml`，新增服务器名 `blender`。使用绝对路径指向项目隔离Python与 `tools/mcp_launch.py`，启动超时90秒、工具超时180秒。精确登记内容和无关设置比较结果见 `logs/mcp-registration.json`。

修改前备份：`C:\Users\Administrator\.codex\config.toml.before-home-design-20261030-185351`。原有code-review、codex_app、cua_repl、fastctx和node_repl设置均与备份逐项一致；未启用或停用它们。

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

- 主模型：`06_blender/home-main-v05.blend`；源几何SHA256：`3245f7e67295ef319ed20df976297279fc298d05e0d3d6fc9e49d9fd1cf56d43`。
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
