# bl_info = {
#     "name": "Wave Function Collapse",
#     "author": "Bakkrimet",
#     "version": (0, 0, 1),
#     "blender": (2, 80, 0),
#     "location": "View3D > Add > Mesh > New Object",
#     "description": "Adds a new Mesh Object",
#     "warning": "",
#     "doc_url": "",
#     "category": "Add Mesh",
# }
#
# import bpy
# from random import random, choice, randint
# from mathutils import Vector
# from enum import Enum
# from bpy.props import (
# #        BoolProperty,
# #        FloatVectorProperty,
#         IntProperty,
# #        FloatProperty,
# #        StringProperty,
# )
#
#
# def clear_collection(collection):
#     if collection:
#         for obj in collection.objects:
#             bpy.data.objects.remove(obj, do_unlink=True)
#
#
# def initialize_collection(collection_name):
#     if collection_name in bpy.data.collections:
#         collection = bpy.data.collections[collection_name]
#         clear_collection(collection)
#     else:
#         collection = bpy.data.collections.new(collection_name)
#         scene = bpy.context.scene
#         scene.collection.children.link(bpy.data.collections[collection_name])
#     return collection
# # ----------------------------------------------
# # Define Basic Python Classes
# # ----------------------------------------------
# x_size = 5
# y_size = 5
# plane_size = 1
#
# plane_dict = {}
#
# collection = initialize_collection("collection_name")
#
# def get_cell(x, y):
#     return plane_dict.get(x, {}).get(y)
#
#
# def delete_cell(x, y):
#     specific_plane = get_cell(x, y)
#     if specific_plane:
#         collection.objects.unlink(specific_plane)
#         del plane_dict[x][y]
#         bpy.data.objects.remove(specific_plane, do_unlink=True)
#
#
# def main(context):
#     collection = initialize_collection()
#
#     for x in range(x_size):
#         plane_dict[x] = {}
#         for y in range(y_size):
#             location = (x * (plane_size * 2), y * (plane_size * 2), 0)
#
#             bpy.ops.object.empty_add(location=location)
#             empty = bpy.context.object
#             empty.name = f"{x:02d}_{y:02d}_holder"
#             bpy.context.collection.objects.unlink(empty)
#             collection.objects.link(empty)
#
#             bpy.ops.mesh.primitive_plane_add(scale=(plane_size, plane_size, 1), enter_editmode=False, align='WORLD',
#                                              location=location)
#             plane = bpy.context.object
#             plane.name = f"{x:02d}_{y:02d}_plane"
#             bpy.context.collection.objects.unlink(plane)
#             collection.objects.link(plane)
#             plane.parent = empty
#             plane.location = (0, 0, 0)
#
#             plane_dict[x][y] = plane
#
#     print(get_cell(x, y))
#     delete_cell(4, 3)
#
# class Cell:
#     def __init__(self, posX, posY, possibleVariantIds, possibleVariants):
#         self.posX = posX
#         self.posY = posY
#         self.possibleVariantIds = possibleVariantIds[:]
#         self.possibleVariants = possibleVariants[:]
#         self.isCollapsed = False
#
#     def __str__(self):
#         return f"{self.posX, self.posY}"
# #        return f"{self.posX}/{self.posY}"
#
#     def get_coords(self):
#         return [self.posX, self.posY]
#
# class Axis(Enum):
#     POS_X = "PosX"
#     NEG_X = "NegX"
#     POS_Y = "PosY"
#     NEG_Y = "NegY"
#
# class Socket(Enum):
#     ROAD_CENTRE = "Road_Centre"
#     PAVEMENT_POS = "Pavement_Positive"
#     PAVEMENT_NEG = "Pavement_Negative"
#     BUILDING = "Building"
#
# class Connector(Enum):
#     POS_X = "PosX_Connector"
#     NEG_X = "NegX_Connector"
#     POS_Y = "PosY_Connector"
#     NEG_Y = "NegY_Connector"
#
# class NeighbourList(Enum):
#     POS_X = "Neighbours_PosX"
#     NEG_X = "Neighbours_NegX"
#     POS_Y = "Neighbours_PosY"
#     NEG_Y = "Neighbours_NegY"
#
# def get_all_axes():
#     return list(Axis)
#
# def get_opposite_axis(axis):
#     match axis:
#         case axis.POS_X:
#             return axis.NEG_X
#         case axis.NEG_X:
#             return axis.POS_X
#         case axis.POS_Y:
#             return axis.NEG_Y
#         case axis.NEG_Y:
#             return axis.POS_Y
#
# # ----------------------------------------------
# # Define Constants
# # ----------------------------------------------
#
# grid_objects_collection_name = "GridObjects"
# prefab_base_collection_name = "PrefabPrimitives"
# prefab_variant_collection_name = "PrefabVariants"
#
# # ----------------------------------------------
# # General/Universal Functions
# # ----------------------------------------------
#
# def instantiate_random_object(xPos, yPos, prefabSize, grid_objects_collection, variant_collection, cell):
# #    chosenVariant = cell.possibleVariants[randint(0, len(cell.possibleVariants)-1)]
#     if len(cell.possibleVariants) > 1:
#         print("too many protos!")
#     chosenVariant = cell.possibleVariants[0]
#     #TODO:  should probably instantiate instead of full copying, at least for debugging
#     variantCopy = chosenVariant.copy()
#     grid_objects_collection.objects.link(variantCopy)
#     variantCopy.location = (xPos * (prefabSize), yPos * (prefabSize), 0)
#     variantCopy.name = f"{xPos:02d}_{yPos:02d}"
#     cell.isCollapsed = True
#
# def safe_dictionary_get(dict, *keys):
#     for key in keys:
#         try:
#             dict = dict[key]
#         except KeyError:
#             return None
#     return dict
#
#
# # ----------------------------------------------
# # WFC Helper Functions
# # ----------------------------------------------
#
# def get_lowest_entropy_cell(uncollapsedCells):
#     cellsWithLowestEntropy = []
#     currentLowestEntropy = 5000;
#     for cell in uncollapsedCells:
#         if len(cell.possibleVariants) == currentLowestEntropy:
#             cellsWithLowestEntropy.append(cell)
#         elif len(cell.possibleVariants) < currentLowestEntropy:
#             cellsWithLowestEntropy.clear()
#             cellsWithLowestEntropy.append(cell)
#             currentLowestEntropy = len(cell.possibleVariants)
#     return choice(cellsWithLowestEntropy)
#
# def collapse_cell(cell):
# #    TODO: use RNG adjusted by weights to determine selected prefab
# #    chosenVariantIndex = choose_random_index()         iterate through, adjust a given variants chance by scaling it based on given weights
#     chosenVariantIndex = randint(0, len(cell.possibleVariants)-1)
#     chosenVariant = cell.possibleVariants[chosenVariantIndex]
#     cell.possibleVariants.clear()
# #   TODO: replace code with cell.possibleVariants = cell.possibleVariants[chosenVariantIndex]
#     cell.possibleVariants = [chosenVariant]
#     print(f"Current cell is {cell.posX}/{cell.posY} \nchosenVariantIndex is {chosenVariantIndex} \nchosenVariant is {chosenVariant}\n")
#
# def get_neighbour_coords(cell_coords, axis):
#     match axis:
#         case axis.POS_X:
#             return (cell_coords[0] + 1,  cell_coords[1])
#         case axis.NEG_X:
#             return (cell_coords[0] -1,  cell_coords[1])
#         case axis.POS_Y:
#             return (cell_coords[0],  cell_coords[1] + 1)
#         case axis.NEG_Y:
#             return (cell_coords[0],  cell_coords[1] - 1)
#
# def propagate(cell, cellMap):
#     cellsAffected = [cell]
#     while (len(cellsAffected) > 0):
#         currentCell = cellsAffected[0]
#         cellsAffected.remove(currentCell)
#         for axis in get_all_axes():
#             oppositeAxis = get_opposite_axis(axis)
#             neighbourCoords = get_neighbour_coords(currentCell.get_coords(), axis)
#             otherCell = safe_dictionary_get(cellMap, neighbourCoords[0], neighbourCoords[1])
#
#
#             print(f"Axis is {axis}\nCurrent cell is {cell}, neibhour cell is {otherCell}\n")
#
#
#     #        otherCell = currentCell.NeighbourAtAxis(currentAxis);
#     #        if (otherCell != null)
#
#
#
# # ----------------------------------------------
# # Panels
# # ----------------------------------------------
#
# class WfcMainPanel(bpy.types.Panel):
#     bl_label = "Wave Function Collapse"
#     bl_idname = "WFC_PT_MAINPANEL"
#     bl_space_type = 'VIEW_3D'
#     bl_region_type = 'UI'
#     bl_catagory = "WFC"
#
#     def draw(self, context):
#         layout = self.layout
#
#         row = layout.row()
#         row.label(text = "Build Grid with WFC")
#         row.operator('object.collapse')
#
# class Collapser(bpy.types.Operator):
#     bl_label = "Collapse"
#     bl_idname = 'object.collapse'
#
#     def execute(self, context):
#         x_size = 5
#         y_size = 5
#         plane_size = 20
#
#         grid_objects_collection = initialize_collection(grid_objects_collection_name)
#         variant_collection = bpy.data.collections[prefab_variant_collection_name]
#         variant_id_list = [object["ID"] for object in variant_collection.objects]
#         variant_list = [object for object in variant_collection.objects]
#
#         cellMap = {}
#         remainingCells = []
#
# #        Build Abstract Grid
#         for x in range(x_size):
#             cellMap[x] = {}
#             for y in range(y_size):
#                 cellMap[x][y] = Cell(x, y, variant_id_list, variant_list)
#                 remainingCells.append(cellMap[x][y])
#         while (len(remainingCells) > 0 ):
#             currentCell = get_lowest_entropy_cell(remainingCells)
#             collapse_cell(currentCell)
#             propagate(currentCell, cellMap)
#             remainingCells.remove(currentCell)
#
#
#         for xKey in cellMap:
#             for yKey in cellMap[xKey]:
#                 currentCell = cellMap[xKey][yKey]
#                 instantiate_random_object(xKey, yKey, plane_size, grid_objects_collection, variant_collection, currentCell)
#
#
#         return {'FINISHED'}
#
#
#
# # ----------------------------------------------
# # Registering/Unregistering
# # ----------------------------------------------
# def register():
#     bpy.utils.register_class(WfcMainPanel)
#     bpy.utils.register_class(Collapser)
#
#
# def unregister():
#     bpy.utils.unregister_class(WfcMainPanel)
#     bpy.utils.unregister_class(Collapser)
#
# if __name__ == "__main__":
#     register()
#