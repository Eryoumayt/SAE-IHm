from .Motif import Motif
from .Case import Case
import json

class Grille():
    def __init__(self, path: str):
        self.__path = path
        self.__dico_brut = self.from_json(self.__path)
        
        self.__grille: dict = {} 
        for i in self.__dico_brut: 
            self.__grille[i] = Motif(self.__dico_brut[i]) 
            
            
    def from_json(self, file_path: str) -> dict:
        # Transforme les fichiers json en dictionnaires python
        with open(file_path) as f:
            return json.load(f)
        
    
    def is_full(self):
        '''
        Vérifie si une grille est complète ou non
        Si la grille est remplie, la fonction renvoie True
        False sinon
        '''
        nb_cases: int = 0
        nb_cases_remplies: int = 0
        
        for i in self.__grille.values():
            for j in i.get_cases():
                # Comptage du nombre de cases
                nb_cases += 1
                
                # Comptage du nombre de cases vides (valeur différente 0)
                if j.valeur != 0:
                    nb_cases_remplies += 1
                    
        if nb_cases == nb_cases_remplies:
            return True
        else:
            return False 
        
        
    def get_motif(self, x: int, y: int) -> Motif:
        '''
        Fonction qui permet de savoir le motif auquel appartient une case
        en fonction de ses coordonnées (x, y)
        Renvoie un motif si elle trouve un point avec ces coordonnées
        None sinon
        '''
        for i in self.__grille.values():
            for j in i.get_cases():
                if j.get_x() == x and j.get_y() == y:
                    return i
        return None 
        
            
    def is_valid(self) -> bool:
        '''
        Fonction qui permet de savoir si la grille
        est valide ou non
        Si elle est valide, la fonction renvoie True
        False sinon
        '''
        if self.is_full() == False:
            return False
        
        for i in self.__grille.values():
            if i.multiples() == True:
                return False
        
        return True
            
        
        
        
    
        
    
    
        
    
        
        

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        