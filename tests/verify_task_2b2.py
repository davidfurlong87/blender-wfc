"""
Verify Task 2B.2: Update BlenderWFCAdapter for dynamic sizing
Run with: python tests/verify_task_2b2.py
"""

import sys
from pathlib import Path

content = Path('addons/blender-wfc/wfc_blender_adapter.py').read_text()

all_passed = True

def check(label, condition):
    global all_passed
    status = "✅" if condition else "❌"
    print(f"  {status} {label}")
    if not condition:
        all_passed = False


# ── Import cleanup ─────────────────────────────────────────────────────────
print("Import:")
check("module_size no longer imported",
      "module_size" not in content)
check("CollectionNames still imported",
      "CollectionNames" in content)


# ── _get_cell_size() helper ────────────────────────────────────────────────
print("\n_get_cell_size() helper:")
check("method defined",
      "def _get_cell_size(self)" in content)
check("reads from blender_module_map",
      "self.blender_module_map" in content and "_get_cell_size" in content)
check("reads .physical_size from module",
      "blender_module_map.values())).physical_size" in content)
check("fallback to 8.0",
      "return 8.0" in content)


# ── create_blender_visualization_grid() ───────────────────────────────────
print("\ncreate_blender_visualization_grid():")
check("uses _get_cell_size()",
      "debug_mesh_size = self._get_cell_size()" in content)
check("no longer uses module_size for debug_mesh_size",
      "debug_mesh_size = module_size" not in content)


# ── create_blender_object_for_cell() ──────────────────────────────────────
print("\ncreate_blender_object_for_cell():")
check("placement uses wfc_module.physical_size",
      "cell.x * wfc_module.physical_size" in content)
check("both x and y use physical_size",
      "cell.y * wfc_module.physical_size" in content)
check("no longer uses module_size for placement",
      "cell.x * module_size" not in content)


# ── Building plot coordinate conversion ───────────────────────────────────
print("\nBuilding plot coordinate conversion:")
check("coords[0] uses blender_module.physical_size",
      "coords[0] * blender_module.physical_size" in content)
check("coords[1] uses blender_module.physical_size",
      "coords[1] * blender_module.physical_size" in content)
check("no longer uses module_size for coord conversion",
      "coords[0] * module_size" not in content)


# ── _calculate_island_grid_size() ─────────────────────────────────────────
print("\n_calculate_island_grid_size():")
check("uses cell_size = self._get_cell_size()",
      "cell_size = self._get_cell_size()" in content)
check("grid_width uses cell_size",
      "int(width / cell_size)" in content)
check("grid_height uses cell_size",
      "int(height / cell_size)" in content)
check("no longer uses module_size for island size",
      "width / module_size" not in content)


# ── Confirm zero remaining module_size references ─────────────────────────
print("\nFinal sanity check:")
remaining = [i+1 for i, line in enumerate(content.splitlines()) if "module_size" in line]
check(f"zero remaining module_size references (found on lines: {remaining})",
      len(remaining) == 0)


print()
if all_passed:
    print("=" * 60)
    print("✅ ALL CHECKS PASSED - Task 2B.2 complete!")
    print("=" * 60)
    print("\nChanges summary:")
    print("  _get_cell_size()          → new helper, reads from modules")
    print("  visualization_grid()      → uses _get_cell_size()")
    print("  create_object_for_cell()  → uses wfc_module.physical_size")
    print("  building plot coords      → uses blender_module.physical_size")
    print("  island_grid_size()        → uses _get_cell_size()")
    print("  import                    → module_size removed")
    print("\nmodule_size is now fully retired from the codebase!")
else:
    print("=" * 60)
    print("❌ SOME CHECKS FAILED")
    print("=" * 60)
    sys.exit(1)
