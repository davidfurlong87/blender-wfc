"""
Pack State — active-pack session management

Holds the single in-memory record of the pack the user is currently working
with.  No Blender dependency so it can be unit-tested independently.

A pack is a named, self-contained group of primitives sharing a grid category,
physical size, resolution multiplier, and a connector registry.  It maps
directly to the JSON library format used by PrimitivePersistence.

Design notes
------------
- The active pack is a plain dict so callers can read individual fields cheaply
  without needing to import a dataclass.
- ``filepath`` may be ``None`` for a newly created pack that has not been
  saved yet.
- The connector registry for the active pack is managed separately in
  ``connector_registry.py`` via ``set_session_registry`` / ``clear_session_registry``.
"""

from typing import Optional, Dict, Any

# ── Active pack state ─────────────────────────────────────────────────────────

_active_pack: Optional[Dict[str, Any]] = None


def get_active_pack() -> Optional[Dict[str, Any]]:
    """Return the active pack dict, or ``None`` if no pack is loaded.

    Keys present when a pack is active:
    - ``name``                 (str)   Human-readable pack name
    - ``category``             (str)   Grid category, e.g. ``'building'``
    - ``filepath``             (str|None)  Absolute path to the JSON file, or None
    - ``physical_size``        (float) Default cell size in metres
    - ``resolution_multiplier``(int)   Default resolution multiplier
    """
    return _active_pack


def has_active_pack() -> bool:
    """Return ``True`` if a pack is currently active."""
    return _active_pack is not None


def set_active_pack(
    name: str,
    category: str,
    filepath: Optional[str] = None,
    physical_size: float = 8.0,
    resolution_multiplier: int = 1,
) -> None:
    """Set (or replace) the active pack.

    Args:
        name:                   Human-readable display name for the pack.
        category:               Grid category string (``'building'``,
                                ``'outer_grid'``, etc.).
        filepath:               Absolute path to the backing JSON file, or
                                ``None`` for a pack that has not been saved yet.
        physical_size:          Default physical size in metres for new
                                primitives created inside this pack.
        resolution_multiplier:  Default resolution multiplier for new
                                primitives created inside this pack.
    """
    global _active_pack
    _active_pack = {
        'name': name,
        'category': category,
        'filepath': filepath,
        'physical_size': physical_size,
        'resolution_multiplier': resolution_multiplier,
    }


def update_active_pack_filepath(filepath: str) -> None:
    """Update only the filepath of the active pack (called after a Save).

    Does nothing if no pack is active.
    """
    if _active_pack is not None:
        _active_pack['filepath'] = filepath


def clear_active_pack() -> None:
    """Deactivate the current pack.

    Does not affect the connector session registry — call
    ``clear_session_registry()`` separately if desired.
    """
    global _active_pack
    _active_pack = None
