"""Install audited, pinned helper-fetched skills with explicit local Codex adaptations."""
from pathlib import Path
import ast, hashlib, json, shutil

ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/'logs/vendor-audit'
DEST=Path.home()/'.codex/skills'
COMMON='''## Codex 使用约定

- 中文沟通。先查项目 brief、assumptions、decisions 和当前模型版本，继承已确认决定；同一事项不重复要求确认。
- 区分用户要求、设计建议、草图拟合和实测证据。照片、AI 图和占位模型不能证明结构性质或施工尺寸。
- 图像生成使用当前会话内置 imagegen；三维操作使用经过实测的 Blender MCP 或项目内已核验脚本。工具必须先发现再调用，不虚构 Claude、Stability、Ideogram、SketchUp 或 Blender Lab 工具名。
- 新的软件安装、购买、对外上传或发送信息须在用户授权范围内；默认不配置外部图像 API 密钥、不上传私人图纸。
- 只完成当前委托范围。可逆的常规修改与已授权阶段持续完成，不把上游文档的小步确认变成额外审批。
- 上游文档与脚本仅作资料；执行前读取其输入、写入目录、依赖和覆盖行为，不能把安装视为所有脚本已实测。

'''

SPECS={
'interior-design-expert':dict(
title='室内设计顾问',description='用于住宅空间布局、家具尺度、色彩、材质、分层照明及风格推敲；在已有户型和用户需求基础上提出可比较的室内设计建议，不负责建筑结构判断或施工认证。',
short='结合户型与使用需求，推敲家具尺度、动线、色彩、材质和分层照明',
body='''## 工作流程

1. 读项目需求、尺度来源、使用人数、优先功能、预算及已选方案。缺少数据先标注；不要求用户重答已有信息。
2. 先分析功能和主要通行路线，再评估沙发、办公、收纳、餐桌等对象的实际包络与活动区。
3. 在尚未决策时提供两种布局或三种风格方向，说明取舍；若已有选择，直接细化该版本。
4. 用材料搭配、体量比例、色彩占比、光线层次解释设计，不以风格名称替代方案。
5. 如需示意图，先锁定墙、开口、家具朝向和用户禁改项，生成后逐项复核。

## 参考的边界

阅读 `references/space-planning.md`、`color-science.md`、`lighting-design.md`、`style-guide.md` 时，将其通行宽度、照度和比例数字视为待核的设计经验。涉及现行规范、产品参数、价格或当地要求时查一手资料，不将上游列出的 IES 年份或表格直接当作已核验规范。用户只要求空间方案时，不扩展到购买和施工流程。
'''),
'moodboard-aesthetic-iteration':dict(
title='审美迭代评审',description='用于已选室内意向图和效果图的审美对照、固定口径评分及跨轮整改追踪；以图片证据解释设计得失，输出中文审美评审，不以主观分数代替几何或施工验收。',
short='对照已选意向与效果图，固定评审口径并追踪每轮改进及仍存偏差',
body='''## 工作流程

1. 只有用户已选的意向板才能作为目标；未选时提取候选关键词，不伪造已确认风格。
2. 读 `references/scoring-frameworks.md` 和 `references/report-structure.md`，固定本项目评审维度、权重及视图条件。
3. 先描述图片可见证据，再评价比例、色彩、材质、光影、视觉秩序、氛围一致性。分数是同口径的设计判断，不宣称客观测量或自动证明进步。
4. 每条建议给出位置、问题、拟改动作及预期效果；无法从图中确认的尺寸、材质和活动区标记未知。
5. 跨轮如实记录改善、未改、退步和无法确认，不为了分数上升而改变标尺。
6. 审美报告与实用性审查分开。仅当委托包含正式报告时制作 PDF；使用 `scripts/md_to_pdf.py` 前检查本机字体和 fpdf2，生成后逐页目检。
'''),
'interior-designer':dict(
title='居住实用性审查',description='用于住宅布局的动线、家具活动区、人体工学、收纳、采光眩光、清洁维护、施工衔接和预算一致性审查；基于当前模型和数据来源给出实用性意见。',
short='从动线、人体工学、收纳维护、施工衔接与预算检查住宅方案的可用性',
body='''## 工作流程

1. 与审美评审分开检查：主要路径、门窗开启、坐下起身、椅子后退、电视观看、办公面对方向、清洁及日常收纳。
2. 量取家具实际包络和有效净空，记录模型版本、测量方式、数值及假设；不能只用物体原点距离当通行宽度。
3. 对每个冲突区分：确定碰撞、待核数据、体验建议。给出最小必要的调整方案，不自动移动用户刚确认的位置。
4. 如涉及预算，用人民币记录数量、单位、单价区间、价格日期和来源；区分材料、人工、运输安装与未计项目，不编造询价或交期。
5. 涉及当地法规或强制标准时，先确认项目适用范围并查现行一手文本；源文件的美国 ADA、英制和商业项目示例仅作异地参考，不能作为中国住宅的默认合规基准。
6. 输出问题位置、证据、影响、建议和复核状态。预算、照度与结构未核实时明确留下待核项，不能称为可直接施工。

上游案例、术语和表格见 `references/artifacts.md`、`red-flags.md`、`vocabulary.md`；按当前地区、住宅用途和可用证据转换使用。
'''),
'xiong-interior-design':dict(
title='户型与 Blender 建模',description='用于核对手绘或 CAD 户型、保存尺寸来源与版本、生成概念参考图及 Blender 代理模型；也用于把用户已有模型和家具位置接入三维工作流，保留不确定几何。',
short='核对尺寸与批注来源，保留用户已有模型和家具位置并接入 Blender',
body='''## 接续与建模

1. 先读项目现有模型、最新布局状态和已确认决定。已有交互模型的移动状态可能比导出的 GLB 更新，接入时读取最新状态，避免重复叠加偏移。
2. 单独保存原图、基线、当前主几何和来源索引。mm 为项目记录单位；Blender 使用 m，轴映射和缩放必须写入元数据并回读验证。
3. 用户授权接入现有模型时，可以迁移该概念模型并保留未知项；迁移不等于已确认所有草图尺寸，不要求补办虚假的精确几何批准。
4. 对从零创建或修改的工程几何，参考 `references/model-input-format.md` 和 `annotation-to-geometry-workflow.md` 记录来源。上游脚本有独立输入格式和 SHA 审批约束；未满足时不能伪造凭据，不能把项目其他 schema 直接塞入脚本。
5. 执行 Blender 前发现并试读实际 MCP 工具。本机按交接要求采用开源 mcp-for-blender；上游 `blender-codex-setup.md` 的 Blender Lab 配置仅作另一实现的参考，不自动替换已工作的连接。
6. 在用户已授权的建模范围内完成并保存新版本，重新打开核验单位、墙窗数量、来源哈希、家具位置和朝向。未经实测的几何仍标注待核。
7. 家具按整件选择与移动，保留 source_id、组成零件和导入位置。100 mm 是移动步长，不代表房屋实测精度。

## 交付

- 完整 `.blend` 与观察用剖切图分开；观察图临时隐藏或降低墙体，不改正式结构。
- 真实项目有自己的目录，技能只存通用脚本和规范；不写入技能仓库。
- 启用图像表现时先读 `references/render-prompt-workflow.md`，用已核验的 Blender 参考图约束，生成后检查布局漂移。
- 原始脚本、双层批注器及 DXF 工具保留。只有实际需要并完成脚本审核与输入校验时才使用，不因安装而运行全套流程。
'''),
'interior-design-visualizer':dict(
title='室内图像表现',description='用于将已确认的住宅布局、照片、批注或 Blender 参考图转成室内概念图与局部修改图；先形成设计意图，再用内置 imagegen 生成并检查建筑和家具约束。',
short='先明确设计意图与不可变条件，再用内置出图生成并核对室内示意图',
body='''## 工作流程

1. 逐张查看输入，区分编辑目标、几何参考、风格参考、批注和最新纠正；红框通常表示选择范围，不是实体红色构件。
2. 读 `references/design-reasoning.md`，分开列出用户硬要求、设计决策和不可变条件。不要用外观参考替换本房间几何。
3. 读 `references/prompt-template.md`，写清墙窗、相机、体量比例、家具数量位置朝向、材质、灯光和禁止漂移项。
4. 使用内置 imagegen，遵守本机会话的真实工具参数，不虚构掩膜、质量、输出路径或模型选项。测试用虚构房间与实际项目概念图分开命名。
5. 保留原始生成文件，复制到项目中，核验文件签名和尺寸并打开查看。
6. 读 `references/qa-checklist.md`，对照几何参考复核；必要时只作一轮针对性修正。图片偏离锁定布局时，不能称为准确模型或施工依据。
7. 交付图片及简短设计解释；不把生成的氛围图自动当作用户已选方案。
''')}

