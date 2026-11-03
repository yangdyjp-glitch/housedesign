"""Measured schematic of the requested co-planar corridor wall and door conflict."""
from pathlib import Path
import json,shutil,math
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'09_delivery/v17-alignment-study';OUT.mkdir(parents=True,exist_ok=True)
shutil.copy2(Path('C:/Users/Administrator/AppData/Local/Temp/codex-clipboard-d2b13355-4992-4e24-93d1-1ee0b13d115d.png'),ROOT/'00_sources/wall-alignment-markup-v17.png')
im=Image.new('RGB',(1500,760),'#f7f5ef');dr=ImageDraw.Draw(im);font=lambda n:ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',n)
dr.text((30,15),'以书柜墙为基准：主卫前墙收回200 mm',font=font(29),fill='#273a33')
def panel(offset,title,variant):
    ox,oy=offset,105;scale=.16
    def p(x,z):return(ox+(x-6700)*scale,oy+(z-3400)*scale)
    def box(x,z,w,d,fill):dr.rectangle([p(x,z),p(x+w,z+d)],fill=fill)
    def line(a,b,c,width=4):dr.line([p(*a),p(*b)],fill=c,width=width)
    dr.text((offset+5,68),title,font=font(23),fill='#273a33')
    box(6916,3400,272,1376,'#a5aaa7');box(6838,3400,350,1376,'#e5c9aa');box(6916,4776,454,120,'#7f8580')
    box(8645,3400,2150,576,'#e1e5df');box(8645,3976,2150,120,'#868e87')
    box(10795,3400,240,2000,'#7f8580');box(9203,4936,120,464,'#7f8580')
    box(8236,4776,120,120,'#6c8c77');box(8236,4776,1087,120,'#6c8c77')
    for x in range(6916,10500,100):line((x,4896),(x+50,4896),'#386f52',2)
    if variant=='conflict':
        box(8236,4976,1087,120,'#e4b6af');box(9203,4096,120,40,'#7f8580')
        line((9223,4156),(9223,4916),'#bb493b',6)
        dr.text(p(9450,4330),'原侧门800',font=font(20),fill='#aa3d35')
        dr.text(p(8350,5170),'旧墙凸出200',font=font(20),fill='#aa3d35')
        dr.text(p(8360,4690),'新墙',font=font(19),fill='#386f52')
        dr.text(p(9270,4800),'相碰',font=font(18),fill='#aa3d35')
    elif variant=='diagonal':
        h=(9203,4210.315);end=(8637.315,4776)
        box(9203,4096,120,114.315,'#7f8580')
        line(h,end,'#386f52',6)
        dr.text(p(8950,4480),'斜角门800',font=font(19),fill='#386f52')
        dr.text(p(8500,5150),'床与柜位置保留',font=font(19),fill='#273a33')
    dr.text(p(6790,4380),'书柜',font=font(20),fill='#614e3c')
    dr.text(p(8470,3520),'床头北侧隔墙',font=font(20),fill='#273a33')
    dr.text(p(9800,5000),'主卫',font=font(23),fill='#273a33')
    dr.text(p(7220,5300),'走廊',font=font(23),fill='#273a33')
panel(30,'对齐后的冲突位置','conflict');panel(790,'可选处理：保留门宽和床位','diagonal')
dr.text((30,625),'基准为两段墙朝走廊一侧的外表面：z = 4896 mm；墙厚120 mm。',font=font(23),fill='#273a33')
dr.text((30,668),'直侧门处净墙段仅680 mm，原800 mm门洞加两端墙垛无法原位容纳。',font=font(23),fill='#6b514c')
dr.text((30,714),'示意来自当前模型，斜角门为未选提案；现场尺寸与构造待核。',font=font(19),fill='#6b736e')
im.save(OUT/'对齐与门口关系.png');print('V17_ALIGNMENT_STUDY_READY')
