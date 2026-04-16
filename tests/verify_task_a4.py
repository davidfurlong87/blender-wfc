"""
Verify Task A4: ensure_primitives_collection / ensure_modules_collection /
                ensure_grid_collection
Run with: python tests/verify_task_a4.py
"""

import sys
import types
from pathlib import Path

# ---------------------------------------------------------------------------
# Minimal bpy stub
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

from collectiontools import (
    ensure_primitives_collection,
    ensure_modules_collection,
    ensure_grid_collection,
)
from wfc_values import CollectionNames, GridCategory

# ---------------------------------------------------------------------------
all_passed = True

def check(label, condition, detail=""):
    global all_passed
    status = "OK  " if condition else "FAIL"
    print(f"  [{status}] {label}" + (f"  ({detail})" if detail else ""))
    if not condition:
        all_passed = False


# -- ensure_primitives_collection -------------------------------------------
print("ensure_primitives_collection:")
col = ensure_primitives_collection(GridCategory.BUILDING)
check("returns a collection",             col is not None)
check("leaf name correct",                col.name == "WFC_Primitives_building")
check("leaf parent is WFC_Primitives",    col._parent is not None and
                                          col._parent.name == CollectionNames.Primitives.value)
check("WFC_Primitives parent is WFC",     col._parent._parent is not None and
                                          col._parent._parent.name == CollectionNames.Root.value)
check("WFC created in store",             CollectionNames.Root.value in bpy.data.collections)
check("WFC_Primitives created in store",  CollectionNames.Primitives.value in bpy.data.collections)
check("WFC_Primitives_building created",  "WFC_Primitives_building" in bpy.data.collections)

print()
print("ensure_primitives_collection idempotent:")
col2 = ensure_primitives_collection(GridCategory.BUILDING)
check("same leaf object returned",        col2 is col)
branch = bpy.data.collections[CollectionNames.Primitives.value]
check("branch not duplicated",            len([c for c in branch.children if c.name == "WFC_Primitives_building"]) == 1)

print()
print("ensure_primitives_collection different category:")
col3 = ensure_primitives_collection(GridCategory.OUTER_GRID)
check("new leaf for outer_grid",          col3.name == "WFC_Primitives_outer_grid")
check("shares same branch parent",        col3._parent is col._parent)


# -- ensure_modules_collection ----------------------------------------------
print()
print("ensure_modules_collection:")
mod_col = ensure_modules_collection(GridCategory.BUILDING)
check("returns a collection",             mod_col is not None)
check("leaf name correct",                mod_col.name == "WFC_Modules_building")
check("leaf parent is WFC_Modules",       mod_col._parent is not None and
                                          mod_col._parent.name == CollectionNames.Modules.value)
check("WFC_Modules parent is WFC",        mod_col._parent._parent is not None and
                                          mod_col._parent._parent.name == CollectionNames.Root.value)
check("WFC_Modules root is same WFC",     mod_col._parent._parent is
                                          bpy.data.collections[CollectionNames.Root.value])

print()
print("ensure_modules_collection idempotent:")
mod_col2 = ensure_modules_collection(GridCategory.BUILDING)
check("same leaf returned",               mod_col2 is mod_col)


# -- ensure_grid_collection -------------------------------------------------
print()
print("ensure_grid_collection:")
grid_col = ensure_grid_collection(GridCategory.OUTER_GRID)
check("returns a collection",             grid_col is not None)
check("leaf name correct",                grid_col.name == "WFC_Grid_outer_grid")
check("leaf parent is WFC_Grid",          grid_col._parent is not None and
                                          grid_col._parent.name == CollectionNames.Grid.value)
check("WFC_Grid parent is WFC",           grid_col._parent._parent is not None and
                                          grid_col._parent._parent.name == CollectionNames.Root.value)

print()
print("ensure_grid_collection works for any depth:")
deep = ensure_grid_collection("room_detail")
check("arbitrary category works",         deep.name == "WFC_Grid_room_detail")
check("shares same WFC_Grid branch",      deep._parent is grid_col._parent)


# -- Branches are isolated between branches ---------------------------------
print()
print("Branch isolation:")
prim_branch   = bpy.data.collections[CollectionNames.Primitives.value]
mod_branch    = bpy.data.collections[CollectionNames.Modules.value]
grid_branch   = bpy.data.collections[CollectionNames.Grid.value]
check("Primitives and Modules are distinct", prim_branch is not mod_branch)
check("Modules and Grid are distinct",       mod_branch is not grid_branch)
check("all three share same root WFC",
      prim_branch._parent is mod_branch._parent is grid_branch._parent)


# -- Package-level import ---------------------------------------------------
print()
print("Package export:")
src = Path("addons/blender-wfc/collectiontools/__init__.py").read_text()
check("ensure_primitives_collection defined", "def ensure_primitives_collection(" in src)
check("ensure_modules_collection defined",    "def ensure_modules_collection(" in src)
check("ensure_grid_collection defined",       "def ensure_grid_collection(" in src)
check("imports CollectionNames",              "CollectionNames" in src)
check("imports primitives_collection_for",    "primitives_collection_for" in src)
check("imports modules_collection_for",       "modules_collection_for" in src)
check("imports grid_collection_for",          "grid_collection_for" in src)


# ---------------------------------------------------------------------------
print()
if all_passed:
    print("=" * 57)
    print("ALL CHECKS PASSED -- Task A4 complete!")
    print("=" * 57)
else:
    print("=" * 57)
    print("SOME CHECKS FAILED")
    print("=" * 57)
    sys.exit(1)
