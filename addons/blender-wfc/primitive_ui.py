"""
Primitive UI - Panels and Operators

This module provides the Blender UI for creating, editing, and managing WFC primitives.
It integrates with the persistence system (Phases 1-3):
- PrimitiveData: Pure Python data structure
- PrimitiveAdapter: Blender ↔ Data conversion
- PrimitivePersistence: JSON save/load

Architecture:
- All Blender ↔ Data operations go through PrimitiveAdapter
- All file operations go through PrimitivePersistence
- All validation happens in PrimitiveData

See docs/features/PRIMITIVE_UI_REFACTORING_ANALYSIS.md for details.
"""

import bpy
import os
from bpy.props import EnumProperty, StringProperty, FloatProperty, IntProperty, BoolProperty
from .wfc_enums import PRIMITIVE_TYPES, CUSTOM_PRIMITIVE_TYPES, get_connector_enum_items, GRID_CATEGORIES, PrimitiveDefinition
from .wfc_values import bl_category_name, GridCategory, DEFAULT_GRID_SIZES
from .primitive_data_actual import *

# Import new persistence system (Phases 1-3)
try:
    from .primitive_adapter import PrimitiveAdapter
    from .primitive_persistence import PrimitivePersistence
    from .primitive_data_core import PrimitiveData
    PERSISTENCE_AVAILABLE = True
except ImportError:
    PERSISTENCE_AVAILABLE = False
    print("Warning: Primitive persistence system not available")


# ============================================================================
# Helper Functions
# ============================================================================

def get_primitive_type_items(self, context):
    """Dynamic enum items for primitive types (used by operators)"""
    items = PRIMITIVE_TYPES.copy()
    items.extend(CUSTOM_PRIMITIVE_TYPES)
    items.append(('CUSTOM', 'Custom', 'Create new custom primitive type'))
    return items


def has_connectors_assigned(obj):
    """Check if object has all connectors assigned"""
    if not obj:
        return False
    return (hasattr(obj, 'x_pos_connector') and obj.x_pos_connector and obj.x_pos_connector != 'NONE' and
            hasattr(obj, 'x_neg_connector') and obj.x_neg_connector and obj.x_neg_connector != 'NONE' and
            hasattr(obj, 'y_pos_connector') and obj.y_pos_connector and obj.y_pos_connector != 'NONE' and
            hasattr(obj, 'y_neg_connector') and obj.y_neg_connector and obj.y_neg_connector != 'NONE')


def is_primitive_complete(obj):
    """Check if object is ready to save as primitive"""
    if not obj:
        return False
    has_type = hasattr(obj, 'primitive_type') and obj.primitive_type and obj.primitive_type != 'NONE'
    return has_type and has_connectors_assigned(obj)


# ============================================================================
# Panel
# ============================================================================

# ============================================================================
# Pack panel (Stage 4 — P2-B / P2-C)
# ============================================================================

class OBJECT_PT_WFCPackPanel(bpy.types.Panel):
    """Shows the active pack name, metadata, and the list of its primitives."""
    bl_label = "WFC Pack"
    bl_idname = "OBJECT_PT_WFCPackPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = bl_category_name
    bl_order = 0  # appears above Primitive Builder (bl_order = 1)

    def draw(self, context):
        from .pack_state import get_active_pack
        layout = self.layout
        pack = get_active_pack()

        # ── Header ───────────────────────────────────────────────────────────
        header = layout.box()
        if pack:
            row = header.row()
            row.label(text=pack['name'], icon='PACKAGE')
            row.operator("object.wfc_rename_pack", text="", icon='GREASEPENCIL')

            # Source-mode badge: JSON / Hybrid / Blend-only
            mode = pack.get('source_mode', 'json_only')
            mode_icon = {
                'json_only':  'FILE_TEXT',
                'hybrid':     'LINKED',
                'blend_only': 'BLENDER',
            }.get(mode, 'FILE_TEXT')
            mode_label = {
                'json_only':  "JSON only",
                'hybrid':     "Hybrid (JSON + Blend)",
                'blend_only': "Blend only",
            }.get(mode, mode)
            header.label(
                text=f"{pack['category']}  |  {pack['physical_size']}m  |  ×{pack['resolution_multiplier']}  |  {mode_label}",
                icon=mode_icon,
            )

            row = header.row(align=True)
            row.operator("object.wfc_load_pack",  text="Load",   icon='FILEBROWSER')
            row.operator("object.wfc_save_pack",  text="Save",   icon='FILE_TICK')
            row.operator("object.wfc_merge_pack", text="Merge…", icon='COLLECTION_NEW')
            row.operator("object.wfc_new_pack",   text="New",    icon='ADD')

            # Material library export (MP-B2)
            header.operator(
                "object.wfc_export_materials",
                text="Export Materials…",
                icon='MATERIAL',
            )

            # Migration helper: offer "Export as Blend" for JSON-only packs
            if mode == 'json_only':
                mig = header.box()
                mig.label(text="Export geometry to a .blend for portability:", icon='INFO')
                mig.operator("object.wfc_export_to_blend", text="Export as Blend…", icon='EXPORT')
        else:
            header.label(text="No active pack", icon='INFO')
            row = header.row(align=True)
            row.operator("object.wfc_new_pack",  text="New Pack",  icon='ADD')
            row.operator("object.wfc_load_pack", text="Load Pack", icon='FILEBROWSER')
            return  # nothing more to show when no pack is active

        # ── Primitive list ────────────────────────────────────────────────────
        layout.separator()
        layout.label(text="Primitives:", icon='OBJECT_DATA')

        try:
            from .collectiontools import ensure_primitives_collection
            col = ensure_primitives_collection(pack['category'])
            objects = sorted(
                [o for o in col.objects if o.type == 'MESH'],
                key=lambda o: o.name,
            )
        except Exception:
            objects = []

        if not objects:
            layout.label(text="No primitives yet — create or load some", icon='INFO')
        else:
            box = layout.box()
            for obj in objects:
                ptype          = getattr(obj, 'primitive_type', 'NONE') or 'NONE'
                has_connectors = bool(getattr(obj, 'x_pos_connector', ''))
                complete       = ptype != 'NONE' and has_connectors
                row = box.row(align=True)
                row.label(
                    text=f"{obj.name}  [{ptype}]",
                    icon='CHECKMARK' if complete else 'ERROR',
                )
                op = row.operator("object.wfc_select_primitive",  text="", icon='RESTRICT_SELECT_OFF')
                op.primitive_name = obj.name
                op = row.operator("object.wfc_rename_primitive",  text="", icon='GREASEPENCIL')
                op.primitive_name = obj.name
                op = row.operator("object.wfc_delete_primitive",  text="", icon='X')
                op.primitive_name = obj.name


# ============================================================================
# Connector Registry sub-panel (Stage 5 — P3-A / P3-C)
# ============================================================================

class OBJECT_PT_WFCConnectorRegistryPanel(bpy.types.Panel):
    """Collapsible sub-panel showing the active pack's connector registry.
    Allows adding, renaming, and deleting connectors without editing JSON."""
    bl_label = "Connector Registry"
    bl_idname = "OBJECT_PT_WFCConnectorRegistryPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = bl_category_name
    bl_parent_id = "OBJECT_PT_WFCPackPanel"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        from .pack_state import has_active_pack
        return has_active_pack()

    def draw(self, context):
        from .connector_registry import get_active_registry
        layout = self.layout
        reg = get_active_registry()
        connectors = sorted(reg.connectors.values(), key=lambda c: c.name)

        if not connectors:
            layout.label(text="No connectors defined", icon='INFO')
        else:
            box = layout.box()
            for conn in connectors:
                row = box.row(align=True)
                compat = ', '.join(conn.compatible_with) if conn.compatible_with else '—'
                # Name + compact compatible-with summary
                row.label(text=conn.name, icon='SYSTEM')
                row.label(text=compat)
                op = row.operator("object.wfc_rename_connector", text="", icon='GREASEPENCIL')
                op.connector_name = conn.name
                op = row.operator("object.wfc_delete_connector", text="", icon='X')
                op.connector_name = conn.name

        layout.operator("object.wfc_add_connector", text="Add Connector", icon='ADD')


# ============================================================================
# Primitive Builder panel
# ============================================================================

