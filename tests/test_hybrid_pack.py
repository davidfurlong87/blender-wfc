"""
Stage 7 — hybrid pack infrastructure tests
===========================================

Tests that can be run without Blender covering:
  - slugify_collection_name
  - resolve_blend_path
  - find_companion_json
  - save_primitive_library with blend_source / blend_collection
  - load_primitive_library with hybrid manifests
  - pack_state hybrid fields (blend_filepath, source_mode, is_hybrid, etc.)
"""

import json
import os
import sys
import tempfile
from types import SimpleNamespace

# ── path setup ────────────────────────────────────────────────────────────────
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, 'addons', 'blender-wfc'))

from primitive_persistence import (
    PrimitivePersistence,
    slugify_collection_name,
    resolve_blend_path,
    find_companion_json,
)
from pack_state import (
    set_active_pack,
    get_active_pack,
    clear_active_pack,
    is_hybrid,
    get_blend_filepath,
    has_active_pack,
    update_active_pack_filepath,
    update_active_pack_blend_filepath,
)

# ── helpers ───────────────────────────────────────────────────────────────────

_passed = 0
_failed = 0


def check(label: str, condition: bool) -> bool:
    global _passed, _failed
    if condition:
        print(f"  [OK  ] {label}")
        _passed += 1
    else:
        print(f"  [FAIL] {label}")
        _failed += 1
    return condition


# ── slugify_collection_name ───────────────────────────────────────────────────

def test_slugify():
    print("\nslugify_collection_name:")
    check("simple two-word name",
          slugify_collection_name("Building Pack") == "Building_Pack_Primitives")
    check("lower-case with spaces",
          slugify_collection_name("my building pack") == "my_building_pack_Primitives")
    check("trailing punctuation stripped",
          slugify_collection_name("building!!") == "building_Primitives")
    check("empty string → WFC_Primitives",
          slugify_collection_name("") == "WFC_Primitives")
    check("pure punctuation → WFC_Primitives",
          slugify_collection_name("!!!") == "WFC_Primitives")
    check("stable across repeated calls",
          slugify_collection_name("Test Pack") == slugify_collection_name("Test Pack"))
    check("hyphens treated like spaces",
          slugify_collection_name("my-pack") == "my_pack_Primitives")


# ── resolve_blend_path ────────────────────────────────────────────────────────

def test_resolve_blend_path():
    print("\nresolve_blend_path:")
    result = resolve_blend_path('/packs/building/pack.json', 'pack.blend')
    check("resolves filename relative to JSON directory",
          result.endswith(os.path.join('building', 'pack.blend')))
    check("returns a string",
          isinstance(result, str))


# ── find_companion_json ───────────────────────────────────────────────────────

def test_find_companion_json():
    print("\nfind_companion_json:")
    with tempfile.TemporaryDirectory() as tmpdir:
        blend_path = os.path.join(tmpdir, 'pack.blend')
        json_path  = os.path.join(tmpdir, 'pack.json')

        open(blend_path, 'w').close()

        check("returns None when no JSON exists",
              find_companion_json(blend_path) is None)

        open(json_path, 'w').close()
        result = find_companion_json(blend_path)
        check("returns path when JSON exists",
              result is not None)
        check("returned path ends with pack.json",
              result is not None and result.endswith('pack.json'))


# ── persistence: save + load with hybrid fields ───────────────────────────────

def test_hybrid_persistence():
    print("\nsave_primitive_library with blend fields:")
    persistence = PrimitivePersistence()

    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = os.path.join(tmpdir, 'pack.json')

        ok, errs = persistence.save_primitive_library(
            primitives=[],
            filepath=json_path,
            library_name="Test Pack",
            blend_source="pack.blend",
            blend_collection="Test_Pack_Primitives",
        )
        check("save returns success",          ok)
        check("no save errors",                errs == [])
        check("file was created",              os.path.exists(json_path))

        with open(json_path) as f:
            data = json.load(f)
        meta = data.get('library_metadata', {})
        check("blend_source written to JSON",      meta.get('blend_source') == 'pack.blend')
        check("blend_collection written to JSON",  meta.get('blend_collection') == 'Test_Pack_Primitives')

        print("\nload_primitive_library with hybrid manifest:")
        prims, loaded_meta, errs = persistence.load_primitive_library(json_path)
        check("blend_source in loaded metadata",
              loaded_meta.get('blend_source') == 'pack.blend')
        check("blend_collection in loaded metadata",
              loaded_meta.get('blend_collection') == 'Test_Pack_Primitives')
        check("empty hybrid pack produces no fatal error",
              not any(e == "No primitives found in library file" for e in errs))

    print("\nload_primitive_library with JSON-only empty pack (must still error):")
    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = os.path.join(tmpdir, 'empty.json')
        ok, errs2 = persistence.save_primitive_library(
            primitives=[], filepath=json_path, library_name="Empty"
        )
        _prims, _meta, load_errs = persistence.load_primitive_library(json_path)
        check("JSON-only empty pack still reports error",
              any("No primitives found" in e for e in load_errs))


