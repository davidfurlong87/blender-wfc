# Complete Metadata System - Implementation Roadmap

**Goal:** Replace ALL hardcoded values with persisted metadata system

**Date:** 2026-04-08  
**Status:** 📋 Ready to Implement

---

## 🎯 Objective

**Eliminate Every Hardcoded Value:**
1. ❌ `module_size = 8` → ✅ `primitive.physical_size`
2. ❌ `primitive_offset_x` → ✅ Auto-calculated from size
3. ❌ `sockets_match()` hardcoded rules → ✅ `connectors.json`
4. ❌ `CONNECTORS` enum hardcoded → ✅ Generated from registry

**Result:** System can faithfully recreate current primitives using ONLY metadata from JSON files.

---

## 📋 Complete System Architecture

### **Data Flow (All Metadata)**

```
┌─────────────────────────────────────────────────────┐
│           USER CREATES PRIMITIVE                    │
│         (Blender mesh + metadata)                   │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│        PRIMITIVE METADATA (Persisted)               │
├─────────────────────────────────────────────────────┤
│  • physical_size: 8.0                               │
│  • grid_category: "outer_grid"                      │
│  • resolution_multiplier: 1                         │
│  • pos_x_connector: "ROAD"  ─────┐                 │
│  • neg_x_connector: "ROAD"       │                 │
│  • pos_y_connector: "ROAD"       │                 │
│  • neg_y_connector: "BUILDING"   │                 │
└──────────────────────────────────┼──────────────────┘
                                   │
              ┌────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────┐
│      CONNECTOR REGISTRY (Persisted)                 │
├─────────────────────────────────────────────────────┤
│  From: data/connectors.json                         │
│                                                      │
│  ROAD:                                              │
│    compatible_with: ["ROAD"]                        │
│    grid_category: "outer_grid"                      │
│                                                      │
│  BUILDING:                                          │
│    compatible_with: ["BUILDING"]                    │
│    grid_category: "outer_grid"                      │
└─────────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│           MODULE GENERATION                         │
├─────────────────────────────────────────────────────┤
│  • Reads primitive.physical_size (no hardcoding!)   │
│  • Creates 4 rotations                              │
│  • Spacing = physical_size * 2 (auto-calc)          │
│  • Connector matching uses registry                 │
└─────────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│              WFC GRID                               │
├─────────────────────────────────────────────────────┤
│  • Cell size = primitive.physical_size              │
│  • Compatible modules from connector registry       │
│  • No hardcoded values anywhere!                    │
└─────────────────────────────────────────────────────┘
```

---

## 🗂️ Files to Create/Modify

### **New Files** ✨
1. `addons/blender-wfc/connector_registry.py` (~200 lines)
2. `addons/blender-wfc/data/connectors.json` (~50 lines)
3. `docs/features/PRIMITIVE_SIZING_SYSTEM_DESIGN.md` ✅ (created)
4. `docs/features/CONNECTOR_COMPATIBILITY_SYSTEM_DESIGN.md` ✅ (created)

### **Files to Modify** 🔧
1. `addons/blender-wfc/primitive_data_core.py` - Add 3 sizing fields
2. `addons/blender-wfc/primitive_ui.py` - Add sizing UI
3. `addons/blender-wfc/wfc_classes.py` - Replace `sockets_match()`
4. `addons/blender-wfc/wfc_blender_adapter.py` - Use registry
5. `addons/blender-wfc/__init__.py` - Refactor `generate_modules()`
6. `addons/blender-wfc/wfc_enums.py` - Generate from registry
7. `addons/blender-wfc/wfc_values.py` - Deprecate globals
8. `tests/test_primitive_data.py` - Add sizing tests

---

## 📅 Complete Implementation Schedule

**Total Estimated Time: 18-25 hours** (MVP: 14-19 hours)

---

### **MILESTONE 1: Core Metadata System** (6-8 hours)

**Goal:** Replace all hardcoded values with persisted metadata

---

#### **Phase 1A: Primitive Sizing Metadata** (2-3 hours)

**Task 1A.1: Add Sizing Fields to PrimitiveData** (1 hour) ⭐ **START HERE**
- [ ] Modify `addons/blender-wfc/primitive_data_core.py`:
  - [x] Add `physical_size: float = 8.0`
  - [x] Add `grid_category: str = "outer_grid"`
  - [x] Add `resolution_multiplier: int = 1`
  - [ ] Add `visualization_offset: float = None` (optional)
