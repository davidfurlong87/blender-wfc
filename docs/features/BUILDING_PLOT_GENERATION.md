# Building Plot Generation Feature

**Status:** 🚧 In Development  
**Priority:** High  
**Complexity:** High

---

## 📋 Overview

Building Plot Generation is a **two-level WFC system** that generates detailed city environments:

1. **Level 1 (Outer Grid):** Generate the city layout (roads, pavements, building plots) - **COMPLETE** ✅
2. **Level 2 (Inner Grid):** Generate buildings on each building plot island using WFC again - **IN DEVELOPMENT** 🚧

### **The Vision**

After the outer grid collapses, we have a city layout with "islands" where buildings should be. Each island becomes a **higher-resolution WFC grid** (4x resolution) that generates detailed buildings using building-specific modules.

---

## 🎯 Goals

1. **Identify building plot islands** from the collapsed outer grid
2. **Group adjacent building plots** into contiguous islands
3. **Create a higher-resolution WFC grid** (4x) for each island
4. **Collapse the inner grid** using building-specific modules
5. **Optimize performance** to prevent UI freezing

---

## 🏗️ Architecture

### **Two-Level WFC System**

```
┌─────────────────────────────────────────────────────────┐
│  LEVEL 1: Outer Grid (City Layout)                     │
│  Resolution: 10x10 cells @ 8m per cell                 │
│  Modules: Roads, Pavements, Building Plots             │
│  Status: ✅ COMPLETE                                    │
└─────────────────────────────────────────────────────────┘
                          ↓
        ┌─────────────────────────────────────┐
        │  Identify Building Plot Islands     │
        │  (Contiguous BUILDING modules)      │
        └─────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  LEVEL 2: Inner Grids (Building Details)               │
│  Resolution: 4x4 cells per outer cell @ 2m per cell    │
│  Modules: Building components (walls, windows, etc.)   │
│  Status: 🚧 IN DEVELOPMENT                             │
└─────────────────────────────────────────────────────────┘
```

### **Example**

**Outer Grid (8m cells):**
```
[ROAD] [ROAD] [ROAD] [ROAD]
[ROAD] [BLDG] [BLDG] [ROAD]
[ROAD] [BLDG] [BLDG] [ROAD]
[ROAD] [ROAD] [ROAD] [ROAD]
```

**Inner Grid for 2x2 Building Island (2m cells):**
```
Each [BLDG] cell becomes a 4x4 grid:
[W] [W] [W] [W]  [W] [W] [W] [W]
[W] [F] [F] [W]  [W] [F] [F] [W]
[W] [F] [F] [W]  [W] [F] [F] [W]
[W] [W] [D] [W]  [W] [W] [W] [W]

[W] [W] [W] [W]  [W] [W] [W] [W]
[W] [F] [F] [W]  [W] [F] [F] [W]
[W] [F] [F] [W]  [W] [F] [F] [W]
[W] [W] [W] [W]  [W] [W] [D] [W]

W=Wall, F=Floor, D=Door
```

---

## 🔧 Current Implementation Status

### **✅ What's Already Built**

1. **`WFCModule._calculate_building_plot_faces()`** (Lines 71-165 in `wfc_classes.py`)
   - Extracts building plot faces from vertex groups
   - Caches results for performance
   - Calculates relative coordinates for reuse

2. **`WFCModule.debug_create_building_plot_planes()`** (Lines 167-241 in `wfc_classes.py`)
   - Creates debug visualization planes for building plots
   - Uses cached data for efficiency

3. **`WFCCell.debug_create_building_plot_planes_from_module()`** (Lines 335-354 in `wfc_classes.py`)
   - Creates building plot planes for a collapsed cell
   - Calculates inner grid offset vectors

4. **Building Plot Classes** (Lines 366-421 in `wfc_classes.py`)
   - `WFCPlot` - Base class for plot data
   - `BuildingPlot` - Building-specific plot
   - `WFCPlotGroup` - Groups adjacent plots
   - `BuildingPlotGroup` - Building-specific group

