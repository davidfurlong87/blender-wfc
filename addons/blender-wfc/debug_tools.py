

def mesh_to_mesh_data():

    obj = bpy.context.active_object

    if obj and obj.type == 'MESH':
        mesh = obj.data
        #    mesh.calc_loop_triangles()  # Ensure triangulation if needed

        verts = [v.co[:] for v in mesh.vertices]
        faces = [p.vertices[:] for p in mesh.polygons]
        mat_indices = [p.material_index for p in mesh.polygons]
        materials = [mat.name for mat in obj.data.materials if mat]

        print(f"Verts, Faces and Materials for {obj.name}")

        # Vertices
        print(f"verts = {verts}")

        # Faces
        print(f"faces = {faces}")

        # Materials
        for mat_name in materials:
            print(f"mat = bpy.data.materials.get('{mat_name}')")
            print("if not mat:")
            print(f"    mat = bpy.data.materials.new(name='{mat_name}')")
            print("mesh_obj.data.materials.append(mat)")

        # Material indices per face

        print("mat_indices = {}".format(mat_indices))
        print("for i, poly in enumerate(mesh_data.polygons):")
        print("    poly.material_index = mat_indices[i]")

        # Mesh creation
        print("mesh_data.from_pydata(verts, [], faces)")
        print("mesh_data.update()")

    else:
        print("Please select a mesh object.")
