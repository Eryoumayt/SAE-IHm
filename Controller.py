import json


class controller():
    def __init__(self, model, view):
        self.model = model
        self.view = view
    
    def create_grid(self):
        self.model.create_grid()
        
        

        
    def view(self):
        self.model.view()
    
    
    def on_case_click(self):
        pass
    
    def on_value_enter(self):
        pass
    
    def on_delete(self):
        pass
    
    
    
    
    def on_open(self):
        pass
    
    def on_save(self):
        pass
    
    def on_check(self):
        pass
    
    def on_solver(self):
        pass
    
    
    
    
        # try:
        #     with open('grilleEx1.json', 'r', encoding='utf-8') as f:
        #         data = json.load(f)
        # except FileNotFoundError:
        #     print("Fichier non trouvé.")
        # except json.JSONDecodeError:
        #     print("Erreur : Le fichier n'est pas un JSON valide.")
            