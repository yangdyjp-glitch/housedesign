# 住宅室内设计系统｜Windows Codex Handoff

> 版本：1.0 ｜交接日期：2026-10-30  
> 用途：将本文件交给 **Windows 本机 Codex**，由其完成环境核验、Skill/MCP 配置，并在日后接收户型资料后开展整套住宅室内设计。  
> 当前状态：**方案已规划；用户本机的安装、连通性、户型和项目数据均未验证；不得声称已经完成安装或设计。**

## 0. 给 Codex 的首条执行指令（请从这里开始）

你现在接手一个“面向零设计基础用户的全屋室内装修设计”长期项目。请**完整阅读本 handoff 文件**并严格按照其中的优先级开展工作：

1. 先检查 Windows 本机环境、既有 Codex Skills、Blender 和 MCP 状态。不要覆盖用户已有配置。
2. 审核并安装下文列出的可用设计 Skills，兼容性不符合要求的先适配或报告，不得假装可用。
3. 配置并实测 `mcp-for-blender`；若依赖、权限、网络或安装失败，记录错误、诊断原因并给出可复现的解决方案。
4. 创建自定义协调 Skill `home-design-director`，通过它组织方案设计、设计评审、几何建模及效果图输出。
5. 创建项目目录和初始状态文档，输出真实的安装验证结果、尚缺资料以及下一步建议。
6. **如果尚未获得户型图与测量尺寸，到“环境就绪、等待设计资料”为止。不要编造真实住宅的户型、尺寸、承重条件或预算。**
7. 用户是设计零基础。以中文解释方案，主动提供明确的可视化选项和优缺点；不要要求用户先学习室内设计软件或美术知识。

成功标准：用户只需上传户型图、提供少量居住偏好，并在重要方案节点作选择，就能获得可追溯、尺寸受约束的全屋设计方案、Blender 可编辑模型及多视角写实效果图。

---

## 1. 项目目标与边界

### 1.1 目标

建立从 `原始户型 / 实测信息` 到 `空间布局 → 风格与意向板 → 材料/家具/照明方案 → Blender 三维场景 → 写实效果图 → 预算与设计清单` 的完整工作流。

设计系统需要主动承担以下角色：

- **AI 主设计师**：主动提出空间组织、审美方向、色彩、材质、灯光、家具配置，不只是执行用户详细指令。
- **审美评审顾问**：检查风格是否统一、设计是否协调，指出可执行的改善方式。
- **居住实用性顾问**：检查动线、家具尺寸、收纳、采光、维护难度、预算和采购落地性。
- **几何与建模执行者**：以经确认的实际尺寸建模，避免渲染图片随意改变空间。
- **视觉表达者**：提供不同风格参考、对比图、房间多角度效果图。

### 1.2 已确认的用户偏好

- 使用平台：**Windows + OpenAI Codex**；后续在用户本机进行设计。
- 使用者：没有室内设计或美术基础，希望 AI **主动协助设计决策**。
- 设计范围：整套住宅，而非单个房间。
- 预期产出：空间布局、三维模型、家具、材质、真实感效果图。
- 核心理念：**设计优先，确认后建模；建模优先，约束后出图。**

### 1.3 尚未提供、不能假设的数据

住宅所在地/适用规范、CAD/PDF 户型图、实际尺寸、净高、梁柱与门窗、承重墙、管井及水电位置、照片、家庭成员及使用习惯、生活方式、预算及币种、装修范围、交付期限、风格偏好。将未知项标注为“待确认”，不要当作事实。

### 1.4 不得越界的事项

- 概念图、AI 图片和初步 DXF **不能直接视作施工图**。
- 不得根据户型图截图臆测承重墙或允许拆改的墙体，不得自行指定结构拆改。
- 不得将带视觉幻觉的 ImageGen 图片反向当成测量依据。
- 涉及结构、机电、给排水、燃气、防水、消防、通风、许可等需注明由当地持证专业人员核验。
- 在未取得授权和预算条件前，不采购、付费、注册外部服务、发布私人户型或上传私人数据至公开仓库。

---

## 2. 工具与 Skill 分工（推荐 3+1 设计核心 + 执行层）

