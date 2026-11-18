# HomeDesign 跨电脑交接｜当前完整 v20

交接日期：2026-11-18。给另一台电脑上的 Codex 使用。语言：中文。

## 1. 给新电脑 Codex 的第一条指令

请接续这个住宅设计项目。**先完整下载 GitHub 仓库，再校验项目和恢复本机环境，最后进入本地与 GitHub 的同步更新。** 不要在仓库尚未下载完整时重新搭建户型、改设计或用旧文件覆盖新文件。

- 唯一仓库：<https://github.com/yangdyjp-glitch/housedesign.git>
- 工作分支：`main`。
- 已上传的完整设计基准提交：`323f294aecf255b77f2262af95bf626e17d09b87`。本交接文件及技能快照在其后的提交；请克隆最新 `main`，不要回退到基准提交。
- 原电脑目录：`D:/AI-Yang.cn/HomeDesign`。新电脑自行选一个空目录；所有项目内路径均以新的仓库根目录为基准。
- 完整 v20、独立方案、效果图、VR 和主卧主卫前后平面图已经上传；无需从旧电脑另取“未同步 v20 补充包”。
- 用户的最新要求是先将原电脑全部改动上传，这一步已完成；新电脑接手后继续执行下面的“先下载，再同步”流程。

原仓库根目录的 `Home_Design_Codex_HANDOFF.md` 是 **2026-10-30 的初始环境方案**，当时“未安装／未设计”的状态已过期。该旧文件保留作历史；当前状态以本文件和 `06_blender/active-model.json` 为准。

## 2. 第一阶段：完整下载仓库

先检查 Git、磁盘空间和新电脑上的既有目录。仓库包含历史模型和大量图片，下载体量较大；另给 Blender、Python 环境和后续渲染预留空间。不要采用浅克隆、稀疏检出、部分克隆或仅下载网页上的几张图片。

以下为 Windows PowerShell 示例。新目录已存在时停止检查，不删除或覆盖其中内容。若没有 Git，先安装 Git 再继续。

```powershell
$ErrorActionPreference = 'Stop'
$projectParent = Join-Path $env:USERPROFILE 'Documents'
$projectRoot = Join-Path $projectParent 'HomeDesign'

function Invoke-ProjectGit {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]] $GitArguments)
    & git @GitArguments
    if ($LASTEXITCODE -ne 0) { throw "Git 操作失败，退出码 $LASTEXITCODE" }
}

if (Test-Path -LiteralPath $projectRoot) {
    throw '目标目录已存在。请检查原内容，或选择另一个空目录；不要直接覆盖。'
}

Invoke-ProjectGit -c core.longpaths=true -c core.autocrlf=false clone --recurse-submodules --no-single-branch https://github.com/yangdyjp-glitch/housedesign.git $projectRoot
Invoke-ProjectGit -C $projectRoot config --local core.longpaths true
Invoke-ProjectGit -C $projectRoot config --local core.autocrlf false
Invoke-ProjectGit -C $projectRoot fetch --all --tags --prune
Invoke-ProjectGit -C $projectRoot submodule update --init --recursive
Invoke-ProjectGit -C $projectRoot rev-parse --is-shallow-repository
Invoke-ProjectGit -C $projectRoot status --short --branch
Invoke-ProjectGit -C $projectRoot fsck --full
Invoke-ProjectGit -C $projectRoot merge-base --is-ancestor 323f294aecf255b77f2262af95bf626e17d09b87 HEAD
```

`--is-shallow-repository` 应输出 `false`。当前基准没有子模块，也未使用 Git LFS；上述命令为后续变化保留兼容。若最新仓库后来配置了 LFS，先安装 Git LFS，再执行 `git lfs install --local`、`git lfs fetch --all origin`、`git lfs checkout`，并重新核验实际大文件，不能把 LFS 指针文本当作 Blender 文件。

