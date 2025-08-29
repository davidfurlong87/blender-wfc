import bpy
import random
from bpy.props import BoolProperty, EnumProperty, StringProperty, FloatProperty, PointerProperty

from math import radians
from bpy.props import BoolProperty, IntProperty, StringProperty
from .wfc_collections import COLLECTION_PANELS, COLLECTION_OPERATORS
import sys
from .wfc_classes import WFCModule, WFCCoordinates, WFCCell
from enum import Enum

# if "wfc_collections" in locals():
# import importlib
#
# importlib.reload(wfc_collections)
#
# importlib.reload(wfctools)

from .wfc_values import bl_category_name, CollectionNames, module_size
from .collectiontools.collection_creation import *
# from .primitive_generation import build_all_primitives


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

# TODO: IGNORED By the EnumProperty, which instead uses ROAD_STRAIGHT etc.
PRIMITIVE_TYPES = [
    ('ROAD', "Road", "Road surface or path"),
    ('BUILDING', "Building", "Structure or building"),
    ('PAVEMENT', "Pavement", "Pedestrian walkway"),
]
aspects = ["posX", "negX", "posY", "negY"]


# class Connectors(Enum):
#     Road = "Road"
#     Building = "Building"
#     PavementPos = "PavementPos"
#     PavementNeg = "PavementNeg"

CONNECTORS = [
    ('ROAD', "Road", ""),
    ('BUILDING', "Building", ""),
    ('PAVEMENTPOS', "PavemntPos", ""),
    ('PAVEMENTNEG', "PavemntNeg", "")
]


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

        obj = context.object
        if obj:
            layout.prop(obj, "primitive_type")
            layout.prop(obj, "x_pos_connector")
            layout.prop(obj, "x_neg_connector")
            layout.prop(obj, "y_pos_connector")
            layout.prop(obj, "y_neg_connector")