# ── pack_state: hybrid fields ─────────────────────────────────────────────────

def test_pack_state_hybrid():
    print("\npack_state — JSON-only (defaults):")
    clear_active_pack()
    set_active_pack(name="TestPack", category="building", filepath="/tmp/pack.json")
    pack = get_active_pack()
    check("source_mode defaults to 'json_only'",  pack['source_mode'] == 'json_only')
    check("blend_filepath defaults to None",       pack['blend_filepath'] is None)
    check("is_hybrid() False for json_only pack",  not is_hybrid())
    check("get_blend_filepath() returns None",     get_blend_filepath() is None)

    print("\npack_state — hybrid pack:")
    set_active_pack(
        name="HybridPack", category="building",
        filepath="/tmp/pack.json",
        blend_filepath="/tmp/pack.blend",
        source_mode="hybrid",
    )
    pack = get_active_pack()
    check("source_mode stored correctly",           pack['source_mode'] == 'hybrid')
    check("blend_filepath stored correctly",        pack['blend_filepath'] == '/tmp/pack.blend')
    check("is_hybrid() True for hybrid pack",       is_hybrid())
    check("get_blend_filepath() returns blend path", get_blend_filepath() == '/tmp/pack.blend')

    print("\npack_state — update_active_pack_blend_filepath:")
    set_active_pack(name="T", category="building")
    update_active_pack_blend_filepath("/tmp/new.blend")
    check("blend_filepath updated",      get_blend_filepath() == '/tmp/new.blend')
    check("source_mode set to hybrid",   get_active_pack()['source_mode'] == 'hybrid')

    print("\npack_state — rename preserves hybrid fields (simulated):")
    set_active_pack(
        name="OriginalName", category="building",
        filepath="/tmp/pack.json",
        blend_filepath="/tmp/pack.blend",
        source_mode="hybrid",
    )
    old = get_active_pack()
    set_active_pack(
        name="RenamedPack",
        category=old['category'],
        filepath=old.get('filepath'),
        physical_size=old['physical_size'],
        resolution_multiplier=old['resolution_multiplier'],
        blend_filepath=old.get('blend_filepath'),
        source_mode=old.get('source_mode', 'json_only'),
    )
    renamed = get_active_pack()
    check("name updated",                renamed['name'] == "RenamedPack")
    check("blend_filepath preserved",    renamed['blend_filepath'] == '/tmp/pack.blend')
    check("source_mode preserved",       renamed['source_mode'] == 'hybrid')

    clear_active_pack()


# ── companion JSON produced by hybrid export ──────────────────────────────────

