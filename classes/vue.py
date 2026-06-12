import sys
import os
import json
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QLabel, QFileDialog, QWidget, QGridLayout, QLineEdit, QMessageBox
from PyQt6.QtGui import QAction, QFont, QIntValidator
from PyQt6.QtCore import Qt, QTimer

TAILLE_CASE = 60

#----- grille du jeu -----#

class GrilleWidget(QWidget):
    '''
    affiche la grille de jeu.
    '''

    def __init__(self):
        super().__init__()

        #place les cases par ligne et colonne#
        self.__layout = QGridLayout()
        self.__layout.setSpacing(0)
        self.__layout.setContentsMargins(0, 0, 0, 0)

        # aligne la grille en haut à gauche pour éviter l'étirement en plein écran#
        self.__layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.setLayout(self.__layout)

        #QLineEdit pour les cases éditables#
        self.__entries = {}

    # -------------------------------------------------------- #

    def afficher(self, grille_data: dict):
        self.__vider()
        self.__entries = {}

        # calcule les bordures entre motifs différents#
        carte_motifs = {}
        for idx, cases in enumerate(grille_data.values()):
            for case in cases:
                carte_motifs[(case[0], case[1])] = idx

        # parcourt chaque motif et crée un widget pour chaque case#
        for idx, cases in enumerate(grille_data.values()):
            for case in cases:
                row = case[0]
                col = case[1]
                valeur_init = case[2]
                # Si 4 éléments, on récupère la valeur du joueur, sinon 0#
                valeur_joueur = case[3] if len(case) == 4 else 0

                # bordure épaisse si le voisin appartient à un motif différent#
                top    = "3px solid black" if carte_motifs.get((row-1, col), -1) != idx else "1px solid gray"
                bottom = "3px solid black" if carte_motifs.get((row+1, col), -1) != idx else "1px solid gray"
                left   = "3px solid black" if carte_motifs.get((row, col-1), -1) != idx else "1px solid gray"
                right  = "3px solid black" if carte_motifs.get((row, col+1), -1) != idx else "1px solid gray"

                style = (
                    f"background-color: lightgray;"
                    f"border-top: {top}; border-bottom: {bottom};"
                    f"border-left: {left}; border-right: {right};"
                )

                if valeur_init != 0:
                    # case avec valeur initiale : lecture seule#
                    label = QLabel(str(valeur_init))
                    label.setFixedSize(TAILLE_CASE, TAILLE_CASE)
                    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
                    label.setStyleSheet(style)
                    self.__layout.addWidget(label, row, col)
                else:
                    # case vide ou avec valeur du joueur : éditable#
                    entry = QLineEdit()
                    entry.setFixedSize(TAILLE_CASE, TAILLE_CASE)
                    entry.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    entry.setFont(QFont("Arial", 16))
                    entry.setMaxLength(1)
                    entry.setValidator(QIntValidator(1, 5))
                    entry.setStyleSheet(style)
                    # Si le joueur avait tapé une valeur, la restaurer#
                    if valeur_joueur != 0:
                        entry.setText(str(valeur_joueur))
                    self.__layout.addWidget(entry, row, col)
                    self.__entries[(row, col)] = entry
                        
    def surligner_conflits(self, conflits):
        """Surligne en rouge les cases en conflit de voisinage.

        Args:
            conflits (set): Ensemble de tuples (row, col) des cases en conflit.
        """
        # D'abord remettre toutes les cases en style normal#
        for (row, col), entry in self.__entries.items():
            self.__reset_style(entry)

        # Puis mettre en rouge les cases en conflit#
        for (row, col) in conflits:
            entry = self.__entries.get((row, col))
            if entry is not None:
                entry.setStyleSheet(entry.styleSheet() + "background-color: red;")
                
    def surligner_selection(self, row, col):
        """Surligne la case sélectionnée en bleu clair.

        Args:
            row (int): Ligne de la case à sélectionner.
            col (int): Colonne de la case à sélectionner.
        """
        # D'abord enlever l'ancienne sélection#
        self.__deselectionner()
        entry = self.__entries.get((row, col))
        if entry is not None:
            entry.setStyleSheet(entry.styleSheet() + "background-color: #ADD8E6;")

    def __deselectionner(self):
        """Remet toutes les cases en fond normal."""
        for (row, col), entry in self.__entries.items():
            style_actuel = entry.styleSheet()
            nouveau_style = style_actuel.replace("background-color: #ADD8E6;", "background-color: lightgray;")
            nouveau_style = nouveau_style.replace("background-color: red;", "background-color: lightgray;")
            entry.setStyleSheet(nouveau_style)

    def __reset_style(self, entry):
        """Remet le fond d'une case à la couleur par défaut.

        Args:
            entry (QLineEdit): La case à réinitialiser.
        """
        style_actuel = entry.styleSheet()
        nouveau_style = style_actuel.replace("background-color: red;", "background-color: lightgray;")
        entry.setStyleSheet(nouveau_style)               
       
    # -------------------------------------------------------- #

    def __vider(self):
        '''
        Supprime tous les widgets de la grille.
        '''
        # prend le premier widget du layout et le supprime, jusqu'à ce qu'il soit vide#
        while self.__layout.count():
            item = self.__layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def nouvelle_partie(self):
        '''
        Remet à zéro toutes les cases saisies par le joueur.
        '''
        for entry in self.__entries.values():
            entry.clear()

    # -------------------------------------------------------- #

    def get_entries(self) -> dict:
        # Renvoie le dictionnaire des cases éditables
        return self.__entries


