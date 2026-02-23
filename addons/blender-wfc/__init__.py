import bpy
import random
from bpy.props import BoolProperty, IntProperty, EnumProperty, StringProperty, FloatProperty, PointerProperty

from math import radians
from enum import Enum
import sys

# ============================================================================
# Module Reloading System
# ============================================================================
# This block ensures that when the addon is reloaded (disabled/enabled),
# all modules are properly reloaded in dependency order.
# See docs/MODULE_RELOADING_GUIDE.md for detailed explanation.

if "bpy" in locals():
    import importlib

    # Level 0: Base modules with no internal dependencies
    if "wfc_values" in locals():
        importlib.reload(wfc_values)
    if "wfc_enums" in locals():
        importlib.reload(wfc_enums)

    # Level 1: Modules that depend only on Level 0
    if "wfc_materials" in locals():
        importlib.reload(wfc_materials)
    # Subpackage modules
    from .collectiontools import collection_creation
    importlib.reload(collection_creation)

    # Level 2: Modules that depend on Level 0-1
    if "wfc_classes" in locals():
        importlib.reload(wfc_classes)
    if "primitive_generation_tools" in locals():
        importlib.reload(primitive_generation_tools)
    if "helper_functions" in locals():
        importlib.reload(helper_functions)

    # Level 3: Modules that depend on Level 0-2
    if "primitive_data_actual" in locals():
        importlib.reload(primitive_data_actual)
    # wfc_grid_builder removed in Phase 4 - functionality moved to adapter
    if "wfc_plots" in locals():
        importlib.reload(wfc_plots)
    if "wfc_plot_tools" in locals():
        importlib.reload(wfc_plot_tools)

    # Level 4: Modules that depend on Level 0-3
    if "primitive_data" in locals():
        importlib.reload(primitive_data)
    if "wfc_collections" in locals():
        importlib.reload(wfc_collections)
    if "wfc_operators" in locals():
        importlib.reload(wfc_operators)

# ============================================================================
# Imports
# ============================================================================
# All imports happen AFTER the reload block to ensure we get the latest versions

from .wfc_values import bl_category_name, CollectionNames, module_size, primitive_offset_x
from .wfc_enums import CONNECTORS, PRIMITIVE_TYPES, CUSTOM_PRIMITIVE_TYPES
from .wfc_materials import build_all_primitive_materials, MaterialPrimitives
from .collectiontools.collection_creation import *
from .wfc_classes import WFCModule, WFCCell, Primitive, Axis, build_module_pairs
from .primitive_generation_tools import *
from .primitive_data_actual import *
from .primitive_data import build_default_primitives, PrimitiveModules, PRIMITIVE_OPERATORS, PRIMITIVE_PANELS, get_primitive_type_items
# wfc_grid_builder removed in Phase 4 - functionality moved to adapter
from .wfc_plots import *
from .wfc_collections import COLLECTION_PANELS, COLLECTION_OPERATORS
from .wfc_operators import *
from .wfc_blender_adapter import get_wfc_adapter, reset_wfc_adapter
from .wfc_algorithm.core import WFCAlgorithm



bl_info = {
    "name": "wfc",
    "author": "",
    "description": "wfc mod",
    "blender": (2, 80, 0),
    "location": "View3D",
    "warning": "",
    "category": "Generic"
}

bl_category_name = "wfc"

class OBJECT_PT_GenerateAndAssign(bpy.types.Panel):
    """Panel for creating a full vertex group"""
    bl_label = "Debug Menu"
    bl_idname = "OBJECT_PT_GenerateAndAssign"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = bl_category_name

    def draw(self, context):
        layout = self.layout

        layout.operator("object.add_wfc_primitives")
        layout.operator("object.clear_wfc_primitives")
        layout.operator("object.build_wfc_modules")
        layout.operator("object.clear_wfc_modules")
        layout.operator("object.wfc_clear_all")
        scene = context.scene
        layout.prop(scene, "total_modules")



class OBJECT_OT_WFCClearAll(bpy.types.Operator):
    """Reset everything and rebuild primitives, modules, and grid"""
    bl_idname = "object.wfc_clear_all"
    bl_label = "Reset Everything"
    # bl_space_type = 'VIEW_3D'
    # bl_region_type = 'UI'
    # bl_category = bl_category_name

    def execute(self, context):
        # Clear everything
        clear_all_primitives()
        clear_all_modules()
        clear_all_cells()

        # Reset adapter
        reset_wfc_adapter()

        # Rebuild primitives and modules
        build_all_primitives()
        generate_modules()

        # NEW: Use adapter to build grid instead of old build_wfc_grid()
        if len(all_modules) > 0:
            adapter = get_wfc_adapter()
            algorithm_modules = adapter.setup_from_blender_modules(all_modules)
            adapter.build_algorithm_module_pairs(algorithm_modules)
            grid = adapter.create_grid_from_blender(algorithm_modules, grid_width=10, grid_height=10)
            adapter.create_blender_visualization_grid(grid_width=10, grid_height=10, all_modules_count=len(all_modules))
            adapter.algorithm = WFCAlgorithm(grid)
            self.report({'INFO'}, "Reset complete - grid created with debug visualization")
        else:
            self.report({'WARNING'}, "Reset complete - no modules to create grid")

        return {'FINISHED'}