class OBJECT_OT_AddWfcPrimitives(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.add_wfc_primitives"
    bl_label = "Re/Generate Primitives"

    def execute(self, context):
        # check if collections exist
        objects = []
        primitives_collection = get_collection_by_name(CollectionNames.Primitives.value)
        build_all_primitives(primitives_collection)

        prims = get_all_objects_from_collection(CollectionNames.Primitives.value)
        return {'FINISHED'}


class OBJECT_OT_ClearWfcPrimitives(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.clear_wfc_primitives"
    bl_label = "Clear Primitives"

    def execute(self, context):
        delete_objects_and_meshes(
            get_all_objects_from_collection(CollectionNames.Primitives.value)
        )
        return {'FINISHED'}

class OBJECT_OT_BuildWfcModules(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.build_wfc_modules"
    bl_label = "Re/Generate Modules"

    def execute(self, context):
        # TODO: check if collections exist

        prims = get_all_objects_from_collection(CollectionNames.Primitives.value)
        if len(prims) > 0:
            generate_modules(prims,get_collection_by_name(CollectionNames.Modules.value))
        return {'FINISHED'}

all_modules = []
all_modules_classes = []
def generate_modules(object_list, modules_collection):
    starting_position = Vector((-50,-50,0))
    offset = module_size * 2
    
    for i, primitive in enumerate(object_list):
        primitive_data = all_primitives[primitive.name]
        posX_placeholder = primitive.x_pos_connector
        negX_placeholder = primitive.x_neg_connector
        posY_placeholder = primitive.y_pos_connector
        negY_placeholder = primitive.y_neg_connector

        for rotation in range(4):
            match rotation:
                case default:
                    module_name = primitive.name + f"_{rotation}"
                    module_data = bpy.data.meshes.new(module_name)
                    module_obj = bpy.data.objects.new(module_name, module_data)
                    module_data.from_pydata(primitive_data.verts, [], primitive_data.faces)
                    module_data.update()
                    module_obj.x_pos_connector = posX_placeholder 
                    module_obj.x_neg_connector = negX_placeholder
                    module_obj.y_pos_connector = posY_placeholder 
                    module_obj.y_neg_connector = negY_placeholder
                    link_object_to_single_collection(module_obj, modules_collection)
                    # TODO: Implement weights system
                    all_modules.append(module_obj)
                    all_modules_classes.append(
                        WFCModule(
                            name = module_name,
                            obj_source = module_obj,
                            module_weight=1,
                            pos_x = posX_placeholder,
                            neg_x= negX_placeholder, 
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

class OBJECT_OT_ClearWfcModules(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.clear_wfc_modules"
    bl_label = "Clear Modules"

    def execute(self, context):
        all_modules.clear
        all_modules_classes.clear
        grid_cells = get_all_objects_from_collection(CollectionNames.Modules.value)
        for obj in grid_cells:
            delete_object_by_name(obj.name)
        # TODO: change to below for cleaning up dupe mesh data
        # delete_objects_and_meshes(
        #     get_all_objects_from_collection(CollectionNames.Primitives.value)
        # )
        return {'FINISHED'}





class Primitive:
    def __init__(self, name, primitive_type, verts, faces, mat_indices, material_names,pos_x_connector,neg_x_connector,pos_y_connector,neg_y_connector):
        self.name = name
        self.primitive_type = primitive_type
        self.verts = verts
        self.faces = faces
        self.mat_indices = mat_indices
        self.material_names = material_names
        self.pos_x_connector =pos_x_connector
        self.neg_x_connector =neg_x_connector
        self.pos_y_connector =pos_y_connector
        self.neg_y_connector =neg_y_connector

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
        obj = context.object
        if obj:
            layout.prop(obj, "remaining_modules")


class OBJECT_OT_BuildWFCGrid(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.build_wfc_grid"
    bl_label = "Build Grid"

    # def poll():
    #     check col exists

    def execute(self, context):

        grid_collection = get_collection_by_name(CollectionNames.Grid.value)
        build_wfc_grid(grid_collection, all_modules_classes)
        return {'FINISHED'}

class OBJECT_OT_ClearWFCGrid(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.clear_wfc_grid"
    bl_label = "Clear Grid"

    def execute(self, context):
        delete_objects_and_meshes(
            get_all_objects_from_collection(CollectionNames.Grid.value)
        )
        return {'FINISHED'}

class OBJECT_OT_FullCollapse(bpy.types.Operator):
    """FullCollapse Tooltip"""
    bl_idname = "object.full_collapse"
    bl_label = "Full Collapse"

    def execute(self, context):
        collapse_process()
        return {'FINISHED'}

class OBJECT_OT_DebugCollapse(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.debug_collapse"
    bl_label = "Debug Collapse"  

    def execute(self, context):
        print("-----------------------")
        print(f"remaining keys: {len([k for k in debug_all_grid_cells])}")


        uncollapsed_cells = [cell for cell in debug_all_grid_cells.values() if cell.isCollapsed == False]
        print(f"uncollapsed cells: {len(uncollapsed_cells)}")
        # TODO: Combine the below, have teh cell_obj be a parameter of cell.
        cell = random.choice(get_lowest_entropy_cells(uncollapsed_cells))
        debug_coords = cell.get_coords_set()
        cell_obj = debug_all_grid_holders[cell.get_coords_set()]
        print(f"cell chosen: {cell}")
        collapse_cell(cell)
        print(f"cell obj remaining modules was: {cell_obj.remaining_modules}")
        cell_obj.remaining_modules = cell.number_of_modules_remaining()
        print(f"cell obj remaining modules is now: {cell_obj.remaining_modules}")
        print(f"Cell collapsed: {cell.isCollapsed}")
        print(f"Module chosen: {cell.return_collapsed_module()}")
        del debug_all_grid_cells[debug_coords]
        del debug_all_grid_holders[debug_coords]

        print(f"remaining keys: {len([k for k in debug_all_grid_cells])}")
        print("-----------------------")



        return {'FINISHED'}

def duplicate_and_move_and_return(target_obj, target_location):
    # Get the objects by name
    # source_obj = bpy.data.objects.get(source_obj_name)
    # target_obj = bpy.data.objects.get(target_obj_name)
    
    duplicate = target_obj.copy()

    # TODO: Hard copy of the mesh data. maybe needed, maybe not
    duplicate.data = target_obj.data.copy()
    # bpy.context.collection.objects.link(duplicate)
    # 
    # Move the duplicate to object A's location
    duplicate.location = target_location
    return duplicate

def get_all_available_sockets_at_axis(cell, axis):
    available_sockets = []
    for module in cell.possibleModules:
        match axis:
            case Axis.POS_X:
                available_sockets.append(module.pos_x)
            case Axis.NEG_X:
                available_sockets.append(module.neg_x)
            case Axis.POS_Y:
                available_sockets.append(module.pos_y)
            case Axis.NEG_Y:
                available_sockets.append(module.neg_y)

# UPNEXT
def propagate(collapsed_cell):
    # initiate list of cells affected
    affected_cells = [collapsed_cell]
    # while that list has something
    while affected_cells >0:
        # pick an affected cell
        affected_cell = affected_cells[0]
        # loop through axes
        for axis in [Axis.POS_X, Axis.NEG_X, Axis.POS_Y, Axis.NEG_Y]:
            # has an uncollapsed neighbour at that axis?
            possible_neighbour_coords = (affected_cell.posX, )
                # get its uncollapsed neighbour neighbour at that axis

            # get list of  remaining modules for affected cell

            # from above, build list of possible neighbour modules at input axis

            

            # get the opposite axis

            # loop through that neighbours




def get_lowest_entropy_cells(uncollapsed_cells):
    current_fewest_modules = 9999
    lowest_entropy_cells = []
    for cell in uncollapsed_cells:
        if cell.number_of_modules_remaining() < current_fewest_modules:
            # New record low found. Set the current lowest amount to this, 
            # reassign possible cel list to a new list with just this
            current_fewest_modules = cell.number_of_modules_remaining()
            lowest_entropy_cells = [cell]
        elif cell.number_of_modules_remaining() == current_fewest_modules:
            lowest_entropy_cells.append(cell)
    return lowest_entropy_cells

def collapse_process():
    # Throw exception below if not
    if (len(all_grid_cells) != 0):
        uncollapsed_cells = [cell_value for cell_value in all_grid_cells.values()]
        while len(uncollapsed_cells) != 0:
            cell_to_collapse = random.choice(get_lowest_entropy_cells(uncollapsed_cells))
            collapse_cell(cell_to_collapse)
            uncollapsed_cells.remove(cell_to_collapse)

    else:
        print("All Grid Cells is Empty")

def collapse_cell(cell):
    print(f"Reamining modules: {len(cell.possibleModules)}")
    # Check modules weight
    default_weight = 1
    # TODO: Repalce below with def get_highest_weight_modules(modules)
    scored_modules = [(build_module_score(default_weight), module) for module in cell.possibleModules]
    module_to_return = scored_modules[0]
    # TODO: Magioc numbers, replace with scored module class -> if current_s_module.score > ...
    for scored_module in scored_modules:
        if scored_module[0] > module_to_return[0]:
            module_to_return = scored_module
    print(f"Cell modules was: {cell.number_of_modules_remaining()}")
    cell.possibleModules = [module_to_return[1]]
    print(f"Cell modules now: {cell.number_of_modules_remaining()}")
    cell.isCollapsed = True
    module_obj = module_to_return[1].obj_source
    placement_location = (cell.posX * (module_size), cell.posY * (module_size), 0)
    collapsed_cell_obj = duplicate_and_move_and_return(module_obj, placement_location)
    collapsed_cell_obj.name = f"{cell.posX:02d}_{cell.posY:02d}-{module_obj.name}"
    link_object_to_single_collection(collapsed_cell_obj, get_collection_by_name(CollectionNames.Grid.value))    


# def get_highest_weight_modules(modules):
#     default_weight = 1
#     weighted_modules = [[build_module_score(default_weight), module] for module in modules]


def build_module_score(module_weight):
    return module_weight * random.randint(1, 101)


    

all_grid_cells = {}
debug_all_grid_cells = {}

all_grid_holders = {}
debug_all_grid_holders = {}


def build_wfc_grid(grid_collection, all_wfc_modules):

    x_size = 10
    y_size = 10
    for x in range(x_size):
        for y in range(y_size):
            cell = WFCCell(
                posX = x, 
                posY = y, 
                possibleModules=all_wfc_modules
                )
            all_grid_cells[(x,y)] = cell
            # TODO: Delete when not needed
            debug_all_grid_cells[(x,y)] = cell

    # UPNEXT -> use all_modules_classes here, search for older references to all_modules, swap to new system
    # TODO: instead of looping through size a second time, instead take the x,y data object and multiply that by moduel size
    for x in range(x_size):
        for y in range(y_size):
            cell_location = (x * (module_size), y * (module_size), 0)

            bpy.ops.mesh.primitive_plane_add(size=2, enter_editmode=False, align='WORLD', location=cell_location, scale=(1, 1, 1))
            cell_obj = bpy.context.active_object

            cell_obj.remaining_modules = len(all_wfc_modules)

            cell_obj.name = f"{x:02d}_{y:02d}_cell"
            link_object_to_single_collection(cell_obj, grid_collection)
            # USE WFCCEll?
            all_grid_holders[(x, y)] = cell_obj
            # TODO: Delete when not needed
            debug_all_grid_holders[(x, y)] = cell_obj


class Socket(Enum):
    ROAD_CENTRE = "Road_Centre"
    PAVEMENT_POS = "Pavement_Positive"
    PAVEMENT_NEG = "Pavement_Negative"
    BUILDING = "Building"

valid_pairs_dictionary = {
    Socket.BUILDING: [Socket.BUILDING],
    Socket.PAVEMENT_POS: [Socket.PAVEMENT_NEG],
    Socket.PAVEMENT_NEG: [Socket.PAVEMENT_POS],
    Socket.ROAD_CENTRE: [Socket.ROAD_CENTRE]
}

class Axis(Enum):
    POS_X = "PosX"
    NEG_X = "NegX"
    POS_Y = "PosY"
    NEG_Y = "NegY"

class MaterialPrimitives(Enum):
    Building = "Building_Primitive"
    Pavement = "Pavement_Primitive"
    Road = "Road_Primitive"


class PrimitiveModules(Enum):
    Building = "Building_Primitive"
    Pavement = "Pavement_Primitive"
    Road = "Road_Primitive"


all_primitives = {}


def build_all_primitives(primitives_collection):
    for material_name in [
        MaterialPrimitives.Building.value,
        MaterialPrimitives.Pavement.value,
        MaterialPrimitives.Road.value
    ]:
        match material_name:
            case MaterialPrimitives.Building.value:
                build_primitive_material(material_name, (0.8, 0.4, 0.2, 1.0))
            case MaterialPrimitives.Pavement.value:
                build_primitive_material(material_name, (0.1, 0.4, 0.8, 1.0))
            case MaterialPrimitives.Road.value:
                build_primitive_material(material_name, (0.05, 0.05, 0.05, 1.0))
            case default:
                build_primitive_material("failure", (0.0, 0.0, 0.0, 1.0))


    building_primitive = Primitive(
        name=PrimitiveModules.Building.value,
        primitive_type="BUILDING",
        verts=[(-4.0, -4.0, -0.4), (-4.0, -4.0, 0.0), (-4.0, 4.0, -0.4), (-4.0, 4.0, 0.0), (4.0, -4.0, -0.4),
               (4.0, -4.0, 0.0), (4.0, 4.0, -0.4), (4.0, 4.0, 0.0)],
        faces=[(0, 1, 3, 2), (6, 7, 5, 4), (2, 3, 7, 6), (4, 5, 1, 0), (7, 3, 1, 5)],
        mat_indices=[0, 0, 0, 0, 0],
        material_names=[
            MaterialPrimitives.Building.value
        ],
        pos_x_connector = "BUILDING",
        neg_x_connector = "BUILDING",
        pos_y_connector = "BUILDING",
        neg_y_connector = "BUILDING"
    )

    pavement_primitive = Primitive(  
        name=PrimitiveModules.Pavement.value,
        primitive_type="PAVEMENT",
        verts=[(-4.0, -4.0, -0.4), (-4.0, -4.0, -0.2), (-4.0, 4.0, -0.4), (-4.0, 4.0, -0.2), (4.0, -4.0, -0.4),
               (4.0, -4.0, -0.2), (4.0, 4.0, -0.4), (4.0, 4.0, -0.2), (0.0, 4.0, -0.4), (0.0, 4.0, -0.2),
               (0.0, -4.0, -0.4), (0.0, -4.0, -0.2), (-4.0, -4.0, 0.0), (-4.0, 4.0, 0.0),
               (0.0, 4.0, 0.0), (0.0, -4.0, 0.0)],
        faces=[(0, 1, 3, 2), (6, 7, 5, 4), (8, 9, 7, 6), (11, 15, 12, 1), (11, 9, 14, 15), (7, 9, 11, 5),
               (4, 5, 11, 10),
               (2, 3, 9, 8), (14, 13, 12, 15), (3, 1, 12, 13), (9, 3, 13, 14), (10, 11, 1, 0)],
        mat_indices=[0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0],
        material_names=[
            MaterialPrimitives.Pavement.value,
            MaterialPrimitives.Road.value
        ],
        pos_x_connector = "ROAD",
        neg_x_connector = "BUILDING",
        pos_y_connector = "PAVEMENTNEG",
        neg_y_connector = "PAVEMENTPOS"
    )

    road_primitive = Primitive(
        name=PrimitiveModules.Road.value,
        primitive_type="ROAD_STRAIGHT",
        verts=[(-4.0, -4.0, -0.4), (-4.0, -4.0, -0.2), (-4.0, 4.0, -0.4), (-4.0, 4.0, -0.2), (4.0, -4.0, -0.4),
               (4.0, -4.0, -0.2), (4.0, 4.0, -0.4), (4.0, 4.0, -0.2)],
        faces=[(0, 1, 3, 2), (6, 7, 5, 4), (2, 3, 7, 6), (4, 5, 1, 0), (2, 6, 4, 0), (7, 3, 1, 5)],
        mat_indices=[0, 0, 0, 0, 0, 0],
        material_names=[
            MaterialPrimitives.Road.value
        ],
        pos_x_connector = "ROAD",
        neg_x_connector = "ROAD",
        pos_y_connector = "ROAD",
        neg_y_connector = "ROAD"
    )

    for i, primitive in enumerate([building_primitive, pavement_primitive, road_primitive]):
        build_primitives(primitive, primitives_collection,
                         location=(i * (module_size * 2), i * (module_size * 0), 0))


def build_primitives(primitive, primitives_collection, location):
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

def build_primitive_material(material_name, colour=(0.8, 0.4, 0.2, 1.0)):
    old_material = bpy.data.materials.get(material_name)
    if not old_material:
        mat = bpy.data.materials.new(name=material_name)
        mat.use_nodes = True

        # Clear default nodes
        nodes = mat.node_tree.nodes
        nodes.clear()

        # Add Diffuse BSDF and Material Output nodes
        diffuse_node = nodes.new(type="ShaderNodeBsdfDiffuse")
        output_node = nodes.new(type="ShaderNodeOutputMaterial")

        # Set the color
        diffuse_node.inputs['Color'].default_value = colour

        # Link Diffuse to Output
        mat.node_tree.links.new(diffuse_node.outputs['BSDF'], output_node.inputs['Surface'])

        # Enable backface culling
        mat.use_backface_culling = True





enum_items_keys = [
    'ROAD_STRAIGHT',
    'PAVEMENT',
    'BUILDING'
]

OPERATORS = [
                OBJECT_OT_AddWfcPrimitives,
                OBJECT_OT_ClearWfcPrimitives,
                OBJECT_OT_BuildWfcModules,
                OBJECT_OT_ClearWfcModules,
                OBJECT_OT_BuildWFCGrid,     
                OBJECT_OT_ClearWFCGrid,
                OBJECT_OT_DebugCollapse,
                OBJECT_OT_FullCollapse
            ] + COLLECTION_OPERATORS

PANELS = [
             OBJECT_PT_GenerateAndAssign,
            OBJECT_PT_WFCGridPanel
         ] + COLLECTION_PANELS

TYPE_CLASSES = []

REGISTER_CLASSES = OPERATORS + PANELS + TYPE_CLASSES


def register():
    for r_class in REGISTER_CLASSES:
        bpy.utils.register_class(r_class)


    bpy.types.Object.primitive_type = bpy.props.EnumProperty(
        name="Primitive",
        description="Classification of object",
        items=[
            ('ROAD_STRAIGHT', "Road_Straight", ""),
            ('PAVEMENT', "Pavement", ""),
            ('BUILDING', "Building", "")
        ]
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
    bpy.types.Object.remaining_modules = bpy.props.IntProperty(
        name="Modules",
        description="Remaining variants"
    )



def unregister():
    for r_class in REGISTER_CLASSES:
        bpy.utils.unregister_class(r_class)

    del bpy.types.Object.primitive_type
    del bpy.types.Object.x_pos_connector
    del bpy.types.Object.x_neg_connector
    del bpy.types.Object.y_pos_connector
    del bpy.types.Object.y_neg_connector
    del bpy.types.Object.remaining_modules

if __name__ == "__main__":
    register()
