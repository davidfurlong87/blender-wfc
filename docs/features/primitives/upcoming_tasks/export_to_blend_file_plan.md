## Export to Blend File — Stage 7 Plan

This document turns the early Stage 7 discussion into a concrete plan.

Goal: support **pack-as-folder** workflows where a pack can be loaded from a
`.blend` file while still keeping a JSON manifest alongside it for metadata,
connectors, versioning, and robust fallback behavior.

---

## Recommended on-disk structure

Each pack should live in its own folder:

- `pack.json` — semantic manifest, connector registry, pack metadata
- `pack.blend` — Blender-native geometry, materials, vertex groups, object custom properties

Example:

- `my_building_pack/pack.json`
- `my_building_pack/pack.blend`

This keeps the JSON diffable and editable outside Blender, while letting the
blend file remain the authoritative source for mesh data.

---

## Design decisions

### 1. Save/load format versioning

Use an **additive upgrade** to the current JSON library format rather than a
full incompatible rewrite.

Planned manifest additions:

- `blend_source`: relative path to the companion `.blend` file, e.g. `pack.blend`
- `blend_collection`: stable collection name inside the `.blend`

This keeps current JSON-only packs valid while allowing hybrid JSON + blend
packs to opt into the new workflow.

### 2. Collection naming inside the pack `.blend`

The appendable collection inside the pack blend should have a **stable internal
name**, stored explicitly in the JSON manifest.

Why not derive it from the current pack name every time?

- pack names may contain spaces or punctuation
- pack names may change later
- changing the collection name would break existing saved packs

Decision:

- on first blend export, generate a slugged collection name such as
  `Building_Pack_Primitives`
- store it in `pack.json` as `blend_collection`
- reuse that stored value on all later saves, even if the user renames the pack

The pack's display name (`library_name`) remains user-facing and editable.
`blend_collection` is an internal stable identifier.

### 3. Source of truth split

The two files have distinct responsibilities:

**`pack.blend` is authoritative for:**

- object geometry
- materials
- UVs
- vertex groups
- Blender custom properties stored on primitive objects

**`pack.json` is authoritative for:**

- pack metadata (`library_name`, category, size, resolution)
- connector registry definitions and compatibility rules
- format versioning and future migration flags
- location of the blend file and collection name

### 4. Connector registry fallback inside the blend

Primary connector storage should remain in `pack.json`.

However, to make standalone `.blend` files still usable, the exported blend
should also contain a Text datablock named:

- `wfc_connectors.json`

This text block stores the connector registry as JSON.

Fallback order when loading connectors:

1. `pack.json` connectors
2. `wfc_connectors.json` text datablock inside the `.blend`
3. infer connector names from primitive object custom properties
4. fall back to the global default connector registry and warn the user

### 5. What happens to primitive geometry in the JSON?

When `blend_source` is present, the loader should treat the `.blend` as the
authoritative source of primitive geometry.

Decision:

- if `blend_source` exists, load geometry from the blend and ignore any JSON
  vertex arrays if they are present
- for new hybrid exports, the JSON should move toward a **manifest-style** file
  rather than a full geometry dump

Initial implementation choice:

- keep the existing `primitives` array only if needed for backward compatibility
- but do not rely on it when `blend_source` is present
- long term, hybrid exports should either omit geometry-heavy arrays entirely or
  reduce them to lightweight metadata-only primitive stubs

---

## Loader behavior

The loader should accept any of these entry points:

- user selects `pack.json`
- user selects `pack.blend`
- later stretch goal: user selects a folder containing both files

### Decision tree

#### Case A — user selects `pack.json`

- load JSON metadata first
- if JSON contains `blend_source`, resolve the companion blend path relative to
  the JSON file
- if the blend exists, load geometry from the blend
- if the blend is missing, continue in JSON-only compatibility mode if possible
  and report a warning

#### Case B — user selects `pack.blend`

- try to find companion JSON in the same folder
- if found, use JSON metadata + connector registry + `blend_collection`
- if not found, still load geometry from the blend if a usable primitive
  collection exists
- if JSON is missing, do **not** auto-create it during load; instead report that
  the pack was loaded in geometry-only mode

#### Case C — blend exists but JSON is incomplete

- geometry still loads
- missing metadata falls back to object properties / sensible defaults
- missing connectors follow the connector fallback order above
- user receives a warning summarising what was reconstructed vs explicitly loaded

### Discovery rules

Relative-path based rules keep the system portable:

- `blend_source` should be stored as a path relative to `pack.json`
- moving the whole pack folder should preserve validity
- absolute paths should be avoided in the saved manifest

---

## Saver behavior

Saving to blend is the higher-risk part and should be implemented after a proof
of concept confirms the Blender API behavior.

### Save Pack as hybrid JSON + blend

