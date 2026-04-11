"""
Manual test for Task 1A.1: Primitive Sizing Metadata

Tests the new physical_size, grid_category, and resolution_multiplier fields.

Run this with: python tests/test_primitive_sizing_manual.py
"""

import sys
from pathlib import Path

# Add addon path to sys.path
addon_path = Path('addons/blender-wfc')
sys.path.insert(0, str(addon_path))

from primitive_data_core import PrimitiveData

def test_basic_sizing_fields():
    """Test that sizing fields are present and have defaults"""
    print("Test 1: Basic sizing fields with defaults")
    
    prim = PrimitiveData(
        name="test_outer_grid",
        primitive_type="ROAD",
        verts=[(0,0,0), (1,0,0), (1,1,0), (0,1,0)],
        faces=[(0,1,2,3)],
        mat_indices=[0],
        material_names=["Material"],
        pos_x_connector="ROAD",
        neg_x_connector="ROAD",
        pos_y_connector="ROAD",
        neg_y_connector="ROAD"
    )
    
    assert prim.physical_size == 8.0, f"Expected physical_size=8.0, got {prim.physical_size}"
    assert prim.grid_category == "outer_grid", f"Expected grid_category='outer_grid', got '{prim.grid_category}'"
    assert prim.resolution_multiplier == 1, f"Expected resolution_multiplier=1, got {prim.resolution_multiplier}"
    
    print("  ✅ Default values correct")
    print(f"     physical_size: {prim.physical_size}")
    print(f"     grid_category: {prim.grid_category}")
    print(f"     resolution_multiplier: {prim.resolution_multiplier}")


