# Beginner Guide: Creating Inner-Building Primitives from Scratch

**Audience:** A user who already understands the basic pack workflow and now wants to create inner-building primitives.

> If you have not created a pack before, start with
> `docs/features/primitives/BEGINNER_PACK_AUTHORING_GUIDE.md` first.

**Goal:** Start in a fresh Blender file, enable the addon, create a new inner-grid building primitive, assign all required metadata in the UI, save it to JSON, and validate that it loads and generates modules correctly.

---

## What You Are Making

This guide is for **inner-grid building primitives** like the examples in:

- `addons/blender-wfc/data/building_library.json`

These are the small **2m x 2m building tiles** used inside the building inner grid.

Examples already in the project:
- `Room`
- `Corridor_H`
- `Corner_Room`
- `Open_Space`

You can use those as references, but this guide is for creating **new geometry that actually looks like the thing you are modeling**.

---

## Important Distinction Before You Start

For this workflow, you are making **inner building modules**, not outer-grid footprint masks.

That means:
- **Grid category should be `building`**
- **Physical size should be `2.0`**
- **Resolution multiplier should be `4`**
- **You do NOT need a `building_plot` vertex group** for basic inner building primitives

`building_plot` vertex groups are mainly important for **outer-grid** primitives that define where inner grids should appear.

---

## Before You Begin

Start with a **fresh Blender file**.

Recommended setup:
- Delete the default cube if you do not need it
- Switch to **Object Mode**
- Save the `.blend` file somewhere convenient

---

## Step 1: Enable the Addon

1. Open Blender.
2. Go to **Edit → Preferences → Add-ons**.
3. Enable the Blender WFC addon.
4. In the 3D Viewport, press **N** to open the right-hand sidebar if it is hidden.
5. Open the **`wfc`** tab.
6. Find the **Primitive Builder** panel.

If you can see **Load from JSON**, the panel is active.

---

## Step 2: Optional Reference Pass

If you want to inspect the existing inner-building primitives first:

1. In **Primitive Builder**, click **Load from JSON**.
2. Open `addons/blender-wfc/data/building_library.json`.
3. The reference primitives will be created in the scene.
4. Study their names, materials, and assigned metadata.

This is optional, but highly recommended for first-time users.

---

## Step 3: Create a New Mesh Object

Create the mesh you actually want to save as a primitive.

Suggested beginner workflow:
1. Press **Shift+A → Mesh** and choose a starting shape such as **Plane** or **Cube**.
2. Rename the object to something clear, for example:
   - `Room_Window_A`
   - `Corridor_Door_A`
   - `Corner_Stair_01`
3. Edit the geometry until it represents the tile you want.

### Modeling rules for this system

- The primitive should represent **one inner building tile**.
- For the standard building inner grid, that means a **2m x 2m footprint**.
- Keep the mesh centered and tidy.
- Before saving, apply transforms with:
  - **Object Mode → Ctrl+A → Rotation & Scale**

Applying transforms is strongly recommended so the saved geometry matches what you intend.

---

## Step 4: Add at Least One Material

The primitive must have at least one material.

1. Select the object.
2. Open the **Material Properties** tab.
3. Add a material slot if needed.
4. Create or assign a material.
5. Give the material a clear name.

Good examples:
- `Building_Room_Window`
- `Building_Corridor_Concrete`
- `Building_Corner_Trim`

The JSON system stores **material names**, so clear names are helpful.

---

## Step 5: Vertex Groups for This Use Case

For **basic inner building primitives**, vertex groups are usually **not required**.

If you do add vertex groups for your own organization:
- keep their names semantic
- keep them distinct from the object name

Avoid this:
- Object name: `building_plot`
- Vertex group: `building_plot`

Prefer this:
- Object name: `Corner_Stair_01`
- Vertex group: `stairs_mask`

---

## Step 6: Assign the Primitive Type

1. Select your mesh object.
2. In **wfc → Primitive Builder**, find **Primitive Type**.
3. Click **Assign Type**.
4. Choose the primitive type that best matches the role of the tile.

Common inner-building choices:
- `ROOM`
- `CORRIDOR`
- `CORNER_ROOM`
- `OPEN_SPACE`

If none of those fit, you can choose a custom type.

After this, the panel should show the assigned type.

---

## Step 7: Assign Connectors and Metadata

1. In **Primitive Builder**, click **Assign Connectors & Metadata**.
2. Fill in the values carefully.

### Required metadata for standard inner-building primitives

