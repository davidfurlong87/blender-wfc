"""
Test PrimitiveAdapter with sizing metadata (Task 1A.3)

This tests that the adapter correctly extracts and applies sizing metadata
when converting between Blender objects and PrimitiveData.

Run in Blender: Run this script in Blender's scripting workspace
"""

import bpy
import sys
from pathlib import Path

# Add addon path
addon_path = Path(bpy.data.filepath).parent / 'addons' / 'blender-wfc'
if str(addon_path) not in sys.path:
    sys.path.insert(0, str(addon_path))

from primitive_adapter import PrimitiveAdapter
from primitive_data_core import PrimitiveData

print("="*70)
print("Task 1A.3: Testing PrimitiveAdapter with Sizing Metadata")
print("="*70)

# Clean up any existing test objects
for obj in bpy.data.objects:
    if obj.name.startswith('test_'):
        bpy.data.objects.remove(obj, do_unlink=True)

adapter = PrimitiveAdapter()

# ============================================================================
# Test 1: Extract sizing metadata from Blender object
# ============================================================================
print("\n--- Test 1: Extract sizing metadata from Blender object ---")

# Create a test cube
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
test_obj = bpy.context.active_object
test_obj.name = "test_building"

# Set primitive properties
test_obj.primitive_type = "BUILDING"
test_obj.x_pos_connector = "WALL"
test_obj.x_neg_connector = "DOOR"
test_obj.y_pos_connector = "WALL"
test_obj.y_neg_connector = "WINDOW"

# Set sizing metadata as custom properties
test_obj['physical_size'] = 2.0
test_obj['grid_category'] = 'building'
test_obj['resolution_multiplier'] = 4

print(f"Created test object: {test_obj.name}")
print(f"  physical_size: {test_obj['physical_size']}")
print(f"  grid_category: {test_obj['grid_category']}")
print(f"  resolution_multiplier: {test_obj['resolution_multiplier']}")

# Extract primitive data
primitive_data, errors = adapter.extract_primitive_from_blender(test_obj)

if errors:
    print(f"⚠️  Extraction warnings: {errors}")

if primitive_data:
    print(f"✅ Extracted PrimitiveData:")
    print(f"  physical_size: {primitive_data.physical_size}")
    print(f"  grid_category: {primitive_data.grid_category}")
    print(f"  resolution_multiplier: {primitive_data.resolution_multiplier}")
    
    assert primitive_data.physical_size == 2.0, "physical_size not extracted"
    assert primitive_data.grid_category == 'building', "grid_category not extracted"
    assert primitive_data.resolution_multiplier == 4, "resolution_multiplier not extracted"
    print("✅ Test 1 PASSED: Sizing metadata extracted correctly")
else:
    print("❌ Test 1 FAILED: Could not extract primitive data")
    sys.exit(1)

# ============================================================================
# Test 2: Create Blender object with sizing metadata
# ============================================================================
print("\n--- Test 2: Create Blender object with sizing metadata ---")

# Create new primitive data with sizing
new_primitive = PrimitiveData(
    name="test_park",
    primitive_type="PARK",
    verts=[(-0.5, -0.5, 0), (0.5, -0.5, 0), (0.5, 0.5, 0), (-0.5, 0.5, 0)],
    faces=[(0, 1, 2, 3)],
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

print(f"Created PrimitiveData: {new_primitive.name}")
print(f"  physical_size: {new_primitive.physical_size}")
print(f"  grid_category: {new_primitive.grid_category}")
print(f"  resolution_multiplier: {new_primitive.resolution_multiplier}")

# Create Blender object from primitive
created_obj, errors = adapter.create_blender_object_from_primitive(
    new_primitive,
    location=(5, 0, 0)
)

if errors:
    print(f"⚠️  Creation warnings: {errors}")

if created_obj:
    print(f"✅ Created Blender object: {created_obj.name}")
    print(f"  physical_size: {created_obj.get('physical_size')}")
    print(f"  grid_category: {created_obj.get('grid_category')}")
    print(f"  resolution_multiplier: {created_obj.get('resolution_multiplier')}")
    
    assert created_obj.get('physical_size') == 1.0, "physical_size not set on object"
    assert created_obj.get('grid_category') == 'park', "grid_category not set on object"
    assert created_obj.get('resolution_multiplier') == 8, "resolution_multiplier not set on object"
    print("✅ Test 2 PASSED: Sizing metadata applied to Blender object")
else:
    print("❌ Test 2 FAILED: Could not create Blender object")
    sys.exit(1)

# ============================================================================
# Test 3: Round-trip preserves sizing metadata
# ============================================================================
print("\n--- Test 3: Round-trip preserves sizing metadata ---")

# Extract from the object we just created
round_trip_data, errors = adapter.extract_primitive_from_blender(created_obj)

if round_trip_data:
    print(f"✅ Round-trip extraction successful")
    print(f"  Original physical_size: {new_primitive.physical_size}")
    print(f"  Round-trip physical_size: {round_trip_data.physical_size}")
    
    assert round_trip_data.physical_size == new_primitive.physical_size
    assert round_trip_data.grid_category == new_primitive.grid_category
    assert round_trip_data.resolution_multiplier == new_primitive.resolution_multiplier
    print("✅ Test 3 PASSED: Round-trip preserves sizing metadata")
else:
    print("❌ Test 3 FAILED: Round-trip extraction failed")
    sys.exit(1)

# ============================================================================
# Test 4: Default values for objects without sizing metadata
# ============================================================================
print("\n--- Test 4: Default values for objects without sizing metadata ---")

# Create object without sizing metadata
bpy.ops.mesh.primitive_plane_add(location=(-5, 0, 0))
default_obj = bpy.context.active_object
default_obj.name = "test_default"
default_obj.primitive_type = "ROAD"
default_obj.x_pos_connector = "ROAD"
default_obj.x_neg_connector = "ROAD"
default_obj.y_pos_connector = "ROAD"
default_obj.y_neg_connector = "ROAD"
# NOTE: No sizing metadata set!

print(f"Created object without sizing metadata: {default_obj.name}")

# Extract - should get defaults
default_data, errors = adapter.extract_primitive_from_blender(default_obj)

if default_data:
    print(f"✅ Extraction with defaults:")
    print(f"  physical_size: {default_data.physical_size} (expected: 8.0)")
    print(f"  grid_category: {default_data.grid_category} (expected: outer_grid)")
    print(f"  resolution_multiplier: {default_data.resolution_multiplier} (expected: 1)")
    
    assert default_data.physical_size == 8.0, "Default physical_size incorrect"
    assert default_data.grid_category == 'outer_grid', "Default grid_category incorrect"
    assert default_data.resolution_multiplier == 1, "Default resolution_multiplier incorrect"
    print("✅ Test 4 PASSED: Defaults applied correctly")
else:
    print("❌ Test 4 FAILED: Extraction failed")
    sys.exit(1)

# ============================================================================
# Summary
# ============================================================================
print("\n" + "="*70)
print("✅ ALL TESTS PASSED!")
print("="*70)
print("\nTask 1A.3 Complete:")
print("  ✅ Adapter extracts sizing metadata from Blender objects")
print("  ✅ Adapter applies sizing metadata to created objects")
print("  ✅ Round-trip preserves all sizing metadata")
print("  ✅ Default values work for objects without metadata")
print("\nNext: Task 1B.1 - Create ConnectorRegistry")
print("="*70)