def test_hybrid_export_manifest():
    """Verify the JSON manifest written alongside a .blend export.

    Simulates what _save_as_blend_file produces:  an empty-primitives JSON
    with blend_source, blend_collection, connectors, and metadata.
    """
    print("\nhybrid export — companion JSON manifest:")
    persistence = PrimitivePersistence()

    connectors = [
        {"name": "WALL", "description": "Wall face", "compatible_with": ["WALL"],
         "grid_category": "building", "is_symmetric": True},
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        blend_path  = os.path.join(tmpdir, 'my_pack.blend')
        json_path   = os.path.join(tmpdir, 'my_pack.json')
        blend_col   = slugify_collection_name("My Pack")

        ok, errs = persistence.save_primitive_library(
            primitives=[],
            filepath=json_path,
            library_name="My Pack",
            connectors=connectors,
            blend_source=os.path.basename(blend_path),
            blend_collection=blend_col,
            metadata={
                'grid_category': 'building',
                'physical_size': '2.0',
                'resolution_multiplier': '4',
                'author': 'WFC Addon',
                'version': '1.0',
            },
        )
        check("manifest saved without errors", ok and errs == [])

        with open(json_path) as f:
            data = json.load(f)
        meta = data.get('library_metadata', {})

        check("blend_source == filename",     meta.get('blend_source') == 'my_pack.blend')
        check("blend_collection == slug",     meta.get('blend_collection') == blend_col)
        check("grid_category in metadata",    meta.get('grid_category') == 'building')
        check("connectors list present",      len(data.get('connectors', [])) == 1)
        check("connector name round-trips",   data['connectors'][0]['name'] == 'WALL')
        check("primitives list is empty",     data.get('primitives', []) == [])

        # Reload and verify the round-trip
        prims, loaded_meta, load_errs = persistence.load_primitive_library(json_path)
        check("blend_source loads back",       loaded_meta.get('blend_source') == 'my_pack.blend')
        check("blend_collection loads back",   loaded_meta.get('blend_collection') == blend_col)
        check("connectors load back",          len(loaded_meta.get('connectors', [])) == 1)
        # An empty-primitives hybrid pack should NOT produce a fatal error
        check("no fatal error on reload",
              not any(e == "No primitives found in library file" for e in load_errs))


def test_blend_collection_stability():
    """The export collection name is preserved on re-export.

    When a pack already has a companion JSON with blend_collection set,
    re-exporting must reuse that name — not generate a new slug — so that
    any user who loaded the original blend can reload the re-exported one
    without changing the manifest.
    """
    print("\nblend_collection stability on re-export:")
    persistence = PrimitivePersistence()

    with tempfile.TemporaryDirectory() as tmpdir:
        json_path  = os.path.join(tmpdir, 'pack.json')
        blend_name = 'pack.blend'
        original_col = "Original_Custom_Collection_Primitives"

        # First export with a custom collection name
        persistence.save_primitive_library(
            primitives=[],
            filepath=json_path,
            library_name="Renamed Pack",
            blend_source=blend_name,
            blend_collection=original_col,
        )

        # Simulate what the save operator does: load the existing manifest
        # to recover blend_collection before re-exporting.
        _, meta, _ = persistence.load_primitive_library(json_path)
        recovered_col = meta.get('blend_collection')

        check("original collection name recovered from manifest",
              recovered_col == original_col)
        check("recovered name differs from new slug (rename scenario)",
              recovered_col != slugify_collection_name("Renamed Pack"))

        # Re-export with the recovered name
        ok, _ = persistence.save_primitive_library(
            primitives=[],
            filepath=json_path,
            library_name="Renamed Pack",
            blend_source=blend_name,
            blend_collection=recovered_col,
        )
        with open(json_path) as f:
            data2 = json.load(f)
        check("re-export preserves original blend_collection",
              data2['library_metadata']['blend_collection'] == original_col)


def test_missing_companion_json():
    """find_companion_json returns None when the JSON does not exist."""
    print("\nmissing companion JSON:")
    with tempfile.TemporaryDirectory() as tmpdir:
        blend_path = os.path.join(tmpdir, 'lonely.blend')
        open(blend_path, 'w').close()
        check("returns None for solo blend",  find_companion_json(blend_path) is None)


def test_companion_json_discovery():
    """find_companion_json resolves the correct path regardless of extension."""
    print("\ncompanion JSON discovery:")
    with tempfile.TemporaryDirectory() as tmpdir:
        blend_path = os.path.join(tmpdir, 'building_pack.blend')
        json_path  = os.path.join(tmpdir, 'building_pack.json')
        open(blend_path, 'w').close()
        open(json_path,  'w').close()

        result = find_companion_json(blend_path)
        check("companion discovered",        result is not None)
        check("correct JSON path",           result == json_path)
        check("stem matches blend stem",
              os.path.splitext(result)[0] == os.path.splitext(blend_path)[0])


# ── runner ────────────────────────────────────────────────────────────────────

def _mock_image(name, packed=False):
    """Minimal stand-in for bpy.types.Image."""
    img = SimpleNamespace()
    img.name = name
    img.packed_file = object() if packed else None
    return img


def _mock_tex_image_node(image):
    """Stand-in for ShaderNodeTexImage."""
    node = SimpleNamespace()
    node.type = 'TEX_IMAGE'
    node.image = image
    return node


def _mock_rgb_node():
    """Stand-in for a non-image node."""
    node = SimpleNamespace()
    node.type = 'RGB'
    return node


def _mock_node_tree(*nodes):
    tree = SimpleNamespace()
    tree.nodes = list(nodes)
    return tree


def _mock_material(name, node_tree=None, use_nodes=True):
    mat = SimpleNamespace()
    mat.name = name
    mat.use_nodes = use_nodes
    mat.node_tree = node_tree
    return mat


# We import the helper directly from the addon module (no Blender needed since
# it only introspects duck-typed objects).
_ADDON_ROOT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'addons', 'blender-wfc',
)
sys.path.insert(0, _ADDON_ROOT)
# Stub out bpy so primitive_ui can be imported without Blender
import types as _types
_bpy_stub = _types.ModuleType('bpy')
_bpy_stub.types = _types.ModuleType('bpy.types')
_bpy_stub.props = _types.ModuleType('bpy.props')
sys.modules.setdefault('bpy', _bpy_stub)
# Import only the helper function — not the whole module (which would fail on
# full registration without a running Blender).
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location(
    'primitive_ui_partial',
    os.path.join(_ADDON_ROOT, 'primitive_ui.py'),
)
# We can't execute the module (bpy.types not fully stubbed), so we parse it
# manually by extracting the function via exec on just its source.
def _load_gather_images_helper():
    """Extract _gather_images_from_materials from primitive_ui.py without
    executing the full module (which requires bpy)."""
    src_path = os.path.join(_ADDON_ROOT, 'primitive_ui.py')
    with open(src_path) as f:
        src = f.read()
    # Find the function definition and extract it
    start = src.index('def _gather_images_from_materials(')
    # Find the next top-level def/class after it
    rest = src[start:]
    lines = rest.splitlines()
    end_line = len(lines)
    for i, line in enumerate(lines[1:], 1):
        if line and not line[0].isspace() and (
            line.startswith('def ') or line.startswith('class ')
            or line.startswith('#')
        ):
            end_line = i
            break
    fn_src = '\n'.join(lines[:end_line])
    ns = {}
    exec(fn_src, ns)
    return ns['_gather_images_from_materials']


