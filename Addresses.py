# Addresses.py
import json
import os
import logging
import ctypes as c
from typing import Dict, Any
import win32gui
import win32process

# === FOLDERY ===
os.makedirs("logs", exist_ok=True)

# === LOGOWANIE ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler("logs/bot.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# === ZMIENNE GLOBALNE ===
config: Dict[str, Any] = {}
process_handle = None
proc_id = None
base_address = None
game_window = None

# === ZMIENNE DO CZYTANIA ===
coordinates_x = coordinates_y = coordinates_z = 0
my_hp = my_hp_max = my_mp = my_mp_max = 0
target_x = target_y = target_z = target_hp = 0
target_name = ""

def load_client(client_name: str = "iglaots") -> bool:
    global config, process_handle, proc_id, base_address, game_window
    global coordinates_x, coordinates_y, coordinates_z
    global my_hp, my_hp_max, my_mp, my_mp_max
    global target_x, target_y, target_z, target_hp, target_name

    path = f"clients/{client_name}.json"
    if not os.path.exists(path):
        logging.error(f"Nie znaleziono: {path}")
        return False

    try:
        with open(path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        logging.info(f"Załadowano: {config['name']}")
    except Exception as e:
        logging.error(f"Błąd JSON: {e}")
        return False

    # === ZNAJDŹ OKNO ===
    game_window = find_window(config.get("client_name", "Tibia"))
    if not game_window:
        logging.error(f"Nie znaleziono okna: {config.get('client_name')}")
        return False

    # === PID + HANDLE ===
    proc_id = win32process.GetWindowThreadProcessId(game_window)[1]
    process_handle = c.windll.kernel32.OpenProcess(0x1F0FFF, False, proc_id)
    if not process_handle:
        logging.error("Nie można otworzyć procesu!")
        return False

    # === BASE ADDRESS ===
    try:
        modules = win32process.EnumProcessModules(process_handle)
        base_address = modules[0]
    except:
        logging.error("Nie można pobrać base address!")
        return False

    # === PIERWSZE ODCZYTANIE ===
    update_global_values()
    logging.info(f"Połączono | PID: {proc_id} | Base: 0x{base_address:X}")
    return True

def find_window(partial_name: str):
    windows = []
    def callback(hwnd, _):
        title = win32gui.GetWindowText(hwnd)
        if partial_name in title and "EasyBot" not in title:
            windows.append(hwnd)
    win32gui.EnumWindows(callback, None)
    return windows[0] if windows else None

def update_global_values():
    global coordinates_x, coordinates_y, coordinates_z
    global my_hp, my_hp_max, my_mp, my_mp_max
    global target_x, target_y, target_z, target_hp, target_name

    if not config or not process_handle:
        return

    from Functions.MemoryFunctions import read_int, read_short, read_byte, read_string

    try:
        coordinates_x = read_int(config["my_x"])
        coordinates_y = read_int(config["my_y"])
        coordinates_z = read_short(config["my_z"])
        my_hp = read_short(config["my_hp"])
        my_hp_max = read_short(config["my_hp_max"])
        my_mp = read_short(config["my_mp"])
        my_mp_max = read_short(config["my_mp_max"])
        target_x = read_int(config["target_x"])
        target_y = read_int(config["target_y"])
        target_z = read_short(config["target_z"])
        target_hp = read_byte(config["target_hp"])
        target_name = read_string(config["target_name"])
    except Exception as e:
        logging.error(f"Błąd odczytu pamięci: {e}")