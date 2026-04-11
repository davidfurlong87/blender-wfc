"""Quick verification that Task 1A.2 tests work"""
import sys
from pathlib import Path

addon_path = Path('addons/blender-wfc')
sys.path.insert(0, str(addon_path))

from primitive_data_core import PrimitiveData

print("Verifying Task 1A.2 test additions...")
print()

# Test defaults
prim = PrimitiveData(
    name='Test',
    primitive_type='ROAD',
    verts=[(0,0,0), (1,0,0), (1,1,0)],
    faces=[(0,1,2)],
    mat_indices=[0],
    material_names=['Material'],
    pos_x_connector='ROAD',
    neg_x_connector='ROAD',
    pos_y_connector='ROAD',
    neg_y_connector='ROAD'
)
assert prim.physical_size == 8.0
assert prim.grid_category == 'outer_grid'
assert prim.resolution_multiplier == 1
print("✅ Default values correct")

# Test custom building primitive
prim2 = PrimitiveData(
    name='Building',
    primitive_type='BUILDING',
    verts=[(0,0,0), (1,0,0), (1,1,0)],
    faces=[(0,1,2)],
    mat_indices=[0],
    material_names=['Material'],
    pos_x_connector='WALL',
    neg_x_connector='DOOR',
    pos_y_connector='WALL',
    neg_y_connector='WALL',
    physical_size=2.0,
    grid_category='building',
    resolution_multiplier=4
)
is_valid, errors = prim2.validate()
assert is_valid
print("✅ Building primitive validates")

# Test serialization
data = prim2.to_dict()
assert data['physical_size'] == 2.0
print("✅ Serialization includes sizing")

# Test deserialization
prim3 = PrimitiveData.from_dict(data)
assert prim3.physical_size == 2.0
print("✅ Deserialization works")

# Test backward compatibility
old_data = {
    'name': 'Legacy',
    'primitive_type': 'ROAD',
    'verts': [[0,0,0], [1,0,0], [1,1,0]],
    'faces': [[0,1,2]],
    'mat_indices': [0],
    'material_names': ['Material'],
    'connectors': {'pos_x': 'ROAD', 'neg_x': 'ROAD', 'pos_y': 'ROAD', 'neg_y': 'ROAD'}
}
prim4 = PrimitiveData.from_dict(old_data)
assert prim4.physical_size == 8.0
print("✅ Backward compatibility works")

# Test validation errors
prim5 = PrimitiveData(
    name='Invalid',
    primitive_type='TEST',
    verts=[(0,0,0), (1,0,0), (1,1,0)],
    faces=[(0,1,2)],
    mat_indices=[0],
    material_names=['Material'],
    pos_x_connector='ROAD',
    neg_x_connector='ROAD',
    pos_y_connector='ROAD',
    neg_y_connector='ROAD',
    physical_size=-1.0
)
is_valid, errors = prim5.validate()
assert not is_valid
print("✅ Validation catches errors")

print()
print("="*60)
print("✅ All Task 1A.2 tests passed!")
print("="*60)
