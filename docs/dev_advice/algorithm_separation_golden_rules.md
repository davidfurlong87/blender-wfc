# Algorithm Separation Guide

## The Golden Rule

**When in doubt, always remember: Algorithm logic should work without Blender. If you can't test it in a plain Python script, it's too coupled.**

## Why Separate Algorithm from UI?

### Current Problem

Your WFC algorithm is tightly coupled to Blender:

```python
# Algorithm logic mixed with Blender code
def collapse_cell(cell):
    # Pure algorithm logic ✅
    scored_modules = [(build_module_score(module.module_weight), module) 
                      for module in cell.possibleModules]
    module_to_return = max(scored_modules, key=lambda x: x[0])
    cell.possibleModules = [module_to_return[1]]
    cell.isCollapsed = True
    
    # Blender-specific code ❌ (mixed in!)
    module_obj = module_to_return[1].obj_source  # Blender object
    placement_location = (cell.posX * (module_size), cell.posY * (module_size), 0)
    collapsed_cell_obj = duplicate_and_move_and_return(module_obj, placement_location)
    cell.replace_mesh_obj(new_obj=collapsed_cell_obj)
    link_object_to_single_collection(collapsed_cell_obj, get_collection_by_name(...))
```

**Problems:**
- Can't test algorithm without Blender running
- Can't reuse algorithm in other contexts (CLI tool, web service, etc.)
- Hard to profile algorithm performance (Blender overhead mixed in)
- Difficult to debug (Blender state affects algorithm)
- Can't easily swap visualization (Godot, Unity, web canvas, etc.)

### Benefits of Separation

✅ **Testability** - Test algorithm with simple Python unit tests  
✅ **Reusability** - Use algorithm in CLI tools, web services, other engines  
✅ **Performance** - Profile pure algorithm without Blender overhead  
✅ **Debugging** - Debug algorithm logic without 3D viewport  
✅ **Flexibility** - Swap visualization layer (Blender, Godot, web, etc.)  
✅ **Maintainability** - Clear boundaries between algorithm and presentation  

---

## The Separation Pattern

### Layer 1: Pure Algorithm (No Blender)

**Location:** `wfc_algorithm/` (new module)

**Responsibilities:**
- WFC algorithm logic
- Constraint propagation
- Entropy calculation
- Module selection
- Grid state management

**Rules:**
- ❌ No `import bpy`
- ❌ No Blender objects
- ❌ No mesh operations
- ✅ Pure Python data structures
- ✅ Can run in plain Python script
- ✅ 100% unit testable

**Example:**
```python
# wfc_algorithm/core.py
class WFCAlgorithm:
    def __init__(self, modules, grid_size):
        self.modules = modules  # List of module IDs
        self.grid = Grid(grid_size)
        
    def collapse_cell(self, x, y):
        """Pure algorithm - no Blender code"""
        cell = self.grid.get_cell(x, y)
        selected_module = self._select_module(cell.possible_modules)
        cell.collapse_to(selected_module)
        return selected_module  # Just return the ID
    
    def propagate(self, x, y):
        """Pure constraint propagation"""
        affected = [(x, y)]
        while affected:
            cx, cy = affected.pop(0)
            for neighbor in self.grid.get_neighbors(cx, cy):
                if self._constrain_neighbor(neighbor, cx, cy):
                    affected.append((neighbor.x, neighbor.y))
```

### Layer 2: Blender Adapter (Thin Wrapper)

**Location:** `wfc_blender_adapter.py` (new module)

**Responsibilities:**
- Convert Blender objects to algorithm data
- Convert algorithm results to Blender objects
- Handle visualization
- Manage Blender collections

**Rules:**
- ✅ Can `import bpy`
- ✅ Can import algorithm layer
- ❌ No algorithm logic here
- ✅ Just translation/visualization

