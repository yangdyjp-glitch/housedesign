from pathlib import Path
import json, math, struct, html
from furnish_model import build_furnishing

OUT = Path(__file__).resolve().parent
VIZ = Path(r'C:\Users\Administrator\.codex\visualizations\2026\10\29\01a187d1-69cc-73a1-805e-834e8e8bb476')
H = 2750
walls, glass, removed, openings = [], [], [], []

def box(name, x, z, w, d, y=0, h=H, kind='wall', confidence='provisional'):
    item = dict(id=name, x=x, z=z, w=w, d=d, y=y, h=h, kind=kind, confidence=confidence)
    (glass if kind == 'glass' else walls).append(item)
    return item

def line(name, axis, c, start, end, thick, cuts=(), kind='wall'):
    pos = start
    for i, cut in enumerate(sorted(cuts, key=lambda a:a[0])):
        a,b,sill,top,ctype = cut
        if a > pos:
            if axis == 'x': box(f'{name}-{i}',pos,c,a-pos,thick,kind=kind)
            else: box(f'{name}-{i}',c,pos,thick,a-pos,kind=kind)
        if sill > 0:
            if axis == 'x': box(f'{name}-sill-{i}',a,c,b-a,thick,h=sill,kind=kind)
            else: box(f'{name}-sill-{i}',c,a,thick,b-a,h=sill,kind=kind)
        if top < H:
            if axis == 'x': box(f'{name}-lintel-{i}',a,c,b-a,thick,y=top,h=H-top,kind=kind)
            else: box(f'{name}-lintel-{i}',c,a,thick,b-a,y=top,h=H-top,kind=kind)
        if ctype == 'window':
            if axis == 'x': box(f'{name}-glass-{i}',a,c+thick/2-12,b-a,24,y=sill,h=top-sill,kind='glass')
            else: box(f'{name}-glass-{i}',c+thick/2-12,a,24,b-a,y=sill,h=top-sill,kind='glass')
        openings.append(dict(wall=name,axis=axis,c=c,start=a,end=b,sill=sill,top=top,type=ctype))
        pos = b
    if pos < end:
        if axis == 'x': box(f'{name}-end',pos,c,end-pos,thick,kind=kind)
        else: box(f'{name}-end',c,pos,thick,end-pos,kind=kind)

# Plan coordinates follow the photograph. All geometry is in millimetres.
# Measured clear widths have priority; unresolved overall length is not forced.
front, step, upper = 9635,1072,4776
floor = [[0,0],[7188,0],[7188,1072],[10795,1072],[10795,front],
         [3500,front],[3500,12410],[438,12410],[438,11168],[0,11168]]

line('outer-top','x',-240,-240,7428,240,[(853,6528,0,2270,'window')],kind='external')
line('outer-left','z',-240,-240,11408,240,[(9535,10765,0,2344,'window')],kind='external')
line('top-step','z',7188,0,1072,240,kind='external')
line('upper-right-top-left','x',832,7188,7849,240,kind='external')
line('upper-right-top-right','x',832,10324,11035,240,kind='external')
line('bay-left','z',7849,572,1072,100,kind='external')
line('bay-right','z',10224,572,1072,100,kind='external')
line('bay-front','x',472,7849,10324,100,[(7949,10224,500,2274,'window')],kind='external')
box('master-bay-seat',7849,572,2475,500,h=500,kind='bay-seat')
line('outer-right','z',10795,1072,9875,240,[(5125,5994,445,1918,'window')],kind='external')
line('front-facade','x',front,3082,11035,240,
     [(3930,4629,448,1920,'window'),(5350,6872,602,2371,'window'),
      (8094,10266,614,2386,'window')],kind='external')
line('lower-projection-right','z',3500,front,12650,240,[(10535,11958,494,1966,'window')],kind='external')
line('lower-projection-bottom','x',12410,198,3740,240,kind='external')
line('lower-projection-left','z',198,11168,12410,240,kind='external')
line('left-step-return','x',11168,-240,1271,180,kind='external')
line('left-short-partition','z',1271,front,11168,120)

