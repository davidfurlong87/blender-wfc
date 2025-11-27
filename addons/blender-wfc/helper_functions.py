import bpy 
from .wfc_values import CollectionNames
from .collectiontools.collection_creation import *

# def clear_data_from_scene(collection_name):
#     #  for list in lists:
#     #       list.clear()
#     return True
     
     
# def clear_all_primitives():
#         all_primitives.clear()
#         delete_objects_and_meshes(
#             get_all_objects_from_collection(CollectionNames.Primitives.value)
#         )

# def clear_all_modules():
#     all_modules.clear()
#     delete_objects_and_meshes(get_all_objects_from_collection(CollectionNames.Modules.value))

# def clear_all_cells():
#     delete_objects_and_meshes(
#         get_all_objects_from_collection(CollectionNames.Grid.value)
#     )
#     # TODO: For this and the other clears, might be better looping through the code list and deleting whatever is there.
#     all_grid_cells.clear()
#     uncollapsed_grid_cells.clear()
