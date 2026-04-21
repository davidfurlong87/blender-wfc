# Primitive Sizing System - Clean Design

**Goal:** Eliminate hardcoded size values and confusion between resolution, cell size, and module size by creating a self-documenting, persisted metadata system.

**Date:** 2026-04-08  
**Status:** 📋 Design Phase

---

## 🔴 Current Problems

### **Problem 1: Hardcoded Global Values**

```python
# wfc_values.py
module_size = 8  # ← What does this control? Outer grid? All grids?
primitive_offset_x = module_size * 4  # ← Why 4? What's this for?
```

**Issues:**
- `module_size = 8` is **only for outer grid** but used globally
- Inner grids need `module_size = 2` but it's not stored anywhere
- Park grids might need `module_size = 1` - no support
- Changing `module_size` breaks everything

### **Problem 2: Terminology Confusion**

| Term | Current Meaning | Confusion |
|------|----------------|-----------|
| `module_size` | Physical size of outer grid cell (8m) | Sounds like it should apply to all modules |
| `resolution` | How many inner cells per outer cell (4) | Not stored anywhere |
| `cell_size` | ??? Not defined | Would be 2m for building (8/4) |
| `primitive_offset_x` | Spacing for primitive visualization | Why hardcoded? |

### **Problem 3: Missing Metadata**

When you save a primitive to JSON, **size information is lost:**
```json
{
  "name": "building_corner",
  "primitive_type": "BUILDING",
  "verts": [[-1, -1, 0], [1, -1, 0], ...],  // ← In what units???
  // ❌ No cell_size
  // ❌ No grid_category  
  // ❌ No resolution info
}
```

**Result:** You can't tell if this primitive is:
- 8x8m for outer grid
- 2x2m for building grid
- 1x1m for park grid

---

## ✅ Proposed Solution: Self-Describing Primitives

### **Core Concept**

**Each primitive knows its own size and purpose.** No hardcoded globals.

```python
@dataclass
class PrimitiveData:
    # Existing fields...
    
    # NEW: Physical size metadata
    physical_size: float = 8.0  # Physical size in meters (8m, 2m, 1m, etc.)
    
    # NEW: Grid category (which grid system this belongs to)
    grid_category: str = "outer_grid"  # "outer_grid", "building", "park", etc.
    
    # NEW: Resolution multiplier (how many of these fit in parent grid cell)
    resolution_multiplier: int = 1  # 1=outer grid, 4=building (4x4), 8=park (8x8)
```

**Key Benefits:**
1. ✅ **Self-documenting** - Primitive says "I'm 2m, for building grids, 4 of me fit in outer cell"
2. ✅ **No hardcoding** - Values persist in JSON, not in code
3. ✅ **No confusion** - Clear what each value means
4. ✅ **Flexible** - Easy to add new grid types

---

## 📐 Sizing System Explained

### **The Hierarchy**

```
Outer Grid (City Layout)
├─ Cell: 8m × 8m
├─ Category: "outer_grid"
└─ Primitives: physical_size=8.0, resolution_multiplier=1

    Inner Grid (Building Detail)
    ├─ Cell: 2m × 2m (8 ÷ 4 = 2)
    ├─ Category: "building"
    ├─ Resolution: 4x4 cells per outer cell
    └─ Primitives: physical_size=2.0, resolution_multiplier=4

        Micro Grid (Fine Detail - Future)
        ├─ Cell: 1m × 1m (8 ÷ 8 = 1)
        ├─ Category: "park_detail"
        ├─ Resolution: 8x8 cells per outer cell
        └─ Primitives: physical_size=1.0, resolution_multiplier=8
```

### **The Math**

Given an outer grid cell of 8m:

| Grid Type | physical_size | resolution_multiplier | Calculation | Result |
|-----------|---------------|----------------------|-------------|--------|
| Outer Grid | 8.0 | 1 | 8 ÷ 1 = 8 | 1 cell per outer cell |
| Building | 2.0 | 4 | 8 ÷ 4 = 2 | 16 cells (4×4) per outer cell |
| Park Detail | 1.0 | 8 | 8 ÷ 8 = 1 | 64 cells (8×8) per outer cell |
| Road Detail | 4.0 | 2 | 8 ÷ 2 = 4 | 4 cells (2×2) per outer cell |

**Formula:**
```python
physical_size = base_outer_size / resolution_multiplier
# Or inversely:
resolution_multiplier = base_outer_size / physical_size
```

---

## 🗂️ Metadata Structure

### **PrimitiveData Fields (Updated)**