class OBJECT_PT_WFCPrimitiveBuilderPanel(bpy.types.Panel):
    """Panel for creating and managing WFC primitives"""
    bl_label = "Primitive Builder"
    bl_idname = "OBJECT_PT_WFCPrimitiveBuilderPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = bl_category_name
    bl_order = 1  # appears below the Pack panel (bl_order = 0)

    def draw(self, context):
        layout = self.layout
        obj = context.object
        
        # Load from JSON is always available — it creates a new object at the
        # cursor, so it requires no selection. Must be before the early return.
        if PERSISTENCE_AVAILABLE:
            layout.operator("object.wfc_load_primitive", text="Load from JSON", icon='IMPORT')
            layout.separator()

        # Remaining sections require a valid mesh selection
        if not obj or obj.type != 'MESH':
            layout.label(text="Select a mesh object", icon='ERROR')
            return
        
        # Section 1: Primitive Type
        box = layout.box()
        box.label(text="Primitive Type:", icon='MESH_DATA')
        
        if obj.primitive_type and obj.primitive_type != 'NONE':
            # Show current type (read-only)
            row = box.row()
            row.prop(obj, "primitive_type", text="Type")
            row.enabled = False
            # TODO: below will correctly assign primitive type, but will not copy the connectors, possibly because they aren't saved project-wide when editing a primitive's connectors 
            box.operator("object.wfc_assign_primitive_type", text="Change Type", icon='EDITMODE_HLT')
        else:
            box.operator("object.wfc_assign_primitive_type", text="Assign Type", icon='ADD')
        
        # Section 2: Connectors (only if type assigned)
        if obj.primitive_type and obj.primitive_type != 'NONE':
            box = layout.box()
            box.label(text="Connectors:", icon='LINKED')

            if has_connectors_assigned(obj):
                # Display current connectors (read-only)
                grid = box.grid_flow(columns=2, align=True)
                col1 = grid.column()
                col1.prop(obj, "x_pos_connector", text="+X")
                col1.prop(obj, "x_neg_connector", text="-X")
                col2 = grid.column()
                col2.prop(obj, "y_pos_connector", text="+Y")
                col2.prop(obj, "y_neg_connector", text="-Y")
                grid.enabled = False

                box.operator("object.wfc_assign_connectors", text="Edit Connectors & Metadata", icon='EDITMODE_HLT')
                box.operator("object.wfc_copy_connectors", text="Copy to Selected", icon='COPYDOWN')
            else:
                box.label(text="No connectors assigned", icon='INFO')
                box.operator("object.wfc_assign_connectors", text="Assign Connectors & Metadata", icon='ADD')

        # Section 3: Grid metadata (only if type assigned) — Task 3A.2
        if obj.primitive_type and obj.primitive_type != 'NONE':
            box = layout.box()
            box.label(text="Grid Metadata:", icon='SNAP_GRID')

            # Category + size + resolution (read-only)
            col = box.column(align=True)
            col.prop(obj, "grid_category", text="Category")
            row = col.row(align=True)
            row.prop(obj, "physical_size", text="Size (m)")
            row.prop(obj, "resolution_multiplier", text="Res")
            col.enabled = False

            # Rotation invariant (read-only checkbox + hint)
            row = box.row()
            row.prop(obj, "rotation_invariant", text="Rotation Invariant")
            row.enabled = False
            if obj.rotation_invariant:
                box.label(text="1 module generated (not 4)", icon='INFO')

        # Section 4: Save (only if primitive is complete)
        if PERSISTENCE_AVAILABLE and is_primitive_complete(obj):
            box = layout.box()
            box.label(text="Save:", icon='FILE')
            box.operator("object.wfc_save_primitive", text="Save to JSON", icon='EXPORT')

        # Section 5: Legacy (deprecation warning)
        layout.separator()
        box = layout.box()
        box.label(text="Legacy (Deprecated):", icon='ERROR')
        box.operator("object.wfc_convert_to_primitive", text="Print to Console (Old)")


# ============================================================================
# Operators
# ============================================================================

class OBJECT_OT_WFCAssignPrimitiveType(bpy.types.Operator):
    """Assign a primitive type to the selected object"""
    bl_idname = "object.wfc_assign_primitive_type"
    bl_label = "Assign Primitive Type"
    bl_options = {'REGISTER', 'UNDO'}

    prim_type: EnumProperty(
        name="Primitive Type",
        description="Select primitive type to assign",
        items=get_primitive_type_items,
    ) # type: ignore

    custom_type_name: StringProperty(
        name="Custom Type Name",
        description="Name for new custom primitive type",
        default="New_Primitive"
    ) # type: ignore

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "prim_type")

        if self.prim_type == 'CUSTOM':
            layout.prop(self, "custom_type_name")

    def execute(self, context):
        obj = context.object

        if not obj:
            self.report({'ERROR'}, "No object selected")
            return {'CANCELLED'}

        if obj.type != 'MESH':
            self.report({'ERROR'}, "Selected object is not a mesh")
            return {'CANCELLED'}

        # Handle custom type creation
        if self.prim_type == 'CUSTOM':
            if not self.custom_type_name.strip():
                self.report({'ERROR'}, "Custom type name cannot be empty")
                return {'CANCELLED'}

            # Preserve the user's casing for the display label; only the
            # internal enum identifier is forced to uppercase so it stays
            # consistent with the built-in types (ROAD_STRAIGHT, ROOM, etc.).
            display_name = self.custom_type_name.strip().replace(' ', '_')
            identifier = display_name.upper()
            new_primitive_def = PrimitiveDefinition(display_name)
            new_enum_item = new_primitive_def.as_blender_enum()  # (IDENTIFIER, display_name, '')

            if new_enum_item not in CUSTOM_PRIMITIVE_TYPES:
                CUSTOM_PRIMITIVE_TYPES.append(new_enum_item)

            obj.primitive_type = identifier
            self.report({'INFO'}, f"Created and assigned custom primitive type: {display_name}")
        else:
            obj.primitive_type = self.prim_type
            self.report({'INFO'}, f"Assigned primitive type: {self.prim_type}")

        context.view_layer.update()
        return {'FINISHED'}


class OBJECT_OT_WFCAssignConnectors(bpy.types.Operator):
    """Assign connector values to the primitive"""
    bl_idname = "object.wfc_assign_connectors"
    bl_label = "Assign Connectors"
    bl_options = {'REGISTER', 'UNDO'}

    pos_x: EnumProperty(
        name="+X Connector",
        description="Connector on positive X face",
        items=get_connector_enum_items
    ) # type: ignore

    neg_x: EnumProperty(
        name="-X Connector",
        description="Connector on negative X face",
        items=get_connector_enum_items
    ) # type: ignore

    pos_y: EnumProperty(
        name="+Y Connector",
        description="Connector on positive Y face",
        items=get_connector_enum_items
    ) # type: ignore

    neg_y: EnumProperty(
        name="-Y Connector",
        description="Connector on negative Y face",
        items=get_connector_enum_items
    ) # type: ignore

    # NEW: Sizing and symmetry metadata (Task 3A.1 Step 3)
    physical_size: FloatProperty(
        name="Physical Size (m)",
        description="Physical size of this primitive in meters",
        default=8.0,
        min=0.1,
        soft_max=100.0
    ) # type: ignore

    grid_category: EnumProperty(
        name="Grid Category",
        description="Which grid system this primitive belongs to",
        items=GRID_CATEGORIES,
        default='outer_grid'
    ) # type: ignore

    resolution_multiplier: IntProperty(
        name="Resolution Multiplier",
        description="How many of these cells fit in one outer grid cell",
        default=1,
        min=1,
        soft_max=16
    ) # type: ignore

    rotation_invariant: BoolProperty(
        name="Rotation Invariant",
        description="All 4 rotations produce identical geometry — only one module will be generated",
        default=False
    ) # type: ignore

    def invoke(self, context, event):
        obj = context.object

        # Pre-populate connectors with existing values if already assigned
        if obj and has_connectors_assigned(obj):
            self.pos_x = obj.x_pos_connector
            self.neg_x = obj.x_neg_connector
            self.pos_y = obj.y_pos_connector
            self.neg_y = obj.y_neg_connector

        if obj:
            # If the object already has category metadata, use it directly.
            if obj.grid_category and obj.grid_category != GridCategory.OUTER_GRID or obj.physical_size != DEFAULT_GRID_SIZES[GridCategory.OUTER_GRID]:
                self.physical_size          = obj.physical_size
                self.grid_category          = obj.grid_category
                self.resolution_multiplier  = obj.resolution_multiplier
                self.rotation_invariant     = obj.rotation_invariant
            else:
                # Fall back to active pack defaults (P2-D) so new primitives
                # created inside a pack are pre-configured correctly.
                from .pack_state import get_active_pack
                pack = get_active_pack()
                if pack:
                    self.grid_category          = pack['category']
                    self.physical_size          = pack['physical_size']
                    self.resolution_multiplier  = pack['resolution_multiplier']
                else:
                    self.physical_size          = obj.physical_size
                    self.grid_category          = obj.grid_category
                    self.resolution_multiplier  = obj.resolution_multiplier
                    self.rotation_invariant     = obj.rotation_invariant

        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout

        # Section 1: Grid metadata
        box = layout.box()
        box.label(text="Grid Metadata:", icon='SNAP_GRID')
        box.prop(self, "grid_category")
        row = box.row(align=True)
        # Physical size is auto-derived when resolution_multiplier > 1.
        # Show it read-only so the user can see the computed value without
        # being able to set an inconsistent value by hand.
        size_col = row.column(align=True)
        size_col.prop(self, "physical_size")
        size_col.enabled = (self.resolution_multiplier == 1)
        row.prop(self, "resolution_multiplier")
        if self.resolution_multiplier > 1:
            _outer = DEFAULT_GRID_SIZES[GridCategory.OUTER_GRID]
            implied = _outer / self.resolution_multiplier
            box.label(
                text=f"Physical size auto-set to {implied:.4g}m  ({_outer:.4g}m ÷ {self.resolution_multiplier})",
                icon='INFO'
            )

        # Section 2: Symmetry
        box = layout.box()
        box.label(text="Symmetry:", icon='MOD_MIRROR')
        box.prop(self, "rotation_invariant")
        if self.rotation_invariant:
            box.label(text="Only 1 module will be generated (not 4)", icon='INFO')

        # Section 3: Connectors
        box = layout.box()
        box.label(text="Connectors:", icon='LINKED')
        box.prop(self, "pos_x")
        box.prop(self, "neg_x")
        box.prop(self, "pos_y")
        box.prop(self, "neg_y")

    def execute(self, context):
        obj = context.object

        if not obj:
            self.report({'ERROR'}, "No object selected")
            return {'CANCELLED'}

        if obj.type != 'MESH':
            self.report({'ERROR'}, "Selected object is not a mesh")
            return {'CANCELLED'}

        if not obj.primitive_type or obj.primitive_type == 'NONE':
            self.report({'ERROR'}, "Assign a primitive type first")
            return {'CANCELLED'}

        # Assign connector values
        obj.x_pos_connector = self.pos_x
        obj.x_neg_connector = self.neg_x
        obj.y_pos_connector = self.pos_y
        obj.y_neg_connector = self.neg_y

        # Assign sizing and symmetry metadata.
        # When resolution_multiplier > 1 the physical size is derived from the
        # outer cell size (8m) so the two values are always consistent.
        obj.grid_category = self.grid_category
        obj.resolution_multiplier = self.resolution_multiplier
        obj.rotation_invariant = self.rotation_invariant
        if self.resolution_multiplier > 1:
            obj.physical_size = DEFAULT_GRID_SIZES[GridCategory.OUTER_GRID] / self.resolution_multiplier
        else:
            obj.physical_size = self.physical_size

        self.report({'INFO'}, f"Assigned connectors and metadata to {obj.name}")
        context.view_layer.update()
        return {'FINISHED'}


