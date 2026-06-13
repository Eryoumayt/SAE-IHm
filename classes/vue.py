import sys
import os
import json
import random
from PyQt6.QtWidgets import (
    QApplication, QHBoxLayout, QVBoxLayout, QMainWindow, QLabel,
    QFileDialog, QWidget, QGridLayout, QLineEdit, QMessageBox,
    QPushButton, QFrame, QGraphicsDropShadowEffect, QSizePolicy,
    QStackedWidget
)
from PyQt6.QtGui import QAction, QFont, QFontDatabase, QIntValidator, QColor, QPalette, QPainter
from PyQt6.QtCore import Qt, QTimer

TAILLE_CASE = 60


#----- grille du jeu -----#

class GrilleWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.__layout = QGridLayout()
        self.__layout.setSpacing(0)
        self.__layout.setContentsMargins(0, 0, 0, 0)
        self.__layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.setLayout(self.__layout)

        self.__entries = {}

        chemin_police = os.path.join(os.path.dirname(__file__), "fonts", "LuckiestGuy-Regular.ttf")
        if os.path.exists(chemin_police):
            font_id = QFontDatabase.addApplicationFont(chemin_police)
            self.__police_case = QFont("Luckiest Guy", 18) if font_id != -1 else QFont("Arial", 18, QFont.Weight.Bold)
        else:
            self.__police_case = QFont("Arial", 18, QFont.Weight.Bold)

    def afficher(self, grille_data: dict):
        self.__vider()
        self.__entries = {}

        fond = "white"
        bordure_fine = "1px solid black"
        bordure_epaisse = "3px solid black"

        carte_motifs = {}
        for idx, cases in enumerate(grille_data.values()):
            for case in cases:
                carte_motifs[(case[0], case[1])] = idx

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
                    label.setFont(self.__police_case)
                    label.setStyleSheet(style)
                    self.__layout.addWidget(label, row, col)
                else:
                    entry = QLineEdit()
                    entry.setFixedSize(TAILLE_CASE, TAILLE_CASE)
                    entry.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    entry.setFont(self.__police_case)
                    entry.setMaxLength(1)
                    entry.setValidator(QIntValidator(1, 9))
                    entry.setStyleSheet(style)
                    self.__layout.addWidget(entry, row, col)
                    self.__entries[(row, col)] = entry

    def surligner_selection(self, row: int, col: int):
        for (r, c), entry in self.__entries.items():
            entry.setStyleSheet(entry.styleSheet().replace("background-color: #cce5ff;", "").replace("background-color: #ff9999;", ""))
            if r == row and c == col:
                entry.setStyleSheet(entry.styleSheet() + "background-color: #cce5ff;")

    def surligner_conflits(self, conflits: set):
        for (row, col) in conflits:
            entry = self.__entries.get((row, col))
            if entry is not None:
                style = entry.styleSheet().replace("background-color: #cce5ff;", "")
                entry.setStyleSheet(style + "background-color: #ff9999;")

    def reinitialiser_couleurs(self):
        for entry in self.__entries.values():
            style = entry.styleSheet()
            style = style.replace("background-color: #cce5ff;", "")
            style = style.replace("background-color: #ff9999;", "")
            entry.setStyleSheet(style)

    def __vider(self):
        while self.__layout.count():
            item = self.__layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def nouvelle_partie(self):
        for entry in self.__entries.values():
            entry.clear()

    def get_entries(self) -> dict:
        return self.__entries


# ----- menu lateral gauche ----- #

