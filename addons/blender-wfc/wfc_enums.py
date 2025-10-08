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

class PrimitiveModules(Enum):
    Building = "Building_Primitive"
    Pavement = "Pavement_Primitive"
    Road = "Road_Primitive"
    Corner = "Corner_Primitive"