import sys
import os
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton, QFrame
from PyQt6.QtGui import QFontDatabase, QFont


class MenuGauche(QWidget):
    def __init__(self):
        super().__init__()

        # -------------- Widgets -------------- #

        # Titre "Menu"
        self.title: QLabel = QLabel("MENU")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet('font-family: "Luckiest Guy"; font-size: 36px; color: #FFFF00;')

        # Ligne séparatrice BLANCHE sous le titre
        self.__separator = QFrame()
        self.__separator.setFrameShape(QFrame.Shape.HLine)
        self.__separator.setFixedHeight(3)
        self.__separator.setStyleSheet("background-color: white; border: none;")

        # Boutons avec style jaune
        self.verify: QPushButton = QPushButton("Vérifier")
        self.solve: QPushButton = QPushButton("Résoudre")
        self.new: QPushButton = QPushButton("Nouvelle Partie")
        self.save: QPushButton = QPushButton("Sauvegarder")
        self.back: QPushButton = QPushButton("Retour Menu")

        # Style des boutons : jaune, orange au clic
        bouton_style = """
            QPushButton {
                background-color: #FFFF00;
                color: black;
                font-family: "Luckiest Guy";
                font-size: 14px;
                border: none;
                border-radius: 6px;
                padding: 10px 5px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #ffe066;
            }
            QPushButton:pressed {
                background-color: #ff8c00;
            }
        """
        for btn in [self.verify, self.solve, self.new, self.save, self.back]:
            btn.setStyleSheet(bouton_style)

        # Record du meilleur temps
        self.__record = None
        self.__label_record = QLabel("Record : --:--")
        self.__label_record.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__label_record.setStyleSheet('font-family: "TECHNOLOGY"; font-size: 20px; color: #FFFF00;')

        # -------------- Layout -------------- #
        self.vboxLayout: QVBoxLayout = QVBoxLayout()
        self.vboxLayout.setContentsMargins(15, 20, 15, 20)
        self.vboxLayout.setSpacing(10)

        self.vboxLayout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.vboxLayout.addWidget(self.__separator)
        self.vboxLayout.addSpacing(10)
        self.vboxLayout.addWidget(self.verify)
        self.vboxLayout.addWidget(self.solve)
        self.vboxLayout.addWidget(self.new)
        self.vboxLayout.addWidget(self.save)
        self.vboxLayout.addWidget(self.back)
        self.vboxLayout.addStretch()
        self.vboxLayout.addWidget(self.__label_record, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.VWidget: QWidget = QWidget()
        self.VWidget.setLayout(self.vboxLayout)

        self.layout: QVBoxLayout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.VWidget)
        self.setLayout(self.layout)

    # -------------- Record -------------- #

    def set_record(self, minutes: int, secondes: int):
        """Met à jour le record si le temps est meilleur que le précédent."""
        temps_total = minutes * 60 + secondes
        if self.__record is None or temps_total < self.__record:
            self.__record = temps_total
            self.__label_record.setText(f"Record : {minutes:02d}:{secondes:02d}")

    def reinitialiser_record(self):
        """Remet le record à zéro."""
        self.__record = None
        self.__label_record.setText("Record : --:--")

    # -------------- Thème -------------- #

    def appliquer_theme(self, sombre: bool):
        """Applique le thème sombre ou clair au menu."""
        if sombre:
            self.setStyleSheet("background-color: #16213e; color: white;")
        else:
            self.setStyleSheet("background-color: #002244; color: white;")

        # Préserver les styles personnalisés
        self.title.setStyleSheet('font-family: "Luckiest Guy"; font-size: 36px; color: #FFFF00;')
        self.__separator.setStyleSheet("background-color: white; border: none;")
        self.__label_record.setStyleSheet('font-family: "TECHNOLOGY"; font-size: 20px; color: #FFFF00;')

        # Re-appliquer le style des boutons
        bouton_style = """
            QPushButton {
                background-color: #FFFF00;
                color: black;
                font-family: "Luckiest Guy";
                font-size: 14px;
                border: none;
                border-radius: 6px;
                padding: 10px 5px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #ffe066;
            }
            QPushButton:pressed {
                background-color: #ff8c00;
            }
        """
        for btn in [self.verify, self.solve, self.new, self.save, self.back]:
            btn.setStyleSheet(bouton_style)

    # -------------- Getters -------------- #

    def get_btn_verify(self):
        return self.verify

    def get_btn_solve(self):
        return self.solve

    def get_btn_new(self):
        return self.new

    def get_btn_save(self):
        return self.save

    def get_btn_back(self):
        return self.back

    def get_label_record(self):
        return self.__label_record


# -------------- MAIN -------------- #

if __name__ == "__main__":
    app = QApplication(sys.argv)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(base_dir, "..", "vue", "qss", "LuckiestGuy-Regular.ttf")
    if os.path.exists(font_path):
        QFontDatabase.addApplicationFont(font_path)

    menu_gauche = MenuGauche()
    menu_gauche.show()

    sys.exit(app.exec())