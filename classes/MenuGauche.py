import sys
import os
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton
from PyQt6.QtGui import QFontDatabase

class MenuGauche(QWidget):
    def __init__(self):
        super().__init__()
        self.layout: QVBoxLayout = QVBoxLayout()
        
        # Widgets#
        self.title: QLabel = QLabel("Menu")
        
        self.verify: QPushButton = QPushButton("Vérifier")
        self.solve: QPushButton = QPushButton("Résoudre")
        self.new: QPushButton = QPushButton("Nouvelle Partie")
        self.save: QPushButton = QPushButton("Sauvegarder")
        self.regles: QPushButton = QPushButton("Règles")
        self.quitter: QPushButton = QPushButton("Quitter")
        
        # Chrono#
        self.__temps = 0
        self.__chrono = QTimer(self)
        self.__chrono.timeout.connect(self.__incrementer)
        self.__label_chrono = QLabel("00:00")
       
        # Layout#
        self.vboxLayout: QVBoxLayout = QVBoxLayout()
        self.vboxLayout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.vboxLayout.addWidget(self.solve)
        self.vboxLayout.addWidget(self.new)
        self.vboxLayout.addWidget(self.save)
        self.vboxLayout.addWidget(self.verify)
        self.vboxLayout.addWidget(self.regles)
        self.vboxLayout.addWidget(self.quitter)
        self.vboxLayout.addWidget(self.__label_chrono, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        self.VWidget: QWidget = QWidget()
        self.VWidget.setLayout(self.vboxLayout)
        
        self.layout.addWidget(self.VWidget, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(self.layout)
    
    # -------------- Chrono -------------- #
    def __incrementer(self):
        self.__temps += 1
        minutes = self.__temps // 60
        secondes = self.__temps % 60
        self.__label_chrono.setText(f"{minutes:02d}:{secondes:02d}")

    def demarrer_chrono(self):
        self.__temps = 0
        self.__label_chrono.setText("00:00")
        self.__chrono.start(1000)

    def arreter_chrono(self):
        self.__chrono.stop()

    def reinitialiser_chrono(self):
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

    # -------------- Getters -------------- #
    def get_btn_verify(self):
        return self.verify
    def get_btn_solve(self):
        return self.solve
    def get_btn_new(self):
        return self.new
    def get_btn_save(self):
        return self.save
    def get_btn_regles(self):
        return self.regles
    def get_btn_quitter(self):
        return self.quitter
    def get_label_chrono(self):
        return self.__label_chrono
