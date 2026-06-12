import sys
import os
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton
from PyQt6.QtGui import QFontDatabase, QFont

class MenuGauche(QWidget):
    def __init__(self):
        super().__init__()
        self.layout: QVBoxLayout = QVBoxLayout()
        
        # Widgets#
        self.title: QLabel = QLabel("Menu")
        self.title.setStyleSheet('font-family: "Luckiest Guy"; font-size: 30px; color: #FFFF00;')
        
        self.verify: QPushButton = QPushButton("Vérifier")
        self.solve: QPushButton = QPushButton("Résoudre")
        self.new: QPushButton = QPushButton("Nouvelle Partie")
        self.save: QPushButton = QPushButton("Sauvegarder")
        
        # Record#
        self.__record = None
        self.__label_record = QLabel("Record : --:--")
        self.__label_record.setStyleSheet('font-family: "TECHNOLOGY"; font-size: 20px; color: #FFFF00;')
        self.__label_record.setAlignment(Qt.AlignmentFlag.AlignHCenter)
       
        # Layout#
        self.vboxLayout: QVBoxLayout = QVBoxLayout()
        self.vboxLayout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.vboxLayout.addWidget(self.solve)
        self.vboxLayout.addWidget(self.new)
        self.vboxLayout.addWidget(self.save)
        self.vboxLayout.addWidget(self.verify)
        self.vboxLayout.addStretch()
        self.vboxLayout.addWidget(self.__label_record, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        self.VWidget: QWidget = QWidget()
        self.VWidget.setLayout(self.vboxLayout)
        
        self.layout.addWidget(self.VWidget, alignment=Qt.AlignmentFlag.AlignCenter)
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

    def appliquer_theme(self, sombre: bool):
        """Applique le thème sombre ou clair au menu."""
        if sombre:
            self.setStyleSheet("background-color: #16213e; color: white;")
            self.title.setStyleSheet('font-family: "Luckiest Guy"; font-size: 30px; color: #FFFF00;')
            self.__label_record.setStyleSheet('font-family: "TECHNOLOGY"; font-size: 20px; color: #FFFF00;')
        else:
            self.setStyleSheet("background-color: #002244; color: white;")
            self.title.setStyleSheet('font-family: "Luckiest Guy"; font-size: 30px; color: #FFFF00;')
            self.__label_record.setStyleSheet('font-family: "TECHNOLOGY"; font-size: 20px; color: #FFFF00;')

    # -------------- Getters -------------- #
    def get_btn_verify(self):
        return self.verify
    def get_btn_solve(self):
        return self.solve
    def get_btn_new(self):
        return self.new
    def get_btn_save(self):
        return self.save
    def get_label_record(self):
        return self.__label_record