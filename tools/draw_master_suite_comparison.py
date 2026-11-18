"""Read-only master-suite extraction, vector plan drawings and matching PNGs.

No scene/model changes. v13 is the pre-expansion architectural baseline;
v20-complete is the current applied concept. All plan coordinates are mm.
"""
import hashlib
import html
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path('D:/AI-Yang.cn/HomeDesign')
OUT = ROOT / '09_delivery/master-suite-plans-20261110'
OUT.mkdir(parents=True, exist_ok=True)
OLD = ROOT / '02_geometry/geometry-master-v13.json'
NEW = ROOT / '02_geometry/geometry-master-v20-complete.json'
ACTIVE = ROOT / '06_blender/active-model.json'
WATCH = [ACTIVE, OLD, NEW, ROOT / '06_blender/home-main-v20-complete.blend']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


before_hashes = {str(p): sha(p) for p in WATCH}
old = json.loads(OLD.read_text(encoding='utf-8'))
new = json.loads(NEW.read_text(encoding='utf-8'))
active = json.loads(ACTIVE.read_text(encoding='utf-8'))
assert before_hashes[str(NEW)] == active['geometry_sha256']
assert active['revision'] == 20
assert not any(f['id'].startswith('master-') for f in old['furnitureObjects'])

C = {
    'paper': '#FFFFFF', 'ink': '#263C39', 'muted': '#667571',
    'rule': '#D5DEDA', 'wall': '#424E4A', 'new': '#347B70',
    'room': '#F6F2EA', 'bath': '#EAF2EF', 'wet': '#DCECE8',
    'wood': '#DBC8AA', 'woodedge': '#A58E70', 'bed': '#FDFCF8',
    'quilt': '#DBE5DA', 'glass': '#669AA7', 'glassfill': '#EEF6F6',
    'oldline': '#B87459', 'corridor': '#F4F6F4', 'service': '#BBC4BF',
}
FONT = 'C:/Windows/Fonts/msyh.ttc'
BOLD = 'C:/Windows/Fonts/msyhbd.ttc'
FONTS = {}


class Drawing:
    """One vector operation stream rendered independently to SVG and PNG."""
    def __init__(self, width, height, title):
        self.w, self.h, self.title = width, height, title
        self.image = Image.new('RGB', (width, height), C['paper'])
        self.draw = ImageDraw.Draw(self.image)
        self.svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(title)}">',
                    '<style>text{font-family:Microsoft YaHei,Noto Sans CJK SC,sans-serif}</style>',
                    f'<rect width="{width}" height="{height}" fill="{C["paper"]}"/>']
        self.labels = []

    def polygon(self, pts, fill=None, stroke=None, width=2):
        if fill:
            self.draw.polygon(pts, fill=fill)
        if stroke:
            self.draw.line(pts + [pts[0]], fill=stroke, width=max(1, round(width)), joint='curve')
        p = ' '.join(f'{x:.3f},{y:.3f}' for x, y in pts)
        self.svg.append(f'<polygon points="{p}" fill="{fill or "none"}" stroke="{stroke or "none"}" stroke-width="{width}"/>')

    def rect(self, x, y, w, h, fill=None, stroke=None, width=2, r=0):
        box = (x, y, x + w, y + h)
        if r:
            self.draw.rounded_rectangle(box, radius=r, fill=fill, outline=stroke, width=max(1, round(width)))
        else:
            self.draw.rectangle(box, fill=fill, outline=stroke, width=max(1, round(width)))
        self.svg.append(f'<rect x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" rx="{r:.3f}" fill="{fill or "none"}" stroke="{stroke or "none"}" stroke-width="{width}"/>')

    def ellipse(self, x, y, w, h, fill=None, stroke=None, width=2):
        self.draw.ellipse((x, y, x + w, y + h), fill=fill, outline=stroke, width=max(1, round(width)))
        self.svg.append(f'<ellipse cx="{x+w/2:.3f}" cy="{y+h/2:.3f}" rx="{w/2:.3f}" ry="{h/2:.3f}" fill="{fill or "none"}" stroke="{stroke or "none"}" stroke-width="{width}"/>')

    def line(self, pts, color=None, width=2, dash=False):
        color = color or C['ink']
        if dash:
            for a, b in zip(pts, pts[1:]):
                length = math.dist(a, b)
                for t in range(0, math.ceil(length), 15):
                    u, v = t / length, min(t + 8, length) / length
                    self.draw.line([(a[0]+u*(b[0]-a[0]), a[1]+u*(b[1]-a[1])), (a[0]+v*(b[0]-a[0]), a[1]+v*(b[1]-a[1]))], fill=color, width=max(1, round(width)))
        else:
            self.draw.line(pts, fill=color, width=max(1, round(width)), joint='curve')
        p = ' '.join(f'{x:.3f},{y:.3f}' for x, y in pts)
        self.svg.append(f'<polyline points="{p}" fill="none" stroke="{color}" stroke-width="{width}"'+(' stroke-dasharray="8 7"' if dash else '')+'/>')

    def text(self, x, y, text, size=28, fill=None, anchor='middle', bold=False):
        fill = fill or C['ink']
        key = (size, bold)
        if key not in FONTS:
            FONTS[key] = ImageFont.truetype(BOLD if bold else FONT, size)
        font = FONTS[key]
        # Anchor y is the line's vertical center, matching the vector labels.
        self.draw.text((x, y), text, font=font, fill=fill,
                       anchor={'middle': 'mm', 'start': 'lm', 'end': 'rm'}[anchor])
        b = self.draw.textbbox((x, y), text, font=font,
                               anchor={'middle': 'mm', 'start': 'lm', 'end': 'rm'}[anchor])
        self.labels.append({'text': text, 'bounds': list(b)})
        self.svg.append(f'<text x="{x:.3f}" y="{y:.3f}" text-anchor="{anchor}" dominant-baseline="central" font-size="{size}" font-weight="{500 if bold else 400}" fill="{fill}">{html.escape(text)}</text>')

    def save(self, base):
        name = OUT / base
        self.image.save(str(name) + '.png', dpi=(160, 160))
        Path(str(name) + '.svg').write_text('\n'.join(self.svg + ['</svg>']), encoding='utf-8')
        assert all(0 <= q['bounds'][0] and q['bounds'][2] <= self.w and 0 <= q['bounds'][1] and q['bounds'][3] <= self.h for q in self.labels), 'clipped text'
        return {'name': base, 'resolution': [self.w, self.h], 'labels': self.labels}


