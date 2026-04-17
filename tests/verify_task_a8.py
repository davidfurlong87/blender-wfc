"""
Verify Task A8: load operator routes primitives into category subcollections.
Run with: python tests/verify_task_a8.py
"""

import sys
import re
from pathlib import Path

sys.path.insert(0, "addons/blender-wfc")
src = Path("addons/blender-wfc/primitive_ui.py").read_text()

all_passed = True

def check(label, condition, detail=""):
    global all_passed
    status = "OK  " if condition else "FAIL"
    print(f"  [{status}] {label}" + (f"  ({detail})" if detail else ""))
    if not condition:
        all_passed = False


# ── Library path changes ─────────────────────────────────────────────────────
print("Library path — per-primitive routing:")

check("ensure_primitives_collection imported inside library branch",
      "from .collectiontools import ensure_primitives_collection" in src)

check("prim_collection resolved per primitive using grid_category",
      "prim_collection = ensure_primitives_collection(prim_data.grid_category)" in src)

check("old single shared prim_collection block removed",
      "prim_collection = get_or_create_collection(CollectionNames.Primitives.value)" not in src)

check("old try/except fallback to scene.collection removed",
      # The old fallback was "prim_collection = context.scene.collection" inside a try block
      not re.search(
          r"except Exception:\s*\n\s*prim_collection = context\.scene\.collection",
          src
      ))

check("old CollectionNames import in operator body removed",
      # Was inside the try block: from .wfc_values import CollectionNames
      "from .wfc_values import CollectionNames" not in src
      or src.count("from .wfc_values import CollectionNames") == 0)

check("resolved collection used in create_blender_object_from_primitive",
      "prim_data, collection=prim_collection, location=loc" in src)


# ── Single-primitive path changes ────────────────────────────────────────────
print()
print("Single-primitive path — correct collection:")

check("ensure_primitives_collection imported in single branch",
      src.count("from .collectiontools import ensure_primitives_collection") == 2)

check("prim_collection resolved from primitive_data.grid_category",
      "prim_collection = ensure_primitives_collection(primitive_data.grid_category)" in src)

check("old context.scene.collection target removed",
      "collection=context.scene.collection" not in src)

check("cursor location still used",
      "location=context.scene.cursor.location" in src)

check("new prim_collection used in single create call",
      "primitive_data,\n                collection=prim_collection,\n                location=context.scene.cursor.location" in src)


# ── No regressions in surrounding structure ───────────────────────────────────
print()
print("No regressions:")

check("library format detection still present",
      "is_library = 'primitives' in _raw" in src)

check("error guard for empty library still present",
      "No primitives loaded from library" in src)

check("spacing accumulation still present",
      "spacing += prim_data.physical_size * 2" in src)

check("select + activate after library load still present",
      "context.view_layer.objects.active = created[-1]" in src)

check("error guard for empty single primitive still present",
      "Failed to load primitive data" in src)

check("OBJECT_OT_WFCLoadPrimitive still registered",
      "OBJECT_OT_WFCLoadPrimitive" in src)


# ── Verify both usages use the same function name (no typos) ─────────────────
print()
print("Consistency:")
usage_count = src.count("ensure_primitives_collection(")
check("ensure_primitives_collection called exactly twice in file",
      usage_count == 2, f"found {usage_count}")

import_count = src.count("from .collectiontools import ensure_primitives_collection")
check("imported twice (once per branch, lazy import)",
      import_count == 2, f"found {import_count}")


# ── Final ─────────────────────────────────────────────────────────────────────
print()
if all_passed:
    print("=" * 57)
    print("ALL CHECKS PASSED -- Task A8 complete!")
    print("=" * 57)
else:
    print("=" * 57)
    print("SOME CHECKS FAILED")
    print("=" * 57)
    sys.exit(1)
