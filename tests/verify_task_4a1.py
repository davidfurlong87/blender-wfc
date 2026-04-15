"""
Verify Task 4A.1: outer_grid_library.json correctness
Run with: python tests/verify_task_4a1.py
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'addons' / 'blender-wfc'))

from primitive_data_core import PrimitiveData
from primitive_persistence import PrimitivePersistence

LIBRARY_PATH = str(Path(__file__).parent.parent / 'addons' / 'blender-wfc' / 'data' / 'outer_grid_library.json')

all_passed = True

def check(label, condition, detail=""):
    global all_passed
    status = "✅" if condition else "❌"
    print(f"  {status} {label}" + (f"  ({detail})" if detail else ""))
    if not condition:
        all_passed = False

# ── File structure ─────────────────────────────────────────────────────────
print("File structure:")
raw = json.loads(Path(LIBRARY_PATH).read_text())
check("file exists and is valid JSON", True)
check("format_version == '1.0'", raw.get("format_version") == "1.0")
check("library_metadata present", "library_metadata" in raw)
check("primitives array present", "primitives" in raw)
check("primitive_count == 3", raw["library_metadata"].get("primitive_count") == 3)
check("3 entries in primitives list", len(raw["primitives"]) == 3)

# ── Round-trip load via PrimitivePersistence ───────────────────────────────
print("\nRound-trip load:")
persistence = PrimitivePersistence()
primitives, meta, errors = persistence.load_primitive_library(LIBRARY_PATH)
check("no load errors", len(errors) == 0, ", ".join(errors) if errors else "")
check("loaded 3 primitives", len(primitives) == 3)

names = {p.name for p in primitives}
check("Building_Primitive present", "Building_Primitive" in names)
check("Corner_Primitive present",   "Corner_Primitive"   in names)
check("Pavement_Primitive present", "Pavement_Primitive" in names)

# ── Per-primitive validation ───────────────────────────────────────────────
by_name = {p.name: p for p in primitives}

print("\nBuilding_Primitive:")
b = by_name["Building_Primitive"]
check("primitive_type == BUILDING",          b.primitive_type == "BUILDING")
check("physical_size == 8.0",                b.physical_size == 8.0)
check("grid_category == outer_grid",         b.grid_category == "outer_grid")
check("resolution_multiplier == 1",          b.resolution_multiplier == 1)
check("rotation_invariant == True",          b.rotation_invariant is True)
check("all 4 connectors are BUILDING",       all(c == "BUILDING" for c in [
    b.pos_x_connector, b.neg_x_connector, b.pos_y_connector, b.neg_y_connector]))
check("25 vertices",                         len(b.verts) == 25)
check("16 faces",                            len(b.faces) == 16)
check("building_plot vertex group present",  "building_plot" in b.vertex_groups)
check("building_plot covers all 25 verts",   len(b.vertex_groups["building_plot"]["vertices"]) == 25)
is_valid, errs = b.validate()
check("PrimitiveData.validate() passes",     is_valid, ", ".join(errs) if errs else "")

print("\nCorner_Primitive:")
c = by_name["Corner_Primitive"]
check("primitive_type == CORNER",            c.primitive_type == "CORNER")
check("physical_size == 8.0",               c.physical_size == 8.0)
check("rotation_invariant == False",         c.rotation_invariant is False)
check("pos_x == ROAD",                       c.pos_x_connector == "ROAD")
check("neg_x == PAVEMENTPOS",               c.neg_x_connector == "PAVEMENTPOS")
check("pos_y == ROAD",                       c.pos_y_connector == "ROAD")
check("neg_y == PAVEMENTNEG",               c.neg_y_connector == "PAVEMENTNEG")
check("25 vertices",                         len(c.verts) == 25)
check("16 faces",                            len(c.faces) == 16)
check("3 vertex groups",                     len(c.vertex_groups) == 3)
is_valid, errs = c.validate()
check("PrimitiveData.validate() passes",     is_valid, ", ".join(errs) if errs else "")

print("\nPavement_Primitive:")
p = by_name["Pavement_Primitive"]
check("primitive_type == PAVEMENT",          p.primitive_type == "PAVEMENT")
check("physical_size == 8.0",               p.physical_size == 8.0)
check("rotation_invariant == False",         p.rotation_invariant is False)
check("pos_x == ROAD",                       p.pos_x_connector == "ROAD")
check("neg_x == BUILDING",                   p.neg_x_connector == "BUILDING")
check("pos_y == PAVEMENTPOS",               p.pos_y_connector == "PAVEMENTPOS")
check("neg_y == PAVEMENTNEG",               p.neg_y_connector == "PAVEMENTNEG")
check("25 vertices",                         len(p.verts) == 25)
check("16 faces",                            len(p.faces) == 16)
check("3 vertex groups",                     len(p.vertex_groups) == 3)
is_valid, errs = p.validate()
check("PrimitiveData.validate() passes",     is_valid, ", ".join(errs) if errs else "")

# ── Metadata (no hardcoded module_size) ───────────────────────────────────
print("\nMetadata consistency:")
check("library_name set",                    meta.get("library_name") == "Outer Grid Library")
check("description non-empty",              bool(meta.get("description")))
check("all primitives: no hardcoded 8 in grid_category",
      all(p.grid_category == "outer_grid" for p in primitives))
check("all primitives: resolution_multiplier == 1",
      all(p.resolution_multiplier == 1 for p in primitives))

print()
if all_passed:
    print("=" * 60)
    print("✅ ALL CHECKS PASSED - Task 4A.1 complete!")
    print("=" * 60)
    print(f"\nLibrary: {LIBRARY_PATH}")
else:
    print("=" * 60)
    print("❌ SOME CHECKS FAILED")
    print("=" * 60)
    sys.exit(1)
