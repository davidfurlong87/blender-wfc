"""
Pure Python primitive data structure (no Blender dependencies)

This module provides a clean, validated data structure for WFC primitives
that can be serialized/deserialized to/from JSON files.

Design Goals:
- No Blender dependencies (can be tested without Blender)
- Full validation with helpful error messages
- Easy serialization to JSON for persistence
- Type-safe with dataclasses
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional


@dataclass
class PrimitiveData:
    """
    Pure Python representation of a WFC primitive
    
    All coordinates are relative to the primitive's center.
    This data structure has no Blender dependencies and can be
    serialized to JSON for storage.
    
    Attributes:
        name: Unique identifier for the primitive
        primitive_type: Type classification (e.g., 'CORNER', 'BUILDING', 'ROAD')
        verts: List of vertex coordinates [(x, y, z), ...]
        faces: List of face vertex indices [(v1, v2, v3, ...), ...]
        mat_indices: Material index for each face [0, 1, 2, ...]
        material_names: List of material names used
        pos_x_connector: Connector type for +X edge
        neg_x_connector: Connector type for -X edge
        pos_y_connector: Connector type for +Y edge
        neg_y_connector: Connector type for -Y edge
        vertex_groups: Dictionary of vertex groups {name: {'vertices': [...], 'weights': [...]}}
        metadata: Optional metadata (author, version, description, etc.)
    """
    name: str
    primitive_type: str
    verts: List[Tuple[float, float, float]]
    faces: List[Tuple[int, ...]]
    mat_indices: List[int]
    material_names: List[str]
    pos_x_connector: str
    neg_x_connector: str
    pos_y_connector: str
    neg_y_connector: str
    vertex_groups: Dict[str, Dict[str, List]] = field(default_factory=dict)
    metadata: Optional[Dict[str, str]] = None
    
    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate primitive data for correctness
        
        Returns:
            (is_valid, error_messages): Tuple of boolean and list of error strings
        """
        errors = []
        
        # Validate name
        if not self.name or not self.name.strip():
            errors.append("Primitive name cannot be empty")
        
        # Validate primitive type
        if not self.primitive_type or not self.primitive_type.strip():
            errors.append("Primitive type cannot be empty")
        
        # Validate vertices
        if not self.verts:
            errors.append("Primitive must have at least one vertex")
        
        for i, vert in enumerate(self.verts):
            if len(vert) != 3:
                errors.append(f"Vertex {i} must have exactly 3 coordinates (x, y, z)")
        
        # Validate faces
        if not self.faces:
            errors.append("Primitive must have at least one face")
        
        max_vert_index = len(self.verts) - 1
        for i, face in enumerate(self.faces):
            if len(face) < 3:
                errors.append(f"Face {i} must have at least 3 vertices")
            
            for j, vert_index in enumerate(face):
                if not isinstance(vert_index, int):
                    errors.append(f"Face {i}, vertex {j}: index must be an integer")
                elif vert_index < 0 or vert_index > max_vert_index:
                    errors.append(f"Face {i}, vertex {j}: index {vert_index} out of range (0-{max_vert_index})")
        
        # Validate material indices
        if len(self.mat_indices) != len(self.faces):
            errors.append(f"Number of material indices ({len(self.mat_indices)}) must match number of faces ({len(self.faces)})")
        
        max_mat_index = len(self.material_names) - 1
        for i, mat_idx in enumerate(self.mat_indices):
            if not isinstance(mat_idx, int):
                errors.append(f"Material index {i} must be an integer")
            elif mat_idx < 0 or mat_idx > max_mat_index:
                errors.append(f"Face {i}: material index {mat_idx} out of range (0-{max_mat_index})")
        
        # Validate materials
        if not self.material_names:
            # TODO: Optional override? optional default mat?
            errors.append("Primitive must have at least one material")
        
        # Validate connectors (just check they're not empty for now)
        if not self.pos_x_connector:
            errors.append("pos_x_connector cannot be empty")
        if not self.neg_x_connector:
            errors.append("neg_x_connector cannot be empty")
        if not self.pos_y_connector:
            errors.append("pos_y_connector cannot be empty")
        if not self.neg_y_connector:
            errors.append("neg_y_connector cannot be empty")
        
        # Validate vertex groups
        for group_name, group_data in self.vertex_groups.items():
            if 'vertices' not in group_data:
                errors.append(f"Vertex group '{group_name}' missing 'vertices' key")
            elif 'weights' not in group_data:
                errors.append(f"Vertex group '{group_name}' missing 'weights' key")
            else:
                vertices = group_data['vertices']
                weights = group_data['weights']
                
                if len(vertices) != len(weights):
                    errors.append(f"Vertex group '{group_name}': vertices and weights must have same length")
                
                for i, vert_idx in enumerate(vertices):
                    if not isinstance(vert_idx, int):
                        errors.append(f"Vertex group '{group_name}', index {i}: must be an integer")
                    elif vert_idx < 0 or vert_idx > max_vert_index:
                        errors.append(f"Vertex group '{group_name}', index {i}: {vert_idx} out of range (0-{max_vert_index})")
        
        return (len(errors) == 0, errors)
    
    def to_dict(self) -> dict:
        """
        Convert to dictionary for JSON serialization

        Returns:
            Dictionary representation of primitive data
        """
        return {
            'name': self.name,
            'primitive_type': self.primitive_type,
            'verts': list(self.verts),  # Ensure lists, not tuples
            'faces': [list(face) for face in self.faces],
            'mat_indices': list(self.mat_indices),
            'material_names': list(self.material_names),
            'connectors': {
                'pos_x': self.pos_x_connector,
                'neg_x': self.neg_x_connector,
                'pos_y': self.pos_y_connector,
                'neg_y': self.neg_y_connector,
            },
            'vertex_groups': self.vertex_groups,
            'metadata': self.metadata or {}
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'PrimitiveData':
        """
        Create PrimitiveData from dictionary (JSON deserialization)

        Args:
            data: Dictionary representation of primitive data

        Returns:
            PrimitiveData instance

        Raises:
            KeyError: If required keys are missing
            ValueError: If data types are incorrect
        """
        # Handle both old and new connector formats
        if 'connectors' in data:
            connectors = data['connectors']
            pos_x = connectors['pos_x']
            neg_x = connectors['neg_x']
            pos_y = connectors['pos_y']
            neg_y = connectors['neg_y']
        else:
            # Legacy format compatibility
            pos_x = data.get('pos_x_connector', '')
            neg_x = data.get('neg_x_connector', '')
            pos_y = data.get('pos_y_connector', '')
            neg_y = data.get('neg_y_connector', '')

        return cls(
            name=data['name'],
            primitive_type=data['primitive_type'],
            verts=[tuple(v) for v in data['verts']],  # Convert to tuples
            faces=[tuple(f) for f in data['faces']],
            mat_indices=data['mat_indices'],
            material_names=data['material_names'],
            pos_x_connector=pos_x,
            neg_x_connector=neg_x,
            pos_y_connector=pos_y,
            neg_y_connector=neg_y,
            vertex_groups=data.get('vertex_groups', {}),
            metadata=data.get('metadata', None)
        )

