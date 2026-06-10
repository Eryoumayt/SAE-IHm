import json



class solver():
    
    def __init__(self,grille):
        with open(grille, 'r', encoding='utf-8') as f: 
            self.grille = json.load(f)     
            
       
        items = self.grille.items()
        self.motifs_tries = sorted(items, key=lambda item: len(item[1])) 
        max_ligne = 0
        max_colonne = 0

        for motif in self.motifs_tries:
            nom = motif[0]
            cases = motif[1]
            for case in cases:
                if case[0] > max_ligne:
                    max_ligne = case[0]
                if case[1] > max_colonne:
                    max_colonne = case[1]

        self.nb_lignes = max_ligne + 1
        self.nb_colonnes = max_colonne + 1
                        
        self.trouver_cases_vides()
        
    def resolver(self, index = 0): 
        
        if index == len(self.ma_liste):
            return True

        case_vide = self.ma_liste[index]
        ligne = case_vide[0]
        colonne = case_vide[1]
        nom_modif = case_vide[2]    
        N = len(self.grille[nom_modif])
        for val in range(1, N + 1):
            if self.verif_voisinage(ligne, colonne, val):
                if self.verif_motif(nom_modif, val):
                    self.modifier_case(nom_modif,ligne, colonne , val)
                    if (self.resolver(index +1 )):
                    
                        return True
                    else: 
                        self.modifier_case(nom_modif,ligne, colonne , 0)
                        
                    
        return False
                
            

    def modifier_case(self, nom_modif, ligne, colonne, nouvelle_val):
        for case in self.grille[nom_modif]:
                        if case[0] == ligne and case[1] == colonne:
                            case[2] = nouvelle_val
        
        
    def verif_motif(self, nom_modif, val):
        for case in self.grille[nom_modif]:
            if case[2] == val:
                return False
        return True
    
    def verif_voisinage(self, ligne, colonne,val):
        decalages = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
        
        for decalage in decalages:
            decalage_ligne = decalage[0]
            decalage_colonne = decalage[1]
            v_ligne = ligne + decalage_ligne
            v_colonne = colonne + decalage_colonne
            
            if v_ligne >=0 and v_colonne >=0 and v_ligne < self.nb_lignes and v_colonne < self.nb_colonnes:
                valeur_voisin = self.get_valeur(v_ligne, v_colonne)
                if valeur_voisin == val:
                    return False
        return True
                
            
                
    def get_valeur(self,ligne,colonne):
        
        
        for motif in self.motifs_tries : 
            nom = motif[0]  
            cases = motif[1]
    
            for case in cases:
                c_ligne = case[0]
                c_colonne = case[1]
                c_valeur = case[2]
                if c_ligne == ligne and c_colonne == colonne:    
                    return c_valeur
        return 0 
         
                
    
                
    def trouver_cases_vides(self):         
        self.ma_liste = []

        for motif in self.motifs_tries : 
            nom = motif[0]  
            cases = motif[1]
    
            for case in cases:
                ligne = case[0]
                colonne = case[1]
                valeur = case[2]

                
                if valeur == 0:    
                    self.ma_liste.append([ligne, colonne,nom])

        return 

s = solver("Grille/grille1.json")
resultat = s.resolver()
if resultat:
    print("Fini ! Solution trouvee")
else:
    print("Pas de solution")