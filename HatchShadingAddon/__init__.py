bl_info = {
    "name" : "Hatch Addon",
    "author" : "CGBlender", 
    "description" : "Hatch addon is a blender addon that will help you to create hatching Npr materials shaders in Blender easily with one click, this addon has a material library that will help you to make 3D comics renderings or art concept art, or 3D Animation...",
    "blender" : (3, 0, 0),
    "version" : (1, 0, 0),
    "location" : "",
    "waring" : "",
    "doc_url": "", 
    "tracker_url": "", 
    "category" : "3D View" 
}


import bpy
import bpy.utils.previews

import bpy
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os


def string_to_int(value):
    if value.isdigit():
        return int(value)
    return 0

def string_to_icon(value):
    if value in bpy.types.UILayout.bl_rna.functions["prop"].parameters["icon"].enum_items.keys():
        return bpy.types.UILayout.bl_rna.functions["prop"].parameters["icon"].enum_items[value].value
    return string_to_int(value)
    
def icon_to_string(value):
    for icon in bpy.types.UILayout.bl_rna.functions["prop"].parameters["icon"].enum_items:
        if icon.value == value:
            return icon.name
    return "NONE"
    
def enum_set_to_string(value):
    if type(value) == set:
        if len(value) > 0:
            return "[" + (", ").join(list(value)) + "]"
        return "[]"
    return value
    
def string_to_type(value, to_type, default):
    try:
        value = to_type(value)
    except:
        value = default
    return value

addon_keymaps = {}
_icons = None
hatch_addon = {}


def sna_update_sna_manganpr_4FEA5(self, context):
    sna_updated_prop = self.sna_manganpr
    ob = bpy.context.active_object
    # Get material
    mat = bpy.data.materials.get("Material")
    if mat is None:
        # create material
        mat = bpy.data.materials.new(name="Material")
    # Assign it to object
    if ob.data.materials:
        # assign to 1st material slot
        ob.data.materials[0] = mat
    else:
        # no slots
        ob.data.materials.append(mat)
    if property_exists("bpy.data.materials[sna_updated_prop]"):
        pass
    else:
        bpy.ops.wm.append(directory=os.path.join(os.path.dirname(__file__), 'assets', 'mangaNPR.blend') + r'\Material', filename=sna_updated_prop, link=False)
        bpy.ops.wm.append(directory=os.path.join(os.path.dirname(__file__), 'assets', 'mangaNPR.blend') + r'\Material', filename='mout', link=False)
        bpy.context.view_layer.objects.active.select_set(state=True, )
    bpy.context.view_layer.objects.active.material_slots[0].material = bpy.data.materials[sna_updated_prop]
def property_exists(prop_path):
    try:
        eval(prop_path)
        return True
    except:
        return False
_item_map = dict()
def make_enum_item(_id, name, descr, preview_id, uid):
    lookup = str(_id)+"\0"+str(name)+"\0"+str(descr)+"\0"+str(preview_id)+"\0"+str(uid)
    if not lookup in _item_map:
        _item_map[lookup] = (_id, name, descr, preview_id, uid)
    return _item_map[lookup]
def load_preview_icon(path):
    global _icons
    if not path in _icons:
        if os.path.exists(path):
            _icons.load(path, path, "IMAGE")
        else:
            return 0
    return _icons[path].icon_id
def load_preview_icon(path):
    global _icons
    if not path in _icons:
        if os.path.exists(path):
            _icons.load(path, path, "IMAGE")
        else:
            return 0
    return _icons[path].icon_id
def load_preview_icon(path):
    global _icons
    if not path in _icons:
        if os.path.exists(path):
            _icons.load(path, path, "IMAGE")
        else:
            return 0
    return _icons[path].icon_id
def load_preview_icon(path):
    global _icons
    if not path in _icons:
        if os.path.exists(path):
            _icons.load(path, path, "IMAGE")
        else:
            return 0
    return _icons[path].icon_id
def load_preview_icon(path):
    global _icons
    if not path in _icons:
        if os.path.exists(path):
            _icons.load(path, path, "IMAGE")
        else:
            return 0
    return _icons[path].icon_id
def load_preview_icon(path):
    global _icons
    if not path in _icons:
        if os.path.exists(path):
            _icons.load(path, path, "IMAGE")
        else:
            return 0
    return _icons[path].icon_id
