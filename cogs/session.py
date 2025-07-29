import discord
from discord.ext import commands, tasks
from discord import app_commands
from discord.ui import View, Select
from core.session_manager import SessionManager
from utils.config_loader import load_config
import logging
import os
from pathlib import Path
from typing import Optional

config = load_config()

# Set up logger once
logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    ch.setFormatter(formatter)
    logger.addHandler(ch)


class SessionSelect(Select):
    def __init__(self, sessions: list[str], current_session: str):
        options = [
            discord.SelectOption(
                label=sess,
                description="Current session" if sess == current_session else "",
                default=(sess == current_session)
            ) for sess in sessions
        ]
        super().__init__(placeholder="Select a session to switch to", options=options, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        selected = self.values[0]
        cog: Optional[SessionCog] = interaction.client.get_cog("SessionCog")
        if cog:
            guild_id = interaction.guild.id
            user_id = interaction.user.id
            cog.set_session_name(guild_id, user_id, selected)
            await interaction.response.send_message(f"🧠 Switched to session `{selected}`", ephemeral=True)
        else:
            await interaction.followup.send("⚠️ SessionCog not found", ephemeral=True)


class SessionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bfl_root = Path(config["bfl_root"])
        temp_file = Path(config["temp_session_file"])

        self.sessions = SessionManager(
            db_path=os.path.join(config["bfl_root"], "sessions.db"),
            max_sessions=config["max_sessions_per_user"]
        )

        logger.debug(f"[SessionCog] SessionManager initialized with data_root={bfl_root}")
        self.active_session = {}  # {guild_id: {user_id: session_name}}
        self.sessions.filter_and_sync_sessions()


    def cog_unload(self):
        self.sessions.filter_and_sync_sessions.cancel()
        logger.debug("[SessionCog] Auto-save task canceled on unload.")

    @tasks.loop(minutes=30)
    async def auto_save_temp_sessions(self):
        try:
            self.sessions.filter_and_sync_sessions()

            logger.info("[AUTO] Temp sessions auto-saved successfully.")
        except Exception as e:
            logger.exception(f"[ERROR] Auto-save failed: {e}")

    def get_session_name(self, guild_id: int, user_id: int) -> str:
        return self.active_session.get(str(guild_id), {}).get(str(user_id), "default")

    def set_session_name(self, guild_id: int, user_id: int, name: str):
        self.active_session.setdefault(str(guild_id), {})[str(user_id)] = name
        logger.debug(f"[DEBUG] Set session for user {user_id} in guild {guild_id} to: {name}")


    @app_commands.command(name="savesession", description="💾 Save your current session to history.")
    async def savesession(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        name = self.get_session_name(guild_id, user_id)

        session_data = self.sessions.get_current_session(guild_id, user_id, name)
        try:
            if session_data:
                if self.sessions.save_session_to_disk(guild_id, user_id, session_data):
                    await interaction.followup.send(f"✅ Session `{name}` saved to history.")
                else:
                    await interaction.followup.send(f"⚠ Failed to save session `{name}`.", ephemeral=True)
            else:
                await interaction.followup.send(f"⚠ Nothing to save for session `{name}`.", ephemeral=True)
        except Exception as e:
            logger.error(f"[ERROR] Could not save session '{name}': {e}", exc_info=True)
            await interaction.followup.send(f"⚠ Failed to save session `{name}` due to an error.", ephemeral=True)
    
    @app_commands.command(name="listsession", description="📂 list all saved session.")
    async def listsession(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        sessions = self.sessions.list_sessions(guild_id, user_id)

        if sessions:
            await interaction.followup.send(f"📂 Your saved sessions:\n```\n" + "\n".join(sessions) + "\n```", ephemeral=False)
        else:
            await interaction.followup.send("🔎 No saved sessions found.", ephemeral=False)
    
    @app_commands.command(name="createsession", description="🆕 Create a new temporary session.")
    async def createsession(self, interaction: discord.Interaction, name: str):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        await interaction.response.defer(thinking=True)

        # Check if session already exists
        if self.sessions.get_current_session(guild_id, user_id, name):
            await interaction.followup.send(f"⚠ A temp session named `{name}` already exists.", ephemeral=True)
            return

        if name in self.sessions.list_sessions(guild_id, user_id):
            await interaction.followup.send(f"⚠ A saved session named `{name}` exists. Use `$switchsession {name}` to access it.", ephemeral=True)
            return
        try:
            self.sessions.update_session(guild_id, user_id, name, [])
            self.set_session_name(guild_id, user_id, name)
            self.sessions.filter_and_sync_sessions()


            await interaction.followup.send(f"🆕 Created and switched to temp session `{name}`.\n💾 Saved to memory.")
        except Exception as e:
            logger.error(f"[ERROR] Could not create session '{name}': {e}", exc_info=True)
            await interaction.followup.send(f"⚠ Failed to create session `{name}`.", ephemeral=True)

    @app_commands.command(name="deletesession", description="🗑️ Delete a saved session.")
    async def deletesession(self, interaction: discord.Interaction, name: str):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        await interaction.response.defer(thinking=True)
        try:
            self.sessions.delete_session(guild_id, user_id, name)
            await interaction.followup.send(f"❌ Session `{name}` deleted.", ephemeral=True)
        except Exception as e:
            logger.error(f"[ERROR] Could not delete session '{name}': {e}", exc_info=True)
            await interaction.followup.send(f"⚠ Failed to delete session `{name}`.", ephemeral=True)

    @app_commands.command(name="clearsession", description="🧹 Clear all messages in the current session.")
    async def clearsession(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        try:
            name = self.get_session_name(guild_id, user_id)
            self.sessions.update_session(guild_id, user_id, name, [])
            self.sessions.filter_and_sync_sessions()


            await interaction.followup.send(f"🧹 Cleared all messages in session `{name}`.", ephemeral=True)
        except Exception as e:
            logger.error(f"[ERROR] Error clearing session: {e}", exc_info=True)
            await interaction.followup.send("⚠️ Failed to clear session.", ephemeral=True)

    @app_commands.command(name="listcurrentsession", description="📌 Show your current session name.")
    async def listcurrentsession(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        try:
            current = self.get_session_name(guild_id, user_id)
            await interaction.followup.send(f"📌 Your current session: `{current}`", ephemeral=True)
        except Exception as e:
            logger.error(f"[ERROR] Error listing current session: {e}", exc_info=True)
            await interaction.followup.send("⚠️ Failed to retrieve current session.", ephemeral=True)

    @app_commands.command(name="switchsession", description="🔄 Switch to a different session.")
    async def switchsession(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        sessions = self.sessions.list_sessions(guild_id, user_id)
        try:
            if not sessions:
                await interaction.followup.send("⚠️ You have no saved sessions to switch to.", ephemeral=True)
                return

            current = self.get_session_name(guild_id, user_id)
            view = View(timeout=60)
            view.add_item(SessionSelect(sessions, current))
            await interaction.followup.send("Select a session to switch:", view=view, ephemeral=True)
        except Exception as e:
            logger.error(f"[ERROR] Error switching session: {e}", exc_info=True)
            await interaction.followup.send("⚠️ Failed to switch session.", ephemeral=True)

async def setup(bot):
    logger.debug("[SessionCog] Loading cog...")
    await bot.add_cog(SessionCog(bot))
    logger.info("[SessionCog] Loaded successfully.")