```python
@dataclass
class PrimitiveData:
    # === Existing Fields ===
    name: str
    primitive_type: str
    verts: List[Tuple[float, float, float]]
    faces: List[Tuple[int, ...]]
    mat_indices: List[int]
    material_names: List[str]
    pos_x_connector: str
    neg_x_connector: str
    pos_y_connector: str
    neg_y_connector: str
    vertex_groups: Dict[str, Dict[str, List]]
    metadata: Dict[str, any] = field(default_factory=dict)
    
    # === NEW: Size Metadata ===
    physical_size: float = 8.0  
    """Physical size of this primitive in meters (8.0, 2.0, 1.0, etc.)"""
    
    grid_category: str = "outer_grid"  
    """Which grid system: 'outer_grid', 'building', 'park', 'road_detail', etc."""
    
    resolution_multiplier: int = 1  
    """How many cells of this size fit in one outer grid cell (1, 2, 4, 8)"""
    
    # === NEW: Optional Display Hints ===
    visualization_offset: float = None  
    """Spacing offset for Blender visualization (auto-calculated if None)"""
```

### **JSON Example**

```json
{
  "format_version": "1.1",
  "primitive": {
    "name": "building_corner_2m",
    "primitive_type": "BUILDING",
    "physical_size": 2.0,
    "grid_category": "building",
    "resolution_multiplier": 4,
    "verts": [[-1.0, -1.0, 0.0], [1.0, -1.0, 0.0], ...],
    "connectors": {
      "pos_x": "WALL",
      "neg_x": "DOOR",
      "pos_y": "WALL",
      "neg_y": "WINDOW"
    },
    "metadata": {
      "created_date": "2026-04-08",
      "author": "User",
      "description": "Corner piece for building interiors"
    }
  }
}
```

---

## 🔧 Code Changes Required

### **1. Update `primitive_data_core.py`**

```python
@dataclass
class PrimitiveData:
    # ... existing fields ...
    
    # NEW fields
    physical_size: float = 8.0
    grid_category: str = "outer_grid"
    resolution_multiplier: int = 1
    visualization_offset: float = None
    
    def validate(self) -> Tuple[bool, List[str]]:
        errors = []
        
        # ... existing validation ...
        
        # NEW: Validate size fields
        if self.physical_size <= 0:
            errors.append("physical_size must be positive")
        
        if self.resolution_multiplier < 1:
            errors.append("resolution_multiplier must be >= 1")
        
        if self.grid_category not in ["outer_grid", "building", "park", "road_detail"]:
            errors.append(f"Unknown grid_category: {self.grid_category}")
        
        # NEW: Validate consistency
        # If outer grid, resolution should be 1
        if self.grid_category == "outer_grid" and self.resolution_multiplier != 1:
            errors.append("Outer grid primitives should have resolution_multiplier=1")
        
        return (len(errors) == 0, errors)
    
    def to_dict(self) -> dict:
        data = {
            # ... existing fields ...
            "physical_size": self.physical_size,
            "grid_category": self.grid_category,
            "resolution_multiplier": self.resolution_multiplier,
        }
        if self.visualization_offset is not None:
            data["visualization_offset"] = self.visualization_offset
        return data
```

---

### **2. Update `wfc_values.py` - Deprecate Hardcoded Values**

```python
# wfc_values.py

# === DEPRECATED: Legacy values for backward compatibility ===
# These will be removed in future version. Use primitive.physical_size instead.
module_size = 8  # ⚠️ DEPRECATED - Use primitive.physical_size
primitive_offset_x = module_size * 4  # ⚠️ DEPRECATED - Auto-calculated

# === NEW: Grid Category Definitions ===
class GridCategory:
    \"\"\"Standard grid category names\"\"\"
    OUTER_GRID = "outer_grid"
    BUILDING = "building"
    PARK = "park"
    ROAD_DETAIL = "road_detail"

# === NEW: Default Sizes (Reference Only) ===
DEFAULT_GRID_SIZES = {
    GridCategory.OUTER_GRID: 8.0,  # 8m cells
    GridCategory.BUILDING: 2.0,     # 2m cells (4x4 per outer)
    GridCategory.PARK: 1.0,         # 1m cells (8x8 per outer)
    GridCategory.ROAD_DETAIL: 4.0,  # 4m cells (2x2 per outer)
}

DEFAULT_RESOLUTIONS = {
    GridCategory.OUTER_GRID: 1,
    GridCategory.BUILDING: 4,
    GridCategory.PARK: 8,
    GridCategory.ROAD_DETAIL: 2,
}
```

---

### **3. Update Module Generation - Use Primitive Metadata**