# Shared partition on the right of the removed enclosure is retained.
line('retained-central-right','z',7188,step,upper+120,140)
# Both indoor faces meet the same z=1072 plane; their thicknesses differ.
line('retained-central-top-stub','x',step-140,6516,7328,140)
line('retained-central-bottom-stub','x',upper,6916,7370,120)
line('upper-right-bottom','x',upper,7370,10795,120,
     [(7370,8236,0,2180,'door'),(9724,10616,0,2100,'door')])

# Small right enclosure; its width annotation conflicts with the 2040 segment.
line('right-small-left','z',9203,4896,7030,120)
line('right-small-bottom','x',6910,9203,10795,120)
box('right-small-service-block',9323,6559,280,351,h=1100,kind='recess')

# Lower row. Clear sizes: 1557x1365, 1557x2060, 2577x3370.
line('lower-narrow-left','z',3082,6090,front,120)
line('lower-narrow-right','z',4759,6090,front,120)
line('lower-narrow-top','x',5970,3082,4759,120,[(3812,4759,0,2100,'door')])
line('lower-narrow-split','x',7455,3082,4759,120,[(3951,4759,0,2100,'door')])
line('lower-centre-top','x',6145,4759,7624,120,[(4943,5811,0,2100,'door')])
line('lower-centre-right','z',7456,6265,front,168)
box('lower-left-service-block',3082,9275,418,360,h=1100,kind='recess')
box('bottom-corner-block',438,12037,373,373,h=H,kind='recess')

# User-requested deletion: these three elements are NEVER part of the live mesh.
removed = [
    dict(id='deleted-vertical',x=4070,z=1072,w=144,d=3704,y=0,h=H,kind='removed'),
    dict(id='deleted-top-return',x=4070,z=932,w=644,d=140,y=0,h=H,kind='removed'),
    dict(id='deleted-bottom-return',x=4070,z=4776,w=1982,d=120,y=0,h=H,kind='removed')]

