import sys
import os
import json
import random
import glob
from PyQt6.QtWidgets import (
    QApplication, QHBoxLayout, QVBoxLayout, QMainWindow, QLabel,
    QFileDialog, QWidget, QGridLayout, QLineEdit, QMessageBox,
    QPushButton, QFrame, QGraphicsDropShadowEffect, QSizePolicy,
    QStackedWidget, QScrollArea
)
# QRadialGradient + QBrush : utilises pour l'effet vignette des differentes interfaces (assombrir les bords)
# QPointF : necessaire comme centre du QRadialGradient (QPoint ne fonctionne pas avec PyQt6)
from PyQt6.QtGui import QAction, QFont, QFontDatabase, QIntValidator, QColor, QPalette, QPainter, QRadialGradient, QBrush
from PyQt6.QtCore import QPointF
# pyqtSignal : permet de creer des signaux personnalises pour la communication entre widgets
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

# Taille en pixels d'une case de la grille#
TAILLE_CASE = 60


# ============================================================ #
#                     GRILLE DU JEU                            #
# ============================================================ #
# Affiche la grille de Suguru avec des QLineEdit pour les cases #
# vides et des QLabel pour les cases pre-remplies. Les bordures entre motifs sont plus épaisses. #


class GrilleWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.__layout = QGridLayout()
        self.__layout.setSpacing(0)       # Pas d'espace entre les cases
        self.__layout.setContentsMargins(0, 0, 0, 0)
        self.__layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.setLayout(self.__layout)
        self.__entries = {}
        # Dictionnaire des cases pre-remplies#
        self.__labels = {}

        # Si la police Luckiest Guy n'existe pas, on utilise Arial
        chemin_police = os.path.join(os.path.dirname(__file__), "fonts", "LuckiestGuy-Regular.ttf")
        if os.path.exists(chemin_police):
            font_id = QFontDatabase.addApplicationFont(chemin_police)
            # font_id == -1 signifie que le chargement a echoue
            self.__police_case = QFont("Luckiest Guy", 18) if font_id != -1 else QFont("Arial", 18, QFont.Weight.Bold)
        else:
            self.__police_case = QFont("Arial", 18, QFont.Weight.Bold)

    def afficher(self, grille_data: dict):
        """Affiche la grille a partir des donnees du modele.

        Args:
            grille_data: dictionnaire {nom_motif: [[ligne, col, valeur], ...]}
                         Chaque cle est un motif (groupe de cases), et la valeur
                         est la liste des cases appartenant a ce motif.
        """
        self.__vider()
        self.__entries = {}
        self.__labels = {}

        fond = "white"
        bordure_fine = "1px solid black"       # Bordure entre cases du meme motif
        bordure_epaisse = "3px solid black"     # Bordure entre cases de motifs differents

        # --- Construction de la carte des motifs ---
        # carte_motifs[(ligne, col)] = index_du_motif
        # Permet de savoir a quel motif appartient chaque case,
        # pour ensuite determiner quelles bordures doivent etre epaisses.
        carte_motifs = {}
        for idx, cases in enumerate(grille_data.values()):
            for case in cases:
                carte_motifs[(case[0], case[1])] = idx

        # --- Affichage de chaque case ---
        for idx, cases in enumerate(grille_data.values()):
            for case in cases:
                row = case[0]
                col = case[1]
                valeur = case[2]

                # Logique des bordures : une bordure est epaisse si la case voisine
                # n'appartient pas au meme motif (idx different).
                # carte_motifs.get((row-1, col), -1) : renvoie -1 si la case voisine
                # n'existe pas (en dehors de la grille), ce qui est != idx => bordure epaisse.
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
                    # Case pre-remplie -> QLabel (non editable par l'utilisateur)
                    label = QLabel(str(valeur))
                    label.setFixedSize(TAILLE_CASE, TAILLE_CASE)
                    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    label.setFont(self.__police_case)
                    label.setStyleSheet(style)
                    self.__layout.addWidget(label, row, col)
                    self.__labels[(row, col)] = label
                else:
                    # Case vide -> QLineEdit (editable par l'utilisateur)
                    entry = QLineEdit()
                    entry.setFixedSize(TAILLE_CASE, TAILLE_CASE)
                    entry.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    entry.setFont(self.__police_case)
                    entry.setMaxLength(1)                         # 1 seul chiffre par case
                    entry.setValidator(QIntValidator(1, 5))       # Accepte uniquement les chiffres 1-5
                    entry.setStyleSheet(style)
                    self.__layout.addWidget(entry, row, col)
                    self.__entries[(row, col)] = entry

    def surligner_selection(self, row: int, col: int):
        """Surligne en bleu clair la case selectionnee et enleve le surlignage des autres."""
        for (r, c), entry in self.__entries.items():
            # On retire les anciens surlignages (bleu ou rouge) du stylesheet
            entry.setStyleSheet(entry.styleSheet().replace("background-color: #cce5ff;", "").replace("background-color: #ff9999;", ""))
            if r == row and c == col:
                # #cce5ff = bleu clair (selection)
                entry.setStyleSheet(entry.styleSheet() + "background-color: #cce5ff;")

    def surligner_conflits(self, conflits: set):
        """Surligne en rouge les cases en conflit (erreur de voisinage)."""
        for (row, col) in conflits:
            entry = self.__entries.get((row, col))
            if entry is not None:
                style = entry.styleSheet().replace("background-color: #cce5ff;", "")
                # #ff9999 = rouge clair (conflit)
                entry.setStyleSheet(style + "background-color: #ff9999;")

    def reinitialiser_couleurs(self):
        """Enleve tous les surlignages (bleu et rouge) des cases editables."""
        for entry in self.__entries.values():
            style = entry.styleSheet()
            style = style.replace("background-color: #cce5ff;", "")
            style = style.replace("background-color: #ff9999;", "")
            entry.setStyleSheet(style)

    def __vider(self):
        """Supprime tous les widgets enfants de la grille (nettoyage avant re-affichage)."""
        while self.__layout.count():
            item = self.__layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()   # Suppression differee pour eviter les crashs

    def nouvelle_partie(self):
        """Vide le contenu de toutes les cases editables (QLineEdit)."""
        for entry in self.__entries.values():
            entry.clear()

    def get_all_values(self) -> dict:
        """Retourne un dictionnaire (row, col) -> valeur pour TOUTES les cellules.

        Combine les valeurs des QLineEdit (cases editables) et des QLabel (cases pre-remplies).
        Si un QLineEdit est vide, sa valeur est 0.
        """
        values = {}
        for (row, col), entry in self.__entries.items():
            texte = entry.text()
            values[(row, col)] = int(texte) if texte.isdigit() else 0
        for (row, col), label in self.__labels.items():
            texte = label.text()
            values[(row, col)] = int(texte) if texte.isdigit() else 0
        return values

    def get_entries(self) -> dict:
        """Retourne uniquement le dictionnaire des QLineEdit (cases editables)."""
        return self.__entries


