"""
Verify Task 2B.3: Deprecate wfc_values.py globals
Run with: python tests/verify_task_2b3.py
"""

import sys
import types
from pathlib import Path

# Provide a minimal bpy stub so wfc_values.py imports cleanly
bpy_mock = types.ModuleType('bpy')
sys.modules.setdefault('bpy', bpy_mock)

sys.path.insert(0, 'addons/blender-wfc')

source = Path('addons/blender-wfc/wfc_values.py').read_text()
import wfc_values

all_passed = True

def check(label, condition):
    global all_passed
    status = "✅" if condition else "❌"
    print(f"  {status} {label}")
    if not condition:
        all_passed = False


# ── Removed ───────────────────────────────────────────────────────────────────
print("Removed:")
check("'import bpy' removed",              "import bpy" not in source)


# ── GridCategory ──────────────────────────────────────────────────────────────
print("\nGridCategory class:")
check("class defined",                     hasattr(wfc_values, 'GridCategory'))
check("OUTER_GRID  = 'outer_grid'",        wfc_values.GridCategory.OUTER_GRID  == 'outer_grid')
check("BUILDING    = 'building'",          wfc_values.GridCategory.BUILDING    == 'building')
check("PARK        = 'park'",              wfc_values.GridCategory.PARK        == 'park')
check("ROAD_DETAIL = 'road_detail'",       wfc_values.GridCategory.ROAD_DETAIL == 'road_detail')


# ── DEFAULT_GRID_SIZES ────────────────────────────────────────────────────────
print("\nDEFAULT_GRID_SIZES dict:")
check("dict defined",                      hasattr(wfc_values, 'DEFAULT_GRID_SIZES'))
gd = wfc_values.DEFAULT_GRID_SIZES
check("outer_grid  → 8.0",                 gd[wfc_values.GridCategory.OUTER_GRID]  == 8.0)
check("building    → 2.0",                 gd[wfc_values.GridCategory.BUILDING]    == 2.0)
check("park        → 1.0",                 gd[wfc_values.GridCategory.PARK]        == 1.0)
check("road_detail → 4.0",                 gd[wfc_values.GridCategory.ROAD_DETAIL] == 4.0)
check("has exactly 4 entries",             len(gd) == 4)


# ── Deprecated fallbacks ──────────────────────────────────────────────────────
print("\nDeprecated fallbacks (still present for safety):")
check("module_size still accessible",      hasattr(wfc_values, 'module_size'))
check("module_size == 8.0",               wfc_values.module_size == 8.0)
check("primitive_offset_x still accessible", hasattr(wfc_values, 'primitive_offset_x'))
check("primitive_offset_x == 32.0",       wfc_values.primitive_offset_x == 32.0)
check("module_size derived from DEFAULT_GRID_SIZES",
      "DEFAULT_GRID_SIZES[GridCategory.OUTER_GRID]" in source)
check("DEPRECATED comment present",       "DEPRECATED" in source)


# ── Sync check — GridCategory values match VALID_CATEGORIES ──────────────────
print("\nSync check with primitive_data_core.py:")
core_source = Path('addons/blender-wfc/primitive_data_core.py').read_text()
for cat in ['outer_grid', 'building', 'park', 'road_detail']:
    check(f"'{cat}' present in VALID_CATEGORIES",
          f"'{cat}'" in core_source or f'"{cat}"' in core_source)


# ── Sync check — GridCategory values match GRID_CATEGORIES in wfc_enums ──────
print("\nSync check with wfc_enums.py:")
enums_source = Path('addons/blender-wfc/wfc_enums.py').read_text()
for cat in ['outer_grid', 'building', 'park', 'road_detail']:
    check(f"'{cat}' present in GRID_CATEGORIES",
          f"'{cat}'" in enums_source)


print()
if all_passed:
    print("=" * 60)
    print("✅ ALL CHECKS PASSED - Task 2B.3 complete!")
    print("=" * 60)
    print("\nwfc_values.py now contains:")
    print("  CollectionNames     — unchanged")
    print("  GridCategory        — NEW: string constants for grid categories")
    print("  DEFAULT_GRID_SIZES  — NEW: reference sizes per category")
    print("  module_size         — DEPRECATED fallback (= 8.0)")
    print("  primitive_offset_x  — DEPRECATED fallback (= 32.0)")
else:
    print("=" * 60)
    print("❌ SOME CHECKS FAILED")
    print("=" * 60)
    sys.exit(1)
