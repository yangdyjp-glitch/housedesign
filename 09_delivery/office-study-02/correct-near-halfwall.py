import bpy,json,math,hashlib,ast,shutil
from pathlib import Path
from mathutils import Vector

ROOT=Path('D:/AI-Yang.cn/HomeDesign');OLD=ROOT/'09_delivery/office-study-01';OUT=ROOT/'09_delivery/office-study-02'
OUT.mkdir(parents=True,exist_ok=True);(OUT/'references').mkdir(exist_ok=True)
shutil.copy2('C:/Users/ADMINI~1/AppData/Local/Temp/codex-clipboard-875b7152-ea49-47eb-8bfe-81c62e93d005.png',OUT/'references/业主红半墙蓝敞开批注.png')
data=json.loads((OLD/'设计参数.json').read_text(encoding='utf-8'));baseline=data['baselineHashes']
assert baseline=={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in baseline}
# Reuse only audited helper definitions. Never execute the original study's top-level builder.
tree=ast.parse((OLD/'build-office.py').read_text(encoding='utf-8'))
helper_names={'box','top','light','tag'}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in helper_names],type_ignores=[]),'office-study-01/helpers-only','exec'))
def tag(o,kind):o['source_id']=kind;o['proposal']='office-study-02';return o

common=data['common'];common['status']='independent02 correction; near halfwall confirmed to bookcase, balcony end open; main v19 untouched'
common['supersededFarReturn']=common.pop('shortReturn');common['supersededFarReturn']['currentStatus']='removed'
common['longLedge'].update(z=2000,lengthZ=2400)
common['nearHalfwall']={'x':5100,'endX':6835,'lengthX':1735,'bodyPlanZ':[4440,4560],'bodyThickness':120,'capPlanZ':[4400,4600],'capDepth':200,'topHeight':950,'bodyFinish':'matte warm white','capFinish':'matches sofa-back ledge in each option','endpoint':'right bookcase front,3mm finish joint','ownerConfirmedEndpoint':True}
common['farOpening']={'planZ':2000,'raisedReturnCount':0,'endCabinetCount':0,'furnitureRailingCount':0,'entry':'from balcony/south end','existingWindowAndExteriorGuardrail':'retained; these are not the removed interior furniture beam'}
common['overallFootprint']={'x':5100,'z':2000,'widthX':1735,'lengthZ':2600,'note':'includes confirmed near-end halfwall, not only desktop'}
common['northBookcaseDoor']={'modulePlanZ':[3976,4776],'operation':'two-track sliding opaque leaves, owner wall creates need to replace former swing opening','leafWidth':408,'travel':384,'frontLeafX':[6838,6856],'rearLeafX':[6858,6876],'wallEndX':6835,'minimumWallToFrontLeafGap':3,'status':'designer interface proposal, not selected hardware or installation approval'}
common['assumptions']=['near solid halfwall to bookcase explicitly confirmed by owner','950 high,120 body,200 cap and3mm finish joint are designer proposals','desk/sofa/chair positions retained','chair rear furniture gap408 remains tight and is not accepted as a passage','north bookcase sliding doors are a proposed response to halfwall, not current main-model changes','no new wall or furniture rail at balcony end; fixed glazing and outdoor guardrail stay','OFF artificial lights off with daylight retained']
for v in data['variants']:
 v['halfwallBodyFinish']='matte warm white';v['halfwallCapFinish']=v['ledgeFinish'];v['storage']='far-end cabinet removed; existing desktop shallow drawer retained only where originally present'
 v['design']='near solid halfwall to bookcase plus sofa-back ledge; completely open balcony end; same option palette retained'
 if v['id']=='A':v.update(support='slim pale-oak ledge and desktop supports; full near-end warm-white halfwall',storage='near-end shallow oak desktop drawer retained; no balcony-end cabinet')
 if v['id']=='B':v.update(accent='sage textile chair and navy task lamp',support='walnut ledge and desktop supports; full near-end warm-white halfwall',storage='no new end cabinet or drawer; right bookcase retained')
 if v['id']=='C':v.update(support='ivory ledge supports and concealed desktop frame; full near-end warm-white halfwall',storage='near-end shallow navy desktop drawer retained; no balcony-end cabinet')
