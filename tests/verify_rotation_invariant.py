"""
Verify Task 3A.1 Step 1: rotation_invariant field on PrimitiveData
Run with: python tests/verify_rotation_invariant.py
"""

import sys
from pathlib import Path

addon_path = Path('addons/blender-wfc')
sys.path.insert(0, str(addon_path))

from primitive_data_core import PrimitiveData

print("="*60)
print("Task 3A.1 Step 1: Verifying rotation_invariant field")
print("="*60)


def make(rotation_invariant=False, **kwargs):
    defaults = dict(
        name="Test", primitive_type="ROAD",
        verts=[(0,0,0),(1,0,0),(1,1,0)], faces=[(0,1,2)],
        mat_indices=[0], material_names=["Material"],
        pos_x_connector="ROAD", neg_x_connector="ROAD",
        pos_y_connector="ROAD", neg_y_connector="ROAD",
        rotation_invariant=rotation_invariant,
    )
    defaults.update(kwargs)
    return PrimitiveData(**defaults)


all_passed = True

def check(label, condition):
    global all_passed
    status = "✅" if condition else "❌"
    print(f"  {status} {label}")
    if not condition:
        all_passed = False


print("\n1: Default value")
prim = make()
check("rotation_invariant defaults to False", prim.rotation_invariant == False)

print("\n2: Explicit True")
prim = make(rotation_invariant=True)
check("rotation_invariant=True accepted", prim.rotation_invariant == True)

print("\n3: Validation — valid cases")
ok, errors = make(rotation_invariant=False).validate()
check("False passes validation", ok)
ok, errors = make(rotation_invariant=True).validate()
check("True passes validation", ok)

print("\n4: Validation — invalid type")
prim = make()
prim.rotation_invariant = "yes"  # type: ignore
ok, errors = prim.validate()
check("Non-bool fails validation", not ok)
check("Error message mentions rotation_invariant", any("rotation_invariant" in e for e in errors))

print("\n5: Serialization — to_dict()")
data = make(rotation_invariant=True).to_dict()
check("'rotation_invariant' key present in dict", 'rotation_invariant' in data)
check("Value is True in dict", data['rotation_invariant'] == True)

print("\n6: Serialization — from_dict()")
raw = {
    'name': 'T', 'primitive_type': 'ROAD',
    'verts': [[0,0,0],[1,0,0],[1,1,0]], 'faces': [[0,1,2]],
    'mat_indices': [0], 'material_names': ['M'],
    'connectors': {'pos_x':'ROAD','neg_x':'ROAD','pos_y':'ROAD','neg_y':'ROAD'},
    'rotation_invariant': True,
}
restored = PrimitiveData.from_dict(raw)
check("from_dict() restores rotation_invariant=True", restored.rotation_invariant == True)

print("\n7: Round-trip")
original = make(rotation_invariant=True)
restored = PrimitiveData.from_dict(original.to_dict())
check("Round-trip preserves rotation_invariant", restored.rotation_invariant == True)

print("\n8: Backward compatibility")
old = {
    'name': 'Legacy', 'primitive_type': 'ROAD',
    'verts': [[0,0,0],[1,0,0],[1,1,0]], 'faces': [[0,1,2]],
    'mat_indices': [0], 'material_names': ['M'],
    'connectors': {'pos_x':'ROAD','neg_x':'ROAD','pos_y':'ROAD','neg_y':'ROAD'},
    # No rotation_invariant key
}
prim = PrimitiveData.from_dict(old)
check("Old JSON without field loads with default False", prim.rotation_invariant == False)
ok, errors = prim.validate()
check("Old JSON primitive is still valid", ok)

print()
if all_passed:
    print("="*60)
    print("✅ ALL CHECKS PASSED")
    print("="*60)
    print("\nStep 1 complete. Ready for Step 2 (register Object properties).")
else:
    print("="*60)
    print("❌ SOME CHECKS FAILED")
    print("="*60)
    sys.exit(1)
