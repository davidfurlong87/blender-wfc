# Project-Wide Remaining Work Roadmap

**Purpose:** This is the authoritative list of planned work that is still **not implemented**.

**Scope:** Consolidates the genuinely open items from the older roadmap / planning docs and excludes work that has already shipped, been superseded, or is only historical context.

## How to use these roadmap docs

Use the roadmap set in this order:

1. **Start here:** `PROJECT_WIDE_REMAINING_WORK_ROADMAP.md`
   - authoritative list of what is still open
   - safest recommended implementation order
2. **Then:** `PRIMITIVE_PACK_AND_CONNECTOR_ROADMAP.md`
   - pack / connector-specific history, phase structure, and remaining stretch work
3. **Then:** `export_to_blend_file_plan.md`
   - hybrid / blend-specific design notes, historical task breakdown, and detailed validation context

**Status legend:**
- [ ] planned, not started
- [/] in progress
- [x] complete
- [-] deferred / intentionally not scheduled

---

## 0. Bugs — fix before anything else

These were reported by a new user working through the pack workflow end-to-end.
They block core functionality and should be resolved before any new features are added.

### 0.1 Export to blend fails: "No mesh primitives found in the active pack collection"

**Source:** New user feedback. Reported when trying to save a pack as `.blend` after
assigning type and metadata to objects.

**Root cause (confirmed by code review):** Two independent causes:

**Primary (the main bug):** `OBJECT_OT_WFCAssignConnectors.execute()` stamps all metadata properties
onto the object (`obj.grid_category`, `obj.x_pos_connector`, etc.) but never calls
`link_object_to_single_collection`. The object stays in Blender's default `Collection`.
All save/export paths and the Pack panel primitive list search exclusively in
`WFC_Primitives_{category}` and find nothing. Same bug applies to `OBJECT_OT_WFCCopyConnectors`
which also copies metadata without re-registering the targets.

**Secondary (silent data loss):** The exporter always looks in `WFC_Primitives_{pack['category']}`.
If the user assigns a different `grid_category` to a primitive (e.g. `'building'`) while the pack
was created as `'outer_grid'`, the primitive lands in the correct collection for its own category
but is silently excluded from the export. No error is shown.

**Implementation tasks (in safe order):**

- [ ] **Primary fix** — In `OBJECT_OT_WFCAssignConnectors.execute()`, after setting metadata, call
  `ensure_primitives_collection(self.grid_category)` then `link_object_to_single_collection(obj, col)`
  (mirrors exactly what the load path already does at line 1481–1486)
- [ ] **Copy fix** — Apply the same registration step to `OBJECT_OT_WFCCopyConnectors.execute()`:
  re-link each target into `WFC_Primitives_{source.grid_category}` after copying its properties
- [ ] **Secondary: add a warning** — In `_save_as_blend_file` and `_save_as_json_file`, after
  collecting objects from `WFC_Primitives_{pack['category']}`, check whether any objects in ALL
  WFC_Primitives_* collections have a `grid_category` that differs from the pack's category.
  If so, emit a `{'WARNING'}` report listing them by name so the user knows they were excluded.
- [ ] **Regression test** — Extend tests to cover: create object → assign via UI operator → confirm
  object appears in `WFC_Primitives_{category}` collection (mock or otherwise)

**Validation steps:**

- [ ] In Blender, create a new mesh cube
- [ ] Create a new pack (e.g. `building`, resolution 4)
- [ ] Run "Assign Type & Connectors" on the cube
- [ ] Open the Pack panel → primitive list: confirm the cube appears (previously empty)
- [ ] Run "Save Pack as Blend" → confirm no "No mesh primitives found" error
- [ ] Repeat for `WFC Copy Type & Connectors` with multiple selected objects
- [ ] Repeat with a primitive assigned to a different category than the pack — confirm warning is shown

### 0.2 Connector Registry not blank when creating a new pack

**Source:** New user feedback. When creating a new pack, the Connector Registry is pre-populated
with connectors from other packs or the global defaults. The user expects to start with a blank
canvas and add connectors explicitly.

**Note:** P3-B specified that `data/connectors.json` should be "the system default / starting
template, not the enforced single source of truth." The current implementation does not honour
this for new packs.

