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
    # NEW: Connector registry (Task 1B.3)
    if "connector_registry" in locals():
        importlib.reload(connector_registry)

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
    if "primitive_ui" in locals():
        importlib.reload(primitive_ui)
    if "wfc_collections" in locals():
        importlib.reload(wfc_collections)
    if "wfc_operators" in locals():
        importlib.reload(wfc_operators)

# ============================================================================
# Imports
# ============================================================================
# All imports happen AFTER the reload block to ensure we get the latest versions

from .wfc_values import (
    bl_category_name, CollectionNames, GridCategory,
    primitives_collection_for, modules_collection_for, grid_collection_for,
    DEFAULT_GRID_SIZES,
)
from .wfc_enums import PRIMITIVE_TYPES, CUSTOM_PRIMITIVE_TYPES, get_connector_enum_items, GRID_CATEGORIES
from .wfc_materials import build_all_primitive_materials, MaterialPrimitives
# NEW: Connector registry (Task 1B.3)
from .connector_registry import connector_registry
from .collectiontools.collection_creation import *
from .wfc_classes import WFCModule, WFCCell, Primitive, Axis, build_module_pairs
from .primitive_generation_tools import *
from .primitive_data_actual import *
from .primitive_ui import build_default_primitives, PRIMITIVE_OPERATORS, PRIMITIVE_PANELS, get_primitive_type_items
# wfc_grid_builder removed in Phase 4 - functionality moved to adapter
from .wfc_plots import *
from .wfc_collections import COLLECTION_PANELS, COLLECTION_OPERATORS
from .wfc_operators import *
from .wfc_blender_adapter import BlenderWFCAdapter, get_wfc_adapter, reset_wfc_adapter
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

        # Rebuild primitives and modules for all categories
        build_all_primitives()
        generate_modules_for_all_loaded_categories()

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
    """Backward-compat shim. Prefer clear_modules_for_category(GridCategory.OUTER_GRID)."""
    clear_modules_for_category(GridCategory.OUTER_GRID)

def clear_all_cells():
    # Use .get() + .all_objects so this is safe even before WFC_Grid exists,
    # and correctly clears objects in WFC_Grid_outer_grid etc. subcollections.
    col = bpy.data.collections.get(CollectionNames.Grid.value)
    if col is not None:
        delete_objects_and_meshes(list(col.all_objects))
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
def get_all_primitives():
    """Return all primitive objects across every category subcollection.

    Uses ``WFC_Primitives.all_objects`` which traverses child collections
    automatically, so objects stored in ``WFC_Primitives_outer_grid``,
    ``WFC_Primitives_building``, etc. are all included without any explicit
    category filtering.

    Returns an empty list (never raises) when the parent collection does not
    yet exist.
    """
    col = bpy.data.collections.get(CollectionNames.Primitives.value)
    if col is None:
        return []
    return list(col.all_objects)


def get_primitives_by_category(category: str):
    """Return all primitive objects for *category* from its dedicated subcollection.

    Collection membership encodes the category — no property scan needed.
    Uses ``ensure_primitives_collection`` so the three-level chain
    (WFC → WFC_Primitives → WFC_Primitives_{category}) is created lazily on
    first access and the call never raises.

    Args:
        category: A :class:`~wfc_values.GridCategory` string such as
            ``'outer_grid'`` or ``'building'``.

    Returns:
        List of :class:`bpy.types.Object` in ``WFC_Primitives_{category}``.
    """
    from .collectiontools import ensure_primitives_collection
    col = ensure_primitives_collection(category)
    return list(col.objects)


class OBJECT_OT_BuildWfcModules(bpy.types.Operator):
    """Regenerate modules for every loaded primitive category"""
    bl_idname = "object.build_wfc_modules"
    bl_label = "Re/Generate Modules"

    def execute(self, context):
        categories = generate_modules_for_all_loaded_categories()
        if not categories:
            self.report({'WARNING'},
                "No primitives loaded. Load a library first.")
            return {'CANCELLED'}
        total = sum(len(get_modules_for_category(cat)) for cat in categories)
        self.report({'INFO'},
            f"Generated {total} modules for: {', '.join(categories)}")
        return {'FINISHED'}

# ── Module storage (keyed by category) ───────────────────────────────────────
_modules_by_category: dict = {}

# Backward-compat aliases — these ARE the list objects stored in the dict.
# Mutate only via .append() / .clear(); never reassign these names.
# New code should call get_modules_for_category(category) instead.
all_modules          = _modules_by_category.setdefault(GridCategory.OUTER_GRID, [])
all_building_modules = _modules_by_category.setdefault(GridCategory.BUILDING,   [])


