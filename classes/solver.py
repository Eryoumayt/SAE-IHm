import json



class solver():
    """Le solveur sert à resoundre la grille de jeu a partir d'une grille de base. via un algorithme de backtracking.et de 3 contraintes :
    - Les cases d'un même motif doivent contenir des valeurs différentes.
    - Les 8 voisins d'une case doivent avoir des valeurs différentes
    - Chaque motif de taille N contient une permutation de 1 à N

    
    """
    
    def __init__(self,grille):
        """Charge la grille de base à partir d'un fichier JSON et initialise les structures de données nécessaires pour le solveur.
        Args:
            grille (str): Le chemin vers le fichier JSON contenant la grille de base.
        
        """
        with open(grille, 'r', encoding='utf-8') as f: 
            self.grille = json.load(f)     
            
       # Trier les motifs par ordre croissant de nombre de cases
        items = self.grille.items()
        self.motifs_tries = sorted(items, key=lambda item: len(item[1])) 
        max_ligne = 0
        max_colonne = 0

        for motif in self.motifs_tries:
            nom = motif[0]
            cases = motif[1]
            for case in cases:
                # Trouver le nombre de lignes et de colonnes de la grille
                if case[0] > max_ligne:
                    max_ligne = case[0]
                if case[1] > max_colonne:
                    max_colonne = case[1]

        # Le nombre de lignes et de colonnes est égal au maximum trouvé + 1 (car les indices commencent à 0)
        self.nb_lignes = max_ligne + 1
        self.nb_colonnes = max_colonne + 1
                        
        self.trouver_cases_vides()
        
    def resolver(self, index = 0): 
        """ 
        Le solveur utilise un algorithme de backtracking pour trouver une solution à la grille de jeu.
        Args:
            index (int, optional): L'index de la case vide à traiter. Par défaut à 0.
            
        Returns: bool: True si une solution a été trouvée, False sinon.
        """
        # Si tous les indices ont été traités, cela signifie que la grille est complète et valide, donc on retourne True.
        if index == len(self.ma_liste):
            return True

        case_vide = self.ma_liste[index]
        ligne = case_vide[0]
        colonne = case_vide[1]
        nom_modif = case_vide[2]    
        # On essaie de placer une valeur de 1 à N dans la case vide, en vérifiant les contraintes de voisinage et de motif.
        N = len(self.grille[nom_modif])
        for val in range(1, N + 1):
            if self.verif_voisinage(ligne, colonne, val):
                if self.verif_motif(nom_modif, val):
                    self.modifier_case(nom_modif,ligne, colonne , val)
                    if (self.resolver(index +1 )):
                    
                        return True
                    else: 
                        # Si la récursion n'a pas abouti à une solution, on réinitialise la case à 0 et on continue à essayer les autres valeurs.
                        self.modifier_case(nom_modif,ligne, colonne , 0)
                        
         # Si aucune valeur n'a permis de trouver une solution, on retourne False pour indiquer que cette branche de l'arbre de recherche n'est pas valide.           
        return False
                
            

    def modifier_case(self, nom_modif, ligne, colonne, nouvelle_val):
        """ 
        modifie la valeur d'une case dans la grille en fonction du motif auquel elle appartient.
        Args:           nom_modif (str): Le nom du motif auquel appartient la case à modifier.
                        ligne (int): La ligne de la case à modifier.
                        colonne (int): La colonne de la case à modifier.
                        nouvelle_val (int): La nouvelle valeur à attribuer à la case.  
        """
        for case in self.grille[nom_modif]:
                        if case[0] == ligne and case[1] == colonne:
                            case[2] = nouvelle_val
        
        
    def verif_motif(self, nom_modif, val):
        """ Vérifie que la valeur à placer dans la case ne viole pas la contrainte de motif, c'est-à-dire qu'elle n'est pas déjà présente dans les autres cases du même motif.
        Args:           nom_modif (str): Le nom du motif auquel appartient la case à vérifier.
                        val (int): La valeur à vérifier.
                        
        Returns:        bool: True si la valeur respecte la contrainte de motif, False sinon.
        """
        for case in self.grille[nom_modif]:
            if case[2] == val:
                return False
        return True
    
    def verif_voisinage(self, ligne, colonne,val):
        """Vérifie que la valeur à placer dans la case ne viole pas la contrainte de voisinage, c'est-à-dire qu'elle n'est pas déjà présente dans les cases adjacentes (horizontalement, verticalement et diagonalement).
        Args:           ligne (int): La ligne de la case à vérifier.
                        colonne (int): La colonne de la case à vérifier.
                        val (int): La valeur à vérifier.
                        
        Returns:        bool: True si la valeur respecte la contrainte de voisinage, False sinon.
        """
        # Les voisins d'une case sont les cases adjacentes horizontalement, verticalement et diagonalement.
        decalages = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
        
        for decalage in decalages:
            decalage_ligne = decalage[0]
            decalage_colonne = decalage[1]
            v_ligne = ligne + decalage_ligne
            v_colonne = colonne + decalage_colonne
            
            # Vérifie que les coordonnées du voisin sont valides (dans les limites de la grille)
            if v_ligne >=0 and v_colonne >=0 and v_ligne < self.nb_lignes and v_colonne < self.nb_colonnes:
                valeur_voisin = self.get_valeur(v_ligne, v_colonne)
                if valeur_voisin == val:
                    return False
        return True
                
            
                
    def get_valeur(self,ligne,colonne):
        """ cherche la valeur d'une case dans la grille en fonction de ses coordonnées (ligne et colonne) et du motif auquel elle appartient.
        Args:           ligne (int): La ligne de la case dont on veut connaître la valeur.
                        colonne (int): La colonne de la case dont on veut connaître la valeur.
                        
        Returns:        int: La valeur de la case à ces coordonnées, ou 0 si la case n'existe pas dans la grille.
                        
        """
        
        
        for motif in self.motifs_tries : 
            nom = motif[0]  
            cases = motif[1]
    
            for case in cases:
                c_ligne = case[0]
                c_colonne = case[1]
                c_valeur = case[2]
                if c_ligne == ligne and c_colonne == colonne:    
                    return c_valeur
                
        # Si aucune case ne correspond aux coordonnées données, cela signifie que la case n'existe pas dans la grille, donc on retourne 0 ou une valeur par défaut.
        return 0 
         
                
    
                
    def trouver_cases_vides(self):         
        """ construit une liste de toutes les cases vides de la grille, c'est-à-dire les cases dont la valeur est égale à 0. Cette liste est utilisée par le solveur pour savoir quelles cases doivent être remplies.
        """
        self.ma_liste = []

        for motif in self.motifs_tries : 
            nom = motif[0]  
            cases = motif[1]
    
            for case in cases:
                ligne = case[0]
                colonne = case[1]
                valeur = case[2]

                # Si la valeur de la case est égale à 0, cela signifie que la case est vide, donc on ajoute ses coordonnées et le nom du motif auquel elle appartient à la liste des cases vides.
                if valeur == 0:    
                    # On ajoute les coordonnées de la case vide et le nom du motif auquel elle appartient à la liste des cases vides.
                    self.ma_liste.append([ligne, colonne,nom])

        return 
