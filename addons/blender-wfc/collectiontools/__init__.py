# Collection tools package
from .collection_creation import (
    ensure_collection,
    get_or_create_collection,
    get_collection_by_name,
    check_collection_exists,
    link_object_to_single_collection,
    get_all_objects_from_collection,
    delete_objects_and_meshes,
    duplicate_and_move_and_return,
)

try:
    # Relative import used when loaded as part of the Blender addon package.
    from ..wfc_values import (
        CollectionNames,
        primitives_collection_for,
        modules_collection_for,
        grid_collection_for,
    )
except ImportError:
    # Absolute import used in standalone test contexts where the addon root
    # is on sys.path but there is no parent package.
    from wfc_values import (  # type: ignore[no-redef]
        CollectionNames,
        primitives_collection_for,
        modules_collection_for,
        grid_collection_for,
    )


def ensure_primitives_collection(category: str):
    """Ensure the full primitives parent chain exists and return the leaf.

    Creates (if missing) the three-level chain::

        WFC  →  WFC_Primitives  →  WFC_Primitives_{category}

    and returns the leaf collection.  Safe to call at any time — existing
    collections are never re-created or cleared.

    Args:
        category: A :class:`~wfc_values.GridCategory` string such as
            ``'outer_grid'`` or ``'building'``.

    Returns:
        The ``WFC_Primitives_{category}`` :class:`bpy.types.Collection`.
    """
    root   = ensure_collection(CollectionNames.Root.value)
    branch = ensure_collection(CollectionNames.Primitives.value, parent=root)
    return  ensure_collection(primitives_collection_for(category), parent=branch)


def ensure_modules_collection(category: str):
    """Ensure the full modules parent chain exists and return the leaf.

    Creates (if missing) the three-level chain::

        WFC  →  WFC_Modules  →  WFC_Modules_{category}

    and returns the leaf collection.  Safe to call at any time — existing
    collections are never re-created or cleared.

    Args:
        category: A :class:`~wfc_values.GridCategory` string such as
            ``'outer_grid'`` or ``'building'``.

    Returns:
        The ``WFC_Modules_{category}`` :class:`bpy.types.Collection`.
    """
    root   = ensure_collection(CollectionNames.Root.value)
    branch = ensure_collection(CollectionNames.Modules.value, parent=root)
    return  ensure_collection(modules_collection_for(category), parent=branch)


def ensure_grid_collection(category: str):
    """Ensure the full grid output parent chain exists and return the leaf.

    Creates (if missing) the three-level chain::

        WFC  →  WFC_Grid  →  WFC_Grid_{category}

    Works for any grid depth — outer grid, building inner grid, future
    inner-within-inner grids — all follow the same pattern with zero code
    changes needed for new depths.

    Args:
        category: A :class:`~wfc_values.GridCategory` string such as
            ``'outer_grid'``, ``'building'``, or ``'room_detail'``.

    Returns:
        The ``WFC_Grid_{category}`` :class:`bpy.types.Collection`.
    """
    root   = ensure_collection(CollectionNames.Root.value)
    branch = ensure_collection(CollectionNames.Grid.value, parent=root)
    return  ensure_collection(grid_collection_for(category), parent=branch)