def load_preview_icon(path):
    global _icons
    if not path in _icons:
        if os.path.exists(path):
            _icons.load(path, path, "IMAGE")
        else:
            return 0
    return _icons[path].icon_id
def load_preview_icon(path):
    global _icons
    if not path in _icons:
        if os.path.exists(path):
            _icons.load(path, path, "IMAGE")
        else:
            return 0
    return _icons[path].icon_id
def load_preview_icon(path):
    global _icons
    if not path in _icons:
        if os.path.exists(path):
            _icons.load(path, path, "IMAGE")
        else:
            return 0
    return _icons[path].icon_id
def load_preview_icon(path):
    global _icons
    if not path in _icons:
        if os.path.exists(path):
            _icons.load(path, path, "IMAGE")
        else:
            return 0
    return _icons[path].icon_id
def load_preview_icon(path):
    global _icons
    if not path in _icons:
        if os.path.exists(path):
            _icons.load(path, path, "IMAGE")
        else:
            return 0
    return _icons[path].icon_id
def load_preview_icon(path):
    global _icons
    if not path in _icons:
        if os.path.exists(path):
            _icons.load(path, path, "IMAGE")
        else:
            return 0
    return _icons[path].icon_id
def load_preview_icon(path):
    global _icons
    if not path in _icons:
        if os.path.exists(path):
            _icons.load(path, path, "IMAGE")
        else:
            return 0
    return _icons[path].icon_id
def load_preview_icon(path):
    global _icons
    if not path in _icons:
        if os.path.exists(path):
            _icons.load(path, path, "IMAGE")
        else:
            return 0
    return _icons[path].icon_id
def load_preview_icon(path):
    global _icons
    if not path in _icons:
        if os.path.exists(path):
            _icons.load(path, path, "IMAGE")
        else:
            return 0
    return _icons[path].icon_id
def load_preview_icon(path):
    global _icons
    if not path in _icons:
        if os.path.exists(path):
            _icons.load(path, path, "IMAGE")
        else:
            return 0
    return _icons[path].icon_id
def load_preview_icon(path):
    global _icons
    if not path in _icons:
        if os.path.exists(path):
            _icons.load(path, path, "IMAGE")
        else:
            return 0
    return _icons[path].icon_id
def load_preview_icon(path):
    global _icons
    if not path in _icons:
        if os.path.exists(path):
            _icons.load(path, path, "IMAGE")
        else:
            return 0
    return _icons[path].icon_id
def load_preview_icon(path):
    global _icons
    if not path in _icons:
        if os.path.exists(path):
            _icons.load(path, path, "IMAGE")
        else:
            return 0
    return _icons[path].icon_id
def load_preview_icon(path):
    global _icons
    if not path in _icons:
        if os.path.exists(path):
            _icons.load(path, path, "IMAGE")
        else:
            return 0
    return _icons[path].icon_id
def load_preview_icon(path):
    global _icons
    if not path in _icons:
        if os.path.exists(path):
            _icons.load(path, path, "IMAGE")
        else:
            return 0
    return _icons[path].icon_id
def load_preview_icon(path):
    global _icons
    if not path in _icons:
        if os.path.exists(path):
            _icons.load(path, path, "IMAGE")
        else:
            return 0
    return _icons[path].icon_id
def load_preview_icon(path):
    global _icons
    if not path in _icons:
        if os.path.exists(path):
            _icons.load(path, path, "IMAGE")
        else:
            return 0
    return _icons[path].icon_id
def load_preview_icon(path):
    global _icons
    if not path in _icons:
        if os.path.exists(path):
            _icons.load(path, path, "IMAGE")
        else:
            return 0
    return _icons[path].icon_id
def load_preview_icon(path):
    global _icons
    if not path in _icons:
        if os.path.exists(path):
            _icons.load(path, path, "IMAGE")
        else:
            return 0
    return _icons[path].icon_id
def load_preview_icon(path):
    global _icons
    if not path in _icons:
        if os.path.exists(path):
            _icons.load(path, path, "IMAGE")
        else:
            return 0
    return _icons[path].icon_id
def load_preview_icon(path):
    global _icons
    if not path in _icons:
        if os.path.exists(path):
            _icons.load(path, path, "IMAGE")
        else:
            return 0
    return _icons[path].icon_id
