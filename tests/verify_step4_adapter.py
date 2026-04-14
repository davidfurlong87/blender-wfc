"""
Verify Task 3A.1 Step 4: PrimitiveAdapter handles rotation_invariant
Run with: python tests/verify_step4_adapter.py
"""

import sys
from pathlib import Path

content = Path('addons/blender-wfc/primitive_adapter.py').read_text()

all_passed = True

def check(label, condition):
    global all_passed
    status = "✅" if condition else "❌"
    print(f"  {status} {label}")
    if not condition:
        all_passed = False

# ── extract_primitive_from_blender ────────────────────────────────────────────
print("extract_primitive_from_blender():")
check("reads physical_size via registered property",
      "physical_size = obj.physical_size" in content)
check("reads grid_category via registered property",
      "grid_category = obj.grid_category" in content)
check("reads resolution_multiplier via registered property",
      "resolution_multiplier = obj.resolution_multiplier" in content)
check("reads rotation_invariant via registered property",
      "rotation_invariant = obj.rotation_invariant" in content)
check("no longer uses obj.get('physical_size'",
      "obj.get('physical_size'" not in content)
check("no longer uses obj.get('grid_category'",
      "obj.get('grid_category'" not in content)
check("no longer uses obj.get('resolution_multiplier'",
      "obj.get('resolution_multiplier'" not in content)
check("rotation_invariant passed to PrimitiveData",
      "rotation_invariant=rotation_invariant" in content)

# ── create_blender_object_from_primitive ──────────────────────────────────────
print("\ncreate_blender_object_from_primitive():")
check("sets physical_size via registered property",
      "mesh_obj.physical_size = primitive_data.physical_size" in content)
check("sets grid_category via registered property",
      "mesh_obj.grid_category = primitive_data.grid_category" in content)
check("sets resolution_multiplier via registered property",
      "mesh_obj.resolution_multiplier = primitive_data.resolution_multiplier" in content)
check("sets rotation_invariant via registered property",
      "mesh_obj.rotation_invariant = primitive_data.rotation_invariant" in content)
check("no longer uses dict-style mesh_obj['physical_size']",
      "mesh_obj['physical_size']" not in content)
check("no longer uses dict-style mesh_obj['grid_category']",
      "mesh_obj['grid_category']" not in content)
check("no longer uses dict-style mesh_obj['resolution_multiplier']",
      "mesh_obj['resolution_multiplier']" not in content)

print()
if all_passed:
    print("=" * 60)
    print("✅ ALL CHECKS PASSED - Step 4 complete!")
    print("=" * 60)
    print("\nTask 3A.1 is fully complete. All 4 steps done:")
    print("  ✅ Step 1: rotation_invariant in PrimitiveData")
    print("  ✅ Step 2: 4 new Object properties registered")
    print("  ✅ Step 3: Operator dialog updated")
    print("  ✅ Step 4: PrimitiveAdapter reads/writes all 4 fields")
else:
    print("=" * 60)
    print("❌ SOME CHECKS FAILED")
    print("=" * 60)
    sys.exit(1)
