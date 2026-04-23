# Primitive Pack & Connector System — Roadmap

**Source:** User feedback gathered after first external handover (2026-04-23)
**Status:** 📋 Prioritised, not yet started

Cross-references:
- `COLLECTION_SYSTEM_AND_GENERICS_ROADMAP.md` — Phase B3 (connector UI), B4 (physical sizes)
- `thoughts_on_import_export_system.md` — pack format sketch

---

## Context

The current "save to JSON / load from JSON" workflow treats primitives as independent
files. The new user's clearest request is that a **pack** — a named, self-contained
collection of primitives, connectors, and shared metadata — should be the primary
working unit throughout the UI.

Two themes emerge from the feedback:

1. **Pack management** — create, edit, save, and load packs as first-class objects
2. **Connector management** — create, rename, and organise connectors from the UI

---

## Priority 1 — Quick bug fixes (no design work required)

### P1-A  Auto-capitalisation of custom primitive types
**Feedback:** "When creating a custom type, the name is auto-capitalised"
**Fix:** Remove or make optional the `.upper()` / `.capitalize()` call applied to
custom type names in the primitive type assignment operator.
**File:** `addons/blender-wfc/primitive_ui.py` or `wfc_enums.py`
**Effort:** Small

### P1-B  Physical size does not update when resolution multiplier changes
**Feedback:** "Physical size isn't updated when updating the resolution multiplier"
**Fix:** When `resolution_multiplier` is set in the Assign Connectors dialog, update
the corresponding `physical_size` display (or enforce a derived relationship so
the two values stay consistent).
**Cross-reference:** Related to B4 in `COLLECTION_SYSTEM_AND_GENERICS_ROADMAP.md`
**Effort:** Small–Medium

---

## Priority 2 — Pack system

The concept is sketched in `thoughts_on_import_export_system.md`. These tasks
make it concrete.

