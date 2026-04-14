# Blender WFC - Wave Function Collapse Addon

## Project Vision

Create a high-performance, well-structured Blender addon that enables procedural environment generation using the Wave Function Collapse (WFC) algorithm. The goal is to allow users to create a small set of modular 3D models and automatically generate complete, coherent worlds from them.

## Core Goals

### 1. **Flexibility & Modularity**
- Quick and easy transition between different model sets
- Support for user-created primitives alongside default ones
- Extensible connector and primitive type systems
- Easy import/export of primitive definitions

### 2. **Performance**
- Efficient WFC algorithm implementation
- Optimized mesh generation and manipulation
- Minimal overhead during collapse process
- Smart caching of computed data (e.g., building plot faces)

### 3. **Code Quality**
- Clean, maintainable architecture
- Clear separation of concerns
- Well-documented code
- Consistent naming conventions
- Proper error handling

## Current Architecture

### Data Flow Pipeline

```
User Models → Primitives → Modules → Grid Cells → Collapsed World
```

1. **Primitives**: Base building blocks with connection rules
   - Defined geometry (vertices, faces, materials)
   - Connector types on each edge (POS_X, NEG_X, POS_Y, NEG_Y)
   - Vertex groups for special features (building plots, etc.)
   - Primitive type classification

2. **Modules**: Rotational variants of primitives
   - 4 rotations (0°, 90°, 180°, 270°) generated per primitive
   - Connector compatibility pairs calculated
   - Module weights for probability control
   - Cached building plot data

3. **Grid Cells**: WFC state containers
   - List of possible modules (entropy)
   - Collapse state (collapsed/uncollapsed)
   - Spatial coordinates
   - Visual debug representation

4. **Collapse Process**: WFC algorithm execution
   - Entropy-based cell selection (lowest entropy first)
   - Weighted random module selection
   - Constraint propagation to neighbors
   - Iterative until all cells collapsed

### Key Components

#### Core Classes (`wfc_classes.py`)
- `Primitive`: Stores primitive geometry and metadata
- `WFCModule`: Rotated module with connector pairs
- `WFCCell`: Grid cell with possible modules
- `WFCPlot` / `BuildingPlot`: Special plot areas for nested generation
- `Axis`: Enum for directional operations

#### Connector System (`wfc_enums.py`)
- Defines how modules can connect to each other
- Current types: ROAD, BUILDING, PAVEMENTPOS, PAVEMENTNEG
- Extensible for new connection types

#### Primitive Management
- `primitive_data.py`: Primitive definitions and operators
- `primitive_data_actual.py`: Hardcoded primitive geometry
- `primitive_generation_tools.py`: Mesh data extraction utilities

#### Grid & Collapse
- `wfc_grid_builder.py`: Grid initialization
- `__init__.py`: Main collapse algorithm and propagation logic

#### Collections System
- Organized Blender collections for different data types
- WFC_Primitives, WFC_Modules, WFC_Grid, WFC_Debug

### Advanced Features

#### Building Plots
- Vertex groups define special areas within primitives
- Building plot faces cached per module
- Support for nested WFC generation (buildings on plots)
- Plot grouping for multi-cell structures

## Known Issues & TODOs

### Architecture Improvements Needed
- [ ] Separate algorithm logic from Blender UI code (See `docs/architecture/ALGORITHM_SEPARATION_GUIDE.md`)
  - [x] **Phase 1: Extract Pure Algorithm** ✅ (See `addons/blender-wfc/wfc_algorithm/README.md`)
    - Created pure algorithm module with no Blender dependencies
    - 33 unit tests pass without Blender
    - Extracted: WFCAlgorithm, Grid, AlgorithmCell, AlgorithmModule
  - [x] **Phase 2: Create Blender Adapter** ✅ (Code Complete - Testing Pending) (See `docs/architecture/PHASE_2_COMPLETE.md`)
    - Created `wfc_blender_adapter.py` (416 lines)
    - Updated 4 operators to use adapter
    - Added 10 TODOs for future refinement
    - Ready for testing in Blender
  - [x] Phase 3: Migrate Operators (if any remaining)
  - [x] Phase 4: Clean Up Old Code
- [x] Move global state (`all_modules`, `all_grid_cells`) into proper data structures ✅
  - Encapsulated in `Grid` class in pure algorithm module
- [ ] Implement proper error handling and validation
- [ ] Create consistent API for primitive import/export
- [x] Refactor module reload system in `__init__.py` ✅ (See `docs/dependencies/MODULE_RELOADING_GUIDE.md`)
- [ ] Add something like 'isSymmetrical' as a parameter for primitives. If that object is 'symmetrical' it will look the same in all four rotations, and should only have a single module made of it (and not four identical rotations)

### Performance Optimizations
- [ ] Profile collapse process for bottlenecks
- [x] Optimize mesh duplication during collapse ✅ (See `docs/performance/MESH_DUPLICATION_ANALYSIS.md`)
- [ ] Consider lazy mesh generation (only create visible cells)
- [ ] Cache connector pair calculations

