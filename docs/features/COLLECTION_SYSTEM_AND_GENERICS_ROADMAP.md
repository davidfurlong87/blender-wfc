# Collection System & Project-Wide Generics — Implementation Roadmap

**Goal:** Remove every manual "Build Collections" requirement, replace the
flat/hardcoded collection model with a fully dynamic category-driven hierarchy,
and reduce hardcoded literals project-wide so that adding a new primitive
category requires touching as few files as possible.

**Date:** 2026-04-16
**Status:** 📋 Ready to Implement

---

## 🎯 Objectives

1. **No blockers** — A missing collection must never prevent any WFC operation.
   Every operator creates what it needs, lazily, the first time it runs.

2. **Dynamic by category** — Collection names are derived from category strings
   at call time (`"WFC_Primitives_{category}"`), not enumerated in code.
   A brand-new category self-organises the moment its library is loaded.

3. **Single module registry** — Replace parallel globals (`all_modules`,
   `all_building_modules`, …) with one `_modules_by_category` dict.

4. **No duplicated generation logic** — `generate_modules()` and
   `generate_building_modules()` become one generic function.

5. **Fewer hardcoded literals** — Category names, connector types, sizes, and
   UI labels that exist as bare strings outside data files are audited and
   moved to their canonical data source.

---

## 🗂️ Collection Tree (Target State)

```
WFC                                  ← static root (keeps outliner clean)
├── WFC_Primitives                   ← static parent, no direct objects
│   ├── WFC_Primitives_outer_grid    ← dynamic, created on first load
│   ├── WFC_Primitives_building      ← dynamic, created on first load
│   └── WFC_Primitives_{category}    ← any future category, zero code change
├── WFC_Modules                      ← static parent, no direct objects
│   ├── WFC_Modules_outer_grid       ← dynamic, created on first generation
│   ├── WFC_Modules_building         ← dynamic, created on first generation
│   └── WFC_Modules_{category}       ← any future category, zero code change
├── WFC_Grid                         ← static parent, no direct objects
│   ├── WFC_Grid_outer_grid          ← dynamic, outer collapse output
│   ├── WFC_Grid_building            ← dynamic, building inner grid output
│   ├── WFC_Grid_room_detail         ← future: inner-within-inner grid
│   └── WFC_Grid_{category}          ← any future grid level, zero code change
└── WFC_Debug                        ← static, ephemeral debug objects
```

All three branches follow the identical `_{category}` pattern.
Adding a new grid resolution — at any depth — requires no structural change:
the new category string drives everything.

**Static collections** (5 fixed names, kept in `CollectionNames`):
`WFC`, `WFC_Primitives`, `WFC_Modules`, `WFC_Grid`, `WFC_Debug`

**Dynamic collections** (never enumerated — derived at runtime via three
symmetric naming helpers):

| Helper | Output |
|--------|--------|
| `primitives_collection_for(category)` | `WFC_Primitives_{category}` |
| `modules_collection_for(category)` | `WFC_Modules_{category}` |
| `grid_collection_for(category)` | `WFC_Grid_{category}` |

---

## 📅 Phase A — Dynamic Collection System

### A1 — Simplify `CollectionNames` + naming helpers
**Files:** `addons/blender-wfc/wfc_values.py`, `addons/blender-wfc/__init__.py`,
`addons/blender-wfc/wfc_collections.py`
- [x] Removed per-category entries (`UserPrimitives`, `BuildingModules`) from `CollectionNames`
- [x] Kept exactly **5 static names**: `Root`, `Primitives`, `Modules`, `Grid`, `Debug`
- [x] Added three symmetric pure functions:
  - [x] `primitives_collection_for(category: str) -> "WFC_Primitives_{category}"`
  - [x] `modules_collection_for(category: str) -> "WFC_Modules_{category}"`
  - [x] `grid_collection_for(category: str) -> "WFC_Grid_{category}"`
- [x] Replaced `CollectionNames.BuildingModules` call sites in `__init__.py`
      with `modules_collection_for(GridCategory.BUILDING)`
- [x] Replaced `CollectionNames.UserPrimitives` in `wfc_collections.py`
      with a plain string literal (legacy, retired in A12)
- [x] Test: 35/35 checks pass (`tests/verify_task_a1.py`)

### A2 — Fix `get_or_create_collection` to accept a parent
**File:** `addons/blender-wfc/collectiontools/collection_creation.py`
- [x] Updated signature: `get_or_create_collection(name, b_delete_objects=False, parent=None)`
- [x] New collections link to `parent.children` when provided, else scene root
- [x] Existing collections returned as-is — never silently re-parented
- [x] All existing call sites (no parent arg) behaviour unchanged
- [x] Hardcoded `bpy.context.scene.collection.children.link` replaced by `attach_to.children.link`
- [x] Test: 20/20 checks pass (`tests/verify_task_a2.py`)

