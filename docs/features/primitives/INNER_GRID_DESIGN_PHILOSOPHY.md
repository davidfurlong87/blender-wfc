# Inner Grid Design Philosophy

**Last Updated:** 2026-04-20

---

## Purpose

This note explains the design rule behind the inner-grid system so future work
does not drift back toward the earlier whole-cell assumptions that caused
placement gaps and missing building coverage.

---

## Core Principle

**The outer grid decides coarse placement; vertex-group-marked faces decide the
true inner-grid footprint.**

That distinction matters because an outer 8x8m cell can be **mixed-use**:
- part building plot
- part pavement
- part road edge or corner treatment

So the inner grid must not assume that every collapsed outer cell contributes
its full 8x8m area to the building footprint.

---

## The Correct Mental Model

### Outer Grid = Coarse Topology
- Cell size: **8.0m**
- Decides which primitive/module is placed at each city-layout location
- Operates at the level of roads, corners, pavements, and building-bearing cells

### Inner Grid = Precise Buildable Area
- Cell size: **2.0m**
- Derived from the **actual marked faces** inside collapsed outer modules
- Can include contributions from mixed cells such as corners or pavements if
  those cells contain faces marked as `building_plot`

---

## Why Primitive Type Alone Is Not Enough

Using only `primitive_type == BUILDING` is too coarse.

It works only when a full 8x8m outer cell is entirely buildable. It fails for
mixed cells, where only some 2x2m sub-faces belong to the building footprint.

That was the root cause of the earlier "padding" problem:
- fully building cells contributed to the inner grid
- mixed cells were ignored
- the visible footprint became too small

The current system fixes this by extracting faces from the `building_plot`
vertex group instead of treating outer cells as all-or-nothing.

---

## Intended Data Flow

1. **Author a primitive** with an 8x8m footprint.
2. **Mark buildable 2x2m faces** using a semantic vertex group such as
   `building_plot`.
3. **Generate rotated modules** from the primitive.
4. **Propagate metadata and vertex groups** from primitive to module.
5. **Collapse the outer grid** using the normal WFC process.
6. **Extract plot faces** from the collapsed modules by reading the vertex group.
7. **Group adjacent plot faces into islands** using face-level adjacency.
8. **Compute island bounds from actual face vertices**, not from outer-cell
   centers.
9. **Size the inner grid from those bounds** using the inner cell size.
10. **Collapse the inner grid** using building modules.

---

## Design Rules to Preserve

### 1. Treat plot masks as semantic data
Vertex groups such as `building_plot` are not decorative. They are part of the
generation contract and define which sub-faces contribute to the next grid
level.

### 2. Prefer geometry-derived bounds over category-derived bounds
If exact face data exists, use it. Do not rebuild the footprint from outer-cell
centers or from primitive categories.

### 3. Keep category and footprint as separate concepts
- `grid_category` / `primitive_type` answer: **what system is this primitive in?**
- vertex groups answer: **which part of this mesh belongs to which plot mask?**

Those are related, but not interchangeable.

### 4. Resolution should come from metadata, not assumptions
The outer cell size, inner cell size, and `resolution_multiplier` must stay
metadata-driven. Avoid reintroducing hardcoded layout assumptions in operators
or visualization code.

---

## Authoring Guidance

### Use distinct names for primitives and vertex groups
Future authors should **avoid naming a primitive and a vertex group the same
thing**.

Use this separation instead:
- **Primitive name** = object identity / module identity
- **Vertex group name** = semantic mask / plot meaning

Good examples:
- Primitive: `Corner_Primitive`
- Vertex group: `building_plot`

- Primitive: `PavementEdge_Primitive`
- Vertex group: `building_plot`

Avoid:
- Primitive: `building_plot`
- Vertex group: `building_plot`

Even though Blender technically allows this, it makes debugging, inspection,
tooling, and code review much more confusing because object identity and plot
semantics become visually indistinguishable.

### Prefer stable semantic vertex-group names
Use shared names such as:
- `building_plot`
- `road_plot`
- `park_plot`

Do not encode primitive identity into the vertex-group name unless the code is
explicitly designed for that.

### Mark only the faces that truly belong to the plot
For mixed cells, mark only the relevant 2x2m sub-faces. Do not mark the whole
8x8m primitive just because its dominant role is "building".

---

## Anti-Patterns to Avoid

- Inferring the inner footprint from `primitive_type` alone
- Assuming one outer cell always maps to a full 4x4 inner area
- Computing bounds from cell centers when exact face vertices are available
- Using object names as though they were semantic plot tags
- Reintroducing separate special-case paths for "building modules" when the
  generic category-driven path already exists

---

## Short Version

If a future change affects inner-grid placement, ask this first:

**Is the code using the actual plot-marked faces, or is it silently falling back
to whole-cell assumptions?**

If it is the latter, it is probably heading toward the same class of bug.