# utils/config_loader.py
import json
import os

def load_config(path="config/config.json"):
    """Loads the global bot configuration."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"[ConfigLoader] Config file not found: {path}")
    with open(path, "r") as f:
        return json.load(f)


def get_allowed_channels(guild_id):
    path = os.path.join("data", "servers", str(guild_id), "channels.json")
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        data = json.load(f)
        return data.get("allowed", [])