from enum import Enum
class PrimitiveDefinition:
    def __init__(self, name, description = ""):
        # self.id = name.to_upper()
        self.name = name
        self.description = description
    
    def as_blender_enum(self):
        return (f'{self.name.upper()}', self.name, self.description)

PRIMITIVE_TYPES=[
    ('NONE', "None", ""),
    ('ROAD_STRAIGHT', "Road_Straight", ""),
    ('PAVEMENT', "Pavement", ""),
    ('BUILDING', "Building", ""),
    ('CORNER', "Corner", ""),
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
        items = [
            (c.name, c.name.replace('_', ' ').title(), c.description)
            for c in connector_registry.connectors.values()
        ]
        if items:
            return items
    except (ImportError, SystemError):
        pass

    # Fallback: return the hardcoded defaults
    return CONNECTORS

class PrimitiveModules(Enum):
    Building = "Building_Primitive"
    Pavement = "Pavement_Primitive"
    Road = "Road_Primitive"
    Corner = "Corner_Primitive"