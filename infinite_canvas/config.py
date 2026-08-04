import os
import json

CONFIG_PATH = os.path.expanduser("~/.config/krita_infinite_canvas.json")

DEFAULT_CONFIG = {
    "margin": 150,
    "expand_step": 600,
    "check_interval": 200,
    "max_canvas_size": 20000,
    "auto_enable": False
}

def load_config():
    if not os.path.exists(CONFIG_PATH):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            config = DEFAULT_CONFIG.copy()
            config.update(data)
            return config
    except Exception:
        return DEFAULT_CONFIG.copy()

def save_config(config):
    try:
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"[InfiniteCanvas] Failed to save config: {e}")