measurements = [
 dict(name='上侧横向总宽',source=7188,used=7188,status='采用'),
 dict(name='上侧浅区进深',source=1072,used=1072,status='采用'),
 dict(name='原中间隔间净宽',source=2974,used=2974,status='墙已删除，保留定位'),
 dict(name='原中间隔间进深',source=3704,used=3704,status='手写末位待核'),
 dict(name='主卧净宽',source=3467,used=3467,status='手写末位待核'),
 dict(name='客卧',source=[2577,3370],used=[2577,3370],status='采用'),
 dict(name='客卫上区',source=[1554,1365],used=[1557,1365],status='与下区对齐，宽差3'),
 dict(name='客卫下区',source=[1557,2060],used=[1557,2060],status='采用'),
 dict(name='次卧底段',source=[3171,2605],used=[3171,2605],status='采用'),
 dict(name='主卫',source=[1472,2014],used=[1472,2014],status='与横墙2040标注冲突，待核'),
 dict(name='厨房底宽/纵深',source=[3062,2775],used=[3062,2775],status='采用'),
 dict(name='左外墙总长',source=11089,used=9635,status='与分段尺寸不闭合，未作为硬约束'),
 dict(name='左侧内部纵向标注',source=6432,used=None,status='起止点待核'),
 dict(name='主卧外墙纵向标注',source=None,used=3704,status='字迹待核，暂与相邻空间对齐'),
 dict(name='主卫下横墙',source=2040,used=1592,status='与净宽标注不闭合，待核'),
 dict(name='阳台窗下缘',source='用户确认落地窗',used=0,status='取消上一版607 mm窗下墙，窗顶2270 mm暂沿原开口'),
 dict(name='主卧飘窗凸出/窗台高',source=[500,'待核'],used=[500,500],status='凸出尺寸沿原图，窗台高500 mm暂定'),
]
rooms = [
 dict(id='open',name='客厅',x=3450,z=3220,detail='用户确认用途为客厅；红圈三段墙已删除，原隔间已并入。'),
 dict(id='balcony',name='阳台',x=3250,z=510,detail='上侧长窗按落地窗处理，下缘为地面；窗顶暂沿原开口2270 mm。'),
 dict(id='upper-right',name='主卧',x=9020,z=2850,detail='净宽按原图3467 mm；上方凸出部分为飘窗，非落地空间。'),
 dict(id='bay',name='飘窗',x=9086,z=805,detail='主卧飘窗：凸出500 mm；窗台高暂定500 mm，需复核。'),
 dict(id='hall',name='通道',x=6020,z=5480,detail='原图通道关系保留；局部尺寸为拟合。'),
 dict(id='small-right',name='主卫',x=10020,z=5920,detail='暂按1472 × 2014 mm；与横墙2040标注冲突。'),
 dict(id='narrow-top',name='客卫上区',shortName='客卫',group='guest-bath',x=3980,z=6730,detail='客卫上区，保留内部隔断和开口；暂按1557 × 1365 mm。'),
 dict(id='narrow-bottom',name='客卫下区',shortName='客卫',group='guest-bath',x=3980,z=8490,detail='与上区同属客卫；净尺寸按原图1557 × 2060 mm。'),
 dict(id='centre',name='客卧',x=6167,z=8120,detail='净尺寸按原图2577 × 3370 mm。'),
 dict(id='lower-right',name='次卧',x=9210,z=8350,detail='底段按原图3171 × 2605 mm；保留上侧转折。'),
 dict(id='projection',name='厨房',x=2060,z=11340,detail='用户确认用途为厨房；底宽3062 mm、纵深2775 mm。'),
]
furniture, furniture_objects, selected_schemes, clearances, furniture_materials = build_furnishing()
features = dict(
 balconyWindow=dict(wall='outer-top',bottom=0,top=2270,type='floor-level-window',topProvisional=True),
 masterBay=dict(seat='master-bay-seat',projection=500,seatHeight=500,seatHeightProvisional=True),
    alignedWalls=dict(indoorFaceAxis='z',indoorFaceCoordinate=1072,segments=['retained-central-top-stub','upper-right-top-left','upper-right-top-right']),
    furnishing=dict(selectedSchemes=selected_schemes,clearances=clearances,officeFacesTV=True,diningBanquette=False,
                    movable=True,moveStepMm=100,movableObjectIds=[q['id'] for q in furniture_objects]))
dimensions = [
 dict(a=[0,-430],b=[7188,-430],label='7188'),
 dict(a=[7328,1800],b=[10795,1800],label='3467*'),
 dict(a=[4879,9925],b=[7456,9925],label='2577'),
 dict(a=[7624,10255],b=[10795,10255],label='3171'),
 dict(a=[438,13000],b=[3500,13000],label='3062'),
 dict(a=[6930,6265],b=[6930,9635],label='3370'),
]
beams = [dict(a=[0,1072],b=[4070,1072],label='h2362？'),
         dict(a=[0,6090],b=[3082,6090],label='h2484？')]
