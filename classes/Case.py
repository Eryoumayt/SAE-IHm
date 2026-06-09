# Classe Case
class Case():
    def __init__(self, position: tuple ,valeur: int):
        self.__position = position
        self.__valeur = valeur
    
    # Setter
    def set_x(self, new_x: int):
        self.__position[0] = new_x
        
    def set_y(self, new_y: int):
        self.__position[1] = new_y
        
    def set_valeur(self, new_val: int):
        self.__valeur = new_val    
    
    
    # Getter
    def get_x(self):
        return self.__position[0]
    
    def get_y(self):
        return self.__position[1]
    
    def get_value(self):
        return self.__valeur
    
    
    
    
    
    
    
    
    
    