5. **Plot Processing Functions** (`wfc_plots.py`)
   - `extract_building_plots_from_cell()` - Extract plots from cells
   - `group_adjacent_building_plots()` - Group contiguous plots
   - `find_adjacent_plots()` - Find neighboring plots
   - `plots_share_edge()` - Check if plots are adjacent

6. **`OBJECT_OT_DebugBuildingPlots` Operator** (Lines 400-455 in `__init__.py`)
   - Debug operator to visualize building plots
   - **Status:** Needs refactoring for new adapter architecture

### **⚠️ Known Issues**

1. **Performance Problem** - Application freezes when processing all cells
   - **Cause:** Synchronous processing of all building plots at once
   - **Impact:** UI becomes unresponsive
   - **Solution:** See "Performance Optimization Strategies" below

2. **Architecture Mismatch** - Old code uses `WFCCell` instances
   - **Cause:** Adapter stores Blender objects, not `WFCCell` instances
   - **Impact:** `OBJECT_OT_DebugBuildingPlots` is non-functional
   - **Solution:** Refactor to work with adapter architecture

3. **Missing Integration** - Not integrated with adapter layer
   - **Cause:** Building plot code predates adapter architecture
   - **Impact:** Can't access grid state properly
   - **Solution:** Create adapter methods for building plot processing

---

## 📝 Implementation Plan

### **Phase 1: Refactor for Adapter Architecture** ⚠️ Medium Risk

**Goal:** Make building plot code work with the new adapter architecture

**Tasks:**
- [ ] Work has been done to implement phase 1, but it's possible the Method/Class names below do not match the current implementation. Verify and update as needed.
- [ ] Unique building plots are now generated for each building 'island', each has its own colour. The building plot debug mesh is padded, with a gap between its end and the beginning of the pavement. This gap seems to increase with the building plot size, and small building areas have no debug plot mesh at all. This padding should be removed.
- [ ] Create `BuildingPlotAdapter` class in `wfc_blender_adapter.py`
- [ ] Add method: `extract_building_plots_from_grid()`
- [ ] Add method: `group_building_plot_islands()`
- [ ] Add method: `create_inner_grid_for_island(island, resolution=4)`
- [ ] Update `OBJECT_OT_DebugBuildingPlots` to use adapter
- [ ] Test building plot extraction and grouping

**Estimated effort:** 3-4 hours

---

### **Phase 2: Performance Optimization** ⚠️ High Risk

**Goal:** Prevent UI freezing during building plot processing

**Tasks:**
- [ ] Implement batch processing (process N cells per frame)
- [ ] Add progress indicator UI
- [ ] Use Blender's modal operator for async processing
- [ ] Cache building plot calculations
- [ ] Profile and optimize bottlenecks

**Estimated effort:** 4-6 hours

---

### **Phase 3: Inner Grid WFC** ⚠️ High Risk

**Goal:** Generate buildings using WFC on inner grids

**Tasks:**
- [ ] Create building-specific primitives (walls, floors, doors, windows)
- [ ] Generate building modules from primitives
- [ ] Implement inner grid collapse using existing WFC algorithm
- [ ] Handle edge constraints (inner grid must connect to outer grid)
- [ ] Visualize inner grid collapse

**Estimated effort:** 6-8 hours

---

### **Phase 4: Integration & Polish** ⚠️ Low Risk

**Goal:** Integrate building generation into main workflow

**Tasks:**
- [ ] Add "Generate Buildings" button to UI
- [ ] Add building generation settings (resolution, style, etc.)
- [ ] Create building-specific collections
- [ ] Add documentation
- [ ] Test full workflow

**Estimated effort:** 2-3 hours

---

## 🚀 Performance Optimization Strategies

### **Problem: UI Freezing**

The current implementation processes all building plots synchronously, causing the UI to freeze.

### **Solution 1: Modal Operator (Recommended)**

Use Blender's modal operator pattern to process building plots over multiple frames.

**Benefits:**
- ✅ UI remains responsive
- ✅ Can show progress indicator
- ✅ Can cancel operation
- ✅ Native Blender pattern