def load_preview_icon(path):
    global _icons
    if not path in _icons:
        if os.path.exists(path):
            _icons.load(path, path, "IMAGE")
        else:
            return 0
    return _icons[path].icon_id
def load_preview_icon(path):
    global _icons
    if not path in _icons:
        if os.path.exists(path):
            _icons.load(path, path, "IMAGE")
        else:
            return 0
    return _icons[path].icon_id

class SNA_PT_LINEDER_61656(bpy.types.Panel):
    bl_label = 'lineder'
    bl_idname = 'SNA_PT_LINEDER_61656'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = ''
    bl_category = 'LNR'
    bl_order = 0
    
    
    @classmethod
    def poll(cls, context):
        return not (False)
    
    def draw_header(self, context):
        layout = self.layout
        
    def draw(self, context):
        layout = self.layout
        layout.template_icon_view(bpy.context.scene, 'sna_manganpr', show_labels=False, scale=5.0, scale_popup=5.0)
        col_1DE4E = layout.column(heading='', align=False)
        col_1DE4E.alert = False
        col_1DE4E.enabled = True
        col_1DE4E.use_property_split = False
        col_1DE4E.use_property_decorate = False
        col_1DE4E.scale_x = 1.0
        col_1DE4E.scale_y = 1.0
        col_1DE4E.alignment = 'Expand'.upper()
        col_1DE4E.prop(bpy.context.view_layer.objects.active.active_material.node_tree.nodes['Hue Saturation Value.001'].inputs[0], 'default_value', text='', icon_value=0, emboss=True)
        col_1DE4E.prop(bpy.context.view_layer.objects.active.active_material.node_tree.nodes['Hue Saturation Value.001'].inputs[1], 'default_value', text='', icon_value=0, emboss=True)
        col_1DE4E.prop(bpy.context.view_layer.objects.active.active_material.node_tree.nodes['Hue Saturation Value.001'].inputs[2], 'default_value', text='', icon_value=0, emboss=True)
        col_1DE4E.prop(bpy.context.view_layer.objects.active.active_material.node_tree.nodes['Hue Saturation Value.001'].inputs[3], 'default_value', text='', icon_value=0, emboss=True)
        col_1DE4E.prop(bpy.context.view_layer.objects.active.active_material.node_tree.nodes['ColorRamp'].color_ramp.elements[0], 'color', text='', icon_value=0, emboss=True)
        col_1DE4E.prop(bpy.context.view_layer.objects.active.active_material.node_tree.nodes['ColorRamp'].color_ramp.elements[0], 'position', text='', icon_value=0, emboss=True)
        col_1DE4E.prop(bpy.context.view_layer.objects.active.active_material.node_tree.nodes['ColorRamp'].color_ramp.elements[1], 'color', text='', icon_value=0, emboss=True)
        col_1DE4E.prop(bpy.context.view_layer.objects.active.active_material.node_tree.nodes['ColorRamp'].color_ramp.elements[1], 'position', text='', icon_value=0, emboss=True)
        col_1DE4E.prop(bpy.context.view_layer.objects.active.active_material.node_tree.nodes['Mix'].inputs[0], 'default_value', text='', icon_value=0, emboss=True)
        
