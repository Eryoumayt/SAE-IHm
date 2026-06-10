import sys
import json
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QFileDialog
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt


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
            self.__label_accueil.setText(f"Grille chargée : {chemin}")

    def get_grille_data(self) -> dict:
        # Renvoie les données brutes de la grille chargée
        return self.__grille_data


if __name__ == "__main__":
    app = QApplication(sys.argv)
    vue = Vue()
    vue.show()
    sys.exit(app.exec())