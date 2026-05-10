import json
import os
from pathlib import Path

CONFIG_FILE = Path.home() / ".buffer-cli-config.json"

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

def load_config():
    if not CONFIG_FILE.exists():
        return {}
    with open(CONFIG_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def set_access_token(token):
    config = load_config()
    config["access_token"] = token
    save_config(config)

def get_access_token():
    config = load_config()
    return config.get("access_token")
