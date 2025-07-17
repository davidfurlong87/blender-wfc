import bpy

from enum import Enum
from random import choice

from bpy.props import EnumProperty
from random import choice
from math import radians
from mathutils import Vector

# ----------------------------------------------
# Define Enums
# ----------------------------------------------

class Socket(Enum):
    ROAD_CENTRE = "Road_Centre"
    PAVEMENT_POS = "Pavement_Positive"
    PAVEMENT_NEG = "Pavement_Negative"
    BUILDING = "Building"

class Axis(Enum):
    POS_X = "PosX"
    NEG_X = "NegX"
    POS_Y = "PosY"
    NEG_Y = "NegY"

class Connector(Enum):
    POS_X = "PosX_Connector"
    NEG_X = "NegX_Connector"
    POS_Y = "PosY_Connector"
    NEG_Y = "NegY_Connector"

class NeighbourList(Enum):
    POS_X = "Neighbours_PosX"
    NEG_X = "Neighbours_NegX"
    POS_Y = "Neighbours_PosY"
    NEG_Y = "Neighbours_NegY"


# ----------------------------------------------
# Define Constants
# ----------------------------------------------

axisDictionary = {
    Axis.POS_X: {
                    "Name": Axis.POS_X.value,
                    "PairedConnectorName": Connector.NEG_X.value,
                    "ConnectorName": Connector.POS_X.value,
                    "PairedAxisName": Axis.NEG_X,
                    "NeigbourListName": NeighbourList.POS_X.value           
                },
    Axis.NEG_X: {
                    "Name": Axis.NEG_X.value,
                    "PairedConnectorName": Connector.POS_X.value,
                    "ConnectorName": Connector.NEG_X.value,
                    "PairedAxisName": Axis.POS_X,
                    "NeigbourListName": NeighbourList.NEG_X.value           
                },
    Axis.POS_Y: {
                    "Name": Axis.POS_Y.value,
                    "PairedConnectorName": Connector.NEG_Y.value,
                    "ConnectorName": Connector.POS_Y.value,
                    "PairedAxisName": Axis.NEG_Y,
                    "NeigbourListName": NeighbourList.POS_Y.value           
                },
    Axis.NEG_Y: {
                    "Name": Axis.NEG_Y.value,
                    "PairedConnectorName": Connector.POS_Y.value,
                    "ConnectorName": Connector.NEG_Y.value,
                    "PairedAxisName": Axis.POS_Y,
                    "NeigbourListName": NeighbourList.NEG_Y.value           
                }
}

grid_objects_collection_name = "GridObjects"
prefab_base_collection_name = "PrefabPrimitives"
prefab_variant_collection_name = "PrefabVariants"

# ----------------------------------------------
# General/Universal Functions
# ----------------------------------------------

def get_collection(collection_name):
    scene = bpy.context.scene
    if collection_name in bpy.data.collections:
        collection = bpy.data.collections[collection_name]
    else:
        collection = bpy.data.collections.new(collection_name)
        scene.collection.children.link(collection)
    return collection


# ----------------------------------------------
# Building Prefabs Functions
# ----------------------------------------------

def generate_default_prefabs(object_list):   
    current_id = 0
    for obj in object_list:
        if obj.name == "Corner":
            obj["ID"] = current_id * 10
            obj["PosX_Connector"] = Socket.ROAD_CENTRE.value
            obj["NegX_Connector"] = Socket.PAVEMENT_POS.value
            obj["PosY_Connector"] = Socket.PAVEMENT_NEG.value
            obj["NegY_Connector"] = Socket.ROAD_CENTRE.value
        elif obj.name == "Pavement":
            obj["ID"] = current_id * 10
            obj["PosX_Connector"] = Socket.ROAD_CENTRE.value
            obj["NegX_Connector"] = Socket.BUILDING.value
            obj["PosY_Connector"] = Socket.PAVEMENT_NEG.value
            obj["NegY_Connector"] = Socket.PAVEMENT_POS.value
        elif obj.name == "Building":
            obj["ID"] = current_id * 10
            obj["PosX_Connector"] = Socket.BUILDING.value
            obj["NegX_Connector"] = Socket.BUILDING.value
            obj["PosY_Connector"] = Socket.BUILDING.value
            obj["NegY_Connector"] = Socket.BUILDING.value
        else:            
            obj["ID"] = current_id * 10
            obj["PosX_Connector"] = ""
            obj["NegX_Connector"] = ""
            obj["PosY_Connector"] = ""
            obj["NegY_Connector"] = ""
        current_id += 1
            
