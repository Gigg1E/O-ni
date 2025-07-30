#utils/guild_db.py
import os
import sqlite3
from utils.config_loader import load_config

config = load_config()

def get_guild_db_path(guild_id):
    guild_folder = os.path.join(config["bfl_root"], str(guild_id))
    os.makedirs(guild_folder, exist_ok=True)
    return os.path.join(guild_folder, "oni_bot.db")

def create_guild_db(guild_id):
    db_path = get_guild_db_path(guild_id)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create example table — adapt schema as needed
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS example_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT NOT NULL,
            value TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()
