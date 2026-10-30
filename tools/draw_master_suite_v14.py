"""Dimensioned plan derived from v14 geometry; not a photograph or site survey."""
from pathlib import Path
import json,math
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'09_delivery/v14-master-suite';OUT.mkdir(parents=True,exist_ok=True)
d=json.loads((ROOT/'02_geometry/geometry-master-v14.json').read_text(encoding='utf-8'))
im=Image.new('RGB',(1600,1800),'#FAFAF7');draw=ImageDraw.Draw(im)
fontpath='C:/Windows/Fonts/msyh.ttc'
def font(n):return ImageFont.truetype(fontpath,n)
def text(x,y,s,n=28,fill='#343D36',anchor='mm'):draw.text((x,y),s,font=font(n),fill=fill,anchor=anchor)
scale=.205;ox=220;oy=360
def pt(x,z):return (ox+(x-7188)*scale,oy+(z-1072)*scale)
def rect(x,z,w,h,fill,outline=None,rad=0):
    a,b=pt(x,z),pt(x+w,z+h)
    if rad:draw.rounded_rectangle([a,b],radius=rad,fill=fill,outline=outline,width=2)
    else:draw.rectangle([a,b],fill=fill,outline=outline,width=2)
def label(x,z,s,n=24,fill='#343D36'):text(*pt(x,z),s,n,fill)
text(70,70,'主卧与主卫 · v14方案',42,anchor='lm')
text(70,126,'新增段与原主卫合并  /  洗手台 → 马桶 → 淋浴',29,anchor='lm')
text(70,172,'尺寸为模型试排，实测、结构、湿区允许性及排水待核',24,'#74796F',anchor='lm')
rect(7328,1072,3467,3704,'#EEE6D5')
rect(8356,4096,847,880,'#EEE6D5')
rect(9323,4096,1472,2814,'#DAE1DB')
rect(9323,6010,1472,900,'#AFBFB2')
rect(7849,572,2475,500,'#D7DCCF')
# Original inner boundary is retained as a dashed provenance line, never a current wall.
for x in range(9323,10795,100):draw.line([pt(x,4896),pt(min(x+55,10795),4896)],fill='#9C8C6A',width=2)
for w in d['walls']:
    if w['x']+w['w']<7188 or w['z']+w['d']<400 or w['z']>7030 or w['y']>0 or (w['h']<=1200 and w['kind']!='recess'):continue
    if w['id'].startswith('outer-right') or w['id'].startswith('retained-central-right') or w['id'].startswith('upper-right') or w['id'].startswith('bay-') or w['id'].startswith('right-small') or w['id'].startswith('retained-central-bottom') or w['id'].startswith('v14-'):
        rect(w['x'],w['z'],w['w'],w['d'],'#69716A' if not w['id'].startswith('v14-') else '#42594C')
for g in d['glass']:
    if g['id'] in ['bay-front-glass-0','outer-right-glass-0']:
        draw.line([pt(g['x'],g['z']),pt(g['x']+g['w'],g['z']+g['d'])],fill='#82A6B5',width=5)
label(9086,760,'原飘窗保留',22)
rect(7328,1272,600,2500,'#D8C6A9',rad=8)
for z in range(1772,3772,500):draw.line([pt(7903,z),pt(7328,z)],fill='#B9A68C',width=2)
rect(8645,1826,2150,2150,'#C4AD8D',rad=16);rect(8720,1876,2000,2000,'#ECEDE4',rad=14);rect(8720,1876,2000,1370,'#97A78C',rad=14)
for x in [8830,9780]:rect(x,3376,800,420,'#FAFAF4',rad=15)
rect(8645,3896,2150,80,'#B5B5A9',rad=5)
label(9720,2610,'2米床',32);label(9720,2860,'头北 · 脚南',23)
label(7628,2430,'衣柜',25);label(7628,2670,'深600',22)
rect(10345,4196,450,800,'#D8C6A9',rad=9)
a,b=pt(10390,4321),pt(10750,4871);draw.ellipse([a,b],fill='#FCFCF5',outline='#B7BEB4',width=2)
label(10020,4510,'洗手台',25)
a,b=pt(9443,5350),pt(10003,5750);draw.ellipse([a,b],fill='#FAFBF5',outline='#AAB3A9',width=2)
rect(9323,5350,150,400,'#FAFBF5',rad=7);label(10430,5540,'马桶',25)
draw.line([pt(9323,6010),pt(10795,6010)],fill='#698D90',width=5)
label(10090,6415,'淋浴区',28);label(10090,6650,'深900',22)
rect(9323,6559,280,351,'#9A9E91');label(9490,6820,'原凸块',16)
# Show the proposed side door open and a clear swing arc.
hx,hz=9203,4156
draw.line([pt(hx,hz),pt(hx-760,hz)],fill='#566D5F',width=7)
arc=[pt(hx-760*math.sin(math.pi*i/60),hz+760*math.cos(math.pi*i/60)) for i in range(31)]
draw.line(arc,fill='#819484',width=2)
label(8590,4590,'侧门',22);label(8510,5260,'局部退200',22)
label(8085,5010,'原主卧门',21)
label(8300,2550,'717',22)
label(9730,1460,'床尾754',22)
label(9790,5020,'虚线：原主卫边界',19,'#8C7B5D')
label(11370,1550,'南 ↑',27)
label(9020,7440,'北 ↓',27)
# Dimension strings placed in the generous margin.
def dimension(x1,z1,x2,z2,s):
    a,b=pt(x1,z1),pt(x2,z2);draw.line([a,b],fill='#8D9589',width=2)
    for p in [a,b]:draw.line([(p[0]-6,p[1]-6),(p[0]+6,p[1]+6)],fill='#8D9589',width=2)
    text((a[0]+b[0])/2+50,(a[1]+b[1])/2,s,23)
dimension(11350,4096,11350,6910,'2814*')
dimension(9323,7220,10795,7220,'1472*')
text(1120,450,'本次已接入',30,anchor='lm')
for i,s in enumerate(['新增隔墙及侧门','洗手台 / 马桶 / 淋浴','2米床与图左衣柜','公共区23件家具原位']):text(1120,505+i*50,s,24,anchor='lm')
text(1120,805,'当前取舍',30,anchor='lm')
for i,s in enumerate(['床右侧贴墙，单侧上下床','门洞暂拟800，通行约720','主卫边界扩展约800','门口局部向走廊退200']):text(1120,860+i*50,s,22,anchor='lm')
text(70,1690,'* 未核尺寸，mm。图示门为观察开启态，主文件默认关闭。',24,'#697267',anchor='lm')
text(70,1740,'原v13模型与8K漫游保留为历史版本；本图以v14几何为准。',24,'#697267',anchor='lm')
im.save(OUT/'主卧主卫调整平面.png')
print('V14_PLAN_READY')
