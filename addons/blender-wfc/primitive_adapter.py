"""
Primitive Adapter - Bridge between Blender and Pure Python Primitive Data

This module provides the adapter layer that converts between Blender objects
and the pure Python PrimitiveData structure.

Design Goals:
- Clean separation: Blender-specific code only in this file
- Validation: All extracted data is validated before use
- Error handling: Clear error messages for users
- Efficiency: Optimized vertex group extraction

See docs/features/PRIMITIVE_GENERATION_ANALYSIS.md for architecture details.
"""

import bpy
from typing import Optional, Tuple, List
from .primitive_data_core import PrimitiveData


class PrimitiveAdapter:
    """
    Adapter for converting between Blender objects and PrimitiveData
    
    This class handles all Blender-specific operations and provides
    a clean interface to work with pure Python primitive data.
    """
    
    def __init__(self):
        """Initialize the adapter"""
        pass
    
    def extract_primitive_from_blender(self, obj: bpy.types.Object) -> Tuple[Optional[PrimitiveData], List[str]]:
        """
        Extract primitive data from a Blender mesh object
        
        Args:
            obj: Blender mesh object with connector properties
            
        Returns:
            (primitive_data, errors): Tuple of PrimitiveData (or None if failed) and error list
        """
        errors = []
        
        # Validate input
        if not obj:
            errors.append("No object provided")
            return None, errors
        
        if obj.type != 'MESH':
            errors.append(f"Object '{obj.name}' is not a mesh (type: {obj.type})")
            return None, errors
        
        mesh = obj.data
        if not mesh:
            errors.append(f"Object '{obj.name}' has no mesh data")
            return None, errors
        
        try:
            # Extract basic mesh data
            verts = [tuple(v.co[:]) for v in mesh.vertices]
            faces = [tuple(p.vertices[:]) for p in mesh.polygons]
            mat_indices = [p.material_index for p in mesh.polygons]
            material_names = [mat.name for mat in obj.data.materials if mat]
            
            # Get primitive type from object property
            primitive_type = getattr(obj, 'primitive_type', 'NONE')
            if primitive_type == 'NONE' or not primitive_type:
                errors.append(f"Object '{obj.name}' has no primitive_type assigned")
                # Don't return yet - collect all errors
            
            # Get connectors from object properties
            pos_x_connector = getattr(obj, 'x_pos_connector', '')
            neg_x_connector = getattr(obj, 'x_neg_connector', '')
            pos_y_connector = getattr(obj, 'y_pos_connector', '')
            neg_y_connector = getattr(obj, 'y_neg_connector', '')
            
            # Check if connectors are assigned
            if not pos_x_connector or not neg_x_connector or not pos_y_connector or not neg_y_connector:
                missing = []
                if not pos_x_connector: missing.append('x_pos_connector')
                if not neg_x_connector: missing.append('x_neg_connector')
                if not pos_y_connector: missing.append('y_pos_connector')
                if not neg_y_connector: missing.append('y_neg_connector')
                errors.append(f"Object '{obj.name}' is missing connectors: {', '.join(missing)}")
            
            # Extract vertex groups (optimized version)
            vertex_groups = self._extract_vertex_groups_optimized(obj)
            
            # Create metadata
            metadata = {
                'blender_object_name': obj.name,
                'extraction_tool': 'PrimitiveAdapter'
            }
            
            # Create PrimitiveData instance
            primitive_data = PrimitiveData(
                name=obj.name,
                primitive_type=primitive_type,
                verts=verts,
                faces=faces,
                mat_indices=mat_indices,
                material_names=material_names,
                pos_x_connector=pos_x_connector,
                neg_x_connector=neg_x_connector,
                pos_y_connector=pos_y_connector,
                neg_y_connector=neg_y_connector,
                vertex_groups=vertex_groups,
                metadata=metadata
            )
            
            # Validate the extracted data
            is_valid, validation_errors = primitive_data.validate()
            if not is_valid:
                errors.extend(validation_errors)
                return None, errors
            
            # Return successful result
            return primitive_data, errors
            
        except Exception as e:
            errors.append(f"Unexpected error extracting primitive from '{obj.name}': {str(e)}")
            return None, errors
    
    def _extract_vertex_groups_optimized(self, obj: bpy.types.Object) -> dict:
        """
        Extract vertex group data from object (optimized version)
        
        This is an O(V × Gv) optimization over the old O(G × V × Gv) version
        where V = vertices, G = groups, Gv = groups per vertex
        
        Args:
            obj: Blender object with vertex groups
            
        Returns:
            Dictionary: {group_name: {'vertices': [...], 'weights': [...]}}
        """
        # Initialize all vertex groups
        vertex_group_data = {vg.name: {'vertices': [], 'weights': []} 
                            for vg in obj.vertex_groups}
        
        # Single pass through vertices
        for vert_index, vertex in enumerate(obj.data.vertices):
            for group in vertex.groups:
                vg_name = obj.vertex_groups[group.group].name
                vertex_group_data[vg_name]['vertices'].append(vert_index)
                vertex_group_data[vg_name]['weights'].append(group.weight)
        
        return vertex_group_data

    def create_blender_object_from_primitive(
        self,
        primitive_data: PrimitiveData,
        collection: Optional[bpy.types.Collection] = None,
        location: Tuple[float, float, float] = (0, 0, 0)
    ) -> Tuple[Optional[bpy.types.Object], List[str]]:
        """
        Create a Blender mesh object from PrimitiveData

        Args:
            primitive_data: PrimitiveData instance to convert
            collection: Blender collection to link object to (None = Scene collection)
            location: World location for the object (x, y, z)

        Returns:
            (mesh_object, errors): Tuple of created object (or None if failed) and error list
        """
        errors = []

        try:
            # Validate primitive data first
            is_valid, validation_errors = primitive_data.validate()
            if not is_valid:
                errors.extend(validation_errors)
                return None, errors

            # Create mesh
            mesh_data = bpy.data.meshes.new(name=primitive_data.name)
            mesh_obj = bpy.data.objects.new(primitive_data.name, mesh_data)
            mesh_obj.location = location

            # Link to collection
            if collection:
                collection.objects.link(mesh_obj)
            else:
                bpy.context.scene.collection.objects.link(mesh_obj)

            # Create mesh geometry from vertices and faces
            mesh_data.from_pydata(primitive_data.verts, [], primitive_data.faces)
            mesh_data.update()

            # Apply materials
            for material_name in primitive_data.material_names:
                material = bpy.data.materials.get(material_name)
                if material:
                    mesh_obj.data.materials.append(material)
                else:
                    errors.append(f"Material '{material_name}' not found in blend file")
                    # Create placeholder material
                    placeholder = bpy.data.materials.new(name=material_name)
                    mesh_obj.data.materials.append(placeholder)

            # Apply material indices to faces
            for i, poly in enumerate(mesh_data.polygons):
                if i < len(primitive_data.mat_indices):
                    poly.material_index = primitive_data.mat_indices[i]

            # Set primitive type property
            mesh_obj.primitive_type = primitive_data.primitive_type

            # Set connector properties
            mesh_obj.x_pos_connector = primitive_data.pos_x_connector
            mesh_obj.x_neg_connector = primitive_data.neg_x_connector
            mesh_obj.y_pos_connector = primitive_data.pos_y_connector
            mesh_obj.y_neg_connector = primitive_data.neg_y_connector

            # Apply vertex groups
            self._apply_vertex_groups(mesh_obj, primitive_data.vertex_groups)

            return mesh_obj, errors

        except Exception as e:
            errors.append(f"Unexpected error creating object from primitive '{primitive_data.name}': {str(e)}")
            return None, errors

    def _apply_vertex_groups(self, obj: bpy.types.Object, vertex_group_data: dict):
        """
        Apply vertex group data to a Blender object

        Args:
            obj: Blender object to apply vertex groups to
            vertex_group_data: Dictionary of vertex group data
        """
        # Clear existing vertex groups
        obj.vertex_groups.clear()

        # Recreate vertex groups
        for group_name, group_data in vertex_group_data.items():
            # Create the vertex group
            vertex_group = obj.vertex_groups.new(name=group_name)

            # Add vertices to the group with their weights
            vertices = group_data.get('vertices', [])
            weights = group_data.get('weights', [])

            for vert_index, weight in zip(vertices, weights):
                vertex_group.add([vert_index], weight, 'REPLACE')

