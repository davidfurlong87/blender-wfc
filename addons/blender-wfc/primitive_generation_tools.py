import bpy

from .wfc_enums import PRIMITIVE_TYPES, CUSTOM_PRIMITIVE_TYPES, CONNECTORS

def get_primitive_type_items(self, context):
    """Dynamic enum  items for primitive types"""
    # TODO: Key = whatever will sort this alphabetically
    return PRIMITIVE_TYPES + CUSTOM_PRIMITIVE_TYPES


def mesh_to_mesh_data(obj, print_debug = False):

    # obj = bpy.context.active_object

    if obj and obj.type == 'MESH':
        mesh = obj.data
        # TODO: round the decimals
        verts = [v.co[:] for v in mesh.vertices]
        faces = [p.vertices[:] for p in mesh.polygons]
        mat_indices = [p.material_index for p in mesh.polygons]
        materials = [mat.name for mat in obj.data.materials if mat]

        # vertex_groups = obj.vertex_groups
        vertex_group_data = capture_vertex_groups(obj)

        if print_debug:
            print(f"Verts, Faces, Materials and Vertex Groups for {obj.name}")
            print(f"verts = {verts},")
            print(f"faces = {faces},")
            print(f"materials = {materials},")
            print(f"mat_indices = {mat_indices},")
            print(f"vertex_groups = {vertex_group_data}")
        return {
            'verts': verts,
            'faces': faces,
            'materials': materials,
            'mat_indices': mat_indices,
            'vertex_groups': vertex_group_data
        }
    else:
        print("Please select a mesh object.")
        return None

def capture_vertex_groups(obj):
    """Capture vertex group data from an object"""
    vertex_group_data = {}
    
    # loop through all the objects vertex groups
    for vertex_group in obj.vertex_groups:
        vertex_indices = []
        vertex_weights = []
        
        # loop through all vertices in obj data
        for vert_index, vertex in enumerate(obj.data.vertices):
            # Check if this vertex is in the vertex group

            # Loop through that vertex's assigned groups
            for group in vertex.groups:
                # If the index of a particular assigned groupd matches the current overall vgroup we're looping on...
                if group.group == vertex_group.index:
                    vertex_indices.append(vert_index)
                    vertex_weights.append(group.weight)
                    break
        
        vertex_group_data[vertex_group.name] = {
            'vertices': vertex_indices,
            'weights': vertex_weights
        }

    return vertex_group_data

def apply_vertex_groups_to_object(obj, vertex_group_data):
    """Apply vertex group data to a new object"""
    # Clear existing vertex groups
    obj.vertex_groups.clear()
    
    # Recreate vertex groups
    for group_name, group_data in vertex_group_data.items():
        # Create the vertex group
        vertex_group = obj.vertex_groups.new(name=group_name)
        
        # Add vertices to the group with their weights
        for vert_index, weight in zip(group_data['vertices'], group_data['weights']):
            vertex_group.add([vert_index], weight, 'REPLACE')
