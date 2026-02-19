# Debug Mesh Behavior - Final Implementation ✅

**Date:** 2026-02-16  
**Status:** Implemented according to user specification

---

## 📋 Expected Behavior (User Specification)

From `wfc_blender_adapter.py` lines 356-368:

1. **User creates primitives**
2. **User creates modules**
3. **User hits "Build Grid"**
   - This creates a debug visualization grid, showing debug meshes with their current entropy.
4. **If user hits "Debug Collapse":**
   - 4a: A debug mesh object is collapsed, and its effect is propagated.
   - 4b: The collapsed debug cell object is **removed**, and a module is put in its place.
   - 4c: The remaining debug mesh objects' color is updated to reflect their current entropy.
5. **If the user presses "Full Collapse":**
   - 5a: The current grid is fully collapsed from its present state.
   - 5b: Because the grid is now collapsed, its debug meshes are no longer needed and are **removed**.

---

## ✅ Implementation

### **Step 3: Build Grid** ✅

**Operator:** `OBJECT_OT_BuildWFCGrid`

**What it does:**
- Creates pure algorithm grid
- Creates debug visualization grid (debug planes showing entropy)
- Initializes adapter with grid
- Does NOT collapse any cells

**Code:**
```python
adapter = get_wfc_adapter()
algorithm_modules = adapter.setup_from_blender_modules(all_modules)
adapter.build_algorithm_module_pairs(algorithm_modules)
grid = adapter.create_grid_from_blender(algorithm_modules, grid_width=10, grid_height=10)
adapter.create_blender_visualization_grid(grid_width=10, grid_height=10, all_modules_count=len(all_modules))
adapter.algorithm = WFCAlgorithm(grid)
```

---

### **Step 4: Debug Collapse** ✅

**Operator:** `OBJECT_OT_DebugCollapse`

**What it does:**
- Collapses one cell (4a)
- **Removes** the debug plane for that cell (4b)
- Places the collapsed module in its place (4b)
- Updates remaining debug planes' entropy display (4c)

**Code changes:**

#### **4b: Remove debug plane (not hide)**

`visualize_collapsed_cell()` - Lines 206-241:
```python
# Remove debug plane (Step 4b: collapsed debug cell object is removed)
coords = cell.get_coords_tuple()
if coords in self.cell_objects:
    debug_obj = self.cell_objects[coords]
    bpy.data.objects.remove(debug_obj, do_unlink=True)  # ✅ REMOVED
    # Store only the collapsed object
    self.cell_objects[coords] = collapsed_cell_obj
```

#### **4c: Update remaining debug planes**

`update_cell_visualization()` - Lines 243-263:
```python
# Only update if it's a debug plane (not a collapsed module)
if not isinstance(cell_obj_data, dict) and not cell.is_collapsed:
    # This is an uncollapsed debug plane - update its entropy display
    cell_obj_data.remaining_modules = cell.number_of_modules_remaining()
```

---

### **Step 5: Full Collapse** ✅

**Operator:** `OBJECT_OT_FullCollapse`

**What it does:**
- Collapses all remaining cells from current state (5a)
- **Removes** all remaining debug planes after collapse is complete (5b)

**Code changes:**

#### **5a: Collapse from current state**

`setup_and_run_full_collapse()` - Lines 325-358:
```python
# Only setup if not already initialized (user should have called "Build Grid" first)
if self.algorithm is None:
    # User didn't build grid first - create it for them
    # ... setup code ...
```

This allows Full Collapse to work on an existing grid (from Build Grid or Debug Collapse).

#### **5b: Remove all debug planes**

New method `remove_all_debug_planes()` - Lines 331-347:
```python
def remove_all_debug_planes(self):
    """
    Remove all remaining debug planes
    
    Step 5b: Because the grid is now collapsed, its debug meshes are no longer needed and are removed.
    """
    coords_to_remove = []
    for coords, cell_obj_data in self.cell_objects.items():
        # If it's still a debug plane (not collapsed), remove it
        if not isinstance(cell_obj_data, dict):
            # This is an uncollapsed debug plane
            try:
                bpy.data.objects.remove(cell_obj_data, do_unlink=True)
                coords_to_remove.append(coords)
            except:
                coords_to_remove.append(coords)
    
    # Clean up the tracking dict
    for coords in coords_to_remove:
        del self.cell_objects[coords]
```

Called at end of `setup_and_run_full_collapse()` - Line 408:
```python
# Step 5b: Remove all remaining debug meshes after full collapse
self.remove_all_debug_planes()
```

---

## 🔄 Data Structure Changes