- [ ] Confirm the new-pack flow clears the session connector registry before activating
- [ ] Make global defaults opt-in: offer an "Import from global defaults" button rather than pre-loading
- [ ] Verify no stale connectors from a previously loaded pack survive into a new pack creation

### 0.3 Pack base-size defaults not propagating to new primitive dialog

**Source:** New user feedback. User set pack base-size to 4 m but the Assign Connectors dialog
opened with different defaults.

**Note:** P2-D (pack-wide physical size and resolution) was planned and marked complete, but
this feedback suggests it is not working correctly.

- [ ] Reproduce: create a pack with non-default size/resolution, then open Assign Connectors on a new object
- [ ] Confirm whether pack defaults pre-populate the dialog correctly
- [ ] Fix the dialog to read pack defaults from the active pack state before showing
- [ ] Verify the fix with both JSON-only and hybrid pack types

### 0.4 Blank `compatible_with` allowed on connector creation — and cannot be fixed afterwards

**Source:** New user feedback.

Two related issues:
- The Add Connector dialog allows saving a connector with a blank `compatible_with` list,
  producing a connector that can never match anything and is permanently broken
- There is no way to edit `compatible_with` after creation; the only workaround is delete and recreate

- [ ] Add validation to the Add Connector operator: block save if `compatible_with` is empty, show a clear error
- [ ] Add an "Edit Connector" operator or inline edit for `compatible_with` on existing connectors
- [ ] Confirm rename (P3-C) and delete (P3-A) still work correctly after this change

### 0.5 Save Pack as Blend does not auto-append `.blend`

**Source:** New user feedback. When a user exports a pack as a blend file, they must manually type
the `.blend` extension or the file is not created as expected.

**Why this belongs in Tier 0:** This is a direct file-save workflow bug in a core user path. It is
small and low-risk to fix, and the addon should not rely on users to supply the extension manually.

- [x] Reproduce by exporting a pack to a filepath without `.blend`
- [x] Update the export operator so it appends `.blend` automatically when the chosen filepath has no extension
- [x] Ensure an existing `.blend` filename is not double-appended
- [x] Confirm the stored `blend_filepath` / active-pack filepath uses the final corrected path
- [ ] Add a regression test or explicit Blender validation step for the missing-extension case

---

## 1. High-priority remaining work

### 1.1 Blend-only connector fallback hardening and validation

**Why it matters:** The core blend-only connector fallback chain is now implemented, but it still needs explicit real-Blender validation and clearer user-facing reporting for malformed embedded data and fallback-path selection.

**Safest remaining implementation order:**

- [ ] Blender smoke test: load a `.blend` with embedded `wfc_connectors.json` and no sidecar JSON
- [ ] Blender smoke test: load a `.blend` with no sidecar JSON and no embedded registry; confirm inferred placeholder connectors activate
- [ ] Blender smoke test: load a `.blend` with malformed embedded `wfc_connectors.json`; confirm fallback to the global registry
- [ ] Harden operator / Pack UI reporting so the exact fallback path is explicit, especially for malformed embedded connector data

**Validation steps:**

- [ ] Export or prepare a pack `.blend` with a known embedded `wfc_connectors.json`
- [ ] Temporarily remove or rename the companion `pack.json`
- [ ] Load the `.blend` directly and confirm the session connector registry contains the embedded connector names
- [ ] Remove the embedded `wfc_connectors.json` text block and reload the `.blend`
- [ ] Confirm connector names referenced by primitive object properties are inferred as placeholder definitions
- [ ] Corrupt the embedded `wfc_connectors.json` payload and reload the `.blend`
- [ ] Confirm a clear warning is shown and the global connector registry is used
- [ ] Confirm no stale session connectors survive from a previously loaded pack

### 1.2 Connector creation UX gaps

**Source:** New user feedback.

#### 1.2a `compatible_with` is free text instead of a dropdown

The Add Connector dialog accepts a comma-separated text string for `compatible_with`. This
means users can type connector names that do not exist in the pack registry, creating silent
compatibility mismatches that only appear at generation time.

- [ ] Replace the free-text `compatible_with` input with a multi-select list of connectors already in the pack registry
- [ ] Show a clear message if the registry is empty ("Add connectors first before defining compatibility")