**Implementation:**
```python
class OBJECT_OT_GenerateBuildings(bpy.types.Operator):
    bl_idname = "object.generate_buildings"
    bl_label = "Generate Buildings"
    
    _timer = None
    _islands = []
    _current_island_index = 0
    
    def modal(self, context, event):
        if event.type == 'TIMER':
            # Process one island per timer tick
            if self._current_island_index < len(self._islands):
                island = self._islands[self._current_island_index]
                self.process_island(island)
                self._current_island_index += 1
                
                # Update progress
                progress = (self._current_island_index / len(self._islands)) * 100
                self.report({'INFO'}, f"Generating buildings: {progress:.0f}%")
            else:
                # Done!
                self.cancel(context)
                return {'FINISHED'}
        
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        # Extract islands
        adapter = get_wfc_adapter()
        self._islands = adapter.extract_building_plot_islands()
        
        # Start modal operation
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    
    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
```

**Drawbacks:**
- ⚠️ More complex code
- ⚠️ Harder to debug

---

### **Solution 2: Batch Processing**

Process building plots in batches with progress updates.

**Benefits:**
- ✅ Simpler than modal operator
- ✅ Can show progress
- ✅ Easier to debug

**Implementation:**
```python
def process_building_plots_batched(adapter, batch_size=10):
    """Process building plots in batches to prevent UI freezing"""
    islands = adapter.extract_building_plot_islands()
    total_islands = len(islands)

    for i in range(0, total_islands, batch_size):
        batch = islands[i:i+batch_size]
        for island in batch:
            process_island(island)

        # Force UI update
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

        # Update progress
        progress = min(100, ((i + batch_size) / total_islands) * 100)
        print(f"Progress: {progress:.0f}%")
```

**Drawbacks:**
- ⚠️ Still blocks UI during batch processing
- ⚠️ Can't cancel mid-batch

---

### **Solution 3: Caching**

Cache building plot calculations to avoid recalculating.

**Benefits:**
- ✅ Dramatically faster on subsequent runs
- ✅ Simple to implement
- ✅ Already partially implemented in `WFCModule`

**Implementation:**
- ✅ Already done: `WFCModule._calculate_building_plot_faces()` caches results
- 🚧 TODO: Cache island grouping results
- 🚧 TODO: Cache inner grid creation

---

### **Recommended Approach**

**Combine all three strategies:**

1. **Use Modal Operator** for async processing
2. **Use Batch Processing** within modal operator (process N islands per tick)
3. **Use Caching** to avoid recalculation

**Example:**
```python
class OBJECT_OT_GenerateBuildings(bpy.types.Operator):
    # ... modal operator setup ...

    def modal(self, context, event):
        if event.type == 'TIMER':
            # Process BATCH_SIZE islands per timer tick
            batch_end = min(
                self._current_island_index + BATCH_SIZE,
                len(self._islands)
            )

            for i in range(self._current_island_index, batch_end):
                island = self._islands[i]
                # Use cached data where possible
                self.process_island_cached(island)

            self._current_island_index = batch_end

            if self._current_island_index >= len(self._islands):
                self.cancel(context)
                return {'FINISHED'}

        return {'RUNNING_MODAL'}
```

---

## 🔍 Technical Details

### **Building Plot Extraction**

**How it works:**

1. **Vertex Groups** - Each module has a `building_plot` vertex group
2. **Face Detection** - Find all faces where ALL vertices are in the vertex group
3. **Coordinate Calculation** - Calculate face centers in module-local coordinates
4. **Caching** - Store results in `module.building_plot_faces_cache`

**Code location:** `WFCModule._calculate_building_plot_faces()` (Lines 71-165 in `wfc_classes.py`)

**Performance:**
- First call: ~0.1-1ms per module (depends on mesh complexity)
- Cached calls: ~0.001ms per module

---

### **Island Grouping**

**How it works:**