- [ ] Update `validate()` method:
  - [x] Check `physical_size > 0`
  - [x] Check `resolution_multiplier >= 1`
  - [x] Check `grid_category` in allowed list
  - [x] Validate consistency (outer_grid → resolution=1)
- [x] Update `to_dict()` to include new fields
- [x] Update `from_dict()` with defaults for backward compatibility

**Task 1A.2: Update Serialization & Tests** (1 hour)
- [x] Test primitive with new fields serializes correctly
- [x] Test old JSON files load with defaults
- [x] Update `tests/test_primitive_data.py`:
  - [x] Test new field validation
  - [x] Test JSON round-trip with metadata
  - [x] Test backward compatibility
- [x] Verify no breaking changes

**Task 1A.3: Update PrimitiveAdapter** (30 min)
- [ ] Modify `primitive_adapter.py`:
  - [ ] Extract sizing metadata from Blender objects
  - [ ] Apply sizing metadata when creating Blender objects
  - [ ] Set custom properties on created objects
- [ ] Test: Extract → Create round-trip preserves metadata

---

#### **Phase 1B: Connector Registry System** (2-3 hours)

**Task 1B.1: Create ConnectorRegistry** (2 hours)
- [x] Create `addons/blender-wfc/connector_registry.py`:
  - [x] `ConnectorDefinition` dataclass
    - [x] `name: str`
    - [x] `description: str`
    - [x] `compatible_with: List[str]`
    - [x] `grid_category: str`
    - [x] `is_symmetric: bool`
  - [x] `ConnectorRegistry` class
    - [x] `register(connector)` method
    - [x] `get(name)` method
    - [x] `matches(a, b)` method ⭐ **Key function**
    - [x] `get_all_for_category(category)` method
    - [x] `to_dict()` / `from_dict()` for JSON
    - [x] `save_to_file()` / `load_from_file()`
  - [x] Global instance: `connector_registry`
  - [x] `_load_defaults()` with outer grid connectors

**Task 1B.2: Create Default Connector Library** (30 min)
- [x] Create `addons/blender-wfc/data/` directory
- [x] Create `addons/blender-wfc/data/connectors.json`:
  - [x] ROAD → ROAD
  - [x] BUILDING → BUILDING
  - [x] PAVEMENTPOS → PAVEMENTNEG
  - [x] PAVEMENTNEG → PAVEMENTPOS
  - [x] WALL, DOOR, WINDOW, HALLWAY (building connectors)
- [x] Add file format versioning

**Task 1B.3: Load Registry on Startup** (30 min)
- [x] Modify `addons/blender-wfc/__init__.py`:
  - [x] Import connector_registry
  - [x] Load `data/connectors.json` in `register()`
  - [x] Add error handling for missing file
- [x] Test: Registry loads on addon enable

---

#### **Phase 1C: Replace Hardcoded Socket Matching** (1-2 hours)

**Task 1C.1: Update Core Matching Function** (30 min)
- [x] Modify `addons/blender-wfc/wfc_classes.py`:
  - [x] Replace `sockets_match()` body:
    ```python
    def sockets_match(socket_a, socket_b):
        from .connector_registry import connector_registry
        return connector_registry.matches(socket_a, socket_b)
    ```
  - [x] Add deprecation comment

**Task 1C.2: Update Adapter Matching** (30 min)
- [ ] Modify `addons/blender-wfc/wfc_blender_adapter.py`:
  - [ ] Update `_sockets_match()` to use registry
  - [ ] Remove hardcoded logic

**Task 1C.3: Test Backward Compatibility** (30 min)
- [ ] Test existing primitives still match correctly
- [ ] Verify ROAD matches ROAD
- [ ] Verify PAVEMENTPOS matches PAVEMENTNEG
- [ ] Test module pair building works

---

### **MILESTONE 2: Dynamic Sizing Integration** (4-6 hours)

**Goal:** Module generation and grid use metadata, no hardcoded sizes

---

#### **Phase 2A: Update Enums & Properties** (1-2 hours)

**Task 2A.1: Make Connector Enums Dynamic** (1 hour)
- [x] Modify `addons/blender-wfc/wfc_enums.py`:
  - [x] Create `get_connector_enum_items()` function
  - [x] Generate `CONNECTORS` from registry
  - [x] Create `get_connector_items_for_category(category)` for filtering
- [ ] Test: CONNECTORS list contains all registry items

**Task 2A.2: Update Property Registration** (1 hour)
- [ ] Modify `addons/blender-wfc/__init__.py`:
  - [ ] Add `physical_size` property to Object
  - [ ] Add `grid_category` property to Object
  - [ ] Add `resolution_multiplier` property to Object
  - [ ] Update connector properties to use dynamic enums (if possible)
