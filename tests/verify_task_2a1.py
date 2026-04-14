"""Verify Task 2A.1: Make Connector Enums Dynamic"""

import sys
from pathlib import Path

print("Verifying Task 2A.1 changes...")
print()

addon = Path('addons/blender-wfc')
files = {
    'wfc_enums.py': (addon / 'wfc_enums.py').read_text(),
    '__init__.py': (addon / '__init__.py').read_text(),
    'primitive_ui.py': (addon / 'primitive_ui.py').read_text(),
}

all_passed = True

# --- wfc_enums.py ---
content = files['wfc_enums.py']
checks = [
    ('def get_connector_enum_items(self=None, context=None):' in content, 'Function defined with (self, context) signature'),
    ('connector_registry.connectors.values()' in content, 'Reads from registry'),
    ('return CONNECTORS' in content, 'Has fallback to CONNECTORS'),
]
print("wfc_enums.py:")
for ok, msg in checks:
    print(f"  {'✅' if ok else '❌'} {msg}")
    if not ok:
        all_passed = False

# --- __init__.py ---
content = files['__init__.py']
checks = [
    ('get_connector_enum_items' in content, 'Imports get_connector_enum_items'),
    ('CONNECTORS' not in content, 'No longer imports CONNECTORS directly'),
    ('connector_items = get_connector_enum_items()' in content, 'Builds list at registration time'),
    ('items=connector_items' in content, 'Passes static list to Object properties'),
]
print("\n__init__.py:")
for ok, msg in checks:
    print(f"  {'✅' if ok else '❌'} {msg}")
    if not ok:
        all_passed = False

# --- primitive_ui.py ---
content = files['primitive_ui.py']
checks = [
    ('get_connector_enum_items' in content, 'Imports get_connector_enum_items'),
    ('CONNECTORS' not in content, 'No longer imports CONNECTORS'),
    ('items=get_connector_enum_items' in content, 'Uses callback (no parentheses)'),
    ("default='ROAD'" not in content, 'No static default (incompatible with dynamic enums)'),
    ('items=CONNECTORS' not in content, 'No hardcoded items=CONNECTORS remaining'),
]
print("\nprimitive_ui.py:")
for ok, msg in checks:
    print(f"  {'✅' if ok else '❌'} {msg}")
    if not ok:
        all_passed = False

# --- Functional test of wfc_enums directly ---
print("\nFunctional test:")
sys.path.insert(0, str(addon))
try:
    import importlib
    import wfc_enums
    importlib.reload(wfc_enums)

    # Test with no args (registration-time call)
    items = wfc_enums.get_connector_enum_items()
    print(f"  get_connector_enum_items() returned {len(items)} items")
    ok = isinstance(items, list) and len(items) > 0
    print(f"  {'✅' if ok else '❌'} Returns a non-empty list")
    if not ok:
        all_passed = False

    # Each item should be a 3-tuple
    all_tuples = all(len(i) == 3 for i in items)
    print(f"  {'✅' if all_tuples else '❌'} All items are 3-tuples (id, name, desc)")
    if not all_tuples:
        all_passed = False

    print(f"  First 4 items: {[i[0] for i in items[:4]]}")

except Exception as e:
    print(f"  ❌ Error: {e}")
    all_passed = False

print()
if all_passed:
    print("=" * 60)
    print("✅ ALL CHECKS PASSED - Task 2A.1 complete!")
    print("=" * 60)
else:
    print("=" * 60)
    print("❌ SOME CHECKS FAILED")
    print("=" * 60)
    sys.exit(1)
