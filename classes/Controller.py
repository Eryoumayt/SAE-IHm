import json
from PyQt6.QtWidgets import  QFileDialog,QMessageBox
from solver import solver
from Grille import Grille


from PyQt6.QtCore import QThread, pyqtSignal

class SolverWorker(QThread):
    termine = pyqtSignal(bool, object)
    
    def __init__(self, chemin):
        super().__init__()
        self.chemin = chemin
    
    def run(self):
        s = solver(self.chemin)
        resultat = s.resolver()
        self.termine.emit(resultat, s.grille)

class controller():
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.case_selectionnee = None
        self.donnees_brutes = None
        self.view.get_action_charger().triggered.connect(self.on_open)
        self.view.get_action_verifier().triggered.connect(self.on_check)
        self.view.get_action_sauvegarder().triggered.connect(self.on_save)
        self.view.get_action_resoudre().triggered.connect(self.on_solver)
        self.view.get_action_nouvelle().triggered.connect(self.new_game)
        
    
    def new_game(self):
        self.view.get_grille_widget().nouvelle_partie()   
        
        
    def on_case_click(self):
        pass
    
    def on_value_enter(self):
        pass
    
    def on_delete(self):
        pass
    
       
    
    def on_open(self):
        chemin, _ = QFileDialog.getOpenFileName(self.view, "Charger une grille", "", "JSON (*.json)")
        if not chemin:
            return
        self.model = Grille(chemin)        
        with open(chemin, 'r', encoding='utf-8') as f:
            donnees_brutes = json.load(f)
        self.view.get_grille_widget().afficher(donnees_brutes)
        self.donnees_brutes = donnees_brutes
        
        # Afficher la grille au centre de la fenêtre
        from PyQt6.QtWidgets import QHBoxLayout, QWidget
        conteneur = QWidget()
        layout_centre = QHBoxLayout()
        layout_centre.addStretch()
        layout_centre.addWidget(self.view.get_grille_widget())
        layout_centre.addStretch()
        conteneur.setLayout(layout_centre)
        self.view.setCentralWidget(conteneur)
    
        
        
    def on_save(self):
        if self.donnees_brutes is None:            
            QMessageBox.warning(self.view, "Attention", "Aucune grille chargée.")
            return
        
        entries = self.view.get_grille_widget().get_entries()        
        grille_sauvegarde = {}

        for nom_motif, cases in self.donnees_brutes.items():            
            nouvelle_liste = []
            for case in cases:
                row, col, valeur_init = case
                entry = entries.get((row, col))
                if entry is not None:
                    texte = entry.text()
                    # convertit le texte en int, 0 si la case est vide#
                    val = int(texte) if texte.isdigit() else 0
                else:
                    val = valeur_init
                nouvelle_liste.append([row, col, val])
            grille_sauvegarde[nom_motif] = nouvelle_liste

        chemin, _ = QFileDialog.getSaveFileName(self.view, "Sauvegarder la grille","","Fichiers JSON (*.json)")
        if chemin:
            with open(chemin, 'w', encoding='utf-8') as f:
                json.dump(grille_sauvegarde, f, indent=4)
            QMessageBox.information(self.view, "Succès", "Grille sauvegardée.")
    
    def on_check(self):
        if self.donnees_brutes is None:
            return
        
        entries = self.view.get_grille_widget().get_entries()
        
        # Pour chaque case saisie par le joueur
        for (row, col), entry in entries.items():
            texte = entry.text()
            if texte.isdigit():
                nouvelle_valeur = int(texte)
            else:
                nouvelle_valeur = 0
            
            # Trouver le motif qui contient cette case
            motif = self.model.get_motif(row, col)
            if motif is not None:
                # Trouver la case dans le motif
                case = motif.get_cases_by_pos(row, col)
                if case is not None:
                    # Mettre à jour la valeur dans le Model
                    case.valeur = nouvelle_valeur
        
        # Vérifier la validité
        valide = self.model.is_valid()
        
        if valide:
            QMessageBox.information(self.view, "Vérification", "La grille est valide !")
        else:
            QMessageBox.warning(self.view, "Vérification", "La grille n'est pas valide.")
        
    def on_solver(self):
        if self.donnees_brutes is None:
            return
        
        with open("temp_grille.json", 'w', encoding='utf-8') as f:
            json.dump(self.donnees_brutes, f)
        
        # Désactiver le bouton pendant la résolution
        self.view.get_action_resoudre().setEnabled(False)
        
        # Lancer le solveur dans un fil séparé
        self.worker = SolverWorker("temp_grille.json")
        self.worker.termine.connect(self.__on_solver_fini)
        self.worker.start()

    def __on_solver_fini(self, resultat, grille):
        # Réactiver le bouton
        self.view.get_action_resoudre().setEnabled(True)
        
        if resultat:
            self.view.get_grille_widget().afficher(grille)
            
            # Re-centrer la grille
            from PyQt6.QtWidgets import QHBoxLayout, QWidget
            conteneur = QWidget()
            layout_centre = QHBoxLayout()
            layout_centre.addStretch()
            layout_centre.addWidget(self.view.get_grille_widget())
            layout_centre.addStretch()
            conteneur.setLayout(layout_centre)
            self.view.setCentralWidget(conteneur)
            
            QMessageBox.information(self.view, "Résolution", "Solution trouvée !")
        else:
            QMessageBox.warning(self.view, "Résolution échouée", "Aucune solution n'a été trouvée pour cette grille.")
        
        
   