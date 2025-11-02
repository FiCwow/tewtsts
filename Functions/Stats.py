import time
import json

start_time = time.time()
xp_start = 0
loot_value = 0

def save():
    stats = {
        "czas": round(time.time() - start_time),
        "xp_h": round((get_current_xp() - xp_start) / ((time.time() - start_time)/3600)),
        "loot": loot_value
    }
    with open("Save/stats.json", "w") as f:
        json.dump(stats, f, indent=2)