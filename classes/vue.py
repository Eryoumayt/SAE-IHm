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
        chemin_police = os.path.join(os.path.dirname(__file__), "fonts", "LuckiestGuy-Regular.ttf")
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
                    # case avec valeur initiale : lecture seule#
                    label = QLabel(str(valeur))
                    label.setFixedSize(TAILLE_CASE, TAILLE_CASE)
                    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    label.setFont(self.__police_case_gras)
                    label.setStyleSheet(style)
                    self.__layout.addWidget(label, row, col)
                else:
                    # case vide#
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
        '''
        Surligne la case selectionnee en bleu clair.
        Remet les autres cases editables en couleur normale.
        '''
        for (r, c), entry in self.__entries.items():
            if r == row and c == col:
                entry.setStyleSheet(entry.styleSheet() + "background-color: #cce5ff;")
            # les autres gardent leur couleur par defaut #

    # -------------------------------------------------------- #

    def surligner_conflits(self, conflits: set):
        '''
        Surligne les cases en conflit en rouge.
        '''
        for (row, col) in conflits:
            entry = self.__entries.get((row, col))
            if entry is not None:
                entry.setStyleSheet(entry.styleSheet() + "background-color: #ff9999;")

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
        self.setWindowTitle("Neonaure")

        # données brutes de la grille chargée#
        self.__grille_data = None
        # thème sombre activé ou non#
        self.__theme_sombre = False

        # Appliquer le thème clair au démarrage
        chemin_clair = os.path.join(os.path.dirname(__file__), "theme_clair.qss")
        with open(chemin_clair, 'r', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

        # chargement des polices #
        # Luckiest Guy pour le titre NEONAURE #
        chemin_luckiest = os.path.join(os.path.dirname(__file__), "fonts", "LuckiestGuy-Regular.ttf")
        chemin_luckiest = os.path.join(os.path.dirname(__file__), "fonts", "LuckiestGuy-Regular.ttf")
        if os.path.exists(chemin_luckiest):
            font_id_luck = QFontDatabase.addApplicationFont(chemin_luckiest)
            self.__police_titre = QFont("Luckiest Guy", 48) if font_id_luck != -1 else QFont("Arial", 48, QFont.Weight.Bold)
        else:
            self.__police_titre = QFont("Arial", 48, QFont.Weight.Bold)

        chemin_techno = os.path.join(os.path.dirname(__file__), "fonts", "TECHNOLOGY.otf")
        if os.path.exists(chemin_techno):
            font_id_techno = QFontDatabase.addApplicationFont(chemin_techno)
            self.__police_chrono = QFont("TECHNOLOGY", 32) if font_id_techno != -1 else QFont("Arial", 32, QFont.Weight.Bold)
        else:
            self.__police_chrono = QFont("Arial", 32, QFont.Weight.Bold)

        # titre NEONAURE! en jaune #
        self.__label_titre = QLabel("NEONAURE!")
        self.__label_titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__label_titre.setFont(self.__police_titre)
        self.__label_titre.setStyleSheet("color: #FFFF00; background-color: transparent;")

        # chrono pour mesurer le temps de jeu#
        self.__temps = 0
        self.__chrono = QTimer(self)
        self.__chrono.timeout.connect(self.__incrementer)
        self.__label_chrono = QLabel("00:00")
        self.__label_chrono.setFont(self.__police_chrono)
        self.__label_chrono.setFixedSize(150, 60)
        self.__label_chrono.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__label_chrono.setStyleSheet("color: #FFFF00; background-color: transparent;")

        # menu lateral a gauche de la grille#
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

        self.__action_verifier = QAction("Verifier la solution", self)
        menu_jeu.addAction(self.__action_verifier)

        self.__action_verifier_voisinage = QAction("Verifier le voisinage", self)
        menu_jeu.addAction(self.__action_verifier_voisinage)

        self.__action_resoudre = QAction("Resoudre", self)
        menu_jeu.addAction(self.__action_resoudre)

        self.__action_nouvelle = QAction("Nouvelle partie", self)
        menu_jeu.addAction(self.__action_nouvelle)

        # menu apparence#
        menu_apparence = menubar.addMenu("Apparence")

        action_clair = QAction("Theme clair", self)
        # applique le thème clair sur toute la fenêtre#
        chemin_clair = os.path.join(os.path.dirname(__file__), "theme_clair.qss")
        action_clair.triggered.connect(lambda: self.__appliquer_theme(chemin_clair))
        menu_apparence.addAction(action_clair)

        action_sombre = QAction("Theme sombre", self)
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

        # détermine si c'est le thème sombre#
        self.__theme_sombre = "sombre" in chemin_qss

        # applique le theme au menu lateral#
        self.__menu_gauche.appliquer_theme(self.__theme_sombre)

        # met a jour les couleurs du titre et du chrono#
        if self.__theme_sombre:
            self.__label_titre.setStyleSheet("color: #FFFF00; background-color: transparent;")
            self.__label_chrono.setStyleSheet("color: #FFFF00; background-color: transparent;")
        else:
            self.__label_titre.setStyleSheet("color: #FFFF00; background-color: transparent;")
            self.__label_chrono.setStyleSheet("color: #FFFF00; background-color: transparent;")

        # re-rend la grille si une grille est chargée#
        if self.__grille_data is not None:
            self.__grille_widget.afficher(self.__grille_data, self.__theme_sombre)

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
            self.__grille_widget.afficher(self.__grille_data, self.__theme_sombre)
            self.afficher_grille_centree()

    def afficher_grille_centree(self):
        '''
        Affiche la grille au centre de la fenetre avec le titre au-dessus,
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
        '''
        Retourne a l'ecran d'accueil, cache la grille et le menu.
        '''
        self.__grille_data = None
        self.__label_accueil = QLabel("Bienvenue dans Neonaure !\nChargez une grille via le menu Fichier.")
        self.__label_accueil.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__label_accueil.setFont(self.__police_titre)
        self.__label_accueil.setStyleSheet("color: #FFFF00; background-color: transparent; font-size: 36px;")
        self.setCentralWidget(self.__label_accueil)

    def __sauvegarder_grille(self):
        '''
        sauvegarde l'état actuel de la grille dans un fichier JSON.
        '''
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
            QMessageBox.information(self, "Succes", "Grille sauvegardee.")


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

    def get_action_verifier_voisinage(self):
        # renvoie l'action vérifier voisinage pour le contrôleur#
        return self.__action_verifier_voisinage

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

    def get_label_titre(self):
        # renvoie le label titre NEONAURE!#
        return self.__label_titre

    def get_theme_sombre(self):
        # renvoie si le thème sombre est activé#
        return self.__theme_sombre

    def get_menu_droit(self) -> MenuDroit:
        # renvoie le menu lateral gauche#
        return self.__menu_droit