def get_modules_for_category(category: str) -> list:
    """Return the live WFCModule list for *category*, creating it if needed.

    The returned list is the same object stored in ``_modules_by_category``,
    so mutations (append / clear) are immediately reflected everywhere.

    Args:
        category: A :class:`~wfc_values.GridCategory` string, e.g.
            ``'outer_grid'`` or ``'building'``.

    Returns:
        Mutable list of :class:`~wfc_classes.WFCModule` instances.
    """
    return _modules_by_category.setdefault(category, [])


def clear_modules_for_category(category: str) -> None:
    """Clear the in-memory module list and delete Blender objects for *category*.

    Safe to call even when the category has never been populated — if the
    list or collection does not yet exist, no error is raised.

    Args:
        category: A :class:`~wfc_values.GridCategory` string.
    """
    mods = _modules_by_category.get(category)
    if mods is not None:
        mods.clear()
    col_name = modules_collection_for(category)
    if check_collection_exists(col_name):
        delete_objects_and_meshes(get_all_objects_from_collection(col_name))


def generate_modules_for_category(category: str) -> None:
    """Generate WFC modules for all primitives belonging to *category*.

    This is the single, generic implementation that replaces the former
    ``generate_modules()`` (outer-grid only) and ``generate_building_modules()``
    (building only).  Both of those names are kept as one-line backward-compat
    shims below.

    The function:

    1. Ensures the category-specific modules collection exists via
       ``ensure_modules_collection(category)`` (lazy, crash-safe).
    2. Fetches primitives via ``get_primitives_by_category(category)``.
    3. Clears then repopulates ``_modules_by_category[category]`` in-place so
       the ``all_modules`` / ``all_building_modules`` aliases stay in sync.
    4. Respects ``rotation_invariant`` — one module if True, four if False.
    5. Applies queued rotations via ``transform_apply`` after placement.
    6. Builds connector pairs via ``build_module_pairs``.

    Args:
        category: A :class:`~wfc_values.GridCategory` string, e.g.
            ``'outer_grid'`` or ``'building'``.
    """
    from .collectiontools import ensure_modules_collection
    modules_collection = ensure_modules_collection(category)
    mods = get_modules_for_category(category)
    mods.clear()

    primitives = get_primitives_by_category(category)
    if not primitives:
        print(f"[WFC] generate_modules_for_category({category!r}): no primitives found.")
        return

    starting_position = Vector((-50, -50, 0))

    for i, primitive in enumerate(primitives):
        posX = primitive.x_pos_connector
        negX = primitive.x_neg_connector
        posY = primitive.y_pos_connector
        negY = primitive.y_neg_connector

        default_weight = 1
        if primitive.name == PrimitiveModules.Building.value:
            default_weight = 1.05  # slight bias toward building tiles in outer grid

        size = getattr(primitive, 'physical_size', DEFAULT_GRID_SIZES.get(category, 8.0))
        offset = size * 2
        rotation_count = 1 if getattr(primitive, 'rotation_invariant', False) else 4

        for rotation in range(rotation_count):
            module_name = f"{primitive.name}_{category}_{rotation}"
            module_data = primitive.data.copy()
            module_obj = bpy.data.objects.new(module_name, module_data)

            module_obj.x_pos_connector = posX
            module_obj.x_neg_connector = negX
            module_obj.y_pos_connector = posY
            module_obj.y_neg_connector = negY
            link_object_to_single_collection(module_obj, modules_collection)

            mods.append(
                WFCModule(
                    name=module_name,
                    obj_source=module_obj,
                    module_weight=default_weight,
                    pos_x=posX,
                    neg_x=negX,
                    pos_y=posY,
                    neg_y=negY,
                    physical_size=size,
                    grid_category=category,
                )
            )
            posX = module_obj.y_neg_connector
            negX = module_obj.y_pos_connector
            posY = module_obj.x_pos_connector
            negY = module_obj.x_neg_connector
            module_obj.location += starting_position + Vector((
                rotation * size + rotation * offset,
                i * size + offset,
                0,
            ))
            module_obj.rotation_euler = (0, 0, radians(rotation * 90))

    bpy.ops.object.select_all(action='DESELECT')
    for obj in modules_collection.objects:
        obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

    bpy.context.scene[f"total_{category}_modules"] = len(mods)

    for module in mods:
        build_module_pairs(module, mods)

    print(f"[WFC] generate_modules_for_category({category!r}): {len(mods)} modules generated.")


def generate_modules():
    """Backward-compat shim. Prefer generate_modules_for_category(GridCategory.OUTER_GRID)."""
    generate_modules_for_category(GridCategory.OUTER_GRID)


