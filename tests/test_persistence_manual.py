"""
Manual tests for primitive persistence (JSON save/load)

Run with: python tests/test_persistence_manual.py
"""

import json
import os
import tempfile
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'addons' / 'blender-wfc'))

from primitive_data_core import PrimitiveData
from primitive_persistence import PrimitivePersistence


def create_sample_primitive():
    """Create a sample valid primitive for testing"""
    return PrimitiveData(
        name="TestPrimitive",
        primitive_type="BUILDING",
        verts=[[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0], [0.0, 1.0, 0.0]],
        faces=[[0, 1, 2, 3]],
        material_names=["TestMaterial"],
        mat_indices=[0],
        pos_x_connector="ROAD",
        neg_x_connector="ROAD",
        pos_y_connector="BUILDING",
        neg_y_connector="BUILDING",
        vertex_groups={},
        metadata={"created_by": "test"}
    )


def test_save_and_load_single():
    """Test saving and loading a single primitive"""
    print("\n" + "="*60)
    print("TEST 1: Save and Load Single Primitive")
    print("="*60)
    
    persistence = PrimitivePersistence()
    primitive = create_sample_primitive()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "test_primitive.json")
        
        # Save
        print(f"Saving primitive '{primitive.name}' to {filepath}...")
        success, errors = persistence.save_primitive_to_file(primitive, filepath)
        
        if success:
            print("✓ Save successful")
        else:
            print(f"✗ Save failed: {errors}")
            return False
        
        # Verify file exists
        if os.path.exists(filepath):
            print("✓ File created")
        else:
            print("✗ File not created")
            return False
        
        # Load
        print(f"Loading primitive from {filepath}...")
        loaded, errors = persistence.load_primitive_from_file(filepath)
        
        if loaded:
            print("✓ Load successful")
            print(f"  Name: {loaded.name}")
            print(f"  Type: {loaded.primitive_type}")
            print(f"  Vertices: {len(loaded.verts)}")
            print(f"  Faces: {len(loaded.faces)}")
        else:
            print(f"✗ Load failed: {errors}")
            return False
        
        # Validate data matches
        if loaded.name == primitive.name and len(loaded.verts) == len(primitive.verts):
            print("✓ Data matches original")
        else:
            print("✗ Data doesn't match")
            return False
    
    return True


def test_save_and_load_library():
    """Test saving and loading a primitive library"""
    print("\n" + "="*60)
    print("TEST 2: Save and Load Primitive Library")
    print("="*60)
    
    persistence = PrimitivePersistence()
    
    # Create multiple primitives
    primitive1 = create_sample_primitive()
    primitive2 = PrimitiveData(
        name="RoadPrimitive",
        primitive_type="ROAD",
        verts=[[0.0, 0.0, 0.0], [2.0, 0.0, 0.0], [2.0, 2.0, 0.0], [0.0, 2.0, 0.0]],
        faces=[[0, 1, 2, 3]],
        material_names=["RoadMaterial"],
        mat_indices=[0],
        pos_x_connector="ROAD",
        neg_x_connector="ROAD",
        pos_y_connector="ROAD",
        neg_y_connector="ROAD",
        vertex_groups={}
    )
    
    primitives = [primitive1, primitive2]
    
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "library.json")
        
        # Save library
        print(f"Saving library with {len(primitives)} primitives...")
        success, errors = persistence.save_primitive_library(
            primitives,
            filepath,
            library_name="Test Library",
            description="Test library with 2 primitives"
        )
        
        if success:
            print("✓ Library save successful")
        else:
            print(f"✗ Library save failed: {errors}")
            return False
        
        # Load library
        print("Loading library...")
        loaded_primitives, metadata, errors = persistence.load_primitive_library(filepath)
        
        if len(loaded_primitives) == 2:
            print(f"✓ Loaded {len(loaded_primitives)} primitives")
            print(f"  Library name: {metadata.get('library_name')}")
            print(f"  Description: {metadata.get('description')}")
            for i, prim in enumerate(loaded_primitives):
                print(f"  {i+1}. {prim.name} ({prim.primitive_type})")
        else:
            print(f"✗ Expected 2 primitives, got {len(loaded_primitives)}")
            if errors:
                print(f"  Errors: {errors}")
            return False
        
        # Test listing primitives
        print("\nListing primitives...")
        primitive_info, errors = persistence.list_primitives_in_library(filepath)
        
        if len(primitive_info) == 2:
            print(f"✓ Listed {len(primitive_info)} primitives")
            for info in primitive_info:
                print(f"  - {info['name']} ({info['primitive_type']}): {info['vertex_count']} verts, {info['face_count']} faces")
        else:
            print(f"✗ Expected 2 primitives, got {len(primitive_info)}")
            return False
    
    return True


def test_invalid_primitive():
    """Test that invalid primitives are rejected"""
    print("\n" + "="*60)
    print("TEST 3: Reject Invalid Primitive")
    print("="*60)
    
    persistence = PrimitivePersistence()
    
    # Create invalid primitive (vertex index out of range)
    invalid_primitive = PrimitiveData(
        name="InvalidPrimitive",
        primitive_type="BUILDING",
        verts=[[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]],
        faces=[[0, 1, 5]],  # Index 5 doesn't exist!
        material_names=["Test"],
        mat_indices=[0],
        pos_x_connector="ROAD",
        neg_x_connector="ROAD",
        pos_y_connector="ROAD",
        neg_y_connector="ROAD"
    )
    
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "invalid.json")
        
        print("Attempting to save invalid primitive...")
        success, errors = persistence.save_primitive_to_file(invalid_primitive, filepath)
        
        if not success:
            print("✓ Invalid primitive correctly rejected")
            print(f"  Error: {errors[0]}")
        else:
            print("✗ Should have rejected invalid primitive")
            return False
    
    return True


def main():
    print("\n" + "="*60)
    print("PRIMITIVE PERSISTENCE TESTS")
    print("="*60)
    
    tests = [
        test_save_and_load_single,
        test_save_and_load_library,
        test_invalid_primitive
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
    
    print("\n" + "="*60)
    if failed == 0:
        print("🎉 ALL TESTS PASSED!")
    else:
        print(f"❌ {failed} test(s) failed, {passed} passed")
    print("="*60)


if __name__ == "__main__":
    main()

