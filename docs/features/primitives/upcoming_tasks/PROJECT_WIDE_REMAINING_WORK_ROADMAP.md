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

### 1.2 Connector validation on pack load

**Why it matters:** Packs can currently load connector strings that do not exist in the pack registry. The system needs a defined policy.

- [ ] Validate primitive connector strings against the active pack registry during JSON / hybrid pack load
- [ ] Decide the policy for unknown connectors:
  - [ ] warn and keep
  - [ ] hard error
  - [ ] auto-create placeholder connectors
- [ ] Surface clear warnings in the Pack UI / operator reports
- [ ] Add tests for each policy branch

### 1.3 Connector-aware context filtering

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

## 3. Deferred / lower-priority work

### 3.1 Primitive authoring legacy UI improvements

These are still reasonable ideas, but the newer pack workflow reduced their urgency.

- [ ] Update Primitive operator (edit an existing saved primitive in place)
- [ ] Primitive library browser UI for browsing / previewing saved primitive assets
- [-] Legacy single-primitive import/export polish beyond the pack workflow

### 3.2 Pack loading UX extensions

- [ ] Folder-based pack loading (`pack folder` instead of choosing `.json` or `.blend` manually)
- [ ] Better conflict-resolution UI for **Merge Pack** (dialog / summary panel instead of report-only feedback)
- [ ] Pack validation / lint report before save or merge

---

## 4. Documentation and cleanup

- [ ] Reconcile older historical docs whose checkboxes no longer match shipped work
- [ ] Add screenshots to the beginner pack guide and pack/connector workflow docs
- [ ] Add a short “Which doc should I read first?” index page for primitive / pack authoring docs

---

## 5. Future suggestions

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

1. [ ] Blend-only connector fallback Blender smoke tests
2. [ ] Blend-only connector fallback reporting hardening
3. [ ] Connector validation policy + tests
4. [ ] End-to-end fresh-scene validation
5. [ ] Performance / responsiveness improvements
6. [ ] Connector-aware context filtering

This order keeps the work focused on **correctness first**, **reliability second**, and **authoring convenience third**.
