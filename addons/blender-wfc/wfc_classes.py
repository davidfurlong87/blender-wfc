import bpy
from enum import Enum
from .collectiontools.collection_creation import *
from .wfc_values import module_size
from mathutils import Vector

class WFCModule:
    def __init__(self, name, obj_source, module_weight, pos_x, neg_x, pos_y, neg_y):
        self.name = name
        self.obj_source = obj_source
        self.module_weight = module_weight
        self.pos_x = pos_x
        self.neg_x = neg_x
        self.pos_y = pos_y
        self.neg_y = neg_y
        self.pos_x_pairs = []
        self.neg_x_pairs = []
        self.pos_y_pairs = []
        self.neg_y_pairs = []

    def __str__(self):
        return self.name

    def get_all_pairs_fox_axis(self, axis):
        match axis:
            case Axis.POS_X:
                return self.pos_x_pairs
            case Axis.NEG_X:
                return  self.neg_x_pairs
            case Axis.POS_Y:
                return self.pos_y_pairs
            case Axis.NEG_Y:
                return self.neg_y_pairs

    def debug_create_building_plot_planes(self, debug_collection_name="Debug_Building_Plots", center_vector = Vector((0, 0, 0))):
        """
        Debug function: Find faces in 'building_plot' vertex group and create 2x2 planes for each
        """
        if not self.obj_source or not self.obj_source.data:
            print(f"No valid obj_source for module {self.name}")
            return []
        
        # Get the building_plot vertex group
        building_plot_vg = self.obj_source.vertex_groups.get('building_plot')
        if not building_plot_vg:
            print(f"No 'building_plot' vertex group found in {self.obj_source.name}")
            return []
        
        # Get vertices that belong to building_plot vertex group
        building_plot_vertices = set()
        for vert_index, vertex in enumerate(self.obj_source.data.vertices):
            for group in vertex.groups:
                if group.group == building_plot_vg.index:
                    building_plot_vertices.add(vert_index)
                    break
        
        print(f"Found {len(building_plot_vertices)} vertices in building_plot group")
        
        # Find faces where ALL vertices are in building_plot
        building_plot_faces = []
        for face_index, face in enumerate(self.obj_source.data.polygons):
            if all(vert_index in building_plot_vertices for vert_index in face.vertices):
                building_plot_faces.append(face_index)
        
        print(f"Found {len(building_plot_faces)} faces in building_plot group")
        
        if not building_plot_faces:
            print("No building plot faces found")
            return []
        
        # Get or create debug collection
        debug_collection = get_or_create_collection(debug_collection_name)
        
        # Create 2x2 planes for each building plot face
        created_planes = []
        for face_index in building_plot_faces:
            face = self.obj_source.data.polygons[face_index]
            
            # Calculate face center in world coordinates
            face_center = Vector((0, 0, 0))
            for vert_index in face.vertices:
                vert_world_pos = self.obj_source.matrix_world @ self.obj_source.data.vertices[vert_index].co
                face_center += vert_world_pos
            face_center /= len(face.vertices)
            
            # Create 2x2 plane at face center
            bpy.ops.mesh.primitive_plane_add(
                size=2.0, 
                location=face_center + center_vector,

                rotation=(0, 0, 0)
            )
            
            plane_obj = bpy.context.active_object
            plane_obj.name = f"{self.name}_building_plot_face_{face_index}"
            
            # Add some height offset for visibility
            plane_obj.location.z += 1.1
            
            # Link to debug collection
            link_object_to_single_collection(plane_obj, debug_collection)
            created_planes.append(plane_obj)
            
            print(f"Created debug plane for face {face_index} at {face_center}")
        
        print(f"Created {len(created_planes)} debug building plot planes for module {self.name}")
        return created_planes








class WFCCell:
    def __init__(self, posX, posY, possibleModules, mesh_obj, world_pos):
        self.posX = posX
        self.posY = posY
        self.coordinates = WFCCoordinates(posX, posY)
        self.possibleModules = possibleModules[:]
        self.isCollapsed = False
        self.mesh_obj = mesh_obj
        self.world_pos = world_pos

    def __str__(self):
        return f"{self.posX, self.posY}"
    
    # def create_building_plot_planes(self):


    def get_coords(self):
        return [self.posX, self.posY]
    
    def get_coords_set(self):
        return (self.posX, self.posY)

    def get_neighbour_coords_set(self, axis):
        match axis:
            case Axis.POS_X:
                return (self.posX + 1, self.posY)
            case Axis.NEG_X:
                return (self.posX - 1, self.posY)
            case Axis.POS_Y:
                return (self.posX, self.posY + 1)
            case Axis.NEG_Y:
                return (self.posX, self.posY - 1)
    
    def number_of_modules_remaining(self):
        return len(self.possibleModules)
    
    def return_collapsed_module(self):
        # TODO: Add a setter for isCollapsed, then remove the check for len(self.possibleModules)
        if (self.isCollapsed and len(self.possibleModules) == 1):
            return self.possibleModules[0]
        else:
            # TODO: EXCEPTION
            print(f"Cell {self.posX, self.posY} NOT YET COLLAPSED")

    def replace_mesh_obj(self, new_obj):
        delete_object_by_name(self.mesh_obj.name)
        self.mesh_obj = new_obj

    def remove_invalid_modules(self, invalid_modules):
        for module in invalid_modules:
            self.possibleModules.remove(module)
        # print(f"mesh_obj.remaining_modules was: {self.mesh_obj.remaining_modules}")
        self.mesh_obj.remaining_modules = len(self.possibleModules)
        # print(f"mesh_obj.remaining_modules is now: {self.mesh_obj.remaining_modules}")
        
        # Update now happens automatically via property callback
    
    def world_pos_as_vector(self):
        return Vector((self.world_pos))
    