class OBJECT_OT_WFCCopyConnectors(bpy.types.Operator):
    """Copy primitive type, connectors, and metadata from the active object
    to every other selected mesh object. Useful for quickly setting up
    multiple primitives with the same connector pattern."""
    bl_idname = "object.wfc_copy_connectors"
    bl_label = "Copy Type & Connectors from Active"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        source = context.active_object

        if not source:
            self.report({'ERROR'}, "No active object")
            return {'CANCELLED'}

        if source.type != 'MESH':
            self.report({'ERROR'}, "Active object is not a mesh")
            return {'CANCELLED'}

        if not getattr(source, 'primitive_type', None) or source.primitive_type == 'NONE':
            self.report({'ERROR'}, "Active object has no primitive type assigned — assign one first")
            return {'CANCELLED'}

        targets = [
            obj for obj in context.selected_objects
            if obj != source and obj.type == 'MESH'
        ]
        if not targets:
            self.report({'WARNING'}, "No other mesh objects selected — select the targets then Shift-click the active")
            return {'CANCELLED'}

        for obj in targets:
            obj.primitive_type         = source.primitive_type
            obj.x_pos_connector        = source.x_pos_connector
            obj.x_neg_connector        = source.x_neg_connector
            obj.y_pos_connector        = source.y_pos_connector
            obj.y_neg_connector        = source.y_neg_connector
            obj.physical_size          = source.physical_size
            obj.grid_category          = source.grid_category
            obj.resolution_multiplier  = source.resolution_multiplier
            obj.rotation_invariant     = source.rotation_invariant

        self.report({'INFO'}, f"Copied type & connectors to {len(targets)} object(s)")
        return {'FINISHED'}


class OBJECT_OT_WFCSavePrimitive(bpy.types.Operator):
    """Save the selected object as a primitive to JSON file"""
    bl_idname = "object.wfc_save_primitive"
    bl_label = "Save Primitive"
    bl_options = {'REGISTER'}

    filepath: StringProperty(
        name="File Path",
        description="Path to save the primitive JSON file",
        subtype='FILE_PATH'
    ) # type: ignore

    filename: StringProperty(
        name="File Name",
        default="primitive.json"
    ) # type: ignore

    def invoke(self, context, event):
        obj = context.object

        if not obj:
            self.report({'ERROR'}, "No object selected")
            return {'CANCELLED'}

        # Set default filename based on object name
        self.filename = f"{obj.name}.json"

        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        obj = context.object

        # Validation
        if not obj:
            self.report({'ERROR'}, "No object selected")
            return {'CANCELLED'}

        if obj.type != 'MESH':
            self.report({'ERROR'}, "Selected object is not a mesh")
            return {'CANCELLED'}

        if not is_primitive_complete(obj):
            self.report({'ERROR'}, "Primitive is incomplete. Assign type and connectors first.")
            return {'CANCELLED'}

        if not PERSISTENCE_AVAILABLE:
            self.report({'ERROR'}, "Persistence system not available")
            return {'CANCELLED'}

        try:
            # Extract primitive data using adapter
            adapter = PrimitiveAdapter()
            primitive_data, extract_errors = adapter.extract_primitive_from_blender(obj)

            if extract_errors:
                for err in extract_errors:
                    self.report({'WARNING'}, err)

            if not primitive_data:
                self.report({'ERROR'}, "Failed to extract primitive data")
                return {'CANCELLED'}

            # Save to file using persistence
            persistence = PrimitivePersistence()
            success, save_errors = persistence.save_primitive_to_file(
                primitive_data,
                self.filepath,
                pretty=True
            )

            if save_errors:
                for err in save_errors:
                    self.report({'ERROR'}, err)

            if success:
                self.report({'INFO'}, f"Saved primitive to {self.filepath}")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "Failed to save primitive")
                return {'CANCELLED'}

        except Exception as e:
            self.report({'ERROR'}, f"Unexpected error: {str(e)}")
            return {'CANCELLED'}


class OBJECT_OT_WFCLoadPrimitive(bpy.types.Operator):
    """Load a primitive from JSON file and create Blender object"""
    bl_idname = "object.wfc_load_primitive"
    bl_label = "Load Primitive"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: StringProperty(
        name="File Path",
        description="Path to the primitive JSON file",
        subtype='FILE_PATH'
    ) # type: ignore

    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'}
    ) # type: ignore

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        if not PERSISTENCE_AVAILABLE:
            self.report({'ERROR'}, "Persistence system not available")
            return {'CANCELLED'}

        try:
            import json as _json
            with open(self.filepath, 'r') as _f:
                _raw = _json.load(_f)
            is_library = 'primitives' in _raw
        except Exception as e:
            self.report({'ERROR'}, f"Could not read file: {e}")
            return {'CANCELLED'}

        persistence = PrimitivePersistence()
        adapter = PrimitiveAdapter()

        if is_library:
            # ── Library format: load all primitives at once ──────────────
            primitives_list, lib_meta, load_errors = persistence.load_primitive_library(self.filepath)

            for err in load_errors:
                self.report({'WARNING'}, err)

            if not primitives_list:
                self.report({'ERROR'}, "No primitives loaded from library")
                return {'CANCELLED'}

            from .collectiontools import ensure_primitives_collection

            created = []
            spacing = 0.0
            for prim_data in primitives_list:
                # Route each primitive into its own category subcollection:
                # WFC → WFC_Primitives → WFC_Primitives_{grid_category}
                prim_collection = ensure_primitives_collection(prim_data.grid_category)
                loc = (spacing, -10.0, 0.0)
                obj, create_errors = adapter.create_blender_object_from_primitive(
                    prim_data, collection=prim_collection, location=loc
                )
                for err in create_errors:
                    self.report({'WARNING'}, err)
                if obj:
                    created.append(obj)
                    spacing += prim_data.physical_size * 2

            if created:
                bpy.ops.object.select_all(action='DESELECT')
                for obj in created:
                    obj.select_set(True)
                context.view_layer.objects.active = created[-1]
                lib_name = lib_meta.get('library_name', 'library')

                # If the pack embeds its own connector definitions, activate
                # a session registry from them so the dropdown only shows
                # connectors that are valid for this pack.
                connector_dicts = lib_meta.get('connectors')
                if connector_dicts:
                    from .connector_registry import (
                        ConnectorRegistry, ConnectorDefinition,
                        set_session_registry,
                    )
                    session_reg = ConnectorRegistry.__new__(ConnectorRegistry)
                    session_reg.connectors = {}
                    for c_dict in connector_dicts:
                        try:
                            cd = ConnectorDefinition.from_dict(c_dict)
                            session_reg.register(cd)
                        except Exception:
                            pass
                    if session_reg.connectors:
                        set_session_registry(session_reg)
                        self.report(
                            {'INFO'},
                            f"Loaded {len(created)} primitives from '{lib_name}' "
                            f"({len(session_reg.connectors)} pack connectors activated)",
                        )
                    else:
                        self.report({'INFO'}, f"Loaded {len(created)} primitives from '{lib_name}'")
                else:
                    self.report({'INFO'}, f"Loaded {len(created)} primitives from '{lib_name}'")

                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "Failed to create any objects from library")
                return {'CANCELLED'}

        else:
            # ── Single primitive format ───────────────────────────────────
            primitive_data, load_errors = persistence.load_primitive_from_file(self.filepath)

            for err in load_errors:
                self.report({'WARNING'}, err)

            if not primitive_data:
                self.report({'ERROR'}, "Failed to load primitive data")
                return {'CANCELLED'}

            from .collectiontools import ensure_primitives_collection
            prim_collection = ensure_primitives_collection(primitive_data.grid_category)
            new_obj, create_errors = adapter.create_blender_object_from_primitive(
                primitive_data,
                collection=prim_collection,
                location=context.scene.cursor.location
            )

            for err in create_errors:
                self.report({'WARNING'}, err)

            if new_obj:
                bpy.ops.object.select_all(action='DESELECT')
                new_obj.select_set(True)
                context.view_layer.objects.active = new_obj
                self.report({'INFO'}, f"Loaded primitive: {new_obj.name}")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "Failed to create object from primitive")
                return {'CANCELLED'}


# ============================================================================
# Connector registry helpers (Stage 5 — P3-A / P3-C)
# ============================================================================

def _primitives_using_connector(connector_name: str, category: str) -> list:
    """Return names of mesh objects in *category*'s primitives collection
    whose connector fields (any of ±X / ±Y) match *connector_name*.

    Returns an empty list if the collection does not exist or is empty.
    """
    _CONNECTOR_FIELDS = (
        'x_pos_connector', 'x_neg_connector',
        'y_pos_connector', 'y_neg_connector',
    )
    try:
        from .collectiontools import ensure_primitives_collection
        col = ensure_primitives_collection(category)
        return [
            obj.name
            for obj in col.objects
            if obj.type == 'MESH'
            and any(getattr(obj, f, '') == connector_name for f in _CONNECTOR_FIELDS)
        ]
    except Exception:
        return []


# ============================================================================
# Connector management operators (Stage 5 — P3-A / P3-C)
# ============================================================================

