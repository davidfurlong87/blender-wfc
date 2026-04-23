"""
Stage 7 PoC — bpy.data.libraries.write() round-trip verification
=================================================================

PURPOSE
-------
Verify that bpy.data.libraries.write() correctly preserves all data
the WFC pack loader will need: mesh geometry, materials, vertex groups,
and WFC custom properties stored as IDProperties.

HOW TO RUN
----------
1. Open Blender.
2. Switch to the Scripting workspace.
3. Open this file (Text > Open).
4. Click Run Script.
5. Check the System Console for results (Window > Toggle System Console).

DO NOT import this file as a Python module — it uses bpy and requires
an active Blender session.

FINDINGS (confirmed after three runs)
--------------------------------------
WRITE PATH — bpy.data.libraries.write()                          CONFIRMED ✓
  [x] Collection data-block is written correctly
  [x] Object, mesh, and material data-blocks are written when
      included in the datablocks set
  [x] All four types must be gathered EXPLICITLY — write() does NOT
      auto-traverse dependencies from the collection root
  [x] Dependency gathering pattern (see write_blend() below):
        datablocks = {col}
        for obj in col.all_objects:
            datablocks.add(obj)
            if obj.data: datablocks.add(obj.data)
            for slot in obj.material_slots:
                if slot.material: datablocks.add(slot.material)

READ PATH — bpy.data.libraries.load()                            CONFIRMED ✓
  [x] Collection appears in src.collections after load
  [x] Collection membership IS correctly restored when all required
      types are requested in the same context manager:
        dst.collections = [COLLECTION_NAME]
        dst.objects     = list(src.objects)
        dst.meshes      = list(src.meshes)
        dst.materials   = list(src.materials)
  [x] Requesting dst.collections ALONE returns the collection shell
      with an empty objects list — every type must be requested.
  [!] NAME COLLISION HAZARD: removing a collection does NOT delete
      its objects or meshes — they become orphans in bpy.data.
      When the file is loaded again, Blender renames the loaded
      copies to avoid conflicts (poc_room → poc_room.001).
      The collection holds poc_room.001; lookups for 'poc_room'
      find the old orphan which is not in the collection → None.
  [x] FIX: explicitly delete objects AND mesh data-blocks before
      loading (see full cleanup in append_and_verify() below).
  [x] PRODUCTION IMPLICATION: the pack loader must always purge
      objects AND their mesh data-blocks (not just unlink from scene)
      before reloading. clear_all_primitives() already does this.

RECOMMENDATION FOR PRODUCTION LOADER (Task 5)
  Use bpy.data.libraries.load() with explicit type requests (Option A).
  The API works correctly. The only rule is: purge existing data-blocks
  by name before loading to prevent Blender's .001 rename behaviour.
  bpy.ops.wm.append() (Option B) remains a valid alternative if a
  single-call approach is preferred, but is not required.
"""

import bpy
import os
import tempfile

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

COLLECTION_NAME = "WFC_PoC_Primitives"
OBJECT_NAME     = "poc_room"
MATERIAL_NAME   = "WFC_PoC_Material"


# ---------------------------------------------------------------------------
# Step 1 — build a minimal test collection
# ---------------------------------------------------------------------------

def _clean(names):
    for name in names:
        obj = bpy.data.objects.get(name)
        if obj:
            bpy.data.objects.remove(obj, do_unlink=True)
        col = bpy.data.collections.get(name)
        if col:
            bpy.data.collections.remove(col)
        mat = bpy.data.materials.get(name)
        if mat:
            bpy.data.materials.remove(mat)


def build_test_collection():
    _clean([COLLECTION_NAME, OBJECT_NAME, MATERIAL_NAME])

    mesh = bpy.data.meshes.new(OBJECT_NAME)
    mesh.from_pydata(
        [(-1, -1, 0), (-1, 1, 0), (1, 1, 0), (1, -1, 0)],
        [],
        [(0, 1, 2, 3)],
    )

    obj = bpy.data.objects.new(OBJECT_NAME, mesh)

    mat = bpy.data.materials.new(MATERIAL_NAME)
    mat.diffuse_color = (0.8, 0.2, 0.2, 1.0)
    obj.data.materials.append(mat)

    vg = obj.vertex_groups.new(name="building_plot")
    vg.add(list(range(4)), 1.0, 'ADD')

    # WFC metadata as IDProperties (the internal storage Blender uses for
    # both registered bpy.props and plain custom properties)
    obj["primitive_type"]       = "ROOM"
    obj["pos_x_connector"]      = "WALL"
    obj["neg_x_connector"]      = "WALL"
    obj["pos_y_connector"]      = "HALLWAY"
    obj["neg_y_connector"]      = "WALL"
    obj["physical_size"]        = 2.0
    obj["grid_category"]        = "building"
    obj["resolution_multiplier"] = 4

    col = bpy.data.collections.new(COLLECTION_NAME)
    bpy.context.scene.collection.children.link(col)
    col.objects.link(obj)

    return col, obj


# ---------------------------------------------------------------------------
# Step 2 — write to a temp .blend file
# ---------------------------------------------------------------------------

