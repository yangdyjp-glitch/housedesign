"""Draw a dimensional concept comparison, without changing any model boundaries."""
from pathlib import Path
from html import escape
import json
ROOT=Path(r'D:\AI-Yang.cn\HomeDesign');OUT=ROOT/'09_delivery';OUT.mkdir(exist_ok=True)
W,H=1600,1270
parts=[f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs><pattern id="wet" width="12" height="12" patternUnits="userSpaceOnUse"><path d="M0 12L12 0" stroke="#d8e3e2" stroke-width="1"/></pattern>
<marker id="arrow" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto-start-reverse"><path d="M1 1L7 4L1 7" fill="none" stroke="#536e66" stroke-width="1.3"/></marker></defs>
<rect width="1600" height="1270" fill="#faf9f5"/>
<g font-family="Microsoft YaHei, sans-serif" fill="#303b36">
<text x="64" y="64" font-size="34" font-weight="500">主卫门位研究 · 保留现有湿区边界</text>
<text x="64" y="104" font-size="21" fill="#657069">两案均为条件性示意。主卧按 2.0 m 床垫研究；未确定洁具、排水或墙体可改性。</text>
<path d="M800 150V1120" stroke="#dedfd8"/>
''']
def text(x,y,label,size=21,fill='#303b36',anchor='start'):
    parts.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}">{escape(label)}</text>')
def panel(left,scheme):
    scale=.143;ox=left+80;oy=235
    def pt(x,y):return ox+x*scale,oy+y*scale
    def rect(x,y,w,h,fill,stroke=None,dash=False,width=2):
        px,py=pt(x,y);parts.append(f'<rect x="{px:.2f}" y="{py:.2f}" width="{w*scale:.2f}" height="{h*scale:.2f}" fill="{fill}"'+(f' stroke="{stroke}" stroke-width="{width}"' if stroke else '')+(' stroke-dasharray="8 6"' if dash else '')+'/>')
    def line(x1,y1,x2,y2,color='#717a73',width=2,dash=False,arrow=False):
        a,b=pt(x1,y1);c,d=pt(x2,y2);parts.append(f'<path d="M{a:.2f} {b:.2f}L{c:.2f} {d:.2f}" fill="none" stroke="{color}" stroke-width="{width}"'+(' stroke-dasharray="7 5"' if dash else '')+(' marker-end="url(#arrow)"' if arrow else '')+'/>')
    def label(x,y,t,size=20,color='#303b36',anchor='middle'):
        px,py=pt(x,y);text(px,py,t,size,color,anchor)
    text(left+64,168,'A  原洞口＋卧室侧明装移门' if scheme=='A' else 'B  条件允许时，小幅向左移门',26)
    text(left+64,202,'先研究门扇停车，不做墙内暗藏口袋。' if scheme=='A' else '需核实墙体、门头和改口条件。',20,'#657069')
    rect(0,0,3467,3704,'#f0ece2')
    rect(1995,3824,1472,2014,'#e7efed')
    rect(1995,3824,1472,2014,'url(#wet)')
    # Current wall references are retained; only B's opening is a dashed research idea.
    for a,b in [((0,0),(3467,0)),((0,0),(0,3704)),((3467,0),(3467,5838)),((1995,3824),(1995,5838)),((1995,5838),(3467,5838)),((0,3764),(42,3764)),((908,3764),(1995,3764))]:line(*a,*b,width=7)
    opening=(2396,3288) if scheme=='A' else (2075,2875)
    line(1995,3764,opening[0],3764,width=7)
    line(opening[1],3764,3467,3764,width=7)
    line(3467,4053,3467,4922,'#8ba8b2',7)
    label(3650,4470,'窗',19,'#58737d')
    # Dashed bed/wardrobe envelopes are clearance studies, not new selected furniture.
    rect(1317,700,2150,2150,'#e0e5da','#7c8c74',True)
    rect(0,100,600,2700,'#e9e5db','#9d9b8e',True)
    label(2392,1630,'2.0 m 床垫',23)
    label(2392,1850,'床架暂按 2150 × 2150',17,'#657069')
    label(300,1400,'衣柜',18)
    label(300,1620,'深600',17,'#657069')
    label(1730,330,'主卧 3467 × 3704*',22)
    label(2700,4680,'主卫',25)
    label(2700,4930,'1472 × 2014*',21)
    label(2700,5230,'洁具位置按排水再排',18,'#657069')
    label(1730,3300,'床尾侧局部净距约 717*',18,'#657069')
    line(600,2200,1317,2200,'#8c978a',1.5)
    label(956,2060,'717*',18)
    label(475,4050,'主卧入口沿用',17,'#657069')
    if scheme=='A':
        rect(1504,3638,892,35,'#cad9d0','#536e66',False,2)
        line(3180,3530,1740,3530,'#536e66',2,False,True)
        line(2396,3764,3288,3764,'#a5b4ad',2,True)
        label(1670,4380,'门扇向左停车',18,'#536e66','end')
        label(1670,4590,'检查床边柜／开关',17,'#657069','end')
        line(1770,4190,1940,3660,'#9ba49d',1.5)
    else:
        line(2075,3764,2875,3764,'#bd8759',4,True)
        line(2396,3885,3288,3885,'#a7aaa0',1.5,True)
        label(1540,4380,'虚线：拟研究新洞口',18,'#956f49','end')
        label(1540,4590,'宽800*，向左约321*',17,'#657069','end')
        line(1640,4190,2170,3764,'#a89b86',1.5)
        label(3171,4100,'592*',18,'#956f49')
        label(3171,4290,'右侧墙段',16,'#657069')
    notes=(['取舍：原洞口保留，门扇可减少占用卫浴内部。','仍需核对移门密封、隐私、停车和床边活动。'] if scheme=='A' else ['取舍：门位左移后，右侧可多留一段连续墙。','尚不能据此确定台盆、马桶和淋浴可同时放下。'])
    for i,t in enumerate(notes):text(left+64,1110+i*34,t,20,'#53615a')
panel(0,'A');panel(800,'B')
text(64,1212,'* 均为当前模型／试排值。主卫宽度与原图2040相关标注冲突，待复尺；本图未回写主卫或主卧边界。',20,'#657069')
parts.append('</g></svg>')
path=OUT/'v10主卫门位研究.svg';path.write_text(''.join(parts),encoding='utf-8')
record=json.loads((ROOT/'01_brief/master-bath-feasibility-v10.json').read_text(encoding='utf-8'))
record.update(diagram=path.relative_to(ROOT).as_posix(),bed_wardrobe_trial_clearance_mm=717,diagram_status='door concepts only; no chosen fixture plan; no main model private-room edits')
(ROOT/'01_brief/master-bath-feasibility-v10.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('BATH_STUDY_DRAWN',str(path))
