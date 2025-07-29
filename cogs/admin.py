# cogs/admin.py

import discord
from discord.ext import commands
from utils.config_loader import load_config
from core.session_manager import SessionManager
import logging
import os
import json

config = load_config()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if not logger.hasHandlers():
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

def is_owner(ctx):
    is_owner = ctx.author.id == ctx.guild.owner_id or ctx.author.guild_permissions.administrator
    logger.debug(f"[USER] Permission check for user {ctx.author.id} on guild {ctx.guild.id}: is_owner={is_owner}")
    return is_owner

class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logger.debug("[DEBUG] Initializing AdminCog")
       

        self.sessions = SessionManager(
            db_path=os.path.join(config["bfl_root"], "sessions.db"),
            max_sessions=config["max_sessions_per_user"]
        )

        logger.debug(f"[DEBUG] SessionManager initialized with data_root={config['bfl_root']}")

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

async def setup(bot):
    logger.debug("[DEBUG] Loading AdminCog cog...")
    await bot.add_cog(AdminCog(bot))
    logger.info("[AI] AdminCog loaded successfully.")