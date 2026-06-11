import json
from PyQt6.QtWidgets import  QFileDialog,QMessageBox,QHBoxLayout, QWidget,QVBoxLayout
from PyQt6.QtCore import Qt
from solver import solver
from Grille import Grille


from PyQt6.QtCore import QThread, pyqtSignal

class SolverWorker(QThread):
    """ 
    Pour executer le solveur separement de l'interface graphique, on utilise un QThread.
    Cela permet de ne pas bloquer l'interface pendant que le solveur travaille.
    """
    termine = pyqtSignal(bool, object)
    
    def __init__(self, chemin):
        super().__init__()
        self.chemin = chemin
    
    def run(self):
        s = solver(self.chemin)
        resultat = s.resolver()
        self.termine.emit(resultat, s.grille)

class controller():
    """Le controlleur pour gérer les interactions entre le modèle (Grille) et la vue (Vue).
    Il connecte les actions de la vue à des méthodes qui manipulent le modèle et mettent à jour la vue en conséquence.
    
    Args: 
    model (Grille): L'instance du modèle représentant la grille de jeu.
    view (Vue): L'instance de la vue représentant l'interface utilisateur.
    Returns: None
    Atributs: 
    model (Grille): L'instance du modèle représentant la grille de jeu.
    view (Vue): L'instance de la vue représentant l'interface utilisateur.
    """
    def __init__(self, model, view):
        """Initialise le contrôleur avec une instance du modèle et de la vue, et connecte les actions de la vue à des méthodes du contrôleur.

        Args:
            model (Grille): L'instance du modèle représentant la grille de jeu.
            view (Vue): L'instance de la vue représentant l'interface utilisateur.
            
        Returns: None
        Atributs: 
            model (Grille): L'instance du modèle représentant la grille de jeu.
            view (Vue): L'instance de la vue représentant l'interface utilisateur.
        """
        self.model = model
        self.view = view
        self.case_selectionnee = None
        self.donnees_brutes = None
        self.view.get_action_charger().triggered.connect(self.on_open)
        self.view.get_action_verifier().triggered.connect(self.on_check)
        self.view.get_action_sauvegarder().triggered.connect(self.on_save)
        self.view.get_action_resoudre().triggered.connect(self.on_solver)
        self.view.get_action_nouvelle().triggered.connect(self.new_game)
        self.view.get_action_verifier_voisinage().triggered.connect(self.on_verifier_voisinage)        
    
    def new_game(self):
        """ Réinitialise la grille et le chrono pour commencer une nouvelle partie.
         
         Args: None 
        Returns: None
        Attributs: None
            
        """
        self.view.get_grille_widget().nouvelle_partie()   
        self.view.reinitialiser_chrono()
        self.view.demarrer_chrono()

        
   
    def on_open(self):
        """ Ouvre une boîte de dialogue pour sélectionner un fichier JSON contenant une grille, charge les données dans le modèle et met à jour la vue pour afficher la grille.
        
        args: None
        Returns: None
        Attributs: None
        """
        chemin, _ = QFileDialog.getOpenFileName(self.view, "Charger une grille", "", "JSON (*.json)")
        if not chemin:
            return
        self.model = Grille(chemin)
        with open(chemin, 'r', encoding='utf-8') as f:
            donnees_brutes = json.load(f)
        self.view.get_grille_widget().afficher(donnees_brutes)
        self.donnees_brutes = donnees_brutes

        # Chrono au-dessus, grille au centre
        conteneur = QWidget()
        layout_horizontal = QHBoxLayout()
        layout_horizontal.addStretch()
        layout_horizontal.addWidget(self.view.get_grille_widget())    # centré
        layout_horizontal.addStretch()
        layout_horizontal.addWidget(self.view.get_label_chrono())  
        conteneur.setLayout(layout_horizontal)  
        self.view.setCentralWidget(conteneur)
        self.view.demarrer_chrono()
        
            
        
    def on_save(self):
        """ Ouvre une boîte de dialogue pour sélectionner un emplacement et un nom de fichier, puis sauvegarde la grille actuelle dans un fichier JSON.
        args: None
        Returns: None
        Attributs: None
        """
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
        """ Vérifie si la grille actuelle est valide en comparant les valeurs saisies par l'utilisateur avec les règles du jeu, et affiche un message indiquant si la grille est valide ou non.
        args: None
        Returns: None
        Attributs: None"""
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
            self.view.arreter_chrono()
        else:
            QMessageBox.warning(self.view, "Vérification", "La grille n'est pas valide.")
        
    def on_solver(self):
        """ Lance le solveur pour trouver une solution à la grille actuelle, et met à jour la vue pour afficher la solution trouvée. Si aucune solution n'est trouvée, affiche un message d'erreur.
        args: None
        Returns: None
        Attributs: None
        """
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
        """ Callback appelé lorsque le solveur a terminé. Met à jour la vue avec la solution trouvée, ou affiche un message d'erreur si aucune solution n'a été trouvée. Réactive le bouton de résolution.
        
            Args:
                resultat (bool): Indique si une solution a été trouvée ou non.
                grille (dict): La grille solution trouvée par le solveur, ou None si aucune solution n'a été trouvée.
                
            Returns: None
            Attributs: None
        """
        self.view.get_action_resoudre().setEnabled(True)
        if resultat:
            self.view.get_grille_widget().afficher(grille)

            conteneur = QWidget()
            layout_vertical = QVBoxLayout()
            layout_vertical.addWidget(self.view.get_label_chrono())
            layout_vertical.setAlignment(self.view.get_label_chrono(), Qt.AlignmentFlag.AlignCenter)

            layout_horizontal = QHBoxLayout()
            layout_horizontal.addStretch()
            layout_horizontal.addWidget(self.view.get_grille_widget())
            layout_horizontal.addStretch()
            layout_vertical.addLayout(layout_horizontal)

            conteneur.setLayout(layout_vertical)
            self.view.setCentralWidget(conteneur)
            self.view.arreter_chrono()

            QMessageBox.information(self.view, "Résolution", "Solution trouvée !")
        else:
            QMessageBox.warning(self.view, "Résolution échouée", "Aucune solution n'a été trouvée pour cette grille.")
        
    def on_verifier_voisinage(self):
        """Détecte les conflits de voisinage et surligne les cases en rouge.

        Parcourt toutes les cases remplies (éditables et non éditables) et 
        vérifie si un des 8 voisins contient la même valeur. Si oui, les 
        cases éditables en conflit sont surlignées en rouge.
        """
        if self.donnees_brutes is None:
            return

        entries = self.view.get_grille_widget().get_entries()

        # Construire un dictionnaire de TOUTES les valeurs#
        toutes_valeurs = {}
        for nom_motif, cases in self.donnees_brutes.items():
            for case in cases:
                row, col, valeur_init = case
                entry = entries.get((row, col))
                if entry is not None:
                    texte = entry.text()
                    val = int(texte) if texte.isdigit() and int(texte) != 0 else 0
                else:
                    val = valeur_init
                if val != 0:
                    toutes_valeurs[(row, col)] = val

        # Vérifier les conflits sur toutes les cases#
        conflits = set()
        for (row, col), val in toutes_valeurs.items():
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    voisin_val = toutes_valeurs.get((row + dr, col + dc))
                    if voisin_val is not None and voisin_val == val:
                        # Surligner seulement les cases éditables#
                        if (row, col) in entries:
                            conflits.add((row, col))
                        if (row + dr, col + dc) in entries:
                            conflits.add((row + dr, col + dc))

        self.view.get_grille_widget().surligner_conflits(conflits)