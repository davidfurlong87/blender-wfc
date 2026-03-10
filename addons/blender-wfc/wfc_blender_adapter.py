"""
Blender WFC Adapter

This module provides the adapter layer between Blender and the pure WFC algorithm.
It handles:
1. Converting Blender modules to AlgorithmModules
2. Converting Blender grid to Grid
3. Running the pure algorithm
4. Visualizing results in Blender

See docs/architecture/ALGORITHM_SEPARATION_GUIDE.md for details.
"""

import bpy
from .wfc_algorithm.core import WFCAlgorithm
from .wfc_algorithm.module import AlgorithmModule
from .wfc_algorithm.cell import AlgorithmCell
from .wfc_algorithm.grid import Grid
from .wfc_algorithm.enums import Axis
from .collectiontools.collection_creation import (
    duplicate_and_move_and_return,
    link_object_to_single_collection,
    get_collection_by_name
)
from .wfc_values import module_size, CollectionNames
from mathutils import Vector


class BlenderWFCAdapter:
    """
    Adapter between Blender and pure WFC algorithm
    
    This class translates between Blender's object-based representation
    and the pure algorithm's data-based representation.
    """
    
    def __init__(self):
        """Initialize the adapter"""
        self.algorithm = None
        self.blender_module_map = {}  # algorithm_id -> WFCModule instance
        self.algorithm_module_map = {}  # algorithm_id -> AlgorithmModule
        self.cell_objects = {}  # (x, y) -> bpy.types.Object (visualization)
        
    def setup_from_blender_modules(self, blender_modules):
        """
        Convert Blender WFCModule instances to pure algorithm modules
        
        Args:
            blender_modules: List of WFCModule instances (from current code)
            
        Returns:
            List of AlgorithmModule instances
        """
        algorithm_modules = []

        for bpy_module in blender_modules:
            # Extract pure data from Blender WFCModule
            # TODO: Consider caching this conversion if performance becomes an issue
            algo_module = AlgorithmModule(
                module_id=bpy_module.name,
                weight=bpy_module.module_weight,
                pos_x=bpy_module.pos_x,
                neg_x=bpy_module.neg_x,
                pos_y=bpy_module.pos_y,
                neg_y=bpy_module.neg_y
            )
            
            algorithm_modules.append(algo_module)

            # Store bidirectional mapping
            # NOTE: Store the WFCModule instance (not obj_source) so we can access methods like _calculate_building_plot_faces()
            self.blender_module_map[bpy_module.name] = bpy_module
            self.algorithm_module_map[bpy_module.name] = algo_module

        return algorithm_modules
    
    def build_algorithm_module_pairs(self, algorithm_modules):
        """
        Build module pair relationships for pure algorithm modules
        
        This is the pure algorithm version of build_module_pairs() from wfc_classes.py
        
        Args:
            algorithm_modules: List of AlgorithmModule instances
        """
        # TODO: This could be optimized by building a connector index
        # instead of O(n²) comparison for each axis
        for module in algorithm_modules:
            for axis in Axis:
                if axis == Axis.POS_X:
                    base_socket = module.pos_x
                    for other_module in algorithm_modules:
                        other_socket = other_module.neg_x
                        if self._sockets_match(base_socket, other_socket):
                            module.add_compatible_module(axis, other_module)
                
                elif axis == Axis.NEG_X:
                    base_socket = module.neg_x
                    for other_module in algorithm_modules:
                        other_socket = other_module.pos_x
                        if self._sockets_match(base_socket, other_socket):
                            module.add_compatible_module(axis, other_module)
                
                elif axis == Axis.POS_Y:
                    base_socket = module.pos_y
                    for other_module in algorithm_modules:
                        other_socket = other_module.neg_y
                        if self._sockets_match(base_socket, other_socket):
                            module.add_compatible_module(axis, other_module)
                
                elif axis == Axis.NEG_Y:
                    base_socket = module.neg_y
                    for other_module in algorithm_modules:
                        other_socket = other_module.pos_y
                        if self._sockets_match(base_socket, other_socket):
                            module.add_compatible_module(axis, other_module)
    
    def _sockets_match(self, socket_a, socket_b):
        """
        Check if two connector sockets are compatible
        
        Extracted from wfc_classes.sockets_match()
        
        Args:
            socket_a: First connector type
            socket_b: Second connector type
            
        Returns:
            True if sockets are compatible
        """
        # TODO: This logic could be simplified with a compatibility matrix
        # or by making connectors match themselves by default
        if socket_a == 'ROAD':
            return socket_b == 'ROAD'
        if socket_a == 'BUILDING':
            return socket_b == 'BUILDING'
        if socket_a == 'PAVEMENTPOS':
            return socket_b == 'PAVEMENTNEG'
        if socket_a == 'PAVEMENTNEG':
            return socket_b == 'PAVEMENTPOS'
        return False

    def create_grid_from_blender(self, algorithm_modules, grid_width, grid_height):
        """
        Create a pure algorithm Grid with cells

        This replaces the global all_grid_cells and uncollapsed_grid_cells

        Args:
            algorithm_modules: List of AlgorithmModule instances
            grid_width: Grid width in cells
            grid_height: Grid height in cells

        Returns:
            Grid instance populated with cells
        """
        grid = Grid(grid_width, grid_height)

        for x in range(grid_width):
            for y in range(grid_height):
                # Create pure algorithm cell
                cell = AlgorithmCell(x, y, algorithm_modules)
                grid.add_cell(cell)

        return grid

    def create_blender_visualization_grid(self, grid_width, grid_height, all_modules_count):
        """
        Create Blender visualization objects for the grid

        This creates the debug plane objects that show cell state.
        Extracted from wfc_grid_builder.build_wfc_grid()

        Args:
            grid_width: Grid width in cells
            grid_height: Grid height in cells
            all_modules_count: Total number of modules (for initial entropy display)
        """
        grid_collection = get_collection_by_name(CollectionNames.Grid.value)
        debug_mesh_size = module_size

        for x in range(grid_width):
            for y in range(grid_height):
                cell_obj_location = (x * debug_mesh_size, y * debug_mesh_size, 0)

                # Create debug plane
                bpy.ops.mesh.primitive_plane_add(
                    size=debug_mesh_size,
                    enter_editmode=False,
                    align='WORLD',
                    location=cell_obj_location,
                    scale=(1, 1, 1)
                )

                cell_obj = bpy.context.active_object
                cell_obj.data.materials.append(bpy.data.materials.get("debug_modules_mat"))
                cell_obj.remaining_modules = all_modules_count
                cell_obj['remaining_modules'] = all_modules_count
                cell_obj.data['remaining_modules'] = all_modules_count
                cell_obj.name = f"{x:02d}_{y:02d}_cell"

                # TODO: Handle case where object is already in collection
                link_object_to_single_collection(cell_obj, grid_collection)

                # Store reference for later updates
                self.cell_objects[(x, y)] = cell_obj

    def visualize_collapsed_cell(self, cell, selected_module):
        """
        Create Blender visualization for a collapsed cell

        This is the Blender-specific part extracted from collapse_cell()

        Args:
            cell: AlgorithmCell that was collapsed
            selected_module: AlgorithmModule that was selected

        Returns:
            Created Blender object
        """
        # Get the WFCModule for this algorithm module
        wfc_module = self.blender_module_map[selected_module.id]
        source_obj = wfc_module.obj_source

        # Calculate placement location
        placement_location = (cell.x * module_size, cell.y * module_size, 0)

        # Create instance of the module
        collapsed_cell_obj = duplicate_and_move_and_return(source_obj, placement_location)
        collapsed_cell_obj.name = f"{cell.x:02d}_{cell.y:02d}-{source_obj.name}"

        # Link to grid collection
        grid_collection = get_collection_by_name(CollectionNames.Grid.value)
        link_object_to_single_collection(collapsed_cell_obj, grid_collection)

        # Remove debug plane (Step 4b: collapsed debug cell object is removed)
        coords = cell.get_coords_tuple()
        if coords in self.cell_objects:
            debug_obj = self.cell_objects[coords]
            bpy.data.objects.remove(debug_obj, do_unlink=True)
            # Store only the collapsed object
            self.cell_objects[coords] = collapsed_cell_obj

        return collapsed_cell_obj

    def update_cell_visualization(self, cell):
        """
        Update the debug visualization for a cell's entropy

        This updates the remaining_modules property on the debug plane.
        Extracted from WFCCell.remove_invalid_modules()

        Step 4c: The remaining debug mesh objects colour is updated to reflect their current entropy.

        Args:
            cell: AlgorithmCell to update visualization for
        """
        coords = cell.get_coords_tuple()
        if coords in self.cell_objects:
            cell_obj_data = self.cell_objects[coords]

            # Only update if it's a debug plane (not a collapsed module)
            # After collapse, cell_objects[coords] is just the collapsed object, not a dict
            if not isinstance(cell_obj_data, dict) and not cell.is_collapsed:
                # This is an uncollapsed debug plane - update its entropy display
                cell_obj_data.remaining_modules = cell.number_of_modules_remaining()

    def collapse_cell_with_visualization(self, cell):
        """
        Collapse a cell and visualize the result

        Combines pure algorithm with Blender visualization

        Args:
            cell: AlgorithmCell to collapse

        Returns:
            Selected AlgorithmModule
        """
        # Run pure algorithm
        selected_module = self.algorithm.collapse_cell(cell)

        # Visualize in Blender
        self.visualize_collapsed_cell(cell, selected_module)

        return selected_module

    def propagate_with_visualization(self, collapsed_cell):
        """
        Propagate constraints and update visualizations

        Combines pure algorithm with Blender visualization updates

        Args:
            collapsed_cell: AlgorithmCell that was just collapsed

        Returns:
            List of affected cells
        """
        # Run pure algorithm
        affected_cells = self.algorithm.propagate(collapsed_cell)

        # Update visualizations for affected cells
        for cell in affected_cells:
            self.update_cell_visualization(cell)

        return affected_cells

    def show_debug_planes(self):
        """
        Show all debug planes (useful for debugging entropy visualization)

        Note: After cells are collapsed, their debug planes are removed, so this
        only shows debug planes for uncollapsed cells.
        """
        for coords, cell_obj_data in self.cell_objects.items():
            # Only uncollapsed cells have debug planes (collapsed cells just have the module)
            if not isinstance(cell_obj_data, dict):
                # Uncollapsed cell - debug plane is the main object
                cell_obj_data.hide_set(False)

    def hide_debug_planes(self):
        """
        Hide all debug planes (default - shows only collapsed modules)

        Note: After cells are collapsed, their debug planes are removed, so this
        only affects uncollapsed cells.
        """
        for coords, cell_obj_data in self.cell_objects.items():
            # Only uncollapsed cells have debug planes
            if not isinstance(cell_obj_data, dict):
                cell_obj_data.hide_set(True)

    def remove_all_debug_planes(self):
        """
        Remove all remaining debug planes

        Step 5b: Because the grid is now collapsed, its debug meshes are no longer needed and are removed.

        This is called after full collapse to clean up any remaining debug visualization.
        """
        coords_to_remove = []
        for coords, cell_obj_data in self.cell_objects.items():
            # If it's still a debug plane (not collapsed), remove it
            if not isinstance(cell_obj_data, dict):
                # This is an uncollapsed debug plane
                try:
                    bpy.data.objects.remove(cell_obj_data, do_unlink=True)
                    coords_to_remove.append(coords)
                except:
                    # Object might already be deleted
                    coords_to_remove.append(coords)

        # Clean up the tracking dict
        for coords in coords_to_remove:
            del self.cell_objects[coords]

    def setup_and_run_full_collapse(self, blender_modules, grid_width=10, grid_height=10):
        """
        Complete workflow: setup algorithm and run full collapse with visualization

        Step 5a: If the user presses "Full Collapse" then the current grid is fully collapsed from its present state.
        Step 5b: Because the grid is now collapsed, its debug meshes are no longer needed and are removed.

        This is the high-level method that replaces the current workflow in operators.

        Args:
            blender_modules: List of WFCModule instances (from current code)
            grid_width: Grid width in cells (default: 10)
            grid_height: Grid height in cells (default: 10)

        Returns:
            List of (cell, selected_module) tuples in collapse order
        """
        # Only setup if not already initialized (user should have called "Build Grid" first)
        if self.algorithm is None:
            # User didn't build grid first - create it for them
            # Step 1: Convert Blender modules to algorithm modules
            algorithm_modules = self.setup_from_blender_modules(blender_modules)

            # Step 2: Build module pair relationships
            self.build_algorithm_module_pairs(algorithm_modules)

            # Step 3: Create pure algorithm grid
            grid = self.create_grid_from_blender(algorithm_modules, grid_width, grid_height)

            # Step 4: Create Blender visualization grid (debug meshes)
            self.create_blender_visualization_grid(grid_width, grid_height, len(algorithm_modules))

            # Step 5: Initialize algorithm with grid
            self.algorithm = WFCAlgorithm(grid)

        # Step 6: Run collapse with visualization
        collapse_history = []
        # Get uncollapsed cells from the algorithm's grid (works whether grid was just created or already existed)
        uncollapsed_cells = self.algorithm.grid.get_uncollapsed_cells()

        while len(uncollapsed_cells) > 0:
            # Import here to avoid circular dependency
            # TODO: Consider moving get_lowest_entropy_cells to a utility module
            from .wfc_algorithm.core import get_lowest_entropy_cells
            import random

            # Select random cell from lowest entropy cells
            cell_to_collapse = random.choice(get_lowest_entropy_cells(uncollapsed_cells))

            # Collapse with visualization
            selected_module = self.collapse_cell_with_visualization(cell_to_collapse)
            collapse_history.append((cell_to_collapse, selected_module))

            # Remove from uncollapsed list
            uncollapsed_cells.remove(cell_to_collapse)

            # Propagate with visualization
            self.propagate_with_visualization(cell_to_collapse)

        # Step 5b: Remove all remaining debug meshes after full collapse
        # TODO: This is removing all debug meshes but is also removing the collapsed cells which I want to keep.
        # self.remove_all_debug_planes()

        return collapse_history

    def debug_collapse_single_cell(self, blender_modules, grid_width=10, grid_height=10):
        """
        Debug mode: setup and collapse just one cell

        Useful for testing and debugging the algorithm step-by-step.

        Args:
            blender_modules: List of WFCModule instances
            grid_width: Grid width in cells (default: 10)
            grid_height: Grid height in cells (default: 10)

        Returns:
            Tuple of (collapsed_cell, selected_module) or None if grid is complete
        """
        # Setup if not already done
        if self.algorithm is None:
            algorithm_modules = self.setup_from_blender_modules(blender_modules)
            self.build_algorithm_module_pairs(algorithm_modules)
            grid = self.create_grid_from_blender(algorithm_modules, grid_width, grid_height)
            self.create_blender_visualization_grid(grid_width, grid_height, len(algorithm_modules))
            self.algorithm = WFCAlgorithm(grid)

        # Check if there are uncollapsed cells
        uncollapsed_cells = self.algorithm.grid.get_uncollapsed_cells()
        if len(uncollapsed_cells) == 0:
            return None

        # Collapse one cell
        from .wfc_algorithm.core import get_lowest_entropy_cells
        import random

        cell_to_collapse = random.choice(get_lowest_entropy_cells(uncollapsed_cells))
        selected_module = self.collapse_cell_with_visualization(cell_to_collapse)
        self.propagate_with_visualization(cell_to_collapse)

        return (cell_to_collapse, selected_module)

    # ========================================================================
    # Plot Extraction and Grouping (Generic for all plot types)
    # ========================================================================

    def extract_plots_from_grid(self, plot_type='building_plot', vertex_group_name=None):
        """
        Extract plot data from collapsed grid cells (generic for any plot type)

        This method works for any plot type: building, road, pavement, park, etc.
        It uses vertex groups to identify plot faces on modules.

        Args:
            plot_type: Type of plot to extract (e.g., 'building', 'road', 'pavement', 'park')
            vertex_group_name: Name of vertex group to look for (default: '{plot_type}_plot')

        Returns:
            List of plot dictionaries with structure:
            {
                'plot_type': str,
                'world_pos': Vector,
                'center_relative': Vector,
                'grid_coord': (int, int),  # Relative to inner grid (0-3, 0-3)
                'outer_cell_coords': (int, int),  # Outer grid coordinates
                'vertices_relative': List[Vector],
                'face_index': int
            }
        """
        if vertex_group_name is None:
            vertex_group_name = f'{plot_type}_plot'

        all_plots = []

        # Iterate through collapsed cells
        for coords, cell_obj in self.cell_objects.items():
            # Skip debug planes (old structure used dicts)
            if isinstance(cell_obj, dict):
                continue

            # Get algorithm cell
            algorithm_cell = self.algorithm.grid.cells.get(coords)
            if not algorithm_cell or not algorithm_cell.is_collapsed:
                continue

            # Get the Blender module that was placed at this cell
            # Note: possible_modules[0] is an AlgorithmModule instance, we need its .id property
            algorithm_module = algorithm_cell.possible_modules[0]
            blender_module = self.blender_module_map.get(algorithm_module.id)


            if blender_module and hasattr(blender_module, 'obj_source'):
                # Extract plot faces from this module using vertex groups
                plot_faces = self._extract_plot_faces_from_module(
                    blender_module,
                    vertex_group_name
                )

                # Convert to world coordinates and add to list
                for face_data in plot_faces:
                    world_pos = Vector((
                        coords[0] * module_size + face_data['center_relative'].x,
                        coords[1] * module_size + face_data['center_relative'].y,
                        0
                    ))

                    plot = {
                        'plot_type': plot_type,
                        'world_pos': world_pos,
                        'center_relative': face_data['center_relative'],
                        'grid_coord': face_data['grid_coord'],
                        'outer_cell_coords': coords,
                        'vertices_relative': face_data['vertices_relative'],
                        'face_index': face_data['face_index']
                    }
                    all_plots.append(plot)

        return all_plots

    def _extract_plot_faces_from_module(self, blender_module, vertex_group_name):
        """
        Extract plot faces from a module using vertex groups

        This is a generic version of WFCModule._calculate_building_plot_faces()
        that works with any vertex group name.

        Args:
            blender_module: WFCModule instance
            vertex_group_name: Name of vertex group to look for

        Returns:
            List of face data dictionaries with relative coordinates
        """
        if not blender_module.obj_source or not blender_module.obj_source.data:
            return []

        # Get the vertex group
        vertex_group = blender_module.obj_source.vertex_groups.get(vertex_group_name)
        if not vertex_group:
            # Silently skip modules without this vertex group
            return []

        # Get vertices that belong to the vertex group
        plot_vertices = set()
        for vert_index, vertex in enumerate(blender_module.obj_source.data.vertices):
            for group in vertex.groups:
                if group.group == vertex_group.index:
                    plot_vertices.add(vert_index)
                    break

        if not plot_vertices:
            return []

        # Find faces where ALL vertices are in the vertex group
        plot_face_indices = []
        for face_index, face in enumerate(blender_module.obj_source.data.polygons):
            if all(vert_index in plot_vertices for vert_index in face.vertices):
                plot_face_indices.append(face_index)

        if not plot_face_indices:
            return []

        # Calculate module center in world coordinates for reference
        obj_world_center = blender_module.obj_source.matrix_world @ Vector((0, 0, 0))

        # Process each face and store relative data
        plot_faces_data = []
        for face_index in plot_face_indices:
            face = blender_module.obj_source.data.polygons[face_index]

            # Calculate face center in world coordinates
            face_center_world = Vector((0, 0, 0))
            for vert_index in face.vertices:
                vert_world_pos = blender_module.obj_source.matrix_world @ blender_module.obj_source.data.vertices[vert_index].co
                face_center_world += vert_world_pos
            face_center_world /= len(face.vertices)

            # Convert to relative coordinates (relative to module center)
            face_center_relative = face_center_world - obj_world_center

            # Get face vertices in relative coordinates
            face_vertices_relative = []
            for vert_index in face.vertices:
                vert_world_pos = blender_module.obj_source.matrix_world @ blender_module.obj_source.data.vertices[vert_index].co
                vert_relative_pos = vert_world_pos - obj_world_center
                face_vertices_relative.append(vert_relative_pos)

            # Calculate grid coordinates (4x4 grid, 0-indexed)
            # Assuming faces are 2x2 units and module is 8x8 units centered at origin
            # Grid ranges from -4 to +4 in both axes, so we map to 0-3 grid coordinates
            grid_x = int((face_center_relative.x + 4) / 2)
            grid_y = int((face_center_relative.y + 4) / 2)

            # Clamp to valid range (0-3)
            grid_x = max(0, min(3, grid_x))
            grid_y = max(0, min(3, grid_y))

            face_data = {
                'face_index': face_index,
                'center_relative': face_center_relative,
                'vertices_relative': face_vertices_relative,
                'vertex_indices': list(face.vertices),
                'grid_coord': (grid_x, grid_y)
            }
            plot_faces_data.append(face_data)

        return plot_faces_data

    def group_plot_islands(self, plots, plot_type='building'):
        """
        Group adjacent plots into islands using flood fill

        Generic method that works for any plot type (building, road, pavement, park, etc.)

        Args:
            plots: List of plot dictionaries from extract_plots_from_grid()
            plot_type: Type of plot being grouped (for naming/identification)

        Returns:
            List of island dictionaries with structure:
            {
                'island_id': int,
                'plot_type': str,
                'plots': List[dict],  # List of plot dictionaries
                'combined_bounds': (min_x, min_y, max_x, max_y),
                'grid_size': (width, height)  # In outer grid cells
            }
        """
        islands = []
        current_island_id = 0
        processed_plots = set()

        for i, plot in enumerate(plots):
            if i in processed_plots:
                continue

            # Start a new island with flood fill
            current_island_plots = []
            plots_to_process = [i]

            while plots_to_process:
                current_plot_index = plots_to_process.pop(0)
                if current_plot_index in processed_plots:
                    continue

                processed_plots.add(current_plot_index)
                current_island_plots.append(plots[current_plot_index])

                # Find adjacent plots
                adjacent_indices = self._find_adjacent_plot_indices(
                    current_plot_index,
                    plots,
                    processed_plots
                )
                plots_to_process.extend(adjacent_indices)

            if current_island_plots:
                # Calculate combined bounds for this island
                combined_bounds = self._calculate_island_bounds(current_island_plots)
                grid_size = self._calculate_island_grid_size(combined_bounds)

                island = {
                    'island_id': current_island_id,
                    'plot_type': plot_type,
                    'plots': current_island_plots,
                    'combined_bounds': combined_bounds,
                    'grid_size': grid_size
                }
                islands.append(island)
                current_island_id += 1

        return islands

    def _find_adjacent_plot_indices(self, target_index, all_plots, processed_plots):
        """Find indices of plots adjacent to the target plot"""
        adjacent_indices = []
        target_plot = all_plots[target_index]
        target_coords = target_plot['outer_cell_coords']
        target_grid_coord = target_plot['grid_coord']

        for i, plot in enumerate(all_plots):
            if i == target_index or i in processed_plots:
                continue

            plot_coords = plot['outer_cell_coords']
            plot_grid_coord = plot['grid_coord']

            # Check if plots are adjacent (same outer cell or neighboring outer cells)
            if self._plots_are_adjacent(
                target_coords, target_grid_coord,
                plot_coords, plot_grid_coord
            ):
                adjacent_indices.append(i)

        return adjacent_indices

    def _plots_are_adjacent(self, coords1, grid_coord1, coords2, grid_coord2):
        """
        Check if two plots are adjacent

        Plots are adjacent if:
        1. They're in the same outer cell and share an edge in the inner grid
        2. They're in neighboring outer cells and share an edge across the boundary
        """
        # Same outer cell - check inner grid adjacency
        if coords1 == coords2:
            dx = abs(grid_coord1[0] - grid_coord2[0])
            dy = abs(grid_coord1[1] - grid_coord2[1])
            # Adjacent if exactly one coordinate differs by 1
            return (dx == 1 and dy == 0) or (dx == 0 and dy == 1)

        # Different outer cells - check if cells are adjacent and plots are on touching edges
        outer_dx = abs(coords1[0] - coords2[0])
        outer_dy = abs(coords1[1] - coords2[1])

        # Outer cells must be adjacent (not diagonal)
        if not ((outer_dx == 1 and outer_dy == 0) or (outer_dx == 0 and outer_dy == 1)):
            return False

        # Check if plots are on the touching edges
        if outer_dx == 1:  # Horizontally adjacent outer cells
            # Plot 1 should be on right edge (grid_x == 3) if coords1[0] < coords2[0]
            # Plot 2 should be on left edge (grid_x == 0) if coords1[0] < coords2[0]
            if coords1[0] < coords2[0]:
                return grid_coord1[0] == 3 and grid_coord2[0] == 0 and grid_coord1[1] == grid_coord2[1]
            else:
                return grid_coord1[0] == 0 and grid_coord2[0] == 3 and grid_coord1[1] == grid_coord2[1]

        if outer_dy == 1:  # Vertically adjacent outer cells
            # Plot 1 should be on top edge (grid_y == 3) if coords1[1] < coords2[1]
            # Plot 2 should be on bottom edge (grid_y == 0) if coords1[1] < coords2[1]
            if coords1[1] < coords2[1]:
                return grid_coord1[1] == 3 and grid_coord2[1] == 0 and grid_coord1[0] == grid_coord2[0]
            else:
                return grid_coord1[1] == 0 and grid_coord2[1] == 3 and grid_coord1[0] == grid_coord2[0]

        return False

    def _calculate_island_bounds(self, island_plots):
        """Calculate combined bounding box for an island"""
        if not island_plots:
            return (0, 0, 0, 0)

        min_x = min(plot['world_pos'].x for plot in island_plots)
        min_y = min(plot['world_pos'].y for plot in island_plots)
        max_x = max(plot['world_pos'].x for plot in island_plots)
        max_y = max(plot['world_pos'].y for plot in island_plots)

        # Expand by plot size (assuming 2x2 plots)
        plot_half_size = 1.0  # Half of 2x2 plot
        return (min_x - plot_half_size, min_y - plot_half_size,
                max_x + plot_half_size, max_y + plot_half_size)

    def _calculate_island_grid_size(self, bounds):
        """Calculate grid size in outer cells for an island"""
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]

        # Convert to outer cell count
        grid_width = max(1, int(width / module_size))
        grid_height = max(1, int(height / module_size))

        return (grid_width, grid_height)

    def create_inner_grid_for_island(self, island, resolution_multiplier=4, inner_modules=None):
        """
        Create a higher-resolution WFC grid for an island

        This creates an inner grid that can be collapsed using the same WFC algorithm
        to generate detailed content (e.g., buildings, parks, etc.) on the island.

        Args:
            island: Island dictionary from group_plot_islands()
            resolution_multiplier: How many inner cells per outer cell (default: 4)
                                   e.g., 4 = 4x4 inner grid per outer cell
                                   Higher = more detail but slower
            inner_modules: List of AlgorithmModule instances to use for inner grid
                          If None, you'll need to provide modules separately

        Returns:
            Grid instance for the inner grid (from wfc_algorithm.grid)

        Example:
            # Create 4x4 inner grid (16 cells per outer cell)
            inner_grid = adapter.create_inner_grid_for_island(island, resolution_multiplier=4)

            # Create 8x8 inner grid (64 cells per outer cell) for more detail
            inner_grid = adapter.create_inner_grid_for_island(island, resolution_multiplier=8)
        """
        # Calculate inner grid dimensions
        grid_size = island['grid_size']  # Size in outer cells
        inner_width = grid_size[0] * resolution_multiplier
        inner_height = grid_size[1] * resolution_multiplier

        # Create inner grid
        inner_grid = Grid(width=inner_width, height=inner_height)

        # If modules provided, create cells with those modules
        if inner_modules:
            for x in range(inner_width):
                for y in range(inner_height):
                    cell = AlgorithmCell(
                        x=x,
                        y=y,
                        possible_modules=inner_modules[:]
                    )
                    inner_grid.add_cell(cell)
        else:
            # Create empty grid (modules will be added later)
            for x in range(inner_width):
                for y in range(inner_height):
                    cell = AlgorithmCell(
                        x=x,
                        y=y,
                        possible_modules=[]
                    )
                    inner_grid.add_cell(cell)

        # TODO: Set edge constraints based on outer grid
        # Inner grid edges should match the outer grid's constraints

        return inner_grid


# Global adapter instance (singleton pattern)
# TODO: Consider using Blender's property system instead of global variable
_global_adapter = None


def get_wfc_adapter():
    """
    Get or create the global WFC adapter instance

    Returns:
        BlenderWFCAdapter instance
    """
    global _global_adapter
    if _global_adapter is None:
        _global_adapter = BlenderWFCAdapter()
    return _global_adapter


def reset_wfc_adapter():
    """
    Reset the global adapter (useful when clearing grid/modules)
    """
    global _global_adapter
    _global_adapter = None

