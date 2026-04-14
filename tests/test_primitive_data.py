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


class TestPrimitiveSizingMetadata:
    """Test sizing metadata fields (Task 1A.2)"""

    def test_default_sizing_values(self):
        """Test that sizing fields have correct defaults"""
        primitive = PrimitiveData(
            name="Test",
            primitive_type="ROAD",
            verts=[(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0)],
            faces=[(0, 1, 2)],
            mat_indices=[0],
            material_names=["Material"],
            pos_x_connector="ROAD",
            neg_x_connector="ROAD",
            pos_y_connector="ROAD",
            neg_y_connector="ROAD"
        )

        # Check defaults
        assert primitive.physical_size == 8.0
        assert primitive.grid_category == "outer_grid"
        assert primitive.resolution_multiplier == 1

    def test_custom_sizing_values(self):
        """Test primitives with custom sizing values"""
        building_prim = PrimitiveData(
            name="Building_Room",
            primitive_type="BUILDING",
            verts=[(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0)],
            faces=[(0, 1, 2)],
            mat_indices=[0],
            material_names=["Material"],
            pos_x_connector="WALL",
            neg_x_connector="DOOR",
            pos_y_connector="WALL",
            neg_y_connector="WINDOW",
            physical_size=2.0,
            grid_category="building",
            resolution_multiplier=4
        )

        assert building_prim.physical_size == 2.0
        assert building_prim.grid_category == "building"
        assert building_prim.resolution_multiplier == 4

        # Should be valid
        is_valid, errors = building_prim.validate()
        assert is_valid, f"Building primitive should be valid: {errors}"

    def test_park_primitive_sizing(self):
        """Test park primitive with fine resolution"""
        park_prim = PrimitiveData(
            name="Park_Detail",
            primitive_type="PARK",
            verts=[(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0)],
            faces=[(0, 1, 2)],
            mat_indices=[0],
            material_names=["Material"],
            pos_x_connector="GRASS",
            neg_x_connector="PATH",
            pos_y_connector="GRASS",
            neg_y_connector="GRASS",
            physical_size=1.0,
            grid_category="park",
            resolution_multiplier=8
        )

        assert park_prim.physical_size == 1.0
        assert park_prim.grid_category == "park"
        assert park_prim.resolution_multiplier == 8

        is_valid, errors = park_prim.validate()
        assert is_valid, f"Park primitive should be valid: {errors}"

    def test_negative_physical_size_fails(self):
        """Test that negative physical_size fails validation"""
        primitive = PrimitiveData(
            name="Invalid",
            primitive_type="TEST",
            verts=[(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0)],
            faces=[(0, 1, 2)],
            mat_indices=[0],
            material_names=["Material"],
            pos_x_connector="ROAD",
            neg_x_connector="ROAD",
            pos_y_connector="ROAD",
            neg_y_connector="ROAD",
            physical_size=-1.0  # Invalid!
        )

        is_valid, errors = primitive.validate()
        assert not is_valid
        assert any("physical_size" in err and "positive" in err for err in errors)

    def test_zero_physical_size_fails(self):
        """Test that zero physical_size fails validation"""
        primitive = PrimitiveData(
            name="Invalid",
            primitive_type="TEST",
            verts=[(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0)],
            faces=[(0, 1, 2)],
            mat_indices=[0],
            material_names=["Material"],
            pos_x_connector="ROAD",
            neg_x_connector="ROAD",
            pos_y_connector="ROAD",
            neg_y_connector="ROAD",
            physical_size=0.0  # Invalid!
        )

        is_valid, errors = primitive.validate()
        assert not is_valid
        assert any("physical_size" in err for err in errors)

    def test_invalid_resolution_multiplier_fails(self):
        """Test that resolution_multiplier < 1 fails validation"""
        primitive = PrimitiveData(
            name="Invalid",
            primitive_type="TEST",
            verts=[(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0)],
            faces=[(0, 1, 2)],
            mat_indices=[0],
            material_names=["Material"],
            pos_x_connector="ROAD",
            neg_x_connector="ROAD",
            pos_y_connector="ROAD",
            neg_y_connector="ROAD",
            resolution_multiplier=0  # Invalid!
        )

        is_valid, errors = primitive.validate()
        assert not is_valid
        assert any("resolution_multiplier" in err for err in errors)

    def test_invalid_grid_category_fails(self):
        """Test that unknown grid_category fails validation"""
        primitive = PrimitiveData(
            name="Invalid",
            primitive_type="TEST",
            verts=[(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0)],
            faces=[(0, 1, 2)],
            mat_indices=[0],
            material_names=["Material"],
            pos_x_connector="ROAD",
            neg_x_connector="ROAD",
            pos_y_connector="ROAD",
            neg_y_connector="ROAD",
            grid_category="invalid_category"  # Invalid!
        )

        is_valid, errors = primitive.validate()
        assert not is_valid
        assert any("grid_category" in err for err in errors)

    def test_outer_grid_inconsistent_resolution_fails(self):
        """Test that outer_grid with resolution != 1 fails validation"""
        primitive = PrimitiveData(
            name="Inconsistent",
            primitive_type="ROAD",
            verts=[(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0)],
            faces=[(0, 1, 2)],
            mat_indices=[0],
            material_names=["Material"],
            pos_x_connector="ROAD",
            neg_x_connector="ROAD",
            pos_y_connector="ROAD",
            neg_y_connector="ROAD",
            grid_category="outer_grid",
            resolution_multiplier=4  # Should be 1 for outer_grid!
        )

        is_valid, errors = primitive.validate()
        assert not is_valid
        assert any("outer grid" in err.lower() and "resolution" in err.lower() for err in errors)

    def test_sizing_serialization(self):
        """Test that sizing fields serialize to dict"""
        primitive = PrimitiveData(
            name="Test",
            primitive_type="BUILDING",
            verts=[(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0)],
            faces=[(0, 1, 2)],
            mat_indices=[0],
            material_names=["Material"],
            pos_x_connector="WALL",
            neg_x_connector="DOOR",
            pos_y_connector="WALL",
            neg_y_connector="WALL",
            physical_size=2.0,
            grid_category="building",
            resolution_multiplier=4
        )

        data = primitive.to_dict()

        # Check that sizing fields are in dict
        assert 'physical_size' in data
        assert 'grid_category' in data
        assert 'resolution_multiplier' in data

        # Check values
        assert data['physical_size'] == 2.0
        assert data['grid_category'] == 'building'
        assert data['resolution_multiplier'] == 4

    def test_sizing_deserialization(self):
        """Test that sizing fields deserialize from dict"""
        data = {
            'name': 'Test',
            'primitive_type': 'BUILDING',
            'verts': [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0]],
            'faces': [[0, 1, 2]],
            'mat_indices': [0],
            'material_names': ['Material'],
            'connectors': {
                'pos_x': 'WALL',
                'neg_x': 'DOOR',
                'pos_y': 'WALL',
                'neg_y': 'WALL'
            },
            'physical_size': 2.0,
            'grid_category': 'building',
            'resolution_multiplier': 4
        }

        primitive = PrimitiveData.from_dict(data)

        assert primitive.physical_size == 2.0
        assert primitive.grid_category == 'building'
        assert primitive.resolution_multiplier == 4

    def test_sizing_round_trip(self):
        """Test that sizing fields survive round-trip serialization"""
        original = PrimitiveData(
            name="RoundTrip",
            primitive_type="BUILDING",
            verts=[(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0)],
            faces=[(0, 1, 2)],
            mat_indices=[0],
            material_names=["Material"],
            pos_x_connector="WALL",
            neg_x_connector="DOOR",
            pos_y_connector="WALL",
            neg_y_connector="WALL",
            physical_size=2.0,
            grid_category="building",
            resolution_multiplier=4
        )

        data = original.to_dict()
        reconstructed = PrimitiveData.from_dict(data)

        assert reconstructed.physical_size == original.physical_size
        assert reconstructed.grid_category == original.grid_category
        assert reconstructed.resolution_multiplier == original.resolution_multiplier

    def test_backward_compatibility_defaults(self):
        """Test that old JSON without sizing fields loads with defaults"""
        # Simulate old JSON format (no sizing fields)
        old_data = {
            'name': 'Legacy',
            'primitive_type': 'ROAD',
            'verts': [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0]],
            'faces': [[0, 1, 2]],
            'mat_indices': [0],
            'material_names': ['Material'],
            'connectors': {
                'pos_x': 'ROAD',
                'neg_x': 'ROAD',
                'pos_y': 'ROAD',
                'neg_y': 'ROAD'
            }
            # NOTE: No physical_size, grid_category, or resolution_multiplier
        }

        primitive = PrimitiveData.from_dict(old_data)

        # Should load with defaults
        assert primitive.physical_size == 8.0
        assert primitive.grid_category == 'outer_grid'
        assert primitive.resolution_multiplier == 1

        # Should be valid
        is_valid, errors = primitive.validate()
        assert is_valid, f"Legacy primitive should be valid: {errors}"


