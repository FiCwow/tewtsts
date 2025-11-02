# General/SelectClientWindow.py
import os
import json
import logging
import win32gui
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QPushButton, QDialog, QMessageBox, QComboBox, QLineEdit, QFormLayout  # <-- DODANO QFormLayout
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize

# === FOLDERY ===
os.makedirs("logs", exist_ok=True)
os.makedirs("clients", exist_ok=True)

# === LOGOWANIE ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler("logs/bot.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class SelectClientWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EasyBot – Zarządzaj OTS-ami")
        self.setFixedSize(520, 620)
        self.selected_client = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Tytuł
        title = QLabel("Wybierz lub dodaj OTS")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #4A90E2;")
        layout.addWidget(title)

        # Przyciski
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Dodaj OTS")
        self.edit_btn = QPushButton("Edytuj")
        self.delete_btn = QPushButton("Usuń")
        for btn in (self.add_btn, self.edit, self.edit_btn, self.delete_btn):
            btn.setStyleSheet("padding: 8px; border-radius: 6px; font-size: 13px;")
            btn_layout.addWidget(btn)
        layout.addLayout(btn_layout)

        self.add_btn.clicked.connect(self.add_ots)
        self.edit_btn.clicked.connect(self.edit_ots)
        self.delete_btn.clicked.connect(self.delete_ots)

        # Lista OTS-ów
        self.client_list = QListWidget()
        self.client_list.setIconSize(QSize(48, 48))
        self.client_list.itemClicked.connect(self.on_client_selected)
        layout.addWidget(self.client_list)

        # Start
        self.start_btn = QPushButton("URUCHOM BOTA")
        self.start_btn.setEnabled(False)
        self.start_btn.clicked.connect(self.start_bot)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2; color: white; font-weight: bold;
                padding: 14px; border-radius: 8px; font-size: 16px;
            }
            QPushButton:disabled { background-color: #555; }
            QPushButton:hover:enabled { background-color: #357ABD; }
        """)
        layout.addWidget(self.start_btn)

        self.load_clients()

    def load_clients(self):
        self.client_list.clear()
        for file in sorted(os.listdir("clients")):
            if not file.endswith(".json"):
                continue
            path = os.path.join("clients", file)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if "name" not in data or "client_name" not in data:
                    continue
                name = data["name"]
                key = file.replace(".json", "")
                item = QListWidgetItem()
                item.setText(name)
                item.setData(Qt.UserRole, key)
                icon_path = f"Images/{data['client_name']}/icon.png"
                item.setIcon(QIcon(icon_path if os.path.exists(icon_path) else "Images/Icon.jpg"))
                self.client_list.addItem(item)
            except Exception as e:
                logging.error(f"Błąd w {file}: {e}")
        if self.client_list.count() == 0:
            item = QListWidgetItem("Brak OTS-ów – dodaj pierwszy!")
            item.setFlags(Qt.NoItemFlags)
            self.client_list.addItem(item)

    def on_client_selected(self, item):
        if item.flags() & Qt.ItemIsSelectable:
            self.selected_client = item.data(Qt.UserRole)
            self.start_btn.setEnabled(True)
            self.edit_btn.setEnabled(True)
            self.delete_btn.setEnabled(True)
        else:
            self.start_btn.setEnabled(False)

    def add_ots(self):
        dialog = OTSEditorDialog()
        if dialog.exec_():
            self.save_ots(dialog.get_data())
            self.load_clients()

    def edit_ots(self):
        if not self.selected_client:
            return
        path = f"clients/{self.selected_client}.json"
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            dialog = OTSEditorDialog(data)
            if dialog.exec_():
                self.save_ots(dialog.get_data(), self.selected_client)
                self.load_clients()
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie można edytować: {e}")

    def delete_ots(self):
        if not self.selected_client:
            return
        reply = QMessageBox.question(self, "Usuń", f"Usunąć {self.selected_client}?")
        if reply == QMessageBox.Yes:
            os.remove(f"clients/{self.selected_client}.json")
            self.load_clients()
            self.selected_client = None
            self.start_btn.setEnabled(False)

    def save_ots(self, data, key=None):
        key = key or data["name"].lower().replace(" ", "")
        path = f"clients/{key}.json"
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logging.info(f"Zapisano OTS: {key}")
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie można zapisać: {e}")

    def start_bot(self):
        if not self.selected_client:
            return
        from General.SelectTibiaTab import SelectTibiaTab
        from Addresses import load_client
        try:
            if load_client(self.selected_client):
                self.tibia_window = SelectTibiaTab()
                self.tibia_window.show()
                self.close()
            else:
                QMessageBox.critical(self, "Błąd", "Nie znaleziono okna gry!")
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"{e}")


class OTSEditorDialog(QDialog):
    def __init__(self, data=None):
        super().__init__()
        self.setWindowTitle("Edytor OTS")
        self.setFixedSize(450, 600)
        self.data = data or {
            "name": "", "client_name": "", "square_size": 60, "collect_threshold": 0.85,
            "my_x": {"base": "", "offset": [0,0], "type": 3},
            "my_y": {"base": "", "offset": [0,0], "type": 3},
            "my_z": {"base": "", "offset": [0,0], "type": 2},
            "my_stats": {"base": ""},
            "my_hp": {"offset": [0,0], "type": 2},
            "my_hp_max": {"offset": [0,0], "type": 2},
            "my_mp": {"offset": [0,0], "type": 2},
            "my_mp_max": {"offset": [0,0], "type": 2},
            "attack": {"base": "", "offset": [0,0], "type": 3},
            "target_x": {"offset": 0, "type": 3},
            "target_y": {"offset": 0, "type": 3},
            "target_z": {"offset": 0, "type": 2},
            "target_hp": {"offset": 0, "type": 1},
            "target_name": {"offset": 0, "type": 6}
        }
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout(self)  # <-- TERAZ DZIAŁA
        self.inputs = {}

        # === WYBÓR OKNA ===
        self.window_combo = QComboBox()
        self.window_combo.addItem("— Wybierz okno Tibii/OTS —")
        self.refresh_windows()
        refresh_btn = QPushButton("Odśwież")
        refresh_btn.clicked.connect(self.refresh_windows)
        window_row = QHBoxLayout()
        window_row.addWidget(self.window_combo)
        window_row.addWidget(refresh_btn)
        layout.addRow("Okno gry:", window_row)

        # === POLA ===
        fields = [
            ("name", "Nazwa OTS", QLineEdit),
            ("square_size", "Rozmiar kwadratu", QLineEdit),
            ("collect_threshold", "Próg zbierania", QLineEdit),
        ]
        for key, label, widget in fields:
            w = widget()
            w.setText(str(self.data.get(key, "")))
            layout.addRow(label, w)
            self.inputs[key] = w

        # === ZAPIS ===
        save_btn = QPushButton("Zapisz OTS")
        save_btn.clicked.connect(self.accept)
        save_btn.setStyleSheet("background-color: #28a745; color: white; padding: 10px; font-weight: bold;")
        layout.addRow(save_btn)

    def refresh_windows(self):
        self.window_combo.clear()
        self.window_combo.addItem("— Wybierz okno Tibii/OTS —")
        windows = []
        def enum_cb(hwnd, _):
            title = win32gui.GetWindowText(hwnd)
            if title and ("tibia" in title.lower() or "ots" in title.lower()) and "EasyBot" not in title:
                windows.append(title)
        win32gui.EnumWindows(enum_cb, None)
        for title in windows:
            short = title[:50] + ("..." if len(title) > 50 else "")
            self.window_combo.addItem(short, title)
        if self.data.get("client_name"):
            idx = self.window_combo.findData(self.data["client_name"])
            if idx > 0:
                self.window_combo.setCurrentIndex(idx)

    def get_data(self):
        data = self.data.copy()
        selected = self.window_combo.currentData()
        if selected and selected != "— Wybierz okno Tibii/OTS —":
            data["client_name"] = selected
        for key, w in self.inputs.items():
            val = w.text().strip()
            if key in ["square_size", "collect_threshold"]:
                data[key] = float(val) if "." in val else int(val)
            else:
                data[key] = val
        return data