import bpy
import random
from bpy.props import BoolProperty, IntProperty, EnumProperty, StringProperty, FloatProperty, PointerProperty

from math import radians
from enum import Enum
import sys

# Reload modules for development
if "bpy" in locals():
    import importlib
    if "wfc_operators" in locals():
        importlib.reload(wfc_operators)
    if "wfc_collections" in locals():
        importlib.reload(wfc_collections)
    if "wfc_classes" in locals():
        importlib.reload(wfc_classes)
    if "wfc_materials" in locals():
        importlib.reload(wfc_materials)
    if "wfc_values" in locals():
        importlib.reload(wfc_values)
    if "primitive_data" in locals():
        importlib.reload(primitive_data)
    if "primitive_data_actual" in locals():
        importlib.reload(primitive_data_actual)
    if "wfc_grid_builder" in locals():
        importlib.reload(wfc_grid_builder)
    if "wfc_plots" in locals():
        importlib.reload(wfc_plots)
    # TODO: how to do this when not used here? can i have it reload inside of a different file?
    if "wfc_enums" in locals():
        importlib.reload(wfc_enums)
    if "primitive_data_actual" in locals():
        importlib.reload(primitive_data_actual)

    if "primitive_generation_tools" in locals():
        importlib.reload(primitive_generation_tools)

    # Reload submodules - simpler approach
    try:
        from .collectiontools import collection_creation
        importlib.reload(collection_creation)
    except:
        pass  # Module not loaded yet or import error

from .wfc_collections import COLLECTION_PANELS, COLLECTION_OPERATORS
from .wfc_classes import WFCModule, WFCCell, Primitive, Axis, build_module_pairs
from .wfc_materials import build_all_primitive_materials, MaterialPrimitives

from .wfc_values import bl_category_name, CollectionNames, module_size, primitive_offset_x
from .collectiontools.collection_creation import *
from .wfc_enums import CONNECTORS, PRIMITIVE_TYPES, CUSTOM_PRIMITIVE_TYPES
from .primitive_data import build_default_primitives, PrimitiveModules, PRIMITIVE_OPERATORS, PRIMITIVE_PANELS, get_primitive_type_items
# TODO: how to do this when not used here?
from .primitive_generation_tools import *
from .primitive_data_actual import *
from .wfc_operators import *

from.wfc_grid_builder import *
from.wfc_plots import *



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
    """Tooltip"""
    bl_idname = "object.wfc_clear_all"
    bl_label = "Reset Everything"
    # bl_space_type = 'VIEW_3D'
    # bl_region_type = 'UI'
    # bl_category = bl_category_name

    def execute(self, context):
        clear_all_primitives()
        clear_all_modules()
        clear_all_cells()
        build_all_primitives()
        generate_modules()
        build_wfc_grid(all_modules,all_grid_cells, uncollapsed_grid_cells)

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
    # TODO: For this and the other clears, might be better looping through the code list and deleting whatever is there.
    all_grid_cells.clear()
    uncollapsed_grid_cells.clear()

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
        layout.operator("object.debug_collapse")
        layout.operator("object.full_collapse")
        
        layout.separator()
        layout.label(text="Debug Tools:")
        layout.operator("object.debug_building_plots")
        
        obj = context.object
        if obj:
            layout.prop(obj, "remaining_modules")

class OBJECT_OT_BuildWFCGrid(bpy.types.Operator):
    """Build a Grid of Uncollapsed Cells"""
    bl_idname = "object.build_wfc_grid"
    bl_label = "Build Grid"

    # def poll():
    #     check col exists

    def execute(self, context):
        clear_all_cells()
        build_wfc_grid(all_modules,all_grid_cells,uncollapsed_grid_cells)

        return {'FINISHED'}

class OBJECT_OT_ClearWFCGrid(bpy.types.Operator):
    """Deletes All Grid Cells and Clears Their Data"""
    bl_idname = "object.clear_wfc_grid"
    bl_label = "Clear Grid"

    def execute(self, context):
        clear_all_cells()
        return {'FINISHED'}
class OBJECT_OT_FullCollapse(bpy.types.Operator):
    """Takes all Uncollapsed Cells from the Grid and collapses each into a single Module"""
    bl_idname = "object.full_collapse"
    bl_label = "Full Collapse"

    def execute(self, context):
        collapse_process()

        # TODO: Add building plot processing after collapse is complete
        # process_building_plots_after_collapse()
        return {'FINISHED'}

# TODO: move to operators when we have a solution for all grid cells
class OBJECT_OT_DebugBuildingPlots(bpy.types.Operator):
    """Debug: Create 2x2 planes for all building plot faces in current modules"""
    bl_idname = "object.debug_building_plots"
    bl_label = "Debug Building Plots"

    def execute(self, context):
        # TODO: ask what global is doing here
        global all_modules
        
        if not all_modules:
            self.report({'ERROR'}, "No WFC modules found. Build modules first.")
            return {'CANCELLED'}
        
        # TODO: quick method to check if outer grid collapsed
        if len(uncollapsed_grid_cells) > 0:
            print(f"Cancelling debug: len(uncollapsed_grid_cells) > 0")
            return {'CANCELLED'}
        
        keys = all_grid_cells.keys()
        total_planes_created = 0
        iterations = 0

        inner_grid = {}
        for key in keys:
            cell = all_grid_cells[key]
            planes = cell.debug_create_building_plot_planes_from_module()
            # module = cell.return_collapsed_module()
            # planes = module.debug_create_building_plot_planes(center_vector=cell.world_pos_as_vector(), name_override = key)
            total_planes_created += len(planes)

            # if len(planes) > 1:

            # iterations += 1
            # if iterations > 6:
            #         break
                
        self.report({'INFO'}, f"Created {total_planes_created} debug building plot planes")
        return {'FINISHED'}

