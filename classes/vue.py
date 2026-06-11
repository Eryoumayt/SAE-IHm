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
        for idx, cases in enumerate(grille_data.values()): #donne un index a chaque motif et associe les cases a cet index#
            for case in cases:
                carte_motifs[(case[0], case[1])] = idx

        # parcourt chaque motif et crée un widget pour chaque case#
        for idx, cases in enumerate(grille_data.values()):
            for case in cases:
                row = case[0]
                col = case[1]
                valeur = case[2]

                # bordure épaisse si le voisin appartient à un motif différent#
                # Si l'index du motif n'existe pas:  retourne -1#
                #est-ce que cet index est différent du motif actuel ? Si oui : bordure épaisse ; Si non : bordure fine #
                top    = "3px solid black" if carte_motifs.get((row-1, col), -1) != idx else "1px solid gray"
                bottom = "3px solid black" if carte_motifs.get((row+1, col), -1) != idx else "1px solid gray"
                left   = "3px solid black" if carte_motifs.get((row, col-1), -1) != idx else "1px solid gray"
                right  = "3px solid black" if carte_motifs.get((row, col+1), -1) != idx else "1px solid gray"

                style = (
                    f"background-color: lightgray;"
                    f"border-top: {top}; border-bottom: {bottom};"
                    f"border-left: {left}; border-right: {right};"
                )

                if valeur != 0:
                    # case avec valeur initiale : lecture seule#
                    label = QLabel(str(valeur))
                    label.setFixedSize(TAILLE_CASE, TAILLE_CASE)
                    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
                    label.setStyleSheet(style)
                    self.__layout.addWidget(label, row, col)
                else:
                    # case vide#
                    entry = QLineEdit()
                    entry.setFixedSize(TAILLE_CASE, TAILLE_CASE)
                    entry.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    entry.setFont(QFont("Arial", 16))
                    entry.setMaxLength(1)
                    entry.setValidator(QIntValidator(1, 5))
                    entry.setStyleSheet(style)
                    self.__layout.addWidget(entry, row, col)
                    self.__entries[(row, col)] = entry

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

        self.__action_sauvegarder = QAction("Sauvegarder la grille", self)
        menu_fichier.addAction(self.__action_sauvegarder)

        menu_fichier.addSeparator()

        self.__action_quitter = QAction("Quitter", self)
        self.__action_quitter.triggered.connect(self.close)
        menu_fichier.addAction(self.__action_quitter)

        #  menu jeu#
        menu_jeu = menubar.addMenu("Jeu")

        self.__action_verifier = QAction("Vérifier la solution", self)
        menu_jeu.addAction(self.__action_verifier)

        self.__action_resoudre = QAction("Résoudre", self)
        menu_jeu.addAction(self.__action_resoudre)

        self.__action_nouvelle = QAction("Nouvelle partie", self)
        menu_jeu.addAction(self.__action_nouvelle)

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

    def __charger_grille(self):
        '''
        ouvre un dossier pour charger un fichier JSON.
        '''
        chemin, _ = QFileDialog.getOpenFileName(
            self,
            "Charger une grille",
            "",
            "Fichiers JSON (*.json)"
        )
        if chemin:
            with open(chemin, 'r', encoding='utf-8') as f:
                self.__grille_data = json.load(f)
            self.__label_accueil.hide()
            self.__grille_widget.afficher(self.__grille_data)

            # met la grille au milieu des écrans#
            conteneur = QWidget()
            layout_centre = QHBoxLayout()
            # espace ajustable sur les côtés pour centrer#
            layout_centre.addStretch()
            layout_centre.addWidget(self.__grille_widget)
            layout_centre.addStretch()
            conteneur.setLayout(layout_centre)
            self.setCentralWidget(conteneur)

    def __sauvegarder_grille(self):
        '''
        sauvegarde l'état actuel de la grille dans un fichier JSON.
        '''
        if self.__grille_data is None:
            QMessageBox.warning(self, "Attention", "Aucune grille chargée.")
            return

        entries = self.__grille_widget.get_entries()
        grille_sauvegarde = {}

        for nom_motif, cases in self.__grille_data.items():
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

        chemin, _ = QFileDialog.getSaveFileName(
            self,
            "Sauvegarder la grille",
            "",
            "Fichiers JSON (*.json)"
        )
        if chemin:
            with open(chemin, 'w', encoding='utf-8') as f:
                json.dump(grille_sauvegarde, f, indent=4)
            QMessageBox.information(self, "Succès", "Grille sauvegardée.")


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

    def get_grille_data(self) -> dict:
        # renvoie les données brutes de la grille chargée#
        return self.__grille_data

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

    def get_charger_grille(self):
        # renvoie la méthode charger grille pour le contrôleur#
        return self.__charger_grille

    def get_sauvegarder_grille(self):
        # renvoie la méthode sauvegarder grille pour le contrôleur#
        return self.__sauvegarder_grille

    def get_label_chrono(self):
        return self.__label_chrono
