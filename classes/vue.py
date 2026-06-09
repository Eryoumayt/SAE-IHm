import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt


class Vue(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Néonaure")

        # Label d'accueil
        self.__label_accueil = QLabel("Bienvenue dans Néonaure !")
        self.__label_accueil.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(self.__label_accueil)

        # Création du menu
        self.__creer_menu()

    def __creer_menu(self):
        menubar = self.menuBar()

        #  Menu Fichier 
        menubar.addMenu("Fichier")

        #  Menu Jeu 
        menubar.addMenu("Jeu")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    vue = Vue()
    vue.show()
    sys.exit(app.exec())