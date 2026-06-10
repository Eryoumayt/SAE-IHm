from Motif import Motif
from Case import Case
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
            for j in i:
                nb_cases += 1
                
                if j.valeur != 0:
                    nb_cases_remplies += 1
                    
        if nb_cases == nb_cases_remplies:
            return True
        else:
            return False 
        
        
    def get_motif(self, x: int, y: int):
        '''
        Fonction qui permet de savoir le motif auquel appartient une case
        en fonction de ses coordonnées (x, y)
        '''
        pass
            
    def is_empty(self) -> bool:
        '''
        Fonction qui permet de savoir si la grille
        est vide ou non
        Si elle est vide, la fonction renvoie True
        False sinon
        '''
        pass
    
    
        
    
        
        

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        