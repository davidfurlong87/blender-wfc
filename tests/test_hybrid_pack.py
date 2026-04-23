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


# ── runner ────────────────────────────────────────────────────────────────────

def run_all():
    test_slugify()
    test_resolve_blend_path()
    test_find_companion_json()
    test_hybrid_persistence()
    test_pack_state_hybrid()

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