class OBJECT_OT_WFCAddConnector(bpy.types.Operator):
    """Add a new connector to the active pack's registry"""
    bl_idname = "object.wfc_add_connector"
    bl_label = "Add Connector"
    bl_options = {'REGISTER', 'UNDO'}

    name: StringProperty(name="Name", default="NEW_CONNECTOR")  # type: ignore
    description: StringProperty(name="Description", default="")  # type: ignore
    compatible_with: StringProperty(
        name="Compatible With",
        description="Comma-separated names of connectors this one can pair with",
        default="",
    )  # type: ignore
    grid_category: EnumProperty(
        name="Grid Category", items=GRID_CATEGORIES, default='building'
    )  # type: ignore
    is_symmetric: BoolProperty(name="Symmetric", default=True)  # type: ignore

    def invoke(self, context, event):
        from .pack_state import get_active_pack
        pack = get_active_pack()
        if pack:
            self.grid_category = pack['category']
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "name")
        layout.prop(self, "description")
        layout.prop(self, "compatible_with")
        layout.label(text="Separate multiple names with commas, e.g.  WALL, DOOR", icon='INFO')
        layout.prop(self, "grid_category")
        layout.prop(self, "is_symmetric")

    def execute(self, context):
        from .connector_registry import (
            ConnectorDefinition, ensure_mutable_session_registry,
        )
        name = self.name.strip().upper().replace(' ', '_')
        if not name:
            self.report({'ERROR'}, "Connector name cannot be empty")
            return {'CANCELLED'}

        compat = [
            c.strip().upper().replace(' ', '_')
            for c in self.compatible_with.split(',')
            if c.strip()
        ]
        new_def = ConnectorDefinition(
            name=name,
            description=self.description.strip(),
            compatible_with=compat,
            grid_category=self.grid_category,
            is_symmetric=self.is_symmetric,
        )
        reg = ensure_mutable_session_registry()
        already_exists = name in reg.connectors
        reg.register(new_def)
        action = "updated" if already_exists else "added"
        self.report({'INFO'}, f"Connector '{name}' {action}")
        return {'FINISHED'}


class OBJECT_OT_WFCDeleteConnector(bpy.types.Operator):
    """Delete a connector from the active registry.
    Blocked when any primitive in the active pack currently uses it."""
    bl_idname = "object.wfc_delete_connector"
    bl_label = "Delete Connector"
    bl_options = {'REGISTER', 'UNDO'}

    connector_name: StringProperty()  # type: ignore

    def execute(self, context):
        from .connector_registry import ensure_mutable_session_registry
        from .pack_state import get_active_pack

        pack = get_active_pack()
        if pack:
            using = _primitives_using_connector(self.connector_name, pack['category'])
            if using:
                sample = ', '.join(using[:3])
                suffix = '…' if len(using) > 3 else ''
                self.report(
                    {'ERROR'},
                    f"Cannot delete '{self.connector_name}': "
                    f"used by {len(using)} primitive(s): {sample}{suffix}",
                )
                return {'CANCELLED'}

        reg = ensure_mutable_session_registry()
        if reg.unregister(self.connector_name):
            self.report({'INFO'}, f"Connector '{self.connector_name}' deleted")
            return {'FINISHED'}
        self.report({'ERROR'}, f"Connector '{self.connector_name}' not found")
        return {'CANCELLED'}


class OBJECT_OT_WFCRenameConnector(bpy.types.Operator):
    """Rename a connector and automatically update every primitive that uses it"""
    bl_idname = "object.wfc_rename_connector"
    bl_label = "Rename Connector"
    bl_options = {'REGISTER', 'UNDO'}

    connector_name: StringProperty()  # type: ignore
    new_name: StringProperty(name="New Name")  # type: ignore

    def invoke(self, context, event):
        self.new_name = self.connector_name
        return context.window_manager.invoke_props_dialog(self, width=320)

    def draw(self, context):
        layout = self.layout
        layout.label(text=f"Renaming: {self.connector_name}", icon='SYSTEM')
        layout.prop(self, "new_name")

    def execute(self, context):
        from .connector_registry import ensure_mutable_session_registry
        from .pack_state import get_active_pack

        new_name = self.new_name.strip().upper().replace(' ', '_')
        if not new_name:
            self.report({'ERROR'}, "Name cannot be empty")
            return {'CANCELLED'}
        if new_name == self.connector_name:
            return {'FINISHED'}

        reg = ensure_mutable_session_registry()
        if not reg.rename(self.connector_name, new_name):
            self.report(
                {'ERROR'},
                f"Could not rename: '{self.connector_name}' not found "
                f"or '{new_name}' already exists",
            )
            return {'CANCELLED'}

        # Update every connector field on every primitive in the active pack
        updated_fields = 0
        pack = get_active_pack()
        if pack:
            _FIELDS = ('x_pos_connector', 'x_neg_connector',
                       'y_pos_connector', 'y_neg_connector')
            try:
                from .collectiontools import ensure_primitives_collection
                col = ensure_primitives_collection(pack['category'])
                for obj in col.objects:
                    if obj.type == 'MESH':
                        for field in _FIELDS:
                            if getattr(obj, field, '') == self.connector_name:
                                setattr(obj, field, new_name)
                                updated_fields += 1
            except Exception as exc:
                self.report(
                    {'WARNING'},
                    f"Registry updated but could not patch primitives: {exc}",
                )
                return {'FINISHED'}

        msg = f"Renamed '{self.connector_name}' → '{new_name}'"
        if updated_fields:
            msg += f"  ({updated_fields} primitive field(s) updated)"
        self.report({'INFO'}, msg)
        return {'FINISHED'}


# ============================================================================
# Pack management operators (Stage 4 — P2-B)
# ============================================================================

class OBJECT_OT_WFCNewPack(bpy.types.Operator):
    """Create a new empty primitive pack and set it as the active pack"""
    bl_idname = "object.wfc_new_pack"
    bl_label = "New Pack"
    bl_options = {'REGISTER', 'UNDO'}

    pack_name: StringProperty(name="Pack Name", default="My Pack")  # type: ignore
    category: EnumProperty(
        name="Grid Category", items=GRID_CATEGORIES, default='building'
    )  # type: ignore
    physical_size: FloatProperty(
        name="Physical Size (m)", default=2.0, min=0.1, soft_max=100.0
    )  # type: ignore
    resolution_multiplier: IntProperty(
        name="Resolution Multiplier", default=4, min=1, soft_max=16
    )  # type: ignore

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=360)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "pack_name")
        layout.prop(self, "category")
        row = layout.row(align=True)
        col = row.column(align=True)
        col.prop(self, "physical_size")
        col.enabled = (self.resolution_multiplier == 1)
        row.prop(self, "resolution_multiplier")
        if self.resolution_multiplier > 1:
            _outer = DEFAULT_GRID_SIZES[GridCategory.OUTER_GRID]
            layout.label(
                text=f"Physical size: {_outer / self.resolution_multiplier:.4g}m  ({_outer:.4g}m ÷ {self.resolution_multiplier})",
                icon='INFO',
            )

    def execute(self, context):
        from .pack_state import set_active_pack
        from .connector_registry import clear_session_registry
        _outer = DEFAULT_GRID_SIZES[GridCategory.OUTER_GRID]
        size = (_outer / self.resolution_multiplier) if self.resolution_multiplier > 1 else self.physical_size
        set_active_pack(
            name=self.pack_name,
            category=self.category,
            physical_size=size,
            resolution_multiplier=self.resolution_multiplier,
        )
        clear_session_registry()
        self.report({'INFO'}, f"Pack '{self.pack_name}' created  ({self.category})")
        return {'FINISHED'}


# ============================================================================
# Material-pack helpers (MP-A1)
# ============================================================================

def _gather_images_from_materials(materials):
    """Return a list of all unique ``bpy.types.Image`` datablocks referenced by
    ``ShaderNodeTexImage`` nodes in the given materials.

    Handles gracefully:
    - ``None`` entries in *materials*
    - materials that have no node tree (``use_nodes`` is False or node_tree is
      ``None``)
    - node trees that contain no ``ShaderNodeTexImage`` nodes
    - image slots on those nodes that are ``None``

    Args:
        materials: Iterable of ``bpy.types.Material`` (or ``None``) objects.

    Returns:
        Deduplicated list of ``bpy.types.Image`` objects (may be empty).
    """
    seen  = set()
    found = []
    for mat in materials:
        if mat is None:
            continue
        if not getattr(mat, 'use_nodes', False):
            continue
        tree = getattr(mat, 'node_tree', None)
        if tree is None:
            continue
        for node in tree.nodes:
            if node.type != 'TEX_IMAGE':
                continue
            img = getattr(node, 'image', None)
            if img is None:
                continue
            if img.name not in seen:
                seen.add(img.name)
                found.append(img)
    return found


def _parse_connector_registry_text(text_content):
    """Parse embedded ``wfc_connectors.json`` text and return connector dicts.

    Returns an empty list when the text is empty, malformed, or does not contain
    a top-level ``connectors`` list.
    """
    import json as _json

    if not text_content:
        return []

    try:
        payload = _json.loads(text_content)
    except Exception:
        return []

    connector_dicts = payload.get('connectors', [])
    if not isinstance(connector_dicts, list):
        return []
    return [cd for cd in connector_dicts if isinstance(cd, dict)]


def _infer_connector_dicts_from_objects(objects, default_category='outer_grid'):
    """Infer placeholder connector definitions from primitive object metadata.

    This is a last-resort recovery path for blend-only loads when no pack-local
    registry can be restored from JSON or embedded text data.  The inferred
    definitions are intentionally conservative placeholder entries: symmetric and
    self-compatible, with the connector name preserved exactly as stored on the
    object.
    """
    inferred = {}
    fields = (
        'x_pos_connector', 'x_neg_connector',
        'y_pos_connector', 'y_neg_connector',
    )

    for obj in objects or []:
        if getattr(obj, 'type', 'MESH') != 'MESH':
            continue
        category = getattr(obj, 'grid_category', None) or default_category
        for field in fields:
            name = str(getattr(obj, field, '') or '').strip()
            if not name or name == 'NONE':
                continue
            if name not in inferred:
                inferred[name] = {
                    'name': name,
                    'description': f"Inferred placeholder connector '{name}' from blend-only pack load",
                    'compatible_with': [name],
                    'grid_category': category,
                    'is_symmetric': True,
                }

    return [inferred[name] for name in sorted(inferred)]