def sna_manganpr_enum_items(self, context):
    enum_items = [['mangaNPR1', 'mangaNPR1', '', load_preview_icon(os.path.join(os.path.dirname(__file__), 'assets', 'too1.png'))], ['mangaNPR2', 'mangaNPR2', '', load_preview_icon(os.path.join(os.path.dirname(__file__), 'assets', 'too2.png'))], ['mangaNPR3', 'mangaNPR3', '', load_preview_icon(os.path.join(os.path.dirname(__file__), 'assets', 'too3.png'))], ['mangaNPR4', 'mangaNPR4', '', load_preview_icon(os.path.join(os.path.dirname(__file__), 'assets', 'too4.png'))], ['mangaNPR5', 'mangaNPR5', '', load_preview_icon(os.path.join(os.path.dirname(__file__), 'assets', 'too5.png'))], ['mangaNPR6', 'mangaNPR6', '', load_preview_icon(os.path.join(os.path.dirname(__file__), 'assets', 'too6.png'))], ['mangaNPR7', 'mangaNPR7', '', load_preview_icon(os.path.join(os.path.dirname(__file__), 'assets', 'too7.png'))], ['mangaNPR8', 'mangaNPR8', '', load_preview_icon(os.path.join(os.path.dirname(__file__), 'assets', 'too8.png'))], ['mangaNPR9', 'mangaNPR9', '', load_preview_icon(os.path.join(os.path.dirname(__file__), 'assets', 'too9.png'))], ['mangaNPR10', 'mangaNPR10', '', load_preview_icon(os.path.join(os.path.dirname(__file__), 'assets', 'too10.png'))], ['mangaNPR11', 'mangaNPR11', '', load_preview_icon(os.path.join(os.path.dirname(__file__), 'assets', 'too11.png'))], ['mangaNPR12', 'mangaNPR12', '', load_preview_icon(os.path.join(os.path.dirname(__file__), 'assets', 'too12.png'))], ['mangaNPR13', 'mangaNPR13', '', load_preview_icon(os.path.join(os.path.dirname(__file__), 'assets', 'too13.png'))], ['mangaNPR14', 'mangaNPR14', '', load_preview_icon(os.path.join(os.path.dirname(__file__), 'assets', 'too14.png'))], ['mangaNPR15', 'mangaNPR15', '', load_preview_icon(os.path.join(os.path.dirname(__file__), 'assets', 'too15.png'))], ['mangaNPR16', 'mangaNPR16', '', load_preview_icon(os.path.join(os.path.dirname(__file__), 'assets', 'too16.png'))], ['mangaNPR17', 'mangaNPR17', '', load_preview_icon(os.path.join(os.path.dirname(__file__), 'assets', 'too17.png'))], ['mangaNPR18', 'mangaNPR18', '', load_preview_icon(os.path.join(os.path.dirname(__file__), 'assets', 'too18.png'))], ['mangaNPR19', 'mangaNPR19', '', load_preview_icon(os.path.join(os.path.dirname(__file__), 'assets', 'too19.png'))], ['mangaNPR20', 'mangaNPR20', '', load_preview_icon(os.path.join(os.path.dirname(__file__), 'assets', 'too20.png'))], ['mangaNPR21', 'mangaNPR21', '', load_preview_icon(os.path.join(os.path.dirname(__file__), 'assets', 'too21.png'))], ['mangaNPR22', 'mangaNPR22', '', load_preview_icon(os.path.join(os.path.dirname(__file__), 'assets', 'too22.png'))], ['mangaNPR23', 'mangaNPR23', '', load_preview_icon(os.path.join(os.path.dirname(__file__), 'assets', 'too23.png'))], ['mangaNPR24', 'mangaNPR24', '', load_preview_icon(os.path.join(os.path.dirname(__file__), 'assets', 'too24.png'))], ['mangaNPR25', 'mangaNPR25', '', load_preview_icon(os.path.join(os.path.dirname(__file__), 'assets', 'too25.png'))], ['mangaNPR26', 'mangaNPR26', '', load_preview_icon(os.path.join(os.path.dirname(__file__), 'assets', 'too26.png'))], ['mangaNPR27', 'mangaNPR27', '', load_preview_icon(os.path.join(os.path.dirname(__file__), 'assets', 'too27.png'))], ['mangaNPR28', 'mangaNPR28', '', load_preview_icon(os.path.join(os.path.dirname(__file__), 'assets', 'too28.png'))], ['mangaNPR29', 'mangaNPR29', '', load_preview_icon(os.path.join(os.path.dirname(__file__), 'assets', 'too29.png'))]]
    return [make_enum_item(item[0], item[1], item[2], item[3], i) for i, item in enumerate(enum_items)]




def register():
    
    global _icons
    _icons = bpy.utils.previews.new()
    bpy.types.Scene.sna_manganpr = bpy.props.EnumProperty(name='mangaNPR', description='', items=sna_manganpr_enum_items, update=sna_update_sna_manganpr_4FEA5)
    
    
    bpy.utils.register_class(SNA_PT_LINEDER_61656)

def unregister():
    
    global _icons
    bpy.utils.previews.remove(_icons)
    
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    for km, kmi in addon_keymaps.values():
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    del bpy.types.Scene.sna_manganpr
    
    
    bpy.utils.unregister_class(SNA_PT_LINEDER_61656)

