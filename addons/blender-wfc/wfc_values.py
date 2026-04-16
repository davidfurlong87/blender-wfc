from enum import Enum


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


DEFAULT_GRID_SIZES = {
    GridCategory.OUTER_GRID:  8.0,
    GridCategory.BUILDING:    2.0,
    GridCategory.PARK:        1.0,
    GridCategory.ROAD_DETAIL: 4.0,
}
"""Reference mapping of grid category → default physical_size in meters.

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

