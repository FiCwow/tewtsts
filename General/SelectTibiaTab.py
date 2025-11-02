# General/SelectTibiaTab.py
import time
from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, QPushButton,
    QLabel, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import QTimer, Qt
from Addresses import (
    update_global_values, config, game_window,
    coordinates_x, coordinates_y, coordinates_z,
    my_hp, my_hp_max, my_mp, my_mp_max,
    target_hp, target_name
)
import win32gui
import logging

class SelectTibiaTab(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EasyBot 2.0 – Dane z gry")
        self.setFixedSize(1000, 650)
        self.running = False
        self.last_hp = 0
        self.last_x = 0
        self.init_ui()
        self.start_update_loop()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)

        # Tytuł
        title = QLabel("EasyBot 2.0 – Odczyt pamięci")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #4A90E2;")
        layout.addWidget(title)

        # Status
        self.status_label = QLabel("Status: <span style='color: orange;'>Oczekiwanie...</span>")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 16px;")
        layout.addWidget(self.status_label)

        # Dane z gry
        self.debug_labels = {}
        for label, key in [
            ("Pozycja", "pos"), ("HP", "hp"), ("MP", "mp"),
            ("Cel", "target")
        ]:
            row = QHBoxLayout()
            row.addWidget(QLabel(f"<b>{label}:</b>"))
            value = QLabel("—")
            value.setStyleSheet("color: #4A90E2; font-weight: bold;")
            row.addWidget(value)
            layout.addLayout(row)
            self.debug_labels[key] = value

        # Przyciski
        btns = QHBoxLayout()
        self.start_btn = QPushButton("START BOT")
        self.stop_btn = QPushButton("STOP BOT")
        self.stop_btn.setEnabled(False)
        for btn in (self.start_btn, self.stop_btn):
            btn.setStyleSheet("padding: 14px; font