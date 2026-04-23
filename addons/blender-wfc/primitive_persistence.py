"""
Primitive Persistence - JSON Save/Load System

This module provides persistence for WFC primitives using JSON files.
It handles both individual primitives and primitive libraries (collections).

Design Goals:
- Human-readable JSON format
- Version control friendly
- Validation on load
- Clear error messages
- Support for primitive libraries (packs)

See docs/features/PRIMITIVE_GENERATION_ANALYSIS.md for architecture details.
"""

import json
import os
import re
from pathlib import Path
from typing import Optional, List, Tuple, Dict

# Support both relative and absolute imports
try:
    from .primitive_data_core import PrimitiveData
except ImportError:
    from primitive_data_core import PrimitiveData


# ---------------------------------------------------------------------------
# Pack file-discovery helpers (Stage 7 — Task 4)
# ---------------------------------------------------------------------------

def slugify_collection_name(pack_name: str) -> str:
    """Convert a pack display name to a stable Blender collection name.

    Generated once on first hybrid export and stored in ``pack.json`` as
    ``blend_collection``.  Subsequent renames of the pack do not change it.

    Rules:
    - Non-word characters (except spaces and hyphens) are stripped.
    - Spaces and hyphens are collapsed to underscores.
    - The suffix ``_Primitives`` is appended.
    - An empty or entirely-punctuation name falls back to ``WFC_Primitives``.

    Examples::

        slugify_collection_name("My Building Pack") -> "My_Building_Pack_Primitives"
        slugify_collection_name("building!!")       -> "building_Primitives"
        slugify_collection_name("")                 -> "WFC_Primitives"
    """
    slug = re.sub(r'[^\w\s-]', '', pack_name)
    slug = re.sub(r'[\s-]+', '_', slug.strip())
    return f"{slug}_Primitives" if slug else "WFC_Primitives"


def resolve_blend_path(json_filepath: str, blend_source: str) -> str:
    """Resolve *blend_source* (a filename or relative path) relative to *json_filepath*.

    Keeps pack folders portable: moving the folder preserves the relationship
    between the two files.

    Example::

        resolve_blend_path('/packs/building/pack.json', 'pack.blend')
        # -> '/packs/building/pack.blend'
    """
    return str(Path(json_filepath).parent / blend_source)


def find_companion_json(blend_filepath: str) -> Optional[str]:
    """Look for a companion ``*.json`` manifest next to a ``*.blend`` file.

    Checks for a file with the same stem and a ``.json`` extension in the
    same directory.  Returns the absolute path string if found, else ``None``.

    Example::

        find_companion_json('/packs/building/pack.blend')
        # -> '/packs/building/pack.json'   (if it exists)
        # -> None                          (if it does not)
    """
    candidate = Path(blend_filepath).with_suffix('.json')
    return str(candidate) if candidate.exists() else None


# ---------------------------------------------------------------------------
# Default library file name for each grid category.
# Used by load_primitives_by_category() to find the right file automatically.
CATEGORY_LIBRARY_FILES: Dict[str, str] = {
    'outer_grid':  'outer_grid_library.json',
    'building':    'building_library.json',
    'park':        'park_library.json',
    'road_detail': 'road_detail_library.json',
}


