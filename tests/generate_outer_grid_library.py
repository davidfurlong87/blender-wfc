"""
Generate outer_grid_library.json from the hardcoded primitive data.

This script recreates the three default WFC outer-grid primitives
(Building, Corner, Pavement) as a JSON library file using the new
metadata-driven PrimitiveData system.

No Blender installation required — PrimitiveData and PrimitivePersistence
are pure Python.

Usage:
    python tests/generate_outer_grid_library.py
"""

import sys
from pathlib import Path

# Allow direct imports without a Blender environment
sys.path.insert(0, str(Path(__file__).parent.parent / 'addons' / 'blender-wfc'))

from primitive_data_core import PrimitiveData
from primitive_persistence import PrimitivePersistence

OUTPUT_PATH = str(Path(__file__).parent.parent / 'addons' / 'blender-wfc' / 'data' / 'outer_grid_library.json')

# ---------------------------------------------------------------------------
# Building_Primitive  (from building_primitive_alt)
# All four connectors are "BUILDING" and the mesh is rotationally symmetric,
# so rotation_invariant = True (generates 1 module instead of 4).
# ---------------------------------------------------------------------------
building = PrimitiveData(
    name="Building_Primitive",
    primitive_type="BUILDING",
    verts=[
        (-4.0, -4.0, 0.0), (-4.0,  4.0, 0.0), ( 4.0, -4.0, 0.0), ( 4.0,  4.0, 0.0),
        (-2.0,  4.0, 0.0), ( 0.0,  4.0, 0.0), ( 2.0,  4.0, 0.0), (-4.0, -2.0, 0.0),
        (-4.0,  0.0, 0.0), (-4.0,  2.0, 0.0), (-2.0, -4.0, 0.0), ( 0.0, -4.0, 0.0),
        ( 2.0, -4.0, 0.0), ( 4.0, -2.0, 0.0), ( 4.0,  0.0, 0.0), ( 4.0,  2.0, 0.0),
        (-2.0, -2.0, 0.0), (-2.0,  0.0, 0.0), (-2.0,  2.0, 0.0), ( 0.0, -2.0, 0.0),
        ( 0.0,  0.0, 0.0), ( 0.0,  2.0, 0.0), ( 2.0, -2.0, 0.0), ( 2.0,  0.0, 0.0),
        ( 2.0,  2.0, 0.0),
    ],
    faces=[
        (24,15, 3, 6), ( 9,18, 4, 1), (18,21, 5, 4), (21,24, 6, 5),
        ( 0,10,16, 7), ( 7,16,17, 8), ( 8,17,18, 9), (10,11,19,16),
        (16,19,20,17), (17,20,21,18), (11,12,22,19), (19,22,23,20),
        (20,23,24,21), (12, 2,13,22), (22,13,14,23), (23,14,15,24),
    ],
    mat_indices=[0]*16,
    material_names=["Building_Primitive"],
    pos_x_connector="BUILDING",
    neg_x_connector="BUILDING",
    pos_y_connector="BUILDING",
    neg_y_connector="BUILDING",
    vertex_groups={
        'building_plot': {
            'vertices': list(range(25)),
            'weights':  [1.0] * 25,
        }
    },
    metadata={"description": "Full building plot — all edges connect to other buildings"},
    physical_size=8.0,
    grid_category="outer_grid",
    resolution_multiplier=1,
    rotation_invariant=True,   # symmetric: 1 module generated
)

# ---------------------------------------------------------------------------
# Corner_Primitive  (from corner_primitive_alt)
# Road on +X and +Y, Pavement on -X and -Y.
# ---------------------------------------------------------------------------
corner = PrimitiveData(
    name="Corner_Primitive",
    primitive_type="CORNER",
    verts=[
        ( 4.0, -4.0, 0.0), ( 4.0,  4.0, 0.0), ( 0.0, -4.0, 0.0), (-4.0, -4.0, 0.0),
        (-4.0,  0.0, 0.0), (-4.0,  4.0, 0.0), (-2.0,  4.0, 0.0), ( 0.0,  0.0, 0.0),
        ( 0.0, -2.0, 0.0), ( 4.0, -2.0, 0.0), (-2.0, -4.0, 0.0), (-4.0, -2.0, 0.0),
        (-2.0, -2.0, 0.0), (-2.0,  0.0, 0.0), ( 4.0,  0.0, 0.0), ( 0.0,  4.0, 0.0),
        ( 2.0, -4.0, 0.0), ( 2.0, -2.0, 0.0), ( 2.0,  4.0, 0.0), ( 2.0,  0.0, 0.0),
        ( 4.0,  2.0, 0.0), (-4.0,  2.0, 0.0), (-2.0,  2.0, 0.0), ( 0.0,  2.0, 0.0),
        ( 2.0,  2.0, 0.0),
    ],
    faces=[
        (12,11, 3,10), (17,16, 0, 9), (22,21, 4,13), (12,10, 2, 8),
        ( 7, 8,17,19), (19,17, 9,14), (23,22,13, 7), (20,24,19,14),
        ( 4,11,12,13), (24,23, 7,19), (13,12, 8, 7), ( 8, 2,16,17),
        (18,15,23,24), ( 1,18,24,20), (15, 6,22,23), ( 6, 5,21,22),
    ],
    mat_indices=[2,1,1,0,1,1,1,1,0,1,0,1,1,1,1,1],
    material_names=["Pavement_Primitive", "Road_Primitive", "Building_Primitive"],
    pos_x_connector="ROAD",
    neg_x_connector="PAVEMENTPOS",
    pos_y_connector="ROAD",
    neg_y_connector="PAVEMENTNEG",
    vertex_groups={
        'building_plot': {
            'vertices': [3, 10, 11, 12],
            'weights':  [1.0, 1.0, 1.0, 1.0],
        },
        'pavement_plot': {
            'vertices': [2, 4, 7, 8, 10, 11, 12, 13, 16, 17, 19, 21, 22, 23, 24],
            'weights':  [1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.5,0.5,0.5,0.5,0.5,0.5,0.25],
        },
        'road_plot': {
            'vertices': [0,1,2,4,5,6,7,8,9,13,14,15,16,17,18,19,20,21,22,23,24],
            'weights':  [1.0]*21,
        },
    },
    metadata={"description": "Corner: road on +X/+Y edges, pavement on -X/-Y edges"},
    physical_size=8.0,
    grid_category="outer_grid",
    resolution_multiplier=1,
    rotation_invariant=False,
)

