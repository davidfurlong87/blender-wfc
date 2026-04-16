"""
Static (no-Blender) verification of Milestone 5 code changes.
Run with: python tests/verify_milestone5_static.py
"""

import sys
import types
import os
from pathlib import Path

# Stub bpy so pure Python modules import cleanly outside Blender
bpy_stub = types.ModuleType('bpy')
bpy_stub.props = types.ModuleType('bpy.props')
bpy_stub.types = types.ModuleType('bpy.types')
sys.modules.setdefault('bpy', bpy_stub)
sys.modules.setdefault('bpy.props', bpy_stub.props)
sys.modules.setdefault('bpy.types', bpy_stub.types)
sys.modules.setdefault('mathutils', types.ModuleType('mathutils'))

sys.path.insert(0, 'addons/blender-wfc')

all_passed = True

def check(label, condition, detail=""):
    global all_passed
    status = "OK" if condition else "FAIL"
    print(f"  [{status}] {label}" + (f"  ({detail})" if detail else ""))
    if not condition:
        all_passed = False

DATA_DIR = os.path.join('addons', 'blender-wfc', 'data')

# ---- 5A.1: load_primitives_by_category ----------------------------------- #
print("Task 5A.1 - load_primitives_by_category:")
from primitive_persistence import PrimitivePersistence, CATEGORY_LIBRARY_FILES

p = PrimitivePersistence()

prims, errs = p.load_primitives_by_category('outer_grid', DATA_DIR)
check("outer_grid: 3 primitives loaded",   len(prims) == 3, f"got {len(prims)}, errs={errs}")
check("outer_grid: all grid_category match", all(x.grid_category == 'outer_grid' for x in prims))

prims, errs = p.load_primitives_by_category('building', DATA_DIR)
check("building: 4 primitives loaded",     len(prims) == 4, f"got {len(prims)}, errs={errs}")
check("building: all grid_category match", all(x.grid_category == 'building' for x in prims))

prims, errs = p.load_primitives_by_category('unknown', DATA_DIR)
check("unknown category: 0 prims + error", len(prims) == 0 and len(errs) > 0)

check("CATEGORY_LIBRARY_FILES has outer_grid",  'outer_grid' in CATEGORY_LIBRARY_FILES)
check("CATEGORY_LIBRARY_FILES has building",    'building'   in CATEGORY_LIBRARY_FILES)
check("CATEGORY_LIBRARY_FILES has park",        'park'       in CATEGORY_LIBRARY_FILES)
check("building maps to building_library.json", CATEGORY_LIBRARY_FILES['building'] == 'building_library.json')

# ---- 5B.1: WFCModule.grid_category (source inspection) ------------------- #
print("\nTask 5B.1 - WFCModule.grid_category:")
wfc_classes_src = Path('addons/blender-wfc/wfc_classes.py').read_text()
check("WFCModule.__init__ accepts grid_category param",
      "def __init__(self, name, obj_source, module_weight, pos_x, neg_x, pos_y, neg_y," in wfc_classes_src
      and "grid_category='outer_grid'" in wfc_classes_src)
check("WFCModule.grid_category stored as self attribute",
      "self.grid_category = grid_category" in wfc_classes_src)
check("physical_size still present",
      "self.physical_size = physical_size" in wfc_classes_src)

# ---- 5B.1: CollectionNames.BuildingModules ------------------------------- #
print("\nTask 5B.1 - CollectionNames:")
from wfc_values import CollectionNames, GridCategory
check("CollectionNames.BuildingModules exists",
      hasattr(CollectionNames, 'BuildingModules'))
check("BuildingModules value == 'WFC_Building_Modules'",
      CollectionNames.BuildingModules.value == 'WFC_Building_Modules')
check("GridCategory.BUILDING == 'building'",    GridCategory.BUILDING == 'building')
check("GridCategory.OUTER_GRID == 'outer_grid'", GridCategory.OUTER_GRID == 'outer_grid')

# ---- 5B.1: __init__.py source inspection --------------------------------- #
print("\nTask 5B.1 - __init__.py source:")
init_src = Path('addons/blender-wfc/__init__.py').read_text()
check("generate_building_modules() defined",   "def generate_building_modules()" in init_src)
check("get_building_modules() defined",        "def get_building_modules()" in init_src)
check("clear_all_building_modules() defined",  "def clear_all_building_modules()" in init_src)
check("all_building_modules list declared",    "all_building_modules = []" in init_src)
check("OBJECT_OT_BuildBuildingModules defined","class OBJECT_OT_BuildBuildingModules" in init_src)
check("build_building_modules registered",     "OBJECT_OT_BuildBuildingModules" in init_src and
                                               "object.build_building_modules" in init_src)
check("grid_category passed to WFCModule in generate_modules",
      "grid_category = getattr(primitive" in init_src)
check("generate_building_modules uses GridCategory.BUILDING",
      "GridCategory.BUILDING" in init_src)

# ---- 5C.1: wfc_blender_adapter.py source inspection --------------------- #
print("\nTask 5C.1 - wfc_blender_adapter.py source:")
adapter_src = Path('addons/blender-wfc/wfc_blender_adapter.py').read_text()
check("get_modules_for_category() defined",        "def get_modules_for_category(" in adapter_src)
check("create_inner_grid_for_island accepts category",
      "def create_inner_grid_for_island(self, island, resolution_multiplier=4," in adapter_src and
      "category=None" in adapter_src)
check("create_inner_grid_for_island returns tuple", "return inner_grid, inner_modules" in adapter_src)

# ---- 5C.2: building inner grid operator ---------------------------------- #
print("\nTask 5C.2 - OBJECT_OT_GenerateBuildingInnerGrid:")
check("operator class defined",    "class OBJECT_OT_GenerateBuildingInnerGrid" in init_src)
check("bl_idname correct",        "object.generate_building_inner_grid" in init_src)
check("operator registered",       "OBJECT_OT_GenerateBuildingInnerGrid" in init_src)
check("panel button added",        '"object.generate_building_inner_grid"' in init_src)
check("Build Building Modules button in panel", '"object.build_building_modules"' in init_src)
check("BlenderWFCAdapter imported", "BlenderWFCAdapter" in init_src)

print()
if all_passed:
    print("=" * 60)
    print("ALL CHECKS PASSED - Milestone 5 code complete!")
    print("=" * 60)
else:
    print("=" * 60)
    print("SOME CHECKS FAILED")
    print("=" * 60)
    sys.exit(1)