def clear_all_primitives():
        all_primitives.clear()
        delete_objects_and_meshes(
            get_all_objects_from_collection(CollectionNames.Primitives.value)
        )

def clear_all_modules():
    all_modules.clear()
    delete_objects_and_meshes(get_all_objects_from_collection(CollectionNames.Modules.value))

def clear_all_cells():
    delete_objects_and_meshes(
        get_all_objects_from_collection(CollectionNames.Grid.value)
    )
    # Note: Grid state is now managed by the adapter, not global variables

class OBJECT_OT_UserPrimitives(bpy.types.Operator):
    """Generate Primitives from User Data"""
    bl_idname = "object.add_wfc_primitives"
    bl_label = "Regen Default Primitives"

    def execute(self, context):
        clear_all_primitives()
        return {'FINISHED'}

class OBJECT_OT_AddWfcPrimitives(bpy.types.Operator):
    """Generate Default Primitives from Hardcoded Data"""
    bl_idname = "object.add_wfc_primitives"
    bl_label = "Regen Default Primitives"

    def execute(self, context):
        clear_all_primitives()
        build_all_primitives()
        return {'FINISHED'}

class OBJECT_OT_ClearWfcPrimitives(bpy.types.Operator):
    """Clears all primitive in-scene and in-code"""
    bl_idname = "object.clear_wfc_primitives"
    bl_label = "Clear Primitives"

    def execute(self, context):
        clear_all_primitives()
        return {'FINISHED'}

# TODO: Currently coming from collection, make it code first. 
# TODO: ALso check if there's a mismatch between code and mesh collection for all of these methods
def get_all_primitives():
    return get_all_objects_from_collection(CollectionNames.Primitives.value)

class OBJECT_OT_BuildWfcModules(bpy.types.Operator):
    """Build Modules from Primitive Data"""
    bl_idname = "object.build_wfc_modules"
    bl_label = "Re/Generate Modules"

    def execute(self, context):
        clear_all_modules()
        # prims = get_all_primitives()
        if len(get_all_primitives()) > 0:
            generate_modules()
        return {'FINISHED'}

all_modules = []

def generate_modules():
    modules_collection = get_collection_by_name(CollectionNames.Modules.value)
    all_modules.clear()
    starting_position = Vector((-50, -50, 0))    
    offset = module_size * 2
    for i, primitive in enumerate(get_all_primitives()):
        # primitive_data = all_primitives[primitive.name]
        posX_placeholder = primitive.x_pos_connector
        negX_placeholder = primitive.x_neg_connector
        posY_placeholder = primitive.y_pos_connector
        negY_placeholder = primitive.y_neg_connector
        default_weight = 1
        if (primitive.name == PrimitiveModules.Building.value):
            default_weight = 1.05

        for rotation in range(4):
            module_name = primitive.name + f"_{rotation}"
            module_data = primitive.data.copy()
            module_obj = bpy.data.objects.new(module_name, module_data)

            module_obj.x_pos_connector = posX_placeholder 
            module_obj.x_neg_connector = negX_placeholder
            module_obj.y_pos_connector = posY_placeholder 
            module_obj.y_neg_connector = negY_placeholder
            link_object_to_single_collection(module_obj, modules_collection)

            all_modules.append(
                WFCModule(
                    name = module_name,
                    obj_source = module_obj,
                    module_weight=default_weight,
                    pos_x = posX_placeholder,
                    neg_x = negX_placeholder, 
                    pos_y = posY_placeholder, 
                    neg_y = negY_placeholder
                )
            )
            posX_placeholder = module_obj.y_neg_connector
            negX_placeholder = module_obj.y_pos_connector
            posY_placeholder = module_obj.x_pos_connector
            negY_placeholder = module_obj.x_neg_connector
            module_obj.location += starting_position + Vector(((rotation * module_size + (rotation * offset)) , (i*module_size+offset), 0))
            module_obj.rotation_euler = (0,0,radians(rotation * 90))

    bpy.ops.object.select_all(action='DESELECT')
    for obj in modules_collection.objects:
        obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

    # TODO: probably move this into an operator
    bpy.context.scene["total_modules"] = len(all_modules)

    for module in all_modules:
        build_module_pairs(module, all_modules)