#### 1.2b Grid Category label on connectors is confusing; resolution-scoped availability is missing

**Source:** New user feedback. The "Grid Category" field on a connector is not intuitive.
Users think in terms of resolution level (outer grid at resolution 1, building at resolution 4)
rather than category names.

- [ ] Add a tooltip or label clarifying what Grid Category means on a connector
- [ ] Investigate adding a resolution-range field to connector definitions (`min_resolution` / `max_resolution` or an explicit list)
- [ ] Decide whether resolution-scoping is part of the connector definition or a filter on the UI dropdown

#### 1.2c Unclear how different grid resolutions coexist in one pack

**Source:** New user feedback. The relationship between resolution 1 (outer grid) and resolution 4
(building inner grid) inside a single pack is not obvious from the UI.

- [ ] Add a short explanatory note or section divider in the Pack panel that explains the resolution relationship
- [ ] Consider showing each resolution level as a distinct group in the primitive list (section 3.2 of pack roadmap)

### 1.5 Primitive naming workflow and rename propagation

**Source:** New user feedback. Users want an explicit way to name a primitive as part of the
authoring workflow, without relying on manual Blender Outliner renaming. When the name changes,
all relevant pack-facing state should stay in sync automatically.

**Why this is high priority:** Primitive identity is user-visible and is likely to appear in the
scene UI, manifests, exported data, and future module-generation/debugging workflows. Manual renaming
is error-prone and encourages state drift.

- [ ] Confirm the current source of truth for primitive naming (`bpy.types.Object.name`, serialized `PrimitiveData.name`, any manifest entry, any cached UI lists)
- [ ] Decide whether a separate editable "primitive display/name" field is actually needed, or whether the correct fix is an explicit rename operator over `obj.name`
- [ ] Add a clear rename flow in the Pack / primitive UI so users do not need to rename manually in Blender's generic UI
- [ ] When a primitive is renamed, update all relevant in-memory and serialized references that depend on the primitive name
- [ ] Add validation for empty names and duplicate names inside the active pack
- [ ] Add an end-to-end validation step or regression test for rename propagation

### 1.3 Connector validation on pack load

**Why it matters:** Packs can currently load connector strings that do not exist in the pack registry. The system needs a defined policy.

- [ ] Validate primitive connector strings against the active pack registry during JSON / hybrid pack load
- [ ] Decide the policy for unknown connectors:
  - [ ] warn and keep
  - [ ] hard error
  - [ ] auto-create placeholder connectors
- [ ] Surface clear warnings in the Pack UI / operator reports
- [ ] Add tests for each policy branch

### 1.4 Connector-aware context filtering

**Why it matters:** The connector dropdown could become much safer and faster to use if it only offered connectors that make sense for the currently selected cell or its surroundings.

- [ ] Expose enough neighbour / outer-grid context to the primitive-assignment workflow
- [ ] Filter connector choices based on surrounding placements or adjacent inner-grid systems
- [ ] Decide UX: strict filtering vs. filtered list with “show all” escape hatch
- [ ] Verify this works without breaking manual authoring workflows

---

## 2. Inner-grid / building workflow follow-ups

### 2.1 Performance and responsiveness

**Source:** building plot / inner-grid planning docs.

- [ ] Batch processing for heavy building-plot or inner-grid work (N cells per frame)
- [ ] Progress indicator UI for long-running generation steps
- [ ] Modal / async operator path to avoid Blender UI freezes
- [ ] Cache repeated building-plot calculations where worthwhile
- [ ] Profile bottlenecks before doing speculative optimisation

### 2.2 End-to-end validation under fresh-scene conditions

**Why it matters:** Several collection-system success criteria are conceptually done, but still need final explicit validation in Blender as a user-facing workflow.

- [ ] Verify that no manual “Build Collections” step is required from a fresh file
- [ ] Verify that loading a category library into an empty scene creates the correct collections lazily
- [ ] Verify a brand-new category added via `data/categories.json` works end-to-end with no Python edits
- [ ] Document the expected “happy path” for fresh-scene validation

---

## 3. Design questions requiring discussion before implementation

### 3.1 Multi-category pack design

**Source:** New user feedback. "A pack should have several different categories within it —
one may be outer grid, another may be inner grid."