# ============================================================ #
#                   MENU LATERAL GAUCHE                         #
# ============================================================ #
# Le fond est peint via paintEvent                              #
# ============================================================ #

class MenuGauche(QWidget):
    def __init__(self):
        super().__init__()
        self.__bg_color = QColor("#16213e")   # Couleur de fond bleu fonce
        self.__layout = QVBoxLayout()
        self.__layout.setContentsMargins(10, 20, 10, 20)
        self.__layout.setSpacing(18)   # Espacement entre chaque element du layout

        # Chargement des polices (Luckiest Guy + fallback Arial)
        chemin_luckiest = os.path.join(os.path.dirname(__file__), "fonts", "LuckiestGuy-Regular.ttf")
        if os.path.exists(chemin_luckiest):
            font_id = QFontDatabase.addApplicationFont(chemin_luckiest)
            self.__police_titre = QFont("Luckiest Guy", 36) if font_id != -1 else QFont("Arial", 36, QFont.Weight.Bold)
            self.__police_bouton = QFont("Luckiest Guy", 14) if font_id != -1 else QFont("Arial", 14, QFont.Weight.Bold)
        else:
            self.__police_titre = QFont("Arial", 36, QFont.Weight.Bold)
            self.__police_bouton = QFont("Arial", 14, QFont.Weight.Bold)

        # --- Titre "MENU" ---
        self.__title = QLabel("MENU")
        self.__title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__title.setFont(self.__police_titre)
        self.__title.setStyleSheet("color: #FFFF00; background-color: transparent;")

        # --- Separateure blanc horizontal ---
        self.__separateur = QFrame()
        self.__separateur.setFrameShape(QFrame.Shape.HLine)   # Ligne horizontale
        self.__separateur.setStyleSheet("color: white; background-color: white; max-height: 2px;")

        # --- Boutons d'action ---
        self.__btn_verifier = QPushButton("Verifier")
        self.__btn_resoudre = QPushButton("Resoudre")
        self.__btn_nouvelle = QPushButton("Nouvelle Partie")
        self.__btn_sauvegarder = QPushButton("Sauvegarder")
        self.__btn_back = QPushButton("Retour Menu")

        # Style commun a tous les boutons (jaune, arrondi, effet hover/pressed)
        boutons = [self.__btn_verifier, self.__btn_resoudre,
                   self.__btn_nouvelle, self.__btn_sauvegarder, self.__btn_back]
        for btn in boutons:
            btn.setFont(self.__police_bouton)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #FFFF00;
                    color: black;
                    border: none;
                    border-radius: 8px;
                    padding: 10px;
                    min-height: 35px;
                }
                QPushButton:hover {
                    background-color: #ffe066;     # Jaune plus clair au survol
                }
                QPushButton:pressed {
                    background-color: #ff8c00;     # Orange au clic
                }
            """)

        # --- Ajout des elements au layout ---
        self.__layout.addWidget(self.__title)
        self.__layout.addSpacing(8)        # Espace entre le titre et le separateur
        self.__layout.addWidget(self.__separateur)
        self.__layout.addSpacing(12)       # Espace entre le separateur et les boutons
        self.__layout.addWidget(self.__btn_verifier)
        self.__layout.addWidget(self.__btn_resoudre)
        self.__layout.addWidget(self.__btn_nouvelle)
        self.__layout.addWidget(self.__btn_sauvegarder)
        self.__layout.addWidget(self.__btn_back)
        self.__layout.addStretch()         # Espace extensible : pousse tout vers le haut

        self.setLayout(self.__layout)

    def paintEvent(self, event):
        """Peint le fond du menu. Obligatoire car setStyleSheet() de QMainWindow
        ecrase les backgrounds definis par stylesheet sur les widgets enfants."""
        painter = QPainter(self)
        painter.fillRect(self.rect(), self.__bg_color)

    def set_bg_color(self, color: str):
        """Change la couleur de fond du menu (utilise par paintEvent)."""
        self.__bg_color = QColor(color)
        self.update()   # Declenche un repaint via paintEvent

    def appliquer_theme(self, sombre: bool):
        """Re-applique les styles apres un changement de theme.
        Necessaire car le QSS de QMainWindow peut ecraser les styles locaux."""
        self.__title.setStyleSheet("color: #FFFF00; background-color: transparent;")
        self.__separateur.setStyleSheet("color: white; background-color: white; max-height: 2px;")
        boutons = [self.__btn_verifier, self.__btn_resoudre,
                   self.__btn_nouvelle, self.__btn_sauvegarder, self.__btn_back]
        for btn in boutons:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #FFFF00;
                    color: black;
                    border: none;
                    border-radius: 8px;
                    padding: 10px;
                    min-height: 35px;
                }
                QPushButton:hover {
                    background-color: #ffe066;
                }
                QPushButton:pressed {
                    background-color: #ff8c00;
                }
            """)

    # --- Getters pour que le Controller puisse connecter les signaux ---
    def get_btn_verifier(self):
        return self.__btn_verifier

    def get_btn_resoudre(self):
        return self.__btn_resoudre

    def get_btn_nouvelle(self):
        return self.__btn_nouvelle

    def get_btn_sauvegarder(self):
        return self.__btn_sauvegarder

    def get_btn_back(self):
        return self.__btn_back

