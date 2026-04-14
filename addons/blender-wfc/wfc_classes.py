import bpy
from enum import Enum
from .collectiontools.collection_creation import *
from mathutils import Vector

class WFCModule:
    def __init__(self, name, obj_source, module_weight, pos_x, neg_x, pos_y, neg_y,
                 physical_size=8.0):
        self.name = name
        self.obj_source = obj_source
        self.module_weight = module_weight
        self.pos_x = pos_x
        self.neg_x = neg_x
        self.pos_y = pos_y
        self.neg_y = neg_y
        self.physical_size = physical_size
        """Physical size of this module in meters — used for grid cell placement"""
        self.pos_x_pairs = []
        self.neg_x_pairs = []
        self.pos_y_pairs = []
        self.neg_y_pairs = []
        # Cached building plot data (relative coordinates)
        self.building_plot_faces_cache = None
        self.building_plot_center_cache = None

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

# UPNEXT: 
    # def inner_grid_coords(global_module_size, inner_grid_module_size, in_faces):
    #     divisions = global_module_size, inner_grid_module_size
    #     faces = in_faces
    #     # assuming outcer cell centre vector = (0,0,0)
    #     # with inner module size == 2
    #     for face in
    #     for x in divisions:
    #         for y in divisions:
    #             inner_grid_coord = (x, y)

    # def sort_faces_based_on_coords(faces_list, divisions_number):
    #     # TODO: check if blender already does this sorting of faces
    #     # sort faces_list based on x, 
    #     returned_sorted_list = []
    #     for x in range(1, divisions_number +1):
    #         for y in range(1, divisions_number +1):
    #             inner_coord = (x, y)
    #             current_face = faces_list[0]
    #             returned_sorted_list.append((inner_coord, current_face))
    #             # set face in someway
    #     # for face in faces_list:


    #     return True

            
    def is_sub_grid_calculated(self):
        if self.building_plot_faces_cache is not None:
            return True
        else:
            return False

    def _calculate_building_plot_faces(self, inner_cell_size = 2):
        """
        Calculate and cache building plot face data with relative coordinates
        Returns: List of face data dictionaries with relative coordinates
        """
        if self.building_plot_faces_cache is not None:
            return self.building_plot_faces_cache
        
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
        building_plot_face_indices = []
        for face_index, face in enumerate(self.obj_source.data.polygons):
            if all(vert_index in building_plot_vertices for vert_index in face.vertices):
                building_plot_face_indices.append(face_index)
        
        print(f"Found {len(building_plot_face_indices)} faces in building_plot group")
        
        if not building_plot_face_indices:
            print("No building plot faces found")
            self.building_plot_faces_cache = []
            return []
        
        # Calculate module center in world coordinates for reference
        obj_world_center = self.obj_source.matrix_world @ Vector((0, 0, 0))
        self.building_plot_center_cache = obj_world_center
        
        # Process each face and store relative data
        building_plot_faces_data = []
        for face_index in building_plot_face_indices:
            face = self.obj_source.data.polygons[face_index]
            
            # Calculate face center in world coordinates
            face_center_world = Vector((0, 0, 0))
            for vert_index in face.vertices:
                vert_world_pos = self.obj_source.matrix_world @ self.obj_source.data.vertices[vert_index].co
                face_center_world += vert_world_pos
            face_center_world /= len(face.vertices)
            
            # Convert to relative coordinates (relative to module center)
            face_center_relative = face_center_world - obj_world_center
            
            # Get face vertices in relative coordinates
            face_vertices_relative = []
            for vert_index in face.vertices:
                # TODO: Ask what the hell the @ is
                vert_world_pos = self.obj_source.matrix_world @ self.obj_source.data.vertices[vert_index].co
                vert_relative_pos = vert_world_pos - obj_world_center
                face_vertices_relative.append(vert_relative_pos)
            
            # TODO: Add some debug vertex groups maybe to work out how this is working
            # TODO: assign magic numbers to vals
            # Calculate grid coordinates (4x4 grid, bottom-left is (1,1))
            # Assuming faces are 2x2 units and module is 8x8 units centered at origin
            # Grid ranges from -4 to +4 in both axes, so we map to 1-4 grid coordinates
            grid_x = int((face_center_relative.x + 4) / 2) + 1
            grid_y = int((face_center_relative.y + 4) / 2) + 1
            
            # TODO: refactor this from 1 -> 4 to 0 -> 3 scale
            # Clamp to valid range (1,1) to (4,4)
            grid_x = max(1, min(4, grid_x))
            grid_y = max(1, min(4, grid_y))

            face_data = {
                'face_index': face_index,
                'center_relative': face_center_relative,
                'vertices_relative': face_vertices_relative,
                'vertex_indices': list(face.vertices),
                'grid_coord': (grid_x -1, grid_y - 1)
            }
            building_plot_faces_data.append(face_data)
        
        # Cache the result
        self.building_plot_faces_cache = building_plot_faces_data
        print(f"Cached {len(building_plot_faces_data)} building plot faces for module {self.name}")
        
        return building_plot_faces_data

    def debug_create_building_plot_planes(self, debug_collection_name="Debug_Building_Plots", center_vector=Vector((0, 0, 0)), name_override = "", inner_grid_offset_vector = Vector((0, 0, 0)), plot_type = 'Building'):
        """
        Debug function: Create 2x2 planes for each building plot face using cached data
        """
        building_plot_faces = self._calculate_building_plot_faces()
        
        if not building_plot_faces:
            return []
        
        debug_collection = get_or_create_collection(debug_collection_name)
        
        # Create 2x2 planes for each building plot face
        created_planes = []
        coords_to_planes = {}
        for face_data in building_plot_faces:
            x_coord = face_data['grid_coord'][0]
            y_coord = face_data['grid_coord'][1]
            face_index = face_data['face_index']
            
            # Calculate world position from relative position and center_vector
            world_position = face_data['center_relative'] + center_vector
            
            # Create 2x2 plane at calculated position
            bpy.ops.mesh.primitive_plane_add(
                size=2.0, 
                location=world_position,
                rotation=(0, 0, 0)
            )
            
            plane_obj = bpy.context.active_object
            # plane_obj.name = f"{self.name}_building_plot_face_{face_index}"
            
            # Add some height offset for visibility
            plane_obj.location.z += 1.1
            

            
            # Update the plane name to include grid coordinates
            if name_override == "":
                plane_obj.name = f"{self.name}_{plot_type}_plot_({face_data['grid_coord'][0]},{face_data['grid_coord'][1]})_face_{face_index}"
            else:
                # UPNEXT: 
                x_coord = int(face_data['grid_coord'][0] + inner_grid_offset_vector.x)
                y_coord = int(face_data['grid_coord'][1] + inner_grid_offset_vector.y)
                # real_x = int(face_data['grid_coord'][0] + inner_grid_offset_vector.x)
                # real_y = int(face_data['grid_coord'][1] + inner_grid_offset_vector.y)
                plane_obj.name = f"{name_override}_{plot_type}_plot_@_({x_coord},{y_coord})"

            #TODO: Store face data as custom properties for reference. Check if working/needed
            plane_obj['face_index'] = face_index
            plane_obj['relative_center_x'] = face_data['center_relative'].x
            plane_obj['relative_center_y'] = face_data['center_relative'].y
            plane_obj['relative_center_z'] = face_data['center_relative'].z
            plane_obj['grid_coord_x'] = x_coord
            plane_obj['grid_coord_y'] = y_coord
            # Link to debug collection
            link_object_to_single_collection(plane_obj, debug_collection)

            created_planes.append(plane_obj)
            coords_to_planes[(x_coord, y_coord)] = plane_obj


            print(f"Created debug plane for face {face_index} at grid ({face_data['grid_coord'][0]},{face_data['grid_coord'][1]}) - relative pos {face_data['center_relative']}")
        if name_override == "":
            print(f"Created {len(created_planes)} debug {plot_type} plot planes for module {self.name}")
        # UPNEXT: Turn this list of planes into a map[Coord -> PlaneObj]
        # return created_planes
        return coords_to_planes

    def get_building_plot_faces_relative(self):
        """
        Public method to get cached building plot face data with relative coordinates
        Returns: List of face data dictionaries
        """
        return self._calculate_building_plot_faces()

    def clear_building_plot_cache(self):
        """
        Clear cached building plot data (useful if obj_source changes)
        """
        self.building_plot_faces_cache = None
        self.building_plot_center_cache = None
    
    def get_inner_grid(self):
        if self.has_inner_grid():
            return self.inner_grid_cells



