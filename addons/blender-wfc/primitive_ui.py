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
from bpy.props import EnumProperty, StringProperty, FloatProperty, IntProperty, BoolProperty
from .wfc_enums import PRIMITIVE_TYPES, CUSTOM_PRIMITIVE_TYPES, get_connector_enum_items, GRID_CATEGORIES, PrimitiveDefinition
from .wfc_values import bl_category_name
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

class OBJECT_PT_WFCPrimitiveBuilderPanel(bpy.types.Panel):
    """Panel for creating and managing WFC primitives"""
    bl_label = "Primitive Builder"
    bl_idname = "OBJECT_PT_WFCPrimitiveBuilderPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = bl_category_name

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

        # Pre-populate connectors with existing values if assigned
        if obj and has_connectors_assigned(obj):
            self.pos_x = obj.x_pos_connector
            self.neg_x = obj.x_neg_connector
            self.pos_y = obj.y_pos_connector
            self.neg_y = obj.y_neg_connector

        # NEW: Pre-populate sizing and symmetry metadata (Task 3A.1 Step 3)
        if obj:
            self.physical_size = obj.physical_size
            self.grid_category = obj.grid_category
            self.resolution_multiplier = obj.resolution_multiplier
            self.rotation_invariant = obj.rotation_invariant

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
            implied = 8.0 / self.resolution_multiplier
            box.label(
                text=f"Physical size auto-set to {implied:.4g}m  (8m ÷ {self.resolution_multiplier})",
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
            obj.physical_size = 8.0 / self.resolution_multiplier
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
    OBJECT_OT_WFCAssignPrimitiveType,
    OBJECT_OT_WFCAssignConnectors,
    OBJECT_OT_WFCCopyConnectors,
    OBJECT_OT_WFCSavePrimitive,
    OBJECT_OT_WFCLoadPrimitive,
    OBJECT_OT_WFCConvertToPrimitive,  # Deprecated but kept for compatibility
]

PRIMITIVE_PANELS = [
    OBJECT_PT_WFCPrimitiveBuilderPanel
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

