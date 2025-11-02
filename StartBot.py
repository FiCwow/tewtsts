# StartBot.py
import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

# === TWORZENIE FOLDERÓW ===
os.makedirs("logs", exist_ok=True)
os.makedirs("clients", exist_ok=True)
os.makedirs("Images", exist_ok=True)
os.makedirs("Save", exist_ok=True)

# === IMPORTUJ OKNO GŁÓWNE ===
try:
    from General.SelectClientWindow import SelectClientWindow
except Exception as e:
    print(f"[BŁĄD] Nie można zaimportować SelectClientWindow: {e}")
    sys.exit(1)

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # === CIEMNY MOTYW ===
    dark_theme = """
        QWidget {
            background-color: #2b2b2b;
            color: #e0e0e0;
            font-family: Segoe UI;
        }
        QPushButton {
            background-color: #3a3a3a;
            color: white;
            padding: 8px;
            border-radius: 6px;
            border: 1px solid #555;
        }
        QPushButton:hover {
            background-color: #4a4a4a;
        }
        QPushButton:pressed {
            background-color: #2a2a2a;
        }
        QPushButton:disabled {
            background-color: #333;
            color: #777;
        }
        QListWidget {
            background-color: #333;
            border: 1px solid #555;
            border-radius: 6px;
        }
        QListWidget::item:selected {
            background-color: #4A90E2;
        }
        QLineEdit, QSpinBox, QComboBox {
            background-color: #3a3a3a;
            border: 1px solid #555;
            border-radius: 4px;
            padding: 4px;
        }
        QLabel {
            color: #e0e0e0;
        }
        QTabWidget::pane {
            border: 1px solid #555;
        }
        QTabBar::tab {
            background: #3a3a3a;
            padding: 8px;
            margin: 2px;
        }
        QTabBar::tab:selected {
            background: #4A90E2;
        }
    """
    app.setStyleSheet(dark_theme)

    # === IKONA APLIKACJI (opcjonalnie) ===
    icon_path = "Images/Icon.jpg"
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # === URUCHOM OKNO GŁÓWNE ===
    window = SelectClientWindow()
    window.show()

    # === START APLIKACJI ===
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()