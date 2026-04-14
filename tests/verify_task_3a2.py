"""
Verify Task 3A.2: Update Panel Display
Run with: python tests/verify_task_3a2.py
"""

import sys
from pathlib import Path

content = Path('addons/blender-wfc/primitive_ui.py').read_text()

all_passed = True

def check(label, condition):
    global all_passed
    status = "✅" if condition else "❌"
    print(f"  {status} {label}")
    if not condition:
        all_passed = False


# ── Section 3 added ──────────────────────────────────────────────────────────
print("Section 3: Grid Metadata added to panel:")
check("Section 3 label present",
      '"Grid Metadata:"' in content and "SNAP_GRID" in content)
check("grid_category displayed",
      'obj, "grid_category"' in content)
check("physical_size displayed",
      'obj, "physical_size"' in content)
check("resolution_multiplier displayed",
      'obj, "resolution_multiplier"' in content)
check("rotation_invariant displayed",
      'obj, "rotation_invariant"' in content)


# ── Read-only enforcement ────────────────────────────────────────────────────
print("\nRead-only enforcement:")
check("metadata column disabled (col.enabled = False)",
      "col.enabled = False" in content)
check("rotation_invariant row disabled (row.enabled = False)",
      "row.enabled = False" in content)


# ── Hints ────────────────────────────────────────────────────────────────────
print("\nHints:")
check("rotation_invariant hint shown when True",
      "1 module generated (not 4)" in content)


# ── Button label updated ────────────────────────────────────────────────────
print("\nButton labels updated:")
check("'Edit Connectors & Metadata' button present",
      "Edit Connectors & Metadata" in content)
check("'Assign Connectors & Metadata' button present",
      "Assign Connectors & Metadata" in content)
check("old 'Edit Connectors' standalone label gone",
      '"Edit Connectors"' not in content)


# ── Section gating ──────────────────────────────────────────────────────────
print("\nSection gating:")
# Metadata section should be gated on primitive_type being assigned
lines = content.splitlines()
metadata_label_line = next(
    (i for i, l in enumerate(lines) if 'Grid Metadata:' in l and 'SNAP_GRID' in l), None
)
if metadata_label_line:
    # Look back up to 10 lines for the gating condition
    context_lines = lines[max(0, metadata_label_line - 10): metadata_label_line]
    gate_present = any(
        "primitive_type" in l and "NONE" in l
        for l in context_lines
    )
    check("metadata section gated on primitive_type assigned", gate_present)
else:
    check("metadata section found in panel", False)


print()
if all_passed:
    print("=" * 60)
    print("✅ ALL CHECKS PASSED - Task 3A.2 complete!")
    print("=" * 60)
    print("\nPanel now shows 3 sections when a primitive type is assigned:")
    print("  Section 1: Primitive Type")
    print("  Section 2: Connectors (read-only) + Edit button")
    print("  Section 3: Grid Metadata (read-only) — NEW")
    print("    • Grid Category")
    print("    • Physical Size (m)  |  Resolution")
    print("    • Rotation Invariant checkbox")
    print("    • Hint when rotation_invariant = True")
else:
    print("=" * 60)
    print("❌ SOME CHECKS FAILED")
    print("=" * 60)
    sys.exit(1)