**Why this is a design question, not a simple fix:** The current pack data model stores a single
`grid_category` at the top level. Changing this to support multiple categories affects the data
schema, the connector registry scoping, the collection system, save/load paths, and the UI.

- [ ] Decide the model: does a pack have one category, or is it a container of sub-packs each with a category?
- [ ] Alternatively: remove the pack-level category requirement and make it per-primitive only
- [ ] Assess impact on the connector registry: connectors are currently category-scoped
- [ ] Assess impact on save/load: `blend_collection` naming uses category today
- [ ] Write a short design note before any implementation begins
- [ ] Implementation should not start until the model decision is recorded and agreed

### 3.2 Configurable outer grid size

**Source:** New user feedback. "When building a grid I am locked in to a 10×10 outer grid.
I want to set this in the UI."

- [ ] Identify where the 10×10 default is set in the grid generation code
- [ ] Add a UI input for grid width and height in the Grid Generation panel
- [ ] Validate that non-square grids work correctly through the collapse algorithm
- [ ] Ensure the setting is persisted or at least clearly visible before generation

### 3.3 State synchronisation / refresh architecture

**Source:** New user feedback. Suggestion for a universal "update state" operator that runs after
user changes and refreshes all relevant internal components automatically.

**Why this is a design question, not a quick fix:** The idea affects operator responsibilities,
source-of-truth rules, Blender property updates, pack state, connector registry state, and any cached
UI lists. Implementing this ad hoc would likely create more hidden coupling.

- [ ] Inventory every user action that should trigger downstream refresh/sync (primitive rename, connector rename/delete, pack rename, category changes, size/resolution changes, etc.)
- [ ] Decide whether the right model is: a universal `refresh_state()` function, operator-specific update hooks, Blender property update callbacks, or a hybrid
- [ ] Define strict source-of-truth rules for scene objects, active pack state, connector registry, and serialized manifest data
- [ ] Define the scope explicitly: internal state synchronisation only, not export/build actions
- [ ] Write a short design note before implementation begins
- [ ] Implementation should not start until the model decision is recorded and agreed

---

## 4. Deferred / lower-priority work

### 4.1 Primitive authoring legacy UI improvements

These are still reasonable ideas, but the newer pack workflow reduced their urgency.

- [ ] Update Primitive operator (edit an existing saved primitive in place)
- [ ] Primitive library browser UI for browsing / previewing saved primitive assets
- [-] Legacy single-primitive import/export polish beyond the pack workflow

### 4.2 Instant module generation from scene primitives (no save/load cycle)

**Source:** User feedback — "I want to add a primitive and immediately start creating modules
without having to save and reload the pack."

**Current behaviour:** Module generation (`Build WFC Modules`) reads from the `WFC_Primitives_{category}`
collection, which is now correctly populated when using "Assign Connectors & Metadata" (fixed in 0.1).
However, the WFC module-building step may still require a formal pack to be active, and users may feel
the need to save and reload before generation works.

**Why this is on the backlog:** With the 0.1 fix in place (objects now auto-register into
`WFC_Primitives_{category}` when assigned), it is worth testing first whether this is already resolved.
If the module builder reads directly from the collection without requiring a save/load cycle, the user
request may be satisfied for free.

**Before implementing anything:**

- [ ] Test: create a primitive, assign type and connectors, then immediately run "Build WFC Modules" —
  confirm whether it picks up the scene primitive correctly
- [ ] If it works already, mark this item complete; document the finding in the beginner guide
- [ ] If it does not work, root-cause whether the blocker is: missing active pack, collection lookup,
  or a module-builder requirement not yet exposed in the UI

**If implementation is needed:**

- [ ] Add a "Generate Modules from Scene" shortcut or operator that does not require a saved pack file
- [ ] Ensure the module builder falls back gracefully when no pack is loaded but `WFC_Primitives_*`
  is non-empty
- [ ] Investigate whether the full save/load cycle could become optional when authoring locally in-scene

### 4.3 Periodic review of the primitive registration and module-generation flow

**Why:** The 0.1 fix solves the immediate collection registration bug. As multi-category packs (3.1)
and instant module generation (4.2) are implemented, the assumptions in this flow will shift. A review
pass at that point will catch any resulting gaps.

