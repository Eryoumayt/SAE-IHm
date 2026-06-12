import sys
import os
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton
from PyQt6.QtGui import QFontDatabase

class MenuGauche(QWidget):
    def __init__(self):
        super().__init__()
        self.layout: QVBoxLayout = QVBoxLayout()
        
        # -------------- Widgets qui compose l'application -------------- #
        # QLabel qui affiche Menu
        self.title: QLabel = QLabel("Menu")
        
        # QPushButtons qui permettent d'accèder à différentes fonctionnalitées
        self.verify: QPushButton = QPushButton("Vérifier")
        self.solve: QPushButton = QPushButton("Résoudre")
        self.new: QPushButton = QPushButton("Nouvelle Partie")
        self.save: QPushButton = QPushButton("Sauvegarder")
        self.back: QPushButton = QPushButton("Retour Menu")
        
        # chrono pour mesurer le temps de jeu #
        self.__temps = 0
        self.__chrono = QTimer(self)
        self.__chrono.timeout.connect(self.__incrementer)
        self.__label_chrono = QLabel("00:00")
       
       # -------------- Ajout des Widgets au layout -------------- #
        self.vboxLayout: QVBoxLayout = QVBoxLayout()
        self.vboxLayout.addWidget(self.title, alignment = Qt.AlignmentFlag.AlignHCenter)
        self.vboxLayout.addWidget(self.solve) ; self.vboxLayout.addWidget(self.new)
        self.vboxLayout.addWidget(self.save) ; self.vboxLayout.addWidget(self.back)
        self.vboxLayout.addWidget(self.__label_chrono, alignment = Qt.AlignmentFlag.AlignHCenter)
        
        self.VWidget: QWidget = QWidget()
        self.VWidget.setLayout(self.vboxLayout)
        
        self.layout.addWidget(self.VWidget, alignment = Qt.AlignmentFlag.AlignCenter)
        self.setLayout(self.layout)
        
    
    # -------------- Méthodes du chronomètre -------------- #
    
    def __incrementer(self):
        # Méthode permettant d'imcrémenter le chronomètre
        self.__temps += 1
        minutes = self.__temps // 60
        secondes = self.__temps % 60
        self.__label_chrono.setText(f"{minutes:02d}:{secondes:02d}")

    def demarrer_chrono(self):
        # Méthode permettant de démarrer le chronomètre
        self.__temps = 0
        self.__label_chrono.setText("00:00")
        self.__chrono.start(1000)  # toutes les 1000ms = 1s

    def arreter_chrono(self):
        # Méthode permettant d'arrêter le chronomètre
        self.__chrono.stop()

    def reinitialiser_chrono(self):
        # Méthode permettant de réinitialiser le chronomètre
        self.__chrono.stop()
        self.__temps = 0
        self.__label_chrono.setText("00:00")

    def appliquer_theme(self, sombre: bool):
        """Applique le thème sombre ou clair au menu."""
        if sombre:
            self.setStyleSheet("background-color: #16213e; color: white;")
            self.title.setStyleSheet("color: #FFFF00;")
            self.__label_chrono.setStyleSheet("color: #FFFF00;")
        else:
            self.setStyleSheet("background-color: #002244; color: white;")
            self.title.setStyleSheet("color: #FFFF00;")
            self.__label_chrono.setStyleSheet("color: #FFFF00;")

# -------------- MAIN -------------- #

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Liaison au fichier de la font (chemin relatif)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(base_dir, "vue\qss", "LuckiestGuy-Regular.ttf")
    QFontDatabase.addApplicationFont(font_path)

    # Liaison au fichier qss pour le style du menu à droite (chemin relatif)
    qss_path = os.path.join(base_dir, "qss", "right_menu.qss")
    with open(qss_path, "r") as f:
       app.setStyleSheet(f.read())
        
    menu_gauche = MenuGauche()
    menu_gauche.show()
        
    sys.exit(app.exec())