class MenuGauche(QWidget):
    def __init__(self):
        super().__init__()
        self.__bg_color = QColor("#16213e")
        self.__layout = QVBoxLayout()
        self.__layout.setContentsMargins(10, 20, 10, 20)
        self.__layout.setSpacing(10)

        chemin_luckiest = os.path.join(os.path.dirname(__file__), "fonts", "LuckiestGuy-Regular.ttf")
        if os.path.exists(chemin_luckiest):
            font_id = QFontDatabase.addApplicationFont(chemin_luckiest)
            self.__police_titre = QFont("Luckiest Guy", 36) if font_id != -1 else QFont("Arial", 36, QFont.Weight.Bold)
            self.__police_bouton = QFont("Luckiest Guy", 14) if font_id != -1 else QFont("Arial", 14, QFont.Weight.Bold)
        else:
            self.__police_titre = QFont("Arial", 36, QFont.Weight.Bold)
            self.__police_bouton = QFont("Arial", 14, QFont.Weight.Bold)

        chemin_techno = os.path.join(os.path.dirname(__file__), "fonts", "Technology.ttf")
        if os.path.exists(chemin_techno):
            font_id_techno = QFontDatabase.addApplicationFont(chemin_techno)
            self.__police_chrono = QFont("TECHNOLOGY", 28) if font_id_techno != -1 else QFont("Arial", 28, QFont.Weight.Bold)
        else:
            self.__police_chrono = QFont("Arial", 28, QFont.Weight.Bold)

        self.__title = QLabel("MENU")
        self.__title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__title.setFont(self.__police_titre)
        self.__title.setStyleSheet("color: #FFFF00; background-color: transparent;")

        self.__separateur = QFrame()
        self.__separateur.setFrameShape(QFrame.Shape.HLine)
        self.__separateur.setStyleSheet("color: white; background-color: white; max-height: 2px;")

        self.__btn_verifier = QPushButton("Verifier")
        self.__btn_resoudre = QPushButton("Resoudre")
        self.__btn_nouvelle = QPushButton("Nouvelle Partie")
        self.__btn_sauvegarder = QPushButton("Sauvegarder")
        self.__btn_back = QPushButton("Retour Menu")

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
                    background-color: #ffe066;
                }
                QPushButton:pressed {
                    background-color: #ff8c00;
                }
            """)

        self.__temps = 0
        self.__chrono = QTimer(self)
        self.__chrono.timeout.connect(self.__incrementer)
        self.__label_chrono = QLabel("00:00")
        self.__label_chrono.setFont(self.__police_chrono)
        self.__label_chrono.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__label_chrono.setStyleSheet("color: #FFFF00; background-color: transparent;")

        self.__label_record = QLabel("Record : --:--")
        self.__label_record.setFont(self.__police_chrono)
        self.__label_record.setStyleSheet("color: #FFFF00; background-color: transparent; font-size: 14px;")
        self.__label_record.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.__layout.addWidget(self.__title)
        self.__layout.addWidget(self.__separateur)
        self.__layout.addWidget(self.__btn_verifier)
        self.__layout.addWidget(self.__btn_resoudre)
        self.__layout.addWidget(self.__btn_nouvelle)
        self.__layout.addWidget(self.__btn_sauvegarder)
        self.__layout.addWidget(self.__btn_back)
        self.__layout.addStretch()
        self.__layout.addWidget(self.__label_chrono)
        self.__layout.addWidget(self.__label_record)

        self.setLayout(self.__layout)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), self.__bg_color)

    def set_bg_color(self, color: str):
        self.__bg_color = QColor(color)
        self.update()

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

    def appliquer_theme(self, sombre: bool):
        self.__title.setStyleSheet("color: #FFFF00; background-color: transparent;")
        self.__label_chrono.setStyleSheet("color: #FFFF00; background-color: transparent;")
        self.__label_record.setStyleSheet("color: #FFFF00; background-color: transparent; font-size: 14px;")
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

    def get_label_chrono(self):
        return self.__label_chrono


# ----- interface de selection de difficulte ----- #

class SelectionDifficulte(QWidget):
    def __init__(self):
        super().__init__()
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#00689f"))
        self.setPalette(palette)

        chemin_luckiest = os.path.join(os.path.dirname(__file__), "fonts", "LuckiestGuy-Regular.ttf")
        if os.path.exists(chemin_luckiest):
            QFontDatabase.addApplicationFont(chemin_luckiest)

        police_titre = QFont("Luckiest Guy")
        police_titre.setPixelSize(110)

        police_texte = QFont("Luckiest Guy")
        police_texte.setPixelSize(20)

        police_bouton = QFont("Luckiest Guy")
        police_bouton.setPixelSize(28)

        layout_principal = QVBoxLayout()
        layout_principal.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_principal.setSpacing(40)
        layout_principal.setContentsMargins(50, 30, 50, 50)

        self.__label_titre = QLabel("NEONAURE!")
        self.__label_titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__label_titre.setFont(police_titre)
        self.__label_titre.setStyleSheet("color: #FFFF00; background-color: transparent;")
        effet_neon = QGraphicsDropShadowEffect()
        effet_neon.setBlurRadius(40)
        effet_neon.setColor(QColor(255, 255, 0))
        effet_neon.setOffset(0, 0)
        self.__label_titre.setGraphicsEffect(effet_neon)

        self.__label_description = QLabel(
            "choisissais le niveau de difficulte\n"
            "(facile: indice + verification en temps reel des voisinages)\n"
            "(difficile: pas d'indice + pas de verification du voisinage des cases)"
        )
        self.__label_description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__label_description.setFont(police_texte)
        self.__label_description.setStyleSheet("color: #ffffff; background-color: transparent;")
        self.__label_description.setWordWrap(True)

        layout_boutons = QHBoxLayout()
        layout_boutons.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_boutons.setSpacing(60)

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
        ombre_facile = QGraphicsDropShadowEffect()
        ombre_facile.setBlurRadius(20)
        ombre_facile.setColor(QColor(0, 0, 0))
        ombre_facile.setOffset(9, 12)
        self.__btn_facile.setGraphicsEffect(ombre_facile)

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
        self.setStyleSheet("background-color: #00689f;")

    def get_btn_facile(self):
        return self.__btn_facile

    def get_btn_difficile(self):
        return self.__btn_difficile


# ------- widget avec fond colore ------- #

class WidgetFond(QWidget):
    def __init__(self, couleur="#1a1a2e"):
        super().__init__()
        self.__bg = QColor(couleur)

    def set_couleur_fond(self, couleur: str):
        self.__bg = QColor(couleur)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), self.__bg)


# ------- vue principale ------- #

class Vue(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Neonaure")

        self.__grille_data = None
        self.__theme_sombre = True
        self.__difficulte_facile = True

        chemin_luckiest = os.path.join(os.path.dirname(__file__), "fonts", "LuckiestGuy-Regular.ttf")
        if os.path.exists(chemin_luckiest):
            font_id_luck = QFontDatabase.addApplicationFont(chemin_luckiest)
            self.__police_titre = QFont("Luckiest Guy", 48) if font_id_luck != -1 else QFont("Arial", 48, QFont.Weight.Bold)
        else:
            self.__police_titre = QFont("Arial", 48, QFont.Weight.Bold)

        chemin_techno = os.path.join(os.path.dirname(__file__), "fonts", "Technology.ttf")
        if os.path.exists(chemin_techno):
            font_id_techno = QFontDatabase.addApplicationFont(chemin_techno)
            self.__police_chrono = QFont("TECHNOLOGY", 28) if font_id_techno != -1 else QFont("Arial", 28, QFont.Weight.Bold)
        else:
            self.__police_chrono = QFont("Arial", 28, QFont.Weight.Bold)

        self.__selection_difficulte = SelectionDifficulte()

        self.__menu_gauche = MenuGauche()
        self.__menu_gauche.setObjectName("menuGauche")
        self.__menu_gauche.appliquer_theme(False)

        self.__grille_widget = GrilleWidget()
        self.__grille_widget.setObjectName("grilleWidget")

        self.__label_titre = QLabel("NEONAURE!")
        self.__label_titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__label_titre.setFont(self.__police_titre)
        self.__label_titre.setStyleSheet("color: #FFFF00; background-color: transparent;")
        effet_neon = QGraphicsDropShadowEffect()
        effet_neon.setBlurRadius(30)
        effet_neon.setColor(QColor(255, 255, 0))
        effet_neon.setOffset(0, 0)
        self.__label_titre.setGraphicsEffect(effet_neon)

        self.__temps = 0
        self.__chrono = QTimer(self)
        self.__chrono.timeout.connect(self.__incrementer)
        self.__label_chrono = QLabel("00:00")
        self.__label_chrono.setFont(self.__police_chrono)
        self.__label_chrono.setFixedSize(150, 50)
        self.__label_chrono.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__label_chrono.setStyleSheet("color: #FFFF00; background-color: transparent;")

        # Construction page jeu
        layout_principal = QHBoxLayout()

        zone_centrale = QVBoxLayout()
        zone_centrale.setAlignment(Qt.AlignmentFlag.AlignCenter)
        zone_centrale.addWidget(self.__label_titre, alignment=Qt.AlignmentFlag.AlignCenter)
        zone_centrale.addWidget(self.__grille_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        zone_centrale.addWidget(self.__label_chrono, alignment=Qt.AlignmentFlag.AlignCenter)

        self.__conteneur_centre = WidgetFond("#1a1a2e")
        self.__conteneur_centre.setObjectName("conteneurCentre")
        self.__conteneur_centre.setLayout(zone_centrale)

        layout_principal.addWidget(self.__menu_gauche, 1)
        layout_principal.addWidget(self.__conteneur_centre, 3)

        self.__widget_jeu = QWidget()
        self.__widget_jeu.setObjectName("widgetJeu")
        self.__widget_jeu.setLayout(layout_principal)

        self.__pages = QStackedWidget()
        self.__pages.addWidget(self.__selection_difficulte)
        self.__pages.addWidget(self.__widget_jeu)
        self.setCentralWidget(self.__pages)

        self.__pages.setCurrentIndex(0)
        # Appliquer le theme sombre au demarrage
        chemin_sombre_init = os.path.join(os.path.dirname(__file__), "theme_sombre.qss")
        with open(chemin_sombre_init, 'r', encoding='utf-8') as f:
            self.setStyleSheet(f.read())
        self.menuBar().hide()

        self.__creer_menu()

    def afficher_difficulte(self):
        self.__pages.setCurrentIndex(0)
        self.setStyleSheet("QMainWindow { background-color: #00689f; }")
        self.menuBar().hide()

    def afficher_grille_centree(self):
        self.__pages.setCurrentIndex(1)
        self.menuBar().show()
        # Couleurs via paintEvent
        self.__menu_gauche.set_bg_color("#16213e")
        if self.__theme_sombre:
            self.__conteneur_centre.set_couleur_fond("#1a1a2e")
        else:
            self.__conteneur_centre.set_couleur_fond("#00689f")

    def __creer_menu(self):
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
        self.__action_theme_clair.triggered.connect(lambda: self.__appliquer_theme(chemin_clair))
        menu_apparence.addAction(self.__action_theme_clair)

        self.__action_theme_sombre = QAction("Theme sombre", self)
        chemin_sombre = os.path.join(os.path.dirname(__file__), "theme_sombre.qss")
        self.__action_theme_sombre.triggered.connect(lambda: self.__appliquer_theme(chemin_sombre))
        menu_apparence.addAction(self.__action_theme_sombre)

    def __appliquer_theme(self, chemin_qss: str):
        with open(chemin_qss, 'r', encoding='utf-8') as f:
            qss = f.read()
        self.setStyleSheet(qss)

        self.__theme_sombre = "sombre" in chemin_qss

        # Couleurs via paintEvent
        self.__menu_gauche.set_bg_color("#16213e")
        if self.__theme_sombre:
            self.__conteneur_centre.set_couleur_fond("#1a1a2e")
        else:
            self.__conteneur_centre.set_couleur_fond("#00689f")

        self.__menu_gauche.appliquer_theme(self.__theme_sombre)

        self.__label_titre.setStyleSheet("color: #FFFF00; background-color: transparent;")
        self.__label_chrono.setStyleSheet("color: #FFFF00; background-color: transparent;")

        if self.__grille_data is not None:
            self.__grille_widget.afficher(self.__grille_data)

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