# ------- vue principal-------- #

class Vue(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Néonaure")

        # données brutes de la grille chargée#
        self.__grille_data = None
        # chrono pour mesurer le temps de jeu#
        self.__temps = 0
        self.__chrono = QTimer(self)
        self.__chrono.timeout.connect(self.__incrementer)
        self.__label_chrono = QLabel("00:00")

        # label d'accueil affiché au démarrage#
        self.__label_accueil = QLabel("Bienvenue dans Néonaure !\nChargez une grille via le menu Fichier.")
        self.__label_accueil.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(self.__label_accueil)

        # composant grille, pas encore affiché#
        self.__grille_widget = GrilleWidget()
        self.__creer_menu()

    # ------------------- menu ------------------#

    def __creer_menu(self):
        menubar = self.menuBar()

        #  menu fichier#
        menu_fichier = menubar.addMenu("Fichier")

        self.__action_charger = QAction("Charger une grille", self)
        menu_fichier.addAction(self.__action_charger)
        self.__action_charger.setShortcut("Ctrl+O")


        self.__action_sauvegarder = QAction("Sauvegarder la grille", self)
        menu_fichier.addAction(self.__action_sauvegarder)
        self.__action_sauvegarder.setShortcut("Ctrl+S")


        menu_fichier.addSeparator()

        self.__action_quitter = QAction("Quitter", self)
        self.__action_quitter.triggered.connect(self.close)
        menu_fichier.addAction(self.__action_quitter)

        #  menu jeu#
        menu_jeu = menubar.addMenu("Jeu")

        self.__action_verifier = QAction("Vérifier la solution", self)
        menu_jeu.addAction(self.__action_verifier)
        self.__action_verifier.setShortcut("Ctrl+V")


        self.__action_resoudre = QAction("Résoudre", self)
        menu_jeu.addAction(self.__action_resoudre)
        self.__action_resoudre.setShortcut("Ctrl+R")


        self.__action_nouvelle = QAction("Nouvelle partie", self)
        menu_jeu.addAction(self.__action_nouvelle)
        self.__action_nouvelle.setShortcut("Ctrl+N")


        # menu apparence#
        menu_apparence = menubar.addMenu("Apparence")

        action_clair = QAction("Thème clair", self)
        # applique le thème clair sur toute la fenêtre#
        chemin_clair = os.path.join(os.path.dirname(__file__), "theme_clair.qss")
        action_clair.triggered.connect(lambda: self.__appliquer_theme(chemin_clair))
        menu_apparence.addAction(action_clair)

        action_sombre = QAction("Thème sombre", self)
        # applique le thème sombre sur toute la fenêtre#
        chemin_sombre = os.path.join(os.path.dirname(__file__), "theme_sombre.qss")
        action_sombre.triggered.connect(lambda: self.__appliquer_theme(chemin_sombre))
        menu_apparence.addAction(action_sombre)

    #--------------- action fichier ----------------- #

    def __appliquer_theme(self, chemin_qss: str):
        '''
        Applique un thème QSS sur toute la fenêtre à partir d'un fichier .qss.
        '''
        with open(chemin_qss, 'r', encoding='utf-8') as f:
            qss = f.read()
        # setStyleSheet applique le style sur la fenêtre et tous ses enfants#
        self.setStyleSheet(qss)


    def __incrementer(self):
        self.__temps += 1
        minutes = self.__temps // 60
        secondes = self.__temps % 60
        self.__label_chrono.setText(f"{minutes:02d}:{secondes:02d}")

    def demarrer_chrono(self):
        self.__temps = 0
        self.__label_chrono.setText("00:00")
        self.__chrono.start(1000)  # toutes les 1000ms = 1s

    def arreter_chrono(self):
        self.__chrono.stop()

    def reinitialiser_chrono(self):
        self.__chrono.stop()
        self.__temps = 0
        self.__label_chrono.setText("00:00")

    #-----------getter-----------------#


    def get_grille_widget(self) -> GrilleWidget:
        # renvoie le composant grille#
        return self.__grille_widget

    def get_action_charger(self):
        # renvoie l'action charger pour le contrôleur#
        return self.__action_charger

    def get_action_sauvegarder(self):
        # renvoie l'action sauvegarder pour le contrôleur#
        return self.__action_sauvegarder

    def get_action_verifier(self):
        # renvoie l'action vérifier pour le contrôleur#
        return self.__action_verifier

    def get_action_resoudre(self):
        # renvoie l'action résoudre pour le contrôleur#
        return self.__action_resoudre

    def get_action_nouvelle(self):
        # renvoie l'action nouvelle partie pour le contrôleur#
        return self.__action_nouvelle

    def get_label_chrono(self):
        return self.__label_chrono
    