def _textblock_to_string(text_block):
    """Return full text content from a Blender Text datablock-like object."""
    if text_block is None:
        return ""
    try:
        return text_block.as_string()
    except Exception:
        pass

    lines = getattr(text_block, 'lines', None)
    if lines is None:
        return ""
    return "\n".join(getattr(line, 'body', '') for line in lines)


def _load_embedded_connector_dicts_from_blend(blend_path: str):
    """Load connector definitions from embedded ``wfc_connectors.json`` text.

    Returns ``(connector_dicts, status)`` where *status* is one of:
    ``'loaded'``, ``'missing'``, ``'malformed'``, or ``'error'``.
    """
    text_name = "wfc_connectors.json"
    existing_names = {text.name for text in bpy.data.texts}
    loaded_text = None

    try:
        with bpy.data.libraries.load(blend_path, link=False) as (src, dst):
            if text_name not in getattr(src, 'texts', []):
                return [], 'missing'
            dst.texts = [text_name]

        new_texts = [
            text for text in bpy.data.texts
            if text.name not in existing_names and text.name.startswith(text_name)
        ]
        loaded_text = new_texts[-1] if new_texts else None
        if loaded_text is None:
            return [], 'error'

        connector_dicts = _parse_connector_registry_text(
            _textblock_to_string(loaded_text)
        )
        if connector_dicts:
            return connector_dicts, 'loaded'
        return [], 'malformed'
    except Exception:
        return [], 'error'
    finally:
        if loaded_text is not None:
            try:
                bpy.data.texts.remove(loaded_text)
            except Exception:
                pass


# ============================================================================
# Migration helper — Export JSON-only pack as Blend (Stage 7 UX polish)
# ============================================================================

class OBJECT_OT_WFCExportToBlend(bpy.types.Operator):
    """Convert a JSON-only pack to a Hybrid pack by exporting geometry to a .blend file.

    Pre-fills the file browser with a path derived from the current JSON
    manifest path (same stem, ``.blend`` extension).  On confirmation the
    full hybrid save workflow runs — geometry goes to ``.blend``, manifest
    is updated in-place, and the pack state switches to ``'hybrid'``.
    """
    bl_idname  = "object.wfc_export_to_blend"
    bl_label   = "Export as Blend"
    bl_options = {'REGISTER'}

    filepath:    StringProperty(subtype='FILE_PATH')  # type: ignore
    filter_glob: StringProperty(default="*.blend", options={'HIDDEN'})  # type: ignore

    def invoke(self, context, event):
        from .pack_state import get_active_pack
        pack = get_active_pack()
        if pack and pack.get('filepath'):
            # Suggest <same folder>/<pack name stem>.blend
            stem = os.path.splitext(pack['filepath'])[0]
            self.filepath = stem + '.blend'
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        # Delegate entirely to the save operator's blend path
        bpy.ops.object.wfc_save_pack('INVOKE_DEFAULT', filepath=self.filepath)
        return {'FINISHED'}


# ============================================================================
# Blend-pack I/O helpers (Stage 7 — Task 5)
# ============================================================================

def _discover_blend_collection(blend_path: str):
    """Inspect *blend_path* and return the most likely WFC primitives collection.

    Checks for collections whose name ends with ``_Primitives`` (the WFC
    naming convention).  If exactly one such collection is found it is
    returned automatically; if there are multiple the caller must resolve
    the ambiguity via a companion JSON manifest.

    Returns the collection name string, or ``None`` when no suitable
    collection is found or the file cannot be read.
    """
    try:
        with bpy.data.libraries.load(blend_path, link=False) as (src, _):
            collections = list(src.collections)
        wfc_cols = [c for c in collections if c.endswith('_Primitives')]
        if len(wfc_cols) == 1:
            return wfc_cols[0]
        if not wfc_cols and len(collections) == 1:
            return collections[0]
    except Exception:
        pass
    return None


def _load_primitives_from_blend(operator, blend_path: str,
                                 blend_collection: str, category: str):
    """Append primitive objects from *blend_path* into ``WFC_Primitives_{category}``.

    Purges any existing objects in the destination collection first to
    prevent Blender's ``.001`` rename behaviour (PoC finding: orphaned
    data-blocks cause name conflicts on re-import).

    Uses ``operator.report()`` for user-visible error messages.

    Args:
        operator:         The calling Blender operator (for ``report()``).
        blend_path:       Absolute path to the ``.blend`` file.
        blend_collection: Name of the collection to append (from
                          ``blend_collection`` in the pack manifest, or
                          discovered via :func:`_discover_blend_collection`).
        category:         Grid category string used to resolve the
                          destination WFC collection.

    Returns:
        List of loaded :class:`bpy.types.Object` instances on success,
        or ``None`` on failure.
    """
    from .collectiontools import (
        ensure_primitives_collection,
        delete_objects_and_meshes,
        link_object_to_single_collection,
    )

    dest_col = ensure_primitives_collection(category)

    # Purge existing objects to avoid .001 name collisions on load
    existing = list(dest_col.objects)
    if existing:
        delete_objects_and_meshes(existing)

    with bpy.data.libraries.load(blend_path, link=False) as (src, dst):
        if blend_collection not in src.collections:
            operator.report(
                {'ERROR'},
                f"Collection '{blend_collection}' not found in '{blend_path}'",
            )
            return None
        # PoC confirmed: all four types must be requested explicitly.
        # Requesting only collections returns an empty collection shell.
        dst.collections = [blend_collection]
        dst.objects     = list(src.objects)
        dst.meshes      = list(src.meshes)
        dst.materials   = list(src.materials)

    imported_col = bpy.data.collections.get(blend_collection)
    if not imported_col:
        operator.report(
            {'ERROR'},
            f"Collection '{blend_collection}' failed to load from '{blend_path}'",
        )
        return None

    loaded = []
    for obj in list(imported_col.objects):
        link_object_to_single_collection(obj, dest_col)
        loaded.append(obj)

    # Remove the now-empty transport collection
    bpy.data.collections.remove(imported_col)

    if not loaded:
        operator.report(
            {'ERROR'},
            f"Collection '{blend_collection}' contained no objects",
        )
        return None

    return loaded


# ============================================================================

