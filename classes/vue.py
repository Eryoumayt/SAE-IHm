import sys
import json
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QFileDialog, QWidget, QGridLayout
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt

TAILLE_CASE = 60


class GrilleWidget(QWidget):
    '''
    affiche la grille de jeu.
    '''
    def __init__(self):
        super().__init__()
        self.__layout = QGridLayout()
        self.__layout.setSpacing(0)
        self.__layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.__layout)

    def afficher(self, grille_data: dict):
        '''
        Construit et affiche la grille à partir de JSON brutes.
        '''
        # Vide l'ancienne grille
        self.__vider()

        # Parcourt chaque motif et crée un label coloré pour chaque case
        for cases in grille_data.values():
            for case in cases:
                row = case[0]
                col = case[1]
                label = QLabel()
                label.setFixedSize(TAILLE_CASE, TAILLE_CASE)
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                label.setStyleSheet("background-color: lightgray; border: 1px solid gray;")
                self.__layout.addWidget(label, row, col)

    def __vider(self):
        '''
        Supprime tous les widgets de la grille.
        '''
        while self.__layout.count():
            item = self.__layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


class Vue(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Néonaure")

        # Données brutes de la grille chargée
        self.__grille_data = None

        # Label d'accueil
        self.__label_accueil = QLabel("Bienvenue dans Néonaure !\nChargez une grille via le menu Fichier.")
        self.__label_accueil.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(self.__label_accueil)

        # Composant grille
        self.__grille_widget = GrilleWidget()

        # Création du menu
        self.__creer_menu()

    def __creer_menu(self):
        menubar = self.menuBar()

        #  Menu Fichier
        menu_fichier = menubar.addMenu("Fichier")

        action_charger = QAction("Charger une grille", self)
        action_charger.triggered.connect(self.__charger_grille)
        menu_fichier.addAction(action_charger)

        menu_fichier.addSeparator()

        action_quitter = QAction("Quitter", self)
        action_quitter.triggered.connect(self.close)
        menu_fichier.addAction(action_quitter)

        #  Menu Jeu
        menubar.addMenu("Jeu")

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
            self.__grille_widget.afficher(self.__grille_data)
            self.setCentralWidget(self.__grille_widget)
            self.adjustSize()

    def get_grille_data(self) -> dict:
        # Renvoie les données brutes de la grille chargée
        return self.__grille_data


if __name__ == "__main__":
    app = QApplication(sys.argv)
    vue = Vue()
    vue.show()
    sys.exit(app.exec())