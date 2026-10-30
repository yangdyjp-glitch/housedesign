"""Preserve the existing project and import the user's latest interactive layout."""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json, shutil

ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT.parent/'outputs'/'house-structure'
HANDOFF=Path(r'C:\Users\Administrator\Documents\WeChat Files\ArcherYang\FileStorage\File\2026-10\Home_Design_Codex_HANDOFF.md')
DIRS=['00_source/original','00_source/references','01_brief','02_geometry/existing-plan',
      '03_layout','04_concepts','05_reviews','06_blender','07_renders','08_budget',
      '09_delivery','logs/vendor-audit/skills','logs/downloads','tools/runtime']
for name in DIRS:(ROOT/name).mkdir(parents=True,exist_ok=True)

def new_text(path,content):
    if not path.exists():path.write_text(content,encoding='utf-8')

def new_json(path,value):new_text(path,json.dumps(value,ensure_ascii=False,indent=2)+'\n')

def preserve(src,dst):
    if src.is_file() and not dst.exists():shutil.copy2(src,dst)
    return dst.is_file()

preserve(HANDOFF,ROOT/HANDOFF.name)
baseline=json.loads((OLD/'house-model.json').read_text(encoding='utf-8'))
preserve(OLD/'house-model.json',ROOT/'02_geometry/geometry-baseline-v04.json')
for name in ['house-plan.svg','house-plan.dxf','模型说明.txt']:
    preserve(OLD/name,ROOT/'02_geometry/existing-plan'/name)
for name in ['house-structure.glb','house-structure.obj','house-structure.mtl']:
    preserve(OLD/name,ROOT/'06_blender'/('baseline-v04-'+name))
for name in ['house-view.template.html','build_model.py','furnish_model.py']:
    preserve(OLD/name,ROOT/'00_source/references'/name)

sources=[Path(r'C:\Users\Administrator\Desktop\房型.jpg'),
 Path(r'C:\Users\ADMINI~1\AppData\Local\Temp\codex-clipboard-9cd2d453-b333-4021-b37e-41631362d66d.png'),
 Path(r'C:\Users\ADMINI~1\AppData\Local\Temp\codex-clipboard-df1537cd-add6-4258-8426-21e02c517ef3.png'),
 Path(r'C:\Users\ADMINI~1\AppData\Local\Temp\codex-clipboard-dd3840b3-08e9-4dcc-bd35-cda470532299.png')]
source_report=[]
for src in sources:
    dst=ROOT/'00_source/original'/src.name
    available=preserve(src,dst)
    source_report.append(dict(original=str(src),copy=str(dst) if available else None,available=available,
       sha256=hashlib.sha256(dst.read_bytes()).hexdigest() if available else None))
new_json(ROOT/'00_source/references/source-manifest.json',source_report)

offsets={
 'tv-low':[0,0],'tv-high':[0,0],'television':[0,0],
 'sofa-modular':[1000,-400],'ottoman':[1000,300],'side-table':[800,100],
 'double-desk':[1300,-300],'office-chair-1':[1100,-300],'office-chair-2':[1100,-400],
 'bookcase':[0,0],'dining-table':[0,0],'dining-chair-1':[0,100],'dining-chair-2':[0,0]}
positions=[dict(id=q['id'],x=q['x']+offsets[q['id']][0],z=q['z']+offsets[q['id']][1],
                dx=offsets[q['id']][0],dz=offsets[q['id']][1]) for q in baseline['furnitureObjects']]
new_json(ROOT/'03_layout/widget-layout-v04-latest.json',dict(source='latest user-operated widget state from this conversation',
    modelRevision=4,view='plan',moveStepMm=100,furniturePositions=positions,
    selectedSchemes=baseline['features']['furnishing']['selectedSchemes']))

master=copy.deepcopy(baseline)
for q in master['furnitureObjects']:
    dx,dz=offsets[q['id']];q['x']+=dx;q['z']+=dz
    q['placement_source']='03_layout/widget-layout-v04-latest.json'
for q in master['furniture']:
    dx,dz=offsets[q['parent']];q['x']+=dx;q['z']+=dz
master['revision']=5
master['project_revision']='v05-ui-layout-import'
master['provenance']=dict(baseline='02_geometry/geometry-baseline-v04.json',layout='03_layout/widget-layout-v04-latest.json',
  geometry_units='mm',blender_units='m',blender_axis_mapping='(plan x, -plan z, height) -> (Blender X, Blender Y, Blender Z); mm / 1000',
  geographic_orientation='unknown; -Y follows downward direction in the source plan, keeping top views unmirrored',
  imported_at=datetime.now(timezone.utc).isoformat(),dimension_status='unverified sketch reconstruction; not a closed measured CAD')