def test_building_primitive():
    """Test building primitive with custom sizing"""
    print("\nTest 2: Building primitive with custom sizing")
    
    prim = PrimitiveData(
        name="test_building",
        primitive_type="BUILDING",
        verts=[(0,0,0), (1,0,0), (1,1,0), (0,1,0)],
        faces=[(0,1,2,3)],
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
    
    assert prim.physical_size == 2.0
    assert prim.grid_category == "building"
    assert prim.resolution_multiplier == 4
    
    print("  ✅ Custom sizing values correct")
    print(f"     physical_size: {prim.physical_size}")
    print(f"     grid_category: {prim.grid_category}")
    print(f"     resolution_multiplier: {prim.resolution_multiplier}")


def test_validation():
    """Test validation of sizing fields"""
    print("\nTest 3: Validation of sizing fields")
    
    # Test valid primitive
    valid_prim = PrimitiveData(
        name="valid",
        primitive_type="BUILDING",
        verts=[(0,0,0), (1,0,0), (1,1,0), (0,1,0)],
        faces=[(0,1,2,3)],
        mat_indices=[0],
        material_names=["Material"],
        pos_x_connector="ROAD",
        neg_x_connector="ROAD",
        pos_y_connector="ROAD",
        neg_y_connector="ROAD",
        physical_size=2.0,
        grid_category="building",
        resolution_multiplier=4
    )
    
    is_valid, errors = valid_prim.validate()
    assert is_valid, f"Expected valid, got errors: {errors}"
    print("  ✅ Valid building primitive passes validation")
    
    # Test invalid physical_size
    invalid_size = PrimitiveData(
        name="invalid_size",
        primitive_type="BUILDING",
        verts=[(0,0,0), (1,0,0), (1,1,0), (0,1,0)],
        faces=[(0,1,2,3)],
        mat_indices=[0],
        material_names=["Material"],
        pos_x_connector="ROAD",
        neg_x_connector="ROAD",
        pos_y_connector="ROAD",
        neg_y_connector="ROAD",
        physical_size=-1.0  # Invalid!
    )
    
    is_valid, errors = invalid_size.validate()
    assert not is_valid, "Expected invalid for negative physical_size"
    assert any("physical_size" in err for err in errors), "Expected physical_size error"
    print(f"  ✅ Negative physical_size caught: {errors}")
    
    # Test invalid grid_category
    invalid_category = PrimitiveData(
        name="invalid_category",
        primitive_type="BUILDING",
        verts=[(0,0,0), (1,0,0), (1,1,0), (0,1,0)],
        faces=[(0,1,2,3)],
        mat_indices=[0],
        material_names=["Material"],
        pos_x_connector="ROAD",
        neg_x_connector="ROAD",
        pos_y_connector="ROAD",
        neg_y_connector="ROAD",
        grid_category="invalid_category"  # Invalid!
    )
    
    is_valid, errors = invalid_category.validate()
    assert not is_valid, "Expected invalid for unknown grid_category"
    assert any("grid_category" in err for err in errors), "Expected grid_category error"
    print(f"  ✅ Invalid grid_category caught: {errors}")
    
    # Test outer grid with wrong resolution
    inconsistent = PrimitiveData(
        name="inconsistent",
        primitive_type="ROAD",
        verts=[(0,0,0), (1,0,0), (1,1,0), (0,1,0)],
        faces=[(0,1,2,3)],
        mat_indices=[0],
        material_names=["Material"],
        pos_x_connector="ROAD",
        neg_x_connector="ROAD",
        pos_y_connector="ROAD",
        neg_y_connector="ROAD",
        grid_category="outer_grid",
        resolution_multiplier=4  # Should be 1 for outer_grid!
    )
    
    is_valid, errors = inconsistent.validate()
    assert not is_valid, "Expected invalid for outer_grid with resolution != 1"
    assert any("resolution" in err.lower() for err in errors), "Expected resolution consistency error"
    print(f"  ✅ Inconsistent outer_grid resolution caught: {errors}")


def test_json_serialization():
    """Test JSON serialization with sizing fields"""
    print("\nTest 4: JSON serialization")
    
    original = PrimitiveData(
        name="test_serialize",
        primitive_type="BUILDING",
        verts=[(0,0,0), (1,0,0), (1,1,0), (0,1,0)],
        faces=[(0,1,2,3)],
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
    
    # Serialize
    data = original.to_dict()
    
    assert 'physical_size' in data, "physical_size missing from dict"
    assert 'grid_category' in data, "grid_category missing from dict"
    assert 'resolution_multiplier' in data, "resolution_multiplier missing from dict"
    
    assert data['physical_size'] == 2.0
    assert data['grid_category'] == 'building'
    assert data['resolution_multiplier'] == 4
    
    print("  ✅ Serialization includes sizing fields")
    print(f"     physical_size: {data['physical_size']}")
    print(f"     grid_category: {data['grid_category']}")
    print(f"     resolution_multiplier: {data['resolution_multiplier']}")
    
    # Deserialize
    restored = PrimitiveData.from_dict(data)
    
    assert restored.physical_size == 2.0
    assert restored.grid_category == 'building'
    assert restored.resolution_multiplier == 4
    
    print("  ✅ Deserialization restores sizing fields correctly")


def test_backward_compatibility():
    """Test that old JSON without sizing fields loads with defaults"""
    print("\nTest 5: Backward compatibility")
    
    # Simulate old JSON format without sizing fields
    old_data = {
        'name': 'old_primitive',
        'primitive_type': 'ROAD',
        'verts': [[0,0,0], [1,0,0], [1,1,0], [0,1,0]],
        'faces': [[0,1,2,3]],
        'mat_indices': [0],
        'material_names': ['Material'],
        'connectors': {
            'pos_x': 'ROAD',
            'neg_x': 'ROAD',
            'pos_y': 'ROAD',
            'neg_y': 'ROAD',
        },
        'vertex_groups': {},
        'metadata': {}
        # NOTE: No physical_size, grid_category, or resolution_multiplier!
    }
    
    # Should load with defaults
    prim = PrimitiveData.from_dict(old_data)
    
    assert prim.physical_size == 8.0, f"Expected default physical_size=8.0, got {prim.physical_size}"
    assert prim.grid_category == 'outer_grid', f"Expected default grid_category='outer_grid', got '{prim.grid_category}'"
    assert prim.resolution_multiplier == 1, f"Expected default resolution_multiplier=1, got {prim.resolution_multiplier}"
    
    print("  ✅ Old JSON loads with default sizing values")
    print(f"     physical_size: {prim.physical_size} (default)")
    print(f"     grid_category: {prim.grid_category} (default)")
    print(f"     resolution_multiplier: {prim.resolution_multiplier} (default)")


if __name__ == '__main__':
    print("="*60)
    print("Task 1A.1: Primitive Sizing Metadata - Manual Tests")
    print("="*60)
    
    try:
        test_basic_sizing_fields()
        test_building_primitive()
        test_validation()
        test_json_serialization()
        test_backward_compatibility()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\nTask 1A.1 is complete! ✨")
        print("Next: Task 1A.2 - Update formal tests")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
