import bpy

class GenerateORGBonesOperator(bpy.types.Operator):
    bl_idname = 'pose.generate_org_bones'
    bl_label = '[HN] Generate ORG Bones'
    bl_options = {'REGISTER', 'UNDO'}

    org_bone_collection_name: bpy.props.StringProperty(name = "ORG Bone Collection Name", default = "ORG")

    def add_constraint(self, context, def_pose_bone, org_pose_bone):
        '''Add a copy transform constraint to the bone'''
        if org_pose_bone is not None:
            constraint = def_pose_bone.constraints.new('COPY_TRANSFORMS')
            constraint.name = "Copy Transforms from ORG"
            constraint.target = context.active_object
            constraint.subtarget = org_pose_bone.name
            constraint.target_space = 'WORLD'
            constraint.owner_space = 'WORLD'

    def add_org_bone(self, context, def_edit_bone, org_bone_name):
        '''Add a new bone to the armature'''
        org_edit_bone = context.active_object.data.edit_bones.new(org_bone_name)
        org_edit_bone.head = def_edit_bone.head
        org_edit_bone.tail = def_edit_bone.tail
        org_edit_bone.roll = def_edit_bone.roll
    
    def execute(self, context):
        '''Execute the operator'''
        if(len(context.selected_pose_bones)) == 0:
            return {'CANCELLED'}
        org_bone_collection = None
        if self.org_bone_collection_name not in bpy.data.collections:
            org_bone_collection = context.active_object.data.collections.new(name = self.org_bone_collection_name)
        else:
            org_bone_collection = context.active_object.data.collections[self.org_bone_collection_name]
        target_bones = context.selected_pose_bones
        for def_pose_bone in target_bones:
            if def_pose_bone.name.startswith('DEF_'):
                org_bone_name = def_pose_bone.name.replace('DEF_', 'ORG_')
                org_pose_bone = None
                if org_bone_name in context.active_object.pose.bones:
                    org_pose_bone = context.active_object.pose.bones[org_bone_name]
                    bpy.ops.object.mode_set(mode = 'EDIT')
                    org_edit_bone = context.active_object.data.edit_bones[org_bone_name]
                    if org_bone_name not in org_edit_bone.collections:
                        org_bone_collection.assign(org_pose_bone)
                    bpy.ops.object.mode_set(mode = 'POSE')
                    if len(def_pose_bone.constraints) == 0:
                        self.add_constraint(context, def_pose_bone, org_pose_bone)
                    else:
                        need_add_constraint = True
                        for constraint in def_pose_bone.constraints:
                            if constraint.type == 'COPY_TRANSFORMS' and constraint.target == context.active_object and constraint.subtarget == org_bone_name:
                                need_add_constraint = False
                                break
                        if need_add_constraint:
                            self.add_constraint(context, def_pose_bone, org_pose_bone)
                else:
                    bpy.ops.object.mode_set(mode = 'EDIT')
                    def_edit_bone = context.active_object.data.edit_bones[def_pose_bone.name]
                    self.add_org_bone(context, def_edit_bone, org_bone_name)

                    bpy.ops.object.mode_set(mode = 'POSE')
                    org_pose_bone = context.active_object.pose.bones[org_bone_name]
                    self.add_constraint(context, def_pose_bone, org_pose_bone)

        bpy.ops.object.mode_set(mode = 'EDIT')
        root_edit_bone = context.active_object.data.edit_bones['ROOT']
        for def_pose_bone in target_bones:
            if def_pose_bone.name.startswith('DEF_'):
                def_bone_name = def_pose_bone.name
                def_edit_bone = context.active_object.data.edit_bones[def_bone_name]
                def_parent_edit_bone = def_edit_bone.parent
                org_edit_bone = context.active_object.data.edit_bones[def_bone_name.replace("DEF_", "ORG_")]
                if def_parent_edit_bone is not None:
                    if def_parent_edit_bone.name is not "ROOT":
                        org_parent_edit_bone = context.active_object.data.edit_bones[def_parent_edit_bone.name.replace("DEF_", "ORG_")]
                        org_edit_bone.parent = org_parent_edit_bone
                    else:
                        if root_edit_bone is not None:
                            org_edit_bone.parent = root_edit_bone
                org_bone_collection.assign(org_edit_bone)
        bpy.ops.object.mode_set(mode = 'POSE')
        

        return {'FINISHED'}
    
def menu_func(self, context):
    '''Add the operator to the menu'''
    self.layout.operator(GenerateORGBonesOperator.bl_idname, text = GenerateORGBonesOperator.bl_label)
    
def register():
    '''Register class'''
    bpy.utils.register_class(GenerateORGBonesOperator)
    bpy.types.VIEW3D_MT_pose.append(menu_func)

def unregister():
    '''Unregister class'''
    bpy.types.VIEW3D_MT_pose.remove(menu_func)
    bpy.utils.unregister_class(GenerateORGBonesOperator)