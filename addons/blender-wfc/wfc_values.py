import bpy
from enum import Enum

bl_category_name = "wfc"

class CollectionNames(Enum):
    Primitives = "WFC_Primitives"
    Modules = "WFC_Modules"
    Grid = "WFC_Grid"

# Base
module_size = 4
