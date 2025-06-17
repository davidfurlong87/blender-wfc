import bpy


def get_cell(x, y):
    return plane_dict.get(x, {}).get(y)

def delete_cell(x, y):
    specific_plane = get_cell(x, y)
    if specific_plane:
        collection.objects.unlink(specific_plane)
        del plane_dict[x][y]
        bpy.data.objects.remove(specific_plane, do_unlink=True)
    
    
collection_name = "GridPlanes"


plane_dict = {}

x_size = 5
y_size = 5
plane_size = 1






def main(context):
    collection = initialize_collection()

    for x in range(x_size):
        plane_dict[x] = {}
        for y in range(y_size):
     
            location = (x * (plane_size * 2), y * (plane_size * 2), 0)

            bpy.ops.object.empty_add(location=location)
            empty = bpy.context.object
            empty.name = f"{x:02d}_{y:02d}_holder"
            bpy.context.collection.objects.unlink(empty)
            collection.objects.link(empty)
            
            bpy.ops.mesh.primitive_plane_add(scale=(plane_size, plane_size, 1), enter_editmode=False, align='WORLD', location=location)
            plane = bpy.context.object
            plane.name = f"{x:02d}_{y:02d}_plane"
            bpy.context.collection.objects.unlink(plane)
            collection.objects.link(plane)
            plane.parent = empty
            plane.location = (0, 0, 0)
            
            plane_dict[x][y] = plane    

    print(get_cell(x, y))
    delete_cell(4, 3)


class SimpleOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.simple_operator"
    bl_label = "Simple Object Operator"

    def execute(self, context):
        main(context)
        return {'FINISHED'}

# Register and add to the "object" menu (required to also use F3 search "Simple Object Operator" for quick access).
def register():
    bpy.utils.register_class(SimpleOperator)


def unregister():
    bpy.utils.unregister_class(SimpleOperator)


if __name__ == "__main__":
    register()

    # test call
#    bpy.ops.object.simple_operator()