class OBJECT_OT_WFCLoadPack(bpy.types.Operator):
    """Load a primitive pack from a JSON or .blend file and set it as the active pack"""
    bl_idname = "object.wfc_load_pack"
    bl_label = "Load Pack"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: StringProperty(subtype='FILE_PATH')  # type: ignore
    filter_glob: StringProperty(default="*.json;*.blend", options={'HIDDEN'})  # type: ignore

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    # ── public entry point ────────────────────────────────────────────────────

    def execute(self, context):
        if not PERSISTENCE_AVAILABLE:
            self.report({'ERROR'}, "Persistence system unavailable")
            return {'CANCELLED'}

        ext = os.path.splitext(self.filepath)[1].lower()
        result = (
            self._load_from_blend_file(context)
            if ext == '.blend'
            else self._load_from_json_file(context)
        )
        if result is None:
            return {'CANCELLED'}

        created, lib_meta, source_mode, json_path, blend_path = result

        # Activate pack state
        from .pack_state import set_active_pack
        set_active_pack(
            name=lib_meta.get('library_name', 'Loaded Pack'),
            category=lib_meta.get('grid_category', GridCategory.OUTER_GRID),
            filepath=json_path,
            physical_size=float(lib_meta.get('physical_size',
                                             DEFAULT_GRID_SIZES[GridCategory.OUTER_GRID])),
            resolution_multiplier=int(lib_meta.get('resolution_multiplier', 1)),
            blend_filepath=blend_path,
            source_mode=source_mode,
        )

        connector_msg = self._activate_connectors(
            lib_meta,
            created=created,
            blend_path=blend_path,
        )

        bpy.ops.object.select_all(action='DESELECT')
        for obj in created:
            obj.select_set(True)
        if created:
            context.view_layer.objects.active = created[-1]

        self.report(
            {'INFO'},
            f"Loaded {len(created)} primitives from "
            f"'{lib_meta.get('library_name', 'pack')}'{connector_msg}",
        )
        return {'FINISHED'}

    # ── private path handlers ─────────────────────────────────────────────────

    def _load_from_json_file(self, context):
        """Handle a ``.json`` file selection.

        Returns ``(created, lib_meta, source_mode, json_path, blend_path)``
        or ``None`` on failure.
        """
        persistence = PrimitivePersistence()
        primitives_list, lib_meta, load_errors = persistence.load_primitive_library(
            self.filepath
        )
        for err in load_errors:
            self.report({'WARNING'}, err)

        # Hybrid pack: manifest points to a companion .blend for geometry
        blend_source = lib_meta.get('blend_source')
        if blend_source:
            from .primitive_persistence import resolve_blend_path
            blend_path = resolve_blend_path(self.filepath, blend_source)
            blend_collection = lib_meta.get('blend_collection') or \
                               _discover_blend_collection(blend_path)
            if not blend_collection:
                self.report(
                    {'ERROR'},
                    f"blend_source is set but blend_collection is unknown. "
                    f"Add 'blend_collection' to {self.filepath}",
                )
                return None
            category = lib_meta.get('grid_category', GridCategory.OUTER_GRID)
            created = _load_primitives_from_blend(self, blend_path, blend_collection, category)
            if created is None:
                return None
            return created, lib_meta, 'hybrid', self.filepath, blend_path

        # JSON-only pack: build objects from vertex data in the JSON
        if not primitives_list:
            self.report({'ERROR'}, "No primitives found in file")
            return None

        adapter = PrimitiveAdapter()
        created = []
        for prim_data in primitives_list:
            obj, _errors = adapter.create_blender_object_from_primitive(prim_data)
            if obj:
                from .collectiontools import ensure_primitives_collection
                col = ensure_primitives_collection(
                    prim_data.grid_category or GridCategory.OUTER_GRID
                )
                from .collectiontools.collection_creation import link_object_to_single_collection
                link_object_to_single_collection(obj, col)
                created.append(obj)

        if not created:
            self.report({'ERROR'}, "Failed to create any objects from pack")
            return None

        return created, lib_meta, 'json_only', self.filepath, None

    def _load_from_blend_file(self, context):
        """Handle a ``.blend`` file selection.

        Looks for a companion JSON manifest in the same directory to get
        metadata and connector registry.  Proceeds in geometry-only mode
        if no manifest is found.

        Returns ``(created, lib_meta, source_mode, json_path, blend_path)``
        or ``None`` on failure.
        """
        from .primitive_persistence import find_companion_json

        companion_json = find_companion_json(self.filepath)
        lib_meta  = {}
        json_path = None

        if companion_json:
            persistence = PrimitivePersistence()
            _, lib_meta, json_errors = persistence.load_primitive_library(companion_json)
            for err in json_errors:
                self.report({'WARNING'}, err)
            json_path = companion_json

        blend_collection = lib_meta.get('blend_collection') or \
                           _discover_blend_collection(self.filepath)
        if not blend_collection:
            self.report(
                {'ERROR'},
                "Cannot determine which collection to load. "
                "Create a companion pack.json with 'blend_collection' set, "
                "or ensure the blend file contains exactly one '*_Primitives' collection.",
            )
            return None

        category = lib_meta.get('grid_category', GridCategory.OUTER_GRID)
        created = _load_primitives_from_blend(
            self, self.filepath, blend_collection, category
        )
        if created is None:
            return None

        source_mode = 'hybrid' if companion_json else 'blend_only'
        return created, lib_meta, source_mode, json_path, self.filepath

    def _activate_connectors(self, lib_meta: dict, created=None, blend_path=None) -> str:
        """Activate the best available connector registry for the loaded pack.

        Resolution order:
        1. connector definitions embedded in the JSON manifest
        2. embedded ``wfc_connectors.json`` text inside the loaded ``.blend``
        3. placeholder connector definitions inferred from primitive object props
        4. the global default registry

        Returns a short suffix for the final operator info message.
        """
        from .connector_registry import (
            ConnectorRegistry, ConnectorDefinition,
            set_session_registry, clear_session_registry, connector_registry,
        )

        def _build_registry(connector_dicts):
            reg = ConnectorRegistry.__new__(ConnectorRegistry)
            reg.connectors = {}
            for cd in connector_dicts or []:
                try:
                    reg.register(ConnectorDefinition.from_dict(cd))
                except Exception:
                    pass
            return reg

        clear_session_registry()

        # 1) Exact registry from manifest JSON.
        manifest_connector_dicts = lib_meta.get('connectors') or []
        if manifest_connector_dicts:
            reg = _build_registry(manifest_connector_dicts)
            if reg.connectors:
                set_session_registry(reg)
                return f", {len(reg.connectors)} connectors activated"

        # 2) Embedded registry inside the .blend file.
        embedded_status = 'missing'
        if blend_path:
            embedded_connector_dicts, embedded_status = \
                _load_embedded_connector_dicts_from_blend(blend_path)
            if embedded_connector_dicts:
                reg = _build_registry(embedded_connector_dicts)
                if reg.connectors:
                    set_session_registry(reg)
                    return f", {len(reg.connectors)} connectors activated from embedded blend data"

        # 3) Infer placeholder connectors from the loaded primitive objects.
        inferred_connector_dicts = _infer_connector_dicts_from_objects(
            created or [],
            default_category=lib_meta.get('grid_category', GridCategory.OUTER_GRID),
        )
        missing_in_global = [
            cd for cd in inferred_connector_dicts
            if cd.get('name') not in connector_registry.connectors
        ]
        if missing_in_global:
            reg = ConnectorRegistry.__new__(ConnectorRegistry)
            reg.connectors = dict(connector_registry.connectors)
            added = 0
            for cd in missing_in_global:
                try:
                    reg.register(ConnectorDefinition.from_dict(cd))
                    added += 1
                except Exception:
                    pass
            if added:
                set_session_registry(reg)
                self.report(
                    {'WARNING'},
                    "Pack connector definitions were unavailable; "
                    f"added {added} inferred placeholder connector(s) from primitive metadata. "
                    "Review compatibility rules before generation.",
                )
                return f", {added} inferred connector placeholder(s) activated"

        # 4) Final fallback to the immutable global defaults.
        if embedded_status == 'malformed':
            self.report(
                {'WARNING'},
                "Embedded connector registry was present but could not be parsed; "
                "using the global connector registry.",
            )
        elif inferred_connector_dicts:
            self.report(
                {'WARNING'},
                "Pack-local connector definitions were unavailable, but all referenced connector names "
                "already exist in the global registry. Using the global connector registry.",
            )
        elif blend_path:
            self.report(
                {'WARNING'},
                "No pack-local connector definitions were found in the manifest, embedded blend data, "
                "or primitive metadata. Using the global connector registry.",
            )
        return ", using global connector registry"


class OBJECT_OT_WFCSavePack(bpy.types.Operator):
    """Save all complete primitives in the active pack to a JSON or .blend file"""
    bl_idname = "object.wfc_save_pack"
    bl_label = "Save Pack"
    bl_options = {'REGISTER'}

    filepath: StringProperty(subtype='FILE_PATH')  # type: ignore
    filter_glob: StringProperty(default="*.json;*.blend", options={'HIDDEN'})  # type: ignore

    def invoke(self, context, event):
        from .pack_state import get_active_pack
        pack = get_active_pack()
        if pack:
            # Prefer the blend filepath when we already have one
            pre = pack.get('blend_filepath') or pack.get('filepath') or ''
            if pre:
                self.filepath = pre
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    # ── public entry point ────────────────────────────────────────────────────

    def execute(self, context):
        from .pack_state import get_active_pack
        pack = get_active_pack()
        if not pack:
            self.report({'ERROR'}, "No active pack — create or load a pack first")
            return {'CANCELLED'}
        if not PERSISTENCE_AVAILABLE:
            self.report({'ERROR'}, "Persistence system unavailable")
            return {'CANCELLED'}

        ext = os.path.splitext(self.filepath)[1].lower()
        if ext == '.blend':
            return self._save_as_blend_file(context, pack)
        return self._save_as_json_file(context, pack)

    # ── JSON-only save (original path) ───────────────────────────────────────

    def _save_as_json_file(self, context, pack):
        from .pack_state import update_active_pack_filepath
        from .collectiontools import ensure_primitives_collection
        from .connector_registry import get_active_registry

        col = ensure_primitives_collection(pack['category'])
        adapter = PrimitiveAdapter()
        primitives, skipped = [], []
        for obj in col.objects:
            if obj.type != 'MESH':
                continue
            prim_data, errors = adapter.extract_primitive_from_blender(obj)
            if prim_data:
                primitives.append(prim_data)
            else:
                skipped.append(f"{obj.name}: {'; '.join(errors)}")

        if not primitives:
            self.report({'ERROR'}, "No complete primitives found — assign type and connectors first")
            return {'CANCELLED'}

        connector_dicts = [c.to_dict() for c in get_active_registry().connectors.values()]

        persistence = PrimitivePersistence()
        success, errors = persistence.save_primitive_library(
            primitives=primitives,
            filepath=self.filepath,
            library_name=pack['name'],
            connectors=connector_dicts,
            metadata={
                'grid_category': pack['category'],
                'physical_size': str(pack['physical_size']),
                'resolution_multiplier': str(pack['resolution_multiplier']),
                'author': 'WFC Addon',
                'version': '1.0',
            },
        )
        if success:
            update_active_pack_filepath(self.filepath)
            msg = f"Saved {len(primitives)} primitive(s)"
            if skipped:
                msg += f"  ({len(skipped)} incomplete skipped)"
            self.report({'INFO'}, msg)
            return {'FINISHED'}

        for err in errors:
            self.report({'ERROR'}, err)
        return {'CANCELLED'}

    # ── Hybrid blend+JSON save ────────────────────────────────────────────────

    def _save_as_blend_file(self, context, pack):
        """Export geometry to a ``.blend`` file and write a companion JSON manifest.

        Workflow
        --------
        1.  Collect every mesh primitive from the category's primitives collection.
        2.  Derive (or reuse) a stable ``blend_collection`` name via
            :func:`~primitive_persistence.slugify_collection_name`.
        3.  Create a temporary export collection, link all primitives into it.
        4.  Optionally embed the connector registry as a ``wfc_connectors.json``
            Text data-block in the blend file (Task 11).
        5.  Write the ``.blend`` file with
            :func:`bpy.data.libraries.write`, gathering all four data-block
            types explicitly (PoC finding).
        6.  Remove the temporary export collection and Text data-block.
        7.  Write the companion ``.json`` manifest next to the ``.blend`` file,
            using the same stem (``pack.blend`` → ``pack.json``).
        8.  Update active pack state to ``'hybrid'``.
        """
        import json as _json
        from .primitive_persistence import slugify_collection_name
        from .collectiontools import (
            ensure_primitives_collection,
            ensure_collection,
            link_object_to_single_collection,
        )
        from .connector_registry import get_active_registry
        from .pack_state import (
            update_active_pack_filepath,
            update_active_pack_blend_filepath,
        )

        # -- 1. Collect primitives ------------------------------------------------
        col = ensure_primitives_collection(pack['category'])
        objects = [o for o in col.objects if o.type == 'MESH']
        if not objects:
            self.report({'ERROR'}, "No mesh primitives found in the active pack collection")
            return {'CANCELLED'}

        # -- 2. Stable collection name -------------------------------------------
        # Re-use the name from an existing hybrid pack so that reloading after a
        # rename still finds the collection.
        existing_blend_path = pack.get('blend_filepath')
        blend_collection = None
        if existing_blend_path:
            # Try to find companion JSON for existing blend_collection
            from .primitive_persistence import find_companion_json, PrimitivePersistence as PP
            cj = find_companion_json(existing_blend_path)
            if cj:
                _, meta, _ = PP().load_primitive_library(cj)
                blend_collection = meta.get('blend_collection')
        if not blend_collection:
            blend_collection = slugify_collection_name(pack['name'])

        # -- 3. Temporary export collection --------------------------------------
        # Objects may live in multiple collections in Blender; linking them to a
        # temporary transport collection does not move them out of WFC_Primitives.
        export_col = bpy.data.collections.new(blend_collection)
        bpy.context.scene.collection.children.link(export_col)
        for obj in objects:
            export_col.objects.link(obj)

        # -- 4. Connector Text data-block (Task 11) ------------------------------
        reg = get_active_registry()
        connector_dicts = [c.to_dict() for c in reg.connectors.values()]
        text_block = None
        TEXT_NAME = "wfc_connectors.json"
        if connector_dicts:
            text_block = bpy.data.texts.get(TEXT_NAME) or bpy.data.texts.new(TEXT_NAME)
            text_block.clear()
            text_block.write(_json.dumps({'connectors': connector_dicts}, indent=2))

        # -- 5. Write blend file (MP-A2: pack external images for portability) ---
        all_mats  = [slot.material for obj in objects for slot in obj.material_slots]
        images    = _gather_images_from_materials(all_mats)

        # Temporarily pack any external images so they travel with the .blend.
        # We record which ones we packed so we can restore their state afterward.
        newly_packed = []
        for img in images:
            if not img.packed_file:   # only pack if not already embedded
                try:
                    img.pack()
                    newly_packed.append(img)
                except Exception:
                    pass              # skip unreadable / generated images

        datablocks: set = {export_col}
        for obj in objects:
            datablocks.add(obj)
            if obj.data:
                datablocks.add(obj.data)
            for slot in obj.material_slots:
                if slot.material:
                    datablocks.add(slot.material)
        for img in images:
            datablocks.add(img)
        if text_block:
            datablocks.add(text_block)

        try:
            bpy.data.libraries.write(self.filepath, datablocks, fake_user=False)
        except Exception as exc:
            self._restore_images(newly_packed)
            self._teardown_export_collection(export_col, text_block)
            self.report({'ERROR'}, f"Failed to write blend file: {exc}")
            return {'CANCELLED'}

        # -- 6. Teardown ---------------------------------------------------------
        self._restore_images(newly_packed)
        self._teardown_export_collection(export_col, text_block)

        # -- 7. Companion JSON manifest ------------------------------------------
        blend_filename = os.path.basename(self.filepath)
        json_path = os.path.splitext(self.filepath)[0] + '.json'

        persistence = PrimitivePersistence()
        success, json_errors = persistence.save_primitive_library(
            primitives=[],          # geometry lives in the blend file
            filepath=json_path,
            library_name=pack['name'],
            connectors=connector_dicts,
            blend_source=blend_filename,
            blend_collection=blend_collection,
            metadata={
                'grid_category': pack['category'],
                'physical_size': str(pack['physical_size']),
                'resolution_multiplier': str(pack['resolution_multiplier']),
                'author': 'WFC Addon',
                'version': '1.0',
            },
        )
        if not success:
            for err in json_errors:
                self.report({'WARNING'}, f"JSON manifest error: {err}")

        # -- 8. Update pack state ------------------------------------------------
        update_active_pack_filepath(json_path)
        update_active_pack_blend_filepath(self.filepath)

        # MP-A3: include image count in the report
        img_msg = f", {len(images)} image(s) bundled" if images else ""
        self.report(
            {'INFO'},
            f"Exported {len(objects)} primitive(s){img_msg}"
            f" → '{os.path.basename(self.filepath)}'"
            + (f" + '{os.path.basename(json_path)}'" if success else ""),
        )
        return {'FINISHED'}

    @staticmethod
    def _restore_images(newly_packed):
        """Unpack images that we temporarily packed for export."""
        for img in newly_packed:
            try:
                img.unpack(method='USE_LOCAL')
            except Exception:
                pass  # if the file no longer exists, leave it packed

    @staticmethod
    def _teardown_export_collection(export_col, text_block):
        """Unlink and remove the temporary export collection and Text data-block."""
        try:
            bpy.context.scene.collection.children.unlink(export_col)
        except Exception:
            pass
        bpy.data.collections.remove(export_col)
        if text_block:
            bpy.data.texts.remove(text_block)


