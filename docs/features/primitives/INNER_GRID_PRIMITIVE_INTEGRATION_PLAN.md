# Inner Grid Primitive Integration Plan

**Goal:** Enable creating, persisting, and using primitives for the inner grid building system as seamlessly as the current hardcoded outer grid primitives.

**Date:** 2026-04-08  
**Status:** 📋 Planning Phase

---

## 🎯 Objective

**Current State:**
- ✅ Outer grid primitives: Hardcoded in `primitive_data_actual.py`
- ✅ Outer grid workflow: `Build Primitives` → `Build Modules` → `Build Grid` → `Collapse`
- ✅ Inner grid system: Exists but uses **hardcoded building primitives**
- ❌ Inner grid primitives: **Cannot persist or manage separately**

**Desired State:**
- ✅ Inner grid primitives: Persisted to JSON, loadable like outer grid primitives
- ✅ Primitive resolution metadata: Each primitive knows its grid resolution (e.g., 2x2, 4x4, 8x8)
- ✅ Seamless workflow: Create → Persist → Load → Use in inner/outer grids
- ✅ Primitive categories: "outer_grid" vs "inner_grid" (building, road, park, etc.)

---

## 🔍 Current System Analysis

### **How Outer Grid Currently Works**

**Step 1: Primitives → Modules**
```python
# __init__.py lines 210-253
def generate_modules():
    for primitive in get_all_primitives():  # From Primitives collection
        # Create 4 rotations
        for rotation in range(4):
            module = create_rotated_module(primitive)
            module.x_pos_connector = ...
            all_modules.append(WFCModule(...))
```

**Step 2: Modules → Grid → Collapse**
```python
# BlenderWFCAdapter
adapter.setup_from_blender_modules(all_modules)
adapter.create_grid_from_blender(modules, width, height)
adapter.collapse_grid()
```

### **How Inner Grid Currently Works**

**Step 1: Extract Building Plots from Collapsed Outer Grid**
```python
# BlenderWFCAdapter lines 464-535
plots = adapter.extract_plots_from_grid(plot_type='building_plot', 
                                        vertex_group_name='building_plot')
```

**Step 2: Group Plots into Islands**
```python
islands = adapter.group_plot_islands(plots, plot_type='building')
```

**Step 3: Create Inner Grid for Island**
```python
# BlenderWFCAdapter lines 782-839
inner_grid = adapter.create_inner_grid_for_island(
    island,
    resolution_multiplier=4,  # 4x4 inner grid per outer cell
    inner_modules=None  # ← PROBLEM: No primitive/module system yet!
)
```

**PROBLEM:** Inner grid has no primitive/module system! Currently hardcoded or missing.

---

## 🧩 Missing Pieces

### **1. Primitive Resolution Metadata** ❌

**Problem:** Primitives don't know what grid resolution they're designed for.

**Example:**
- Outer grid primitive: 8x8m, resolution = 1 (one cell)
- Inner grid primitive: 2x2m, resolution = 4 (for 4x4 inner grid)
- Park grid primitive: 1x1m, resolution = 8 (for 8x8 finer grid)

**Required:**
```python
@dataclass
class PrimitiveData:
    name: str
    primitive_type: str
    grid_resolution: int = 1  # ← NEW: Default 1 for outer grid
    grid_category: str = "outer_grid"  # ← NEW: "outer_grid", "building", "park", etc.
    # ... existing fields
```

### **2. Primitive Loading by Category** ❌

**Problem:** No way to load "building primitives" separately from "outer grid primitives".

**Required:**
```python
# Load all outer grid primitives
outer_primitives = load_primitives_by_category("outer_grid")

# Load all building primitives for inner grids
building_primitives = load_primitives_by_category("building")

# Load all park primitives
park_primitives = load_primitives_by_category("park")
```

### **3. Module Generation from Inner Grid Primitives** ❌

**Problem:** `generate_modules()` is hardcoded for outer grid only.

**Required:**
```python
# Generate outer grid modules (existing)
outer_modules = generate_modules_from_primitives(outer_primitives, module_size=8)

# Generate inner grid modules (NEW)
building_modules = generate_modules_from_primitives(building_primitives, module_size=2)
```

### **4. Inner Grid Module Storage/Management** ❌

**Problem:** No global storage for building modules like `all_modules` for outer grid.

