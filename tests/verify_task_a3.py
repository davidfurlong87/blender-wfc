"""
Verify Task A3: ensure_collection — universal crash-safe collection getter.
Run with: python tests/verify_task_a3.py
"""

import sys
import types
from pathlib import Path

# ---------------------------------------------------------------------------
# Minimal bpy stub (same pattern as verify_task_a2.py)
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
        self._parent = None

class _ChildrenProxy:
    def __init__(self, owner):
        self._owner = owner
        self._children = []
    def link(self, col):
        self._children.append(col)
        col._parent = self._owner
    def __iter__(self):
        return iter(self._children)

scene_root = _FakeCollection("Scene Collection")
bpy.context = types.SimpleNamespace(
    scene=types.SimpleNamespace(collection=scene_root),
    collection=scene_root,
)

_store = {}

class _CollectionsData:
    def __contains__(self, name): return name in _store
    def __getitem__(self, name):  return _store[name]
    def new(self, name):
        col = _FakeCollection(name)
        _store[name] = col
        return col

bpy.data = types.SimpleNamespace(collections=_CollectionsData())
bpy.data.objects = []
bpy.data.meshes = types.SimpleNamespace(remove=lambda m: None)

sys.modules["bpy"] = bpy
mathutils_stub = types.ModuleType("mathutils")
mathutils_stub.Vector = lambda *a, **kw: None
mathutils_stub.Matrix = lambda *a, **kw: None
sys.modules["mathutils"] = mathutils_stub

sys.path.insert(0, "addons/blender-wfc")

from collectiontools.collection_creation import ensure_collection, get_or_create_collection

# ---------------------------------------------------------------------------
all_passed = True

def check(label, condition, detail=""):
    global all_passed
    status = "OK  " if condition else "FAIL"
    print(f"  [{status}] {label}" + (f"  ({detail})" if detail else ""))
    if not condition:
        all_passed = False


# -- Missing collection created, no parent → scene root --------------------
print("Missing collection, no parent:")
col = ensure_collection("WFC_New_A")
check("returns a collection",           col is not None)
check("has correct name",               col.name == "WFC_New_A")
check("created in data store",          "WFC_New_A" in bpy.data.collections)
check("linked under scene root",        col in list(scene_root.children))


# -- Missing collection, parent provided → child of parent -----------------
print()
print("Missing collection, parent provided:")
parent = ensure_collection("WFC_Modules")
child  = ensure_collection("WFC_Modules_park", parent=parent)
check("child created",                  "WFC_Modules_park" in bpy.data.collections)
check("child linked under parent",      child in list(parent.children))
check("child NOT under scene root",     child not in list(scene_root.children))
check("child._parent is parent",        child._parent is parent)


# -- Existing collection returned as-is ------------------------------------
print()
print("Existing collection returned as-is:")
col2 = ensure_collection("WFC_New_A")
check("same object returned",           col2 is col)
check("scene root children stable",
      len([c for c in scene_root.children if c.name == "WFC_New_A"]) == 1)

other_parent = ensure_collection("WFC_Other")
col3 = ensure_collection("WFC_New_A", parent=other_parent)
check("existing col not re-parented",   col3._parent is not other_parent)


# -- Never raises, never returns None --------------------------------------
print()
print("Safety guarantees:")
try:
    result = ensure_collection("WFC_Brand_New_Safe")
    check("does not raise on new collection", True)
    check("result is not None",              result is not None)
except Exception as e:
    check("does not raise on new collection", False, str(e))
    check("result is not None",              False)


# -- No b_delete_objects footgun -------------------------------------------
print()
print("API cleanliness:")
import inspect
sig = inspect.signature(ensure_collection)
check("no b_delete_objects parameter",  "b_delete_objects" not in sig.parameters)
check("has collection_name parameter",  "collection_name"  in sig.parameters)
check("has parent parameter",           "parent"           in sig.parameters)


# -- Importable from collectiontools package -------------------------------
print()
print("Package export:")
try:
    from collectiontools import ensure_collection as ec
    check("importable from collectiontools package", ec is ensure_collection)
except ImportError as e:
    check("importable from collectiontools package", False, str(e))


# -- Source checks ---------------------------------------------------------
print()
print("Source checks:")
src = Path("addons/blender-wfc/collectiontools/collection_creation.py").read_text()
check("ensure_collection defined",          "def ensure_collection(" in src)
check("delegates to get_or_create_collection",
      "return get_or_create_collection(" in src)
check("appears after get_or_create_collection in file",
      src.index("def ensure_collection(") > src.index("def get_or_create_collection("))
check("docstring mentions recommended for new code",
      "recommended" in src)


print()
if all_passed:
    print("=" * 55)
    print("ALL CHECKS PASSED -- Task A3 complete!")
    print("=" * 55)
else:
    print("=" * 55)
    print("SOME CHECKS FAILED")
    print("=" * 55)
    sys.exit(1)
