# Architecture Documentation

This directory contains documentation for architectural improvements to the Blender WFC addon.

## Overview

The goal is to separate the pure WFC algorithm logic from Blender-specific code, creating a clean 3-layer architecture:

1. **Pure Algorithm Layer** - WFC algorithm with no Blender dependencies
2. **Adapter Layer** - Converts between Blender and algorithm
3. **UI Layer** - Blender operators and panels

## Documentation Files

### 📘 [ALGORITHM_SEPARATION_GUIDE.md](ALGORITHM_SEPARATION_GUIDE.md)
**Comprehensive guide on separating algorithm from Blender**

**Key sections:**
- **The Golden Rule:** "Algorithm logic should work without Blender"
- **Why Separate?** - Benefits and current problems
- **The Separation Pattern** - 3-layer architecture explained
- **Current State Analysis** - What's already separated vs what's mixed
- **Migration Strategy** - 4-phase plan
- **Example: Separating collapse_cell()** - Before/after comparison
- **Testing Strategy** - How to test pure algorithm
- **Common Pitfalls** - What to avoid

**Read this first** to understand the overall approach.

---

### 🚀 [QUICK_START_SEPARATION.md](QUICK_START_SEPARATION.md)
**Practical step-by-step guide for migration**

**Key sections:**
- **The Simple Rule:** "If it doesn't need `import bpy`, it shouldn't have `import bpy`"
- **5-Step Migration Process:**
  1. Identify what to separate
  2. Create pure algorithm module
  3. Create pure data classes
  4. Create Blender adapter
  5. Update operators to use adapter
- **Migration Checklist** - For each function/class
- **Common Scenarios** - Real examples with solutions
- **Testing Your Separation** - 3 tests to verify success
- **Troubleshooting** - Common problems and fixes

**Use this** when actually implementing the separation.

---

## Quick Reference

### When in Doubt...

> **"Algorithm logic should work without Blender. If you can't test it in a plain Python script, it's too coupled."**

### The 3 Layers

```
┌─────────────────────────────────────┐
│  Layer 3: Blender UI (Operators)    │  ← User interaction
│  - OBJECT_OT_FullCollapse           │  ← Button clicks
│  - OBJECT_OT_DebugCollapse          │  ← UI feedback
└─────────────────────────────────────┘
              ↓ calls
┌─────────────────────────────────────┐
│  Layer 2: Blender Adapter           │  ← Translation layer
│  - BlenderWFCAdapter                │  ← Blender ↔ Algorithm
│  - setup_from_blender()             │  ← Visualization
│  - collapse_cell_and_visualize()    │
└─────────────────────────────────────┘
              ↓ calls
┌─────────────────────────────────────┐
│  Layer 1: Pure Algorithm            │  ← Pure WFC logic
│  - WFCAlgorithm                     │  ← No Blender imports
│  - collapse_cell()                  │  ← Unit testable
│  - propagate()                      │  ← Reusable
└─────────────────────────────────────┘
```

### Quick Decision Tree

**Is this function doing WFC algorithm logic?**
- YES → Put in Layer 1 (Pure Algorithm)
- NO → Continue...

**Is this function creating/modifying Blender objects?**
- YES → Put in Layer 2 (Adapter)
- NO → Continue...

**Is this function handling user interaction?**
- YES → Put in Layer 3 (Operators)
- NO → Re-evaluate what it's doing

---

## Current State

### ✅ Already Pure (No changes needed)

- `build_module_score()` - Pure function
- `get_lowest_entropy_cells()` - Pure function
- `build_module_pairs()` - Pure function
- `Primitive` class - Pure data
- `Axis` enum - Pure data

### ❌ Mixed (Needs separation)

- `collapse_cell()` - Algorithm + Blender mixed
- `propagate()` - Algorithm + Blender mixed
- `collapse_process()` - Algorithm + Blender mixed
- `WFCCell` class - Has `mesh_obj` attribute
- `WFCModule` class - Has `obj_source` attribute
- `WFCCell.remove_invalid_modules()` - Updates Blender object
- `WFCCell.replace_mesh_obj()` - Calls Blender functions

---

## Migration Plan

### Phase 1: Extract Pure Algorithm ✅ Low Risk
**Goal:** Create pure algorithm layer without breaking existing code

**Tasks:**
- [ ] Create `wfc_algorithm/` module structure
- [ ] Copy algorithm functions to new module
- [ ] Remove Blender dependencies from copies
- [ ] Write unit tests for pure algorithm
- [ ] Verify tests pass without Blender

**Estimated effort:** 2-4 hours

---

### Phase 2: Create Adapter Layer ⚠️ Medium Risk
**Goal:** Create Blender adapter that uses pure algorithm

**Tasks:**
- [ ] Create `wfc_blender_adapter.py`
- [ ] Implement Blender → Algorithm conversion
- [ ] Implement Algorithm → Blender conversion
- [ ] Implement visualization functions
- [ ] Test adapter with simple cases

**Estimated effort:** 3-5 hours

---

### Phase 3: Migrate Operators ⚠️ Medium Risk
**Goal:** Update operators to use adapter instead of mixed code

**Tasks:**
- [ ] Update `OBJECT_OT_FullCollapse`
- [ ] Update `OBJECT_OT_DebugCollapse`
- [ ] Update `OBJECT_OT_BuildWFCGrid`
- [ ] Test each operator after migration
- [ ] Verify functionality unchanged

**Estimated effort:** 2-3 hours

---

### Phase 4: Clean Up ✅ Low Risk
**Goal:** Remove old mixed code

**Tasks:**
- [ ] Remove old algorithm functions from `__init__.py`
- [ ] Update `WFCCell` to be pure
- [ ] Update `WFCModule` to be pure
- [ ] Remove global state
- [ ] Update documentation

**Estimated effort:** 1-2 hours

---

## Benefits After Separation

### ✅ Testability
```python
# Can test algorithm without Blender!
from wfc_algorithm.core import WFCAlgorithm

algo = WFCAlgorithm(modules=['A', 'B', 'C'], grid_size=(10, 10))
algo.collapse_cell(0, 0)
assert algo.grid.get_cell(0, 0).is_collapsed
```

### ✅ Reusability
```python
# Can use algorithm in CLI tool
from wfc_algorithm.core import WFCAlgorithm

algo = WFCAlgorithm(modules=load_modules(), grid_size=(50, 50))
algo.collapse_all()
export_to_json(algo.grid)
```

### ✅ Performance Profiling
```python
# Can profile pure algorithm without Blender overhead
import cProfile
from wfc_algorithm.core import WFCAlgorithm

profiler = cProfile.Profile()
profiler.enable()
algo.collapse_all()
profiler.disable()
# Pure algorithm performance, no Blender noise!
```

### ✅ Flexibility
```python
# Can swap visualization layer
# Blender, Godot, Unity, web canvas, etc.
from wfc_algorithm.core import WFCAlgorithm
from godot_adapter import GodotWFCAdapter  # Different adapter!

algo = WFCAlgorithm(modules=..., grid_size=...)
adapter = GodotWFCAdapter(algo)
adapter.visualize_all()
```

---

## Related Documentation

- `../performance/PERFORMANCE_OPTIMIZATION_GUIDE.md` - Performance optimization strategies
- `../dependencies/MODULE_RELOADING_GUIDE.md` - Module reload system
- `../../PROJECT_OVERVIEW.md` - Project goals and overview

