bl_info = {'name':'Home Design · 100 mm','author':'HomeDesign local project','version':(1,0,0),'blender':(4,5,0),'category':'3D View'}
import bpy, json
from pathlib import Path

class HOMEDESIGN_OT_move(bpy.types.Operator):
    bl_idname='home_design.move'
    bl_label='移动家具 100 mm'
    bl_options={'REGISTER','UNDO'}
    axis:bpy.props.EnumProperty(items=[('X','X',''),('Y','Y','')],default='X')
    direction:bpy.props.IntProperty(default=1,min=-1,max=1)

    @classmethod
    def poll(cls,context):
        return any(o.get('home_design_role')=='furniture' for o in context.selected_objects)

    def execute(self,context):
        index=0 if self.axis=='X' else 1
        for obj in context.selected_objects:
            if obj.get('home_design_role')=='furniture':
                obj.location[index]=round(obj.location[index]+self.direction*0.1,6)
        return {'FINISHED'}

class HOMEDESIGN_OT_export_layout(bpy.types.Operator):
    bl_idname='home_design.export_layout'
    bl_label='保存当前家具位置'

    def execute(self,context):
        root=Path(context.scene.get('home_design_project_root',r'D:\AI-Yang.cn\HomeDesign'))
        target=root/'03_layout/blender-layout-latest.json'
        target.parent.mkdir(parents=True,exist_ok=True)
        objects=[]
        for obj in context.scene.objects:
            if obj.get('home_design_role')=='furniture':
                x=round(obj.location.x*1000,3);z=round(-obj.location.y*1000,3)
                objects.append(dict(id=obj['source_id'],x=x,z=z,
                    dx=round(x-obj['import_x_mm'],3),dz=round(z-obj['import_z_mm'],3),
                    rotation_z_degrees=round(obj.rotation_euler.z*180/3.141592653589793,3)))
        target.write_text(json.dumps(dict(units='mm',revision=5,relative_to='geometry-master-v05',objects=objects),ensure_ascii=False,indent=2),encoding='utf-8')
        self.report({'INFO'},'已保存：03_layout/blender-layout-latest.json')
        return {'FINISHED'}

class HOMEDESIGN_PT_movement(bpy.types.Panel):
    bl_label='家具位置 · 100 mm'
    bl_idname='HOMEDESIGN_PT_movement'
    bl_space_type='VIEW_3D';bl_region_type='UI';bl_category='家装'

    def draw(self,context):
        layout=self.layout
        obj=context.active_object
        if not obj or obj.get('home_design_role')!='furniture':
            layout.label(text='单击选择家具后移动')
            return
        layout.label(text=obj.get('display_name',obj.name))
        layout.label(text='每次 100 mm；Ctrl+Z 撤销')
        row=layout.row(align=True)
        op=row.operator('home_design.move',text='← 100');op.axis='X';op.direction=-1
        op=row.operator('home_design.move',text='100 →');op.axis='X';op.direction=1
        row=layout.row(align=True)
        op=row.operator('home_design.move',text='↑ 100');op.axis='Y';op.direction=1
        op=row.operator('home_design.move',text='100 ↓');op.axis='Y';op.direction=-1
        layout.separator()
        layout.label(text=f'图面 X：{obj.location.x*1000:.0f} mm')
        layout.label(text=f'图面 Z：{-obj.location.y*1000:.0f} mm')
        layout.operator('home_design.export_layout',text='保存当前家具位置')

CLASSES=(HOMEDESIGN_OT_move,HOMEDESIGN_OT_export_layout,HOMEDESIGN_PT_movement)
def register():
    for cls in CLASSES:bpy.utils.register_class(cls)
def unregister():
    for cls in reversed(CLASSES):bpy.utils.unregister_class(cls)
