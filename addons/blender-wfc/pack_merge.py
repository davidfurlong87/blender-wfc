"""
Pack Merge — pure-Python merge logic (no Blender dependency)

Merges two packs — each represented as a list of primitive dicts and a list
of connector dicts — into a single combined result.

Conflict categories
-------------------
Primitives
    - **No conflict**: different names → both included.
    - **Identical**: same name AND same data → incoming silently dropped (dedup).
    - **Name collision**: same name, different data → resolved by policy.

Connectors
    - **No conflict**: different names → both included.
    - **Identical**: same name AND identical ``to_dict()`` → incoming silently dropped.
    - **Compatible**: same name, same ``is_symmetric`` and ``grid_category``, but
      ``compatible_with`` lists differ → auto-merged (union of both lists).
    - **True conflict**: ``is_symmetric`` or ``grid_category`` differ → resolved by
      policy (KEEP_BOTH falls back to KEEP_ACTIVE for connectors, because two
      connectors cannot share a name).

Conflict policies
-----------------
``KEEP_ACTIVE``
    For any collision, keep the active pack's version and discard the incoming.
``KEEP_INCOMING``
    For any collision, replace the active version with the incoming one.
``KEEP_BOTH``
    For primitives: rename the incoming entry (append ``_2``, ``_3``, …) and
    include both.  For connectors: not possible — falls back to KEEP_ACTIVE.
"""

from __future__ import annotations
from typing import List, Tuple, NamedTuple


# ---------------------------------------------------------------------------
# Public result types
# ---------------------------------------------------------------------------

class MergeConflict(NamedTuple):
    """Record of a single conflict and how it was resolved."""
    kind:       str   # 'primitive' | 'connector'
    name:       str   # The conflicting name
    resolution: str   # 'kept_active' | 'kept_incoming' | 'kept_both' | 'merged'
    detail:     str   # Human-readable explanation


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _prim_key(p: dict) -> tuple:
    """Stable comparison key for a primitive dict (ignores metadata dict)."""
    return (
        p.get('primitive_type'),
        tuple(map(tuple, p.get('verts', []))),
        tuple(map(tuple, p.get('faces', []))),
        p.get('connectors', {}).get('pos_x'),
        p.get('connectors', {}).get('neg_x'),
        p.get('connectors', {}).get('pos_y'),
        p.get('connectors', {}).get('neg_y'),
        p.get('physical_size'),
        p.get('grid_category'),
        p.get('resolution_multiplier'),
    )


def _conn_key(c: dict) -> tuple:
    """Stable comparison key for a connector dict."""
    return (
        c.get('is_symmetric'),
        c.get('grid_category'),
        tuple(sorted(c.get('compatible_with', []))),
    )


def _unique_name(name: str, taken: set) -> str:
    """Return *name* suffixed with _2, _3, … until it is not in *taken*."""
    candidate = f"{name}_2"
    n = 3
    while candidate in taken:
        candidate = f"{name}_{n}"
        n += 1
    return candidate


# ---------------------------------------------------------------------------
# Main public function
# ---------------------------------------------------------------------------

def merge_packs(
    active_primitives:   List[dict],
    active_connectors:   List[dict],
    incoming_primitives: List[dict],
    incoming_connectors: List[dict],
    conflict_policy:     str = 'KEEP_ACTIVE',
) -> Tuple[List[dict], List[dict], List[MergeConflict]]:
    """Merge two packs and return the combined result.

    Args:
        active_primitives:   Primitive dicts from the currently active pack.
        active_connectors:   Connector dicts from the currently active pack.
        incoming_primitives: Primitive dicts from the pack being merged in.
        incoming_connectors: Connector dicts from the pack being merged in.
        conflict_policy:     One of ``'KEEP_ACTIVE'``, ``'KEEP_INCOMING'``,
                             or ``'KEEP_BOTH'``.

    Returns:
        ``(merged_primitives, merged_connectors, conflicts)`` where *conflicts*
        is a list of :class:`MergeConflict` records (may be empty).
    """
    merged_prims, conflicts = _merge_primitives(
        active_primitives, incoming_primitives, conflict_policy
    )
    merged_conns, conn_conflicts = _merge_connectors(
        active_connectors, incoming_connectors, conflict_policy
    )
    return merged_prims, merged_conns, conflicts + conn_conflicts


