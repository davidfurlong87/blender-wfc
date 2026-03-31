"""
Blender test script for PrimitiveAdapter

This script must be run from within Blender's Python console or text editor.
It tests the round-trip conversion: Blender Object -> PrimitiveData -> Blender Object

How to run:
1. Open Blender
2. Enable the WFC addon
3. Open the Text Editor
4. Load this script
5. Click "Run Script"

Expected output:
- Test cube is created
- Primitive is extracted
- New object is created from primitive data
- Validation passes
"""

import bpy
import sys
from pathlib import Path

# Add the addon path (adjust if needed)
addon_path = Path(bpy.utils.user_resource('SCRIPTS')) / "addons" / "blender-wfc"
if str(addon_path) not in sys.path:
    sys.path.insert(0, str(addon_path))

from primitive_adapter import PrimitiveAdapter
from primitive_data_core import PrimitiveData


def create_test_cube():
    """Create a simple test cube with materials and connectors"""
    # Delete existing test objects
    for obj in bpy.data.objects:
        if obj.name.startswith("TestCube"):
            bpy.data.objects.remove(obj, do_unlink=True)
    
    # Create cube
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
    test_obj = bpy.context.active_object
    test_obj.name = "TestCube_Original"
    
    # Create test material
    if "TestMaterial" not in bpy.data.materials:
        mat = bpy.data.materials.new(name="TestMaterial")
        mat.diffuse_color = (0.8, 0.2, 0.2, 1.0)
    
    # Assign material
    test_obj.data.materials.append(bpy.data.materials["TestMaterial"])
    
    # Set primitive properties
    test_obj.primitive_type = 'BUILDING'
    test_obj.x_pos_connector = 'ROAD'
    test_obj.x_neg_connector = 'ROAD'
    test_obj.y_pos_connector = 'BUILDING'
    test_obj.y_neg_connector = 'BUILDING'
    
    # Add a vertex group
    vgroup = test_obj.vertex_groups.new(name='test_group')
    vgroup.add([0, 1, 2, 3], 1.0, 'REPLACE')
    
    return test_obj


def test_extraction():
    """Test extracting primitive data from Blender object"""
    print("\n" + "="*60)
    print("TEST 1: Extract Primitive from Blender Object")
    print("="*60)
    
    # Create test object
    test_obj = create_test_cube()
    print(f"✓ Created test object: {test_obj.name}")
    
    # Extract primitive data
    adapter = PrimitiveAdapter()
    primitive_data, errors = adapter.extract_primitive_from_blender(test_obj)
    
    if errors:
        print(f"⚠ Warnings during extraction:")
        for err in errors:
            print(f"  - {err}")
    
    if primitive_data is None:
        print("✗ FAILED: Could not extract primitive data")
        return None
    
    print(f"✓ Extracted primitive data successfully")
    print(f"  Name: {primitive_data.name}")
    print(f"  Type: {primitive_data.primitive_type}")
    print(f"  Vertices: {len(primitive_data.verts)}")
    print(f"  Faces: {len(primitive_data.faces)}")
    print(f"  Materials: {primitive_data.material_names}")
    print(f"  Connectors: +X={primitive_data.pos_x_connector}, -X={primitive_data.neg_x_connector}")
    print(f"  Vertex Groups: {list(primitive_data.vertex_groups.keys())}")
    
    # Validate
    is_valid, validation_errors = primitive_data.validate()
    if is_valid:
        print(f"✓ Validation passed")
    else:
        print(f"✗ Validation failed:")
        for err in validation_errors:
            print(f"  - {err}")
        return None
    
    return primitive_data


def test_creation(primitive_data):
    """Test creating Blender object from primitive data"""
    print("\n" + "="*60)
    print("TEST 2: Create Blender Object from PrimitiveData")
    print("="*60)
    
    # Modify name to avoid conflict
    primitive_data.name = "TestCube_Recreated"
    
    # Create object
    adapter = PrimitiveAdapter()
    collection = bpy.context.scene.collection
    new_obj, errors = adapter.create_blender_object_from_primitive(
        primitive_data, 
        collection=collection,
        location=(5, 0, 0)  # Offset so we can see both
    )
    
    if errors:
        print(f"⚠ Warnings during creation:")
        for err in errors:
            print(f"  - {err}")
    
    if new_obj is None:
        print("✗ FAILED: Could not create object")
        return None
    
    print(f"✓ Created object successfully: {new_obj.name}")
    print(f"  Location: {new_obj.location}")
    print(f"  Vertices: {len(new_obj.data.vertices)}")
    print(f"  Faces: {len(new_obj.data.polygons)}")
    print(f"  Materials: {[m.name for m in new_obj.data.materials]}")
    print(f"  Primitive Type: {new_obj.primitive_type}")
    print(f"  Connectors: +X={new_obj.x_pos_connector}, -X={new_obj.x_neg_connector}")
    print(f"  Vertex Groups: {[vg.name for vg in new_obj.vertex_groups]}")
    
    return new_obj


def test_round_trip():
    """Test complete round trip"""
    print("\n" + "="*60)
    print("TEST 3: Round Trip (Extract -> Serialize -> Create)")
    print("="*60)
    
    # Step 1: Extract
    primitive_data = test_extraction()
    if not primitive_data:
        print("✗ Round trip failed at extraction step")
        return
    
    # Step 2: Serialize to dict and back
    data_dict = primitive_data.to_dict()
    print(f"✓ Serialized to dictionary ({len(data_dict)} keys)")
    
    primitive_data_restored = PrimitiveData.from_dict(data_dict)
    print(f"✓ Deserialized from dictionary")
    
    # Step 3: Create object
    new_obj = test_creation(primitive_data_restored)
    if not new_obj:
        print("✗ Round trip failed at creation step")
        return
    
    print("\n" + "="*60)
    print("🎉 ALL TESTS PASSED!")
    print("="*60)
    print("✓ Blender Object -> PrimitiveData: SUCCESS")
    print("✓ PrimitiveData -> Dict -> PrimitiveData: SUCCESS")
    print("✓ PrimitiveData -> Blender Object: SUCCESS")
    print("\nCheck the 3D viewport:")
    print("  - 'TestCube_Original' at (0, 0, 0)")
    print("  - 'TestCube_Recreated' at (5, 0, 0)")


if __name__ == "__main__":
    test_round_trip()

