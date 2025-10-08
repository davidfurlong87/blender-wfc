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

def pavement_primitive():
    return Primitive(
        name=PrimitiveModules.Pavement.value,
        primitive_type="PAVEMENT",
        verts = [(4.0, -4.0, -0.2), (4.0, 4.0, -0.2), (0.0, 4.0, -0.2), (0.0, -4.0, -0.2), (-4.0, -4.0, 0.0), (-4.0, 4.0, 0.0), (0.0, 4.0, 0.0), (0.0, -4.0, 0.0), (-2.0, -4.0, 0.0), (-2.0, 4.0, 0.0)],

        # faces = [(2, 3, 1, 0), (6, 4, 9, 10), (3, 4, 6, 1), (0, 1, 6, 5), (12, 8, 7, 11), (9, 12, 11, 10)],
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

def building_primitive():
    return Primitive(
        name=PrimitiveModules.Building.value,
        primitive_type="BUILDING",
        # verts=[(-4.0, -4.0, -0.4), (-4.0, -4.0, 0.0), (-4.0, 4.0, -0.4), (-4.0, 4.0, 0.0), (4.0, -4.0, -0.4),
        #         (4.0, -4.0, 0.0), (4.0, 4.0, -0.4), (4.0, 4.0, 0.0)],
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


# Verts, Faces, Materials and Vertex Groups for Building_Primitive
verts = [(-4.0, -4.0, 0.0), (-4.0, 4.0, 0.0), (4.0, -4.0, 0.0), (4.0, 4.0, 0.0)]
faces = [(3, 1, 0, 2)]
materials = ['Building_Primitive']
mat_indices = [0]
vertex_groups = {'building_plot': {'vertices': [0, 1, 2, 3], 'weights': [1.0, 1.0, 1.0, 1.0]}}