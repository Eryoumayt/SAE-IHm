from Case import Case

class Motif():
    def __init__(self, cases: list):
        # Liste d'objets Case appartenant à ce motif
        self.__cases = []
        for c in cases:
            self.__cases.append(Case([c[0], c[1]], c[2]))
            
    # Getter
    def get_cases(self) -> list:
        # Renvoie la liste des cases du motif
        return self.__cases
    
    def get_cases_by_pos(self, x: int, y: int):
        # Renvoie une case en fonction de ses coordonnées
        for i in self.__cases:
            if i.get_x() == x and i.get_y() == y:
                return i
        
        print("Aucune case ayant pour coordonnées (x = ",x,", y =", y,")")
        return None

    def get_taille(self) -> int:
        # Renvoie le nombre de cases du motif
        return len(self.__cases)

    def get_valeurs(self) -> list:
        # Renvoie la liste des valeurs actuelles des cases
        valeurs = []
        for case in self.__cases:
            valeurs.append(case.valeur)
        return valeurs

    def get_valeurs_manquantes(self) -> list:
        # Renvoie les valeurs de 1 à N qui ne sont pas encore placées
        manquantes = []
        for v in range(1, self.get_taille() + 1):
            if v not in self.get_valeurs():
                manquantes.append(v)
        return manquantes
    
# ---------------------------------------------- #    
    
    def multiples(self) -> bool:
        '''
        Fonction qui vérifie si une valeur est présente 
        plusieurs fois dans un même motif
        
        Si c'est le cas, alors la fonction renvoie True
        False sinon 
        '''
        liste_valeurs: list = []
        for i in self.get_cases():
            if i.valeur != 0: # On ignore les cases vides
                if i.valeur not in liste_valeurs:
                    # On ajoute les valeurs dans une liste et si elle est déjà dans la liste
                    # Alors c'est un doublon (donc on renvoie True)
                    liste_valeurs.append(i.valeur)
                else:
                    return True
            
        return False