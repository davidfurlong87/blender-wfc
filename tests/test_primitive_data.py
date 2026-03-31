"""
Unit tests for PrimitiveData class

These tests do NOT require Blender - they test the pure Python data structure.
Run with: python -m pytest tests/test_primitive_data.py
"""

import sys
from pathlib import Path

# Add the addons directory to the path so we can import primitive_data_core
addon_path = Path(__file__).parent.parent / "addons" / "blender-wfc"
# TODO: is this permanent?
sys.path.insert(0, str(addon_path))

from primitive_data_core import PrimitiveData


class TestPrimitiveDataValidation:
    """Test validation methods"""
    
    def test_valid_primitive(self):
        """Test that a valid primitive passes validation"""
        primitive = PrimitiveData(
            name="Test_Primitive",
            primitive_type="TEST",
            verts=[(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0), (0.0, 1.0, 0.0)],
            faces=[(0, 1, 2, 3)],
            mat_indices=[0],
            material_names=["TestMaterial"],
            pos_x_connector="ROAD",
            neg_x_connector="ROAD",
            pos_y_connector="PAVEMENT",
            neg_y_connector="PAVEMENT",
            vertex_groups={},
            metadata=None
        )
        
        is_valid, errors = primitive.validate()
        assert is_valid, f"Valid primitive failed validation: {errors}"
        assert len(errors) == 0
    
    def test_empty_name(self):
        """Test that empty name fails validation"""
        primitive = PrimitiveData(
            name="",
            primitive_type="TEST",
            verts=[(0.0, 0.0, 0.0)],
            faces=[(0,)],
            mat_indices=[0],
            material_names=["TestMaterial"],
            pos_x_connector="ROAD",
            neg_x_connector="ROAD",
            pos_y_connector="ROAD",
            neg_y_connector="ROAD"
        )
        
        is_valid, errors = primitive.validate()
        assert not is_valid
        assert any("name" in err.lower() for err in errors)
    
    def test_invalid_vertex_count(self):
        """Test that vertices with wrong coordinate count fail"""
        primitive = PrimitiveData(
            name="Test",
            primitive_type="TEST",
            verts=[(0.0, 0.0), (1.0, 1.0)],  # Only 2 coordinates
            faces=[(0, 1)],
            mat_indices=[0],
            material_names=["TestMaterial"],
            pos_x_connector="ROAD",
            neg_x_connector="ROAD",
            pos_y_connector="ROAD",
            neg_y_connector="ROAD"
        )
        
        is_valid, errors = primitive.validate()
        assert not is_valid
        assert any("3 coordinates" in err for err in errors)
    
    def test_face_index_out_of_range(self):
        """Test that face with invalid vertex index fails"""
        primitive = PrimitiveData(
            name="Test",
            primitive_type="TEST",
            verts=[(0.0, 0.0, 0.0), (1.0, 0.0, 0.0)],
            faces=[(0, 1, 5)],  # Index 5 doesn't exist
            mat_indices=[0],
            material_names=["TestMaterial"],
            pos_x_connector="ROAD",
            neg_x_connector="ROAD",
            pos_y_connector="ROAD",
            neg_y_connector="ROAD"
        )
        
        is_valid, errors = primitive.validate()
        assert not is_valid
        assert any("out of range" in err for err in errors)
    
    def test_material_index_count_mismatch(self):
        """Test that material indices must match face count"""
        primitive = PrimitiveData(
            name="Test",
            primitive_type="TEST",
            verts=[(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0)],
            faces=[(0, 1, 2), (0, 2, 1)],
            mat_indices=[0],  # Only 1 material index for 2 faces
            material_names=["TestMaterial"],
            pos_x_connector="ROAD",
            neg_x_connector="ROAD",
            pos_y_connector="ROAD",
            neg_y_connector="ROAD"
        )
        
        is_valid, errors = primitive.validate()
        assert not is_valid
        assert any("must match number of faces" in err for err in errors)
    
    def test_vertex_group_validation(self):
        """Test vertex group validation"""
        primitive = PrimitiveData(
            name="Test",
            primitive_type="TEST",
            verts=[(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0)],
            faces=[(0, 1, 2)],
            mat_indices=[0],
            material_names=["TestMaterial"],
            pos_x_connector="ROAD",
            neg_x_connector="ROAD",
            pos_y_connector="ROAD",
            neg_y_connector="ROAD",
            vertex_groups={
                "test_group": {
                    "vertices": [0, 1, 5],  # Index 5 out of range
                    "weights": [1.0, 1.0, 1.0]
                }
            }
        )
        
        is_valid, errors = primitive.validate()
        assert not is_valid
        assert any("out of range" in err and "test_group" in err for err in errors)


