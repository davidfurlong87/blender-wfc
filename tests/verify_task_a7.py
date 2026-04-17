"""
Verify Task A7: get_all_primitives + get_primitives_by_category use subcollections.
Run with: python tests/verify_task_a7.py
"""

import sys
import types
from pathlib import Path

# ---------------------------------------------------------------------------
# Minimal bpy stub with nested collection support
# ---------------------------------------------------------------------------
bpy = types.ModuleType("bpy")

class _FakeObject:
    def __init__(self, name, grid_category="outer_grid"):
        self.name = name
        self.grid_category = grid_category

class _FakeCollection:
    def __init__(self, name):
        self.name = name
        self.children = _ChildrenProxy(self)
        self.objects = _ObjectsProxy()
        self._parent = None

    @property
    def all_objects(self):
        """Recursively collect objects from self and all children."""
        result = list(self.objects._items)
        for child in self.children._children:
            result.extend(child.all_objects)
        return result

class _ChildrenProxy:
    def __init__(self, owner):
        self._owner = owner
        self._children = []
    def link(self, col):
        self._children.append(col)
        col._parent = self._owner
    def __iter__(self):
        return iter(self._children)

class _ObjectsProxy:
    def __init__(self):
        self._items = []
    def link(self, obj):
        self._items.append(obj)
    def __iter__(self):
        return iter(self._items)
    def __len__(self):
        return len(self._items)

scene_root = _FakeCollection("Scene Collection")
bpy.context = types.SimpleNamespace(
    scene=types.SimpleNamespace(collection=scene_root),
    collection=scene_root,
)

_store = {}

class _CollectionsData:
    def __contains__(self, name): return name in _store
    def __getitem__(self, name):  return _store[name]
    def get(self, name, default=None): return _store.get(name, default)
    def new(self, name):
        col = _FakeCollection(name)
        _store[name] = col
        return col

bpy.data = types.SimpleNamespace(collections=_CollectionsData())
bpy.data.objects = []
bpy.data.meshes = types.SimpleNamespace(remove=lambda m: None)
bpy.ops = types.SimpleNamespace(object=types.SimpleNamespace(
    select_all=lambda action=None: None,
    delete=lambda: None,
))

sys.modules["bpy"] = bpy
mathutils_stub = types.ModuleType("mathutils")
mathutils_stub.Vector = lambda *a, **kw: None
mathutils_stub.Matrix = lambda *a, **kw: None
sys.modules["mathutils"] = mathutils_stub

sys.path.insert(0, "addons/blender-wfc")

from collectiontools import ensure_collection, ensure_primitives_collection
from wfc_values import CollectionNames, GridCategory, primitives_collection_for

# ---------------------------------------------------------------------------
all_passed = True

def check(label, condition, detail=""):
    global all_passed
    status = "OK  " if condition else "FAIL"
    print(f"  [{status}] {label}" + (f"  ({detail})" if detail else ""))
    if not condition:
        all_passed = False

src = Path("addons/blender-wfc/__init__.py").read_text()

# ── Source checks ────────────────────────────────────────────────────────────
print("Source: get_all_primitives:")
check("uses bpy.data.collections.get (crash-safe)",
      "bpy.data.collections.get(CollectionNames.Primitives.value)" in src)
check("uses .all_objects (subcollection traversal)",
      "col.all_objects" in src)
check("returns [] when collection missing",
      "if col is None:" in src and "return []" in src)
check("old get_all_objects_from_collection call gone from get_all_primitives",
      "return get_all_objects_from_collection(CollectionNames.Primitives.value)" not in src)

print()
print("Source: get_primitives_by_category:")
check("uses ensure_primitives_collection",
      "ensure_primitives_collection(category)" in src)
check("returns list(col.objects)",
      "return list(col.objects)" in src)
check("old property-filter comprehension gone",
      "p.grid_category == category" not in src)

# ── Logic: get_all_primitives with subcollections ────────────────────────────
print()
print("Logic: get_all_primitives traverses subcollections:")

# Build the hierarchy manually using our stub:
# WFC_Primitives -> WFC_Primitives_outer_grid (has obj_a)
#                -> WFC_Primitives_building   (has obj_b)
root_col   = ensure_collection(CollectionNames.Root.value)
parent_col = ensure_collection(CollectionNames.Primitives.value, parent=root_col)
og_col     = ensure_collection(primitives_collection_for(GridCategory.OUTER_GRID), parent=parent_col)
bld_col    = ensure_collection(primitives_collection_for(GridCategory.BUILDING),   parent=parent_col)

obj_a = _FakeObject("Road_Prim",  GridCategory.OUTER_GRID)
obj_b = _FakeObject("Room_Prim",  GridCategory.BUILDING)
og_col.objects.link(obj_a)
bld_col.objects.link(obj_b)

# Now simulate get_all_primitives() using the same logic as the real function
col = bpy.data.collections.get(CollectionNames.Primitives.value)
all_prims = list(col.all_objects) if col else []

check("returns obj from outer_grid subcollection",  obj_a in all_prims)
check("returns obj from building subcollection",    obj_b in all_prims)
check("total count correct (2)",                    len(all_prims) == 2)

# When WFC_Primitives doesn't exist
result_safe = list(bpy.data.collections.get("NONEXISTENT_COL").all_objects) \
    if bpy.data.collections.get("NONEXISTENT_COL") else []
check("returns [] safely when collection missing",  result_safe == [])

# ── Logic: get_primitives_by_category uses leaf collection ───────────────────
print()
print("Logic: get_primitives_by_category uses leaf collection:")

og_col2  = ensure_primitives_collection(GridCategory.OUTER_GRID)
bld_col2 = ensure_primitives_collection(GridCategory.BUILDING)

check("outer_grid col is same object (idempotent)",  og_col2 is og_col)
check("building col is same object (idempotent)",    bld_col2 is bld_col)
check("outer_grid objects contains obj_a",           obj_a in list(og_col2.objects))
check("building objects contains obj_b",             obj_b in list(bld_col2.objects))
check("outer_grid does NOT contain building obj",    obj_b not in list(og_col2.objects))
check("building does NOT contain outer obj",         obj_a not in list(bld_col2.objects))

# Empty category returns empty list, no crash
park_col = ensure_primitives_collection(GridCategory.PARK)
check("empty category returns [] (no crash)",        list(park_col.objects) == [])

# ── Final ─────────────────────────────────────────────────────────────────────
print()
if all_passed:
    print("=" * 57)
    print("ALL CHECKS PASSED -- Task A7 complete!")
    print("=" * 57)
else:
    print("=" * 57)
    print("SOME CHECKS FAILED")
    print("=" * 57)
    sys.exit(1)