1. **Extract Plots** - Get all building plots from collapsed cells
2. **Flood Fill** - Group adjacent plots using flood fill algorithm
3. **Calculate Bounds** - Determine bounding box for each island
4. **Calculate Grid Size** - Determine inner grid resolution (4x outer cell size)

**Code location:** `group_adjacent_building_plots()` in `wfc_plots.py`

**Performance:**
- O(N²) where N = number of plots
- **Bottleneck:** `find_adjacent_plots()` checks all plots for each plot
- **Optimization:** Use spatial hashing to reduce to O(N)

---

### **Inner Grid Creation**

**How it works:**

1. **Calculate Grid Dimensions** - Based on island bounds and resolution multiplier
2. **Create Grid Cells** - Create WFC cells for inner grid
3. **Set Edge Constraints** - Cells at island edges must match outer grid
4. **Collapse Grid** - Use existing WFC algorithm to collapse inner grid

**Code location:** Not yet implemented

**Estimated performance:**
- Grid creation: ~1-5ms per island
- Grid collapse: ~10-100ms per island (depends on grid size)
- **Total for 10 islands:** ~100-1000ms (0.1-1 second)

---

## 🎨 Visualization Strategy

### **Debug Visualization**

**Purpose:** Visualize building plot islands before generating buildings

**Implementation:**
1. Create colored planes for each island
2. Different color per island
3. Show island ID and grid size as text

**Benefits:**
- ✅ Verify island detection is correct
- ✅ Identify performance bottlenecks (too many small islands?)
- ✅ Debug edge cases

---

### **Progress Visualization**

**Purpose:** Show progress during building generation

**Implementation:**
1. Update status text in UI
2. Highlight currently processing island
3. Show progress bar (if using modal operator)

**Benefits:**
- ✅ User knows operation is running
- ✅ User can estimate time remaining
- ✅ User can cancel if needed

---

## 📚 Code Examples

### **Example 1: Extract Building Plots (Current Architecture)**

```python
# This is the OLD way (needs refactoring)
def extract_building_plots_old():
    all_building_plots = []

    for cell in all_grid_cells.values():  # ❌ Uses old global variable
        if cell.isCollapsed:
            module = cell.return_collapsed_module()

            # Get cached building plot faces
            faces = module._calculate_building_plot_faces()

            for face in faces:
                # Create plot with world coordinates
                world_pos = Vector((
                    cell.posX * module_size + face['center_relative'].x,
                    cell.posY * module_size + face['center_relative'].y,
                    0
                ))
                plot = BuildingPlot(world_pos, face['bounds'], cell)
                all_building_plots.append(plot)

    return all_building_plots
```

---

### **Example 2: Extract Building Plots (New Adapter Architecture)**

```python
# This is the NEW way (recommended)
def extract_building_plots_from_adapter(adapter):
    """Extract building plots using the adapter architecture"""
    all_building_plots = []

    # Get all collapsed cells from adapter
    for coords, cell_obj in adapter.cell_objects.items():
        # Skip debug planes
        if isinstance(cell_obj, dict):
            continue

        # Get the module that was placed at this cell
        # We need to track which module was placed (TODO: add to adapter)
        algorithm_cell = adapter.algorithm.grid.cells.get(coords)
        if not algorithm_cell or not algorithm_cell.is_collapsed:
            continue

        # Get the Blender module from algorithm module ID
        algorithm_module_id = algorithm_cell.possible_modules[0]
        blender_module = adapter.blender_module_map.get(algorithm_module_id)

        if blender_module:
            # Get cached building plot faces
            faces = blender_module._calculate_building_plot_faces()

            for face in faces:
                # Create plot with world coordinates
                world_pos = Vector((
                    coords[0] * module_size + face['center_relative'].x,
                    coords[1] * module_size + face['center_relative'].y,
                    0
                ))
                plot = BuildingPlot(world_pos, face['bounds'], None)  # TODO: Need cell reference
                all_building_plots.append(plot)

    return all_building_plots
```

---

### **Example 3: Create Inner Grid for Island**

