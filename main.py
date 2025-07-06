import sys
import sqlite3
import os
from dotenv import load_dotenv
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QListWidget, QTabWidget, QCheckBox, QSplitter, QGroupBox, QSizePolicy,
    QFrame, QListWidgetItem, QDialog, QLineEdit, QMessageBox
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, Qt

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "carrello.db")


class LoginDialog(QDialog):
    def __init__(self, cursor):
        super().__init__()
        self.cursor = cursor
        self.setWindowTitle("Login")
        layout = QVBoxLayout()
        self.user_edit = QLineEdit()
        self.user_edit.setPlaceholderText("Username")
        self.pass_edit = QLineEdit()
        self.pass_edit.setPlaceholderText("Password")
        self.pass_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.handle_login)
        layout.addWidget(QLabel("Username:"))
        layout.addWidget(self.user_edit)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.pass_edit)
        layout.addWidget(self.login_btn)
        self.setLayout(layout)
        self.staff_id = None
        self.staff_name = None

    def handle_login(self):
        u = self.user_edit.text()
        p = self.pass_edit.text()

        # Determine available columns in staff table
        self.cursor.execute("PRAGMA table_info(staff)")
        cols = {r[1] for r in self.cursor.fetchall()}

        if "operator_id" in cols and "full_name" in cols:
            id_col = "operator_id"
            name_col = "full_name"
        else:
            id_col = "id"
            name_col = "name"

        if "password" in cols:
            query = f"SELECT {id_col}, {name_col} FROM staff WHERE username=? AND password=?"
            params = (u, p)
        else:
            query = f"SELECT {id_col}, {name_col} FROM staff WHERE username=?"
            params = (u,)

        self.cursor.execute(query, params)
        row = self.cursor.fetchone()
        if row:
            self.staff_id, self.staff_name = row
            self.accept()
        else:
            QMessageBox.warning(self, "Errore", "Credenziali non valide")