| 级别 | Skill / 工具 | 主要责任 | 官方/项目来源及风险 |
|---|---|---|---|
| P0 主设计 | `interior-design-expert` | 空间规划、色彩理论、家居比例、灯光、风格方向 | [curiositech/some_claude_skills](https://github.com/curiositech/some_claude_skills/blob/main/.claude/skills/interior-design-expert/SKILL.md)。原为 Claude Skill，部分工具声明指向 Stability AI MCP，需要适配 Codex。 |
| P0 审美顾问 | `moodboard-aesthetic-iteration` | 意向板、风格一致性、审美复核与跨版本整改 | [gujun1502/arch-skills](https://github.com/gujun1502/arch-skills/blob/main/skills/moodboard-aesthetic-iteration/SKILL.md)。审查并规范 YAML front matter；仓库公开页面可见元数据解析警告，不能盲信直接安装成功。 |
| P0 实用性顾问 | `interior-designer` | 动线、家具尺寸、材料耐用性、灯光、预算/采购清单 | [wonsukchoi/domain-experts](https://github.com/wonsukchoi/domain-experts/blob/main/roles/interior-designer/SKILL.md)。部分示例是美国商业空间和 ADA 规则，**不得直接套用到未知地区住宅**。 |
| P0 协调层 | `home-design-director`（自建） | 统一调度、阶段门禁、用户选项、设计版本和需求约束 | 用内置 `$skill-creator` 或手工建立；设计要求见第 5 节。 |
| P1 户型与几何 | `xiong-interior-design` | CAD 截图整理、布局标注、简易 DXF、Blender 白模/GLB | [xionglaoshi/xiong-interior-design](https://github.com/xionglaoshi/xiong-interior-design)。以确认的几何为基础，不能自动识别结构性质。 |
| P1 局部可视化 | `interior-design-visualizer` | 房间照片/参考图与设计要求整合，局部改造可视化 | [RyanZhang10/interior-design-visualizer](https://github.com/RyanZhang10/interior-design-visualizer/tree/main/interior-design-visualizer)。需确认当前 Codex 内置图像生成能力可用。 |
| P1 三维执行 | Blender + `mcp-for-blender` | 三维几何、家具代理体及精细模型、材质、灯光、相机、场景修改 | [ahujasid/mcp-for-blender](https://github.com/ahujasid/mcp-for-blender)。注意原 `blender-mcp` 包名已迁移为 `mcp-for-blender`。 |
| P1 写实渲染 | Codex 内置 `imagegen` 和/或 Blender 渲染 | 风格意向图、草图转写实、局部改图、受几何约束的最终出图 | [OpenAI imagegen Skill](https://github.com/openai/skills/blob/main/skills/.system/imagegen/SKILL.md)。优先使用内置模式；CLI/API Key 不是默认前置条件。 |

**设计责任的优先顺序：** `home-design-director` → `interior-design-expert` 形成方案 → `moodboard-aesthetic-iteration` 与 `interior-designer` 分别评审 → 由用户审批 → `xiong-interior-design` 和 Blender MCP 实施 → ImageGen/Blender 输出最终效果图。

注意：这些 Skill 是知识和工作流约束，不能保证等同于持证室内设计师，也不会因为安装后就自动变成独立并行的多智能体。协调器应清楚控制调用顺序、读取对应说明并生成可检查的评审记录。

---

## 3. Windows 环境配置与验证 Runbook

### 3.1 先检查（不改动）

在 PowerShell 运行：

```powershell
Get-Command git, python, py, uvx, codex -ErrorAction SilentlyContinue |
    Select-Object Name, Source

if (Get-Command codex -ErrorAction SilentlyContinue) {
    codex mcp list
}
```

另检查 Blender 是否已安装及其实际版本、是否有 Codex 桌面客户端/CLI、`$env:CODEX_HOME` 与 `$env:USERPROFILE\.codex` 实际位置，以及用户是否已安装同名 Skill。记录结果。**不要盲目覆盖 `config.toml` 或清空既有 MCP 列表。**

### 3.2 Blender MCP 推荐安装方式

先从 [Blender 官网](https://www.blender.org/download/)安装 Blender（若本机尚无），然后按 [mcp-for-blender README](https://github.com/ahujasid/mcp-for-blender) 的现行说明配置。优先使用受控、可审计的方式，而不是直接执行联网的一键 PowerShell 脚本：

```powershell
winget install --id=astral-sh.uv -e
```

**关闭并重新打开 PowerShell**，验证 `uvx --version`。然后：

```powershell
uvx mcp-for-blender setup
```

在安装引导中选择 Codex；已存在的同名配置先检查，避免重复添加。若自动引导失败，且确认 `codex` CLI 可用，可改用**手动方式**：

```powershell
codex mcp add blender -- uvx mcp-for-blender
uvx mcp-for-blender install-addon
codex mcp list
```

如果没有 Codex CLI，可在 Codex Desktop 设置中将 STDIO MCP 服务器 `blender` 指向 `uvx mcp-for-blender`，或**谨慎**合并至用户已有的 `config.toml`：

```toml
[mcp_servers.blender]
command = "uvx"
args = ["mcp-for-blender"]
```

仅为示例；已存在 `[mcp_servers.blender]` 时不得再追加重复段。若桌面端找不到 `uvx`，按 `Get-Command uvx` 的实际路径改为绝对路径。

Blender 内：`Edit → Preferences → Add-ons` 中确认 `MCP for Blender` 已启用；进入 3D Viewport，按 `N` 找到插件面板，需要时点击 `Start MCP Server`。重新启动 Codex 使 MCP 工具重新发现。不要同时从多个客户端争用同一插件服务端。

**隐私检查**：在使用第三方 Blender MCP 前，查看 README 中的 telemetry 与附加资产下载说明；如用户需要禁用遥测，应核查其当前版本文档并设置 `DISABLE_TELEMETRY=true`（具体落点依当前 MCP 配置）。不自动启用额外付费、资产库或外部 API。

**MCP 必须实际做一次最小测试**：创建一个边长 2 m 的测试立方体、指定材质，保存测试 `.blend`，重新打开并读回场景对象、尺寸与材质；完成后可清理测试场景。单纯出现在 `codex mcp list` 不能算连通测试通过。

### 3.3 安装第三方设计 Skills

优先使用 Codex 自带的 `$skill-installer`（如果当前版本可用），以其实际说明为准；否则在**临时目录**检出相应 GitHub 仓库，先审核内容，再把目标 Skill 子目录复制到 `$CODEX_HOME/skills/<skill-name>/`（未设置 `CODEX_HOME` 时默认 `%USERPROFILE%\.codex\skills`）。必须完整保留 `SKILL.md`、`references/`、必要的 `assets/` 和所需 `scripts/`。

要安装的目录（均已核对仓库路径；用户本机尚未安装）：

```text
https://github.com/curiositech/some_claude_skills
  .claude/skills/interior-design-expert/

https://github.com/gujun1502/arch-skills
  skills/moodboard-aesthetic-iteration/

https://github.com/wonsukchoi/domain-experts
  roles/interior-designer/

https://github.com/xionglaoshi/xiong-interior-design
  [仓库根目录即 Skill 目录，含 SKILL.md / scripts / references]

https://github.com/RyanZhang10/interior-design-visualizer
  interior-design-visualizer/
```

适配要求：

1. 先检查所有外部 Skill 的授权、联网操作、Shell/Python 脚本、外部服务依赖与敏感数据行为；未经许可不运行陌生安装脚本。
2. 验证 `SKILL.md` YAML front matter 至少有有效 `name` 与 `description`；对有语法问题的元数据在**本地副本**中修复并保留原始备份与修改说明，不擅自改变原仓库。
3. `interior-design-expert` 原有 `allowed-tools` 中的 Claude/Stability AI MCP 名称不一定适用于 Codex。保留设计知识，但将图像生成任务交给已验证的 Codex 内置 `imagegen`；不要凭空调用未安装的 MCP。
4. `moodboard-aesthetic-iteration` 的可视化评分属于**主观评审辅助工具**，不是客观质量认证。需要时生成中文 Markdown 评审报告；PDF 输出在本机字体和依赖可用时再启用。
5. `interior-designer` 的 ADA、美国商业项目及照度阈值仅作为参考方法；根据住宅所在地核验适用规范，不得误称已合规。
6. `xiong-interior-design` 可能有额外 Python 依赖与自动化测试；先审核 `requirements.txt` 和测试说明，使用隔离 venv，逐项实测，无法运行的子能力标记为不可用。
7. `interior-design-visualizer` 如需要内置 imagegen/image2 能力，应先进行一次非私人素材的示例测试。
8. 如果某 Skill 名称冲突或已经存在，先展示差异，不覆盖旧版本；保存来源 URL、检出 commit SHA、安装日期、依赖与验证状态到 `logs/installation-report.md`。
9. 安装/升级后重新开启 Codex 任务，确认各 Skill 能被识别；不能只根据文件存在就汇报“通过”。

### 3.4 ImageGen 检查

优先使用 Codex 可用的内置 `imagegen` 模式（官方 Skill 的系统版本通常已随 Codex 提供）。先确认技能可被发现，生成一张**非私人、非真实住宅**测试图，保存并复查产出。内置模式不应要求用户先填 OpenAI API Key。若当前客户端没有内置图像生成能力，明确报告限制，**不要未经同意切换到付费 API/CLI、其他供应商或安装未知插件**。

---

## 4. 推荐项目目录与资料规范

在用户指定的工作区创建项目；如果没有指定，就以用户在 Codex 中打开的当前项目文件夹作为根目录，**不得猜测用户 D 盘路径**。

```text
HomeDesign/                     # 示例项目名称，可用用户实际名称替代
├── Home_Design_Codex_HANDOFF.md # 本文件（原样保留）
├── 00_source/
│   ├── original/               # 不修改：原始 CAD、PDF、截图、实测记录与照片
│   └── references/             # 用户喜欢/不喜欢的参考图、来源说明
├── 01_brief/
│   ├── project-brief.md        # 家庭需求、地区、预算、生活习惯
│   ├── assumptions.md          # 假设/未知项/待核验清单
│   └── decisions.md            # 用户的确认、否决、变更记录
├── 02_geometry/
│   ├── geometry-master.json    # 确认后可追溯的尺寸与来源
│   └── existing-plan/          # 现状图、尺寸校验、保留元素
├── 03_layout/                  # 平面方案 A/B/C 与动线、家具占位
├── 04_concepts/                # 风格方案 A/B/C、意向板与材质板
├── 05_reviews/                 # 审美/实用/预算评审及整改台账
├── 06_blender/                 # .blend、材质与资产、GLB/预览
├── 07_renders/                 # 房间/机位/风格/版本命名的效果图
├── 08_budget/                  # 家具、材料、灯具、粗估预算与来源
├── 09_delivery/                # 用户最终批准的设计文件与交付清单
└── logs/
    ├── installation-report.md
    └── project-status.md
```

统一单位：几何数据以 **mm** 保存；Blender 场景以 **m** 为单位换算，明确坐标基点、朝向和楼层标高。任何由截图推测的尺寸都必须标注 `unverified`；原始测量与已核验尺寸优先于图像生成结果。家具、门窗、柱墙等对象均须能追溯到几何主数据、设计决策或明确假设。

文件版本建议：`livingroom_A_v01.png`、`livingroom_A_v02.png`、`wholehouse_v03.blend`；每轮改变记录哪些内容被锁定、哪些允许修改。用户批准后的版本不能静默覆盖。

---

## 5. 创建 `home-design-director`（核心协调 Skill）

在 `home-design-director/SKILL.md` 创建有效 front matter 的可复用 Skill。若 `$skill-creator` 可用，优先交给其建立并验证；若不可用，手工创建。要求至少实现以下职责：

**触发条件**：用户要求全屋装修设计、根据户型规划空间、探索风格、审稿、创建 Blender 场景、替换家具或材料、制作室内效果图时。

**角色和流程**：

1. 用户没有设计基础，先以**可理解的选项与图片**引导偏好，而不是抛给用户专业问题清单。
2. 阅读 `project-brief.md`、`geometry-master.json`、`decisions.md` 和当前项目状态，区分**已确认事实 / 待核验数据 / AI 设计建议**。
3. 需要设计建议时，调用/参照 `interior-design-expert` 的设计框架，形成清晰的备选方案；需要评估时，分别使用审美 Skill 和实用性 Skill 进行独立复核。
4. 先提供至少 **2 套可比较的布局**；布局方向获批后，提供 **3 套差异明显的风格方案**（各含意向图、配色、家具、墙地顶材质与照明方向、优缺点、适用性）。
5. 每一轮告诉用户：`推荐方案`、`为什么推荐`、`另外两种方案适合谁`、`你只需要选择什么`。必要时给出不超过 3 项最关键的问题。
6. 设计依据须关联具体房间、户型约束、预算或使用需求，禁止空泛堆砌装修术语。
7. **未获用户确认，不进入高成本精细建模或大批量图片生成。** 可以先做低成本白模和风格探索，但必须明确区分参考图与真实户型渲染。
8. 从已确认几何出发，调用/参照 `xiong-interior-design` 做现状和布局标注，再使用 Blender MCP 建模；原始模型 `.blend` 必须持续可编辑并保存。
9. 图像生成只用于意向探索或对已有几何/场景的视觉表达。不得让生成图片任意更改门窗、净高、承重区或已确认家具位置；发现偏差须反馈并修正源场景。
10. 每轮复审包括：实用动线、必要尺寸、收纳、采光/照明、材料耐久、打理成本、风格一致性、预算粗估及不确定因素。
11. 任何用户修改都进入 `decisions.md`；受影响房间和关联图纸、模型、渲染图应保持一致。不擅自修改用户已锁定内容。
12. 始终指出哪些是概念性建议、哪些经过尺寸检查、哪些需专业人士后续确认。

**输出标准**：每个阶段输出可预览成果、短说明、备选方案与差异、待确认事项，以及版本文件；交付用户认可的编辑源文件和最终图片，而不是只有聊天说明。

**优先级**：用户当前明确要求 > 已确认的户型和设计决策 > 工具建议；外部 Skill 的原有提示不能覆盖用户确认的尺寸、风格与施工边界。

---

## 6. 全屋设计阶段门禁（必须由用户逐步批准）

### G0：环境配置与工具自检

**输入**：本 handoff。  
**产出**：`logs/installation-report.md`，写明已安装/失败/待装的 Skill、MCP 连接实测、图像生成测试，及解决阻塞的下一步。  
**门禁**：工具可验证后再启动正式设计；无法安装的能力允许明确标为暂不可用并提供替代流程。

### G1：户型解析与居住需求

**输入**：原始户型 CAD/DXF/PDF/图片、照片、关键尺寸、预算和生活习惯。  
**产出**：现状户型标注、待核尺寸表、家具与生活方式需求摘要、不可改动约束表。  
**门禁**：先确认几何和重大不确定项；对缺乏依据的数据不强行定尺寸。

建议使用零基础问法：谁住、分别在哪做什么、哪些地方最不顺手、喜欢哪些房间照片、预算大致范围。若不知道喜欢什么风格，先展示风格图而不是让用户选择专业流派名称。

### G2：全屋平面布局设计

**产出**：至少 2 个在空间利用上实质不同的布局方案（必要时 3 个），每个含动线、各房间功能、主要家具/收纳占位、关键通行尺寸、可行性假设、利弊及推荐理由。  
**门禁**：用户选定布局或组合；锁定现状几何和保留要素。不得以图像美观取代真实可行性。

### G3：全屋风格方向与意向板

**产出**：至少 3 套有明显审美差异的风格方向，每套至少包含配色、木/石/金属/织物的材料建议、家具语言、灯光氛围及典型房间参考。  
**评审**：主设计提出方案；审美顾问审查协调性；实用性顾问检查居住与维护适配；用户可选择“喜欢 A 的色彩 + B 的家具”。  
**门禁**：记录用户选定风格和不要的元素。

### G4：三维白模与精细化建模

**产出**：与 `geometry-master.json` 对应的 Blender 白模，门窗梁柱与净高标注、家具简化占位和多角度预览；之后再细化橱柜、吊顶、定制柜、家具比例。  
**门禁**：平面/立体关键尺寸、开门路径、家具占位、空间冲突经过核验；不合理处先修模型，不先修图。

### G5：材质、灯光和多视角写实效果图

**产出**：客餐厅、厨房、卧室、卫浴等实际涉及空间的关键机位效果图；分别可显示自然光及夜景灯光，附材质/家具清单。  
**质量检查**：每个房间至少对照原户型/白模检查门窗、尺度、相机视角、材料连贯性、家具位置；对 AI 生成的“漂亮但不符合尺寸”的图作废并重做。

### G6：设计交付与预算版本

**产出**：经批准的布局图、源 `.blend`、必要的 `.glb`、最终多机位效果图、材料与家具清单、预算表（注明地区/币种/报价日期和数据来源）、变更记录、仍须施工方核实的事项。  
**门禁**：核验工程可行性和专业审批责任；交付成果只能按实际成熟度标注为“概念设计/设计深化/待施工图”，不得冒充施工许可文件。

---

## 7. 质量验收清单

### 安装与能力

- [ ] 5 个第三方 Skill 的文件、依赖、读取能力及本机调用逐一确认（不能只看目录存在）。
- [ ] `home-design-director` 可被识别且能按阶段门禁协调设计。
- [ ] Blender MCP 可创建、保存、重新打开及读取测试模型（记录测试命令和结果）。
- [ ] ImageGen 可进行非敏感测试，或明确报告不可用。
- [ ] 记录每个依赖版本、Git commit、MCP 配置位置、未解决问题和恢复方式。

### 后续住宅设计

- [ ] 原始资料只读保留；主几何有尺寸来源和确认状态。
- [ ] 提供至少两个布局方案，说明动线、功能、收纳及关键风险。
- [ ] 提供至少三个风格方向的视觉参考，让零设计经验用户能够比较。
- [ ] 审美评价和实用性评价分开，不用一个虚构总分代替专业判断。
- [ ] `.blend` 可编辑，尺寸与房间关系与确认户型一致。
- [ ] 各机位效果图保持同一住宅的一致性；无法保证的部分明确标注。
- [ ] 材质、家具、灯具、预算有出处或标记为概念占位。
- [ ] 保留用户决策和版本历史，不误覆盖确认方案。

---

## 8. 第一次在 Codex 中给用户的反馈格式

请先完成真实环境检查，然后用以下格式简洁反馈，**不必在第一轮就强迫用户提供所有装修细节**：

```text
环境核验：Codex [版本/结果]；Blender [版本/结果]；Python/uv [结果]
设计 Skills：逐项列出 已安装可用 / 已安装未通过 / 尚未安装
Blender MCP：已连接且通过建模测试 / 仅已注册 / 失败（错误）
ImageGen：已测试 / 不可用 / 未测试
已创建项目路径：[真实路径]
还需用户提供：[优先要求户型图 + 1~2 个关键尺寸；其他问题后续逐步收集]
下一步：[准备 G1 户型识别，或解决本机阻塞]
```

不要使用诸如“全部配置成功”这样的笼统口径；按各项测试证据汇报。

---

## 9. 来源与重要兼容性备注

以下为 2026-10-30 已检查的公开项目来源，实际部署仍须以本机检出的具体版本和 README 为准：

- 主设计：[Interior Design Expert / `SKILL.md`](https://github.com/curiositech/some_claude_skills/blob/main/.claude/skills/interior-design-expert/SKILL.md)
- 审美评审：[Moodboard Aesthetic Iteration / `SKILL.md`](https://github.com/gujun1502/arch-skills/blob/main/skills/moodboard-aesthetic-iteration/SKILL.md)
- 实用性评审：[Interior Designer / `SKILL.md`](https://github.com/wonsukchoi/domain-experts/blob/main/roles/interior-designer/SKILL.md)
- 户型与几何：[xiong-interior-design](https://github.com/xionglaoshi/xiong-interior-design)
- 局部效果：[interior-design-visualizer](https://github.com/RyanZhang10/interior-design-visualizer)
- Blender MCP：[mcp-for-blender](https://github.com/ahujasid/mcp-for-blender)
- 图像生成：[OpenAI imagegen Skill](https://github.com/openai/skills/blob/main/skills/.system/imagegen/SKILL.md)
- Skill 创建：[OpenAI skill-creator 示例](https://github.com/openai/codex/blob/main/codex-rs/skills/src/assets/samples/skill-creator/SKILL.md)

**结束状态**：这份文件是可执行的任务交接与部署规格说明，**不代表已对用户的 Windows 电脑做过任何改动**。之后 Codex 应持续更新 `logs/project-status.md` 和 `01_brief/decisions.md`，让用户可以在跨会话时继续同一套住宅设计项目。