# ============================================================ #
#             INTERFACE DE SELECTION DE DIFFICULTE               #
# ============================================================ #

class SelectionDifficulte(QWidget):
    def __init__(self):
        super().__init__()
        self.__bg_color = QColor("#00a6ff")   # Bleu clair
        chemin_luckiest = os.path.join(os.path.dirname(__file__), "fonts", "LuckiestGuy-Regular.ttf")#chargement de la police "Luckiest Guy"#
        if os.path.exists(chemin_luckiest):
            QFontDatabase.addApplicationFont(chemin_luckiest)

        # Police du titre ;taille 110px
        police_titre = QFont("Luckiest Guy")
        police_titre.setPixelSize(110)

        # Police du texte descriptif
        police_texte = QFont("Luckiest Guy")
        police_texte.setPixelSize(20)

        # Police des boutons Facile/Difficile
        police_bouton = QFont("Luckiest Guy")
        police_bouton.setPixelSize(28)

        # Layout principal vertical centre
        layout_principal = QVBoxLayout()
        layout_principal.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_principal.setSpacing(40)
        layout_principal.setContentsMargins(50, 30, 50, 50)

        #  Titre "NEONAURE!" avec effet neon
        self.__label_titre = QLabel("NEONAURE!")
        self.__label_titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__label_titre.setFont(police_titre)
        self.__label_titre.setStyleSheet("color: #FFFF00; background-color: transparent;")
        # QGraphicsDropShadowEffect : cree un halo flou autour du texte
        effet_neon = QGraphicsDropShadowEffect()
        effet_neon.setBlurRadius(40)
        effet_neon.setColor(QColor(255, 255, 0))   # Halo jaune
        effet_neon.setOffset(0, 0)                   # Centre sur le texte
        self.__label_titre.setGraphicsEffect(effet_neon)

        # --- Texte descriptif des modes ---
        self.__label_description = QLabel(
            "choisissais le niveau de difficulte\n"
            "(facile: indice + verification en temps reel des voisinages)\n"
            "(difficile: pas d'indice + pas de verification du voisinage des cases)"
        )
        self.__label_description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__label_description.setFont(police_texte)
        self.__label_description.setStyleSheet("color: #ffffff; background-color: transparent;")
        self.__label_description.setWordWrap(True)

        # Boutons Facile / Difficile 
        layout_boutons = QHBoxLayout()
        layout_boutons.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_boutons.setSpacing(60)

        # Bouton Facile
        self.__btn_facile = QPushButton("Facile")
        self.__btn_facile.setFont(police_bouton)
        self.__btn_facile.setMinimumSize(220, 80)
        self.__btn_facile.setStyleSheet("""
            QPushButton {
                background-color: #ffff00;
                color: black;
                border: none;
                border-radius: 12px;
                padding: 15px 40px;
            }
            QPushButton:hover {
                background-color: #ffe066;
            }
            QPushButton:pressed {
                background-color: #ff8c00;
            }
        """)
        # Ombre portee sous le bouton 
        ombre_facile = QGraphicsDropShadowEffect()
        ombre_facile.setBlurRadius(20)
        ombre_facile.setColor(QColor(0, 0, 0))
        ombre_facile.setOffset(9, 12)   # Decalage vers le bas-droite
        self.__btn_facile.setGraphicsEffect(ombre_facile)

        # Bouton Difficile (meme style que Facile)
        self.__btn_difficile = QPushButton("Difficile")
        self.__btn_difficile.setFont(police_bouton)
        self.__btn_difficile.setMinimumSize(220, 80)
        self.__btn_difficile.setStyleSheet("""
            QPushButton {
                background-color: #ffff00;
                color: black;
                border: none;
                border-radius: 12px;
                padding: 15px 40px;
            }
            QPushButton:hover {
                background-color: #ffe066;
            }
            QPushButton:pressed {
                background-color: #ff8c00;
            }
        """)
        ombre_difficile = QGraphicsDropShadowEffect()
        ombre_difficile.setBlurRadius(20)
        ombre_difficile.setColor(QColor(0, 0, 0))
        ombre_difficile.setOffset(9, 12)
        self.__btn_difficile.setGraphicsEffect(ombre_difficile)

        layout_boutons.addWidget(self.__btn_facile)
        layout_boutons.addWidget(self.__btn_difficile)

        layout_principal.addWidget(self.__label_titre)
        layout_principal.addWidget(self.__label_description)
        layout_principal.addLayout(layout_boutons)

        self.setLayout(layout_principal)

    def paintEvent(self, event):
        """Peint le fond bleu + l'effet vignette (assombrir les bords).
        - QPointF est OBLIGATOIRE en PyQt6 (QPoint provoque un TypeError)
        - Le rayon est 65% de la plus grande dimension du widget
        """
        painter = QPainter(self)
        # 1) Fond bleu principal
        painter.fillRect(self.rect(), self.__bg_color)
        # 2) Vignette par-dessus : degrade radial qui assombrit les bords
        centre = QPointF(self.width() / 2, self.height() / 2)
        rayon = max(self.width(), self.height()) * 0.65
        gradient = QRadialGradient(centre, rayon)
        # Les couleurs sont en RGBA : (rouge, vert, bleu, alpha)
        # alpha=0 = transparent, alpha=255 = opaque
        gradient.setColorAt(0.0, QColor(0, 0, 0, 0))           # centre : transparent
        gradient.setColorAt(0.4, QColor(0, 0, 0, 0))           # 40% : encore transparent
        gradient.setColorAt(0.7, QColor(0, 58, 122, 150))      # debut de l'ombre
        gradient.setColorAt(0.85, QColor(0, 58, 122, 210))     # ombre moyenne
        gradient.setColorAt(1.0, QColor(0, 58, 122, 255))      # ombre maximale aux extremites
        painter.fillRect(self.rect(), QBrush(gradient))

    def get_btn_facile(self):
        return self.__btn_facile

    def get_btn_difficile(self):
        return self.__btn_difficile


