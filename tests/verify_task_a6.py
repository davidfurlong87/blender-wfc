"""
Verify Task A6: generate_modules_for_category + backward-compat shims
Run with: python tests/verify_task_a6.py
"""

import sys
import re
from pathlib import Path

sys.path.insert(0, "addons/blender-wfc")
src = Path("addons/blender-wfc/__init__.py").read_text()

all_passed = True

def check(label, condition, detail=""):
    global all_passed
    status = "OK  " if condition else "FAIL"
    print(f"  [{status}] {label}" + (f"  ({detail})" if detail else ""))
    if not condition:
        all_passed = False


# ── New unified function exists ─────────────────────────────────────────────
print("Unified generate_modules_for_category:")
check("function defined",
      "def generate_modules_for_category(category: str)" in src)
check("uses ensure_modules_collection",
      "ensure_modules_collection(category)" in src)
check("uses get_primitives_by_category(category)",
      "get_primitives_by_category(category)" in src)
check("uses get_modules_for_category(category)",
      "mods = get_modules_for_category(category)" in src)
check("uses DEFAULT_GRID_SIZES for size fallback",
      "DEFAULT_GRID_SIZES.get(category" in src)
check("uses category directly for grid_category",
      "grid_category=category," in src)
check("module name includes category",
      'f"{primitive.name}_{category}_{rotation}"' in src)
check("scene property key is generic",
      'f"total_{category}_modules"' in src)
check("has early-return when no primitives",
      "no primitives found" in src)
check("uses build_module_pairs",
      "build_module_pairs(module, mods)" in src)
check("has print confirmation",
      "modules generated" in src)


# ── Old generate_modules → one-line shim ────────────────────────────────────
print()
print("generate_modules() shim:")
# Find the shim definition and verify it's a one-liner body
shim_match = re.search(
    r"def generate_modules\(\):[^\n]*\n\s+\"\"\"[^\n]*\"\"\"\n\s+(generate_modules_for_category\(GridCategory\.OUTER_GRID\))",
    src
)
check("is a one-liner shim calling generate_modules_for_category(OUTER_GRID)",
      shim_match is not None or
      ("def generate_modules():" in src and
       "generate_modules_for_category(GridCategory.OUTER_GRID)" in src))
check("no longer contains the old loop body",
      # The old body had get_all_primitives() call inside generate_modules
      not re.search(r"def generate_modules\(\):[^d]*get_all_primitives\(\)", src))
check("appears AFTER generate_modules_for_category",
      src.index("def generate_modules():") >
      src.index("def generate_modules_for_category("))


# ── generate_building_modules → one-line shim ───────────────────────────────
print()
print("generate_building_modules() shim:")
check("is a shim calling generate_modules_for_category(BUILDING)",
      "def generate_building_modules():" in src and
      "generate_modules_for_category(GridCategory.BUILDING)" in src)
check("no longer contains building loop body",
      not re.search(r"def generate_building_modules\(\):[^d]*for i, primitive", src))
check("appears after generate_modules_for_category",
      src.index("def generate_building_modules():") >
      src.index("def generate_modules_for_category("))


# ── Other shims still present ────────────────────────────────────────────────
print()
print("Other backward-compat shims still present:")
check("get_building_modules shim present",
      "def get_building_modules():" in src and
      "get_modules_for_category(GridCategory.BUILDING)" in src)
check("clear_all_building_modules shim present",
      "def clear_all_building_modules():" in src and
      "clear_modules_for_category(GridCategory.BUILDING)" in src)


# ── Old duplicated code gone ─────────────────────────────────────────────────
print()
print("Old duplicated code removed:")
check("_b{rotation} naming pattern gone",
      '"_b{rotation}"' not in src and
      "f\"_b{rotation}\"" not in src)
check("hardcoded starting_position (-50, -100, 0) gone",
      "(-50, -100, 0)" not in src)
check("old hardcoded total_building_modules scene key gone",
      '"total_building_modules"' not in src)
check("old Mirrors generate_modules() docstring gone",
      "Mirrors generate_modules()" not in src)


# ── DEFAULT_GRID_SIZES now imported ─────────────────────────────────────────
print()
print("DEFAULT_GRID_SIZES import:")
check("DEFAULT_GRID_SIZES in wfc_values import block",
      "DEFAULT_GRID_SIZES" in src[:src.index("def register(") if "def register(" in src else len(src)])


# ── Operator call sites still reference the shim names (unchanged) ──────────
print()
print("Operator call sites unchanged:")
check("OBJECT_OT_BuildBuildingModules still calls generate_building_modules()",
      "generate_building_modules()" in src)
check("generate_modules() still called in load/rebuild path",
      src.count("generate_modules()") >= 2)


# ── Final ─────────────────────────────────────────────────────────────────────
print()
if all_passed:
    print("=" * 57)
    print("ALL CHECKS PASSED -- Task A6 complete!")
    print("=" * 57)
else:
    print("=" * 57)
    print("SOME CHECKS FAILED")
    print("=" * 57)
    sys.exit(1)
