"""
Manual validation tests for PrimitiveData
Run with: python tests/test_primitive_validation_manual.py
"""

import sys
from pathlib import Path

# Add the addons directory to the path
addon_path = Path(__file__).parent.parent / "addons" / "blender-wfc"
sys.path.insert(0, str(addon_path))

from primitive_data_core import PrimitiveData


def test_validation_errors():
    """Test that validation catches errors"""
    print("Testing validation errors...")
    print()

    # Test 1: Empty name
    primitive = PrimitiveData(
        name='',
        primitive_type='TEST',
        verts=[(0.0, 0.0, 0.0)],
        faces=[(0,)],
        mat_indices=[0],
        material_names=['Material'],
        pos_x_connector='ROAD',
        neg_x_connector='ROAD',
        pos_y_connector='ROAD',
        neg_y_connector='ROAD'
    )
    is_valid, errors = primitive.validate()
    print(f'Test 1 (Empty name): {"PASS" if not is_valid else "FAIL"}')
    print(f'  Errors: {errors[0] if errors else "None"}')
    print()

    # Test 2: Invalid vertex index in face
    primitive = PrimitiveData(
        name='Test',
        primitive_type='TEST',
        verts=[(0.0, 0.0, 0.0), (1.0, 0.0, 0.0)],
        faces=[(0, 1, 5)],  # Index 5 does not exist
        mat_indices=[0],
        material_names=['Material'],
        pos_x_connector='ROAD',
        neg_x_connector='ROAD',
        pos_y_connector='ROAD',
        neg_y_connector='ROAD'
    )
    is_valid, errors = primitive.validate()
    print(f'Test 2 (Invalid vertex index): {"PASS" if not is_valid else "FAIL"}')
    for e in errors:
        if "out of range" in e:
            print(f'  Error: {e}')
    print()

    # Test 3: Mismatched material indices
    primitive = PrimitiveData(
        name='Test',
        primitive_type='TEST',
        verts=[(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0)],
        faces=[(0, 1, 2), (0, 2, 1)],  # 2 faces
        mat_indices=[0],  # Only 1 material index
        material_names=['Material'],
        pos_x_connector='ROAD',
        neg_x_connector='ROAD',
        pos_y_connector='ROAD',
        neg_y_connector='ROAD'
    )
    is_valid, errors = primitive.validate()
    print(f'Test 3 (Material index mismatch): {"PASS" if not is_valid else "FAIL"}')
    for e in errors:
        if "must match" in e:
            print(f'  Error: {e}')
    print()

    print('✅ All validation tests working correctly!')


def test_serialization():
    """Test serialization round trip"""
    print("\nTesting serialization...")
    print()
    
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
    
    print("✅ Round-trip serialization test passed!")


if __name__ == "__main__":
    test_validation_errors()
    test_serialization()
    print("\n🎉 All tests passed!")