- [ ] Test: Properties appear on objects

---

#### **Phase 2B: Refactor Module Generation** (2-3 hours)

**Task 2B.1: Update generate_modules_from_primitives()** (2 hours)
- [x] Modify `addons/blender-wfc/wfc_classes.py`:
  - [x] Add `physical_size` parameter to `WFCModule.__init__()`
- [x] Modify `addons/blender-wfc/__init__.py`:
  - [x] Read `physical_size` from primitive objects
  - [x] Calculate `offset = physical_size * 2` (dynamic, per primitive)
  - [x] Position modules using `physical_size` not `module_size`
  - [x] Store `physical_size` on WFCModule instances
  - [x] Honor `rotation_invariant` — generate 1 module instead of 4 when True
  - [x] `build_from_primitive_data()` sets all 4 metadata fields on objects
  - [x] `build_all_primitives()` uses `physical_size` for display spacing
  - [x] `module_size` and `primitive_offset_x` imports removed
- [ ] Test: Generate modules from primitives with different sizes in Blender

**Task 2B.2: Update BlenderWFCAdapter for Dynamic Sizing** (1 hour)
- [x] Modify `addons/blender-wfc/wfc_blender_adapter.py`:
  - [x] Add `_get_cell_size()` helper — reads from first module, fallback 8.0
  - [x] Update `create_blender_visualization_grid()` → `_get_cell_size()`
  - [x] Update `create_blender_object_for_cell()` → `wfc_module.physical_size`
  - [x] Update building plot coordinate conversion → `blender_module.physical_size`
  - [x] Update `_calculate_island_grid_size()` → `_get_cell_size()`
  - [x] Remove `module_size` import
- [x] Modify `addons/blender-wfc/wfc_classes.py`:
  - [x] Update `WFCPlot.get_world_bounds()` → `cell_size=8.0` parameter
  - [x] Remove `module_size` import
- [x] Modify `addons/blender-wfc/wfc_plots.py`:
  - [x] Building plot faces and world pos → `cell_size = module.physical_size`
  - [x] Remove `module_size` import
- [x] Zero live `module_size` references remaining (definition stays in `wfc_values.py`)
- [ ] Test: Grid cells sized correctly (Blender)

**Task 2B.3: Deprecate wfc_values.py Globals** (30 min)
- [x] Modify `addons/blender-wfc/wfc_values.py`:
  - [x] Remove unused `import bpy`
  - [x] Add `GridCategory` class with string constants
  - [x] Create `DEFAULT_GRID_SIZES` dict (outer_grid=8.0, building=2.0, park=1.0, road_detail=4.0)
  - [x] Mark `module_size` and `primitive_offset_x` as DEPRECATED with comments
  - [x] `module_size` derived from `DEFAULT_GRID_SIZES` (single source of truth)
  - [x] Verified sync with `VALID_CATEGORIES` and `GRID_CATEGORIES` in other files
- [x] Test: 28/28 checks pass

---

### **MILESTONE 3: UI & Workflow** (3-4 hours)

**Goal:** Users can assign and manage metadata via UI

---

#### **Phase 3A: Update Primitive UI** (2-3 hours)

**Task 3A.1: Add Sizing & Symmetry Metadata to Primitive Operator** (3 hours)

*Step 1: Extend PrimitiveData with rotation_invariant field*
- [x] Modify `addons/blender-wfc/primitive_data_core.py`:
  - [x] Add `rotation_invariant: bool = False`
  - [x] Update `validate()` (type check)
  - [x] Update `to_dict()` / `from_dict()` with backward-compatible default
- [x] Update `tests/test_primitive_data.py` with new field tests

*Step 2: Register new Object properties in __init__.py*
- [x] Modify `addons/blender-wfc/__init__.py` `register()`:
  - [x] `bpy.types.Object.physical_size` as `FloatProperty`
  - [x] `bpy.types.Object.grid_category` as `EnumProperty`
  - [x] `bpy.types.Object.resolution_multiplier` as `IntProperty`
  - [x] `bpy.types.Object.rotation_invariant` as `BoolProperty`
- [x] Modify `unregister()`:
  - [x] Delete all 4 new properties