def get_building_modules():
    """Backward-compat shim. Prefer get_modules_for_category(GridCategory.BUILDING)."""
    return get_modules_for_category(GridCategory.BUILDING)


def clear_all_building_modules():
    """Backward-compat shim. Prefer clear_modules_for_category(GridCategory.BUILDING)."""
    clear_modules_for_category(GridCategory.BUILDING)


def generate_building_modules():
    """Backward-compat shim. Prefer generate_modules_for_category(GridCategory.BUILDING)."""
    generate_modules_for_category(GridCategory.BUILDING)


def generate_modules_for_all_loaded_categories() -> list:
    """Generate (or regenerate) modules for every category that has loaded primitives.

    Walks the ``WFC_Primitives`` child collections to discover all populated
    categories dynamically — no hardcoded category list, no code changes
    needed when a new category is introduced.

    Clears existing modules for each discovered category before regenerating,
    so this is safe to call repeatedly.

    Returns:
        List of category name strings that were processed.  Empty if no
        primitives are loaded yet.
    """
    prefix = primitives_collection_for("")   # → "WFC_Primitives_"
    prim_parent = bpy.data.collections.get(CollectionNames.Primitives.value)
    if not prim_parent:
        return []

    categories = [
        col.name[len(prefix):]
        for col in prim_parent.children
        if col.objects and col.name.startswith(prefix)
    ]

    for category in categories:
        clear_modules_for_category(category)
        generate_modules_for_category(category)

    return categories


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

        layout.separator()
        layout.label(text="Inner Grid (Building):")
        layout.operator("object.generate_building_inner_grid")

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
    """Visualize plot islands (generic for building, road, pavement, park plots)"""
    bl_idname = "object.debug_building_plots"
    bl_label = "Debug Plot Islands"

    def execute(self, context):
        adapter = get_wfc_adapter()

        if adapter.algorithm is None:
            self.report({'ERROR'}, "No grid found. Run Full Collapse first.")
            return {'CANCELLED'}

        # Check if grid is fully collapsed
        if len(adapter.algorithm.grid.uncollapsed_cells) > 0:
            self.report({'ERROR'}, "Grid not fully collapsed. Run Full Collapse first.")
            return {'CANCELLED'}

        # Extract and group building plots using generic adapter methods
        building_plots = adapter.extract_plots_from_grid(
            plot_type='building',
            vertex_group_name='building_plot'
        )

        if not building_plots:
            self.report({'WARNING'}, "No building plots found. Make sure modules have 'building_plot' vertex groups.")
            return {'CANCELLED'}

        # Group plots into islands
        islands = adapter.group_plot_islands(building_plots, plot_type='building')

        self.report({'INFO'}, f"Found {len(islands)} building plot islands with {len(building_plots)} total plots")

        # Visualize islands with colored planes
        self.visualize_islands(islands)

        return {'FINISHED'}

    def visualize_islands(self, islands):
        """Create colored debug planes for each island"""
        import random
        from .wfc_values import CollectionNames
        from .collectiontools.collection_creation import get_collection_by_name

        debug_collection = get_collection_by_name(CollectionNames.Debug.value)

        for island in islands:
            # Random color per island
            color = (random.random(), random.random(), random.random(), 0.5)

            # Create plane for island bounds
            bounds = island['combined_bounds']
            center_x = (bounds[0] + bounds[2]) / 2
            center_y = (bounds[1] + bounds[3]) / 2
            width = bounds[2] - bounds[0]
            height = bounds[3] - bounds[1]

            bpy.ops.mesh.primitive_plane_add(
                size=1,
                location=(center_x, center_y, 0.1)
            )
            plane = bpy.context.active_object
            plane.scale = (width/2, height/2, 1)
            plane.name = f"Island_{island['island_id']}_plots_{len(island['plots'])}"

            # Create material
            mat = bpy.data.materials.new(name=f"Island_{island['island_id']}_Mat")
            mat.use_nodes = True
            mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = color
            plane.data.materials.append(mat)

            # Link to debug collection
            for coll in plane.users_collection:
                coll.objects.unlink(plane)
            debug_collection.objects.link(plane)

