import discord
from discord import app_commands
from discord.ext import commands
from core.session_manager import SessionManager
import logging
import json
import tempfile
import os

# --- Setup logger ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if not logger.hasHandlers():
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

import zipfile
from typing import Optional

class ExportCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session_mgr = SessionManager("data/servers/sessions.db")
        self.db_path = self.session_mgr.db_path

    @app_commands.command(name="export", description="Export your session(s) by name or all")
    @app_commands.describe(session_name="Optional: the name of the session to export (export all if omitted)")
    async def export(self, interaction: discord.Interaction, session_name: Optional[str] = None):
        await interaction.response.defer(thinking=True)
        logger.debug(f"[Export] Export command called by user {interaction.user.id} in guild {interaction.guild.id} with session_name={session_name}")
        user_id = interaction.user.id

        if session_name:
            # Export one session
            data = self.session_mgr.export_user_session(user_id, session_name)
            if not data:
                await interaction.followup.send(f"❌ Session '{session_name}' not found.", ephemeral=True)
                logger.error(f"[Export] Session '{session_name}' not found for user {user_id}")
                return

            content = json.dumps(data, indent=2)
            filename = f"{session_name}.json"

            with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8', suffix='.json') as f:
                logger.debug(f"[Export] Writing single session to temp file: {f.name}")
                f.write(content)
                temp_path = f.name

            await interaction.followup.send(
                content=f"📦 Exported session `{session_name}` successfully!",
                file=discord.File(temp_path, filename=filename)
            )
            os.remove(temp_path)
            logger.info(f"[Export] Session '{session_name}' exported successfully for user {user_id}")

        else:
            # Export all sessions for user as zip
            sessions = self.session_mgr.get_all_sessions_for_user(user_id)
            # Expected: sessions is a dict: { session_name: data, ... }
            if not sessions:
                await interaction.followup.send("❌ You have no sessions to export.", ephemeral=True)
                logger.error(f"[Export] No sessions found for user {user_id}")
                return

            with tempfile.TemporaryDirectory() as tempdir:
                zip_path = os.path.join(tempdir, f"sessions_{user_id}.zip")
                with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                    for sname, sdata in sessions.items():
                        filename = f"{sname}.json"
                        file_path = os.path.join(tempdir, filename)
                        with open(file_path, "w", encoding="utf-8") as f:
                            json.dump(sdata, f, indent=2)
                        zipf.write(file_path, arcname=filename)
                        logger.debug(f"[Export] Added '{filename}' to zip for user {user_id}")

                await interaction.followup.send(
                    content=f"📦 Exported all your sessions successfully!",
                    file=discord.File(zip_path, filename=f"sessions_{user_id}.zip")
                )
                logger.info(f"[Export] All sessions exported successfully for user {user_id}")


async def setup(bot):
    logger.debug("[DEBUG] Loading ExportCog cog...")
    await bot.add_cog(ExportCog(bot))
    logger.info("[AI] ExportCog loaded successfully.")
