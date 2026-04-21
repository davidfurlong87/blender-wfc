# Debug Mesh Visibility Fix ✅

**Date:** 2026-02-16  
**Issue:** Debug meshes were visible after cell collapse, and duplicate debug meshes were being created

---

## 🐛 Issues Fixed

### **Issue 1: Debug Meshes Visible After Collapse**

**Problem:** When a cell was collapsed, both the debug plane AND the collapsed module were visible, creating visual clutter.

**User Request:** 
> "Ideally I would want the choice to see the debug meshes or not. I would want the default to be that the debug mesh is not visible after its cell is collapsed."

**Solution:** 
- Modified `visualize_collapsed_cell()` to hide debug planes instead of deleting them
- Debug planes are now hidden by default (`hide_set(True)`)
- Debug planes are kept for debugging purposes (can be shown/hidden on demand)

---

### **Issue 2: Duplicate Debug Mesh Creation**

**Problem:** 
- `OBJECT_OT_BuildWFCGrid` created one set of debug meshes using old `build_wfc_grid()`
- Then `create_blender_visualization_grid()` created another set when running collapse
- Result: Two overlapping sets of debug meshes

**User Request:**
> "class OBJECT_OT_BuildWFCGrid builds an initial group of debug meshes which visually show entropy. the new method create_blender_visualization_grid then also seems to create an additional group of debug meshes. Ideally I would just like the second group, if those debug meshes correctly show entropy."

**Solution:**
- Updated `OBJECT_OT_BuildWFCGrid` to use the adapter instead of old `build_wfc_grid()`
- Now creates only ONE set of debug meshes that correctly show entropy
- Added check in `setup_and_run_full_collapse()` to avoid recreating grid if it already exists

---

## 🔧 Changes Made

### **1. Updated `wfc_blender_adapter.py`**

#### **Modified `visualize_collapsed_cell()` (Lines 206-245)**

**Before:**
```python
# Replace debug plane with actual module
coords = cell.get_coords_tuple()
if coords in self.cell_objects:
    debug_obj = self.cell_objects[coords]
    bpy.data.objects.remove(debug_obj, do_unlink=True)  # ❌ Deleted
    self.cell_objects[coords] = collapsed_cell_obj
```

**After:**
```python
# Hide debug plane but keep it for debugging purposes
coords = cell.get_coords_tuple()
if coords in self.cell_objects:
    debug_obj = self.cell_objects[coords]
    debug_obj.hide_set(True)  # ✅ Hidden in viewport
    debug_obj.hide_render = True  # ✅ Hidden in renders
    # Store both debug plane and collapsed object
    self.cell_objects[coords] = {
        'debug': debug_obj,
        'collapsed': collapsed_cell_obj
    }
```

#### **Modified `update_cell_visualization()` (Lines 247-269)**

Updated to handle both dict (collapsed) and direct object (uncollapsed) formats:

```python
if isinstance(cell_obj_data, dict):
    # Cell is collapsed, update debug plane if it exists
    if 'debug' in cell_obj_data and not cell.is_collapsed:
        cell_obj_data['debug'].remaining_modules = cell.number_of_modules_remaining()
else:
    # Cell is not collapsed, update debug plane directly
    if not cell.is_collapsed:
        cell_obj_data.remaining_modules = cell.number_of_modules_remaining()
```

#### **Added `show_debug_planes()` and `hide_debug_planes()` methods (Lines 313-329)**

```python
def show_debug_planes(self):
    """Show all debug planes (useful for debugging entropy visualization)"""
    for coords, cell_obj_data in self.cell_objects.items():
        if isinstance(cell_obj_data, dict) and 'debug' in cell_obj_data:
            cell_obj_data['debug'].hide_set(False)
        elif not isinstance(cell_obj_data, dict):
            cell_obj_data.hide_set(False)

def hide_debug_planes(self):
    """Hide all debug planes (default - shows only collapsed modules)"""
    for coords, cell_obj_data in self.cell_objects.items():
        if isinstance(cell_obj_data, dict) and 'debug' in cell_obj_data:
            cell_obj_data['debug'].hide_set(True)
```