# ---------------------------------------------------------------------------
# Primitive merge
# ---------------------------------------------------------------------------

def _merge_primitives(
    active:   List[dict],
    incoming: List[dict],
    policy:   str,
) -> Tuple[List[dict], List[MergeConflict]]:
    """Return merged primitive list and any conflicts encountered."""
    result:    List[dict]          = list(active)
    conflicts: List[MergeConflict] = []
    taken = {p['name'] for p in active}

    active_by_name = {p['name']: p for p in active}

    for prim in incoming:
        name = prim['name']

        if name not in active_by_name:
            # No conflict — add directly.
            result.append(prim)
            taken.add(name)
            continue

        if _prim_key(prim) == _prim_key(active_by_name[name]):
            # Identical — silent dedup.
            continue

        # Name collision with different data.
        if policy == 'KEEP_INCOMING':
            idx = next(i for i, p in enumerate(result) if p['name'] == name)
            result[idx] = prim
            conflicts.append(MergeConflict(
                kind='primitive', name=name, resolution='kept_incoming',
                detail=f"Replaced active '{name}' with incoming version.",
            ))
        elif policy == 'KEEP_BOTH':
            new_name = _unique_name(name, taken)
            renamed  = dict(prim, name=new_name)
            result.append(renamed)
            taken.add(new_name)
            conflicts.append(MergeConflict(
                kind='primitive', name=name, resolution='kept_both',
                detail=f"Kept active '{name}'; incoming renamed to '{new_name}'.",
            ))
        else:  # KEEP_ACTIVE (default)
            conflicts.append(MergeConflict(
                kind='primitive', name=name, resolution='kept_active',
                detail=f"Kept active '{name}'; incoming version discarded.",
            ))

    return result, conflicts


# ---------------------------------------------------------------------------
# Connector merge
# ---------------------------------------------------------------------------

def _merge_connectors(
    active:   List[dict],
    incoming: List[dict],
    policy:   str,
) -> Tuple[List[dict], List[MergeConflict]]:
    """Return merged connector list and any conflicts encountered."""
    result:    List[dict]          = list(active)
    conflicts: List[MergeConflict] = []

    active_by_name: dict[str, dict] = {c['name']: c for c in active}

    for conn in incoming:
        name = conn['name']

        if name not in active_by_name:
            # No conflict — add directly.
            result.append(conn)
            active_by_name[name] = conn
            continue

        existing = active_by_name[name]

        if _conn_key(conn) == _conn_key(existing):
            # Fully identical — silent dedup.
            continue

        # Check for the "compatible" case: only compatible_with differs.
        if (conn.get('is_symmetric') == existing.get('is_symmetric')
                and conn.get('grid_category') == existing.get('grid_category')):
            # Auto-merge: take the union of compatible_with lists.
            merged_cw = sorted(set(
                existing.get('compatible_with', []) +
                conn.get('compatible_with', [])
            ))
            idx = next(i for i, c in enumerate(result) if c['name'] == name)
            result[idx] = dict(existing, compatible_with=merged_cw)
            active_by_name[name] = result[idx]
            conflicts.append(MergeConflict(
                kind='connector', name=name, resolution='merged',
                detail=(
                    f"'{name}' compatible_with lists merged → {merged_cw}."
                ),
            ))
            continue

        # True conflict: is_symmetric or grid_category differ.
        # KEEP_BOTH is not meaningful for connectors (name is the key in
        # primitive fields), so it falls back to KEEP_ACTIVE.
        if policy == 'KEEP_INCOMING':
            idx = next(i for i, c in enumerate(result) if c['name'] == name)
            result[idx] = conn
            active_by_name[name] = conn
            conflicts.append(MergeConflict(
                kind='connector', name=name, resolution='kept_incoming',
                detail=f"Replaced active connector '{name}' with incoming version.",
            ))
        else:  # KEEP_ACTIVE or KEEP_BOTH
            conflicts.append(MergeConflict(
                kind='connector', name=name, resolution='kept_active',
                detail=f"Kept active connector '{name}'; incoming version discarded.",
            ))

    return result, conflicts
