#----- lancement -----#
import sys
from PyQt6.QtWidgets import QApplication
from vue import Vue
from Controller import controller

if __name__ == "__main__":
    app = QApplication(sys.argv)
    vue = Vue()
    ctrl = controller(None, vue)
    vue.show()
    sys.exit(app.exec())