### Feature Gaps
- [ ] User primitive workflow incomplete
- [ ] No save/load for generated worlds
- [ ] Limited 3D support (currently 2D grid)
- [ ] No undo support for collapse operations
- [x] **Building plot generation - Phase 1 Complete** ✅ (See `docs/features/BUILDING_PLOT_GENERATION.md`)
  - Generic plot extraction from collapsed outer grid
  - Island grouping with flood-fill algorithm
  - Inner grid creation with configurable resolution
  - Debug visualization working
  - **Next:** Phase 3 - Create building primitives and implement inner grid WFC collapse

### Code Quality
- [ ] Inconsistent naming (posX/posY vs x/y)
- [ ] Magic numbers throughout (replace with constants)
- [ ] Typos in method names (`get_all_pairs_fox_axis`)
- [ ] TODO comments need addressing
- [ ] Missing docstrings on many functions

### Future Testing
- [ ] Lots of hardcoded terms like connectors, primitives. One change could break a lot of things. Need a test for this stuff to make sure everything still works.
- [ ] Add unit tests for all new functions
- [ ] Add integration tests for full pipeline
- [ ] Add UI tests for operator workflows

### Known Bugs
#### Addon Loading Error
When loading the addon the following error occurs.

```
Exception in module unregister(): '/Users/dfg03/Projects/wfc_repo/blender-wfc/addons/blender-wfc/__init__.py'
Traceback (most recent call last):
  File "/Applications/Blender.app/Contents/Resources/3.3/scripts/modules/addon_utils.py", line 421, in disable
    mod.unregister()
  File "/Users/dfg03/Projects/wfc_repo/blender-wfc/addons/blender-wfc/__init__.py", line 584, in unregister
    bpy.utils.unregister_class(r_class)
RuntimeError: unregister_class(...):, missing bl_rna attribute from 'RNAMeta' instance (may not be registered)
```
## Development Workflow

### Testing Changes
1. Modify addon code
2. Reload addon in Blender (Preferences → Add-ons → Disable/Enable "wfc")
3. Use Debug Menu to test pipeline:
   - Regen Default Primitives
   - Re/Generate Modules
   - Build Grid
   - Debug Collapse (single step) or Full Collapse

### Adding New Modules
See `docs/QUICK_START_RELOADING.md` for step-by-step guide.

**Quick version:**
1. Determine what your module imports from the addon
2. Find the reload level of your dependencies
3. Add reload entry in `__init__.py` at (max dependency level + 1)
4. Add import statement after the reload block
5. Test by disabling/enabling the addon

### Adding New Primitives
1. Create geometry in Blender
2. Assign materials
3. Set connector properties (x_pos_connector, etc.)
4. Add vertex groups for special features
5. Use "Convert to primitive" operator
6. Copy printed data to `primitive_data_actual.py`

## Future Vision

### Short Term
- Stabilize user primitive workflow
- Improve performance of collapse process
- Better error handling and user feedback
- Documentation for end users

### Medium Term
- 3D grid support (vertical stacking)
- Nested WFC for building interiors
- Constraint painting (force certain modules in areas)
- Biome/zone system for varied regions

### Long Term
- Real-time preview during collapse
- Multi-threaded collapse process
- GPU acceleration for large grids
- Integration with other procedural systems (vegetation, props)
- Export to game engines

## Current Status

**Phase 4 Complete (with known issue)** ✅⚠️

The WFC algorithm has been successfully separated from Blender UI code and all old code has been cleaned up:
- ✅ **Phase 1:** Pure algorithm module created (`wfc_algorithm/`)
- ✅ **Phase 2:** Blender adapter layer created (`wfc_blender_adapter.py`)
- ✅ **Phase 3:** All operators migrated to use adapter (8 operators)
- ✅ **Phase 4:** All orphaned code removed (~125 lines cleaned up)
- ✅ 33 unit tests passing (run without Blender in 0.001 seconds)
- ✅ Debug mesh behavior implemented (Steps 3, 4a, 4b, 4c, 5a working)
- ⚠️ **Known Issue:** Step 5b (remove debug planes after full collapse) commented out - `remove_all_debug_planes()` was removing collapsed cells along with debug planes
- ⚠️ **Known Issue:** `OBJECT_OT_DebugBuildingPlots` operator needs refactoring for new architecture
- ✅ 10+ TODOs added for future refinement

**Architecture separation is now complete!** The codebase has clean 3-layer separation with zero orphaned code.

See `docs/architecture/` for detailed documentation on each phase.

---

## Notes for AI Assistant

- Always check for existing patterns before suggesting new approaches
- Performance is critical - avoid unnecessary mesh operations
- Maintain compatibility with Blender 2.80+
- Respect the existing connector system when adding features
- Test changes with the debug operators before full collapse
- Consider both hardcoded and user-created primitive workflows

