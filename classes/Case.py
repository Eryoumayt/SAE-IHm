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
    
    
    # Autres méthodes
    def compare_valeur(self, valeur: int) -> bool:
        if self.get_value() == valeur:
            return True
        else:
            return False
        
    def compare_pos(self, pos_x, pos_y):
        if self.get_x() == pos_x and self.get_y() == pos_y:
            return True
        else:
            return False
    
    
    
    
    
    
    
    
    
    
    
    