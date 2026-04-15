"""
Verify Task 4B.1: building_library.json correctness
Run with: python tests/verify_task_4b1.py
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'addons' / 'blender-wfc'))

from primitive_data_core import PrimitiveData
from primitive_persistence import PrimitivePersistence

LIBRARY_PATH = str(
    Path(__file__).parent.parent / 'addons' / 'blender-wfc' / 'data' / 'building_library.json'
)

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
check("format_version == '1.0'",      raw.get("format_version") == "1.0")
check("library_metadata present",     "library_metadata" in raw)
check("primitives array present",     "primitives" in raw)
check("primitive_count == 4",         raw["library_metadata"].get("primitive_count") == 4)
check("4 entries in primitives list", len(raw["primitives"]) == 4)

# ── Round-trip load ────────────────────────────────────────────────────────
print("\nRound-trip load:")
persistence = PrimitivePersistence()
primitives, meta, errors = persistence.load_primitive_library(LIBRARY_PATH)
check("no load errors",        len(errors) == 0, ", ".join(errors) if errors else "")
check("loaded 4 primitives",   len(primitives) == 4)

names = {p.name for p in primitives}
check("Room present",         "Room"         in names)
check("Corridor_H present",   "Corridor_H"   in names)
check("Corner_Room present",  "Corner_Room"  in names)
check("Open_Space present",   "Open_Space"   in names)

by_name = {p.name: p for p in primitives}

# ── Sizing metadata (all must be building grid) ────────────────────────────
print("\nSizing metadata (all primitives):")
for p in primitives:
    check(f"{p.name}: physical_size == 2.0",          p.physical_size == 2.0)
    check(f"{p.name}: grid_category == 'building'",   p.grid_category == "building")
    check(f"{p.name}: resolution_multiplier == 4",    p.resolution_multiplier == 4)

# ── Rotation invariance ────────────────────────────────────────────────────
print("\nRotation invariance:")
check("Room is rotation_invariant",        by_name["Room"].rotation_invariant       is True)
check("Open_Space is rotation_invariant",  by_name["Open_Space"].rotation_invariant is True)
check("Corridor_H is NOT invariant",       by_name["Corridor_H"].rotation_invariant is False)
check("Corner_Room is NOT invariant",      by_name["Corner_Room"].rotation_invariant is False)

# ── Connector values ───────────────────────────────────────────────────────
print("\nConnectors:")
r = by_name["Room"]
check("Room: all WALL",  all(c == "WALL" for c in [
    r.pos_x_connector, r.neg_x_connector, r.pos_y_connector, r.neg_y_connector]))

ch = by_name["Corridor_H"]
check("Corridor_H: +X/-X HALLWAY",  ch.pos_x_connector == "HALLWAY" and ch.neg_x_connector == "HALLWAY")
check("Corridor_H: +Y/-Y WALL",     ch.pos_y_connector == "WALL"    and ch.neg_y_connector == "WALL")

cr = by_name["Corner_Room"]
check("Corner_Room: +X DOOR",    cr.pos_x_connector == "DOOR")
check("Corner_Room: -X WALL",    cr.neg_x_connector == "WALL")
check("Corner_Room: +Y HALLWAY", cr.pos_y_connector == "HALLWAY")
check("Corner_Room: -Y WALL",    cr.neg_y_connector == "WALL")

os_ = by_name["Open_Space"]
check("Open_Space: all EMPTY", all(c == "EMPTY" for c in [
    os_.pos_x_connector, os_.neg_x_connector, os_.pos_y_connector, os_.neg_y_connector]))

# ── validate() passes ──────────────────────────────────────────────────────
print("\nPrimitiveData.validate():")
for p in primitives:
    is_valid, errs = p.validate()
    check(f"{p.name}: passes", is_valid, ", ".join(errs) if errs else "")

# ── Library metadata ───────────────────────────────────────────────────────
print("\nLibrary metadata:")
check("library_name == 'Building Library'",   meta.get("library_name") == "Building Library")
check("description non-empty",               bool(meta.get("description")))

# ── Compatibility with outer_grid (physical_size check) ───────────────────
print("\nCompatibility vs outer grid:")
outer_cell = 8.0
for p in primitives:
    cells = outer_cell / p.physical_size
    check(f"{p.name}: {cells:.0f} cells fit in 8 m outer cell",
          outer_cell % p.physical_size == 0.0)

print()
if all_passed:
    print("=" * 60)
    print("✅ ALL CHECKS PASSED - Task 4B.1 complete!")
    print("=" * 60)
else:
    print("=" * 60)
    print("❌ SOME CHECKS FAILED")
    print("=" * 60)
    sys.exit(1)
