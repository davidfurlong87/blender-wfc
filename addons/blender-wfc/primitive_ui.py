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
from bpy.props import EnumProperty, StringProperty
from .wfc_enums import PRIMITIVE_TYPES, CUSTOM_PRIMITIVE_TYPES, CONNECTORS, PrimitiveDefinition
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
        
        # Check if object is valid
        # TODO: this check skips the 'always available' load from json method below when no object is selected. with no obj here, the user has no way of loading from json
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
                
                box.operator("object.wfc_assign_connectors", text="Edit Connectors", icon='EDITMODE_HLT')
            else:
                box.label(text="No connectors assigned", icon='INFO')
                box.operator("object.wfc_assign_connectors", text="Assign Connectors", icon='ADD')
        
        # Section 3: Persistence (only if persistence system available)
        if PERSISTENCE_AVAILABLE and is_primitive_complete(obj):
            box = layout.box()
            box.label(text="Save/Load:", icon='FILE')
            box.operator("object.wfc_save_primitive", text="Save to JSON", icon='EXPORT')
        
        # Section 4: Load (always available)
        # TODO: make always available? At the moment a primitive can only be loaded if an object in the scene is se
        if PERSISTENCE_AVAILABLE:
            layout.operator("object.wfc_load_primitive", text="Load from JSON", icon='IMPORT')
        
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

            clean_name = self.custom_type_name.strip().upper().replace(' ', '_')
            new_primitive_def = PrimitiveDefinition(clean_name)
            new_enum_item = new_primitive_def.as_blender_enum()

            if new_enum_item not in CUSTOM_PRIMITIVE_TYPES:
                CUSTOM_PRIMITIVE_TYPES.append(new_enum_item)

            obj.primitive_type = clean_name
            self.report({'INFO'}, f"Created and assigned custom primitive type: {clean_name}")
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
        items=CONNECTORS,
        default='ROAD'
    ) # type: ignore

    neg_x: EnumProperty(
        name="-X Connector",
        description="Connector on negative X face",
        items=CONNECTORS,
        default='ROAD'
    ) # type: ignore

    pos_y: EnumProperty(
        name="+Y Connector",
        description="Connector on positive Y face",
        items=CONNECTORS,
        default='ROAD'
    ) # type: ignore

    neg_y: EnumProperty(
        name="-Y Connector",
        description="Connector on negative Y face",
        items=CONNECTORS,
        default='ROAD'
    ) # type: ignore

    def invoke(self, context, event):
        obj = context.object

        # Pre-populate with existing values if they exist
        if obj and has_connectors_assigned(obj):
            self.pos_x = obj.x_pos_connector
            self.neg_x = obj.x_neg_connector
            self.pos_y = obj.y_pos_connector
            self.neg_y = obj.y_neg_connector

        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "pos_x")
        layout.prop(self, "neg_x")
        layout.prop(self, "pos_y")
        layout.prop(self, "neg_y")

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

        self.report({'INFO'}, f"Assigned connectors to {obj.name}")
        context.view_layer.update()
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
            # Load from file using persistence
            persistence = PrimitivePersistence()
            primitive_data, load_errors = persistence.load_primitive_from_file(self.filepath)

            if load_errors:
                for err in load_errors:
                    self.report({'WARNING'}, err)

            if not primitive_data:
                self.report({'ERROR'}, "Failed to load primitive data")
                return {'CANCELLED'}

            # Create Blender object using adapter
            adapter = PrimitiveAdapter()
            new_obj, create_errors = adapter.create_blender_object_from_primitive(
                primitive_data,
                collection=context.scene.collection,
                location=context.scene.cursor.location
            )

            if create_errors:
                for err in create_errors:
                    self.report({'WARNING'}, err)

            if new_obj:
                # Select the new object
                bpy.ops.object.select_all(action='DESELECT')
                new_obj.select_set(True)
                context.view_layer.objects.active = new_obj

                self.report({'INFO'}, f"Loaded primitive: {new_obj.name}")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "Failed to create object from primitive")
                return {'CANCELLED'}

        except Exception as e:
            self.report({'ERROR'}, f"Unexpected error: {str(e)}")
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