class OBJECT_OT_ClearWfcModules(bpy.types.Operator):
    """Clear all Module Data and Meshes"""
    bl_idname = "object.clear_wfc_modules"
    bl_label = "Clear Modules"

    def execute(self, context):
        clear_all_modules()
        # NEW: Reset adapter when clearing modules
        reset_wfc_adapter()
        return {'FINISHED'}

# TODO: For future, add boolean flag to block all creation of debug meshes
# TODO: Add operator for deleting all debug meshes
class OBJECT_OT_ShowDebugPlanes(bpy.types.Operator):
    """Show debug planes (entropy visualization)"""
    bl_idname = "object.show_debug_planes"
    bl_label = "Show Debug Planes"

    def execute(self, context):
        adapter = get_wfc_adapter()
        adapter.show_debug_planes()
        self.report({'INFO'}, "Debug planes visible")
        return {'FINISHED'}

class OBJECT_OT_HideDebugPlanes(bpy.types.Operator):
    """Hide debug planes (show only collapsed modules)"""
    bl_idname = "object.hide_debug_planes"
    bl_label = "Hide Debug Planes"

    def execute(self, context):
        adapter = get_wfc_adapter()
        adapter.hide_debug_planes()
        self.report({'INFO'}, "Debug planes hidden")
        return {'FINISHED'}

class OBJECT_PT_WFCGridPanel(bpy.types.Panel):
    bl_label = "Build Grid"
    bl_idname = "OBJECT_PT_WFCGridPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = bl_category_name

    def draw(self, context):
        layout = self.layout
        # layout.prop(context.scene, "clear_collections")
        layout.operator("object.build_wfc_grid")
        layout.operator("object.clear_wfc_grid")

        # Debug visualization controls
        layout.separator()
        layout.label(text="Debug Visualization:")
        layout.operator("object.show_debug_planes")
        layout.operator("object.hide_debug_planes")
        layout.operator("object.debug_collapse")
        layout.operator("object.full_collapse")
        
        layout.separator()
        layout.label(text="Debug Tools:")
        layout.operator("object.debug_building_plots")
        
        obj = context.object
        if obj:
            layout.prop(obj, "remaining_modules")

class OBJECT_OT_BuildWFCGrid(bpy.types.Operator):
    """Build a Grid of Uncollapsed Cells (shows initial entropy)"""
    bl_idname = "object.build_wfc_grid"
    bl_label = "Build Grid"

    # def poll():
    #     check col exists

    def execute(self, context):
        # NEW: Use adapter to create grid visualization
        clear_all_cells()
        reset_wfc_adapter()

        if len(all_modules) == 0:
            self.report({'ERROR'}, "No modules found. Generate modules first.")
            return {'CANCELLED'}

        adapter = get_wfc_adapter()

        # Setup algorithm modules
        algorithm_modules = adapter.setup_from_blender_modules(all_modules)
        adapter.build_algorithm_module_pairs(algorithm_modules)

        # Create grid and visualization (but don't collapse)
        grid = adapter.create_grid_from_blender(algorithm_modules, grid_width=10, grid_height=10)
        adapter.create_blender_visualization_grid(grid_width=10, grid_height=10, all_modules_count=len(all_modules))
        adapter.algorithm = WFCAlgorithm(grid)

        self.report({'INFO'}, "Grid created with debug visualization")
        return {'FINISHED'}

class OBJECT_OT_ClearWFCGrid(bpy.types.Operator):
    """Deletes All Grid Cells and Clears Their Data"""
    bl_idname = "object.clear_wfc_grid"
    bl_label = "Clear Grid"

    def execute(self, context):
        clear_all_cells()
        # NEW: Reset adapter when clearing grid
        reset_wfc_adapter()
        return {'FINISHED'}
class OBJECT_OT_FullCollapse(bpy.types.Operator):
    """Takes all Uncollapsed Cells from the Grid and collapses each into a single Module"""
    bl_idname = "object.full_collapse"
    bl_label = "Full Collapse"

    def execute(self, context):
        # NEW: Use adapter for clean separation
        # TODO: Consider adding progress indicator for large grids
        adapter = get_wfc_adapter()

        # Check if we have modules
        if len(all_modules) == 0:
            self.report({'ERROR'}, "No modules found. Generate modules first.")
            return {'CANCELLED'}

        # Run full collapse with visualization
        collapse_history = adapter.setup_and_run_full_collapse(
            blender_modules=all_modules,
            grid_width=10,  # TODO: Make this configurable via UI property
            grid_height=10  # TODO: Make this configurable via UI property
        )

        self.report({'INFO'}, f"Collapsed {len(collapse_history)} cells")

        # TODO: Add building plot processing after collapse is complete
        # process_building_plots_after_collapse()
        return {'FINISHED'}