class Plan:
    def __init__(self, d, ox):
        self.d, self.ox = d, ox
        self.s = .19
        self.left = ox + 76
        self.top = 262
        self.xmin, self.zmin = 6800, 400

    def pt(self, x, z):
        return self.left + (x-self.xmin)*self.s, self.top+(z-self.zmin)*self.s

    def rect(self, x, z, w, h, fill, stroke=None, r=0, width=2):
        X, Y = self.pt(x,z)
        self.d.rect(X, Y, w*self.s, h*self.s, fill, stroke, width, r*self.s)

    def poly(self, pts, fill, stroke=None, width=2):
        self.d.polygon([self.pt(x,z) for x,z in pts], fill, stroke, width)

    def line(self, pts, color=C['ink'], width=2, dash=False):
        self.d.line([self.pt(x,z) for x,z in pts], color, width, dash)

    def text(self, x, z, text, size=28, fill=None, anchor='middle', bold=False):
        self.d.text(*self.pt(x,z), text, size, fill, anchor, bold)

    def ellipse(self, x,z,w,h,fill,stroke=None,width=2):
        X,Y=self.pt(x,z)
        self.d.ellipse(X,Y,w*self.s,h*self.s,fill,stroke,width)

    def hdim(self, a, b, z, label, ext_to=None):
        self.line([(a,z),(b,z)], C['muted'], 1.5)
        for x in [a,b]:
            self.line([(x-30,z-30),(x+30,z+30)],C['muted'],2)
            if ext_to is not None:
                self.line([(x,z+50),(x,ext_to)],C['rule'],1)
        self.text((a+b)/2,z-95,label,26,C['muted'])

    def vdim(self, a, b, x, label, face=None):
        self.line([(x,a),(x,b)],C['muted'],1.5)
        for z in [a,b]:
            self.line([(x-30,z-30),(x+30,z+30)],C['muted'],2)
            if face is not None:
                self.line([(face,z),(x-50,z)],C['rule'],1)
        px,py=self.pt(x,(a+b)/2)
        self.d.rect(px-52,py-20,104,40,C['paper'])
        self.d.text(px,py,label,26,C['muted'])


