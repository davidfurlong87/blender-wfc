import bpy
import re

generated_modules = {  
}

class WFCModuleProperty(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    pos_x: bpy.props.StringProperty()
    neg_x: bpy.props.StringProperty()
    pos_y: bpy.props.StringProperty()
    neg_y: bpy.props.StringProperty()

class OBJECT_PT_WFCPanel(bpy.types.Panel):
    bl_label = "Module Gen"
    bl_idname = "OBJECT_PT_wfc"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "WFC"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Build Modules:")
        # layout.prop(context.scene, "rename_regex")
        layout.label(text="Commands:")
        
        row = layout.row()
        op = layout.operator("object.wfc_generate_modules")
        op = layout.operator("object.wfc_build_grid")


# def check_collection_exists(col_name):
#     for collection in bpy.data.collections:
#         if collection.name == col_name:
#             print('collection_exists')
#             return True
#     print('collection_not_found')
#     return False

# def clear_collection_and_return(collection_name):

#     bpy.ops.object.select_all(action='DESELECT')
#     old_modules = bpy.data.collections[collection_name].all_objects
#     for obj in old_modules:
#         bpy.data.objects[obj.name].select_set(True)
#             # TODO: delete module 
        
#             # TODO: unlink module
#             # bpy.context.scene. obj
#             # TODO: whatever else, clear datablock etc.
#     bpy.ops.object.delete() 
#     return bpy.data.collections[collection_name]




def build_wfc_collection(collection_name):
    if (check_collection_exists(collection_name)):
        return clear_collection_and_return(collection_name)
    else:
        bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(bpy.data.collections[collection_name])
        return bpy.data.collections[collection_name]
    
def add_new_module(base_module, collection):
    for instance in range(4):
        # instantiate new module
        new_module = base_module.copy()
        # create unique data
        new_module.data = new_module.data.copy()
        new_module.name = base_module.name + f"_{instance}"
        collection.objects.link(new_module)



class OBJECT_OT_GenerateModules(bpy.types.Operator):
    bl_idname = "object.wfc_generate_modules"
    bl_label = "Generate Modules"
    bl_description = "Renames mesh objects based on user-defined regex"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        base_modules = bpy.data.collections['wfc_base_modules'].all_objects
        modules_collection = build_wfc_collection('wfc_modules')
        
        for obj in base_modules:
            if obj.type == 'MESH':  
                print(obj.name)
                add_new_module(obj, modules_collection)
        return {'FINISHED'}

class OBJECT_OT_BuildGrid(bpy.types.Operator):
    bl_idname = "object.wfc_build_grid"
    bl_label = "Build Grid"
    bl_description = "Builds the grid"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        grid_collection = build_wfc_collection('wfc_grid')
        
        return {'FINISHED'}

PANELS = [
    OBJECT_PT_WFCPanel
]

OPERATORS = [
    OBJECT_OT_GenerateModules,
    OBJECT_OT_BuildGrid
]

WFC_CLASSES = PANELS + OPERATORS

def register():
    bpy.utils.register_class(WFCModuleProperty)

    for wfc_class in WFC_CLASSES:
        bpy.utils.register_class(wfc_class)
    # bpy.utils.register_class(OBJECT_PT_WFCPanel)
    # bpy.utils.register_class(OBJECT_OT_GenerateModules)
    # bpy.utils.register_class(OBJECT_OT_BuildGrid)

    bpy.types.Scene.base_wfc_modules_collection_name = bpy.props.StringProperty(
        name="Regex Pattern",
        description="Name for Collection of prototypes.",
        default="wfc_base_modules"
    )
    bpy.types.Scene.wfc_modules_collection_name = bpy.props.StringProperty(
        name="Regex Pattern",
        description="Name for Collection of WFC modules.",
        default="wfc_modules"
    )
    bpy.types.Scene.wfc_grid_x = bpy.props.IntProperty(
        name="Grid Size X",
        description="Grid x size.",
        default=10
    )
    bpy.types.Scene.wfc_grid_y = bpy.props.IntProperty(
        name="Grid Size Y",
        description="Grid y size.",
        default=10
    )


def unregister():
    bpy.utils.unregister_class(WFCModuleProperty)
    for wfc_class in WFC_CLASSES:
        bpy.utils.unregister_class(wfc_class)
    # bpy.utils.unregister_class(OBJECT_PT_WFCPanel)
    # bpy.utils.unregister_class(OBJECT_OT_GenerateModules)
    # bpy.utils.unregister_class(OBJECT_OT_BuildGrid)


    del bpy.types.Scene.base_wfc_modules_collection_name
    del bpy.types.Scene.wfc_modules_collection_name


if __name__ == "__main__":
    register()