# ============================================================ #
#             CLIQUABLE D'UNE GRILLE                  #
# ============================================================ #

class MiniGrillePreview(QFrame):
    """Preview miniature cliquable d'une grille de Suguru"""
    clicked = pyqtSignal(str)

    def __init__(self, chemin_grille: str, numero: int):
        super().__init__()
        self.__chemin = chemin_grille
        self.__numero = numero
        # Change le curseur en "pointeur cliquable" au survol
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        # Fond transparent (on voit le fond bleu de la page a travers)
        self.setStyleSheet("MiniGrillePreview { background-color: transparent; }")

        # Charger les donnees de la grille depuis le fichier JSON
        with open(chemin_grille, 'r', encoding='utf-8') as f:
            grille_data = json.load(f)

        chemin_police = os.path.join(os.path.dirname(__file__), "fonts", "LuckiestGuy-Regular.ttf") #police#
        if os.path.exists(chemin_police):
            police_mini = QFont("Luckiest Guy", 7)    # Police pour les numeros dans les cases
            police_nom = QFont("Luckiest Guy", 13)    # Police pour "grilleN"
        else:
            police_mini = QFont("Arial", 7, QFont.Weight.Bold)
            police_nom = QFont("Arial", 13, QFont.Weight.Bold)

        # Taille d'une case dans la miniature (plus petit que TAILLE_CASE)
        TAILLE_MINI = 22

        # Layout principal vertical (grille + nom)
        layout_principal = QVBoxLayout(self)
        layout_principal.setSpacing(3)
        layout_principal.setContentsMargins(5, 5, 5, 5)
        layout_principal.setAlignment(Qt.AlignmentFlag.AlignCenter)

        #  Carte des motifs (meme logique que GrilleWidget) 
        carte_motifs = {}
        for idx, cases in enumerate(grille_data.values()):
            for case in cases:
                carte_motifs[(case[0], case[1])] = idx

        #  Widget grille miniature 
        grid_widget = QWidget()
        grid_widget.setStyleSheet("background-color: transparent;")
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(0)
        grid_layout.setContentsMargins(0, 0, 0, 0)

        bordure_fine = "1px solid black"
        bordure_epaisse = "2px solid black"   # Un peu plus fin que la grille principale (2px vs 3px)

        for idx, cases in enumerate(grille_data.values()):
            for case in cases:
                row, col, valeur = case[0], case[1], case[2]

                # Meme logique de bordures que GrilleWidget.afficher()
                top = bordure_epaisse if carte_motifs.get((row-1, col), -1) != idx else bordure_fine
                bottom = bordure_epaisse if carte_motifs.get((row+1, col), -1) != idx else bordure_fine
                left = bordure_epaisse if carte_motifs.get((row, col-1), -1) != idx else bordure_fine
                right = bordure_epaisse if carte_motifs.get((row, col+1), -1) != idx else bordure_fine

                # Noir et blanc : texte noir, bordures noires
                style = (
                    f"background-color: white;"
                    f"color: black;"
                    f"border-top: {top}; border-bottom: {bottom};"
                    f"border-left: {left}; border-right: {right};"
                )

                # Toutes les cases sont des QLabel (non editables dans la miniature)
                cell = QLabel(str(valeur) if valeur != 0 else "")
                cell.setFixedSize(TAILLE_MINI, TAILLE_MINI)
                cell.setAlignment(Qt.AlignmentFlag.AlignCenter)
                cell.setFont(police_mini)
                cell.setStyleSheet(style)
                grid_layout.addWidget(cell, row, col)

        # --- Cadre jaune autour de la grille ---
        self.__frame_grille = QFrame()
        self.__frame_grille.setStyleSheet("QFrame { border: 3px solid #ffff00; background-color: transparent; }")
        frame_layout = QVBoxLayout(self.__frame_grille)
        frame_layout.setContentsMargins(2, 2, 2, 2)
        frame_layout.addWidget(grid_widget)

        layout_principal.addWidget(self.__frame_grille, alignment=Qt.AlignmentFlag.AlignCenter)

        # --- Nom de la grille ("grille1", "grille2", etc.) ---
        label_nom = QLabel(f"grille{numero}")
        label_nom.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_nom.setFont(police_nom)
        label_nom.setStyleSheet("color: #ffffff; background-color: transparent;")
        layout_principal.addWidget(label_nom)

    def mousePressEvent(self, event):
        """Emet le signal 'clicked' avec le chemin du fichier grille quand on clique."""
        self.clicked.emit(self.__chemin)

    def enterEvent(self, event):
        """Au survol : bordure plus epaisse et plus claire (effet hover)."""
        self.__frame_grille.setStyleSheet("QFrame { border: 4px solid #ffe066; background-color: transparent; }")

    def leaveEvent(self, event):
        """Quand on quitte le survol : bordure normale."""
        self.__frame_grille.setStyleSheet("QFrame { border: 3px solid #ffff00; background-color: transparent; }")

    def get_chemin(self):
        return self.__chemin


