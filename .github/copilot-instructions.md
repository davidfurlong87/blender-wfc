# Copilot Instructions for blender-wfc

## Project Overview
This repository is a Blender addon implementing Wave Function Collapse (WFC) algorithms for procedural generation. The codebase is organized for Blender integration, with core logic and UI components in Python.

## Key Directories & Files
- `addons/blender-wfc/`: Main addon code
  - `wfc_classes.py`, `wfc_collections.py`, `wfc_values.py`: Core WFC logic and data structures
  - `wfc_tools.py`, `primitive_generation.py`, `materials.py`: Generation, manipulation, and material assignment
  - `wfc_ui_panel.py`: Blender UI integration
  - `debug_tools.py`: Debugging utilities
  - `collectiontools/collection_creation.py`: Collection management helpers
  - `__init__.py`: Registers Blender addon modules
- `.blend` files: Example Blender projects for development/testing

## Architecture & Data Flow
- **Modular Design:** Each file encapsulates a distinct aspect of the addon (UI, generation, data, debugging).
- **Blender API Integration:** All code interacts with Blender via its Python API (`bpy`). Registration and property definitions are handled in `__init__.py` and `gennerateProps.py`.
- **WFC Algorithm:** Core logic is in `wfc_classes.py` and related files. Data flows from Blender scene/collections to WFC logic, then results are applied back to Blender objects.

## Developer Workflows
- **Addon Installation:** Copy `addons/blender-wfc/` into Blender's addons directory, or use the `.blend` files for direct testing.
- **Debugging:** Use `debug_tools.py` for logging and inspection. Print statements and Blender's console are primary debugging tools.
- **Testing:** No formal test suite detected. Manual testing is done via Blender UI and example `.blend` files.
- **Reloading:** After code changes, reload the addon in Blender (disable/enable in Addons panel).

## Project-Specific Conventions
- **Naming:** Files and classes use `wfc_` prefix for clarity.
- **Properties:** Custom Blender properties are defined in `gennerateProps.py` and registered in `__init__.py`.
- **Collections:** Collection management is abstracted in `collectiontools/collection_creation.py` and `wfc_collections.py`.
- **Debugging:** Use `debug_tools.py` for any logging or inspection needs.

## Integration Points
- **Blender Python API (`bpy`)**: All external integration is through Blender's scripting API.
- **No external Python dependencies** detected beyond Blender's standard library.

## Example Patterns
- Registering a class:
  ```python
  bpy.utils.register_class(MyClass)
  ```
- Defining a custom property:
  ```python
  bpy.types.Object.my_prop = bpy.props.IntProperty(name="My Prop")
  ```
- Accessing collections:
  ```python
  bpy.data.collections['CollectionName']
  ```

## Recommendations for AI Agents
- Always reload the Blender addon after making code changes.
- Use the provided `.blend` files for manual testing and debugging.
- Follow the modular structure: keep UI, logic, and data definitions separate.
- Reference `debug_tools.py` for any debugging or logging additions.

---
*Update this file as project conventions evolve. For questions, review the source files listed above.*
