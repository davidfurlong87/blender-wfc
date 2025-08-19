
#
# import bpy
# from random import random, choice, randint
# from mathutils import Vector
# from enum import Enum

# # ----------------------------------------------
# # Define Basic Python Classes
# # ----------------------------------------------

# def delete_cell(x, y):
#     specific_plane = get_cell(x, y)
#     if specific_plane:
#         collection.objects.unlink(specific_plane)
#         del plane_dict[x][y]
#         bpy.data.objects.remove(specific_plane, do_unlink=True)
#
#



#

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