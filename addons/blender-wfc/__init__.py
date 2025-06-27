# from wfctools import *
from bpy.props import BoolProperty, IntProperty, StringProperty
from .wfc_collections import COLLECTION_PANELS, COLLECTION_OPERATORS
import sys

# if "wfc_collections" in locals():
import importlib
importlib.reload(wfc_collections)


# importlib.reload(wfctools)
from .wfc_values import bl_category_name, CollectionNames
from .collectiontools.collection_creation import *

import bpy
import random
from bpy.props import BoolProperty, EnumProperty, StringProperty, FloatProperty

bl_info = {
    "name": "wfc",
    "author": "",
    "description": "efc mod",
    "blender": (2, 80, 0),
    "location": "View3D",
    "warning": "",
    "category": "Generic"
}

bl_category_name = "wfc"

aspects = ["posX", "negX", "posY", "negY"]

class OBJECT_PT_GenerateAndAssign(bpy.types.Panel):
    """Panel for creating a full vertex group"""
    bl_label = "Debug Menu"
    bl_idname = "OBJECT_PT_GenerateAndAssign"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = bl_category_name

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "debug_text_separator")
        layout.prop(context.scene, "clear_collections")

        layout.operator("object.add_wfc_primitives")
        layout.operator("object.clear_wfc_primitives")
        layout.operator("object.add_wfc_text")
        layout.operator("object.clear_wfc_text")
        obj = context.object
        if obj:
            layout.prop(obj, "primitive_type")


class OBJECT_OT_AddWfcPrimitives(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.add_wfc_primitives"
    bl_label = "add stuff debug"

    def execute(self, context):
        # check if collections exist
        objects = []
        primitives_collection = get_collection_by_name(CollectionNames.Primitives.value)
        for i in range(20):
            bpy.ops.mesh.primitive_cube_add(location=(i * 2, 0, 0))
            obj = bpy.context.object
            obj.name = f"Foo_{i}"
            print(obj.name)
            objects.append(obj)

        assign_random_types_to_objects(objects)
        for obj in objects:
            link_object_to_single_collection(obj, primitives_collection)
        return {'FINISHED'}

class OBJECT_OT_ClearWfcPrimitives(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.clear_wfc_primitives"
    bl_label = "clear wfc debug"

    def execute(self, context):
        delete_objects_and_meshes(
            get_all_objects_from_collection(CollectionNames.Primitives.value)
            )
        return {'FINISHED'}

class OBJECT_OT_AddWfcText(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.add_wfc_text"
    bl_label = "add debug text"

    def execute(self, context):
        primitive_collection = get_collection_by_name(CollectionNames.Primitives.value)
        old_text_objects = get_collection_objects_of_type(primitive_collection, 'FONT')
        if len(old_text_objects) > 0:
            delete_objects_and_meshes(old_text_objects)
        primitives = get_all_objects_from_collection(CollectionNames.Primitives.value)
        if len(primitives) > 0:
            for primitive in primitives:
                add_wfc_debug_text(primitive)
               
        return {'FINISHED'}

class OBJECT_OT_ClearWfcText(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.clear_wfc_text"
    bl_label = "clear debug text"

    def execute(self, context):
        primitive_collection = get_collection_by_name(CollectionNames.Primitives.value)
        old_text_objects = get_collection_objects_of_type(primitive_collection, 'FONT')
        if len(old_text_objects) > 0:
            delete_objects_and_meshes(old_text_objects)

        return {'FINISHED'}

def create_objects_with_random_types():
    objects = []
    for i in range(20):
        bpy.ops.mesh.primitive_cube_add(location=(i * 2, 0, 0))
        obj = bpy.context.object
        obj.name = f"Primitive_{i}"
        # obj.primitive_type = random.choice(['TYPE_A', 'TYPE_B', 'TYPE_C'])
        objects.add(obj)
        print(obj.name, obj.primitive_type)

    assign_random_types_to_objects(objects)


def assign_random_types_to_objects(objects):
    for obj in objects:
        print(obj.name)
        prim_type = random.choice(enum_items_keys)
        obj.data['PrimitiveType'] = prim_type
        print(f"Obj is: {obj.name}, prim_type: {prim_type}")
        obj.primitive_type = random.choice(enum_items_keys)
    # for obj in bpy.data.objects:
    #     if hasattr(obj, "primitive_type"):
    #         print(obj.name, obj.primitive_type)

def add_wfc_debug_text(mesh):
    # objs = get_collection_objects_of_type(collection, 'MESH')

    for aspect in aspects:
        bpy.ops.object.text_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        bpy.context.object.data.align_x = 'CENTER'
        text_obj = bpy.context.active_object
        text_obj.name = f"{mesh.name}_text_{aspect}"
        text_obj.data.body = f"{mesh.name}_text_{aspect}_db"
        link_object_to_single_collection(text_obj, get_collection_by_name(CollectionNames.Primitives.value))

    # separator_y = Vector(bpy.types.Scene.debug_text_separator).y
    # median_x = median_point_x = get_median_point_of_objects(get_collection_objects_of_type(collection), dimension='x')
    # lowest_y = get_lowest_y_from_objects(get_collection_objects_of_type(collection))



    # text_obj.location = Vector((median_x, lowest_y - separator_y, 0))


# enum_items = [
#     ('ROAD_STRAIGHT', "Road_Straight", ""),
#     ('CORNER', "Corner", ""),
#     ('BUILDING', "Building", "")
# ]
enum_items_keys = [
    'ROAD_STRAIGHT',
    'CORNER',
    'BUILDING'
]


# def create_objects_with_random_types():
#     #    register_enum_property()

#     for i in range(20):
#         bpy.ops.mesh.primitive_cube_add(location=(i * 2, 0, 0))
#         obj = bpy.context.object
#         obj.name = f"Object_{i}"
#         obj.primitive_type = random.choice(enum_items_keys)


PANELS = [
             OBJECT_PT_GenerateAndAssign,

         ] + COLLECTION_PANELS

OPERATORS = [
                OBJECT_OT_AddWfcPrimitives,
                OBJECT_OT_ClearWfcPrimitives,
                OBJECT_OT_AddWfcText,
                OBJECT_OT_ClearWfcText

            ] + COLLECTION_OPERATORS

REGISTER_CLASSES = PANELS + OPERATORS


def register():
    for r_class in REGISTER_CLASSES:
        bpy.utils.register_class(r_class)

    bpy.types.Object.primitive_type = bpy.props.EnumProperty(
        name="Object Type",
        description="Classification of object",
        items=[
    ('ROAD_STRAIGHT', "Road_Straight", ""),
    ('CORNER', "Corner", ""),
    ('BUILDING', "Building", "")
]
    )

    bpy.types.Scene.clear_collections = bpy.props.BoolProperty(
        name="Clear Collections",
        default=True
    )


    bpy.types.Scene.debug_text_separator = bpy.props.FloatVectorProperty(
        name="",
        description="Vector by which text will be separated."
    )

def unregister():
    for r_class in REGISTER_CLASSES:
        bpy.utils.unregister_class(r_class)  
    
    del bpy.types.Scene.clear_collections
    del bpy.types.Scene.debug_text_separator
    del bpy.types.Object.primitive_type

if __name__ == "__main__":
    register()
