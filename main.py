#----- lancement -----#
import os
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase
from PyQt6.QtCore import Qt
from vue.menu import Menu
from classes.vue import Vue
from classes.Controller import controller



if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    luckiest_guy = os.path.join(base_dir, "vue", "qss", "LuckiestGuy-Regular.ttf")
    QFontDatabase.addApplicationFont(luckiest_guy)
    
    technology = os.path.join(base_dir, "vue", "qss", "Technology.ttf")
    QFontDatabase.addApplicationFont(technology)

    qss_path = os.path.join(base_dir, "vue", "qss", "menu_style.qss")    
    with open(qss_path, "r") as f:
        app.setStyleSheet(f.read())
    menu = Menu()
    menu.setWindowState(Qt.WindowState.WindowMaximized)
    menu.show()
    
    def lancer_jeu():
        menu.close()
        fenetre = Vue()
        menu.ctrl = controller(None, fenetre)
        fenetre.setWindowState(Qt.WindowState.WindowMaximized)
        fenetre.show()
        
    menu.get_start().clicked.connect(lancer_jeu)
    sys.exit(app.exec())