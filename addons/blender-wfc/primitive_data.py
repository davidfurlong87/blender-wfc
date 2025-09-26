import bpy

from .wfc_classes import Primitive
from .wfc_materials import MaterialPrimitives
from enum import Enum
from .wfc_values import bl_category_name
from .primitive_generation_tools import mesh_to_mesh_data

class OBJECT_PT_WFCPrimitiveBuilderPanel(bpy.types.Panel):
    """Managing the creation of Primitive data"""
    bl_label = "Prim Gen"
    bl_idname = "OBJECT_PT_WFCPrimitiveBuilderPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = bl_category_name

    def draw(self, context):
        layout = self.layout
        # Var for primitives in scene
        # Import/export for primitives types/connectors/plot_definitions 
        obj = context.object
        if obj:
            
            # TODO: check in code or in object properties?   
            if obj.primitive_type and obj.primitive_type != 'NONE':
                layout.prop(obj, "primitive_type")
            else:
                row = layout.row()
                layout.operator("object.wfc_convert_to_primitive")

            # if connectors
                #     layout.prop(obj, "x_pos_connector")
                #     layout.prop(obj, "x_neg_connector")
                #     layout.prop(obj, "y_pos_connector")
                #     layout.prop(obj, "y_neg_connector")
            # else    
                # button to add connectors
                # layout.operator("object.connector")
                    # TODO: other conditional for unique plot groups
                    # TODO: Edit mode operator for adding vertex group to plots definition?
                        # TODO: for above, allow for selection from current plots, or to assign a new one
                    # TODO: Edit mode operator for adding vertex group (edge) to connectors
                        # TODO: for above, allow for selection from current connectors, or to assign a new one
            # else
                # layout.operator("object.primitive_establisher")                   

class OBJECT_OT_WFCAssignPrimitiveType(bpy.types.Operator):
    """Assigns a pre-existing WFC Primitive Type to Object"""
    bl_idname = "object.wfc_assign_primitive_type"
    bl_label = "Assign Primitive Type"

    
    def execute(self, context):

        # TODO: The below, or panel.redraw or whatever
        context.view_layer.update()

        return {'FINISHED'}

class OBJECT_OT_WFCConvertToPrimitive(bpy.types.Operator):
    """Takes User data and converts to a primitive"""
    bl_idname = "object.wfc_convert_to_primitive"
    bl_label = "Convert to primitive"

    def execute(self, context):
        obj = context.object
        # TODO: below should always be teh case when hitting this?
        if obj:
            # TODO: check if already in primitives?
            mesh_to_mesh_data(obj, print_debug = True)
        else:
            return {'ERROR'}
        return {'FINISHED'}


class OBJECT_OT_WFCPrimitiveBuilder(bpy.types.Operator):
    """Scan User Collection and Build Primitives from custom data"""
    bl_idname = "object.wfc_primitive_builder"
    bl_label = "Build from custom data"

    def execute(self, context):
        # If d_userprimitives == 0
            # return error
        # Check user data dictionary/list
        # if non-empty delete
        # clear_all_primitives()
        return {'FINISHED'}

class PrimitiveModules(Enum):
    Building = "Building_Primitive"
    Pavement = "Pavement_Primitive"
    Road = "Road_Primitive"
    Corner = "Corner_Primitive"

def build_default_primitives():
    return [
        building_primitive(),
        corner_primitive(),
        pavement_primitive()
        ]


def building_primitive():
    return Primitive(
        name=PrimitiveModules.Building.value,
        primitive_type="BUILDING",
        verts=[(-4.0, -4.0, -0.4), (-4.0, -4.0, 0.0), (-4.0, 4.0, -0.4), (-4.0, 4.0, 0.0), (4.0, -4.0, -0.4),
                (4.0, -4.0, 0.0), (4.0, 4.0, -0.4), (4.0, 4.0, 0.0)],
        faces=[(0, 1, 3, 2), (6, 7, 5, 4), (2, 3, 7, 6), (4, 5, 1, 0), (7, 3, 1, 5)],
        mat_indices=[0, 0, 0, 0, 0],
        material_names=[
            MaterialPrimitives.Building.value
        ],
        pos_x_connector = "BUILDING",
        neg_x_connector = "BUILDING",
        pos_y_connector = "BUILDING",
        neg_y_connector = "BUILDING"
    )

def corner_primitive():
    return Primitive(
        name=PrimitiveModules.Corner.value,
        primitive_type="CORNER",
        verts = [(4.0, -4.0, -0.2), (4.0, 4.0, -0.2), (0.0, -4.0, -0.2), (-4.0, -4.0, 0.0), (-4.0, 0.0, -0.2), (-4.0, 4.0, -0.2), (0.0, -4.0, 0.0), (0.0, 0.0, -0.2), (0.0, 0.0, 0.0), (-4.0, 0.0, 0.0), (-2.0, -4.0, 0.0), (-4.0, -2.0, 0.0), (-2.0, -2.0, 0.0)],
        faces = [(7, 4, 9, 8), (12, 11, 3, 10), (7, 2, 0, 1), (1, 5, 4, 7), (2, 7, 8, 6), (8, 12, 10, 6), (9, 11, 12, 8)],        mat_indices = [1, 2, 1, 1, 0, 0, 0],
        material_names = [
        MaterialPrimitives.Pavement.value,
        MaterialPrimitives.Road.value,
        MaterialPrimitives.Building.value
        ],
        pos_x_connector = "ROAD",
        neg_x_connector = "PAVEMENTPOS",
        pos_y_connector = "ROAD",
        neg_y_connector = "PAVEMENTNEG"
    )

def pavement_primitive():
    return Primitive(
        name=PrimitiveModules.Pavement.value,
        primitive_type="PAVEMENT",
        verts = [(4, -4, -0.4), (4, -4, -0.2), (4, 4, -0.4), (4, 4, -0.2), (0, 4, -0.2), (0, -4, -0.4), (0, -4, -0.2), (-4, -4, 0), (-4, 4, 0), (0, 4, 0), (0, -4, 0), (-2, -4, 0), (-2, 4, 0)],
        faces = [(2, 3, 1, 0), (6, 4, 9, 10), (3, 4, 6, 1), (0, 1, 6, 5), (12, 8, 7, 11), (9, 12, 11, 10)],
        
        mat_indices = [1, 0, 1, 1, 2, 0],

        material_names=[
            MaterialPrimitives.Pavement.value,
            MaterialPrimitives.Road.value,
            MaterialPrimitives.Building.value
        ],
        pos_x_connector = "ROAD",
        neg_x_connector = "BUILDING",
        pos_y_connector = "PAVEMENTPOS",
        neg_y_connector = "PAVEMENTNEG"
    )

PRIMITIVE_OPERATORS = [
    OBJECT_OT_WFCConvertToPrimitive,
    OBJECT_OT_WFCPrimitiveBuilder
]

PRIMITIVE_PANELS = [
    OBJECT_PT_WFCPrimitiveBuilderPanel
]
