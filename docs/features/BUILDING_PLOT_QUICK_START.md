# Building Plot Generation - Quick Start Guide

**For developers who want to get started quickly**

---

## 🎯 What You're Building

A **two-level WFC system** where:
1. **Level 1:** Generate city layout (roads, pavements, building plots) ✅ **DONE**
2. **Level 2:** Generate buildings on each plot island using WFC again 🚧 **TODO**

---

## 🚀 Quick Implementation Path

### **Step 1: Add Building Plot Extraction to Adapter** (1-2 hours)

**File:** `addons/blender-wfc/wfc_blender_adapter.py`

Add this method to `BlenderWFCAdapter` class:

```python
def extract_building_plots(self):
    """
    Extract building plot data from collapsed grid
    
    Returns:
        List of BuildingPlot instances
    """
    from .wfc_classes import BuildingPlot
    from mathutils import Vector
    from .wfc_values import module_size
    
    all_building_plots = []
    
    # Iterate through collapsed cells
    for coords, cell_obj in self.cell_objects.items():
        # Skip debug planes (old structure)
        if isinstance(cell_obj, dict):
            continue
        
        # Get algorithm cell
        algorithm_cell = self.algorithm.grid.cells.get(coords)
        if not algorithm_cell or not algorithm_cell.is_collapsed:
            continue
        
        # Get the Blender module
        algorithm_module_id = algorithm_cell.possible_modules[0]
        blender_module = self.blender_module_map.get(algorithm_module_id)
        
        if blender_module:
            # Get building plot faces (cached)
            faces = blender_module._calculate_building_plot_faces()
            
            for face in faces:
                # Calculate world position
                world_pos = Vector((
                    coords[0] * module_size + face['center_relative'].x,
                    coords[1] * module_size + face['center_relative'].y,
                    0
                ))
                
                # Create plot
                plot = BuildingPlot(world_pos, face['bounds'], None)
                plot.outer_cell_coords = coords
                all_building_plots.append(plot)
    
    return all_building_plots
```

---

### **Step 2: Add Island Grouping to Adapter** (1 hour)

**File:** `addons/blender-wfc/wfc_blender_adapter.py`

Add this method to `BlenderWFCAdapter` class:

```python
def group_building_plot_islands(self):
    """
    Group adjacent building plots into islands
    
    Returns:
        List of BuildingPlotGroup instances
    """
    from .wfc_plots import group_adjacent_building_plots
    
    # Extract all building plots
    all_plots = self.extract_building_plots()
    
    # Group adjacent plots
    islands = group_adjacent_building_plots(all_plots)
    
    return islands
```

---

### **Step 3: Create Debug Visualization Operator** (1 hour)

**File:** `addons/blender-wfc/__init__.py`

Replace `OBJECT_OT_DebugBuildingPlots` with:

```python
class OBJECT_OT_DebugBuildingPlots(bpy.types.Operator):
    """Visualize building plot islands"""
    bl_idname = "object.debug_building_plots"
    bl_label = "Debug Building Plots"

    def execute(self, context):
        adapter = get_wfc_adapter()
        
        if adapter.algorithm is None:
            self.report({'ERROR'}, "No grid found. Run Full Collapse first.")
            return {'CANCELLED'}
        
        # Check if grid is fully collapsed
        if len(adapter.algorithm.grid.uncollapsed_cells) > 0:
            self.report({'ERROR'}, "Grid not fully collapsed. Run Full Collapse first.")
            return {'CANCELLED'}
        
        # Extract and group building plots
        islands = adapter.group_building_plot_islands()
        
        self.report({'INFO'}, f"Found {len(islands)} building plot islands")
        
        # Visualize islands (create colored planes)
        self.visualize_islands(islands)
        
        return {'FINISHED'}
    
    def visualize_islands(self, islands):
        """Create colored debug planes for each island"""
        import random
        from .wfc_values import CollectionNames
        from .collectiontools.collection_creation import get_collection_by_name
        
        debug_collection = get_collection_by_name(CollectionNames.Debug.value)
        
        for i, island in enumerate(islands):
            # Random color per island
            color = (random.random(), random.random(), random.random(), 0.5)
            
            # Create plane for island bounds
            bounds = island.combined_bounds
            center_x = (bounds[0] + bounds[2]) / 2
            center_y = (bounds[1] + bounds[3]) / 2
            width = bounds[2] - bounds[0]
            height = bounds[3] - bounds[1]
            
            bpy.ops.mesh.primitive_plane_add(
                size=1,
                location=(center_x, center_y, 0.1)
            )
            plane = bpy.context.active_object
            plane.scale = (width/2, height/2, 1)
            plane.name = f"Island_{i}_plots_{len(island.plots)}"
            
            # Create material
            mat = bpy.data.materials.new(name=f"Island_{i}_Mat")
            mat.use_nodes = True
            mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = color
            plane.data.materials.append(mat)
            
            # Link to debug collection
            for coll in plane.users_collection:
                coll.objects.unlink(plane)
            debug_collection.objects.link(plane)
```

