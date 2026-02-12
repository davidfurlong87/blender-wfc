"""
Pure WFC algorithm core - no Blender dependencies

Extracted from __init__.py
Contains the main WFC algorithm logic without any Blender-specific code
"""

import random
from .grid import Grid
from .cell import AlgorithmCell
from .module import AlgorithmModule
from .enums import Axis


def score_module(module_weight):
    """
    Calculate weighted random score for module selection
    
    Pure function - no Blender dependencies
    Extracted from build_module_score() in __init__.py
    
    Args:
        module_weight: Weight value for the module
        
    Returns:
        Weighted random score
    """
    return module_weight * random.randint(1, 10001)


def select_highest_scored_module(modules):
    """
    Select module with highest weighted random score
    
    Pure function - extracted from collapse_cell() in __init__.py
    
    Args:
        modules: List of AlgorithmModule instances
        
    Returns:
        AlgorithmModule with highest score
    """
    if not modules:
        return None
    
    scored_modules = [(score_module(module.weight), module) for module in modules]
    highest = scored_modules[0]
    
    for scored_module in scored_modules:
        if scored_module[0] > highest[0]:
            highest = scored_module
    
    return highest[1]


def get_lowest_entropy_cells(uncollapsed_cells):
    """
    Get cells with lowest entropy (fewest possible modules)
    
    Pure function - no Blender dependencies
    Extracted from __init__.py (unchanged)
    
    Args:
        uncollapsed_cells: List of AlgorithmCell instances
        
    Returns:
        List of AlgorithmCell instances with lowest entropy
    """
    current_fewest_modules = 9999
    lowest_entropy_cells = []
    
    for cell in uncollapsed_cells:
        if cell.number_of_modules_remaining() < current_fewest_modules:
            current_fewest_modules = cell.number_of_modules_remaining()
            lowest_entropy_cells = [cell]
        elif cell.number_of_modules_remaining() == current_fewest_modules:
            lowest_entropy_cells.append(cell)
    
    return lowest_entropy_cells


class WFCAlgorithm:
    """
    Pure WFC algorithm implementation
    
    Encapsulates the Wave Function Collapse algorithm without any Blender dependencies.
    Uses Grid to manage state instead of global variables.
    """
    
    def __init__(self, grid=None):
        """
        Initialize WFC algorithm
        
        Args:
            grid: Grid instance (optional, can be set later)
        """
        self.grid = grid if grid is not None else Grid()
    
    def collapse_cell(self, cell):
        """
        Collapse a cell to a single module
        
        Pure algorithm - extracted from collapse_cell() in __init__.py
        Returns the selected module instead of creating Blender objects
        
        Args:
            cell: AlgorithmCell instance to collapse
            
        Returns:
            AlgorithmModule that was selected
        """
        # Select module using weighted random scoring
        selected_module = select_highest_scored_module(cell.possible_modules)
        
        # Collapse cell to selected module
        cell.collapse_to(selected_module)
        
        # Update grid state
        self.grid.mark_cell_collapsed(cell)
        
        return selected_module
    
    def propagate(self, collapsed_cell):
        """
        Propagate constraints from collapsed cell to neighbors
        
        Pure algorithm - extracted from propagate() in __init__.py
        Removed Blender mesh updates
        
        Args:
            collapsed_cell: AlgorithmCell that was just collapsed
            
        Returns:
            List of cells that were affected by propagation
        """
        affected_cells = [collapsed_cell]
        affected_cells_result = []
        
        while len(affected_cells) > 0:
            current_cell = affected_cells.pop(0)
            
            for axis in Axis:
                neighbor_coords = current_cell.get_neighbor_coords(axis)
                
                # Check if neighbor exists
                if self.grid.has_cell_by_coords(neighbor_coords):
                    neighbor_cell = self.grid.get_cell_by_coords(neighbor_coords)
                    
                    # Only propagate to uncollapsed cells
                    if neighbor_cell and not neighbor_cell.is_collapsed:
                        # Get valid modules for this axis from current cell's possible modules
                        possible_pairs = []
                        for module in current_cell.possible_modules:
                            possible_pairs.extend(module.get_all_pairs_for_axis(axis))
                        
                        # Find modules in neighbor that are NOT compatible
                        invalid_modules = [
                            module for module in neighbor_cell.possible_modules 
                            if module not in possible_pairs
                        ]
                        
                        # Remove invalid modules and continue propagation if any were removed
                        if len(invalid_modules) > 0:
                            neighbor_cell.remove_modules(invalid_modules)
                            affected_cells.append(neighbor_cell)
                            affected_cells_result.append(neighbor_cell)

        return affected_cells_result

    def collapse_all(self):
        """
        Collapse all cells in the grid

        Pure algorithm - extracted from collapse_process() in __init__.py

        Returns:
            List of (cell, selected_module) tuples in collapse order
        """
        collapse_history = []

        if self.grid.get_cell_count() == 0:
            return collapse_history

        uncollapsed_cells = self.grid.get_uncollapsed_cells()

        while len(uncollapsed_cells) > 0:
            # Select random cell from lowest entropy cells
            cell_to_collapse = random.choice(get_lowest_entropy_cells(uncollapsed_cells))

            # Collapse the cell
            selected_module = self.collapse_cell(cell_to_collapse)
            collapse_history.append((cell_to_collapse, selected_module))

            # Remove from uncollapsed list
            uncollapsed_cells.remove(cell_to_collapse)

            # Propagate constraints
            self.propagate(cell_to_collapse)

        return collapse_history