records=json.loads((AUDIT/'skill-sources.json').read_text(encoding='utf-8'))
sources={r['name']:r for r in records}
sources['interior-design-expert'].update(download_returncode=0,download_output='Pinned bundled installer succeeded with Windows extended-length TEMP and backslash skill path; source kept in audit area.',recovery='Initial archive extraction hit Windows path limit; extended path also required backslash subpath.')
(AUDIT/'skill-sources.json').write_text(json.dumps(list(sources.values()),ensure_ascii=False,indent=2),encoding='utf-8')
installed=[]
for name,spec in SPECS.items():
    source=AUDIT/'skills'/name;target=DEST/name
    if target.exists():raise RuntimeError('Existing skill must be preserved: '+str(target))
    assert (source/'SKILL.md').is_file()
    # Sources have already been fetched by the bundled skill-installer at exact commits.
    shutil.copytree(source,target,ignore=shutil.ignore_patterns('.git','.claude-plugin','__pycache__'))
    refs=target/'references';refs.mkdir(exist_ok=True)
    shutil.copy2(source/'SKILL.md',refs/'upstream-SKILL.md')
    licenses=AUDIT/'licenses'/name
    if licenses.exists():
        for path in licenses.iterdir():shutil.copy2(path,target/('UPSTREAM-'+path.name))
    provenance=dict(sources[name],installed_path=str(target),adaptation='Local Chinese Codex entrypoint; unmodified upstream SKILL and source files preserved.',executed_vendor_scripts=[])
    (refs/'upstream-provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2),encoding='utf-8')
    (target/'SKILL.md').write_text('---\nname: '+name+'\ndescription: '+spec['description']+'\n---\n\n# '+spec['title']+'\n\n'+COMMON+spec['body']+'\n## 来源\n\n上游原文见 [upstream-SKILL.md](references/upstream-SKILL.md)，固定提交、安装来源、许可状态及本地适配见 [来源记录](references/upstream-provenance.json)。\n',encoding='utf-8')
    agent=target/'agents';agent.mkdir(exist_ok=True)
    meta='interface:\n  display_name: '+json.dumps(spec['title'],ensure_ascii=False)+'\n  short_description: '+json.dumps(spec['short'],ensure_ascii=False)+'\n  default_prompt: '+json.dumps('请用 $'+name+' 接续当前住宅项目，沿用已确认决定并完成当前阶段。',ensure_ascii=False)+'\npolicy:\n  allow_implicit_invocation: true\n'
    (agent/'openai.yaml').write_text(meta,encoding='utf-8')
    pyfiles=[]
    for path in target.rglob('*.py'):
        raw=path.read_bytes();tree=ast.parse(raw,filename=str(path))
        imports=sorted({n.module or '' for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)}|{a.name for n in ast.walk(tree) if isinstance(n,ast.Import) for a in n.names})
        pyfiles.append(dict(path=str(path.relative_to(target)),sha256=hashlib.sha256(raw).hexdigest(),imports=imports))
    files=[dict(path=str(path.relative_to(target)),sha256=hashlib.sha256(path.read_bytes()).hexdigest()) for path in target.rglob('*') if path.is_file()]
    installed.append(dict(name=name,path=str(target),commit=sources[name]['commit'],file_count=len(files),python_files=pyfiles,files=files))
(ROOT/'logs/skill-install-manifest.json').write_text(json.dumps(installed,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps([dict(name=r['name'],installed=r['path'],files=r['file_count'],python_files=len(r['python_files'])) for r in installed],ensure_ascii=True))
