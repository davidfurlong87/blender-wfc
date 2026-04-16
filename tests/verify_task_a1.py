"""
Verify Task A1: CollectionNames simplified to 5 static entries + 3 naming helpers.
Run with: python tests/verify_task_a1.py
"""

import sys
import types
from pathlib import Path

bpy_stub = types.ModuleType('bpy')
bpy_stub.props = types.ModuleType('bpy.props')
bpy_stub.types = types.ModuleType('bpy.types')
sys.modules.setdefault('bpy', bpy_stub)
sys.modules.setdefault('bpy.props', bpy_stub.props)
sys.modules.setdefault('bpy.types', bpy_stub.types)
sys.modules.setdefault('mathutils', types.ModuleType('mathutils'))

sys.path.insert(0, 'addons/blender-wfc')

from wfc_values import (
    CollectionNames,
    primitives_collection_for,
    modules_collection_for,
    grid_collection_for,
)

all_passed = True

def check(label, condition, detail=""):
    global all_passed
    status = "OK  " if condition else "FAIL"
    print(f"  [{status}] {label}" + (f"  ({detail})" if detail else ""))
    if not condition:
        all_passed = False


# -- Static names: exactly 5 -----------------------------------------------
print("CollectionNames -- exactly 5 static entries:")
names = [e.name for e in CollectionNames]
check("5 entries total",           len(names) == 5, f"got {len(names)}: {names}")
check("Root present",              "Root"       in names)
check("Primitives present",        "Primitives" in names)
check("Modules present",           "Modules"    in names)
check("Grid present",              "Grid"       in names)
check("Debug present",             "Debug"      in names)
check("UserPrimitives removed",    "UserPrimitives"  not in names)
check("BuildingModules removed",   "BuildingModules" not in names)
check("GridOuter not present",     "GridOuter"  not in names)
check("GridInner not present",     "GridInner"  not in names)

print()
print("CollectionNames -- values:")
check("Root  == 'WFC'",               CollectionNames.Root.value       == "WFC")
check("Primitives == 'WFC_Primitives'", CollectionNames.Primitives.value == "WFC_Primitives")
check("Modules == 'WFC_Modules'",     CollectionNames.Modules.value    == "WFC_Modules")
check("Grid == 'WFC_Grid'",           CollectionNames.Grid.value       == "WFC_Grid")
check("Debug == 'WFC_Debug'",         CollectionNames.Debug.value      == "WFC_Debug")

# -- primitives_collection_for ----------------------------------------------
print()
print("primitives_collection_for():")
check("outer_grid -> WFC_Primitives_outer_grid",
      primitives_collection_for("outer_grid") == "WFC_Primitives_outer_grid")
check("building -> WFC_Primitives_building",
      primitives_collection_for("building") == "WFC_Primitives_building")
check("park -> WFC_Primitives_park",
      primitives_collection_for("park") == "WFC_Primitives_park")
check("unknown/future category accepted without error",
      primitives_collection_for("industrial") == "WFC_Primitives_industrial")

# -- modules_collection_for ------------------------------------------------
print()
print("modules_collection_for():")
check("outer_grid -> WFC_Modules_outer_grid",
      modules_collection_for("outer_grid") == "WFC_Modules_outer_grid")
check("building -> WFC_Modules_building",
      modules_collection_for("building") == "WFC_Modules_building")
check("unknown/future category accepted without error",
      modules_collection_for("industrial") == "WFC_Modules_industrial")

# -- grid_collection_for ---------------------------------------------------
print()
print("grid_collection_for():")
check("outer_grid -> WFC_Grid_outer_grid",
      grid_collection_for("outer_grid") == "WFC_Grid_outer_grid")
check("building -> WFC_Grid_building",
      grid_collection_for("building") == "WFC_Grid_building")
check("room_detail (future depth) -> WFC_Grid_room_detail",
      grid_collection_for("room_detail") == "WFC_Grid_room_detail")
check("unknown/future category accepted without error",
      grid_collection_for("industrial") == "WFC_Grid_industrial")

# -- Symmetry: all three helpers share the same suffix pattern -------------
print()
print("Symmetry -- all three helpers end with the category string:")
for cat in ("outer_grid", "building", "park", "road_detail", "room_detail"):
    check(
        f"{cat}: primitives/modules/grid all end with category",
        primitives_collection_for(cat).endswith(cat)
        and modules_collection_for(cat).endswith(cat)
        and grid_collection_for(cat).endswith(cat),
    )

# -- No stale references in source files -----------------------------------
print()
print("Source hygiene -- no stale CollectionNames references:")
init_src   = Path("addons/blender-wfc/__init__.py").read_text()
coll_src   = Path("addons/blender-wfc/wfc_collections.py").read_text()
check("CollectionNames.BuildingModules gone from __init__.py",
      "CollectionNames.BuildingModules" not in init_src)
check("CollectionNames.UserPrimitives gone from wfc_collections.py",
      "CollectionNames.UserPrimitives" not in coll_src)
check("modules_collection_for used in __init__.py (replacing BuildingModules)",
      "modules_collection_for" in init_src)

print()
if all_passed:
    print("=" * 55)
    print("ALL CHECKS PASSED -- Task A1 complete!")
    print("=" * 55)
else:
    print("=" * 55)
    print("SOME CHECKS FAILED")
    print("=" * 55)
    sys.exit(1)