# ---------------------------------------------------------------------------
# Pavement_Primitive  (from pavement_primitive_alt)
# Road on +X, Building on -X, PavementPos/PavementNeg on Y.
# ---------------------------------------------------------------------------
pavement = PrimitiveData(
    name="Pavement_Primitive",
    primitive_type="PAVEMENT",
    verts=[
        ( 4.0, -4.0, 0.0), ( 4.0,  4.0, 0.0), ( 4.0,  0.0, 0.0), ( 4.0, -2.0, 0.0),
        (-4.0, -4.0, 0.0), (-4.0,  4.0, 0.0), ( 0.0,  4.0, 0.0), ( 0.0, -4.0, 0.0),
        (-2.0, -4.0, 0.0), (-2.0,  4.0, 0.0), ( 4.0,  2.0, 0.0), (-4.0, -2.0, 0.0),
        (-4.0,  0.0, 0.0), (-4.0,  2.0, 0.0), ( 0.0,  2.0, 0.0), ( 0.0,  0.0, 0.0),
        ( 0.0, -2.0, 0.0), (-2.0, -2.0, 0.0), (-2.0,  0.0, 0.0), (-2.0,  2.0, 0.0),
        ( 2.0, -4.0, 0.0), ( 2.0,  4.0, 0.0), ( 2.0,  2.0, 0.0), ( 2.0,  0.0, 0.0),
        ( 2.0, -2.0, 0.0),
    ],
    faces=[
        ( 6, 9,19,14), (24,16, 7,20), (17,11, 4, 8), (16,17, 8, 7),
        (14,19,18,15), (15,18,17,16), ( 9, 5,13,19), (19,13,12,18),
        (18,12,11,17), (21, 6,14,22), (22,14,15,23), (23,15,16,24),
        ( 2,23,24, 3), (10,22,23, 2), ( 1,21,22,10), ( 3,24,20, 0),
    ],
    mat_indices=[0,1,2,0,0,0,2,2,2,1,1,1,1,1,1,1],
    material_names=["Pavement_Primitive", "Road_Primitive", "Building_Primitive"],
    pos_x_connector="ROAD",
    neg_x_connector="BUILDING",
    pos_y_connector="PAVEMENTPOS",
    neg_y_connector="PAVEMENTNEG",
    vertex_groups={
        'building_plot': {
            'vertices': [4,5,8,9,11,12,13,17,18,19],
            'weights':  [1.0]*10,
        },
        'pavement_plot': {
            'vertices': [6,7,8,9,14,15,16,17,18,19,20,21,22,23,24],
            'weights':  [1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.5,0.5,0.5,0.5,0.5],
        },
        'road_plot': {
            'vertices': [0,1,2,3,10,20,21,22,23,24],
            'weights':  [1.0,1.0,1.0,1.0,1.0,0.5,0.5,0.5,0.5,0.5],
        },
    },
    metadata={"description": "Pavement strip: road on +X, building on -X"},
    physical_size=8.0,
    grid_category="outer_grid",
    resolution_multiplier=1,
    rotation_invariant=False,
)

# ---------------------------------------------------------------------------
# Save the library
# ---------------------------------------------------------------------------
primitives = [building, corner, pavement]

persistence = PrimitivePersistence()
success, errors = persistence.save_primitive_library(
    primitives=primitives,
    filepath=OUTPUT_PATH,
    library_name="Outer Grid Library",
    description=(
        "Default outer-grid WFC primitives (Building, Corner, Pavement). "
        "Physical size: 8 m. Grid category: outer_grid. Resolution: 1."
    ),
    metadata={
        "author": "WFC System",
        "version": "1.0",
        "source": "primitive_data_actual.py (_alt variants)",
    }
)

if success:
    print(f"✅  Saved {len(primitives)} primitives → {OUTPUT_PATH}")
    for p in primitives:
        ri = " [rotation_invariant]" if p.rotation_invariant else ""
        print(f"    • {p.name}  ({p.primitive_type}){ri}")
else:
    print("❌  Save failed:")
    for err in errors:
        print(f"    {err}")
    sys.exit(1)