Proposed workflow:

1. gather all primitives for the active pack category
2. gather the dependency graph needed for export:
   - objects
   - meshes
   - materials
   - images / other linked data if required
3. ensure there is a dedicated export collection named from `blend_collection`
4. write a `.blend` file containing that collection and its dependencies
5. write or update `pack.json` with:
   - metadata
   - connector registry
   - `blend_source`
   - `blend_collection`
6. embed `wfc_connectors.json` text datablock into the blend

### Save Pack as JSON only

Keep the current JSON-only export path as a legacy / compatibility option.

This is still useful for:

- debugging
- diff-friendly geometry snapshots
- workflows that do not want Blender binary files

### Upgrade path

Existing JSON-only packs should be convertible by loading them into Blender and
running a new export path:

- **Export Pack to Blend**

That export writes `pack.blend`, adds `blend_source` + `blend_collection` to the
manifest, and keeps the original JSON metadata intact.

---

## UI implications

### Load Pack

The existing pack loader should be extended to accept:

- `.json`
- `.blend`

Behavior should be unified so both entry points produce the same in-memory pack
state and the same scene collections.

### Save Pack

Two reasonable UI options exist:

1. infer the format from the chosen file extension
2. present an explicit format dropdown in the save dialog

Recommended initial choice:

- keep it simple and route by extension
- `.json` => current JSON-only path
- `.blend` => hybrid export (`.blend` + sidecar `pack.json`)

If the user saves to `.blend`, the addon should write both files into the same
folder.

---

## Pack state implications

Current `pack_state.py` assumes a single JSON filepath.

Stage 7 will likely require tracking both:

- manifest filepath (`pack.json`)
- blend filepath (`pack.blend`)

At minimum, the plan should ensure that the active pack can always answer:

- where its JSON manifest lives
- where its blend file lives, if any
- whether it is JSON-only or hybrid

---

## Validation requirements

The loader and saver should be robust against missing files and partial data.

Required checks:

- missing `blend_source`
- missing blend file referenced by JSON
- missing JSON sidecar when opening a blend
- missing `blend_collection`
- collection not found inside the `.blend`
- missing connector registry in both JSON and blend text datablock
- primitives missing required WFC object properties

Each failure mode should produce a clear warning or error with a suggested next
action where possible.

---

## Proof of concept required before implementation

Before committing to the saver architecture, verify that
`bpy.data.libraries.write()` can correctly export:

- primitive objects
- mesh data
- materials
- vertex groups
- required custom properties

Open question to answer in the PoC:

- how much of the dependency graph must be gathered manually before writing?

This is the main technical uncertainty in Stage 7 and should be resolved first.

---

## Recommended implementation order

### Phase 1 — PoC / risk reduction

- create a tiny throwaway export test using `bpy.data.libraries.write()`
- confirm whether reloading preserves geometry, materials, vertex groups, and
  custom WFC metadata

### Phase 2 — Read path first

- implement blend-pack loading before saving
- support `.json` + `.blend` companion discovery
- support `.blend`-only fallback mode

This gives immediate value and is lower risk than the write path.

### Phase 3 — Save path

- implement hybrid export
- embed connector registry text datablock
- persist `blend_source` and `blend_collection`

### Phase 4 — UX polish

- improve warnings and migration messaging
- optionally add folder-based pack loading
- optionally add explicit conversion UI for JSON-only packs

---

## Implementation task breakdown

These are the concrete implementation tasks that follow from the design above.

### Task 1 — PoC: verify Blender write/read round-trip

**Goal:** remove the main technical risk before touching production save code.

- create a small throwaway script that writes a minimal collection to a test
  `.blend` using `bpy.data.libraries.write()`
- include at least one primitive object with:
  - mesh data
  - one material
  - one vertex group
  - WFC custom properties (`primitive_type`, connectors, size/category metadata)
- re-open or re-append that test file and verify the data survives round-trip
- document exactly which datablocks must be gathered manually for export

**Output:** PoC script + written findings added to this document or a linked note.

### Task 2 — Add hybrid-pack manifest fields to persistence layer

**Goal:** allow JSON manifests to describe companion blend files.

- extend the JSON library schema with:
  - `blend_source`
  - `blend_collection`
- make `primitive_persistence.py` preserve these fields when loading and saving
- ensure older JSON-only packs still load without errors
- decide whether hybrid packs keep full `primitives` geometry arrays temporarily
  for backward compatibility or move to metadata-only stubs

**Primary files:**

- `addons/blender-wfc/primitive_persistence.py`
- `addons/blender-wfc/data/*.json` (sample fixtures if needed)

### Task 3 — Extend active pack state for hybrid sources

**Goal:** let the current in-memory pack record both its JSON manifest and its
blend file.