# ============================================================ #
#           INTERFACE DE SELECTION DE GRILLE                     #
# ============================================================ #

class SelectionGrille(QWidget):
    """Interface de choix de grille, apres avoir selectionne la difficulte"""
    # Signal emis quand l'utilisateur clique sur une grille
    grille_choisie = pyqtSignal(str)   # emet le chemin du fichier grille clique
    # Signal emis quand l'utilisateur clique sur Retour
    retour_demande = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.__bg_color = QColor("#00a6ff")   # Meme bleu que SelectionDifficulte
        self.__previews = []                   # Liste des MiniGrillePreview affiches

        # Polices
        chemin_luckiest = os.path.join(os.path.dirname(__file__), "fonts", "LuckiestGuy-Regular.ttf")
        if os.path.exists(chemin_luckiest):
            QFontDatabase.addApplicationFont(chemin_luckiest)

        police_titre = QFont("Luckiest Guy")
        police_titre.setPixelSize(90)

        police_texte = QFont("Luckiest Guy")
        police_texte.setPixelSize(20)

        police_bouton = QFont("Luckiest Guy")
        police_bouton.setPixelSize(22)

        # Layout principal vertical centre
        layout_principal = QVBoxLayout()
        layout_principal.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_principal.setSpacing(20)
        layout_principal.setContentsMargins(30, 20, 30, 20)

        # --- Titre "NEONAURE!" (meme style que SelectionDifficulte) ---
        self.__label_titre = QLabel("NEONAURE!")
        self.__label_titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__label_titre.setFont(police_titre)
        self.__label_titre.setStyleSheet("color: #FFFF00; background-color: transparent;")
        effet_neon = QGraphicsDropShadowEffect()
        effet_neon.setBlurRadius(40)
        effet_neon.setColor(QColor(255, 255, 0))
        effet_neon.setOffset(0, 0)
        self.__label_titre.setGraphicsEffect(effet_neon)
        layout_principal.addWidget(self.__label_titre)

        #  Texte "Fais le choix de ta grille ...."
        self.__label_description = QLabel("Fais le choix de ta grille ....")
        self.__label_description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__label_description.setFont(police_texte)
        self.__label_description.setStyleSheet("color: #ffffff; background-color: transparent;")
        layout_principal.addWidget(self.__label_description)

        #  Zone scrollable contenant les aperçus de grilles 
        self.__grille_container = QWidget()
        self.__grille_container.setStyleSheet("background-color: transparent;")
        self.__grille_layout = QGridLayout()
        self.__grille_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__grille_layout.setSpacing(15)
        self.__grille_layout.setContentsMargins(10, 10, 10, 10)
        self.__grille_container.setLayout(self.__grille_layout)

        # QScrollArea : permet de scroller si les grilles ne tiennent pas dans l'ecran
        scroll = QScrollArea()
        scroll.setWidget(self.__grille_container)
        scroll.setWidgetResizable(True)   # Le container s'adapte a la largeur du scroll
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 10px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 80);
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;           # Cache les fleches haut/bas de la scrollbar
            }
        """)
        # stretch=1 : le scroll prend tout l'espace vertical restant
        layout_principal.addWidget(scroll, stretch=1)

        # --- Bouton Retour (aligne a droite) ---
        layout_bas = QHBoxLayout()
        layout_bas.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.__btn_retour = QPushButton("Retour")
        self.__btn_retour.setFont(police_bouton)
        self.__btn_retour.setMinimumSize(160, 55)
        self.__btn_retour.setStyleSheet("""
            QPushButton {
                background-color: #ffff00;
                color: black;
                border: none;
                border-radius: 12px;
                padding: 10px 30px;
            }
            QPushButton:hover {
                background-color: #ffe066;
            }
            QPushButton:pressed {
                background-color: #ff8c00;
            }
        """)
        ombre_retour = QGraphicsDropShadowEffect()
        ombre_retour.setBlurRadius(15)
        ombre_retour.setColor(QColor(0, 0, 0))
        ombre_retour.setOffset(5, 8)
        self.__btn_retour.setGraphicsEffect(ombre_retour)
        # Connexion directe : cliquer sur Retour emet le signal retour_demande
        self.__btn_retour.clicked.connect(self.retour_demande.emit)

        layout_bas.addWidget(self.__btn_retour)
        layout_principal.addLayout(layout_bas)

        self.setLayout(layout_principal)

        # Charger les grilles disponibles au demarrage
        self.charger_grilles()

    def charger_grilles(self):
        """Charge toutes les grilles du dossier Grille et cree les previews.

        Disposition : 6 grilles sur la premiere ligne, 5 sur la deuxieme.
        La deuxieme ligne est centree par rapport a la premiere.
        Les fichiers grilleTest.json sont exclus.
        """
        # Supprimer les anciens previews (utile si on recharge la page)
        for preview in self.__previews:
            preview.clicked.disconnect()                  # Deconnecter le signal
            self.__grille_layout.removeWidget(preview)   # Retirer du layout
            preview.deleteLater()                         # Supprimer le widget
        self.__previews = []

        # Trouver les fichiers de grille dans le dossier ../Grille
        base_dir = os.path.dirname(os.path.abspath(__file__))
        dossier_grilles = os.path.join(base_dir, "..", "Grille")
        fichiers = sorted(glob.glob(os.path.join(dossier_grilles, "grille*.json")))
        # Exclure les fichiers de test
        fichiers = [f for f in fichiers if "grilleTest" not in os.path.basename(f)]

        # Nombre de grilles sur la premiere ligne
        nb_premiere_ligne = 6

        for i, chemin in enumerate(fichiers):
            nom_fichier = os.path.basename(chemin)
            # Extraire le numero du nom de fichier (grille1.json -> 1)
            numero = i + 1
            try:
                nom_sans_ext = os.path.splitext(nom_fichier)[0]  # "grille1"
                numero_str = nom_sans_ext.replace("grille", "")  # "1"
                if numero_str.isdigit():
                    numero = int(numero_str)
            except (ValueError, AttributeError):
                pass

            # Creer le preview et connecter son signal clicked
            preview = MiniGrillePreview(chemin, numero)
            preview.clicked.connect(self.grille_choisie.emit)
            self.__previews.append(preview)

            if i < nb_premiere_ligne:
                # Premiere ligne : colonnes 0 a 5
                self.__grille_layout.addWidget(preview, 0, i)
            else:
                # Deuxieme ligne : centree par rapport a la premiere
                # offset = decalage pour centrer les 5 grilles sous les 6
                # Formule : (6 - 5) // 2 = 0, donc commence a la colonne 0
                # Si on avait 6+4, offset = (6-4)//2 = 1, commencerait a la colonne 1
                offset = (nb_premiere_ligne - (len(fichiers) - nb_premiere_ligne)) // 2
                self.__grille_layout.addWidget(preview, 1, offset + (i - nb_premiere_ligne))

    def paintEvent(self, event):
        """Meme effet vignette que SelectionDifficulte (voir commentaires la-bas)."""
        painter = QPainter(self)
        painter.fillRect(self.rect(), self.__bg_color)
        centre = QPointF(self.width() / 2, self.height() / 2)
        rayon = max(self.width(), self.height()) * 0.65
        gradient = QRadialGradient(centre, rayon)
        gradient.setColorAt(0.0, QColor(0, 0, 0, 0))
        gradient.setColorAt(0.4, QColor(0, 0, 0, 0))
        gradient.setColorAt(0.7, QColor(0, 58, 122, 150))
        gradient.setColorAt(0.85, QColor(0, 58, 122, 210))
        gradient.setColorAt(1.0, QColor(0, 58, 122, 255))
        painter.fillRect(self.rect(), QBrush(gradient))

    def get_btn_retour(self):
        return self.__btn_retour

    def rafraichir(self):
        """Recharge les grilles (appele avant d'afficher la page)."""
        self.charger_grilles()


# ============================================================ #
#                 WIDGET AVEC FOND COLORE                       #
# ============================================================ #

class WidgetFond(QWidget):
    def __init__(self, couleur="#1a1a2e"):
        super().__init__()
        self.__bg = QColor(couleur)

    def set_couleur_fond(self, couleur: str):
        """Change la couleur de fond et redessine."""
        self.__bg = QColor(couleur)
        self.update()   # Declenche paintEvent

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), self.__bg)


