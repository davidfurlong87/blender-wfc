"""
Pure WFC Algorithm Module

This module contains the Wave Function Collapse algorithm implementation
with NO Blender dependencies. All code here should be testable without
running Blender.

The Golden Rule: "Algorithm logic should work without Blender."

See docs/architecture/ALGORITHM_SEPARATION_GUIDE.md for details.
"""

from .core import (
    WFCAlgorithm,
    score_module,
    select_highest_scored_module,
    get_lowest_entropy_cells,
)
from .grid import Grid
from .cell import AlgorithmCell
from .module import AlgorithmModule
from .enums import Axis

__all__ = [
    'WFCAlgorithm',
    'Grid',
    'AlgorithmCell',
    'AlgorithmModule',
    'Axis',
    'score_module',
    'select_highest_scored_module',
    'get_lowest_entropy_cells',
]