class TestPrimitiveDataSerialization:
    """Test serialization/deserialization"""
    
    def test_to_dict(self):
        """Test conversion to dictionary"""
        primitive = PrimitiveData(
            name="Test_Primitive",
            primitive_type="TEST",
            verts=[(0.0, 0.0, 0.0), (1.0, 0.0, 0.0)],
            faces=[(0, 1)],
            mat_indices=[0],
            material_names=["TestMaterial"],
            pos_x_connector="ROAD",
            neg_x_connector="PAVEMENT",
            pos_y_connector="BUILDING",
            neg_y_connector="NONE"
        )
        
        data = primitive.to_dict()
        
        assert data['name'] == "Test_Primitive"
        assert data['primitive_type'] == "TEST"
        assert 'connectors' in data
        assert data['connectors']['pos_x'] == "ROAD"
        assert data['connectors']['neg_x'] == "PAVEMENT"
        assert data['connectors']['pos_y'] == "BUILDING"
        assert data['connectors']['neg_y'] == "NONE"

    def test_from_dict(self):
        """Test creation from dictionary"""
        data = {
            'name': 'Test_Primitive',
            'primitive_type': 'TEST',
            'verts': [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]],
            'faces': [[0, 1]],
            'mat_indices': [0],
            'material_names': ['TestMaterial'],
            'connectors': {
                'pos_x': 'ROAD',
                'neg_x': 'PAVEMENT',
                'pos_y': 'BUILDING',
                'neg_y': 'NONE'
            }
        }

        primitive = PrimitiveData.from_dict(data)

        assert primitive.name == "Test_Primitive"
        assert primitive.primitive_type == "TEST"
        assert len(primitive.verts) == 2
        assert primitive.pos_x_connector == "ROAD"
        assert primitive.neg_y_connector == "NONE"

    def test_round_trip_serialization(self):
        """Test that to_dict -> from_dict preserves data"""
        original = PrimitiveData(
            name="RoundTrip_Test",
            primitive_type="CORNER",
            verts=[(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0)],
            faces=[(0, 1, 2)],
            mat_indices=[0],
            material_names=["Material1", "Material2"],
            pos_x_connector="ROAD",
            neg_x_connector="ROAD",
            pos_y_connector="PAVEMENT",
            neg_y_connector="PAVEMENT",
            vertex_groups={
                "plot": {
                    "vertices": [0, 1],
                    "weights": [1.0, 0.5]
                }
            },
            metadata={"author": "Test", "version": "1.0"}
        )

        # Convert to dict and back
        data = original.to_dict()
        reconstructed = PrimitiveData.from_dict(data)

        # Validate reconstruction
        assert reconstructed.name == original.name
        assert reconstructed.primitive_type == original.primitive_type
        assert reconstructed.verts == original.verts
        assert reconstructed.faces == original.faces
        assert reconstructed.pos_x_connector == original.pos_x_connector
        assert reconstructed.vertex_groups == original.vertex_groups
        assert reconstructed.metadata == original.metadata

        # Validate that reconstructed primitive is valid
        is_valid, errors = reconstructed.validate()
        assert is_valid, f"Reconstructed primitive invalid: {errors}"

    def test_legacy_format_compatibility(self):
        """Test that old format (without 'connectors' key) still works"""
        data = {
            'name': 'Legacy_Primitive',
            'primitive_type': 'TEST',
            'verts': [[0.0, 0.0, 0.0]],
            'faces': [[0]],
            'mat_indices': [0],
            'material_names': ['Material'],
            'pos_x_connector': 'ROAD',
            'neg_x_connector': 'ROAD',
            'pos_y_connector': 'ROAD',
            'neg_y_connector': 'ROAD'
        }

        primitive = PrimitiveData.from_dict(data)

        assert primitive.pos_x_connector == "ROAD"
        assert primitive.neg_x_connector == "ROAD"


if __name__ == "__main__":
    print("Running PrimitiveData tests...")
    print("\nNote: These tests require pytest. Install with: pip install pytest")
    print("Run with: python -m pytest tests/test_primitive_data.py -v")