```python
# __init__.py - Refactored generate_modules()

def generate_modules_from_primitives(
    primitives: List[bpy.types.Object],
    collection_name: str = None,
    location_offset: Vector = Vector((-50, -50, 0))
) -> List[WFCModule]:
    """
    Generate rotated modules from primitives using their metadata

    NO HARDCODED SIZES - reads from primitive properties!
    """
    if collection_name is None:
        collection_name = CollectionNames.Modules.value

    modules_collection = get_collection_by_name(collection_name)
    modules = []

    for i, prim_obj in enumerate(primitives):
        # Read size from primitive (NOT from global module_size!)
        prim_size = prim_obj.get("physical_size", 8.0)  # Default to 8.0 if not set
        grid_category = prim_obj.get("grid_category", "outer_grid")

        # Calculate visualization offset based on primitive size
        offset = prim_size * 2

        # Extract connectors
        pos_x = prim_obj.x_pos_connector
        neg_x = prim_obj.x_neg_connector
        pos_y = prim_obj.y_pos_connector
        neg_y = prim_obj.y_neg_connector

        # Generate 4 rotations
        for rotation in range(4):
            module_name = f"{prim_obj.name}_{rotation}"
            module_data = prim_obj.data.copy()
            module_obj = bpy.data.objects.new(module_name, module_data)

            # Copy metadata to module
            module_obj["physical_size"] = prim_size
            module_obj["grid_category"] = grid_category

            # Set connectors (rotate for each rotation)
            module_obj.x_pos_connector = pos_x
            module_obj.x_neg_connector = neg_x
            module_obj.y_pos_connector = pos_y
            module_obj.y_neg_connector = neg_y

            link_object_to_single_collection(module_obj, modules_collection)

            # Position using primitive's size (not global module_size!)
            position = location_offset + Vector((
                (rotation * prim_size + (rotation * offset)),
                (i * prim_size + offset),
                0
            ))
            module_obj.location = position
            module_obj.rotation_euler = (0, 0, radians(rotation * 90))

            # Create WFCModule with metadata
            wfc_module = WFCModule(
                name=module_name,
                obj_source=module_obj,
                module_weight=1.0,
                pos_x=pos_x,
                neg_x=neg_x,
                pos_y=pos_y,
                neg_y=neg_y
            )
            # Store size info in WFCModule
            wfc_module.physical_size = prim_size
            wfc_module.grid_category = grid_category

            modules.append(wfc_module)

            # Rotate connectors for next rotation
            pos_x, neg_x, pos_y, neg_y = neg_y, pos_y, pos_x, neg_x

    # Apply rotations
    bpy.ops.object.select_all(action='DESELECT')
    for obj in modules_collection.objects:
        obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

    return modules

# Backward-compatible wrapper
def generate_modules():
    """Legacy function - generates outer grid modules only"""
    outer_primitives = [p for p in get_all_primitives()
                       if p.get("grid_category", "outer_grid") == "outer_grid"]
    return generate_modules_from_primitives(
        outer_primitives,
        CollectionNames.Modules.value
    )

# NEW: Category-specific generators
def generate_building_modules():
    """Generate modules from building primitives"""
    building_prims = [p for p in get_all_primitives()
                     if p.get("grid_category") == "building"]
    return generate_modules_from_primitives(
        building_prims,
        "Building_Modules"
    )
```

---

### **4. Update `BlenderWFCAdapter` - Dynamic Sizing**

```python
# wfc_blender_adapter.py

def create_blender_object_for_cell(self, cell, selected_module):
    """Place module in grid using its own size metadata"""
    wfc_module = self.blender_module_map[selected_module.id]
    source_obj = wfc_module.obj_source

    # Read size from module (NOT from global module_size!)
    cell_size = getattr(wfc_module, 'physical_size', 8.0)

    # Calculate placement using module's size
    placement_location = (cell.x * cell_size, cell.y * cell_size, 0)

    # Create instance
    collapsed_cell_obj = duplicate_and_move_and_return(source_obj, placement_location)
    collapsed_cell_obj.name = f"{cell.x:02d}_{cell.y:02d}-{source_obj.name}"

    # Link to grid collection
    grid_collection = get_collection_by_name(CollectionNames.Grid.value)
    link_object_to_single_collection(collapsed_cell_obj, grid_collection)

    return collapsed_cell_obj

def create_blender_visualization_grid(self, grid_width, grid_height, modules):
    """Create debug grid using module sizes"""
    grid_collection = get_collection_by_name(CollectionNames.Grid.value)

    # Get cell size from first module (all should be same category)
    if modules and len(modules) > 0:
        first_module = modules[0]
        cell_size = getattr(first_module, 'physical_size', 8.0)
    else:
        cell_size = 8.0  # Fallback

    # Create debug planes using dynamic cell_size
    for x in range(grid_width):
        for y in range(grid_height):
            bpy.ops.mesh.primitive_plane_add(size=cell_size, location=(x * cell_size, y * cell_size, 0))
            # ... rest of debug plane setup
```