data = dict(title='房屋主模型 · 家具100mm移动',revision=4,units='mm',height=H,
    geometry_status='依据手绘图的初步空间复原；非闭合实测CAD或施工图',
    photo='C:/Users/Administrator/Desktop/房型.jpg',
    reference='C:/Users/ADMINI~1/AppData/Local/Temp/codex-clipboard-9cd2d453-b333-4021-b37e-41631362d66d.png',
    alignment_reference='C:/Users/ADMINI~1/AppData/Local/Temp/codex-clipboard-df1537cd-add6-4258-8426-21e02c517ef3.png',
    assumptions=['外墙厚240 mm、内墙厚120–168 mm为建模暂定值，并非承重判断。',
      '统一墙高2750 mm为暂定值；照片中的h/D标注仅用于局部窗洞参考。',
      '尺寸暂按毫米读取；无方位信息，方向沿用照片。',
      '优先保留墙体关系和清楚的分段净尺寸；外轮廓总长未闭合，纵向位置含拟合。',
      '房间用途已按用户说明更新；客卫保留原图中的上下两区及内部隔断。',
      '阳台按照片上侧长窗区域理解，窗下缘至地面，窗顶2270 mm暂沿原开口。',
      '主卧凸出部分为飘窗，凸出500 mm；窗台高500 mm暂定，未将其计为可步入地面。',
      '红框两段墙以室内侧墙面z=1072 mm对齐；因墙厚不同，不强制墙中心线相同。',
      '入口位置、梁柱与承重属性仍未确认。',
      '三段红圈墙已从OBJ、GLB和现状平面中删除；DELETED_REFERENCE层仅留核对位置。',
      '家具采用用户所选红A、蓝B、绿B、黄A、黑B；黑B取消卡座，餐桌长边直接靠墙。',
      '双人办公桌在沙发后，两席同向面对电视；书柜独立在座位后方，座椅活动区与通道分开。',
      '家具尺寸为方案尺寸，非产品实测或定制下单尺寸；浅木、暖白与灰米色仅作材质示意。'],
    floor=floor,walls=walls,glass=glass,removed=removed,openings=openings,
    rooms=rooms,features=features,dimensions=dimensions,beams=beams,measurements=measurements,
    furniture=furniture,furnitureObjects=furniture_objects,furnitureMaterials=furniture_materials)
(OUT/'house-model.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')

def cross(a,b,c): return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def triangulate(poly):
    ids=list(range(len(poly))); tris=[]
    area=sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in ids)
    if area<0: ids.reverse()
    while len(ids)>3:
        found=False
        for i in range(len(ids)):
            a,b,c=ids[i-1],ids[i],ids[(i+1)%len(ids)]
            if cross(poly[a],poly[b],poly[c])<=0: continue
            def inside(p): return cross(poly[a],poly[b],p)>=0 and cross(poly[b],poly[c],p)>=0 and cross(poly[c],poly[a],p)>=0
            if any(inside(poly[q]) for q in ids if q not in [a,b,c]): continue
            tris.append([a,b,c]); ids.pop(i); found=True; break
        if not found: raise ValueError('Floor triangulation failed')
    tris.append(ids); return tris

FACES=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
def mesh_box(q):
    x,z,y,w,d,h=[q[k]/1000 for k in ['x','z','y','w','d','h']]
    pts=[[x,y,z],[x+w,y,z],[x+w,y,z+d],[x,y,z+d],
         [x,y+h,z],[x+w,y+h,z],[x+w,y+h,z+d],[x,y+h,z+d]]
    # Plan z is negated to keep a right-handed Y-up export coordinate system.
    pts=[[p[0],p[1],-p[2]] for p in pts]
    return pts,[list(reversed(f)) for f in FACES]

def mesh_cylinder(q,segments=24):
    cx=(q['x']+q['w']/2)/1000;cz=(q['z']+q['d']/2)/1000
    rx=q['w']/2000;rz=q['d']/2000
    pts=[[cx+rx*math.cos(i*2*math.pi/segments),y/1000,-cz-rz*math.sin(i*2*math.pi/segments)]
         for y in [q['y'],q['y']+q['h']] for i in range(segments)]
    faces=[list(reversed(range(segments))),list(range(segments,segments*2))]
    faces += [[i,(i+1)%segments,(i+1)%segments+segments,i+segments] for i in range(segments)]
    return pts,faces

materials=[dict(name='wall',color=[.80,.82,.80,1],roughness=.95),
           dict(name='floor',color=[.71,.76,.73,1],roughness=1),
           dict(name='glass',color=[.47,.73,.81,.32],roughness=.2)]+list(furniture_materials.values())
