import sys
import os
import json
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QMainWindow, QLabel, QFileDialog, QWidget, QGridLayout, QLineEdit, QMessageBox
from PyQt6.QtGui import QAction, QFont, QFontDatabase, QIntValidator
from PyQt6.QtCore import Qt, QTimer
from .MenuGauche import MenuGauche

TAILLE_CASE = 60

#----- grille du jeu -----#

class GrilleWidget(QWidget):
    '''
    affiche la grille de jeu.
    '''

    def __init__(self):
        super().__init__()

        # Identifiant pour le QSS
        self.setObjectName("grilleWidget")

        # Bordure jaune
        self.setStyleSheet("""
            #grilleWidget {
                border: 3px solid #FFFF00;
                background-color: transparent;
            }
        """)

        #place les cases par ligne et colonne#
        self.__layout = QGridLayout()
        self.__layout.setSpacing(0)
        self.__layout.setContentsMargins(0, 0, 0, 0)

        # aligne la grille en haut à gauche pour éviter l'étirement en plein écran#
        self.__layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.setLayout(self.__layout)

        #QLineEdit pour les cases éditables#
        self.__entries = {}

        # chargement de la police Luckiest Guy pour les cases #
        chemin_police = os.path.join(os.path.dirname(__file__), "..", "vue", "qss", "LuckiestGuy-Regular.ttf")
        if os.path.exists(chemin_police):
            font_id = QFontDatabase.addApplicationFont(chemin_police)
            self.__police_case = QFont("Luckiest Guy", 18) if font_id != -1 else QFont("Arial", 18, QFont.Weight.Bold)
            self.__police_case_gras = QFont("Luckiest Guy", 18) if font_id != -1 else QFont("Arial", 18, QFont.Weight.Bold)
        else:
            self.__police_case = QFont("Arial", 18, QFont.Weight.Bold)
            self.__police_case_gras = QFont("Arial", 18, QFont.Weight.Bold)

    # -------------------------------------------------------- #

    def afficher(self, grille_data: dict, sombre: bool = False):
        self.__vider()
        self.__entries = {}

        # la grille est toujours blanche avec bordures noires et texte noir #
        fond = "white"
        bordure_fine = "1px solid black"
        bordure_epaisse = "3px solid black"

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
                valeur = case[2]

                top    = bordure_epaisse if carte_motifs.get((row-1, col), -1) != idx else bordure_fine
                bottom = bordure_epaisse if carte_motifs.get((row+1, col), -1) != idx else bordure_fine
                left   = bordure_epaisse if carte_motifs.get((row, col-1), -1) != idx else bordure_fine
                right  = bordure_epaisse if carte_motifs.get((row, col+1), -1) != idx else bordure_fine

                style = (
                    f"background-color: {fond};"
                    f"color: black;"
                    f"border-top: {top}; border-bottom: {bottom};"
                    f"border-left: {left}; border-right: {right};"
                )

                if valeur != 0:
                    label = QLabel(str(valeur))
                    label.setFixedSize(TAILLE_CASE, TAILLE_CASE)
                    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    label.setFont(self.__police_case_gras)
                    label.setStyleSheet(style)
                    self.__layout.addWidget(label, row, col)
                else:
                    entry = QLineEdit()
                    entry.setFixedSize(TAILLE_CASE, TAILLE_CASE)
                    entry.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    entry.setFont(self.__police_case)
                    entry.setMaxLength(1)
                    entry.setValidator(QIntValidator(1, 5))
                    entry.setStyleSheet(style)
                    self.__layout.addWidget(entry, row, col)
                    self.__entries[(row, col)] = entry

    # -------------------------------------------------------- #

    def surligner_selection(self, row: int, col: int):
        for (r, c), entry in self.__entries.items():
            if r == row and c == col:
                entry.setStyleSheet(entry.styleSheet() + "background-color: #cce5ff;")

    # -------------------------------------------------------- #

    def surligner_conflits(self, conflits: set):
        for (row, col) in conflits:
            entry = self.__entries.get((row, col))
            if entry is not None:
                entry.setStyleSheet(entry.styleSheet() + "background-color: #ff9999;")

    # -------------------------------------------------------- #

    def __vider(self):
        while self.__layout.count():
            item = self.__layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def nouvelle_partie(self):
        for entry in self.__entries.values():
            entry.clear()

    # -------------------------------------------------------- #

    def get_entries(self) -> dict:
        return self.__entries


# ------- vue principal-------- #

