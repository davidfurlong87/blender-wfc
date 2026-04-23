"""
Tests for pack_merge.py — pure-Python merge logic.

All tests run without Blender.
"""

import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, 'addons', 'blender-wfc'))

from pack_merge import merge_packs, MergeConflict

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


def _prim(name, ptype='BUILDING', px='WALL', nx='WALL', py='WALL', ny='WALL',
          category='building', size=2.0):
    return {
        'name': name,
        'primitive_type': ptype,
        'verts': [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)],
        'faces': [(0, 1, 2, 3)],
        'mat_indices': [0],
        'material_names': ['Mat'],
        'connectors': {'pos_x': px, 'neg_x': nx, 'pos_y': py, 'neg_y': ny},
        'physical_size': size,
        'grid_category': category,
        'resolution_multiplier': 1,
    }


def _conn(name, cw=None, symmetric=True, category='building'):
    return {
        'name': name,
        'description': '',
        'compatible_with': cw if cw is not None else [name],
        'grid_category': category,
        'is_symmetric': symmetric,
    }


# ── Primitive tests ───────────────────────────────────────────────────────────

def test_no_conflict_disjoint():
    print("\nPrimitives — no conflict (disjoint names):")
    a = [_prim('wall')]
    b = [_prim('corner')]
    prims, conns, conflicts = merge_packs(a, [], b, [])
    check("both primitives present",  len(prims) == 2)
    check("no conflicts",             conflicts == [])
    check("names correct",            {p['name'] for p in prims} == {'wall', 'corner'})


def test_identical_primitive_deduped():
    print("\nPrimitives — identical → silent dedup:")
    p = _prim('wall')
    prims, _, conflicts = merge_packs([p], [], [p], [])
    check("only one primitive",   len(prims) == 1)
    check("no conflicts",         conflicts == [])


def test_collision_keep_active():
    print("\nPrimitives — name collision KEEP_ACTIVE:")
    active   = [_prim('wall', px='WALL')]
    incoming = [_prim('wall', px='DOOR')]
    prims, _, conflicts = merge_packs(active, [], incoming, [], 'KEEP_ACTIVE')
    check("one primitive in result",        len(prims) == 1)
    check("active version kept",            prims[0]['connectors']['pos_x'] == 'WALL')
    check("one conflict recorded",          len(conflicts) == 1)
    check("resolution == kept_active",      conflicts[0].resolution == 'kept_active')
    check("kind == primitive",              conflicts[0].kind == 'primitive')


def test_collision_keep_incoming():
    print("\nPrimitives — name collision KEEP_INCOMING:")
    active   = [_prim('wall', px='WALL')]
    incoming = [_prim('wall', px='DOOR')]
    prims, _, conflicts = merge_packs(active, [], incoming, [], 'KEEP_INCOMING')
    check("one primitive in result",        len(prims) == 1)
    check("incoming version kept",          prims[0]['connectors']['pos_x'] == 'DOOR')
    check("resolution == kept_incoming",    conflicts[0].resolution == 'kept_incoming')


def test_collision_keep_both():
    print("\nPrimitives — name collision KEEP_BOTH:")
    active   = [_prim('wall', px='WALL')]
    incoming = [_prim('wall', px='DOOR')]
    prims, _, conflicts = merge_packs(active, [], incoming, [], 'KEEP_BOTH')
    names = {p['name'] for p in prims}
    check("two primitives in result",       len(prims) == 2)
    check("original name preserved",        'wall' in names)
    check("incoming renamed to wall_2",     'wall_2' in names)
    check("resolution == kept_both",        conflicts[0].resolution == 'kept_both')
    # Verify the active copy is unchanged
    active_copy = next(p for p in prims if p['name'] == 'wall')
    check("active connector unchanged",     active_copy['connectors']['pos_x'] == 'WALL')


def test_keep_both_chain():
    """KEEP_BOTH increments the suffix if _2 is already taken."""
    print("\nPrimitives — KEEP_BOTH suffix chaining:")
    a = [_prim('wall'), _prim('wall_2')]
    b = [_prim('wall', px='DOOR')]
    prims, _, conflicts = merge_packs(a, [], b, [], 'KEEP_BOTH')
    names = {p['name'] for p in prims}
    check("three primitives total",         len(prims) == 3)
    check("wall_3 created (not wall_2)",    'wall_3' in names)


# ── Connector tests ───────────────────────────────────────────────────────────

def test_connector_no_conflict():
    print("\nConnectors — no conflict (disjoint names):")
    a = [_conn('WALL')]
    b = [_conn('DOOR')]
    _, conns, conflicts = merge_packs([], a, [], b)
    check("both connectors present",   len(conns) == 2)
    check("no conflicts",              conflicts == [])


