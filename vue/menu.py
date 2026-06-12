import sys
import os
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton
from PyQt6.QtGui import QFontDatabase

class Menu(QWidget):
    def __init__(self):
        
        super().__init__()
        self.layout: QVBoxLayout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setWindowTitle("Néonaure")
        self.resize(400, 700)
        
        # ------------- QLabel (Titre) ------------- #
        
        self.game_title: QLabel = QLabel("Néonaure")
        self.game_title.setObjectName("Title")
        
        # ------------- QPushButtons (Démarrer et Paramètres) ------------- #
        
        self.start: QPushButton = QPushButton("Démarrer")
        
        self.settings: QPushButton = QPushButton("Paramètres")
        
        # ------------- QLabel (Crédit en bas de page) ------------- #
        
        self.credits: QLabel = QLabel("Isaac PILLE-YARD - Youenn DEZITTER - Arthur LECLERC")
        self.credits.setObjectName("Credits")
        
        # ------------- Ajouts des Widgets au Layout ------------- #
        
        self.vboxLayout = QVBoxLayout()
        
        self.vboxLayout.addWidget(self.game_title)
        self.vboxLayout.addWidget(self.start) ; self.vboxLayout.addWidget(self.settings)
        
        self.vboxWidget = QWidget()
        self.vboxWidget.setLayout(self.vboxLayout)
        
        self.layout.addStretch() # Permet d'espacer vboxWidget au centre
        self.layout.addWidget(self.vboxWidget, alignment = Qt.AlignmentFlag.AlignCenter)
        self.layout.addStretch() # Permet de déplacer les crédits en bas de page
        self.layout.addWidget(self.credits, alignment = Qt.AlignmentFlag.AlignCenter)
        
        
 # ------------- Getters ------------- #
    def get_start(self):
       return self.start
        
        
# -------------- MAIN -------------- #

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
    
#     base_dir = os.path.dirname(os.path.abspath(__file__))
#     font_path = os.path.join(base_dir, "qss", "LuckiestGuy-Regular.ttf")
#     QFontDatabase.addApplicationFont(font_path)

#     qss_path = os.path.join(base_dir, "qss", "menu_style.qss")
#     with open(qss_path, "r") as f:
#         app.setStyleSheet(f.read())
        
#     menu = Menu()
#     menu.show()
        
#     sys.exit(app.exec())