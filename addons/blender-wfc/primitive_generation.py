# import bpy
# from enum import Enum
# from .wfc_values import module_size
#
#
# class Primitive:
#     def __init__(self, name, verts, faces, mat_indices, material_names):
#         self.name = name
#         self.verts = verts
#         self.faces = faces
#         self.mat_indices = mat_indices
#         self.material_names = material_names
#
#
# class MaterialPrimitives(Enum):
#     Building = "Building_Primitive"
#     Pavement = "Pavement_Primitive"
#     Road = "Road_Primitive"
#
#
# class PrimitiveModules(Enum):
#     Building = "Building_Primitive"
#     Pavement = "Pavement_Primitive"
#     Road = "Road_Primitive"
#
#
# def build_all_primitives(primitives_collection):
#     for material_name in [
#         MaterialPrimitives.Building.value,
#         MaterialPrimitives.Pavement.value,
#         MaterialPrimitives.Road.value
#     ]:
#         match material_name:
#             case MaterialPrimitives.Building.value:
#                 build_primitive_material(material_name, (0.8, 0.4, 0.2, 1.0))
#             case MaterialPrimitives.Pavement.value:
#                 build_primitive_material(material_name, (0.1, 0.4, 0.8, 1.0))
#             case MaterialPrimitives.Road.value:
#                 build_primitive_material(material_name, (0.05, 0.05, 0.05, 1.0))
#             case default:
#                 build_primitive_material("failure", (0.0, 0.0, 0.0, 1.0))
#
#         # material = bpy.data.materials.get(material_name)
#         # if not material:
#         #     build_primitive_material(name=material_name, color=)
#         #     mat = bpy.data.materials.new(name=material_name)
#
#     building_primitive = Primitive(
#         name=PrimitiveModules.Building.value,
#         verts=[(-4.0, -4.0, -0.4), (-4.0, -4.0, 0.0), (-4.0, 4.0, -0.4), (-4.0, 4.0, 0.0), (4.0, -4.0, -0.4),
#                (4.0, -4.0, 0.0), (4.0, 4.0, -0.4), (4.0, 4.0, 0.0)],
#         faces=[(0, 1, 3, 2), (6, 7, 5, 4), (2, 3, 7, 6), (4, 5, 1, 0), (7, 3, 1, 5)],
#         mat_indices=[0, 0, 0, 0, 0],
#         material_names=[
#             MaterialPrimitives.Building.value
#         ]
#     )
#
#     pavement_primitive = Primitive(
#         name=PrimitiveModules.Pavement.value,
#         verts=[(-4.0, -4.0, -0.4), (-4.0, -4.0, -0.2), (-4.0, 4.0, -0.4), (-4.0, 4.0, -0.2), (4.0, -4.0, -0.4),
#                (4.0, -4.0, -0.2), (4.0, 4.0, -0.4), (4.0, 4.0, -0.2), (0.0, 4.0, -0.4), (0.0, 4.0, -0.2),
#                (0.0, -4.0, -0.4), (0.0, -4.0, -0.2), (-4.0, -4.0, 0.0), (-4.0, 4.0, 0.0),
#                (0.0, 4.0, 0.0), (0.0, -4.0, 0.0)],
#         faces=[(0, 1, 3, 2), (6, 7, 5, 4), (8, 9, 7, 6), (11, 15, 12, 1), (11, 9, 14, 15), (7, 9, 11, 5),
#                (4, 5, 11, 10),
#                (2, 3, 9, 8), (14, 13, 12, 15), (3, 1, 12, 13), (9, 3, 13, 14), (10, 11, 1, 0)],
#         mat_indices=[0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0],
#         material_names=[
#             MaterialPrimitives.Pavement.value,
#             MaterialPrimitives.Road.value
#         ]
#     )
#
#     road_primitive = Primitive(
#         name=PrimitiveModules.Road.value,
#         verts=[(-4.0, -4.0, -0.4), (-4.0, -4.0, -0.2), (-4.0, 4.0, -0.4), (-4.0, 4.0, -0.2), (4.0, -4.0, -0.4),
#                (4.0, -4.0, -0.2), (4.0, 4.0, -0.4), (4.0, 4.0, -0.2)],
#         faces=[(0, 1, 3, 2), (6, 7, 5, 4), (2, 3, 7, 6), (4, 5, 1, 0), (2, 6, 4, 0), (7, 3, 1, 5)],
#         mat_indices=[0, 0, 0, 0, 0, 0],
#         material_names=[
#             MaterialPrimitives.Road.value
#         ]
#     )
#
#     for i, primitive in enumerate([building_primitive, pavement_primitive, road_primitive]):
#         build_primitives(primitive, primitives_collection,
#                          location=(i * (module_size * 2), i * (module_size * 0), 0))
#
#
# def build_primitives(primitive, primitives_collection, location):
#     mesh_data = bpy.data.meshes.new(name=primitive.name)
#     mesh_obj = bpy.data.objects.new(primitive.name, mesh_data)
#     mesh_obj.location = location
#     primitives_collection.objects.link(mesh_obj)
#
#     mesh_data.from_pydata(primitive.verts, [], primitive.faces)
#     mesh_data.update()
#
#     for material_name in primitive.material_names:
#         mesh_obj.data.materials.append(bpy.data.materials.get(material_name))
#
#     for i, poly in enumerate(mesh_data.polygons):
#         poly.material_index = primitive.mat_indices[i]
#
# def build_primitive_material(material_name, colour=(0.8, 0.4, 0.2, 1.0)):
#     old_material = bpy.data.materials.get(material_name)
#     if not old_material:
#         mat = bpy.data.materials.new(name=material_name)
#         mat.use_nodes = True
#
#         # Clear default nodes
#         nodes = mat.node_tree.nodes
#         nodes.clear()
#
#         # Add Diffuse BSDF and Material Output nodes
#         diffuse_node = nodes.new(type="ShaderNodeBsdfDiffuse")
#         output_node = nodes.new(type="ShaderNodeOutputMaterial")
#
#         # Set the color
#         diffuse_node.inputs['Color'].default_value = colour
#
#         # Link Diffuse to Output
#         mat.node_tree.links.new(diffuse_node.outputs['BSDF'], output_node.inputs['Surface'])
#
#         # Enable backface culling
#         mat.use_backface_culling = True