master['features']['furnishing']['layoutEdited']=True
master['features']['furnishing']['initialClearances']=master['features']['furnishing'].pop('clearances')
chairs=[q for q in master['furniture'] if q['parent'].startswith('office-chair')]
book=next(q for q in master['furnitureObjects'] if q['id']=='bookcase')
chair_edge=max(q['x']+q['w'] for q in chairs)
master['features']['furnishing']['currentReview']=dict(officeChairEastEdgeMm=chair_edge,bookcaseFrontMm=book['x'],
  localGapMm=book['x']-chair_edge,status='needs layout review; do not alter user placement automatically')
new_json(ROOT/'02_geometry/geometry-master.json',master)
new_json(ROOT/'02_geometry/geometry-master-v05.json',master)

new_text(ROOT/'01_brief/project-brief.md','''# 住宅设计项目概要

用户已授权按交接文件搭建设计环境，并接入现有模型。语言：中文；使用平台：Windows 本机 Codex。

## 已有资料与范围

- 已有手绘测量图、三张位置/功能标注图、毫米几何数据、13件简化家具、GLB/OBJ/DXF/SVG 和100 mm交互布局。
- 当前只深化客厅、办公区、电视柜、书柜和餐厅；用户此前要求其他区域先不考虑，搭建设计系统不自动扩大本阶段装修范围。
- 房间功能已确认：下凸区厨房、连通空间客厅、右上主卧、右侧小间主卫、右下次卧、下排中间客卧；下排左上和左下同属客卫。
- 已选组合：红A低柜及端高柜；蓝B模块沙发及脚凳；绿B双人桌；黄A两端高柜与中部书架；黑B餐桌取消卡座，长边靠墙。
- 办公桌在沙发后，座位朝电视。最近7件家具的手动移动已另存版本并导入主几何。

## 待确认

地区与适用规范、家庭成员与生活习惯、预算/币种、净高实测、承重与机电条件、风格、期限。已有户型资料不要求重复提供。
''')
new_text(ROOT/'01_brief/assumptions.md','''# 假设与待核验

- 墙高2750 mm、外墙240 mm、内墙120–168 mm为建模暂定值，不代表承重判断。
- 左侧总长拟合9635 mm与手写11089 mm不闭合；主卫净宽与横墙2040 mm标注有冲突；保留原识读记录。
- 阳台为落地窗；主卧凸出部分为飘窗，凸出500 mm，窗台高500 mm暂定。
- 三段红圈墙仅从数字模型删除，不能据此确认现场允许拆除。
- 家具尺寸与浅木/暖白/灰米色材质为方案占位。新布局来源为用户在交互模型中的操作，不等同于已完成动线审批。
- 更新后的办公椅最右外缘与书柜间局部净空约408 mm，需在后续布局评审中核对。保持用户位置，不自行回退。
- 不将旧版本的1100 mm座椅活动区及1088 mm通道继续当作最新布局实测值。
''')
new_text(ROOT/'01_brief/decisions.md','''# 用户决策记录

| 日期 | 决策 | 适用范围 |
|---|---|---|
| 2026-10-30 | 删除红圈竖墙、上端短墙、下端横墙，保留右侧分隔墙 | 数字模型 |
| 2026-10-30 | 确认全部房间用途，阳台落地窗、主卧飘窗，红框横墙室内侧对齐 | 现状模型 |
| 2026-10-30 | 仅讨论五个标色区域，其他区域先不考虑 | 当前设计范围 |
| 2026-10-30 | 办公桌在沙发后，使用者面向电视 | 布局约束 |
| 2026-10-30 | 红A、蓝B、绿B、黄A、黑B；取消卡座，餐桌直接靠墙 | 已选家具组合 |
| 2026-10-30 | 所有新增家具可点击移动，100 mm步进 | 交互模型 |
| 2026-10-30 | 用户手动移动7件家具，保留最新widget快照 | 03_layout/widget-layout-v04-latest.json |
| 2026-10-30 | 按交接文件搭建环境，并接入现有模型 | 本次授权 |

后续不得静默覆盖本版本；尺寸未核验、局部通道待评审不等于用户撤销上述选择。
''')
new_text(ROOT/'logs/project-status.md','''# 项目状态

阶段：G0 设计环境搭建进行中；已有G1/G2局部资料与G4简化模型，不从空白重建。

- 原交接文件已原样保留，已有来源与几何基线已留档。
- 用户最新100 mm移动位置已接入 geometry-master.json，暂存为v05。
- 目标：审核并安装5个设计技能，建立协调技能，验证Blender MCP，生成可编辑Blender白模。
- 工具安装、MCP握手、保存重开与图像生成测试结果以 installation-report.md 和实际测试日志为准。
- 真实住宅其他区域暂不新增家具；不开展未确认的高成本精细建模或批量效果图。
''')
print(json.dumps(dict(project=str(ROOT),furnitureObjects=len(master['furnitureObjects']),
    movedObjects=sum(any(v) for v in offsets.values()),localOfficeGapMm=book['x']-chair_edge,
    originalImagesAvailable=sum(q['available'] for q in source_report)),ensure_ascii=True))
