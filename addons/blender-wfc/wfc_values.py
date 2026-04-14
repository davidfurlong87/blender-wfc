from enum import Enum


bl_category_name = "wfc"


class CollectionNames(Enum):
    Primitives    = "WFC_Primitives"
    UserPrimitives = "WFC_User_Primitives"
    Modules       = "WFC_Modules"
    Grid          = "WFC_Grid"
    Debug         = "WFC_Debug"


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


# ── DEPRECATED ────────────────────────────────────────────────────────────────
# Retained as fallback constants for any code not yet migrated.
# No new code should import these — use primitive.physical_size or
# DEFAULT_GRID_SIZES[GridCategory.OUTER_GRID] instead.
# Scheduled for removal after full migration is complete.

module_size = DEFAULT_GRID_SIZES[GridCategory.OUTER_GRID]
"""DEPRECATED: Hardcoded outer-grid cell size. Use primitive.physical_size."""

primitive_offset_x = module_size * 4
"""DEPRECATED: Hardcoded display layout offset. Use physical_size-based spacing."""