furniture_mat_ids={key:i+3 for i,key in enumerate(furniture_materials)}

meshes=[]
for q in walls+glass:
    p,f=mesh_box(q)
    meshes.append((q['id'],p,f,2 if q['kind']=='glass' else (1 if q['kind']=='bay-seat' else 0)))
for q in furniture:
    p,f=mesh_cylinder(q) if q['shape']=='cylinder' else mesh_box(q)
    meshes.append((q['id'],p,f,furniture_mat_ids[q['material']]))
floorverts=[[x/1000,0,-z/1000] for x,z in floor]+[[x/1000,-.1,-z/1000] for x,z in floor]
n=len(floor)
toptris=triangulate(floor)
floorfaces=toptris+[[k+n for k in reversed(t)] for t in toptris]+[[i+n,(i+1)%n+n,(i+1)%n,i] for i in range(n)]
meshes.insert(0,('floor',floorverts,floorfaces,1))

obj=['# Preliminary spatial model. Units: meters. Y up. Deleted walls excluded.','mtllib house-structure.mtl']
offset=1
for name,pts,faces,mat in meshes:
    obj.extend(['o '+name,'usemtl '+materials[mat]['name']])
    obj += ['v '+' '.join(f'{v:.6f}' for v in p) for p in pts]
    obj += ['f '+' '.join(str(v+offset) for v in f) for f in faces]
    offset+=len(pts)
(OUT/'house-structure.obj').write_text('\n'.join(obj)+'\n',encoding='utf-8')
mtl=[]
for material in materials:
    mtl += ['newmtl '+material['name'],'Kd '+' '.join(str(v) for v in material['color'][:3]),'d '+str(material['color'][3])]
(OUT/'house-structure.mtl').write_text('\n'.join(mtl)+'\n',encoding='utf-8')

# GLB 2.0, one named node per wall segment; deleted walls are not exported.
binary=bytearray(); views=[]; access=[]; gm=[]; nodes=[]
def add_buffer(raw,target=None):
    while len(binary)%4: binary.append(0)
    v=dict(buffer=0,byteOffset=len(binary),byteLength=len(raw))
    if target:v['target']=target
    views.append(v); binary.extend(raw); return len(views)-1
for name,pts,faces,mat in meshes:
    pview=add_buffer(struct.pack('<'+'f'*(3*len(pts)),*[v for p in pts for v in p]),34962)
    pa=len(access); access.append(dict(bufferView=pview,componentType=5126,count=len(pts),type='VEC3',min=[min(p[i] for p in pts) for i in range(3)],max=[max(p[i] for p in pts) for i in range(3)]))
    ids=[]
    for f in faces:
        for j in range(1,len(f)-1):ids += [f[0],f[j],f[j+1]]
    iview=add_buffer(struct.pack('<'+'H'*len(ids),*ids),34963)
    ia=len(access); access.append(dict(bufferView=iview,componentType=5123,count=len(ids),type='SCALAR'))
    gm.append(dict(name=name,primitives=[dict(attributes=dict(POSITION=pa),indices=ia,material=mat)]))
    nodes.append(dict(name=name,mesh=len(gm)-1))
gltf=dict(asset=dict(version='2.0',generator='Measured-sketch spatial reconstruction'),
    scene=0,scenes=[dict(nodes=list(range(len(nodes))))],nodes=nodes,meshes=gm,
    materials=[dict(name=m['name'],doubleSided=True,**({'alphaMode':'BLEND'} if m['color'][3]<1 else {}),
      pbrMetallicRoughness=dict(baseColorFactor=m['color'],metallicFactor=.15 if m['name']=='dark-metal' else 0,roughnessFactor=m['roughness'])) for m in materials],
    buffers=[dict(byteLength=len(binary))],bufferViews=views,accessors=access,
    extras=dict(units='meter',metadataUnits='mm',status=data['geometry_status'],assumptions=data['assumptions'],rooms=rooms,features=features,furnitureObjects=furniture_objects))