class OBJECT_OT_DebugCollapse(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.debug_collapse"
    bl_label = "Debug Collapse"  

    def execute(self, context):
        uncollapsed_cells = uncollapsed_grid_cells.values()
        cell = random.choice(get_lowest_entropy_cells(uncollapsed_cells))
        collapse_cell(cell)
        propagate(cell)
        del uncollapsed_grid_cells[cell.get_coords_set()]

        cell_obj = cell.mesh_obj
        cell_obj.remaining_modules = cell.number_of_modules_remaining()

        return {'FINISHED'}


def propagate(collapsed_cell):
    affected_cells = [collapsed_cell]
    all_cell_keys = [key for key in all_grid_cells.keys()]
    # TODO: purpose of this is to allow me to update meshData/material inputs

    while len(affected_cells) >0:
        affected_cell = affected_cells[0]
        affected_cells.remove(affected_cell)
        for axis in Axis:
            possible_pairs = []
            neighbour_coords = affected_cell.get_neighbour_coords_set(axis)

            # TODO: crappy getOrElse, change
            if neighbour_coords in all_cell_keys:
                neighbour_cell = all_grid_cells[neighbour_coords]
                if (neighbour_cell and neighbour_cell.isCollapsed == False):
                    match axis:
                        case Axis.POS_X:
                            for module in affected_cell.possibleModules:
                                possible_pairs.extend(module.pos_x_pairs)
                        case Axis.NEG_X:
                            for module in affected_cell.possibleModules:
                                possible_pairs.extend(module.neg_x_pairs)
                        case Axis.POS_Y:
                            for module in affected_cell.possibleModules:
                                possible_pairs.extend(module.pos_y_pairs)
                        case Axis.NEG_Y:
                            for module in affected_cell.possibleModules:
                                possible_pairs.extend(module.neg_y_pairs)

                    invalid_modules = [module for module in neighbour_cell.possibleModules if module not in possible_pairs]
                    if len(invalid_modules) > 0:
                        neighbour_cell.remove_invalid_modules(invalid_modules)
                        affected_cells.append(neighbour_cell)

def get_lowest_entropy_cells(uncollapsed_cells):
    current_fewest_modules = 9999
    lowest_entropy_cells = []
    for cell in uncollapsed_cells:
        if cell.number_of_modules_remaining() < current_fewest_modules:
            current_fewest_modules = cell.number_of_modules_remaining()
            lowest_entropy_cells = [cell]
        elif cell.number_of_modules_remaining() == current_fewest_modules:
            lowest_entropy_cells.append(cell)
    return lowest_entropy_cells

def collapse_process():
    # TODO: Throw exception below if not
    if (len(all_grid_cells) != 0):
        # TODO: Uncollapsed cell already exists elsewhere
        uncollapsed_cells = [cell_value for cell_value in uncollapsed_grid_cells.values()]
        while len(uncollapsed_cells) != 0:
            cell_to_collapse = random.choice(get_lowest_entropy_cells(uncollapsed_cells))
            collapse_cell(cell_to_collapse)
            uncollapsed_cells.remove(cell_to_collapse)
            del uncollapsed_grid_cells[cell_to_collapse.get_coords_set()]
            propagate(cell_to_collapse)

def collapse_cell(cell):
    # TODO: Replace below with def get_highest_weight_modules(modules)
    scored_modules = [(build_module_score(module.module_weight), module) for module in cell.possibleModules]
    module_to_return = scored_modules[0]
    # TODO: Magic numbers, replace with scored module class -> if current_s_module.score > ...
    for scored_module in scored_modules:
        if scored_module[0] > module_to_return[0]:
            module_to_return = scored_module
    cell.possibleModules = [module_to_return[1]]
    cell.isCollapsed = True
    module_obj = module_to_return[1].obj_source
    placement_location = (cell.posX * (module_size), cell.posY * (module_size), 0)
    collapsed_cell_obj = duplicate_and_move_and_return(module_obj, placement_location)
    collapsed_cell_obj.name = f"{cell.posX:02d}_{cell.posY:02d}-{module_obj.name}"
    cell.replace_mesh_obj(new_obj=collapsed_cell_obj)
    link_object_to_single_collection(collapsed_cell_obj, get_collection_by_name(CollectionNames.Grid.value))    

def build_module_score(module_weight):
    return module_weight * random.randint(1, 10001)

all_grid_cells = {}
uncollapsed_grid_cells = {}
debug_all_grid_cells = {}

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
                OBJECT_OT_DebugBuildingPlots
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
