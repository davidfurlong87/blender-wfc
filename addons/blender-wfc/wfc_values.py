import bpy
from enum import Enum

bl_category_name = "wfc"


class CollectionNames(Enum):
    Primitives = "WFC_Primitives"
    Modules = "WFC_Modules"
    Grid = "WFC_Grid"
    Debug = "WFC_Debug"


# def get_opposite_axis(axis):
#     match axis:
#         case axis.POS_X:
#             return axis.NEG_X
#         case axis.NEG_X:
#             return axis.POS_X
#         case axis.POS_Y:
#             return axis.NEG_Y
#         case axis.NEG_Y:
#             return axis.POS_Y

# Base
module_size = 8

primitive_offset_x = module_size * 4

import bpy


