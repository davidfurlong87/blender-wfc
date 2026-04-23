import bpy
from .wfc_values import CollectionNames
from .collectiontools import (
    ensure_collection,
    ensure_primitives_collection,
    ensure_modules_collection,
    ensure_grid_collection,
)

bl_category_name = "wfc"


class OBJECT_PT_WFCTree(bpy.types.Panel):
    """Utility panel for inspecting and repairing the WFC collection tree.

    The tree is created lazily as operators run, so pressing this button
    is never required.  It is retained as a convenience for users who
    want to pre-create the full hierarchy, or to repair it after an
    accidental manual deletion.
    """
    bl_label = "WFC Tree"
    bl_idname = "OBJECT_PT_WFCTree"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = bl_category_name

    def draw(self, context):
        layout = self.layout
        layout.label(text="Collection tree is built automatically.", icon='INFO')
        layout.label(text="Use this only to repair a broken tree.")
        layout.operator("object.wfc_ensure_tree", icon='FILE_FOLDER')


class OBJECT_OT_WFCEnsureTree(bpy.types.Operator):
    """Ensure the full WFC collection hierarchy exists.

    Non-destructive: creates any missing static collections and the default
    category subcollections.  Never clears or deletes existing content.
    Safe to run at any time without losing work.
    """
    bl_idname = "object.wfc_ensure_tree"
    bl_label = "Reset/Ensure WFC Tree"

    def execute(self, context):
        # Static roots — always present
        root = ensure_collection(CollectionNames.Root.value)
        ensure_collection(CollectionNames.Primitives.value, parent=root)
        ensure_collection(CollectionNames.Modules.value,    parent=root)
        ensure_collection(CollectionNames.Grid.value,       parent=root)
        ensure_collection(CollectionNames.Debug.value,      parent=root)

        # Default category subcollections
        from .wfc_values import GridCategory
        for category in (GridCategory.OUTER_GRID, GridCategory.BUILDING):
            ensure_primitives_collection(category)
            ensure_modules_collection(category)
            ensure_grid_collection(category)

        self.report({'INFO'}, "WFC collection tree is intact.")
        return {'FINISHED'}


COLLECTION_PANELS = [
    OBJECT_PT_WFCTree,
]

COLLECTION_OPERATORS = [
    OBJECT_OT_WFCEnsureTree,
]
