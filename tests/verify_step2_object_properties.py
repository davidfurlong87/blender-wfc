"""
Verify Task 3A.1 Step 2: New Object properties registered in __init__.py
Run with: python tests/verify_step2_object_properties.py
"""

import sys
from pathlib import Path

content = Path('addons/blender-wfc/__init__.py').read_text()
enums = Path('addons/blender-wfc/wfc_enums.py').read_text()

all_passed = True

def check(label, condition):
    global all_passed
    status = "✅" if condition else "❌"
    print(f"  {status} {label}")
    if not condition:
        all_passed = False

print("wfc_enums.py — GRID_CATEGORIES defined:")
check("GRID_CATEGORIES list present",        "GRID_CATEGORIES = [" in enums)
check("'outer_grid' entry present",          "'outer_grid'" in enums)
check("'building' entry present",            "'building'" in enums)
check("'park' entry present",                "'park'" in enums)
check("'road_detail' entry present",         "'road_detail'" in enums)
check("GRID_CATEGORIES has descriptions",    "city layout" in enums)

print()
print("__init__.py — imports:")
check("GRID_CATEGORIES imported",            "GRID_CATEGORIES" in content)

print()
print("__init__.py — register():")
check("physical_size = FloatProperty",       "Object.physical_size = FloatProperty" in content)
check("physical_size min=0.1",               "min=0.1" in content)
check("grid_category = EnumProperty",        "Object.grid_category = EnumProperty" in content)
check("grid_category uses GRID_CATEGORIES",  "items=GRID_CATEGORIES" in content)
check("grid_category default='outer_grid'",  "default='outer_grid'" in content)
check("resolution_multiplier = IntProperty", "Object.resolution_multiplier = IntProperty" in content)
check("resolution_multiplier min=1",         "min=1" in content)
check("rotation_invariant = BoolProperty",   "Object.rotation_invariant = BoolProperty" in content)
check("rotation_invariant default=False",    "default=False" in content)

print()
print("__init__.py — unregister():")
check("del physical_size",                   "del bpy.types.Object.physical_size" in content)
check("del grid_category",                   "del bpy.types.Object.grid_category" in content)
check("del resolution_multiplier",           "del bpy.types.Object.resolution_multiplier" in content)
check("del rotation_invariant",              "del bpy.types.Object.rotation_invariant" in content)

print()
print("wfc_enums.py — functional (no Blender needed):")
sys.path.insert(0, 'addons/blender-wfc')
try:
    import wfc_enums
    cats = wfc_enums.GRID_CATEGORIES
    check("GRID_CATEGORIES is a list",           isinstance(cats, list))
    check("Has 4 categories",                    len(cats) == 4)
    check("Each item is a 3-tuple",              all(len(c) == 3 for c in cats))
    ids = [c[0] for c in cats]
    check("Contains 'outer_grid'",               'outer_grid' in ids)
    check("Contains 'building'",                 'building' in ids)
    check("Contains 'park'",                     'park' in ids)
    check("Contains 'road_detail'",              'road_detail' in ids)
except Exception as e:
    print(f"  ❌ Import error: {e}")
    all_passed = False

print()
if all_passed:
    print("=" * 60)
    print("✅ ALL CHECKS PASSED - Step 2 complete!")
    print("=" * 60)
    print("\nIn Blender, after reload:")
    print("  obj.physical_size        → FloatProperty")
    print("  obj.grid_category        → EnumProperty (4 options)")
    print("  obj.resolution_multiplier → IntProperty")
    print("  obj.rotation_invariant   → BoolProperty")
else:
    print("=" * 60)
    print("❌ SOME CHECKS FAILED")
    print("=" * 60)
    sys.exit(1)