# EXAMPLE USAGE
# First call - calculates and caches
# module.debug_create_building_plot_planes(center_vector=Vector((10, 20, 0)))

# Second call - uses cache, much faster
# module.debug_create_building_plot_planes(center_vector=Vector((50, 100, 0)))

# Access cached data directly
# face_data = module.get_building_plot_faces_relative()
# for face in face_data:
#     print(f"Face {face['face_index']} center: {face['center_relative']}")


class WFCCell:
    def __init__(self, posX, posY, possibleModules, mesh_obj, world_pos):
        self.posX = posX
        self.posY = posY
        self.coordinates = WFCCoordinates(posX, posY)
        self.possibleModules = possibleModules[:]
        self.isCollapsed = False
        self.mesh_obj = mesh_obj
        self.world_pos = world_pos
        self.inner_grid_cells = {}

    def __str__(self):
        return f"{self.posX, self.posY}"

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
        self.mesh_obj.remaining_modules = len(self.possibleModules)
        
        # TODO: Update now happens automatically via property callback. Remove the above?
    
    def world_pos_as_vector(self):
        return Vector((self.world_pos))
    
    def has_inner_grid(self):
        if len(self.inner_grid_cells.keys()) > 0:
            return True
        else:
            return False
    
    def inner_grid_vector(self, inner_grid_resolution = 4): # i.e 4x4
        # TODO: is it more performant to do one calculation of (inner_grid_resolution * vector)?
        return Vector((self.posX * inner_grid_resolution, self.posY * inner_grid_resolution))

    def debug_create_building_plot_planes_from_module(self):
        """Debug: Create 2x2 planes for all building plot faces in current modules"""

        inner_grid_offset_vector = self.inner_grid_vector(inner_grid_resolution = 4)
        self.inner_grid_cells = self.return_collapsed_module().debug_create_building_plot_planes(center_vector=self.world_pos_as_vector(), name_override = self.get_coords_set(), inner_grid_offset_vector = inner_grid_offset_vector)
        print(f"Plane debug for {self.posX, self.posY}:")
        # print(f"\tFace cache:")
        module = self.return_collapsed_module()
        print(f"Module {module.name}\n\tCalculated: {module.is_sub_grid_calculated()}")



        # for cached_face in module.building_plot_faces_cache:
        #     print(cached_face['grid_coord'])

        #     print(f"\t\t Grid Coord rel. to Module: {cached_face['grid_coord']}")
        #     cell_pos = (cached_face['grid_coord'][0] + inner_grid_offset_vector.x, cached_face['grid_coord'][1] + inner_grid_offset_vector.y)
        #     print(f"\t\t Grid Coord rel. to Cell {self.posX, self.posY}: {cell_pos}")
            

            # NOTES:
            # 2/1
            # 1/1, 2/1, 3/1, 4/1
            # 5/1, 6/1, 7/1, 8/1

            # 3/1 -> convert to pos-1, multiply by 4
            # 1/1, 2/1, 3/1, 4/1
            # 9/1, 10/1, 11/1, 12/1
        return self.inner_grid_cells
    