---

## 🎨 UI Changes

### **Update `primitive_ui.py` - Add Size Fields**

```python
class OBJECT_OT_WFCAssignConnectors(bpy.types.Operator):
    """Assign connector values and size metadata to the primitive"""

    # ... existing connector fields ...

    # NEW: Size metadata fields
    physical_size: FloatProperty(
        name="Physical Size (m)",
        description="Size of primitive in meters",
        default=8.0,
        min=0.1,
        max=100.0
    )

    grid_category: EnumProperty(
        name="Grid Category",
        description="Which grid system this primitive belongs to",
        items=[
            ('outer_grid', "Outer Grid", "Main city grid (default 8m)"),
            ('building', "Building", "Interior building grid (default 2m)"),
            ('park', "Park", "Park detail grid (default 1m)"),
            ('road_detail', "Road Detail", "Road detail grid (default 4m)"),
        ],
        default='outer_grid'
    )

    resolution_multiplier: IntProperty(
        name="Resolution Multiplier",
        description="How many cells fit in outer grid cell (auto-set by category)",
        default=1,
        min=1,
        max=16
    )

    def invoke(self, context, event):
        # Pre-populate
        obj = context.object
        if obj:
            self.physical_size = obj.get("physical_size", 8.0)
            self.grid_category = obj.get("grid_category", "outer_grid")
            self.resolution_multiplier = obj.get("resolution_multiplier", 1)

            # Pre-populate connectors...

        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout

        # Size section
        box = layout.box()
        box.label(text="Size Metadata:", icon='SNAP_GRID')
        box.prop(self, "grid_category")
        box.prop(self, "physical_size")
        box.prop(self, "resolution_multiplier")

        # Auto-calculate helper
        if self.grid_category != 'outer_grid':
            calculated_size = 8.0 / self.resolution_multiplier
            box.label(text=f"Calculated size: {calculated_size:.2f}m", icon='INFO')

        layout.separator()

        # Connectors section
        box = layout.box()
        box.label(text="Connectors:", icon='LINKED')
        box.prop(self, "pos_x")
        # ... rest of connectors

    def execute(self, context):
        obj = context.object

        # ... existing validation ...

        # Assign size metadata
        obj["physical_size"] = self.physical_size
        obj["grid_category"] = self.grid_category
        obj["resolution_multiplier"] = self.resolution_multiplier

        # Assign connectors
        obj.x_pos_connector = self.pos_x
        # ... rest of connectors

        self.report({'INFO'}, f"Assigned metadata: {self.physical_size}m, {self.grid_category}")
        return {'FINISHED'}
```

---

## 📊 Migration Strategy

### **Phase 1: Add Fields (Backward Compatible)**
1. Add new fields to `PrimitiveData` with defaults
2. Old JSON files without fields → use defaults (8.0, "outer_grid", 1)
3. New JSON files save all fields

### **Phase 2: Update Code to Use Metadata**
1. Refactor `generate_modules()` to read `physical_size` from primitives
2. Update `BlenderWFCAdapter` to use dynamic sizing
3. Update UI to set metadata

### **Phase 3: Deprecate Hardcoded Values**
1. Add deprecation warnings for global `module_size`
2. Migration tool to add metadata to existing primitives
3. Update documentation

### **Phase 4: Remove Hardcoded Values** (Future)
1. Remove global `module_size` entirely
2. All sizing from primitive metadata only

---

## ✅ Benefits Summary

| Before | After |
|--------|-------|
| ❌ `module_size = 8` hardcoded | ✅ `primitive.physical_size` persisted |
| ❌ Inner grid size unknown | ✅ `primitive.grid_category = "building"` explicit |
| ❌ Resolution in code only | ✅ `primitive.resolution_multiplier = 4` saved |
| ❌ Can't mix grid types | ✅ Multiple grid types coexist |
| ❌ Confusing terminology | ✅ Self-documenting fields |
| ❌ Size lost in JSON | ✅ Full metadata in JSON |

---

## 🚀 Implementation Order

1. **Step 1:** Add fields to `PrimitiveData` (30 min)
2. **Step 2:** Update validation & serialization (30 min)
3. **Step 3:** Update UI to assign metadata (1 hour)
4. **Step 4:** Test: Create primitive with metadata, save, load (30 min)
5. **Step 5:** Refactor `generate_modules()` to use metadata (2 hours)
6. **Step 6:** Update `BlenderWFCAdapter` for dynamic sizing (2 hours)
7. **Step 7:** Test full workflow (1 hour)

**Total: ~7-8 hours**

---

**Ready to start with Step 1?**
```
