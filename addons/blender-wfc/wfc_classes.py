import bpy

class WFCModule:
    def __init__(self, name, obj_source, module_weight, pos_x, neg_x, pos_y, neg_y):
        self.name = name
        self.obj_source = obj_source
        self.module_weight = module_weight
        self.pos_x = pos_x
        self.neg_x = neg_x
        self.pos_y = pos_y
        self.neg_y = neg_y
        
class WFCCell:
    def __init__(self, posX, posY, possibleModules):
        self.posX = posX
        self.posY = posY
        self.coordinates = WFCCoordinates(posX, posY)
        # self.possibleVariantIds = possibleVariantIds[:]
        self.possibleModules = possibleModules[:]
        self.isCollapsed = False
        # TODO: Implement the below
        # self.cell_obj = cell_obj

    def __str__(self):
        return f"{self.posX, self.posY}"
#        return f"{self.posX}/{self.posY}"

    def get_coords(self):
        return [self.posX, self.posY]
    
    def get_coords_set(self):
        return (self.posX, self.posY)
    
    def number_of_modules_remaining(self):
        return len(self.possibleModules)
    
    def return_collapsed_module(self):
        print(f"(self.number_of_modules_remaining): {(self.number_of_modules_remaining())}")
        if (self.isCollapsed):
            return self.possibleModules[0]
        else:
            # TODO: EXCEPTION
            print(f"Cell {self.posX, self.posY} NOT YET COLLAPSED")


# TODO:rename posX/Y. this looks like its an axis, just x/y is fine
class WFCCoordinates:
    def __init__(self, posX, posY):
        self.posX = posX
        self.posY = posY

    def __str__(self):
        return f"{self.posX, self.posY}"