def write_blend(col, filepath):
    datablocks = {col}
    for obj in col.all_objects:
        datablocks.add(obj)
        if obj.data:
            datablocks.add(obj.data)
        for slot in obj.material_slots:
            if slot.material:
                datablocks.add(slot.material)

    bpy.data.libraries.write(filepath, datablocks, fake_user=False)
    print(f"[PoC] Written {len(datablocks)} datablocks → {filepath}")


# ---------------------------------------------------------------------------
# Step 3 — append back and verify
# ---------------------------------------------------------------------------

def append_and_verify(filepath):
    # Full teardown before loading.
    #
    # Removing a collection does NOT delete its objects or meshes — they
    # become orphans in bpy.data.  If they are still present when the file
    # is loaded, Blender renames the incoming copies (poc_room → poc_room.001)
    # to avoid conflicts.  The collection then holds poc_room.001 while any
    # name-based lookup for 'poc_room' finds the old orphan → None.
    #
    # Fix: delete objects AND their mesh data-blocks explicitly first.
    col = bpy.data.collections.get(COLLECTION_NAME)
    if col:
        for obj in list(col.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        for scene in bpy.data.scenes:
            if COLLECTION_NAME in scene.collection.children:
                scene.collection.children.unlink(col)
        bpy.data.collections.remove(col)

    # Belt-and-braces: also purge any remaining orphans with our known names.
    orphan_obj = bpy.data.objects.get(OBJECT_NAME)
    if orphan_obj:
        bpy.data.objects.remove(orphan_obj, do_unlink=True)
    orphan_mesh = bpy.data.meshes.get(OBJECT_NAME)
    if orphan_mesh and orphan_mesh.users == 0:
        bpy.data.meshes.remove(orphan_mesh)
    orphan_mat = bpy.data.materials.get(MATERIAL_NAME)
    if orphan_mat and orphan_mat.users == 0:
        bpy.data.materials.remove(orphan_mat)

    with bpy.data.libraries.load(filepath, link=False) as (src, dst):
        print(f"[PoC] Collections in file: {src.collections}")
        print(f"[PoC] Objects in file:     {src.objects}")
        print(f"[PoC] Meshes in file:      {src.meshes}")
        print(f"[PoC] Materials in file:   {src.materials}")

        if COLLECTION_NAME not in src.collections:
            print(f"[PoC] ERROR: '{COLLECTION_NAME}' not found in saved file")
            return False

        # KEY FINDING: bpy.data.libraries.load() is fully explicit.
        # Requesting dst.collections alone returns an empty collection —
        # every type you need must be requested separately.
        dst.collections = [COLLECTION_NAME]
        dst.objects     = list(src.objects)
        dst.meshes      = list(src.meshes)
        dst.materials   = list(src.materials)

    appended = bpy.data.collections.get(COLLECTION_NAME)
    if not appended:
        print("[PoC] ERROR: collection missing after append")
        return False
    bpy.context.scene.collection.children.link(appended)

    print(f"[PoC] appended.objects after load: {[o.name for o in appended.objects]}")

    obj = appended.objects.get(OBJECT_NAME)
    if not obj:
        print("[PoC] ERROR: object missing from appended collection")
        return False

    results = []

    def check(label, value):
        ok = bool(value)
        results.append((ok, label))
        return ok

    check("mesh — 4 vertices",                 len(obj.data.vertices) == 4)
    check("mesh — 1 face",                     len(obj.data.polygons) == 1)
    check("material slot present",             len(obj.material_slots) > 0)
    check("material not None",                 obj.material_slots[0].material is not None)
    check("vertex group 'building_plot'",      "building_plot" in obj.vertex_groups)
    check("primitive_type == ROOM",            obj.get("primitive_type") == "ROOM")
    check("pos_x_connector == WALL",           obj.get("pos_x_connector") == "WALL")
    check("pos_y_connector == HALLWAY",        obj.get("pos_y_connector") == "HALLWAY")
    check("physical_size == 2.0",              obj.get("physical_size") == 2.0)
    check("grid_category == building",         obj.get("grid_category") == "building")
    check("resolution_multiplier == 4",        obj.get("resolution_multiplier") == 4)

    passed = sum(1 for ok, _ in results if ok)
    total  = len(results)

    print("\n[PoC] === Round-trip results ===")
    for ok, label in results:
        icon = "OK  " if ok else "FAIL"
        print(f"  [{icon}] {label}")

    print(f"\n[PoC] {passed}/{total} checks passed")
    return passed == total


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

_tmp_fh = tempfile.NamedTemporaryFile(suffix=".blend", delete=False)
_tmp_fh.close()
tmp = _tmp_fh.name
print("\n[PoC] ========================================")
print("[PoC] Stage 7 — Blend round-trip PoC")
print(f"[PoC] Temp file: {tmp}")

col, _obj = build_test_collection()
write_blend(col, tmp)
success = append_and_verify(tmp)

try:
    os.remove(tmp)
    print(f"[PoC] Cleaned up {tmp}")
except OSError:
    pass

if success:
    print("\n[PoC] ✓ bpy.data.libraries.write() is viable for pack export")
else:
    print("\n[PoC] ✗ Some checks failed — update findings in docstring")
