# from wfctools import *

from .wfc_collections import COLLECTION_PANELS, COLLECTION_OPERATORS
import sys

# if "wfc_collections" in locals():
import importlib
importlib.reload(wfc_collections)


# importlib.reload(wfctools)


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


class OBJECT_PT_GenerateAndAssign(bpy.types.Panel):
    """Panel for creating a full vertex group"""
    bl_label = "Add and Assign Label"
    bl_idname = "OBJECT_PT_GenerateAndAssign"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = bl_category_name

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "vertex_group_name")
        layout.operator("object.add_wfc_primitives")


class OBJECT_OT_AddWfcPrimitives(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.add_wfc_primitives"
    bl_label = "add stuff debug"

    #    @classmethod
    #    def poll(cls, context):
    #        space = context.space_data
    #        return space.type == 'NODE_EDITOR'

    def execute(self, context):
        # check if collections exist


        create_objects_with_random_types()

        return {'FINISHED'}


def create_objects_with_random_types():
    objects = []
    for i in range(20):
        bpy.ops.mesh.primitive_cube_add(location=(i * 2, 0, 0))
        obj = bpy.context.object
        obj.name = f"Object_{i}"
        obj.my_type = random.choice(['TYPE_A', 'TYPE_B', 'TYPE_C'])
        objects.add(obj)

    assign_random_types_to_objects(objects)


def assign_random_types_to_objects(objects):
    for obj in objects:
        obj.my_type = random.choice(['TYPE_A', 'TYPE_B', 'TYPE_C'])
    for obj in bpy.data.objects:
        if hasattr(obj, "my_type"):
            print(obj.name, obj.my_type)


enum_items = [
    ('ROAD_STRAIGHT', "Road_Straight", ""),
    ('CORNER', "Corner", ""),
    ('BUILDING', "Building", "")
]
enum_items_keys = [
    'ROAD_STRAIGHT',
    'CORNER',
    'BUILDING'
]


def create_objects_with_random_types():
    #    register_enum_property()

    for i in range(20):
        bpy.ops.mesh.primitive_cube_add(location=(i * 2, 0, 0))
        obj = bpy.context.object
        obj.name = f"Object_{i}"
        obj.my_type = random.choice(enum_items_keys)


PANELS = [
             OBJECT_PT_GenerateAndAssign,

         ] + COLLECTION_PANELS

OPERATORS = [
                OBJECT_OT_AddWfcPrimitives,

            ] + COLLECTION_OPERATORS

REGISTER_CLASSES = PANELS + OPERATORS


def register():
    for r_class in REGISTER_CLASSES:
        bpy.utils.register_class(r_class)

    bpy.types.Object.my_type = bpy.props.EnumProperty(
        name="Object Type",
        description="Classification of object",
        items=enum_items
    )

    bpy.types.Scene.clear_collections = bpy.props.BoolProperty(
        name="Clear Collections",
        default=True
    )

def unregister():
    for r_class in REGISTER_CLASSES:
        bpy.utils.unregister_class(r_class)
    del bpy.types.Object.my_type


if __name__ == "__main__":
    register()
