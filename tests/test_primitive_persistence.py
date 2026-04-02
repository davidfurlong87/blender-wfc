"""
Tests for primitive persistence (JSON save/load)

These tests verify that primitives can be saved to and loaded from JSON files
correctly, including validation and error handling.
"""

import pytest
import json
import os
import tempfile
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'addons' / 'blender-wfc'))

from primitive_data_core import PrimitiveData
from primitive_persistence import PrimitivePersistence


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_primitive():
    """Create a sample valid primitive for testing"""
    return PrimitiveData(
        name="TestPrimitive",
        primitive_type="BUILDING",
        verts=[[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0], [0.0, 1.0, 0.0]],
        faces=[[0, 1, 2, 3]],
        material_names=["TestMaterial"],
        mat_indices=[0],
        pos_x_connector="ROAD",
        neg_x_connector="ROAD",
        pos_y_connector="BUILDING",
        neg_y_connector="BUILDING",
        vertex_groups={},
        metadata={"created_by": "test"}
    )


@pytest.fixture
def persistence():
    """Create a PrimitivePersistence instance"""
    return PrimitivePersistence()


def test_save_single_primitive(persistence, sample_primitive, temp_dir):
    """Test saving a single primitive to a file"""
    filepath = os.path.join(temp_dir, "test_primitive.json")
    
    success, errors = persistence.save_primitive_to_file(sample_primitive, filepath)
    
    assert success, f"Save failed with errors: {errors}"
    assert os.path.exists(filepath), "File was not created"
    
    # Verify file contains valid JSON
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    assert 'format_version' in data
    assert 'primitive' in data
    assert data['primitive']['name'] == "TestPrimitive"


def test_load_single_primitive(persistence, sample_primitive, temp_dir):
    """Test loading a single primitive from a file"""
    filepath = os.path.join(temp_dir, "test_primitive.json")
    
    # Save first
    persistence.save_primitive_to_file(sample_primitive, filepath)
    
    # Load
    loaded_primitive, errors = persistence.load_primitive_from_file(filepath)
    
    assert loaded_primitive is not None, f"Load failed with errors: {errors}"
    assert loaded_primitive.name == sample_primitive.name
    assert loaded_primitive.primitive_type == sample_primitive.primitive_type
    assert len(loaded_primitive.verts) == len(sample_primitive.verts)
    assert len(loaded_primitive.faces) == len(sample_primitive.faces)


def test_round_trip_single_primitive(persistence, sample_primitive, temp_dir):
    """Test save -> load -> save cycle"""
    filepath1 = os.path.join(temp_dir, "primitive1.json")
    filepath2 = os.path.join(temp_dir, "primitive2.json")
    
    # Save original
    success1, _ = persistence.save_primitive_to_file(sample_primitive, filepath1)
    assert success1
    
    # Load
    loaded, _ = persistence.load_primitive_from_file(filepath1)
    assert loaded is not None
    
    # Save loaded version
    success2, _ = persistence.save_primitive_to_file(loaded, filepath2)
    assert success2
    
    # Compare JSON files (should be identical)
    with open(filepath1, 'r') as f1, open(filepath2, 'r') as f2:
        data1 = json.load(f1)
        data2 = json.load(f2)
        assert data1 == data2


def test_save_invalid_primitive(persistence, temp_dir):
    """Test that invalid primitives are rejected"""
    filepath = os.path.join(temp_dir, "invalid.json")
    
    # Create invalid primitive (vertex index out of range)
    invalid_primitive = PrimitiveData(
        name="Invalid",
        primitive_type="BUILDING",
        verts=[[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]],
        faces=[[0, 1, 5]],  # Index 5 doesn't exist!
        material_names=["Test"],
        mat_indices=[0],
        pos_x_connector="ROAD",
        neg_x_connector="ROAD",
        pos_y_connector="ROAD",
        neg_y_connector="ROAD"
    )
    
    success, errors = persistence.save_primitive_to_file(invalid_primitive, filepath)
    
    assert not success, "Should reject invalid primitive"
    assert len(errors) > 0, "Should return error messages"


def test_load_nonexistent_file(persistence):
    """Test loading from a file that doesn't exist"""
    loaded, errors = persistence.load_primitive_from_file("/nonexistent/file.json")
    
    assert loaded is None
    assert len(errors) > 0
    assert "not found" in errors[0].lower()


def test_save_primitive_library(persistence, sample_primitive, temp_dir):
    """Test saving multiple primitives to a library file"""
    filepath = os.path.join(temp_dir, "library.json")
    
    # Create multiple primitives
    primitive2 = PrimitiveData(
        name="Primitive2",
        primitive_type="ROAD",
        verts=[[0.0, 0.0, 0.0], [2.0, 0.0, 0.0], [2.0, 2.0, 0.0], [0.0, 2.0, 0.0]],
        faces=[[0, 1, 2, 3]],
        material_names=["RoadMaterial"],
        mat_indices=[0],
        pos_x_connector="ROAD",
        neg_x_connector="ROAD",
        pos_y_connector="ROAD",
        neg_y_connector="ROAD"
    )
    
    primitives = [sample_primitive, primitive2]
    
    success, errors = persistence.save_primitive_library(
        primitives,
        filepath,
        library_name="Test Library",
        description="Test library description"
    )
    
    assert success, f"Library save failed: {errors}"
    assert os.path.exists(filepath)
    
    # Verify structure
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    assert 'library_metadata' in data
    assert 'primitives' in data
    assert len(data['primitives']) == 2
    assert data['library_metadata']['library_name'] == "Test Library"


def test_load_primitive_library(persistence, sample_primitive, temp_dir):
    """Test loading multiple primitives from a library file"""
    filepath = os.path.join(temp_dir, "library.json")
    
    # Save library first
    primitives_to_save = [sample_primitive]
    persistence.save_primitive_library(primitives_to_save, filepath, library_name="Test")
    
    # Load library
    loaded_primitives, metadata, errors = persistence.load_primitive_library(filepath)
    
    assert len(loaded_primitives) == 1, f"Load failed: {errors}"
    assert metadata['library_name'] == "Test"
    assert loaded_primitives[0].name == sample_primitive.name


def test_list_primitives_in_library(persistence, sample_primitive, temp_dir):
    """Test listing primitives without fully loading them"""
    filepath = os.path.join(temp_dir, "library.json")
    
    persistence.save_primitive_library([sample_primitive], filepath)
    
    primitive_info, errors = persistence.list_primitives_in_library(filepath)
    
    assert len(primitive_info) == 1, f"List failed: {errors}"
    assert primitive_info[0]['name'] == "TestPrimitive"
    assert primitive_info[0]['primitive_type'] == "BUILDING"
    assert primitive_info[0]['vertex_count'] == 4
    assert primitive_info[0]['face_count'] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