class TestRotationInvariant:
    """Test rotation_invariant field (Task 3A.1 Step 1)"""

    def _make_primitive(self, **kwargs):
        """Helper to create a minimal valid primitive"""
        defaults = dict(
            name="Test",
            primitive_type="ROAD",
            verts=[(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0)],
            faces=[(0, 1, 2)],
            mat_indices=[0],
            material_names=["Material"],
            pos_x_connector="ROAD",
            neg_x_connector="ROAD",
            pos_y_connector="ROAD",
            neg_y_connector="ROAD",
        )
        defaults.update(kwargs)
        return PrimitiveData(**defaults)

    def test_default_is_false(self):
        """rotation_invariant defaults to False"""
        prim = self._make_primitive()
        assert prim.rotation_invariant == False

    def test_can_set_true(self):
        """rotation_invariant can be explicitly set to True"""
        prim = self._make_primitive(rotation_invariant=True)
        assert prim.rotation_invariant == True

    def test_false_is_valid(self):
        """rotation_invariant=False passes validation"""
        prim = self._make_primitive(rotation_invariant=False)
        is_valid, errors = prim.validate()
        assert is_valid, f"Expected valid: {errors}"

    def test_true_is_valid(self):
        """rotation_invariant=True passes validation"""
        prim = self._make_primitive(rotation_invariant=True)
        is_valid, errors = prim.validate()
        assert is_valid, f"Expected valid: {errors}"

    def test_non_bool_fails_validation(self):
        """rotation_invariant with a non-bool type fails validation"""
        prim = self._make_primitive(rotation_invariant="yes")  # type: ignore
        is_valid, errors = prim.validate()
        assert not is_valid
        assert any("rotation_invariant" in err for err in errors)

    def test_serialized_to_dict(self):
        """rotation_invariant is included in to_dict() output"""
        prim = self._make_primitive(rotation_invariant=True)
        data = prim.to_dict()
        assert 'rotation_invariant' in data
        assert data['rotation_invariant'] == True

    def test_deserialized_from_dict(self):
        """rotation_invariant is restored from from_dict()"""
        data = {
            'name': 'Test',
            'primitive_type': 'ROAD',
            'verts': [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0]],
            'faces': [[0, 1, 2]],
            'mat_indices': [0],
            'material_names': ['Material'],
            'connectors': {
                'pos_x': 'ROAD', 'neg_x': 'ROAD',
                'pos_y': 'ROAD', 'neg_y': 'ROAD'
            },
            'rotation_invariant': True,
        }
        prim = PrimitiveData.from_dict(data)
        assert prim.rotation_invariant == True

    def test_round_trip(self):
        """rotation_invariant survives to_dict() → from_dict() round-trip"""
        original = self._make_primitive(rotation_invariant=True)
        restored = PrimitiveData.from_dict(original.to_dict())
        assert restored.rotation_invariant == original.rotation_invariant

    def test_backward_compatibility_defaults_false(self):
        """Old JSON without rotation_invariant loads with default False"""
        old_data = {
            'name': 'Legacy',
            'primitive_type': 'ROAD',
            'verts': [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0]],
            'faces': [[0, 1, 2]],
            'mat_indices': [0],
            'material_names': ['Material'],
            'connectors': {
                'pos_x': 'ROAD', 'neg_x': 'ROAD',
                'pos_y': 'ROAD', 'neg_y': 'ROAD'
            }
            # NOTE: No rotation_invariant field
        }
        prim = PrimitiveData.from_dict(old_data)
        assert prim.rotation_invariant == False
        is_valid, errors = prim.validate()
        assert is_valid, f"Legacy primitive should be valid: {errors}"


if __name__ == "__main__":
    print("Running PrimitiveData tests...")
    print("\nNote: These tests require pytest. Install with: pip install pytest")
    print("Run with: python -m pytest tests/test_primitive_data.py -v")