**Required:**
```python
# Global storage (like existing all_modules)
all_building_modules = []
all_park_modules = []

# Or better: categorized storage
primitive_modules = {
    "outer_grid": [],
    "building": [],
    "park": [],
    "road_detail": []
}
```

### **5. UI for Managing Primitive Categories** ❌

**Problem:** No UI to specify which grid a primitive is for.

**Required:**
- Dropdown in "Assign Type" to select grid category
- Filter in "Load" dialog to load by category
- Visual indicator of primitive category

---

## 📋 Implementation Plan

### **Phase A: Extend PrimitiveData Structure** (1-2 hours)

**Goal:** Add grid resolution and category metadata to primitives.

**Tasks:**
1. **Extend `PrimitiveData`** in `primitive_data_core.py`
   ```python
   @dataclass
   class PrimitiveData:
       # Existing fields...
       grid_resolution: int = 1  # How many cells this primitive spans
       grid_category: str = "outer_grid"  # Which grid system it belongs to
       cell_size: float = 8.0  # Physical size of one grid cell (meters)
   ```

2. **Update Validation**
   - Validate `grid_resolution >= 1`
   - Validate `grid_category` is in allowed list
   - Validate `cell_size > 0`

3. **Update Serialization**
   - Add fields to `to_dict()` and `from_dict()`
   - Maintain backward compatibility (default values)

4. **Update Tests**
   - Test new fields serialize correctly
   - Test validation catches invalid values

**Files Modified:**
- `addons/blender-wfc/primitive_data_core.py`
- `tests/test_primitive_data.py`

---

### **Phase B: Update UI for Grid Categories** (1-2 hours)

**Goal:** Allow users to specify grid category when creating primitives.

**Tasks:**
1. **Add Grid Category Property**
   ```python
   # In __init__.py register()
   bpy.types.Object.primitive_grid_category = EnumProperty(
       name="Grid Category",
       items=[
           ('outer_grid', "Outer Grid", "Main city grid primitives"),
           ('building', "Building", "Inner grid building primitives"),
           ('park', "Park", "Park detail primitives"),
           ('road_detail', "Road Detail", "Road detail primitives"),
       ]
   )
   ```

2. **Update `OBJECT_OT_WFCAssignConnectors`**
   - Add grid_resolution field (IntProperty, default=1)
   - Add grid_category field (EnumProperty)
   - Add cell_size field (FloatProperty, default=8.0)

3. **Update Panel Display**
   - Show grid category in primitive builder panel
   - Show resolution and cell size (read-only after assignment)

**Files Modified:**
- `addons/blender-wfc/__init__.py`
- `addons/blender-wfc/primitive_ui.py`

---

### **Phase C: Primitive Library Management** (2-3 hours)

**Goal:** Organize primitives by category, load by category.

**Tasks:**
1. **Extend `PrimitivePersistence`**
   ```python
   def save_primitives_library_by_category(
       self, 
       primitives: List[PrimitiveData], 
       category: str,
       filepath: str
   ):
       """Save all primitives of a category to a library file"""
       pass
   
   def load_primitives_by_category(
       self,
       category: str,
       filepath: str = None
   ) -> List[PrimitiveData]:
       """Load all primitives matching a category"""
       pass
   ```

2. **Create Default Library Structure**
   ```
   addons/blender-wfc/data/
   ├── primitives/
   │   ├── outer_grid_library.json
   │   ├── building_library.json
   │   ├── park_library.json
   │   └── road_detail_library.json
   ```

3. **Add Library Load Operators**
   - `OBJECT_OT_WFCLoadPrimitiveLibrary` - Load entire category library
   - Auto-create primitives in scene from library
   - Option to merge with existing or replace

**Files Modified:**
- `addons/blender-wfc/primitive_persistence.py`
- `addons/blender-wfc/primitive_ui.py`

**Files Created:**
- `addons/blender-wfc/data/` (directory)
- `addons/blender-wfc/data/building_library.json` (example)

---

### **Phase D: Module Generation System Refactoring** (3-4 hours)

**Goal:** Make module generation generic, support any primitive category.

