"""
Verify Task 3B.2: Add Helper Functions
Run with: python tests/verify_task_3b2.py
"""

import sys
import types
from pathlib import Path

# Stub bpy so wfc_values imports cleanly outside Blender
sys.modules.setdefault('bpy', types.ModuleType('bpy'))
sys.path.insert(0, 'addons/blender-wfc')

init_src   = Path('addons/blender-wfc/__init__.py').read_text()
values_src = Path('addons/blender-wfc/wfc_values.py').read_text()

all_passed = True

def check(label, condition):
    global all_passed
    status = "✅" if condition else "❌"
    print(f"  {status} {label}")
    if not condition:
        all_passed = False


# ── calculate_cell_size — static checks ──────────────────────────────────────
print("wfc_values.py — calculate_cell_size() static:")
check("function defined",
      "def calculate_cell_size(physical_size: float, resolution_multiplier: int)" in values_src)
check("returns physical_size / resolution_multiplier",
      "return physical_size / resolution_multiplier" in values_src)
check("raises ValueError on resolution < 1",
      "ValueError" in values_src)
check("docstring has examples",
      "calculate_cell_size(8.0, 1)" in values_src)

# ── calculate_cell_size — functional ─────────────────────────────────────────
print("\nwfc_values.py — calculate_cell_size() functional:")
import wfc_values

check("outer grid (8.0, 1) → 8.0",    wfc_values.calculate_cell_size(8.0, 1)  == 8.0)
check("building  (8.0, 4) → 2.0",     wfc_values.calculate_cell_size(8.0, 4)  == 2.0)
check("park      (8.0, 8) → 1.0",     wfc_values.calculate_cell_size(8.0, 8)  == 1.0)
check("road detail (8.0, 2) → 4.0",   wfc_values.calculate_cell_size(8.0, 2)  == 4.0)
check("custom (6.0, 3) → 2.0",        wfc_values.calculate_cell_size(6.0, 3)  == 2.0)
check("resolution=1 always returns physical_size",
      wfc_values.calculate_cell_size(5.5, 1) == 5.5)

# Verify raises on invalid input
try:
    wfc_values.calculate_cell_size(8.0, 0)
    check("raises ValueError for resolution=0", False)
except ValueError:
    check("raises ValueError for resolution=0", True)

try:
    wfc_values.calculate_cell_size(8.0, -1)
    check("raises ValueError for resolution=-1", False)
except ValueError:
    check("raises ValueError for resolution=-1", True)

# ── calculate_cell_size matches DEFAULT_GRID_SIZES ───────────────────────────
print("\nConsistency with DEFAULT_GRID_SIZES:")
gc = wfc_values.GridCategory
gd = wfc_values.DEFAULT_GRID_SIZES

check("outer_grid: calculate matches DEFAULT",
      wfc_values.calculate_cell_size(gd[gc.OUTER_GRID], 1) == gd[gc.OUTER_GRID])
check("building: calculate_cell_size(8.0, 4) matches DEFAULT",
      wfc_values.calculate_cell_size(gd[gc.OUTER_GRID], 4) == gd[gc.BUILDING])
check("park: calculate_cell_size(8.0, 8) matches DEFAULT",
      wvc := wfc_values.calculate_cell_size(gd[gc.OUTER_GRID], 8),
      wvc == gd[gc.PARK]) if False else check(
      "park: calculate_cell_size(8.0, 8) matches DEFAULT",
      wfc_values.calculate_cell_size(gd[gc.OUTER_GRID], 8) == gd[gc.PARK])


# ── get_primitives_by_category — static checks ───────────────────────────────
print("\n__init__.py — get_primitives_by_category() static:")
check("function defined",
      "def get_primitives_by_category(category: str):" in init_src)
check("filters by p.grid_category == category",
      "p.grid_category == category" in init_src)
check("uses get_all_primitives()",
      "get_all_primitives()" in init_src and
      "get_primitives_by_category" in init_src)
check("placed after get_all_primitives()",
      init_src.index("def get_primitives_by_category") >
      init_src.index("def get_all_primitives"))
check("docstring mentions GridCategory",
      "GridCategory" in init_src[init_src.index("def get_primitives_by_category"):
                                  init_src.index("def get_primitives_by_category") + 500])


print()
if all_passed:
    print("=" * 60)
    print("✅ ALL CHECKS PASSED - Task 3B.2 complete!")
    print("=" * 60)
    print("\nTwo new helpers available:")
    print()
    print("  wfc_values.calculate_cell_size(physical_size, resolution)")
    print("    calculate_cell_size(8.0, 1)  → 8.0  (outer grid)")
    print("    calculate_cell_size(8.0, 4)  → 2.0  (building)")
    print("    calculate_cell_size(8.0, 8)  → 1.0  (park)")
    print()
    print("  __init__.get_primitives_by_category(category)")
    print("    get_primitives_by_category(GridCategory.BUILDING)")
    print("    → list of bpy.types.Object with grid_category == 'building'")
else:
    print("=" * 60)
    print("❌ SOME CHECKS FAILED")
    print("=" * 60)
    sys.exit(1)