def test_connector_identical_deduped():
    print("\nConnectors — identical → silent dedup:")
    c = _conn('WALL')
    _, conns, conflicts = merge_packs([], [c], [], [c])
    check("one connector only",   len(conns) == 1)
    check("no conflicts",         conflicts == [])


def test_connector_compatible_with_merged():
    print("\nConnectors — compatible_with-only diff → auto-merged:")
    active   = [_conn('WALL', cw=['WALL'])]
    incoming = [_conn('WALL', cw=['WALL', 'OPEN_WALL'])]
    _, conns, conflicts = merge_packs([], active, [], incoming)
    check("one connector",                  len(conns) == 1)
    check("compatible_with is union",
          set(conns[0]['compatible_with']) == {'WALL', 'OPEN_WALL'})
    check("resolution == merged",           conflicts[0].resolution == 'merged')
    check("kind == connector",              conflicts[0].kind == 'connector')


def test_connector_true_conflict_keep_active():
    print("\nConnectors — true conflict KEEP_ACTIVE:")
    active   = [_conn('WALL', symmetric=True)]
    incoming = [_conn('WALL', symmetric=False)]
    _, conns, conflicts = merge_packs([], active, [], incoming, 'KEEP_ACTIVE')
    check("one connector",                  len(conns) == 1)
    check("active kept (symmetric=True)",   conns[0]['is_symmetric'] is True)
    check("resolution == kept_active",      conflicts[0].resolution == 'kept_active')


def test_connector_true_conflict_keep_incoming():
    print("\nConnectors — true conflict KEEP_INCOMING:")
    active   = [_conn('WALL', symmetric=True)]
    incoming = [_conn('WALL', symmetric=False)]
    _, conns, conflicts = merge_packs([], active, [], incoming, 'KEEP_INCOMING')
    check("one connector",                   len(conns) == 1)
    check("incoming kept (symmetric=False)", conns[0]['is_symmetric'] is False)
    check("resolution == kept_incoming",     conflicts[0].resolution == 'kept_incoming')


def test_connector_keep_both_falls_back_to_keep_active():
    """KEEP_BOTH cannot duplicate connectors (name is the key in primitives)."""
    print("\nConnectors — KEEP_BOTH falls back to KEEP_ACTIVE for true conflicts:")
    active   = [_conn('WALL', symmetric=True)]
    incoming = [_conn('WALL', symmetric=False)]
    _, conns, conflicts = merge_packs([], active, [], incoming, 'KEEP_BOTH')
    check("one connector only",             len(conns) == 1)
    check("active version kept",            conns[0]['is_symmetric'] is True)
    check("resolution == kept_active",      conflicts[0].resolution == 'kept_active')


# ── Mixed merge ───────────────────────────────────────────────────────────────

def test_full_merge_no_conflicts():
    print("\nFull merge — no conflicts:")
    ap = [_prim('wall')]
    ac = [_conn('WALL')]
    bp = [_prim('corner')]
    bc = [_conn('DOOR')]
    prims, conns, conflicts = merge_packs(ap, ac, bp, bc)
    check("2 primitives",    len(prims) == 2)
    check("2 connectors",    len(conns) == 2)
    check("no conflicts",    conflicts == [])


def test_full_merge_mixed_conflicts():
    print("\nFull merge — mixed conflicts:")
    ap = [_prim('wall', px='WALL')]
    ac = [_conn('WALL', cw=['WALL'])]
    bp = [_prim('wall', px='DOOR'), _prim('corner')]
    bc = [_conn('WALL', cw=['WALL', 'OPEN_WALL']), _conn('DOOR')]
    prims, conns, conflicts = merge_packs(ap, ac, bp, bc, 'KEEP_ACTIVE')
    check("2 primitives (collision kept active + new corner)",  len(prims) == 2)
    check("2 connectors (WALL auto-merged + DOOR added)",       len(conns) == 2)
    # 1 primitive conflict (kept_active) + 1 connector auto-merge
    check("2 conflicts recorded",   len(conflicts) == 2)
    prim_c = [c for c in conflicts if c.kind == 'primitive']
    conn_c = [c for c in conflicts if c.kind == 'connector']
    check("primitive conflict kept_active",   prim_c[0].resolution == 'kept_active')
    check("connector conflict merged",        conn_c[0].resolution == 'merged')


# ── runner ────────────────────────────────────────────────────────────────────

def run_all():
    test_no_conflict_disjoint()
    test_identical_primitive_deduped()
    test_collision_keep_active()
    test_collision_keep_incoming()
    test_collision_keep_both()
    test_keep_both_chain()
    test_connector_no_conflict()
    test_connector_identical_deduped()
    test_connector_compatible_with_merged()
    test_connector_true_conflict_keep_active()
    test_connector_true_conflict_keep_incoming()
    test_connector_keep_both_falls_back_to_keep_active()
    test_full_merge_no_conflicts()
    test_full_merge_mixed_conflicts()

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