**Tasks:**
1. **Create Generic Module Generator**
   ```python
   def generate_modules_from_primitives(
       primitives: List[bpy.types.Object],
       collection_name: str,
       module_size: float = 8.0,
       location_offset: Vector = Vector((0, 0, 0))
   ) -> List[WFCModule]:
       """
       Generate rotated modules from primitives (works for any category)

       Args:
           primitives: List of primitive objects
           collection_name: Collection to place modules in
           module_size: Physical size of modules (8.0 for outer, 2.0 for building)
           location_offset: Where to place module visualization

       Returns:
           List of WFCModule instances
       """
       modules = []
       for i, primitive in enumerate(primitives):
           for rotation in range(4):
               module = create_rotated_module(primitive, rotation, module_size)
               modules.append(module)
       return modules
   ```

2. **Refactor Existing `generate_modules()`**
   - Extract generic logic into `generate_modules_from_primitives()`
   - Keep `generate_modules()` as wrapper for backward compatibility
   - Use for outer grid only

3. **Create Inner Grid Module Generators**
   ```python
   def generate_building_modules():
       """Generate modules from building primitives"""
       building_prims = get_primitives_by_category("building")
       return generate_modules_from_primitives(
           building_prims,
           "Building_Modules",
           module_size=2.0
       )

   def generate_park_modules():
       """Generate modules from park primitives"""
       park_prims = get_primitives_by_category("park")
       return generate_modules_from_primitives(
           park_prims,
           "Park_Modules",
           module_size=1.0
       )
   ```

4. **Add Module Category Storage**
   ```python
   # Replace global all_modules with categorized storage
   all_modules = {
       "outer_grid": [],
       "building": [],
       "park": [],
       "road_detail": []
   }

   # Or keep backward compat:
   all_outer_modules = []  # existing
   all_building_modules = []  # NEW
   all_park_modules = []  # NEW
   ```

**Files Modified:**
- `addons/blender-wfc/__init__.py` (refactor generate_modules)
- `addons/blender-wfc/wfc_values.py` (add building_module_size constant)

**Files Created:**
- `addons/blender-wfc/module_generation.py` (optional: extract logic)

---

### **Phase E: Inner Grid Workflow Integration** (2-3 hours)

**Goal:** Connect inner grid system to use generated building modules.

**Tasks:**
1. **Update `BlenderWFCAdapter.create_inner_grid_for_island()`**
   ```python
   def create_inner_grid_for_island(
       self,
       island,
       resolution_multiplier=4,
       inner_modules=None,  # Can now pass building modules!
       category="building"  # Auto-load if modules not provided
   ):
       # If modules not provided, auto-load from category
       if inner_modules is None:
           inner_modules = self.get_modules_for_category(category)

       # Create grid with modules
       inner_grid = Grid(width=inner_width, height=inner_height)
       # ... populate with inner_modules
   ```

2. **Add Helper Method**
   ```python
   def get_modules_for_category(self, category: str) -> List[AlgorithmModule]:
       """
       Get algorithm modules for a specific category

       This bridges the gap between Blender modules and algorithm modules
       for different grid categories.
       """
       if category == "building":
           return self.setup_from_blender_modules(all_building_modules)
       elif category == "park":
           return self.setup_from_blender_modules(all_park_modules)
       # ...
   ```

3. **Update Building Plot Operator**
   ```python
   class OBJECT_OT_DebugBuildingPlots(bpy.types.Operator):
       def execute(self, context):
           # ... existing plot extraction code

           # NEW: Auto-generate building modules if needed
           if len(all_building_modules) == 0:
               building_prims = load_primitives_by_category("building")
               generate_building_modules()

           # NEW: Create and collapse inner grids
           for island in islands:
               inner_grid = adapter.create_inner_grid_for_island(
                   island,
                   resolution_multiplier=4,
                   category="building"  # Auto-loads building modules
               )
               adapter.collapse_inner_grid(inner_grid, island)
   ```

**Files Modified:**
- `addons/blender-wfc/wfc_blender_adapter.py`
- `addons/blender-wfc/wfc_operators.py` (update building plot operator)

---

### **Phase F: UI Polish & Workflow** (2-3 hours)

**Goal:** Create smooth user experience for managing inner grid primitives.

