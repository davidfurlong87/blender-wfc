import bpy

remaining_modules_attribute_name = "remaining_modules"
debug_modules_mat_name = "debug_modules_mat"

def get_or_create_material(material_name):
    material = bpy.data.materials.get(material_name)
    if material:
        return material
    else:
        material = bpy.data.materials.new(name=material_name)
        material.use_nodes = True
        return material


def build_material(material_name, delete_existing=True):
    material = get_or_create_material(material_name)
    nodes = [node for node in material.node_tree.nodes]
    for node in nodes:
        material.node_tree.nodes.remove(node)

    object_attribute_node = material.node_tree.nodes.new('ShaderNodeAttribute')
    object_attribute_node.location = (-600, -000)
    object_attribute_node.attribute_type = 'INSTANCER'
    object_attribute_node.attribute_name = remaining_modules_attribute_name

    scene_attribute_node = material.node_tree.nodes.new("ShaderNodeValue")
    scene_attribute_node.location = (-600, -200)
    scene_attribute_node.label = "TotalModules"
    data_path = 'nodes["Value"].outputs[0].default_value'
    driver = material.node_tree.driver_add(data_path)
    driver.driver.type = 'SCRIPTED'
    driver.driver.expression = 'bpy.context.scene.total_modules'

    # var = driver.driver.variables.new()
    # var.name = 'scene_total_modules'
    # var.type = 'SINGLE_PROP'
    # target = var.targets[0]
    # target.id_type = 'SCENE'
    # target.id = bpy.data.scenes["Scene"]
    # target.data_path = "total_modules"

    divider_node = material.node_tree.nodes.new("ShaderNodeMath")
    divider_node.operation = 'DIVIDE'
    divider_node.location = (-350, -50)

    material.node_tree.links.new(object_attribute_node.outputs[2], divider_node.inputs[0])
    material.node_tree.links.new(scene_attribute_node.outputs[0], divider_node.inputs[1])

    subtract_node = material.node_tree.nodes.new("ShaderNodeMath")
    subtract_node.location = (-150, -50)
    subtract_node.operation = 'SUBTRACT'
    subtract_node.inputs[0].default_value = 1

    material.node_tree.links.new(divider_node.outputs[0], subtract_node.inputs[1])

    hsv_node = material.node_tree.nodes.new("ShaderNodeHueSaturation")
    hsv_node.location = (50, -50)
    hsv_node.inputs[0].default_value = 0.8
    hsv_node.inputs[4].default_value = (0, 0, 0.8, 1)

    material.node_tree.links.new(subtract_node.outputs[0], hsv_node.inputs["Fac"])

    diffuse_bsdf_node = material.node_tree.nodes.new('ShaderNodeBsdfDiffuse')
    diffuse_bsdf_node.location = (600, 0)
    diffuse_bsdf_node.inputs[0].default_value = (1, 0, 0, 1)

    material.node_tree.links.new(hsv_node.outputs[0], diffuse_bsdf_node.inputs["Color"])

    material_output = material.node_tree.nodes.new('ShaderNodeOutputMaterial')
    material_output.location = (800, 0)

    material.node_tree.links.new(diffuse_bsdf_node.outputs[0], material_output.inputs["Surface"])

    #    add1_node.hide = True
    #    add1_node.select = False

    bpy.context.object.active_material = material


build_material(debug_modules_mat_name)