*Step 3: Update OBJECT_OT_WFCAssignConnectors operator*
- [x] Modify `addons/blender-wfc/primitive_ui.py`:
  - [x] Add operator properties:
    - [x] `physical_size: FloatProperty`
    - [x] `grid_category: EnumProperty` (outer_grid, building, park, road_detail)
    - [x] `resolution_multiplier: IntProperty`
    - [x] `rotation_invariant: BoolProperty`
  - [x] Update `invoke()` to pre-populate all 4 fields from object
  - [x] Update `draw()` with sizing + symmetry section
  - [x] Add auto-calculate helper (physical_size = 8.0 / resolution_multiplier)
  - [x] Update `execute()` to write all 4 fields to object properties

*Step 4: Update PrimitiveAdapter*
- [x] Modify `addons/blender-wfc/primitive_adapter.py`:
  - [x] Extract `rotation_invariant` from `obj.rotation_invariant`
  - [x] Apply `rotation_invariant` to created objects
  - [x] Switched existing 3 fields from dict-style to registered-property access

- [ ] Test: Can assign all metadata via dialog
- [ ] Test: Values persist on object after dialog closes
- [ ] Test: Pre-population shows correct values on re-open

**Task 3A.2: Update Panel Display** (1 hour)
- [ ] Modify `OBJECT_PT_WFCPrimitiveBuilderPanel`:
  - [ ] Show current size metadata (read-only)
  - [ ] Display grid category
  - [ ] Display physical size and resolution
- [ ] Test: Panel shows metadata correctly

---

#### **Phase 3B: UI Polish & Fixes** (1 hour)

**Task 3B.1: Fix Load Button Availability** (30 min)
- [ ] Modify `primitive_ui.py`:
  - [ ] Move "Load from JSON" button before object check
  - [ ] Always available regardless of selection
- [ ] Test: Can load primitive without selecting object

**Task 3B.2: Add Helper Functions** (30 min)
- [ ] Add utility functions:
  - [ ] `get_primitives_by_category(category)` - Filter primitives
  - [ ] `calculate_cell_size(physical_size, resolution)` - Helper
- [ ] Test: Helper functions work correctly

---

### **MILESTONE 4: Testing & Validation** (2-3 hours)

**Goal:** Verify system works end-to-end with no hardcoded values

---

#### **Phase 4A: Core System Testing** (1-2 hours)

**Task 4A.1: Recreate Hardcoded Primitives** (1 hour)
- [ ] Create primitives matching `primitive_data_actual.py`:
  - [ ] Building primitive (8m, outer_grid, resolution=1)
  - [ ] Road primitive (8m, outer_grid, resolution=1)
  - [ ] Pavement primitive (8m, outer_grid, resolution=1)
  - [ ] Corner primitive (8m, outer_grid, resolution=1)
- [ ] Assign all metadata via UI
- [ ] Save to `data/outer_grid_library.json`
- [ ] Test: Load and verify geometry identical

**Task 4A.2: Test Full Outer Grid Workflow** (1 hour)
- [ ] Load outer grid primitives
- [ ] Build primitives collection
- [ ] Generate modules
- [ ] Build grid (e.g., 5x5)
- [ ] Collapse grid
- [ ] Verify:
  - [ ] No errors
  - [ ] Modules positioned correctly
  - [ ] Connectors match correctly
  - [ ] Grid cells are 8m × 8m
  - [ ] NO `module_size` used anywhere

---

#### **Phase 4B: Multi-Grid Testing** (1 hour)

**Task 4B.1: Create Building Primitives** (30 min)
- [ ] Create test building primitive:
  - [ ] physical_size = 2.0
  - [ ] grid_category = "building"
  - [ ] resolution_multiplier = 4
  - [ ] Connectors: WALL, DOOR, WINDOW
- [ ] Save to `data/building_library.json`
- [ ] Load and verify

**Task 4B.2: Test Building Module Generation** (30 min)
- [ ] Load building primitives
- [ ] Generate building modules
- [ ] Verify:
  - [ ] Modules positioned at 2m spacing
  - [ ] Different from outer grid modules
  - [ ] Metadata preserved
- [ ] (Inner grid integration deferred to MILESTONE 5)

---

### **MILESTONE 5: Inner Grid Integration** (Optional - 5-8 hours)

**Goal:** Building inner grids work with new metadata system

---

#### **Phase 5A: Primitive Library Management** (2-3 hours)

**Task 5A.1: Category-Based Library System** (2 hours)
- [ ] Modify `primitive_persistence.py`:
  - [ ] `save_primitives_library_by_category()`
  - [ ] `load_primitives_by_category()`
  - [ ] Filter by grid_category
- [ ] Create library structure:
  - [ ] `data/outer_grid_library.json`
  - [ ] `data/building_library.json`
  - [ ] `data/park_library.json`

