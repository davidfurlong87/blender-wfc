# Beginner Guide: Creating a Primitive Pack from Scratch

**Audience:** A brand-new user with basic Blender familiarity and no prior knowledge of this addon.

**Goal:** Start with an empty scene, create a brand new pack with no existing connectors or primitives, add your first connectors, create one or more primitives, save the pack, reload it, and verify that it works with module generation.

---

## What a Pack Is

A **pack** is the main working unit in the WFC addon.

A pack contains:
- pack metadata (name, category, default size, resolution)
- a connector registry for that pack
- one or more primitives
- optionally, a companion `.blend` file for geometry and materials

In practice, you work in this order:
1. **Create a new pack**
2. **Create connectors for that pack**
3. **Create primitives inside that pack**
4. **Assign type + connectors + metadata to each primitive**
5. **Save the pack**
6. **Generate modules and test the result**

---

## Before You Begin

1. Open Blender.
2. Enable the **Blender WFC** addon in **Edit → Preferences → Add-ons**.
3. Open the **3D Viewport**.
4. Press **N** to open the right-hand sidebar if it is hidden.
5. Open the **`wfc`** tab.
6. Confirm that you can see the **WFC Pack** panel and the **Primitive Builder** panel.

Recommended starting conditions:
- use a fresh Blender file
- delete the default cube if you do not need it
- save the `.blend` somewhere sensible before doing major work

---

## Step 1 — Create a New Pack

In **WFC Pack**:
1. Click **New Pack**.
2. Fill in the dialog:
   - **Pack Name** — the user-facing name of the pack
   - **Category** — choose the grid system this pack belongs to
   - **Physical Size** — default size for primitives in this pack
   - **Resolution Multiplier** — how many inner cells fit inside one outer-grid cell
3. Click **OK**.

### Choosing the right defaults

Use these common starting points:
- **Outer-grid pack:** category `outer_grid`, size `8.0`, resolution `1`
- **Building inner-grid pack:** category `building`, size `2.0`, resolution `4`

If you are unsure, start with **`building` / `2.0` / `4`** for small building tiles.

After this step, the Pack panel should show your pack name and its defaults.

---

## Step 2 — Create Connectors for the Pack

A brand new pack starts with no pack-specific connectors, so create them before authoring primitives.

In **WFC Pack → Connector Registry**:
1. Expand **Connector Registry**.
2. Click **Add Connector**.
3. Enter:
   - **Name** — short identifier such as `WALL`, `DOOR`, `WINDOW`, `EMPTY`
   - **Description** — optional human-readable explanation
   - **Compatible With** — comma-separated list of connector names this connector can connect to
   - **Grid Category** — should normally match the pack category
   - **Is Symmetric** — enable if it connects to itself; disable for one-way pairs
4. Click **OK**.
5. Repeat until the pack has the connectors it needs.

### Good first connector set for a building pack

Create these five:
- `WALL` → compatible with `WALL`
- `DOOR` → compatible with `DOOR`
- `WINDOW` → compatible with `WINDOW`
- `HALLWAY` → compatible with `HALLWAY`
- `EMPTY` → compatible with `EMPTY`

If you make a spelling mistake, use **Rename** in the Connector Registry panel.

---

## Step 3 — Create the First Primitive Mesh

1. In Blender, create a mesh with **Shift+A → Mesh**.
2. Model the primitive you want.
3. Rename the object to something descriptive, for example:
   - `Room_A`
   - `Corridor_Straight_A`
   - `Corner_Window_A`
4. Apply transforms in **Object Mode → Ctrl+A → Rotation & Scale**.
5. Add at least one material in **Material Properties**.

### Important modeling rules
- keep the mesh centered and tidy
- use clear object names
- do not use the same name for an object and a vertex group
- for a building inner-grid primitive, model one tile at a time

---

## Step 4 — Assign Primitive Type

With the object selected:
1. In **Primitive Builder**, click **Assign Type**.
2. Choose a built-in type or a custom type.
3. Confirm the object now shows the assigned type.

Choose names that describe the primitive's role, not just its appearance.

---

## Step 5 — Assign Connectors and Metadata

With the object still selected:
1. Click **Assign Connectors & Metadata**.
2. Set:
   - **Grid Category** — should match the active pack
   - **Physical Size** — usually inherits from the pack default
   - **Resolution Multiplier** — usually inherits from the pack default
   - **Rotation Invariant** — enable only if all 4 rotations are equivalent
3. Assign the four edge connectors:
   - **+X** = right side
   - **-X** = left side
   - **+Y** = top side
   - **-Y** = bottom side
4. Click **OK**.

Minimum requirement: the primitive must have a type and all four connectors assigned.

---

## Step 6 — Create More Primitives

Repeat **Step 3** through **Step 5** for each additional primitive.

Use the Pack panel to manage them:
- **Select** — jump to a primitive
- **Rename** — rename it safely
- **Delete** — remove it from the pack

Tip: if several primitives share the same connector pattern, use **Copy Type & Connectors from Active**.

---

## Step 7 — Save the Pack

In **WFC Pack**:
1. Click **Save**.
2. Choose the save format by file extension:
   - **`.json`** → JSON-only pack
   - **`.blend`** → hybrid pack (`pack.blend` + companion `pack.json`)
3. Save the file.

### Recommended choice

For real production work, prefer **saving to `.blend`**.
That writes:
- a `.blend` file for geometry, materials, images, and Blender-native data
- a sidecar `.json` manifest for pack metadata and connector registry

If you already have a JSON-only pack loaded, you can also use **Export as Blend…** later.

---

## Step 8 — Reload the Pack to Verify It

1. Click **Load** in the Pack panel.
2. Load the file you just saved (`.json` or `.blend`).
3. Confirm:
   - the pack name appears correctly
   - primitives appear in the Pack panel
   - the Connector Registry shows your connectors
   - selecting a primitive still shows the correct type and connectors

If this works, the pack structure is valid.

---

## Step 9 — Generate Modules and Test the Workflow

After at least one valid primitive exists in the pack:
1. Use the appropriate module-generation button for your category.
2. Confirm modules are created without errors.
3. If you are testing a building pack, continue into the inner-grid workflow.
4. If you are testing an outer-grid pack, continue into grid generation / collapse.

This is the quickest real validation that your connectors and metadata are coherent.

---

## First-Pack Checklist

- [ ] New pack created
- [ ] Pack category / size / resolution set correctly
- [ ] Connector registry created for the pack
- [ ] At least one primitive mesh created
- [ ] Primitive type assigned
- [ ] All four connectors assigned
- [ ] At least one material assigned
- [ ] Pack saved
- [ ] Pack reloaded successfully
- [ ] Module generation runs without errors

If all ten are true, you have successfully created your first pack from scratch.
