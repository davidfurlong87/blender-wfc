from enum import Enum
import json
import os as _os


bl_category_name = "wfc"


class CollectionNames(Enum):
    """The five static WFC collections that always exist.

    All category-specific sub-collections are derived dynamically via the three
    naming helpers below (primitives_collection_for, modules_collection_for,
    grid_collection_for).  Do NOT add per-category entries here.

    Tree::

        WFC                         ← Root
        ├── WFC_Primitives          ← Primitives  (parent, no direct objects)
        │   └── WFC_Primitives_{category}          (dynamic)
        ├── WFC_Modules             ← Modules     (parent, no direct objects)
        │   └── WFC_Modules_{category}             (dynamic)
        ├── WFC_Grid                ← Grid        (parent, no direct objects)
        │   └── WFC_Grid_{category}               (dynamic, any depth)
        └── WFC_Debug               ← Debug
    """
    Root       = "WFC"
    Primitives = "WFC_Primitives"
    Modules    = "WFC_Modules"
    Grid       = "WFC_Grid"
    Debug      = "WFC_Debug"


def primitives_collection_for(category: str) -> str:
    """Return the Blender collection name for primitives of *category*.

    Example::

        primitives_collection_for('building')   # → 'WFC_Primitives_building'
        primitives_collection_for('outer_grid') # → 'WFC_Primitives_outer_grid'
    """
    return f"WFC_Primitives_{category}"


def modules_collection_for(category: str) -> str:
    """Return the Blender collection name for WFC modules of *category*.

    Example::

        modules_collection_for('building')   # → 'WFC_Modules_building'
        modules_collection_for('outer_grid') # → 'WFC_Modules_outer_grid'
    """
    return f"WFC_Modules_{category}"


def grid_collection_for(category: str) -> str:
    """Return the Blender collection name for grid output of *category*.

    Works for any grid depth — outer grids, inner grids, and future
    inner-within-inner grids all follow the identical pattern.

    Example::

        grid_collection_for('outer_grid')   # → 'WFC_Grid_outer_grid'
        grid_collection_for('building')     # → 'WFC_Grid_building'
        grid_collection_for('room_detail')  # → 'WFC_Grid_room_detail'
    """
    return f"WFC_Grid_{category}"


class GridCategory:
    """Valid grid category string identifiers (Task 2B.3).

    Use these constants wherever a grid_category string is needed, rather
    than bare string literals.

    These values must stay in sync with:
      - VALID_CATEGORIES in primitive_data_core.py
      - GRID_CATEGORIES in wfc_enums.py (Blender EnumProperty items)
    """
    OUTER_GRID  = 'outer_grid'
    BUILDING    = 'building'
    PARK        = 'park'
    ROAD_DETAIL = 'road_detail'


def _load_categories_data() -> list:
    """Load category definitions from data/categories.json.

    Falls back to a hardcoded list if the file is missing or malformed so the
    add-on always has sensible defaults.
    """
    _FALLBACK = [
        {"id": "outer_grid",   "label": "Outer Grid",   "description": "Main city layout grid (default 8m cells)",   "default_physical_size": 8.0, "default_resolution_multiplier": 1},
        {"id": "building",     "label": "Building",     "description": "Interior building grid (default 2m cells)",  "default_physical_size": 2.0, "default_resolution_multiplier": 4},
        {"id": "park",         "label": "Park",         "description": "Park detail grid (default 1m cells)",        "default_physical_size": 1.0, "default_resolution_multiplier": 8},
        {"id": "road_detail",  "label": "Road Detail",  "description": "Road detail grid (default 4m cells)",        "default_physical_size": 4.0, "default_resolution_multiplier": 2},
    ]
    try:
        _data_dir = _os.path.join(_os.path.dirname(__file__), 'data')
        _path = _os.path.join(_data_dir, 'categories.json')
        with open(_path, 'r', encoding='utf-8') as _f:
            return json.load(_f).get('categories', _FALLBACK)
    except Exception:
        return _FALLBACK


#: Raw list of category dicts loaded from ``data/categories.json``.
#: Other modules (e.g. ``wfc_enums``) can import this to avoid re-reading the file.
CATEGORIES_DATA: list = _load_categories_data()

DEFAULT_GRID_SIZES: dict = {
    cat['id']: cat['default_physical_size']
    for cat in CATEGORIES_DATA
}
"""Reference mapping of grid category → default physical_size in meters.

Loaded from ``data/categories.json``; falls back to hardcoded values if the
file is unavailable.

These are defaults only. Each primitive stores its own physical_size on
the PrimitiveData object and the registered Blender object property.
Use primitive.physical_size (or obj.physical_size) in all production code.
"""


def calculate_cell_size(physical_size: float, resolution_multiplier: int) -> float:
    """Calculate the world-space size of a single grid cell in meters.

    For the outer grid (resolution_multiplier=1), cell_size == physical_size.
    For sub-grids the primitive is divided evenly, so each cell is smaller.

    Args:
        physical_size: The primitive's physical_size in meters
        resolution_multiplier: How many cells span one outer grid cell (>= 1)

    Returns:
        Size of one cell in meters

    Raises:
        ValueError: If resolution_multiplier is less than 1

    Examples:
        calculate_cell_size(8.0, 1) == 8.0   # outer grid
        calculate_cell_size(8.0, 4) == 2.0   # building grid
        calculate_cell_size(8.0, 8) == 1.0   # park grid
    """
    if resolution_multiplier < 1:
        raise ValueError(
            f"resolution_multiplier must be >= 1, got {resolution_multiplier}"
        )
    return physical_size / resolution_multiplier


# ── DEPRECATED ────────────────────────────────────────────────────────────────
# Retained as fallback constants for any code not yet migrated.
# No new code should import these — use primitive.physical_size or
# DEFAULT_GRID_SIZES[GridCategory.OUTER_GRID] instead.
# Scheduled for removal after full migration is complete.

module_size = DEFAULT_GRID_SIZES[GridCategory.OUTER_GRID]
"""DEPRECATED: Hardcoded outer-grid cell size. Use primitive.physical_size."""

primitive_offset_x = module_size * 4
"""DEPRECATED: Hardcoded display layout offset. Use physical_size-based spacing."""

