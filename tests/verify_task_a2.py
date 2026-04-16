"""
Verify Task A2: get_or_create_collection accepts a parent parameter.
Run with: python tests/verify_task_a2.py
"""

import sys
import types
from pathlib import Path

# ---------------------------------------------------------------------------
# Minimal bpy stub — enough to exercise collection_creation.py logic
# ---------------------------------------------------------------------------
bpy = types.ModuleType("bpy")
bpy.ops = types.ModuleType("bpy.ops")
bpy.ops.object = types.SimpleNamespace(
    select_all=lambda action: None,
    delete=lambda: None,
)

class _FakeCollection:
    def __init__(self, name):
        self.name = name
        self.children = _ChildrenProxy(self)
        self.objects = []

    def __repr__(self):
        return f"<Collection '{self.name}'>"

class _ChildrenProxy:
    def __init__(self, owner):
        self._owner = owner
        self._children = []

    def link(self, col):
        self._children.append(col)
        col._parent = self._owner

    def __iter__(self):
        return iter(self._children)

# Scene has one root collection
scene_root = _FakeCollection("Scene Collection")

bpy.context = types.SimpleNamespace(
    scene=types.SimpleNamespace(collection=scene_root),
    collection=scene_root,
)

_collections_store = {}

class _CollectionsData:
    def __contains__(self, name):
        return name in _collections_store
    def __getitem__(self, name):
        return _collections_store[name]
    def new(self, name):
        col = _FakeCollection(name)
        _collections_store[name] = col
        return col

bpy.data = types.SimpleNamespace(collections=_CollectionsData())
bpy.data.objects = []
bpy.data.meshes = types.SimpleNamespace(remove=lambda m: None)

sys.modules["bpy"] = bpy
sys.modules["bpy.ops"] = bpy.ops
mathutils_stub = types.ModuleType("mathutils")
mathutils_stub.Vector = lambda *a, **kw: None
mathutils_stub.Matrix = lambda *a, **kw: None
sys.modules["mathutils"] = mathutils_stub

sys.path.insert(0, "addons/blender-wfc")

from collectiontools.collection_creation import (
    get_or_create_collection,
    check_collection_exists,
)

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
all_passed = True

def check(label, condition, detail=""):
    global all_passed
    status = "OK  " if condition else "FAIL"
    print(f"  [{status}] {label}" + (f"  ({detail})" if detail else ""))
    if not condition:
        all_passed = False


# -- Backward compat: no parent → links to scene root ----------------------
print("Backward compat (no parent arg):")
col_a = get_or_create_collection("WFC_Test_A")
check("collection created",                "WFC_Test_A" in bpy.data.collections)
check("linked to scene root",              col_a in list(scene_root.children))
check("returns collection object",         col_a.name == "WFC_Test_A")

col_a2 = get_or_create_collection("WFC_Test_A")
check("existing collection returned",      col_a2 is col_a)
check("scene root children count stable",
      len([c for c in scene_root.children if c.name == "WFC_Test_A"]) == 1)


# -- New behaviour: parent provided → links to parent ----------------------
print()
print("New behaviour (parent provided):")
parent_col = get_or_create_collection("WFC_Modules")
check("parent collection created",         "WFC_Modules" in bpy.data.collections)

child_col = get_or_create_collection("WFC_Modules_building", parent=parent_col)
check("child collection created",          "WFC_Modules_building" in bpy.data.collections)
check("linked to parent, not scene root",  child_col in list(parent_col.children))
check("NOT directly under scene root",
      child_col not in [c for c in scene_root.children])
check("child._parent is parent_col",       getattr(child_col, "_parent", None) is parent_col)


# -- parent=None explicitly → same as no parent ----------------------------
print()
print("parent=None explicit:")
col_b = get_or_create_collection("WFC_Test_B", parent=None)
check("links to scene root when parent=None", col_b in list(scene_root.children))


# -- Existing collection: returned as-is, not re-parented ------------------
print()
print("Existing collection not re-parented:")
other_parent = get_or_create_collection("WFC_Other_Parent")
child_col_again = get_or_create_collection("WFC_Modules_building", parent=other_parent)
check("same object returned",              child_col_again is child_col)
check("original parent unchanged",        getattr(child_col, "_parent", None) is parent_col)


# -- b_delete_objects still works (backward compat) ------------------------
print()
print("b_delete_objects backward compat:")
src = Path("addons/blender-wfc/collectiontools/collection_creation.py").read_text()
check("b_delete_objects param still present",
      "b_delete_objects=False" in src)
check("parent param added after b_delete_objects",
      src.index("parent=None") > src.index("b_delete_objects=False"))


# -- Source checks ---------------------------------------------------------
print()
print("Source checks:")
check("attach_to logic present",
      "attach_to = parent if parent is not None else" in src)
check("attach_to.children.link(collection) used",
      "attach_to.children.link(collection)" in src)
check("hardcoded scene.collection.children.link gone",
      "bpy.context.scene.collection.children.link" not in src)


print()
if all_passed:
    print("=" * 55)
    print("ALL CHECKS PASSED -- Task A2 complete!")
    print("=" * 55)
else:
    print("=" * 55)
    print("SOME CHECKS FAILED")
    print("=" * 55)
    sys.exit(1)
