import bpy

from .wfc_classes import Primitive
from .wfc_materials import MaterialPrimitives
from enum import Enum

class PrimitiveModules(Enum):
    Building = "Building_Primitive"
    Pavement = "Pavement_Primitive"
    Road = "Road_Primitive"
    Corner = "Corner_Primitive"

def build_default_primitives():
    return [
        building_primitive(),
        corner_primitive(),
        pavement_primitive()
        ]


def building_primitive():
    return Primitive(
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

def corner_primitive():
    return Primitive(
        name=PrimitiveModules.Corner.value,
        primitive_type="CORNER",
        verts = [(4.0, -4.0, -0.2), (4.0, 4.0, -0.2), (0.0, -4.0, -0.2), (-4.0, -4.0, 0.0), (-4.0, 0.0, -0.2), (-4.0, 4.0, -0.2), (0.0, -4.0, 0.0), (0.0, 0.0, -0.2), (0.0, 0.0, 0.0), (-4.0, 0.0, 0.0), (-2.0, -4.0, 0.0), (-4.0, -2.0, 0.0), (-2.0, -2.0, 0.0)],
        faces = [(7, 4, 9, 8), (12, 11, 3, 10), (7, 2, 0, 1), (1, 5, 4, 7), (2, 7, 8, 6), (8, 12, 10, 6), (9, 11, 12, 8)],        mat_indices = [1, 2, 1, 1, 0, 0, 0],
        material_names = [
        MaterialPrimitives.Pavement.value,
        MaterialPrimitives.Road.value,
        MaterialPrimitives.Building.value
        ],
        pos_x_connector = "ROAD",
        neg_x_connector = "PAVEMENTPOS",
        pos_y_connector = "ROAD",
        neg_y_connector = "PAVEMENTNEG"
    )

def pavement_primitive():
    return Primitive(
        name=PrimitiveModules.Pavement.value,
        primitive_type="PAVEMENT",
        verts = [(4, -4, -0.4), (4, -4, -0.2), (4, 4, -0.4), (4, 4, -0.2), (0, 4, -0.2), (0, -4, -0.4), (0, -4, -0.2), (-4, -4, 0), (-4, 4, 0), (0, 4, 0), (0, -4, 0), (-2, -4, 0), (-2, 4, 0)],
        faces = [(2, 3, 1, 0), (6, 4, 9, 10), (3, 4, 6, 1), (0, 1, 6, 5), (12, 8, 7, 11), (9, 12, 11, 10)],
        
        mat_indices = [1, 0, 1, 1, 2, 0],

        material_names=[
            MaterialPrimitives.Pavement.value,
            MaterialPrimitives.Road.value,
            MaterialPrimitives.Building.value
        ],
        pos_x_connector = "ROAD",
        neg_x_connector = "BUILDING",
        pos_y_connector = "PAVEMENTPOS",
        neg_y_connector = "PAVEMENTNEG"
    )
