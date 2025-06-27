import bpy
from mathutils import Vector, Matrix

# -------------------------------------------
# ------------OBJECT GETTER FUNCS---------------
# -------------------------------------------
#  Functions
def get_selected_objects_of_type(*mesh_types):
    if len(mesh_types) == 0:
        return [obj for obj in bpy.context.selected_objects]
    else:
        return [obj for obj in bpy.context.selected_objects if obj.type in mesh_types]

def get_all_objects_of_type(*mesh_types):
    if len(mesh_types) == 0:
        return [obj for obj in bpy.data.objects]
    else:
        return [obj for obj in bpy.data.objects if obj.type in mesh_types]

def get_collection_objects_of_type(collection, *mesh_types):
    if len(mesh_types) == 0:
        return [obj for obj in collection.objects]
    else:
        return [obj for obj in collection.objects if obj.type in mesh_types]

def get_selected_meshes():
    return get_selected_objects_of_type('MESH')


def get_active_object():
    return bpy.context.active_object


# Collections

# -------------------------------------------
# ------------COLLECTION FUNCS---------------
# -------------------------------------------
def link_object_to_single_collection(obj, collection_to_keep):
    collection_to_keep.objects.link(obj)
    unlink_from_other_collections(obj, collection_to_keep)

def unlink_from_other_collections(obj, collection_to_keep):
    for collection in obj.users_collection:
        if collection.name != collection_to_keep.name:
            collection.objects.unlink(obj)
            
def link_selected_objects_to_collection(collection):
    for obj in get_selected_objects_of_type():
        if obj.name not in collection.objects:
            link_object_to_single_collection(obj, collection)


# TODO: Check for usage and remove
# Deprecated
def clear_collection(collection):
    if collection:
        for obj in collection.objects:
            bpy.data.objects.remove(obj, do_unlink=True)

def clear_collection_of_type(collection, *mesh_types):
    for obj in [obj for obj in collection.objects if obj.type in mesh_types]:
        bpy.data.objects.remove(obj, do_unlink=True)

def check_collection_exists(collection_name):
    if collection_name in bpy.data.collections:
        return True
    else:
        return False
    
def get_collection_by_name(collection_name):
    # TODO: Does this work? bpy.data.collections.get(target_collection_name)
    # Assumes the collection exists
    return bpy.data.collections[collection_name]

def get_active_collection():
    return bpy.context.collection


def create_new_collection(collection_name):
    return bpy.data.collections.new(collection_name)

def get_or_create_collection(collection_name, b_delete_objects=False):
    if check_collection_exists(collection_name):
        if b_delete_objects:
            clear_collection(bpy.data.collections[collection_name])
        return get_collection_by_name(collection_name)
    else:
        collection = create_new_collection(collection_name)
        bpy.context.scene.collection.children.link(collection)
        return collection

def move_objects_to_new_collection(collection_name):
    bpy.ops.object.move_to_collection(collection_index=0, is_new=True, new_collection_name=collection_name)


# TODO: Check for usage and remove
# Deprecated
def delete_object_by_name(obj_name):
    bpy.data.objects.remove(bpy.data.objects[obj_name])


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



# TODO: Check for usage and remove
# @Deprecated
def get_all_objects_from_collection(collection_name):
    return [obj for obj in get_collection_by_name(collection_name).objects]

def clear_collection_and_return(collection_name):

    # objs_to_delete = bpy.data.collections[collection_name].all_objects
    # delete_objects_and_meshes(objs_to_delete)
    delete_objects_and_meshes(get_all_objects_from_collection(collection_name))
    get_all_objects_from_collection(collection_name)
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