- **Grid Category:** `building`
- **Physical Size (m):** `2.0`
- **Resolution Multiplier:** `4`

### Rotation Invariant

Set **Rotation Invariant** to:
- **ON** if rotating the tile gives the same result in all 4 directions
- **OFF** if rotation changes either the geometry or the connector meaning

Examples:
- `Room` with the same walls on all sides → usually **ON**
- `Corridor_H` → usually **OFF**
- `Corner_Room` → usually **OFF**
- `Open_Space` with identical open edges → usually **ON**

### Connector meanings

For building primitives, common connectors include:
- `WALL`
- `DOOR`
- `WINDOW`
- `HALLWAY`
- `EMPTY`

### How to think about +X / -X / +Y / -Y

These refer to the object's **local sides**:
- `+X` = right side
- `-X` = left side
- `+Y` = top side
- `-Y` = bottom side

Think of the tile from a top-down view before module rotation is generated.

### Reference patterns from the existing building library

- `Room` → all four sides `WALL`
- `Corridor_H` → `+X/-X = HALLWAY`, `+Y/-Y = WALL`
- `Corner_Room` → `+X = DOOR`, `+Y = HALLWAY`, `-X/-Y = WALL`
- `Open_Space` → all four sides `EMPTY`

When finished, confirm the object now shows:
- connectors assigned
- category `building`
- size `2.0`
- resolution `4`

---

## Step 8: Validate Before Saving

Use this checklist.

### Minimum UI validation

Your object should now meet all of these:
- it is a **mesh object**
- it has a **primitive type**
- all **4 connectors** are assigned
- the **Grid Metadata** section shows the expected values
- the **Save to JSON** button appears in the panel

### Strong validation checklist

Also confirm these manually:
- the primitive has at least **one material**
- the object name is clear and descriptive
- transforms have been applied with **Ctrl+A → Rotation & Scale**
- the tile footprint matches the intended **2m x 2m** role
- `rotation_invariant` is set correctly
- any vertex groups you created do **not** have the same name as the object

---

## Step 9: Save to JSON

1. In **Primitive Builder**, click **Save to JSON**.
2. Choose a save location.
3. Save the file.

For beginners, saving **one primitive per JSON file** is easiest.

---

## Step 10: Validate by Reloading

This is the safest beginner validation workflow.

1. Open a **new fresh Blender file**.
2. Enable the addon again if needed.
3. Open **wfc → Primitive Builder**.
4. Click **Load from JSON**.
5. Load the JSON file you just saved.

Now verify:
- the object appears successfully
- the object is created in `WFC → WFC_Primitives → WFC_Primitives_building`
- the type/connectors/metadata are still present in the panel
- the material names came back correctly

If the object loads and the panel still shows the correct metadata, the round-trip is working.

---

## Step 11: Validate Module Generation

This is the next-level check and is strongly recommended.

1. With your primitive loaded, go to the main **wfc** workflow panel.
2. Click **Re/Generate Modules**.
3. Inspect the generated building modules in `WFC → WFC_Modules → WFC_Modules_building`.

Expected result:
- if **Rotation Invariant = ON** → you should get **1 module**
- if **Rotation Invariant = OFF** → you should get **4 rotated modules**

If the module count is wrong, the most likely cause is that `rotation_invariant` was set incorrectly.

---

## Common Beginner Mistakes

### “Save to JSON” does not appear
Usually means one of these is missing:
- primitive type
- one or more connectors

### The primitive loads into the wrong category collection
Usually means **Grid Category** was set incorrectly.

### The primitive looks the wrong size after loading
Usually means transforms were not applied before saving, or the geometry footprint does not match the intended 2m tile.

### The primitive generates the wrong number of modules
Usually means **Rotation Invariant** was set incorrectly.

### The primitive is hard to inspect because materials all look the same
Missing materials are now created with quick debug colours automatically, but it is still better to give your real materials clear names.

---

## Recommended Beginner Workflow Summary

For each new inner-building primitive:

1. Create a **2m x 2m mesh**
2. Add at least **one material**
3. **Assign Type**
4. **Assign Connectors & Metadata**
5. Set:
   - `grid_category = building`
   - `physical_size = 2.0`
   - `resolution_multiplier = 4`
6. Save to JSON
7. Load it back into a fresh file
8. Run **Re/Generate Modules**
9. Confirm the module count and rotations are correct

If those steps succeed, the primitive is in good shape for use in the existing inner-grid building workflow.