bl_space_type = {
    "name" : "Object Adder",
    "author" : "Bakkrimet",
    "Version" : (1,0),
    "blender" : (3,6,1),
    "location" : "View3d > Tool",
    "warning" : "",
    "wiki_url" : "",
    "category" : "Add Mesh",    
}



import bpy



def main(context):
    def clear_collection(collection):
        if collection:
            for obj in collection.objects:
                bpy.data.objects.remove(obj, do_unlink=True)
                               
    def initialize_collection():
        if collection_name in bpy.data.collections:
            collection = bpy.data.collections[collection_name]
            clear_collection(collection)
        else:
            collection = bpy.data.collections.new(collection_name)
            scene = bpy.context.scene
            scene.collection.children.link(bpy.data.collections[collection_name])
        return collection

    def create_cell(x, y):
        location = (x * (plane_size * 2), y * (plane_size * 2), 0)

    #            bpy.ops.object.empty_add(location=location)
    #            empty = bpy.context.object
    #            empty.name = f"{x:02d}_{y:02d}_holder"
    #            bpy.context.collection.objects.unlink(empty)
    #            collection.objects.link(empty)
                
        bpy.ops.mesh.primitive_plane_add(scale=(plane_size, plane_size, 1), enter_editmode=False, align='WORLD', location=location)
        plane = bpy.context.object
        plane.name = f"{x:02d}_{y:02d}_plane"
    #            bpy.context.collection.objects.unlink(plane)
    #            collection.objects.link(plane)
    #            plane.parent = empty
    #    plane.location = (0, 0, 0)
        return plane


    def get_cell(x, y):
        return plane_dict.get(x, {}).get(y)

    def delete_cell(x, y):
        specific_plane = get_cell(x, y)
        if specific_plane:
            collection.objects.unlink(specific_plane)
            del plane_dict[x][y]
            bpy.data.objects.remove(specific_plane, do_unlink=True)

    def menu_func(self, context):
        self.layout.operator(SimpleOperator.bl_idname, text=SimpleOperator.bl_label)
        
    collection_name = "GridPlanes"

    plane_dict = {}

    x_size = 5
    y_size = 5
    plane_size = 1
    scene = bpy.context.scene
    collection = initialize_collection()

    for x in range(x_size):
        plane_dict[x] = {}
        for y in range(y_size):
            plane = create_cell(x, y)
            plane_dict[x][y] = plane    
   

    delete_cell(4, 3)


class SimpleOperator(bpy.types.Operator):
    """d"""
    bl_idname = "object.simple_operator"
    bl_label = "Simple Object Operator"
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        main(context)
        return {'FINISHED'}


class LayoutDemoPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "WFC"
    bl_idname = "SCENE_PT_layout"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout

        scene = context.scene

        # Big render button
        layout.label(text="Big Button:")
        row = layout.row()
        row.scale_y = 3.0
        row.operator("object.simple_operator")


def register():
    bpy.utils.register_class(SimpleOperator)
#    bpy.types.VIEW3D_MT_object.append(menu_func)
    bpy.utils.register_class(LayoutDemoPanel)


def unregister():
    bpy.utils.unregister_class(SimpleOperator)
#    bpy.types.VIEW3D_MT_object.remove(menu_func)
    bpy.utils.unregister_class(LayoutDemoPanel)


if __name__ == "__main__":
    register()
