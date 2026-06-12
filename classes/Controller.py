import json
from PyQt6.QtWidgets import  QFileDialog,QMessageBox,QHBoxLayout, QWidget,QVBoxLayout
from PyQt6.QtCore import Qt,QObject,QEvent
from PyQt6.QtGui import QShortcut, QKeySequence
from .solver import solver
from .Grille import Grille
from PyQt6.QtCore import QThread, pyqtSignal

class SolverWorker(QThread):
    """ 
    Pour executer le solveur separement de l'interface graphique, on utilise un QThread.
    Cela permet de ne pas bloquer l'interface pendant que le solveur travaille.
    Args: chemin (str): Le chemin vers le fichier JSON de la grille à résoudre.
    Attributes: chemin (str): Le chemin vers le fichier JSON de la grille à résoudre.
    """
    termine = pyqtSignal(bool, object)
    
    def __init__(self, chemin):
        super().__init__()
        self.chemin = chemin
    
    def run(self):
        s = solver(self.chemin)
        resultat = s.resolver()
        self.termine.emit(resultat, s.grille)

class controller(QObject):
    """Le controlleur pour gérer les interactions entre le modèle (Grille) et la vue (Vue).
    Il connecte les actions de la vue à des méthodes qui manipulent le modèle et mettent à jour la vue en conséquence.
    
    Args: 
    model (Grille): L'instance du modèle représentant la grille de jeu.
    view (Vue): L'instance de la vue représentant l'interface utilisateur.
    Attributes: 
    model (Grille): L'instance du modèle représentant la grille de jeu.
    view (Vue): L'instance de la vue représentant l'interface utilisateur.
    """
    def __init__(self, model, view):
        """Initialise le contrôleur avec une instance du modèle et de la vue, et connecte les actions de la vue à des méthodes du contrôleur.

        Args:
            model (Grille): L'instance du modèle représentant la grille de jeu.
            view (Vue): L'instance de la vue représentant l'interface utilisateur.
            
        Attributes: 
            model (Grille): L'instance du modèle représentant la grille de jeu.
            view (Vue): L'instance de la vue représentant l'interface utilisateur.
        """
        super().__init__()

        self.model = model
        self.view = view
        self.case_selectionnee = None
        self.donnees_brutes = None
        self.chemin_grille = None
        self.view.get_action_charger().triggered.connect(self.on_open)
        self.view.get_action_verifier().triggered.connect(self.on_check)
        self.view.get_action_sauvegarder().triggered.connect(self.on_save)
        self.view.get_action_resoudre().triggered.connect(self.on_solver)
        self.view.get_action_nouvelle().triggered.connect(self.new_game)
        # self.view.get_action_verifier_voisinage().triggered.connect(self.on_verifier_voisinage)   
        QShortcut(QKeySequence(Qt.Key.Key_Delete), self.view).activated.connect(self.on_delete)     
    
    def __charger_grille(self, chemin):
        """Charge une grille depuis un fichier JSON et met à jour la vue.
        Args:
            chemin (str): Le chemin vers le fichier JSON contenant la grille à charger.
        Attributes: 
            model (Grille): L'instance du modèle représentant la grille de jeu, mise à jour avec la nouvelle grille chargée.            
            donnees_brutes (dict): Les données brutes de la grille chargée, utilisées pour afficher la grille dans la vue.
            chemin_grille (str): Le chemin vers le fichier JSON de la grille actuellement chargée, utilisé pour les opérations de sauvegarde et de nouvelle partie.
        """
        self.model = Grille(chemin)
        with open(chemin, 'r', encoding='utf-8') as f:
            self.donnees_brutes = json.load(f)
        self.chemin_grille = chemin

        self.view.get_grille_widget().afficher(self.donnees_brutes)

        conteneur = QWidget()
        layout_horizontal = QHBoxLayout()
        layout_horizontal.addStretch()
        layout_horizontal.addWidget(self.view.get_grille_widget())
        layout_horizontal.addStretch()
        layout_horizontal.addWidget(self.view.get_label_chrono())
        conteneur.setLayout(layout_horizontal)
        self.view.setCentralWidget(conteneur)

        entries = self.view.get_grille_widget().get_entries()
        for (row, col), entry in entries.items():
            entry.installEventFilter(self)
            entry.textChanged.connect(lambda texte, r=row, c=col: self.on_value_enter(r, c))

        self.view.reinitialiser_chrono()
        self.view.demarrer_chrono()
        self.view.get_action_resoudre().setEnabled(True)

    def on_open(self):
        """Ouvre une boîte de dialogue pour sélectionner un fichier JSON contenant une grille.
        Attributes: 
            chemin_grille (str): Le chemin vers le fichier JSON de la grille actuellement chargée, utilisé pour les opérations de sauvegarde et de nouvelle partie.
        """
        chemin, _ = QFileDialog.getOpenFileName(self.view, "Charger une grille", "", "JSON (*.json)")
        if not chemin:
            return
        self.__charger_grille(chemin)

    def new_game(self):
        """Réinitialise la grille et le chrono pour commencer une nouvelle partie.

        Attributes:
            chemin_grille (str): Le chemin vers le fichier JSON de la grille actuellement chargée
        """
        if self.chemin_grille is not None:
            self.__charger_grille(self.chemin_grille)
        
    def on_save(self):
        """Ouvre une boîte de dialogue pour sauvegarder la grille actuelle dans un fichier JSON.
        Les cases éditables sont sauvegardées avec leur valeur initiale (0) et la valeur du joueur,
        pour que les cases restent éditables au rechargement tout en conservant la progression.
        """
        if self.donnees_brutes is None:
            QMessageBox.warning(self.view, "Attention", "Aucune grille chargée.")
            return

        entries = self.view.get_grille_widget().get_entries()
        grille_sauvegarde = {}

        for nom_motif, cases in self.donnees_brutes.items():
            nouvelle_liste = []
            for case in cases:
                row = case[0]
                col = case[1]
                valeur_init = case[2]                
                entry = entries.get((row, col))
                if entry is not None:
                    # Case éditable : valeur_init=0, valeur_joueur=ce qui est tapé#
                    texte = entry.text()
                    valeur_joueur = int(texte) if texte.isdigit() else 0
                    nouvelle_liste.append([row, col, 0, valeur_joueur])
                else:
                    # Case fixe : valeur_init=la valeur, valeur_joueur=0#
                    nouvelle_liste.append([row, col, valeur_init, 0])
            grille_sauvegarde[nom_motif] = nouvelle_liste

        chemin, _ = QFileDialog.getSaveFileName(self.view, "Sauvegarder la grille", "", "Fichiers JSON (*.json)")
        if chemin:
            with open(chemin, 'w', encoding='utf-8') as f:
                json.dump(grille_sauvegarde, f, indent=4)
            QMessageBox.information(self.view, "Succès", "Grille sauvegardée.")
        
    def on_check(self):
        """ Vérifie si la grille actuelle est valide en comparant les valeurs saisies par l'utilisateur avec les règles du jeu, et affiche un message indiquant si la grille est valide ou non.
  """
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

        """
        self.view.get_action_resoudre().setEnabled(True)

        if resultat:
            self.view.get_grille_widget().afficher(grille)
            # Reconnecter les signaux des entries#
            entries = self.view.get_grille_widget().get_entries()
            for (row, col), entry in entries.items():
                entry.installEventFilter(self)
                entry.textChanged.connect(lambda texte, r=row, c=col: self.on_value_enter(r, c))
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
        self.worker.quit()
        self.worker.wait()
        
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
                row = case[0]
                col = case[1]
                valeur_init = case[2]
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
        
        
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.FocusIn:
            entries = self.view.get_grille_widget().get_entries()
            for (row, col), entry in entries.items():
                if entry is obj:
                    self.case_selectionnee = (row, col)
                    self.view.get_grille_widget().surligner_selection(row, col)
                    break

        elif event.type() == QEvent.Type.KeyPress:
            entries = self.view.get_grille_widget().get_entries()
            if event.key() == Qt.Key.Key_Delete:
                self.on_delete()
                return True
            # Flèches directionnelles#
            if self.case_selectionnee is not None:
                row, col = self.case_selectionnee
                if event.key() == Qt.Key.Key_Up and (row - 1, col) in entries:
                    entries[(row - 1, col)].setFocus()
                    return True
                elif event.key() == Qt.Key.Key_Down and (row + 1, col) in entries:
                    entries[(row + 1, col)].setFocus()
                    return True
                elif event.key() == Qt.Key.Key_Left and (row, col - 1) in entries:
                    entries[(row, col - 1)].setFocus()
                    return True
                elif event.key() == Qt.Key.Key_Right and (row, col + 1) in entries:
                    entries[(row, col + 1)].setFocus()
                    return True

        return False

    def on_value_enter(self, row, col):
        """Gère la saisie d'une valeur dans une case et valide en temps réel.

        Args:
            row (int): Ligne de la case modifiée.
            col (int): Colonne de la case modifiée.

        """

        # Auto-avance : passer à la prochaine case vide#
        entries = self.view.get_grille_widget().get_entries()
        entry = entries.get((row, col))
        texte = entry.text()
        if not texte:  # case vide, ne rien faire#
            return
        if texte.isdigit() and (int(texte) > 5 or int(texte) == 0):
            entry.clear()
            return
        
        if entry is not None and entry.text().isdigit() and int(entry.text()) != 0:
            # Chercher la prochaine case vide après celle-ci#
            positions = sorted(entries.keys())
            idx = positions.index((row, col))
            for i in range(idx + 1, len(positions)):
                prochaine = entries[positions[i]]
                if not prochaine.text().isdigit() or int(prochaine.text()) == 0:
                    prochaine.setFocus()
                    # Lancer la vérification de voisinage automatiquement#
                    self.on_verifier_voisinage()
                    return
            # Si rien après, chercher depuis le début#
            for i in range(0, idx):
                prochaine = entries[positions[i]]
                if not prochaine.text().isdigit() or int(prochaine.text()) == 0:
                    prochaine.setFocus()
                    self.on_verifier_voisinage()

                    return
        self.on_verifier_voisinage()

        
                
        

    def on_delete(self):
        """Efface la valeur de la case actuellement sélectionnée.
         Si une case est sélectionnée, son contenu est effacé et le focus est maintenu sur cette case.

        Attributes: case_selectionnee (tuple): Les coordonnées (row, col) de la case actuellement sélectionnée.
        """
        if self.case_selectionnee is not None:
            entries = self.view.get_grille_widget().get_entries()
            entry = entries.get(self.case_selectionnee)
            if entry is not None:
                entry.clear()