class WFCPlot:
    def __init__(self, world_pos, local_bounds, parent_cell):
        self.world_pos = world_pos
        self.local_bounds = local_bounds  # Local bounds within the 8x8 module
        self.parent_cell = parent_cell
        self.is_processed = False

    def get_world_bounds(self):
        """Convert local bounds to world coordinates"""
        cell_world_pos = Vector((self.parent_cell.posX * module_size, 
                                self.parent_cell.posY * module_size, 0))
        return [(cell_world_pos.x + bound[0], cell_world_pos.y + bound[1]) 
                for bound in self.local_bounds]

class BuildingPlot(WFCPlot):
    def __init__(self, world_pos, local_bounds, parent_cell):
        super().__init__(world_pos, local_bounds, parent_cell)
        self.building_group_id = None


class WFCPlotGroup:
    def __init__(self, group_id, plots):
        self.group_id = group_id
        self.plots = plots
        self.combined_bounds = self._calculate_combined_bounds()
        self.building_grid_size = self._calculate_building_grid_size()
    
    def _calculate_combined_bounds(self):
        """Calculate the bounding box of all plots in this group"""
        all_bounds = []
        for plot in self.plots:
            all_bounds.extend(plot.get_world_bounds())
        
        min_x = min(bound[0] for bound in all_bounds)
        min_y = min(bound[1] for bound in all_bounds)
        max_x = max(bound[0] for bound in all_bounds)
        max_y = max(bound[1] for bound in all_bounds)
        
        return (min_x, min_y, max_x, max_y)
    
    def _calculate_building_grid_size(self):
        """Determine grid size for building generation based on plot size"""
        bounds = self.combined_bounds
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        
        # Example: 1 grid cell per 2x2m area
        grid_x = max(1, int(width / 2))
        grid_y = max(1, int(height / 2))
        
        return (grid_x, grid_y)
    
class BuildingPlotGroup(WFCPlotGroup):
    def __init__(self, group_id, plots):
        super().__init__(group_id, plots)
        self.building_modules = []  # To be filled with selected building modules

# TODO:rename posX/Y. this looks like its an axis, just x/y is fine
class WFCCoordinates:
    def __init__(self, posX, posY):
        self.posX = posX
        self.posY = posY

    def __str__(self):
        return f"{self.posX, self.posY}"

class Axis(Enum):
    POS_X = "PosX"
    NEG_X = "NegX"
    POS_Y = "PosY"
    NEG_Y = "NegY"

class Primitive:
    def __init__(self, name, primitive_type, verts, faces, mat_indices, material_names,pos_x_connector,neg_x_connector,pos_y_connector,neg_y_connector, vertex_group_data):
        self.name = name
        self.primitive_type = primitive_type
        self.verts = verts
        self.faces = faces
        self.mat_indices = mat_indices
        self.material_names = material_names
        self.pos_x_connector = pos_x_connector
        self.neg_x_connector = neg_x_connector
        self.pos_y_connector = pos_y_connector
        self.neg_y_connector = neg_y_connector
        self.vertex_group_data = vertex_group_data

def sockets_match(socket_a, socket_b):
    if (socket_a == 'ROAD'):
            if (socket_b == 'ROAD'):
                return True
            else:
                return False
    if (socket_a == 'BUILDING'):
        if (socket_b == 'BUILDING'):
            return True
        else:
            return False
    if (socket_a == 'PAVEMENTPOS'):
        if (socket_b == 'PAVEMENTNEG'):
            return True
        else:
            return False
    if (socket_a == 'PAVEMENTNEG'):
        if (socket_b == 'PAVEMENTPOS'):
            return True
        else:
            return False

def build_module_pairs(module, all_modules):
    for axis in Axis:
        match axis:
            case Axis.POS_X:
                base_socket = module.pos_x
                for other_module in all_modules:
                    other_socket = other_module.neg_x
                    if sockets_match(base_socket, other_socket):
                        # print(f"Pair: {module.name} pos_x = {module.pos_x} and {other_module.name} neg_x = {other_module.neg_x}")
                        module.pos_x_pairs.append(other_module)
            case Axis.NEG_X:
                base_socket = module.neg_x
                for other_module in all_modules:
                    other_socket = other_module.pos_x
                    if sockets_match(base_socket, other_socket):
                        # print(f"Pair: {module.name} neg_x = {module.neg_x} and {other_module.name} pos_x = {other_module.pos_x}")
                        module.neg_x_pairs.append(other_module)

            case Axis.POS_Y:
                base_socket = module.pos_y
                for other_module in all_modules:
                    other_socket = other_module.neg_y
                    if sockets_match(base_socket, other_socket):
                        # print(f"Pair: {module.name} pos_y = {module.pos_y} and {other_module.name} neg_y = {other_module.neg_y}")
                        module.pos_y_pairs.append(other_module)
            case Axis.NEG_Y:
                base_socket = module.neg_y
                for other_module in all_modules:
                    other_socket = other_module.pos_y
                    if sockets_match(base_socket, other_socket):
                        # print(f"Pair: {module.name} neg_y = {module.neg_y} and {other_module.name} pos_y = {other_module.pos_y}")
                        module.neg_y_pairs.append(other_module)



# def safe_dictionary_get(dict, *keys):
#     for key in keys:
#         try:
#             dict = dict[key]
#         except KeyError:
#             return None
#     return dict