class Vue(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Neonaure")

        # données brutes de la grille chargée#
        self.__grille_data = None
        # thème sombre activé ou non#
        self.__theme_sombre = False

        # Appliquer le thème clair au démarrage
        chemin_clair = os.path.join(os.path.dirname(__file__), "theme_clair.qss")
        if os.path.exists(chemin_clair):
            with open(chemin_clair, 'r', encoding='utf-8') as f:
                self.setStyleSheet(f.read())

        # chargement de la police Luckiest Guy pour le titre NEONAURE #
        chemin_luckiest = os.path.join(os.path.dirname(__file__), "..", "vue", "qss", "LuckiestGuy-Regular.ttf")
        if os.path.exists(chemin_luckiest):
            font_id_luck = QFontDatabase.addApplicationFont(chemin_luckiest)
            self.__police_titre = QFont("Luckiest Guy", 48) if font_id_luck != -1 else QFont("Arial", 48, QFont.Weight.Bold)
        else:
            self.__police_titre = QFont("Arial", 48, QFont.Weight.Bold)

        # chargement de la police TECHNOLOGY pour le chrono #
        chemin_techno = os.path.join(os.path.dirname(__file__), "..", "vue", "qss", "Technology.ttf")
        if os.path.exists(chemin_techno):
            font_id_techno = QFontDatabase.addApplicationFont(chemin_techno)
            self.__police_chrono = QFont("TECHNOLOGY", 32) if font_id_techno != -1 else QFont("Arial", 32, QFont.Weight.Bold)
        else:
            self.__police_chrono = QFont("Arial", 32, QFont.Weight.Bold)

        # ---- TITRE NEONAURE! en gros jaune Luckiest Guy ---- #
        self.__label_titre = QLabel("NEONAURE!")
        self.__label_titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__label_titre.setFont(self.__police_titre)
        self.__label_titre.setStyleSheet("color: #FFFF00; background-color: transparent;")

        # ---- CHRONO en TECHNOLOGY jaune ---- #
        self.__temps = 0
        self.__chrono = QTimer(self)
        self.__chrono.timeout.connect(self.__incrementer)
        self.__label_chrono = QLabel("00:00")
        self.__label_chrono.setFont(self.__police_chrono)
        self.__label_chrono.setFixedSize(150, 60)
        self.__label_chrono.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__label_chrono.setStyleSheet("color: #FFFF00; background-color: transparent;")

        # menu lateral gauche#
        self.__menu_gauche = MenuGauche()

        # label d'accueil affiché au démarrage#
        self.__label_accueil = QLabel("Bienvenue dans Neonaure !\nChargez une grille via le menu Fichier.")
        self.__label_accueil.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__label_accueil.setFont(self.__police_titre)
        self.__label_accueil.setStyleSheet("color: #FFFF00; background-color: transparent; font-size: 36px;")
        self.setCentralWidget(self.__label_accueil)

        # composant grille, pas encore affiché#
        self.__grille_widget = GrilleWidget()
        self.__creer_menu()

    # ------------------- menu ------------------#

    def __creer_menu(self):
        menubar = self.menuBar()

        menu_fichier = menubar.addMenu("Fichier")

        self.__action_charger = QAction("Charger une grille", self)
        menu_fichier.addAction(self.__action_charger)

        self.__action_sauvegarder = QAction("Sauvegarder la grille", self)
        menu_fichier.addAction(self.__action_sauvegarder)

        menu_fichier.addSeparator()

        self.__action_quitter = QAction("Quitter", self)
        self.__action_quitter.triggered.connect(self.close)
        menu_fichier.addAction(self.__action_quitter)

        menu_jeu = menubar.addMenu("Jeu")

        self.__action_verifier = QAction("Verifier la solution", self)
        menu_jeu.addAction(self.__action_verifier)

        self.__action_verifier_voisinage = QAction("Verifier le voisinage", self)
        menu_jeu.addAction(self.__action_verifier_voisinage)

        self.__action_resoudre = QAction("Resoudre", self)
        menu_jeu.addAction(self.__action_resoudre)

        self.__action_nouvelle = QAction("Nouvelle partie", self)
        menu_jeu.addAction(self.__action_nouvelle)

        menu_apparence = menubar.addMenu("Apparence")

        action_clair = QAction("Theme clair", self)
        chemin_clair = os.path.join(os.path.dirname(__file__), "theme_clair.qss")
        action_clair.triggered.connect(lambda: self.__appliquer_theme(chemin_clair))
        menu_apparence.addAction(action_clair)

        action_sombre = QAction("Theme sombre", self)
        chemin_sombre = os.path.join(os.path.dirname(__file__), "theme_sombre.qss")
        action_sombre.triggered.connect(lambda: self.__appliquer_theme(chemin_sombre))
        menu_apparence.addAction(action_sombre)

    #--------------- action fichier ----------------- #

    def __appliquer_theme(self, chemin_qss: str):
        with open(chemin_qss, 'r', encoding='utf-8') as f:
            qss = f.read()
        self.setStyleSheet(qss)

        self.__theme_sombre = "sombre" in chemin_qss
        self.__menu_gauche.appliquer_theme(self.__theme_sombre)

        if self.__theme_sombre:
            self.__label_titre.setStyleSheet("color: #FFFF00; background-color: transparent;")
            self.__label_chrono.setStyleSheet("color: #FFFF00; background-color: transparent;")
        else:
            self.__label_titre.setStyleSheet("color: #FFFF00; background-color: transparent;")
            self.__label_chrono.setStyleSheet("color: #FFFF00; background-color: transparent;")

        if self.__grille_data is not None:
            self.__grille_widget.afficher(self.__grille_data, self.__theme_sombre)

    def __charger_grille(self):
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
            self.__grille_widget.afficher(self.__grille_data, self.__theme_sombre)
            self.afficher_grille_centree()

    def afficher_grille_centree(self):
        '''
        Affiche la grille au centre avec le titre NEONAURE! au-dessus,
        le menu a gauche et le chrono a droite.
        '''
        conteneur = QWidget()
        layout_principal = QHBoxLayout()
        # menu lateral a gauche#
        layout_principal.addWidget(self.__menu_gauche, alignment=Qt.AlignmentFlag.AlignTop)
        # espace pour centrer la grille#
        layout_principal.addStretch()
        # colonne centrale : titre + grille #
        layout_centre = QVBoxLayout()
        layout_centre.addWidget(self.__label_titre, alignment=Qt.AlignmentFlag.AlignCenter)
        layout_centre.addWidget(self.__grille_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        layout_centre.addStretch()
        layout_principal.addLayout(layout_centre)
        # espace entre la grille et le chrono#
        layout_principal.addStretch()
        # chrono a droite, aligne en haut#
        layout_principal.addWidget(self.__label_chrono, alignment=Qt.AlignmentFlag.AlignTop)
        conteneur.setLayout(layout_principal)
        self.setCentralWidget(conteneur)

    def retour_accueil(self):
        self.__grille_data = None
        self.__label_accueil = QLabel("Bienvenue dans Neonaure !\nChargez une grille via le menu Fichier.")
        self.__label_accueil.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__label_accueil.setFont(self.__police_titre)
        self.__label_accueil.setStyleSheet("color: #FFFF00; background-color: transparent; font-size: 36px;")
        self.setCentralWidget(self.__label_accueil)

    def __sauvegarder_grille(self):
        if self.__grille_data is None:
            QMessageBox.warning(self, "Attention", "Aucune grille chargee.")
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
            QMessageBox.information(self, "Succes", "Grille sauvegardee.")

    def __incrementer(self):
        self.__temps += 1
        minutes = self.__temps // 60
        secondes = self.__temps % 60
        self.__label_chrono.setText(f"{minutes:02d}:{secondes:02d}")

    def demarrer_chrono(self):
        self.__temps = 0
        self.__label_chrono.setText("00:00")
        self.__chrono.start(1000)

    def arreter_chrono(self):
        self.__chrono.stop()

    def reinitialiser_chrono(self):
        self.__chrono.stop()
        self.__temps = 0
        self.__label_chrono.setText("00:00")

    #-----------getter-----------------#

    def get_grille_data(self) -> dict:
        return self.__grille_data

    def get_grille_widget(self) -> GrilleWidget:
        return self.__grille_widget

    def get_action_charger(self):
        return self.__action_charger

    def get_action_sauvegarder(self):
        return self.__action_sauvegarder

    def get_action_verifier(self):
        return self.__action_verifier

    def get_action_verifier_voisinage(self):
        return self.__action_verifier_voisinage

    def get_action_resoudre(self):
        return self.__action_resoudre

    def get_action_nouvelle(self):
        return self.__action_nouvelle

    def get_charger_grille(self):
        return self.__charger_grille

    def get_sauvegarder_grille(self):
        return self.__sauvegarder_grille

    def get_label_chrono(self):
        return self.__label_chrono

    def get_label_titre(self):
        return self.__label_titre

    def get_theme_sombre(self):
        return self.__theme_sombre

    def get_menu_gauche(self) -> MenuGauche:
        return self.__menu_gauche