import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QHBoxLayout

class Menu(QWidget):
    def __init__(self):
        
        super().__init__()
        self.layout: QHBoxLayout = QHBoxLayout()
        self.setLayout(self.layout)
        
        
        
        self.show()
        
# -------------- MAIN -------------- #

if __name__ == "__main__":
    app = QApplication(sys.argv)
    menu = Menu()
    sys.exit(app.exec())