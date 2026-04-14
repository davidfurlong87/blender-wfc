"""
Verify Task 2B.1: Refactor Module Generation
Run with: python tests/verify_task_2b1.py
"""

import sys
from pathlib import Path

init = Path('addons/blender-wfc/__init__.py').read_text()
classes = Path('addons/blender-wfc/wfc_classes.py').read_text()

all_passed = True

def check(label, condition):
    global all_passed
    status = "✅" if condition else "❌"
    print(f"  {status} {label}")
    if not condition:
        all_passed = False


# ── wfc_classes.py — WFCModule ─────────────────────────────────────────────
print("wfc_classes.py — WFCModule:")
check("physical_size parameter added",
      "physical_size=8.0" in classes)
check("self.physical_size set",
      "self.physical_size = physical_size" in classes)


# ── __init__.py — imports ──────────────────────────────────────────────────
print("\n__init__.py — imports:")
check("module_size no longer imported",
      "module_size" not in init)
check("primitive_offset_x no longer imported",
      "primitive_offset_x" not in init)


# ── __init__.py — build_from_primitive_data() ──────────────────────────────
print("\n__init__.py — build_from_primitive_data():")
check("sets physical_size on object",
      "mesh_obj.physical_size = primitive.physical_size" in init)
check("sets grid_category on object",
      "mesh_obj.grid_category = primitive.grid_category" in init)
check("sets resolution_multiplier on object",
      "mesh_obj.resolution_multiplier = primitive.resolution_multiplier" in init)
check("sets rotation_invariant on object",
      "mesh_obj.rotation_invariant = primitive.rotation_invariant" in init)


# ── __init__.py — generate_modules() ──────────────────────────────────────
print("\n__init__.py — generate_modules():")
check("reads size from primitive.physical_size",
      "size = primitive.physical_size" in init)
check("offset calculated from size not module_size",
      "offset = size * 2" in init)
check("rotation_count from rotation_invariant",
      "rotation_count = 1 if primitive.rotation_invariant else 4" in init)
check("loop uses rotation_count not hardcoded 4",
      "for rotation in range(rotation_count)" in init)
check("positioning uses size not module_size",
      "rotation * size + (rotation * offset)" in init)
check("WFCModule receives physical_size",
      "physical_size = size" in init)


# ── __init__.py — build_all_primitives() ──────────────────────────────────
print("\n__init__.py — build_all_primitives():")
check("display spacing uses primitive.physical_size",
      "display_spacing = primitive.physical_size * 2" in init)
check("location uses display_spacing",
      "i * display_spacing" in init)
check("no module_size in file at all",
      "module_size" not in init)
check("no primitive_offset_x in file at all",
      "primitive_offset_x" not in init)


# ── Functional test — WFCModule ────────────────────────────────────────────
print("\nFunctional test — WFCModule (via AST, no bpy required):")
import ast

source = Path('addons/blender-wfc/wfc_classes.py').read_text()
tree = ast.parse(source)

# Find the WFCModule class and its __init__ signature
module_class = next(
    (n for n in ast.walk(tree)
     if isinstance(n, ast.ClassDef) and n.name == 'WFCModule'), None
)
init_fn = next(
    (n for n in ast.walk(module_class)
     if isinstance(n, ast.FunctionDef) and n.name == '__init__'), None
) if module_class else None

if init_fn:
    arg_names = [a.arg for a in init_fn.args.args]
    defaults = [ast.literal_eval(d) for d in init_fn.args.defaults]
    # defaults align to the last N args
    defaults_map = dict(zip(arg_names[-len(defaults):], defaults))

    check("physical_size in __init__ args",          "physical_size" in arg_names)
    check("physical_size default is 8.0",            defaults_map.get("physical_size") == 8.0)
    check("self is first arg",                        arg_names[0] == "self")
    check("existing args still present (name)",       "name" in arg_names)
    check("existing args still present (pos_x)",      "pos_x" in arg_names)
    check("physical_size is last new addition",       arg_names[-1] == "physical_size")
else:
    print("  ❌ Could not parse WFCModule.__init__ — check wfc_classes.py")
    all_passed = False


print()
if all_passed:
    print("=" * 60)
    print("✅ ALL CHECKS PASSED - Task 2B.1 complete!")
    print("=" * 60)
    print("\nChanges summary:")
    print("  wfc_classes.py   → WFCModule.physical_size added")
    print("  __init__.py      → generate_modules() reads from primitive")
    print("  __init__.py      → rotation_invariant honoured (1 vs 4 rotations)")
    print("  __init__.py      → build_from_primitive_data() sets all 4 fields")
    print("  __init__.py      → build_all_primitives() uses physical_size spacing")
    print("  __init__.py      → module_size + primitive_offset_x imports removed")
    print("\nNext: Task 2B.2 — Update BlenderWFCAdapter for dynamic sizing")
else:
    print("=" * 60)
    print("❌ SOME CHECKS FAILED")
    print("=" * 60)
    sys.exit(1)