class OBJECT_OT_WFCExportMaterials(bpy.types.Operator):
    """Export a standalone material library from the active pack.

    Gathers every unique material used by the active pack's primitives and
    writes them — along with any referenced image textures — to a
    ``materials.blend`` file.  The resulting file contains only materials and
    images (no geometry), making it a lightweight shared library that other
    packs can link against.

    External images are temporarily packed into Blender's memory before
    writing so the ``.blend`` is fully self-contained, then restored to their
    original state.
    """
    bl_idname  = "object.wfc_export_materials"
    bl_label   = "Export Materials"
    bl_options = {'REGISTER'}

    filepath:    StringProperty(subtype='FILE_PATH')  # type: ignore
    filter_glob: StringProperty(default="*.blend", options={'HIDDEN'})  # type: ignore

    def invoke(self, context, event):
        from .pack_state import get_active_pack
        pack = get_active_pack()
        if pack:
            # Suggest <pack folder>/materials.blend
            base = pack.get('blend_filepath') or pack.get('filepath') or ''
            folder = os.path.dirname(base) if base else ''
            self.filepath = os.path.join(folder, 'materials.blend')
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        from .pack_state import get_active_pack
        from .collectiontools import ensure_primitives_collection

        pack = get_active_pack()
        if not pack:
            self.report({'ERROR'}, "No active pack — load or create a pack first")
            return {'CANCELLED'}

        col = ensure_primitives_collection(pack['category'])
        objects = [o for o in col.objects if o.type == 'MESH']
        if not objects:
            self.report({'ERROR'}, "No mesh primitives found in the active pack")
            return {'CANCELLED'}

        # Gather unique materials
        all_mats = []
        seen_names = set()
        for obj in objects:
            for slot in obj.material_slots:
                if slot.material and slot.material.name not in seen_names:
                    seen_names.add(slot.material.name)
                    all_mats.append(slot.material)

        if not all_mats:
            self.report({'WARNING'}, "No materials found on pack primitives")
            return {'CANCELLED'}

        images = _gather_images_from_materials(all_mats)

        # Temporarily pack external images
        newly_packed = []
        for img in images:
            if not img.packed_file:
                try:
                    img.pack()
                    newly_packed.append(img)
                except Exception:
                    pass

        datablocks = set(all_mats) | set(images)

        try:
            bpy.data.libraries.write(self.filepath, datablocks, fake_user=False)
        except Exception as exc:
            OBJECT_OT_WFCSavePack._restore_images(newly_packed)
            self.report({'ERROR'}, f"Failed to write materials file: {exc}")
            return {'CANCELLED'}

        OBJECT_OT_WFCSavePack._restore_images(newly_packed)

        img_msg = f", {len(images)} image(s) bundled" if images else ""
        self.report(
            {'INFO'},
            f"Exported {len(all_mats)} material(s){img_msg}"
            f" → '{os.path.basename(self.filepath)}'",
        )
        return {'FINISHED'}