# def generate_variants(object_list, target_collection_name):
#     target_collection = get_collection(target_collection_name)
#     offset = Vector((100,0,0))
#     for base_object in object_list:
#         posX_placeholder = base_object["PosX_Connector"]
#         negX_placeholder = base_object["NegX_Connector"]
#         posY_placeholder = base_object["PosY_Connector"]
#         negY_placeholder = base_object["NegY_Connector"]
        
#         for rotation in range(4):
#             new_obj = base_object.copy()
#             new_obj.name = base_object.name + f"_{rotation}"
#             new_obj.data = base_object.data.copy()
#             new_obj["ID"] = new_obj["ID"] + rotation
#             new_obj.location += base_object.location + Vector(((rotation * 20) + rotation * 20, 0, 0)) + offset
#             new_obj.rotation_euler = (0,0,radians(rotation * 90))

#             new_obj["PosX_Connector"] = posX_placeholder
#             new_obj["NegX_Connector"] = negX_placeholder
#             new_obj["PosY_Connector"] = posY_placeholder
#             new_obj["NegY_Connector"] = negY_placeholder
            
#             posX_placeholder = new_obj["NegY_Connector"]
#             negX_placeholder = new_obj["PosY_Connector"]
#             posY_placeholder = new_obj["PosX_Connector"]
#             negY_placeholder = new_obj["NegX_Connector"] 
            
#             target_collection.objects.link(new_obj)

def check_neighbours_match(neighbourA, neighbourB):
    if neighbourA == Socket.ROAD_CENTRE.value and neighbourB == Socket.ROAD_CENTRE.value:
        return True
    if neighbourA == Socket.PAVEMENT_POS.value and neighbourB == Socket.PAVEMENT_NEG.value:
        return True
    if neighbourA == Socket.PAVEMENT_NEG.value and neighbourB == Socket.PAVEMENT_POS.value:
        return True
    if neighbourA == Socket.BUILDING.value and neighbourB == Socket.BUILDING.value:
        return True
    else:
        return False
    
def get_valid_neighbours(socket, connector_to_check, variantObjectList):
    listOfNeighbours = []
    for neighbourObject in variantObjectList:
        neighbourSocket = neighbourObject[connector_to_check]
        if check_neighbours_match(socket, neighbourSocket):
            listOfNeighbours.append(neighbourObject)
    
    return listOfNeighbours



def build_neighbour_lists(variant_collection_name):
    variantObjectList = get_collection(variant_collection_name).objects
    for object in variantObjectList:
#        Lopp through all axes
        for key in axisDictionary:
#           Reset the neighbour group for that axis
            object[axisDictionary[key]["NeigbourListName"]] = ""
#           Get the socket value of its connector 
            socket = object[axisDictionary[key]["ConnectorName"]]
#            Get the axis to check for this axis
            connector_to_check = axisDictionary[key]["PairedConnectorName"]
            listOfNeighbours = get_valid_neighbours(socket, connector_to_check, variantObjectList)

            for n in listOfNeighbours:
                object[axisDictionary[key]["NeigbourListName"]] = object[axisDictionary[key]["NeigbourListName"]] + n.name + " "
    


# ----------------------------------------------
# Main 
# ----------------------------------------------



base_prefab_objects = get_collection(prefab_base_collection_name).objects
#generate_default_prefabs(base_prefab_objects)
#generate_variants(base_prefab_objects,prefab_variant_collection_name)
build_neighbour_lists(prefab_variant_collection_name)

#DEBUG
# ----------------------------------------------
# Debug Functions
# ----------------------------------------------

#variantObjectList = get_collection(prefab_variant_collection_name).objects
#build_empty_neighbour_lists(variantObjectList)

def build_empty_neighbour_lists(variantObjectList):
    for object in variantObjectList:
        for key in axisDictionary:
            object[axisDictionary[key]["NeigbourListName"]] = ""
            object[axisDictionary[key]["NeigbourListName"]] =  axisDictionary[key]["PairedConnectorName"]

def generate_empty_properties(object_list):
    current_id = 0
    for object in object_list:
        object["ID"] = current_id
        for key in axisDictionary:
            object[axisDictionary[key]["NeigbourListName"]] = ""
            object[axisDictionary[key]["ConnectorName"]] = ""
        current_id += 1
        

            