**Example:**
```python
# wfc_blender_adapter.py
import bpy
from .wfc_algorithm.core import WFCAlgorithm

class BlenderWFCAdapter:
    def __init__(self):
        self.algorithm = None
        self.module_objects = {}  # Map module_id -> bpy.types.Object
        
    def setup_from_blender_modules(self, blender_modules):
        """Convert Blender modules to algorithm data"""
        module_data = []
        for bpy_module in blender_modules:
            module_id = bpy_module.name
            module_data.append({
                'id': module_id,
                'weight': bpy_module.get('weight', 1.0),
                'connectors': self._extract_connectors(bpy_module)
            })
            self.module_objects[module_id] = bpy_module
        
        self.algorithm = WFCAlgorithm(module_data, grid_size=(10, 10))
    
    def collapse_and_visualize(self, x, y):
        """Run algorithm, then visualize result"""
        # Algorithm layer (pure)
        selected_module_id = self.algorithm.collapse_cell(x, y)
        
        # Visualization layer (Blender)
        self._create_blender_object(x, y, selected_module_id)
    
    def _create_blender_object(self, x, y, module_id):
        """Blender-specific visualization"""
        source_obj = self.module_objects[module_id]
        location = (x * 8, y * 8, 0)
        duplicate = duplicate_and_move_and_return(source_obj, location)
        # ... Blender-specific code ...
```

### Layer 3: Blender Operators (UI)

**Location:** `wfc_operators.py` (existing)

**Responsibilities:**
- User interaction
- Button clicks
- UI feedback
- Progress reporting

**Rules:**
- ✅ Calls adapter layer
- ❌ No algorithm logic
- ❌ No direct algorithm access

**Example:**
```python
# wfc_operators.py
class OBJECT_OT_FullCollapse(bpy.types.Operator):
    bl_idname = "object.full_collapse"
    bl_label = "Full Collapse"
    
    def execute(self, context):
        adapter = get_wfc_adapter()  # Get singleton
        
        # Just call adapter - no algorithm logic here
        adapter.collapse_all()
        
        self.report({'INFO'}, "Collapse complete")
        return {'FINISHED'}
```

---

## Current State Analysis

### What's Already Separated ✅

**Pure Data Classes:**
- `WFCModule` - mostly pure (except `obj_source`)
- `WFCCell` - mostly pure (except `mesh_obj`)
- `Primitive` - pure data ✅
- `Axis` enum - pure ✅

**Pure Algorithm Functions:**
- `get_lowest_entropy_cells()` - pure ✅
- `build_module_score()` - pure ✅
- `build_module_pairs()` - pure ✅

### What's Mixed ❌

**Algorithm + Blender Mixed:**
- `collapse_cell()` - algorithm logic + mesh creation
- `propagate()` - algorithm logic + mesh updates
- `collapse_process()` - algorithm loop + Blender state
- `WFCCell.remove_invalid_modules()` - updates `mesh_obj.remaining_modules`
- `WFCCell.replace_mesh_obj()` - calls Blender delete function

**Blender-Dependent Data:**
- `WFCModule.obj_source` - stores Blender object
- `WFCCell.mesh_obj` - stores Blender object

---

## Migration Strategy

### Phase 1: Extract Pure Algorithm (Low Risk)

**Goal:** Create pure algorithm layer without breaking existing code

