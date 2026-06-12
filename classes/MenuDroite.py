import sys
import os
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton
from PyQt6.QtGui import QFontDatabase

class MenuDroite(QWidget):
    def __init__(self):
        pass
    
    

# -------------- MAIN -------------- #

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Liaison au fichier de la font (chemin relatif)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(base_dir, "vue\qss\LuckiestGuy-Regular.ttf", "LuckiestGuy-Regular.ttf")
    QFontDatabase.addApplicationFont(font_path)

    # Liaison au fichier qss pour le style du menu à droite (chemin relatif)
    qss_path = os.path.join(base_dir, "qss", "right_menu.qss")
    with open(qss_path, "r") as f:
        app.setStyleSheet(f.read())
        
    menu_droite = MenuDroite()
    menu_droite.show()
        
    sys.exit(app.exec())