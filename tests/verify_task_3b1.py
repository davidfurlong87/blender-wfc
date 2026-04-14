"""
Verify Task 3B.1: Fix Load Always Available
Run with: python tests/verify_task_3b1.py
"""

from pathlib import Path

content = Path('addons/blender-wfc/primitive_ui.py').read_text()
lines = content.splitlines()

all_passed = True

def check(label, condition):
    global all_passed
    status = "✅" if condition else "❌"
    print(f"  {status} {label}")
    if not condition:
        all_passed = False


# ── Load button is before early return ───────────────────────────────────────
print("Load button position:")

load_line = next((i for i, l in enumerate(lines)
                  if 'operator("object.wfc_load_primitive"' in l), None)
return_line = next((i for i, l in enumerate(lines)
                    if "obj.type != 'MESH'" in l), None)

check("wfc_load_primitive found in file",        load_line is not None)
check("early return guard found in file",        return_line is not None)
check("load button appears BEFORE early return", load_line is not None and
                                                  return_line is not None and
                                                  load_line < return_line)


# ── Load button is guarded only by PERSISTENCE_AVAILABLE ─────────────────────
print("\nLoad button gating:")
# Find the block containing the load operator
load_ctx = lines[max(0, load_line - 4): load_line + 2] if load_line else []
load_ctx_str = "\n".join(load_ctx)
check("guarded by PERSISTENCE_AVAILABLE",        "PERSISTENCE_AVAILABLE" in load_ctx_str)
check("not gated on obj or obj.type",            "obj.type" not in load_ctx_str)
check("separator after load button",             any("separator" in l for l in lines[load_line:load_line+4]))


# ── TODO and duplicate section removed ───────────────────────────────────────
print("\nCleanup:")
check("old TODO about load availability removed",
      "make always available?" not in content)
check("duplicate 'Section 4: Load' label removed",
      content.count("Section 4:") == 1)
check("load operator called exactly once in draw()",
      content.count('operator("object.wfc_load_primitive"') == 1)


# ── Section numbering is correct ─────────────────────────────────────────────
print("\nSection numbering:")
check("Section 4 is 'Save'",    "Section 4: Save" in content)
check("Section 5 is 'Legacy'",  "Section 5: Legacy" in content)
check("no orphaned 'Section 4: Load'", "Section 4: Load" not in content)


# ── Other sections unchanged ─────────────────────────────────────────────────
print("\nOther sections unchanged:")
check("Section 1: Primitive Type still present",  "Section 1: Primitive Type" in content)
check("Section 2: Connectors still present",      "Section 2: Connectors" in content)
check("Section 3: Grid metadata still present",   "Section 3: Grid metadata" in content)
check("Save operator still present",              "wfc_save_primitive" in content)
check("Legacy section still present",             "Legacy (Deprecated)" in content)


print()
if all_passed:
    print("=" * 60)
    print("✅ ALL CHECKS PASSED - Task 3B.1 complete!")
    print("=" * 60)
    print("\nPanel layout (no object selected):")
    print("  [ Load from JSON ]     ← always visible")
    print("  Select a mesh object   ← message shown here")
    print()
    print("Panel layout (mesh selected):")
    print("  [ Load from JSON ]     ← always visible")
    print("  ─ Primitive Type ──────")
    print("  ─ Connectors ──────────")
    print("  ─ Grid Metadata ───────")
    print("  ─ Save ─────────────── ← only when complete")
    print("  ─ Legacy ──────────────")
else:
    print("=" * 60)
    print("❌ SOME CHECKS FAILED")
    print("=" * 60)
    import sys; sys.exit(1)
