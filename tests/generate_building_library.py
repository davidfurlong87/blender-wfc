"""
Generate building_library.json — minimal building interior primitives.

Building grid: physical_size=2.0 m, grid_category='building',
resolution_multiplier=4 (a 4×4 sub-grid inside each 8 m outer cell).

Connector types used (from connectors.json):
    WALL     — solid wall, compatible with WALL/DOOR/WINDOW
    DOOR     — opening, compatible with WALL/DOOR/HALLWAY
    WINDOW   — opening, compatible with WALL/WINDOW
    EMPTY    — open space, compatible with EMPTY
    HALLWAY  — passage, compatible with HALLWAY/DOOR

Primitives:
    Room        — WALL on all four sides, rotation_invariant=True
    Corridor_H  — HALLWAY on +X/-X, WALL on +Y/-Y (horizontal run)
    Corner_Room — DOOR on +X, HALLWAY on +Y, WALL on -X/-Y
    Open_Space  — EMPTY on all four sides, rotation_invariant=True

All primitives use a simple 2×2 m flat quad (z=0).  The intent is to
exercise the metadata system; the actual geometry is intentionally minimal
so the test does not depend on specific vert/face layouts.

Usage:
    python tests/generate_building_library.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'addons' / 'blender-wfc'))

from primitive_data_core import PrimitiveData
from primitive_persistence import PrimitivePersistence

OUTPUT_PATH = str(
    Path(__file__).parent.parent / 'addons' / 'blender-wfc' / 'data' / 'building_library.json'
)

# Shared geometry: 2×2 flat quad centred at origin (matches 2 m building cell)
_VERTS = [(-1.0, -1.0, 0.0), (-1.0, 1.0, 0.0), (1.0, -1.0, 0.0), (1.0, 1.0, 0.0)]
_FACES = [(0, 1, 3, 2)]

def _make(name, ptype, pos_x, neg_x, pos_y, neg_y, rotation_invariant=False, description=""):
    return PrimitiveData(
        name=name,
        primitive_type=ptype,
        verts=_VERTS,
        faces=_FACES,
        mat_indices=[0],
        material_names=["Building_Interior"],
        pos_x_connector=pos_x,
        neg_x_connector=neg_x,
        pos_y_connector=pos_y,
        neg_y_connector=neg_y,
        vertex_groups={},           # simple geometry — no vertex groups needed
        metadata={"description": description},
        physical_size=2.0,
        grid_category="building",
        resolution_multiplier=4,    # 4×4 sub-grid inside each 8 m outer cell
        rotation_invariant=rotation_invariant,
    )


room = _make(
    name="Room",
    ptype="ROOM",
    pos_x="WALL", neg_x="WALL", pos_y="WALL", neg_y="WALL",
    rotation_invariant=True,
    description="Enclosed room — all walls, 1 module generated (rotation invariant)",
)

corridor_h = _make(
    name="Corridor_H",
    ptype="CORRIDOR",
    pos_x="HALLWAY", neg_x="HALLWAY", pos_y="WALL", neg_y="WALL",
    rotation_invariant=False,
    description="Horizontal corridor — hallway on +X/-X, wall on +Y/-Y",
)

corner_room = _make(
    name="Corner_Room",
    ptype="CORNER_ROOM",
    pos_x="DOOR", neg_x="WALL", pos_y="HALLWAY", neg_y="WALL",
    rotation_invariant=False,
    description="Corner room — door on +X, hallway on +Y, walls on -X/-Y",
)

open_space = _make(
    name="Open_Space",
    ptype="OPEN_SPACE",
    pos_x="EMPTY", neg_x="EMPTY", pos_y="EMPTY", neg_y="EMPTY",
    rotation_invariant=True,
    description="Open area — no walls in any direction, 1 module generated",
)

primitives = [room, corridor_h, corner_room, open_space]

persistence = PrimitivePersistence()
success, errors = persistence.save_primitive_library(
    primitives=primitives,
    filepath=OUTPUT_PATH,
    library_name="Building Library",
    description=(
        "Interior building primitives for WFC sub-grid generation. "
        "Physical size: 2 m. Grid category: building. Resolution multiplier: 4."
    ),
    metadata={
        "author": "WFC System",
        "version": "1.0",
        "grid_category": "building",
        "physical_size": "2.0",
        "resolution_multiplier": "4",
    },
)

if success:
    print(f"✅  Saved {len(primitives)} primitives → {OUTPUT_PATH}")
    for p in primitives:
        ri = " [rotation_invariant]" if p.rotation_invariant else ""
        print(f"    • {p.name}  ({p.primitive_type}){ri}")
        print(f"      +X:{p.pos_x_connector}  -X:{p.neg_x_connector}"
              f"  +Y:{p.pos_y_connector}  -Y:{p.neg_y_connector}")
else:
    print("❌  Save failed:")
    for err in errors:
        print(f"    {err}")
    sys.exit(1)