---

### **Step 4: Test It!** (30 minutes)

1. **Generate outer grid:**
   - Generate Primitives
   - Generate Modules
   - Full Collapse

2. **Visualize building plots:**
   - Click "Debug Building Plots"
   - You should see colored planes for each island

3. **Verify:**
   - Each island is a different color
   - Islands are contiguous (no gaps)
   - Island count makes sense

---

## 🎨 Expected Result

After Step 4, you should see:
- Your collapsed city grid (roads, pavements, building plots)
- Colored transparent planes showing building plot islands
- Console output: "Found N building plot islands"

**Example:**
```
Found 5 building plot islands
Island_0_plots_4  (4 plots, blue)
Island_1_plots_2  (2 plots, red)
Island_2_plots_1  (1 plot, green)
Island_3_plots_6  (6 plots, yellow)
Island_4_plots_3  (3 plots, purple)
```

---

## 🚀 Next Steps (After Quick Start)

Once you have island visualization working:

1. **Add Inner Grid Creation** - Create 4x4 grid for each island
2. **Add Building Modules** - Create building-specific primitives/modules
3. **Add Inner Grid Collapse** - Use WFC to collapse inner grids
4. **Add Performance Optimization** - Use modal operator to prevent freezing

See `BUILDING_PLOT_GENERATION.md` for detailed implementation plan.

---

## 🐛 Common Issues

### **Issue: "No 'building_plot' vertex group found"**

**Cause:** Your modules don't have building plot vertex groups

**Solution:** Add vertex groups to your primitive meshes:
1. Select primitive in Edit mode
2. Create vertex group named "building_plot"
3. Assign faces that should be building plots
4. Regenerate modules

---

### **Issue: "Found 0 building plot islands"**

**Cause:** No building plots in your modules, or grid not collapsed

**Solution:**
1. Make sure grid is fully collapsed (no uncollapsed cells)
2. Make sure at least one module has building plot vertex groups
3. Check console for "No 'building_plot' vertex group found" messages

---

### **Issue: Application freezes**

**Cause:** Too many building plots being processed at once

**Solution:**
1. Use smaller grid (5x5 instead of 10x10)
2. Reduce number of building plot faces per module
3. Implement modal operator (see main documentation)

---

## 📝 Code Checklist

- [ ] Added `extract_building_plots()` to adapter
- [ ] Added `group_building_plot_islands()` to adapter
- [ ] Updated `OBJECT_OT_DebugBuildingPlots` operator
- [ ] Tested with small grid (5x5)
- [ ] Verified islands are detected correctly
- [ ] Verified visualization works

---

## 🎯 Success Criteria

**You're done with Quick Start when:**
- ✅ You can visualize building plot islands
- ✅ Islands are colored differently
- ✅ Island count matches expectations
- ✅ No errors in console

**Time estimate:** 3-4 hours total

---

**Ready to start? Begin with Step 1!** 🚀