### A3 — Add `ensure_collection(name, parent=None)`
**Files:** `addons/blender-wfc/collectiontools/collection_creation.py`,
`addons/blender-wfc/collectiontools/__init__.py`
- [x] Added `ensure_collection(collection_name, parent=None)` after `get_or_create_collection`
- [x] Delegates to `get_or_create_collection` — no `b_delete_objects` footgun
- [x] Existing collection → returned as-is, never re-parented
- [x] Missing collection → created under `parent` (or scene root if `None`)
- [x] Guaranteed to never raise and never return `None`
- [x] Exported from `collectiontools/__init__.py` for clean package-level imports
- [x] Test: 24/24 checks pass (`tests/verify_task_a3.py`)

### A4 — Add `ensure_primitives_collection` / `ensure_modules_collection` / `ensure_grid_collection`
**File:** `addons/blender-wfc/collectiontools/__init__.py`
- [x] `ensure_primitives_collection(category)` → WFC → WFC_Primitives → WFC_Primitives_{category}
- [x] `ensure_modules_collection(category)`    → WFC → WFC_Modules    → WFC_Modules_{category}
- [x] `ensure_grid_collection(category)`       → WFC → WFC_Grid       → WFC_Grid_{category}
- [x] All three are idempotent — calling twice returns the same object, no duplicates
- [x] All three share the same `WFC` root collection (verified by test)
- [x] `ensure_grid_collection` works for any arbitrary category string (any depth)
- [x] Imported from `wfc_values` absolutely — works in both Blender and test contexts
- [x] Test: 34/34 checks pass (`tests/verify_task_a4.py`)

### A5 — Replace module globals with `_modules_by_category` dict
**File:** `addons/blender-wfc/__init__.py`
- [x] `_modules_by_category: dict = {}` declared as single source of truth
- [x] `all_modules` and `all_building_modules` are live aliases via `setdefault` — existing call sites unchanged
- [x] `get_modules_for_category(category)` → `_modules_by_category.setdefault(category, [])`
- [x] `clear_modules_for_category(category)` → clears list in-place + conditionally deletes Blender objects
- [x] `clear_all_modules()` / `get_building_modules()` / `clear_all_building_modules()` → shims
- [x] `generate_modules()` and `generate_building_modules()` use local `mods` variable
- [x] `generate_building_modules()` upgraded to use `ensure_modules_collection`
- [x] Test: 35/35 checks pass (`tests/verify_task_a5.py`)

### A6 — Merge generation functions → `generate_modules_for_category`
**File:** `addons/blender-wfc/__init__.py`
- [x] `generate_modules_for_category(category: str)` — single implementation for all categories
- [x] Uses `ensure_modules_collection(category)` — lazy, crash-safe (no bare `get_collection_by_name`)
- [x] Uses `get_primitives_by_category(category)` — filtered by category
- [x] Module names include category: `{name}_{category}_{rotation}` — no `_b` hack needed
- [x] Uses `DEFAULT_GRID_SIZES.get(category, 8.0)` as fallback for `physical_size`
- [x] Scene property key: `f"total_{category}_modules"` — generic
- [x] `generate_modules()` → one-line shim for `OUTER_GRID`
- [x] `generate_building_modules()` → one-line shim for `BUILDING`
- [x] Removed: `_b{rotation}` naming, `(-50, -100, 0)` starting position, hardcoded `total_building_modules` key
- [x] `DEFAULT_GRID_SIZES` added to `wfc_values` import in `__init__.py`
- [x] All operator call sites unchanged (still call shim names)
- [x] Test: 28/28 checks pass (`tests/verify_task_a6.py`)

### A7 — Update `get_all_primitives` + `get_primitives_by_category`
**File:** `addons/blender-wfc/__init__.py`
- [x] `get_all_primitives()` → `bpy.data.collections.get(...).all_objects` — traverses all
      category subcollections automatically; returns `[]` (never raises) if parent missing
- [x] `get_primitives_by_category(cat)` → `ensure_primitives_collection(cat).objects` —
      collection membership encodes category; no property scan needed
- [x] Old `get_all_objects_from_collection(CollectionNames.Primitives.value)` call removed
- [x] Old `p.grid_category == category` property filter removed
- [x] Test: 22/22 checks pass (`tests/verify_task_a7.py`)

### A8 — Route load operator to category subcollections
**File:** `addons/blender-wfc/primitive_ui.py`
- [x] **Library path**: `prim_collection` now resolved *per primitive* inside the loop via
      `ensure_primitives_collection(prim_data.grid_category)` — different categories in one
      library file automatically go into separate leaf collections
- [x] **Single path**: replaced `collection=context.scene.collection` (scene root!) with
      `ensure_primitives_collection(primitive_data.grid_category)`
- [x] Removed old `try/except` block with hardcoded `get_or_create_collection(WFC_Primitives)`
- [x] Works for every known and future category with zero code changes
- [x] Test: 21/21 checks pass (`tests/verify_task_a8.py`)

