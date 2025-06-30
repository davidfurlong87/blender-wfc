# # import bpy
# # import random
# # from bpy.props import BoolProperty, EnumProperty, StringProperty, FloatProperty
#
# # # from .collectiontools.collection_creation import build_or_return_collection
# # import wfc

#def add_wfc_debug_text(mesh):
    # objs = get_collection_objects_of_type(collection, 'MESH')

    # for aspect in aspects:
    #     bpy.ops.object.text_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    #     bpy.context.object.data.align_x = 'CENTER'
    #     text_obj = bpy.context.active_object
    #     text_obj.name = f"{mesh.name}_text_{aspect}"
    #     text_obj.data.body = f"{mesh.name}_text_{aspect}_db"
    #     text_obj.data.resolution_u = 2
    #     link_object_to_single_collection(text_obj, get_collection_by_name(CollectionNames.Primitives.value))

# # bl_category_name = "wfc"
# class OBJECT_OT_AddWfcText(bpy.types.Operator):
#     """Tooltip"""
#     bl_idname = "object.add_wfc_text"
#     bl_label = "add debug text"
#
#     def execute(self, context):
#         primitive_collection = get_collection_by_name(CollectionNames.Primitives.value)
#         old_text_objects = get_collection_objects_of_type(primitive_collection, 'FONT')
#         if len(old_text_objects) > 0:
#             # TODO: Delete data also
#             for text in old_text_objects:
#                 delete_object_by_name(text.name)
#         primitives = get_all_objects_from_collection(CollectionNames.Primitives.value)
#         if len(primitives) > 0:
#             for primitive in primitives:
#                 add_wfc_debug_text(primitive)
#
#         return {'FINISHED'}
#
#
# class OBJECT_OT_ClearWfcText(bpy.types.Operator):
#     """Tooltip"""
#     bl_idname = "object.clear_wfc_text"
#     bl_label = "clear debug text"
#
#     def execute(self, context):
#         primitive_collection = get_collection_by_name(CollectionNames.Primitives.value)
#         old_text_objects = get_collection_objects_of_type(primitive_collection, 'FONT')
#         if len(old_text_objects) > 0:
#             # TODO: Delete data also
#             for text in old_text_objects:
#                 delete_object_by_name(text.name)
#             # delete_objects_and_meshes(old_text_objects)
#
#         return {'FINISHED'}
#
# # class OBJECT_PT_BuildCollections(bpy.types.Panel):
# #     bl_label = "Build Collections"
# #     bl_idname = "OBJECT_PT_BuildCollections"
# #     bl_space_type = 'VIEW_3D'
# #     bl_region_type = 'UI'
# #     bl_category = bl_category_name
#
# #     def draw(self, context):
# #         layout = self.layout
# #         layout.prop(context.scene, "clear_collections")
# #         layout.operator("object.build_default_collections")
# # class OBJECT_OT_BuildDefaultCollections(bpy.types.Operator):
# #     """Tooltip"""
# #     bl_idname = "object.build_default_collections"
# #     bl_label = "build collections debug"
#
# # #    @classmethod
# # #    def poll(cls, context):
# # #        space = context.space_data
# # #        return space.type == 'NODE_EDITOR'
#
# #     def execute(self, context):
# #         prefix = "wfc_"
# #         collections_to_create = [
# #             'Grid',
# #             'Primitives',
# #             'Modules'
# #         ]
#
# #         default_collections = [build_or_return_collection(prefix + collection_to_create, True) for collection_to_create in collections_to_create]
#
# #         return {'FINISHED'}
#
#
# # COLLECTION_PANELS = [
# #     OBJECT_PT_BuildCollections,
# # ]
#
# # COLLECTION_OPERATORS = [
# #     OBJECT_OT_BuildDefaultCollections,
#
# # ]

# def mesh_to_mesh_data():

    # obj = bpy.context.active_object
    #
    # if obj and obj.type == 'MESH':
    #     mesh = obj.data
    #     #    mesh.calc_loop_triangles()  # Ensure triangulation if needed
    #
    #     verts = [v.co[:] for v in mesh.vertices]
    #     faces = [p.vertices[:] for p in mesh.polygons]
    #     mat_indices = [p.material_index for p in mesh.polygons]
    #     materials = [mat.name for mat in obj.data.materials if mat]
    #
    #     print(f"Verts, Faces and Materials for {obj.name}")
    #
    #     # Vertices
    #     print(f"verts = {verts}")
    #
    #     # Faces
    #     print(f"faces = {faces}")
    #
    #     # Materials
    #     for mat_name in materials:
    #         print(f"mat = bpy.data.materials.get('{mat_name}')")
    #         print("if not mat:")
    #         print(f"    mat = bpy.data.materials.new(name='{mat_name}')")
    #         print("mesh_obj.data.materials.append(mat)")
    #
    #     # Material indices per face
    #
    #     print("mat_indices = {}".format(mat_indices))
    #     print("for i, poly in enumerate(mesh_data.polygons):")
    #     print("    poly.material_index = mat_indices[i]")
    #
    #     # Mesh creation
    #     print("mesh_data.from_pydata(verts, [], faces)")
    #     print("mesh_data.update()")
    #
    # else:
    #     print("Please select a mesh object.")
