"""
Unit tests for pure data classes (Module, Cell, Grid)

These tests verify the data structures work correctly without Blender
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from wfc_algorithm.module import AlgorithmModule
from wfc_algorithm.cell import AlgorithmCell
from wfc_algorithm.grid import Grid
from wfc_algorithm.enums import Axis


class TestAlgorithmModule(unittest.TestCase):
    """Test AlgorithmModule class"""
    
    def setUp(self):
        """Create test module"""
        self.module = AlgorithmModule(
            module_id='TestModule',
            weight=2.5,
            pos_x='ROAD',
            neg_x='BUILDING',
            pos_y='PAVEMENT',
            neg_y='ROAD'
        )
    
    def test_module_initialization(self):
        """Module should initialize with correct values"""
        self.assertEqual(self.module.id, 'TestModule')
        self.assertEqual(self.module.weight, 2.5)
        self.assertEqual(self.module.pos_x, 'ROAD')
        self.assertEqual(self.module.neg_x, 'BUILDING')
    
    def test_module_pairs_empty(self):
        """Module pairs should start empty"""
        self.assertEqual(len(self.module.pos_x_pairs), 0)
        self.assertEqual(len(self.module.neg_x_pairs), 0)
    
    def test_add_compatible_module(self):
        """Should add compatible modules"""
        other = AlgorithmModule('Other', 1.0, 'ROAD', 'ROAD', 'ROAD', 'ROAD')
        
        self.module.add_compatible_module(Axis.POS_X, other)
        
        self.assertEqual(len(self.module.pos_x_pairs), 1)
        self.assertIn(other, self.module.pos_x_pairs)
    
    def test_add_duplicate_module(self):
        """Should not add duplicate modules"""
        other = AlgorithmModule('Other', 1.0, 'ROAD', 'ROAD', 'ROAD', 'ROAD')
        
        self.module.add_compatible_module(Axis.POS_X, other)
        self.module.add_compatible_module(Axis.POS_X, other)
        
        self.assertEqual(len(self.module.pos_x_pairs), 1)
    
    def test_get_all_pairs_for_axis(self):
        """Should return correct pairs for each axis"""
        other = AlgorithmModule('Other', 1.0, 'ROAD', 'ROAD', 'ROAD', 'ROAD')
        
        self.module.add_compatible_module(Axis.POS_X, other)
        
        pairs = self.module.get_all_pairs_for_axis(Axis.POS_X)
        self.assertEqual(len(pairs), 1)
        self.assertIn(other, pairs)


class TestAlgorithmCell(unittest.TestCase):
    """Test AlgorithmCell class"""
    
    def setUp(self):
        """Create test modules and cell"""
        self.modules = [
            AlgorithmModule('A', 1.0, 'ROAD', 'ROAD', 'ROAD', 'ROAD'),
            AlgorithmModule('B', 1.0, 'BUILDING', 'BUILDING', 'BUILDING', 'BUILDING'),
            AlgorithmModule('C', 1.0, 'PAVEMENT', 'PAVEMENT', 'PAVEMENT', 'PAVEMENT'),
        ]
        self.cell = AlgorithmCell(5, 7, self.modules)
    
    def test_cell_initialization(self):
        """Cell should initialize with correct values"""
        self.assertEqual(self.cell.x, 5)
        self.assertEqual(self.cell.y, 7)
        self.assertEqual(len(self.cell.possible_modules), 3)
        self.assertFalse(self.cell.is_collapsed)
    
    def test_cell_copies_module_list(self):
        """Cell should copy module list, not reference it"""
        self.cell.possible_modules.append(AlgorithmModule('D', 1.0, 'ROAD', 'ROAD', 'ROAD', 'ROAD'))
        self.assertEqual(len(self.modules), 3)  # Original unchanged
        self.assertEqual(len(self.cell.possible_modules), 4)
    
    def test_get_coords(self):
        """Should return coordinates as list"""
        coords = self.cell.get_coords()
        self.assertEqual(coords, [5, 7])
    
    def test_get_coords_tuple(self):
        """Should return coordinates as tuple"""
        coords = self.cell.get_coords_tuple()
        self.assertEqual(coords, (5, 7))
    
    def test_get_neighbor_coords(self):
        """Should return correct neighbor coordinates"""
        self.assertEqual(self.cell.get_neighbor_coords(Axis.POS_X), (6, 7))
        self.assertEqual(self.cell.get_neighbor_coords(Axis.NEG_X), (4, 7))
        self.assertEqual(self.cell.get_neighbor_coords(Axis.POS_Y), (5, 8))
        self.assertEqual(self.cell.get_neighbor_coords(Axis.NEG_Y), (5, 6))
    
    def test_number_of_modules_remaining(self):
        """Should return correct module count"""
        self.assertEqual(self.cell.number_of_modules_remaining(), 3)
    
    def test_collapse_to(self):
        """Should collapse cell to single module"""
        module = self.modules[0]
        self.cell.collapse_to(module)
        
        self.assertTrue(self.cell.is_collapsed)
        self.assertEqual(len(self.cell.possible_modules), 1)
        self.assertEqual(self.cell.possible_modules[0], module)
    
    def test_get_collapsed_module(self):
        """Should return collapsed module"""
        module = self.modules[0]
        self.cell.collapse_to(module)
        
        collapsed = self.cell.get_collapsed_module()
        self.assertEqual(collapsed, module)
    
    def test_get_collapsed_module_not_collapsed(self):
        """Should return None if not collapsed"""
        collapsed = self.cell.get_collapsed_module()
        self.assertIsNone(collapsed)
    
    def test_remove_modules(self):
        """Should remove invalid modules"""
        to_remove = [self.modules[0], self.modules[2]]
        removed_count = self.cell.remove_modules(to_remove)
        
        self.assertEqual(removed_count, 2)
        self.assertEqual(len(self.cell.possible_modules), 1)
        self.assertEqual(self.cell.possible_modules[0], self.modules[1])


class TestGrid(unittest.TestCase):
    """Test Grid class"""
    
    def setUp(self):
        """Create test grid and cells"""
        self.grid = Grid(3, 3)
        self.modules = [
            AlgorithmModule('A', 1.0, 'ROAD', 'ROAD', 'ROAD', 'ROAD'),
            AlgorithmModule('B', 1.0, 'BUILDING', 'BUILDING', 'BUILDING', 'BUILDING'),
        ]
    
    def test_grid_initialization(self):
        """Grid should initialize empty"""
        self.assertEqual(self.grid.width, 3)
        self.assertEqual(self.grid.height, 3)
        self.assertEqual(self.grid.get_cell_count(), 0)
    
    def test_add_cell(self):
        """Should add cell to grid"""
        cell = AlgorithmCell(0, 0, self.modules)
        self.grid.add_cell(cell)
        
        self.assertEqual(self.grid.get_cell_count(), 1)
        self.assertEqual(self.grid.get_uncollapsed_count(), 1)
    
    def test_get_cell(self):
        """Should retrieve cell by coordinates"""
        cell = AlgorithmCell(1, 2, self.modules)
        self.grid.add_cell(cell)
        
        retrieved = self.grid.get_cell(1, 2)
        self.assertEqual(retrieved, cell)
    
    def test_get_cell_not_found(self):
        """Should return None for non-existent cell"""
        retrieved = self.grid.get_cell(5, 5)
        self.assertIsNone(retrieved)
    
    def test_has_cell(self):
        """Should check cell existence"""
        cell = AlgorithmCell(1, 2, self.modules)
        self.grid.add_cell(cell)
        
        self.assertTrue(self.grid.has_cell(1, 2))
        self.assertFalse(self.grid.has_cell(5, 5))
    
    def test_mark_cell_collapsed(self):
        """Should remove cell from uncollapsed set"""
        cell = AlgorithmCell(0, 0, self.modules)
        self.grid.add_cell(cell)
        
        self.assertEqual(self.grid.get_uncollapsed_count(), 1)
        
        cell.collapse_to(self.modules[0])
        self.grid.mark_cell_collapsed(cell)
        
        self.assertEqual(self.grid.get_uncollapsed_count(), 0)
        self.assertEqual(self.grid.get_cell_count(), 1)  # Still in grid
    
    def test_is_complete(self):
        """Should check if all cells collapsed"""
        cell1 = AlgorithmCell(0, 0, self.modules)
        cell2 = AlgorithmCell(0, 1, self.modules)
        self.grid.add_cell(cell1)
        self.grid.add_cell(cell2)
        
        self.assertFalse(self.grid.is_complete())
        
        cell1.collapse_to(self.modules[0])
        self.grid.mark_cell_collapsed(cell1)
        self.assertFalse(self.grid.is_complete())
        
        cell2.collapse_to(self.modules[1])
        self.grid.mark_cell_collapsed(cell2)
        self.assertTrue(self.grid.is_complete())


if __name__ == '__main__':
    unittest.main()

