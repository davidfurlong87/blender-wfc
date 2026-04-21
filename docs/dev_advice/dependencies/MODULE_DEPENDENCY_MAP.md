# Module Dependency Map

This document shows the dependency relationships between all modules in the addon.

## Visual Dependency Tree

```
Level 0 (Foundation - No Internal Dependencies)
├── wfc_values.py
│   └── Exports: CollectionNames, module_size, bl_category_name, primitive_offset_x
│
└── wfc_enums.py
    └── Exports: CONNECTORS, PRIMITIVE_TYPES, CUSTOM_PRIMITIVE_TYPES, PrimitiveModules

Level 1 (Depends on Level 0 only)
├── wfc_materials.py
│   ├── Imports: (none from addon)
│   └── Exports: MaterialPrimitives, build_all_primitive_materials
│
└── collectiontools/collection_creation.py
    ├── Imports: (none from addon)
    └── Exports: get_collection_by_name, link_object_to_single_collection, etc.

Level 2 (Depends on Level 0-1)
├── wfc_classes.py
│   ├── Imports: collectiontools.collection_creation, wfc_values
│   └── Exports: WFCModule, WFCCell, Primitive, Axis, build_module_pairs
│
├── primitive_generation_tools.py
│   ├── Imports: wfc_enums
│   └── Exports: get_primitive_type_items, mesh_to_mesh_data, capture_vertex_groups
│
└── helper_functions.py
    ├── Imports: wfc_values, collectiontools.collection_creation
    └── Exports: (commented out functions)

Level 3 (Depends on Level 0-2)
├── primitive_data_actual.py
│   ├── Imports: wfc_classes, wfc_materials, wfc_enums
│   └── Exports: building_primitive_alt, corner_primitive_alt, pavement_primitive_alt
│
├── wfc_grid_builder.py
│   ├── Imports: wfc_classes, collectiontools.collection_creation, wfc_values
│   └── Exports: build_wfc_grid, GridParameters
│
├── wfc_plots.py
│   ├── Imports: wfc_classes, wfc_values
│   └── Exports: extract_building_plots_from_cell, group_adjacent_building_plots
│
└── wfc_plot_tools.py
    ├── Imports: (commented out)
    └── Exports: (commented out)

Level 4 (Depends on Level 0-3)
├── primitive_data.py
│   ├── Imports: wfc_enums, wfc_classes, wfc_materials, wfc_values,
│   │           primitive_generation_tools, primitive_data_actual
│   └── Exports: build_default_primitives, PrimitiveModules, PRIMITIVE_OPERATORS, PRIMITIVE_PANELS
│
├── wfc_collections.py
│   ├── Imports: wfc_values, collectiontools.collection_creation
│   └── Exports: COLLECTION_PANELS, COLLECTION_OPERATORS
│
└── wfc_operators.py
    ├── Imports: (minimal)
    └── Exports: (operators)

Level 5 (__init__.py - The Orchestrator)
└── __init__.py
    ├── Imports: ALL of the above
    └── Exports: Registers all classes, operators, panels
```

## Dependency Rules

### Rule 1: Lower levels cannot import from higher levels
❌ **WRONG:** `wfc_values.py` importing from `wfc_classes.py`
✅ **RIGHT:** `wfc_classes.py` importing from `wfc_values.py`

### Rule 2: Same-level imports are allowed but be careful
⚠️ **CAUTION:** If two Level 2 modules import from each other, you have a circular dependency

### Rule 3: Skip levels freely
✅ **OK:** Level 4 module can import from Level 0, 1, 2, or 3

## Adding a New Module Checklist

- [ ] Identify all addon modules you need to import from
- [ ] Find the highest level among your dependencies
- [ ] Place your module at (highest dependency level + 1)
- [ ] Add reload entry in `__init__.py` at your level
- [ ] Add import statement after the reload block
- [ ] Test the reload works

## Circular Dependency Detection

If you get import errors, you might have a circular dependency:

```
Module A imports Module B
Module B imports Module A
```

**Solutions:**
1. Move shared code to a lower-level module
2. Use late imports (import inside functions, not at module level)
3. Restructure to break the cycle

## Module Purposes Quick Reference

| Module | Purpose |
|--------|---------|
| `wfc_values` | Constants and configuration values |
| `wfc_enums` | Enumerations for connectors, primitive types |
| `wfc_materials` | Material creation and management |
| `collection_creation` | Blender collection utilities |
| `wfc_classes` | Core WFC data structures (Module, Cell, Primitive) |
| `primitive_generation_tools` | Mesh data extraction utilities |
| `primitive_data_actual` | Hardcoded primitive geometry definitions |
| `wfc_grid_builder` | Grid initialization logic |
| `wfc_plots` | Building plot extraction and grouping |
| `primitive_data` | Primitive management UI and operators |
| `wfc_collections` | Collection management UI |
| `wfc_operators` | WFC operators (currently minimal) |
| `__init__.py` | Addon registration and main WFC algorithm |

## When to Create a New Module

**Create a new module when:**
- You have a cohesive set of related functions (>100 lines)
- You want to separate concerns (UI vs logic)
- Multiple other modules need the same functionality

**Don't create a new module when:**
- It's just 1-2 small functions (add to existing module)
- It would create circular dependencies
- It's tightly coupled to one specific module (add it there)

