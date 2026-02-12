# Pure WFC Algorithm Module

**Status:** ✅ Phase 1 Complete - Pure algorithm layer extracted

This module contains the Wave Function Collapse algorithm implementation with **NO Blender dependencies**. All code here is testable without running Blender.

## The Golden Rule

> **"Algorithm logic should work without Blender. If you can't test it in a plain Python script, it's too coupled."**

## Module Structure

```
wfc_algorithm/
├── __init__.py          # Public API exports
├── core.py              # Main WFC algorithm (WFCAlgorithm class)
├── grid.py              # Grid data structure
├── cell.py              # Pure cell class (no Blender objects)
├── module.py            # Pure module class (no Blender objects)
├── enums.py             # Axis enum
├── README.md            # This file
└── tests/               # Unit tests (run without Blender)
    ├── __init__.py
    ├── test_core.py
    └── test_data_classes.py
```

## Key Classes

### `WFCAlgorithm`
Main algorithm class that encapsulates the WFC logic.

**Methods:**
- `collapse_cell(cell)` - Collapse a cell to a single module
- `propagate(collapsed_cell)` - Propagate constraints to neighbors
- `collapse_all()` - Collapse all cells in the grid

### `Grid`
Grid data structure that replaces global variables.

**Methods:**
- `add_cell(cell)` - Add a cell to the grid
- `get_cell(x, y)` - Get cell at coordinates
- `get_uncollapsed_cells()` - Get all uncollapsed cells
- `mark_cell_collapsed(cell)` - Mark cell as collapsed

### `AlgorithmCell`
Pure cell class without Blender objects.

**Attributes:**
- `x, y` - Grid coordinates
- `possible_modules` - List of possible modules
- `is_collapsed` - Collapse state

**Methods:**
- `collapse_to(module)` - Collapse to single module
- `remove_modules(invalid_modules)` - Remove invalid modules
- `get_neighbor_coords(axis)` - Get neighbor coordinates

### `AlgorithmModule`
Pure module class without Blender objects.

**Attributes:**
- `id` - Module identifier (used to reference Blender object in adapter)
- `weight` - Module weight for selection
- `pos_x, neg_x, pos_y, neg_y` - Connector types
- `pos_x_pairs, neg_x_pairs, pos_y_pairs, neg_y_pairs` - Compatible modules

**Methods:**
- `get_all_pairs_for_axis(axis)` - Get compatible modules for axis
- `add_compatible_module(axis, module)` - Add compatible module

## Pure Functions

### `score_module(module_weight)`
Calculate weighted random score for module selection.

### `select_highest_scored_module(modules)`
Select module with highest weighted random score.

### `get_lowest_entropy_cells(uncollapsed_cells)`
Get cells with lowest entropy (fewest possible modules).

## Running Tests

Tests run **without Blender** using Python's built-in unittest:

```bash
cd addons/blender-wfc
python -m unittest discover -s wfc_algorithm/tests -p "test_*.py" -v
```

**Test Results:**
- ✅ 33 tests pass
- ✅ All tests run without Blender
- ✅ 100% pure Python

## What Changed from Original Code

### Extracted from `__init__.py`
- `build_module_score()` → `score_module()`
- `get_lowest_entropy_cells()` → `get_lowest_entropy_cells()` (unchanged)
- `collapse_cell()` → `WFCAlgorithm.collapse_cell()` (removed Blender visualization)
- `propagate()` → `WFCAlgorithm.propagate()` (removed Blender updates)
- `collapse_process()` → `WFCAlgorithm.collapse_all()` (removed Blender code)

### Extracted from `wfc_classes.py`
- `WFCModule` → `AlgorithmModule` (removed `obj_source` attribute)
- `WFCCell` → `AlgorithmCell` (removed `mesh_obj` attribute)
- `Axis` enum → `Axis` enum (unchanged)

### New Classes
- `Grid` - Encapsulates grid state (replaces global variables)
- `WFCAlgorithm` - Encapsulates algorithm logic

## What's NOT in This Module

❌ No `import bpy`  
❌ No Blender objects (`bpy.types.Object`, `bpy.types.Mesh`)  
❌ No mesh operations  
❌ No collection operations  
❌ No visualization code  

All Blender-specific code belongs in the **adapter layer** (Phase 2).

## Next Steps (Phase 2)

Create `wfc_blender_adapter.py` that:
1. Converts Blender modules → AlgorithmModules
2. Creates Grid from Blender scene
3. Calls pure algorithm
4. Visualizes results in Blender

See `docs/architecture/ALGORITHM_SEPARATION_GUIDE.md` for details.

## Benefits

✅ **Testable** - Can test algorithm without Blender  
✅ **Reusable** - Can use algorithm in CLI tools, other engines  
✅ **Debuggable** - Can debug pure Python without Blender overhead  
✅ **Fast** - Tests run in milliseconds  
✅ **Maintainable** - Clear separation of concerns  