**Tasks:**
1. **Add Primitive Library Panel**
   ```python
   class OBJECT_PT_WFCPrimitiveLibraryPanel(bpy.types.Panel):
       \"\"\"Panel for managing primitive libraries\"\"\"

       def draw(self, context):
           layout = self.layout

           # Section: Outer Grid
           box = layout.box()
           box.label(text="Outer Grid Primitives", icon='WORLD')
           box.operator("object.wfc_load_primitive_library",
                       text="Load Outer Grid Library").category = "outer_grid"
           box.label(text=f"Loaded: {len(get_primitives_by_category('outer_grid'))}")

           # Section: Building
           box = layout.box()
           box.label(text="Building Primitives", icon='HOME')
           box.operator("object.wfc_load_primitive_library",
                       text="Load Building Library").category = "building"
           box.label(text=f"Loaded: {len(get_primitives_by_category('building'))}")
   ```

2. **Create Operators**
   - `OBJECT_OT_WFCLoadPrimitiveLibrary` - Load library by category
   - `OBJECT_OT_WFCSavePrimitiveLibrary` - Save current primitives of category
   - `OBJECT_OT_WFCGenerateCategoryModules` - Generate modules for category

3. **Update Main Panel**
   - Add "Build Building Modules" button (like "Build Modules" for outer grid)
   - Add "Build Park Modules" button
   - Show counts: "Outer: 3 primitives, 12 modules" etc.

4. **Add Workflow Documentation**
   - Create user guide for inner grid primitive workflow
   - Add tooltips to operators
   - Create example .blend file with primitives

**Files Modified:**
- `addons/blender-wfc/primitive_ui.py`

**Files Created:**
- `docs/user_guides/INNER_GRID_PRIMITIVES_WORKFLOW.md`
- `examples/inner_grid_primitives.blend`

---

## 📊 Summary: Full Workflow

### **Outer Grid Workflow (Existing - No Changes)**
1. User: Create outer grid primitive (8x8m)
2. User: Assign type + connectors → Save to JSON
3. User: Click "Build Primitives" (loads from library)
4. User: Click "Build Modules" (generates rotations)
5. User: Click "Build Grid" → "Collapse"
6. ✅ Outer city grid created

### **Inner Grid Workflow (NEW)**
1. User: Create building primitive (2x2m)
2. User: Assign type + connectors + **category="building" + resolution=4**
3. User: Save to **building_library.json**
4. User: Load **building_library.json** into scene
5. User: Click **"Build Building Modules"** (NEW button)
6. User: Click "Collapse Outer Grid" (existing)
7. User: Click **"Generate Building Islands"** (NEW button)
8. System: Extracts building plots from outer grid
9. System: Groups into islands
10. System: Creates inner grids with building modules
11. System: Collapses inner grids
12. ✅ Buildings generated on plots!

---

## ⏱️ Time Estimates

| Phase | Description | Time | Priority |
|-------|-------------|------|----------|
| **Phase A** | Extend PrimitiveData structure | 1-2 hours | **Critical** |
| **Phase B** | Update UI for categories | 1-2 hours | **Critical** |
| **Phase C** | Library management | 2-3 hours | **Critical** |
| **Phase D** | Module generation refactor | 3-4 hours | **Critical** |
| **Phase E** | Inner grid integration | 2-3 hours | **Critical** |
| **Phase F** | UI polish & workflow | 2-3 hours | High |
| **Total** | | **11-17 hours** | |

**MVP (Phases A-E):** 9-14 hours
**Full System (All Phases):** 11-17 hours

---

## 🎯 Success Criteria

- [ ] Can create building primitive with resolution=4, category="building"
- [ ] Can save building primitive to `building_library.json`
- [ ] Can load building library and auto-create primitives in scene
- [ ] Can click "Build Building Modules" to generate modules
- [ ] Building modules stored separately from outer grid modules
- [ ] Inner grid system uses building modules automatically
- [ ] Building islands collapse with building modules
- [ ] Workflow is as smooth as outer grid workflow

---

## 🚀 Next Steps

**Option 1: Start with Phase A** (Recommended)
- Extend data structure first
- Foundation for everything else
- Can test/validate immediately

**Option 2: Prototype End-to-End**
- Create simple example manually
- Test inner grid with hardcoded building primitives
- Then implement persistence

**Option 3: UI-First Approach**
- Design UI mockups first
- Get user feedback
- Then implement backend

**Recommendation:** Start with Phase A (data structure), then B (UI), then test with manual JSON before automating C-F.

---

**Ready to proceed? Which phase should we start with?**
