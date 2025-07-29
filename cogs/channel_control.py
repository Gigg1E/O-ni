# cogs/channel_control.py

import discord
from discord.ext import commands
from discord import app_commands
import os
import json
import logging

from utils.config_loader import load_config

config = load_config()

# ---------- Logger Setup ----------
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if not logger.hasHandlers():
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# ---------- Channel JSON File Handling ----------

def get_channel_file(guild_id):
    path = os.path.join(config["bfl_root"], str(guild_id), "channels.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    logger.debug(f"[DEBUG] Channel file path resolved: {path}")
    return path

def load_allowed_channels(guild_id):
    path = get_channel_file(guild_id)
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f).get("allowed", [])
        except json.JSONDecodeError as e:
            logger.error(f"[ERROR] Failed to decode JSON for guild {guild_id}: {e}", exc_info=True)
    return []

def save_allowed_channels(guild_id, allowed):
    path = get_channel_file(guild_id)
    try:
        with open(path, "w") as f:
            json.dump({"allowed": allowed}, f, indent=4)
        logger.debug(f"[DEBUG] Saved allowed channels: {allowed} for guild {guild_id}")
    except Exception as e:
        logger.error(f"[ERROR] Failed to save allowed channels for guild {guild_id}: {e}", exc_info=True)

# ---------- Permissions Check ----------

def is_admin(ctx: commands.Context):
    result = (
        ctx.author.id == ctx.guild.owner_id
        or ctx.author.guild_permissions.administrator
    )
    logger.debug(f"[DEBUG] Admin check for user {ctx.author.id} in guild {ctx.guild.id}: {result}")
    return result

def is_adminInteraction(interaction: discord.Interaction):
    result = (
        interaction.user.id == interaction.guild.owner_id
        or interaction.user.guild_permissions.administrator
    )
    logger.debug(f"[DEBUG] Admin check for user {interaction.user.id} in guild {interaction.guild.id}: {result}")
    return result

# ---------- Channel Control Cog ----------

class ChannelControl(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        logger.debug("[DEBUG] ChannelControl Cog initialized")

    def is_allowed(self, guild_id: int, channel_id: int) -> bool:
        allowed = load_allowed_channels(guild_id)
        result = not allowed or channel_id in allowed
        logger.debug(f"[DEBUG] is_allowed result for channel {channel_id} in guild {guild_id}: {result}")
        return result

    @commands.command(name="allowchannel", help="✅ Allow this channel for bot interaction.")
    @commands.check(is_admin)
    async def allowchannel(self, ctx: commands.Context):
        guild_id = ctx.guild.id
        channel_id = ctx.channel.id

        allowed = load_allowed_channels(guild_id)
        if channel_id in allowed:
            await ctx.send("🔄 This channel is already allowed.")
        else:
            allowed.append(channel_id)
            save_allowed_channels(guild_id, allowed)
            await ctx.send("✅ Channel allowed for bot interaction.")

    @commands.command(name="disallowchannel", help="❌ Remove this channel from bot access.")
    @commands.check(is_admin)
    async def disallowchannel(self, ctx: commands.Context):
        guild_id = ctx.guild.id
        channel_id = ctx.channel.id

        allowed = load_allowed_channels(guild_id)
        if channel_id in allowed:
            allowed.remove(channel_id)
            save_allowed_channels(guild_id, allowed)
            await ctx.send("⛔ This channel has been disallowed.")
        else:
            await ctx.send("⚠ This channel was not in the allowed list.")

    @commands.command(name="listallowed", help="📄 List allowed channels in this server.")
    @commands.check(is_admin)
    async def listallowed(self, ctx: commands.Context):
        guild_id = ctx.guild.id
        allowed = load_allowed_channels(guild_id)

        if not allowed:
            await ctx.send("📢 All channels are allowed (no restrictions set).")
            return

        mentions = []
        for ch_id in allowed:
            channel = ctx.guild.get_channel(ch_id)
            mentions.append(f"- {channel.mention if channel else f'#{ch_id}'}")

        await ctx.send("✅ Allowed channels:\n" + "\n".join(mentions))

    # '/' commands for list server support
    @app_commands.command(name="listallowed", description="📄 List allowed channels in this server.")
    async def listallowed(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        allowed = load_allowed_channels(guild_id)

        if not allowed:
            await interaction.response.send_message("📢 All channels are allowed (no restrictions set).")
            return

        mentions = []
        for ch_id in allowed:
            channel = interaction.guild.get_channel(ch_id)
            mentions.append(f"- {channel.mention if channel else f'#{ch_id}'}")

        await interaction.followup.send("✅ Allowed channels:\n" + "\n".join(mentions))


# ---------- Cog Setup ----------

async def setup(bot: commands.Bot):
    logger.debug("[DEBUG] Loading ChannelControl cog...")
    await bot.add_cog(ChannelControl(bot))
    logger.info("[AI] ChannelControl cog loaded successfully.")