debug_calculated_vgs = False
# TODO: move to operators when we have a solution for all grid cells
class OBJECT_OT_DebugBuildingPlots(bpy.types.Operator):
    """Debug: Create 2x2 planes for all building plot faces in current modules"""
    bl_idname = "object.debug_building_plots"
    bl_label = "Debug Building Plots"

    def execute(self, context):
        # TODO: ask what global is doing here
        # Is it searching all 'files' and reporting what it finds?
        global all_modules

        if not all_modules:
            self.report({'ERROR'}, "No WFC modules found. Build modules first.")
            return {'CANCELLED'}
        global debug_calculated_vgs
        if debug_calculated_vgs == False:
            print("not yet calced vgs")
            for module in all_modules:
                print(module.name)
                module._calculate_building_plot_faces(inner_cell_size = 2)
            debug_calculated_vgs = True
            # TODO: This is requiring me to hit the button twice
            return {'FINISHED'}

        # NEW: Use adapter to access grid state instead of old global variables
        adapter = get_wfc_adapter()

        if adapter.algorithm is None:
            self.report({'ERROR'}, "No grid found. Build grid first.")
            return {'CANCELLED'}

        # TODO: quick method to check if outer grid collapsed
        if len(adapter.algorithm.grid.uncollapsed_cells) > 0:
            print(f"Cancelling debug: len(uncollapsed_cells) > 0")
            return {'CANCELLED'}

        # NOTE: This operator uses old WFCCell class methods that may not be compatible
        # with the new architecture. It accesses cell_objects which now only stores
        # collapsed module objects, not WFCCell instances.
        # TODO: Refactor this operator to work with the new adapter architecture

        total_planes_created = 0
        print("Calculated building plot faces. Creating dummy plot meshes")

        # Iterate through collapsed cells
        for coords, cell_obj in adapter.cell_objects.items():
            # Skip if this is a dict (old debug plane structure)
            if isinstance(cell_obj, dict):
                continue

            # TODO: This needs refactoring - the old WFCCell methods are not available
            # in the new architecture. For now, this operator is non-functional.
            # planes = cell.debug_create_building_plot_planes_from_module()
            # total_planes_created += len(planes)

        self.report({'WARNING'}, f"This operator needs refactoring for new architecture")
        return {'FINISHED'}

class OBJECT_OT_DebugCollapse(bpy.types.Operator):
    """Collapse a single cell (useful for debugging step-by-step)"""
    bl_idname = "object.debug_collapse"
    bl_label = "Debug Collapse"

    def execute(self, context):
        # NEW: Use adapter for clean separation
        adapter = get_wfc_adapter()

        # Check if we have modules
        if len(all_modules) == 0:
            self.report({'ERROR'}, "No modules found. Generate modules first.")
            return {'CANCELLED'}

        # Collapse one cell
        result = adapter.debug_collapse_single_cell(
            blender_modules=all_modules,
            grid_width=10,  # TODO: Make this configurable via UI property
            grid_height=10  # TODO: Make this configurable via UI property
        )

        if result is None:
            self.report({'INFO'}, "Grid is complete - all cells collapsed")
            return {'FINISHED'}

        cell, selected_module = result
        self.report({'INFO'}, f"Collapsed cell ({cell.x}, {cell.y}) to {selected_module.id}")

        return {'FINISHED'}

# ============================================================================
# OLD WFC FUNCTIONS - REMOVED IN PHASE 4
# ============================================================================
# The following functions have been replaced by the adapter layer:
# - propagate() → adapter.propagate_with_visualization()
# - collapse_process() → adapter.setup_and_run_full_collapse()
# - collapse_cell() → adapter.collapse_cell_with_visualization()
# - build_module_score() → wfc_algorithm.core.score_module()
# - get_lowest_entropy_cells() → wfc_algorithm.core.get_lowest_entropy_cells()
#
# Global variables replaced by adapter state:
# - all_grid_cells → adapter.algorithm.grid.cells
# - uncollapsed_grid_cells → adapter.algorithm.grid.uncollapsed_cells
# ============================================================================

# TODO: USED? If not, delete
class Socket(Enum):
    ROAD_CENTRE = "Road_Centre"
    PAVEMENT_POS = "Pavement_Positive"
    PAVEMENT_NEG = "Pavement_Negative"
    BUILDING = "Building"

