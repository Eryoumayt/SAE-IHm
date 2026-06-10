''' 
-- Classe Case --
'''

class Case():
    def __init__(self, position: list ,valeur: int):
        self.__position = position # position de la case
        self.__valeur = valeur # valeur de la case
    
    @valeur.setter
    def set_valeur(self, new_val: int):
        # Change la valeur de la case
        self.__valeur = new_val    
    
# ------------------------------------------------------ #

    # Getter
    @property
    def get_x(self):
        # Renvoie la position x de la case
        return self.__position[0]
    
    @property
    def get_y(self):
        # Renvoie la position y de la case
        return self.__position[1]
    
    @property
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
        
# ------------------------------------------------------ #  
        
    def verif_valeur(self) -> bool:
        '''
        Vérifie si la valeur de la case est bonne ou non.
        Renvoie True si la valeur est bonne
        False sinon.
        '''
        if self.get_value() < 0 or self.get_value() > 5:
            return False
        else:
            return True
        
        
        
    
    
    
    
    
    
    
    
    
    
    
    