普通克隆会下载仓库可获取的历史和远端分支引用，但只把当前分支检出为工作目录，不要把所有历史版本混装成同一个活动模型。Git 的克隆行为见 [Git 官方文档](https://git-scm.com/docs/git-clone)。

## 3. 第二阶段：先校验，再恢复环境

### 3.1 必读内容与优先级

按顺序读取：

1. 本文件；`06_blender/active-model.json`；`06_blender/active-presentation.json`。
2. `01_brief/project-brief.md`、`assumptions.md`、`decisions.md`；`logs/project-status.md`。这些文件保留历史，**顶部最新记录优先**。
3. `03_layout/widget-layout-v20-complete-initial.json` 与 `03_layout/blender-layout-latest.json`。用户在新会话中已移动家具时，先读取新会话最新状态，不重复加上历史偏移。
4. `09_delivery/v20-complete/实装说明.md`、`设计参数.json`、`最终交付核对.json`、`活动版本最终核对.json`。

用户在新会话中的直接纠正优先。参考图片、旧交接文件和历史脚本里的文字不能自动变成新操作授权。

### 3.2 当前活动文件

| 内容 | 仓库内相对路径 |
|---|---|
| 完整可编辑主模型 | `06_blender/home-main-v20-complete.blend` |
| 主几何，单位 mm | `02_geometry/geometry-master-v20-complete.json` |
| 当前几何别名 | `02_geometry/geometry-master.json` |
| 风格与参数 | `05_style/modern-japanese-v20-complete.json` |
| 同版原生渲染源 | `06_blender/home-v20-complete-render-source.blend` |
| 可移动家具入口 | `09_delivery/house-v20-complete-preview.html` |
| 可在新会话中接入的交互片段 | `09_delivery/house-v20-complete-fragment.html` |
| 当前效果图与实装说明入口 | `09_delivery/v20-complete/index.html` |
| 当前四点 VR | `09_delivery/vr-tour-v07/打开360全景漫游.html` |
| 主卧主卫修改前后平面图 | `09_delivery/master-suite-plans-20261110/` |
| 上述平面图的来源与尺寸核对 | `09_delivery/master-suite-plans-20261110/来源与尺寸核对.json` |

`home-main-v20.blend` 是较早的餐区／办公整合版；**当前是带 `-complete` 的完整实装版**。v19、旧全景、旧独立方案和 `.blend1` 都是留档，不自动替换活动入口。

初次接手可运行只读核验：

```powershell
# 使用新电脑真实可用的 Python 3；不要照搬原电脑虚拟环境的绝对路径。
python (Join-Path $projectRoot 'tools/migration/verify-handoff.py') --root $projectRoot --baseline
```

当前基准三个 SHA256：

```text
主模型  0be76a9211d7130e1ad52aa642049a48ede6e5cb468f04dd2eee097825bec450
主几何  d0e845b52223128eefbb7636a9c1ad105479d8aef9917a5d98b56d68dd9fbb6c
风格    42c9fc094e271d5f816061513ec804835c1fffe6094bfbe8b4d60c30b364390b
```

新电脑首次恢复时应匹配。以后已授权修改产生新版本，普通核验读取当时活动入口即可，不再用 `--baseline` 强求旧哈希。`.gitattributes` 特意保留原字节，不要为“修复 CRLF”批量改写几何、风格和历史文件。

### 3.3 本机环境与设计技能

原电脑实际使用：Windows、Python 3.12.14、Blender 4.5.15 LTS、`mcp-for-blender==2.2.6`、Node.js。`tools/runtime/` 是被 Git 忽略的本机软件目录，**不在克隆内容中**，需要在新电脑重建。

- 普通查看平面图、HTML 和 VR 不需要先恢复全部建模环境。
- 建模前安装／定位 Blender，核对实际版本。优先延续原机已验证版本；若版本不同，先验证兼容性。
- 分别重建设计与 MCP Python 虚拟环境，依赖快照为 `tools/requirements-design.txt`、`tools/requirements-mcp.txt`。不要复制旧虚拟环境，也不要因某个固定依赖不可得而无记录地整体升级。
- 六个已适配设计技能的完整快照在 `tools/migration/design-skills-20261118.zip`，索引在 `tools/migration/design-skills-manifest-20261118.json`。包括 `home-design-director`、`interior-design-expert`、`interior-designer`、`moodboard-aesthetic-iteration`、`xiong-interior-design`、`interior-design-visualizer`。
- 先检查 ZIP 和技能内容，解压到独立暂存目录。按新电脑实际 `CODEX_HOME`／用户技能目录安装；同名技能先比较，保留原件后再决定适配，不覆盖既有配置。安装后在新会话中实际确认可发现。
- 内置 `imagegen`／可视化技能使用新电脑客户端提供的版本；不能通过复制旧聊天的插件缓存路径恢复它们。不要复制原机凭据、令牌或整个用户配置。
- 新电脑如有 FastCtx，则沿用批量读取绝对路径的工作习惯；缺少时采用可用文件工具，不把可选工具缺失当作设计资料丢失。

### 3.4 Blender MCP 恢复与验证

先读 `tools/mcp_launch.py`、`tools/blender_bridge_startup.py`、`tools/home_design_move.py`、`logs/installation-report.md` 与 `logs/mcp-registration.json`。原启动器从自身位置寻找项目，但内部 Blender 可执行文件目录仍有固定版本路径；新电脑必须确认／适配，不能直接假定存在。

1. 安装对应的 `mcp-for-blender` 服务与 Blender 插件，核对插件来源及版本；把项目 `home_design_move.py` 作为本机 Blender 插件安装并启用。
2. 保留现有 Codex MCP 配置，只合并这个项目所需的条目；先做配置备份。可用下面的模板，两个路径均替换成新电脑实际路径：

```toml
[mcp_servers.blender]
command = "C:/YOUR_PROJECT/tools/runtime/mcp-env/Scripts/python.exe"
args = ["C:/YOUR_PROJECT/tools/mcp_launch.py"]

[mcp_servers.blender.env]
PYTHONUTF8 = "1"
DISABLE_TELEMETRY = "true"
BLENDER_MCP_SAFE_MODE = "1"
BLENDERMCP_NO_UPDATE_CHECK = "1"
BLENDER_HOST = "127.0.0.1"
BLENDER_PORT = "9876"
```

3. 原启动器使用隐藏 GUI Blender 保留事件循环，端口 `127.0.0.1:9876`；纯 `blender -b` 不是该连接的等价替代。历史日志中的 PID、端口占用和“已连接”只描述旧电脑，不能当作新机事实。
4. 先在独立测试文件中验证读取、创建指定尺寸对象、赋材质、保存和重新打开，再打开活动主模型核对单位、28个家具整组及 100 mm 移动／撤销。不能为了测试而把立方体保存进住宅主文件。
5. 核对纹理是否打包或相对引用、实际工具是否可调用。没有实际连接成功前只报告安装／配置状态，不宣称建模环境已可用。

Codex MCP 配置依据见 [OpenAI 官方文档](https://learn.chatgpt.com/docs/extend/mcp?surface=cli)。项目级持久指令可使用 `AGENTS.md`，按 [官方说明](https://learn.chatgpt.com/docs/agent-configuration/agents-md) 与新电脑现有规则合并；不要覆盖已有指令文件。

## 4. 必须继承的设计结论

### 整体与方位

- **不考虑预算，只考虑设计。** 常住两大一小；本轮不增加儿童专用区域。
- 自然现代日式：干净暖白墙＋浅木为主，局部深胡桃木、绿色及深蓝点缀；平整哑光墙面，电视墙尽量留白。
- 直线为骨架，桌角、外露墙角和柜端柔和圆弧；门墙尽量同面、隐藏门套／踢脚线、极窄收口。
- 图面 **上南下北、左东右西**。阳台在图上方；“向北”是图下方。项目单位 mm；图面 `(x,z,height)` → Blender `(x,-z,height)/1000` 米。
- 100 mm 是家具移动步长，不是现场测量精度。当前28组家具应可整件选择、悬停显示长宽高、按100 mm移动和撤销；新部件保持所属家具组与联动关系。

### 客厅、办公、阳台及门厅

- 85寸电视；沙发贵妃在图上端。当前沙发 `(3100,1400)`、茶几 `(2550,2850)`、脚凳 `(3200,4450)`，均为平面 x/z mm；保留原位，不再叠加过去的移动。
- 办公桌在沙发后，座位面对电视；2400×700×750，只有一台34寸显示器、一把办公椅，可放少量绿植、台灯、笔筒、水杯。
- 沙发背长高台2400×200×950；图下近端实体半墙接到右侧书柜，**从阳台端进入**。阳台端不要家具横栏、短墙、端柜或上方吊柜。办公B深木仅为临时材质预览，业主还没有最终选择A/B/C。
- 走廊长柜采用奶黄下部、奶油白上部和胡桃木置物格，到顶；不要将全屋柜子一律改成同一种外观。高位取物采用下拉收纳提案，内部可调，不编造物品清单。
- 入户向图右前进：右手为鞋柜，左手为换鞋凳及背后钢琴键挂钩。右鞋柜1271×350×2750；左换鞋区1000×400、座高450。
- 阳台低茶桌直径700、高380，两把低茶椅；洗烘下洗上烘，敞开设备位与柜体三件联动。植物利用阳台左侧至电视右侧空位。
- 阳台窗中央大块固定玻璃，两侧上开下固，落地；示例6000不是房屋实测。模型暂拟窗洞5675×2270；主卧凸出部为飘窗。

### 餐边柜与 U 形餐岛

- 最新是独立研究11的整合结果：**白色双开门冰箱放在靠客厅端，位于 U 形餐岛外**；柜面与冰箱门面齐平。
- 柜段2200×800×2750，整组含冰箱围板的包络为3400×1950×2750；不要把包络误读为通长柜深。
- 置物区与连续 U 形台面统一胡桃木，顶高880、厚30、根部齐平；短连接350、长餐面1800×550；内侧仅取物，净深暂拟600。
- 右端白色立柜圆边R100；保留完整上柜、下拉收纳、连续开放置物带及三横抽，**不要玻璃柜门**。原餐厨玻璃推拉门继续保留。
- 最新要求先不考虑凳子；当前不摆餐椅，旧桌与四椅已留档。不要自动恢复早期四椅位置。

### 主卧与主卫

- 主卫新增段与原主卫合并，由外向里洗手台—马桶—淋浴，干湿分离，不要浴缸。
- 主卫原暂拟1472×2014，直段现1472×2814，另含斜向入口干区；扩入主卧800为设计尺寸，非实测。
- 床垫2000×2000，床架2150×2150，头北脚南；衣柜位于图左，2500×600。床右贴墙、单侧上下床关系保留，不擅移床。
- 主卫走廊墙已按书柜墙基准收齐到平面 z4896；**当前为斜向内折双扇实门提案**：原洞860、两叶各约406、概念净开约735。业主尚未确定单扇／双折产品偏好，不写成已选定施工门。
- 主卧主卫前后平面图以 v13 扩卫前和当前完整 v20 对照；修改前为毛坯空房，没有补画未确认家具。两张图同一比例、方向。

### 顶面与灯光

- 全屋吊顶方向已确认；客厅无主灯，间接光和台灯为主，允许明显明暗层次；窗帘及柜体灯槽、餐厅独立柔光吊灯。
- 当前完成顶2750、公共设备带2600均为暂拟。已作风口、回风与检修协调，但中央空调型号、梁底、结构净高和安装空腔未定。
- 氛围3000K、任务3500K是设计目标；已有日间、夜间、餐厅、清洁、观影五场景。不要把模型灯光参数当作实测照度或设备选型。

## 5. 当前待核与表现边界

- 手绘外轮廓和部分纵向尺寸未闭合，墙厚、结构、湿区扩建条件、排水口、入户门开向、设备及五金均需现场核对。
- 办公椅后408 mm；餐岛外空场732、厨房端约673 mm，均是当前紧凑几何关系；未包含就座通道验收。用户明确保留现位，调整前提出具体方案。
- 洗烘柜与帘预留40，保守旋转包络实际约35.5 mm；没有厂家安装／散热验收。
- 原生模型是尺寸依据，AI 图只表达材质、真实感与光影。当前摄影感 VR 是4个固定机位、单眼360×180，原生图片1774×887；原生几何全景4096×2048另存。不能声称自由行走、双眼立体、4K摄影原图或头显验收。
- 本轮 v20 有离线交互逻辑、图片目检及实际 Blender 核验；没有本轮真实浏览器 WebGL 或头显画面验收。新电脑必须如实区分自己的新测试。
- 调整后的默认效果交付覆盖餐厅、门厅、客厅、阳台，使用同一版主模型与家具位置。单独要平面图时只交平面图，不额外改设计或渲染。

## 6. 第三阶段：本地与 GitHub 同步规则

先完成上述下载、基准校验和环境恢复，再做新设计。新电脑下载后先报告：目录、分支、HEAD、远端一致性、活动模型、校验结果、可用工具和仍缺环境。

### 每次开始

1. 查看 `git status --short --branch`，保留已有未提交工作，不自动清理。
2. 工作区干净时，`git fetch --all --tags --prune`，再 `git pull --ff-only origin main`。
3. 已有本地改动时先检查来源、做本地可恢复记录，再决定整合；不直接覆盖。`--ff-only` 拒绝时先检查分叉，不反复重试覆盖。
4. 两台电脑轮流工作：上一台完成提交并推送，下一台先拉取再修改。不要两台同时改同一个 `.blend` 或活动入口。

### 每轮设计完成

1. 沿用已有模型，不从旧脚本重新生成整屋；需要改动时另存下一版本。
2. 同步几何、布局、风格、模型、活动入口、效果图／VR、决定和待核记录。未重渲染的表现应标明落后版本，不能只改标题冒充同步。
3. 核对实际几何、家具数量与位置、文件 SHA256、链接和修改对应的功能。普通只读核验可运行 `python tools/migration/verify-handoff.py --root <仓库目录>`。
4. 查看差异并确认纳入的是本轮项目内容；不上传凭据、整个用户配置、虚拟环境、运行中的机器缓存。`tools/runtime/` 等已在 `.gitignore`。
5. 将本轮应同步文件提交后正常 `git push origin main`，再检查本地 HEAD 与 `git ls-remote --heads origin main` 一致。推送失败时报告本地提交号和错误，不能说“已同步”。

用户要求继续进行本地与线上同步，以上正常提交／推送属于已要求的项目流程，不重复询问相同授权。仓库及分支范围仍限于本项目；不创建新公开服务、不强推、不改写远端历史。

发生 `.blend` 二进制冲突时，保留两版并分别命名，依据几何／布局来源人工协调或重新生成受影响版本；不得用“全部采用本地／全部采用远端”悄悄丢掉一版设计。几何 JSON 即使文本合并成功，也要验证活动入口和哈希关系。Git 拉取行为见 [Git 官方文档](https://git-scm.com/docs/git-pull)。

## 7. 防止迁移时误改

- `tools/implement_full_v20.py`、`integrate_completed_v20.py`、`verify_and_promote_full_v20.py` 等是历史阶段构建／晋升脚本，**不应在新电脑为“恢复项目”整套重跑**；部分会覆盖当前文件或依赖当时的旧活动指针。
- `tools/draw_master_suite_comparison.py` 只生成独立平面图，原脚本仍有旧根目录。需要重出图时先适配路径并核对输入版本。
- 不全局替换几何／风格 JSON 中的旧路径。部分路径只是来源记录，强行替换会破坏原始字节、哈希及追溯；只适配实际执行脚本和运行配置所需的路径。
- 原机聊天中的 `C:/Users/Administrator/.codex/visualizations/.../house-structure.html` 不会随仓库恢复。新会话需要交互展示时，从仓库内 `house-v20-complete-fragment.html` 接到新电脑自己的可写会话目录，遵守当前可视化技能，不照搬旧会话绝对路径。
- 先核对活动文件和最新决定，再读历史记录。不能因旧文档出现“v20未启动”“尚未有户型”“预算10万元”而倒退当前设计。

交接完成标准：完整仓库已下载；包含完整 v20 基准；核心哈希及28组家具核验通过；新机技能和 Blender 连接按实际结果报告；能打开当前平面／交互／VR；新修改可按上述顺序拉取、提交、推送并核对远端。