- update `pack_state.py` to track:
  - manifest filepath
  - blend filepath (optional)
  - pack source mode (`json_only` / `hybrid` / `blend_only`)
- update load/save call sites to populate the expanded state correctly

**Primary file:** `addons/blender-wfc/pack_state.py`

### Task 4 — Implement path/discovery helpers

**Goal:** centralise all file-discovery rules in one place instead of scattering
them across UI operators.

- add helpers for:
  - resolving `blend_source` relative to `pack.json`
  - finding likely companion JSON for a selected `.blend`
  - normalising sidecar file names (`pack.json`, `pack.blend`)
- ensure missing-file cases produce explicit errors/warnings

**Likely home:** `primitive_persistence.py` or a new small pack I/O helper module.

### Task 5 — Implement read-only blend-pack loader

**Goal:** load geometry from `.blend` without yet supporting save.

- load the named `blend_collection` from the companion `.blend`
- append/link the collection contents into the current scene
- move the imported primitives into the existing category-specific WFC
  collections so the rest of the add-on sees the usual structure
- reconstruct `PrimitiveData` / object metadata from imported object properties

**Primary files:**

- `addons/blender-wfc/primitive_ui.py`
- `addons/blender-wfc/primitive_adapter.py`
- `addons/blender-wfc/collectiontools/*`

### Task 6 — Implement connector-registry fallback chain

**Goal:** make `.blend` loading resilient even without a perfect sidecar JSON.

- load connectors from `pack.json` when available
- if missing, attempt to read `wfc_connectors.json` from the imported blend data
- if still missing, infer connector names referenced by primitive objects
- if inference fails or is incomplete, fall back to the default global registry
  and warn the user

**Primary files:**

- `addons/blender-wfc/connector_registry.py`
- `addons/blender-wfc/primitive_ui.py`

### Task 7 — Unify the Pack UI load path

**Goal:** the user should be able to choose either `.json` or `.blend` and get
the same active-pack result.

- extend the pack load operator to accept `.blend`
- route `.json` and `.blend` selections through the discovery helpers
- ensure both paths populate:
  - active pack state
  - session connector registry
  - primitives collection
  - pack panel metadata display

**Primary file:** `addons/blender-wfc/primitive_ui.py`

### Task 8 — Add automated tests for hybrid load behavior

**Goal:** prevent regressions before adding the save path.

- add focused tests for:
  - JSON-only pack still loads
  - JSON with `blend_source` resolves correctly
  - selected `.blend` with companion JSON loads correctly
  - `.blend` with missing JSON enters geometry-only fallback mode cleanly
  - missing `blend_collection` or missing collection yields clear errors

**Likely location:** `tests/` alongside the existing verification scripts.

### Task 9 — Implement export dependency collection

**Goal:** prepare the exact datablock set needed for `.blend` export.

- gather primitive objects in the active pack
- gather dependent meshes, materials, and any other required linked data
- create or reuse the stable export collection named by `blend_collection`
- verify the dependency set against the PoC findings before writing

**Primary files:**

- `addons/blender-wfc/primitive_ui.py`
- `addons/blender-wfc/primitive_adapter.py`

### Task 10 — Implement hybrid save/export path

**Goal:** save `pack.blend` + `pack.json` together.

- write the export collection to `.blend`
- update/write `pack.json` with:
  - metadata
  - connectors
  - `blend_source`
  - `blend_collection`
- keep the existing JSON-only save path working unchanged

**Primary files:**

- `addons/blender-wfc/primitive_ui.py`
- `addons/blender-wfc/primitive_persistence.py`

### Task 11 — Embed connector-registry fallback into the exported blend

**Goal:** make standalone blend files more self-contained.

- write a `wfc_connectors.json` text datablock during export
- define how it is updated on repeated saves
- teach the loader to read it when sidecar JSON connectors are unavailable

### Task 12 — UX polish and migration helpers

**Goal:** make the hybrid system understandable and easy to adopt.

- improve load/save warnings and info messages
- optionally add explicit “Export Pack to Blend” conversion UI
- optionally add folder-based pack loading later if file-based loading proves solid

### Task 13 — Final validation pass

**Goal:** confirm Stage 7 works end-to-end before considering follow-on work.

- verify JSON-only, hybrid, and blend-only fallback workflows manually or via
  targeted tests
- confirm pack renaming does not break `blend_collection`
- confirm session connector registries still activate correctly for hybrid packs
- confirm imported packs still work with module generation and downstream WFC
  operators

---

## Summary

Recommended architecture:

- **JSON remains the semantic manifest**
- **`.blend` becomes the authoritative geometry container**
- **packs are best treated as folders containing both files**
- **loader is permissive and reconstructive**
- **saver is gated behind a Blender write-path proof of concept**