# ============================================================ #
#                     VUE PRINCIPALE                            #
# ============================================================ #
# QMainWindow contenant un QStackedWidget avec 3 pages :        #
#   - Index 0 : SelectionDifficulte (choix facile/difficile)   #
#   - Index 1 : SelectionGrille (choix de la grille)           #
#   - Index 2 : Page de jeu (MenuGauche + grille + chrono)     #


class Vue(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Neonaure")

        self.__grille_data = None          # Donnees de la grille en cours
        self.__theme_sombre = True         # Theme actuel
        self.__difficulte_facile = True    # Mode facile par defaut

        # --- Chargement des polices ---
        chemin_luckiest = os.path.join(os.path.dirname(__file__), "fonts", "LuckiestGuy-Regular.ttf")
        if os.path.exists(chemin_luckiest):
            font_id_luck = QFontDatabase.addApplicationFont(chemin_luckiest)
            self.__police_titre = QFont("Luckiest Guy", 48) if font_id_luck != -1 else QFont("Arial", 48, QFont.Weight.Bold)
        else:
            self.__police_titre = QFont("Arial", 48, QFont.Weight.Bold)

        chemin_techno = os.path.join(os.path.dirname(__file__), "fonts", "Technology.ttf")
        if os.path.exists(chemin_techno):
            font_id_techno = QFontDatabase.addApplicationFont(chemin_techno)
            # "TECHNOLOGY" est le nom de la police (pas le nom du fichier)
            self.__police_chrono = QFont("TECHNOLOGY", 28) if font_id_techno != -1 else QFont("Arial", 28, QFont.Weight.Bold)
        else:
            self.__police_chrono = QFont("Arial", 28, QFont.Weight.Bold)

        # ============================================================ #
        #                  CREATION DES 3 PAGES                         #
        # ============================================================ #

        # Page 0 : selection de difficulte
        self.__selection_difficulte = SelectionDifficulte()

        # Page 1 : selection de grille
        self.__selection_grille = SelectionGrille()

        # Page 2 : jeu (menu gauche + zone centrale)
        self.__menu_gauche = MenuGauche()
        self.__menu_gauche.setObjectName("menuGauche")   # Identifiant pour le QSS
        self.__menu_gauche.appliquer_theme(False)

        self.__grille_widget = GrilleWidget()
        self.__grille_widget.setObjectName("grilleWidget")

        # --- Titre "NEONAURE!" (zone de jeu) ---
        self.__label_titre = QLabel("NEONAURE!")
        self.__label_titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__label_titre.setFont(self.__police_titre)
        self.__label_titre.setStyleSheet("color: #FFFF00; background-color: transparent;")
        effet_neon = QGraphicsDropShadowEffect()
        effet_neon.setBlurRadius(30)
        effet_neon.setColor(QColor(255, 255, 0))
        effet_neon.setOffset(0, 0)
        self.__label_titre.setGraphicsEffect(effet_neon)

        # --- Chronometre (zone centrale) ---
        self.__temps = 0
        self.__chrono = QTimer(self)
        self.__chrono.timeout.connect(self.__incrementer)   # Toutes les 1000ms = 1 seconde
        self.__label_chrono = QLabel("00:00")
        self.__label_chrono.setFont(self.__police_chrono)
        self.__label_chrono.setFixedSize(150, 50)
        self.__label_chrono.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__label_chrono.setStyleSheet("color: #FFFF00; background-color: transparent;")

        # ============================================================ #
        #              CONSTRUCTION DE LA PAGE DE JEU                   #
        # ============================================================ #


        layout_principal = QHBoxLayout()

        zone_centrale = QVBoxLayout()
        zone_centrale.setContentsMargins(0, 15, 0, 15)
        # AlignTop : le titre reste fixe en haut (pas centre verticalement)
        # AlignHCenter : le contenu est centre horizontalement
        zone_centrale.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        zone_centrale.addWidget(self.__label_titre, alignment=Qt.AlignmentFlag.AlignCenter)
        zone_centrale.addSpacing(15)    # Espace entre le titre et la grille
        zone_centrale.addWidget(self.__grille_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        zone_centrale.addSpacing(10)    # Espace entre la grille et le chrono
        zone_centrale.addWidget(self.__label_chrono, alignment=Qt.AlignmentFlag.AlignCenter)
        zone_centrale.addStretch()      # Espace extensible en bas : absorbe l'espace vide

        # WidgetFond : conteneur avec fond peint via paintEvent
        self.__conteneur_centre = WidgetFond("#1a1a2e")
        self.__conteneur_centre.setObjectName("conteneurCentre")
        self.__conteneur_centre.setLayout(zone_centrale)

        # Les proportions 1:3 signifient que le menu prend ~25% et la zone centrale ~75%
        layout_principal.addWidget(self.__menu_gauche, 1)
        layout_principal.addWidget(self.__conteneur_centre, 3)

        self.__widget_jeu = QWidget()
        self.__widget_jeu.setObjectName("widgetJeu")
        self.__widget_jeu.setLayout(layout_principal)

        # ============================================================ #
        #               QSTACKEDWIDGET : NAVIGATION                     #
        # ============================================================ #
        # 3 pages : 0=difficulte, 1=grille, 2=jeu                     #
        # setCurrentIndex() pour changer de page                        #
        # ============================================================ #

        self.__pages = QStackedWidget()
        self.__pages.addWidget(self.__selection_difficulte)  # index 0
        self.__pages.addWidget(self.__selection_grille)      # index 1
        self.__pages.addWidget(self.__widget_jeu)            # index 2
        self.setCentralWidget(self.__pages)

        # Page d'accueil : selection de difficulte
        self.__pages.setCurrentIndex(0)

        # Appliquer le theme sombre au demarrage via le fichier QSS
        chemin_sombre_init = os.path.join(os.path.dirname(__file__), "theme_sombre.qss")
        with open(chemin_sombre_init, 'r', encoding='utf-8') as f:
            self.setStyleSheet(f.read())
        # Cacher la barre de menu sur la page d'accueil
        self.menuBar().hide()

        self.__creer_menu()

    # ============================================================ #
    #              METHODES DE NAVIGATION ENTRE PAGES               #
    # ============================================================ #

    def afficher_difficulte(self):
        """Affiche la page de selection de difficulte (index 0)."""
        self.__pages.setCurrentIndex(0)
        self.setStyleSheet("")      # Vide le QSS pour que paintEvent fonctionne
        self.menuBar().hide()

    def afficher_selection_grille(self):
        """Affiche la page de selection de grille (index 1)."""
        self.__selection_grille.rafraichir()   # Recharge les grilles
        self.__pages.setCurrentIndex(1)
        self.setStyleSheet("")
        self.menuBar().hide()

    def afficher_grille_centree(self):
        """Affiche la page de jeu (index 2)."""
        self.__pages.setCurrentIndex(2)
        self.menuBar().show()
        # Re-appliquer les couleurs de fond via paintEvent
        self.__menu_gauche.set_bg_color("#16213e")
        if self.__theme_sombre:
            self.__conteneur_centre.set_couleur_fond("#1a1a2e")
        else:
            self.__conteneur_centre.set_couleur_fond("#00689f")

    # ============================================================ #
    #                  BARRE DE MENU (MENUBAR)                      #
    # ============================================================ #

    def __creer_menu(self):
        """Cree la barre de menu avec Fichier, Jeu et Apparence."""
        menubar = self.menuBar()

        menu_fichier = menubar.addMenu("Fichier")

        self.__action_charger = QAction("Charger une grille", self)
        self.__action_charger.setShortcut("Ctrl+O")
        menu_fichier.addAction(self.__action_charger)

        self.__action_sauvegarder = QAction("Sauvegarder la grille", self)
        self.__action_sauvegarder.setShortcut("Ctrl+S")
        menu_fichier.addAction(self.__action_sauvegarder)

        menu_fichier.addSeparator()

        self.__action_quitter = QAction("Quitter", self)
        self.__action_quitter.triggered.connect(self.close)
        menu_fichier.addAction(self.__action_quitter)

        menu_jeu = menubar.addMenu("Jeu")

        self.__action_verifier = QAction("Verifier la solution", self)
        menu_jeu.addAction(self.__action_verifier)

        self.__action_resoudre = QAction("Resoudre", self)
        self.__action_resoudre.setShortcut("Ctrl+R")
        menu_jeu.addAction(self.__action_resoudre)

        self.__action_nouvelle = QAction("Nouvelle partie", self)
        self.__action_nouvelle.setShortcut("Ctrl+N")
        menu_jeu.addAction(self.__action_nouvelle)

        menu_jeu.addSeparator()

        self.__action_regles = QAction("Regles du Neonature", self)
        menu_jeu.addAction(self.__action_regles)

        menu_apparence = menubar.addMenu("Apparence")

        self.__action_theme_clair = QAction("Theme clair", self)
        chemin_clair = os.path.join(os.path.dirname(__file__), "theme_clair.qss")
        # lambda : capture chemin_clair pour le passer a __appliquer_theme
        self.__action_theme_clair.triggered.connect(lambda: self.__appliquer_theme(chemin_clair))
        menu_apparence.addAction(self.__action_theme_clair)

        self.__action_theme_sombre = QAction("Theme sombre", self)
        chemin_sombre = os.path.join(os.path.dirname(__file__), "theme_sombre.qss")
        self.__action_theme_sombre.triggered.connect(lambda: self.__appliquer_theme(chemin_sombre))
        menu_apparence.addAction(self.__action_theme_sombre)

    def __appliquer_theme(self, chemin_qss: str):
        """Applique un theme QSS et met a jour les couleurs des widgets.

        IMPORTANT : Apres avoir change le QSS, il faut re-appliquer les styles
        locaux (couleurs, backgrounds) car le QSS global peut les ecraser.
        Il faut aussi re-afficher la grille pour que les styles des cases
        soient mis a jour.
        """
        with open(chemin_qss, 'r', encoding='utf-8') as f:
            qss = f.read()
        self.setStyleSheet(qss)

        # Detecter le theme a partir du nom du fichier
        self.__theme_sombre = "sombre" in chemin_qss

        # Re-appliquer les couleurs via paintEvent
        self.__menu_gauche.set_bg_color("#16213e")
        if self.__theme_sombre:
            self.__conteneur_centre.set_couleur_fond("#1a1a2e")
        else:
            self.__conteneur_centre.set_couleur_fond("#00689f")

        # Re-appliquer les styles du menu gauche
        self.__menu_gauche.appliquer_theme(self.__theme_sombre)

        # Re-appliquer les styles du titre et du chrono
        self.__label_titre.setStyleSheet("color: #FFFF00; background-color: transparent;")
        self.__label_chrono.setStyleSheet("color: #FFFF00; background-color: transparent;")

        if self.__grille_data is not None:
            # Sauvegarder les valeurs actuelles avant de re-afficher
            # (sinon les saisies de l'utilisateur seraient perdues)
            valeurs_actuelles = self.__grille_widget.get_all_values()
            self.__grille_widget.afficher(self.__grille_data)
            # Restaurer les valeurs saisies par l'utilisateur dans les QLineEdit
            entries = self.__grille_widget.get_entries()
            for (row, col), valeur in valeurs_actuelles.items():
                # On ne restaure que les valeurs non-nulles (chiffres saisis)
                # car les cases vides (0) correspondent a des QLineEdit vides
                if (row, col) in entries and valeur != 0:
                    entries[(row, col)].setText(str(valeur))

    # ============================================================ #
    #                      CHRONOMETRE                              #
    # ============================================================ #

    def __incrementer(self):
        """Incremente le chronometre de 1 seconde (appele par QTimer)."""
        self.__temps += 1
        minutes = self.__temps // 60
        secondes = self.__temps % 60
        self.__label_chrono.setText(f"{minutes:02d}:{secondes:02d}")   # Format MM:SS

    def demarrer_chrono(self):
        """Demarre le chronometre a zero."""
        self.__temps = 0
        self.__label_chrono.setText("00:00")
        self.__chrono.start(1000)   # Toutes les 1000ms = 1 seconde

    def arreter_chrono(self):
        """Arrete le chronometre sans le reinitialiser."""
        self.__chrono.stop()

    def reinitialiser_chrono(self):
        """Arrete et remet le chronometre a zero."""
        self.__chrono.stop()
        self.__temps = 0
        self.__label_chrono.setText("00:00")

    # ============================================================ #
    #                       GETTERS / SETTERS                       #
    # ============================================================ #                                  

    def get_grille_data(self) -> dict:
        return self.__grille_data

    def set_grille_data(self, data):
        self.__grille_data = data

    def get_grille_widget(self) -> GrilleWidget:
        return self.__grille_widget

    def get_menu_gauche(self) -> MenuGauche:
        return self.__menu_gauche

    def get_selection_difficulte(self) -> SelectionDifficulte:
        return self.__selection_difficulte

    def get_selection_grille(self) -> SelectionGrille:
        return self.__selection_grille

    def get_difficulte_facile(self) -> bool:
        return self.__difficulte_facile

    def set_difficulte_facile(self, valeur: bool):
        self.__difficulte_facile = valeur

    def get_action_charger(self):
        return self.__action_charger

    def get_action_sauvegarder(self):
        return self.__action_sauvegarder

    def get_action_quitter(self):
        return self.__action_quitter

    def get_action_verifier(self):
        return self.__action_verifier

    def get_action_resoudre(self):
        return self.__action_resoudre

    def get_action_nouvelle(self):
        return self.__action_nouvelle

    def get_action_regles(self):
        return self.__action_regles

    def get_action_theme_clair(self):
        return self.__action_theme_clair

    def get_action_theme_sombre(self):
        return self.__action_theme_sombre

    def get_label_chrono(self):
        return self.__label_chrono

    def get_label_titre(self):
        return self.__label_titre

    def get_theme_sombre(self):
        return self.__theme_sombre