class OBJECT_OT_WFCMergePack(bpy.types.Operator):
    """Merge another JSON pack into the active pack.

    Loads the incoming pack's primitives and connectors and merges them with
    the active pack according to the selected conflict policy:

    Keep Active   — on any name collision, keep the active pack's version.
    Keep Incoming — on any name collision, replace with the incoming version.
    Keep Both     — rename the incoming primitive to avoid the collision
                    (connectors fall back to Keep Active when names conflict).

    Identical primitives / connectors are silently de-duplicated.
    Connectors whose only difference is ``compatible_with`` are auto-merged
    (union of both lists) regardless of the conflict policy.

    Note: only JSON packs are supported as the incoming source.  To merge a
    hybrid pack, load it into the scene first, save it as JSON, then merge.
    """
    bl_idname  = "object.wfc_merge_pack"
    bl_label   = "Merge Pack"
    bl_options = {'REGISTER', 'UNDO'}

    filepath:        StringProperty(subtype='FILE_PATH')  # type: ignore
    filter_glob:     StringProperty(default="*.json", options={'HIDDEN'})  # type: ignore
    conflict_policy: bpy.props.EnumProperty(  # type: ignore
        name="On Conflict",
        description="How to resolve name collisions between the two packs",
        items=[
            ('KEEP_ACTIVE',   "Keep Active",
             "Keep the active pack's version; discard the incoming one"),
            ('KEEP_INCOMING', "Keep Incoming",
             "Replace the active pack's version with the incoming one"),
            ('KEEP_BOTH',     "Keep Both",
             "Rename the incoming primitive (_2, _3, …) and include both"),
        ],
        default='KEEP_ACTIVE',
    )

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def draw(self, context):
        self.layout.prop(self, "conflict_policy")

    def execute(self, context):
        if not PERSISTENCE_AVAILABLE:
            self.report({'ERROR'}, "Persistence system unavailable")
            return {'CANCELLED'}

        from .pack_state import get_active_pack
        from .pack_merge import merge_packs
        from .connector_registry import (
            ConnectorRegistry, ConnectorDefinition, set_session_registry,
            get_active_registry,
        )
        from .collectiontools import ensure_primitives_collection
        from .collectiontools.collection_creation import link_object_to_single_collection

        pack = get_active_pack()
        if not pack:
            self.report({'ERROR'}, "No active pack — load or create a pack first")
            return {'CANCELLED'}

        # -- Load incoming pack --------------------------------------------------
        persistence = PrimitivePersistence()
        incoming_prims, incoming_meta, load_errors = persistence.load_primitive_library(
            self.filepath
        )
        for err in load_errors:
            self.report({'WARNING'}, err)

        incoming_category = incoming_meta.get('grid_category', '')
        if incoming_category and incoming_category != pack['category']:
            self.report(
                {'ERROR'},
                f"Category mismatch: active pack is '{pack['category']}' "
                f"but incoming pack is '{incoming_category}'. "
                "Only packs with the same grid category can be merged.",
            )
            return {'CANCELLED'}

        if not incoming_prims:
            self.report({'ERROR'}, "Incoming pack contains no primitives to merge")
            return {'CANCELLED'}

        # -- Build dicts for merge engine ----------------------------------------
        adapter = PrimitiveAdapter()
        col = ensure_primitives_collection(pack['category'])

        # Active primitives: extract PrimitiveData from the scene, convert to dict
        active_prim_dicts = []
        for obj in col.objects:
            if obj.type != 'MESH':
                continue
            pd, _ = adapter.extract_primitive_from_blender(obj)
            if pd:
                active_prim_dicts.append(pd.to_dict())

        incoming_prim_dicts = [p.to_dict() for p in incoming_prims]

        active_conn_dicts   = [
            c.to_dict() for c in get_active_registry().connectors.values()
        ]
        incoming_conn_dicts = incoming_meta.get('connectors', [])

        # -- Merge ---------------------------------------------------------------
        merged_prim_dicts, merged_conn_dicts, conflicts = merge_packs(
            active_prim_dicts,
            active_conn_dicts,
            incoming_prim_dicts,
            incoming_conn_dicts,
            self.conflict_policy,
        )

        # -- Apply: load only the NEW primitives into the scene ------------------
        active_names = {p['name'] for p in active_prim_dicts}
        added = 0
        for pd_dict in merged_prim_dicts:
            if pd_dict['name'] in active_names:
                continue  # already in the scene
            from .primitive_data_core import PrimitiveData
            pd = PrimitiveData.from_dict(pd_dict)
            obj, errors = adapter.create_blender_object_from_primitive(pd)
            if obj:
                link_object_to_single_collection(obj, col)
                added += 1

        # -- Apply: update session connector registry ----------------------------
        reg = ConnectorRegistry.__new__(ConnectorRegistry)
        reg.connectors = {}
        for cd in merged_conn_dicts:
            try:
                reg.register(ConnectorDefinition.from_dict(cd))
            except Exception:
                pass
        if reg.connectors:
            set_session_registry(reg)

        # -- Report --------------------------------------------------------------
        n_conflicts = len(conflicts)
        conflict_summary = ""
        if n_conflicts:
            resolutions = {}
            for c in conflicts:
                resolutions.setdefault(c.resolution, 0)
                resolutions[c.resolution] += 1
            parts = [f"{v} {k.replace('_', ' ')}" for k, v in resolutions.items()]
            conflict_summary = f" ({', '.join(parts)})"

        self.report(
            {'INFO'},
            f"Merged: +{added} primitive(s) from "
            f"'{incoming_meta.get('library_name', 'incoming pack')}'. "
            f"{n_conflicts} conflict(s){conflict_summary}.",
        )
        return {'FINISHED'}


class OBJECT_OT_WFCRenamePack(bpy.types.Operator):
    """Rename the active pack"""
    bl_idname = "object.wfc_rename_pack"
    bl_label = "Rename Pack"
    bl_options = {'REGISTER', 'UNDO'}

    new_name: StringProperty(name="New Name", default="")  # type: ignore

    def invoke(self, context, event):
        from .pack_state import get_active_pack
        pack = get_active_pack()
        self.new_name = pack['name'] if pack else ""
        return context.window_manager.invoke_props_dialog(self, width=300)

    def draw(self, context):
        self.layout.prop(self, "new_name")

    def execute(self, context):
        from .pack_state import get_active_pack, set_active_pack
        pack = get_active_pack()
        if not pack:
            self.report({'ERROR'}, "No active pack")
            return {'CANCELLED'}
        if not self.new_name.strip():
            self.report({'ERROR'}, "Name cannot be empty")
            return {'CANCELLED'}
        set_active_pack(
            name=self.new_name.strip(),
            category=pack['category'],
            filepath=pack.get('filepath'),
            physical_size=pack['physical_size'],
            resolution_multiplier=pack['resolution_multiplier'],
            # Preserve hybrid fields so renaming a pack never loses its .blend link
            blend_filepath=pack.get('blend_filepath'),
            source_mode=pack.get('source_mode', 'json_only'),
        )
        return {'FINISHED'}


# ============================================================================
# Primitive list operators (Stage 4 — P2-C)
# ============================================================================

class OBJECT_OT_WFCSelectPrimitive(bpy.types.Operator):
    """Select this primitive in the viewport"""
    bl_idname = "object.wfc_select_primitive"
    bl_label = "Select"
    bl_options = {'REGISTER', 'UNDO'}

    primitive_name: StringProperty()  # type: ignore

    def execute(self, context):
        obj = bpy.data.objects.get(self.primitive_name)
        if not obj:
            self.report({'ERROR'}, f"Object '{self.primitive_name}' not found")
            return {'CANCELLED'}
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj
        return {'FINISHED'}


class OBJECT_OT_WFCRenamePrimitive(bpy.types.Operator):
    """Rename this primitive"""
    bl_idname = "object.wfc_rename_primitive"
    bl_label = "Rename Primitive"
    bl_options = {'REGISTER', 'UNDO'}

    primitive_name: StringProperty()  # type: ignore
    new_name: StringProperty(name="New Name")  # type: ignore

    def invoke(self, context, event):
        self.new_name = self.primitive_name
        return context.window_manager.invoke_props_dialog(self, width=300)

    def draw(self, context):
        self.layout.prop(self, "new_name")

    def execute(self, context):
        if not self.new_name.strip():
            self.report({'ERROR'}, "Name cannot be empty")
            return {'CANCELLED'}
        obj = bpy.data.objects.get(self.primitive_name)
        if not obj:
            self.report({'ERROR'}, f"Object '{self.primitive_name}' not found")
            return {'CANCELLED'}
        obj.name = self.new_name.strip()
        if obj.data:
            obj.data.name = self.new_name.strip()
        return {'FINISHED'}


class OBJECT_OT_WFCDeletePrimitive(bpy.types.Operator):
    """Remove this primitive from the scene"""
    bl_idname = "object.wfc_delete_primitive"
    bl_label = "Delete Primitive"
    bl_options = {'REGISTER', 'UNDO'}

    primitive_name: StringProperty()  # type: ignore

    def execute(self, context):
        obj = bpy.data.objects.get(self.primitive_name)
        if not obj:
            self.report({'WARNING'}, f"Object '{self.primitive_name}' not found")
            return {'CANCELLED'}
        mesh = obj.data if obj.type == 'MESH' else None
        bpy.data.objects.remove(obj, do_unlink=True)
        if mesh and mesh.users == 0:
            bpy.data.meshes.remove(mesh)
        return {'FINISHED'}


class OBJECT_OT_WFCConvertToPrimitive(bpy.types.Operator):
    """[DEPRECATED] Print primitive data to console (use Save to JSON instead)"""
    bl_idname = "object.wfc_convert_to_primitive"
    bl_label = "Convert to Primitive (Deprecated)"

    def execute(self, context):
        obj = context.object

        if not obj:
            self.report({'ERROR'}, "No object selected")
            return {'CANCELLED'}

        if obj.type != 'MESH':
            self.report({'ERROR'}, "Selected object is not a mesh")
            return {'CANCELLED'}

        # Import old method for backward compatibility
        from .primitive_generation_tools import mesh_to_mesh_data

        self.report({'WARNING'}, "This operator is deprecated. Use 'Save to JSON' instead.")
        mesh_to_mesh_data(obj, print_debug=True)

        return {'FINISHED'}


# ============================================================================
# Registration
# ============================================================================

PRIMITIVE_OPERATORS = [
    # Primitive authoring
    OBJECT_OT_WFCAssignPrimitiveType,
    OBJECT_OT_WFCAssignConnectors,
    OBJECT_OT_WFCCopyConnectors,
    OBJECT_OT_WFCSavePrimitive,
    OBJECT_OT_WFCLoadPrimitive,
    # Pack management (Stage 4 — P2-B)
    OBJECT_OT_WFCNewPack,
    OBJECT_OT_WFCLoadPack,
    OBJECT_OT_WFCSavePack,
    OBJECT_OT_WFCRenamePack,
    OBJECT_OT_WFCMergePack,
    # Blend export / migration (Stage 7 — UX polish)
    OBJECT_OT_WFCExportToBlend,
    # Material pack (MP-B1)
    OBJECT_OT_WFCExportMaterials,
    # Primitive list actions (Stage 4 — P2-C)
    OBJECT_OT_WFCSelectPrimitive,
    OBJECT_OT_WFCRenamePrimitive,
    OBJECT_OT_WFCDeletePrimitive,
    # Connector registry management (Stage 5 — P3-A / P3-C)
    OBJECT_OT_WFCAddConnector,
    OBJECT_OT_WFCDeleteConnector,
    OBJECT_OT_WFCRenameConnector,
    # Deprecated
    OBJECT_OT_WFCConvertToPrimitive,
]

PRIMITIVE_PANELS = [
    OBJECT_PT_WFCPackPanel,                  # bl_order = 0 — appears first
    OBJECT_PT_WFCConnectorRegistryPanel,     # sub-panel of PackPanel
    OBJECT_PT_WFCPrimitiveBuilderPanel,      # bl_order = 1
]


# ============================================================================
# Legacy Support (from primitive_data_actual.py)
# ============================================================================

def build_default_primitives():
    """Build default hardcoded primitives (legacy support)"""
    return [
        building_primitive_alt(),
        corner_primitive_alt(),
        pavement_primitive_alt()
    ]

