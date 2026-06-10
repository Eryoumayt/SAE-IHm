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

    def get_taille(self) -> int:
        # Renvoie le nombre de cases du motif
        return len(self.__cases)

    def get_valeurs(self) -> list:
        # Renvoie la liste des valeurs actuelles des cases
        valeurs = []
        for case in self.__cases:
            valeurs.append(case.get_value())
        return valeurs

    def get_valeurs_manquantes(self) -> list:
        # Renvoie les valeurs de 1 à N qui ne sont pas encore placées
        manquantes = []
        for v in range(1, self.get_taille() + 1):
            if v not in self.get_valeurs():
                manquantes.append(v)
        return manquantes