"""
Pure algorithm grid class - no Blender dependencies

Encapsulates grid state that was previously stored in global variables
"""

from .cell import AlgorithmCell


class Grid:
    """
    Grid data structure for WFC algorithm
    
    Encapsulates all grid cells and provides methods for grid operations.
    Replaces global variables: all_grid_cells, uncollapsed_grid_cells
    """
    
    def __init__(self, width=0, height=0):
        """
        Initialize an empty grid
        
        Args:
            width: Grid width (number of cells in X direction)
            height: Grid height (number of cells in Y direction)
        """
        self.width = width
        self.height = height
        self.cells = {}  # (x, y) -> AlgorithmCell
        self.uncollapsed_cells = {}  # (x, y) -> AlgorithmCell
    
    def add_cell(self, cell):
        """
        Add a cell to the grid
        
        Args:
            cell: AlgorithmCell instance
        """
        coords = cell.get_coords_tuple()
        self.cells[coords] = cell
        if not cell.is_collapsed:
            self.uncollapsed_cells[coords] = cell
    
    def get_cell(self, x, y):
        """
        Get cell at coordinates
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            AlgorithmCell instance or None if not found
        """
        return self.cells.get((x, y))
    
    def get_cell_by_coords(self, coords):
        """
        Get cell by coordinate tuple
        
        Args:
            coords: Tuple (x, y)
            
        Returns:
            AlgorithmCell instance or None if not found
        """
        return self.cells.get(coords)
    
    def has_cell(self, x, y):
        """Check if cell exists at coordinates"""
        return (x, y) in self.cells
    
    def has_cell_by_coords(self, coords):
        """Check if cell exists at coordinate tuple"""
        return coords in self.cells
    
    def get_all_cells(self):
        """Get all cells as a list"""
        return list(self.cells.values())
    
    def get_uncollapsed_cells(self):
        """Get all uncollapsed cells as a list"""
        return list(self.uncollapsed_cells.values())
    
    def mark_cell_collapsed(self, cell):
        """
        Mark a cell as collapsed and remove from uncollapsed set
        
        Args:
            cell: AlgorithmCell instance that was collapsed
        """
        coords = cell.get_coords_tuple()
        if coords in self.uncollapsed_cells:
            del self.uncollapsed_cells[coords]
    
    def get_neighbor(self, cell, axis):
        """
        Get neighbor cell in given direction
        
        Args:
            cell: AlgorithmCell instance
            axis: Axis enum value
            
        Returns:
            AlgorithmCell instance or None if no neighbor exists
        """
        neighbor_coords = cell.get_neighbor_coords(axis)
        return self.get_cell_by_coords(neighbor_coords)
    
    def is_complete(self):
        """Check if all cells are collapsed"""
        return len(self.uncollapsed_cells) == 0
    
    def get_cell_count(self):
        """Get total number of cells"""
        return len(self.cells)
    
    def get_uncollapsed_count(self):
        """Get number of uncollapsed cells"""
        return len(self.uncollapsed_cells)
    
    def clear(self):
        """Clear all cells from the grid"""
        self.cells.clear()
        self.uncollapsed_cells.clear()

