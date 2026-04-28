from enum import Enum
class PrimitiveDefinition:
    def __init__(self, name, description = ""):
        # self.id = name.to_upper()
        self.name = name
        self.description = description
    
    def as_blender_enum(self):
        return (f'{self.name.upper()}', self.name, self.description)

PRIMITIVE_TYPES=[
    # ── Outer grid (8 m) ─────────────────────────────────────────────────
    ('NONE',          "None",          ""),
    ('ROAD_STRAIGHT', "Road Straight", "Straight road segment"),
    ('PAVEMENT',      "Pavement",      "Pavement strip alongside road"),
    ('BUILDING',      "Building",      "Full building plot cell"),
    ('CORNER',        "Corner",        "Corner where road meets pavement"),
    # ── Building interior (2 m) ──────────────────────────────────────────
    ('ROOM',          "Room",          "Enclosed room — walls on all sides"),
    ('CORRIDOR',      "Corridor",      "Straight corridor / hallway run"),
    ('CORNER_ROOM',   "Corner Room",   "Room with door on one side, hallway on another"),
    ('OPEN_SPACE',    "Open Space",    "Fully open area — no walls"),
    # ── Park (1 m) ───────────────────────────────────────────────────────
    ('GRASS',         "Grass",         "Grass area"),
    ('PATH',          "Path",          "Paved or gravel path"),
    ('FEATURE',       "Feature",       "Park feature (fountain, bench, tree, etc.)"),
]

CUSTOM_PRIMITIVE_TYPES = []

CONNECTORS = [
    ('ROAD', "Road", ""),
    ('BUILDING', "Building", ""),
    ('PAVEMENTPOS', "PavementPos", ""),
    ('PAVEMENTNEG', "PavementNeg", "")
]
"""Fallback connector list - used when the registry is not yet available"""


def get_connector_enum_items(self=None, context=None):
    """
    Get connector enum items from the connector registry.

    Accepts optional (self, context) so it can be used directly as a Blender
    EnumProperty callback on operator class properties, AND called without
    arguments at registration time for bpy.types.Object properties.

    Falls back to the hardcoded CONNECTORS list if the registry is unavailable.

    Returns:
        List of (identifier, name, description) tuples for Blender EnumProperty
    """
    try:
        from .connector_registry import get_active_registry, is_session_registry_set
        active = get_active_registry()
        items = sorted(
            [
                (c.name, c.name.replace('_', ' ').title(), c.description)
                for c in active.connectors.values()
            ],
            key=lambda item: item[1]  # sort by display name
        )
        if items:
            return items

        # A session registry is explicitly active but has no connectors yet
        # (e.g. a brand-new pack).  Return a placeholder instead of falling
        # back to the global hardcoded defaults, which belong to a completely
        # different pack and would be deeply confusing.
        if is_session_registry_set():
            return [('NONE', '(no connectors — add one first)', '')]

    except (ImportError, SystemError):
        pass

    # No session override at all: fall back to the global hardcoded defaults.
    return CONNECTORS

def _build_grid_categories() -> list:
    """Build GRID_CATEGORIES enum items from ``data/categories.json``.

    Falls back to a hardcoded list if the data module is unavailable (e.g. during
    Blender registration before the add-on path is on sys.path).
    """
    _FALLBACK = [
        ('outer_grid',   "Outer Grid",   "Main city layout grid (default 8m cells)"),
        ('building',     "Building",     "Interior building grid (default 2m cells)"),
        ('park',         "Park",         "Park detail grid (default 1m cells)"),
        ('road_detail',  "Road Detail",  "Road detail grid (default 4m cells)"),
    ]
    try:
        from .wfc_values import CATEGORIES_DATA
        items = [(c['id'], c['label'], c['description']) for c in CATEGORIES_DATA]
        return items if items else _FALLBACK
    except (ImportError, SystemError, KeyError):
        return _FALLBACK


GRID_CATEGORIES: list = _build_grid_categories()
"""Grid category enum items for Blender EnumProperty.

Loaded from ``data/categories.json`` via ``wfc_values.CATEGORIES_DATA``.
A new category added to ``categories.json`` automatically appears in all
EnumProperty dropdowns — no Python changes required.
"""


class PrimitiveModules(Enum):
    Building = "Building_Primitive"
    Pavement = "Pavement_Primitive"
    Road = "Road_Primitive"
    Corner = "Corner_Primitive"