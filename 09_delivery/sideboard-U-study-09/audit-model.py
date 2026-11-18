from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
out=Path('D:/AI-Yang.cn/HomeDesign/09_delivery/sideboard-U-study-09')
bpy.ops.wm.open_mainfile(filepath=str(out/'同色等高U形餐岛-完整下拉上柜.blend'))
scene=bpy.context.scene;top=bpy.data.objects['continuous-U-top-880-09']
bm=bmesh.new();bm.from_mesh(top.data)
remaining=set(bm.verts);components=0
while remaining:
    components+=1;stack=[remaining.pop()]
    while stack:
        v=stack.pop()
        for e in v.link_edges:
            nxt=e.other_vert(v)
            if nxt in remaining:remaining.remove(nxt);stack.append(nxt)
manifold=all(e.is_manifold for e in bm.edges);bm.free()
assert components==1 and manifold
def bounds(o):
    pts=[o.matrix_world@Vector(v) for v in o.bound_box]
    return dict(u=[round(min(p.x for p in pts)*1000,3),round(max(p.x for p in pts)*1000,3)],
      v=[round(-max(p.y for p in pts)*1000,3),round(-min(p.y for p in pts)*1000,3)],
      h=[round(min(p.z for p in pts)*1000,3),round(max(p.z for p in pts)*1000,3)])
poses={}
for frame in (1,30,45,60):
    scene.frame_set(frame);bpy.context.view_layer.update()
    poses[str(frame)]=dict(door=bounds(bpy.data.objects['complete-upper-door-4-09']),
       trays=[bounds(o) for o in scene.objects if o.name.startswith('pulldown-4-tray')],
       basket_location=list(bpy.data.objects['pulldown-assembly-4-09'].location))
assert poses['1']['door']['v']==[781,800]
assert poses['45']['basket_location'][2]==0
assert abs(poses['45']['basket_location'][1]+.385)<.00001
assert abs(poses['60']['basket_location'][2]+.385)<.00001
assert sorted(t['h'][0] for t in poses['60']['trays'])==[1505,1729]
result=dict(single_connected_U_mesh=True,watertight_raw_top_mesh=manifold,
   one_top_material=len(top.data.materials)==1,top_bounds=bounds(top),animation_poses=poses,
   real_hardware_kinematics_certified=False,human_reach_certified=False,
   explanation='illustrative door-open, forward-then-down sequence; specific hardware sweep, side-access station and load remain pending')
(out/'native-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print('Native U mesh, closed door, and illustrative deployment poses passed. No file saved over the model.')
