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


class BlenderWFCAdapter:
    """
    Adapter between Blender and pure WFC algorithm
    
    This class translates between Blender's object-based representation
    and the pure algorithm's data-based representation.
    """
    
    def __init__(self):
        """Initialize the adapter"""
        self.algorithm = None
        self.blender_module_map = {}  # algorithm_id -> bpy.types.Object
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
            self.blender_module_map[bpy_module.name] = bpy_module.obj_source
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
        # Get the Blender object for this module
        source_obj = self.blender_module_map[selected_module.id]

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
        # TODO: This is removing all debug meshes but is also removing the collapsed modules.
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