### P2-A  Define the pack data model
A pack is a JSON file containing:
- Pack-level metadata: name, description, grid category, physical size, resolution multiplier
- The full connector registry valid for this pack
- An array of primitive entries (same format as today's per-primitive JSON)

Pack-level metadata becomes the **default** for any new primitive created inside it.

### P2-B  Pack management UI (create / load / save / rename)
**Feedback:** "I should be able to create a new pack and then create primitives within it"

New UI section: **Pack** (above Primitive Builder)
- **New Pack** — opens a dialog for name, category, default physical size/resolution
- **Load Pack** — file browser (replaces "Load from JSON", which stays as a legacy path)
- **Save Pack** — saves the active pack (all in-scene primitives for this category)
- **Rename Pack** — in-place rename without touching the filesystem

The active pack name should be visible in the panel at all times.

### P2-C  Primitive list within a pack
**Feedback:** "There is no way of knowing which primitives are in which pack"
**Feedback:** "There is no way of renaming/deleting a primitive once it has been created"

Add a scrollable list inside the Pack panel showing all primitives currently in the pack.
Each entry shows: primitive name, type, connector summary.
Per-entry actions:
- **Rename** — edits the object name and updates the pack
- **Delete** — removes the Blender object and removes it from the active pack
- **Select** — selects the object in the viewport

### P2-D  Pack-wide physical size and resolution
**Feedback:** "There seems to be no way of setting a pack-wide physical size"

Pack-level defaults (set in P2-A) pre-populate the metadata dialog when a new
primitive is created inside the pack. The user can still override per primitive.

---

## Priority 3 — Connector system

### P3-A  Create and delete connectors from the UI
**Feedback:** "Need system for adding new connectors. Current system is tightly bound
to the connector_registry.py file"

New **Connector Registry** section in the UI:
- List all connectors for the active pack
- **Add Connector** — name + compatible-with list
- **Delete Connector** — only allowed if no primitive in the pack currently uses it
- Saved into the pack JSON alongside primitives

**Cross-reference:** B3 in `COLLECTION_SYSTEM_AND_GENERICS_ROADMAP.md` covers loading
the UI dropdown from `connectors.json`. P3-A extends this to allow in-UI editing.

### P3-B  Pack-scoped connector registry
**Feedback:** "No interaction between primitive creation and connector_registry.
The design should be that a connector registry is specific to a particular pack"

- Connectors defined in a pack are only available within that pack's UI session
- Loading a pack also loads its connector registry
- Global `data/connectors.json` becomes the system default / starting template,
  not the enforced single source of truth
- Merging connectors from two packs is a future stretch goal

### P3-C  Rename connector after creation
**Feedback:** "Spelling mistakes become permanent at the moment"

- Rename a connector from the Connector Registry list
- Any primitive in the pack that references the old name is updated automatically
- Warn if the connector is used in primitives from a different loaded pack

### P3-D  Quick-copy connectors from active object
**Feedback:** "Quick-copy system for connectors. 'Copy Type/Connectors from active'"

Button in the Primitive Builder panel: **Copy Type & Connectors from Active**
- Sets the type, pos_x/neg_x/pos_y/neg_y connectors, and rotation_invariant on the
  selected object(s) to match the currently active object

### P3-E  Connector sorting and categorisation
**Feedback:** "Alphabetise connectors. Or categorise them."

- Sort connector dropdown alphabetically by default
- Optional: allow connectors to carry a `display_category` field in the registry
  so the dropdown can show grouped headings (e.g. "Outer Grid / Building / Road")
- Longer-term: the code already identifies which inner-grid system a cell is adjacent
  to — this context could be used to filter the connector dropdown to only show
  connectors relevant to the current cell's surroundings

---

## Deferred / Stretch Goals

- **Load pack from a .blend file** — in addition to JSON, allow a pack to be loaded
  directly from a `.blend` file. The blend file already contains mesh geometry,
  materials, and vertex groups as native Blender data, so the loader would read the
  WFC metadata properties from each object (primitive_type, connectors, physical_size,
  etc.) rather than a JSON structure. The connector registry for the pack would need
  to be stored somewhere in the blend file (e.g. a text data-block or custom scene
  properties). This is complementary to the JSON path, not a replacement — both
  formats would remain valid pack sources.
  **Prerequisite:** P2-A (pack data model) and P2-B (pack management UI) must be
  stable first, since the blend-file loader must produce the same in-memory pack
  object that the JSON loader produces.

- **Merge two packs** — combine primitives and connectors from two JSON files,
  detecting and resolving connector name conflicts
- **Connector-aware context filtering** — restrict the connector dropdown based on
  what the outer grid has placed adjacent to the current cell
- **Material pack** — export materials alongside primitives for a fully portable pack

---

## Summary Table

| ID  | Item                                      | New / Existing | Effort |
|-----|-------------------------------------------|----------------|--------|
| P1-A | Fix auto-capitalisation of custom types  | New            | Small  |
| P1-B | Physical size / resolution consistency   | Extends B4     | Small  |
| P2-A | Pack data model                          | Extends import/export sketch | Medium |
| P2-B | Pack management UI                       | New            | Large  |
| P2-C | Primitive list (rename / delete)         | New            | Medium |
| P2-D | Pack-wide defaults                       | New            | Small  |
| P3-A | Create/delete connectors from UI         | Extends B3     | Medium |
| P3-B | Pack-scoped connector registry           | New            | Large  |
| P3-C | Rename connector after creation          | New            | Medium |
| P3-D | Quick-copy connectors from active        | New            | Small  |
| P3-E | Connector sorting and categorisation     | New            | Small  |

---

## Recommended Implementation Order

This section considers all active roadmaps together:
- This file (P-items)
- `COLLECTION_SYSTEM_AND_GENERICS_ROADMAP.md` (A and B items)

The guiding principle is: **unblock the user quickly, then build foundations before
features that depend on them.**

---

### Stage 1 — Immediate fixes (no dependencies, high visible impact)

These can be done in any order, independently of everything else.

1. **P1-A** — Fix auto-capitalisation of custom type names
2. **P1-B** — Keep physical size consistent with resolution multiplier
3. **P3-D** — Quick-copy type and connectors from active object
4. **P3-E** — Alphabetise the connector dropdown

All four are small, self-contained, and directly address the feedback from the
first external user. Delivering these first demonstrates responsiveness and clears
friction from the existing workflow before the larger pack system lands.

---

### Stage 2 — Complete the collection system (existing roadmap, nearly done)

The generics roadmap Phase A is mostly complete (A1–A8 done). Finishing it now
avoids carrying half-done infrastructure into the pack work.

5. **A9** — Crash-safe clear functions
6. **A10** — Route operator callers to generic generation function
7. **A11** — Route all grid output to `WFC_Grid_{category}`
8. **A12** — Retire "Build Collections" as a required workflow step

These are prerequisite hygiene for the pack system: the pack UI needs stable,
crash-safe collection management underneath it.

---

### Stage 3 — Pack data model and connector foundation

These are design tasks that everything else depends on. Doing them before writing
any UI avoids having to redesign while building.

9.  **P2-A** — Define the pack data model (JSON schema, in-memory representation)
10. **B3** (partial) — Load the connector dropdown from the active pack's registry
    instead of the global `connectors.json`
11. **P3-B** — Implement pack-scoped connector registry (load/save with pack)

At the end of Stage 3, the system knows what a pack is and connectors are
pack-local. Nothing in the UI changes yet, but the data layer is solid.

---

### Stage 4 — Pack management UI

Build the UI on top of the stable data layer from Stage 3.

12. **P2-B** — Pack management panel: New / Load / Save / Rename
13. **P2-C** — Primitive list inside the pack with Rename / Delete / Select
14. **P2-D** — Pack-wide physical size and resolution pre-populate the metadata dialog

At the end of Stage 4, the pack is the primary working unit visible to the user.
The old "Load from JSON" path stays as a legacy entry point.

---

### Stage 5 — Full connector management UI

With packs working, connectors can be exposed fully.

15. **P3-A** — Add / delete connectors from the Connector Registry panel
16. **P3-C** — Rename connector (with automatic update of affected primitives)

---

### Stage 6 — Remaining generics (Phase B audit)

17. **B1** — Audit hardcoded literals across the codebase
18. **B2** — Category-driven panel buttons (outcome depends on B1)
19. **B4** — Physical sizes and resolutions driven from a `categories.json` config

These are valuable but can wait until the pack and connector systems are stable,
because B4 in particular overlaps with the pack-level defaults added in Stage 4.

---

### Stage 7 — Deferred / stretch goals

In rough order of value:

20. **Load pack from .blend file** — depends on P2-A/B being stable
21. **Merge two packs** — depends on pack-scoped connector registry (Stage 3)
22. **Connector-aware context filtering** — depends on the outer grid collapse system
23. **Material pack** — depends on the pack format being finalised

---

### Dependency diagram (simplified)

```
Stage 1 (P1-A, P1-B, P3-D, P3-E)   ← no dependencies, start immediately
     |
Stage 2 (A9–A12)                    ← finish existing collection roadmap
     |
Stage 3 (P2-A, B3-partial, P3-B)   ← data model and connector foundation
     |
Stage 4 (P2-B, P2-C, P2-D)         ← pack UI
     |
Stage 5 (P3-A, P3-C)               ← connector management UI
     |
Stage 6 (B1, B2, B4)               ← generics audit and cleanup
     |
Stage 7 (stretch goals)
```
