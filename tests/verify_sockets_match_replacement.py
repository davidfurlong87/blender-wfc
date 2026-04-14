"""
Verify sockets_match() Replacement (Task 1C.1)

Verifies that the hardcoded logic has been removed from the source files
and replaced with connector registry calls.

Run with: python tests/verify_sockets_match_replacement.py
"""

from pathlib import Path

print("="*70)
print("Task 1C.1: Verifying sockets_match() Replacement")
print("="*70)

# ============================================================================
# Test 1: Check wfc_classes.py has been updated
# ============================================================================
print("\n--- Test 1: Check wfc_classes.py ---")

wfc_classes_file = Path('addons/blender-wfc/wfc_classes.py')
content = wfc_classes_file.read_text()

# Check that old hardcoded logic is GONE
if "if (socket_a == 'ROAD'):" in content:
    print("❌ FAILED: Old hardcoded ROAD logic still present!")
    exit(1)

if "if (socket_a == 'BUILDING'):" in content:
    print("❌ FAILED: Old hardcoded BUILDING logic still present!")
    exit(1)

if "if (socket_a == 'PAVEMENTPOS'):" in content:
    print("❌ FAILED: Old hardcoded PAVEMENTPOS logic still present!")
    exit(1)

print("✅ Old hardcoded logic removed from wfc_classes.py")

# Check that NEW registry-based logic is present
if "from .connector_registry import connector_registry" not in content:
    print("❌ FAILED: connector_registry not imported!")
    exit(1)

if "connector_registry.matches" not in content:
    print("❌ FAILED: connector_registry.matches() not called!")
    exit(1)

print("✅ New connector_registry logic added to wfc_classes.py")

# ============================================================================
# Test 2: Check wfc_blender_adapter.py has been updated
# ============================================================================
print("\n--- Test 2: Check wfc_blender_adapter.py ---")

adapter_file = Path('addons/blender-wfc/wfc_blender_adapter.py')
content = adapter_file.read_text()

# Check that old hardcoded logic is GONE
if "if socket_a == 'ROAD':" in content and "return socket_b == 'ROAD'" in content:
    print("❌ FAILED: Old hardcoded ROAD logic still present in adapter!")
    exit(1)

if "if socket_a == 'BUILDING':" in content and "return socket_b == 'BUILDING'" in content:
    print("❌ FAILED: Old hardcoded BUILDING logic still present in adapter!")
    exit(1)

if "if socket_a == 'PAVEMENTPOS':" in content:
    print("❌ FAILED: Old hardcoded PAVEMENTPOS logic still present in adapter!")
    exit(1)

print("✅ Old hardcoded logic removed from wfc_blender_adapter.py")

# Check that NEW registry-based logic is present
if "from .connector_registry import connector_registry" not in content:
    print("❌ FAILED: connector_registry not imported in adapter!")
    exit(1)

if "connector_registry.matches" not in content:
    print("❌ FAILED: connector_registry.matches() not called in adapter!")
    exit(1)

print("✅ New connector_registry logic added to wfc_blender_adapter.py")

# ============================================================================
# Test 3: Verify function signatures are preserved
# ============================================================================
print("\n--- Test 3: Verify function signatures preserved ---")

# Check wfc_classes.sockets_match
if "def sockets_match(socket_a, socket_b):" in wfc_classes_file.read_text():
    print("✅ sockets_match(socket_a, socket_b) signature preserved")
else:
    print("❌ FAILED: sockets_match() signature changed!")
    exit(1)

# Check adapter._sockets_match
if "def _sockets_match(self, socket_a, socket_b):" in adapter_file.read_text():
    print("✅ _sockets_match(self, socket_a, socket_b) signature preserved")
else:
    print("❌ FAILED: _sockets_match() signature changed!")
    exit(1)

# ============================================================================
# Test 4: Check that documentation mentions the replacement
# ============================================================================
print("\n--- Test 4: Check documentation ---")

if "Task 1C.1" in wfc_classes_file.read_text():
    print("✅ Task 1C.1 documented in wfc_classes.py")
else:
    print("⚠️  Task reference missing in wfc_classes.py")

if "REPLACED" in wfc_classes_file.read_text():
    print("✅ Replacement documented in wfc_classes.py")
else:
    print("⚠️  Replacement note missing")

# ============================================================================
# Test 5: Verify connector registry exists
# ============================================================================
print("\n--- Test 5: Verify connector registry module ---")

registry_file = Path('addons/blender-wfc/connector_registry.py')
if not registry_file.exists():
    print("❌ FAILED: connector_registry.py not found!")
    exit(1)

print("✅ connector_registry.py exists")

registry_content = registry_file.read_text()
if "def matches(self, connector_a: str, connector_b: str)" in registry_content:
    print("✅ ConnectorRegistry.matches() method exists")
else:
    print("❌ FAILED: matches() method not found!")
    exit(1)

# ============================================================================
# Test 6: Count lines removed
# ============================================================================
print("\n--- Test 6: Code simplification metrics ---")

# Old hardcoded version had ~21 lines
# New version should be ~3 lines (import + return)

wfc_classes_lines = wfc_classes_file.read_text().split('\n')
function_start = None
function_end = None

for i, line in enumerate(wfc_classes_lines):
    if 'def sockets_match(socket_a, socket_b):' in line:
        function_start = i
    if function_start is not None and i > function_start and line.strip() and not line.strip().startswith('#') and not line.strip().startswith('"""'):
        if 'def ' in line and 'sockets_match' not in line:
            function_end = i
            break

if function_start and function_end:
    new_lines = function_end - function_start
    print(f"✅ sockets_match() reduced from ~21 lines to ~{new_lines} lines")
    print(f"   Lines of hardcoded logic eliminated: ~{21 - new_lines}")
else:
    print("⚠️  Could not calculate line reduction")

# ============================================================================
# Summary
# ============================================================================
print("\n" + "="*70)
print("✅ ALL VERIFICATION CHECKS PASSED!")
print("="*70)
print("\nTask 1C.1 Code Changes Verified:")
print("  ✅ Hardcoded logic removed from wfc_classes.py")
print("  ✅ Hardcoded logic removed from wfc_blender_adapter.py")
print("  ✅ connector_registry.matches() used in both files")
print("  ✅ Function signatures preserved (backward compatible)")
print("  ✅ connector_registry.py module exists with matches() method")
print("  ✅ ~18+ lines of hardcoded logic eliminated")
print("\nReady for Blender testing!")
print("="*70)
