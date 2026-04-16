"""
Verify Task A5: _modules_by_category dict + get/clear_modules_for_category
Run with: python tests/verify_task_a5.py
"""

import sys
import re
from pathlib import Path

src = Path("addons/blender-wfc/__init__.py").read_text()

all_passed = True

def check(label, condition, detail=""):
    global all_passed
    status = "OK  " if condition else "FAIL"
    print(f"  [{status}] {label}" + (f"  ({detail})" if detail else ""))
    if not condition:
        all_passed = False


# ── Source: dict declaration ────────────────────────────────────────────────
print("Source: _modules_by_category dict declared:")
check("dict variable declared",
      "_modules_by_category: dict = {}" in src)
check("old all_modules = [] global gone",
      re.search(r"^all_modules\s*=\s*\[\]", src, re.MULTILINE) is None)
check("old all_building_modules = [] standalone global gone",
      re.search(r"^all_building_modules\s*=\s*\[\]", src, re.MULTILINE) is None)


# ── Source: backward-compat aliases ─────────────────────────────────────────
print()
print("Source: backward-compat aliases:")
check("all_modules alias uses setdefault OUTER_GRID",
      "all_modules          = _modules_by_category.setdefault(GridCategory.OUTER_GRID, [])" in src)
check("all_building_modules alias uses setdefault BUILDING",
      "all_building_modules = _modules_by_category.setdefault(GridCategory.BUILDING,   [])" in src)
check("aliases appear AFTER dict declaration",
      src.index("all_modules          = _modules_by_category") >
      src.index("_modules_by_category: dict = {}"))


# ── Source: get_modules_for_category ────────────────────────────────────────
print()
print("Source: get_modules_for_category:")
check("function defined",
      "def get_modules_for_category(category: str)" in src)
check("uses setdefault",
      "return _modules_by_category.setdefault(category, [])" in src)
check("has docstring",
      "get_modules_for_category" in src and "Mutable list" in src)


# ── Source: clear_modules_for_category ──────────────────────────────────────
print()
print("Source: clear_modules_for_category:")
check("function defined",
      "def clear_modules_for_category(category: str)" in src)
check("clears in-place via .get()",
      "mods = _modules_by_category.get(category)" in src)
check("checks collection exists before deleting",
      "if check_collection_exists(col_name):" in src)
check("uses modules_collection_for(category) for col name",
      "col_name = modules_collection_for(category)" in src)


# ── Source: clear_all_modules shim ──────────────────────────────────────────
print()
print("Source: clear_all_modules shim:")
check("clear_all_modules calls clear_modules_for_category",
      "clear_modules_for_category(GridCategory.OUTER_GRID)" in src)
check("clear_all_modules no longer references all_modules.clear()",
      "def clear_all_modules" in src and
      "all_modules.clear()" not in src)


# ── Source: building shims ───────────────────────────────────────────────────
print()
print("Source: building shims:")
check("get_building_modules delegates to get_modules_for_category",
      "return get_modules_for_category(GridCategory.BUILDING)" in src)
check("clear_all_building_modules delegates to clear_modules_for_category",
      "clear_modules_for_category(GridCategory.BUILDING)" in src)
check("old all_building_modules.clear() in clear_all_building_modules gone",
      "all_building_modules.clear()" not in src)


# ── Source: generate_modules uses mods local ────────────────────────────────
print()
print("Source: generate_modules internals:")
check("generate_modules uses get_modules_for_category(OUTER_GRID)",
      "mods = get_modules_for_category(GridCategory.OUTER_GRID)" in src)
check("generate_modules uses mods.clear()",
      # verify mods.clear() exists (used by both generators)
      "mods.clear()" in src)
check("generate_modules uses mods.append",
      "mods.append(" in src)
check("generate_modules uses build_module_pairs(module, mods)",
      "build_module_pairs(module, mods)" in src)


# ── Source: generate_building_modules uses mods local ───────────────────────
print()
print("Source: generate_building_modules internals:")
check("uses get_modules_for_category(BUILDING)",
      "mods = get_modules_for_category(GridCategory.BUILDING)" in src)
check("uses ensure_modules_collection instead of get_or_create_collection",
      "ensure_modules_collection(GridCategory.BUILDING)" in src)
check("old all_building_modules.append gone from generate fn",
      "all_building_modules.append(" not in src)


# ── Logic: alias stays in sync with dict ────────────────────────────────────
print()
print("Logic: alias / dict consistency (simulated):")
sys.path.insert(0, "addons/blender-wfc")
from wfc_values import GridCategory  # stdlib-safe, no bpy

_modules_by_category = {}
all_modules_alias          = _modules_by_category.setdefault(GridCategory.OUTER_GRID, [])
all_building_modules_alias = _modules_by_category.setdefault(GridCategory.BUILDING,   [])

def _get(cat):
    return _modules_by_category.setdefault(cat, [])

def _clear(cat):
    mods = _modules_by_category.get(cat)
    if mods is not None:
        mods.clear()

# append via dict accessor → alias reflects it
_get(GridCategory.OUTER_GRID).append("outer_mod_1")
check("outer alias reflects dict append",  all_modules_alias == ["outer_mod_1"])

_get(GridCategory.BUILDING).append("building_mod_1")
check("building alias reflects dict append", all_building_modules_alias == ["building_mod_1"])

# clear via dict accessor → alias reflects it
_clear(GridCategory.OUTER_GRID)
check("outer alias reflects dict clear",   all_modules_alias == [])
check("building alias unaffected",         all_building_modules_alias == ["building_mod_1"])

# same object identity
check("outer alias is same object as dict entry",
      all_modules_alias is _modules_by_category[GridCategory.OUTER_GRID])
check("building alias is same object as dict entry",
      all_building_modules_alias is _modules_by_category[GridCategory.BUILDING])


# ── Final ────────────────────────────────────────────────────────────────────
print()
if all_passed:
    print("=" * 57)
    print("ALL CHECKS PASSED -- Task A5 complete!")
    print("=" * 57)
else:
    print("=" * 57)
    print("SOME CHECKS FAILED")
    print("=" * 57)
    sys.exit(1)
