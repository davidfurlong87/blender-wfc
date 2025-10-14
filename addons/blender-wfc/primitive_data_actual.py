from .wfc_classes import Primitive
from .wfc_materials import MaterialPrimitives
from .wfc_enums import PrimitiveModules


def corner_primitive():
    return Primitive(
        name=PrimitiveModules.Corner.value,
        primitive_type="CORNER",
        verts = [(4.0, -4.0, -0.2), (4.0, 4.0, -0.2), (0.0, -4.0, -0.2), (-4.0, -4.0, 0.0), (-4.0, 0.0, -0.2), (-4.0, 4.0, -0.2), (0.0, -4.0, 0.0), (0.0, 0.0, -0.2), (0.0, 0.0, 0.0), (-4.0, 0.0, 0.0), (-2.0, -4.0, 0.0), (-4.0, -2.0, 0.0), (-2.0, -2.0, 0.0)],
        faces = [(7, 4, 9, 8), (12, 11, 3, 10), (7, 2, 0, 1), (1, 5, 4, 7), (2, 7, 8, 6), (8, 12, 10, 6), (9, 11, 12, 8)],
        mat_indices = [1, 2, 1, 1, 0, 0, 0],
        material_names = [
        MaterialPrimitives.Pavement.value,
        MaterialPrimitives.Road.value,
        MaterialPrimitives.Building.value
        ],
        pos_x_connector = "ROAD",
        neg_x_connector = "PAVEMENTPOS",
        pos_y_connector = "ROAD",
        neg_y_connector = "PAVEMENTNEG",
        vertex_group_data = {'building_plot': {'vertices': [3, 10, 11, 12], 'weights': [1.0, 1.0, 1.0, 1.0]}, 'pavement_plot': {'vertices': [2, 4, 6, 7, 8, 9, 10, 11, 12], 'weights': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]}, 'road_plot': {'vertices': [0, 1, 2, 4, 5, 7], 'weights': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]}}
    )

def corner_primitive_alt():
    return Primitive(
        name=PrimitiveModules.Corner.value,
        primitive_type="CORNER",
        verts = [(4.0, -4.0, 0.0), (4.0, 4.0, 0.0), (0.0, -4.0, 0.0), (-4.0, -4.0, 0.0), (-4.0, 0.0, 0.0), (-4.0, 4.0, 0.0), (-2.0, 4.0, 0.0), (0.0, 0.0, 0.0), (0.0, -2.0, 0.0), (4.0, -2.0, 0.0), (-2.0, -4.0, 0.0), (-4.0, -2.0, 0.0), (-2.0, -2.0, 0.0), (-2.0, 0.0, 0.0), (4.0, 0.0, 0.0), (0.0, 4.0, 0.0), (2.0, -4.0, 0.0), (2.0, -2.0, 0.0), (2.0, 4.0, 0.0), (2.0, 0.0, 0.0), (4.0, 2.0, 0.0), (-4.0, 2.0, 0.0), (-2.0, 2.0, 0.0), (0.0, 2.0, 0.0), (2.0, 2.0, 0.0)],
        faces = [(12, 11, 3, 10), (17, 16, 0, 9), (22, 21, 4, 13), (12, 10, 2, 8), (7, 8, 17, 19), (19, 17, 9, 14), (23, 22, 13, 7), (20, 24, 19, 14), (4, 11, 12, 13), (24, 23, 7, 19), (13, 12, 8, 7), (8, 2, 16, 17), (18, 15, 23, 24), (1, 18, 24, 20), (15, 6, 22, 23), (6, 5, 21, 22)],
        mat_indices = [2, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1],
        material_names = [
        MaterialPrimitives.Pavement.value,
        MaterialPrimitives.Road.value,
        MaterialPrimitives.Building.value
        ],
        pos_x_connector = "ROAD",
        neg_x_connector = "PAVEMENTPOS",
        pos_y_connector = "ROAD",
        neg_y_connector = "PAVEMENTNEG",
        vertex_group_data = {'building_plot': {'vertices': [3, 10, 11, 12], 'weights': [1.0, 1.0, 1.0, 1.0]}, 'pavement_plot': {'vertices': [2, 4, 7, 8, 10, 11, 12, 13, 16, 17, 19, 21, 22, 23, 24], 'weights': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.25]}, 'road_plot': {'vertices': [0, 1, 2, 4, 5, 6, 7, 8, 9, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24], 'weights': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]}}

    )

def pavement_primitive():
    return Primitive(
        name=PrimitiveModules.Pavement.value,
        primitive_type="PAVEMENT",
        verts = [(4.0, -4.0, -0.2), (4.0, 4.0, -0.2), (0.0, 4.0, -0.2), (0.0, -4.0, -0.2), (-4.0, -4.0, 0.0), (-4.0, 4.0, 0.0), (0.0, 4.0, 0.0), (0.0, -4.0, 0.0), (-2.0, -4.0, 0.0), (-2.0, 4.0, 0.0)],
        faces = [(3, 2, 6, 7), (1, 2, 3, 0), (9, 5, 4, 8), (6, 9, 8, 7)],
        mat_indices = [0, 1, 2, 0],
        material_names=[
            MaterialPrimitives.Pavement.value,
            MaterialPrimitives.Road.value,
            MaterialPrimitives.Building.value
        ],
        pos_x_connector = "ROAD",
        neg_x_connector = "BUILDING",
        pos_y_connector = "PAVEMENTPOS",
        neg_y_connector = "PAVEMENTNEG",
        vertex_group_data = {'building_plot': {'vertices': [4, 5, 8, 9], 'weights': [1.0, 1.0, 1.0, 1.0]}, 'pavement_plot': {'vertices': [2, 3, 6, 7, 8, 9], 'weights': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]}, 'road_plot': {'vertices': [0, 1, 2, 3], 'weights': [1.0, 1.0, 1.0, 1.0]}}
    )

