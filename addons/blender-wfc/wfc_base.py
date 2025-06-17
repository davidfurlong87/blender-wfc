import bpy



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


