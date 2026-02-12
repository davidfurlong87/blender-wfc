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

## Next Steps

See `docs/architecture/QUICK_START_SEPARATION.md` for step-by-step migration guide.

