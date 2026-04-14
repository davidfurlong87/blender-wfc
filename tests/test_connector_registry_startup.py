"""
Test Connector Registry Startup (Task 1B.3)

Tests that the connector registry loads correctly when the addon initializes.

Run in Blender: This script simulates addon startup and verifies the registry loads.
"""

import sys
from pathlib import Path

# Add addon path
addon_path = Path('addons/blender-wfc')
sys.path.insert(0, str(addon_path))

print("="*70)
print("Task 1B.3: Testing Connector Registry Startup")
print("="*70)

# ============================================================================
# Test 1: Import connector_registry module
# ============================================================================
print("\n--- Test 1: Import connector_registry module ---")

try:
    from connector_registry import connector_registry
    print(f"✅ Module imported successfully")
    print(f"   Registry has {len(connector_registry.connectors)} default connectors")
except Exception as e:
    print(f"❌ Failed to import: {e}")
    sys.exit(1)

# ============================================================================
# Test 2: Verify default connectors are loaded
# ============================================================================
print("\n--- Test 2: Verify default connectors are loaded ---")

expected_defaults = ["ROAD", "BUILDING", "PAVEMENTPOS", "PAVEMENTNEG"]
for conn_name in expected_defaults:
    if connector_registry.get(conn_name) is None:
        print(f"❌ Default connector '{conn_name}' not found")
        sys.exit(1)

print(f"✅ All default connectors present: {', '.join(expected_defaults)}")

# ============================================================================
# Test 3: Load from data/connectors.json
# ============================================================================
print("\n--- Test 3: Load from data/connectors.json ---")

connectors_file = addon_path / 'data' / 'connectors.json'

if not connectors_file.exists():
    print(f"❌ File not found: {connectors_file}")
    sys.exit(1)

print(f"✅ File exists: {connectors_file}")

# Clear registry and reload from file (simulate fresh load)
connector_registry.connectors.clear()
success = connector_registry.load_from_file(str(connectors_file))

if not success:
    print(f"❌ Failed to load from file")
    sys.exit(1)

print(f"✅ Loaded from file successfully")
print(f"   Total connectors: {len(connector_registry.connectors)}")

# ============================================================================
# Test 4: Verify all expected connectors are present
# ============================================================================
print("\n--- Test 4: Verify expected connectors ---")

expected_connectors = {
    "outer_grid": ["ROAD", "BUILDING", "PAVEMENTPOS", "PAVEMENTNEG"],
    "building": ["WALL", "DOOR", "WINDOW", "HALLWAY", "EMPTY"],
    "park": ["GRASS", "PATH", "FOUNTAIN", "BENCH", "TREE"]
}

total_expected = sum(len(conns) for conns in expected_connectors.values())
total_found = len(connector_registry.connectors)

print(f"Expected at least {total_expected} connectors, found {total_found}")

for category, conn_names in expected_connectors.items():
    print(f"\n{category}:")
    category_connectors = connector_registry.get_all_for_category(category)
    for name in conn_names:
        conn = connector_registry.get(name)
        if conn:
            print(f"  ✅ {name} → {', '.join(conn.compatible_with)}")
        else:
            print(f"  ❌ {name} MISSING")
            sys.exit(1)

# ============================================================================
# Test 5: Verify matching works after load
# ============================================================================
print("\n--- Test 5: Verify matching works after load ---")

test_cases = [
    ("ROAD", "ROAD", True, "outer_grid"),
    ("ROAD", "BUILDING", False, "outer_grid"),
    ("PAVEMENTPOS", "PAVEMENTNEG", True, "outer_grid"),
    ("WALL", "DOOR", True, "building"),
    ("WALL", "WINDOW", True, "building"),
    ("WINDOW", "DOOR", False, "building"),
    ("GRASS", "PATH", True, "park"),
    ("TREE", "GRASS", True, "park"),
    ("TREE", "PATH", False, "park"),
]

all_passed = True
for conn_a, conn_b, expected, category in test_cases:
    result = connector_registry.matches(conn_a, conn_b)
    status = "✅" if result == expected else "❌"
    if result != expected:
        all_passed = False
    print(f"{status} {conn_a} + {conn_b} = {result} (expected {expected}) [{category}]")

if not all_passed:
    print("❌ Some matching tests failed")
    sys.exit(1)

print("✅ All matching tests passed")

# ============================================================================
# Test 6: Simulate _load_connector_registry() function
# ============================================================================
print("\n--- Test 6: Simulate _load_connector_registry() function ---")

def _load_connector_registry_test():
    """Simulates the function in __init__.py"""
    from pathlib import Path
    
    # Get path to connectors.json
    addon_dir = Path(__file__).parent.parent / 'addons' / 'blender-wfc'
    connectors_file = addon_dir / 'data' / 'connectors.json'
    
    print(f"[WFC] Loading connector registry from: {connectors_file}")
    
    if connectors_file.exists():
        try:
            # Clear and reload to simulate fresh startup
            connector_registry.connectors.clear()
            success = connector_registry.load_from_file(str(connectors_file))
            if success:
                connector_count = len(connector_registry.connectors)
                connector_names = ', '.join(list(connector_registry.connectors.keys())[:5])
                if connector_count > 5:
                    connector_names += f', ... ({connector_count - 5} more)'
                print(f"[WFC] ✅ Loaded {connector_count} connectors: {connector_names}")
                return True
            else:
                print(f"[WFC] ⚠️  Failed to load connectors")
                return False
        except Exception as e:
            print(f"[WFC] ❌ Error loading connector registry: {e}")
            return False
    else:
        print(f"[WFC] ⚠️  Connector file not found: {connectors_file}")
        return False

success = _load_connector_registry_test()

if success:
    print(f"✅ Startup simulation successful")
    print(f"   Registry now has {len(connector_registry.connectors)} connectors")
else:
    print(f"❌ Startup simulation failed")
    sys.exit(1)

# ============================================================================
# Summary
# ============================================================================
print("\n" + "="*70)
print("✅ ALL CONNECTOR REGISTRY STARTUP TESTS PASSED!")
print("="*70)
print("\nTask 1B.3 Complete:")
print("  ✅ connector_registry module imports correctly")
print("  ✅ Default connectors loaded on import")
print("  ✅ data/connectors.json exists and is valid")
print("  ✅ All expected connectors present (14 total)")
print("  ✅ Matching works correctly after loading")
print("  ✅ _load_connector_registry() simulation works")
print("\nReady for Blender testing:")
print("  1. Enable addon in Blender")
print("  2. Check console for connector loading messages")
print("  3. Verify no errors during startup")
print("\nNext: Task 1C.1 - Replace hardcoded sockets_match() function")
print("="*70)
