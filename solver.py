import json



class solver():
    
    def __init__(self,grille):
        with open('grille1.json', 'r', encoding='utf-8')as f : 
            self.grille = json.load(f)     
            
        items = self.grille.items()
        self.motifs_tries = sorted(items, key=lambda item: len(item[1])) 
        
    def resolver(self): 
        
        for motif in self.motifs_tries : 
            nom = motif[0]      
            cases = motif[1]
            for case in cases:
                ligne = case[0]      
                colonne = case[1]    
                valeur = case[2]     

        
        if (1 contrainre)
            if ( 2 emme contraite)
                if (3eme contraintre )
        
    
        
        return 