jb=json.dumps(gltf,separators=(',',':'),ensure_ascii=True).encode()
while len(jb)%4:jb+=b' '
while len(binary)%4:binary.append(0)
glb=struct.pack('<III',0x46546C67,2,12+8+len(jb)+8+len(binary))+struct.pack('<II',len(jb),0x4E4F534A)+jb+struct.pack('<II',len(binary),0x004E4942)+binary
(OUT/'house-structure.glb').write_bytes(glb)

# DXF uses millimetres. Removed reference is explicitly off in layer settings.
dxf=['0','SECTION','2','HEADER','9','$ACADVER','1','AC1015','9','$INSUNITS','70','4','0','ENDSEC','0','SECTION','2','TABLES','0','TABLE','2','LAYER','70','8']
for layer,col in [('WALL',7),('WINDOW',4),('DELETED_REFERENCE',-1),('FLOOR',8),('LABEL',7),('BAY_SEAT',8),('FURNITURE',3),('FURNITURE_LABEL',3)]:
    dxf+=['0','LAYER','2',layer,'70','0','62',str(col),'6','CONTINUOUS']
dxf += ['0','ENDTAB','0','ENDSEC','0','SECTION','2','ENTITIES']
def dxf_line(a,b,layer):
    dxf.extend(['0','LINE','8',layer,'10',str(a[0]),'20',str(-a[1]),'30','0','11',str(b[0]),'21',str(-b[1]),'31','0'])
def dxf_rect(q,layer):
    x,z,w,d=[q[k] for k in ['x','z','w','d']];p=[[x,z],[x+w,z],[x+w,z+d],[x,z+d]]
    for i in range(4): dxf_line(p[i],p[(i+1)%4],layer)
for q in walls:
    if q['y']<=1200<q['y']+q['h']: dxf_rect(q,'WALL')
    if q['kind']=='bay-seat': dxf_rect(q,'BAY_SEAT')
for q in glass:dxf_rect(q,'WINDOW')
for q in removed:dxf_rect(q,'DELETED_REFERENCE')
for q in furniture_objects:
    if q['id']=='side-table':
        dxf+=['0','CIRCLE','8','FURNITURE','10',str(q['x']+q['w']/2),'20',str(-q['z']-q['d']/2),'30','0','40',str(q['w']/2)]
    else:dxf_rect(q,'FURNITURE')
for i in range(len(floor)): dxf_line(floor[i],floor[(i+1)%len(floor)],'FLOOR')
def dxf_unicode(s):
    return ''.join(c if ord(c)<128 else '\\U+'+format(ord(c),'04X') for c in s)
for r in rooms:
    rx,rz=(1600,5400) if r['id']=='open' else (r['x'],r['z'])
    dxf+=['0','TEXT','8','LABEL','10',str(rx),'20',str(-rz),'30','0','40','180','1',dxf_unicode(r['name'])]
for q in furniture_objects:
    if q['label']:dxf+=['0','TEXT','8','FURNITURE_LABEL','10',str(q['x']+q['w']/2),'20',str(-q['z']-q['d']/2),'30','0','40','150','50',str(-q['labelRotate']),'1',dxf_unicode(q['name'])]
dxf+=['0','ENDSEC','0','EOF']
(OUT/'house-plan.dxf').write_text('\n'.join(dxf)+'\n',encoding='ascii')

