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
    """Affiche la grille de jeu."""

    def __init__(self):
        super().__init__()
        self.setObjectName("grilleWidget")
        self.setStyleSheet("""
            #grilleWidget {
                border: 3px solid #FFFF00;
                background-color: transparent;
            }
        """)

        self.__layout = QGridLayout()
        self.__layout.setSpacing(0)
        self.__layout.setContentsMargins(0, 0, 0, 0)
        self.__layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.setLayout(self.__layout)
        self.__entries = {}
        self.__fond_courant = "white"

        # Chargement de la police Luckiest Guy pour les cases
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
        """Affiche la grille à partir des données JSON.
        
        Args:
            grille_data (dict): Les données de la grille.
            sombre (bool): Si True, utilise le thème sombre pour les cases.
        """
        self.__vider()
        self.__entries = {}

        if sombre:
            fond = "#2d2d2d"
            couleur_texte = "white"
            bordure_fine = "1px solid #555"
            bordure_epaisse = "3px solid #888"
        else:
            fond = "white"
            couleur_texte = "black"
            bordure_fine = "1px solid black"
            bordure_epaisse = "3px solid black"

        self.__fond_courant = fond

        # Calcule les bordures entre motifs différents
        carte_motifs = {}
        for idx, cases in enumerate(grille_data.values()):
            for case in cases:
                carte_motifs[(case[0], case[1])] = idx

        # Parcourt chaque motif et crée un widget pour chaque case
        for idx, cases in enumerate(grille_data.values()):
            for case in cases:
                row = case[0]
                col = case[1]
                valeur_init = case[2]
                # Si 4 éléments, on récupère la valeur du joueur, sinon 0
                valeur_joueur = case[3] if len(case) == 4 else 0

                top    = bordure_epaisse if carte_motifs.get((row-1, col), -1) != idx else bordure_fine
                bottom = bordure_epaisse if carte_motifs.get((row+1, col), -1) != idx else bordure_fine
                left   = bordure_epaisse if carte_motifs.get((row, col-1), -1) != idx else bordure_fine
                right  = bordure_epaisse if carte_motifs.get((row, col+1), -1) != idx else bordure_fine

                style = (
                    f"background-color: {fond};"
                    f"color: {couleur_texte};"
                    f"border-top: {top}; border-bottom: {bottom};"
                    f"border-left: {left}; border-right: {right};"
                )

                if valeur_init != 0:
                    # Case avec valeur initiale : lecture seule
                    label = QLabel(str(valeur_init))
                    label.setFixedSize(TAILLE_CASE, TAILLE_CASE)
                    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    label.setFont(self.__police_case_gras)
                    label.setStyleSheet(style)
                    self.__layout.addWidget(label, row, col)
                else:
                    # Case vide ou avec valeur du joueur : éditable
                    entry = QLineEdit()
                    entry.setFixedSize(TAILLE_CASE, TAILLE_CASE)
                    entry.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    entry.setFont(self.__police_case)
                    entry.setMaxLength(1)
                    entry.setValidator(QIntValidator(1, 5))
                    entry.setStyleSheet(style)
                    # Si le joueur avait tapé une valeur, la restaurer
                    if valeur_joueur != 0:
                        entry.setText(str(valeur_joueur))
                    self.__layout.addWidget(entry, row, col)
                    self.__entries[(row, col)] = entry

    # -------------------------------------------------------- #

    def surligner_conflits(self, conflits: set):
        """Surligne en rouge les cases en conflit de voisinage.

        Args:
            conflits (set): Ensemble de tuples (row, col) des cases en conflit.
        """
        # D'abord remettre toutes les cases en style normal
        for (row, col), entry in self.__entries.items():
            self.__reset_style(entry)
        # Couleur de conflit adaptée au thème
        couleur_conflit = "#8b3a3a" if self.__fond_courant != "white" else "#ff9999"
        # Puis mettre en rouge les cases en conflit
        for (row, col) in conflits:
            entry = self.__entries.get((row, col))
            if entry is not None:
                entry.setStyleSheet(entry.styleSheet() + f"background-color: {couleur_conflit};")

    def surligner_selection(self, row: int, col: int):
        """Surligne la case sélectionnée en bleu clair.

        Args:
            row (int): Ligne de la case à sélectionner.
            col (int): Colonne de la case à sélectionner.
        """
        self.__deselectionner()
        entry = self.__entries.get((row, col))
        if entry is not None:
            couleur_sel = "#3a5f8a" if self.__fond_courant != "white" else "#cce5ff"
            entry.setStyleSheet(entry.styleSheet() + f"background-color: {couleur_sel};")

    def __deselectionner(self):
        """Remet toutes les cases en fond normal."""
        for (row, col), entry in self.__entries.items():
            style_actuel = entry.styleSheet()
            nouveau_style = style_actuel
            for couleur in ["#cce5ff", "#3a5f8a", "#ff9999", "#8b3a3a"]:
                nouveau_style = nouveau_style.replace(f"background-color: {couleur};", f"background-color: {self.__fond_courant};")
            entry.setStyleSheet(nouveau_style)

    def __reset_style(self, entry):
        """Remet le fond d'une case à la couleur par défaut.

        Args:
            entry (QLineEdit): La case à réinitialiser.
        """
        style_actuel = entry.styleSheet()
        nouveau_style = style_actuel
        for couleur in ["#ff9999", "#8b3a3a"]:
            nouveau_style = nouveau_style.replace(f"background-color: {couleur};", f"background-color: {self.__fond_courant};")
        entry.setStyleSheet(nouveau_style)

    # -------------------------------------------------------- #

    def __vider(self):
        """Supprime tous les widgets de la grille."""
        while self.__layout.count():
            item = self.__layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def nouvelle_partie(self):
        """Remet à zéro toutes les cases saisies par le joueur."""
        for entry in self.__entries.values():
            entry.clear()

    # -------------------------------------------------------- #

    def get_entries(self) -> dict:
        """Renvoie le dictionnaire des cases éditables."""
        return self.__entries


