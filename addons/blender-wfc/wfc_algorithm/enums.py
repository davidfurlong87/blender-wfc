"""
Pure algorithm enums - no Blender dependencies

Extracted from wfc_classes.py
"""

from enum import Enum


class Axis(Enum):
    """Enum for grid directions"""
    POS_X = "PosX"
    NEG_X = "NegX"
    POS_Y = "PosY"
    NEG_Y = "NegY"