# Editable vector plan; the removed wall is absent by default.
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1050" height="1260" viewBox="-900 -1100 12800 15200">',
 '<rect x="-900" y="-1100" width="12800" height="15200" fill="#fff"/>',
 '<style>text{font-family:Microsoft YaHei,Noto Sans CJK SC,sans-serif;fill:#273e48} .room{font-size:180px;text-anchor:middle} .dim{font-size:170px;text-anchor:middle}</style>',
 '<text x="-240" y="-620" font-size="270">房屋主模型 · 已选家具布局</text>',
 '<text x="-240" y="-300" font-size="155">单位 mm · 初步拟合模型 · 墙厚与墙高暂定</text>',
 '<polygon points="'+' '.join(f'{x},{z}' for x,z in floor)+'" fill="#eef3f1"/>']
for q in walls:
    if q['kind']=='bay-seat':
        svg.append(f'<rect x="{q["x"]}" y="{q["z"]}" width="{q["w"]}" height="{q["d"]}" fill="#cbd4d3"/>')
for q in walls:
    if q['y']<=1200<q['y']+q['h']:
        svg.append(f'<rect x="{q["x"]}" y="{q["z"]}" width="{q["w"]}" height="{q["d"]}" fill="#344b54"/>')
for q in glass:svg.append(f'<rect x="{q["x"]}" y="{q["z"]}" width="{q["w"]}" height="{q["d"]}" fill="#5a96ad"/>')
for q in sorted(furniture,key=lambda p:p['y']+p['h']):
    fill='#'+''.join(f'{round(c*255):02x}' for c in furniture_materials[q['material']]['color'][:3])
    if q['shape']=='cylinder':
        svg.append(f'<ellipse cx="{q["x"]+q["w"]/2}" cy="{q["z"]+q["d"]/2}" rx="{q["w"]/2}" ry="{q["d"]/2}" fill="{fill}" stroke="#59635e" stroke-width="10"/>')
    else:svg.append(f'<rect x="{q["x"]}" y="{q["z"]}" width="{q["w"]}" height="{q["d"]}" fill="{fill}" stroke="#59635e" stroke-width="10"/>')
for r in rooms:
    rx,rz=(1600,5400) if r['id']=='open' else (r['x'],r['z'])
    svg.append(f'<text class="room" x="{rx}" y="{rz}">{html.escape(r["name"])}</text>')
for q in furniture_objects:
    if q['label']:
        x,z=q['x']+q['w']/2,q['z']+q['d']/2
        svg.append(f'<text class="room" transform="translate({x},{z}) rotate({q["labelRotate"]})" style="paint-order:stroke;stroke:#fff;stroke-width:45">{html.escape(q["name"])}</text>')
for b in beams:
    a,c=b['a'],b['b'];svg.append(f'<path d="M{a[0]} {a[1]}L{c[0]} {c[1]}" fill="none" stroke="#9a8d72" stroke-width="20" stroke-dasharray="80 70"/>')
for dim in dimensions:
    a,b=dim['a'],dim['b'];mx=(a[0]+b[0])/2;mz=(a[1]+b[1])/2
    svg.append(f'<path d="M{a[0]} {a[1]}L{b[0]} {b[1]}" stroke="#65767b" stroke-width="10"/>')
    svg.append(f'<text class="dim" x="{mx}" y="{mz-70}">{dim["label"]}</text>')
svg += ['<text x="-240" y="13600" font-size="155">红A / 蓝B / 绿B / 黄A / 黑B：办公朝电视；餐桌靠墙，取消卡座。</text>',
 '<text x="-240" y="13840" font-size="155">* 手写尺寸待核；总长与分段未闭合，非实测闭合CAD / 施工图。</text>','</svg>']
(OUT/'house-plan.svg').write_text('\n'.join(svg),encoding='utf-8')

