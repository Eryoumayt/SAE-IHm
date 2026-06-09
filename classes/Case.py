''' 
-- Classe Case --
'''

class Case():
    def __init__(self, position: list ,valeur: int):
        self.__position = position # position de la case
        self.__valeur = valeur # valeur de la case
    
    # Setter
    def set_x(self, new_x: int):
        # Change la position x de la case
        self.__position[0] = new_x
        
    def set_y(self, new_y: int):
        # Change la position y de la case
        self.__position[1] = new_y
        
    def set_valeur(self, new_val: int):
        # Change la valeur de la case
        self.__valeur = new_val    
    
# ------------------------------------------------------ #

    # Getter
    def get_x(self):
        # Renvoie la position x de la case
        return self.__position[0]
    
    def get_y(self):
        # Renvoie la position y de la case
        return self.__position[1]
    
    def get_value(self):
        # Renvoie la valeur de la case
        return self.__valeur
    
# ------------------------------------------------------ #    
    
    # Comparateurs
    def compare_valeur(self, valeur: int) -> bool:
        '''
        Compare la valeur de la case à celle d'un entier.
        Si la valeur de la case est égale à l'entier, alors True est renvoyé.
        Sinon on renvoie False.
        '''
        if self.get_value() == valeur:
            return True
        else:
            return False
        
    def compare_pos(self, pos_x, pos_y):
        '''
        Compare les coordonnées de la case à celle insérés dans la fonction.
        Si les coordonnées sont les mêmes, alors on renvoie True
        Sinon False.
        '''
        if self.get_x() == pos_x and self.get_y() == pos_y:
            return True
        else:
            return False
        
        
        
    
    
    
    
    
    
    
    
    
    
    
    