class PrimitivePersistence:
    """
    Handles saving and loading primitives to/from JSON files

    Supports both individual primitives and primitive libraries (collections
    of multiple primitives in a single file).
    """

    def __init__(self, default_library_path: Optional[str] = None):
        """
        Initialize the persistence manager
        
        Args:
            default_library_path: Path to default primitive library file
        """
        self.default_library_path = default_library_path
        self.format_version = "1.0"
    
    def save_primitive_to_file(
        self, 
        primitive_data: PrimitiveData, 
        filepath: str,
        pretty: bool = True
    ) -> Tuple[bool, List[str]]:
        """
        Save a single primitive to a JSON file
        
        Args:
            primitive_data: PrimitiveData to save
            filepath: Path to save file
            pretty: If True, format JSON with indentation (default: True)
            
        Returns:
            (success, errors): Tuple of success boolean and error list
        """
        errors = []
        
        try:
            # Validate primitive data first
            is_valid, validation_errors = primitive_data.validate()
            if not is_valid:
                errors.extend(validation_errors)
                return False, errors
            
            # Convert to dictionary
            data_dict = primitive_data.to_dict()
            
            # Wrap in format metadata
            output = {
                'format_version': self.format_version,
                'primitive': data_dict
            }
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
            
            # Write to file
            with open(filepath, 'w') as f:
                if pretty:
                    json.dump(output, f, indent=2, sort_keys=False)
                else:
                    json.dump(output, f)
            
            return True, errors
            
        except IOError as e:
            errors.append(f"File I/O error: {str(e)}")
            return False, errors
        except Exception as e:
            errors.append(f"Unexpected error saving primitive: {str(e)}")
            return False, errors
    
    def load_primitive_from_file(self, filepath: str) -> Tuple[Optional[PrimitiveData], List[str]]:
        """
        Load a single primitive from a JSON file
        
        Args:
            filepath: Path to JSON file
            
        Returns:
            (primitive_data, errors): Tuple of PrimitiveData (or None) and error list
        """
        errors = []
        
        try:
            # Check file exists
            if not os.path.exists(filepath):
                errors.append(f"File not found: {filepath}")
                return None, errors
            
            # Read file
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Check format version
            if 'format_version' in data:
                version = data['format_version']
                if version != self.format_version:
                    errors.append(f"Format version mismatch: file has {version}, expected {self.format_version}")
                    # Continue anyway - might still work
            
            # Extract primitive data
            if 'primitive' in data:
                primitive_dict = data['primitive']
            else:
                # Legacy format - assume entire file is primitive data
                primitive_dict = data
            
            # Create PrimitiveData from dictionary
            primitive_data = PrimitiveData.from_dict(primitive_dict)
            
            # Validate loaded data
            is_valid, validation_errors = primitive_data.validate()
            if not is_valid:
                errors.extend(validation_errors)
                return None, errors
            
            return primitive_data, errors
            
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON in file {filepath}: {str(e)}")
            return None, errors
        except IOError as e:
            errors.append(f"File I/O error: {str(e)}")
            return None, errors
        except KeyError as e:
            errors.append(f"Missing required key in JSON: {str(e)}")
            return None, errors
        except Exception as e:
            errors.append(f"Unexpected error loading primitive: {str(e)}")
            return None, errors

    def save_primitive_library(
        self,
        primitives: List[PrimitiveData],
        filepath: str,
        library_name: str = "Primitive Library",
        description: str = "",
        metadata: Optional[Dict[str, str]] = None,
        connectors: Optional[List[dict]] = None,
        blend_source: Optional[str] = None,
        blend_collection: Optional[str] = None,
        pretty: bool = True
    ) -> Tuple[bool, List[str]]:
        """Save multiple primitives to a single library (pack) JSON file.

        Args:
            primitives:        List of PrimitiveData instances.  May be empty
                               for a hybrid pack where geometry lives in a
                               companion ``.blend`` file.
            filepath:          Path to write the JSON file.
            library_name:      Human-readable pack name.
            description:       Pack description string.
            metadata:          Extra key/value pairs merged into
                               ``library_metadata`` (author, version, etc.).
            connectors:        Optional list of connector definition dicts from
                               ``ConnectorDefinition.to_dict()``.  Embedded
                               under ``"connectors"`` so the pack is
                               self-contained and can restore its session
                               registry on load.
            blend_source:      Relative path to a companion ``.blend`` file
                               (e.g. ``"pack.blend"``).  When set, the loader
                               treats the blend as the authoritative geometry
                               source and writes ``blend_source`` into
                               ``library_metadata``.
            blend_collection:  Stable Blender collection name inside the blend
                               (e.g. ``"Building_Pack_Primitives"``).  Use
                               :func:`slugify_collection_name` to generate this
                               on first export.  Written into
                               ``library_metadata`` alongside *blend_source*.
            pretty:            If ``True``, write indented JSON (default).

        Returns:
            ``(success, errors)``
        """
        errors = []

        try:
            # Validate all primitives first
            all_valid = True
            for i, primitive in enumerate(primitives):
                is_valid, validation_errors = primitive.validate()
                if not is_valid:
                    errors.append(f"Primitive {i} ({primitive.name}) validation failed:")
                    errors.extend([f"  - {err}" for err in validation_errors])
                    all_valid = False

            if not all_valid:
                return False, errors

            # Convert all primitives to dictionaries
            primitive_dicts = [p.to_dict() for p in primitives]

            # Create library structure
            library_metadata = metadata or {}
            library_metadata['library_name'] = library_name
            library_metadata['description'] = description
            library_metadata['primitive_count'] = len(primitives)

            # Hybrid pack fields — written when a companion .blend file exists.
            # blend_source is a filename/relative path; blend_collection is the
            # stable collection name inside the .blend to append on load.
            if blend_source is not None:
                library_metadata['blend_source'] = blend_source
            if blend_collection is not None:
                library_metadata['blend_collection'] = blend_collection

            output = {
                'format_version': self.format_version,
                'library_metadata': library_metadata,
                'primitives': primitive_dicts,
            }
            # Embed connector definitions when provided so the pack is
            # self-contained and can restore its own session registry on load.
            if connectors:
                output['connectors'] = connectors

            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)

            # Write to file
            with open(filepath, 'w') as f:
                if pretty:
                    json.dump(output, f, indent=2, sort_keys=False)
                else:
                    json.dump(output, f)

            return True, errors

        except IOError as e:
            errors.append(f"File I/O error: {str(e)}")
            return False, errors
        except Exception as e:
            errors.append(f"Unexpected error saving library: {str(e)}")
            return False, errors

    def load_primitive_library(self, filepath: str) -> Tuple[List[PrimitiveData], Dict[str, str], List[str]]:
        """
        Load multiple primitives from a library file

        Args:
            filepath: Path to library JSON file

        Returns:
            (primitives, metadata, errors): Tuple of primitive list, metadata dict, and error list
        """
        errors = []
        primitives = []
        metadata = {}

        try:
            # Check file exists
            if not os.path.exists(filepath):
                errors.append(f"File not found: {filepath}")
                return primitives, metadata, errors

            # Read file
            with open(filepath, 'r') as f:
                data = json.load(f)

            # Check format version
            if 'format_version' in data:
                version = data['format_version']
                if version != self.format_version:
                    errors.append(f"Format version mismatch: file has {version}, expected {self.format_version}")

            # Extract metadata
            metadata = data.get('library_metadata', {})

            # Surface the pack-embedded connector definitions (if any) through
            # the metadata dict so callers can activate a session registry
            # without needing to re-read the file.  The key is 'connectors'
            # to match the JSON structure directly.
            if 'connectors' in data:
                metadata['connectors'] = data['connectors']

            # Extract primitives
            primitive_dicts = data.get('primitives', [])

            if not primitive_dicts:
                # A hybrid pack (blend_source present) intentionally stores no
                # vertex geometry in the JSON — the .blend file is the source.
                # Return the populated metadata so the caller can proceed with
                # blend loading.  A JSON-only pack with no primitives is an
                # error and should be reported.
                if not metadata.get('blend_source'):
                    errors.append("No primitives found in library file")
                return primitives, metadata, errors

            # Create PrimitiveData instances
            for i, primitive_dict in enumerate(primitive_dicts):
                try:
                    primitive_data = PrimitiveData.from_dict(primitive_dict)

                    # Validate
                    is_valid, validation_errors = primitive_data.validate()
                    if is_valid:
                        primitives.append(primitive_data)
                    else:
                        errors.append(f"Primitive {i} ({primitive_dict.get('name', 'unknown')}) validation failed:")
                        errors.extend([f"  - {err}" for err in validation_errors])
                except Exception as e:
                    errors.append(f"Error loading primitive {i}: {str(e)}")

            return primitives, metadata, errors

        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON in file {filepath}: {str(e)}")
            return primitives, metadata, errors
        except IOError as e:
            errors.append(f"File I/O error: {str(e)}")
            return primitives, metadata, errors
        except Exception as e:
            errors.append(f"Unexpected error loading library: {str(e)}")
            return primitives, metadata, errors

    def load_primitives_by_category(
        self,
        category: str,
        data_dir: str,
    ) -> Tuple[List[PrimitiveData], List[str]]:
        """
        Load all primitives for a given grid category from the default library file.

        Looks up the standard library filename for *category* via
        ``CATEGORY_LIBRARY_FILES``, resolves it relative to *data_dir*, then
        calls ``load_primitive_library()`` and filters the result to only
        include primitives whose ``grid_category`` matches *category*.

        Args:
            category:  Grid category string, e.g. ``'building'`` or
                       ``'outer_grid'``.  Must be a key in
                       ``CATEGORY_LIBRARY_FILES``.
            data_dir:  Absolute path to the directory that contains the
                       library JSON files (typically the addon's ``data/``
                       folder).

        Returns:
            ``(primitives, errors)``

            - *primitives*: List of ``PrimitiveData`` whose
              ``grid_category == category``.  Empty on failure.
            - *errors*: List of human-readable error / warning strings.

        Example::

            persistence = PrimitivePersistence()
            data_dir = os.path.join(os.path.dirname(__file__), 'data')
            prims, errs = persistence.load_primitives_by_category('building', data_dir)
        """
        errors: List[str] = []

        filename = CATEGORY_LIBRARY_FILES.get(category)
        if filename is None:
            errors.append(
                f"Unknown category '{category}'. "
                f"Known categories: {list(CATEGORY_LIBRARY_FILES.keys())}"
            )
            return [], errors

        filepath = os.path.join(data_dir, filename)
        if not os.path.exists(filepath):
            errors.append(
                f"Library file not found for category '{category}': {filepath}"
            )
            return [], errors

        all_primitives, _meta, load_errors = self.load_primitive_library(filepath)
        errors.extend(load_errors)

        # Secondary filter — the library *should* already be category-specific,
        # but this guards against mixed-category files in the future.
        filtered = [p for p in all_primitives if p.grid_category == category]

        if all_primitives and not filtered:
            errors.append(
                f"Library '{filename}' contained {len(all_primitives)} primitive(s) "
                f"but none matched category '{category}'."
            )

        return filtered, errors

    def list_primitives_in_library(self, filepath: str) -> Tuple[List[Dict[str, str]], List[str]]:
        """
        List primitives in a library file without fully loading them

        Args:
            filepath: Path to library JSON file

        Returns:
            (primitive_info, errors): List of dicts with name/type, and error list
        """
        errors = []
        primitive_info = []

        try:
            if not os.path.exists(filepath):
                errors.append(f"File not found: {filepath}")
                return primitive_info, errors

            with open(filepath, 'r') as f:
                data = json.load(f)

            primitive_dicts = data.get('primitives', [])

            for prim_dict in primitive_dicts:
                primitive_info.append({
                    'name': prim_dict.get('name', 'Unknown'),
                    'primitive_type': prim_dict.get('primitive_type', 'Unknown'),
                    'vertex_count': len(prim_dict.get('verts', [])),
                    'face_count': len(prim_dict.get('faces', []))
                })

            return primitive_info, errors

        except Exception as e:
            errors.append(f"Error listing primitives: {str(e)}")
            return primitive_info, errors

