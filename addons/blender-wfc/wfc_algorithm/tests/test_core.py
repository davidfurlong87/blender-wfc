"""
Unit tests for core WFC algorithm functions

These tests verify the pure algorithm logic without Blender
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from wfc_algorithm.core import (
    score_module,
    select_highest_scored_module,
    get_lowest_entropy_cells,
    WFCAlgorithm
)
from wfc_algorithm.module import AlgorithmModule
from wfc_algorithm.cell import AlgorithmCell
from wfc_algorithm.grid import Grid
from wfc_algorithm.enums import Axis


class TestScoreModule(unittest.TestCase):
    """Test module scoring function"""
    
    def test_score_module_returns_positive(self):
        """Score should be positive for positive weight"""
        score = score_module(1.0)
        self.assertGreater(score, 0)
    
    def test_score_module_in_range(self):
        """Score should be within expected range"""
        score = score_module(1.0)
        self.assertGreaterEqual(score, 1)
        self.assertLessEqual(score, 10001)
    
    def test_score_module_weighted(self):
        """Higher weight should generally produce higher scores"""
        # Run multiple times to account for randomness
        high_scores = [score_module(10.0) for _ in range(100)]
        low_scores = [score_module(0.1) for _ in range(100)]
        
        avg_high = sum(high_scores) / len(high_scores)
        avg_low = sum(low_scores) / len(low_scores)
        
        self.assertGreater(avg_high, avg_low)


class TestSelectHighestScoredModule(unittest.TestCase):
    """Test module selection function"""
    
    def setUp(self):
        """Create test modules"""
        self.modules = [
            AlgorithmModule('A', 1.0, 'ROAD', 'ROAD', 'ROAD', 'ROAD'),
            AlgorithmModule('B', 1.0, 'BUILDING', 'BUILDING', 'BUILDING', 'BUILDING'),
            AlgorithmModule('C', 1.0, 'PAVEMENT', 'PAVEMENT', 'PAVEMENT', 'PAVEMENT'),
        ]
    
    def test_select_from_modules(self):
        """Should select one module from list"""
        selected = select_highest_scored_module(self.modules)
        self.assertIn(selected, self.modules)
    
    def test_select_empty_list(self):
        """Should return None for empty list"""
        selected = select_highest_scored_module([])
        self.assertIsNone(selected)
    
    def test_select_single_module(self):
        """Should return the only module"""
        selected = select_highest_scored_module([self.modules[0]])
        self.assertEqual(selected, self.modules[0])


class TestGetLowestEntropyCells(unittest.TestCase):
    """Test entropy calculation function"""
    
    def setUp(self):
        """Create test modules and cells"""
        self.modules = [
            AlgorithmModule('A', 1.0, 'ROAD', 'ROAD', 'ROAD', 'ROAD'),
            AlgorithmModule('B', 1.0, 'BUILDING', 'BUILDING', 'BUILDING', 'BUILDING'),
            AlgorithmModule('C', 1.0, 'PAVEMENT', 'PAVEMENT', 'PAVEMENT', 'PAVEMENT'),
        ]
    
    def test_single_lowest_entropy(self):
        """Should return cell with fewest modules"""
        cells = [
            AlgorithmCell(0, 0, self.modules),  # 3 modules
            AlgorithmCell(0, 1, self.modules[:2]),  # 2 modules (lowest)
            AlgorithmCell(1, 0, self.modules),  # 3 modules
        ]
        
        lowest = get_lowest_entropy_cells(cells)
        self.assertEqual(len(lowest), 1)
        self.assertEqual(lowest[0], cells[1])
    
    def test_multiple_lowest_entropy(self):
        """Should return all cells with same lowest entropy"""
        cells = [
            AlgorithmCell(0, 0, self.modules),  # 3 modules
            AlgorithmCell(0, 1, self.modules[:2]),  # 2 modules (lowest)
            AlgorithmCell(1, 0, self.modules[:2]),  # 2 modules (lowest)
        ]
        
        lowest = get_lowest_entropy_cells(cells)
        self.assertEqual(len(lowest), 2)
        self.assertIn(cells[1], lowest)
        self.assertIn(cells[2], lowest)
    
    def test_empty_list(self):
        """Should return empty list for empty input"""
        lowest = get_lowest_entropy_cells([])
        self.assertEqual(len(lowest), 0)


class TestWFCAlgorithm(unittest.TestCase):
    """Test WFC algorithm class"""
    
    def setUp(self):
        """Create test modules and grid"""
        self.modules = [
            AlgorithmModule('A', 1.0, 'ROAD', 'ROAD', 'ROAD', 'ROAD'),
            AlgorithmModule('B', 1.0, 'ROAD', 'ROAD', 'ROAD', 'ROAD'),
        ]
        
        # Set up module pairs (all modules compatible with each other)
        for module in self.modules:
            for axis in Axis:
                for other_module in self.modules:
                    module.add_compatible_module(axis, other_module)
        
        self.grid = Grid(2, 2)
        self.algorithm = WFCAlgorithm(self.grid)
    
    def test_collapse_cell(self):
        """Should collapse cell to single module"""
        cell = AlgorithmCell(0, 0, self.modules)
        self.grid.add_cell(cell)
        
        selected = self.algorithm.collapse_cell(cell)
        
        self.assertTrue(cell.is_collapsed)
        self.assertEqual(len(cell.possible_modules), 1)
        self.assertIn(selected, self.modules)
    
    def test_collapse_updates_grid(self):
        """Should remove cell from uncollapsed set"""
        cell = AlgorithmCell(0, 0, self.modules)
        self.grid.add_cell(cell)
        
        self.assertEqual(self.grid.get_uncollapsed_count(), 1)
        
        self.algorithm.collapse_cell(cell)
        
        self.assertEqual(self.grid.get_uncollapsed_count(), 0)


if __name__ == '__main__':
    unittest.main()

