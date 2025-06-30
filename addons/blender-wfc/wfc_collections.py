import bpy
import random
from bpy.props import BoolProperty, EnumProperty, StringProperty, FloatProperty
from .wfc_values import CollectionNames

from .collectiontools.collection_creation import build_or_return_collection
from .collectiontools import *

bl_category_name = "wfc"

class OBJECT_PT_BuildCollections(bpy.types.Panel):
    bl_label = "Build Collections"
    bl_idname = "OBJECT_PT_BuildCollections"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = bl_category_name

    def draw(self, context):
        layout = self.layout
        # layout.prop(context.scene, "clear_collections")
        layout.operator("object.build_default_collections")

class OBJECT_OT_BuildDefaultCollections(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.build_default_collections"
    bl_label = "build collections debug"

    def execute(self, context):
        
        collections_to_create = [
            CollectionNames.Grid.value,
            CollectionNames.Modules.value,
            CollectionNames.Primitives.value
        ]
        # TODO: var needed?
        default_collections = [build_or_return_collection(collection_to_create, True) for collection_to_create in collections_to_create]

        return {'FINISHED'}


COLLECTION_PANELS = [
    OBJECT_PT_BuildCollections,
]

COLLECTION_OPERATORS = [
    OBJECT_OT_BuildDefaultCollections,

]
