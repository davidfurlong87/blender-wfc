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
        from .connector_registry import connector_registry
        items = sorted(
            [
                (c.name, c.name.replace('_', ' ').title(), c.description)
                for c in connector_registry.connectors.values()
            ],
            key=lambda item: item[1]  # sort by display name, case-insensitive order
        )
        if items:
            return items
    except (ImportError, SystemError):
        pass

    # Fallback: return the hardcoded defaults
    return CONNECTORS

GRID_CATEGORIES = [
    ('outer_grid',   "Outer Grid",   "Main city layout grid (default 8m cells)"),
    ('building',     "Building",     "Interior building grid (default 2m cells)"),
    ('park',         "Park",         "Park detail grid (default 1m cells)"),
    ('road_detail',  "Road Detail",  "Road detail grid (default 4m cells)"),
]
"""Grid category enum items for Blender EnumProperty.
Must stay in sync with VALID_CATEGORIES in primitive_data_core.py."""


class PrimitiveModules(Enum):
    Building = "Building_Primitive"
    Pavement = "Pavement_Primitive"
    Road = "Road_Primitive"
    Corner = "Corner_Primitive"