def rectpoly(w):
    if 'planProfileLocalMm' in w:
        return [(w['x']+x,w['z']+z) for x,z in w['planProfileLocalMm']]
    return [(w['x'],w['z']),(w['x']+w['w'],w['z']),
            (w['x']+w['w'],w['z']+w['d']),(w['x'],w['z']+w['d'])]


def clipped_rect(w, xmin, zmin, xmax, zmax):
    # Only the two common right external rectangles need trimming.
    q = dict(w)
    a,b=max(xmin,w['x']),max(zmin,w['z'])
    c,d=min(xmax,w['x']+w['w']),min(zmax,w['z']+w['d'])
    if c<=a or d<=b: return None
    q.update(x=a,z=b,w=c-a,d=d-b)
    return q


def draw_panel(d, ox, after=False):
    g = new if after else old
    p = Plan(d,ox)
    d.text(ox+78,176,'修改后' if after else '修改前',42,bold=True,anchor='start')
    d.text(ox+280,178,'当前 v20 布局' if after else '扩卫前原始边界 · v13',28,fill=C['muted'],anchor='start')
    # Direct source footprints. The common bedroom stays rectangular in the
    # old plan; the new dry pocket is read from its explicit profile.
    p.rect(7328,1072,3467,3704,C['room'])
    p.rect(6800,4896,2403,650,C['corridor'])
    if after:
        for q in g['bathParts']:
            if q['id'] in ['v14-bath-floor-main','v14-bath-floor-service-side','v20f-bath-extension-floor']:
                p.poly(rectpoly(q),C['bath'])
            elif q['id'].startswith('v14-shower-zone-floor'):
                p.poly(rectpoly(q),C['wet'])
        foyer=next(q for q in g['bathParts'] if q['id']=='v20f-foyer-floor')
        p.poly(rectpoly(foyer),C['room'])
    else:
        p.rect(9323,4896,1472,2014,C['bath'])

    base_ids={'upper-right-top-left-end','upper-right-top-right-end','bay-left-end','bay-right-end',
              'bay-front-0','bay-front-end','outer-right-0','outer-right-end',
              'retained-central-right-end','retained-central-bottom-stub-end',
              'right-small-bottom-end','right-small-service-block'}
    if not after: base_ids|={'upper-right-bottom-1','upper-right-bottom-end','right-small-left-end'}
    else: base_ids|={'v14-master-head-wall','v14-bath-left-top-jamb',
                     'v14-bath-left-bottom','v14-master-foyer-return',
                     'v14-master-foyer-front','v20f-bath-diagonal-bottom-jamb'}
    for w in g['walls']:
        if w['id'] not in base_ids: continue
        q=w
        if w['id'].startswith('outer-right') or w['id']=='retained-central-bottom-stub-end':
            q=clipped_rect(w,6916,472,11035,7030)
            if q is None: continue
        new_wall_ids={'v14-master-head-wall','v14-bath-left-top-jamb','v20f-bath-diagonal-bottom-jamb'}
        color=C['new'] if after and w['id'] in new_wall_ids else C['wall']
        if w['id']=='right-small-service-block': color=C['service']
        p.poly(rectpoly(q),color)

    # Bay seat/window and the retained bathroom window. Sill walls do not
    # appear as full-height solid plan cuts.
    p.rect(7949,572,2275,500,C['wood'],C['woodedge'],width=1)
    p.rect(7949,472,2275,100,C['glassfill'],C['glass'],width=2)
    p.line([(7949,522),(10224,522)],C['glass'],2)
    p.text(9086,820,'飘窗',29)
    p.rect(10795,5125,240,869,C['glassfill'],C['glass'],width=2)
    p.line([(10915,5125),(10915,5994)],C['glass'],2)
    p.hdim(7328,10795,275,'净宽 3467',ext_to=820)

    # Main entry is unchanged; no swing direction was established in either
    # historical source, so show the closed line and a labeled opening.
    p.line([(7370,4836),(8236,4836)],C['woodedge'],4)
    p.line([(7370,4806),(7370,4866)],C['woodedge'],3)
    p.line([(8236,4806),(8236,4866)],C['woodedge'],3)
    p.text(7790,5125,'主卧入口',27)
    p.text(7850,5410,'公共走廊',25,C['muted'])

    if not after:
        p.text(9100,2700,'原主卧',40,bold=True)
        p.text(9100,3020,'未布置家具',27,C['muted'])
        p.line([(9724,4836),(10616,4836)],C['woodedge'],4)
        p.text(10035,5240,'原门洞 892',24,C['muted'])
        p.text(10060,5790,'原主卫',36,bold=True)
        p.text(10060,6120,'1472 × 2014',26,C['muted'])
        p.text(10060,6400,'洁具未排布',25,C['muted'])
        p.vdim(1072,4776,11320,'3704',face=11035)
        p.vdim(4896,6910,11320,'2014',face=11035)
        p.hdim(9323,10795,7310,'1472',ext_to=7050)
    else:
        f={q['id']:q for q in g['furnitureObjects']}
        for fid in ['master-wardrobe','master-bed','master-vanity','master-toilet']:
            assert fid in f
        wardrobe=f['master-wardrobe']
        p.rect(wardrobe['x'],wardrobe['z'],wardrobe['w'],wardrobe['d'],C['wood'],C['woodedge'],width=2)
        for z in range(1772,3772,500): p.line([(7328,z),(7928,z)],C['woodedge'],1)
        # Place the wardrobe label above its silhouette rather than hiding
        # its five modules. It stays inside the existing empty top strip.
        p.text(7630,1190,'衣柜',24)
        bedparts=[q for q in g['furniture'] if q.get('parent')=='master-bed']
        for q in bedparts:
            fill = C['wood'] if q['id'] in ['v14-bed-base','v14-bed-headboard'] else C['quilt'] if q['id']=='v14-bed-quilt' else C['bed']
            p.rect(q['x'],q['z'],q['w'],q['d'],fill,C['woodedge'],r=45,width=1.3)
        p.text(9720,2590,'2米床',37,bold=True)
        p.text(9720,2880,'床垫 2000 × 2000',24)
        p.text(9720,3060,'床头在图下方 · 北',24,C['muted'])
        p.hdim(7928,8645,3080,'717')
        p.text((7928+8645)/2,3280,'净距',23,C['muted'])

        v=f['master-vanity']
        p.rect(v['x'],v['z'],v['w'],v['d'],C['wood'],C['woodedge'],r=45,width=1.5)
        p.ellipse(10390,4321,360,550,C['bed'],C['muted'])
        p.ellipse(10435,4410,260,360,C['glassfill'],C['rule'],1)
        p.line([(10750,4547),(10630,4547)],C['muted'],3)
        p.text(10570,4910,'洗手台',24)
        wc=f['master-toilet']
        p.ellipse(wc['x']+130,wc['z'],550,400,C['bed'],C['muted'])
        p.ellipse(wc['x']+260,wc['z']+65,310,270,None,C['rule'])
        p.rect(wc['x'],wc['z'],150,400,C['bed'],C['muted'],r=25)
        p.text(10380,5550,'马桶',30)

        p.line([(9323,6010),(10059,6010)],C['glass'],5)
        p.line([(10059,6030),(10795,6030)],C['glass'],5)
        p.line([(10100,5994),(10100,6064)],C['glass'],4)
        p.text(10060,5840,'淋浴移门',24,C['muted'])
        p.line([(10745,6470),(10520,6470)],C['muted'],3)
        p.ellipse(10430,6390,180,180,C['bed'],C['muted'])
        p.rect(10455,6810,280,24,C['muted'])
        p.text(10000,6480,'淋浴区',31,bold=True)
        p.text(10000,6750,'进深 900',24,C['muted'])
        # Source-derived closed bifold profile: actual shape, not its
        # rectangular bounding box. No unverified opening arc is invented.
        for q in g['bathParts']:
            if q['id'].startswith('v20f-bath-bifold-leaf'):
                p.poly(rectpoly(q),C['wood'],C['woodedge'],1.8)
        p.text(7860,4450,'卧室内通道',24,C['muted'])
        # Door label lives in the empty corridor and points to the diagonal.
        p.line([(8870,4480),(8710,5160),(8580,5160)],C['new'],1.8)
        p.text(8550,5170,'双折门',25,C['new'],anchor='end')
        p.text(8770,5405,'门洞 860 · 提案',23,C['muted'])
        # Reference only: old boundary has been opened. Keep it a line, not
        # a false wall, and avoid the basin footprint.
        p.line([(9335,4896),(10250,4896)],C['oldline'],2.5,True)
        p.text(9770,5090,'原主卫分界',23,C['oldline'])
        p.vdim(1072,3976,11320,'2904',face=11035)
        p.text(11320,2320,'床区',24,C['muted'])
        p.vdim(4096,6910,11320,'2814',face=11035)
        p.hdim(9323,10795,7310,'1472',ext_to=7050)
        # A readable external ruler shows the expansion separately.
        p.vdim(4096,4896,11750,'800')
        p.text(11750,3970,'扩入',24,C['new'])

    # Both plans use the identical frame, not separate auto-fit scales.
    d.text(ox+78,1694,'布局说明',27,bold=True,anchor='start')
    notes = (
        ['主卧净宽3467；原主卫暂拟1472 × 2014。',
         '保留扩卫前边界与两个原有门洞；开向未定。',
         '原始毛坯未确定床、衣柜及洁具，不补画布置。']
        if not after else
        ['主卫向主卧扩入800；入口 → 台盆 → 马桶 → 淋浴。',
         '衣柜2500 × 600；床架2150 × 2150；台盆800 × 450。',
         '绿色为新增隔墙；虚线为原主卫分界；门型为提案。']
    )
    for i,t in enumerate(notes): d.text(ox+78,1744+i*43,t,26,C['muted'],anchor='start')
    return p


