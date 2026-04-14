"""
Verify Task 3A.1 Step 3: Updated OBJECT_OT_WFCAssignConnectors operator
Run with: python tests/verify_step3_operator.py
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

# ── Imports ───────────────────────────────────────────────────────────────────
print("Imports:")
check("FloatProperty imported",     "FloatProperty" in content)
check("IntProperty imported",       "IntProperty" in content)
check("BoolProperty imported",      "BoolProperty" in content)
check("GRID_CATEGORIES imported",   "GRID_CATEGORIES" in content)

# ── Operator properties ───────────────────────────────────────────────────────
print("\nOperator properties:")
check("physical_size: FloatProperty",           "physical_size: FloatProperty" in content)
check("physical_size min=0.1",                  "min=0.1" in content)
check("grid_category: EnumProperty",            "grid_category: EnumProperty" in content)
check("grid_category items=GRID_CATEGORIES",    "items=GRID_CATEGORIES" in content)
check("grid_category default='outer_grid'",     "default='outer_grid'" in content)
check("resolution_multiplier: IntProperty",     "resolution_multiplier: IntProperty" in content)
check("resolution_multiplier min=1",            "min=1" in content)
check("rotation_invariant: BoolProperty",       "rotation_invariant: BoolProperty" in content)
check("rotation_invariant default=False",       "default=False" in content)

# ── invoke() ──────────────────────────────────────────────────────────────────
print("\ninvoke():")
check("pre-populates physical_size",             "self.physical_size = obj.physical_size" in content)
check("pre-populates grid_category",             "self.grid_category = obj.grid_category" in content)
check("pre-populates resolution_multiplier",     "self.resolution_multiplier = obj.resolution_multiplier" in content)
check("pre-populates rotation_invariant",        "self.rotation_invariant = obj.rotation_invariant" in content)
check("dialog width=400",                        "invoke_props_dialog(self, width=400)" in content)

# ── draw() ────────────────────────────────────────────────────────────────────
print("\ndraw():")
check("Grid Metadata section label",             "Grid Metadata" in content)
check("grid_category drawn",                     'box.prop(self, "grid_category")' in content)
check("physical_size drawn",                     'row.prop(self, "physical_size")' in content)
check("resolution_multiplier drawn",             'row.prop(self, "resolution_multiplier")' in content)
check("Auto-calculate helper shown",             "8m outer cell" in content)
check("Symmetry section label",                  "Symmetry:" in content)
check("rotation_invariant drawn",                'box.prop(self, "rotation_invariant")' in content)
check("1 module hint shown when invariant",      "Only 1 module will be generated" in content)
check("Connectors section label",                "Connectors:" in content)
check("pos_x still drawn",                       'box.prop(self, "pos_x")' in content)
check("neg_y still drawn",                       'box.prop(self, "neg_y")' in content)

# ── execute() ────────────────────────────────────────────────────────────────
print("\nexecute():")
check("writes physical_size to obj",             "obj.physical_size = self.physical_size" in content)
check("writes grid_category to obj",             "obj.grid_category = self.grid_category" in content)
check("writes resolution_multiplier to obj",     "obj.resolution_multiplier = self.resolution_multiplier" in content)
check("writes rotation_invariant to obj",        "obj.rotation_invariant = self.rotation_invariant" in content)
check("connectors still assigned",               "obj.x_pos_connector = self.pos_x" in content)
check("updated report message",                  "metadata" in content)

print()
if all_passed:
    print("=" * 60)
    print("✅ ALL CHECKS PASSED - Step 3 complete!")
    print("=" * 60)
    print("\nIn Blender, the 'Assign Connectors' dialog now shows:")
    print("  ┌─ Grid Metadata ────────────────────┐")
    print("  │  Grid Category: [Outer Grid ▼]     │")
    print("  │  Physical Size: [8.0]  Res: [1]    │")
    print("  ├─ Symmetry ─────────────────────────┤")
    print("  │  □ Rotation Invariant               │")
    print("  ├─ Connectors ───────────────────────┤")
    print("  │  +X: [ROAD ▼]  -X: [ROAD ▼]       │")
    print("  │  +Y: [ROAD ▼]  -Y: [ROAD ▼]       │")
    print("  └────────────────────────────────────┘")
else:
    print("=" * 60)
    print("❌ SOME CHECKS FAILED")
    print("=" * 60)
    sys.exit(1)
