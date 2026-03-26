import bpy

# TODO: confirm these imports are in-line with the standards set in __init__.py. Confirm they'll correctly reload
from .wfc_enums import PRIMITIVE_TYPES, CUSTOM_PRIMITIVE_TYPES, CONNECTORS, PrimitiveModules, PrimitiveDefinition
from .wfc_classes import Primitive
from .wfc_materials import MaterialPrimitives
from enum import Enum
from .wfc_values import bl_category_name
from .primitive_generation_tools import get_primitive_type_items, mesh_to_mesh_data
from bpy.props import EnumProperty
from .primitive_data_actual import *

# TODO: confirm (or not) if this approach can successfully create a dynamic enum in operator contexts
def get_primitive_type_items(self, context):
    """Dynamic enum  items for primitive types"""
    items = PRIMITIVE_TYPES.copy()
    items.extend(CUSTOM_PRIMITIVE_TYPES)
    items.append(('CUSTOM', 'Custom', 'Create new custom primitive type'))

    return items


class OBJECT_PT_WFCPrimitiveBuilderPanel(bpy.types.Panel):
    """Managing the creation of Primitive data"""
    bl_label = "Prim Gen"
    bl_idname = "OBJECT_PT_WFCPrimitiveBuilderPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = bl_category_name

    def draw(self, context):
        layout = self.layout
        # TODO: somewhere in this panel there should be a management system for primitive types, connector types, plot types etc. Allow users to quickly create and delete their own.
        # TODO: Import/export/profile system for the above. The import could be a colleciton of types and their details. need to amend primitive types class to include grid resolution.


        # TODO: Var for total primitives in scene
        obj = context.object
        if obj:         
            row = layout.row()
            row.operator("object.wfc_convert_to_primitive")
            # TODO: align the below code with blender_adapter updates.
            if obj.primitive_type and obj.primitive_type != 'NONE':
                # i.e. is this object already added to primitives? If so, show the user the details.
                # TODO: align with blender adapter. 
                # TODO: the below should be read-only, unless the user forces an update
                # TODO: show warning if there's a discrepancy between this object and the blender adapter data.
                layout.prop(obj, "primitive_type")
            else:
                row = layout.row()
                row.operator("object.wfc_assign_primitive_type")
            # TODO: the below should be displayed if the user has already made this object a primitive. should be read-only, unless the user forces an update
            # if connectors
                #     layout.prop(obj, "x_pos_connector")
                #     layout.prop(obj, "x_neg_connector")
                #     layout.prop(obj, "y_pos_connector")
                #     layout.prop(obj, "y_neg_connector")
            # else    
            # TODO: some sort of error-handling here would be good. No connectors? Why not?
                # button to add connectors
                # layout.operator("object.connector")
                    # TODO: Edit mode operator for adding vertex group to plots definition? allow user to select faces/edges/verts and assign to a pre-configured vertex group (matching plots, or a generic form of them)
                        # TODO: for above, allow for selection from current plots, or to assign a new one
                    # TODO: Edit mode operator for adding vertex group (edge) to connectors
                        # TODO: for above, allow for selection from current connectors, or to assign a new one                 

class OBJECT_OT_WFCAssignPrimitiveType(bpy.types.Operator):
    """Assigns a pre-existing WFC Primitive Type to Object"""
    bl_idname = "object.wfc_assign_primitive_type"
    bl_label = "Assign Primitive Type"

# TODO: the idea here is to have a single source of truth for primitive types, defined elsewhere.
# TODO: when the user selects "Assign Primitive Type" they'll be presented with a drop-down box, from which they can select their primitive type and assign it to this object.
# TODO: another solution might be to have a drop-down box on the panel at all times. user selects object -> selects type from box -> hits "assign"
# TODO: regardless of solution, all relevant components in the adapter/algorithm must be updated, maintaining a single source of truth
    prim_type: EnumProperty(
        name="Primitive Type",
        description="Select primitive type to assign",
        items=get_primitive_type_items,
    ) # type: ignore

# TODO: could be replaced with the primitive management system above.
    custom_type_name: bpy.props.StringProperty(
        name="Custom Type Name",
        description="Name for new custom primitive type",
        default="New_Primitive"
    ) # type: ignore

    def invoke(self, context, event):
        # This shows the operator properties in a popup dialog
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "prim_type")
        
        # Show custom name field when custom is selected
        if self.prim_type == 'CUSTOM':
            layout.prop(self, "custom_type_name")

    def execute(self, context):
        mesh_obj = context.object
        if not mesh_obj:
            self.report({'ERROR'}, "No object selected")
            return {'CANCELLED'}          
        if self.prim_type == 'CUSTOM':
            if not self.custom_type_name.strip():
                self.report({'ERROR'}, "Custom type name cannot be empty")
                return {'CANCELLED'}
            
            clean_name = self.custom_type_name.strip().upper().replace(' ', '_')
            new_primitive_def = PrimitiveDefinition(clean_name)
            new_enum_item = new_primitive_def.as_blender_enum()

            # Check if it already exists
            if new_enum_item not in CUSTOM_PRIMITIVE_TYPES:
                CUSTOM_PRIMITIVE_TYPES.append(new_enum_item)

            mesh_obj.primitive_type = clean_name

            self.report({'INFO'}, f"Created and assigned custom primitive type: {clean_name}")
        else:
            # Assign the selected primitive type
            mesh_obj.primitive_type = self.prim_type
            self.report({'INFO'}, f"Assigned primitive type: {self.prim_type}")
    
        context.view_layer.update()
        return {'FINISHED'}

class OBJECT_OT_WFCConvertToPrimitive(bpy.types.Operator):
    """Takes User data and converts to a primitive"""
    bl_idname = "object.wfc_convert_to_primitive"
    bl_label = "Convert to primitive"

    # def invoke(self, context):
    #     obj = context.object
    #     if obj:  
    #         return {True}
    #     else:
    #         return False
    
    def execute(self, context):
        obj = context.object
        # TODO: below should always be the case when hitting this?
        if obj:
            mesh_to_mesh_data(obj, print_debug = True)
        else:
            return {'ERROR'}
        return {'FINISHED'}


# class PrimitiveModules(Enum):
#     Building = "Building_Primitive"
#     Pavement = "Pavement_Primitive"
#     Road = "Road_Primitive"
#     Corner = "Corner_Primitive"

def build_default_primitives():
    # return [
    #     building_primitive(),
    #     corner_primitive(),
    #     pavement_primitive()
    #     ]
    return [
        building_primitive_alt(),
        corner_primitive_alt(),
        pavement_primitive_alt()
    ]


PRIMITIVE_OPERATORS = [
    OBJECT_OT_WFCConvertToPrimitive,
    OBJECT_OT_WFCAssignPrimitiveType
    ]

PRIMITIVE_PANELS = [
    OBJECT_PT_WFCPrimitiveBuilderPanel
]