# TODO: Sufficient now, but the inner grid process should be generic in the future.
class OBJECT_OT_GenerateBuildingInnerGrid(bpy.types.Operator):
    """Collapse building plot islands using building-category WFC modules (inner grid)"""
    bl_idname = "object.generate_building_inner_grid"
    bl_label = "Collapse Building Islands"

    def execute(self, context):
        import random
        from .wfc_algorithm.core import WFCAlgorithm, get_lowest_entropy_cells

        adapter = get_wfc_adapter()

        # ── Guard: outer grid must be collapsed first ──────────────────────
        if adapter.algorithm is None:
            self.report({'ERROR'}, "No outer grid found. Run Full Collapse first.")
            return {'CANCELLED'}
        if len(adapter.algorithm.grid.uncollapsed_cells) > 0:
            self.report({'ERROR'}, "Outer grid not fully collapsed. Run Full Collapse first.")
            return {'CANCELLED'}

        # ── Guard: building modules must exist ────────────────────────────
        if not all_building_modules:
            self.report({'ERROR'},
                "No building modules found. "
                "Load building primitives then press 'Build Building Modules'.")
            return {'CANCELLED'}

        # ── Extract & group building plot islands ──────────────────────────
        building_plots = adapter.extract_plots_from_grid(
            plot_type='building', vertex_group_name='building_plot'
        )
        if not building_plots:
            self.report({'WARNING'},
                "No building plots found. Make sure collapsed modules have "
                "'building_plot' vertex groups.")
            return {'CANCELLED'}

        islands = adapter.group_plot_islands(building_plots, plot_type='building')

        # ── Set up building algorithm modules (done once for all islands) ──
        build_adapter = BlenderWFCAdapter()
        algo_building_modules = build_adapter.setup_from_blender_modules(all_building_modules)
        build_adapter.build_algorithm_module_pairs(algo_building_modules)

        # ── Resolve resolution_multiplier from first building module ───────
        resolution = 4  # default
        if all_building_modules:
            res = getattr(all_building_modules[0].obj_source, 'resolution_multiplier', None)
            if res and res > 0:
                resolution = res

        total_collapsed = 0
        for island in islands:
            inner_grid, _ = adapter.create_inner_grid_for_island(
                island,
                resolution_multiplier=resolution,
                inner_modules=algo_building_modules,
            )
            build_adapter.build_algorithm_module_pairs(algo_building_modules)

            # Collapse the inner grid fully
            inner_wfc = WFCAlgorithm(inner_grid)
            uncollapsed = inner_grid.get_uncollapsed_cells()
            while uncollapsed:
                cell_to_collapse = random.choice(get_lowest_entropy_cells(uncollapsed))
                inner_wfc.collapse_cell(cell_to_collapse)
                inner_wfc.propagate(cell_to_collapse)
                uncollapsed.remove(cell_to_collapse)
                total_collapsed += 1

            # Visualize collapsed inner grid cells.
            # bounds[0/1] are the outer *edges* of the island (corner, not cell centre).
            # Building module objects are centred at their origin, so each must be
            # placed at the centre of its inner cell = edge + cell_size / 2.
            bounds = island['combined_bounds']
            cell_size = all_building_modules[0].physical_size if all_building_modules else 2.0
            half = cell_size / 2
            origin_x = bounds[0] + half
            origin_y = bounds[1] + half
            from .collectiontools import ensure_grid_collection
            grid_collection = ensure_grid_collection(GridCategory.BUILDING)
            for cell in inner_grid.cells.values():
                if cell.is_collapsed and cell.possible_modules:
                    algo_mod = cell.possible_modules[0]
                    wfc_mod = build_adapter.blender_module_map.get(algo_mod.id)
                    if wfc_mod and wfc_mod.obj_source:
                        loc = (
                            origin_x + cell.x * cell_size,
                            origin_y + cell.y * cell_size,
                            0.05,
                        )
                        result_obj = duplicate_and_move_and_return(wfc_mod.obj_source, loc)
                        result_obj.name = (
                            f"bld_{island['island_id']}_{cell.x:02d}_{cell.y:02d}"
                        )
                        link_object_to_single_collection(result_obj, grid_collection)

        self.report({'INFO'},
            f"Collapsed {total_collapsed} inner-grid cells across {len(islands)} island(s).")
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
        # Use physical_size if available (PrimitiveData), fall back to 8.0 for
        # legacy Primitive objects from build_default_primitives() which predate
        # the metadata system.
        size = getattr(primitive, 'physical_size', 8.0)
        display_spacing = size * 2
        build_from_primitive_data(primitive, primitives_collection,
                         location=(
                             (i * display_spacing) - (size * 4),
                             -10,
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
    # Set sizing and symmetry metadata. Use getattr fallbacks for legacy
    # Primitive objects (from build_default_primitives) that predate PrimitiveData.
    mesh_obj.physical_size = getattr(primitive, 'physical_size', 8.0)
    mesh_obj.grid_category = getattr(primitive, 'grid_category', 'outer_grid')
    mesh_obj.resolution_multiplier = getattr(primitive, 'resolution_multiplier', 1)
    mesh_obj.rotation_invariant = getattr(primitive, 'rotation_invariant', False)
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
                OBJECT_OT_GenerateBuildingInnerGrid,
                OBJECT_OT_ShowDebugPlanes,
                OBJECT_OT_HideDebugPlanes
            ] + COLLECTION_OPERATORS + PRIMITIVE_OPERATORS

PANELS = [
             OBJECT_PT_GenerateAndAssign,
            OBJECT_PT_WFCGridPanel
         ] + COLLECTION_PANELS + PRIMITIVE_PANELS

TYPE_CLASSES = []

REGISTER_CLASSES = OPERATORS + PANELS + TYPE_CLASSES


def _load_connector_registry():
    """
    Load connector registry from JSON file on addon startup (Task 1B.3)

    Loads connectors from data/connectors.json. If file is missing or corrupt,
    falls back to default connectors defined in connector_registry.py.
    """
    from pathlib import Path

    # Get path to connectors.json (same directory as this file)
    addon_dir = Path(__file__).parent
    connectors_file = addon_dir / 'data' / 'connectors.json'

    print(f"[WFC] Loading connector registry from: {connectors_file}")

    if connectors_file.exists():
        try:
            success = connector_registry.load_from_file(str(connectors_file))
            if success:
                connector_count = len(connector_registry.connectors)
                connector_names = ', '.join(list(connector_registry.connectors.keys())[:5])
                if connector_count > 5:
                    connector_names += f', ... ({connector_count - 5} more)'
                print(f"[WFC] ✅ Loaded {connector_count} connectors: {connector_names}")
            else:
                print(f"[WFC] ⚠️  Failed to load connectors from {connectors_file}")
                print(f"[WFC] Using default connectors")
        except Exception as e:
            print(f"[WFC] ❌ Error loading connector registry: {e}")
            print(f"[WFC] Using default connectors")
    else:
        print(f"[WFC] ⚠️  Connector file not found: {connectors_file}")
        print(f"[WFC] Using default connectors from connector_registry.py")

    # Print summary
    print(f"[WFC] Connector registry ready with {len(connector_registry.connectors)} connectors")


def register():
    # NEW: Load connector registry from JSON (Task 1B.3)
    _load_connector_registry()

    for r_class in REGISTER_CLASSES:
        bpy.utils.register_class(r_class)

    bpy.types.Scene.total_modules = IntProperty(default=0)

    bpy.types.Object.primitive_type = bpy.props.EnumProperty(
        name="Primitive",
        description="Classification of object",
        items = get_primitive_type_items
    )
    # Build connector items from registry - registry is already loaded at this point
    connector_items = get_connector_enum_items()
    bpy.types.Object.x_pos_connector = bpy.props.EnumProperty(
        name="XPos",
        description="Classification of object",
        items=connector_items
    )
    bpy.types.Object.x_neg_connector = bpy.props.EnumProperty(
        name="XNeg",
        description="Classification of object",
        items=connector_items
    )
    bpy.types.Object.y_pos_connector = bpy.props.EnumProperty(
        name="YPos",
        description="Classification of object",
        items=connector_items
    )
    bpy.types.Object.y_neg_connector = bpy.props.EnumProperty(
        name="YNeg",
        description="Classification of object",
        items=connector_items
    )

    # NEW: Primitive sizing and symmetry metadata (Task 3A.1 Step 2)
    bpy.types.Object.physical_size = FloatProperty(
        name="Physical Size (m)",
        description="Physical size of this primitive in meters",
        default=8.0,
        min=0.1,
        soft_max=100.0
    )
    bpy.types.Object.grid_category = EnumProperty(
        name="Grid Category",
        description="Which grid system this primitive belongs to",
        items=GRID_CATEGORIES,
        default='outer_grid'
    )
    bpy.types.Object.resolution_multiplier = IntProperty(
        name="Resolution Multiplier",
        description="How many of these cells fit in one outer grid cell",
        default=1,
        min=1,
        soft_max=16
    )
    bpy.types.Object.rotation_invariant = BoolProperty(
        name="Rotation Invariant",
        description="All 4 rotations produce identical geometry — only one module will be generated",
        default=False
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
    # NEW: Primitive sizing and symmetry metadata (Task 3A.1 Step 2)
    del bpy.types.Object.physical_size
    del bpy.types.Object.grid_category
    del bpy.types.Object.resolution_multiplier
    del bpy.types.Object.rotation_invariant

if __name__ == "__main__":
    register()
