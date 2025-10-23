import bpy
from .wfc_classes import WFCCell
from .collectiontools.collection_creation import *
from.wfc_values import module_size, CollectionNames

class GridParameters:
    def __init__(self, x_size, y_size, debug_mesh_size):
        self.x_size = x_size
        self.y_size = y_size
        self.debug_mesh_size = debug_mesh_size

def build_wfc_grid(all_wfc_modules, all_grid_cells, uncollapsed_grid_cells):
    grid_collection = get_collection_by_name(CollectionNames.Grid.value)
    x_size = 10
    y_size = 10
    # debug_mesh_size = 2
    debug_mesh_size = module_size
    for x in range(x_size):
        for y in range(y_size):
            cell_obj_location = (x * (debug_mesh_size), y * (debug_mesh_size), 0)
            bpy.ops.mesh.primitive_plane_add(size=debug_mesh_size, enter_editmode=False, align='WORLD', location=cell_obj_location, scale=(1, 1, 1))
            cell_obj = bpy.context.active_object
            cell_obj.data.materials.append(bpy.data.materials.get("debug_modules_mat"))
            cell_obj.remaining_modules = len(all_wfc_modules)
            cell_obj['remaining_modules'] = len(all_wfc_modules)
            cell_obj.data['remaining_modules'] = len(all_wfc_modules)
            cell_obj.name = f"{x:02d}_{y:02d}_cell"
            # TODO: Currently fails when the below was already the active collection. Modify method so that if its already in colelction then skip
            link_object_to_single_collection(cell_obj, grid_collection)

            cell = WFCCell(
                posX = x, 
                posY = y, 
                possibleModules=all_wfc_modules,
                mesh_obj = cell_obj,
                world_pos = cell_obj_location
                )
            all_grid_cells[(x,y)] = cell
            uncollapsed_grid_cells[(x, y)] = cell

# def build_inner_grid():
#     # take all current grid cells 

#     # loop through each

#         # for each, loop through faces
#             # if face has matching
#     all_grid_cells