notes='''房屋主模型与家具布置说明

交互移动：主模型中13件家具均可点击选中、拖动，或从列表选择后用方向按钮、偏移输入框移动。每件家具的所有部件一起移动，座椅独立移动。位移以各自初始摆放点为起点、按100 mm步进，保留原有靠墙起点；可撤销上次移动。平面与立体同步。位置通过会话状态保留，静态三维与CAD文件记录此包生成时的初始摆放，后续按确认后的布局再生成。

本次填充：红A低柜与端部高柜；蓝B模块沙发、可移脚凳、小圆边几；绿B沙发后的双人办公桌，两席同向朝电视；黄A两端高柜、中部开放书架与下柜；黑B取消卡座，餐桌长边直接贴客卫外侧墙，外侧保留两把活动餐椅。其他房间未增加家具。

主要家具：电视低柜3200×400×450，高柜900×550×2400；沙发2400×950，脚凳850×650，边几直径450；双人桌2400×650、桌高750；书柜3600×350×2400；餐桌1400×750、高750。均为方案尺寸，需现场复尺与产品核对。

横向关系：沙发背x=3800，桌面x=4000至4650，座椅活动区x=4650至5750，主通道x=5750至6838，书柜x=6838至7188。沙发与桌留200；座椅活动区1100包含椅子及拉出空间；后方另设1088宽通道。餐桌右侧x=3082与墙面相接，未设置卡座。

为避开保留短墙，书柜在现有拟合模型内向阳台侧平移24 mm；3600总宽不变。

浅木、暖白与灰米色为材质示意；GLB、OBJ、DXF与平面图已包含所选家具。家具按独立对象命名，便于继续修改。

已按第二张图片删除红圈内三段墙体：竖墙、上端短墙和下端横墙。其右侧分隔墙保留。

用途：原下凸区为厨房；连通空间为客厅；右上为主卧；右侧小空间为主卫；右下为次卧；下排中间为客卧；下排左上、左下同属客卫，保留原图内部隔断。

本次校正：阳台上侧长窗取消607 mm窗下墙，玻璃从地面起，窗顶暂沿原开口2270 mm。主卧凸出部分改为飘窗，增加500 mm高窗台，凸出500 mm；窗台高仍为暂定，地面未延伸为可步入房间。红框两段横墙统一室内侧墙面z=1072 mm；墙厚不同，墙中心线不强制相同。

预览默认使用正常透视投影，近处等长物体显示更大；另保留正交立体和平面尺寸视图。导出三维几何不受投影选择影响。

模型采用毫米读取草图，三维文件以米导出、Y轴向上。GLB和OBJ均不含已删除墙；DXF的DELETED_REFERENCE为关闭状态的核对图层。

这是一份初步空间关系模型。图中多处尺寸不能同时闭合，因此优先保留墙体关系和清楚的分段净尺寸。当前左侧总长拟合值9635 mm，与手写11089 mm不一致；主卫1472 mm净宽与2040 mm横墙标注也不能对应。完整识读记录见house-model.json。

墙高暂定2750 mm；外墙厚240 mm、内墙厚120–168 mm为建模参数。图中的h/D仅作为局部窗洞参考，不代表已经确认全屋层高。窗洞位置及小凹凸也需要现场复核。没有标注朝向。

交付内容：
house-structure.glb：可在常见三维软件中打开的模型
house-structure.obj / house-structure.mtl：可编辑网格模型
house-plan.dxf：毫米单位的平面矢量线稿
house-plan.svg：可编辑标注平面图
house-model.json：尺寸、墙体、删除记录、家具对象、所选方案和假设

本次删除只表示模型修改；草图不足以判断墙体承重属性或确定现场拆除方案。
'''
(OUT/'模型说明.txt').write_text(notes,encoding='utf-8')

template=(OUT/'house-view.template.html').read_text(encoding='utf-8')
fragment=template.replace('HOUSE_DATA_PLACEHOLDER',json.dumps(data,ensure_ascii=False,separators=(',',':')))
VIZ.mkdir(parents=True,exist_ok=True)
(VIZ/'house-structure.html').write_text(fragment,encoding='utf-8')
print(json.dumps(dict(walls=len(walls),glass=len(glass),removed=len(removed),meshes=len(meshes),glb_bytes=len(glb),visualization=str(VIZ/'house-structure.html')),ensure_ascii=False))
