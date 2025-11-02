# Functions/Walker.py
import json
import os
import time
import random
import logging
from typing import List, Dict, Any
import Addresses
from Functions.ImageFunctions import click_on_tile, is_tile_blocked
from Functions.MemoryFunctions import read_int, read_short

# --- Logowanie ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')

# --- Stałe ---
WALK_DELAY_MIN = 0.6
WALK_DELAY_MAX = 1.2
STAIR_DELAY = 1.5

# --- Zmienne ---
waypoints: List[Dict[str, Any]] = []
current_index = 0
is_running = False

# --- Ładowanie waypoints ---
def load_waypoints(file_name: str = "default") -> bool:
    global waypoints, current_index
    path = f"Save/Waypoints/{file_name}.json"
    if not os.path.exists(path):
        logging.error(f"Nie znaleziono pliku: {path}")
        return False

    try:
        with open(path, 'r', encoding='utf-8') as f:
            waypoints = json.load(f)
        current_index = 0
        logging.info(f"Załadowano {len(waypoints)} waypointów z {file_name}")
        return True
    except Exception as e:
        logging.error(f"Błąd odczytu waypoints: {e}")
        return False

# --- Zapisywanie ---
def save_waypoints(file_name: str = "default"):
    path = f"Save/Waypoints/{file_name}.json"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(waypoints, f, indent=2, ensure_ascii=False)
    logging.info(f"Zapisano waypoints: {path}")

# --- Dodaj waypoint ---
def add_waypoint(x: int, y: int, z: int, direction: str = "Center", label: str = "", action: str = ""):
    waypoint = {
        "x": x, "y": y, "z": z,
        "direction": direction,
        "label": label,
        "action": action
    }
    waypoints.append(waypoint)
    logging.info(f"Dodano waypoint: {x},{y},{z} | {direction} | {label or '—'}")

# --- Główna pętla ---
def start_walking(file_name: str = "default"):
    global is_running
    if is_running:
        return
    if not load_waypoints(file_name):
        return
    is_running = True
    logging.info("Walker uruchomiony!")

    while is_running and waypoints:
        walk_step()
        time.sleep(random.uniform(WALK_DELAY_MIN, WALK_DELAY_MAX))

    is_running = False
    logging.info("Walker zatrzymany.")

def stop_walking():
    global is_running
    is_running = False

# --- Krok ---
def walk_step():
    global current_index
    if current_index >= len(waypoints):
        current_index = 0
        return

    wp = waypoints[current_index]
    my_x = read_int(Addresses.config["my_x"])
    my_y = read_int(Addresses.config["my_y"])
    my_z = read_short(Addresses.config["my_z"])

    # Sprawdź label
    if wp.get("label"):
        logging.info(f"[Label] {wp['label']}")

    # Wykonaj akcję
    if wp.get("action"):
        execute_action(wp["action"], wp["x"], wp["y"])

    # Idź w stronę waypointa
    dx = wp["x"] - my_x
    dy = wp["y"] - my_y

    direction = wp["direction"]
    if direction == "Center":
        if abs(dx) <= 1 and abs(dy) <= 1 and my_z == wp["z"]:
            current_index += 1
            return
    else:
        # Mapowanie kierunków
        dir_map = {
            "North": (0, -1), "South": (0, 1),
            "East": (1, 0), "West": (-1, 0),
            "NorthEast": (1, -1), "NorthWest": (-1, -1),
            "SouthEast": (1, 1), "SouthWest": (-1, 1)
        }
        if direction in dir_map:
            target_dx, target_dy = dir_map[direction]
            if dx == target_dx and dy == target_dy and my_z == wp["z"]:
                current_index += 1
                return

    # Ruch w stronę
    if abs(dx) > abs(dy):
        move_x = 1 if dx > 0 else -1
        move_y = 0
    else:
        move_x = 0
        move_y = 1 if dy > 0 else -1

    target_x = my_x + move_x
    target_y = my_y + move_y

    if not is_tile_blocked(target_x, target_y, my_z):
        click_on_tile(target_x, target_y)
        time.sleep(STAIR_DELAY if "stairs" in wp.get("label", "").lower() else 0.3)

# --- Akcje ---
def execute_action(action: str, x: int, y: int):
    parts = action.split()
    if not parts:
        return
    cmd = parts[0].lower()

    if cmd == "use_item" and len(parts) > 1:
        item_id = int(parts[1])
        use_item_on_tile(item_id, x, y)
    elif cmd == "say":
        text = " ".join(parts[1:])
        send_message(text)
    elif cmd == "wait":
        delay = float(parts[1]) if len(parts) > 1 else 1.0
        time.sleep(delay)

# --- Pomocnicze ---
def use_item_on_tile(item_id: int, x: int, y: int):
    # Tu użyj ImageFunctions lub pamięci
    logging.info(f"Używam item {item_id} na {x},{y}")

def send_message(text: str):
    # Tu wklej kod z SmartHotkeys lub Input
    logging.info(f"Wysyłam: {text}")