"""
Pure algorithm module class - no Blender dependencies

Extracted from wfc_classes.WFCModule
Stores only algorithm data, no Blender objects
"""

from .enums import Axis


class AlgorithmModule:
    """
    Pure module class for WFC algorithm
    
    Stores module data and connection rules without any Blender objects.
    The module_id should be used to reference the corresponding Blender object
    in the adapter layer.
    """
    
    def __init__(self, module_id, weight, pos_x, neg_x, pos_y, neg_y):
        """
        Initialize a pure algorithm module
        
        Args:
            module_id: Unique identifier for this module (e.g., module name)
            weight: Module weight for weighted random selection
            pos_x: Connector type for positive X direction
            neg_x: Connector type for negative X direction
            pos_y: Connector type for positive Y direction
            neg_y: Connector type for negative Y direction
        """
        self.id = module_id
        self.weight = weight
        self.pos_x = pos_x
        self.neg_x = neg_x
        self.pos_y = pos_y
        self.neg_y = neg_y
        
        # Lists of compatible modules for each direction
        # These are populated during module pair building
        self.pos_x_pairs = []
        self.neg_x_pairs = []
        self.pos_y_pairs = []
        self.neg_y_pairs = []
    
    def __str__(self):
        return str(self.id)
    
    def __repr__(self):
        return f"AlgorithmModule(id={self.id}, weight={self.weight})"
    
    def get_all_pairs_for_axis(self, axis):
        """
        Get all compatible modules for a given axis
        
        Args:
            axis: Axis enum value (POS_X, NEG_X, POS_Y, NEG_Y)
            
        Returns:
            List of compatible AlgorithmModule instances
        """
        match axis:
            case Axis.POS_X:
                return self.pos_x_pairs
            case Axis.NEG_X:
                return self.neg_x_pairs
            case Axis.POS_Y:
                return self.pos_y_pairs
            case Axis.NEG_Y:
                return self.neg_y_pairs
    
    def add_compatible_module(self, axis, module):
        """
        Add a compatible module for a given axis
        
        Args:
            axis: Axis enum value
            module: AlgorithmModule instance that is compatible
        """
        match axis:
            case Axis.POS_X:
                if module not in self.pos_x_pairs:
                    self.pos_x_pairs.append(module)
            case Axis.NEG_X:
                if module not in self.neg_x_pairs:
                    self.neg_x_pairs.append(module)
            case Axis.POS_Y:
                if module not in self.pos_y_pairs:
                    self.pos_y_pairs.append(module)
            case Axis.NEG_Y:
                if module not in self.neg_y_pairs:
                    self.neg_y_pairs.append(module)