# ------- vue principale -------- #

class Vue(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Néonaure")

        # Données brutes de la grille chargée
        self.__grille_data = None
        # Thème sombre activé ou non
        self.__theme_sombre = False

        # Appliquer le thème clair au démarrage
        chemin_clair = os.path.join(os.path.dirname(__file__), "theme_clair.qss")
        if os.path.exists(chemin_clair):
            with open(chemin_clair, 'r', encoding='utf-8') as f:
                self.setStyleSheet(f.read())

        # Chargement de la police Luckiest Guy pour le titre NEONAURE
        chemin_luckiest = os.path.join(os.path.dirname(__file__), "..", "vue", "qss", "LuckiestGuy-Regular.ttf")
        if os.path.exists(chemin_luckiest):
            font_id_luck = QFontDatabase.addApplicationFont(chemin_luckiest)
            self.__police_titre = QFont("Luckiest Guy", 48) if font_id_luck != -1 else QFont("Arial", 48, QFont.Weight.Bold)
        else:
            self.__police_titre = QFont("Arial", 48, QFont.Weight.Bold)

        # Chargement de la police TECHNOLOGY pour le chrono
        chemin_techno = os.path.join(os.path.dirname(__file__), "..", "vue", "qss", "Technology.ttf")
        if os.path.exists(chemin_techno):
            font_id_techno = QFontDatabase.addApplicationFont(chemin_techno)
            self.__police_chrono = QFont("TECHNOLOGY", 32) if font_id_techno != -1 else QFont("Arial", 32, QFont.Weight.Bold)
        else:
            self.__police_chrono = QFont("Arial", 32, QFont.Weight.Bold)

        # Titre NEONAURE!
        self.__label_titre = QLabel("NEONAURE!")
        self.__label_titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__label_titre.setFont(self.__police_titre)
        self.__label_titre.setStyleSheet("color: #FFFF00; background-color: transparent;")

        # Chrono
        self.__temps = 0
        self.__chrono = QTimer(self)
        self.__chrono.timeout.connect(self.__incrementer)
        self.__label_chrono = QLabel("00:00")
        self.__label_chrono.setFont(self.__police_chrono)
        self.__label_chrono.setFixedSize(150, 60)
        self.__label_chrono.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__label_chrono.setStyleSheet("color: #FFFF00; background-color: transparent;")

        # Menu latéral gauche
        self.__menu_gauche = MenuGauche()

        # Label d'accueil affiché au démarrage
        self.__label_accueil = QLabel("Bienvenue dans Néonaure !\nCliquez sur Nouvelle Partie pour commencer.")
        self.__label_accueil.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__label_accueil.setFont(self.__police_titre)
        self.__label_accueil.setStyleSheet("color: #FFFF00; background-color: transparent; font-size: 36px;")

        # Composant grille, pas encore affiché
        self.__grille_widget = GrilleWidget()

        # ===== Layout PERMANENT (construit une seule fois) =====
        self.__conteneur = QWidget()
        self.__layout_principal = QHBoxLayout()

        # Gauche : menu latéral
        self.__layout_principal.addWidget(self.__menu_gauche, alignment=Qt.AlignmentFlag.AlignTop)

        # Espace
        self.__layout_principal.addStretch()

        # Centre : titre + (accueil OU grille)
        self.__layout_centre = QVBoxLayout()
        self.__layout_centre.addWidget(self.__label_titre, alignment=Qt.AlignmentFlag.AlignCenter)
        self.__layout_centre.addWidget(self.__label_accueil, alignment=Qt.AlignmentFlag.AlignCenter)
        self.__layout_centre.addWidget(self.__grille_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        self.__layout_centre.addStretch()
        self.__layout_principal.addLayout(self.__layout_centre)

        # Espace
        self.__layout_principal.addStretch()

        # Droite : chrono
        self.__layout_principal.addWidget(self.__label_chrono, alignment=Qt.AlignmentFlag.AlignTop)

        self.__conteneur.setLayout(self.__layout_principal)
        self.setCentralWidget(self.__conteneur)

        # État initial : afficher l'accueil, cacher le jeu
        self.__label_accueil.show()
        self.__grille_widget.hide()
        self.__label_titre.hide()
        self.__label_chrono.hide()

        self.__creer_menu()

    # ------------------- menu bar ------------------#

    def __creer_menu(self):
        """Crée la barre de menu (Fichier + Jeu + Apparence)."""
        menubar = self.menuBar()

        menu_fichier = menubar.addMenu("Fichier")
        self.__action_charger = QAction("Charger une grille", self)
        self.__action_charger.setShortcut("Ctrl+O")
        menu_fichier.addAction(self.__action_charger)

        self.__action_sauvegarder = QAction("Sauvegarder", self)
        self.__action_sauvegarder.setShortcut("Ctrl+S")
        menu_fichier.addAction(self.__action_sauvegarder)

        menu_jeu = menubar.addMenu("Jeu")

        self.__action_regles = QAction("Règles du jeu", self)
        self.__action_regles.triggered.connect(self.__afficher_regles)
        menu_jeu.addAction(self.__action_regles)

        menu_jeu.addSeparator()

        self.__action_quitter = QAction("Quitter", self)
        self.__action_quitter.triggered.connect(self.close)
        menu_jeu.addAction(self.__action_quitter)

        menu_apparence = menubar.addMenu("Apparence")
        self.__action_theme_clair = QAction("Thème clair", self)
        chemin_clair = os.path.join(os.path.dirname(__file__), "theme_clair.qss")
        self.__action_theme_clair.triggered.connect(lambda: self.__appliquer_theme(chemin_clair))
        menu_apparence.addAction(self.__action_theme_clair)

        self.__action_theme_sombre = QAction("Thème sombre", self)
        chemin_sombre = os.path.join(os.path.dirname(__file__), "theme_sombre.qss")
        self.__action_theme_sombre.triggered.connect(lambda: self.__appliquer_theme(chemin_sombre))
        menu_apparence.addAction(self.__action_theme_sombre)

    # --------------- règles --------------- #

    def __afficher_regles(self):
        """Affiche une boîte de dialogue avec les règles du jeu."""
        QMessageBox.information(self, "Règles du Néonaure",
            "Le Néonaure est un puzzle similaire au Suguru.\n\n"
            "3 règles :\n"
            "1. Chaque case doit contenir un chiffre.\n"
            "2. Les 8 voisins d'une case doivent avoir des valeurs différentes.\n"
            "3. Chaque motif de taille N doit contenir une permutation de 1 à N."
        )

    # --------------- layout --------------- #

    def afficher_accueil(self):
        """Affiche l'écran d'accueil (sans détruire aucun widget)."""
        self.__label_accueil.show()
        self.__grille_widget.hide()
        self.__label_titre.hide()
        self.__label_chrono.hide()

    def afficher_grille_centree(self):
        """Affiche la grille au centre avec le titre et le chrono (sans détruire aucun widget)."""
        self.__label_accueil.hide()
        self.__grille_widget.show()
        self.__label_titre.show()
        self.__label_chrono.show()

    # --------------- thème --------------- #

    def __appliquer_theme(self, chemin_qss: str):
        """Applique un thème QSS sur toute la fenêtre."""
        with open(chemin_qss, 'r', encoding='utf-8') as f:
            qss = f.read()
        self.setStyleSheet(qss)

        self.__theme_sombre = "sombre" in chemin_qss
        self.__menu_gauche.appliquer_theme(self.__theme_sombre)

        self.__label_titre.setStyleSheet("color: #FFFF00; background-color: transparent;")
        self.__label_chrono.setStyleSheet("color: #FFFF00; background-color: transparent;")

        # Reconstruire la grille avec les bonnes couleurs si une grille est chargée
        if self.__grille_data is not None:
            self.__grille_widget.afficher(self.__grille_data, self.__theme_sombre)

    # --------------- chrono --------------- #

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

    # ----------- setters ----------- #

    def set_grille_data(self, data):
        """Enregistre les données brutes de la grille (pour le changement de thème).

        Args:
            data (dict): Les données brutes de la grille.
        """
        self.__grille_data = data

    # -----------getters-----------------#

    def get_grille_widget(self) -> GrilleWidget:
        return self.__grille_widget

    def get_menu_gauche(self) -> MenuGauche:
        return self.__menu_gauche

    def get_action_charger(self):
        return self.__action_charger

    def get_action_sauvegarder(self):
        return self.__action_sauvegarder

    def get_action_quitter(self):
        return self.__action_quitter

    def get_action_regles(self):
        return self.__action_regles

    def get_action_theme_clair(self):
        return self.__action_theme_clair

    def get_action_theme_sombre(self):
        return self.__action_theme_sombre

    def get_label_chrono(self):
        return self.__label_chrono

    def get_theme_sombre(self) -> bool:
        return self.__theme_sombre