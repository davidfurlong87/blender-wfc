# from wfctools import *
from bpy.props import BoolProperty, IntProperty, StringProperty
from .wfc_collections import COLLECTION_PANELS, COLLECTION_OPERATORS
import sys

# if "wfc_collections" in locals():
# import importlib
#
# importlib.reload(wfc_collections)
#
# importlib.reload(wfctools)
from .wfc_values import bl_category_name, CollectionNames
from .collectiontools.collection_creation import *
# from .primitive_generation import build_all_primitives

import bpy
import random
from bpy.props import BoolProperty, EnumProperty, StringProperty, FloatProperty, PointerProperty

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
PRIMITIVE_TYPES = [
    ('ROAD', "Road", "Road surface or path"),
    ('BUILDING', "Building", "Structure or building"),
    ('PAVEMENT', "Pavement", "Pedestrian walkway"),
]
aspects = ["posX", "negX", "posY", "negY"]
CONNECTORS = [
    ('ROAD', "Road", ""),
    ('BUILDING', "Building", ""),
    ('PAVEMENTPOS', "Roadpos", ""),
    ('PAVEMENTNEG', "Roadneg", "")
]


class ModuleProperties(bpy.types.PropertyGroup):
    primitive_type: EnumProperty(
        name="Real World Type",
        description="Classification of object",
        items=PRIMITIVE_TYPES
    )

    x_pos_connector: EnumProperty(
        name="X Pos Connector",
        description="",
        items=CONNECTORS
    )
    x_neg_connector: EnumProperty(
        name="X Neg Connector",
        description="",
        items=CONNECTORS
    )
    y_pos_connector: EnumProperty(
        name="Y Pos Connector",
        description="",
        items=CONNECTORS
    )
    y_neg_connector: EnumProperty(
        name="Y Neg Connector",
        description="",
        items=CONNECTORS
    )


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
        for prim in prims:
            prim_type = random.choice(enum_items_keys)
            prim.primitive_type = "PAVEMENT"
            prim.x_pos_connector = "ROAD"
            prim.x_neg_connector = "BUILDING"
            prim.y_pos_connector = "PAVEMENTPOS"
            prim.y_neg_connector = "PAVEMENTNEG"
            # prim.data['PrimitiveType'] = prim_type
            # prim.data['x_pos_connector'] = random.choice([item[0] for item in CONNECTORS])
            # prim.data['x_neg_connector'] = bpy.types.Object.x_neg_connector.BUILDING
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
import bpy
from enum import Enum
from .wfc_values import module_size


class Primitive:
    def __init__(self, name, verts, faces, mat_indices, material_names,pos_x_connector,neg_x_connector,pos_y_connector,neg_y_connector):
        self.name = name
        self.verts = verts
        self.faces = faces
        self.mat_indices = mat_indices
        self.material_names = material_names
        self.pos_x_connector =pos_x_connector
        self.neg_x_connector =neg_x_connector


class MaterialPrimitives(Enum):
    Building = "Building_Primitive"
    Pavement = "Pavement_Primitive"
    Road = "Road_Primitive"


class PrimitiveModules(Enum):
    Building = "Building_Primitive"
    Pavement = "Pavement_Primitive"
    Road = "Road_Primitive"


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
        verts=[(-4.0, -4.0, -0.4), (-4.0, -4.0, 0.0), (-4.0, 4.0, -0.4), (-4.0, 4.0, 0.0), (4.0, -4.0, -0.4),
               (4.0, -4.0, 0.0), (4.0, 4.0, -0.4), (4.0, 4.0, 0.0)],
        faces=[(0, 1, 3, 2), (6, 7, 5, 4), (2, 3, 7, 6), (4, 5, 1, 0), (7, 3, 1, 5)],
        mat_indices=[0, 0, 0, 0, 0],
        material_names=[
            MaterialPrimitives.Building.value
        ]
    )

    pavement_primitive = Primitive(
        name=PrimitiveModules.Pavement.value,
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
        ]
    )

    road_primitive = Primitive(
        name=PrimitiveModules.Road.value,
        verts=[(-4.0, -4.0, -0.4), (-4.0, -4.0, -0.2), (-4.0, 4.0, -0.4), (-4.0, 4.0, -0.2), (4.0, -4.0, -0.4),
               (4.0, -4.0, -0.2), (4.0, 4.0, -0.4), (4.0, 4.0, -0.2)],
        faces=[(0, 1, 3, 2), (6, 7, 5, 4), (2, 3, 7, 6), (4, 5, 1, 0), (2, 6, 4, 0), (7, 3, 1, 5)],
        mat_indices=[0, 0, 0, 0, 0, 0],
        material_names=[
            MaterialPrimitives.Road.value
        ]
    )

    for i, primitive in enumerate([building_primitive, pavement_primitive, road_primitive]):
        build_primitives(primitive, primitives_collection,
                         location=(i * (module_size * 2), i * (module_size * 0), 0))


def build_primitives(primitive, primitives_collection, location):
    mesh_data = bpy.data.meshes.new(name=primitive.name)
    mesh_obj = bpy.data.objects.new(primitive.name, mesh_data)
    mesh_obj.location = location
    primitives_collection.objects.link(mesh_obj)

    mesh_data.from_pydata(primitive.verts, [], primitive.faces)
    mesh_data.update()

    for material_name in primitive.material_names:
        mesh_obj.data.materials.append(bpy.data.materials.get(material_name))

    for i, poly in enumerate(mesh_data.polygons):
        poly.material_index = primitive.mat_indices[i]

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
                # OBJECT_OT_AddWfcText,
                # OBJECT_OT_ClearWfcText

            ] + COLLECTION_OPERATORS

PANELS = [
             OBJECT_PT_GenerateAndAssign,

         ] + COLLECTION_PANELS

TYPE_CLASSES = [ModuleProperties]

REGISTER_CLASSES = OPERATORS + PANELS + TYPE_CLASSES


def register():
    for r_class in REGISTER_CLASSES:
        bpy.utils.register_class(r_class)

    # bpy.types.Object.my_props = PointerProperty(type=ModuleProperties)

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



def unregister():
    for r_class in REGISTER_CLASSES:
        bpy.utils.unregister_class(r_class)

    del bpy.types.Object.primitive_type
    del bpy.types.Object.x_pos_connector
    del bpy.types.Object.x_neg_connector
    del bpy.types.Object.y_pos_connector
    del bpy.types.Object.y_neg_connector

if __name__ == "__main__":
    register()
