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

## 📅 Implementation Schedule

### **Phase 1: Foundation (3-4 hours)**

#### **Task 1.1: Create ConnectorRegistry** (2 hours)
- [ ] Create `connector_registry.py`
  - [ ] `ConnectorDefinition` dataclass
  - [ ] `ConnectorRegistry` class
  - [ ] `matches()` method
  - [ ] JSON serialization
- [ ] Create `data/connectors.json` with defaults
- [ ] Test: Load and query registry

#### **Task 1.2: Add Sizing to PrimitiveData** (1 hour)
- [ ] Add fields to `primitive_data_core.py`:
  - [ ] `physical_size: float = 8.0`
  - [ ] `grid_category: str = "outer_grid"`
  - [ ] `resolution_multiplier: int = 1`
- [ ] Update `validate()` method
- [ ] Update `to_dict()` and `from_dict()`
- [ ] Test: Create primitive with metadata, serialize, deserialize

#### **Task 1.3: Update Tests** (30 min)
- [ ] Add tests for new fields
- [ ] Test validation
- [ ] Test JSON round-trip

---

### **Phase 2: Integration (3-4 hours)**

#### **Task 2.1: Replace Hardcoded Socket Matching** (1 hour)
- [ ] Update `wfc_classes.sockets_match()`:
  ```python
  def sockets_match(socket_a, socket_b):
      from .connector_registry import connector_registry
      return connector_registry.matches(socket_a, socket_b)
  ```
- [ ] Update `wfc_blender_adapter._sockets_match()` similarly
- [ ] Test: Verify existing primitives still work

#### **Task 2.2: Update Enums to Use Registry** (1 hour)
- [ ] Modify `wfc_enums.py`:
  - [ ] `get_connector_enum_items()` function
  - [ ] Dynamic `CONNECTORS` generation
- [ ] Update `__init__.py` property registration
- [ ] Test: Connectors appear in UI

#### **Task 2.3: Refactor Module Generation** (2 hours)
- [ ] Update `generate_modules_from_primitives()`:
  - [ ] Read `physical_size` from primitive
  - [ ] Calculate offset dynamically
  - [ ] No `module_size` global usage
- [ ] Update `BlenderWFCAdapter.create_blender_object_for_cell()`:
  - [ ] Use module's `physical_size`
  - [ ] Dynamic cell placement
- [ ] Test: Generate modules from primitives

---

### **Phase 3: UI & Polish (2-3 hours)**

#### **Task 3.1: Update Primitive UI** (2 hours)
- [ ] Modify `OBJECT_OT_WFCAssignConnectors`:
  - [ ] Add `physical_size` field
  - [ ] Add `grid_category` enum
  - [ ] Add `resolution_multiplier` field
  - [ ] Auto-calculate helper display
- [ ] Update panel to show metadata
- [ ] Test: Assign metadata via UI

#### **Task 3.2: Deprecate Hardcoded Values** (30 min)
- [ ] Update `wfc_values.py`:
  - [ ] Add deprecation comments
  - [ ] Add `GridCategory` class
  - [ ] Add `DEFAULT_GRID_SIZES` dict
- [ ] Verify backward compatibility

#### **Task 3.3: Create Default Connector Library** (30 min)
- [ ] Populate `data/connectors.json` with:
  - [ ] ROAD, BUILDING, PAVEMENTPOS, PAVEMENTNEG (outer_grid)
  - [ ] WALL, DOOR, WINDOW, HALLWAY (building)
- [ ] Add load function in `__init__.py`

---

### **Phase 4: Testing & Validation (2 hours)**

#### **Task 4.1: Recreate Hardcoded Primitives** (1 hour)
- [ ] Create primitives matching `primitive_data_actual.py`
- [ ] Assign all metadata (size, category, connectors)
- [ ] Save to JSON
- [ ] Load from JSON
- [ ] Verify geometry matches

#### **Task 4.2: Test Full Workflow** (1 hour)
- [ ] Create outer grid primitive (8m)
- [ ] Save to `outer_grid_library.json`
- [ ] Load library
- [ ] Generate modules
- [ ] Build grid
- [ ] Collapse grid
- [ ] Verify NO hardcoded values used

---

## ✅ Success Criteria

**System is complete when:**

- [ ] Can create primitive with metadata in UI
- [ ] All metadata saved to JSON
- [ ] Load primitive from JSON with all metadata
- [ ] Generate modules using primitive's `physical_size`
- [ ] Grid uses dynamic cell sizing
- [ ] Connector matching uses registry only
- [ ] Can add new connector without code change
- [ ] Can support building grid (2m) alongside outer grid (8m)
- [ ] NO references to global `module_size` in critical paths
- [ ] NO hardcoded connector rules in code

---

## 📊 Time Estimate Summary

| Phase | Tasks | Estimated Time |
|-------|-------|----------------|
| **Phase 1** | Foundation | 3-4 hours |
| **Phase 2** | Integration | 3-4 hours |
| **Phase 3** | UI & Polish | 2-3 hours |
| **Phase 4** | Testing | 2 hours |
| **Total** | | **10-13 hours** |

---

## 🎯 Immediate Next Steps

**Start with Phase 1, Task 1.2** (Easiest first):

```python
# addons/blender-wfc/primitive_data_core.py

@dataclass
class PrimitiveData:
    # ... existing fields ...
    
    # NEW: Sizing metadata
    physical_size: float = 8.0
    grid_category: str = "outer_grid"
    resolution_multiplier: int = 1
```

**Estimated time: 30 minutes**

Then continue with Task 1.1 (ConnectorRegistry), then integration.

---

**Ready to start?** I recommend beginning with the primitive sizing (Task 1.2) since it's the quickest win and gives immediate value!