def pavement_primitive_alt():
    return Primitive(
        name=PrimitiveModules.Pavement.value,
        primitive_type="PAVEMENT",
        verts = [(4.0, -4.0, 0.0), (4.0, 4.0, 0.0), (4.0, 0.0, 0.0), (4.0, -2.0, 0.0), (-4.0, -4.0, 0.0), (-4.0, 4.0, 0.0), (0.0, 4.0, 0.0), (0.0, -4.0, 0.0), (-2.0, -4.0, 0.0), (-2.0, 4.0, 0.0), (4.0, 2.0, 0.0), (-4.0, -2.0, 0.0), (-4.0, 0.0, 0.0), (-4.0, 2.0, 0.0), (0.0, 2.0, 0.0), (0.0, 0.0, 0.0), (0.0, -2.0, 0.0), (-2.0, -2.0, 0.0), (-2.0, 0.0, 0.0), (-2.0, 2.0, 0.0), (2.0, -4.0, 0.0), (2.0, 4.0, 0.0), (2.0, 2.0, 0.0), (2.0, 0.0, 0.0), (2.0, -2.0, 0.0)],
        faces = [(6, 9, 19, 14), (24, 16, 7, 20), (17, 11, 4, 8), (16, 17, 8, 7), (14, 19, 18, 15), (15, 18, 17, 16), (9, 5, 13, 19), (19, 13, 12, 18), (18, 12, 11, 17), (21, 6, 14, 22), (22, 14, 15, 23), (23, 15, 16, 24), (2, 23, 24, 3), (10, 22, 23, 2), (1, 21, 22, 10), (3, 24, 20, 0)],
        mat_indices = [0, 1, 2, 0, 0, 0, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1],
        material_names=[
            MaterialPrimitives.Pavement.value,
            MaterialPrimitives.Road.value,
            MaterialPrimitives.Building.value
        ],
        pos_x_connector = "ROAD",
        neg_x_connector = "BUILDING",
        pos_y_connector = "PAVEMENTPOS",
        neg_y_connector = "PAVEMENTNEG",        
        vertex_group_data = {'building_plot': {'vertices': [4, 5, 8, 9, 11, 12, 13, 17, 18, 19], 'weights': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]}, 'pavement_plot': {'vertices': [6, 7, 8, 9, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24], 'weights': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.5, 0.5, 0.5, 0.5, 0.5]}, 'road_plot': {'vertices': [0, 1, 2, 3, 10, 20, 21, 22, 23, 24], 'weights': [1.0, 1.0, 1.0, 1.0, 1.0, 0.5, 0.5, 0.5, 0.5, 0.5]}}

    )


def building_primitive():
    return Primitive(
        name=PrimitiveModules.Building.value,
        primitive_type="BUILDING",
        verts = [(-4.0, -4.0, 0.0), (-4.0, 4.0, 0.0), (4.0, -4.0, 0.0), (4.0, 4.0, 0.0)],
        faces = [(3, 1, 0, 2)],
        mat_indices = [0],
        material_names=[
            MaterialPrimitives.Building.value
        ],
        pos_x_connector = "BUILDING",
        neg_x_connector = "BUILDING",
        pos_y_connector = "BUILDING",
        neg_y_connector = "BUILDING",
        vertex_group_data = {'building_plot': {'vertices': [0, 1, 2, 3], 'weights': [1.0, 1.0, 1.0, 1.0]}}
    )

def building_primitive_alt():
    return Primitive(
        name=PrimitiveModules.Building.value,
        primitive_type="BUILDING",
        verts = [(-4.0, -4.0, 0.0), (-4.0, 4.0, 0.0), (4.0, -4.0, 0.0), (4.0, 4.0, 0.0), (-2.0, 4.0, 0.0), (0.0, 4.0, 0.0), (2.0, 4.0, 0.0), (-4.0, -2.0, 0.0), (-4.0, 0.0, 0.0), (-4.0, 2.0, 0.0), (-2.0, -4.0, 0.0), (0.0, -4.0, 0.0), (2.0, -4.0, 0.0), (4.0, -2.0, 0.0), (4.0, 0.0, 0.0), (4.0, 2.0, 0.0), (-2.0, -2.0, 0.0), (-2.0, 0.0, 0.0), (-2.0, 2.0, 0.0), (0.0, -2.0, 0.0), (0.0, 0.0, 0.0), (0.0, 2.0, 0.0), (2.0, -2.0, 0.0), (2.0, 0.0, 0.0), (2.0, 2.0, 0.0)],
        faces = [(24, 15, 3, 6), (9, 18, 4, 1), (18, 21, 5, 4), (21, 24, 6, 5), (0, 10, 16, 7), (7, 16, 17, 8), (8, 17, 18, 9), (10, 11, 19, 16), (16, 19, 20, 17), (17, 20, 21, 18), (11, 12, 22, 19), (19, 22, 23, 20), (20, 23, 24, 21), (12, 2, 13, 22), (22, 13, 14, 23), (23, 14, 15, 24)],
        mat_indices = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        material_names=[
            MaterialPrimitives.Building.value
        ],
        pos_x_connector = "BUILDING",
        neg_x_connector = "BUILDING",
        pos_y_connector = "BUILDING",
        neg_y_connector = "BUILDING",
        vertex_group_data = {'building_plot': {'vertices': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24], 'weights': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]}}
    )
