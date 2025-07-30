# cogs/admin.py

import discord
from discord.ext import commands
from utils.config_loader import load_config
from core.session_manager import SessionManager
import zipfile
import tempfile
import logging
import shutil
from datetime import datetime
import os
import json
import sqlite3

config = load_config()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if not logger.hasHandlers():
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    ch.setFormatter(formatter)
    logger.addHandler(ch)


session_manager = SessionManager("data/servers/sessions.db")
max_sessions=config["max_sessions_per_user"]

def is_owner(ctx):
    is_owner = ctx.author.id == ctx.guild.owner_id or ctx.author.guild_permissions.administrator
    logger.debug(f"[USER] Permission check for user {ctx.author.id} on guild {ctx.guild.id}: is_owner={is_owner}")
    return is_owner

class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logger.debug("[DEBUG] Initializing AdminCog")

        self.sessions = session_manager
        self.db_path = self.sessions.db_path

        logger.debug(f"[DEBUG] SessionManager initialized with db_path={self.db_path} / max_sessions={max_sessions} / session_manager={self.sessions}")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """📁 Ensure folder structure is created when bot joins a server."""
        server_id = str(guild.id)
        path = os.path.join("data", "servers", server_id)
        os.makedirs(path, exist_ok=True)

        file_path = os.path.join(path, "channels.json")
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                json.dump({"welcome_channel": None}, f, indent=4)
            logger.info(f"[SERVER] Initialized server folder and channels.json for guild {server_id}")
        else:
            logger.info(f"[SERVER] Server folder already exists for guild {server_id}")

    @commands.command(name="setwelcome")
    @commands.has_permissions(administrator=True)
    async def set_welcome_channel(self, ctx, channel: discord.TextChannel):
        """📌 Set the welcome channel for this server."""
        server_id = str(ctx.guild.id)
        path = os.path.join("data", "servers", server_id)
        os.makedirs(path, exist_ok=True)

        file_path = os.path.join(path, "channels.json")
        data = {}

        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                data = json.load(f)

        data["welcome_channel"] = channel.id

        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)

        await ctx.send(f"✅ Welcome channel set to {channel.mention}")
        logger.info(f"[ADMIN] Welcome channel set to {channel.id} for guild {server_id}")

    @commands.command()
    @commands.check(is_owner)
    async def shutdown(self, ctx):
        """🛑 Safely shut down O-ni and flush session data to disk."""
        user_id = ctx.author.id
        guild_id = ctx.guild.id
        logger.info(f"[USER] Shutdown command invoked by user {user_id} in guild {guild_id}")
        try:
            await ctx.send("Shutting down. Saving all temp sessions...")
            self.sessions.filter_and_sync_sessions()
            self.sessions.flush_all_to_disk()
            self.sessions.temp_sessions.clear()
            self.sessions.flush_all_to_disk()
            logger.info("[AI] Sessions flushed and memory cleared.")
            await ctx.send("O-ni has been shut down safely. Goodbye! 👋")
            await self.bot.close()
        except Exception as e:
            logger.error(f"[ERROR] Error shutting down: {e}", exc_info=True)
            await ctx.send("⚠️ Error saving sessions and/or shutting down!")

    @commands.command()
    @commands.check(is_owner)
    async def reloadcogs(self, ctx):
        """♻ Reload all extensions (dev use only)."""
        user_id = ctx.author.id
        guild_id = ctx.guild.id
        logger.info(f"[USER] Reloadcogs command invoked by user {user_id} in guild {guild_id}")
        try:
            for ext in self.bot.extensions.copy():
                logger.debug(f"[DEBUG] Reloading extension: {ext}")
                await self.bot.reload_extension(ext)
            await ctx.send("🔄 All cogs reloaded.")
            logger.info("[AI] All cogs reloaded successfully.")
        except Exception as e:
            logger.error(f"[ERROR] Error reloading cogs: {e}", exc_info=True)
            await ctx.send("⚠️ Failed to reload cogs!")


    @commands.command(name="listdbsessions")
    @commands.has_permissions(administrator=True)
    async def list_db_sessions(self, ctx):
        """Admin command to list all sessions stored in the database."""
        logger.info(f"[COMMAND] listdbsessions invoked by {ctx.author} ({ctx.author.id})")
        await ctx.send("Command received, processing...", ephemeral=True)
        if not os.path.exists(self.db_path):
            await ctx.send("❌ No session database found.")
            return

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT guild_id, user_id, session_name FROM sessions")
            rows = cursor.fetchall()
            conn.close()

            logger.debug(f"[DB] Retrieved {len(rows)} rows from session DB")

            if not rows:
                await ctx.send("📁 No sessions found in the database.")
                return

            output = []
            for row in rows:
                g, u, s = row
                output.append(f"Guild: `{g}` | User: `{u}` | Session: `{s}`")

            chunks = [output[i:i+10] for i in range(0, len(output), 10)]
            for chunk in chunks:
                await ctx.send("\n".join(chunk))

        except Exception as e:
            logger.exception("[DB ERROR] Failed to query session DB")
            await ctx.send(f"❌ Error occurred: `{e}`")

    @commands.command(name="export")
    @commands.has_permissions(administrator=True)
    async def export_command(self, ctx, subcommand: str = None):
        if subcommand == "all":
            await self.export_all(ctx)
        else:
            await ctx.send("❓ Usage: `$export all`")

    async def export_all(self, ctx):
        await ctx.send("⏳ Exporting all sessions, please wait...")

        data = self.sessions.export_all_sessions()

        # Create temp folder
        temp_dir = tempfile.mkdtemp()
        export_folder = os.path.join(temp_dir, "EXPORTFOLDER")
        os.makedirs(export_folder, exist_ok=True)

        for guild_id, users in data.items():
            for user_id, sessions in users.items():
                user_dir = os.path.join(export_folder, str(guild_id), str(user_id))
                os.makedirs(user_dir, exist_ok=True)
                for session_name, session_data in sessions.items():
                    try:
                        file_path = os.path.join(user_dir, f"{session_name}.json")
                        with open(file_path, "w") as f:
                            json.dump(session_data, f, indent=4)
                    except Exception as e:
                        print(f"⚠️ Failed to write session '{session_name}': {e}")

        # Create zip
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"export_{timestamp}.zip"
        zip_path = os.path.join(temp_dir, zip_filename)
        shutil.make_archive(zip_path.replace(".zip", ""), 'zip', export_folder)

        # Send result
        try:
            await ctx.send(
                "✅ Export complete.",
                file=discord.File(zip_path, filename=zip_filename)
            )
        except discord.HTTPException:
            try:
                await ctx.author.send(
                    "⚠️ File too large to send in the channel. Here's your export via DM:",
                    file=discord.File(zip_path, filename=zip_filename)
                )
            except discord.HTTPException:
                await ctx.send("❌ Could not send file. It's likely too large for Discord.")

        # Clean up
        shutil.rmtree(temp_dir)



async def setup(bot):
    logger.debug("[DEBUG] Loading AdminCog cog...")
    await bot.add_cog(AdminCog(bot))
    logger.info("[AI] AdminCog loaded successfully.")