all_primitives = {}

def build_all_primitives():
    # TODO: check if collections exist
    primitives_collection = get_collection_by_name(CollectionNames.Primitives.value)
    build_all_primitive_materials()
    primitives = build_default_primitives()
    
    for i, primitive in enumerate(primitives):
        build_from_primitive_data(primitive, primitives_collection,
                         location=(
                             (i * (module_size * 2)) - primitive_offset_x, 
                             i * (module_size * 0) -10, 
                             0
                             )
                         )

def build_from_primitive_data(primitive, primitives_collection, location):
    """Create a new mesh object with vertex groups from captured data"""

    mesh_data = bpy.data.meshes.new(name=primitive.name)
    mesh_obj = bpy.data.objects.new(primitive.name, mesh_data)
    mesh_obj.location = location
    # TODO: Link object to single collection
    primitives_collection.objects.link(mesh_obj)
    all_primitives[primitive.name] = primitive
    mesh_data.from_pydata(primitive.verts, [], primitive.faces)
    mesh_data.update()

    for material_name in primitive.material_names:
        mesh_obj.data.materials.append(bpy.data.materials.get(material_name))

    for i, poly in enumerate(mesh_data.polygons):
        poly.material_index = primitive.mat_indices[i]
    


    mesh_obj.primitive_type = primitive.primitive_type
    mesh_obj.x_pos_connector = primitive.pos_x_connector
    mesh_obj.x_neg_connector = primitive.neg_x_connector
    mesh_obj.y_pos_connector = primitive.pos_y_connector
    mesh_obj.y_neg_connector = primitive.neg_y_connector
    apply_vertex_groups_to_object(mesh_obj, primitive.vertex_group_data)

OPERATORS = [
                OBJECT_OT_WFCClearAll,
                OBJECT_OT_UserPrimitives,
                OBJECT_OT_AddWfcPrimitives,
                OBJECT_OT_ClearWfcPrimitives,
                OBJECT_OT_BuildWfcModules,
                OBJECT_OT_ClearWfcModules,
                OBJECT_OT_BuildWFCGrid,
                OBJECT_OT_ClearWFCGrid,
                OBJECT_OT_DebugCollapse,
                OBJECT_OT_FullCollapse,
                OBJECT_OT_DebugBuildingPlots,
                OBJECT_OT_ShowDebugPlanes,
                OBJECT_OT_HideDebugPlanes
            ] + COLLECTION_OPERATORS + PRIMITIVE_OPERATORS

PANELS = [
             OBJECT_PT_GenerateAndAssign,
            OBJECT_PT_WFCGridPanel
         ] + COLLECTION_PANELS + PRIMITIVE_PANELS

TYPE_CLASSES = []

REGISTER_CLASSES = OPERATORS + PANELS + TYPE_CLASSES


def register():
    for r_class in REGISTER_CLASSES:
        bpy.utils.register_class(r_class)

    bpy.types.Scene.total_modules = IntProperty(default=0)

    bpy.types.Object.primitive_type = bpy.props.EnumProperty(
        name="Primitive",
        description="Classification of object",
        items = get_primitive_type_items
    )
    bpy.types.Object.x_pos_connector = bpy.props.EnumProperty(
        name="XPos",
        description="Classification of object",
        items=CONNECTORS
    )
    bpy.types.Object.x_neg_connector = bpy.props.EnumProperty(
        name="XNeg",
        description="Classification of object",
        items=CONNECTORS
    )
    bpy.types.Object.y_pos_connector = bpy.props.EnumProperty(
        name="YPos",
        description="Classification of object",
        items=CONNECTORS
    )
    bpy.types.Object.y_neg_connector = bpy.props.EnumProperty(
        name="YNeg",
        description="Classification of object",
        items=CONNECTORS
    )
    def update_remaining_modules(self, context):
        context.view_layer.update()
    
    bpy.types.Object.remaining_modules = bpy.props.IntProperty(
        name="Modules",
        description="Remaining variants",
        update=update_remaining_modules
    )

def unregister():
    # TODO: reverse this for safe unregister
    for r_class in REGISTER_CLASSES:
        bpy.utils.unregister_class(r_class)

    del bpy.types.Scene.total_modules
    del bpy.types.Object.primitive_type
    del bpy.types.Object.x_pos_connector
    del bpy.types.Object.x_neg_connector
    del bpy.types.Object.y_pos_connector
    del bpy.types.Object.y_neg_connector
    del bpy.types.Object.remaining_modules

if __name__ == "__main__":
    register()
