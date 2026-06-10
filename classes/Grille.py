from Motif import Motif
from Case import Case
import json

class Grille():
    def __init__(self, path: str):
        self.__path = path
        self.__dico_brut = self.from_json(self.__path)
        
        self.__grille: dict = {} 
        for i in range(len(self.__dico_brut) - 1): 
            self.__grille["motif"+i] = Motif(self.__dico_brut[i]) 
            
            
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
            for j in i:
                nb_cases += 1
                
                if j[2] != 0:
                    nb_cases_remplies += 1
                    
        if nb_cases == nb_cases_remplies:
            return True
        else:
            return False 
            
        
    
        
    
        
        

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        