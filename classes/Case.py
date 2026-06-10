''' 
-- Classe Case --
'''

class Case():
    def __init__(self, position: list ,valeur: int):
        self.__position = position # position de la case
        self.__valeur = valeur # valeur de la case
    
    # Modification et récupération de la valeur
    @property
    def valeur(self):
        # Renvoie la valeur de la case
        return self.__valeur
    
    @valeur.setter
    def valeur(self, new_val: int):
        # Change la valeur de la case
        self.__valeur = new_val    
    
# ------------------------------------------------------ #

    # Coordonnées du point
    def get_x(self):
        # Renvoie la position x de la case
        return self.__position[0]
    
    def get_y(self):
        # Renvoie la position y de la case
        return self.__position[1]

# ------------------------------------------------------ #    
    
    # Comparateurs
    def compare_valeur(self, v: int) -> bool:
        '''
        Compare la valeur de la case à celle d'un entier.
        Si la valeur de la case est égale à l'entier, alors True est renvoyé.
        Sinon on renvoie False.
        '''
        if self.valeur() == v:
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
        if self.valeur() < 0 or self.valeur() > 5:
            return False
        else:
            return True
        
        
        
    
    
    
    
    
    
    
    
    
    
    
    