data['sourceStudy']='office-study-01';data['userCorrection']='red near end solid halfwall connected to bookcase; blue far/window end no furniture obstruction'
records=[]

def bounds(o):
 points=[o.matrix_world@Vector(v) for v in o.bound_box]
 return {'x':[round(min(q.x for q in points)*1000,3),round(max(q.x for q in points)*1000,3)],'z':[round(-max(q.y for q in points)*1000,3),round(-min(q.y for q in points)*1000,3)],'h':[round(min(q.z for q in points)*1000,3),round(max(q.z for q in points)*1000,3)]}

for v in data['variants']:
 vid=v['id'];folder=OUT/vid;folder.mkdir(exist_ok=True)
 bpy.ops.wm.open_mainfile(filepath=str(OLD/vid/f'办公区-{vid}-独立提案.blend'));sc=bpy.context.scene;sc.frame_set(1)
 ledge=bpy.data.materials['Pale oak'] if vid=='A' else bpy.data.materials['Walnut'] if vid=='B' else bpy.data.materials['Ivory solid surface']
 white=bpy.data.materials['Warm white'];metal=bpy.data.materials['Dark metal'];glow=bpy.data.materials['Warm strip diffuser']
 for o in list(sc.objects):
  if o.get('source_id') in ['long-raised-ledge','short-raised-return'] or o.name.startswith(('Ledge support','Sage shallow end storage','Recessed long strip','Recessed return strip')):
   bpy.data.objects.remove(o,do_unlink=True)
 th=v['ledgeThickness'];rr=v['ledgeRadius']
 long=top('Sofa-back ledge2400 H950 open far end',5100,2000,950-th,200,2400,th,rr,ledge,'long-raised-ledge')
 for zz in [2040,3175,4330]:tag(box('Long ledge support02',5120,zz,0,55,45,950-th,ledge,6),'ledge-support')
 body=tag(box('Near solid halfwall to right bookcase',5100,4440,0,1735,120,950-th,white,10),'near-halfwall-solid-body')
 cap=top('Near halfwall cap1735x200 H950',5100,4400,950-th,1735,200,th,rr,ledge,'near-halfwall-cap')
 tag(box('Concealed long ledge light02',5280,2070,950-th-8,9,2250,8,glow,1),'long-ledge-light')
 tag(box('Concealed near cap light over desk only02',5350,4425,950-th-8,600,9,8,glow,1),'near-halfwall-light')
 near_light=light('Near halfwall indirect02','AREA',(5.65,-4.40,.90),8,.7,(5.65,-4.05,.75))
 # New full-width halfwall meets the bookcase. Model a bypass sliding pair for the north800 module.
 # Remove the former solid proxy carcass and swing leaves; keep cabinet envelope/placement fixed.
 for name in ['v19-book-hall-body','v19-book-hall-door-0','v19-book-hall-door-1']:
  if name in bpy.data.objects:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
 carcasses=[('back',7170,3976,0,18,800,2750),('south side',6878,3976,0,310,18,2750),('north side',6878,4758,0,310,18,2750),('top',6878,3994,2732,292,764,18),('base',6878,3994,80,292,764,18)]
 for name,x,z,h,w,d,hh in carcasses:tag(box('North sliding carcass02 '+name,x,z,h,w,d,hh,white,1),'bookcase')
 for level in [600,1200,1800,2400]:tag(box('North sliding shelf02',6888,3994,level,282,764,18,white,1),'bookcase')
 front=tag(box('North bookcase front sliding leaf02',6838,3980,4,18,408,2692,white,2),'bookcase-sliding-front')
 rear=tag(box('North bookcase rear sliding leaf02',6858,4364,4,18,408,2692,white,2),'bookcase-sliding-rear')
 front.location.y=-(3980+408/2)/1000;front.keyframe_insert(data_path='location',frame=1)
 front.location.y-=.384;front.keyframe_insert(data_path='location',frame=40)
 for fc in front.animation_data.action.fcurves:
  for point in fc.keyframe_points:point.interpolation='LINEAR'
 sc.frame_end=40;sc.frame_set(1)
 sc['parameters']=json.dumps(data,ensure_ascii=False);sc['proposalStatus']='Independent02: owner-confirmed near solid halfwall to bookcase, far balcony end clear. No main integration.'
 artificial=[o for o in sc.objects if o.type=='LIGHT' and o.name in ['Ledge indirect soft','Task lamp','Ambient reflected','Near halfwall indirect02']]
 emiss=glow.node_tree.nodes.get('Principled BSDF')
 for state in ['OFF','ON']:
  for o in artificial:o.hide_render=(state=='OFF')
  emiss.inputs['Emission Strength'].default_value=0 if state=='OFF' else 3
  sc.render.filepath=str(folder/f'{vid}-{state}-半墙敞开端实体参考.png');bpy.ops.render.render(write_still=True)
 model=folder/f'办公区-{vid}-近端半墙远端敞开-独立02.blend';bpy.ops.wm.save_as_mainfile(filepath=str(model))
 bodyname=body.name;capname=cap.name;longname=long.name;frontname=front.name;rearname=rear.name
 bpy.ops.wm.open_mainfile(filepath=str(model));sc=bpy.context.scene;sc.frame_set(1);bpy.context.view_layer.update()
 r={'variant':vid,'model':str(model),'nearSolidBody':bounds(bpy.data.objects[bodyname]),'nearCap':bounds(bpy.data.objects[capname]),'longLedge':bounds(bpy.data.objects[longname]),
    'monitorCount':sum(o.get('source_part')=='double-desk-monitor-screen-34' for o in sc.objects),'chairGroupCount':len(set(o.get('source_id') for o in sc.objects if o.get('source_id')=='office-chair-1')),
    'farReturnCount':sum(o.get('source_id')=='short-raised-return' for o in sc.objects),'farEndCabinetCount':sum(o.name.startswith('Sage shallow end storage') for o in sc.objects),
    'slidingDoorSamples':[]}
 for frame in [1,20,40]:
  sc.frame_set(frame);bpy.context.view_layer.update();fb=bounds(bpy.data.objects[frontname]);rb=bounds(bpy.data.objects[rearname])
  r['slidingDoorSamples'].append({'frame':frame,'front':fb,'rear':rb,'wallToFrontLeafGapX':fb['x'][0]-r['nearCap']['x'][1],'leafTrackGapX':rb['x'][0]-fb['x'][1]})
 assert r['nearCap']['h'][1]==950 and r['nearSolidBody']['h'][0]==0
 assert r['nearCap']['x']==[5100,6835] and r['nearCap']['z']==[4400,4600]
 assert r['longLedge']['z']==[2000,4400] and r['farReturnCount']==0 and r['farEndCabinetCount']==0
 assert r['monitorCount']==1 and r['chairGroupCount']==1
 assert all(p['wallToFrontLeafGapX']>=3 and p['leafTrackGapX']>=2 for p in r['slidingDoorSamples'])
 records.append(r)

after={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in baseline};assert after==baseline
(OUT/'设计参数.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'模型回读.json').write_text(json.dumps({'records':records,'baselineBefore':baseline,'baselineAfter':after,'mainUnchanged':True},ensure_ascii=False,indent=2),encoding='utf-8')
print('NEAR_HALFWALL_OPEN_FAR_COMPLETE',json.dumps({'models':3,'nearHalfwall':[1735,120,950],'farReturns':0,'mainUnchanged':True}))
