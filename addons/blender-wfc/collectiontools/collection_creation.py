import bpy


def clear_collection(collection):
    if collection:
        for obj in collection.objects:
            bpy.data.objects.remove(obj, do_unlink=True)

def delete_objects_and_meshes(objs_to_delete):
    # Deselect all first
    bpy.ops.object.select_all(action='DESELECT')

    for obj in objs_to_delete:
        # Deselect all others and select the target object
        obj.select_set(True)

        # Store mesh data before deleting the object
        mesh_data = obj.data
        obj_name = obj.name

        # Delete the object
        bpy.ops.object.delete()

        # if mesh_data.users == 0:
        bpy.data.meshes.remove(mesh_data)

def check_collection_exists(collection_name):
    if collection_name in bpy.data.collections:
        return True
    else:
        return False




def clear_collection_and_return(collection_name):

    objs_to_delete = bpy.data.collections[collection_name].all_objects
    delete_objects_and_meshes(objs_to_delete)
    return bpy.data.collections[collection_name]

def build_or_return_collection(collection_name, b_empty_collection = False):
    if collection_name in bpy.data.collections:
        collection = bpy.data.collections[collection_name]
        if b_empty_collection:
            clear_collection(collection)
    else:
        collection = bpy.data.collections.new(collection_name)
        scene = bpy.context.scene
        scene.collection.children.link(bpy.data.collections[collection_name])
    return collection