### **Before (hiding debug planes):**
```python
self.cell_objects[coords] = {
    'debug': debug_obj,      # Hidden but kept
    'collapsed': collapsed_obj
}
```

### **After (removing debug planes):**
```python
self.cell_objects[coords] = collapsed_obj  # Just the collapsed module
```

**Benefit:** Simpler data structure, cleaner scene, matches expected behavior.

---

## 🎯 User Workflow

### **Typical Workflow:**

1. **Generate Primitives** → Creates base building blocks
2. **Generate Modules** → Creates rotational variants
3. **Build Grid** → Creates debug visualization (entropy display)
4. **Debug Collapse** (optional) → Collapse one cell at a time, see propagation
   - Debug plane is removed for collapsed cell
   - Remaining debug planes update their entropy display
5. **Full Collapse** → Collapse all remaining cells
   - All remaining debug planes are removed
   - Only collapsed modules remain

### **Alternative Workflow (skip Build Grid):**

1. **Generate Primitives**
2. **Generate Modules**
3. **Full Collapse** → Creates grid and collapses it in one step
   - Debug planes are created temporarily during collapse
   - All debug planes are removed at the end

---

## 📊 Summary of Changes

### **Files Modified:**
1. ✅ `addons/blender-wfc/wfc_blender_adapter.py`

### **Methods Modified:**
1. ✅ `visualize_collapsed_cell()` - Remove debug plane instead of hiding
2. ✅ `update_cell_visualization()` - Simplified to handle only uncollapsed cells
3. ✅ `show_debug_planes()` - Updated to work with new data structure
4. ✅ `hide_debug_planes()` - Updated to work with new data structure
5. ✅ `setup_and_run_full_collapse()` - Added call to remove debug planes

### **Methods Added:**
1. ✅ `remove_all_debug_planes()` - Remove all remaining debug planes after full collapse

---

## ✅ Behavior Verification

- [x] Step 3: Build Grid creates debug visualization
- [x] Step 4a: Debug Collapse collapses one cell
- [x] Step 4b: Debug plane is **removed** (not hidden)
- [x] Step 4c: Remaining debug planes update entropy
- [x] Step 5a: Full Collapse works from current state
- [ ] Step 5b: All debug planes are **removed** after full collapse ⚠️ **TODO** (currently commented out due to bug)

**Current Status:** Steps 3, 4a, 4b, 4c, and 5a are working correctly. Step 5b has a bug and is commented out for now.

---

## 🐛 Bug Fixes

### **Bug 1: UnboundLocalError** ✅ FIXED

**Issue:** Line 393 referenced `grid` variable which was only defined inside the `if self.algorithm is None:` block.

**Error:**
```
UnboundLocalError: local variable 'grid' referenced before assignment
```

**Fix:** Changed line 393 from:
```python
uncollapsed_cells = grid.get_uncollapsed_cells()
```

To:
```python
uncollapsed_cells = self.algorithm.grid.get_uncollapsed_cells()
```

**Reason:** `self.algorithm.grid` is always available regardless of whether the algorithm was just initialized or already existed from a previous "Build Grid" call.

---

### **Bug 2: remove_all_debug_planes() Removing Collapsed Cells** ⚠️ TODO

**Issue:** The `remove_all_debug_planes()` method (line 416) was removing all debug meshes but was also removing the collapsed cells which should be kept.

**Current Status:** Line 416 has been commented out to preserve collapsed cells.

**Code (lines 414-416):**
```python
# Step 5b: Remove all remaining debug meshes after full collapse
# TODO: This is removing all debug meshes but is also removing the collapsed cells which I want to keep.
# self.remove_all_debug_planes()
```

**Impact:**
- ✅ Collapsed cells are now preserved correctly
- ⚠️ Debug planes are NOT removed after full collapse (they remain in the scene)
- 📝 TODO: Fix `remove_all_debug_planes()` to only remove debug planes, not collapsed cells

**Future Fix Needed:** Update `remove_all_debug_planes()` logic to distinguish between debug planes and collapsed cells, removing only the former.

## Bugs:
Error: Python: Traceback (most recent call last):
  File "/Users/dfg03/Projects/wfc_repo/blender-wfc/addons/blender-wfc/__init__.py", line 372, in execute
    collapse_history = adapter.setup_and_run_full_collapse(
  File "/Users/dfg03/Projects/wfc_repo/blender-wfc/addons/blender-wfc/wfc_blender_adapter.py", line 392, in setup_and_run_full_collapse
    uncollapsed_cells = grid.get_uncollapsed_cells()
UnboundLocalError: local variable 'grid' referenced before assignment