def header(d, combined=False):
    d.text(78,64,'主卧与主卫 · 布局平面图',46,bold=True,anchor='start')
    d.text(78,113,'上南 · 下北 · 左东 · 右西    /    单位 mm    /    同比例对照',26,C['muted'],anchor='start')
    d.line([(78,142),(d.w-78,142)],C['rule'],2)
    d.text(78,1907,'模型方案尺寸，尚未现场复尺；墙体、排水及门窗安装条件待核。',25,C['muted'],anchor='start')


reports=[]
for label, after in [('主卧主卫-修改前',False),('主卧主卫-修改后-v20',True)]:
    d=Drawing(1200,1960,label)
    header(d)
    draw_panel(d,0,after)
    reports.append(d.save(label))

both=Drawing(2480,1960,'主卧主卫修改前后对照')
header(both,True)
both.line([(1240,170),(1240,1842)],C['rule'],2)
draw_panel(both,0,False)
draw_panel(both,1280,True)
reports.append(both.save('主卧主卫-修改前后对照'))

assert {str(p): sha(p) for p in WATCH} == before_hashes, 'source mutation'
manifest={
    'date':'2026-11-10','purpose':'separate read-only master bedroom and bath plan comparison',
    'before':{'path':str(OLD),'sha256':sha(OLD),'meaning':'pre-bath-expansion v13 boundaries; no owner-confirmed private furniture or fixtures at that stage'},
    'after':{'path':str(NEW),'sha256':sha(NEW),'meaning':'active complete v20; all four master-suite furniture positions preserved'},
    'units':'mm','plan_orientation':'up south, down north, left east, right west',
    'same_scale':True,'scale_px_per_mm':.19,
    'drawn_cut':'solid walls with y<=510mm except bay and window sills symbolized as openings',
    'door_display':'existing entry/original bath door openings: closed line, no unverified swing; current diagonal bifold: true closed profile',
    'before_bath_mm':[1472,2014],'after_bath_rect_mm':[1472,2814],
    'after_diagonal_dry_pocket_included':True,
    'after_furniture_positions':{q['id']:{k:q[k] for k in ['x','z','w','d']} for q in new['furnitureObjects'] if q['id'].startswith('master-')},
    'source_models_unchanged':True,
    'outputs':[{'name':r['name'],'resolution':r['resolution'],'png_sha256':sha(OUT/(r['name']+'.png')),'svg_sha256':sha(OUT/(r['name']+'.svg'))} for r in reports],
    'text_bounds_passed':True,'visual_inspection_pending':True,
}
(OUT/'来源与尺寸核对.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'图纸说明.txt').write_text('主卧与主卫修改前后对照\n\n修改前：v13扩卫前原始边界，主卫1472×2014mm。未给原始空房补画家具或洁具。\n修改后：当前v20完整模型，主卫直段1472×2814mm，含斜向入口；床、衣柜、台盆及马桶均沿用主模型坐标。\n两图同一比例和方向：上南下北、左东右西；单位mm。\n双折门是为对齐走廊墙线而采用的设计提案，尚未选定产品。图中关闭展示；原门开向未确定。\n模型源文件未修改。非现场实测或施工图。\nPNG用于查看；SVG为可缩放矢量图。\n',encoding='utf-8')
print(json.dumps({'output_directory':str(OUT),'files':[r['name'] for r in reports],'same_scale':True,'sources_unchanged':True},ensure_ascii=True))
