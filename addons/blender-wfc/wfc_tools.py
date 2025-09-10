
# # ----------------------------------------------
# # General/Universal Functions
# # ----------------------------------------------


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