#### **Modified `setup_and_run_full_collapse()` (Lines 331-360)**

Added check to avoid duplicate grid creation:

```python
# Only setup if not already initialized
if self.algorithm is None:
    # ... create grid and visualization ...
```

---

### **2. Updated `__init__.py`**

#### **Modified `OBJECT_OT_BuildWFCGrid` (Lines 312-341)**

**Before:**
```python
def execute(self, context):
    clear_all_cells()
    build_wfc_grid(all_modules, all_grid_cells, uncollapsed_grid_cells)  # ❌ Old method
    return {'FINISHED'}
```

**After:**
```python
def execute(self, context):
    # NEW: Use adapter to create grid visualization
    clear_all_cells()
    reset_wfc_adapter()
    
    if len(all_modules) == 0:
        self.report({'ERROR'}, "No modules found. Generate modules first.")
        return {'CANCELLED'}
    
    adapter = get_wfc_adapter()
    
    # Setup algorithm modules
    algorithm_modules = adapter.setup_from_blender_modules(all_modules)
    adapter.build_algorithm_module_pairs(algorithm_modules)
    
    # Create grid and visualization (but don't collapse)
    grid = adapter.create_grid_from_blender(algorithm_modules, grid_width=10, grid_height=10)
    adapter.create_blender_visualization_grid(grid_width=10, grid_height=10, all_modules_count=len(all_modules))
    adapter.algorithm = WFCAlgorithm(grid)
    
    self.report({'INFO'}, "Grid created with debug visualization")
    return {'FINISHED'}
```

#### **Added New Operators (Lines 261-281)**

```python
class OBJECT_OT_ShowDebugPlanes(bpy.types.Operator):
    """Show debug planes (entropy visualization)"""
    bl_idname = "object.show_debug_planes"
    bl_label = "Show Debug Planes"

    def execute(self, context):
        adapter = get_wfc_adapter()
        adapter.show_debug_planes()
        self.report({'INFO'}, "Debug planes visible")
        return {'FINISHED'}

class OBJECT_OT_HideDebugPlanes(bpy.types.Operator):
    """Hide debug planes (show only collapsed modules)"""
    bl_idname = "object.hide_debug_planes"
    bl_label = "Hide Debug Planes"

    def execute(self, context):
        adapter = get_wfc_adapter()
        adapter.hide_debug_planes()
        self.report({'INFO'}, "Debug planes hidden")
        return {'FINISHED'}
```

#### **Updated UI Panel (Lines 283-300)**

Added debug visualization controls to the Grid panel:

```python
def draw(self, context):
    layout = self.layout
    layout.operator("object.build_wfc_grid")
    layout.operator("object.clear_wfc_grid")
    
    # Debug visualization controls
    layout.separator()
    layout.label(text="Debug Visualization:")
    layout.operator("object.show_debug_planes")
    layout.operator("object.hide_debug_planes")
```

#### **Registered New Operators (Lines 612-613)**

```python
OPERATORS = [
    # ... existing operators ...
    OBJECT_OT_ShowDebugPlanes,
    OBJECT_OT_HideDebugPlanes
] + COLLECTION_OPERATORS + PRIMITIVE_OPERATORS
```

---

## ✅ Result

### **Default Behavior:**
- Debug planes are **hidden** after cell collapse
- Only collapsed modules are visible
- Clean, uncluttered visualization

### **Debug Mode:**
- Click "Show Debug Planes" to see entropy visualization
- Click "Hide Debug Planes" to return to clean view
- Debug planes update in real-time during propagation

### **No More Duplicates:**
- Only ONE set of debug meshes is created
- "Build Grid" button now uses the adapter
- Full Collapse and Debug Collapse reuse existing grid if present

---

## 🎯 User Workflow

1. **Generate Modules** - Create rotational variants
2. **Build Grid** - Create debug visualization (optional - can skip to step 3)
3. **Full Collapse** or **Debug Collapse** - Run WFC algorithm
4. **Show/Hide Debug Planes** - Toggle entropy visualization as needed

**Default view:** Only collapsed modules visible (clean)  
**Debug view:** Debug planes visible (shows entropy)

