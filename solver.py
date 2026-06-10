import json



class solver():
    
    def __init__(self,grille):
        with open('grille1.json', 'r', encoding='utf-8')as f : 
            self.grille = json.load(f)     
            
        items = self.grille.items()
        self.motifs_tries = sorted(items, key=lambda item: len(item[1])) 
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
                if ():
                    if ( ):
                        if ():
                            pass
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
        
    
                
    def trouver_cases_vides(self):         
        self.ma_liste = []

        for motif in self.motifs_tries : 
            nom = motif[0]  
            cases = motif[1]
    
            for case in cases:
                ligne = case[0]
                colonne = case[1]
                nom_modif = case[2]

                
                if nom_modif == 0:    
                    self.ma_liste.append([ligne, colonne,nom])

        return 