**Steps:**
1. Create `wfc_algorithm/` module
2. Copy algorithm functions to new module
3. Remove Blender dependencies from copies
4. Write unit tests for pure algorithm
5. Keep existing code working (don't break anything yet)

**Files to create:**
- `wfc_algorithm/__init__.py`
- `wfc_algorithm/core.py` - Main WFC algorithm
- `wfc_algorithm/grid.py` - Grid data structure
- `wfc_algorithm/cell.py` - Pure cell class
- `wfc_algorithm/module.py` - Pure module class
- `wfc_algorithm/tests/` - Unit tests

### Phase 2: Create Adapter Layer (Medium Risk)

**Goal:** Create Blender adapter that uses pure algorithm

**Steps:**
1. Create `wfc_blender_adapter.py`
2. Implement conversion functions (Blender ↔ Algorithm)
3. Implement visualization functions
4. Test adapter with simple cases

**Files to create:**
- `wfc_blender_adapter.py`

### Phase 3: Migrate Operators (Medium Risk)

**Goal:** Update operators to use adapter instead of mixed code

**Steps:**
1. Update one operator at a time
2. Test each operator after migration
3. Keep old code commented out until verified

**Files to modify:**
- `__init__.py` - Update operators

### Phase 4: Clean Up (Low Risk)

**Goal:** Remove old mixed code

**Steps:**
1. Remove old algorithm functions from `__init__.py`
2. Update `WFCCell` and `WFCModule` to be pure
3. Remove global state (`all_grid_cells`, etc.)
4. Update documentation

---

## Example: Separating `collapse_cell()`

### Before (Mixed)

```python
# In __init__.py
def collapse_cell(cell):
    # Algorithm logic
    scored_modules = [(build_module_score(module.module_weight), module) 
                      for module in cell.possibleModules]
    module_to_return = scored_modules[0]
    for scored_module in scored_modules:
        if scored_module[0] > module_to_return[0]:
            module_to_return = scored_module
    cell.possibleModules = [module_to_return[1]]
    cell.isCollapsed = True
    
    # Blender code
    module_obj = module_to_return[1].obj_source
    placement_location = (cell.posX * (module_size), cell.posY * (module_size), 0)
    collapsed_cell_obj = duplicate_and_move_and_return(module_obj, placement_location)
    collapsed_cell_obj.name = f"{cell.posX:02d}_{cell.posY:02d}-{module_obj.name}"
    cell.replace_mesh_obj(new_obj=collapsed_cell_obj)
    link_object_to_single_collection(collapsed_cell_obj, get_collection_by_name(...))
```

### After (Separated)

```python
# wfc_algorithm/core.py (Pure algorithm)
class WFCAlgorithm:
    def collapse_cell(self, x, y):
        """Pure algorithm - returns selected module ID"""
        cell = self.grid.get_cell(x, y)
        
        # Score all possible modules
        scored = [(self._score_module(m), m) for m in cell.possible_modules]
        selected = max(scored, key=lambda x: x[0])[1]
        
        # Update cell state
        cell.collapse_to(selected)
        
        return selected  # Just return the ID
    
    def _score_module(self, module):
        return module.weight * random.randint(1, 10001)

# wfc_blender_adapter.py (Blender visualization)
class BlenderWFCAdapter:
    def collapse_cell_and_visualize(self, x, y):
        """Run algorithm + create Blender object"""
        # Algorithm (pure)
        selected_module_id = self.algorithm.collapse_cell(x, y)
        
        # Visualization (Blender)
        self._visualize_collapsed_cell(x, y, selected_module_id)
    
    def _visualize_collapsed_cell(self, x, y, module_id):
        """Create Blender object for collapsed cell"""
        source_obj = self.module_objects[module_id]
        location = (x * module_size, y * module_size, 0)
        
        duplicate = duplicate_and_move_and_return(source_obj, location)
        duplicate.name = f"{x:02d}_{y:02d}-{module_id}"
        
        link_object_to_single_collection(duplicate, self.grid_collection)
```

---

## Testing Strategy

### Pure Algorithm Tests (Easy!)

```python
# wfc_algorithm/tests/test_collapse.py
import unittest
from wfc_algorithm.core import WFCAlgorithm

class TestCollapse(unittest.TestCase):
    def test_collapse_reduces_entropy(self):
        """Test that collapsing a cell reduces its entropy to 1"""
        algo = WFCAlgorithm(modules=['A', 'B', 'C'], grid_size=(3, 3))
        
        # Before collapse
        cell = algo.grid.get_cell(0, 0)
        self.assertEqual(len(cell.possible_modules), 3)
        
        # Collapse
        selected = algo.collapse_cell(0, 0)
        
        # After collapse
        self.assertEqual(len(cell.possible_modules), 1)
        self.assertEqual(cell.possible_modules[0], selected)
        self.assertTrue(cell.is_collapsed)
    
    def test_propagation_constrains_neighbors(self):
        """Test that propagation removes invalid modules from neighbors"""
        # ... test without any Blender code!
```

### Adapter Tests (Requires Blender)

```python
# tests/test_blender_adapter.py
import bpy
from wfc_blender_adapter import BlenderWFCAdapter

def test_adapter_creates_objects():
    """Test that adapter creates Blender objects correctly"""
    adapter = BlenderWFCAdapter()
    adapter.setup_from_blender_modules(bpy.data.collections['Modules'].objects)
    
    adapter.collapse_cell_and_visualize(0, 0)
    
    # Verify Blender object was created
    assert bpy.data.objects.get('00_00-Module_1_0') is not None
```

---

## Common Pitfalls

### ❌ Pitfall 1: Storing Blender objects in algorithm classes

```python
# WRONG - Algorithm class stores Blender object
class WFCModule:
    def __init__(self, name, obj_source):  # ❌ Blender object
        self.name = name
        self.obj_source = obj_source  # ❌ Can't test without Blender

# RIGHT - Algorithm class stores only data
class WFCModule:
    def __init__(self, module_id, weight, connectors):
        self.id = module_id  # ✅ Just a string
        self.weight = weight  # ✅ Just a number
        self.connectors = connectors  # ✅ Just data
```

### ❌ Pitfall 2: Mixing algorithm and visualization in one function

```python
# WRONG - Mixed responsibilities
def collapse_cell(cell):
    selected = select_module(cell)  # Algorithm
    create_mesh(selected)  # Visualization
    # Can't test algorithm without creating meshes!

# RIGHT - Separated responsibilities
def collapse_cell(cell):  # Pure algorithm
    return select_module(cell)

def visualize_cell(cell, module_id):  # Separate visualization
    create_mesh(module_id)
```

### ❌ Pitfall 3: Global Blender state in algorithm

```python
# WRONG - Algorithm depends on Blender global state
def propagate(cell):
    collection = bpy.data.collections['Grid']  # ❌ Blender dependency
    # ... algorithm logic ...

# RIGHT - Algorithm uses its own state
def propagate(self, cell):
    # Uses self.grid, not Blender collections
    # ... algorithm logic ...
```

---
<!-- TODO: COPY-PASTED from an older file. Merge with stuff above -->
# Quick Start: Separating Algorithm from Blender

## The Simple Rule

**When in doubt: If it doesn't need `import bpy`, it shouldn't have `import bpy`.**

## 5-Step Migration Process

### Step 1: Identify What to Separate

**Ask yourself:**
- Does this function do WFC algorithm logic? → Separate it
- Does this function create/modify Blender objects? → Keep it in adapter
- Does this class store algorithm state? → Separate it
- Does this class store Blender objects? → Split it

**Quick Test:**
```python
# Can you test this function without Blender running?
# YES → Should be in algorithm layer
# NO → Should be in adapter layer
```

### Step 2: Create Pure Algorithm Module

**Create the structure:**

```
addons/blender-wfc/
├── wfc_algorithm/          # NEW - Pure algorithm
│   ├── __init__.py
│   ├── core.py            # Main WFC algorithm
│   ├── grid.py            # Grid data structure
│   ├── cell.py            # Pure cell class
│   ├── module.py          # Pure module class
│   └── tests/             # Unit tests
│       ├── __init__.py
│       ├── test_core.py
│       └── test_grid.py
├── wfc_blender_adapter.py  # NEW - Blender adapter
├── __init__.py             # MODIFY - Use adapter
└── ... (existing files)
```

**Start with the simplest pure function:**

```python
# wfc_algorithm/core.py
import random

def score_module(module_weight):
    """Pure function - no Blender dependencies"""
    return module_weight * random.randint(1, 10001)

def select_highest_scored(modules):
    """Pure function - selects module with highest score"""
    scored = [(score_module(m.weight), m) for m in modules]
    return max(scored, key=lambda x: x[0])[1]
```

### Step 3: Create Pure Data Classes

**Extract data from Blender-dependent classes:**

```python
# wfc_algorithm/module.py
class AlgorithmModule:
    """Pure module - no Blender objects"""
    def __init__(self, module_id, weight, connectors):
        self.id = module_id
        self.weight = weight
        self.pos_x = connectors['pos_x']
        self.neg_x = connectors['neg_x']
        self.pos_y = connectors['pos_y']
        self.neg_y = connectors['neg_y']
        self.pos_x_pairs = []
        self.neg_x_pairs = []
        self.pos_y_pairs = []
        self.neg_y_pairs = []

# wfc_algorithm/cell.py
class AlgorithmCell:
    """Pure cell - no Blender objects"""
    def __init__(self, x, y, possible_modules):
        self.x = x
        self.y = y
        self.possible_modules = possible_modules[:]
        self.is_collapsed = False
    
    def collapse_to(self, module):
        """Pure algorithm - just update state"""
        self.possible_modules = [module]
        self.is_collapsed = True
    
    def remove_modules(self, invalid_modules):
        """Pure algorithm - just update list"""
        for module in invalid_modules:
            self.possible_modules.remove(module)
```

### Step 4: Create Blender Adapter

**Translate between Blender and algorithm:**

```python
# wfc_blender_adapter.py
import bpy
from .wfc_algorithm.core import WFCAlgorithm
from .wfc_algorithm.module import AlgorithmModule
from .collectiontools.collection_creation import *

class BlenderWFCAdapter:
    """Adapter between Blender and pure WFC algorithm"""
    
    def __init__(self):
        self.algorithm = None
        self.module_map = {}  # algorithm_id -> blender_object
        self.cell_objects = {}  # (x, y) -> blender_object
    
    def setup_from_blender(self, blender_modules, grid_size):
        """Convert Blender modules to algorithm data"""
        algorithm_modules = []
        
        for bpy_module in blender_modules:
            # Extract pure data from Blender object
            algo_module = AlgorithmModule(
                module_id=bpy_module.name,
                weight=bpy_module.get('weight', 1.0),
                connectors={
                    'pos_x': bpy_module.x_pos_connector,
                    'neg_x': bpy_module.x_neg_connector,
                    'pos_y': bpy_module.y_pos_connector,
                    'neg_y': bpy_module.y_neg_connector
                }
            )
            algorithm_modules.append(algo_module)
            
            # Store mapping for visualization
            self.module_map[bpy_module.name] = bpy_module
        
        # Create pure algorithm
        self.algorithm = WFCAlgorithm(algorithm_modules, grid_size)
    
    def collapse_cell(self, x, y):
        """Run algorithm and visualize result"""
        # Pure algorithm (no Blender)
        selected_module = self.algorithm.collapse_cell(x, y)
        
        # Visualization (Blender)
        self._create_cell_object(x, y, selected_module.id)
        
        return selected_module
    
    def _create_cell_object(self, x, y, module_id):
        """Blender-specific visualization"""
        source_obj = self.module_map[module_id]
        location = (x * 8, y * 8, 0)
        
        duplicate = duplicate_and_move_and_return(source_obj, location)
        duplicate.name = f"{x:02d}_{y:02d}-{module_id}"
        
        self.cell_objects[(x, y)] = duplicate
        
        # Link to collection
        grid_collection = get_collection_by_name("WFC_Grid")
        link_object_to_single_collection(duplicate, grid_collection)
```

### Step 5: Update Operators to Use Adapter

**Modify operators to use adapter instead of mixed code:**

```python
# __init__.py

# Create global adapter instance
_wfc_adapter = None

def get_wfc_adapter():
    """Get or create the WFC adapter singleton"""
    global _wfc_adapter
    if _wfc_adapter is None:
        _wfc_adapter = BlenderWFCAdapter()
    return _wfc_adapter

class OBJECT_OT_FullCollapse(bpy.types.Operator):
    bl_idname = "object.full_collapse"
    bl_label = "Full Collapse"
    
    def execute(self, context):
        adapter = get_wfc_adapter()
        
        # Setup if not already done
        if adapter.algorithm is None:
            modules = get_all_objects_from_collection("WFC_Modules")
            adapter.setup_from_blender(modules, grid_size=(10, 10))
        
        # Run collapse (algorithm + visualization)
        adapter.collapse_all()
        
        self.report({'INFO'}, "Collapse complete")
        return {'FINISHED'}
```

---

## Migration Checklist

For each function/class you're migrating:

### Algorithm Functions
- [ ] Remove all `import bpy` statements
- [ ] Remove all Blender object references
- [ ] Remove all mesh operations
- [ ] Remove all collection operations
- [ ] Use pure Python data structures only
- [ ] Write unit test (without Blender)
- [ ] Verify test passes

### Data Classes
- [ ] Remove `obj_source` / `mesh_obj` attributes
- [ ] Store only IDs/names instead of Blender objects
- [ ] Remove methods that call Blender functions
- [ ] Keep only pure data and algorithm logic
- [ ] Write unit test
- [ ] Verify test passes

### Adapter Functions
- [ ] Create conversion function (Blender → Algorithm)
- [ ] Create conversion function (Algorithm → Blender)
- [ ] Create visualization function
- [ ] Test with simple case
- [ ] Verify Blender objects created correctly

### Operators
- [ ] Get adapter instance
- [ ] Call adapter methods (not algorithm directly)
- [ ] Handle UI feedback
- [ ] Test in Blender
- [ ] Verify functionality unchanged

---

## Common Scenarios

### Scenario 1: Function uses Blender objects

**Before:**
```python
def collapse_cell(cell):
    # ... algorithm logic ...
    module_obj = module.obj_source  # ❌ Blender object
    duplicate = duplicate_and_move_and_return(module_obj, location)
```

**After:**
```python
# Algorithm layer
def collapse_cell(self, x, y):
    # ... algorithm logic ...
    return selected_module  # ✅ Just return data

# Adapter layer
def collapse_cell_and_visualize(self, x, y):
    selected = self.algorithm.collapse_cell(x, y)
    self._create_object(x, y, selected.id)  # Blender code here
```

### Scenario 2: Class stores Blender objects

**Before:**
```python
class WFCModule:
    def __init__(self, name, obj_source):  # ❌ Blender object
        self.name = name
        self.obj_source = obj_source
```

**After:**
```python
# Algorithm layer
class AlgorithmModule:
    def __init__(self, module_id, weight):  # ✅ Pure data
        self.id = module_id
        self.weight = weight

# Adapter layer
class BlenderWFCAdapter:
    def __init__(self):
        self.module_map = {}  # id -> bpy.types.Object
```

### Scenario 3: Global state

**Before:**
```python
all_grid_cells = {}  # ❌ Global state

def propagate(cell):
    for key in all_grid_cells.keys():  # ❌ Uses global
        # ...
```

**After:**
```python
# Algorithm layer
class WFCAlgorithm:
    def __init__(self):
        self.grid = Grid()  # ✅ Instance state
    
    def propagate(self, x, y):
        for cell in self.grid.get_all_cells():  # ✅ Uses instance
            # ...

# Adapter layer
class BlenderWFCAdapter:
    def __init__(self):
        self.algorithm = WFCAlgorithm()  # ✅ Owns algorithm instance
```

---

## Testing Your Separation

### Test 1: Can you import the algorithm module?

```python
# In a plain Python script (no Blender)
from wfc_algorithm.core import WFCAlgorithm

# If this works, you've separated successfully!
algo = WFCAlgorithm(modules=[], grid_size=(10, 10))
```

### Test 2: Can you run algorithm tests without Blender?

```bash
# From command line (no Blender)
cd addons/blender-wfc
python -m pytest wfc_algorithm/tests/

# If tests run, you've separated successfully!
```

### Test 3: Does the Blender addon still work?

```python
# In Blender
# Click "Full Collapse" button
# If it works, you've maintained functionality!
```

---

## Troubleshooting

### Problem: "ImportError: cannot import name 'bpy'"

**Cause:** Algorithm module is trying to import bpy

**Solution:** Remove all `import bpy` from algorithm modules

### Problem: "Algorithm tests fail with 'module has no attribute obj_source'"

**Cause:** Algorithm code still references Blender objects

**Solution:** Replace Blender object references with IDs/data

### Problem: "Blender addon doesn't work after migration"

**Cause:** Adapter not properly converting between layers

**Solution:** Check adapter conversion functions, verify mappings

### Problem: "Can't test algorithm without Blender"

**Cause:** Algorithm still has Blender dependencies

**Solution:** Review algorithm code, remove all Blender imports/objects

---

## Success Criteria

You've successfully separated when:

✅ Algorithm module has zero `import bpy` statements  
✅ Algorithm tests run without Blender  
✅ Algorithm classes store no Blender objects  
✅ Adapter handles all Blender interaction  
✅ Operators use adapter, not algorithm directly  
✅ Blender addon functionality unchanged  

---

## Next Steps

1. Start with simplest function (`score_module`)
2. Write test for it
3. Move to next function
4. Repeat until all algorithm code is separated
5. Create adapter
6. Update operators
7. Test everything
8. Remove old code

See `docs/architecture/ALGORITHM_SEPARATION_GUIDE.md` for detailed explanation.