**Task 5A.2: Library UI Operators** (1 hour)
- [ ] Create `OBJECT_OT_WFCLoadPrimitiveLibrary`
- [ ] Create `OBJECT_OT_WFCSavePrimitiveLibrary`
- [ ] Add to panel with category selection

---

#### **Phase 5B: Module Generation Refactoring** (1-2 hours)

**Task 5B.1: Create Category-Specific Generators** (1-2 hours)
- [ ] Add `generate_building_modules()` to `__init__.py`
- [ ] Add `generate_park_modules()` to `__init__.py`
- [ ] Refactor common logic
- [ ] Store in categorized collections

---

#### **Phase 5C: Inner Grid Workflow Integration** (2-3 hours)

**Task 5C.1: Update BlenderWFCAdapter for Inner Grids** (2 hours)
- [ ] Add `get_modules_for_category(category)` method
- [ ] Update `create_inner_grid_for_island()`:
  - [ ] Accept `category` parameter
  - [ ] Auto-load modules if not provided
  - [ ] Use correct `physical_size` for grid

**Task 5C.2: Update Building Plot Operators** (1 hour)
- [ ] Auto-generate building modules if needed
- [ ] Pass building modules to inner grid creation
- [ ] Test full building generation workflow

---

## 📊 Updated Time Estimates

| Milestone | Phases | Total Time | Priority |
|-----------|--------|------------|----------|
| **M1: Core Metadata** | 1A, 1B, 1C | 6-8 hours | **Critical** |
| **M2: Dynamic Sizing** | 2A, 2B | 4-6 hours | **Critical** |
| **M3: UI & Workflow** | 3A, 3B | 3-4 hours | **Critical** |
| **M4: Testing** | 4A, 4B | 2-3 hours | **Critical** |
| **M5: Inner Grid** | 5A, 5B, 5C | 5-8 hours | Optional |
| **TOTAL (MVP)** | M1-M4 | **15-21 hours** | |
| **TOTAL (Full)** | M1-M5 | **20-29 hours** | |

---

## ✅ Success Criteria by Milestone

### **Milestone 1 Success Criteria**
- [ ] PrimitiveData has sizing fields with validation
- [ ] Connector registry loads from JSON
- [ ] `sockets_match()` uses registry
- [ ] Existing primitives still work
- [ ] Tests pass

### **Milestone 2 Success Criteria**
- [ ] Connector enums generated from registry
- [ ] Module generation reads `physical_size` from primitives
- [ ] Grid cells sized dynamically (no `module_size` global)
- [ ] Can generate modules with different sizes
- [ ] Tests pass

### **Milestone 3 Success Criteria**
- [ ] UI can assign sizing metadata
- [ ] UI can assign connectors filtered by category
- [ ] Load button always available
- [ ] Panel displays metadata
- [ ] User can create primitive with full metadata

### **Milestone 4 Success Criteria**
- [ ] Can recreate hardcoded primitives from JSON
- [ ] Outer grid workflow works end-to-end
- [ ] Building primitives (2m) can be created and saved
- [ ] NO hardcoded values used in critical paths
- [ ] Full system validation complete

### **Milestone 5 Success Criteria (Optional)**
- [ ] Library management by category works
- [ ] Building modules generate correctly
- [ ] Inner grid uses building modules
- [ ] Building islands collapse with inner grids
- [ ] Multi-grid system fully functional

---

## 🎯 Immediate Next Steps

**START HERE: Task 1A.1** ⭐ (Marked in schedule above)

This is the foundation for everything else. Here's exactly what to do:

### **Step 1: Add 3 fields to PrimitiveData** (30-45 min)

**File:** `addons/blender-wfc/primitive_data_core.py`

**Add these fields:**
```python
@dataclass
class PrimitiveData:
    # ... existing fields (name, primitive_type, verts, etc.) ...

    # NEW: Physical size metadata
    physical_size: float = 8.0
    """Physical size of this primitive in meters"""

    grid_category: str = "outer_grid"
    """Which grid system: 'outer_grid', 'building', 'park', etc."""

    resolution_multiplier: int = 1
    """How many cells fit in one outer grid cell"""
```

**Update validation, to_dict(), and from_dict()** as shown in design docs.

### **Step 2: Test immediately** (15 min)

Create a test primitive with metadata, validate, serialize, and deserialize.

### **Step 3: Continue to Task 1A.2**

Update tests and serialization, then move to PrimitiveAdapter updates.

---

**See schedule above for complete task breakdown!** 🚀