- [ ] Review the full flow from "user creates mesh → assigns metadata → modules generated → pack exported"
  after multi-category (3.1) and instant-generation (4.2) work is complete
- [ ] Check for any remaining cases where an object can carry WFC properties but not be visible to
  save, export, or module-build paths
- [ ] Update the beginner guide to reflect the final expected workflow

### 4.4 Pack loading UX extensions

- [ ] Folder-based pack loading (`pack folder` instead of choosing `.json` or `.blend` manually)
- [ ] Better conflict-resolution UI for **Merge Pack** (dialog / summary panel instead of report-only feedback)
- [ ] Pack validation / lint report before save or merge

---

## 5. Documentation and cleanup

- [ ] Reconcile older historical docs whose checkboxes no longer match shipped work
- [ ] Add screenshots to the beginner pack guide and pack/connector workflow docs
- [ ] Add a short “Which doc should I read first?” index page for primitive / pack authoring docs

---

## 6. Future suggestions

These are not formal commitments yet, but they are strong candidates for future planning.

### User-facing improvements
- [ ] Pack templates (e.g. “new building pack”, “new outer-grid pack”)
- [ ] Default placeholder materials for rapid prototyping
- [ ] Categorised connector dropdowns (not just alphabetical)
- [ ] Example packs shipped with matching demo scenes

### Technical improvements
- [ ] Shared material library references between multiple packs
- [ ] Pack diff / compare tool before merge
- [ ] Pack schema migration helper for future format changes
- [ ] Automated Blender smoke-test harness for docs-defined workflows

---

## Recommended next implementation order

Items are grouped into tiers by **risk and dependency**. Complete one tier before starting the next.
Higher tiers depend on correctness established by lower tiers.

### Tier 0 — Critical bugs (fix before anything else)

These block existing core workflows for any new user. No new features should be added until these pass.

1. [x] **0.1a** Primary fix — `AssignConnectors.execute()` must call `link_object_to_single_collection` after stamping metadata
2. [x] **0.1b** Copy fix — `CopyConnectors.execute()` must re-link each target into `WFC_Primitives_{category}` after copying
3. [ ] **0.1c** Secondary warning — exporters should warn when primitives exist in a different category than the pack
4. [ ] **0.1d** Regression test for the registration flow
5. [ ] **0.2** Connector Registry not blank on new pack creation — fixed and verified
6. [ ] **0.3** Pack base-size defaults not propagating to new primitive dialog — fixed and verified
7. [ ] **0.4** Blank `compatible_with` allowed and cannot be edited — validation added, edit operator added
8. [x] **0.5** Auto-append `.blend` during pack export when the user omits the extension

### Tier 1 — High-impact UX fixes (bounded changes, low risk)

Safe to implement once Tier 0 is done. Each item is self-contained.

9. [ ] **1.2a** Replace `compatible_with` free text with a dropdown of existing pack connectors
10. [ ] **1.2b** Add tooltip / clarify Grid Category label on connector creation
11. [ ] **1.2c** Add resolution-relationship explanation to the Pack panel
12. [ ] **1.5** Add an explicit primitive rename flow and validate name propagation
13. [ ] **1.1** Blend-only connector fallback Blender smoke tests
14. [ ] **1.1** Blend-only connector fallback reporting hardening

### Tier 2 — Connector and pack system quality (medium risk, bounded scope)

15. [ ] **1.3** Connector validation policy on pack load + tests
16. [ ] **2.2** End-to-end fresh-scene validation in Blender
17. [ ] **3.2** Configurable outer grid size UI

### Tier 3 — Design-dependent work (requires design decision first)

18. [ ] **3.1** Multi-category pack — design decision recorded before any code is written
19. [ ] **3.3** State synchronisation / refresh model — design decision recorded before any code is written
20. [ ] **1.4** Connector-aware context filtering — blocked by outer grid system being queryable

### Tier 4 — Performance and long-running work (address after system is stable)

21. [ ] **2.1** Performance / responsiveness improvements (profile first)

---

**Guiding principle:** correctness and data integrity first → usability second → new features third → architecture last.

Recent user feedback has been triaged into roadmap items **0.5**, **1.5**, and **3.3** above.