class MainWindow(QMainWindow):
    def __init__(self, conn, staff_id, staff_name):
        super().__init__()
        self.setWindowTitle("Carrello Farmaci - GUI Qt + SQLite")
        self.resize(1600, 900)

        self.conn = conn
        self.cursor = self.conn.cursor()
        self.staff_id = staff_id
        self.staff_name = staff_name

        self.farmaci_per_paziente = {}

        self.allocazioni = {}
        self.farmaci_da_somministrare = []
        self.farmaco_corrente_index = 0

        self.new_schema = self._detect_schema()


        self.view = QWebEngineView()
        self.view.load(QUrl("http://localhost:3000"))
        self.web_frame = QFrame()
        web_layout = QVBoxLayout()
        web_layout.setContentsMargins(0, 0, 0, 0)
        web_layout.setSpacing(0)
        web_layout.addWidget(self.view)
        self.web_frame.setLayout(web_layout)
        self.web_frame.setMinimumHeight(600)
        self.web_frame.setStyleSheet("QFrame { border: 1px solid #ccc; border-radius: 8px; background-color: #ffffff; }")

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 6px;
                background: #fafafa;
            }
            QTabBar::tab {
                background: #e0e0e0;
                border: 1px solid #ccc;
                padding: 8px 14px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 4px;
            }
            QTabBar::tab:selected {
                background: #ffffff;
                font-weight: bold;
                color: #000;
            }
        """)
        self.tabs.addTab(self._create_caricamento_tab(), "1. Caricamento")
        self.tabs.addTab(self._create_somministrazione_tab(), "2. Somministrazione")

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.tabs)
        splitter.addWidget(self.web_frame)
        splitter.setSizes([1000, 600])
        self.setCentralWidget(splitter)
        self.statusBar().showMessage(f"Operatore: {self.staff_name} (ID {self.staff_id})")

        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                font-size: 14px;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QGroupBox {
                border: 1px solid lightgray;
                border-radius: 8px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
                font-weight: bold;
                color: #333;
            }
            QListWidget, QComboBox {
                padding: 6px;
                border: 1px solid lightgray;
                border-radius: 4px;
                background-color: white;
            }
            QCheckBox {
                padding: 5px;
            }
            QLabel {
                font-size: 13px;
                color: #222;
            }
        """)

    def _detect_schema(self):
        """Return True if the DB uses the new columns (drug_code, qty_on_hand)."""
        self.cursor.execute("PRAGMA table_info(inventory)")
        cols = {r[1] for r in self.cursor.fetchall()}
        return "qty_on_hand" in cols

    def ensure_drug(self, name):
        """Ensure a drug exists and return its identifier (id or code)."""
        if self.new_schema:
            self.cursor.execute(
                "INSERT OR IGNORE INTO drug_master (drug_code, name) VALUES (?, ?)",
                (name, name),
            )
            self.cursor.execute(
                "SELECT drug_code FROM drug_master WHERE drug_code = ?",
                (name,),
            )
        else:
            self.cursor.execute(
                "INSERT OR IGNORE INTO drug_master (name) VALUES (?)",
                (name,),
            )
            self.cursor.execute(
                "SELECT id FROM drug_master WHERE name = ?",
                (name,),
            )
        row = self.cursor.fetchone()
        return row[0] if row else name

    def ensure_batch(self, drug, batch_number="DEF"):
        """Return the batch identifier for a drug, creating it if missing."""
        if self.new_schema:
            self.cursor.execute(
                "INSERT OR IGNORE INTO batch (drug_code, batch_number) VALUES (?, ?)",
                (drug, batch_number),
            )
            self.cursor.execute(
                "SELECT batch_id FROM batch WHERE drug_code=? AND batch_number=?",
                (drug, batch_number),
            )
            row = self.cursor.fetchone()
            return row[0] if row else None
        else:
            self.cursor.execute(
                "INSERT OR IGNORE INTO batch (drug_id, code) VALUES (?, ?)",
                (drug, batch_number),
            )
            return batch_number

    def ensure_compartment(self, drawer_id, number):
        """Return a compartment reference, inserting if needed."""
        if self.new_schema:
            comp_id = drawer_id * 100 + number
            label = f"D{drawer_id}-C{number}"
            self.cursor.execute(
                "INSERT OR IGNORE INTO compartment (compartment_id, drawer_id, label) VALUES (?, ?, ?)",
                (comp_id, drawer_id, label),
            )
            return comp_id
        else:
            self.cursor.execute(
                "INSERT OR IGNORE INTO compartment (drawer_id, number) VALUES (?, ?)",
                (drawer_id, number),
            )
            return number

    def add_inventory(self, drug, batch, drawer_id, number, qty):
        if self.new_schema:
            comp_id = self.ensure_compartment(drawer_id, number)
            self.cursor.execute(
                "INSERT OR IGNORE INTO inventory (compartment_id, drug_code, batch_id, qty_on_hand) VALUES (?, ?, ?, 0)",
                (comp_id, drug, batch),
            )
            self.cursor.execute(
                "SELECT qty_on_hand FROM inventory WHERE compartment_id=? AND drug_code=? AND batch_id=?",
                (comp_id, drug, batch),
            )
            row = self.cursor.fetchone()
            current = row[0] if row else 0
            self.cursor.execute(
                "UPDATE inventory SET qty_on_hand=? WHERE compartment_id=? AND drug_code=? AND batch_id=?",
                (current + qty, comp_id, drug, batch),
            )
            self.cursor.execute(
                "INSERT INTO movement (movement_type, compartment_id, drug_code, batch_id, qty, operator_id, timestamp) VALUES ('carico', ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)",
                (comp_id, drug, batch, qty, self.staff_id),
            )
        else:
            self.cursor.execute(
                "INSERT OR IGNORE INTO inventory (drug_id, batch_code, drawer_id, compartment_number, quantity) VALUES (?, ?, ?, ?, 0)",
                (drug, batch, drawer_id, number),
            )
            self.cursor.execute(
                "SELECT quantity FROM inventory WHERE drug_id=? AND batch_code=? AND drawer_id=? AND compartment_number=?",
                (drug, batch, drawer_id, number),
            )
            row = self.cursor.fetchone()
            current = row[0] if row else 0
            self.cursor.execute(
                "UPDATE inventory SET quantity=? WHERE drug_id=? AND batch_code=? AND drawer_id=? AND compartment_number=?",
                (current + qty, drug, batch, drawer_id, number),
            )
            self.cursor.execute(
                "INSERT INTO movement (drug_id, batch_code, drawer_id, compartment_number, change, movement_type, staff_id) VALUES (?, ?, ?, ?, ?, 'load', ?)",
                (drug, batch, drawer_id, number, qty, self.staff_id),
            )

    def remove_inventory(self, drug, batch, drawer_id, number, qty):
        if self.new_schema:
            comp_id = self.ensure_compartment(drawer_id, number)
            self.cursor.execute(
                "SELECT qty_on_hand FROM inventory WHERE compartment_id=? AND drug_code=? AND batch_id=?",
                (comp_id, drug, batch),
            )
            row = self.cursor.fetchone()
            if not row or row[0] <= 0:
                return
            new_q = max(0, row[0] - qty)
            self.cursor.execute(
                "UPDATE inventory SET qty_on_hand=? WHERE compartment_id=? AND drug_code=? AND batch_id=?",
                (new_q, comp_id, drug, batch),
            )
            self.cursor.execute(
                "INSERT INTO movement (movement_type, compartment_id, drug_code, batch_id, qty, operator_id, timestamp) VALUES ('somministrazione', ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)",
                (comp_id, drug, batch, -qty, self.staff_id),
            )
        else:
            self.cursor.execute(
                "SELECT quantity FROM inventory WHERE drug_id=? AND batch_code=? AND drawer_id=? AND compartment_number=?",
                (drug, batch, drawer_id, number),
            )
            row = self.cursor.fetchone()
            if not row or row[0] <= 0:
                return
            new_q = max(0, row[0] - qty)
            self.cursor.execute(
                "UPDATE inventory SET quantity=? WHERE drug_id=? AND batch_code=? AND drawer_id=? AND compartment_number=?",
                (new_q, drug, batch, drawer_id, number),
            )
            self.cursor.execute(
                "INSERT INTO movement (drug_id, batch_code, drawer_id, compartment_number, change, movement_type, staff_id) VALUES (?, ?, ?, ?, ?, 'dispense', ?)",
                (drug, batch, drawer_id, number, -qty, self.staff_id),
            )

    def _create_caricamento_tab(self):
        layout = QHBoxLayout()
        sx_group = QGroupBox("Seleziona Pazienti del Giro")
        sx = QVBoxLayout()

        self.dropdown_pazienti = QComboBox()
        self.dropdown_pazienti.addItems(["Mario Rossi", "Lucia Verdi", "Anna Bianchi", "Giuseppe Neri"])
        sx.addWidget(self.dropdown_pazienti)

        self.btn_aggiungi_paziente = QPushButton("Aggiungi Paziente")
        self.btn_aggiungi_paziente.clicked.connect(self.aggiungi_paziente)
        sx.addWidget(self.btn_aggiungi_paziente)

        self.lista_pazienti = QListWidget()
        sx.addWidget(self.lista_pazienti)

        self.btn_carica = QPushButton("Recupera Farmaci da API")
        self.btn_carica.clicked.connect(self.carica_medicinali)
        sx.addWidget(self.btn_carica)

        sx_group.setLayout(sx)

        dx_group = QGroupBox("Inserimento Farmaci")
        dx = QVBoxLayout()
        self.box_medicinali = QListWidget()
        dx.addWidget(self.box_medicinali)

        self.checkbox_caricato = QCheckBox("Farmaco inserito")
        self.checkbox_caricato.setEnabled(False)
        self.checkbox_caricato.stateChanged.connect(self.conferma_caricamento_farmaco)
        dx.addWidget(self.checkbox_caricato)

        self.btn_prossimo_farmaco = QPushButton("→ Prossimo Farmaco")
        self.btn_prossimo_farmaco.setEnabled(False)
        self.btn_prossimo_farmaco.clicked.connect(self.prossimo_farmaco)
        dx.addWidget(self.btn_prossimo_farmaco)

        dx_group.setLayout(dx)
        layout.addWidget(sx_group, 2)
        layout.addWidget(dx_group, 3)
        container = QWidget()
        container.setLayout(layout)
        return container

    def _create_somministrazione_tab(self):
        layout = QVBoxLayout()
        group = QGroupBox("Somministrazione Farmaci")
        group_layout = QVBoxLayout()

        form_layout = QHBoxLayout()
        label_paz = QLabel("Paziente:")
        label_paz.setFixedWidth(80)
        self.combo_pazienti = QComboBox()
        self.combo_pazienti.currentIndexChanged.connect(self.avvia_somministrazione)
        form_layout.addWidget(label_paz)
        form_layout.addWidget(self.combo_pazienti)

        self.label_farmaco_corrente = QLabel("Farmaco da somministrare:")
        self.label_farmaco_corrente.setStyleSheet("font-size: 15px; font-weight: bold; margin-top: 10px;")

        self.lista_farmaci_stato = QListWidget()
        self.lista_farmaci_stato.setFixedHeight(200)
        self.lista_farmaci_stato.itemClicked.connect(self.visualizza_farmaco_da_lista)
        self.cassetto_aperto_corrente = None

        self.btn_conferma_somministrazione = QPushButton("✓ Somministrato")
        self.btn_conferma_somministrazione.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn_conferma_somministrazione.setFixedHeight(40)
        self.btn_conferma_somministrazione.clicked.connect(self.prossimo_farmaco_da_somministrare)

        group_layout.addLayout(form_layout)
        group_layout.addWidget(self.label_farmaco_corrente)
        group_layout.addWidget(self.lista_farmaci_stato)
        group_layout.addWidget(self.btn_conferma_somministrazione)

        group.setLayout(group_layout)
        layout.addWidget(group)

        container = QWidget()
        container.setLayout(layout)
        return container

    def aggiungi_paziente(self):
        nome = self.dropdown_pazienti.currentText()
        if nome not in self.farmaci_per_paziente:
            self.farmaci_per_paziente[nome] = []
            self.lista_pazienti.addItem(nome)
            self.combo_pazienti.addItem(nome)


    def visualizza_farmaco_da_lista(self, item):
        nome_farmaco = item.text().strip("✅⏳ ").strip()
        self.label_farmaco_corrente.setText(f"Farmaco da somministrare: {nome_farmaco}")

        info = self.allocazioni.get(nome_farmaco)
        if not info:
            return

        cassetto_target = f"Cassetto{info['cassetto']}"

        # 🔁 Se si sta cambiando cassetto, chiudi quello precedente
        if self.cassetto_aperto_corrente and self.cassetto_aperto_corrente != cassetto_target:
            script_chiudi = f'window.chiudiCassetto("{self.cassetto_aperto_corrente}");'
            self.view.page().runJavaScript(script_chiudi)

        # 🧼 Spegni sempre lo scomparto attivo prima di illuminarne uno nuovo
        if self.cassetto_aperto_corrente:
            script_spegni = f'window.spegniScompartoAssociato("{self.cassetto_aperto_corrente}");'
            self.view.page().runJavaScript(script_spegni)

        # ✅ Apri il cassetto e illumina lo scomparto corretto
        script_apri = f'window.apriScomparto({info["cassetto"]}, {info["scomparto"]});'
        self.view.page().runJavaScript(script_apri)

        # 🔁 Aggiorna stato cassetto aperto
        self.cassetto_aperto_corrente = cassetto_target

            
    def carica_medicinali(self):
        from random import sample
        farmaci_possibili = ["Paracetamolo", "Ibuprofene", "Amoxicillina", "Aspirina", "Omeprazolo", "Metformina"]
        self.box_medicinali.clear()
        farmaci_giro = []
        scomparto_id = 1

        for i in range(self.lista_pazienti.count()):
            nome = self.lista_pazienti.item(i).text()
            farmaci = sample(farmaci_possibili, 3)
            self.farmaci_per_paziente[nome] = farmaci

            for f in farmaci:
                drug = self.ensure_drug(f)
                batch = self.ensure_batch(drug)

                drawer_id = ((scomparto_id - 1) // 6) + 1
                number = ((scomparto_id - 1) % 6) + 1
                cassetto = drawer_id
                scomparto = number
                scomparto_id += 1

                self.add_inventory(drug, batch, drawer_id, number, 1)

                self.allocazioni[f] = {
                    "cassetto": cassetto,
                    "scomparto": scomparto,
                    "drug": drug,
                    "batch": batch,
                    "drawer_id": drawer_id,
                    "number": number,
                }
                farmaci_giro.append(f)

        self.conn.commit()
        self.box_medicinali.addItems(farmaci_giro)
        if self.box_medicinali.count() > 0:
            self.box_medicinali.setCurrentRow(0)
            self.visualizza_farmaco_corrente()

    def visualizza_farmaco_corrente(self):
        farmaco = self.box_medicinali.currentItem().text()
        if farmaco in self.allocazioni:
            info = self.allocazioni[farmaco]
            script = f'window.apriScomparto({info["cassetto"]}, {info["scomparto"]});'
            self.view.page().runJavaScript(script)

            # ✅ Riattiva il checkbox ogni volta che si seleziona un farmaco
            self.checkbox_caricato.setEnabled(True)
            self.checkbox_caricato.setChecked(False)
            self.btn_prossimo_farmaco.setEnabled(False)

    def conferma_caricamento_farmaco(self):
        if self.checkbox_caricato.isChecked():
            farmaco = self.box_medicinali.currentItem().text()
            self.btn_prossimo_farmaco.setEnabled(True)
            info = self.allocazioni.get(farmaco)
            if info:
                script = f'window.chiudiCassetto("Cassetto{info["cassetto"]}");'
                self.view.page().runJavaScript(script)
            self.conn.commit()

    def prossimo_farmaco(self):
        row = self.box_medicinali.currentRow()
        if row < self.box_medicinali.count() - 1:
            self.box_medicinali.setCurrentRow(row + 1)
            self.visualizza_farmaco_corrente()
        else:
            self.checkbox_caricato.setEnabled(False)
            self.btn_prossimo_farmaco.setEnabled(False)

    def avvia_somministrazione(self):
        paziente = self.combo_pazienti.currentText()
        self.farmaci_da_somministrare = self.farmaci_per_paziente.get(paziente, [])
        self.farmaco_corrente_index = 0
        self.mostra_farmaco_corrente()
        self.aggiorna_lista_farmaci_stato(paziente)

    def mostra_farmaco_corrente(self):
        if self.farmaco_corrente_index < len(self.farmaci_da_somministrare):
            farmaco = self.farmaci_da_somministrare[self.farmaco_corrente_index]
            info = self.allocazioni.get(farmaco)
            if not info:
                return

            cassetto_target = f"Cassetto{info['cassetto']}"

            if self.cassetto_aperto_corrente and self.cassetto_aperto_corrente != cassetto_target:
                script_chiudi = f'window.chiudiCassetto("{self.cassetto_aperto_corrente}");'
                self.view.page().runJavaScript(script_chiudi)

            if self.cassetto_aperto_corrente:
                script_spegni = f'window.spegniScompartoAssociato("{self.cassetto_aperto_corrente}");'
                self.view.page().runJavaScript(script_spegni)

            script_apri = f'window.apriScomparto({info["cassetto"]}, {info["scomparto"]});'
            self.view.page().runJavaScript(script_apri)
            self.cassetto_aperto_corrente = cassetto_target

            self.label_farmaco_corrente.setText(f"Farmaco da somministrare: {farmaco}")
                
    def prossimo_farmaco_da_somministrare(self):
        if self.farmaco_corrente_index >= len(self.farmaci_da_somministrare):
            return

        farmaco = self.farmaci_da_somministrare[self.farmaco_corrente_index]
        info = self.allocazioni.get(farmaco)
        if info:
            self.remove_inventory(
                info["drug"],
                info["batch"],
                info["drawer_id"],
                info["number"],
                1,
            )
        self.conn.commit()

        # 🔒 Chiudi cassetto attuale
        if self.cassetto_aperto_corrente:
            script_chiudi = f'window.chiudiCassetto("{self.cassetto_aperto_corrente}");'
            self.view.page().runJavaScript(script_chiudi)
            self.cassetto_aperto_corrente = None

        self.farmaco_corrente_index += 1
        self.mostra_farmaco_corrente()
        self.aggiorna_lista_farmaci_stato(self.combo_pazienti.currentText())

    def aggiorna_lista_farmaci_stato(self, paziente):
        self.lista_farmaci_stato.clear()
        for i, f in enumerate(self.farmaci_da_somministrare):
            stato = "✅" if i < self.farmaco_corrente_index else "⏳"
            item = QListWidgetItem(f"{stato} {f}")
            self.lista_farmaci_stato.addItem(item)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    login = LoginDialog(cursor)
    if login.exec() != QDialog.DialogCode.Accepted:
        sys.exit(0)
    window = MainWindow(conn, login.staff_id, login.staff_name)
    window.show()
    sys.exit(app.exec())