```python
def create_inner_grid_for_island(adapter, island, resolution_multiplier=4):
    """
    Create a higher-resolution WFC grid for a building island

    Args:
        adapter: BlenderWFCAdapter instance
        island: BuildingPlotGroup instance
        resolution_multiplier: How many inner cells per outer cell (default: 4)

    Returns:
        Grid instance for the inner grid
    """
    from wfc_algorithm import Grid, AlgorithmCell

    # Calculate inner grid dimensions
    bounds = island.combined_bounds
    width_in_outer_cells = (bounds[2] - bounds[0]) / module_size
    height_in_outer_cells = (bounds[3] - bounds[1]) / module_size

    inner_width = int(width_in_outer_cells * resolution_multiplier)
    inner_height = int(height_in_outer_cells * resolution_multiplier)

    # Create inner grid
    inner_grid = Grid(width=inner_width, height=inner_height)

    # Get building modules (TODO: create building-specific modules)
    building_modules = get_building_modules()  # TODO: implement

    # Create cells
    for x in range(inner_width):
        for y in range(inner_height):
            cell = AlgorithmCell(
                x=x,
                y=y,
                possible_modules=building_modules[:]
            )
            inner_grid.add_cell(cell)

    # TODO: Set edge constraints based on outer grid

    return inner_grid
```

---

## 🧪 Testing Strategy

### **Unit Tests**

1. **Test island detection**
   - Single cell island
   - Multi-cell island
   - Multiple separate islands
   - No islands (all roads)

2. **Test adjacency detection**
   - Horizontal adjacency
   - Vertical adjacency
   - Diagonal (should NOT be adjacent)
   - Edge cases (tolerance)

3. **Test inner grid creation**
   - Correct dimensions
   - Correct cell count
   - Edge constraints applied

---

### **Integration Tests**

1. **Test full workflow**
   - Generate outer grid
   - Extract building plots
   - Group islands
   - Create inner grids
   - Collapse inner grids

2. **Test performance**
   - Measure time for each step
   - Verify no UI freezing
   - Test with large grids (20x20)

---

## 🎯 Success Criteria

**Phase 1 (Refactor):**
- ✅ Building plot extraction works with adapter
- ✅ Island grouping works with adapter
- ✅ Debug visualization shows islands correctly

**Phase 2 (Performance):**
- ✅ No UI freezing during processing
- ✅ Progress indicator shows status
- ✅ Can process 10x10 grid in < 5 seconds

**Phase 3 (Inner Grid):**
- ✅ Inner grids created correctly
- ✅ Inner grids collapse successfully
- ✅ Buildings look reasonable

**Phase 4 (Integration):**
- ✅ Full workflow works end-to-end
- ✅ Documentation complete
- ✅ User can generate city with buildings in < 30 seconds

---

## 📖 Related Documentation

- `docs/architecture/ALGORITHM_SEPARATION_GUIDE.md` - Adapter architecture
- `docs/PERFORMANCE_OPTIMIZATION.md` - Performance profiling guide
- `PROJECT_OVERVIEW.md` - Feature gaps section

---

## 🚧 Next Steps

**Immediate next steps:**

1. **Read this document** to understand the feature
2. **Choose a phase** to start with (recommend Phase 1)
3. **Create a task list** using the task management tools
4. **Start implementation** following the plan

**Recommended starting point:**

Start with **Phase 1, Task 1**: Create `BuildingPlotAdapter` class

This will give you a clean foundation to build on and integrate with the existing adapter architecture.

---

## ❓ Questions to Consider

1. **Building Modules:** What should building modules look like?
   - Simple boxes?
   - Detailed walls/windows/doors?
   - Multiple building styles?

2. **Resolution:** Is 4x the right multiplier?
   - Higher = more detail, slower
   - Lower = less detail, faster

3. **Constraints:** How should inner grid edges connect to outer grid?
   - Must match outer cell's building plot faces?
   - Free to do anything?

4. **Visualization:** What debug visualization would be most helpful?
   - Colored islands?
   - Grid overlay?
   - Both?

---

**Good luck with the implementation! 🚀**


