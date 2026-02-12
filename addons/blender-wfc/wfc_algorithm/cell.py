"""
Pure algorithm cell class - no Blender dependencies

Extracted from wfc_classes.WFCCell
Stores only algorithm state, no Blender objects
"""

from .enums import Axis


class AlgorithmCell:
    """
    Pure cell class for WFC algorithm
    
    Stores cell state and possible modules without any Blender objects.
    The cell coordinates can be used to reference the corresponding Blender
    visualization in the adapter layer.
    """
    
    def __init__(self, x, y, possible_modules):
        """
        Initialize a pure algorithm cell
        
        Args:
            x: X coordinate in the grid
            y: Y coordinate in the grid
            possible_modules: List of AlgorithmModule instances that could occupy this cell
        """
        self.x = x
        self.y = y
        self.possible_modules = possible_modules[:]  # Copy the list
        self.is_collapsed = False
    
    def __str__(self):
        return f"Cell({self.x}, {self.y})"
    
    def __repr__(self):
        return f"AlgorithmCell(x={self.x}, y={self.y}, modules={len(self.possible_modules)}, collapsed={self.is_collapsed})"
    
    def get_coords(self):
        """Get coordinates as a list [x, y]"""
        return [self.x, self.y]
    
    def get_coords_tuple(self):
        """Get coordinates as a tuple (x, y)"""
        return (self.x, self.y)
    
    def get_neighbor_coords(self, axis):
        """
        Get coordinates of neighbor cell in given direction
        
        Args:
            axis: Axis enum value (POS_X, NEG_X, POS_Y, NEG_Y)
            
        Returns:
            Tuple (x, y) of neighbor coordinates
        """
        match axis:
            case Axis.POS_X:
                return (self.x + 1, self.y)
            case Axis.NEG_X:
                return (self.x - 1, self.y)
            case Axis.POS_Y:
                return (self.x, self.y + 1)
            case Axis.NEG_Y:
                return (self.x, self.y - 1)
    
    def number_of_modules_remaining(self):
        """Get count of possible modules (entropy)"""
        return len(self.possible_modules)
    
    def collapse_to(self, module):
        """
        Collapse cell to a single module
        
        Args:
            module: AlgorithmModule instance to collapse to
        """
        self.possible_modules = [module]
        self.is_collapsed = True
    
    def get_collapsed_module(self):
        """
        Get the collapsed module
        
        Returns:
            AlgorithmModule instance if collapsed, None otherwise
        """
        if self.is_collapsed and len(self.possible_modules) == 1:
            return self.possible_modules[0]
        else:
            return None
    
    def remove_modules(self, invalid_modules):
        """
        Remove invalid modules from possibilities
        
        Args:
            invalid_modules: List of AlgorithmModule instances to remove
            
        Returns:
            Number of modules removed
        """
        removed_count = 0
        for module in invalid_modules:
            if module in self.possible_modules:
                self.possible_modules.remove(module)
                removed_count += 1
        return removed_count