class WFCPlot:
    def __init__(self, world_pos, local_bounds, parent_cell):
        self.world_pos = world_pos
        self.local_bounds = local_bounds  # Local bounds within the 8x8 module
        self.parent_cell = parent_cell
        self.is_processed = False

    def get_world_bounds(self, cell_size: float = 8.0):
        """Convert local bounds to world coordinates.

        Args:
            cell_size: Physical size of a grid cell in meters. Defaults to 8.0
                       (outer grid). Pass module.physical_size for accuracy.
        """
        cell_world_pos = Vector((self.parent_cell.posX * cell_size,
                                 self.parent_cell.posY * cell_size, 0))
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
    """
    Check if two connector sockets are compatible

    REPLACED: Hardcoded logic replaced with connector registry (Task 1C.1)

    Args:
        socket_a: First connector type
        socket_b: Second connector type

    Returns:
        True if sockets are compatible, False otherwise
    """
    from .connector_registry import connector_registry
    return connector_registry.matches(socket_a, socket_b)

def build_module_pairs(module, all_modules):
    for axis in Axis:
        match axis:
            case Axis.POS_X:
                base_socket = module.pos_x
                for other_module in all_modules:
                    other_socket = other_module.neg_x
                    if sockets_match(base_socket, other_socket):
                        module.pos_x_pairs.append(other_module)
            case Axis.NEG_X:
                base_socket = module.neg_x
                for other_module in all_modules:
                    other_socket = other_module.pos_x
                    if sockets_match(base_socket, other_socket):
                        module.neg_x_pairs.append(other_module)

            case Axis.POS_Y:
                base_socket = module.pos_y
                for other_module in all_modules:
                    other_socket = other_module.neg_y
                    if sockets_match(base_socket, other_socket):
                        module.pos_y_pairs.append(other_module)
            case Axis.NEG_Y:
                base_socket = module.neg_y
                for other_module in all_modules:
                    other_socket = other_module.pos_y
                    if sockets_match(base_socket, other_socket):
                        module.neg_y_pairs.append(other_module)



# def safe_dictionary_get(dict, *keys):
#     for key in keys:
#         try:
#             dict = dict[key]
#         except KeyError:
#             return None
#     return dict