### A9 — Fix `clear_*` functions to be crash-safe
**File:** `addons/blender-wfc/__init__.py`
- [ ] `clear_all_primitives()` — check collection exists before clearing
- [ ] `clear_all_modules()` — delegate to `clear_modules_for_category` per key
- [ ] `clear_all_cells()` — existence check before clearing
- [ ] Missing collection = nothing to clear = not an error

### A10 — Update operator callers and panel buttons
**File:** `addons/blender-wfc/__init__.py`
- [ ] `OBJECT_OT_BuildWfcModules` → calls `generate_modules_for_category('outer_grid')`
- [ ] `OBJECT_OT_BuildBuildingModules` → calls `generate_modules_for_category('building')`
- [ ] Both operators share the single implementation; panel buttons stay explicit

### A11 — Route every grid level's output to `WFC_Grid_{category}`
**File:** `addons/blender-wfc/__init__.py`
- [ ] `OBJECT_OT_GenerateBuildingInnerGrid` places result objects in
      `ensure_collection(grid_collection_for('building'))` → `WFC_Grid_building`
- [ ] Outer grid collapse (`visualize_collapsed_cell`) writes to
      `grid_collection_for('outer_grid')` → `WFC_Grid_outer_grid`
- [ ] Future inner-within-inner grids follow the same call — one helper,
      any depth, no new static names needed
- [ ] Remove `CollectionNames.GridOuter` / `GridInner` references (no longer exist)

### A12 — Retire "Build Collections" as a workflow requirement
**Files:** `addons/blender-wfc/wfc_collections.py`, `addons/blender-wfc/__init__.py`
- [ ] Remove "Build Collections" button from the main WFC workflow panel
- [ ] Repurpose operator as optional "Reset WFC Tree" utility:
  - [ ] Non-destructive: creates any missing collections, never clears content
- [ ] Update panel layout with a brief note where the button was

---

## 📅 Phase B — Project-Wide Generics

*Scope is intentionally exploratory. B1 audit drives the priority of B2–B4.*

### B1 — Audit hardcoded values across the codebase
**Goal:** Produce a grouped inventory before changing anything.
- [ ] Scan all non-data files for bare category string literals
      (`'building'`, `'outer_grid'`, etc.)
- [ ] Scan for bare size/resolution literals (`8.0`, `2.0`, `4`)
      outside `wfc_values.py` and `DEFAULT_GRID_SIZES`
- [ ] Scan for connector type strings (`'BUILDING'`, `'ROAD'`, `'WALL'`, etc.)
      outside JSON files
- [ ] Classify each occurrence: **safe to leave** / **should be data-driven**
- [ ] Output: annotated list in this document (or a linked audit file)

### B2 — Category-driven panel buttons
**Depends on:** B1 audit, Phase A complete
- [ ] Decide strategy:
  - Option A — Generate buttons dynamically from loaded categories at draw time
  - Option B — Keep named buttons, share implementation via `generate_modules_for_category`
- [ ] Implement chosen strategy
- [ ] Verify a new category gets a button (or is otherwise accessible) with zero code change

### B3 — Connector type strings
**Depends on:** B1 audit
- [ ] Validate connector strings against `connectors.json` at library load time
- [ ] Explore populating the UI dropdown from `connectors.json` dynamically
      rather than the static `GRID_CATEGORIES` enum
- [ ] Decide: should unknown connectors warn, error, or be accepted silently?

### B4 — Physical sizes and resolutions
**Depends on:** B1 audit
- [ ] Evaluate moving all size/resolution defaults into a config file
      (e.g. `data/categories.json`) alongside `connectors.json`
- [ ] `categories.json` would define: category name, default physical size,
      default resolution multiplier, display label
- [ ] `GridCategory` constants and `DEFAULT_GRID_SIZES` become generated from
      this file, not hand-coded

---

## ✅ Success Criteria

### Phase A
- [ ] "Build Collections" button is no longer required before any operation
- [ ] Loading `building_library.json` with no existing collections works end-to-end
- [ ] Adding a hypothetical `'industrial'` category requires zero changes to
      collection, module-generation, or load-operator code
- [ ] `WFC_Primitives_outer_grid`, `WFC_Modules_building`, `WFC_Grid_building`,
      etc. appear automatically as the user works through the workflow
- [ ] All three tree branches (`Primitives`, `Modules`, `Grid`) follow the
      identical `_{category}` pattern — verified by inspection
- [ ] A future inner-within-inner grid level (e.g. `'room_detail'`) can be
      wired up by passing the new category string to `grid_collection_for()`;
      no `CollectionNames` entries or structural changes required

### Phase B
- [ ] B1 audit complete with all occurrences classified
- [ ] No bare category string literals exist outside `wfc_values.py` and data files
- [ ] A new grid category can be added by editing `connectors.json` /
      `categories.json` alone (no Python changes)