_gather_images_from_materials = _load_gather_images_helper()


def test_gather_images():
    print("\n_gather_images_from_materials:")
    img_a = _mock_image('brick.png')
    img_b = _mock_image('concrete.png')

    # Case 1: None in material list
    result = _gather_images_from_materials([None])
    check("None material → empty list",      result == [])

    # Case 2: material with use_nodes=False
    mat_no_nodes = _mock_material('mat_no_nodes', use_nodes=False)
    result = _gather_images_from_materials([mat_no_nodes])
    check("use_nodes=False → empty list",    result == [])

    # Case 3: material with node_tree=None
    mat_no_tree = _mock_material('mat_no_tree', node_tree=None)
    result = _gather_images_from_materials([mat_no_tree])
    check("node_tree=None → empty list",     result == [])

    # Case 4: node tree with no image nodes
    tree_no_img = _mock_node_tree(_mock_rgb_node())
    mat_no_img  = _mock_material('mat_no_img', node_tree=tree_no_img)
    result = _gather_images_from_materials([mat_no_img])
    check("no TEX_IMAGE nodes → empty list", result == [])

    # Case 5: image node with image=None
    tree_null_img = _mock_node_tree(_mock_tex_image_node(None))
    mat_null_img  = _mock_material('mat_null', node_tree=tree_null_img)
    result = _gather_images_from_materials([mat_null_img])
    check("image=None on node → empty list", result == [])

    # Case 6: one material, one image
    tree_one = _mock_node_tree(_mock_tex_image_node(img_a))
    mat_one  = _mock_material('mat_one', node_tree=tree_one)
    result   = _gather_images_from_materials([mat_one])
    check("one image returned",              len(result) == 1)
    check("correct image name",             result[0].name == 'brick.png')

    # Case 7: two materials sharing the same image → deduplicated
    tree_b = _mock_node_tree(_mock_tex_image_node(img_a))
    mat_b  = _mock_material('mat_b', node_tree=tree_b)
    result = _gather_images_from_materials([mat_one, mat_b])
    check("shared image deduplicated",       len(result) == 1)

    # Case 8: two materials with different images
    tree_c = _mock_node_tree(_mock_tex_image_node(img_b))
    mat_c  = _mock_material('mat_c', node_tree=tree_c)
    result = _gather_images_from_materials([mat_one, mat_c])
    check("two distinct images returned",    len(result) == 2)
    names  = {r.name for r in result}
    check("both image names present",        names == {'brick.png', 'concrete.png'})

    # Case 9: empty list of materials
    result = _gather_images_from_materials([])
    check("empty input → empty list",        result == [])


def run_all():
    test_slugify()
    test_resolve_blend_path()
    test_find_companion_json()
    test_hybrid_persistence()
    test_pack_state_hybrid()
    test_hybrid_export_manifest()
    test_blend_collection_stability()
    test_missing_companion_json()
    test_companion_json_discovery()
    test_gather_images()

    print(f"\n{'=' * 57}")
    total = _passed + _failed
    if _failed == 0:
        print(f"ALL CHECKS PASSED — {_passed}/{total}")
    else:
        print(f"FAILURES: {_failed}/{total}")
    return _failed == 0


if __name__ == '__main__':
    success = run_all()
    sys.exit(0 if success else 1)
