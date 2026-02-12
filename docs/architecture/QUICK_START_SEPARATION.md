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

