import os
import json
import sqlite3
import logging
from pathlib import Path
from typing import List, Dict, Any

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if not logger.hasHandlers():
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

class SessionManager:
    def __init__(self, db_path: str, max_sessions: int = 5):
        self.db_path = Path(db_path)
        self.max_sessions = max_sessions
        self.temp_sessions = {}  # in-memory cache
        self._initialize_db()

    def _initialize_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    guild_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    session_name TEXT NOT NULL,
                    messages TEXT NOT NULL,
                    PRIMARY KEY (guild_id, user_id, session_name)
                );
            """)
            conn.commit()
            conn.close()
            logger.info(f"[AI] SQLite database initialized at {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"[ERROR] Failed to initialize SQLite database at {self.db_path}: {e}", exc_info=True)
            raise

    def _get_db_connection(self):
        return sqlite3.connect(self.db_path)

    def _load_session_from_db(self, guild_id: str, user_id: str, session_name: str) -> List[Dict[str, str]] | None:
        conn = self._get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT messages FROM sessions
                WHERE guild_id = ? AND user_id = ? AND session_name = ?;
            """, (str(guild_id), str(user_id), session_name))
            row = cursor.fetchone()
            if row:
                messages_json = row[0]
                messages = json.loads(messages_json)
                logger.info(f"[AI] Loaded session '{session_name}' for user {user_id} from DB")
                return messages
            else:
                logger.debug(f"[DEBUG] Session '{session_name}' not found in DB for user {user_id}")
                return None
        except (sqlite3.Error, json.JSONDecodeError) as e:
            logger.error(f"[ERROR] Failed to load or decode session '{session_name}' from DB: {e}", exc_info=True)
            return None
        finally:
            conn.close()

    def _save_session_to_db(self, guild_id: str, user_id: str, session_name: str, messages: List[Dict[str, str]]):
        conn = self._get_db_connection()
        cursor = conn.cursor()
        try:
            messages_json = json.dumps(messages)
            cursor.execute("""
                INSERT OR REPLACE INTO sessions (guild_id, user_id, session_name, messages)
                VALUES (?, ?, ?, ?);
            """, (str(guild_id), str(user_id), session_name, messages_json))
            conn.commit()
            logger.info(f"[AI] Saved/Updated session '{session_name}' for user {user_id} in guild {guild_id} to DB")
            return True
        except sqlite3.Error as e:
            logger.error(f"[ERROR] Failed to save session '{session_name}' to DB: {e}", exc_info=True)
            return False
        finally:
            conn.close()

    def _store_temp(self, guild_id: str, user_id: str, session_name: str, messages: List[Dict[str, str]]):
        self.temp_sessions.setdefault(str(guild_id), {}).setdefault(str(user_id), {})[session_name] = messages
        logger.debug(f"[DEBUG] Stored session '{session_name}' in temp for user {user_id} in guild {guild_id} (messages count: {len(messages)})")

    def get_current_session(self, guild_id: str, user_id: str, session_name: str) -> List[Dict[str, str]]:
        session = self.temp_sessions.get(str(guild_id), {}).get(str(user_id), {}).get(session_name, None)
        if session is not None:
            logger.debug(f"[DEBUG] Retrieved current session '{session_name}' from temp for user {user_id} in guild {guild_id} (messages count: {len(session)})")
            return session
        else:
            db_messages = self._load_session_from_db(guild_id, user_id, session_name)
            if db_messages is not None:
                self._store_temp(guild_id, user_id, session_name, db_messages)
                return db_messages
            else:
                return []

    def update_session(self, guild_id: str, user_id: str, session_name: str, messages: List[Dict[str, str]]):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO sessions
                    (guild_id, user_id, session_name, messages)
                    VALUES (?, ?, ?, ?);
                """, (str(guild_id), str(user_id), session_name, json.dumps(messages)))
                conn.commit()
            self._store_temp(guild_id, user_id, session_name, messages)
            logger.info(f"[AI] Updated session '{session_name}' for user {user_id} in guild {guild_id}")
            return True
        except sqlite3.Error as e:
            logger.error(f"[ERROR] Failed to update session '{session_name}' for user {user_id} in guild {guild_id}: {e}", exc_info=True)
            return False

    def export_user_session(self, user_id: int, session_name: str) -> dict:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT messages FROM sessions WHERE user_id = ? AND session_name = ?", (user_id, session_name))
        row = c.fetchone()
        conn.close()

        if not row:
            return None

        try:
            content = json.loads(row[0])
        except json.JSONDecodeError:
            content = {"content": row[0]}

        return content

    def export_all_sessions(self) -> dict:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT guild_id, user_id, session_name, messages FROM sessions")
        rows = c.fetchall()
        conn.close()

        export_data = {}
        for guild_id, user_id, session_name, content in rows:
            export_data.setdefault(str(guild_id), {}).setdefault(str(user_id), {})[session_name] = content
        return export_data


    def get_all_sessions_for_user(self, user_id: int) -> List[str]:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT session_name FROM sessions WHERE user_id = ?", (user_id,))
            rows = cursor.fetchall()
            conn.close()

            session_names = [row[0] for row in rows]
            logger.debug(f"[SessionManager] Found {len(session_names)} sessions for user {user_id}")
            return session_names

        except Exception as e:
            logger.error(f"[SessionManager] Failed to fetch sessions for user {user_id}: {e}")
            return []


    def list_sessions(self, guild_id: str, user_id: str) -> List[str]:
        conn = self._get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT session_name FROM sessions
                WHERE guild_id = ? AND user_id = ?;
            """, (str(guild_id), str(user_id)))
            sessions = [row[0] for row in cursor.fetchall()]
            return sessions
        except sqlite3.Error as e:
            logger.error(f"[ERROR] Failed to list sessions for user {user_id} in guild {guild_id}: {e}", exc_info=True)
            return []
        finally:
            conn.close()

    def delete_session(self, guild_id: str, user_id: str, session_name: str):
        try:
            if str(guild_id) in self.temp_sessions and \
               str(user_id) in self.temp_sessions[str(guild_id)] and \
               session_name in self.temp_sessions[str(guild_id)][str(user_id)]:
                del self.temp_sessions[str(guild_id)][str(user_id)][session_name]
                logger.info(f"[AI] Deleted session '{session_name}' from temp for user {user_id} in guild {guild_id}")
        except KeyError:
            logger.debug(f"[DEBUG] Session '{session_name}' not found in temp for deletion due to missing keys.")

        conn = self._get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                DELETE FROM sessions
                WHERE guild_id = ? AND user_id = ? AND session_name = ?;
            """, (str(guild_id), str(user_id), session_name))
            conn.commit()
        except sqlite3.Error as e:
            logger.error(f"[ERROR] Failed to delete session '{session_name}' from DB: {e}", exc_info=True)
        finally:
            conn.close()

    def filter_and_sync_sessions(self):
        logger.info("[SYNC] Filtering and syncing all temp sessions to DB...")
        for guild_id, users in list(self.temp_sessions.items()):
            for user_id, sessions in list(users.items()):
                for session_name, messages in list(sessions.items()):
                    if isinstance(messages, list) and all('role' in m and 'content' in m for m in messages):
                        if messages:
                            self._save_session_to_db(guild_id, user_id, session_name, messages)
                        else:
                            del self.temp_sessions[guild_id][user_id][session_name]
                            if not self.temp_sessions[guild_id][user_id]:
                                del self.temp_sessions[guild_id][user_id]
                            if not self.temp_sessions[guild_id]:
                                del self.temp_sessions[guild_id]
                    else:
                        del self.temp_sessions[guild_id][user_id][session_name]
                        if not self.temp_sessions[guild_id][user_id]:
                            del self.temp_sessions[guild_id][user_id]
                        if not self.temp_sessions[guild_id]:
                            del self.temp_sessions[guild_id]
        logger.info("[SYNC] Filtering and sync completed.")

    def flush_all_to_disk(self):
        logger.info("[AI] Flushing all temp sessions to disk on shutdown (via sync).")
        self.filter_and_sync_sessions()
        logger.info("[AI] Completed flushing all temp sessions to disk.")