"""User-selected furnishings; coordinates and dimensions are millimetres."""

MATERIALS = {
    'wood': dict(name='oak', color=[.64,.47,.31,1], roughness=.75),
    'cabinet': dict(name='warm-white-cabinet', color=[.91,.89,.83,1], roughness=.85),
    'fabric': dict(name='greige-upholstery', color=[.69,.68,.63,1], roughness=1),
    'fabric-dark': dict(name='upholstery-frame', color=[.55,.55,.51,1], roughness=1),
    'metal': dict(name='dark-metal', color=[.18,.20,.20,1], roughness=.5),
    'screen': dict(name='display-screen', color=[.035,.055,.065,1], roughness=.3),
    'book': dict(name='muted-book-spines', color=[.43,.53,.50,1], roughness=1),
}

def build_furnishing():
    objects, parts = [], []
    # The retained return starts at z=4776. Move the full 3600-wide bookcase
    # 24 mm toward the balcony so its end meets that return without overlap.
    placement_offsets={'bookcase':(0,-24)}

    def obj(id, name, zone, scheme, x,z,w,d,h, detail, label=False, facing=None, rotate=0):
        dx,dz=placement_offsets.get(id,(0,0));x+=dx;z+=dz
        record=dict(id=id,name=name,zone=zone,scheme=scheme,x=x,z=z,w=w,d=d,h=h,
                    detail=detail,label=label,labelRotate=rotate)
        if facing:record['facing']=facing
        objects.append(record)
        return id

    def b(parent, tag, x,z,w,d,y,h, material='wood', shape='box'):
        assert min(w,d,h)>0
        dx,dz=placement_offsets.get(parent,(0,0));x+=dx;z+=dz
        parts.append(dict(id=parent+'-'+tag,parent=parent,kind='furniture',shape=shape,
                          x=x,z=z,w=w,d=d,y=y,h=h,material=material))

    def cyl(parent,tag,cx,cz,r,y,h,material='metal'):
        b(parent,tag,cx-r,cz-r,r*2,r*2,y,h,material,'cylinder')

    def cabinet(parent,tag,x,z,w,d,y,h,doors=2,front='positive-x'):
        b(parent,tag+'-body',x,z,w,d,y,h,'cabinet')
        b(parent,tag+'-top',x,z,w,d,y+h-20,20)
        for i in range(doors):
            dx=x+w-18 if front=='positive-x' else x
            b(parent,tag+f'-door-{i}',dx,z+4+i*d/doors,18,d/doors-8,y+4,h-28,'cabinet')
            b(parent,tag+f'-handle-{i}',dx+(0 if front!='positive-x' else 15),z+(i+.5)*d/doors-45,3,90,y+h*.62,10,'metal')

    # Red A: a low TV cabinet and a separate tall cabinet at the dining end.
    q=obj('tv-low','电视低柜','red','A',0,1800,400,3200,450,
          '红 A：3200×400×450 低柜；配餐厅端 900×550×2400 高柜。',True,rotate=-90)
    cabinet(q,'case',0,1800,400,3200,70,380,4)
    b(q,'plinth',45,1840,300,3120,0,70,'metal')
    q=obj('tv-high','电视端部高柜','red','A',0,5100,550,900,2400,
          '红 A：高柜在靠餐厅一端，靠阳台端保持低矮。')
    cabinet(q,'case',0,5100,550,900,60,2340,2)
    b(q,'plinth',40,5140,470,820,0,60,'metal')
    q=obj('television','电视','red','A',30,2550,65,1700,1600,
          '电视面向沙发与办公座位；屏幕大小为方案示意。',facing='positive-x')
    b(q,'body',30,2550,60,1700,640,960,'metal')
    b(q,'screen',90,2575,5,1650,665,910,'screen')

    # Blue B: the sofa faces negative X, with a detached movable ottoman.
    q=obj('sofa-modular','模块沙发','blue','B',2850,2300,950,2400,850,
          '蓝 B：2400×950 模块沙发，面向电视；脚凳可单独移动。',True,'negative-x')
    b(q,'base',2870,2320,910,2360,100,190,'fabric-dark')
    b(q,'back',3660,2300,140,2400,280,570,'fabric-dark')
    for i in range(3):
        b(q,f'seat-{i}',2850,2448+i*701,798,685,290,140,'fabric')
        b(q,f'back-cushion-{i}',3550,2450+i*700,110,682,430,350,'fabric')
    for z in [2300,4560]:b(q,f'arm-{z}',2850,z,950,140,280,350,'fabric')
    for x in [2920,3680]:
        for z in [2370,4570]:b(q,f'foot-{x}-{z}',x,z,55,55,0,100,'metal')
    q=obj('ottoman','可移脚凳','blue','B',2000,4050,850,650,430,
          '蓝 B：850×650 可移脚凳，当前靠沙发前侧摆放。')
    b(q,'base',2020,4070,810,610,80,210,'fabric-dark')
    b(q,'cushion',2000,4050,850,650,290,140,'fabric')
    for x in [2070,2720]:
        for z in [4120,4560]:b(q,f'foot-{x}-{z}',x,z,50,50,0,80,'metal')
    q=obj('side-table','小圆边几','blue','B',1925,3025,450,450,500,
          '蓝 B：直径450 小圆边几；取消原 A 方案的大圆茶几。')
    cyl(q,'top',2150,3250,225,470,30,'wood')
    cyl(q,'stem',2150,3250,35,30,440)
    cyl(q,'base',2150,3250,145,0,30)

    # Green B: the table is immediately behind the sofa; both users face TV.
    q=obj('double-desk','双人办公桌','green','B',4000,2300,650,2400,1300,
          '绿 B：2400×650 双人桌；两人朝电视。桌与沙发背留200，座椅活动区1100，椅后另留约1100通道。',True,'negative-x',-90)
    b(q,'top',4000,2300,650,2400,720,30)
    for x in [4040,4560]:
        for z in [2340,4610]:b(q,f'leg-{x}-{z}',x,z,50,50,0,720,'metal')
    b(q,'rail',4040,2340,40,2320,645,55,'metal')
    for i,cz in enumerate([2900,4100],1):
        cyl(q,f'monitor-base-{i}',4200,cz,110,750,20)
        b(q,f'monitor-stand-{i}',4130,cz-22,45,44,770,235,'metal')
        b(q,f'monitor-body-{i}',4100,cz-250,45,500,970,330,'metal')
        b(q,f'monitor-screen-{i}',4145,cz-238,3,476,982,306,'screen')
        b(q,f'keyboard-{i}',4410,cz-220,140,440,750,16,'metal')
        cyl(q,f'mouse-{i}',4500,cz+310,35,750,20)
        c=obj(f'office-chair-{i}',f'办公椅{i}','green','B',4800,cz-265,500,530,950,
              '办公椅在桌子右侧，靠背在右侧，人面向左侧电视。',facing='negative-x')
        b(c,'seat',4800,cz-250,500,500,420,65,'fabric-dark')
        b(c,'back',5235,cz-250,65,500,485,465,'fabric-dark')
        for z in [cz-265,cz+235]:
            b(c,f'arm-{z}',4870,z,330,30,640,35,'metal')
            b(c,f'arm-support-{z}',5140,z,35,30,485,155,'metal')
        cyl(c,'column',5050,cz,35,90,330)
        b(c,'base-x',4775,cz-25,550,50,60,30,'metal')
        b(c,'base-z',5025,cz-275,50,550,60,30,'metal')
        for dx,dz in [(-250,0),(250,0),(0,-250),(0,250)]:cyl(c,f'caster-{dx}-{dz}',5050+dx,cz+dz,30,0,60)

    # Yellow A: independent bookcase; no desk attaches to its middle.
    q=obj('bookcase','书柜与储物','yellow','A',6838,1200,350,3600,2400,
          '黄 A：3600×350×2400；两端各800高柜，中部2000，上开放书架、下封闭柜。',True,'negative-x',-90)
    cabinet(q,'north-tower',6838,1200,350,800,0,2400,2,'negative-x')
    cabinet(q,'south-tower',6838,4000,350,800,0,2400,2,'negative-x')
    cabinet(q,'lower-case',6838,2000,350,2000,0,800,4,'negative-x')
    b(q,'back',7168,2000,20,2000,800,1600,'cabinet')
    for z in [2000,2991,3982]:b(q,f'partition-{z}',6838,z,330,18,800,1600)
    for y in [800,1200,1600,2000,2380]:b(q,f'shelf-{y}',6838,2000,350,2000,y,20)
    for row in range(4):
        for bay in range(2):
            for i in range(5):
                z=2090+bay*1000+i*125
                b(q,f'book-{row}-{bay}-{i}',6870,z,230,70,820+row*400,240+(i%3)*35,'book' if i%2 else 'cabinet')

    # Black B amendment: remove the bench and move the long table edge to wall.
    q=obj('dining-table','靠墙餐桌','ink','B',2332,7300,750,1400,750,
          '黑 B 调整：1400×750 餐桌长边直接靠客卫外侧墙，取消卡座，外侧两把活动餐椅。',True,rotate=-90)
    b(q,'top',2332,7300,750,1400,720,30)
    for x in [2382,2982]:
        for z in [7350,8600]:b(q,f'leg-{x}-{z}',x,z,50,50,0,720)
    for i,z in enumerate([7450,8200],1):
        c=obj(f'dining-chair-{i}',f'餐椅{i}','ink','B',1832,z,450,450,850,
              '活动餐椅位于餐桌外侧；原卡座及靠墙侧座位取消。',facing='positive-x')
        b(c,'seat',1832,z,450,450,420,40,'fabric')
        b(c,'back',1832,z,55,450,460,390)
        for x in [1852,2212]:
            for zz in [z+20,z+380]:b(c,f'leg-{x}-{zz}',x,zz,50,50,0,420)

    selections=[
        dict(zone='red',option='A',name='低柜＋端部高柜'),
        dict(zone='blue',option='B',name='模块沙发＋可移脚凳'),
        dict(zone='green',option='B',name='沙发后双人桌，面向电视'),
        dict(zone='yellow',option='A',name='两端高柜＋中部书架'),
        dict(zone='ink',option='B',name='靠墙餐桌，取消卡座',amendment='no-banquette-table-against-wall'),
    ]
    clearances=dict(sofaToDesk=200,deskDepth=650,officeChairMovement=1100,
                    officePassage=1088,passageBounds=[5750,1200,1088,3600],
                    diningWallX=3082,diningTableWallGap=0,diningBanquette=False)
    return parts,objects,selections,clearances,MATERIALS
