import json
import random
import glob
import os
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtCore import Qt, QObject, QEvent
from PyQt6.QtGui import QShortcut, QKeySequence
from .solver import solver
from .Grille import Grille
from PyQt6.QtCore import QThread, pyqtSignal


class SolverWorker(QThread):
    termine = pyqtSignal(bool, object)

    def __init__(self, chemin):
        super().__init__()
        self.chemin = chemin

    def run(self):
        s = solver(self.chemin)
        resultat = s.resolver()
        self.termine.emit(resultat, s.grille)


class controller(QObject):

    def __init__(self, model, view):
        super().__init__()

        self.model = model
        self.view = view
        self.case_selectionnee = None
        self.donnees_brutes = None
        self.chemin_grille = None
        self.__difficulte_facile = True

        # Connexions page difficulte
        self.view.get_selection_difficulte().get_btn_facile().clicked.connect(self.__on_difficulte_facile)
        self.view.get_selection_difficulte().get_btn_difficile().clicked.connect(self.__on_difficulte_difficile)

        # Connexions sidebar
        self.view.get_menu_gauche().get_btn_verifier().clicked.connect(self.on_check)
        self.view.get_menu_gauche().get_btn_resoudre().clicked.connect(self.on_solver)
        self.view.get_menu_gauche().get_btn_nouvelle().clicked.connect(self.new_game)
        self.view.get_menu_gauche().get_btn_sauvegarder().clicked.connect(self.on_save)
        self.view.get_menu_gauche().get_btn_back().clicked.connect(self.__on_retour_menu)

        # Connexions menu bar
        self.view.get_action_charger().triggered.connect(self.on_open)
        self.view.get_action_sauvegarder().triggered.connect(self.on_save)
        self.view.get_action_quitter().triggered.connect(self.view.close)
        self.view.get_action_regles().triggered.connect(self.on_regles)

        # Connexions changement de theme
        self.view.get_action_theme_clair().triggered.connect(self.__on_theme_change)
        self.view.get_action_theme_sombre().triggered.connect(self.__on_theme_change)

        # Raccourcis clavier
        QShortcut(QKeySequence(Qt.Key.Key_Delete), self.view).activated.connect(self.on_delete)
        QShortcut(QKeySequence("Ctrl+R"), self.view).activated.connect(self.on_solver)
        QShortcut(QKeySequence("Ctrl+N"), self.view).activated.connect(self.new_game)

    # -------------------------------------------------------- #

    def __on_difficulte_facile(self):
        self.__difficulte_facile = True
        self.view.set_difficulte_facile(True)
        self.new_game()

    def __on_difficulte_difficile(self):
        self.__difficulte_facile = False
        self.view.set_difficulte_facile(False)
        self.new_game()

    def __on_retour_menu(self):
        self.view.afficher_difficulte()

    # -------------------------------------------------------- #

    def __reconnecter_signaux(self):
        entries = self.view.get_grille_widget().get_entries()
        for (row, col), entry in entries.items():
            entry.installEventFilter(self)
            try:
                entry.textChanged.disconnect()
            except (RuntimeError, TypeError):
                pass
            entry.textChanged.connect(lambda texte, r=row, c=col: self.on_value_enter(r, c))

    # -------------------------------------------------------- #

    def __charger_grille(self, chemin):
        self.model = Grille(chemin)
        with open(chemin, 'r', encoding='utf-8') as f:
            self.donnees_brutes = json.load(f)
        self.chemin_grille = chemin

        self.view.set_grille_data(self.donnees_brutes)
        self.view.get_grille_widget().afficher(self.donnees_brutes)
        self.view.afficher_grille_centree()
        self.__reconnecter_signaux()

        self.view.reinitialiser_chrono()
        self.view.demarrer_chrono()
        self.view.get_menu_gauche().get_btn_resoudre().setEnabled(True)

    # -------------------------------------------------------- #

    def on_open(self):
        chemin, _ = QFileDialog.getOpenFileName(self.view, "Charger une grille", "", "JSON (*.json)")
        if not chemin:
            return
        self.__charger_grille(chemin)

    # -------------------------------------------------------- #

    def new_game(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        dossier_grilles = os.path.join(base_dir, "..", "Grille")
        grilles = glob.glob(os.path.join(dossier_grilles, "*.json"))
        if grilles:
            grille_choisie = random.choice(grilles)
            self.__charger_grille(grille_choisie)

    # -------------------------------------------------------- #

    def on_save(self):
        if self.donnees_brutes is None:
            QMessageBox.warning(self.view, "Attention", "Aucune grille chargee.")
            return

        entries = self.view.get_grille_widget().get_entries()
        grille_sauvegarde = {}

        for nom_motif, cases in self.donnees_brutes.items():
            nouvelle_liste = []
            for case in cases:
                row = case[0]
                col = case[1]
                valeur_init = case[2]
                entry = entries.get((row, col))
                if entry is not None:
                    texte = entry.text()
                    valeur_joueur = int(texte) if texte.isdigit() else 0
                    nouvelle_liste.append([row, col, 0, valeur_joueur])
                else:
                    nouvelle_liste.append([row, col, valeur_init, 0])
            grille_sauvegarde[nom_motif] = nouvelle_liste

        chemin, _ = QFileDialog.getSaveFileName(self.view, "Sauvegarder la grille", "", "Fichiers JSON (*.json)")
        if chemin:
            with open(chemin, 'w', encoding='utf-8') as f:
                json.dump(grille_sauvegarde, f, indent=4)
            QMessageBox.information(self.view, "Succes", "Grille sauvegardee.")

    # -------------------------------------------------------- #

    def on_check(self):
        if self.donnees_brutes is None:
            return

        entries = self.view.get_grille_widget().get_entries()
        for (row, col), entry in entries.items():
            texte = entry.text()
            nouvelle_valeur = int(texte) if texte.isdigit() else 0
            motif = self.model.get_motif(row, col)
            if motif is not None:
                case = motif.get_cases_by_pos(row, col)
                if case is not None:
                    case.valeur = nouvelle_valeur

        valide = self.model.is_valid()
        if valide:
            QMessageBox.information(self.view, "Verification", "La grille est valide !")
            self.view.arreter_chrono()
        else:
            QMessageBox.warning(self.view, "Verification", "La grille n'est pas valide.")

    # -------------------------------------------------------- #

    def on_solver(self):
        if self.donnees_brutes is None:
            return

        with open("temp_grille.json", 'w', encoding='utf-8') as f:
            json.dump(self.donnees_brutes, f)

        self.view.get_menu_gauche().get_btn_resoudre().setEnabled(False)
        self.worker = SolverWorker("temp_grille.json")
        self.worker.termine.connect(self.__on_solver_fini)
        self.worker.start()

    # -------------------------------------------------------- #

    def __on_solver_fini(self, resultat, grille):
        self.view.get_menu_gauche().get_btn_resoudre().setEnabled(True)

        if resultat:
            self.view.get_grille_widget().afficher(grille)
            self.__reconnecter_signaux()
            self.view.arreter_chrono()
            QMessageBox.information(self.view, "Resolution", "Solution trouvee !")
        else:
            QMessageBox.warning(self.view, "Resolution echouee", "Aucune solution n'a ete trouvee pour cette grille.")
        self.worker.quit()
        self.worker.wait()

    # -------------------------------------------------------- #

    def __on_theme_change(self):
        self.__reconnecter_signaux()

    # -------------------------------------------------------- #

    def on_regles(self):
        QMessageBox.information(self.view, "Regles du Neonature",
            "Le Neonature est un puzzle similaire au Suguru.\n\n"
            "3 regles :\n"
            "1. Chaque case doit contenir un chiffre.\n"
            "2. Les 8 voisins d'une case doivent avoir des valeurs differentes.\n"
            "3. Chaque motif de taille N doit contenir une permutation de 1 a N.\n\n"
            "Raccourcis :\n"
            "Ctrl+O : Charger une grille\n"
            "Ctrl+S : Sauvegarder\n"
            "Ctrl+R : Resoudre\n"
            "Ctrl+N : Nouvelle partie\n"
            "Suppr : Effacer la case\n"
            "Fleches : Naviguer entre les cases"
        )

    # -------------------------------------------------------- #

    def on_verifier_voisinage(self):
        if self.donnees_brutes is None:
            return

        entries = self.view.get_grille_widget().get_entries()

        toutes_valeurs = {}
        for nom_motif, cases in self.donnees_brutes.items():
            for case in cases:
                row = case[0]
                col = case[1]
                valeur_init = case[2]
                entry = entries.get((row, col))
                if entry is not None:
                    texte = entry.text()
                    val = int(texte) if texte.isdigit() and int(texte) != 0 else 0
                else:
                    val = valeur_init
                if val != 0:
                    toutes_valeurs[(row, col)] = val

        conflits = set()
        for (row, col), val in toutes_valeurs.items():
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    voisin_val = toutes_valeurs.get((row + dr, col + dc))
                    if voisin_val is not None and voisin_val == val:
                        if (row, col) in entries:
                            conflits.add((row, col))
                        if (row + dr, col + dc) in entries:
                            conflits.add((row + dr, col + dc))

        self.view.get_grille_widget().surligner_conflits(conflits)

    # -------------------------------------------------------- #

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.FocusIn:
            entries = self.view.get_grille_widget().get_entries()
            for (row, col), entry in entries.items():
                if entry is obj:
                    self.case_selectionnee = (row, col)
                    self.view.get_grille_widget().surligner_selection(row, col)
                    break

        elif event.type() == QEvent.Type.KeyPress:
            entries = self.view.get_grille_widget().get_entries()
            if event.key() == Qt.Key.Key_Delete:
                self.on_delete()
                return True
            if self.case_selectionnee is not None:
                row, col = self.case_selectionnee
                if event.key() == Qt.Key.Key_Up and (row - 1, col) in entries:
                    entries[(row - 1, col)].setFocus()
                    return True
                elif event.key() == Qt.Key.Key_Down and (row + 1, col) in entries:
                    entries[(row + 1, col)].setFocus()
                    return True
                elif event.key() == Qt.Key.Key_Left and (row, col - 1) in entries:
                    entries[(row, col - 1)].setFocus()
                    return True
                elif event.key() == Qt.Key.Key_Right and (row, col + 1) in entries:
                    entries[(row, col + 1)].setFocus()
                    return True

        return False

    # -------------------------------------------------------- #

    def on_value_enter(self, row, col):
        entries = self.view.get_grille_widget().get_entries()
        entry = entries.get((row, col))
        texte = entry.text()
        if not texte:
            return
        if texte.isdigit() and (int(texte) > 5 or int(texte) == 0):
            entry.clear()
            return

        if entry is not None and entry.text().isdigit() and int(entry.text()) != 0:
            positions = sorted(entries.keys())
            idx = positions.index((row, col))
            for i in range(idx + 1, len(positions)):
                prochaine = entries[positions[i]]
                if not prochaine.text().isdigit() or int(prochaine.text()) == 0:
                    prochaine.setFocus()
                    if self.__difficulte_facile:
                        self.on_verifier_voisinage()
                    return
            for i in range(0, idx):
                prochaine = entries[positions[i]]
                if not prochaine.text().isdigit() or int(prochaine.text()) == 0:
                    prochaine.setFocus()
                    if self.__difficulte_facile:
                        self.on_verifier_voisinage()
                    return
        if self.__difficulte_facile:
            self.on_verifier_voisinage()

    # -------------------------------------------------------- #

    def on_delete(self):
        if self.case_selectionnee is not None:
            entries = self.view.get_grille_widget().get_entries()
            entry = entries.get(self.case_selectionnee)
            if entry is not None:
                entry.clear()
